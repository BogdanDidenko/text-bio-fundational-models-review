import copy
import json
import unittest

from pydantic import ValidationError

from scripts.build_representation_library import BASE, compile_release, objects
from scripts.docling_graph_templates.representation_library import AssemblyDocument, CatalogSeed
from scripts.review_representation_library_change import review


def seed():
    return {"release": "0.1.0", "blocks": [{
        "block_id": "operation.lookup", "kind": "operation", "label": "Lookup",
        "definition": "Select rows by identifiers.", "boundaries": "Input identifiers refer to the declared table.",
        "input_roles": ["indices", "table"], "output_roles": ["selected_rows"],
        "aliases": [], "status": "reviewed_candidate", "composition": [],
        "examples": [{"record_id": "paper", "trajectory_id": "use", "element_kind": "step", "element_ids": ["lookup"], "rationale": "Documented."}],
    }], "mappings": [{"kind": "operation", "source_label": "embedding_lookup", "block_id": "operation.lookup", "relation": "specialization", "rationale": "Embedding table lookup."}], "decisions": []}


class LibraryContractTests(unittest.TestCase):
    def test_source_alias_cannot_have_two_meanings(self):
        value = seed()
        value["mappings"].append(copy.deepcopy(value["mappings"][0]))
        with self.assertRaises(ValidationError):
            CatalogSeed.model_validate(value)

    def test_unknown_composition_rejected(self):
        value = seed()
        value["blocks"][0]["composition"] = ["operation.absent"]
        with self.assertRaises(ValidationError):
            CatalogSeed.model_validate(value)

    def test_kind_mismatch_rejected(self):
        value = seed()
        value["mappings"][0]["kind"] = "representation"
        with self.assertRaises(ValidationError):
            CatalogSeed.model_validate(value)

    def test_no_source_size_constraints(self):
        banned = {"maxLength", "minLength", "maxItems", "minItems", "maxProperties", "minProperties"}
        for model in (CatalogSeed, AssemblyDocument):
            for obj in objects(model.model_json_schema()):
                self.assertFalse(set(obj) & banned)

    def test_new_example_is_compatible_and_requires_new_release(self):
        before = seed()
        after = copy.deepcopy(before)
        after["release"] = "0.1.1"
        after["blocks"][0]["aliases"].append("table_lookup")
        result = review(before, after)
        self.assertFalse(result["requires_author_approval"])
        self.assertTrue(result["new_release_required"])
        self.assertFalse(result["same_release_modified"])

    def test_definition_change_requires_author_review(self):
        before = seed()
        after = copy.deepcopy(before)
        after["release"] = "0.2.0"
        after["blocks"][0]["definition"] = "Generate a sampled latent."
        self.assertTrue(review(before, after)["requires_author_approval"])

    def test_changed_mapping_and_deletion_require_review(self):
        before = seed()
        after = copy.deepcopy(before)
        after["mappings"] = []
        self.assertTrue(review(before, after)["requires_author_approval"])


class PilotCompilationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = compile_release(BASE)

    def test_complete_pilot_and_round_trip(self):
        report = self.output["validation.json"]
        self.assertEqual(report["record_count"], 4)
        self.assertEqual(report["trajectory_count"], 47)
        self.assertTrue(report["lossless_round_trip"])
        self.assertFalse(report["canonical_migration"])

    def test_all_assemblies_pin_release_and_validate(self):
        for assembly in self.output["assemblies.json"]:
            AssemblyDocument.model_validate(assembly)
            self.assertEqual(assembly["library_sha256"], self.output["catalog.json"]["library_sha256"])

    def test_dangling_operand_rejected(self):
        assembly = copy.deepcopy(self.output["assemblies.json"][0])
        assembly["operations"][0]["inputs"][0]["node_id"] = "absent"
        with self.assertRaises(ValidationError):
            AssemblyDocument.model_validate(assembly)

    def test_numeric_width_rejected(self):
        assembly = copy.deepcopy(self.output["assemblies.json"][0])
        assembly["nodes"][0]["symbolic_shape"] = ["768"]
        with self.assertRaises(ValidationError):
            AssemblyDocument.model_validate(assembly)

    def test_same_shape_does_not_create_shared_identity(self):
        self.assertTrue(all(not assembly["identity_links"] for assembly in self.output["assemblies.json"]))

    def test_unknown_bindings_are_preserved_as_proposals(self):
        proposals = {item["proposal_id"] for item in self.output["catalog.json"]["proposals"]}
        for assembly in self.output["assemblies.json"]:
            for obj in objects(assembly):
                if obj.get("relation") == "unresolved" and "proposal_id" in obj:
                    self.assertIn(obj["proposal_id"], proposals)

    def test_evidence_snapshot_contains_full_quotes_and_native_id_gap(self):
        for item in self.output["evidence.json"]:
            self.assertTrue(item["quote"])
            self.assertEqual(item["verification"], "literal_own_section_match_at_capture")
            self.assertIsNone(item["native_pdf_item"])

    def test_composites_preserve_real_ports_and_branches(self):
        composites = [block for block in self.output["catalog.json"]["blocks"] if block["kind"] == "composite"]
        self.assertTrue(composites)
        for block in composites:
            for example in block["examples"]:
                graph = example["source_subgraph"]
                self.assertTrue(graph)
                nodes = {node["node_id"] for node in graph["nodes"]}
                for step in graph["operations"]:
                    self.assertTrue(set(step["outputs"]) <= nodes)
                    self.assertTrue({item["node_id"] for item in step["inputs"]} <= nodes)
                self.assertEqual(graph["status"], "documented_source_instance")


if __name__ == "__main__":
    unittest.main()
