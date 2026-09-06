#!/usr/bin/env python3
"""Build the reviewed atlas view after the unchanged, method-locked atlas build."""

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from atlas_review_amendments import apply_review_amendments, membership_ids, unresolved_id
from build_input_representation_atlas import FAMILY_META, SUBTYPE_EXAMPLES, write_json

ROOT = Path(__file__).resolve().parents[1]


def reviewed_view(atlas, files, root):
    view = deepcopy(atlas)
    routes = []
    for model in view["architectures"]:
        for item in model["routes"]:
            row = deepcopy(item)
            old_review = row.pop("review_amendment", None)
            if old_review:
                row.update(old_review["original"])
            routes.append({**row, "model_id": model["model_id"], "record_id": model["record_id"]})
    routes, applied = apply_review_amendments(routes, files, root)
    if not applied and not atlas["meta"].get("review_amendments"):
        return view
    by_model = defaultdict(list)
    for route in routes:
        by_model[route["model_id"]].append(route)
    catalog = {s["subtype_id"]: {**s, "family_id": f["family_id"]} for f in view["families"] for s in f["subtypes"]}
    for model in view["architectures"]:
        rows = by_model[model["model_id"]]
        if not any(r.get("review_amendment") for r in rows) and not any(r.get("review_amendment") for r in model["routes"]):
            continue
        model["routes"] = [{k: v for k, v in r.items() if k not in {"model_id", "record_id"}} for r in rows]
        counts = Counter(r["carrier_subtype"] for r in rows)
        if set(counts) - set(catalog) - {"unclear"}:
            raise ValueError("Amendment introduced an unknown taxonomy subtype")
        model["subtype_counts"] = dict(counts)
        model["subtypes"] = sorted(s for s in counts if s != "unclear")
        model["primary_subtype"] = max(counts, key=lambda s: (counts[s], s))
        model["unresolved_families"] = sorted({r["carrier_family"] for r in rows if r["carrier_subtype"] == "unclear"})
        model["membership_ids"] = membership_ids(model)
        model["lifecycle_phases"] = sorted({r["lifecycle_phase"] for r in rows})
        model["illustrative_examples"] = []
        for subtype in model["subtypes"]:
            row = next(r for r in rows if r["carrier_subtype"] == subtype)
            example = SUBTYPE_EXAMPLES[subtype]
            model["illustrative_examples"].append({"subtype_id": subtype, "family_id": row["carrier_family"], "route_id": row["route_id"], "example_input": example["input"], "example_carrier": example["carrier"], "example_interface": example["model"], "actual_source": row["source_object_verbatim"], "actual_model_visible_form": row["model_visible_form_verbatim"]})
    states = []
    for family in view["families"]:
        rows = [r for r in routes if r["carrier_family"] == family["family_id"]]
        for subtype in family["subtypes"]:
            matches = [r for r in rows if r["carrier_subtype"] == subtype["subtype_id"]]
            subtype["route_count"] = len(matches)
            subtype["model_count"] = len({r["model_id"] for r in matches})
        unclear = [r for r in rows if r["carrier_subtype"] == "unclear"]
        if unclear:
            state = {"subtype_id": unresolved_id(family["family_id"]), "family_id": family["family_id"], "leaf_id": family["code"] + " ?", "name": "Subtype unresolved", "annotation_state": True, "definition": "The carrier family is identified. Available evidence leaves the subtype unresolved.", "route_count": len(unclear), "model_count": len({r["model_id"] for r in unclear})}
            states.append(state)
            catalog[state["subtype_id"]] = state
    nodes = [n for n in view["graph"]["nodes"] if n["type"] in {"root", "family", "subtype"}]
    edges = [e for e in view["graph"]["edges"] if e["type"] in {"contains_family", "contains_subtype"} and not e["target"].startswith("subtype::unresolved::")]
    for state in states:
        node_id = f"subtype::{state['subtype_id']}"
        nodes.append({"id": node_id, "type": "annotation_state", "label": state["name"], "subtype_id": state["subtype_id"], "family_id": state["family_id"], "leaf_id": state["leaf_id"]})
        edges.append({"id": f"edge::{state['family_id']}::{state['subtype_id']}", "source": f"family::{state['family_id']}", "target": node_id, "type": "contains_annotation_state"})
    groups = defaultdict(list)
    for model in view["architectures"]:
        groups[tuple(membership_ids(model))].append(model)
    for signature, models in sorted(groups.items()):
        group_id = "membership_" + hashlib.sha1("|".join(signature).encode()).hexdigest()[:12]
        models.sort(key=lambda m: m["model_name"].casefold())
        family_ids = sorted({catalog[s]["family_id"] for s in signature}, key=lambda f: FAMILY_META[f]["code"])
        node_id = f"group::{group_id}"
        nodes.append({"id": node_id, "type": "membership_group", "label": " + ".join(catalog[s]["leaf_id"] for s in signature), "group_id": group_id, "subtype_ids": list(signature), "family_ids": family_ids, "model_ids": [m["model_id"] for m in models], "model_count": len(models)})
        for subtype in signature:
            edges.append({"id": f"edge::{subtype}::{group_id}", "source": f"subtype::{subtype}", "target": node_id, "type": "defines_membership_group"})
        for model in models:
            model["membership_group_id"] = group_id
            model_id = f"model::{model['model_id']}"
            nodes.append({"id": model_id, "type": "model", "label": model["model_name"], "model_id": model["model_id"], "membership_group_id": group_id})
            edges.append({"id": f"edge::{group_id}::{model['model_id']}", "source": node_id, "target": model_id, "type": "contains_model"})
    view["annotation_states"] = states
    view["graph"].update(nodes=nodes, edges=edges)
    view["graph"]["counts"].update(annotation_states=len(states), membership_groups=len(groups), edges=len(edges))
    view["meta"].update(review_amendments=applied, unresolved_subtype_routes=sum(r["carrier_subtype"] == "unclear" for r in routes), membership_group_count=len(groups), classification_view="Frozen taxonomy with dated author-led review amendments")
    view["filter_values"]["lifecycle_phases"] = sorted({r["lifecycle_phase"] for r in routes})
    return view


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas-root", type=Path, default=ROOT / "docs/input-representation-atlas")
    parser.add_argument("--amendments", type=Path, default=ROOT / "data/input_representation_audit_amendments")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    file = args.atlas_root / "data/atlas.json"
    original = json.loads(file.read_text())
    updated = reviewed_view(original, sorted(args.amendments.glob("*.json")), ROOT)
    if args.check:
        if original != updated:
            raise SystemExit("Atlas review amendments are stale: run apply_atlas_review_amendments.py before publishing")
    else:
        write_json(file, updated)
        report_path = args.atlas_root / "data/build_report.json"
        report = json.loads(report_path.read_text())
        report.update(review_amendments=updated["meta"].get("review_amendments", []), subtype_route_counts=dict(Counter(r["carrier_subtype"] for m in updated["architectures"] for r in m["routes"])), graph_nodes=len(updated["graph"]["nodes"]), graph_edges=len(updated["graph"]["edges"]))
        write_json(report_path, report)
    print(json.dumps({"status": "ok", "amendments": updated["meta"].get("review_amendments", []), "unresolved_subtype_routes": updated["meta"].get("unresolved_subtype_routes", 0)}))


if __name__ == "__main__":
    main()
