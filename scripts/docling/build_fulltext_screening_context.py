#!/usr/bin/env python3
"""Build section-grounded screening inputs from Docling markdown outputs."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INCLUDE = ROOT / "data/docling_include_final_coverage_2026-07-09/final_docling_manifest.csv"
DEFAULT_UNCERTAIN = ROOT / "data/docling_uncertain_final_coverage_2026-07-09/final_docling_manifest.csv"
DEFAULT_OUT = ROOT / "data/fulltext_screening_context_2026-07-09"


@dataclass
class Section:
    level: int
    heading: str
    body: str
    start_line: int
    end_line: int


SECTION_RULES: dict[str, list[str]] = {
    "abstract": [
        r"^abstract$",
        r"^summary$",
    ],
    "introduction": [
        r"^introduction$",
        r"^\d+\.?\s*introduction$",
        r"^background$",
    ],
    "discussion_conclusion": [
        r"^discussion$",
        r"^\d+\.?\s*discussion$",
        r"^conclusion[s]?$",
        r"^\d+\.?\s*conclusion[s]?$",
        r"^discussion and conclusion[s]?$",
        r"^concluding remarks$",
    ],
    "data_representation": [
        r"\bdataset[s]?\b",
        r"\bdata collection\b",
        r"\bdata curation\b",
        r"\bdata preprocessing\b",
        r"\bpre-?processing\b",
        r"\btraining data\b",
        r"\bpretraining data\b",
        r"\bcorpus\b",
        r"\bmodel input\b",
        r"\binput representation\b",
        r"\brepresentation\b",
        r"\bfeature[- ]question[- ]answer\b",
        r"\bquestion[- ]answer pairs\b",
        r"\barchitecture\b",
        r"\bmodel architecture\b",
        r"\bmethods?\b",
        r"\bmaterials and methods\b",
    ],
}


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


def norm_heading(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text).strip()
    text = re.sub(r"^[\dA-Z]+(?:\.\d+)*\.?\s+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def parse_markdown_sections(path: Path) -> list[Section]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    headings: list[tuple[int, int, str]] = []
    for idx, line in enumerate(lines):
        match = re.match(r"^(#{1,8})\s+(.+?)\s*$", line)
        if match:
            headings.append((idx, len(match.group(1)), norm_heading(match.group(2))))
    sections: list[Section] = []
    for pos, (start, level, heading) in enumerate(headings):
        end = len(lines)
        for next_start, next_level, _ in headings[pos + 1 :]:
            if next_level <= level:
                end = next_start
                break
        body = clean_text("\n".join(lines[start + 1 : end]))
        if body:
            sections.append(Section(level=level, heading=heading, body=body, start_line=start + 1, end_line=end))
    return sections


def matches(section: Section, group: str) -> bool:
    heading = section.heading.lower()
    return any(re.search(pattern, heading) for pattern in SECTION_RULES[group])


def trim(text: str, max_chars: int) -> str:
    text = clean_text(text)
    if max_chars <= 0:
        return text
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 20]
    last_stop = max(cut.rfind(". "), cut.rfind("\n\n"), cut.rfind("; "))
    if last_stop > max_chars * 0.55:
        cut = cut[: last_stop + 1]
    return cut.rstrip() + " [truncated]"


def extract_document_opening(path: Path, max_chars: int) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    kept: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.fullmatch(r"\d+", stripped):
            continue
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            continue
        kept.append(stripped)
        if max_chars > 0 and len("\n".join(kept)) >= max_chars * 2:
            break
    return trim("\n".join(kept), max_chars)


def choose_sections(sections: list[Section], group: str, max_count: int) -> list[Section]:
    candidates = [s for s in sections if matches(s, group)]
    if group == "data_representation":
        availability_only = re.compile(r"\b(data availability|availability of data|code availability|supplementary data)\b", re.I)
        preferred = [s for s in candidates if not availability_only.search(s.heading)]
        candidates = preferred or candidates
        def priority(section: Section) -> tuple[int, int]:
            heading = section.heading.lower()
            if re.search(r"\b(input representation|model input|data representation|sample representation|embedding representation|question[- ]answer pairs?|feature[- ]question[- ]answer)\b", heading):
                return (0, section.start_line)
            if re.search(r"\b(dataset|datasets|data collection|data curation|data preprocessing|pre-?processing|training data|pretraining data|corpus)\b", heading):
                return (1, section.start_line)
            if re.search(r"\b(model architecture|architecture|model architecture and training|architecture and pretraining)\b", heading):
                return (2, section.start_line)
            if re.search(r"\b(methods?|materials and methods|methodology|online methods)\b", heading):
                return (3, section.start_line)
            return (4, section.start_line)

        candidates = sorted(candidates, key=priority)
    return candidates[:max_count]


def section_payload(section: Section, group: str, max_chars: int) -> dict[str, Any]:
    return {
        "section_type": group,
        "heading": section.heading,
        "heading_level": section.level,
        "line_start": section.start_line,
        "line_end": section.end_line,
        "text": trim(section.body, max_chars),
        "original_chars": len(section.body),
    }


def build_context(row: dict[str, str], max_section_chars: int) -> tuple[dict[str, Any], dict[str, Any]]:
    markdown = ROOT / row["markdown"] if row.get("markdown") else None
    if not markdown or not markdown.exists():
        return {}, {"status": "missing_markdown", "selected": []}

    sections = parse_markdown_sections(markdown)
    selected: list[dict[str, Any]] = []
    for group, max_count in [
        ("abstract", 1),
        ("introduction", 1),
        ("discussion_conclusion", 2),
        ("data_representation", 4),
    ]:
        for section in choose_sections(sections, group, max_count):
            selected.append(section_payload(section, group, max_section_chars))

    seen = set()
    deduped = []
    for item in selected:
        key = (item["section_type"], item["heading"], item["line_start"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    fallback_status = ""
    if not deduped:
        opening = extract_document_opening(markdown, max_section_chars)
        if opening:
            deduped.append(
                {
                    "section_type": "document_opening",
                    "heading": "Docling opening text",
                    "heading_level": 0,
                    "line_start": 1,
                    "line_end": 0,
                    "text": opening,
                    "original_chars": len(opening),
                }
            )
            fallback_status = "fallback_document_opening"

    context_parts = []
    for item in deduped:
        context_parts.append(
            f"[{item['section_type']}: {item['heading']}]\n{item['text']}"
        )
    context = "\n\n".join(context_parts)
    abstract_text = next((item["text"] for item in deduped if item["section_type"] == "abstract"), "")
    audit = {
        "status": fallback_status or ("ok" if deduped else "no_matching_sections"),
        "markdown": rel(markdown),
        "selected": [
            {k: v for k, v in item.items() if k != "text"}
            for item in deduped
        ],
        "all_headings": [s.heading for s in sections],
    }
    payload = {
        "abstract": abstract_text,
        "full_text_context": context,
        "section_evidence": deduped,
        "docling_markdown": rel(markdown),
        "docling_chunks": row.get("chunks", ""),
        "docling_status": row.get("final_docling_status", ""),
    }
    return payload, audit


def read_manifest(path: Path, corpus: str) -> list[dict[str, str]]:
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("final_docling_status") != "docling_ok":
                continue
            rows.append({**row, "source_corpus": corpus})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-manifest", default=str(DEFAULT_INCLUDE))
    parser.add_argument("--uncertain-manifest", default=str(DEFAULT_UNCERTAIN))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT))
    parser.add_argument(
        "--max-section-chars",
        type=int,
        default=0,
        help="Maximum characters per selected section; 0 keeps full selected sections.",
    )
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    rows.extend(read_manifest(Path(args.include_manifest), "include"))
    rows.extend(read_manifest(Path(args.uncertain_manifest), "uncertain"))
    if args.limit:
        rows = rows[: args.limit]

    records = []
    audit_rows = []
    heading_counter: Counter[str] = Counter()
    selected_heading_counter: Counter[str] = Counter()
    for row in rows:
        context, audit = build_context(row, args.max_section_chars)
        for heading in audit.get("all_headings", []):
            heading_counter[heading.lower()] += 1
        for item in audit.get("selected", []):
            selected_heading_counter[f"{item['section_type']} | {item['heading'].lower()}"] += 1

        record = {
            "record_id": row.get("candidate_id") or row.get("record_id"),
            "source_record_id": row.get("record_id", ""),
            "candidate_id": row.get("candidate_id", ""),
            "source_corpus": row.get("source_corpus", ""),
            "title": row.get("title", ""),
            "doi": row.get("doi", ""),
            "year": row.get("year", ""),
            "venue": row.get("venue", ""),
            "sources": [],
            **context,
        }
        records.append(record)
        audit_rows.append(
            {
                "record_id": record["record_id"],
                "source_record_id": record["source_record_id"],
                "source_corpus": record["source_corpus"],
                "title": record["title"],
                "doi": record["doi"],
                "docling_status": row.get("final_docling_status", ""),
                "context_status": audit["status"],
                "markdown": audit.get("markdown", ""),
                "selected_section_count": len(audit.get("selected", [])),
                "selected_sections_json": json.dumps(audit.get("selected", []), ensure_ascii=False),
            }
        )

    input_payload = {
        "metadata": {
            "created_by": "scripts/docling/build_fulltext_screening_context.py",
            "include_manifest": rel(args.include_manifest),
            "uncertain_manifest": rel(args.uncertain_manifest),
            "max_section_chars": args.max_section_chars,
            "record_count": len(records),
            "note": "Records contain title, extracted abstract, and selected Docling-derived full_text_context sections for full-text screening. Full articles are not embedded unless a selected section itself spans the article.",
        },
        "records": records,
    }
    (outdir / "fulltext_screening_input.json").write_text(
        json.dumps(input_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with (outdir / "fulltext_section_audit.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(audit_rows[0].keys()) if audit_rows else [])
        writer.writeheader()
        writer.writerows(audit_rows)
    (outdir / "heading_frequency.json").write_text(
        json.dumps(
            {
                "all_headings": heading_counter.most_common(),
                "selected_headings": selected_heading_counter.most_common(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "records": len(records),
                "output": rel(outdir / "fulltext_screening_input.json"),
                "audit": rel(outdir / "fulltext_section_audit.csv"),
                "heading_frequency": rel(outdir / "heading_frequency.json"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
