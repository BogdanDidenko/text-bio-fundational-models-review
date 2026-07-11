#!/usr/bin/env python3
"""Audit the canonical VLM Docling corpus and final screening evidence inputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from docling_core.types.doc import DoclingDocument


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = (
    ROOT
    / "data/docling_include_vlm_52_2026-07-10_nolimits/manifests"
    / "canonical_docling_profile_manifest.csv"
)
DEFAULT_SCREENING = (
    ROOT
    / "data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10"
    / "input_records.json"
)
DEFAULT_OUTPUT = ROOT / "data/taxonomy_planning_2026-07-10"
SAMPLE_IDS = [
    "full_2026-07-06__rec_001519",
    "july_update_2026-07-06__rec_000060",
    "full_2026-07-06__rec_000060",
    "full_2026-07-06__rec_001218",
    "full_2026-07-06__rec_000063",
    "full_2026-07-06__rec_001773",
    "full_2026-07-06__rec_000086",
    "full_2026-07-06__rec_001838",
    "full_2026-07-06__rec_003188",
    "full_2026-07-06__rec_003629",
]


def resolve(path: str | Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def rel(path: str | Path) -> str:
    value = resolve(path)
    try:
        return str(value.relative_to(ROOT))
    except ValueError:
        return str(value)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def normalized_heading(value: str) -> str:
    value = re.sub(r"^#+\s*", "", value.casefold()).strip()
    value = re.sub(r"^\d+(?:\.\d+)*[.)]?\s+", "", value)
    return "".join(char for char in value if char.isalnum())


def markdown_sections(text: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    headings: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,8})\s+(.+?)\s*$", line)
        if match:
            headings.append((index, len(match.group(1)), match.group(2)))
    sections = []
    for position, (start, level, heading) in enumerate(headings):
        end = len(lines)
        for next_start, next_level, _ in headings[position + 1 :]:
            if next_level <= level:
                end = next_start
                break
        body = "\n".join(lines[start + 1 : end]).strip()
        sections.append(
            {
                "heading": heading,
                "heading_key": normalized_heading(heading),
                "level": level,
                "line_start": start + 1,
                "line_end": end,
                "text": body,
                "chars": len(body),
            }
        )
    return sections


def percentile(values: list[int], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def distribution(values: list[int]) -> dict[str, float | int]:
    if not values:
        return {"count": 0, "min": 0, "p25": 0, "median": 0, "p75": 0, "max": 0}
    return {
        "count": len(values),
        "min": min(values),
        "p25": round(percentile(values, 0.25), 1),
        "median": round(statistics.median(values), 1),
        "p75": round(percentile(values, 0.75), 1),
        "max": max(values),
    }


def picture_description(picture: Any) -> str:
    meta = getattr(picture, "meta", None)
    description = getattr(meta, "description", None)
    return str(getattr(description, "text", "") or "")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_title(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--screening-input", type=Path, default=DEFAULT_SCREENING)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with args.manifest.open(newline="", encoding="utf-8") as stream:
        manifest = list(csv.DictReader(stream))
    raw_screening = read_json(args.screening_input)
    screening = raw_screening.get("records", raw_screening) if isinstance(raw_screening, dict) else raw_screening
    screening_by_id: dict[str, dict[str, Any]] = {}
    for record in screening:
        for key in (record.get("record_id"), record.get("candidate_id")):
            if key:
                screening_by_id[str(key)] = record

    paper_rows: list[dict[str, Any]] = []
    heading_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for row in manifest:
        candidate_id = row["candidate_id"]
        doc_path = resolve(row["docling_json"])
        markdown_path = resolve(row["markdown"])
        screen = screening_by_id.get(candidate_id, {})
        try:
            document = DoclingDocument.load_from_json(doc_path)
            stored_markdown = markdown_path.read_text(encoding="utf-8")
            exported_markdown = document.export_to_markdown()
        except Exception as exc:
            failures.append({"candidate_id": candidate_id, "error": repr(exc)})
            continue

        items = list(document.iterate_items())
        items_with_provenance = sum(bool(getattr(item, "prov", None)) for item, _ in items)
        descriptions = [picture_description(picture) for picture in document.pictures]
        selected = str(screen.get("selected_full_text_sections") or "")
        abstract = str(screen.get("abstract") or "")
        evidence = screen.get("section_evidence") or []
        selected_section_chars = [int(section.get("original_chars") or len(section.get("text") or "")) for section in evidence]
        selected_ratio = len(selected) / len(stored_markdown) if stored_markdown else 0.0
        paper_rows.append(
            {
                "candidate_id": candidate_id,
                "source_record_id": row.get("source_record_id", ""),
                "title": row.get("title", ""),
                "screening_input_found": bool(screen),
                "abstract_chars": len(abstract),
                "selected_full_text_sections_chars": len(selected),
                "selected_section_count": len(evidence),
                "selected_section_chars_total": sum(selected_section_chars),
                "selected_to_canonical_markdown_ratio": round(selected_ratio, 6),
                "docling_json": rel(doc_path),
                "markdown": rel(markdown_path),
                "source_pdf": rel(row["source_pdf"]),
                "source_pdf_sha256": file_sha256(resolve(row["source_pdf"])),
                "document_name": document.name,
                "texts": len(document.texts),
                "tables": len(document.tables),
                "pictures": len(document.pictures),
                "groups": len(document.groups),
                "body_children": len(document.body.children),
                "iterated_items": len(items),
                "items_with_provenance": items_with_provenance,
                "stored_markdown_chars": len(stored_markdown),
                "exported_markdown_chars": len(exported_markdown),
                "stored_export_sha256_equal": hashlib.sha256(stored_markdown.encode()).hexdigest()
                == hashlib.sha256(exported_markdown.encode()).hexdigest(),
                "picture_descriptions": sum(bool(value) for value in descriptions),
                "all_pictures_described": len(descriptions) == sum(bool(value) for value in descriptions),
            }
        )

        for section in evidence:
            heading_path = section.get("heading_path_text") or " > ".join(section.get("heading_path") or [])
            heading_rows.append(
                {
                    "candidate_id": candidate_id,
                    "title": row.get("title", ""),
                    "target_section_types": ";".join(section.get("target_section_types") or [section.get("section_type", "")]),
                    "heading_path": heading_path,
                    "heading": section.get("heading", ""),
                    "chars": int(section.get("original_chars") or len(section.get("text") or "")),
                    "coverage_ratio_recorded": section.get("section_coverage_ratio", ""),
                    "contains_evidence_quote": section.get("contains_evidence_quote", ""),
                    "contains_chunk_excerpt": section.get("contains_chunk_excerpt", ""),
                }
            )

        if candidate_id in SAMPLE_IDS:
            sections = markdown_sections(stored_markdown)
            recovered = []
            for section in evidence:
                heading_path = section.get("heading_path") or []
                target = str(section.get("heading") or (heading_path[-1] if heading_path else ""))
                matches = [item for item in sections if item["heading_key"] == normalized_heading(target)]
                recovered.append(
                    {
                        "target_section_types": section.get("target_section_types") or [section.get("section_type", "")],
                        "requested_heading": target,
                        "matching_heading_count": len(matches),
                        "recovered_nonempty": any(item["chars"] > 0 for item in matches),
                        "candidate_recovered_chars": [item["chars"] for item in matches],
                    }
                )
            sample_rows.append(
                {
                    "candidate_id": candidate_id,
                    "title": row.get("title", ""),
                    "docling_load_ok": True,
                    "native_structure": {
                        "texts": len(document.texts),
                        "tables": len(document.tables),
                        "pictures": len(document.pictures),
                        "groups": len(document.groups),
                        "body_children": len(document.body.children),
                        "items_with_provenance": items_with_provenance,
                    },
                    "markdown_export_ok": bool(exported_markdown),
                    "all_pictures_described": all(bool(value) for value in descriptions),
                    "selected_sections": recovered,
                }
            )

    selected_lengths = [int(row["selected_full_text_sections_chars"]) for row in paper_rows]
    abstract_lengths = [int(row["abstract_chars"]) for row in paper_rows]
    markdown_lengths = [int(row["stored_markdown_chars"]) for row in paper_rows]
    section_lengths = [int(row["chars"]) for row in heading_rows]
    heading_counts = Counter(row["heading_path"] for row in heading_rows)
    pdf_hashes: dict[str, list[dict[str, Any]]] = {}
    for row in paper_rows:
        pdf_hashes.setdefault(str(row["source_pdf_sha256"]), []).append(row)
    exact_pdf_duplicates = [
        [
            {
                "candidate_id": item["candidate_id"],
                "title": item["title"],
                "source_pdf": item["source_pdf"],
            }
            for item in group
        ]
        for group in pdf_hashes.values()
        if len(group) > 1
    ]
    selected_hashes: dict[str, list[dict[str, Any]]] = {}
    for record in screening:
        candidate_id = str(record.get("candidate_id") or record.get("record_id") or "")
        if candidate_id not in {row["candidate_id"] for row in paper_rows}:
            continue
        for section in record.get("section_evidence") or []:
            text = " ".join(str(section.get("text") or "").casefold().split())
            key = hashlib.sha256(text.encode()).hexdigest()
            selected_hashes.setdefault(key, []).append(
                {
                    "candidate_id": candidate_id,
                    "heading_path": section.get("heading_path_text", ""),
                }
            )
    exact_section_duplicates = [group for group in selected_hashes.values() if len(group) > 1]
    near_title_pairs = []
    for index, left in enumerate(paper_rows):
        for right in paper_rows[index + 1 :]:
            similarity = SequenceMatcher(
                None, normalized_title(str(left["title"])), normalized_title(str(right["title"]))
            ).ratio()
            if similarity >= 0.82:
                near_title_pairs.append(
                    {
                        "left_candidate_id": left["candidate_id"],
                        "right_candidate_id": right["candidate_id"],
                        "left_title": left["title"],
                        "right_title": right["title"],
                        "title_similarity": round(similarity, 6),
                    }
                )
    summary = {
        "canonical_manifest": rel(args.manifest),
        "screening_input": rel(args.screening_input),
        "canonical_profiles": len(manifest),
        "profiles_loaded": len(paper_rows),
        "load_failures": failures,
        "screening_inputs_matched": sum(bool(row["screening_input_found"]) for row in paper_rows),
        "profiles_with_empty_abstract": sum(int(row["abstract_chars"]) == 0 for row in paper_rows),
        "profiles_with_empty_selected_sections": sum(
            int(row["selected_full_text_sections_chars"]) == 0 for row in paper_rows
        ),
        "profiles_with_no_selected_section_objects": sum(int(row["selected_section_count"]) == 0 for row in paper_rows),
        "profiles_with_selected_ratio_ge_0_8": sum(
            float(row["selected_to_canonical_markdown_ratio"]) >= 0.8 for row in paper_rows
        ),
        "profiles_with_all_pictures_described": sum(bool(row["all_pictures_described"]) for row in paper_rows),
        "profiles_with_exact_stored_markdown_export": sum(
            bool(row["stored_export_sha256_equal"]) for row in paper_rows
        ),
        "profiles_with_tables": sum(int(row["tables"]) > 0 for row in paper_rows),
        "pictures": sum(int(row["pictures"]) for row in paper_rows),
        "picture_descriptions": sum(int(row["picture_descriptions"]) for row in paper_rows),
        "tables": sum(int(row["tables"]) for row in paper_rows),
        "items_with_provenance": sum(int(row["items_with_provenance"]) for row in paper_rows),
        "abstract_chars": distribution(abstract_lengths),
        "selected_full_text_sections_chars": distribution(selected_lengths),
        "individual_selected_section_chars": distribution(section_lengths),
        "canonical_markdown_chars": distribution(markdown_lengths),
        "selected_section_objects": len(heading_rows),
        "unique_selected_heading_paths": len(heading_counts),
        "duplicate_heading_paths_across_papers": [
            {"heading_path": heading, "count": count}
            for heading, count in heading_counts.most_common()
            if count > 1
        ],
        "sample_ids": SAMPLE_IDS,
        "sample_profiles_verified": len(sample_rows),
        "sample_section_targets": sum(len(row["selected_sections"]) for row in sample_rows),
        "sample_section_targets_recovered": sum(
            section["recovered_nonempty"]
            for row in sample_rows
            for section in row["selected_sections"]
        ),
        "exact_source_pdf_duplicate_groups": exact_pdf_duplicates,
        "exact_selected_section_duplicate_groups": exact_section_duplicates,
        "near_title_pairs_similarity_ge_0_82": near_title_pairs,
    }

    write_csv(args.output_dir / "paper_audit.csv", paper_rows)
    write_csv(args.output_dir / "selected_section_headings.csv", heading_rows)
    write_json(args.output_dir / "corpus_audit.json", summary)
    write_json(args.output_dir / "representative_sample_validation.json", sample_rows)

    report = [
        "# Canonical Corpus and Screening-Input Audit",
        "",
        f"- Canonical profiles: {summary['profiles_loaded']}/{summary['canonical_profiles']} loaded.",
        f"- Screening inputs matched: {summary['screening_inputs_matched']}/{summary['canonical_profiles']}.",
        f"- Pictures with native descriptions: {summary['picture_descriptions']}/{summary['pictures']}.",
        f"- Stored Markdown exactly reproduced from native profiles: {summary['profiles_with_exact_stored_markdown_export']}/{summary['canonical_profiles']}.",
        f"- Tables represented in native profiles: {summary['tables']}.",
        f"- Native items carrying provenance: {summary['items_with_provenance']}.",
        f"- Empty abstracts: {summary['profiles_with_empty_abstract']}.",
        f"- Empty selected full-text inputs: {summary['profiles_with_empty_selected_sections']}.",
        f"- Selected inputs covering >=80% of canonical Markdown: {summary['profiles_with_selected_ratio_ge_0_8']}.",
        f"- Representative section targets recovered by heading boundary: {summary['sample_section_targets_recovered']}/{summary['sample_section_targets']}.",
        f"- Exact source-PDF duplicate groups: {len(summary['exact_source_pdf_duplicate_groups'])}.",
        f"- Near-title linkage candidates (similarity >=0.82): {len(summary['near_title_pairs_similarity_ge_0_82'])}.",
        "",
        "## Length distributions",
        "",
        "| Evidence unit | Min | P25 | Median | P75 | Max |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, key in (
        ("Abstract", "abstract_chars"),
        ("Selected full-text input", "selected_full_text_sections_chars"),
        ("Individual selected section", "individual_selected_section_chars"),
        ("Canonical Markdown", "canonical_markdown_chars"),
    ):
        values = summary[key]
        report.append(
            f"| {label} | {values['min']} | {values['p25']} | {values['median']} | {values['p75']} | {values['max']} |"
        )
    report.extend(
        [
            "",
            "## Artifacts",
            "",
            "- `corpus_audit.json`: aggregate machine-readable audit.",
            "- `paper_audit.csv`: one row per canonical paper.",
            "- `selected_section_headings.csv`: one row per selected evidence section.",
            "- `representative_sample_validation.json`: native-structure and section-recovery checks for ten papers.",
        ]
    )
    (args.output_dir / "screening_input_audit.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
