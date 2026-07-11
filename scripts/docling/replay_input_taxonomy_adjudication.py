#!/usr/bin/env python3
"""Replay and validate one logged taxonomy-adjudication response."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

from adjudicate_input_taxonomy import (
    DEFAULT_INVENTORY,
    DEFAULT_MANIFEST,
    ROOT,
    FinalAdjudicatedTaxonomyDocument,
    aggregate_grounding,
    dense_candidates,
    group_inventory,
    load_dense_run,
    load_native_item_texts,
    read_json,
    repair_candidate_ref_namespaces,
    repair_dense_links,
    repair_route_quotes,
    validate_result,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-id", required=True)
    parser.add_argument("--llm-log", type=Path, required=True)
    parser.add_argument("--request-index", type=int)
    parser.add_argument("--dense-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--canonical-manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    responses = []
    for line_number, line in enumerate(args.llm_log.read_text(encoding="utf-8").splitlines(), 1):
        event = json.loads(line)
        if event.get("event") == "response" and event.get("content"):
            responses.append((line_number, event))
    if not responses:
        raise RuntimeError(f"No nonempty response in {args.llm_log}")

    result = None
    selected_line = None
    selected_event = None
    schema_errors = []
    selectable = [
        item
        for item in responses
        if args.request_index is None or item[1].get("request_index") == args.request_index
    ]
    if not selectable:
        raise RuntimeError(
            f"No response for request index {args.request_index} in {args.llm_log}"
        )
    for line_number, event in reversed(selectable):
        try:
            result = FinalAdjudicatedTaxonomyDocument.model_validate_json(event["content"])
            selected_line = line_number
            selected_event = event
            break
        except Exception as exc:
            schema_errors.append({"line_number": line_number, "error": repr(exc)})
    if result is None or selected_event is None or selected_line is None:
        raise RuntimeError(f"No schema-valid response: {schema_errors}")

    with args.canonical_manifest.open(newline="", encoding="utf-8") as stream:
        row = next(
            item for item in csv.DictReader(stream) if item["candidate_id"] == args.record_id
        )
    markdown = (ROOT / row["markdown"]).read_text(encoding="utf-8")
    native_items = load_native_item_texts(ROOT / row["docling_json"])
    discovery = group_inventory(read_json(args.inventory))[args.record_id]
    dense_map = load_dense_run(args.dense_run)
    dense, automatic_dense_exclusions = dense_candidates(
        args.record_id, dense_map[args.record_id]
    )

    quote_repairs = repair_route_quotes(
        result, discovery, dense, markdown, native_items
    )
    namespace_repairs = repair_candidate_ref_namespaces(result)
    dense_link_repairs = repair_dense_links(result)
    errors = validate_result(result, discovery, dense, markdown, native_items)
    if errors:
        raise RuntimeError("Replay validation failed: " + "; ".join(errors))

    payload = result.model_dump(mode="json")
    discovery_by_ref = {item["route_ref"]: item for item in discovery}
    dense_by_ref = {item["candidate_ref"]: item for item in dense}
    for route in payload["input_routes"]:
        route["adjudicated_grounding"] = aggregate_grounding(
            route, discovery_by_ref, dense_by_ref, markdown, native_items
        )
    summary = {
        "status": "ok",
        "record_id": args.record_id,
        "title": row["title"],
        "doi": row.get("doi", ""),
        "model": "openai/gpt-5.4-mini",
        "temperature": 0.0,
        "max_tokens": None,
        "context_limit": None,
        "source_markdown": row["markdown"],
        "source_markdown_sha256": hashlib.sha256(markdown.encode()).hexdigest(),
        "discovery_candidate_count": len(discovery),
        "dense_candidate_count": len(dense) + len(automatic_dense_exclusions),
        "eligible_dense_candidate_count": len(dense),
        "automatic_dense_exclusion_count": len(automatic_dense_exclusions),
        "automatic_dense_exclusions": automatic_dense_exclusions,
        "replay_source_llm_log": str(args.llm_log),
        "replay_source_llm_log_sha256": hashlib.sha256(args.llm_log.read_bytes()).hexdigest(),
        "replay_source_line_number": selected_line,
        "replay_source_request_index": selected_event.get("request_index"),
        "ignored_later_schema_errors": schema_errors,
        "quote_repair_count": len(quote_repairs),
        "quote_repairs": quote_repairs,
        "candidate_ref_namespace_repair_count": len(namespace_repairs),
        "candidate_ref_namespace_repairs": namespace_repairs,
        "dense_link_repair_count": len(dense_link_repairs),
        "dense_link_repairs": dense_link_repairs,
        **payload,
    }
    record_dir = args.output_dir / "records" / re.sub(
        r"[^A-Za-z0-9._-]", "_", args.record_id
    )
    write_json(record_dir / "adjudicated_routes.json", summary)
    write_json(args.output_dir / "run_summary.json", [summary])
    write_json(
        args.output_dir / "replay_manifest.json",
        {
            "record_id": args.record_id,
            "source_llm_log": str(args.llm_log),
            "source_llm_log_sha256": summary["replay_source_llm_log_sha256"],
            "source_line_number": selected_line,
            "source_request_index": selected_event.get("request_index"),
            "validation_errors": [],
        },
    )
    print(json.dumps({"record_id": args.record_id, "status": "ok"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
