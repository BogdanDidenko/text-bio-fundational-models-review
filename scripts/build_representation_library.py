"""Build an operation constructor from complete preserved source annotations."""

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.docling_graph_templates.representation_library import (
    OperationAssembly, OperationCatalog, restore_source, validate_operation_ports,
)

BASE = ROOT / "analysis/representation_block_library_2026-10-04"
PUBLIC = ROOT / "docs/input-representation-atlas/component-library/data"
PACKETS = ROOT / "analysis/nickerson_taxonomy_2026-09-20/object_unit_reassessment_2026-09-22/section_id_corpus_55_2026-10-04/records"


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def quote_key(record, evidence):
    return digest(encoded([record, evidence["section_id"], evidence["quote"], evidence["kind"]]))


# These exact labels identify already reviewed source operations. Parameters retain
# specialization; module names, biological sources and widths do not create types.
DIRECT = {
    "tpm_normalization": ("normalize", {"method": "TPM", "scope": "source-defined expression axes"}),
    "log_one_plus_normalization": ("log_transform", {"method": "log1p"}),
    "english_tokenization": ("tokenize", {"source_alphabet": "text", "segmentation": "source tokenizer"}),
    "nucleotide_tokenization": ("tokenize", {"source_alphabet": "nucleotide", "segmentation": "source tokenizer"}),
    "feature_projection": ("project", {"method": "source-defined learned projection"}),
    "linear_projection": ("project", {"method": "linear"}),
    "gene_filtering": ("select", {"criterion": "source-defined gene filter"}),
    "protein_coding_filter_and_shared_gene_selection": ("select", {"criterion": "protein-coding and shared gene selection; aligned sources"}),
    "rank_threshold_new_position_selection": ("select", {"criterion": "rank threshold and previously unrevealed positions"}),
    "marker_channel_grouping": ("partition", {"method": "channel grouping"}),
    "spatial_image_tiling": ("partition", {"method": "spatial tiling"}),
    "separate_cls_and_gene_positions": ("partition", {"method": "CLS/gene position split"}),
    "sequence_concatenation": ("concatenate", {"axis": "sequence position", "order": "source-defined"}),
    "multimodal_embedding_concatenation": ("concatenate", {"axis": "unspecified", "order": "source-defined modality order"}),
    "spatial_latent_concatenation": ("concatenate", {"axis": "unspecified", "order": "structural latent and current noisy state"}),
    "token_padding": ("pad", {"target_length": "n_target_tokens", "value": "source padding token"}),
    "template_conditioned_prompt_serialization": ("serialize", {"template": "source prompt template"}),
    "additive_modality_fusion": ("add", {"alignment": "documented modality contributions"}),
    "spatial_expression_alignment": ("align", {"basis": "spatial correspondence"}),
    "histology_color_augmentation": ("augment", {"policy": "histology color augmentation"}),
}
LOOKUPS = {"embedding_lookup", "token_embedding", "gene_identifier_to_vocabulary_index",
           "ensembl_to_hgnc_reference_mapping", "gene_keyed_reference_lookup", "read_shared_gene_output_parameters"}


def decompose(row, library_hash, release):
    t = row["trajectory"]
    result = {key: t[key] for key in ("trajectory_id", "model_variant", "task_configuration", "lifecycle_phase",
                                     "model_role", "recipient_component", "receipt_inputs", "evidence", "open_questions")}
    result.update(contract_version="operation-assembly-v1", record_id=row["record_id"], library_release=release,
                  library_sha256=library_hash, nodes=[{**node, "origin": "source_annotation"} for node in t["nodes"]],
                  calls=[], bypasses=[], source_steps=t["steps"])
    for step in t["steps"]:
        label = step["operation_type"]
        refs = [item["node_id"] for item in step["inputs"]]
        out = step["outputs"]
        ordinal = 0

        def node(suffix, origin="documented_intermediate", content=None):
            nid = step["step_id"] + "::" + suffix
            result["nodes"].append({"node_id": nid, "representation_type": suffix, "symbolic_shape": None,
                "axis_semantics": None, "information_content": content or f"Documented intermediate after {suffix}",
                "contextual_role": "model_parameter" if origin == "implicit_parameter" else "intermediate_representation",
                "evidence": step["evidence"], "uncertainty": "Exact internal shape and axes are unspecified at this reconstructed boundary.",
                "origin": origin})
            return nid

        def call(op, inputs, outputs, params=None, condition=None, note=None):
            nonlocal ordinal
            ordinal += 1
            result["calls"].append({"call_id": step["step_id"] + "::" + str(ordinal), "operation_id": op,
                "component": step["component"], "inputs": inputs, "outputs": outputs,
                "parameters": {**(params or {}), "source_port_roles": [item["port_role"] for item in step["inputs"]]},
                "condition": condition, "source_step_id": step["step_id"], "evidence": step["evidence"],
                "uncertainty": note or step["uncertainty"],
                "status": "documented_operation" if op else "unexpanded_source_boundary"})

        def lookup(output):
            if label == "gene_keyed_reference_lookup":
                table, keys = refs[0], refs[1:]
                kind = "precomputed reference"
            elif label in {"ensembl_to_hgnc_reference_mapping", "read_shared_gene_output_parameters"}:
                keys, table = refs[:1], refs[1]
                kind = "identifier reference" if label.startswith("ensembl") else "shared embedding matrix"
            else:
                keys = refs
                kind = "vocabulary mapping" if label == "gene_identifier_to_vocabulary_index" else "embedding matrix"
                table = node("lookup_table", "implicit_parameter", f"{kind} belonging to {step['component']}; values and sharing are unasserted")
            call("lookup", {"keys": keys, "table": [table]}, {"values": output},
                 {"resource_kind": kind, "trainability": "unspecified at this component/phase boundary"})

        if label in DIRECT:
            op, params = DIRECT[label]
            call(op, {"values": refs}, {"values": out}, params)
        elif label in LOOKUPS:
            lookup(out)
        elif label == "embedding_lookup_layer_norm":
            intermediate = node("looked_up_vectors")
            lookup([intermediate])
            call("normalize", {"values": [intermediate]}, {"values": out}, {"method": "LayerNorm", "axes": "source-defined feature axes"})
        elif label in {"relu_mlp_layer_norm_encoding", "leaky_relu_mlp_layer_norm_projection"}:
            intermediate = node("projected_values")
            call("project", {"values": refs}, {"values": [intermediate]},
                 {"method": "MLP", "activation": "ReLU" if label.startswith("relu_") else "LeakyReLU"})
            call("normalize", {"values": [intermediate]}, {"values": out}, {"method": "LayerNorm"})
        elif label == "dataset_aware_expression_normalization":
            intermediate = node("scaled_expression")
            condition = "input dataset contains raw counts requiring preprocessing"
            call("normalize", {"values": refs}, {"values": [intermediate]}, {"method": "CP10K"}, condition)
            call("log_transform", {"values": [intermediate]}, {"values": out}, {"method": "log1p"}, condition)
            result["bypasses"].append({"source_node_id": refs[0], "target_node_id": out[0],
                "condition": "input dataset is already normalized; both preprocessing operations are bypassed", "source_step_id": step["step_id"]})
        elif label == "optional_normalization_and_missing_value_imputation":
            intermediate = node("optionally_normalized_reference")
            call("normalize", {"values": refs[:1]}, {"values": [intermediate]}, {"method": "LayerNorm"},
                 "source lookup is present and optional LayerNorm is enabled")
            result["bypasses"].append({"source_node_id": refs[0], "target_node_id": intermediate,
                "condition": "optional LayerNorm is disabled or source lookup is unavailable", "source_step_id": step["step_id"]})
            call("impute", {"values": [intermediate], "availability_context": refs[1:]},
                 {"values": out[:1], "missingness": out[1:]}, {"replacement": "zero", "availability_source": "source lookup presence"})
        elif label == "mlp_encoding_and_slot_split":
            intermediate = node("mlp_output")
            call("project", {"values": refs}, {"values": [intermediate]}, {"method": "residual MLP"})
            call("partition", {"values": [intermediate]}, {"values": out}, {"method": "latent feature slot split"})
        elif label == "prepend_learned_cls_and_flatten_cell_batch":
            call("concatenate", {"values": [refs[1], refs[0]]}, {"values": out},
                 {"axis": "sequence position", "order": "CLS then gene positions",
                  "unexpanded_layout": "source also documents batch/cell reshaping; its placement relative to this boundary remains unexpanded"})
        elif label == "expand_cls_and_concatenate_gene_features":
            intermediate = node("expanded_cell_summary")
            call("reshape", {"values": refs[1:2]}, {"values": [intermediate]},
                 {"method": "expand cell summary across gene positions"})
            call("concatenate", {"values": [refs[0], intermediate]}, {"values": out},
                 {"axis": "feature coordinate", "order": "gene feature then expanded cell summary"})
        elif label == "descending_expression_gene_selection_and_serialization":
            ranked = node("ranked_gene_identifiers")
            selected = node("selected_ranked_gene_identifiers")
            call("rank", {"values": refs[:1], "identifiers": refs[1:]}, {"values": [ranked]},
                 {"order": "descending expression", "tie_handling": "unspecified"})
            call("select", {"values": [ranked]}, {"values": [selected]}, {"criterion": "top-ranked expressed genes; source top-K"})
            call("serialize", {"values": [selected]}, {"values": out}, {"template": "ordered gene-name sentence"})
        elif label == "query_self_attention_and_cross_attention_stack":
            intermediate = node("self_attended_queries")
            call("self_attention", {"values": refs[:1]}, {"values": [intermediate]}, {"repeat_schedule": "within each documented repeated transformer block"})
            call("cross_attention", {"queries": [intermediate], "key_values": refs[1:2]}, {"values": out},
                 {"method": "query-to-source attention", "repeat_schedule": "motif repeated within the documented stack"})
        elif label in {"cross_attention_resampling", "cross_attention_with_asymmetric_ports"}:
            arguments = {"queries": refs[:1], "key_values": refs[1:2]}
            if refs[2:]:
                arguments["mask"] = refs[2:]
            call("cross_attention", arguments, {"values": out}, {"method": "source-defined attention/resampling"})
        elif label in {"prior_sampling", "reparameterized_sampling", "temperature_token_sampling"}:
            arguments = {"distribution": refs[:1]}
            if len(refs) > 1:
                arguments["noise" if label == "reparameterized_sampling" else "context"] = refs[1:]
            call("sample", arguments, {"values": out}, {"method": label})
        elif label == "clamp_nonnegative_and_select_new_predictions":
            intermediate = node("nonnegative_predictions")
            call("clamp", {"values": refs[:1]}, {"values": [intermediate]}, {"lower": "zero"})
            call("select", {"values": [intermediate], "selectors": refs[1:]}, {"values": out}, {"criterion": "newly accepted gene positions"})
        elif label in {"replace_control_values_with_ground_truth", "scatter_new_values_preserve_previous_state_and_update_mask"}:
            if label == "replace_control_values_with_ground_truth":
                args = {"state": refs[:1], "replacements": refs[1:2], "indices": refs[2:3], "context": refs[3:]}
            else:
                # Historical operands explicitly name prior state, old mask, new positions and accepted values.
                roles = {item["port_role"]: item["node_id"] for item in step["inputs"]}
                args = {"state": [], "replacements": [], "indices": [], "context": []}
                for role, ref in roles.items():
                    destination = "replacements" if "new clamped predictions" in role else "indices" if "new accepted positions" in role else "state"
                    args[destination].append(ref)
            call("update", args, {"values": out}, {"method": "indexed replacement", "preserve_unselected": True})
        else:
            call(None, {"source_operands": refs}, {"source_results": out},
                 {"source_operation": label}, note=step["uncertainty"] or "Documented module boundary retained; internal primitive decomposition needs source review.")
    OperationAssembly.model_validate(result)
    if restore_source(result) != t:
        raise ValueError("Source trajectory changed during operation decomposition")
    return result


def compile_release(base):
    catalog = OperationCatalog.model_validate_json((base / "operation_catalog.json").read_text()).model_dump()
    library_hash = digest(encoded(catalog))
    rows = [json.loads(line) for line in (base / "pilot_input.jsonl").read_text().splitlines() if line.strip()]
    snapshot = json.loads((base / "evidence_snapshot.json").read_text())
    evidence = {item["evidence_id"]: item for item in snapshot["evidence"]}
    assemblies = [decompose(row, library_hash, catalog["release"]) for row in rows]
    usage = defaultdict(list)
    pending = defaultdict(list)
    examples = []
    for assembly in assemblies:
        validate_operation_ports(assembly, catalog)
        for call in assembly["calls"]:
            occurrence = {"record_id": assembly["record_id"], "trajectory_id": assembly["trajectory_id"],
                "call_id": call["call_id"], "source_step_id": call["source_step_id"],
                "parameters": call["parameters"], "condition": call["condition"], "component": call["component"],
                "inputs": call["inputs"], "outputs": call["outputs"],
                "evidence_ids": list(dict.fromkeys(quote_key(assembly["record_id"], item) for item in call["evidence"]))}
            if any(ref not in evidence for ref in occurrence["evidence_ids"]):
                raise ValueError("Missing captured evidence")
            if call["operation_id"]:
                usage[call["operation_id"]].append(occurrence)
            else:
                pending[call["parameters"]["source_operation"]].append(occurrence)
    supplement = base / "supplemental_examples.json"
    if supplement.exists():
        extra = json.loads(supplement.read_text())
        for item in extra["evidence"]:
            evidence[item["evidence_id"]] = item
        examples = extra["examples"]
        for example in examples:
            example["assembly"]["library_release"] = catalog["release"]
            example["assembly"]["library_sha256"] = library_hash
            OperationAssembly.model_validate(example["assembly"])
            validate_operation_ports(example["assembly"], catalog)
            if any(ref not in evidence for ref in example["evidence_ids"]):
                raise ValueError("Missing supplemental source evidence")
    public_blocks = []
    for block in catalog["blocks"]:
        actual = usage[block["operation_id"]]
        supplementary = [item for item in examples if item["operation_id"] == block["operation_id"]]
        public_blocks.append({**block, "usage": actual, "supplemental_examples": supplementary,
            "reuse_record_ids": sorted({item["record_id"] for item in actual}),
            "status": "source_backed" if actual or supplementary else "definition_only"})
    unresolved = [{"source_operation": label, "occurrences": uses, "status": "unexpanded_source_boundary"}
                  for label, uses in sorted(pending.items())]
    reused = [block for block in public_blocks if len(block["reuse_record_ids"]) > 1]
    report = {"status": "operation_constructor_pilot", "release": catalog["release"],
        "record_count": len(snapshot["records"]), "trajectory_count": len(assemblies),
        "operation_types": len(public_blocks), "cross_paper_reused_types": len(reused),
        "primitive_calls": sum(len(item["usage"]) for item in public_blocks),
        "unexpanded_source_steps": sum(len(item["occurrences"]) for item in unresolved),
        "unexpanded_source_labels": len(unresolved), "lossless_source_restoration": True,
        "library_sha256": library_hash, "source_sizes_modified": False, "canonical_migration": False,
        "pilot_input_sha256": digest((base / "pilot_input.jsonl").read_bytes()),
        "evidence_snapshot_sha256": digest((base / "evidence_snapshot.json").read_bytes())}
    return {"catalog.json": {**catalog, "library_sha256": library_hash, "blocks": public_blocks,
                "records": snapshot["records"], "pending": unresolved, "report": report},
            "assemblies.json": assemblies, "evidence.json": list(evidence.values()),
            "validation.json": report, "assembly.schema.json": OperationAssembly.model_json_schema(),
            "catalog-seed.schema.json": OperationCatalog.model_json_schema(), "supplemental-examples.json": examples}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--public", type=Path, default=PUBLIC)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    outputs = compile_release(args.base)
    frozen = args.base / "releases" / outputs["catalog.json"]["release"]
    if (frozen / "freeze.json").exists():
        lock = json.loads((frozen / "freeze.json").read_text())
        if any(digest(encoded(payload)) != lock["artifacts"].get(name) for name, payload in outputs.items()):
            raise SystemExit("Frozen operation release changed; create a reviewed new version")
    for name, payload in outputs.items():
        for target in (args.public / name, args.base / "release" / name):
            data = encoded(payload)
            if args.check:
                if not target.exists() or target.read_bytes() != data:
                    raise SystemExit(f"Stale or absent projection: {target}")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
    if args.freeze:
        if args.check:
            raise SystemExit("Check is read-only")
        frozen.mkdir(parents=True, exist_ok=True)
        for name, payload in outputs.items():
            (frozen / name).write_bytes(encoded(payload))
        (frozen / "freeze.json").write_bytes(encoded({"release": outputs["catalog.json"]["release"],
            "artifacts": {name: digest(encoded(payload)) for name, payload in outputs.items()}}))
    print(json.dumps(outputs["validation.json"], indent=2))


if __name__ == "__main__":
    main()
