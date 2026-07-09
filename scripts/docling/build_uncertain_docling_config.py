#!/usr/bin/env python3
"""Build a no-VLM Docling config for UNCERTAIN screening records with PDFs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCREENING = REPO / "data/screening_codex_full_2026-07-06/final_screening_results.json"
FULL_TEXT_ROOT = REPO / "data/full_text_downloads_2026-07-07"
OUT_CONFIG = REPO / "scripts/docling/config_docling_uncertain_no_vlm_2026-07-08.json"
OUT_CSV = REPO / "data/docling_uncertain_no_vlm_2026-07-08_pdf_mapping.csv"
OUT_MD = REPO / "data/docling_uncertain_no_vlm_2026-07-08_pdf_mapping.md"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def title_slug(title: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in title)[:80]


def candidate_id(record_id: str) -> str:
    return f"full_2026-07-06__{record_id}"


def choose_pdf(record_id: str) -> Path | None:
    prefix = candidate_id(record_id)
    pdfs = sorted(
        [
            p
            for p in FULL_TEXT_ROOT.rglob("*.pdf")
            if prefix in str(p) and p.is_file() and p.stat().st_size > 100_000
        ],
        key=lambda p: (
            0 if "manual" in str(p).lower() else 1,
            0 if "openalex_content" in str(p).lower() else 1,
            0 if "europepmc" in p.name.lower() else 1,
            p.stat().st_size,
            str(p),
        ),
    )
    return pdfs[0] if pdfs else None


def main() -> int:
    records = json.loads(SCREENING.read_text(encoding="utf-8"))["records"]
    uncertain = [r for r in records if r.get("final_decision") == "UNCERTAIN"]

    rows: list[dict[str, Any]] = []
    pdf_items: list[dict[str, str]] = []
    for record in uncertain:
        pdf = choose_pdf(record["record_id"])
        row = {
            "record_id": record["record_id"],
            "candidate_id": candidate_id(record["record_id"]),
            "title": record.get("title", ""),
            "doi": record.get("doi", ""),
            "final_code": record.get("final_code", ""),
            "uncertainty_reason": record.get("uncertainty_reason", ""),
            "pdf_found": bool(pdf),
            "pdf_path": rel(pdf) if pdf else "",
            "pdf_bytes": pdf.stat().st_size if pdf else "",
        }
        rows.append(row)
        if pdf:
            pdf_items.append(
                {
                    "record_id": record["record_id"],
                    "candidate_id": candidate_id(record["record_id"]),
                    "path": rel(pdf),
                    "title": record.get("title", ""),
                    "doi": record.get("doi", ""),
                }
            )

    config = {
        "name": "docling_uncertain_no_vlm_2026-07-08",
        "description": (
            "No-VLM Docling preprocessing batch for UNCERTAIN records from "
            "data/screening_codex_full_2026-07-06/final_screening_results.json."
        ),
        "output_root": "data/docling_uncertain_no_vlm_2026-07-08",
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
        "source_screening_file": rel(SCREENING),
        "uncertain_records_total": len(uncertain),
        "pdf_records_total": len(pdf_items),
        "missing_pdf_records_total": len(uncertain) - len(pdf_items),
        "pdfs": pdf_items,
    }

    OUT_CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    missing = [row for row in rows if not row["pdf_found"]]
    lines = [
        "# UNCERTAIN records Docling no-VLM PDF mapping",
        "",
        f"- Source screening file: `{rel(SCREENING)}`",
        f"- UNCERTAIN records: {len(uncertain)}",
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
            f"- `{row['record_id']}` {row['title']}" for row in missing
        )
    else:
        lines.append("- none")
    lines.extend(["", "## PDF Records", ""])
    lines.extend(
        f"- `{row['record_id']}` `{row['pdf_path']}`"
        for row in rows
        if row["pdf_found"]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "uncertain_records": len(uncertain),
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
