"""Protocol v2 for operation decomposition: structure anchored to the reviewed atlas routes.

v1 let the agent choose how to split a paper into trajectories and steps, which made run-to-run
results unstable (replicates/agreement.json). v2 fixes the structure from the atlas: exactly one
trajectory per atlas configuration and, for each atlas route, exactly one step per element of the
route's verbatim transformation chain, in order, with fixed IDs. The agent's remaining choice is the
operation decomposition of each step, guided by an explicit decision table. The full paper text is
still supplied in full.
"""

import json

from scripts.operation_decomposition import (
    ATLAS, PHASES, ROLES, _evidence_schema, _obj, _string_or_null, _strings_or_null, validate_document,
)

PROTOCOL = "operation-decomposition-v2"


def atlas_skeleton(record_id, atlas=None):
    atlas = atlas or json.loads(ATLAS.read_text())
    configs = {}
    for model in (m for m in atlas["architectures"] if m["record_id"] == record_id):
        for route in model["routes"]:
            cfg = configs.setdefault(route["configuration_id"], {
                "configuration_id": route["configuration_id"], "model_name": model["model_name"],
                "lifecycle_phase": route["lifecycle_phase"],
                "task_or_configuration_verbatim": route["task_or_configuration_verbatim"], "routes": []})
            chain = list(route["transformation_chain_verbatim"] or [])
            recorded = bool(chain)
            if not recorded:  # atlas recorded source -> model-visible form only: one fixed direct step
                chain = [f"(no chain recorded) {route['source_object_verbatim']} -> {route['model_visible_form_verbatim']}"]
            cfg["routes"].append({
                "route_id": route["route_id"], "route_label": route["route_label"],
                "source_object_verbatim": route["source_object_verbatim"],
                "transformation_chain_verbatim": chain, "chain_recorded": recorded,
                "model_visible_form_verbatim": route["model_visible_form_verbatim"],
                "insertion_or_fusion_verbatim": route["insertion_or_fusion_verbatim"],
                "fusion_topology": route["fusion_topology"], "text_role": route["text_role"],
                "evidence_quote": route["evidence_quote"], "section_heading": route["section_heading"],
                "expected_step_ids": [f"{route['route_id']}__s{k:02d}" for k in range(1, len(chain) + 1)]})
    for cfg in configs.values():
        cfg["routes"].sort(key=lambda r: r["route_id"])
    return [configs[k] for k in sorted(configs)]


def extraction_schema_v2(catalog, skeleton):
    ev = {"type": "array", "items": _evidence_schema()}
    node = _obj({"node_id": {"type": "string"}, "representation_type": {"type": "string"},
                 "symbolic_shape": _strings_or_null(), "axis_semantics": _strings_or_null(),
                 "information_content": {"type": "string"}, "contextual_role": {"type": "string"},
                 "evidence": ev, "uncertainty": _string_or_null()})
    intermediate = _obj({**node["properties"], "origin": {"type": "string", "enum": ["documented_intermediate", "implicit_parameter"]}})
    binding = _obj({"port": {"type": "string"}, "node_ids": {"type": "array", "items": {"type": "string"}}})
    operand = _obj({"node_id": {"type": "string"}, "port_role": {"type": "string"}})
    op_ids = [b["operation_id"] for b in catalog["blocks"]]
    call = _obj({"operation_id": {"type": ["string", "null"], "enum": op_ids + [None]},
                 "inputs": {"type": "array", "items": binding}, "outputs": {"type": "array", "items": binding},
                 "parameters": {"type": "array", "items": _obj({"name": {"type": "string"}, "value": {"type": "string"}})},
                 "condition": _string_or_null(), "uncertainty": _string_or_null()})
    bypass = _obj({"source_node_id": {"type": "string"}, "target_node_id": {"type": "string"}, "condition": {"type": "string"}})
    step_ids = [s for cfg in skeleton for r in cfg["routes"] for s in r["expected_step_ids"]]
    route_ids = [r["route_id"] for cfg in skeleton for r in cfg["routes"]]
    step = _obj({"step_id": {"type": "string", "enum": step_ids}, "route_id": {"type": "string", "enum": route_ids},
                 "chain_element": {"type": "string"}, "component": {"type": "string"}, "operation_type": {"type": "string"},
                 "inputs": {"type": "array", "items": operand}, "outputs": {"type": "array", "items": {"type": "string"}},
                 "evidence": ev, "uncertainty": _string_or_null(),
                 "intermediate_nodes": {"type": "array", "items": intermediate},
                 "decomposition": {"type": "array", "items": call},
                 "bypasses": {"type": "array", "items": bypass}})
    trajectory = _obj({"trajectory_id": {"type": "string", "enum": [c["configuration_id"] for c in skeleton]},
                       "model_variant": {"type": "string"}, "task_configuration": {"type": "string"},
                       "lifecycle_phase": {"type": "string", "enum": PHASES},
                       "model_role": {"type": "string", "enum": ROLES}, "recipient_component": {"type": "string"},
                       "nodes": {"type": "array", "items": node}, "steps": {"type": "array", "items": step},
                       "receipt_inputs": {"type": "array", "items": operand}, "evidence": ev,
                       "open_questions": {"type": "array", "items": {"type": "string"}}})
    proposal = _obj({"source_operation": {"type": "string"}, "why_no_existing_operation": {"type": "string"},
                     "compared_operation_ids": {"type": "array", "items": {"type": "string"}}})
    return _obj({"record_id": {"type": "string"}, "trajectories": {"type": "array", "items": trajectory},
                 "coverage_questions": {"type": "array", "items": {"type": "string"}},
                 "operation_proposals": {"type": "array", "items": proposal}})


RULES_V2 = """Output contract v2 (enforced mechanically; violations are returned to you):

STRUCTURE IS FIXED BY THE ATLAS SKELETON BELOW. Do not add, drop, merge or split trajectories or steps.
- Return exactly one trajectory per atlas configuration; trajectory_id = configuration_id.
- In that trajectory, for EVERY route of the configuration, return exactly one step per element of the
  route's transformation_chain_verbatim, in chain order, using the given expected_step_ids
  (<route_id>__s01, __s02, ...). Set route_id to the route and chain_element to the chain element text
  copied exactly.
- A route with chain_recorded false has one fixed step from its source object to its model-visible
  form; decide its operation(s) from the paper text with the same table.
- Data flow: the route's source object is a node; step 1 consumes it; step k consumes step k-1's
  output (plus any parameter table or side input the paper states for that element); the last step's
  output is the route's model-visible form and appears in receipt_inputs. Several routes of one
  configuration may share the source node only when their source_object_verbatim is identical.
- Evidence quotes are copied VERBATIM from the cited section of the paper text. Every node, step and
  trajectory needs evidence. The atlas route evidence_quote may be reused when it is literally in the
  cited section.

OPERATION DECISION TABLE (apply per step, in this order; the first matching row decides):
1. The chain element is the receiving model itself, or a named learned module (encoder, decoder,
   transformer, backbone, LLM, foundation model, Q-Former, ViT, GNN ...) whose internal computation the
   paper does not state step by step  -> ONE call with operation_id null (unexpanded boundary).
2. The paper states, for this element, several operations and their order -> one call per stated
   operation, in that order, with intermediate_nodes between them.
3. Otherwise ONE call chosen by the computation the element performs:
   tokenizer, tokenization, k-mer, BPE, split text into tokens .................. tokenize
   embedding layer, token/gene/value embedding, vocabulary or index mapping, look up . lookup
   linear layer, projection, projector, adapter, connector, MLP, mapped into the
     language model's embedding space ............................................ project
   prompt, template, instruction format, cell sentence, converting values to text .. serialize
   rank or order by value ......................................................... rank
   top-k, filter, highly variable genes, subset, choose ............................ select
   normalisation (library size, TPM, CP10K, z-score, LayerNorm) .................... normalize
   log / log1p .................................................................... log_transform
   bin, discretise, quantise into intervals ........................................ bin
   concatenate, append, prepend, interleave into one sequence ..................... concatenate
   sum, add element-wise .......................................................... add
   cross-attention / self-attention stated as the operation ....................... cross_attention / self_attention
   split, patchify, tile, crop into patches ....................................... partition
   pad ............................................................................ pad
   sample, draw, noise ............................................................ sample
   augment ........................................................................ augment
   align, register, match coordinates ............................................. align
   reshape, flatten, expand, broadcast ............................................ reshape
   impute, fill missing ........................................................... impute
   clamp, clip .................................................................... clamp
   indexed overwrite / replace values at positions ................................ update
   none of the above .............................................................. operation_id null
- Ports: use the catalog port names exactly. Every catalog-declared parameter must be present: give the
  value the paper states, otherwise exactly "unspecified". Never infer a value from convention.
- A computation that no catalog operation represents is operation_id null and is listed in
  operation_proposals with the compared operation_ids.
"""


def validate_v2(doc, record_id, sections, catalog, library_sha256, release, skeleton):
    errors = []
    by_cfg = {c["configuration_id"]: c for c in skeleton}
    got = [t["trajectory_id"] for t in doc.get("trajectories", [])]
    missing, extra = sorted(set(by_cfg) - set(got)), sorted(set(got) - set(by_cfg))
    dup = sorted({t for t in got if got.count(t) > 1})
    if missing:
        errors.append(f"missing trajectories for configurations {missing}")
    if extra:
        errors.append(f"trajectories not in the atlas skeleton {extra}")
    if dup:
        errors.append(f"configurations returned more than once {dup}")
    for t in doc.get("trajectories", []):
        cfg = by_cfg.get(t["trajectory_id"])
        if not cfg:
            continue
        steps = {}
        for s in t["steps"]:
            steps.setdefault(s["route_id"], []).append(s)
        for route in cfg["routes"]:
            want = route["expected_step_ids"]
            have = [s["step_id"] for s in steps.get(route["route_id"], [])]
            if have != want:
                errors.append(f"{t['trajectory_id']} / route {route['route_id']}: steps must be exactly {want} in "
                              f"this order; got {have}")
                continue
            for s, element in zip(steps[route["route_id"]], route["transformation_chain_verbatim"]):
                if s["chain_element"] != element:
                    errors.append(f"{t['trajectory_id']} / {s['step_id']}: chain_element must be exactly {element!r}")
                if not s["step_id"].startswith(s["route_id"] + "__"):
                    errors.append(f"{t['trajectory_id']} / {s['step_id']}: route_id does not match the step")
        foreign = sorted(set(steps) - {r["route_id"] for r in cfg["routes"]})
        if foreign:
            errors.append(f"{t['trajectory_id']}: steps belong to routes of another configuration {foreign}")
    base_errors, warnings, assemblies = validate_document(doc, record_id, sections, catalog, library_sha256, release)
    errors += base_errors
    return errors, warnings, (assemblies if not errors else [])


def route_signatures(doc):
    """Ordered operation sequence per route (boundary = '<boundary>'), for agreement measurement."""
    out = {}
    for t in doc.get("trajectories", []):
        steps = sorted(t["steps"], key=lambda s: s["step_id"])
        for s in steps:
            ops = [c["operation_id"] or "<boundary>" for c in s["decomposition"]] or ["<boundary>"]
            out.setdefault(s["route_id"], []).extend(ops + ["|"])
    return {r: tuple(v) for r, v in out.items()}
