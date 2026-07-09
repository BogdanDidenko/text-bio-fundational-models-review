#!/usr/bin/env python3
"""Build final Docling coverage manifest for INCLUDE records."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MAPPING = REPO / "data/docling_include_no_vlm_2026-07-09_pdf_mapping.csv"
OUT_ROOT = REPO / "data/docling_include_no_vlm_2026-07-09"
OUT_DIR = REPO / "data/docling_include_final_coverage_2026-07-09"


def rel(path: Path | str | None) -> str:
    if not path:
        return ""
    value = Path(path)
    if not value.is_absolute():
        value = REPO / value
    try:
        return str(value.relative_to(REPO))
    except ValueError:
        return str(value)


def slug(text: str, limit: int = 96) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")
    return value[:limit] or "document"


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def artifact_paths(candidate_id: str) -> dict[str, Path]:
    stem = slug(candidate_id)
    return {
        "docling_json": OUT_ROOT / "documents" / f"{stem}.docling.json",
        "markdown": OUT_ROOT / "markdown" / f"{stem}.md",
        "chunks": OUT_ROOT / "chunks" / f"{stem}.jsonl",
        "figures_manifest": OUT_ROOT / "figures" / stem / "figures_manifest.json",
    }


def row_flags(row: dict[str, Any]) -> list[str]:
    flags = []
    if row["final_docling_status"] == "docling_ok":
        if int(row.get("chunk_count") or 0) < 5:
            flags.append("low_chunk_count")
        if int(row.get("markdown_chars") or 0) < 3000:
            flags.append("low_markdown_chars")
        if int(row.get("figure_count") or 0) == 0:
            flags.append("no_figures")
    elif row["final_docling_status"] == "docling_failed_or_missing_artifact":
        flags.append("docling_conversion_failed_or_missing_artifact")
    elif row["final_docling_status"] in {"missing_pdf", "not_found_after_manual_retry"}:
        flags.append("not_found_after_manual_retry")
    return flags


def build_rows() -> list[dict[str, Any]]:
    rows = []
    with MAPPING.open(newline="", encoding="utf-8") as f:
        records = list(csv.DictReader(f))

    for rec in records:
        candidate_id = rec["candidate_id"]
        pdf_path = REPO / rec["pdf_path"] if rec.get("pdf_path") else None
        paths = artifact_paths(candidate_id)
        artifacts_exist = all(path.exists() for path in paths.values())

        status = "not_found_after_manual_retry"
        if rec.get("pdf_found") == "True":
            status = "docling_ok" if artifacts_exist else "docling_failed_or_missing_artifact"

        figure_count = ""
        if paths["figures_manifest"].exists():
            figure_count = len(read_json(paths["figures_manifest"]))
        chunk_count = count_jsonl(paths["chunks"]) if paths["chunks"].exists() else ""
        markdown_chars = (
            len(paths["markdown"].read_text(encoding="utf-8"))
            if paths["markdown"].exists()
            else ""
        )
        docling_json_bytes = (
            paths["docling_json"].stat().st_size if paths["docling_json"].exists() else ""
        )

        pdf_sha256 = ""
        if pdf_path and pdf_path.exists():
            pdf_sha256 = sha256_path(pdf_path)

        row = {
            "candidate_id": candidate_id,
            "source_run": rec.get("source_run", ""),
            "record_id": rec.get("record_id", ""),
            "title": rec.get("title", ""),
            "doi": rec.get("doi", ""),
            "manifest_status": rec.get("manifest_status", ""),
            "pdf_found": rec.get("pdf_found", ""),
            "pdf_path": rec.get("pdf_path", ""),
            "pdf_bytes": rec.get("pdf_bytes", ""),
            "pdf_sha256": pdf_sha256,
            "final_docling_status": status,
            "docling_json": rel(paths["docling_json"]) if paths["docling_json"].exists() else "",
            "markdown": rel(paths["markdown"]) if paths["markdown"].exists() else "",
            "chunks": rel(paths["chunks"]) if paths["chunks"].exists() else "",
            "chunk_count": chunk_count,
            "figure_count": figure_count,
            "figures_manifest": rel(paths["figures_manifest"])
            if paths["figures_manifest"].exists()
            else "",
            "markdown_chars": markdown_chars,
            "docling_json_bytes": docling_json_bytes,
            "notes": "",
        }
        row["quality_flags"] = ";".join(row_flags(row))
        if status == "docling_failed_or_missing_artifact":
            row["notes"] = "PDF was present in mapping, but complete Docling artifacts were not created."
        elif status == "not_found_after_manual_retry":
            row["notes"] = (
                "No PDF found after automated retry passes, web/manual-link retry, "
                "and user manual-download sweep."
            )
        rows.append(row)

    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]], path: Path) -> None:
    total = len(rows)
    ok = sum(1 for row in rows if row["final_docling_status"] == "docling_ok")
    not_found = sum(
        1
        for row in rows
        if row["final_docling_status"] in {"missing_pdf", "not_found_after_manual_retry"}
    )
    failed = sum(
        1
        for row in rows
        if row["final_docling_status"] == "docling_failed_or_missing_artifact"
    )
    pdf_found = sum(1 for row in rows if row["pdf_found"] == "True")
    chunks = sum(int(row["chunk_count"] or 0) for row in rows)
    figures = sum(int(row["figure_count"] or 0) for row in rows)
    flagged = [row for row in rows if row["quality_flags"]]
    ok_flagged = [
        row
        for row in flagged
        if row["final_docling_status"] == "docling_ok"
    ]
    duplicate_hashes = {
        sha
        for sha in {row["pdf_sha256"] for row in rows if row["pdf_sha256"]}
        if sum(1 for row in rows if row["pdf_sha256"] == sha) > 1
    }

    lines = [
        "# Final Docling Coverage for INCLUDE Records",
        "",
        f"Generated at: `{time.strftime('%Y-%m-%dT%H:%M:%S%z')}`",
        "",
        "## Summary",
        "",
        f"- INCLUDE records total: {total}",
        f"- PDF available before Docling: {pdf_found}",
        f"- Docling OK: {ok}",
        f"- Docling failed / missing artifact: {failed}",
        f"- Not found after full-text retries: {not_found}",
        f"- Total selected chunks: {chunks}",
        f"- Total selected figures: {figures}",
        f"- Records with QA flags: {len(flagged)} "
        f"({not_found} not found after retries; {failed} failed/missing artifacts; "
        f"{len(ok_flagged)} low-quality OK artifact)",
        f"- Duplicate PDF hashes among INCLUDE records: {len(duplicate_hashes)}",
        "",
        "## Failed Docling conversions / missing artifacts",
        "",
    ]
    failed_rows = [
        row
        for row in rows
        if row["final_docling_status"] == "docling_failed_or_missing_artifact"
    ]
    if failed_rows:
        for row in failed_rows:
            lines.extend(
                [
                    f"- `{row['candidate_id']}` {row['title']}",
                    f"  - PDF: `{row['pdf_path']}`",
                    f"  - notes: {row['notes']}",
                ]
            )
    else:
        lines.append("- None")

    lines.extend(["", "## PDFs not found after retries", ""])
    missing_rows = [
        row
        for row in rows
        if row["final_docling_status"] in {"missing_pdf", "not_found_after_manual_retry"}
    ]
    if missing_rows:
        for row in missing_rows:
            lines.append(f"- `{row['candidate_id']}` `{row['record_id']}` {row['title']}")
    else:
        lines.append("- None")

    lines.extend(["", "## QA flags", ""])
    if ok_flagged:
        for row in ok_flagged:
            lines.append(
                f"- `{row['candidate_id']}` chunks={row['chunk_count']} "
                f"figures={row['figure_count']} flags=`{row['quality_flags']}`"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## Duplicate PDF hashes", ""])
    if duplicate_hashes:
        for sha in sorted(duplicate_hashes):
            dup_rows = [row for row in rows if row["pdf_sha256"] == sha]
            lines.append(f"- `{sha}` ({len(dup_rows)} records)")
            for row in dup_rows:
                lines.append(f"  - `{row['candidate_id']}` {row['title']}")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `final_docling_manifest.csv`: one row per INCLUDE record.",
            "- `final_docling_manifest.json`: same content as JSON.",
            "- `final_docling_coverage_summary.md`: this summary.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = build_rows()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(rows, OUT_DIR / "final_docling_manifest.csv")
    (OUT_DIR / "final_docling_manifest.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_markdown(rows, OUT_DIR / "final_docling_coverage_summary.md")
    print(
        json.dumps(
            {
                "out_dir": rel(OUT_DIR),
                "records_total": len(rows),
                "docling_ok": sum(
                    1 for row in rows if row["final_docling_status"] == "docling_ok"
                ),
                "docling_failed_or_missing_artifact": sum(
                    1
                    for row in rows
                    if row["final_docling_status"]
                    == "docling_failed_or_missing_artifact"
                ),
                "not_found_after_manual_retry": sum(
                    1
                    for row in rows
                    if row["final_docling_status"]
                    in {"missing_pdf", "not_found_after_manual_retry"}
                ),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
