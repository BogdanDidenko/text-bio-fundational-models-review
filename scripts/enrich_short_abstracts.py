#!/usr/bin/env python3
"""
Enrich records that have short/truncated abstracts (GS snippets etc).

Strategy:
  1. S2 by DOI (if available)
  2. CrossRef by DOI (if available)
  3. S2 by title search (primary path for GS-only records)
  4. PubMed by PMID (if available)

Only replaces abstract if the new one is longer than existing.

Usage:
  python enrich_short_abstracts.py --keys api_keys.json
  python enrich_short_abstracts.py --keys api_keys.json --max-len 250 --dry-run
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
from enrich_abstracts import fetch_abstract_openalex_doi

RECORDS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "deduplicated_records.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "enrichment_short_abstracts_log.json")

MIN_USEFUL_ABSTRACT = 10  # below this = "no abstract"


def retry_get(url, headers=None, params=None, max_retries=3, base_delay=2):
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


def fetch_s2_by_doi(doi, api_key=None):
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{quote(doi, safe='')}"
    headers = {"x-api-key": api_key} if api_key else None
    r = retry_get(url, headers=headers, params={"fields": "abstract"})
    if r is None:
        return None
    abstract = r.json().get("abstract")
    if abstract and len(abstract.strip()) > MIN_USEFUL_ABSTRACT:
        return abstract.strip()
    return None


def fetch_crossref_by_doi(doi):
    url = f"https://api.crossref.org/works/{quote(doi, safe='')}"
    headers = {"User-Agent": "SystematicReviewBot/1.0 (mailto:review@example.com)"}
    r = retry_get(url, headers=headers)
    if r is None:
        return None
    abstract = r.json().get("message", {}).get("abstract", "")
    if abstract and len(abstract.strip()) > MIN_USEFUL_ABSTRACT:
        return re.sub(r"<[^>]+>", "", abstract).strip()
    return None


def fetch_crossref_by_title(record):
    """Fetch abstract from CrossRef by title search (no DOI needed)."""
    url = "https://api.crossref.org/works"
    headers = {"User-Agent": "SystematicReviewBot/1.0 (mailto:review@example.com)"}
    title = str(record.get("title") or "")
    params = {"query.bibliographic": title[:200], "rows": 5}

    r = retry_get(url, headers=headers, params=params)
    if r is None:
        return None

    items = r.json().get("message", {}).get("items", [])
    rejections = []
    for item in items:
        abstract = item.get("abstract", "")
        candidate = {
            "title": (item.get("title") or [""])[0],
            "year": next(
                (parts[0][0] for key in ("published-print", "published-online", "issued")
                 if (parts := (item.get(key) or {}).get("date-parts")) and parts[0]), None
            ),
            "authors": item.get("author") or [],
            "doi": item.get("DOI", ""),
        }
        accepted, status, evidence = accept_title_candidate(record, candidate)
        if abstract and accepted:
            return {
                "accepted": True,
                "abstract": re.sub(r"<[^>]+>", "", abstract).strip(),
                "match": evidence,
                "match_status": status,
                "candidate_doi": candidate["doi"],
            }
        if abstract:
            rejections.append(
                {
                    "candidate_doi": candidate["doi"],
                    "reason": status,
                    "evidence": evidence,
                }
            )
    return {"accepted": False, "rejections": rejections}


def fetch_s2_by_title(record, api_key=None):
    title = str(record.get("title") or "")
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": title[:200], "limit": 5, "fields": "title,abstract,year,authors,paperId"}
    headers = {"x-api-key": api_key} if api_key else None
    r = retry_get(url, headers=headers, params=params)
    if r is None:
        return None

    papers = r.json().get("data", [])
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


def fetch_pubmed_by_pmid(pmid, api_key=None):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": pmid, "rettype": "abstract", "retmode": "text"}
    if api_key:
        params["api_key"] = api_key
    r = retry_get(url, params=params)
    if r is None:
        return None

    lines = r.text.strip().split("\n")
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
    if len(abstract) > MIN_USEFUL_ABSTRACT:
        return abstract
    return None


def main():
    parser = argparse.ArgumentParser(description="Enrich short/truncated abstracts")
    parser.add_argument("--keys", help="Path to api_keys.json")
    parser.add_argument("--input", default=RECORDS_PATH, help="Input JSON record artifact")
    parser.add_argument("--output", default=None, help="Output JSON; defaults to overwriting --input")
    parser.add_argument("--log-output", default=LOG_PATH)
    parser.add_argument("--max-len", type=int, default=250,
                        help="Treat abstracts shorter than this as 'short' (default: 250)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Max records to process (0=all)")
    args = parser.parse_args()
    records_path = args.input
    output_path = args.output or records_path

    ncbi_key = None
    s2_key = None
    openalex_key = None
    if args.keys:
        with open(args.keys) as f:
            keys = json.load(f)
        ncbi_key = keys.get("ncbi")
        s2_key = keys.get("semantic_scholar") or keys.get("S2_API_KEY")
        openalex_key = keys.get("openalex") or keys.get("OPENALEX_API_KEY")

    with open(records_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data["records"]

    # Find records with short abstracts
    short_indices = []
    for i, r in enumerate(records):
        ab = r.get("abstract", "")
        if isinstance(ab, str) and MIN_USEFUL_ABSTRACT < len(ab.strip()) < args.max_len:
            short_indices.append(i)

    print(f"Total records: {len(records)}")
    print(f"Short abstracts (<{args.max_len} chars): {len(short_indices)}")

    if args.limit:
        short_indices = short_indices[:args.limit]
        print(f"Processing first {len(short_indices)}")

    log = {
        "enrichment_version": 2,
        "started": datetime.now().isoformat(),
        "max_len_threshold": args.max_len,
        "total_short": len(short_indices),
        "enriched": 0,
        "s2_doi": 0,
        "openalex_doi": 0,
        "crossref": 0,
        "s2_title": 0,
        "pubmed": 0,
        "not_found": 0,
        "details": [],
    }

    enriched = 0
    for idx_num, rec_idx in enumerate(short_indices):
        rec = records[rec_idx]
        doi = rec.get("doi", "").strip()
        pmid = rec.get("pmid", "").strip()
        title = rec.get("title", "").strip()
        old_len = len(rec.get("abstract", ""))

        if idx_num % 50 == 0:
            print(f"  Processing {idx_num+1}/{len(short_indices)} (enriched: {enriched})...", flush=True)

        new_abstract = None
        source = None
        title_result = None

        # 1. S2 by DOI
        if doi and not new_abstract:
            new_abstract = fetch_s2_by_doi(doi, s2_key)
            if new_abstract and len(new_abstract) > old_len:
                source = "s2_doi"
                log["s2_doi"] += 1
            else:
                new_abstract = None
            time.sleep(0.12)

        # 2. OpenAlex by DOI
        if doi and not new_abstract:
            new_abstract = fetch_abstract_openalex_doi(doi, openalex_key)
            if new_abstract and len(new_abstract) > old_len:
                source = "openalex_doi"
                log["openalex_doi"] += 1
            else:
                new_abstract = None
            time.sleep(0.1)

        # 3. CrossRef by DOI
        if doi and not new_abstract:
            new_abstract = fetch_crossref_by_doi(doi)
            if new_abstract and len(new_abstract) > old_len:
                source = "crossref"
                log["crossref"] += 1
            else:
                new_abstract = None
            time.sleep(0.1)

        # 4. CrossRef by title (fast, no rate limit issues)
        if not new_abstract and title:
            title_result = fetch_crossref_by_title(rec)
            new_abstract = title_result["abstract"] if title_result and title_result.get("accepted") else None
            if new_abstract and len(new_abstract) > old_len:
                source = "crossref_title"
                log["crossref_title"] = log.get("crossref_title", 0) + 1
            else:
                new_abstract = None
            time.sleep(0.05)

        # 5. PubMed by PMID
        if pmid and not new_abstract:
            new_abstract = fetch_pubmed_by_pmid(pmid, ncbi_key)
            if new_abstract and len(new_abstract) > old_len:
                source = "pubmed"
                log["pubmed"] += 1
            else:
                new_abstract = None
            time.sleep(0.1)

        # 6. S2 by title, with title plus independent metadata corroboration.
        # if not new_abstract and title:
        #     title_result = fetch_s2_by_title(rec, s2_key)
        #     new_abstract = title_result["abstract"] if title_result else None
        #     if new_abstract and len(new_abstract) > old_len:
        #         source = "s2_title"
        #         log["s2_title"] += 1
        #     else:
        #         new_abstract = None
        #     time.sleep(0.5)

        if new_abstract and source:
            enriched += 1
            if not args.dry_run:
                records[rec_idx]["abstract"] = new_abstract
                records[rec_idx]["abstract_enriched_from"] = source
                records[rec_idx]["abstract_old_len"] = old_len
            detail = {
                "cluster_id": rec.get("cluster_id"),
                "title": title[:80],
                "source": source,
                "old_len": old_len,
                "new_len": len(new_abstract),
                "sources_db": rec.get("sources", []),
            }
            if source == "crossref_title":
                detail["title_match"] = title_result["match"]
                detail["title_match_status"] = title_result["match_status"]
                detail["source_candidate_doi"] = title_result["candidate_doi"]
            log["details"].append(detail)
        else:
            log["not_found"] += 1
            if title_result and title_result.get("rejections"):
                log["details"].append(
                    {
                        "cluster_id": rec.get("cluster_id"),
                        "title": title[:80],
                        "source": None,
                        "crossref_title_search_rejections": title_result["rejections"],
                    }
                )

    log["enriched"] = enriched
    log["finished"] = datetime.now().isoformat()

    print()
    print("=" * 60)
    print("SHORT ABSTRACT ENRICHMENT RESULTS")
    print("=" * 60)
    print(f"  Processed:     {len(short_indices)}")
    print(f"  Enriched:      {enriched} ({enriched/max(len(short_indices),1)*100:.1f}%)")
    print(f"    S2 (DOI):    {log['s2_doi']}")
    print(f"    OpenAlex DOI:{log['openalex_doi']}")
    print(f"    CrossRef DOI:{log['crossref']}")
    print(f"    CrossRef tit:{log.get('crossref_title', 0)}")
    print(f"    PubMed:      {log['pubmed']}")
    print(f"    S2 (title):  {log['s2_title']}")
    print(f"  Not found:     {log['not_found']}")

    if not args.dry_run:
        # Also strip HTML from all abstracts while we're at it
        html_cleaned = 0
        for r in records:
            ab = r.get("abstract", "")
            if isinstance(ab, str) and re.search(r'<[a-z/][^>]*>', ab, re.IGNORECASE):
                cleaned = re.sub(r'<[^>]+>', '', ab).strip()
                cleaned = re.sub(r'\s+', ' ', cleaned)
                if cleaned != ab:
                    r["abstract"] = cleaned
                    html_cleaned += 1
        print(f"  HTML stripped:  {html_cleaned} records")

        # Save
        data["metadata"]["short_abstract_enrichment"] = {
            "date": datetime.now().isoformat(),
            "threshold": args.max_len,
            "total_short": len(short_indices),
            "enriched": enriched,
            "html_cleaned": html_cleaned,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Saved: {output_path}")

    with open(args.log_output, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"  Log: {args.log_output}")
    print("\nDone.")


if __name__ == "__main__":
    main()
