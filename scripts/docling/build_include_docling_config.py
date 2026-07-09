#!/usr/bin/env python3
"""Build a no-VLM Docling config for INCLUDE screening records with PDFs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MASTER = REPO / "data/full_text_downloads_2026-07-07/master_manifest_complete.csv"
FULL_TEXT_ROOTS = [
    REPO / "data/full_text_downloads_2026-07-07",
    REPO / "data/screening_codex_2026-06-10/full_texts",
    REPO / "data/full_text_problem_retry_2026-07-08/manual_downloads",
    REPO / "data/full_text_include_missing_retry_2026-07-09",
]
OUT_CONFIG = REPO / "scripts/docling/config_docling_include_no_vlm_2026-07-09.json"
OUT_CSV = REPO / "data/docling_include_no_vlm_2026-07-09_pdf_mapping.csv"
OUT_MD = REPO / "data/docling_include_no_vlm_2026-07-09_pdf_mapping.md"


def rel(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def norm(value: str) -> str:
    return value.lower().replace("-", "_")


def is_pdf_candidate(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".pdf" and path.stat().st_size > 100_000


def score_pdf(path: Path) -> tuple[int, int, int, int, str]:
    text = norm(str(path))
    return (
        0 if "manual" in text or "browser" in text else 1,
        0 if "openalex_content" in text else 1,
        0 if "europepmc" in text else 1,
        -path.stat().st_size,
        str(path),
    )


def pdfs_in_folder(folder: str) -> list[Path]:
    if not folder:
        return []
    path = Path(folder)
    if not path.is_absolute():
        path = REPO / path
    if not path.exists():
        return []
    return [p for p in path.rglob("*.pdf") if is_pdf_candidate(p)]


def choose_pdf(row: dict[str, str]) -> Path | None:
    candidate_id = row["candidate_id"]
    record_id = row["record_id"]
    pdfs: list[Path] = []

    pdfs.extend(pdfs_in_folder(row.get("folder", "")))

    needle_values = {
        norm(candidate_id),
        norm(candidate_id.replace("__", "_")),
    }
    for root in FULL_TEXT_ROOTS:
        if not root.exists():
            continue
        for pdf in root.rglob("*.pdf"):
            if not is_pdf_candidate(pdf):
                continue
            text = norm(str(pdf.relative_to(REPO)))
            if any(needle in text for needle in needle_values):
                pdfs.append(pdf)

    # Previous June full-text folders are keyed by record_id only.
    if row.get("source_run") == "june_update_2026-06-10":
        old_root = REPO / "data/screening_codex_2026-06-10/full_texts"
        if old_root.exists():
            for pdf in old_root.rglob("*.pdf"):
                if is_pdf_candidate(pdf) and record_id in str(pdf):
                    pdfs.append(pdf)

    unique = sorted(set(pdfs), key=score_pdf)
    return unique[0] if unique else None


def main() -> int:
    rows = list(csv.DictReader(MASTER.open(encoding="utf-8")))
    include = [row for row in rows if row.get("decision") == "INCLUDE"]

    mapping_rows: list[dict[str, Any]] = []
    pdf_items: list[dict[str, str]] = []
    for row in include:
        pdf = choose_pdf(row)
        mapping_row = {
            "candidate_id": row["candidate_id"],
            "source_run": row.get("source_run", ""),
            "record_id": row["record_id"],
            "title": row.get("title", ""),
            "doi": row.get("doi", ""),
            "manifest_status": row.get("status", ""),
            "pdf_found": bool(pdf),
            "pdf_path": rel(pdf),
            "pdf_bytes": pdf.stat().st_size if pdf else "",
        }
        mapping_rows.append(mapping_row)
        if pdf:
            pdf_items.append(
                {
                    "candidate_id": row["candidate_id"],
                    "record_id": row["record_id"],
                    "path": rel(pdf),
                    "title": row.get("title", ""),
                    "doi": row.get("doi", ""),
                }
            )

    config = {
        "name": "docling_include_no_vlm_2026-07-09",
        "description": (
            "No-VLM Docling preprocessing batch for INCLUDE records from "
            "data/full_text_downloads_2026-07-07/master_manifest_complete.csv."
        ),
        "output_root": "data/docling_include_no_vlm_2026-07-09",
        "settings": {
            "picture_description_backend": "none",
            "do_ocr": False,
            "do_table_structure": True,
            "table_former_mode": "ACCURATE",
            "do_cell_matching": True,
            "generate_page_images": True,
            "generate_picture_images": True,
            "images_scale": 2.0,
            "do_formula_enrichment": False,
            "heading_hierarchy": {
                "enabled": True,
                "use_bookmarks": True,
                "use_numbering": True,
                "use_style": True,
            },
        },
        "source_manifest": rel(MASTER),
        "include_records_total": len(include),
        "pdf_records_total": len(pdf_items),
        "missing_pdf_records_total": len(include) - len(pdf_items),
        "pdfs": pdf_items,
    }

    OUT_CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(mapping_rows[0].keys()))
        writer.writeheader()
        writer.writerows(mapping_rows)

    missing = [row for row in mapping_rows if not row["pdf_found"]]
    lines = [
        "# INCLUDE records Docling no-VLM PDF mapping",
        "",
        f"- Source manifest: `{rel(MASTER)}`",
        f"- INCLUDE records: {len(include)}",
        f"- With PDF: {len(pdf_items)}",
        f"- Missing PDF: {len(missing)}",
        f"- Config: `{rel(OUT_CONFIG)}`",
        f"- CSV: `{rel(OUT_CSV)}`",
        "",
        "## Missing PDFs",
        "",
    ]
    if missing:
        lines.extend(
            f"- `{row['candidate_id']}` `{row['record_id']}` {row['title']}"
            for row in missing
        )
    else:
        lines.append("- none")
    lines.extend(["", "## PDF Records", ""])
    lines.extend(
        f"- `{row['candidate_id']}` `{row['pdf_path']}`"
        for row in mapping_rows
        if row["pdf_found"]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "include_records": len(include),
                "pdf_records": len(pdf_items),
                "missing_pdf_records": len(missing),
                "config": rel(OUT_CONFIG),
                "mapping_csv": rel(OUT_CSV),
                "mapping_md": rel(OUT_MD),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
