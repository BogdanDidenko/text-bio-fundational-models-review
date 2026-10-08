"""Corpus-wide operation decomposition: packets, agent contract, compiler and validator.

Agents (native `codex exec`, see run_operation_decomposition.py) return a strict-schema
document. This module turns it into `OperationAssembly` objects with the same contract,
evidence identity and lossless source restoration as the frozen four-paper pilot.
Nothing here calls a model.
"""

import hashlib
import json
import re
from pathlib import Path

from scripts.docling_graph_templates.representation_library import (
    OperationAssembly, restore_source, validate_operation_ports,
)
from scripts.docling_graph_templates.symbolic_trajectories import Trajectory

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "analysis/representation_block_library_2026-10-04/operation_catalog.json"
ATLAS = ROOT / "docs/input-representation-atlas/data/atlas.json"
PILOT_RECORDS = {"full_2026-07-06__rec_000771", "full_2026-07-06__rec_001319",
                 "full_2026-07-06__rec_003517", "full_2026-07-06__rec_003852"}
SOURCE_DIRS = [
    ROOT / "data/docling_include_vlm_52_2026-07-10_nolimits/markdown",
    ROOT / "data/living_catalog_updates/update_2026-08-09/11_docling_vlm/profiles/markdown",
    ROOT / "data/living_catalog_updates/update_2026-08-09/11_docling_vlm_manual_recall_xunzi_2026-08-11/profiles/markdown",
]
HEADING = re.compile(r"^#{1,6}\s")
EVIDENCE_KINDS = ["paper_text", "table", "caption", "equation_context", "vlm_description"]
PHASES = ["pretraining", "training", "fine_tuning", "test_time_adaptation", "inference", "evaluation", "unspecified"]
ROLES = ["primary_model", "auxiliary_component", "baseline", "ablation", "unresolved"]


def sha(text):
    return hashlib.sha256(text.encode() if isinstance(text, str) else text).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


# ---------------------------------------------------------------- packets

def split_sections(raw):
    """Recovered section scheme of the pilot packets (verified on all 89 pilot evidence items).

    A section runs from one level-1..6 Markdown heading line up to the next heading of any
    level; its text is those lines joined by newlines plus one trailing newline. IDs number
    headings from sec_0001 in document order; heading paths follow heading levels.
    """
    lines = raw.split("\n")
    heads = [i for i, line in enumerate(lines) if HEADING.match(line)]
    stack, sections = [], []
    for k, start in enumerate(heads):
        end = heads[k + 1] if k + 1 < len(heads) else len(lines)
        level = len(lines[start]) - len(lines[start].lstrip("#"))
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, lines[start].lstrip("#").strip()))
        text = "\n".join(lines[start:end]) + "\n"
        sections.append({"section_id": f"sec_{k + 1:04d}", "heading_path": [t for _, t in stack],
                         "heading_level": level, "text": text, "text_sha256": sha(text)})
    return sections


def source_path(record_id):
    batch, rid = record_id.split("__")
    stem = batch.replace("-", "_") + "_" + rid
    for folder in SOURCE_DIRS:
        hits = sorted(p for p in folder.glob(f"{stem}*.md") if p.name == f"{stem}.md" or p.name.startswith(stem + "_"))
        if hits:
            return hits[0]
    raise FileNotFoundError(f"No canonical full-text Markdown for {record_id}")


def build_packet(record_id):
    path = source_path(record_id)
    raw = path.read_text(encoding="utf-8")
    sections = split_sections(raw)
    manifest = {"record_id": record_id, "source_path": str(path.relative_to(ROOT)), "source_sha256": sha(raw),
                "sections": [{k: v for k, v in s.items() if k != "text"} for s in sections]}
    manifest["packet_sha256"] = sha(encoded(manifest))
    return manifest, {s["section_id"]: s for s in sections}


def atlas_seed(record_id, atlas=None):
    atlas = atlas or json.loads(ATLAS.read_text())
    models = [m for m in atlas["architectures"] if m["record_id"] == record_id]
    if not models:
        raise KeyError(record_id)
    keep = ("model_name", "configuration_count", "route_count", "modalities", "lifecycle_phases",
            "fusion_topologies", "text_roles", "subtypes")
    return {"record_id": record_id, "paper_title": models[0]["paper_title"], "doi": models[0].get("doi"),
            "models": [{**{k: m.get(k) for k in keep},
                        "atlas_examples": [{k: ex.get(k) for k in ("actual_source", "actual_model_visible_form", "example_interface")}
                                           for ex in m.get("illustrative_examples") or []]} for m in models]}


# ---------------------------------------------------------------- agent contract

def _evidence_schema():
    return {"type": "object", "additionalProperties": False, "required": ["section_id", "quote", "kind"],
            "properties": {"section_id": {"type": "string"}, "quote": {"type": "string"},
                           "kind": {"type": "string", "enum": EVIDENCE_KINDS}}}


def _string_or_null():
    return {"type": ["string", "null"]}


def _strings_or_null():
    return {"anyOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}]}


def _obj(props, required=None):
    return {"type": "object", "additionalProperties": False, "required": required or list(props), "properties": props}


def extraction_schema(catalog):
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
    step = _obj({"step_id": {"type": "string"}, "component": {"type": "string"}, "operation_type": {"type": "string"},
                 "inputs": {"type": "array", "items": operand}, "outputs": {"type": "array", "items": {"type": "string"}},
                 "evidence": ev, "uncertainty": _string_or_null(),
                 "intermediate_nodes": {"type": "array", "items": intermediate},
                 "decomposition": {"type": "array", "items": call},
                 "bypasses": {"type": "array", "items": bypass}})
    trajectory = _obj({"trajectory_id": {"type": "string"}, "model_variant": {"type": "string"},
                       "task_configuration": {"type": "string"}, "lifecycle_phase": {"type": "string", "enum": PHASES},
                       "model_role": {"type": "string", "enum": ROLES}, "recipient_component": {"type": "string"},
                       "nodes": {"type": "array", "items": node}, "steps": {"type": "array", "items": step},
                       "receipt_inputs": {"type": "array", "items": operand}, "evidence": ev,
                       "open_questions": {"type": "array", "items": {"type": "string"}}})
    proposal = _obj({"source_operation": {"type": "string"}, "why_no_existing_operation": {"type": "string"},
                     "compared_operation_ids": {"type": "array", "items": {"type": "string"}}})
    return _obj({"record_id": {"type": "string"}, "trajectories": {"type": "array", "items": trajectory},
                 "coverage_questions": {"type": "array", "items": {"type": "string"}},
                 "operation_proposals": {"type": "array", "items": proposal}})


ISSUES = ["unsupported_by_quote", "wrong_operation", "wrong_port_binding", "missing_or_wrong_parameter",
          "invented_algebra_or_order", "missing_step_or_branch", "missing_model_or_context", "wrong_phase_or_role", "other"]


def review_schema():
    finding = _obj({"trajectory_id": {"type": "string"}, "step_id": _string_or_null(),
                    "issue_type": {"type": "string", "enum": ISSUES}, "severity": {"type": "string", "enum": ["blocking", "minor"]},
                    "detail": {"type": "string"}, "required_change": {"type": "string"},
                    "evidence": {"type": "array", "items": _evidence_schema()}})
    return _obj({"record_id": {"type": "string"}, "verdict": {"type": "string", "enum": ["accept", "revise"]},
                 "findings": {"type": "array", "items": finding}, "coverage_summary": {"type": "string"}})


# ---------------------------------------------------------------- compiler

def quote_key(record, evidence):
    return sha(encoded([record, evidence["section_id"], evidence["quote"], evidence["kind"]]))


def _bindings(items):
    out = {}
    for item in items:
        out.setdefault(item["port"], []).extend(item["node_ids"])
    return out


def compile_document(doc, catalog, library_sha256, release):
    """Agent document -> (assemblies, source trajectories). Raises ValueError on contract errors."""
    assemblies, sources = [], []
    for t in doc["trajectories"]:
        source = {k: t[k] for k in ("trajectory_id", "model_variant", "task_configuration", "lifecycle_phase",
                                    "model_role", "recipient_component", "nodes", "receipt_inputs", "evidence", "open_questions")}
        source["steps"] = [{k: s[k] for k in ("step_id", "component", "operation_type", "inputs", "outputs", "evidence", "uncertainty")}
                           for s in t["steps"]]
        Trajectory.model_validate(source)
        nodes = [{**n, "origin": "source_annotation"} for n in t["nodes"]]
        calls, bypasses = [], []
        for s in t["steps"]:
            for n in s["intermediate_nodes"]:
                nodes.append({**n, "node_id": n["node_id"]})
            decomposition = s["decomposition"] or [{"operation_id": None, "inputs": [], "outputs": [], "parameters": [],
                                                    "condition": None, "uncertainty": None}]
            for ordinal, c in enumerate(decomposition, 1):
                params = {p["name"]: p["value"] for p in c["parameters"]}
                if c["operation_id"] is None:
                    inputs = {"source_operands": [i["node_id"] for i in s["inputs"]]}
                    outputs = {"source_results": list(s["outputs"])}
                    params = {**params, "source_operation": s["operation_type"]}
                else:
                    inputs, outputs = _bindings(c["inputs"]), _bindings(c["outputs"])
                params["source_port_roles"] = [i["port_role"] for i in s["inputs"]]
                calls.append({"call_id": f"{s['step_id']}::{ordinal}", "operation_id": c["operation_id"],
                              "component": s["component"], "inputs": inputs, "outputs": outputs, "parameters": params,
                              "condition": c["condition"], "source_step_id": s["step_id"], "evidence": s["evidence"],
                              "uncertainty": c["uncertainty"] or s["uncertainty"],
                              "status": "documented_operation" if c["operation_id"] else "unexpanded_source_boundary"})
            bypasses += [{**b, "source_step_id": s["step_id"]} for b in s["bypasses"]]
        assembly = {"contract_version": "operation-assembly-v1", "record_id": doc["record_id"],
                    "library_release": release, "library_sha256": library_sha256,
                    **{k: source[k] for k in ("trajectory_id", "model_variant", "task_configuration", "lifecycle_phase",
                                              "model_role", "recipient_component", "receipt_inputs", "evidence", "open_questions")},
                    "nodes": nodes, "calls": calls, "bypasses": bypasses, "source_steps": source["steps"]}
        OperationAssembly.model_validate(assembly)
        validate_operation_ports(assembly, catalog)
        if restore_source(assembly) != source:
            raise ValueError(f"{t['trajectory_id']}: source trajectory not restorable from assembly")
        assemblies.append(assembly)
        sources.append(source)
    return assemblies, sources


# ---------------------------------------------------------------- validator

def _all_evidence(doc):
    for t in doc["trajectories"]:
        for e in t["evidence"]:
            yield t["trajectory_id"], "trajectory", e
        for n in t["nodes"]:
            for e in n["evidence"]:
                yield t["trajectory_id"], f"node {n['node_id']}", e
        for s in t["steps"]:
            for e in s["evidence"]:
                yield t["trajectory_id"], f"step {s['step_id']}", e
            for n in s["intermediate_nodes"]:
                for e in n["evidence"]:
                    yield t["trajectory_id"], f"intermediate {n['node_id']}", e


def closest_span_hint(text, quote):
    """Return the closest exact source span so a repair can copy it verbatim."""
    import difflib
    probe = quote[:200]
    match = difflib.SequenceMatcher(None, text, probe, autojunk=False).find_longest_match(0, len(text), 0, len(probe))
    if match.size < 20:
        return " (no close span found in this section; cite the section that states it)"
    start = max(0, match.a - match.b)
    return f"; closest exact text in this section: {text[start:start + len(quote)]!r}"


def canonicalize_quotes(doc, sections):
    """Replace quotes that differ from the source ONLY in whitespace with the exact source span.

    Docling text contains irregular runs of spaces around symbols that agents cannot reproduce.
    Words, punctuation and casing must still match exactly; anything else stays an error.
    Returns the number of quotes replaced (recorded in the record status).
    """
    replaced = 0
    cache = {}

    def normalized(sid):
        if sid not in cache:
            text = sections[sid]["text"]
            chars, index = [], []
            for i, ch in enumerate(text):
                if ch.isspace():
                    if chars and chars[-1] == " ":
                        continue
                    chars.append(" ")
                else:
                    chars.append(ch)
                index.append(i)
            cache[sid] = ("".join(chars), index)
        return cache[sid]

    for _, _, e in _all_evidence(doc):
        section = sections.get(e["section_id"])
        if section is None or not e["quote"].strip() or e["quote"] in section["text"]:
            continue
        probe = re.sub(r"\s+", " ", e["quote"].strip())
        norm, index = normalized(e["section_id"])
        hit = norm.find(probe)
        if hit < 0 or norm.find(probe, hit + 1) >= 0:
            continue
        start, end = index[hit], index[hit + len(probe) - 1] + 1
        e["quote"] = section["text"][start:end]
        replaced += 1
    return replaced


def validate_document(doc, record_id, sections, catalog, library_sha256, release):
    """Return (errors, warnings, assemblies). Errors block acceptance; warnings go to the reviewer."""
    errors, warnings = [], []
    if doc.get("record_id") != record_id:
        errors.append(f"record_id must be {record_id}")
    if not doc.get("trajectories"):
        errors.append("No trajectories returned")
    blocks = {b["operation_id"]: b for b in catalog["blocks"]}
    for tid, where, e in _all_evidence(doc):
        section = sections.get(e["section_id"])
        if section is None:
            errors.append(f"{tid} / {where}: unknown section {e['section_id']}")
        elif not e["quote"].strip() or e["quote"] not in section["text"]:
            errors.append(f"{tid} / {where}: quote is not a literal substring of {e['section_id']}: {e['quote'][:120]!r}"
                          + closest_span_hint(section["text"], e["quote"]))
    seen_tids = set()
    for t in doc.get("trajectories", []):
        tid = t["trajectory_id"]
        if tid in seen_tids:
            errors.append(f"Duplicate trajectory_id {tid}")
        seen_tids.add(tid)
        if not t["evidence"]:
            errors.append(f"{tid}: trajectory needs evidence")
        for n in t["nodes"] + [n for s in t["steps"] for n in s["intermediate_nodes"]]:
            shape, axes = n["symbolic_shape"], n["axis_semantics"]
            if shape is not None and any(ch.isdigit() for axis in shape for ch in axis):
                errors.append(f"{tid} / node {n['node_id']}: symbolic_shape {shape} contains a digit; use named axes only")
            if shape is not None and axes is not None and len(shape) != len(axes):
                errors.append(f"{tid} / node {n['node_id']}: symbolic_shape has {len(shape)} axes but axis_semantics has "
                              f"{len(axes)}; give one axis_semantics entry per shape axis, or set axis_semantics to null")
        defined = [n["node_id"] for n in t["nodes"]] + [n["node_id"] for s in t["steps"] for n in s["intermediate_nodes"]]
        duplicated = sorted({n for n in defined if defined.count(n) > 1})
        if duplicated:
            errors.append(f"{tid}: node_id defined more than once {duplicated}")
        known = set(defined)
        refs = [("receipt_inputs", o["node_id"]) for o in t["receipt_inputs"]]
        for s in t["steps"]:
            refs += [(f"step {s['step_id']} inputs", o["node_id"]) for o in s["inputs"]]
            refs += [(f"step {s['step_id']} outputs", n) for n in s["outputs"]]
            for c in s["decomposition"]:
                refs += [(f"step {s['step_id']} call {c['operation_id']} port {b['port']}", n)
                         for b in c["inputs"] + c["outputs"] for n in b["node_ids"]]
            refs += [(f"step {s['step_id']} bypass", n) for b in s["bypasses"] for n in (b["source_node_id"], b["target_node_id"])]
        for where, node_id in refs:
            if node_id not in known:
                errors.append(f"{tid} / {where}: node {node_id!r} is not defined in this trajectory's nodes or any "
                              "step's intermediate_nodes; define it (with evidence) or reference an existing node")
        for s in t["steps"]:
            if not s["evidence"]:
                errors.append(f"{tid} / {s['step_id']}: step needs evidence")
            ops = [c for c in s["decomposition"] if c["operation_id"]]
            if ops and len(ops) != len(s["decomposition"]):
                errors.append(f"{tid} / {s['step_id']}: mixes library calls with an unexpanded boundary; split the source step")
            for c in ops:
                if c["operation_id"] not in blocks:
                    errors.append(f"{tid} / {s['step_id']}: unknown operation_id {c['operation_id']!r}")
                    continue
                block = blocks[c["operation_id"]]
                names = [p["name"] for p in c["parameters"]]
                missing = [p for p in block["parameters"] if p not in names]
                if missing:
                    errors.append(f"{tid} / {s['step_id']} / {c['operation_id']}: declared parameters missing {missing}; "
                                  "use the value 'unspecified' when the source does not establish one")
                for p in c["parameters"]:
                    if not p["value"].strip():
                        errors.append(f"{tid} / {s['step_id']} / {c['operation_id']}: empty value for {p['name']}")
            ops = [c for c in ops if c["operation_id"] in blocks]
            if ops:
                consumed = {n for c in ops for b in c["inputs"] for n in b["node_ids"]}
                produced = {n for c in ops for b in c["outputs"] for n in b["node_ids"]}
                step_in = {i["node_id"] for i in s["inputs"]}
                inter = {n["node_id"] for n in s["intermediate_nodes"]}
                if step_in - consumed:
                    errors.append(f"{tid} / {s['step_id']}: source operands not consumed by any call {sorted(step_in - consumed)}")
                if set(s["outputs"]) - produced:
                    errors.append(f"{tid} / {s['step_id']}: source results not produced by any call {sorted(set(s['outputs']) - produced)}")
                stray = consumed - step_in - produced - inter
                if stray:
                    errors.append(f"{tid} / {s['step_id']}: calls read nodes that are neither step operands nor produced here {sorted(stray)}")
                for n in inter:
                    if n not in produced and not any(x["origin"] == "implicit_parameter" and x["node_id"] == n for x in s["intermediate_nodes"]):
                        errors.append(f"{tid} / {s['step_id']}: documented intermediate {n} is never produced")
    if errors:
        return errors, warnings, []
    try:
        assemblies, _ = compile_document(doc, catalog, library_sha256, release)
    except Exception as exc:  # pydantic / port / restoration errors are reported verbatim to the agent
        return [f"Contract validation: {exc}"], warnings, []
    produced_anywhere = {}
    for a in assemblies:
        made = {n for c in a["calls"] for ns in c["outputs"].values() for n in ns}
        roots = [n["node_id"] for n in a["nodes"] if n["node_id"] not in made]
        if not a["receipt_inputs"]:
            warnings.append(f"{a['trajectory_id']}: no receiving operand")
        produced_anywhere[a["trajectory_id"]] = (len(roots), len(a["calls"]))
    return errors, warnings, assemblies


def coverage_warnings(doc, seed):
    variants = " ".join(t["model_variant"].lower() for t in doc["trajectories"])
    return [f"Atlas model '{m['model_name']}' does not appear in any model_variant; cover it or state why in coverage_questions"
            for m in seed["models"] if m["model_name"].lower() not in variants]


def evidence_entries(record_id, assemblies, sections, manifest):
    out = {}
    for a in assemblies:
        items = list(a["evidence"]) + [e for n in a["nodes"] for e in n["evidence"]] + [e for c in a["calls"] for e in c["evidence"]]
        for e in items:
            s = sections[e["section_id"]]
            eid = quote_key(record_id, e)
            out[eid] = {**e, "evidence_id": eid, "record_id": record_id, "heading_path": s["heading_path"],
                        "section_sha256": s["text_sha256"], "source_sha256": manifest["source_sha256"],
                        "quote_start_char_in_section": s["text"].find(e["quote"]),
                        "verification": "literal_own_section_match_at_capture",
                        "provenance_kind": "recovered_markdown_section_id", "native_pdf_item": None}
    return out


# ---------------------------------------------------------------- pilot conversion

def pilot_document(record_id, assemblies, catalog):
    """Express frozen pilot assemblies in the agent format (round-trip test and worked examples).

    Declared parameters a pilot call did not carry are filled with 'unspecified', exactly as the
    agent contract requires; everything else is copied unchanged.
    """
    blocks = {b["operation_id"]: b for b in catalog["blocks"]}
    trajectories = []
    for a in [x for x in assemblies if x["record_id"] == record_id]:
        steps = []
        for s in a["source_steps"]:
            decomposition = []
            for c in (c for c in a["calls"] if c["source_step_id"] == s["step_id"] and c["operation_id"]):
                params = [{"name": k, "value": v if isinstance(v, str) else json.dumps(v)}
                          for k, v in c["parameters"].items() if k != "source_port_roles"]
                params += [{"name": p, "value": "unspecified"} for p in blocks[c["operation_id"]]["parameters"]
                           if p not in c["parameters"]]
                decomposition.append({"operation_id": c["operation_id"],
                                      "inputs": [{"port": k, "node_ids": v} for k, v in c["inputs"].items()],
                                      "outputs": [{"port": k, "node_ids": v} for k, v in c["outputs"].items()],
                                      "parameters": params, "condition": c["condition"],
                                      "uncertainty": c["uncertainty"] if c["uncertainty"] != s["uncertainty"] else None})
            steps.append({**s, "decomposition": decomposition,
                          "intermediate_nodes": [n for n in a["nodes"] if n["origin"] != "source_annotation"
                                                 and n["node_id"].startswith(s["step_id"] + "::")],
                          "bypasses": [{k: b[k] for k in ("source_node_id", "target_node_id", "condition")}
                                       for b in a["bypasses"] if b["source_step_id"] == s["step_id"]]})
        trajectories.append({**{k: a[k] for k in ("trajectory_id", "model_variant", "task_configuration", "lifecycle_phase",
                                                  "model_role", "recipient_component", "receipt_inputs", "evidence",
                                                  "open_questions")},
                             "nodes": [{k: v for k, v in n.items() if k != "origin"} for n in a["nodes"]
                                       if n["origin"] == "source_annotation"],
                             "steps": steps})
    return {"record_id": record_id, "trajectories": trajectories, "coverage_questions": [], "operation_proposals": []}


def write_worked_examples(path, assemblies, catalog):
    doc = pilot_document("full_2026-07-06__rec_000771", assemblies, catalog)
    example = [{"source": "reviewed pilot, ChatNT (full_2026-07-06__rec_000771); quotes are from that paper",
                "note": "Tokenization, a lookup with an implicit parameter table, a documented intermediate, "
                        "and unexpanded module boundaries.",
                "trajectory": next(t for t in doc["trajectories"] if t["trajectory_id"] == "benchmark_fine_tuning")}]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(example))
    return example
