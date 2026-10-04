"""Compile a reviewed description library and lossless pilot assemblies for Pages.

Capture reads the existing pilot/source packets; ordinary build/check use the frozen
snapshot, so CI needs neither a model endpoint nor another PDF conversion.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.docling_graph_templates.representation_library import AssemblyDocument, CatalogSeed

BASE = ROOT / "analysis/representation_block_library_2026-10-04"
PILOT = ROOT / "analysis/nickerson_taxonomy_2026-09-20/object_unit_reassessment_2026-09-22/symbolic_trajectory_supervised_2026-10-04"
PACKETS = PILOT.parent / "section_id_corpus_55_2026-10-04/records"
PUBLIC = ROOT / "docs/input-representation-atlas/component-library/data"
PAPERS = {
    "full_2026-07-06__rec_001319": "InstructCell",
    "full_2026-07-06__rec_000771": "ChatNT",
    "full_2026-07-06__rec_003852": "MUPAD",
    "full_2026-07-06__rec_003517": "X-Cell",
}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


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


def capture_inputs(base):
    rows = [json.loads(line) for line in (PILOT / "trajectories.reviewed.jsonl").read_text().splitlines() if line.strip()]
    ledger = {}
    records = {}
    for row in rows:
        record = row["record_id"]
        path = PACKETS / record
        packet = path / "packet_with_context.md"
        if digest(packet.read_bytes()) != row["input_packet_sha256"]:
            raise ValueError(f"Packet changed: {record}")
        manifest = json.loads((path / "packet_manifest.json").read_text())
        sections = {item["section_id"]: item for item in manifest["sections"]}
        source = Path(row["source_artifact"])
        row["source_artifact_sha256"] = digest(source.read_bytes())
        row["source_artifact"] = str(source.relative_to(ROOT))
        records[record] = {"paper": PAPERS[record], "source_sha256": manifest["source_sha256"],
                           "input_packet_sha256": row["input_packet_sha256"]}
        for item in objects(row["trajectory"]):
            if "quote" not in item:
                continue
            section = sections[item["section_id"]]
            body = (path / "sections" / f'{item["section_id"]}.md').read_text()
            if not item["quote"] or item["quote"] not in body:
                raise ValueError(f"Unmatched own-section quotation: {record} {item['section_id']}")
            key = quote_key(record, item)
            ledger[key] = {**item, "evidence_id": key, "record_id": record,
                           "heading_path": section["heading_path"], "section_sha256": section["text_sha256"],
                           "source_sha256": manifest["source_sha256"],
                           "quote_start_char_in_section": body.index(item["quote"]),
                           "verification": "literal_own_section_match_at_capture",
                           "provenance_kind": "recovered_markdown_section_id", "native_pdf_item": None}
    base.mkdir(parents=True, exist_ok=True)
    snapshot = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows).encode()
    (base / "pilot_input.jsonl").write_bytes(snapshot)
    (base / "evidence_snapshot.json").write_bytes(encoded({"records": records, "evidence": list(ledger.values())}))


def bind(kind, label, mappings, blocks):
    mapping = mappings.get((kind, label))
    if mapping:
        block = blocks[mapping["block_id"]]
        return {"block_id": block["block_id"], "block_version": block["version"],
                "relation": mapping["relation"], "rationale": mapping["rationale"], "proposal_id": None}
    return {"block_id": None, "block_version": None, "relation": "unresolved",
            "rationale": "No steward-approved mapping for this source label; preserve its complete documented instance.",
            "proposal_id": kind + "." + digest(label.encode())}


def restore_trajectory(assembly, context):
    nodes = {node["node_id"]: node for node in assembly["nodes"]}
    steps = {step["step_id"]: step for step in assembly["operations"]}
    recipient = next(item for item in assembly["recipients"] if item["recipient_id"] == context["recipient_id"])
    rename = {ref: nodes[ref]["original_node_id"] for ref in context["node_ids"]}
    original_nodes = []
    for ref in context["node_ids"]:
        node = {key: value for key, value in nodes[ref].items() if key not in {"binding", "original_node_id"}}
        node["node_id"] = rename[ref]
        original_nodes.append(node)
    original_steps = []
    for ref in context["step_ids"]:
        step = {key: value for key, value in steps[ref].items()
                if key not in {"binding", "component_binding", "original_step_id", "normalized_input_roles"}}
        step["step_id"] = steps[ref]["original_step_id"]
        step["inputs"] = [{**item, "node_id": rename[item["node_id"]]} for item in step["inputs"]]
        step["outputs"] = [rename[item] for item in step["outputs"]]
        original_steps.append(step)
    return {key: context[key] for key in ("trajectory_id", "model_variant", "task_configuration", "lifecycle_phase", "model_role", "evidence", "open_questions")} | {
        "recipient_component": recipient["component"], "nodes": original_nodes, "steps": original_steps,
        "receipt_inputs": [{**item, "node_id": rename[item["node_id"]]} for item in recipient["inputs"]]}


def source_subgraph(trajectory, elements, mappings, blocks):
    """Keep real branch topology and crossing ports in a composite source example."""
    chosen = {step["step_id"] for step in elements}
    produced = {ref for step in elements for ref in step["outputs"]}
    consumed = {item["node_id"] for step in elements for item in step["inputs"]}
    involved = produced | consumed
    outside = [step for step in trajectory["steps"] if step["step_id"] not in chosen]
    crossings = [{"node_id": item["node_id"], "consumer": step["step_id"], "port_role": item["port_role"]}
                 for step in outside for item in step["inputs"] if item["node_id"] in produced]
    crossings += [{"node_id": item["node_id"], "consumer": "recipient", "port_role": item["port_role"]}
                  for item in trajectory["receipt_inputs"] if item["node_id"] in produced]
    exported = (produced - consumed) | {item["node_id"] for item in crossings}
    return {"status": "documented_source_instance", "template_generalization": "requires_steward_review",
            "boundary_inputs": sorted(consumed - produced), "boundary_outputs": sorted(exported),
            "external_receiving_ports": crossings,
            "nodes": [{**node, "binding": bind("representation", node["representation_type"], mappings, blocks)}
                      for node in trajectory["nodes"] if node["node_id"] in involved],
            "operations": [{**step, "binding": bind("operation", step["operation_type"], mappings, blocks),
                            "component_binding": bind("component", step["component"], mappings, blocks)} for step in elements]}


def compile_release(base):
    seed = CatalogSeed.model_validate_json((base / "catalog_seed.json").read_text()).model_dump()
    rows = [json.loads(line) for line in (base / "pilot_input.jsonl").read_text().splitlines() if line.strip()]
    snapshot = json.loads((base / "evidence_snapshot.json").read_text())
    seed_hash = digest(encoded(seed))
    blocks = {block["block_id"]: block for block in seed["blocks"]}
    mappings = {(item["kind"], item["source_label"]): item for item in seed["mappings"]}
    original = {(row["record_id"], row["trajectory"]["trajectory_id"]): row["trajectory"] for row in rows}
    if len(original) != len(rows):
        raise ValueError("Duplicate source trajectory key")
    evidence_by_id = {item["evidence_id"]: item for item in snapshot["evidence"]}
    assemblies = {}
    proposals = {}
    usage = defaultdict(list)
    for row in rows:
        record, t = row["record_id"], row["trajectory"]
        assembly = assemblies.setdefault(record, {
            "contract_version": "representation-assembly-v1", "record_id": record,
            "input_packet_sha256": row["input_packet_sha256"], "source_artifact": row["source_artifact"],
            "source_artifact_sha256": row["source_artifact_sha256"],
            "library_release": seed["release"], "library_sha256": seed_hash,
            "nodes": [], "operations": [], "recipients": [], "contexts": [], "identity_links": [],
            "coverage_questions": ["Cross-context identity was not inferred during lossless adaptation; explicit source-backed identity links remain a review task."]})
        prefix = t["trajectory_id"] + "::"
        context = {key: t[key] for key in ("trajectory_id", "model_variant", "task_configuration", "lifecycle_phase", "model_role", "evidence", "open_questions")}
        context.update(node_ids=[], step_ids=[], recipient_id=prefix + "recipient")
        for node in t["nodes"]:
            item = {**node, "node_id": prefix + node["node_id"], "original_node_id": node["node_id"],
                    "binding": bind("representation", node["representation_type"], mappings, blocks)}
            assembly["nodes"].append(item)
            context["node_ids"].append(item["node_id"])
        for step in t["steps"]:
            item = {**step, "step_id": prefix + step["step_id"], "original_step_id": step["step_id"],
                    "binding": bind("operation", step["operation_type"], mappings, blocks),
                    "component_binding": bind("component", step["component"], mappings, blocks),
                    "normalized_input_roles": {},
                    "inputs": [{**operand, "node_id": prefix + operand["node_id"]} for operand in step["inputs"]],
                    "outputs": [prefix + ref for ref in step["outputs"]]}
            assembly["operations"].append(item)
            context["step_ids"].append(item["step_id"])
        assembly["recipients"].append({"recipient_id": context["recipient_id"], "component": t["recipient_component"],
            "binding": bind("component", t["recipient_component"], mappings, blocks),
            "inputs": [{**operand, "node_id": prefix + operand["node_id"]} for operand in t["receipt_inputs"]]})
        assembly["contexts"].append(context)
        for obj in objects(t):
            if "quote" in obj and quote_key(record, obj) not in evidence_by_id:
                raise ValueError("Missing captured evidence")
        for kind, elements, label_field, id_field in (
            ("representation", t["nodes"], "representation_type", "node_id"),
            ("operation", t["steps"], "operation_type", "step_id"),
            ("component", t["steps"], "component", "step_id"),
            ("component", [{"component": t["recipient_component"], "recipient_id": "recipient"}], "component", "recipient_id"),
        ):
            for element in elements:
                binding = bind(kind, element[label_field], mappings, blocks)
                occurrence = {"record_id": record, "trajectory_id": t["trajectory_id"],
                              "element_id": element[id_field], "source_label": element[label_field], "relation": binding["relation"]}
                if binding["block_id"]:
                    usage[binding["block_id"]].append(occurrence)
                else:
                    proposal = proposals.setdefault(binding["proposal_id"], {"proposal_id": binding["proposal_id"],
                        "kind": kind, "source_label": element[label_field], "status": "awaiting_steward_review", "occurrences": []})
                    proposal["occurrences"].append(occurrence)
    for assembly in assemblies.values():
        AssemblyDocument.model_validate(assembly)
        for context in assembly["contexts"]:
            if restore_trajectory(assembly, context) != original[(assembly["record_id"], context["trajectory_id"])]:
                raise ValueError("Lossless trajectory round trip failed")
    public_blocks = []
    for block in seed["blocks"]:
        examples = []
        for example in block["examples"]:
            trajectory = original[(example["record_id"], example["trajectory_id"])]
            if example["element_kind"] == "node":
                elements = [node for node in trajectory["nodes"] if node["node_id"] in example["element_ids"]]
            elif example["element_kind"] in {"step", "subgraph"}:
                elements = [step for step in trajectory["steps"] if step["step_id"] in example["element_ids"]]
            else:
                elements = [{"recipient_component": trajectory["recipient_component"], "receipt_inputs": trajectory["receipt_inputs"], "evidence": trajectory["evidence"]}]
            if example["element_kind"] != "recipient" and len(elements) != len(example["element_ids"]):
                raise ValueError(f"Missing example element: {block['block_id']}")
            ev_ids = list(dict.fromkeys(quote_key(example["record_id"], item) for element in elements for item in objects(element) if "quote" in item))
            if not ev_ids:
                raise ValueError(f"Example has no evidence: {block['block_id']}")
            examples.append({**example, "paper": PAPERS[example["record_id"]], "evidence_ids": ev_ids,
                             "elements": elements, "lifecycle_phase": trajectory["lifecycle_phase"],
                             "source_subgraph": source_subgraph(trajectory, elements, mappings, blocks)
                             if example["element_kind"] == "subgraph" else None})
        public_blocks.append({**block, "examples": examples, "usage": usage[block["block_id"]]})
    report = {"status": "development_candidate", "record_count": len(assemblies), "trajectory_count": len(rows),
              "block_counts": dict(Counter(block["kind"] for block in seed["blocks"])),
              "unique_evidence_count": len(evidence_by_id), "extension_proposals": len(proposals),
              "lossless_round_trip": True, "assembly_schema_pass": True,
              "source_validation": "own-section literal checks at capture; source entailment requires scientific review",
              "shared_identity": "no cross-context identity inferred", "canonical_migration": False,
              "source_sizes_modified": False, "library_sha256": seed_hash,
              "pilot_input_sha256": digest((base / "pilot_input.jsonl").read_bytes()),
              "evidence_snapshot_sha256": digest((base / "evidence_snapshot.json").read_bytes())}
    catalog = {"contract_version": "representation-library-v1", "release": seed["release"], "library_sha256": seed_hash,
               "status": "development_candidate", "records": snapshot["records"], "blocks": public_blocks,
               "proposals": list(proposals.values()), "decisions": seed["decisions"], "report": report}
    return {"catalog.json": catalog, "assemblies.json": list(assemblies.values()),
            "evidence.json": snapshot["evidence"], "validation.json": report,
            "assembly.schema.json": AssemblyDocument.model_json_schema(), "catalog-seed.schema.json": CatalogSeed.model_json_schema()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--public", type=Path, default=PUBLIC)
    parser.add_argument("--capture-inputs", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--freeze", action="store_true", help="Preserve immutable release files after validation")
    args = parser.parse_args()
    if args.check and (args.capture_inputs or args.freeze):
        parser.error("Check is read-only")
    if args.capture_inputs:
        capture_inputs(args.base)
    outputs = compile_release(args.base)
    release = outputs["catalog.json"]["release"]
    frozen = args.base / "releases" / release
    if (frozen / "freeze.json").exists():
        lock = json.loads((frozen / "freeze.json").read_text())
        for name, payload in outputs.items():
            if digest(encoded(payload)) != lock["artifacts"].get(name):
                raise SystemExit(f"Frozen release {release} changed: {name}. Review the change and create a new version.")
            if not (frozen / name).exists() or digest((frozen / name).read_bytes()) != lock["artifacts"][name]:
                raise SystemExit(f"Frozen artifact changed: {name}")
    failures = []
    for name, payload in outputs.items():
        data = encoded(payload)
        targets = [args.public / name, args.base / "release" / name]
        for target in targets:
            if args.check:
                if not target.exists() or target.read_bytes() != data:
                    failures.append(str(target.relative_to(ROOT)))
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
    if failures:
        raise SystemExit("Stale/missing generated artifacts: " + ", ".join(failures))
    if args.freeze:
        frozen.mkdir(parents=True, exist_ok=True)
        for name, payload in outputs.items():
            (frozen / name).write_bytes(encoded(payload))
        (frozen / "catalog_seed.json").write_bytes((args.base / "catalog_seed.json").read_bytes())
        (frozen / "freeze.json").write_bytes(encoded({"release": release,
            "library_sha256": outputs["catalog.json"]["library_sha256"],
            "artifacts": {name: digest(encoded(payload)) for name, payload in outputs.items()},
            "pilot_input_sha256": digest((args.base / "pilot_input.jsonl").read_bytes()),
            "evidence_snapshot_sha256": digest((args.base / "evidence_snapshot.json").read_bytes())}))
    print(json.dumps(outputs["validation.json"], indent=2))


if __name__ == "__main__":
    main()
