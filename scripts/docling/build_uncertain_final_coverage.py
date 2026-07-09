#!/usr/bin/env python3
"""Build final Docling coverage manifest for UNCERTAIN records."""

from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MAPPING = REPO / "data/docling_uncertain_no_vlm_2026-07-08_pdf_mapping.csv"
OUT_DIR = REPO / "data/docling_uncertain_final_coverage_2026-07-09"
REC_RE = re.compile(r"rec_\d{6}")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: str | Path | None) -> str:
    if not path:
        return ""
    value = Path(path)
    if not value.is_absolute():
        value = REPO / value
    try:
        return str(value.relative_to(REPO))
    except ValueError:
        return str(value)


def record_ids_from_item(item: dict[str, Any]) -> set[str]:
    values = [
        item.get("record_id", ""),
        item.get("candidate_id", ""),
        item.get("source_pdf", ""),
        item.get("source_html", ""),
        item.get("docling_json", ""),
        item.get("markdown", ""),
        item.get("chunks", ""),
    ]
    return set(REC_RE.findall(" ".join(str(v) for v in values)))


def source_kind(item: dict[str, Any]) -> str:
    if item.get("source_pdf"):
        return "pdf"
    if item.get("source_html"):
        return "html"
    return ""


def source_file(item: dict[str, Any]) -> str:
    return item.get("source_pdf") or item.get("source_html") or ""


def item_score(item: dict[str, Any]) -> tuple[int, int, int, float]:
    """Prefer successful PDF conversions, then richer documents."""
    ok = 1 if item.get("status") == "ok" else 0
    pdf = 1 if source_kind(item) == "pdf" else 0
    chunks = int(item.get("chunk_count") or 0)
    elapsed = float(item.get("elapsed_sec") or 0.0)
    return (ok, pdf, chunks, elapsed)


def load_uncertain_records() -> list[dict[str, str]]:
    with MAPPING.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_docling_items() -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    manifest_paths = sorted(REPO.glob("data/docling_uncertain*/manifests/docling*_manifest.json"))
    for manifest_path in manifest_paths:
        data = read_json(manifest_path)
        rows = data.get("results", data if isinstance(data, list) else [])
        for item in rows:
            item = dict(item)
            item["_manifest"] = rel(manifest_path)
            item["_output_root"] = rel(manifest_path.parents[1])
            for record_id in record_ids_from_item(item):
                grouped.setdefault(record_id, []).append(item)
    return grouped


def build_rows(records: list[dict[str, str]], grouped: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rows = []
    for rec in records:
        record_id = rec["record_id"]
        attempts = grouped.get(record_id, [])
        best = max(attempts, key=item_score) if attempts else {}
        status = "docling_ok" if best.get("status") == "ok" else "unavailable_or_failed"
        notes = ""
        if record_id == "rec_002409":
            status = "unavailable_gated"
            notes = "Publisher full text is gated/blocked; Chrome retry returned 403 / Just a moment via SAGE redirect."
        elif best.get("status") != "ok" and attempts:
            notes = "Only failed Docling attempts found."
        elif not attempts:
            notes = "No Docling attempt found."
        rows.append(
            {
                "record_id": record_id,
                "candidate_id": rec.get("candidate_id", ""),
                "title": rec.get("title", ""),
                "doi": rec.get("doi", ""),
                "final_code": rec.get("final_code", ""),
                "uncertainty_reason": rec.get("uncertainty_reason", ""),
                "final_docling_status": status,
                "selected_attempt_status": best.get("status", ""),
                "source_kind": source_kind(best),
                "source_file": rel(source_file(best)),
                "docling_json": rel(best.get("docling_json")),
                "markdown": rel(best.get("markdown")),
                "chunks": rel(best.get("chunks")),
                "chunk_count": best.get("chunk_count", ""),
                "figure_count": best.get("figure_count", ""),
                "figures_manifest": rel(best.get("figures_manifest")),
                "manifest": best.get("_manifest", ""),
                "output_root": best.get("_output_root", ""),
                "attempt_count": len(attempts),
                "notes": notes,
            }
        )
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]], path: Path) -> None:
    total = len(rows)
    ok = sum(1 for row in rows if row["final_docling_status"] == "docling_ok")
    gated = sum(1 for row in rows if row["final_docling_status"] == "unavailable_gated")
    pdf_ok = sum(
        1
        for row in rows
        if row["final_docling_status"] == "docling_ok" and row["source_kind"] == "pdf"
    )
    html_ok = sum(
        1
        for row in rows
        if row["final_docling_status"] == "docling_ok" and row["source_kind"] == "html"
    )
    chunks = sum(int(row["chunk_count"] or 0) for row in rows if row["final_docling_status"] == "docling_ok")
    figures = sum(int(row["figure_count"] or 0) for row in rows if row["figure_count"] not in ("", None))
    lines = [
        "# Final Docling Coverage for UNCERTAIN Records",
        "",
        f"Generated at: `{time.strftime('%Y-%m-%dT%H:%M:%S%z')}`",
        "",
        "## Summary",
        "",
        f"- UNCERTAIN records total: {total}",
        f"- Docling OK: {ok}",
        f"- PDF Docling OK: {pdf_ok}",
        f"- HTML Docling OK: {html_ok}",
        f"- Unavailable/gated: {gated}",
        f"- Total selected chunks: {chunks}",
        f"- Total selected figures: {figures}",
        "",
        "## Remaining unavailable/gated",
        "",
    ]
    remaining = [row for row in rows if row["final_docling_status"] != "docling_ok"]
    if remaining:
        for row in remaining:
            lines.extend(
                [
                    f"- `{row['record_id']}` {row['title']}",
                    f"  - DOI: `{row['doi']}`",
                    f"  - status: {row['final_docling_status']}",
                    f"  - notes: {row['notes']}",
                ]
            )
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `final_docling_manifest.csv`: one row per UNCERTAIN record.",
            "- `final_docling_manifest.json`: same content as JSON.",
            "- `final_docling_coverage_summary.md`: this summary.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    records = load_uncertain_records()
    grouped = load_docling_items()
    rows = build_rows(records, grouped)
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
                "unavailable_gated": sum(
                    1
                    for row in rows
                    if row["final_docling_status"] == "unavailable_gated"
                ),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
