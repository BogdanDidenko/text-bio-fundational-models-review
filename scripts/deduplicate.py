#!/usr/bin/env python3
"""
Deduplication of systematic review search results.

Conservative strategy (no fuzzy matching):
  1. Normalize all records (DOI, title, IDs)
  2. Exact DOI matching
  3. Exact PMID matching
  4. Exact arXiv ID matching
  5. Exact normalized title matching
  6. Preprint→published: keep published version, note preprint DOI

Input:  data/exports/*_2026-02-06.json  (7 database exports)
Output: data/deduplicated_records.json   (unique records with source tracking)
        data/deduplication_log.csv       (every merge decision with reason)
        data/deduplication_stats.json    (summary statistics)
"""

import json
import os
import re
import csv
import unicodedata
from datetime import datetime
from collections import defaultdict

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "exports")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

EXPORT_FILES = {
    "pubmed": "pubmed_2026-02-06.json",
    "scopus": "scopus_2026-02-06.json",
    "semantic_scholar": "semantic_scholar_2026-02-06.json",
    "arxiv": "arxiv_2026-02-06.json",
    "biorxiv_medrxiv": "biorxiv_medrxiv_2026-02-06.json",
    "springernature": "springernature_filtered_2026-02-06.json",
    "google_scholar": "google_scholar_2026-02-06.json",
}

# Preprint DOI prefixes
PREPRINT_DOI_PREFIXES = (
    "10.1101/",       # bioRxiv / medRxiv
    "10.48550/arxiv", # arXiv
)


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def normalize_doi(doi: str) -> str:
    """Normalize DOI to a canonical lowercase form without URL prefix."""
    if not doi:
        return ""
    doi = doi.strip()
    # Strip common URL prefixes
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix):]
            break
    return doi.lower().strip()


def normalize_arxiv_id(arxiv_id: str) -> str:
    """Normalize arXiv ID: strip version suffix (e.g. v1, v2)."""
    if not arxiv_id:
        return ""
    arxiv_id = arxiv_id.strip()
    # Remove version suffix
    return re.sub(r"v\d+$", "", arxiv_id).lower()


def normalize_title(title: str) -> str:
    """
    Normalize title for exact matching:
    - Unicode NFC normalization
    - Lowercase
    - Strip HTML tags
    - Remove all punctuation
    - Collapse whitespace
    """
    if not title:
        return ""
    title = unicodedata.normalize("NFC", title)
    title = title.lower()
    # Remove HTML tags (some S2 abstracts have them)
    title = re.sub(r"<[^>]+>", "", title)
    # Remove all punctuation and special characters (keep letters, digits, spaces)
    title = re.sub(r"[^\w\s]", "", title)
    # Collapse whitespace
    title = re.sub(r"\s+", " ", title).strip()
    return title


def is_preprint_doi(doi: str) -> bool:
    """Check if a DOI belongs to a preprint server."""
    ndoi = normalize_doi(doi)
    return any(ndoi.startswith(prefix) for prefix in PREPRINT_DOI_PREFIXES)


# ---------------------------------------------------------------------------
# Record loading
# ---------------------------------------------------------------------------

def load_records(db_name: str, filename: str) -> list[dict]:
    """Load records from an export JSON file into a unified format."""
    path = os.path.join(EXPORTS_DIR, filename)
    if not os.path.exists(path):
        print(f"  WARNING: {path} not found, skipping")
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract records array from wrapper or use list directly
    if isinstance(data, dict):
        records = data.get("records", [])
    elif isinstance(data, list):
        records = data
    else:
        return []

    unified = []
    for r in records:
        rec = {
            "source_db": db_name,
            "title_original": (r.get("title") or "").strip(),
            "title_normalized": normalize_title(r.get("title") or ""),
            "doi_original": (r.get("doi") or "").strip(),
            "doi_normalized": normalize_doi(r.get("doi") or ""),
            "pmid": (r.get("pmid") or "").strip() if r.get("pmid") else "",
            "arxiv_id_original": (r.get("arxiv_id") or "").strip() if r.get("arxiv_id") else "",
            "arxiv_id_normalized": normalize_arxiv_id(r.get("arxiv_id") or ""),
            "s2_id": (r.get("s2_id") or "").strip() if r.get("s2_id") else "",
            "abstract": (r.get("abstract") if isinstance(r.get("abstract"), str) else "").strip(),
            "authors": r.get("authors", []),
            "year": str(r.get("year") or "").strip(),
            "venue": (r.get("venue") or r.get("journal") or r.get("publicationName") or "").strip(),
            "date": (r.get("date") or r.get("publicationDate") or "").strip(),
            "url": (r.get("url") or r.get("open_access_pdf") or "").strip(),
        }

        # For Scopus: extract scopus_id
        if db_name == "scopus":
            rec["scopus_id"] = (r.get("scopus_id") or "").strip()

        # For EuropePMC: extract epmc_id
        if db_name == "biorxiv_medrxiv":
            rec["epmc_id"] = (r.get("epmc_id") or "").strip()

        unified.append(rec)

    return unified


# ---------------------------------------------------------------------------
# Deduplication engine
# ---------------------------------------------------------------------------

class DeduplicationEngine:
    """
    Conservative deduplication with full logging.

    Merge order:
      1. Exact DOI
      2. Exact PMID
      3. Exact arXiv ID
      4. Exact normalized title

    After merging, preprint→published linking is applied.
    """

    def __init__(self):
        # Each "cluster" is a group of records deemed to be the same paper
        # cluster_id → list of records
        self.clusters: dict[int, list[dict]] = {}
        self.next_cluster_id = 0

        # Indexes: value → cluster_id
        self.doi_index: dict[str, int] = {}
        self.pmid_index: dict[str, int] = {}
        self.arxiv_index: dict[str, int] = {}
        self.title_index: dict[str, int] = {}

        # Log: list of (record_summary, action, reason, cluster_id)
        self.log: list[dict] = []

    def _new_cluster(self, record: dict) -> int:
        cid = self.next_cluster_id
        self.next_cluster_id += 1
        self.clusters[cid] = [record]
        return cid

    def _merge_into(self, record: dict, cluster_id: int, reason: str):
        """Merge a record into an existing cluster."""
        self.clusters[cluster_id].append(record)
        self.log.append({
            "action": "MERGE",
            "reason": reason,
            "cluster_id": cluster_id,
            "source_db": record["source_db"],
            "title": record["title_original"][:100],
            "doi": record["doi_original"],
            "matched_with_db": self.clusters[cluster_id][0]["source_db"],
            "matched_with_title": self.clusters[cluster_id][0]["title_original"][:100],
        })

    def _register_indexes(self, record: dict, cluster_id: int):
        """Register all IDs of a record in the lookup indexes."""
        if record["doi_normalized"]:
            self.doi_index.setdefault(record["doi_normalized"], cluster_id)
        if record["pmid"]:
            self.pmid_index.setdefault(record["pmid"], cluster_id)
        if record["arxiv_id_normalized"]:
            self.arxiv_index.setdefault(record["arxiv_id_normalized"], cluster_id)
        if record["title_normalized"]:
            self.title_index.setdefault(record["title_normalized"], cluster_id)

    def _find_cluster(self, record: dict) -> tuple[int | None, str]:
        """Try to find an existing cluster for this record. Returns (cluster_id, reason) or (None, "")."""
        # Step 1: DOI match
        if record["doi_normalized"]:
            cid = self.doi_index.get(record["doi_normalized"])
            if cid is not None:
                return cid, f"DOI match: {record['doi_normalized']}"

        # Step 2: PMID match
        if record["pmid"]:
            cid = self.pmid_index.get(record["pmid"])
            if cid is not None:
                return cid, f"PMID match: {record['pmid']}"

        # Step 3: arXiv ID match
        if record["arxiv_id_normalized"]:
            cid = self.arxiv_index.get(record["arxiv_id_normalized"])
            if cid is not None:
                return cid, f"arXiv ID match: {record['arxiv_id_normalized']}"

        # Step 4: Exact normalized title match
        if record["title_normalized"]:
            cid = self.title_index.get(record["title_normalized"])
            if cid is not None:
                return cid, f"Exact title match"

        return None, ""

    def add_record(self, record: dict):
        """Add a record, merging into existing cluster or creating a new one."""
        cid, reason = self._find_cluster(record)

        if cid is not None:
            self._merge_into(record, cid, reason)
            # Also register any NEW IDs this record brings
            self._register_indexes(record, cid)
        else:
            cid = self._new_cluster(record)
            self._register_indexes(record, cid)
            self.log.append({
                "action": "NEW",
                "reason": "No match found",
                "cluster_id": cid,
                "source_db": record["source_db"],
                "title": record["title_original"][:100],
                "doi": record["doi_original"],
                "matched_with_db": "",
                "matched_with_title": "",
            })

    def resolve_preprints(self) -> list[dict]:
        """
        For each cluster, pick the best representative record.
        If cluster has both preprint and published DOI → keep published, note preprint.
        """
        preprint_log = []

        for cid, records in self.clusters.items():
            if len(records) < 2:
                continue

            # Collect all DOIs in this cluster
            dois = [(r["doi_normalized"], r["source_db"]) for r in records if r["doi_normalized"]]
            preprint_dois = [d for d, s in dois if is_preprint_doi(d)]
            published_dois = [d for d, s in dois if d and not is_preprint_doi(d)]

            if preprint_dois and published_dois:
                preprint_log.append({
                    "cluster_id": cid,
                    "published_doi": published_dois[0],
                    "preprint_dois": preprint_dois,
                    "title": records[0]["title_original"][:100],
                })

        return preprint_log

    def get_deduplicated_records(self) -> list[dict]:
        """
        Return one representative record per cluster, enriched with source tracking.

        Priority for representative: record with most metadata
        (prefer published DOI > preprint DOI > no DOI;
         prefer records with abstract; prefer PubMed/Scopus for metadata quality).
        """
        DB_PRIORITY = {
            "pubmed": 1,
            "scopus": 2,
            "semantic_scholar": 3,
            "biorxiv_medrxiv": 4,
            "springernature": 5,
            "arxiv": 6,
            "google_scholar": 7,
        }

        results = []
        for cid, records in self.clusters.items():
            # Sort: published DOI first, then by DB priority, then by abstract length
            def sort_key(r):
                has_published_doi = 1 if (r["doi_normalized"] and not is_preprint_doi(r["doi_normalized"])) else 2
                has_any_doi = 1 if r["doi_normalized"] else 2
                db_prio = DB_PRIORITY.get(r["source_db"], 99)
                abs_len = -len(r["abstract"])  # longer abstract = better
                return (has_published_doi, has_any_doi, db_prio, abs_len)

            sorted_records = sorted(records, key=sort_key)
            best = sorted_records[0]

            # Use the longest abstract from any record in the cluster
            # (the representative may come from a DB without abstracts, e.g. Scopus)
            best_abstract = best["abstract"]
            if len(records) > 1:
                all_abstracts = [r["abstract"] for r in records if r["abstract"]]
                if all_abstracts:
                    best_abstract = max(all_abstracts, key=len)

            # Collect all source databases and IDs
            sources = list(set(r["source_db"] for r in records))
            all_dois = list(set(r["doi_original"] for r in records if r["doi_original"]))
            all_pmids = list(set(r["pmid"] for r in records if r["pmid"]))
            all_arxiv_ids = list(set(r["arxiv_id_original"] for r in records if r["arxiv_id_original"]))

            # Check preprint→published
            preprint_dois = [d for d in all_dois if is_preprint_doi(d)]
            published_dois = [d for d in all_dois if d and not is_preprint_doi(d)]

            result = {
                "cluster_id": cid,
                "title": best["title_original"],
                "title_normalized": best["title_normalized"],
                "doi": published_dois[0] if published_dois else (all_dois[0] if all_dois else ""),
                "preprint_doi": preprint_dois[0] if (preprint_dois and published_dois) else "",
                "pmid": all_pmids[0] if all_pmids else "",
                "arxiv_id": all_arxiv_ids[0] if all_arxiv_ids else "",
                "abstract": best_abstract,
                "authors": best["authors"],
                "year": best["year"],
                "venue": best["venue"],
                "date": best["date"],
                "url": best["url"],
                "sources": sorted(sources),
                "n_sources": len(sources),
                "all_dois": all_dois,
                "duplicate_count": len(records),
            }
            results.append(result)

        # Sort by cluster_id for deterministic output
        results.sort(key=lambda r: r["cluster_id"])
        return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("DEDUPLICATION OF SYSTEMATIC REVIEW SEARCH RESULTS")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Strategy: Conservative (exact matching only, no fuzzy)")
    print("=" * 60)

    # Load all records
    all_records = []
    db_counts = {}
    for db_name, filename in EXPORT_FILES.items():
        records = load_records(db_name, filename)
        db_counts[db_name] = len(records)
        all_records.extend(records)
        print(f"  {db_name:25s}: {len(records):5d} records loaded")

    total_raw = len(all_records)
    print(f"  {'TOTAL':25s}: {total_raw:5d} records")
    print()

    # Run deduplication
    engine = DeduplicationEngine()

    # Add records in a deterministic order.
    # We add databases with best metadata first, so the "representative"
    # record is more likely to come from PubMed/Scopus when metadata is tied.
    db_order = ["pubmed", "scopus", "semantic_scholar", "biorxiv_medrxiv",
                "springernature", "arxiv", "google_scholar"]

    for db_name in db_order:
        db_records = [r for r in all_records if r["source_db"] == db_name]
        for r in db_records:
            engine.add_record(r)

    # Get results
    deduplicated = engine.get_deduplicated_records()
    preprint_links = engine.resolve_preprints()

    # Statistics
    n_unique = len(deduplicated)
    n_duplicates = total_raw - n_unique
    merge_reasons = defaultdict(int)
    for entry in engine.log:
        if entry["action"] == "MERGE":
            # Extract reason type
            reason = entry["reason"]
            if reason.startswith("DOI match"):
                merge_reasons["DOI match"] += 1
            elif reason.startswith("PMID match"):
                merge_reasons["PMID match"] += 1
            elif reason.startswith("arXiv ID match"):
                merge_reasons["arXiv ID match"] += 1
            elif reason.startswith("Exact title match"):
                merge_reasons["Exact title match"] += 1

    # Print summary
    print("DEDUPLICATION RESULTS")
    print("=" * 60)
    print(f"  Records before dedup : {total_raw:,}")
    print(f"  Unique records       : {n_unique:,}")
    print(f"  Duplicates removed   : {n_duplicates:,} ({n_duplicates/total_raw*100:.1f}%)")
    print()
    print("  Merge reasons:")
    for reason, count in sorted(merge_reasons.items(), key=lambda x: -x[1]):
        print(f"    {reason:25s}: {count:5d}")
    print()
    print(f"  Preprint→published links: {len(preprint_links)}")
    print()

    # Records found by N databases
    source_distribution = defaultdict(int)
    for r in deduplicated:
        source_distribution[r["n_sources"]] += 1
    print("  Records found by N databases:")
    for n in sorted(source_distribution.keys()):
        print(f"    {n} database(s): {source_distribution[n]:5d} records")
    print()

    # Cross-database overlap matrix
    print("  Cross-database overlap (records found in both):")
    # Build per-record source sets
    overlap = defaultdict(int)
    for r in deduplicated:
        srcs = r["sources"]
        for i, a in enumerate(srcs):
            for b in srcs[i+1:]:
                key = tuple(sorted([a, b]))
                overlap[key] += 1

    # Print top overlaps
    for (a, b), count in sorted(overlap.items(), key=lambda x: -x[1])[:10]:
        print(f"    {a} ∩ {b}: {count}")
    print()

    # Save outputs
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Deduplicated records
    out_path = os.path.join(OUTPUT_DIR, "deduplicated_records.json")
    output = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "strategy": "Conservative exact matching (DOI → PMID → arXiv ID → normalized title)",
            "total_before_dedup": total_raw,
            "total_after_dedup": n_unique,
            "duplicates_removed": n_duplicates,
            "source_files": EXPORT_FILES,
        },
        "records": deduplicated,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {out_path}")

    # 2. Deduplication log (CSV)
    log_path = os.path.join(OUTPUT_DIR, "deduplication_log.csv")
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "action", "reason", "cluster_id", "source_db", "title", "doi",
            "matched_with_db", "matched_with_title"
        ])
        writer.writeheader()
        writer.writerows(engine.log)
    print(f"  Saved: {log_path}")

    # 3. Statistics JSON
    stats_path = os.path.join(OUTPUT_DIR, "deduplication_stats.json")
    stats = {
        "created": datetime.now().isoformat(),
        "records_per_database": db_counts,
        "total_before_dedup": total_raw,
        "total_after_dedup": n_unique,
        "duplicates_removed": n_duplicates,
        "duplicate_rate": round(n_duplicates / total_raw * 100, 1),
        "merge_reasons": dict(merge_reasons),
        "preprint_to_published_links": len(preprint_links),
        "preprint_links": preprint_links,
        "source_distribution": {str(k): v for k, v in sorted(source_distribution.items())},
    }
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {stats_path}")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
