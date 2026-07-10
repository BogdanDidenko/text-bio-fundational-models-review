#!/usr/bin/env python3
"""Build clean screening-pipeline records from Docling Graph evidence runs."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH_OUTPUT = ROOT / "data/docling_graph_screening_evidence_sample10_2026-07-10_gpt54mini_direct_nolimits"
DEFAULT_BASE_RECORDS = ROOT / "data/screening_codex_fulltext_2026-07-09/input_records.json"
DEFAULT_OUT = ROOT / "data/fulltext_screening_context_2026-07-10_docling_graph_direct_sample10"
FULL_DOCUMENT_RATIO = 0.90
ROOT_CONTAINER_RATIO = 0.80


def rel(path: Path | str | None) -> str:
    if not path:
        return ""
    value = Path(path)
    if not value.is_absolute():
        value = ROOT / value
    try:
        return str(value.relative_to(ROOT))
    except ValueError:
        return str(value)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def base_record_index(path: Path) -> dict[str, dict[str, Any]]:
    raw = load_json(path)
    records = raw.get("records", []) if isinstance(raw, dict) else raw
    index: dict[str, dict[str, Any]] = {}
    for record in records:
        for key in (record.get("record_id"), record.get("candidate_id"), record.get("doi")):
            if key:
                index[str(key)] = record
    return index


def graph_summaries(graph_output: Path) -> list[Path]:
    return sorted(graph_output.rglob("screening_evidence_summary.json"))


def lookup_base(summary: dict[str, Any], index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    for key in (summary.get("record_id"), summary.get("candidate_id"), summary.get("doi")):
        if key and str(key) in index:
            return index[str(key)]
    return {}


def heading_path_text(section: dict[str, Any]) -> str:
    path = section.get("heading_path") or []
    return " > ".join(str(item) for item in path) or str(section.get("heading") or "")


def markdown_stats(summary: dict[str, Any]) -> tuple[int, int]:
    path = Path(summary.get("source_markdown") or "")
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        return 0, 0
    text = path.read_text(encoding="utf-8", errors="replace")
    headings = sum(bool(re.match(r"^#{1,8}\s+.+?\s*$", line)) for line in text.splitlines())
    return len(text), headings


def section_quality(section: dict[str, Any], markdown_chars: int, heading_count: int) -> dict[str, Any]:
    derived = section.get("derived_full_section") or {}
    text_chars = len(derived.get("text") or section.get("text") or "")
    coverage = text_chars / markdown_chars if markdown_chars else 0.0
    heading_path = section.get("heading_path") or derived.get("heading_path") or []
    root_container = bool(
        len(heading_path) == 1
        and heading_count > 1
        and coverage >= ROOT_CONTAINER_RATIO
    )
    full_document_like = coverage >= FULL_DOCUMENT_RATIO
    return {
        "section_coverage_ratio": round(coverage, 6),
        "root_container": root_container,
        "full_document_like": full_document_like,
    }


def section_for_input(section: dict[str, Any], quality: dict[str, Any]) -> dict[str, Any]:
    derived = section.get("derived_full_section") or {}
    text = derived.get("text") or section.get("text") or ""
    return {
        "section_type": section.get("section_type", ""),
        "heading": derived.get("heading") or section.get("heading", ""),
        "heading_path": derived.get("heading_path") or section.get("heading_path", []),
        "heading_path_text": heading_path_text(derived or section),
        "heading_level": derived.get("heading_level"),
        "line_start": derived.get("line_start"),
        "line_end": derived.get("line_end"),
        "text": text,
        "original_chars": len(text),
        "evidence_quote": section.get("evidence_quote", ""),
        "evidence_section_heading": section.get("evidence_section_heading", ""),
        "contains_evidence_quote": bool(derived.get("contains_evidence_quote")),
        "contains_chunk_excerpt": bool(derived.get("contains_chunk_excerpt")),
        "chunk_id": section.get("chunk_id"),
        "pages": section.get("pages", []),
        "doc_item_refs": section.get("doc_item_refs", []),
        "docling_graph_node_id": section.get("docling_graph_node_id", ""),
        "docling_graph_provenance": section.get("docling_graph_provenance", {}),
        "grounding_source": section.get("grounding_source", ""),
        "match_type": section.get("match_type", ""),
        "source_markdown": derived.get("source_markdown", ""),
        "derivation_source": derived.get("derivation_source", ""),
        **quality,
    }


def section_key(section: dict[str, Any]) -> tuple[str, Any, Any, str]:
    return (
        str(section.get("source_markdown") or ""),
        section.get("line_start"),
        section.get("line_end"),
        str(section.get("heading_path_text") or ""),
    )


def candidate_sections(grounding: dict[str, Any], section_type: str) -> list[dict[str, Any]]:
    chunks = grounding.get(f"{section_type}_chunks") or []
    if chunks:
        return chunks
    return [
        item for item in grounding.get("sections_for_screening", [])
        if item.get("section_type") == section_type
    ]


def choose_sections_for_input(
    summary: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grounding = summary.get("section_grounding") or {}
    markdown_chars, heading_count = markdown_stats(summary)
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    missing_targets: list[str] = []

    for section_type in ("data_source", "input_representation"):
        candidates = candidate_sections(grounding, section_type)
        prepared: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for candidate in candidates:
            quality = section_quality(candidate, markdown_chars, heading_count)
            prepared.append((candidate, quality))
        usable = [
            (candidate, quality)
            for candidate, quality in prepared
            if (candidate.get("derived_full_section") or {}).get("status") == "ok"
            and (candidate.get("derived_full_section") or {}).get("text")
            and not quality["full_document_like"]
        ]
        if not usable:
            missing_targets.append(section_type)
            for candidate, quality in prepared:
                rejected.append({
                    "section_type": section_type,
                    "heading_path": candidate.get("heading_path", []),
                    "chunk_id": candidate.get("chunk_id"),
                    "reason": "full_document_like_or_no_valid_derived_section",
                    **quality,
                })
            continue

        # Prefer specific non-root sections. Evidence flags break ties, then
        # deeper heading trails, then shorter sections.
        usable.sort(
            key=lambda item: (
                not item[1]["root_container"],
                bool((item[0].get("derived_full_section") or {}).get("contains_evidence_quote")),
                bool((item[0].get("derived_full_section") or {}).get("contains_chunk_excerpt")),
                len(item[0].get("heading_path") or []),
                -len((item[0].get("derived_full_section") or {}).get("text") or ""),
            ),
            reverse=True,
        )
        candidate, quality = usable[0]
        selected.append(section_for_input(candidate, quality))
        for other, other_quality in prepared:
            if other is candidate:
                continue
            if other_quality["full_document_like"]:
                rejected.append({
                    "section_type": section_type,
                    "heading_path": other.get("heading_path", []),
                    "chunk_id": other.get("chunk_id"),
                    "reason": "full_document_like_not_selected",
                    **other_quality,
                })

    # One grounded section may legitimately support both target types. Keep it
    # once in the LLM input and preserve both semantic roles in metadata.
    deduped: dict[tuple[str, Any, Any, str], dict[str, Any]] = {}
    for section in selected:
        key = section_key(section)
        if key not in deduped:
            section["target_section_types"] = [section["section_type"]]
            deduped[key] = section
        elif section["section_type"] not in deduped[key]["target_section_types"]:
            deduped[key]["target_section_types"].append(section["section_type"])

    return list(deduped.values()), {
        "method": "Graph provenance alternatives + full-document rejection + section deduplication",
        "markdown_chars": markdown_chars,
        "markdown_heading_count": heading_count,
        "missing_targets": missing_targets,
        "rejected_sections": rejected,
    }


def make_record(summary: dict[str, Any], base: dict[str, Any], summary_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    grounding = summary.get("section_grounding") or {}
    selected, selection_audit = choose_sections_for_input(summary)
    section_blocks = []
    for section in selected:
        label = ", ".join(section.get("target_section_types", [section["section_type"]]))
        heading = section["heading_path_text"]
        section_blocks.append(f"[{label}: {heading}]\n{section['text']}")

    # The Graph manifest uses short rec_* identifiers, which can repeat across
    # include/uncertain corpora. Preserve the composite screening ID instead.
    record_id = base.get("record_id") or summary.get("record_id", "")
    record = {
        "record_id": record_id,
        "candidate_id": summary.get("candidate_id") or base.get("candidate_id", ""),
        "source_record_id": base.get("source_record_id") or summary.get("record_id", ""),
        "source_corpus": summary.get("source_corpus") or base.get("source_corpus", ""),
        "title": summary.get("title") or base.get("title", ""),
        "abstract": base.get("abstract", ""),
        "doi": summary.get("doi") or base.get("doi", ""),
        "year": base.get("year", ""),
        "venue": base.get("venue", ""),
        "sources": base.get("sources", []),
        "selected_full_text_sections": "\n\n".join(section_blocks),
        "section_evidence": selected,
        "section_selection_audit": selection_audit,
        "docling_markdown": summary.get("source_markdown", ""),
        "docling_status": "docling_ok",
        "docling_graph_evidence_summary": rel(summary_path),
        "docling_graph_extraction_contract": summary.get("extraction_contract", ""),
        "docling_graph_model": "gpt-5.4-mini",
        "docling_graph_provenance_path": summary.get("provenance_path", ""),
        "docling_graph_provenance_bind_stats": summary.get("provenance_bind_stats", {}),
        "docling_graph_provenance_resolution": summary.get("provenance_resolution", ""),
    }
    audit = {
        "record_id": record_id,
        "candidate_id": record["candidate_id"],
        "source_corpus": record["source_corpus"],
        "title": record["title"],
        "status": grounding.get("status", "no_grounded_sections"),
        "section_count": len(selected),
        "missing_targets": " | ".join(selection_audit["missing_targets"]),
        "rejected_full_document_sections": sum(
            item.get("reason", "").startswith("full_document_like")
            for item in selection_audit["rejected_sections"]
        ),
        "data_source_headings": " | ".join(s["heading_path_text"] for s in selected if s["section_type"] == "data_source"),
        "input_representation_headings": " | ".join(s["heading_path_text"] for s in selected if s["section_type"] == "input_representation"),
        "data_source_chars": sum(len(s["text"]) for s in selected if s["section_type"] == "data_source"),
        "input_representation_chars": sum(len(s["text"]) for s in selected if s["section_type"] == "input_representation"),
        "selected_full_text_sections_chars": len(record["selected_full_text_sections"]),
        "provenance_unresolved": (summary.get("provenance_bind_stats") or {}).get("unresolved", ""),
        "graph_summary": rel(summary_path),
    }
    return record, audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph-output", type=Path, default=DEFAULT_GRAPH_OUTPUT)
    parser.add_argument("--base-records", type=Path, default=DEFAULT_BASE_RECORDS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--require-both-targets",
        action="store_true",
        help="Keep only records with both data_source and input_representation sections.",
    )
    args = parser.parse_args()

    summaries = graph_summaries(args.graph_output)
    index = base_record_index(args.base_records)
    records: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    missing_base: list[str] = []
    for summary_path in summaries:
        summary = load_json(summary_path)
        base = lookup_base(summary, index)
        if not base:
            missing_base.append(summary.get("record_id", summary_path.parent.name))
        record, audit = make_record(summary, base, summary_path)
        records.append(record)
        audits.append(audit)

    excluded_records: list[dict[str, Any]] = []
    if args.require_both_targets:
        kept_records: list[dict[str, Any]] = []
        kept_audits: list[dict[str, Any]] = []
        for record, audit in zip(records, audits):
            target_types = {
                target_type
                for section in record["section_evidence"]
                for target_type in section.get("target_section_types", [section["section_type"]])
            }
            if {"data_source", "input_representation"} <= target_types:
                kept_records.append(record)
                kept_audits.append(audit)
            else:
                excluded_records.append({
                    "record_id": record["record_id"],
                    "candidate_id": record["candidate_id"],
                    "title": record["title"],
                    "missing_targets": audit.get("missing_targets", ""),
                    "section_count": audit.get("section_count", 0),
                    "selection_audit": record.get("section_selection_audit", {}),
                })
        records, audits = kept_records, kept_audits

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.output_dir / "fulltext_screening_input.json", records)
    with (args.output_dir / "fulltext_screening_input.jsonl").open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    with (args.output_dir / "fulltext_section_audit.csv").open("w", newline="", encoding="utf-8") as f:
        fields = list(audits[0].keys()) if audits else []
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(audits)
    write_json(args.output_dir / "run_metadata.json", {
        "created_by": "scripts/docling/build_docling_graph_pipeline_input.py",
        "graph_output": rel(args.graph_output),
        "base_records": rel(args.base_records),
        "require_both_targets": args.require_both_targets,
        "records": len(records),
        "source_records_before_filter": len(records) + len(excluded_records),
        "section_type_counts": dict(Counter(
            target_type
            for record in records
            for section in record["section_evidence"]
            for target_type in section.get("target_section_types", [section["section_type"]])
        )),
        "records_with_data_source": sum(any("data_source" in s.get("target_section_types", [s["section_type"]]) for s in r["section_evidence"]) for r in records),
        "records_with_input_representation": sum(any("input_representation" in s.get("target_section_types", [s["section_type"]]) for s in r["section_evidence"]) for r in records),
        "records_with_both_targets": sum(
            {target_type for s in r["section_evidence"] for target_type in s.get("target_section_types", [s["section_type"]])}
            >= {"data_source", "input_representation"}
            for r in records
        ),
        "records_with_any_selected_section": sum(bool(r["section_evidence"]) for r in records),
        "rejected_full_document_sections": sum(a["rejected_full_document_sections"] for a in audits),
        "records_with_missing_targets": sum(bool(a["missing_targets"]) for a in audits),
        "missing_base_records": missing_base,
        "excluded_records": excluded_records,
        "no_section_truncation": True,
        "note": "Input uses full heading-boundary sections reconstructed from Docling Graph provenance. Identical sections are emitted once, root/document-level sections covering >=90% of markdown are rejected, and no max-section-chars cap is applied.",
    })
    print(json.dumps({
        "records": len(records),
        "output": rel(args.output_dir / "fulltext_screening_input.json"),
        "jsonl": rel(args.output_dir / "fulltext_screening_input.jsonl"),
        "audit": rel(args.output_dir / "fulltext_section_audit.csv"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
