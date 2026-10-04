"""Classify candidate catalog diffs; semantic changes need explicit author review."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.docling_graph_templates.representation_library import CatalogSeed


def review(before, after):
    old = CatalogSeed.model_validate(before).model_dump()
    new = CatalogSeed.model_validate(after).model_dump()
    changes = []
    old_blocks = {item["block_id"]: item for item in old["blocks"]}
    new_blocks = {item["block_id"]: item for item in new["blocks"]}
    for bid, block in old_blocks.items():
        current = new_blocks.get(bid)
        if current is None:
            changes.append({"subject": bid, "kind": "removed_block", "requires_author_approval": True})
            continue
        semantic = ("kind", "definition", "boundaries", "input_roles", "output_roles", "composition", "status")
        changed = [field for field in semantic if block[field] != current[field]]
        if changed:
            changes.append({"subject": bid, "kind": "meaning_or_contract_change", "fields": changed, "requires_author_approval": True})
        for field in ("examples", "aliases"):
            removed = [item for item in block[field] if item not in current[field]]
            added = [item for item in current[field] if item not in block[field]]
            if removed or added:
                changes.append({"subject": bid, "kind": field + "_change", "removed": removed, "added": added,
                                "requires_author_approval": bool(removed)})
    for bid in new_blocks.keys() - old_blocks.keys():
        changes.append({"subject": bid, "kind": "new_block", "requires_author_approval": False})
    before_maps = {(item["kind"], item["source_label"]): item for item in old["mappings"]}
    after_maps = {(item["kind"], item["source_label"]): item for item in new["mappings"]}
    for key, mapping in before_maps.items():
        if after_maps.get(key) != mapping:
            changes.append({"subject": list(key), "kind": "existing_mapping_change", "requires_author_approval": True})
    for key in after_maps.keys() - before_maps.keys():
        changes.append({"subject": list(key), "kind": "new_mapping", "requires_author_approval": False})
    affected = {item["subject"] for item in changes if isinstance(item["subject"], str)}
    existing_mapping_changed = any(item["kind"] == "existing_mapping_change" for item in changes)
    return {"before_release": old["release"], "after_release": new["release"], "changes": changes,
            "requires_author_approval": any(item["requires_author_approval"] for item in changes),
            "new_release_required": bool(changes),
            "same_release_modified": bool(changes) and old["release"] == new["release"],
            "affected_source_labels": [item["source_label"] for item in old["mappings"]
                                       if item["block_id"] in affected or existing_mapping_changed],
            "semantic_entailment": "steward source review required"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    result = review(json.loads(args.before.read_text()), json.loads(args.after.read_text()))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["requires_author_approval"] or result["same_release_modified"]:
        raise SystemExit(2)
