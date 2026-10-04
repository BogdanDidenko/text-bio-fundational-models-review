import copy
import unittest

from pydantic import ValidationError

from scripts.build_representation_library import BASE, compile_release, objects
from scripts.docling_graph_templates.representation_library import (
    OperationAssembly, OperationCatalog, restore_source, validate_operation_ports,
)
from scripts.review_representation_library_change import review


class OperationLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = compile_release(BASE)
        cls.catalog = cls.output["catalog.json"]
        cls.assemblies = cls.output["assemblies.json"]

    def test_catalog_contains_operations_only(self):
        for block in self.catalog["blocks"]:
            self.assertIn("operation_id", block)
            self.assertNotIn("kind", block)
        self.assertIn("lookup", {item["operation_id"] for item in self.catalog["blocks"]})

    def test_all_original_trajectories_preserved(self):
        import json
        original = {(row["record_id"], row["trajectory"]["trajectory_id"]): row["trajectory"]
                    for row in (json.loads(line) for line in (BASE / "pilot_input.jsonl").read_text().splitlines())}
        self.assertEqual(len(self.assemblies), 47)
        for assembly in self.assemblies:
            self.assertEqual(restore_source(assembly), original[(assembly["record_id"], assembly["trajectory_id"])])

    def test_every_call_has_valid_ports_and_refs(self):
        for assembly in self.assemblies:
            OperationAssembly.model_validate(assembly)
            validate_operation_ports(assembly, self.catalog)

    def test_lookup_has_explicit_table_and_reuses_type(self):
        lookup = next(block for block in self.catalog["blocks"] if block["operation_id"] == "lookup")
        self.assertGreaterEqual(len(lookup["reuse_record_ids"]), 3)
        for assembly in self.assemblies:
            for call in assembly["calls"]:
                if call["operation_id"] == "lookup":
                    self.assertTrue(call["inputs"]["keys"])
                    self.assertEqual(len(call["inputs"]["table"]), 1)

    def test_lookup_and_layernorm_are_separate_calls(self):
        for assembly in self.assemblies:
            for source in assembly["source_steps"]:
                if source["operation_type"] == "embedding_lookup_layer_norm":
                    calls = [call for call in assembly["calls"] if call["source_step_id"] == source["step_id"]]
                    self.assertEqual([call["operation_id"] for call in calls], ["lookup", "normalize"])
                    self.assertEqual(calls[0]["outputs"]["values"], calls[1]["inputs"]["values"])

    def test_expression_scaling_and_log_are_separate_with_bypass(self):
        for assembly in self.assemblies:
            for source in assembly["source_steps"]:
                if source["operation_type"] == "dataset_aware_expression_normalization":
                    calls = [call for call in assembly["calls"] if call["source_step_id"] == source["step_id"]]
                    self.assertEqual([call["operation_id"] for call in calls], ["normalize", "log_transform"])
                    self.assertTrue(all(call["condition"] for call in calls))
                    self.assertTrue(any(edge["source_step_id"] == source["step_id"] for edge in assembly["bypasses"]))

    def test_same_operation_keeps_different_methods(self):
        methods = {call["parameters"].get("method") for assembly in self.assemblies for call in assembly["calls"] if call["operation_id"] == "normalize"}
        self.assertTrue({"TPM", "CP10K", "LayerNorm"} <= methods)

    def test_unknown_fusion_algebra_is_preserved(self):
        for assembly in self.assemblies:
            for source in assembly["source_steps"]:
                if source["operation_type"] == "combine_identity_value_and_mask":
                    calls = [call for call in assembly["calls"] if call["source_step_id"] == source["step_id"]]
                    self.assertEqual(len(calls), 1)
                    self.assertIsNone(calls[0]["operation_id"])

    def test_missing_or_unknown_port_fails(self):
        assembly = copy.deepcopy(next(item for item in self.assemblies if any(call["operation_id"] == "lookup" for call in item["calls"])))
        call = next(call for call in assembly["calls"] if call["operation_id"] == "lookup")
        call["inputs"].pop("table")
        with self.assertRaises(ValueError):
            validate_operation_ports(assembly, self.catalog)

    def test_dangling_operand_fails(self):
        assembly = copy.deepcopy(self.assemblies[0])
        assembly["calls"][0]["inputs"] = {"values": ["absent"]}
        with self.assertRaises(ValidationError):
            OperationAssembly.model_validate(assembly)

    def test_no_size_constraints(self):
        for schema in (OperationAssembly.model_json_schema(), OperationCatalog.model_json_schema()):
            for item in objects(schema):
                self.assertFalse(set(item) & {"minLength", "maxLength", "minItems", "maxItems"})

    def test_binning_supplement_keeps_two_lookup_branches(self):
        example = next(block for block in self.catalog["blocks"] if block["operation_id"] == "bin")["supplemental_examples"][0]
        assembly = example["assembly"]
        OperationAssembly.model_validate(assembly)
        validate_operation_ports(assembly, self.catalog)
        self.assertEqual(example["source_status"], "WITHDRAWN")
        self.assertEqual(len([call for call in assembly["calls"] if call["operation_id"] == "lookup"]), 3)
        fusion = next(call for call in assembly["calls"] if call["operation_id"] == "add")
        self.assertEqual(fusion["inputs"]["values"], ["gene_vectors", "value_vectors"])
        self.assertNotIn(example["record_id"], self.catalog["records"])

    def test_semantic_change_requires_author_review(self):
        raw = {key: self.catalog[key] for key in ("contract_version", "release")}
        raw["blocks"] = [{key: value for key,value in block.items() if key not in {"usage", "supplemental_examples", "reuse_record_ids", "status"}} for block in self.catalog["blocks"]]
        changed = copy.deepcopy(raw)
        changed["release"] = "1.1.0"
        changed["blocks"][0]["definition"] = "Different scientific meaning"
        self.assertTrue(review(raw,changed)["requires_author_approval"])


if __name__ == "__main__":
    unittest.main()
