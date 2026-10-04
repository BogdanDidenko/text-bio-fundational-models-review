"""Review operation-library changes without altering existing frozen releases."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.docling_graph_templates.representation_library import OperationCatalog


def review(before, after):
    old = OperationCatalog.model_validate(before).model_dump()
    new = OperationCatalog.model_validate(after).model_dump()
    previous = {block["operation_id"]: block for block in old["blocks"]}
    current = {block["operation_id"]: block for block in new["blocks"]}
    changes = []
    for oid, block in previous.items():
        if oid not in current:
            changes.append({"operation_id": oid, "action": "removal", "requires_author_approval": True})
        elif current[oid] != block:
            changes.append({"operation_id": oid, "action": "definition_or_signature_change", "requires_author_approval": True})
    for oid in current.keys() - previous.keys():
        changes.append({"operation_id": oid, "action": "new_operation", "requires_author_approval": False})
    return {"changes": changes, "requires_author_approval": any(item["requires_author_approval"] for item in changes),
            "same_release_modified": bool(changes) and old["release"] == new["release"],
            "source_review": "New operation proposals require evidence and comparison with existing operation contracts."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    report = review(json.loads(args.before.read_text()), json.loads(args.after.read_text()))
    print(json.dumps(report, indent=2))
    if report["requires_author_approval"] or report["same_release_modified"]:
        raise SystemExit(2)
