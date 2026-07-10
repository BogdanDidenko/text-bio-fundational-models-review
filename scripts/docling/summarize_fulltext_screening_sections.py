#!/usr/bin/env python3
"""Summarize Docling sections used as full-text screening input."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTEXT_DIR = ROOT / "data/fulltext_screening_context_2026-07-09_compact_v2"
DEFAULT_RUN_DIR = ROOT / "data/screening_codex_fulltext_2026-07-09"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_records(input_path: Path) -> dict[str, dict[str, Any]]:
    payload = read_json(input_path)
    return {str(row["record_id"]): row for row in payload["records"]}


def prompt_counts(run_dir: Path) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for role in ["scope_reviewer", "architecture_reviewer", "adjudicator"]:
        role_dir = run_dir / "role_logs" / role
        prompts = sorted(role_dir.glob("batch_*.prompt.txt"))
        counts[role] = {
            "prompt_files": len(prompts),
            "with_selected_full_text_sections": 0,
            "with_section_evidence": 0,
            "with_first_pass_outputs": 0,
        }
        for path in prompts:
            text = path.read_text(encoding="utf-8", errors="replace")
            counts[role]["with_selected_full_text_sections"] += int(
                '"selected_full_text_sections"' in text or '"full_text_context"' in text
            )
            counts[role]["with_section_evidence"] += int('"section_evidence"' in text)
            counts[role]["with_first_pass_outputs"] += int('"first_pass_outputs"' in text)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context-dir", default=str(DEFAULT_CONTEXT_DIR))
    parser.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    args = parser.parse_args()

    context_dir = Path(args.context_dir)
    run_dir = Path(args.run_dir)
    input_path = context_dir / "fulltext_screening_input.json"
    audit_path = context_dir / "fulltext_section_audit.csv"
    out_dir = run_dir / "section_input_stats"
    out_dir.mkdir(parents=True, exist_ok=True)

    records = load_records(input_path)
    audit_rows = list(csv.DictReader(audit_path.open(newline="", encoding="utf-8")))

    section_type_instances: Counter[str] = Counter()
    section_type_records: dict[str, set[str]] = defaultdict(set)
    heading_instances: Counter[tuple[str, str]] = Counter()
    heading_records: dict[tuple[str, str], set[str]] = defaultdict(set)
    heading_by_source: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    heading_chars: dict[tuple[str, str], list[int]] = defaultdict(list)
    status_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    selected_count_distribution: Counter[int] = Counter()

    per_record_rows: list[dict[str, Any]] = []
    section_instance_rows: list[dict[str, Any]] = []

    for audit in audit_rows:
        rid = audit["record_id"]
        rec = records[rid]
        selected = json.loads(audit["selected_sections_json"] or "[]")
        status_counts[audit["context_status"]] += 1
        source_counts[audit["source_corpus"]] += 1
        selected_count_distribution[len(selected)] += 1

        headings_by_type: dict[str, list[str]] = defaultdict(list)
        original_chars = 0
        for idx, section in enumerate(selected, 1):
            stype = section["section_type"]
            heading = section["heading"]
            key = (stype, heading)
            section_type_instances[stype] += 1
            section_type_records[stype].add(rid)
            heading_instances[key] += 1
            heading_records[key].add(rid)
            heading_by_source[key][audit["source_corpus"]] += 1
            chars = int(section.get("original_chars") or 0)
            heading_chars[key].append(chars)
            original_chars += chars
            headings_by_type[stype].append(heading)
            section_instance_rows.append(
                {
                    "record_id": rid,
                    "source_corpus": audit["source_corpus"],
                    "title": audit["title"],
                    "section_index": idx,
                    "section_type": stype,
                    "heading": heading,
                    "heading_level": section.get("heading_level", ""),
                    "line_start": section.get("line_start", ""),
                    "line_end": section.get("line_end", ""),
                    "original_chars": chars,
                    "markdown": audit["markdown"],
                }
            )

        per_record_rows.append(
            {
                "record_id": rid,
                "source_record_id": audit["source_record_id"],
                "source_corpus": audit["source_corpus"],
                "context_status": audit["context_status"],
                "selected_section_count": len(selected),
                "selected_full_text_sections_chars": len(
                    rec.get("selected_full_text_sections", rec.get("full_text_context", ""))
                ),
                "abstract_chars": len(rec.get("abstract", "")),
                "selected_original_chars_total": original_chars,
                "abstract_headings": " | ".join(headings_by_type.get("abstract", [])),
                "introduction_headings": " | ".join(headings_by_type.get("introduction", [])),
                "discussion_conclusion_headings": " | ".join(headings_by_type.get("discussion_conclusion", [])),
                "data_representation_headings": " | ".join(headings_by_type.get("data_representation", [])),
                "document_opening_headings": " | ".join(headings_by_type.get("document_opening", [])),
                "docling_markdown": rec.get("docling_markdown", ""),
                "title": audit["title"],
                "doi": audit["doi"],
            }
        )

    heading_rows = []
    for (stype, heading), count in heading_instances.most_common():
        chars = heading_chars[(stype, heading)]
        heading_rows.append(
            {
                "section_type": stype,
                "heading": heading,
                "occurrences": count,
                "record_count": len(heading_records[(stype, heading)]),
                "include_occurrences": heading_by_source[(stype, heading)].get("include", 0),
                "uncertain_occurrences": heading_by_source[(stype, heading)].get("uncertain", 0),
                "avg_original_chars": round(mean(chars), 1) if chars else 0,
                "max_original_chars": max(chars) if chars else 0,
            }
        )

    type_rows = []
    for stype, count in section_type_instances.most_common():
        type_rows.append(
            {
                "section_type": stype,
                "occurrences": count,
                "record_count": len(section_type_records[stype]),
            }
        )

    write_csv(
        out_dir / "section_input_by_record.csv",
        per_record_rows,
        [
            "record_id",
            "source_record_id",
            "source_corpus",
            "context_status",
            "selected_section_count",
            "selected_full_text_sections_chars",
            "abstract_chars",
            "selected_original_chars_total",
            "abstract_headings",
            "introduction_headings",
            "discussion_conclusion_headings",
            "data_representation_headings",
            "document_opening_headings",
            "docling_markdown",
            "title",
            "doi",
        ],
    )
    write_csv(
        out_dir / "section_instances.csv",
        section_instance_rows,
        [
            "record_id",
            "source_corpus",
            "title",
            "section_index",
            "section_type",
            "heading",
            "heading_level",
            "line_start",
            "line_end",
            "original_chars",
            "markdown",
        ],
    )
    write_csv(
        out_dir / "section_heading_counts.csv",
        heading_rows,
        [
            "section_type",
            "heading",
            "occurrences",
            "record_count",
            "include_occurrences",
            "uncertain_occurrences",
            "avg_original_chars",
            "max_original_chars",
        ],
    )
    write_csv(out_dir / "section_type_counts.csv", type_rows, ["section_type", "occurrences", "record_count"])

    prompt_summary = prompt_counts(run_dir)
    summary = {
        "input": rel(input_path),
        "audit": rel(audit_path),
        "run_dir": rel(run_dir),
        "record_count": len(records),
        "source_counts": dict(source_counts),
        "context_status_counts": dict(status_counts),
        "selected_section_count_distribution": dict(sorted(selected_count_distribution.items())),
        "section_type_counts": type_rows,
        "top_heading_counts": heading_rows[:30],
        "agent_prompt_counts": prompt_summary,
        "agent_input_fields": {
            "scope_reviewer": [
                "record_id",
                "candidate_id",
                "source_record_id",
                "source_corpus",
                "title",
                "abstract",
                "doi",
                "year",
                "venue",
                "sources",
                "selected_full_text_sections",
                "section_evidence",
                "docling_markdown",
            ],
            "architecture_reviewer": [
                "record_id",
                "candidate_id",
                "source_record_id",
                "source_corpus",
                "title",
                "abstract",
                "doi",
                "year",
                "venue",
                "sources",
                "selected_full_text_sections",
                "section_evidence",
                "docling_markdown",
            ],
            "adjudicator": [
                "record_id",
                "candidate_id",
                "source_record_id",
                "source_corpus",
                "title",
                "abstract",
                "doi",
                "year",
                "venue",
                "sources",
                "selected_full_text_sections",
                "section_evidence",
                "docling_markdown",
                "first_pass_outputs",
            ],
        },
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Full-Text Screening Section Input Statistics",
        "",
        "This file summarizes the exact Docling-derived sections used to build the full-text agent screening input.",
        "",
        "## Inputs",
        "",
        f"- Screening input JSON: `{rel(input_path)}`",
        f"- Section audit CSV: `{rel(audit_path)}`",
        f"- Screening run: `{rel(run_dir)}`",
        "",
        "## Record Counts",
        "",
        f"- Total records: **{len(records)}**",
    ]
    for source, count in source_counts.most_common():
        md_lines.append(f"- `{source}` records: **{count}**")
    md_lines.extend(["", "## Context Status", ""])
    for status, count in status_counts.most_common():
        md_lines.append(f"- `{status}`: **{count}**")
    md_lines.extend(["", "## Selected Section Count Per Record", ""])
    for count, records_with_count in sorted(selected_count_distribution.items()):
        md_lines.append(f"- `{count}` selected sections: **{records_with_count}** records")
    md_lines.extend(["", "## Section Type Counts", "", "| Section type | Section instances | Records with type |", "|---|---:|---:|"])
    for row in type_rows:
        md_lines.append(f"| `{row['section_type']}` | {row['occurrences']} | {row['record_count']} |")
    md_lines.extend(["", "## Top Exact Section Headings Used", "", "| Section type | Heading | Occurrences | Records | Include | Uncertain |", "|---|---|---:|---:|---:|---:|"])
    for row in heading_rows[:40]:
        md_lines.append(
            f"| `{row['section_type']}` | {row['heading']} | {row['occurrences']} | {row['record_count']} | {row['include_occurrences']} | {row['uncertain_occurrences']} |"
        )
    md_lines.extend(
        [
            "",
            "## What Each Agent Role Received",
            "",
            "All roles used the same full-text evidence fields. The adjudicator additionally received the first-pass reviewer outputs and Python gate result.",
            "",
            "| Role | Prompt files | Prompts with `selected_full_text_sections` | Prompts with `section_evidence` | Prompts with `first_pass_outputs` |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for role, counts in prompt_summary.items():
        md_lines.append(
            f"| `{role}` | {counts['prompt_files']} | {counts['with_selected_full_text_sections']} | {counts['with_section_evidence']} | {counts['with_first_pass_outputs']} |"
        )
    md_lines.extend(
        [
            "",
            "Agent prompts did not include raw PDFs, `section_evidence`, or `docling_markdown`. The evidence supplied for analysis was title/abstract metadata plus the complete selected text in `selected_full_text_sections`; structured evidence and Docling markdown remain in input records for auditability only.",
            "",
            "## Output Tables",
            "",
            "- `section_input_by_record.csv`: one row per screened record, with the exact headings selected for that record.",
            "- `section_instances.csv`: one row per selected section instance.",
            "- `section_heading_counts.csv`: aggregate counts by exact heading and section type.",
            "- `section_type_counts.csv`: aggregate counts by section type.",
            "- `summary.json`: machine-readable version of this summary.",
        ]
    )
    (out_dir / "SECTION_INPUT_STATS.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps({"out_dir": rel(out_dir), "records": len(records)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
