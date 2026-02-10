#!/usr/bin/env python3
"""
Enrich deduplicated records with missing abstracts.

Fetches abstracts from multiple APIs for records that lack them:
  1. Semantic Scholar (by DOI, then by title)
  2. CrossRef (by DOI)
  3. PubMed Entrez (by PMID)

Usage:
  python enrich_abstracts.py
  python enrich_abstracts.py --keys api_keys.json   # for higher S2/NCBI rate limits
  python enrich_abstracts.py --dry-run               # just report, don't modify

Input:  data/deduplicated_records.json
Output: data/deduplicated_records.json (updated in place)
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
    missing = [i for i, r in enumerate(records) if not has_abstract(r)]

    print(f"Total records: {total}")
    print(f"Missing abstracts: {len(missing)}")
    if args.limit:
        missing = missing[:args.limit]
        print(f"Processing first {len(missing)} records")
    print()

    # Enrichment log
    log = {
        "started": datetime.now().isoformat(),
        "total_missing": len(missing),
        "s2_doi_found": 0,
        "s2_title_found": 0,
        "crossref_found": 0,
        "pubmed_found": 0,
        "still_missing": 0,
        "details": [],
    }

    enriched_count = 0
    for idx, rec_idx in enumerate(missing):
        rec = records[rec_idx]
        doi = rec.get("doi", "").strip()
        pmid = rec.get("pmid", "").strip()
        title = rec.get("title", "").strip()
        sources = rec.get("sources", [])

        if idx % 50 == 0:
            print(f"  Processing {idx+1}/{len(missing)} (enriched so far: {enriched_count})...")

        abstract = None
        source_api = None

        # Strategy 1: S2 by DOI
        if doi and not abstract:
            abstract = fetch_abstract_s2_doi(doi, s2_key)
            if abstract:
                source_api = "s2_doi"
                log["s2_doi_found"] += 1
            time.sleep(0.15)  # S2 rate limit: ~100 req/5min without key

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
            log["still_missing"] += 1
            log["details"].append({
                "cluster_id": rec.get("cluster_id"),
                "title": title[:100],
                "doi": doi,
                "source_api": None,
                "abstract_len": 0,
            })

    log["finished"] = datetime.now().isoformat()
    log["enriched"] = enriched_count

    # Print summary
    print()
    print("=" * 60)
    print("ENRICHMENT RESULTS")
    print("=" * 60)
    print(f"  Records processed:   {len(missing)}")
    print(f"  Abstracts found:     {enriched_count} ({enriched_count/len(missing)*100:.1f}%)" if missing else "")
    print(f"    via S2 (DOI):      {log['s2_doi_found']}")
    print(f"    via CrossRef:      {log['crossref_found']}")
    print(f"    via PubMed:        {log['pubmed_found']}")
    print(f"    via S2 (title):    {log['s2_title_found']}")
    print(f"  Still missing:       {log['still_missing']}")
    print()

    if not args.dry_run and enriched_count > 0:
        # Update metadata
        data["metadata"]["abstract_enrichment"] = {
            "date": datetime.now().isoformat(),
            "enriched_count": enriched_count,
            "sources": {
                "s2_doi": log["s2_doi_found"],
                "crossref": log["crossref_found"],
                "pubmed": log["pubmed_found"],
                "s2_title": log["s2_title_found"],
            }
        }

        # Recalculate abstract stats
        new_has_abs = sum(1 for r in records if has_abstract(r))
        print(f"  Abstract coverage: {new_has_abs}/{total} ({new_has_abs/total*100:.1f}%)")
        print()

        with open(RECORDS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Updated: {RECORDS_PATH}")

    # Save log
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {LOG_PATH}")

    print("\nDone.")


if __name__ == "__main__":
    main()
