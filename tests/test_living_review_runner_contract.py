from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_living_review_pipeline.py"
RUNBOOK = ROOT / "protocol/LIVING_REVIEW_RUNBOOK.md"


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


if __name__ == "__main__":
    unittest.main()
