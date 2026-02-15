#!/usr/bin/env python3
"""
Reproducible Systematic Review Search Script
=============================================

Reproduces the literature search for:
"Generative Foundation Models Bridging Text and Biological Data: A Scoping Review"

Usage:
    python reproduce_search.py --keys api_keys.json
    python reproduce_search.py --keys api_keys.json --databases pubmed,scopus
    python reproduce_search.py --keys api_keys.json --output-dir results/

Requires: pip install requests scholarly
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, date

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(SCRIPT_DIR, "search_config.json")
DATE_CUTOFF = "2026-02-28"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def retry_request(url, params=None, headers=None, max_retries=3, delay=2.0):
    """GET request with exponential backoff."""
    for attempt in range(max_retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=60)
            if r.status_code == 429:
                wait = delay * (2 ** attempt)
                log(f"  Rate limited (429). Waiting {wait:.0f}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait = delay * (2 ** attempt)
                log(f"  Request error: {e}. Retrying in {wait:.0f}s...")
                time.sleep(wait)
            else:
                raise
    return None


def date_within_cutoff(date_str, cutoff=DATE_CUTOFF):
    """Check if a date string is <= cutoff. Handles YYYY-MM-DD, YYYY-MM, YYYY."""
    if not date_str:
        return True
    try:
        if len(date_str) == 4:
            return int(date_str) <= int(cutoff[:4])
        if len(date_str) == 7:
            return date_str <= cutoff[:7]
        return date_str[:10] <= cutoff
    except (ValueError, TypeError):
        return True


def save_results(output_dir, db_name, data):
    """Save results to JSON file."""
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(output_dir, f"{db_name}_{today}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log(f"  Saved {filepath}")
    return filepath


# ---------------------------------------------------------------------------
# 1. PubMed (NCBI Entrez)
# ---------------------------------------------------------------------------

def search_pubmed(config, keys):
    """Search PubMed via Entrez E-utilities API."""
    log("PubMed: Starting search...")
    api_key = keys.get("ncbi", "")
    query = config["databases"]["pubmed"]["query"]

    # Step 1: ESearch to get count and history
    params = {
        "db": "pubmed",
        "retmode": "json",
        "retmax": 0,
        "usehistory": "y",
        "term": query,
    }
    if api_key:
        params["api_key"] = api_key

    r = retry_request("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params=params)
    data = r.json()
    result = data["esearchresult"]
    count = int(result["count"])
    webenv = result["webenv"]
    qkey = result["querykey"]
    log(f"  PubMed: {count} results found")

    # Step 2: EFetch in batches of 500
    records = []
    batch_size = 500
    for start in range(0, count, batch_size):
        log(f"  Fetching {start+1}-{min(start+batch_size, count)} of {count}...")
        fetch_params = {
            "db": "pubmed",
            "retmode": "xml",
            "rettype": "abstract",
            "WebEnv": webenv,
            "query_key": qkey,
            "retstart": start,
            "retmax": batch_size,
        }
        if api_key:
            fetch_params["api_key"] = api_key

        fr = retry_request("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params=fetch_params)
        root = ET.fromstring(fr.content)

        for article in root.findall(".//PubmedArticle"):
            rec = _parse_pubmed_article(article)
            if rec:
                records.append(rec)

        time.sleep(0.2)

    log(f"  PubMed: {len(records)} records retrieved")
    return {
        "database": "PubMed",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "query": query,
        "filters": "free full text[sb], English[Language], 2018-01-01 to 2026-02-28",
        "total_results": count,
        "records_fetched": len(records),
        "records": records,
    }


def _parse_pubmed_article(article):
    """Parse a single PubmedArticle XML element."""
    pmid_el = article.find(".//PMID")
    if pmid_el is None:
        return None
    pmid = pmid_el.text

    medline = article.find(".//MedlineCitation")
    art = medline.find(".//Article") if medline is not None else None
    if art is None:
        return None

    title = art.findtext(".//ArticleTitle", "")
    abstract_parts = art.findall(".//Abstract/AbstractText")
    abstract = " ".join(t.text or "" for t in abstract_parts) if abstract_parts else ""

    # Authors
    authors = []
    for au in art.findall(".//AuthorList/Author"):
        last = au.findtext("LastName", "")
        first = au.findtext("ForeName", "")
        if last:
            authors.append(f"{last} {first}".strip())
    authors_str = "; ".join(authors)

    # Date
    pub_date = art.find(".//Journal/JournalIssue/PubDate")
    year = pub_date.findtext("Year", "") if pub_date is not None else ""
    month = pub_date.findtext("Month", "") if pub_date is not None else ""

    # Journal
    journal = art.findtext(".//Journal/Title", "")

    # DOI
    doi = ""
    for aid in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
        if aid.get("IdType") == "doi":
            doi = aid.text or ""
            break

    return {
        "pmid": pmid,
        "doi": doi,
        "title": title,
        "abstract": abstract,
        "authors": authors_str,
        "year": year,
        "month": month,
        "journal": journal,
        "source": "pubmed",
    }


# ---------------------------------------------------------------------------
# 2. Scopus (Elsevier API)
# ---------------------------------------------------------------------------

def search_scopus(config, keys):
    """Search Scopus via Elsevier API."""
    log("Scopus: Starting search...")
    api_key = keys.get("scopus", "")
    if not api_key:
        log("  WARNING: No Scopus API key provided. Skipping.")
        return None

    query = config["databases"]["scopus"]["query"]
    date_post_filter = config["databases"]["scopus"].get("date_post_filter", DATE_CUTOFF)

    headers = {
        "Accept": "application/json",
    }

    # Paginated search
    records = []
    total = None
    start = 0
    per_page = 25

    while True:
        params = {
            "query": query,
            "start": start,
            "count": per_page,
            "sort": "pubyear",
            "apiKey": api_key,
        }
        r = retry_request("https://api.elsevier.com/content/search/scopus", params=params, headers=headers)
        data = r.json()

        search_results = data.get("search-results", {})
        if total is None:
            total = int(search_results.get("opensearch:totalResults", 0))
            log(f"  Scopus: {total} results found")

        entries = search_results.get("entry", [])
        if not entries or (len(entries) == 1 and "error" in entries[0]):
            break

        for entry in entries:
            rec = _parse_scopus_entry(entry)
            if rec:
                records.append(rec)

        start += per_page
        if start >= total:
            break

        log(f"  Fetched {min(start, total)} of {total}...")
        time.sleep(0.15)

    # Post-filter by date
    pre_filter_count = len(records)
    records = [r for r in records if date_within_cutoff(r.get("date", ""), date_post_filter)]
    log(f"  Scopus: {pre_filter_count} retrieved, {len(records)} after date filter (<= {date_post_filter})")

    return {
        "database": "Scopus",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "query": query,
        "filters": f"PUBYEAR > 2017, OPENACCESS(1), LANGUAGE(English), post-filter <= {date_post_filter}",
        "total_results": total,
        "records_before_date_filter": pre_filter_count,
        "records_fetched": len(records),
        "records": records,
    }


def _parse_scopus_entry(entry):
    """Parse a single Scopus search result entry."""
    return {
        "scopus_id": entry.get("dc:identifier", "").replace("SCOPUS_ID:", ""),
        "doi": entry.get("prism:doi", ""),
        "title": entry.get("dc:title", ""),
        "authors": entry.get("dc:creator", ""),
        "journal": entry.get("prism:publicationName", ""),
        "year": entry.get("prism:coverDate", "")[:4] if entry.get("prism:coverDate") else "",
        "date": entry.get("prism:coverDate", ""),
        "cited_by": entry.get("citedby-count", "0"),
        "source": "scopus",
    }


# ---------------------------------------------------------------------------
# 3. Semantic Scholar (Bulk Search API)
# ---------------------------------------------------------------------------

def search_semantic_scholar(config, keys):
    """Search Semantic Scholar via /paper/search/bulk API."""
    log("Semantic Scholar: Starting search...")
    api_key = keys.get("semantic_scholar", "")
    s2_config = config["databases"]["semantic_scholar"]
    fields = s2_config["fields"]
    year_range = s2_config["year_range"]
    date_post_filter = s2_config.get("date_post_filter", DATE_CUTOFF)

    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    all_records = {}  # keyed by paperId for dedup

    for query_name, query_text in s2_config["queries"].items():
        log(f"  S2 query '{query_name}': searching...")
        token = None
        query_count = 0

        while True:
            params = {
                "query": query_text,
                "fields": fields,
                "year": year_range,
            }
            if token:
                params["token"] = token

            r = retry_request(
                "https://api.semanticscholar.org/graph/v1/paper/search/bulk",
                params=params, headers=headers,
            )
            data = r.json()

            if "data" not in data:
                log(f"    No data in response: {str(data)[:200]}")
                break

            for paper in data["data"]:
                pid = paper.get("paperId", "")
                if pid and pid not in all_records:
                    all_records[pid] = _parse_s2_paper(paper)
                    query_count += 1

            token = data.get("token")
            if not token:
                break

            time.sleep(1.0)

        log(f"    '{query_name}': {query_count} new records")

    records = list(all_records.values())

    # Post-filter by date
    pre_filter_count = len(records)
    records = [r for r in records if date_within_cutoff(r.get("date", ""), date_post_filter)]
    log(f"  S2: {pre_filter_count} total unique, {len(records)} after date filter (<= {date_post_filter})")

    return {
        "database": "Semantic Scholar (bulk)",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "query": s2_config["queries"]["main"],
        "filters": f"year={year_range}, post-filter <= {date_post_filter}",
        "total_results": pre_filter_count,
        "records_fetched": len(records),
        "records": records,
    }


def _parse_s2_paper(paper):
    """Parse a single Semantic Scholar paper object."""
    ext = paper.get("externalIds") or {}
    authors_list = paper.get("authors") or []
    authors_str = "; ".join(a.get("name", "") for a in authors_list)
    oa_pdf = paper.get("openAccessPdf") or {}

    return {
        "s2_id": paper.get("paperId", ""),
        "doi": ext.get("DOI", ""),
        "arxiv_id": ext.get("ArXiv", ""),
        "pmid": ext.get("PubMed", ""),
        "title": paper.get("title", ""),
        "abstract": paper.get("abstract") or "",
        "year": paper.get("year"),
        "venue": paper.get("venue", ""),
        "citation_count": paper.get("citationCount", 0),
        "fields_of_study": paper.get("fieldsOfStudy") or [],
        "publication_types": paper.get("publicationTypes") or [],
        "open_access_pdf": oa_pdf.get("url", ""),
        "date": paper.get("publicationDate", ""),
        "authors": authors_str,
        "source": "semantic_scholar",
    }


# ---------------------------------------------------------------------------
# 4. arXiv (arXiv API)
# ---------------------------------------------------------------------------

def search_arxiv(config, keys):
    """Search arXiv via the arXiv API with multiple sub-queries."""
    log("arXiv: Starting search...")
    arxiv_config = config["databases"]["arxiv"]
    cat_filter = arxiv_config.get("category_filter", "")
    date_filter = arxiv_config.get("date_filter", "")

    all_records = {}  # keyed by arxiv_id

    for query_name, query_text in arxiv_config["queries"].items():
        full_query = query_text
        if cat_filter:
            full_query = f"({full_query}) AND ({cat_filter})"

        log(f"  arXiv query '{query_name}': searching...")
        encoded_query = full_query

        records_in_query = 0
        start = 0
        max_results = 500

        while True:
            params = {
                "search_query": encoded_query,
                "start": start,
                "max_results": max_results,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }

            r = retry_request("https://export.arxiv.org/api/query", params=params)
            if r is None:
                log(f"    arXiv request failed after retries for '{query_name}'. Skipping batch.")
                break
            root = ET.fromstring(r.content)

            ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
            entries = root.findall("atom:entry", ns)

            if not entries:
                break

            new_in_batch = 0
            for entry in entries:
                rec = _parse_arxiv_entry(entry, ns, query_name)
                if rec:
                    aid = rec["arxiv_id"]
                    # Apply date filter
                    if date_filter and rec.get("date"):
                        pub_date = rec["date"].replace("-", "")[:8]
                        date_from = "20180101"
                        date_to = "20260228"
                        if pub_date < date_from or pub_date > date_to:
                            continue
                    if aid not in all_records:
                        all_records[aid] = rec
                        new_in_batch += 1
                        records_in_query += 1

            start += max_results
            if len(entries) < max_results:
                break

            time.sleep(3.0)

        log(f"    '{query_name}': {records_in_query} new records")

    records = list(all_records.values())
    log(f"  arXiv: {len(records)} total unique records")

    return {
        "database": "arXiv",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "queries": arxiv_config["queries"],
        "filters": f"categories: {cat_filter}, date: {date_filter}",
        "total_unique_results": len(records),
        "records": records,
    }


def _parse_arxiv_entry(entry, ns, query_name):
    """Parse a single arXiv Atom entry."""
    id_url = entry.findtext("atom:id", "", ns)
    if not id_url:
        return None
    # Extract arxiv ID from URL: http://arxiv.org/abs/2301.12345v1
    arxiv_id = id_url.split("/abs/")[-1] if "/abs/" in id_url else id_url

    title = entry.findtext("atom:title", "", ns).replace("\n", " ").strip()
    abstract = entry.findtext("atom:summary", "", ns).replace("\n", " ").strip()
    published = entry.findtext("atom:published", "", ns)[:10]

    authors = []
    for author in entry.findall("atom:author", ns):
        name = author.findtext("atom:name", "", ns)
        if name:
            authors.append(name)

    categories = []
    for cat in entry.findall("atom:category", ns):
        term = cat.get("term", "")
        if term:
            categories.append(term)

    # DOI
    doi = ""
    for link in entry.findall("atom:link", ns):
        if link.get("title") == "doi":
            doi = link.get("href", "")

    return {
        "arxiv_id": arxiv_id,
        "doi": doi,
        "title": title,
        "abstract": abstract,
        "authors": "; ".join(authors),
        "date": published,
        "year": published[:4] if published else "",
        "categories": categories,
        "source": "arxiv",
        "found_by_query": query_name,
    }


# ---------------------------------------------------------------------------
# 5. bioRxiv / medRxiv (via EuropePMC)
# ---------------------------------------------------------------------------

def search_biorxiv(config, keys):
    """Search bioRxiv/medRxiv preprints via EuropePMC REST API."""
    log("bioRxiv/medRxiv (EuropePMC): Starting search...")
    query = config["databases"]["biorxiv_medrxiv"]["query"]

    records = []
    cursor = "*"
    page = 0

    while True:
        params = {
            "query": query,
            "resultType": "core",
            "pageSize": 1000,
            "format": "json",
            "cursorMark": cursor,
        }

        r = retry_request("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params=params)
        data = r.json()

        results = data.get("resultList", {}).get("result", [])
        if not results:
            break

        for item in results:
            rec = _parse_europepmc_result(item)
            if rec:
                records.append(rec)

        next_cursor = data.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        page += 1

        hit_count = data.get("hitCount", "?")
        log(f"  Fetched {len(records)} of {hit_count}...")
        time.sleep(0.3)

    log(f"  bioRxiv/medRxiv: {len(records)} records retrieved")

    return {
        "database": "EuropePMC (bioRxiv/medRxiv preprints)",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "query": query,
        "filters": "SRC:PPR, FIRST_PDATE:[2018-01-01 TO 2026-02-28]",
        "total_results": len(records),
        "records_fetched": len(records),
        "records": records,
    }


def _parse_europepmc_result(item):
    """Parse a single EuropePMC result."""
    return {
        "epmc_id": item.get("id", ""),
        "doi": item.get("doi", ""),
        "pmid": item.get("pmid", ""),
        "title": item.get("title", ""),
        "abstract": item.get("abstractText") or "",
        "authors": item.get("authorString", ""),
        "journal": item.get("journalTitle", ""),
        "date": item.get("firstPublicationDate", ""),
        "year": item.get("pubYear", ""),
        "source_db": item.get("source", ""),
        "source": "europepmc_preprints",
    }


# ---------------------------------------------------------------------------
# 6. SpringerNature (Meta API + OA API)
# ---------------------------------------------------------------------------

def search_springernature(config, keys):
    """Search SpringerNature via Meta API v2 and Open Access API."""
    log("SpringerNature: Starting search...")
    sn_config = config["databases"]["springernature"]
    query = sn_config["query"]
    date_filter = sn_config["date_filter"]
    validation = sn_config["validation_patterns"]

    meta_key = keys.get("springernature_Meta_API", "")
    oa_key = keys.get("springernature_Open_Access_API", "")

    all_records = {}  # keyed by DOI

    # Search Meta API
    if meta_key:
        log("  SpringerNature Meta API: searching...")
        meta_records = _sn_paginated_search(
            "https://api.springernature.com/meta/v2/json",
            meta_key, query, date_filter,
        )
        for rec in meta_records:
            doi = rec.get("doi", "")
            if doi:
                all_records[doi] = rec
        log(f"  Meta API: {len(meta_records)} records retrieved")
    else:
        log("  WARNING: No SpringerNature Meta API key. Skipping Meta API.")

    # Search OA API
    if oa_key:
        log("  SpringerNature OA API: searching...")
        oa_records = _sn_paginated_search(
            "https://api.springernature.com/openaccess/json",
            oa_key, query, date_filter,
        )
        new_oa = 0
        for rec in oa_records:
            doi = rec.get("doi", "")
            if doi and doi not in all_records:
                all_records[doi] = rec
                new_oa += 1
        log(f"  OA API: {len(oa_records)} records ({new_oa} new after dedup)")
    else:
        log("  WARNING: No SpringerNature OA API key. Skipping OA API.")

    raw_count = len(all_records)
    raw_records = list(all_records.values())

    # Post-retrieval title/abstract validation
    block_a = re.compile(validation["block_a"], re.IGNORECASE)
    block_b = re.compile(validation["block_b"], re.IGNORECASE)
    block_c = re.compile(validation["block_c"], re.IGNORECASE)

    filtered = []
    for rec in raw_records:
        abstract = rec.get("abstract", "")
        if isinstance(abstract, dict):
            abstract = str(abstract)
        text = f"{rec.get('title', '')} {abstract}"
        if block_a.search(text) and block_b.search(text) and block_c.search(text):
            filtered.append(rec)

    log(f"  SpringerNature: {raw_count} raw -> {len(filtered)} after title/abstract validation")

    return {
        "database": "SpringerNature",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "query": query,
        "date_filter": date_filter,
        "filters": f"{date_filter}, post-retrieval validation (3 concept blocks in title/abstract)",
        "total_raw": raw_count,
        "total_validated": len(filtered),
        "records_fetched": len(filtered),
        "records": filtered,
        "raw_records_file": "springernature_raw",
    }, raw_records


def _sn_paginated_search(base_url, api_key, query, date_filter, max_pages=500):
    """Paginated search against SpringerNature API. Returns list of parsed records."""
    records = []
    start = 1
    page_size = 25
    total = None

    for page_num in range(max_pages):
        full_query = f"{query} {date_filter}"
        encoded_q = urllib.parse.quote(full_query)

        url = f"{base_url}?q={encoded_q}&api_key={api_key}&s={start}&p={page_size}"
        try:
            r = retry_request(url)
            if r is None:
                log(f"    SN request failed after retries at page {page_num}. Stopping.")
                break
            data = r.json()
        except Exception as e:
            log(f"    SN error at page {page_num}: {e}")
            break

        # Check for rate limit / errors
        if "result" not in data and "records" not in data:
            error_msg = str(data)[:200]
            if "exceeded" in error_msg.lower() or "rate" in error_msg.lower():
                log(f"    Rate limited at page {page_num}. Stopping.")
                break
            if "premium" in error_msg.lower():
                log(f"    Premium feature error: {error_msg}")
                break
            log(f"    Unexpected response: {error_msg}")
            break

        if total is None:
            try:
                total = int(data["result"][0]["total"])
                log(f"    Total in API: {total}")
            except (KeyError, IndexError):
                total = 0

        recs = data.get("records", [])
        if not recs:
            break

        for rec in recs:
            parsed = _parse_sn_record(rec)
            if parsed:
                records.append(parsed)

        start += page_size
        if start > total:
            break

        if page_num % 50 == 49:
            log(f"    Retrieved {len(records)} of {total}...")

        time.sleep(0.5)

    return records


def _parse_sn_record(rec):
    """Parse a single SpringerNature record."""
    doi = rec.get("doi", "")
    if not doi:
        identifier = rec.get("identifier", "")
        if identifier.startswith("doi:"):
            doi = identifier[4:]

    authors = rec.get("creators", [])
    if isinstance(authors, list):
        author_names = [a.get("creator", "") for a in authors if isinstance(a, dict)]
    else:
        author_names = []

    abstract = rec.get("abstract", "")
    if isinstance(abstract, dict):
        abstract = str(abstract)

    return {
        "source": "springernature",
        "title": rec.get("title", ""),
        "doi": doi,
        "url": (rec.get("url", [{}])[0].get("value", "") if isinstance(rec.get("url"), list) else ""),
        "authors": author_names,
        "publicationDate": rec.get("publicationDate", ""),
        "publicationName": rec.get("publicationName", ""),
        "contentType": rec.get("contentType", ""),
        "abstract": abstract,
        "openaccess": rec.get("openaccess", ""),
    }


# ---------------------------------------------------------------------------
# 7. Google Scholar (scholarly library)
# ---------------------------------------------------------------------------

GS_QUERY_TIMEOUT = 120  # seconds max per query before assuming rate-limited


def _gs_run_query(scholarly_mod, query_text, year_low, year_high, max_results, results_list):
    """Run a single GS query in a thread. Appends results to results_list."""
    try:
        search_results = scholarly_mod.search_pubs(query_text, year_low=year_low, year_high=year_high)
        count = 0
        for result in search_results:
            if count >= max_results:
                break
            results_list.append(result)
            count += 1
    except Exception as e:
        results_list.append(e)


def search_google_scholar(config, keys):
    """Search Google Scholar via scholarly Python library."""
    import threading

    log("Google Scholar: Starting search...")
    try:
        from scholarly import scholarly
    except ImportError:
        log("  WARNING: 'scholarly' library not installed. pip install scholarly")
        return None

    gs_config = config["databases"]["google_scholar"]
    queries = gs_config["queries"]
    max_per_query = gs_config.get("max_per_query", 200)
    year_low, year_high = gs_config.get("year_range", [2018, 2026])

    all_records = []
    seen_titles = set()
    rate_limited = False

    for i, query_text in enumerate(queries):
        if rate_limited:
            log(f"  GS query {i+1}/{len(queries)}: SKIPPED (rate-limited)")
            continue

        query_id = f"gs_q{i+1}"
        log(f"  GS query {i+1}/{len(queries)}: '{query_text[:60]}...'")

        raw_results = []
        t = threading.Thread(
            target=_gs_run_query,
            args=(scholarly, query_text, year_low, year_high, max_per_query, raw_results),
            daemon=True,
        )
        t.start()
        t.join(timeout=GS_QUERY_TIMEOUT)

        if t.is_alive():
            log(f"    Timeout after {GS_QUERY_TIMEOUT}s — Google Scholar is rate-limiting.")
            log(f"    Collected {len(raw_results)} results before timeout.")
            rate_limited = True
            # Process whatever results we got before the timeout
        else:
            # Check if the last item is an exception
            if raw_results and isinstance(raw_results[-1], Exception):
                e = raw_results.pop()
                log(f"    ERROR in GS query {i+1}: {e}")
                rate_limited = True

        count = 0
        for result in raw_results:
            if isinstance(result, Exception):
                continue
            bib = result.get("bib", {})
            title = bib.get("title", "")
            title_lower = title.lower().strip()
            if title_lower in seen_titles:
                continue
            seen_titles.add(title_lower)

            rec = {
                "source": "google_scholar",
                "query_id": query_id,
                "title": title,
                "authors": bib.get("author", []),
                "year": bib.get("pub_year", ""),
                "abstract": bib.get("abstract", ""),
                "venue": bib.get("venue", ""),
                "url": result.get("pub_url", result.get("eprint_url", "")),
                "num_citations": result.get("num_citations", 0),
                "citedby_url": result.get("citedby_url", ""),
            }
            all_records.append(rec)
            count += 1

        log(f"    Retrieved {count} records")

        time.sleep(5.0)

    log(f"  Google Scholar: {len(all_records)} total unique records")

    return all_records  # Returns list directly (same format as original export)


# ---------------------------------------------------------------------------
# Ground Truth Validation
# ---------------------------------------------------------------------------

def validate_ground_truth(all_results, ground_truth):
    """Check if ground truth models appear in search results."""
    log("\n--- Ground Truth Validation ---")

    must_find = ground_truth.get("must_find", [])
    related = ground_truth.get("related_excluded", [])

    db_names = list(all_results.keys())
    header = "| Model | " + " | ".join(db_names) + " | Total |"
    sep = "|---|" + "|".join(["---"] * len(db_names)) + "|---|"
    log(header)
    log(sep)

    all_models = must_find + related

    for model in all_models:
        counts = []
        total = 0
        pattern = re.compile(re.escape(model), re.IGNORECASE)

        for db_name in db_names:
            records = all_results[db_name]
            hits = sum(1 for r in records if pattern.search(r.get("title", "")))
            counts.append(str(hits))
            total += hits

        marker = "" if model in must_find else " (excl)"
        log(f"| {model}{marker} | " + " | ".join(counts) + f" | {total} |")

    # Summary
    found = []
    missing = []
    for model in must_find:
        pattern = re.compile(re.escape(model), re.IGNORECASE)
        total_hits = 0
        for db_name in db_names:
            records = all_results[db_name]
            total_hits += sum(1 for r in records if pattern.search(r.get("title", "")))
        if total_hits > 0:
            found.append(model)
        else:
            missing.append(model)

    log(f"\nMust-find: {len(found)}/{len(must_find)} found")
    if missing:
        log(f"MISSING: {', '.join(missing)}")
    else:
        log("All must-find models found!")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Reproducible systematic review search across 7 databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reproduce_search.py --keys api_keys.json
  python reproduce_search.py --keys api_keys.json --databases pubmed,arxiv
  python reproduce_search.py --keys api_keys.json --output-dir my_results/
        """,
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Path to search_config.json")
    parser.add_argument("--keys", required=True, help="Path to api_keys.json with your API keys")
    parser.add_argument("--output-dir", default="output", help="Directory for output files (default: output/)")
    parser.add_argument(
        "--databases",
        default=None,
        help="Comma-separated list of databases to search (default: all enabled). "
             "Options: pubmed,scopus,semantic_scholar,arxiv,biorxiv_medrxiv,springernature,google_scholar",
    )
    parser.add_argument(
        "--gs-fallback",
        default=None,
        help="Path to a cached Google Scholar JSON file. If GS is rate-limited and returns "
             "fewer results than this file, the cached results are used instead. "
             "Google Scholar has no official API and aggressively rate-limits scraping, "
             "so providing a fallback ensures reproducibility.",
    )
    args = parser.parse_args()

    # Load config
    with open(args.config, "r") as f:
        config = json.load(f)

    # Load API keys
    with open(args.keys, "r") as f:
        keys = json.load(f)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Determine which databases to search
    selected = None
    if args.databases:
        selected = [d.strip() for d in args.databases.split(",")]

    log(f"Review: {config['metadata']['review_title']}")
    log(f"Date range: {config['metadata']['date_from']} to {config['metadata']['date_to']}")
    log(f"Output directory: {args.output_dir}")
    log("")

    # Run searches
    all_results = {}
    summary = {}

    db_functions = {
        "pubmed": search_pubmed,
        "scopus": search_scopus,
        "semantic_scholar": search_semantic_scholar,
        "arxiv": search_arxiv,
        "biorxiv_medrxiv": search_biorxiv,
        "springernature": search_springernature,
        "google_scholar": search_google_scholar,
    }

    for db_name, search_func in db_functions.items():
        db_config = config["databases"].get(db_name, {})
        if not db_config.get("enabled", False):
            continue
        if selected and db_name not in selected:
            continue

        log(f"\n{'='*60}")
        try:
            if db_name == "springernature":
                result, raw_records = search_func(config, keys)
                # Save raw records too
                today = datetime.now().strftime("%Y-%m-%d")
                raw_path = os.path.join(args.output_dir, f"springernature_raw_{today}.json")
                with open(raw_path, "w", encoding="utf-8") as f:
                    json.dump(raw_records, f, ensure_ascii=False, indent=2)
                log(f"  Saved raw records: {raw_path}")
            elif db_name == "google_scholar":
                result = search_func(config, keys)
            else:
                result = search_func(config, keys)

            if result is None:
                log(f"  {db_name}: Skipped (missing API key or error)")
                continue

            # Save results
            if db_name == "google_scholar":
                # GS returns a plain list
                # Check if we should use the fallback (cached) results
                if args.gs_fallback and os.path.exists(args.gs_fallback):
                    with open(args.gs_fallback, "r", encoding="utf-8") as ff:
                        fallback_data = json.load(ff)
                    if len(result) < len(fallback_data):
                        log(f"  GS live search returned {len(result)} records, "
                            f"fallback has {len(fallback_data)} records.")
                        log(f"  Using fallback results from {args.gs_fallback}")
                        result = fallback_data

                today = datetime.now().strftime("%Y-%m-%d")
                filepath = os.path.join(args.output_dir, f"google_scholar_{today}.json")
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                log(f"  Saved {filepath}")
                all_results[db_name] = result
                summary[db_name] = len(result)
            else:
                save_results(args.output_dir, db_name, result)
                all_results[db_name] = result.get("records", [])
                summary[db_name] = result.get("records_fetched", len(result.get("records", [])))

        except Exception as e:
            log(f"  ERROR in {db_name}: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    log(f"\n{'='*60}")
    log("SEARCH SUMMARY")
    log(f"{'='*60}")
    total = 0
    for db_name, count in summary.items():
        log(f"  {db_name:25s}: {count:>6d} records")
        total += count
    log(f"  {'TOTAL (before dedup)':25s}: {total:>6d} records")

    # Ground truth validation
    if all_results and config.get("ground_truth"):
        validate_ground_truth(all_results, config["ground_truth"])

    # Save summary
    today = datetime.now().strftime("%Y-%m-%d")
    summary_path = os.path.join(args.output_dir, f"search_summary_{today}.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "search_date": today,
            "config_file": args.config,
            "date_range": f"{config['metadata']['date_from']} to {config['metadata']['date_to']}",
            "results_per_database": summary,
            "total_before_dedup": total,
        }, f, ensure_ascii=False, indent=2)
    log(f"\nSummary saved: {summary_path}")
    log("Done.")


if __name__ == "__main__":
    main()
