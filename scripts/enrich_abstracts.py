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

from metadata_match import accept_title_candidate
from reproduce_search import _openalex_abstract

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


def fetch_abstract_openalex_doi(doi, api_key=None):
    """Fetch and reconstruct an abstract from an OpenAlex Work by DOI."""
    url = f"https://api.openalex.org/works/doi:{quote(doi, safe='')}"
    params = {"api_key": api_key} if api_key else None
    r = retry_get(url, params=params)
    if r is None:
        return None
    abstract = _openalex_abstract(r.json().get("abstract_inverted_index"))
    if len(abstract.strip()) > MIN_ABSTRACT_LEN:
        return abstract.strip()
    return None


def fetch_abstract_s2_title(record, api_key=None):
    """Fetch abstract from Semantic Scholar by title search."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    title = str(record.get("title") or "")
    params = {"query": title[:200], "limit": 5, "fields": "title,abstract,year,authors,paperId"}

    r = retry_get(url, headers=headers, params=params)
    if r is None:
        return None

    data = r.json()
    papers = data.get("data", [])
    if not papers:
        return None

    rejections = []
    for p in papers:
        if not p.get("abstract"):
            continue
        accepted, status, evidence = accept_title_candidate(record, p)
        if accepted:
            return {
                "accepted": True,
                "abstract": p["abstract"].strip(),
                "match": evidence,
                "match_status": status,
                "candidate_id": p.get("paperId", ""),
            }
        rejections.append(
            {
                "candidate_id": p.get("paperId", ""),
                "reason": status,
                "evidence": evidence,
            }
        )
    return {"accepted": False, "rejections": rejections}


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
    parser.add_argument("--input", default=RECORDS_PATH, help="Input JSON record artifact")
    parser.add_argument("--output", default=None, help="Output JSON; defaults to overwriting --input")
    parser.add_argument("--excluded-output", default=EXCLUDED_PATH)
    parser.add_argument("--log-output", default=LOG_PATH)
    parser.add_argument("--dry-run", action="store_true", help="Report only, don't modify records")
    parser.add_argument("--limit", type=int, default=0, help="Max records to process (0=all)")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip API fetching, only run exclusion step")
    args = parser.parse_args()
    records_path = args.input
    output_path = args.output or records_path

    # Load API keys
    s2_key = None
    ncbi_key = None
    openalex_key = None
    if args.keys:
        with open(args.keys) as f:
            keys = json.load(f)
        s2_key = keys.get("semantic_scholar") or keys.get("S2_API_KEY")
        ncbi_key = keys.get("ncbi")
        openalex_key = keys.get("openalex") or keys.get("OPENALEX_API_KEY")

    # Load records
    with open(records_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data["records"]
    total = len(records)

    # ------------------------------------------------------------------
    # Step 1: Fetch missing abstracts from APIs
    # ------------------------------------------------------------------
    log = {
        "enrichment_version": 2,
        "started": datetime.now().isoformat(),
        "total_records": total,
        "total_missing_before": 0,
        "s2_doi_found": 0,
        "openalex_doi_found": 0,
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
    fetch_list = []

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
            title_result = None

            # Strategy 1: S2 by DOI
            if doi and not abstract:
                abstract = fetch_abstract_s2_doi(doi, s2_key)
                if abstract:
                    source_api = "s2_doi"
                    log["s2_doi_found"] += 1
                time.sleep(0.15)

            # Strategy 2: OpenAlex by DOI
            if doi and not abstract:
                abstract = fetch_abstract_openalex_doi(doi, openalex_key)
                if abstract:
                    source_api = "openalex_doi"
                    log["openalex_doi_found"] += 1
                time.sleep(0.1)

            # Strategy 3: CrossRef by DOI
            if doi and not abstract:
                abstract = fetch_abstract_crossref(doi)
                if abstract:
                    source_api = "crossref"
                    log["crossref_found"] += 1
                time.sleep(0.1)

            # Strategy 4: PubMed by PMID
            if pmid and not abstract:
                abstract = fetch_abstract_pubmed(pmid, ncbi_key)
                if abstract:
                    source_api = "pubmed"
                    log["pubmed_found"] += 1
                time.sleep(0.12)

            # Strategy 5: S2 by title (for records without DOI/PMID)
            if not doi and not pmid and title and not abstract:
                title_result = fetch_abstract_s2_title(rec, s2_key)
                if title_result and title_result.get("accepted"):
                    abstract = title_result["abstract"]
                    source_api = "s2_title"
                    log["s2_title_found"] += 1
                time.sleep(0.15)

            if abstract:
                enriched_count += 1
                if not args.dry_run:
                    records[rec_idx]["abstract"] = abstract
                    records[rec_idx]["abstract_source"] = source_api
                detail = {
                    "cluster_id": rec.get("cluster_id"),
                    "title": title[:100],
                    "doi": doi,
                    "source_api": source_api,
                    "abstract_len": len(abstract),
                }
                if source_api == "s2_title":
                    detail["title_match"] = title_result["match"]
                    detail["title_match_status"] = title_result["match_status"]
                    detail["source_candidate_id"] = title_result["candidate_id"]
                log["details"].append(detail)
            else:
                detail = {
                    "cluster_id": rec.get("cluster_id"),
                    "title": title[:100],
                    "doi": doi,
                    "source_api": None,
                    "abstract_len": 0,
                }
                if title_result and title_result.get("rejections"):
                    detail["s2_title_search_rejections"] = title_result["rejections"]
                log["details"].append(detail)

        log["enriched"] = enriched_count

        print()
        print("=" * 60)
        print("ENRICHMENT — STEP 1: API FETCH")
        print("=" * 60)
        print(f"  Records processed:   {len(fetch_list)}")
        if fetch_list:
            print(f"  Abstracts found:     {enriched_count} ({enriched_count/len(fetch_list)*100:.1f}%)")
        print(f"    via S2 (DOI):      {log['s2_doi_found']}")
        print(f"    via OpenAlex DOI:  {log['openalex_doi_found']}")
        print(f"    via CrossRef:      {log['crossref_found']}")
        print(f"    via PubMed:        {log['pubmed_found']}")
        print(f"    via S2 (title):    {log['s2_title_found']}")
    elif args.skip_fetch:
        print("  Skipping API fetch (--skip-fetch)")
    print()

    # A bounded fetch is a diagnostic/probe mode. It must not turn records that
    # were never attempted into implicit screening exclusions.
    unattempted_missing = (
        len(missing) - len(fetch_list)
        if not args.skip_fetch and args.limit and len(missing) > len(fetch_list)
        else 0
    )
    if unattempted_missing:
        log.update(
            {
                "finished": datetime.now().isoformat(),
                "status": "incomplete_fetch_limit",
                "unattempted_missing_abstracts": unattempted_missing,
            }
        )
        with open(args.log_output, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        print(
            "ABSTRACT ENRICHMENT INCOMPLETE: "
            f"{unattempted_missing} missing abstracts were not attempted; "
            "no screening artifact was written."
        )
        return 2

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
                "reason": "No abstract available after API enrichment (S2, OpenAlex, Crossref, PubMed)",
                "total_excluded": len(excluded_records),
                "exclusion_code": "EC_NO_ABSTRACT",
            },
            "records": excluded_records,
        }
        with open(args.excluded_output, "w", encoding="utf-8") as f:
            json.dump(excluded_output, f, ensure_ascii=False, indent=2)
        print(f"  Excluded: {len(excluded_records)} records → {args.excluded_output}")

        # Update main records file
        data["records"] = included_records
        data["metadata"]["abstract_enrichment"] = {
            "date": datetime.now().isoformat(),
            "enriched_count": log["enriched"],
            "excluded_no_abstract": len(excluded_records),
            "records_for_screening": len(included_records),
            "sources": {
                "s2_doi": log["s2_doi_found"],
                "openalex_doi": log["openalex_doi_found"],
                "crossref": log["crossref_found"],
                "pubmed": log["pubmed_found"],
                "s2_title": log["s2_title_found"],
            }
        }
        data["metadata"]["total_after_dedup"] = len(included_records)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Updated:  {len(included_records)} records → {output_path}")
    elif args.dry_run:
        log["excluded_no_abstract"] = len(still_missing)
        log["records_for_screening"] = total - len(still_missing)
        print(f"  [DRY RUN] Would exclude {len(still_missing)} records")
        print(f"  [DRY RUN] Would keep {total - len(still_missing)} records for screening")
    else:
        log["records_for_screening"] = len(records)
        excluded_output = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "reason": "No abstract available after API enrichment (S2, OpenAlex, Crossref, PubMed)",
                "total_excluded": 0,
                "exclusion_code": "EC_NO_ABSTRACT",
            },
            "records": [],
        }
        with open(args.excluded_output, "w", encoding="utf-8") as f:
            json.dump(excluded_output, f, ensure_ascii=False, indent=2)
        data.setdefault("metadata", {})["abstract_enrichment"] = {
            "date": datetime.now().isoformat(),
            "enriched_count": log["enriched"],
            "excluded_no_abstract": 0,
            "records_for_screening": len(records),
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Updated:  {len(records)} records → {output_path}")

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
    with open(args.log_output, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {args.log_output}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
