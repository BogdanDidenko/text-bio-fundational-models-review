#!/usr/bin/env python3
"""
Enrich deduplicated records with missing abstracts, then exclude
records that still lack abstracts.

Pipeline:
  1. Fetch abstracts from S2/CrossRef/PubMed APIs for records missing them
  2. Exclude records that still have no abstract after enrichment
     (saved to data/excluded_no_abstract.json for audit)

Usage:
  python enrich_abstracts.py --keys api_keys.json
  python enrich_abstracts.py --keys api_keys.json --dry-run
  python enrich_abstracts.py --skip-fetch            # only run exclusion step

Input:  data/deduplicated_records.json
Output: data/deduplicated_records.json (updated — only records WITH abstracts)
        data/excluded_no_abstract.json (records excluded for missing abstract)
        data/enrichment_log.json (detailed log)
"""

import json
import os
import re
import time
import argparse
import requests
from datetime import datetime
from urllib.parse import quote

RECORDS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "deduplicated_records.json")
EXCLUDED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "excluded_no_abstract.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "enrichment_log.json")

# Minimum abstract length to consider "present"
MIN_ABSTRACT_LEN = 10


def has_abstract(record):
    """Check if a record has a meaningful abstract."""
    abs_text = record.get("abstract", "")
    return isinstance(abs_text, str) and len(abs_text.strip()) > MIN_ABSTRACT_LEN


def retry_get(url, headers=None, params=None, max_retries=3, base_delay=2):
    """GET request with exponential backoff for rate limits."""
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            if r.status_code == 429:
                wait = base_delay * (2 ** attempt)
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                return None
            time.sleep(base_delay)
    return None


# ---------------------------------------------------------------------------
# API fetchers
# ---------------------------------------------------------------------------

def fetch_abstract_s2_doi(doi, api_key=None):
    """Fetch abstract from Semantic Scholar by DOI."""
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{quote(doi, safe='')}"
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    params = {"fields": "abstract"}

    r = retry_get(url, headers=headers, params=params)
    if r is None:
        return None

    data = r.json()
    abstract = data.get("abstract")
    if abstract and len(abstract.strip()) > MIN_ABSTRACT_LEN:
        return abstract.strip()
    return None


def fetch_abstract_s2_title(title, api_key=None):
    """Fetch abstract from Semantic Scholar by title search."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    params = {"query": title[:200], "limit": 3, "fields": "title,abstract"}

    r = retry_get(url, headers=headers, params=params)
    if r is None:
        return None

    data = r.json()
    papers = data.get("data", [])
    if not papers:
        return None

    # Find best title match
    title_lower = title.lower().strip()
    for p in papers:
        p_title = (p.get("title") or "").lower().strip()
        if p_title == title_lower and p.get("abstract"):
            return p["abstract"].strip()

    # If no exact match, take first result if title is very similar
    if papers[0].get("abstract") and papers[0].get("title"):
        p_title = papers[0]["title"].lower().strip()
        # Simple check: titles share >80% words
        t_words = set(title_lower.split())
        p_words = set(p_title.split())
        if t_words and p_words:
            overlap = len(t_words & p_words) / max(len(t_words), len(p_words))
            if overlap > 0.8:
                return papers[0]["abstract"].strip()

    return None


def fetch_abstract_crossref(doi):
    """Fetch abstract from CrossRef by DOI."""
    url = f"https://api.crossref.org/works/{quote(doi, safe='')}"
    headers = {"User-Agent": "SystematicReviewBot/1.0 (mailto:bogdan@example.com)"}

    r = retry_get(url, headers=headers)
    if r is None:
        return None

    data = r.json()
    message = data.get("message", {})
    abstract = message.get("abstract", "")
    if abstract and len(abstract.strip()) > MIN_ABSTRACT_LEN:
        # CrossRef abstracts often have JATS XML tags — strip them
        abstract = re.sub(r"<[^>]+>", "", abstract).strip()
        return abstract
    return None


def fetch_abstract_pubmed(pmid, api_key=None):
    """Fetch abstract from PubMed Entrez by PMID."""
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": pmid,
        "rettype": "abstract",
        "retmode": "text",
    }
    if api_key:
        params["api_key"] = api_key

    r = retry_get(url, params=params)
    if r is None:
        return None

    text = r.text.strip()
    # The text format returns title + authors + abstract + journal info
    # Extract abstract: typically after the author list and before the journal/DOI
    # Look for a blank line followed by text
    lines = text.split("\n")
    abstract_lines = []
    in_abstract = False
    for i, line in enumerate(lines):
        if line.strip() == "" and i > 2 and not in_abstract:
            in_abstract = True
            continue
        if in_abstract:
            if line.strip() == "" and abstract_lines:
                break
            if line.strip():
                abstract_lines.append(line.strip())

    abstract = " ".join(abstract_lines)
    if len(abstract) > MIN_ABSTRACT_LEN:
        return abstract
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Enrich records with missing abstracts")
    parser.add_argument("--keys", help="Path to api_keys.json")
    parser.add_argument("--dry-run", action="store_true", help="Report only, don't modify records")
    parser.add_argument("--limit", type=int, default=0, help="Max records to process (0=all)")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip API fetching, only run exclusion step")
    args = parser.parse_args()

    # Load API keys
    s2_key = None
    ncbi_key = None
    if args.keys:
        with open(args.keys) as f:
            keys = json.load(f)
        s2_key = keys.get("semantic_scholar")
        ncbi_key = keys.get("ncbi")

    # Load records
    with open(RECORDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data["records"]
    total = len(records)

    # ------------------------------------------------------------------
    # Step 1: Fetch missing abstracts from APIs
    # ------------------------------------------------------------------
    log = {
        "started": datetime.now().isoformat(),
        "total_records": total,
        "total_missing_before": 0,
        "s2_doi_found": 0,
        "s2_title_found": 0,
        "crossref_found": 0,
        "pubmed_found": 0,
        "enriched": 0,
        "still_missing_after_fetch": 0,
        "excluded_no_abstract": 0,
        "records_for_screening": 0,
        "details": [],
    }

    missing = [i for i, r in enumerate(records) if not has_abstract(r)]
    log["total_missing_before"] = len(missing)

    print(f"Total records: {total}")
    print(f"Missing abstracts: {len(missing)}")

    if not args.skip_fetch and missing:
        if args.limit:
            fetch_list = missing[:args.limit]
            print(f"Processing first {len(fetch_list)} records")
        else:
            fetch_list = missing
        print()

        enriched_count = 0
        for idx, rec_idx in enumerate(fetch_list):
            rec = records[rec_idx]
            doi = rec.get("doi", "").strip()
            pmid = rec.get("pmid", "").strip()
            title = rec.get("title", "").strip()

            if idx % 50 == 0:
                print(f"  Processing {idx+1}/{len(fetch_list)} (enriched so far: {enriched_count})...")

            abstract = None
            source_api = None

            # Strategy 1: S2 by DOI
            if doi and not abstract:
                abstract = fetch_abstract_s2_doi(doi, s2_key)
                if abstract:
                    source_api = "s2_doi"
                    log["s2_doi_found"] += 1
                time.sleep(0.15)

            # Strategy 2: CrossRef by DOI
            if doi and not abstract:
                abstract = fetch_abstract_crossref(doi)
                if abstract:
                    source_api = "crossref"
                    log["crossref_found"] += 1
                time.sleep(0.1)

            # Strategy 3: PubMed by PMID
            if pmid and not abstract:
                abstract = fetch_abstract_pubmed(pmid, ncbi_key)
                if abstract:
                    source_api = "pubmed"
                    log["pubmed_found"] += 1
                time.sleep(0.12)

            # Strategy 4: S2 by title (for records without DOI/PMID)
            if not doi and not pmid and title and not abstract:
                abstract = fetch_abstract_s2_title(title, s2_key)
                if abstract:
                    source_api = "s2_title"
                    log["s2_title_found"] += 1
                time.sleep(0.15)

            if abstract:
                enriched_count += 1
                if not args.dry_run:
                    records[rec_idx]["abstract"] = abstract
                    records[rec_idx]["abstract_source"] = source_api
                log["details"].append({
                    "cluster_id": rec.get("cluster_id"),
                    "title": title[:100],
                    "doi": doi,
                    "source_api": source_api,
                    "abstract_len": len(abstract),
                })
            else:
                log["details"].append({
                    "cluster_id": rec.get("cluster_id"),
                    "title": title[:100],
                    "doi": doi,
                    "source_api": None,
                    "abstract_len": 0,
                })

        log["enriched"] = enriched_count

        print()
        print("=" * 60)
        print("ENRICHMENT — STEP 1: API FETCH")
        print("=" * 60)
        print(f"  Records processed:   {len(fetch_list)}")
        if fetch_list:
            print(f"  Abstracts found:     {enriched_count} ({enriched_count/len(fetch_list)*100:.1f}%)")
        print(f"    via S2 (DOI):      {log['s2_doi_found']}")
        print(f"    via CrossRef:      {log['crossref_found']}")
        print(f"    via PubMed:        {log['pubmed_found']}")
        print(f"    via S2 (title):    {log['s2_title_found']}")
    elif args.skip_fetch:
        print("  Skipping API fetch (--skip-fetch)")
    print()

    # ------------------------------------------------------------------
    # Step 2: Exclude records without abstract
    # ------------------------------------------------------------------
    still_missing = [i for i, r in enumerate(records) if not has_abstract(r)]
    log["still_missing_after_fetch"] = len(still_missing)

    print("=" * 60)
    print("ENRICHMENT — STEP 2: EXCLUDE RECORDS WITHOUT ABSTRACT")
    print("=" * 60)
    print(f"  Records without abstract after enrichment: {len(still_missing)}")

    if still_missing and not args.dry_run:
        # Separate records into included and excluded
        excluded_records = [records[i] for i in still_missing]
        included_records = [r for i, r in enumerate(records) if i not in set(still_missing)]

        log["excluded_no_abstract"] = len(excluded_records)
        log["records_for_screening"] = len(included_records)

        # Save excluded records for audit trail
        excluded_output = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "reason": "No abstract available after API enrichment (S2, CrossRef, PubMed)",
                "total_excluded": len(excluded_records),
                "exclusion_code": "EC_NO_ABSTRACT",
            },
            "records": excluded_records,
        }
        with open(EXCLUDED_PATH, "w", encoding="utf-8") as f:
            json.dump(excluded_output, f, ensure_ascii=False, indent=2)
        print(f"  Excluded: {len(excluded_records)} records → {EXCLUDED_PATH}")

        # Update main records file
        data["records"] = included_records
        data["metadata"]["abstract_enrichment"] = {
            "date": datetime.now().isoformat(),
            "enriched_count": log["enriched"],
            "excluded_no_abstract": len(excluded_records),
            "records_for_screening": len(included_records),
            "sources": {
                "s2_doi": log["s2_doi_found"],
                "crossref": log["crossref_found"],
                "pubmed": log["pubmed_found"],
                "s2_title": log["s2_title_found"],
            }
        }
        data["metadata"]["total_after_dedup"] = len(included_records)

        with open(RECORDS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Updated:  {len(included_records)} records → {RECORDS_PATH}")
    elif args.dry_run:
        log["excluded_no_abstract"] = len(still_missing)
        log["records_for_screening"] = total - len(still_missing)
        print(f"  [DRY RUN] Would exclude {len(still_missing)} records")
        print(f"  [DRY RUN] Would keep {total - len(still_missing)} records for screening")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    log["finished"] = datetime.now().isoformat()
    print()
    print("=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"  Total after dedup:         {total}")
    print(f"  Missing before enrichment: {log['total_missing_before']}")
    print(f"  Enriched via API:          {log['enriched']}")
    print(f"  Excluded (no abstract):    {log['excluded_no_abstract']}")
    print(f"  Records for screening:     {log['records_for_screening']}")
    print()

    # Save log
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {LOG_PATH}")

    print("\nDone.")


if __name__ == "__main__":
    main()
