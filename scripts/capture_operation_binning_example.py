"""Freeze a source-backed constructor example from an existing selected section."""

import json

from scripts.build_representation_library import BASE, PACKETS, digest, encoded, quote_key
from scripts.docling_graph_templates.representation_library import OperationAssembly, restore_source


def capture():
    record = "full_2026-07-06__rec_001277"
    section_id = "sec_0022"
    folder = PACKETS / record
    body = (folder / "sections" / f"{section_id}.md").read_text()
    manifest = json.loads((folder / "packet_manifest.json").read_text())
    section = next(item for item in manifest["sections"] if item["section_id"] == section_id)
    evidence = {"section_id": section_id, "quote": body, "kind": "paper_text"}
    eid = quote_key(record, evidence)
    nodes = []

    def node(nid, form, content, role="intermediate_representation"):
        nodes.append({"node_id": nid, "representation_type": form, "symbolic_shape": None,
            "axis_semantics": None, "information_content": content, "contextual_role": role,
            "evidence": [evidence], "uncertainty": "Exact tensor layout is not reconstructed in this section-only example."})

    node("expression", "expression_values", "Measured single-cell expression", "sample_input")
    node("gene_ids", "gene_identifiers", "Identifiers aligned to expression positions", "sample_input")
    node("logged", "log_expression", "Log1p transformed expression")
    node("selected_values", "selected_expression", "HVG-selected expression")
    node("selected_genes", "selected_gene_identifiers", "Identifiers of the selected genes")
    node("gene_vocabulary", "vocabulary_table", "Gene identifier to vocabulary-index mapping", "reference_resource")
    node("gene_indices", "gene_vocabulary_indices", "Vocabulary identifiers for selected genes")
    node("bin_indices", "expression_bin_indices", "Equal-interval nonzero expression bins with zero preserved")
    node("gene_table", "embedding_matrix", "Gene embedding-layer parameters emb_g; trainability unspecified in this section", "model_parameter")
    node("bin_table", "embedding_matrix", "Expression embedding-layer parameters emb_x; a separate table", "model_parameter")
    node("gene_vectors", "gene_embeddings", "Selected gene embedding vectors")
    node("value_vectors", "expression_embeddings", "Selected expression-bin embedding vectors")
    node("fused", "summed_input_embeddings", "Element-wise sum supplied to Transformer encoder blocks")
    calls = []
    steps = []

    def call(cid, op, inputs, outputs, parameters):
        steps.append({"step_id": cid, "operation_type": op, "component": "OKR-Cell input embedding module",
            "inputs": [{"node_id": ref, "port_role": port} for port, refs in inputs.items() for ref in refs],
            "outputs": [ref for refs in outputs.values() for ref in refs], "evidence": [evidence],
            "uncertainty": "Section-only reconstruction; missing equations and training details remain unresolved."})
        calls.append({"call_id": cid, "operation_id": op, "component": "OKR-Cell input embedding module",
            "inputs": inputs, "outputs": outputs, "parameters": parameters, "condition": None,
            "source_step_id": cid, "evidence": [evidence], "uncertainty": steps[-1]["uncertainty"],
            "status": "documented_operation"})

    call("log", "log_transform", {"values": ["expression"]}, {"values": ["logged"]}, {"method": "log1p"})
    call("hvg", "select", {"values": ["logged", "gene_ids"]}, {"values": ["selected_values", "selected_genes"]}, {"criterion": "highly variable genes", "method": "unspecified"})
    call("gene_token_ids", "lookup", {"keys": ["selected_genes"], "table": ["gene_vocabulary"]}, {"values": ["gene_indices"]}, {"resource_kind": "gene vocabulary"})
    call("bins", "bin", {"values": ["selected_values"]}, {"values": ["bin_indices"]}, {"strategy": "equal_interval", "scope": "per_cell_nonzero_values", "zero_handling": "retain zero", "bin_edges": "source-defined; formula not decoded"})
    call("gene_lookup", "lookup", {"keys": ["gene_indices"], "table": ["gene_table"]}, {"values": ["gene_vectors"]}, {"resource_kind": "embedding matrix", "trainability": "unspecified"})
    call("value_lookup", "lookup", {"keys": ["bin_indices"], "table": ["bin_table"]}, {"values": ["value_vectors"]}, {"resource_kind": "embedding matrix", "trainability": "unspecified"})
    call("fusion", "add", {"values": ["gene_vectors", "value_vectors"]}, {"values": ["fused"]}, {"alignment": "selected gene position and shared embedding feature coordinate"})
    trajectory = {"trajectory_id": "input_embedding_section_example", "model_variant": "OKR-Cell input module",
        "task_configuration": "Section-only shared input embedding example", "lifecycle_phase": "unspecified", "model_role": "unresolved",
        "recipient_component": "Transformer encoder blocks", "nodes": nodes, "steps": steps,
        "receipt_inputs": [{"node_id": "fused", "port_role": "input embeddings"}], "evidence": [evidence],
        "open_questions": ["Source title is marked WITHDRAWN in the inventory. This example describes the documented mechanism and changes no eligibility decision.",
            "Missing equations, HVG algorithm, matrix training status, special-token placement and phase-specific masking remain unspecified."]}
    assembly = {**{key: value for key, value in trajectory.items() if key not in {"nodes", "steps"}},
        "contract_version": "operation-assembly-v1", "record_id": record, "library_release": "1.0.0", "library_sha256": "set_at_build",
        "nodes": [{**item, "origin": "source_annotation"} for item in nodes], "calls": calls, "bypasses": [], "source_steps": steps}
    OperationAssembly.model_validate(assembly)
    if restore_source(assembly) != trajectory:
        raise ValueError("Supplemental source reconstruction changed")
    item = {**evidence, "evidence_id": eid, "record_id": record, "paper": "OKR-Cell (WITHDRAWN source)",
        "heading_path": section["heading_path"], "section_sha256": section["text_sha256"],
        "source_sha256": manifest["source_sha256"], "quote_start_char_in_section": 0,
        "verification": "literal_own_section_match_at_capture", "provenance_kind": "recovered_markdown_section_id", "native_pdf_item": None}
    examples = [{"operation_id": op, "record_id": record, "paper": "OKR-Cell", "source_status": "WITHDRAWN",
                 "scope": "supplemental mechanism example; outside four-record assembly/reuse denominators",
                 "evidence_ids": [eid], "assembly": assembly} for op in {call["operation_id"] for call in calls}]
    (BASE / "supplemental_examples.json").write_bytes(encoded({"examples": sorted(examples, key=lambda x: x["operation_id"]), "evidence": [item]}))


if __name__ == "__main__":
    capture()
