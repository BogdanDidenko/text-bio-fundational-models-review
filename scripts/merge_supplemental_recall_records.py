#!/usr/bin/env python3
"""Merge declared recall corrections into an update before cumulative deduplication."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from deduplicate import normalize_doi, normalize_title


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("records") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError(f"Unsupported record artifact: {path}")
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record_title(record: dict[str, Any]) -> str:
    return str(record.get("title") or record.get("title_original") or "").strip()


def record_doi(record: dict[str, Any]) -> str:
    return normalize_doi(
        str(record.get("doi") or record.get("doi_normalized") or record.get("doi_original") or "")
    )


def record_key(record: dict[str, Any]) -> tuple[str, str]:
    return record_doi(record), normalize_title(record_title(record))


def validate_declaration(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("schema_version") != 1:
        raise ValueError("Supplemental recall declaration requires schema_version=1")
    declarations = payload.get("declarations")
    if not isinstance(declarations, list) or not declarations:
        raise ValueError("Supplemental recall declaration has no declarations")
    for index, declaration in enumerate(declarations, start=1):
        record = declaration.get("record") or {}
        if not record_title(record):
            raise ValueError(f"Supplemental declaration {index} has no title")
        if not any(
            str(record.get(field) or "").strip()
            for field in ("doi", "doi_normalized", "pmid", "arxiv_id", "url")
        ):
            raise ValueError(
                f"Supplemental declaration {index} requires DOI, PMID, arXiv ID, or source URL"
            )
        for field in ("reason", "source_url", "resolver", "declared_at"):
            if not str(declaration.get(field) or "").strip():
                raise ValueError(f"Supplemental declaration {index} has no {field}")
    return declarations


def merge_records(
    canonical: list[dict[str, Any]], declarations: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    merged = [dict(row) for row in canonical]
    by_doi = {record_doi(row) for row in canonical if record_doi(row)}
    by_title = {
        normalize_title(record_title(row)) for row in canonical if normalize_title(record_title(row))
    }
    audit: list[dict[str, Any]] = []
    next_cluster = max(
        (
            int(match.group())
            for row in canonical
            if (match := re.search(r"\d+", str(row.get("cluster_id") or "")))
        ),
        default=0,
    )
    declared_keys: set[tuple[str, str]] = set()
    for declaration in declarations:
        record = dict(declaration["record"])
        doi, title = record_key(record)
        if (doi, title) in declared_keys:
            raise ValueError(f"Duplicate supplemental declaration: {record_title(record)}")
        declared_keys.add((doi, title))
        if (doi and doi in by_doi) or (title and title in by_title):
            audit.append(
                {
                    "title": record_title(record),
                    "doi": doi,
                    "disposition": "already_present_in_within_update_cohort",
                    "reason": declaration["reason"],
                }
            )
            continue
        next_cluster += 1
        record.setdefault("cluster_id", f"supplemental_{next_cluster:06d}")
        record["supplemental_recall"] = {
            "reason": declaration["reason"],
            "source_url": declaration["source_url"],
            "resolver": declaration["resolver"],
            "declared_at": declaration["declared_at"],
        }
        merged.append(record)
        if doi:
            by_doi.add(doi)
        if title:
            by_title.add(title)
        audit.append(
            {
                "title": record_title(record),
                "doi": doi,
                "cluster_id": record["cluster_id"],
                "disposition": "added_before_cumulative_deduplication",
                "reason": declaration["reason"],
            }
        )
    return merged, audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--declarations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    args = parser.parse_args()

    canonical = read_records(args.canonical)
    declaration_payload = json.loads(args.declarations.read_text(encoding="utf-8"))
    declarations = validate_declaration(declaration_payload)
    merged, audit = merge_records(canonical, declarations)
    write_json(
        args.output,
        {
            "schema_version": 1,
            "created": now_iso(),
            "canonical_source": str(args.canonical),
            "supplemental_declarations": str(args.declarations),
            "canonical_records": len(canonical),
            "records": merged,
        },
    )
    write_json(
        args.audit_output,
        {
            "schema_version": 1,
            "created": now_iso(),
            "declarations": len(declarations),
            "added": sum(row["disposition"].startswith("added") for row in audit),
            "already_present": sum(row["disposition"].startswith("already") for row in audit),
            "rows": audit,
        },
    )
    print(json.dumps({"records": len(merged), "audit": audit}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
