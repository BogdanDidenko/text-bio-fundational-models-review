"""Mechanical coding of every agent route on the design-pattern axes (TAXONOMY_SPEC.md).

Input: analysis/design_taxonomy_2026-10-13/chains.json (scripts/build_chain_table.py).
Output: taxonomy_codebook.csv (one row per route) with the rule that fired and evidence step ids.
  python3 scripts/build_design_taxonomy.py
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "analysis/design_taxonomy_2026-10-13"

OPAQUE = {"learned_module", "fusion_unspecified", "no_catalog_operation", "external_generator", "consensus_tie"}
NEUTRAL = {"source_provenance", "identity"}
ENCODE = {"project", "lookup", "cross_attention", "self_attention", "reshape"}
SUBTYPE_FALLBACK = {  # used only when the chain has no decided operation for the route
    "native_biological_token_stream": "verbatim", "multi_track_structural_symbol_stream": "verbatim",
    "structured_biological_prompt_or_task_scaffold": "verbatim", "serialized_biological_context_or_ordered_profile": "verbatim",
    "plain_language_prompt_or_question": "verbatim", "raw_slide_or_patch_input": "verbatim",
    "patch_context_or_case_level_visual_reasoning": "verbatim", "symbolic_structural_constraint": "verbatim",
    "coordinate_backbone_or_shape_conditioning": "verbatim", "noisy_diffusion_state": "verbatim",
    "direct_projected_embedding": "learned_compression", "connector_mediated_embedding": "learned_compression",
    "pooled_or_aggregated_embedding": "learned_compression", "virtual_token_prefix": "learned_compression",
    "learned_quantized_id_or_codebook_token": "discretised",
}
TEXT_ROLE = {"instruction_or_query": "instruction", "modality_or_task_selector": "instruction",
             "metadata_or_context": "context", "semantic_annotation": "context",
             "biological_payload": "payload", "paired_alignment_supervision": "supervision",
             "generated_output": "supervision", "no_text_on_this_route": "none"}


def ops_of(steps):
    return [(s["step_id"], c["operation_id"]) for s in steps for c in s["calls"]]


def a1(r):
    if r["source_modality"] == "text":
        return "text_source", "source modality is text"
    fam = r["carrier_family"]
    return {"text_native_token_stream": ("verbalised", "non-text source, text-native carrier"),
            "discrete_biological_symbol_stream": ("symbolic", "discrete biological symbol carrier"),
            "dense_continuous_carrier": ("embedded", "dense continuous carrier"),
            "visual_raster_carrier": ("perceptual", "visual raster carrier"),
            "geometric_or_diffusion_state_carrier": ("perceptual", "geometric/diffusion carrier")}[fam]


def a2(r):
    f, fam = r["fusion_topology"], r["carrier_family"]
    if f in ("tokenizer_sequence", "interleaving"):
        return "token_stream", f
    if f == "concatenation":
        if fam in ("text_native_token_stream", "discrete_biological_symbol_stream"):
            return "token_stream", "concatenation of a text/symbol carrier"
        return "embedding_slot", "concatenation of a dense/visual carrier"
    m = {"prefix": "embedding_slot", "placeholder_replacement": "embedding_slot", "cross_attention": "attention_bridge",
         "query_bottleneck": "attention_bridge", "shared_latent_alignment": "latent_alignment",
         "side_or_generative_conditioning": "conditioning", "encoder_decoder": "conditioning",
         "retrieval_or_tool_context": "external_context"}
    return m.get(f, "unresolved"), f


def a3(r, steps):
    if r["source_modality"] == "text":
        return "not_applicable", "text source", [], []
    ops = ops_of(steps)
    names = [o for _, o in ops]
    mods = [m for m, test in (("subset", "select" in names), ("normalised", any(o in names for o in ("normalize", "log_transform")))) if test]
    ev = lambda want: [s for s, o in ops if o in want]  # noqa: E731
    if "rank" in names:
        return "order_only", "rank in chain", ev({"rank"}), mods
    if "bin" in names or r["carrier_subtype"] == "learned_quantized_id_or_codebook_token":
        return "discretised", "bin in chain or quantised code carrier", ev({"bin"}), mods
    if a1(r)[0] in ("verbalised", "symbolic") and any(o in ("serialize", "tokenize") for o in names):
        return "verbatim", "text/symbol carrier formed by serialize/tokenize", ev({"serialize", "tokenize"}), mods
    if any(o in ENCODE for o in names) or any(s["category"] == "learned_module" for s in steps):
        return "learned_compression", "encoder/projection or learned module", ev(ENCODE) or [s["step_id"] for s in steps if s["category"] == "learned_module"], mods
    if any(o in ("serialize", "tokenize") for o in names):
        return "verbatim", "serialize/tokenize without rank, bin or encoder", ev({"serialize", "tokenize"}), mods
    fb = SUBTYPE_FALLBACK.get(r["carrier_subtype"])
    if fb:
        return fb, f"atlas carrier subtype fallback ({r['carrier_subtype']})", [], mods
    return "unresolved", "no decided library operation", [], mods


def a5(steps):
    comp = [s for s in steps if s["category"] not in NEUTRAL]
    if not comp:
        return "no_computation", 0.0, None
    opaque = sum(s["category"] in OPAQUE for s in comp) / len(comp)
    slots = [v for s in steps for c in s["calls"] for v in c["parameter_status"].values()]
    stated = sum(v == "stated" for v in slots) / len(slots) if slots else None
    if not any(s["category"] == "library_operation" for s in comp):
        cls = "opaque"
    elif opaque == 0 and stated is not None and stated >= 2 / 3:
        cls = "transparent"
    else:
        cls = "partial"
    return cls, round(opaque, 3), None if stated is None else round(stated, 3)


def code(r, steps=None):
    steps = steps if steps is not None else r["steps"]
    v1, w1 = a1(r)
    v2, w2 = a2(r)
    v3, w3, e3, mods = a3(r, steps)
    v5, opq, stated = a5(steps)
    return {"A1_carrier_formation": v1, "A1_rule": w1, "A2_interface": v2, "A2_rule": w2,
            "A3_information": v3, "A3_rule": w3, "A3_modifiers": "+".join(mods), "A3_evidence_steps": " ".join(e3),
            "A4_text_role": TEXT_ROLE.get(r["text_role"], "unresolved"), "A5_transparency": v5,
            "opaque_step_share": opq, "stated_parameter_share": stated}


def main():
    rows = json.loads((D / "chains.json").read_text())
    out = []
    for r in rows:
        out.append({k: r[k] for k in ("record_id", "model_id", "model_name", "configuration_id", "route_id", "route_label",
                                      "lifecycle_phase", "source_modality", "carrier_family", "carrier_subtype",
                                      "fusion_topology", "text_role")}
                   | {"operation_chain": " | ".join("+".join(c["operation_id"] for c in s["calls"]) or s["category"] for s in r["steps"])}
                   | code(r))
    with open(D / "taxonomy_codebook.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(json.dumps({"routes": len(out)}))


if __name__ == "__main__":
    main()
