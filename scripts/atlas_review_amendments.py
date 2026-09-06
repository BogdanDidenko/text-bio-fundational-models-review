"""Apply explicit post-extraction review amendments to the atlas view only."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path


def apply_review_amendments(routes, files, root):
    amended = deepcopy(routes)
    by_id = {row["route_id"]: row for row in amended}
    applied = []
    seen = set()
    allowed = {"carrier_subtype", "input_status", "lifecycle_phase", "evidence_quote", "section_heading", "pages", "doc_item_refs", "uncertainty"}
    for file in files:
        record = json.loads(file.read_text())
        route_id = record["route_id"]
        if route_id not in by_id:
            expected_record = record["expected"].get("record_id")
            if expected_record and any(row.get("record_id") == expected_record for row in amended):
                raise ValueError(f"Reviewed record remains but route identity changed: {route_id}; reconcile the amendment")
            continue
        if route_id in seen:
            raise ValueError(f"Multiple review amendments for {route_id}")
        seen.add(route_id)
        route = by_id[route_id]
        for field, value in record["expected"].items():
            if route.get(field) != value:
                raise ValueError(f"Review amendment source changed: {route_id}/{field}")
        if set(record["updates"]) - allowed:
            raise ValueError("Review amendment changes an unsupported field")
        source = record["evidence_source"]
        text_path = root / source["path"]
        text = text_path.read_text()
        if hashlib.sha256(text_path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError("Review evidence source hash changed")
        quote = record["updates"]["evidence_quote"]
        if quote not in text or quote not in text.splitlines()[source["line"] - 1]:
            raise ValueError("Amended quote does not match its cited source line")
        original = {field: route.get(field) for field in record["updates"]}
        route.update(record["updates"])
        route["review_amendment"] = {
            "case_id": record["case_id"], "date": record["date"],
            "status": record["status"], "procedure": record["procedure"],
            "model_role": record["model_role"], "operation_purpose": record["operation_purpose"],
            "author_confirmed_fields": record["author_confirmed_fields"],
            "rationale": record["rationale"], "evidence_source": source,
            "original": original,
        }
        applied.append({"path": str(file.relative_to(root)), "sha256": hashlib.sha256(file.read_bytes()).hexdigest(), "route_id": route_id})
    return amended, applied


def unresolved_id(family_id):
    return f"unresolved::{family_id}"


def membership_ids(architecture):
    return sorted(architecture["subtypes"] + [unresolved_id(f) for f in architecture.get("unresolved_families", [])])
