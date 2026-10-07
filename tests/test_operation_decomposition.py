import ast
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import build_operation_corpus, build_representation_library
from scripts.build_representation_library import BASE, compile_release
from scripts.docling_graph_templates.representation_library import restore_source
from scripts.operation_decomposition import (
    ATLAS, CATALOG, PILOT_RECORDS, build_packet, encoded, evidence_entries, extraction_schema,
    pilot_document, review_schema, sha, validate_document,
)


class OperationDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text())
        cls.release = compile_release(BASE)
        cls.assemblies = cls.release["assemblies.json"]
        cls.included = sorted({m["record_id"] for m in json.loads(ATLAS.read_text())["architectures"]})

    def test_packets_reproduce_every_pilot_evidence_section(self):
        snapshot = json.loads((BASE / "evidence_snapshot.json").read_text())
        packets = {record: build_packet(record) for record in snapshot["records"]}
        for item in snapshot["evidence"]:
            manifest, sections = packets[item["record_id"]]
            self.assertEqual(manifest["source_sha256"], item["source_sha256"])
            section = sections[item["section_id"]]
            self.assertEqual(section["text_sha256"], item["section_sha256"])
            self.assertEqual(section["text"].find(item["quote"]), int(item["quote_start_char_in_section"]))
            path = item["heading_path"] if isinstance(item["heading_path"], list) else ast.literal_eval(item["heading_path"])
            self.assertEqual(section["heading_path"], path)

    def test_every_included_record_has_a_packet(self):
        self.assertEqual(len(self.included), 55)
        for record in self.included:
            manifest, sections = build_packet(record)
            self.assertTrue(sections, record)

    def test_agent_format_round_trips_all_pilot_trajectories(self):
        restored = 0
        for record in sorted(PILOT_RECORDS):
            _, sections = build_packet(record)
            doc = pilot_document(record, self.assemblies, self.catalog)
            errors, _, compiled = validate_document(doc, record, sections, self.catalog, "x", "test")
            self.assertEqual(errors, [])
            original = [a for a in self.assemblies if a["record_id"] == record]
            for old, new in zip(original, compiled):
                self.assertEqual(restore_source(old), restore_source(new))
                self.assertEqual([(c["operation_id"], c["inputs"], c["outputs"], c["source_step_id"]) for c in old["calls"]],
                                 [(c["operation_id"], c["inputs"], c["outputs"], c["source_step_id"]) for c in new["calls"]])
                restored += 1
        self.assertEqual(restored, 47)

    def _pilot(self):
        record = "full_2026-07-06__rec_001319"
        return record, build_packet(record)[1], pilot_document(record, self.assemblies, self.catalog)

    def _errors(self, mutate):
        record, sections, doc = self._pilot()
        doc = copy.deepcopy(doc)
        mutate(doc)
        return validate_document(doc, record, sections, self.catalog, "x", "test")[0]

    def _first_library_step(self, doc):
        return next(s for t in doc["trajectories"] for s in t["steps"] if s["decomposition"])

    def test_paraphrased_quote_is_rejected(self):
        def mutate(doc):
            doc["trajectories"][0]["steps"][0]["evidence"][0]["quote"] += " (paraphrase)"
        self.assertTrue(any("literal substring" in e for e in self._errors(mutate)))

    def test_unknown_section_is_rejected(self):
        def mutate(doc):
            doc["trajectories"][0]["evidence"][0]["section_id"] = "sec_9999"
        self.assertTrue(any("unknown section" in e for e in self._errors(mutate)))

    def test_missing_declared_parameter_is_rejected(self):
        def mutate(doc):
            call = self._first_library_step(doc)["decomposition"][0]
            call["parameters"] = [p for p in call["parameters"] if p["name"] != self._declared(call)[0]]
        self.assertTrue(any("declared parameters missing" in e for e in self._errors(mutate)))

    def _declared(self, call):
        return next(b for b in self.catalog["blocks"] if b["operation_id"] == call["operation_id"])["parameters"]

    def test_unconsumed_source_operand_is_rejected(self):
        def mutate(doc):
            step = self._first_library_step(doc)
            step["inputs"].append({"node_id": doc["trajectories"][0]["nodes"][0]["node_id"], "port_role": "extra"})
            for call in step["decomposition"]:
                for binding in call["inputs"]:
                    binding["node_ids"] = [n for n in binding["node_ids"] if n != doc["trajectories"][0]["nodes"][0]["node_id"]]
        self.assertTrue(any("not consumed" in e or "Contract validation" in e for e in self._errors(mutate)))

    def test_mixed_boundary_and_library_calls_are_rejected(self):
        def mutate(doc):
            step = self._first_library_step(doc)
            step["decomposition"].append({"operation_id": None, "inputs": [], "outputs": [], "parameters": [],
                                          "condition": None, "uncertainty": None})
        self.assertTrue(any("mixes library calls" in e for e in self._errors(mutate)))

    def test_invented_operation_is_rejected(self):
        def mutate(doc):
            self._first_library_step(doc)["decomposition"][0]["operation_id"] = "gene_fusion"
        self.assertTrue(any("unknown operation_id" in e for e in self._errors(mutate)))

    def test_schemas_are_strict_for_structured_output(self):
        def walk(node):
            if isinstance(node, dict):
                if node.get("type") == "object":
                    self.assertFalse(node["additionalProperties"])
                    self.assertEqual(sorted(node["required"]), sorted(node["properties"]))
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)
        walk(extraction_schema(self.catalog))
        walk(review_schema())

    def test_evidence_identity_matches_pilot(self):
        record, sections, doc = self._pilot()
        manifest = build_packet(record)[0]
        _, _, compiled = validate_document(doc, record, sections, self.catalog, "x", "test")
        produced = set(evidence_entries(record, compiled, sections, manifest))
        pilot = {e["evidence_id"] for e in self.release["evidence.json"] if e["record_id"] == record}
        self.assertEqual(produced, pilot)

    def test_accepted_corpus_record_reaches_the_release(self):
        record = "full_2026-07-06__rec_000060"
        manifest, sections = build_packet(record)
        section = next(s for s in sections.values() if len(s["text"]) > 200)
        quote = section["text"][section["text"].index("\n") + 1:][:80].strip()
        ev = [{"section_id": section["section_id"], "quote": quote, "kind": "paper_text"}]
        node = lambda nid: {"node_id": nid, "representation_type": nid, "symbolic_shape": None, "axis_semantics": None,
                            "information_content": nid, "contextual_role": "sample_input", "evidence": ev, "uncertainty": None}
        doc = {"record_id": record, "coverage_questions": [], "operation_proposals": [], "trajectories": [{
            "trajectory_id": "t", "model_variant": "m", "task_configuration": "c", "lifecycle_phase": "inference",
            "model_role": "primary_model", "recipient_component": "r", "nodes": [node("a"), node("b")],
            "steps": [{"step_id": "s", "component": "k", "operation_type": "opaque_module", "inputs": [{"node_id": "a", "port_role": "x"}],
                       "outputs": ["b"], "evidence": ev, "uncertainty": None, "intermediate_nodes": [], "bypasses": [],
                       "decomposition": [{"operation_id": None, "inputs": [], "outputs": [], "parameters": [],
                                          "condition": None, "uncertainty": None}]}],
            "receipt_inputs": [{"node_id": "b", "port_role": "y"}], "evidence": ev, "open_questions": []}]}
        errors, _, compiled = validate_document(doc, record, sections, self.catalog, "x", "test")
        self.assertEqual(errors, [])
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "records" / record
            (folder / "sections").mkdir(parents=True)
            (folder / "sections" / f"{section['section_id']}.md").write_text(section["text"], encoding="utf-8")
            (folder / "packet_manifest.json").write_bytes(encoded(manifest))
            (folder / "assemblies.json").write_bytes(encoded(compiled))
            (folder / "evidence.json").write_bytes(encoded(list(evidence_entries(record, compiled, sections, manifest).values())))
            (folder / "status.json").write_bytes(encoded({"record_id": record, "status": "accepted"}))
            corpus = build_operation_corpus.collect(Path(tmp), False)
            target = Path(tmp) / "corpus.json"
            target.write_bytes(encoded(corpus))
            with mock.patch.object(build_representation_library, "CORPUS_PATH", target):
                merged = compile_release(BASE)
        self.assertIn(record, merged["catalog.json"]["records"])
        self.assertEqual(merged["validation.json"]["record_count"], 5)
        self.assertEqual(merged["validation.json"]["pilot_record_count"], 4)
        self.assertEqual(len(merged["assemblies.json"]), 48)
        self.assertIn("opaque_module", {p["source_operation"] for p in merged["catalog.json"]["pending"]})


if __name__ == "__main__":
    unittest.main()
