from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_living_review_pipeline.py"
RUNBOOK = ROOT / "protocol/LIVING_REVIEW_RUNBOOK.md"
sys.path.insert(0, str(ROOT / "scripts"))

from run_living_review_pipeline import Pipeline


class LivingReviewRunnerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = RUNNER.read_text(encoding="utf-8")
        cls.runbook = RUNBOOK.read_text(encoding="utf-8")

    def test_f6_is_part_of_routine_taxonomy_classification(self) -> None:
        stage = self.runner[
            self.runner.index("    def stage_taxonomy_classification") :
            self.runner.index("    def stage_crop_validation")
        ]
        for required in (
            "run_taxonomy_semantic_sufficiency_audit.py",
            '"f6-prepare"',
            '"semantic_reviewer"',
            '"adversarial_reviewer"',
            '"f6-adjudicate"',
            '"f6-finalize"',
            "semantic_sufficiency_action_queue.csv",
            "raise ManualGate",
        ):
            self.assertIn(required, stage)

    def test_f7_is_part_of_routine_crop_validation(self) -> None:
        stage = self.runner[
            self.runner.index("    def stage_crop_validation") :
            self.runner.index("    def stage_snapshot")
        ]
        for required in (
            "run_atlas_exact_preview_validation.py",
            "run_atlas_replacement_validation.py",
            '"f7-prepare"',
            '"exact_preview_validator"',
            '"input_role_validator"',
            '"f7-replacement-finalize"',
            '"f7-finalize"',
            "unresolved_models",
            "proposed_crossvalidated_crop_ledger.json",
        ):
            self.assertIn(required, stage)
        self.assertLess(stage.index("unresolved_models"), stage.index("shutil.copy2(proposed"))

    def test_snapshot_cannot_precede_f6_or_f7(self) -> None:
        taxonomy = self.runner.index("    def stage_taxonomy_classification")
        crops = self.runner.index("    def stage_crop_validation")
        snapshot = self.runner.index("    def stage_snapshot")
        self.assertLess(taxonomy, crops)
        self.assertLess(crops, snapshot)

    def test_runbook_uses_only_the_canonical_checkout_as_working_directory(self) -> None:
        self.assertIn('cd "$REVIEW_REPO_ROOT"', self.runbook)
        self.assertNotIn("cd /Users/bogdan.didenko/lpnu/review", self.runbook)
        self.assertNotIn('cd "$REVIEW_ARTIFACT_ROOT"', self.runbook)

    def test_stage_validation_resolves_migrated_artifacts_and_inventory_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact_root = root / "artifact-store"
            migrated = artifact_root / "data/living_catalog_updates/update_test/payload.bin"
            migrated.parent.mkdir(parents=True)
            migrated.write_bytes(b"migrated immutable evidence")

            config = {
                "baseline_search_end": "2026-07-06",
                "master_record_files": [],
                "baseline_taxonomy_root": str(root / "taxonomy"),
                "baseline_docling_corpus_roots": [],
                "baseline_crop_ledger": str(root / "crops.json"),
                "living_state": str(root / "current.json"),
                "updates_root": str(root / "updates"),
                "atlas_output": str(root / "atlas"),
                "artifact_roots": [str(artifact_root)],
            }
            args = argparse.Namespace(
                config=root / "config.json",
                run_id="update_test",
                date_from="2026-07-07",
                date_to="2026-08-09",
                force=False,
                manage_server=False,
                from_stage=None,
                through_stage=None,
            )
            pipeline = Pipeline(args, config)
            relative_path = "data/living_catalog_updates/update_test/payload.bin"
            old_path = "/old/machine/review/data/living_catalog_updates/update_test/payload.bin"
            digest = hashlib.sha256(migrated.read_bytes()).hexdigest()
            declared_artifact = {
                "path": relative_path,
                "bytes": migrated.stat().st_size,
                "sha256": digest,
            }
            inventoried_artifact = {
                "path": old_path,
                "bytes": migrated.stat().st_size,
                "sha256": digest,
            }
            inventory = root / "artifact_inventory.json"
            inventory.write_text(
                json.dumps({"stage": "search", "files": [inventoried_artifact]}),
                encoding="utf-8",
            )
            pipeline.manifest["stages"] = {
                "search": {
                    "status": "complete",
                    "human_input_fingerprints": [],
                    "artifacts": [declared_artifact],
                    "artifact_inventory": str(inventory),
                    "artifact_inventory_sha256": hashlib.sha256(
                        inventory.read_bytes()
                    ).hexdigest(),
                }
            }

            self.assertEqual(pipeline.stage_validation_issues("search"), [])


if __name__ == "__main__":
    unittest.main()
