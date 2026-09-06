import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from atlas_review_amendments import apply_review_amendments, membership_ids
from apply_atlas_review_amendments import reviewed_view


class AtlasReviewAmendmentTests(unittest.TestCase):
    def fixture(self, root):
        source = root / "paper.md"
        source.write_text("Teacher receives gene features.\n")
        route = {"route_id": "r1", "carrier_family": "text_native_token_stream", "carrier_subtype": "structured_biological_prompt_or_task_scaffold", "evidence_quote": "Earlier unrelated quote."}
        record = {
            "route_id": "r1", "case_id": "P023", "date": "2026-09-06", "status": "reviewed_with_subtype_uncertainty", "procedure": "author-led assisted",
            "model_role": "auxiliary_teacher", "operation_purpose": "training_data_construction", "author_confirmed_fields": ["carrier_subtype"], "rationale": "Format unconfirmed.",
            "expected": {"carrier_subtype": route["carrier_subtype"]},
            "updates": {"carrier_subtype": "unclear", "evidence_quote": "Teacher receives gene features."},
            "evidence_source": {"path": "paper.md", "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "line": 1},
        }
        file = root / "amendment.json"
        file.write_text(json.dumps(record))
        return route, record, file

    def test_preserves_original_and_other_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            route, _, file = self.fixture(root)
            rows = [route, {"route_id": "r2", "carrier_subtype": "unchanged"}]
            original = deepcopy(rows)
            result, applied = apply_review_amendments(rows, [file], root)
            self.assertEqual(rows, original)
            self.assertEqual(result[1], original[1])
            self.assertEqual(result[0]["carrier_subtype"], "unclear")
            self.assertEqual(result[0]["review_amendment"]["original"]["evidence_quote"], route["evidence_quote"])
            self.assertEqual(len(applied), 1)

    def test_stale_source_or_changed_candidate_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            route, _, file = self.fixture(root)
            route["carrier_subtype"] = "changed"
            with self.assertRaisesRegex(ValueError, "source changed"):
                apply_review_amendments([route], [file], root)
            route["carrier_subtype"] = "structured_biological_prompt_or_task_scaffold"
            (root / "paper.md").write_text("Different text.")
            with self.assertRaisesRegex(ValueError, "hash changed"):
                apply_review_amendments([route], [file], root)

    def test_absent_route_is_not_added(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, _, file = self.fixture(root)
            self.assertEqual(apply_review_amendments([], [file], root), ([], []))

    def test_uncertainty_is_family_scoped_membership(self):
        model = {"subtypes": [], "unresolved_families": ["text_native_token_stream"]}
        self.assertEqual(membership_ids(model), ["unresolved::text_native_token_stream"])

    def test_changed_route_identity_in_same_record_requires_reconciliation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, record, file = self.fixture(root)
            record["expected"]["record_id"] = "paper_a"
            file.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "route identity changed"):
                apply_review_amendments([{"route_id": "new_id", "record_id": "paper_a"}], [file], root)

    def test_identity_changes_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            route, record, file = self.fixture(root)
            record["updates"]["model_id"] = "another_model"
            file.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "unsupported field"):
                apply_review_amendments([route], [file], root)

    def test_view_is_idempotent_and_uncertainty_does_not_add_a_subtype(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            route, _, file = self.fixture(root)
            route.update(lifecycle_phase="inference", source_object_verbatim="genes", model_visible_form_verbatim="gene text")
            family = route["carrier_family"]
            subtype = route["carrier_subtype"]
            model = {"model_id": "model_a", "record_id": "record_a", "model_name": "Teacher", "routes": [route], "subtypes": [subtype]}
            atlas = {"architectures": [model], "families": [{"family_id": family, "code": "F1", "subtypes": [{"subtype_id": subtype, "leaf_id": "F1.L2"}]}], "graph": {"nodes": [], "edges": [], "counts": {"subtypes": 1}}, "meta": {}, "filter_values": {}}
            first = reviewed_view(atlas, [file], root)
            self.assertEqual(first, reviewed_view(first, [file], root))
            self.assertEqual(first["graph"]["counts"]["subtypes"], 1)
            self.assertEqual(first["graph"]["counts"]["annotation_states"], 1)
            self.assertEqual(first["families"][0]["subtypes"][0]["route_count"], 0)
            self.assertEqual(first["architectures"][0]["illustrative_examples"], [])


if __name__ == "__main__":
    unittest.main()
