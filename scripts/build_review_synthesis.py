"""Descriptive synthesis tables for the scoping-review manuscript (55 records, 109 models).

Reads the current atlas and the cumulative master record sets. Writes a per-model charting
table (supplementary), dimension counts and a publication-year table. Counts are "models
carrying at least one route with the value"; a model can carry several values per dimension.
"""

import csv
import glob
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "docs/input-representation-atlas/data/atlas.json"
OUT = ROOT / "analysis/review_synthesis_2026-10-07"
DIMENSIONS = ("families", "fusion_topologies", "text_roles", "lifecycle_phases", "subtypes")
# Records added by top-ups whose search window lies wholly inside 2026 (date-filtered searches).
WINDOW_2026 = ("june_update_2026-06-10__", "july_update_2026-07-06__", "update_2026-08-09__")


def norm(text):
    return re.sub(r"\W+", "", (text or "").lower())[:70]


def publication_years(records):
    by_doi, by_title = {}, {}
    files = [ROOT / "data/deduplicated_records.json"] + [Path(p) for p in glob.glob(str(ROOT / "data/dedup_update_*/*.json"))]
    for path in files:
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        rows = data if isinstance(data, list) else data.get("records", [])
        for row in rows if isinstance(rows, list) else []:
            year = str(row.get("year") or "")[:4] if isinstance(row, dict) else ""
            if year.isdigit():
                if row.get("doi"):
                    by_doi.setdefault(row["doi"].lower(), int(year))
                by_title.setdefault(norm(row.get("title")), int(year))
    years, basis = {}, {}
    for rid, model in records.items():
        year = by_doi.get((model.get("doi") or "").lower()) or by_title.get(norm(model["paper_title"]))
        if year:
            years[rid], basis[rid] = year, "master record metadata"
        elif rid.startswith(WINDOW_2026):
            years[rid], basis[rid] = 2026, "search window (2026 top-up)"
        else:
            raise SystemExit(f"No publication year for {rid}")
    return years, basis


def main():
    atlas = json.loads(ATLAS.read_text())
    models = atlas["architectures"]
    labels = {f["family_id"]: f["label"] for f in atlas["families"]}
    records = {}
    for m in models:
        records.setdefault(m["record_id"], m)
    years, basis = publication_years(records)
    OUT.mkdir(parents=True, exist_ok=True)

    with open(OUT / "charting_table_models.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["model_name", "record_id", "paper_title", "doi", "year", "year_basis", "routes", "configurations",
                         "input_families", "primary_subtype", "fusion_topologies", "text_roles", "lifecycle_phases", "modalities"])
        for m in sorted(models, key=lambda x: (x["paper_title"].lower(), x["model_name"].lower())):
            writer.writerow([m["model_name"], m["record_id"], m["paper_title"], m.get("doi") or "", years[m["record_id"]],
                             basis[m["record_id"]], m["route_count"], m["configuration_count"],
                             "; ".join(labels.get(f, f) for f in m["families"]), m.get("primary_subtype") or "",
                             "; ".join(m["fusion_topologies"]), "; ".join(m["text_roles"]),
                             "; ".join(m["lifecycle_phases"]), "; ".join(m["modalities"])])

    summary = {"records": len(records), "studies": atlas["meta"]["study_count"], "models": len(models),
               "routes": sum(m["route_count"] for m in models), "configurations": sum(m["configuration_count"] for m in models),
               "records_by_year": dict(sorted(Counter(years.values()).items())),
               "year_basis": dict(Counter(basis.values())),
               "models_per_record": dict(sorted(Counter(Counter(m["record_id"] for m in models).values()).items())),
               "family_combinations": Counter(" + ".join(labels[f] for f in sorted(m["families"])) for m in models).most_common(),
               "routes_by_family": dict(Counter({labels[f]: sum(m["family_counts"].get(f, 0) for m in models) for f in labels}).most_common())}
    for dim in DIMENSIONS:
        counts = Counter(v for m in models for v in (m[dim] or []))
        summary[f"models_by_{dim}"] = dict(counts.most_common())
    summary["models_by_families"] = {labels[k]: v for k, v in summary["models_by_families"].items()}
    (OUT / "synthesis_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("records", "models", "routes", "records_by_year", "year_basis")}, indent=1))


if __name__ == "__main__":
    main()
