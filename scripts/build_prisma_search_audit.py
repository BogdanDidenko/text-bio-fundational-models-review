#!/usr/bin/env python3
"""PRISMA-S search audit: every database x search round, read from the committed search exports.

Outputs (analysis/prisma_search_audit_2026-10-14/):
- search_runs_by_database.csv  one row per round x database: window, execution date, interface, date and
  access limits as executed, API total, records fetched, records retained, raw retrieval before
  post-retrieval validation, and run notes;
- search_strategies_as_executed.md  the exact query strings of every database in every round, copied in full
  from the export files.

Nothing is typed in: each value is read from the export JSON or the round summary.

  python3 scripts/build_prisma_search_audit.py
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/prisma_search_audit_2026-10-14"
ROUNDS = [
    ("1 baseline (v3.1)", "2018-01-01", "2026-02-28", ROOT / "data/exports_v31", "2026-02-15", "scripts/search_config.json"),
    ("2 April top-up", "2026-03-01", "2026-04-14", ROOT / "data/exports_update", "2026-04-14", "scripts/search_config_update.json"),
    ("3 June top-up", "2026-04-15", "2026-06-10",
     ROOT / "analysis/codex_screening_run_artifacts_20260706/inputs/exports_update_2026-06-10", "2026-06-10",
     "scripts/search_config_update_2026-06-10.json"),
    ("4 July top-up", "2026-06-11", "2026-07-06",
     ROOT / "analysis/codex_screening_run_artifacts_20260706/inputs/exports_update_2026-07-06", "2026-07-06",
     "scripts/search_config_update_2026-07-06.json"),
    ("5 August living update (v3.3)", "2026-07-07", "2026-08-09",
     ROOT / "data/living_catalog_updates/update_2026-08-09/00_search/exports", "2026-08-09",
     "data/living_catalog_updates/update_2026-08-09/00_search/search_config.json"),
]
DBS = ["pubmed", "scopus", "openalex", "semantic_scholar", "arxiv", "biorxiv_medrxiv", "springernature", "google_scholar"]


def load(p):
    return json.loads(Path(p).read_text())


def records(d):
    if isinstance(d, list):
        return d
    return d.get("records") or d.get("results") or d.get("papers") or []


def query_text(d, cfg_db):
    if isinstance(d, dict):
        if d.get("query"):
            return d["query"] if isinstance(d["query"], str) else json.dumps(d["query"], indent=1)
        if d.get("queries"):
            q = d["queries"]
            return "\n".join(f"[{k}] {v}" for k, v in q.items()) if isinstance(q, dict) else "\n".join(map(str, q))
    if cfg_db:
        q = cfg_db.get("queries") or cfg_db.get("query")
        if isinstance(q, dict):
            return "\n".join(f"[{k}] {v}" for k, v in q.items())
        if isinstance(q, list):
            return "\n".join(map(str, q))
        if isinstance(q, str):
            return q
    return ""


def date_clause(db, q, meta, cfg_db):
    """Date restriction as executed, read from the query string first and the export metadata second."""
    if db == "pubmed":
        m = re.findall(r'"(\d{4}/\d{2}/\d{2})"\[Date - Publication\]', q)
        return f"[Date - Publication] {m[0]} to {m[1]}" if len(m) >= 2 else ""
    if db == "biorxiv_medrxiv":
        m = re.search(r"FIRST_PDATE:\[[^\]]+\]", q)
        return m.group(0) if m else ""
    if db == "scopus":
        m = re.search(r"PUBYEAR\s*>\s*\d{4}", q)
        lo, hi = cfg_db.get("date_from_post_filter"), cfg_db.get("date_post_filter")
        post = f"; exact-date post-filter {lo or 'none'} to {hi}" if hi else ""
        return (m.group(0) if m else "") + post
    if db == "semantic_scholar":
        lo, hi = cfg_db.get("date_from_post_filter"), cfg_db.get("date_post_filter")
        return f"year={cfg_db.get('year_range', '')}; exact-date post-filter {lo or 'none'} to {hi}" if hi else \
            str(meta.get("filters", ""))
    if db == "arxiv":
        m = re.search(r"submittedDate:\[[^\]]+\]", str(meta.get("filters", "")) + " " + str(cfg_db.get("date_filter", "")))
        return m.group(0) if m else ""
    if db == "springernature":
        return str(meta.get("date_filter") or cfg_db.get("date_filter") or "")
    if db == "openalex":
        m = re.findall(r"(from_publication_date:[\d-]+|to_publication_date:[\d-]+)", str(meta.get("filters", "")))
        return ",".join(m)
    if db == "google_scholar":
        yr = meta.get("year_range") or cfg_db.get("year_range")
        return f"year range {yr} (year-level only)" if yr else ""
    return ""


def access_limits(db, q, meta):
    s = q + " " + str(meta.get("filters", ""))
    out = []
    for pat, lab in [(r'"?free full text"?\[sb\]', "free full text[sb]"), (r"English\[Language\]", "English[Language]"),
                     (r"OPENACCESS\(1\)", "OPENACCESS(1)"), (r"LANGUAGE\(English\)", "LANGUAGE(English)"),
                     (r"LIMIT-TO\(DOCTYPE", "DOCTYPE limit"), (r"is_oa:true", "is_oa:true"), (r"language:en", "language:en"),
                     (r"SRC:PPR", "SRC:PPR (preprints)"), (r"cat:cs\.LG", "arXiv categories cs.LG/cs.AI/cs.CL/q-bio.GN/q-bio.QM/stat.ML"),
                     (r"post-retrieval validation", "three-block title/abstract validation after retrieval")]:
        if re.search(pat, s):
            out.append(lab)
    if db == "springernature" and "Open Access" not in " ".join(out):
        pass
    return "; ".join(dict.fromkeys(out))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, strategies = [], []
    for label, lo, hi, folder, end, cfg_path in ROUNDS:
        cfg = load(ROOT / cfg_path)
        summ_files = sorted(folder.glob("search_summary_*.json"))
        summ = load(summ_files[0]) if summ_files else {}
        strategies.append(f"## Round {label}: {lo} to {hi}\n\nConfig: `{cfg_path}`. Exports: `{folder.relative_to(ROOT)}`.\n")
        for db in DBS:
            files = [f for f in sorted(folder.glob(f"{db}_*.json")) if "_raw_" not in f.name]
            cfg_db = (cfg.get("databases") or {}).get(db, {})
            if not files:
                rows.append({"round": label, "window_from": lo, "window_to": hi, "database": db, "searched": "no"})
                continue
            d = load(files[0])
            meta = d if isinstance(d, dict) else {}
            q = query_text(d, cfg_db)
            raw_files = sorted(folder.glob(f"{db}_raw_*.json"))
            raw_n = meta.get("total_raw")
            if raw_n is None and raw_files:
                raw_n = len(records(load(raw_files[0])))
            n = len(records(d))
            rows.append({
                "round": label, "window_from": lo, "window_to": hi, "database": db, "searched": "yes",
                "executed": meta.get("search_date") or summ.get("search_date") or end,
                "interface": meta.get("database", ""),
                "date_restriction_as_executed": date_clause(db, q, meta, cfg_db),
                "other_limits_as_executed": access_limits(db, q, meta),
                "api_total": meta.get("total_results", meta.get("total_unique_results", "")),
                "fetched": meta.get("records_fetched", ""),
                "retained": n,
                "raw_before_validation": raw_n if raw_n is not None else "",
                "summary_count": (summ.get("results_per_database") or {}).get(db, ""),
                "export_file": str(files[0].relative_to(ROOT)),
            })
            strategies.append(f"### {db} (executed {rows[-1]['executed']}; retained {n})\n\n```text\n{q}\n```\n")
        notes = summ.get("notes")
        if notes:
            strategies.append(f"Round notes: {notes}\n")
        if summ.get("date_status_by_database"):
            strategies.append("Date status by database: `" + json.dumps(summ["date_status_by_database"]) + "`\n")
    cols = ["round", "window_from", "window_to", "database", "searched", "executed", "interface",
            "date_restriction_as_executed", "other_limits_as_executed", "api_total", "fetched", "retained",
            "raw_before_validation", "summary_count", "export_file"]
    with open(OUT / "search_runs_by_database.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    (OUT / "search_strategies_as_executed.md").write_text(
        "# Search strategies as executed (generated by `scripts/build_prisma_search_audit.py`)\n\n" + "\n".join(strategies))
    tot = {}
    for r in rows:
        if r.get("searched") == "yes":
            tot[r["round"]] = tot.get(r["round"], 0) + int(r["retained"])
    print(json.dumps(tot, indent=1), sum(tot.values()))


if __name__ == "__main__":
    main()
