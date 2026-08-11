#!/usr/bin/env python3
"""Create a dated top-up search config without changing the search concepts."""

from __future__ import annotations

import argparse
import copy
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "scripts/search_config_living_v3_3.json"


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid ISO date: {value}") from exc


def replace_exact(pattern: str, replacement: str, value: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, value)
    if count != 1:
        raise RuntimeError(f"Expected one {label} date clause, found {count}")
    return updated


def build_config(template: dict[str, Any], start: date, end: date) -> dict[str, Any]:
    if start > end:
        raise ValueError("date_from must not be after date_to")
    config = copy.deepcopy(template)
    start_iso, end_iso = start.isoformat(), end.isoformat()
    start_compact, end_compact = start.strftime("%Y%m%d"), end.strftime("%Y%m%d")
    start_pubmed, end_pubmed = start.strftime("%Y/%m/%d"), end.strftime("%Y/%m/%d")

    metadata = config["metadata"]
    metadata.update(
        {
            "protocol_version": f"living-v3.3-update-{end_iso}",
            "date_from": start_iso,
            "date_to": end_iso,
            "search_mode": "incremental_update",
            "run_historical_ground_truth_validation": False,
            "google_scholar_acquisition": "provider_export_required",
            "search_update": (
                f"Update search covering {start_iso} to {end_iso}. Same concept "
                "blocks as v3.1, the living-v3.2 Scopus wildcard syntax correction, "
                "and the living-v3.3 single-query Google Scholar translation; only "
                "date filters change between runs."
            ),
        }
    )
    databases = config["databases"]

    pubmed = databases["pubmed"]
    pubmed["query"] = replace_exact(
        r'\("\d{4}/\d{2}/\d{2}"\[Date - Publication\]\s*:\s*"\d{4}/\d{2}/\d{2}"\[Date - Publication\]\)',
        f'("{start_pubmed}"[Date - Publication] : "{end_pubmed}"[Date - Publication])',
        pubmed["query"],
        "PubMed",
    )
    pubmed["notes"] = f"Update search: {start_iso} to {end_iso} only."

    scopus = databases["scopus"]
    scopus["query"] = replace_exact(
        r"PUBYEAR\s*>\s*\d{4}",
        f"PUBYEAR > {start.year - 1}",
        scopus["query"],
        "Scopus PUBYEAR",
    )
    scopus["date_from_post_filter"] = start_iso
    scopus["date_post_filter"] = end_iso
    scopus["notes"] = (
        f"Update: PUBYEAR > {start.year - 1}; exact post-filter {start_iso}..{end_iso}."
    )

    semantic = databases["semantic_scholar"]
    semantic["year_range"] = f"{start.year}-{end.year}"
    semantic["date_from_post_filter"] = start_iso
    semantic["date_post_filter"] = end_iso
    semantic["notes"] = (
        f"Update: year range {start.year}-{end.year}, exact post-filter "
        f"{start_iso}..{end_iso}."
    )

    openalex = databases["openalex"]
    openalex["date_from"] = start_iso
    openalex["date_to"] = end_iso
    openalex["notes"] = (
        f"Update: exact publication-date filter {start_iso}..{end_iso}; "
        "English and open-access works."
    )

    arxiv = databases["arxiv"]
    arxiv["date_filter"] = f"submittedDate:[{start_compact} TO {end_compact}]"
    arxiv["notes"] = f"Update: date range {start_iso} to {end_iso}."

    preprints = databases["biorxiv_medrxiv"]
    preprints["query"] = replace_exact(
        r"FIRST_PDATE:\[\d{4}-\d{2}-\d{2}\s+TO\s+\d{4}-\d{2}-\d{2}\]",
        f"FIRST_PDATE:[{start_iso} TO {end_iso}]",
        preprints["query"],
        "Europe PMC FIRST_PDATE",
    )
    preprints["notes"] = f"Update: date range {start_iso} to {end_iso}."

    springer = databases["springernature"]
    springer["date_filter"] = f"datefrom:{start_iso} dateto:{end_iso}"
    springer["notes"] = f"Update: date range {start_iso} to {end_iso}."

    scholar = databases["google_scholar"]
    scholar["year_range"] = [start.year, end.year]
    scholar["notes"] = (
        f"Update: year filter {start.year}..{end.year}. Google Scholar has no "
        "month-level filter; exact metadata dates and cumulative deduplication are used."
    )
    return config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--date-from", type=parse_date, required=True)
    parser.add_argument("--date-to", type=parse_date, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    template = json.loads(args.template.read_text(encoding="utf-8"))
    config = build_config(template, args.date_from, args.date_to)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "date_from": args.date_from.isoformat(),
                "date_to": args.date_to.isoformat(),
                "databases": [
                    name
                    for name, value in config["databases"].items()
                    if value.get("enabled")
                ],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
