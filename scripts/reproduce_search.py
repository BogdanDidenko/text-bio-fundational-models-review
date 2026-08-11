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
import hashlib
import json
import os
import queue as queue_module
import re
import sys
import tempfile
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, date
from pathlib import Path

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
    last_error = None
    for attempt in range(max_retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=60)
            if r.status_code == 429:
                last_error = RuntimeError(
                    f"HTTP 429 rate limit after {attempt + 1}/{max_retries} attempts"
                )
                if attempt < max_retries - 1:
                    wait = delay * (2 ** attempt)
                    log(f"  Rate limited (429). Waiting {wait:.0f}s...")
                    time.sleep(wait)
                continue
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = delay * (2 ** attempt)
                log(f"  Request error: {e}. Retrying in {wait:.0f}s...")
                time.sleep(wait)
            else:
                raise
    raise last_error or RuntimeError("request failed without a response")


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


def date_after_cutoff(date_str, cutoff):
    """Check if a date string is >= cutoff. Handles YYYY-MM-DD, YYYY-MM, YYYY."""
    if not date_str or not cutoff:
        return True
    try:
        if len(date_str) == 4:
            return int(date_str) >= int(cutoff[:4])
        if len(date_str) == 7:
            return date_str >= cutoff[:7]
        return date_str[:10] >= cutoff
    except (ValueError, TypeError):
        return True


def classify_interval_date(date_value, date_from, date_to):
    """Classify a source date without pretending coarse dates are day-precise."""
    value = str(date_value or "").strip()
    if not value:
        return "unknown_missing"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value[:10]):
        day = value[:10]
        return "in_range" if date_from <= day <= date_to else "out_of_range"
    if re.fullmatch(r"\d{4}-\d{2}", value):
        month_from = date_from[:7]
        month_to = date_to[:7]
        return "in_range" if month_from <= value <= month_to else "out_of_range"
    if re.fullmatch(r"\d{4}", value):
        if date_from[:4] == date_to[:4] == value and (
            date_from[5:] != "01-01" or date_to[5:] != "12-31"
        ):
            return "unknown_year_only"
        return "in_range" if date_from[:4] <= value <= date_to[:4] else "out_of_range"
    return "unknown_unparseable"


def filter_interval_records(records, date_from, date_to):
    """Keep exact hits plus uncertain-date candidates, while making both visible."""
    kept = []
    excluded = []
    counts = {}
    for record in records:
        status = classify_interval_date(record.get("date"), date_from, date_to)
        counts[status] = counts.get(status, 0) + 1
        annotated = dict(record)
        annotated["search_date_status"] = status
        if status == "out_of_range":
            excluded.append(annotated)
        else:
            kept.append(annotated)
    return kept, excluded, {
        "date_from": date_from,
        "date_to": date_to,
        "policy": "include uncertain dates for recall; expose status; exclude confirmed out-of-range",
        "counts": counts,
        "excluded_out_of_range": len(excluded),
    }


def complete_execution(**extra):
    return {"status": "complete", "complete": True, **extra}


def incomplete_execution(reason, **extra):
    return {"status": "incomplete", "complete": False, "reason": reason, **extra}


def query_signature(queries, year_range, date_from="", date_to="", acquisition=None):
    payload = json.dumps(
        {
            "queries": queries,
            "year_range": year_range,
            "date_from": date_from,
            "date_to": date_to,
            "acquisition": acquisition or {},
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sha256_json(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def atomic_write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def retry_after_seconds(response):
    value = (response.headers.get("Retry-After") or "").strip()
    if value.isdigit():
        return int(value)
    return None


class SemanticScholarRateLimitError(RuntimeError):
    pass


class SemanticScholarRequestController:
    """Single-process 1 RPS controller with a non-secret request audit."""

    minimum_request_spacing_seconds = 1.1
    fallback_backoff_seconds = (60, 120, 240, 480, 900)

    def __init__(self, headers):
        self.headers = headers
        self.last_started = None
        self.events = []

    def request(self, params, request_context):
        for attempt, fallback_wait in enumerate(self.fallback_backoff_seconds, start=1):
            if self.last_started is not None:
                remaining = self.minimum_request_spacing_seconds - (time.monotonic() - self.last_started)
                if remaining > 0:
                    time.sleep(remaining)
            started = datetime.now().isoformat()
            self.last_started = time.monotonic()
            try:
                response = requests.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search/bulk",
                    params=params,
                    headers=self.headers,
                    timeout=60,
                )
            except requests.RequestException as exc:
                self.events.append(
                    {
                        **request_context,
                        "attempt": attempt,
                        "started": started,
                        "status_code": None,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
                raise
            event = {
                **request_context,
                "attempt": attempt,
                "started": started,
                "status_code": response.status_code,
                "retry_after_seconds": retry_after_seconds(response),
                "response_sha256": hashlib.sha256(response.content).hexdigest(),
            }
            self.events.append(event)
            if response.status_code != 429:
                response.raise_for_status()
                return response
            wait = event["retry_after_seconds"]
            wait = wait if wait is not None else fallback_wait
            event["scheduled_wait_seconds"] = wait
            if attempt < len(self.fallback_backoff_seconds):
                log(f"    S2 rate limited; retrying after {wait}s (attempt {attempt}).")
                time.sleep(wait)
        raise SemanticScholarRateLimitError(
            "Semantic Scholar rate limit persisted after five paced attempts"
        )


def save_results(output_dir, db_name, data, file_date=None):
    """Save results to JSON file."""
    file_date = file_date or datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(output_dir, f"{db_name}_{file_date}.json")
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

    # PubMed can return transient 500s for long Boolean queries sent as GET URLs.
    # POST keeps the query body identical while avoiding URL-length/proxy issues.
    for attempt in range(5):
        try:
            r = requests.post(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                data=params,
                timeout=60,
            )
            r.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            if attempt == 4:
                raise
            wait = 2 * (2 ** attempt)
            log(f"  PubMed ESearch error: {e}. Retrying in {wait:.0f}s...")
            time.sleep(wait)
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
    execution = (
        complete_execution(expected_records=count, fetched_records=len(records))
        if len(records) == count
        else incomplete_execution(
            "PubMed EFetch count does not match ESearch count",
            expected_records=count,
            fetched_records=len(records),
        )
    )
    return {
        "database": "PubMed",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "query": query,
        "filters": config["databases"]["pubmed"].get("notes", query),
        "total_results": count,
        "records_fetched": len(records),
        "records": records,
        "execution": execution,
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
    day = pub_date.findtext("Day", "") if pub_date is not None else ""
    month_lookup = {
        name: f"{index:02d}"
        for index, name in enumerate(
            ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
            start=1,
        )
    }
    normalized_month = month_lookup.get(month[:3].title(), month.zfill(2) if month.isdigit() else "")
    publication_date = year
    if year and normalized_month:
        publication_date = f"{year}-{normalized_month}"
        if day.isdigit():
            publication_date += f"-{int(day):02d}"

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
        "date": publication_date,
        "journal": journal,
        "source": "pubmed",
        "search_date_status": "in_range_database_filter",
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
        return {
            "database": "Scopus",
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "query": config["databases"]["scopus"]["query"],
            "records_fetched": 0,
            "records": [],
            "execution": incomplete_execution("Scopus API key missing"),
        }

    query = config["databases"]["scopus"]["query"]
    date_post_filter = config["databases"]["scopus"].get("date_post_filter", DATE_CUTOFF)

    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": api_key,
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

    # Post-filter by date. Coarse or absent source dates remain recall candidates,
    # but they are explicitly labelled instead of silently treated as exact hits.
    pre_filter_count = len(records)
    date_from_filter = config["databases"]["scopus"].get("date_from_post_filter", "")
    records, out_of_range, date_audit = filter_interval_records(
        records, date_from_filter, date_post_filter
    )
    log(f"  Scopus: {pre_filter_count} retrieved, {len(records)} after date filter"
        f" ({date_from_filter or '...'} to {date_post_filter})")

    return {
        "database": "Scopus",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "query": query,
        "filters": (
            f"{config['databases']['scopus'].get('notes', query)}; exact post-filter "
            f"{date_from_filter or 'unbounded'} to {date_post_filter}"
        ),
        "total_results": total,
        "records_before_date_filter": pre_filter_count,
        "records_fetched": len(records),
        "records": records,
        "out_of_range_records": out_of_range,
        "date_filter_audit": date_audit,
        "execution": (
            complete_execution(expected_records=total, fetched_before_filter=pre_filter_count)
            if total == pre_filter_count
            else incomplete_execution(
                "Scopus pagination ended before all reported results were fetched",
                expected_records=total,
                fetched_before_filter=pre_filter_count,
            )
        ),
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
# 3. OpenAlex (Works Search API)
# ---------------------------------------------------------------------------

def _openalex_abstract(inverted_index):
    """Reconstruct display text from OpenAlex's abstract inverted index."""
    if not isinstance(inverted_index, dict) or not inverted_index:
        return ""
    positioned = []
    for token, positions in inverted_index.items():
        for position in positions or []:
            if isinstance(position, int):
                positioned.append((position, token))
    return " ".join(token for _, token in sorted(positioned))


def _openalex_external_id(value, prefix):
    text = str(value or "").strip()
    if not text:
        return ""
    lowered = text.lower()
    marker = prefix.lower()
    if marker in lowered:
        return text[lowered.rfind(marker) + len(marker):].strip("/")
    return text.strip("/")


def _parse_openalex_work(work, query_ids):
    ids = work.get("ids") or {}
    primary_location = work.get("primary_location") or {}
    best_oa = work.get("best_oa_location") or {}
    source = primary_location.get("source") or {}
    authors = []
    for authorship in work.get("authorships") or []:
        name = ((authorship.get("author") or {}).get("display_name") or "").strip()
        if name:
            authors.append(name)
    doi = work.get("doi") or ids.get("doi") or ""
    return {
        "openalex_id": str(work.get("id") or "").rsplit("/", 1)[-1],
        "doi": _openalex_external_id(doi, "doi.org/"),
        "pmid": _openalex_external_id(ids.get("pmid"), "pubmed.ncbi.nlm.nih.gov/"),
        "title": work.get("display_name") or work.get("title") or "",
        "abstract": _openalex_abstract(work.get("abstract_inverted_index")),
        "authors": authors,
        "year": work.get("publication_year") or "",
        "date": work.get("publication_date") or "",
        "journal": source.get("display_name") or "",
        "url": (
            best_oa.get("pdf_url")
            or best_oa.get("landing_page_url")
            or primary_location.get("landing_page_url")
            or work.get("doi")
            or work.get("id")
            or ""
        ),
        "type": work.get("type") or "",
        "is_oa": bool((work.get("open_access") or {}).get("is_oa")),
        "found_by_query": ",".join(sorted(query_ids)),
        "query_ids": sorted(query_ids),
        "source": "openalex",
        "search_date_status": "in_range_database_filter",
    }


def _openalex_request(params, api_key, max_retries=5):
    """Request one OpenAlex page without exposing the API key in errors or logs."""
    request_params = dict(params)
    request_params["api_key"] = api_key
    last_status = None
    for attempt in range(max_retries):
        try:
            response = requests.get(
                "https://api.openalex.org/works",
                params=request_params,
                timeout=60,
            )
        except requests.RequestException as exc:
            raise RuntimeError(
                f"OpenAlex network failure ({type(exc).__name__}); request URL suppressed"
            ) from None
        last_status = response.status_code
        if response.status_code == 429 and attempt < max_retries - 1:
            wait = retry_after_seconds(response) or 2 ** attempt
            log(f"  OpenAlex rate limited; retrying after {wait}s")
            time.sleep(wait)
            continue
        if response.status_code >= 400:
            try:
                payload = response.json()
                detail = payload.get("message") or payload.get("error") or "request rejected"
            except (ValueError, AttributeError):
                detail = "request rejected"
            raise RuntimeError(
                f"OpenAlex HTTP {response.status_code}: {str(detail)[:300]}; request URL suppressed"
            )
        return response.json()
    raise RuntimeError(f"OpenAlex HTTP {last_status} after {max_retries} attempts")


def search_openalex(config, keys):
    """Search OpenAlex Works with exact date/OA/language filters and cursor paging."""
    log("OpenAlex: Starting search...")
    api_key = keys.get("openalex") or keys.get("OPENALEX_API_KEY") or ""
    source_config = config["databases"]["openalex"]
    if not api_key:
        return {
            "database": "OpenAlex",
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "queries": source_config.get("queries", {}),
            "records_fetched": 0,
            "records": [],
            "execution": incomplete_execution("OpenAlex API key missing"),
        }, {"database": "OpenAlex", "records": []}

    date_from = source_config["date_from"]
    date_to = source_config["date_to"]
    base_filters = (
        f"from_publication_date:{date_from},to_publication_date:{date_to},"
        "language:en,is_oa:true"
    )
    query_scopes = source_config.get("query_scopes") or {}
    by_id = {}
    membership = {}
    query_runs = {}

    for query_id, query in source_config["queries"].items():
        scope = query_scopes.get(query_id, "title_and_abstract")
        if scope not in {"title", "title_and_abstract", "fulltext"}:
            raise ValueError(f"Unsupported OpenAlex query scope for {query_id}: {scope}")
        query_filter = base_filters
        search_params = {}
        if scope == "fulltext":
            search_params["search"] = query
        else:
            search_field = "title.search" if scope == "title" else "title_and_abstract.search"
            query_filter += f",{search_field}:{query}"
        cursor = "*"
        fetched = 0
        expected = None
        pages = 0
        while cursor:
            payload = _openalex_request(
                {
                    **search_params,
                    "filter": query_filter,
                    "cursor": cursor,
                    "per-page": 100,
                },
                api_key,
            )
            pages += 1
            meta = payload.get("meta") or {}
            if expected is None:
                expected = int(meta.get("count") or 0)
                log(f"  OpenAlex query '{query_id}': {expected} results")
            results = payload.get("results") or []
            fetched += len(results)
            for work in results:
                work_id = str(work.get("id") or "")
                if not work_id:
                    continue
                by_id.setdefault(work_id, work)
                membership.setdefault(work_id, set()).add(query_id)
            next_cursor = meta.get("next_cursor")
            cursor = (
                next_cursor
                if results and next_cursor and fetched < (expected or 0)
                else None
            )
        query_runs[query_id] = {
            "expected_records": expected or 0,
            "fetched_records": fetched,
            "pages": pages,
            "scope": scope,
            "complete": fetched == (expected or 0),
        }

    records = [
        _parse_openalex_work(by_id[work_id], membership[work_id])
        for work_id in sorted(by_id)
    ]
    complete = all(run["complete"] for run in query_runs.values())
    raw = {
        "database": "OpenAlex",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "queries": source_config["queries"],
        "filters": base_filters,
        "query_scopes": query_scopes,
        "query_runs": query_runs,
        "query_membership": {
            work_id: sorted(query_ids) for work_id, query_ids in sorted(membership.items())
        },
        "records": [by_id[work_id] for work_id in sorted(by_id)],
    }
    result = {
        "database": "OpenAlex",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "queries": source_config["queries"],
        "filters": base_filters,
        "query_scopes": query_scopes,
        "query_runs": query_runs,
        "records_fetched": len(records),
        "records": records,
        "execution": (
            complete_execution(query_runs=query_runs)
            if complete
            else incomplete_execution("OpenAlex cursor pagination incomplete", query_runs=query_runs)
        ),
    }
    log(f"  OpenAlex: {len(records)} unique records retrieved")
    return result, raw


# ---------------------------------------------------------------------------
# 4. Semantic Scholar (Bulk Search API)
# ---------------------------------------------------------------------------

def _s2_identity(config, api_key):
    source = config["databases"]["semantic_scholar"]
    payload = {
        "endpoint": "https://api.semanticscholar.org/graph/v1/paper/search/bulk",
        "queries": source["queries"],
        "fields": source["fields"],
        "year_range": source["year_range"],
        "date_from_post_filter": source.get("date_from_post_filter", ""),
        "date_post_filter": source.get("date_post_filter", DATE_CUTOFF),
    }
    return {
        "config_sha256": sha256_json(payload),
        "key_fingerprint": hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16] if api_key else "unauthenticated",
        **payload,
    }


def _load_s2_checkpoint(state_dir, identity, query_names):
    state_path = state_dir / "checkpoint.json"
    if state_path.exists():
        checkpoint = json.loads(state_path.read_text(encoding="utf-8"))
        if checkpoint.get("identity") != identity:
            raise RuntimeError(
                "Semantic Scholar checkpoint identity differs from the requested search; "
                "start a new state directory rather than mixing query lineages"
            )
        return checkpoint
    checkpoint = {
        "schema_version": 1,
        "identity": identity,
        "created": datetime.now().isoformat(),
        "queries": {
            name: {"completed": False, "next_token": None, "pages": []}
            for name in query_names
        },
        "request_events": [],
    }
    atomic_write_json(state_path, checkpoint)
    return checkpoint


def _s2_add_paper(all_records, paper, query_name):
    paper_id = paper.get("paperId") or ""
    if not paper_id:
        raise RuntimeError("Semantic Scholar response contains a paper without paperId")
    if paper_id not in all_records:
        parsed = _parse_s2_paper(paper)
        parsed["found_by_queries"] = [query_name]
        all_records[paper_id] = parsed
        return True
    memberships = all_records[paper_id].setdefault("found_by_queries", [])
    if query_name not in memberships:
        memberships.append(query_name)
    return False


def _s2_restore_records(state_dir, checkpoint):
    all_records = {}
    for query_name, state in checkpoint["queries"].items():
        for page in state.get("pages", []):
            raw_path = state_dir / page["raw_file"]
            if not raw_path.is_file():
                raise RuntimeError(f"Semantic Scholar checkpoint references missing raw page: {raw_path}")
            payload = json.loads(raw_path.read_text(encoding="utf-8"))
            for paper in payload.get("response", {}).get("data", []):
                _s2_add_paper(all_records, paper, query_name)
    return all_records


def search_semantic_scholar(config, keys, state_dir=None):
    """Resumable, paced Semantic Scholar bulk search with page-level evidence."""
    log("Semantic Scholar: Starting search...")
    api_key = keys.get("semantic_scholar", "") or keys.get("S2_API_KEY", "")
    s2_config = config["databases"]["semantic_scholar"]
    fields = s2_config["fields"]
    year_range = s2_config["year_range"]
    date_post_filter = s2_config.get("date_post_filter", DATE_CUTOFF)
    state_dir = Path(state_dir or "semantic_scholar_state")
    identity = _s2_identity(config, api_key)
    checkpoint = _load_s2_checkpoint(state_dir, identity, s2_config["queries"])
    state_path = state_dir / "checkpoint.json"

    headers = {"x-api-key": api_key} if api_key else {}
    controller = SemanticScholarRequestController(headers)
    all_records = _s2_restore_records(state_dir, checkpoint)

    try:
        for query_name, query_text in s2_config["queries"].items():
            state = checkpoint["queries"][query_name]
            if state.get("completed"):
                continue
            log(f"  S2 query '{query_name}': searching...")
            while not state.get("completed"):
                token = state.get("next_token")
                page_number = len(state.get("pages", []))
                params = {"query": query_text, "fields": fields, "year": year_range}
                if token:
                    params["token"] = token
                response = controller.request(
                    params,
                    {
                        "query_name": query_name,
                        "page_number": page_number,
                        "token_in_sha256": hashlib.sha256(str(token or "").encode()).hexdigest(),
                    },
                )
                try:
                    data = response.json()
                except ValueError as exc:
                    raise RuntimeError("Semantic Scholar returned non-JSON content") from exc
                raw_file = Path("raw") / query_name / f"page_{page_number:05d}.json"
                raw_payload = {
                    "query_name": query_name,
                    "page_number": page_number,
                    "token_in": token,
                    "token_out": data.get("token"),
                    "retrieved_at": datetime.now().isoformat(),
                    "response": data,
                }
                atomic_write_json(state_dir / raw_file, raw_payload)
                if not isinstance(data.get("data"), list):
                    raise RuntimeError("Semantic Scholar response does not contain a data list")
                page_added = sum(
                    _s2_add_paper(all_records, paper, query_name) for paper in data["data"]
                )
                state["pages"].append(
                    {
                        "raw_file": str(raw_file),
                        "raw_sha256": sha256_json(raw_payload),
                        "token_in_sha256": hashlib.sha256(str(token or "").encode()).hexdigest(),
                        "token_out_sha256": hashlib.sha256(str(data.get("token") or "").encode()).hexdigest(),
                        "records_received": len(data["data"]),
                        "unique_global_added": page_added,
                    }
                )
                state["next_token"] = data.get("token")
                state["completed"] = not bool(data.get("token"))
                checkpoint["request_events"].extend(controller.events)
                controller.events.clear()
                checkpoint["updated"] = datetime.now().isoformat()
                atomic_write_json(state_path, checkpoint)
            log(f"    '{query_name}': {len(state['pages'])} page(s) complete")
    except Exception:
        checkpoint["request_events"].extend(controller.events)
        checkpoint["updated"] = datetime.now().isoformat()
        atomic_write_json(state_path, checkpoint)
        raise

    records = list(all_records.values())
    query_execution = [
        {
            "query_name": query_name,
            "complete": state["completed"],
            "pages_completed": len(state["pages"]),
            "records_received": sum(page["records_received"] for page in state["pages"]),
        }
        for query_name, state in checkpoint["queries"].items()
    ]

    # Post-filter by date
    pre_filter_count = len(records)
    date_from_filter = s2_config.get("date_from_post_filter", "")
    records, out_of_range, date_audit = filter_interval_records(
        records, date_from_filter, date_post_filter
    )
    log(f"  S2: {pre_filter_count} total unique, {len(records)} after date filter"
        f" ({date_from_filter or '...'} to {date_post_filter})")

    return {
        "database": "Semantic Scholar (bulk)",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "query": s2_config["queries"].get("main", next(iter(s2_config["queries"].values()), "")),
        "queries": s2_config["queries"],
        "filters": (
            f"year={year_range}, exact post-filter "
            f"{date_from_filter or 'unbounded'} to {date_post_filter}"
        ),
        "total_results": pre_filter_count,
        "records_fetched": len(records),
        "records": records,
        "out_of_range_records": out_of_range,
        "date_filter_audit": date_audit,
        "query_execution": query_execution,
        "checkpoint": str(state_path),
        "execution": (
            complete_execution(query_count=len(query_execution))
            if len(query_execution) == len(s2_config["queries"])
            and all(row["complete"] for row in query_execution)
            else incomplete_execution(
                "one or more Semantic Scholar queries did not complete",
                query_execution=query_execution,
            )
        ),
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
    query_execution = []

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
                query_execution.append({
                    "query_name": query_name,
                    "complete": False,
                    "reason": "request failed after retries",
                    "new_records": records_in_query,
                })
                break
            root = ET.fromstring(r.content)

            ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
            entries = root.findall("atom:entry", ns)

            if not entries:
                query_execution.append({
                    "query_name": query_name,
                    "complete": True,
                    "new_records": records_in_query,
                })
                break

            # Parse date range from config date_filter string
            # Format: "submittedDate:[YYYYMMDD TO YYYYMMDD]"
            arxiv_date_from = ""
            arxiv_date_to = ""
            if date_filter:
                import re as _re
                m = _re.search(r'\[(\d{8})\s+TO\s+(\d{8})\]', date_filter)
                if m:
                    arxiv_date_from = m.group(1)
                    arxiv_date_to = m.group(2)

            new_in_batch = 0
            for entry in entries:
                rec = _parse_arxiv_entry(entry, ns, query_name)
                if rec:
                    aid = rec["arxiv_id"]
                    # Apply date filter
                    if arxiv_date_from and rec.get("date"):
                        pub_date = rec["date"].replace("-", "")[:8]
                        if pub_date < arxiv_date_from or pub_date > arxiv_date_to:
                            continue
                    if aid not in all_records:
                        all_records[aid] = rec
                        new_in_batch += 1
                        records_in_query += 1

            start += max_results
            if len(entries) < max_results:
                query_execution.append({
                    "query_name": query_name,
                    "complete": True,
                    "new_records": records_in_query,
                })
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
        "records_fetched": len(records),
        "records": records,
        "query_execution": query_execution,
        "execution": (
            complete_execution(query_count=len(query_execution))
            if len(query_execution) == len(arxiv_config["queries"])
            and all(row["complete"] for row in query_execution)
            else incomplete_execution(
                "one or more arXiv queries did not complete",
                query_execution=query_execution,
            )
        ),
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
        "search_date_status": "in_range_database_filter",
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
    expected = None

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
        if expected is None:
            expected = int(data.get("hitCount", 0))

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
    execution = (
        complete_execution(expected_records=expected, fetched_records=len(records), pages=page + 1)
        if expected == len(records)
        else incomplete_execution(
            "EuropePMC fetched count does not match hitCount",
            expected_records=expected,
            fetched_records=len(records),
            pages=page + 1,
        )
    )

    return {
        "database": "EuropePMC (bioRxiv/medRxiv preprints)",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "query": query,
        "filters": config["databases"]["biorxiv_medrxiv"].get("notes", query),
        "total_results": len(records),
        "records_fetched": len(records),
        "records": records,
        "execution": execution,
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
        "search_date_status": "in_range_database_filter",
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
    interface_execution = {}

    # Search Meta API
    if meta_key:
        log("  SpringerNature Meta API: searching...")
        meta_records, meta_execution = _sn_paginated_search(
            "https://api.springernature.com/meta/v2/json",
            meta_key, query, date_filter,
        )
        interface_execution["meta"] = meta_execution
        for rec in meta_records:
            doi = rec.get("doi", "")
            if doi:
                all_records[doi] = rec
        log(f"  Meta API: {len(meta_records)} records retrieved")
    else:
        log("  WARNING: No SpringerNature Meta API key. Skipping Meta API.")
        interface_execution["meta"] = incomplete_execution("Meta API key missing")

    # Search OA API
    if oa_key:
        log("  SpringerNature OA API: searching...")
        oa_records, oa_execution = _sn_paginated_search(
            "https://api.springernature.com/openaccess/json",
            oa_key, query, date_filter,
        )
        interface_execution["open_access"] = oa_execution
        new_oa = 0
        for rec in oa_records:
            doi = rec.get("doi", "")
            if doi and doi not in all_records:
                all_records[doi] = rec
                new_oa += 1
        log(f"  OA API: {len(oa_records)} records ({new_oa} new after dedup)")
    else:
        log("  WARNING: No SpringerNature OA API key. Skipping OA API.")
        interface_execution["open_access"] = incomplete_execution("Open Access API key missing")

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
        "interface_execution": interface_execution,
        "execution": (
            complete_execution(interfaces=interface_execution)
            if all(row["complete"] for row in interface_execution.values())
            else incomplete_execution(
                "both SpringerNature interfaces must complete",
                interfaces=interface_execution,
            )
        ),
    }, raw_records


def _sn_paginated_search(base_url, api_key, query, date_filter, max_pages=500):
    """Paginated SpringerNature search with an explicit completeness result."""
    records = []
    start = 1
    page_size = 25
    total = None
    failure_reason = ""
    ended_naturally = False

    for page_num in range(max_pages):
        full_query = f"{query} {date_filter}"
        encoded_q = urllib.parse.quote(full_query)

        url = f"{base_url}?q={encoded_q}&api_key={api_key}&s={start}&p={page_size}"
        try:
            r = retry_request(url)
            if r is None:
                log(f"    SN request failed after retries at page {page_num}. Stopping.")
                failure_reason = "request failed after retries"
                break
            data = r.json()
        except Exception as e:
            log(f"    SN error at page {page_num}: {e}")
            failure_reason = f"response error: {type(e).__name__}"
            break

        # Check for rate limit / errors
        if "result" not in data and "records" not in data:
            error_msg = str(data)[:200]
            if "exceeded" in error_msg.lower() or "rate" in error_msg.lower():
                log(f"    Rate limited at page {page_num}. Stopping.")
                failure_reason = "rate limited"
                break
            if "premium" in error_msg.lower():
                log(f"    Premium feature error: {error_msg}")
                failure_reason = "premium feature error"
                break
            log(f"    Unexpected response: {error_msg}")
            failure_reason = "unexpected response"
            break

        if total is None:
            try:
                total = int(data["result"][0]["total"])
                log(f"    Total in API: {total}")
            except (KeyError, IndexError):
                total = 0

        recs = data.get("records", [])
        if not recs:
            ended_naturally = True
            break

        for rec in recs:
            parsed = _parse_sn_record(rec)
            if parsed:
                records.append(parsed)

        start += page_size
        if start > total:
            ended_naturally = True
            break

        if page_num % 50 == 49:
            log(f"    Retrieved {len(records)} of {total}...")

        time.sleep(0.5)

    complete = not failure_reason and ended_naturally and total is not None and len(records) == total
    execution = (
        complete_execution(expected_records=total, fetched_records=len(records))
        if complete
        else incomplete_execution(
            failure_reason or "pagination stopped before the reported total",
            expected_records=total,
            fetched_records=len(records),
            max_pages=max_pages,
        )
    )
    return records, execution


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
        "search_date_status": "in_range_database_filter",
    }


# ---------------------------------------------------------------------------
# 7. Google Scholar (scholarly library)
# ---------------------------------------------------------------------------

GS_QUERY_TIMEOUT = 120  # seconds max per query before assuming rate-limited


def load_google_scholar_provider_export(config, export_path):
    """Validate a provider-mediated Scholar capture before it can enter dedup."""
    payload = json.loads(Path(export_path).read_text(encoding="utf-8"))
    bundle = payload.get("query_bundle") or {}
    gs_config = config["databases"]["google_scholar"]
    metadata = config["metadata"]
    expected_signature = query_signature(
        gs_config["queries"],
        gs_config["year_range"],
        metadata["date_from"],
        metadata["date_to"],
        bundle.get("acquisition"),
    )
    if bundle.get("queries") != gs_config["queries"]:
        raise RuntimeError("Google Scholar provider export has different query strings")
    if bundle.get("year_range") != gs_config["year_range"]:
        raise RuntimeError("Google Scholar provider export has a different year range")
    if bundle.get("date_from") != metadata["date_from"] or bundle.get("date_to") != metadata["date_to"]:
        raise RuntimeError("Google Scholar provider export has a different review interval")
    if payload.get("query_signature") != expected_signature:
        raise RuntimeError("Google Scholar provider export query signature does not match its bundle")
    raw_manifest = payload.get("raw_response_manifest") or []
    if not raw_manifest or not all(row.get("sha256") and row.get("artifact") for row in raw_manifest):
        raise RuntimeError("Google Scholar provider export lacks a hashed raw-response manifest")
    for row in raw_manifest:
        artifact_path = Path(export_path).parent / row["artifact"]
        if not artifact_path.is_file():
            raise RuntimeError(f"Google Scholar raw artifact is missing: {artifact_path}")
        digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        if digest != row["sha256"]:
            raise RuntimeError(f"Google Scholar raw artifact hash mismatch: {artifact_path}")
    expected_ids = [f"gs_q{index}" for index in range(1, len(gs_config["queries"]) + 1)]
    query_execution = payload.get("query_execution") or []
    by_id = {row.get("query_id"): row for row in query_execution}
    if set(by_id) != set(expected_ids):
        raise RuntimeError("Google Scholar provider export does not cover exactly the configured queries")
    if not all(row.get("execution_complete") and row.get("retrieval_complete") for row in by_id.values()):
        raise RuntimeError("Google Scholar provider export contains an incomplete query")
    records = payload.get("records")
    if not isinstance(records, list):
        raise RuntimeError("Google Scholar provider export records must be a list")
    normalized = []
    for row in records:
        membership = row.get("query_ids") or ([row["query_id"]] if row.get("query_id") else [])
        if not membership or not set(membership).issubset(set(expected_ids)):
            raise RuntimeError("Google Scholar record has invalid query membership")
        normalized.append(
            {
                **row,
                "source": "google_scholar",
                "query_id": membership[0],
                "query_ids": membership,
                "search_date_status": row.get("search_date_status", "unknown_year_only"),
            }
        )
    return {
        "database": "Google Scholar (provider-mediated)",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "queries": gs_config["queries"],
        "year_range": gs_config["year_range"],
        "query_signature": expected_signature,
        "date_precision": "year_only; supplementary discovery source",
        "provider_export": str(export_path),
        "raw_response_manifest": raw_manifest,
        "records_fetched": len(normalized),
        "records": normalized,
        "query_execution": query_execution,
        "execution": complete_execution(
            execution_complete=True,
            retrieval_complete=True,
            source_exhaustive="unknown",
            canonical_update_eligible=True,
        ),
    }


def _gs_run_query_process(query_text, year_low, year_high, max_results, queue):
    """Run one Scholar query in a killable child process."""
    try:
        from scholarly import scholarly

        search_results = scholarly.search_pubs(
            query_text, year_low=year_low, year_high=year_high
        )
        results = []
        capped = False
        for result in search_results:
            if len(results) >= max_results:
                capped = True
                break
            results.append(result)
        queue.put({"status": "complete", "results": results, "capped": capped})
    except Exception as e:
        queue.put({"status": "error", "error": f"{type(e).__name__}: {e}"})


def _legacy_gs_run_query(scholarly_mod, query_text, year_low, year_high, max_results, results_list):
    """Backward-compatible helper retained for external imports."""
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


def search_google_scholar(config, keys, provider_export=None):
    """Search Google Scholar via scholarly Python library."""
    if provider_export:
        return load_google_scholar_provider_export(config, provider_export)
    if config.get("metadata", {}).get("google_scholar_acquisition") == "provider_export_required":
        return {
            "database": "Google Scholar",
            "records_fetched": 0,
            "records": [],
            "query_execution": [],
            "execution": incomplete_execution(
                "provider-mediated Google Scholar export is required for incremental updates"
            ),
        }
    import multiprocessing

    log("Google Scholar: Starting search...")
    try:
        import scholarly  # noqa: F401
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
    query_execution = []
    context = multiprocessing.get_context("spawn")

    for i, query_text in enumerate(queries):
        if rate_limited:
            log(f"  GS query {i+1}/{len(queries)}: SKIPPED (rate-limited)")
            query_execution.append({
                "query_id": f"gs_q{i+1}",
                "complete": False,
                "status": "skipped_after_failure",
            })
            continue

        query_id = f"gs_q{i+1}"
        log(f"  GS query {i+1}/{len(queries)}: '{query_text[:60]}...'")

        queue = context.Queue()
        process = context.Process(
            target=_gs_run_query_process,
            args=(query_text, year_low, year_high, max_per_query, queue),
        )
        process.start()
        process.join(timeout=GS_QUERY_TIMEOUT)

        raw_results = []
        capped = False
        if process.is_alive():
            log(f"    Timeout after {GS_QUERY_TIMEOUT}s — Google Scholar is rate-limiting.")
            process.terminate()
            process.join(timeout=5)
            rate_limited = True
            query_execution.append({
                "query_id": query_id,
                "complete": False,
                "status": "timeout",
                "timeout_seconds": GS_QUERY_TIMEOUT,
            })
        else:
            try:
                payload = queue.get(timeout=2)
            except queue_module.Empty:
                payload = {
                    "status": "error",
                    "error": f"child process exited {process.exitcode} without a result",
                }
            if payload["status"] != "complete":
                log(f"    ERROR in GS query {i+1}: {payload.get('error', 'unknown error')}")
                rate_limited = True
                query_execution.append({
                    "query_id": query_id,
                    "complete": False,
                    "status": "error",
                    "reason": payload.get("error", "unknown error"),
                })
            else:
                raw_results = payload["results"]
                capped = bool(payload.get("capped"))

        count = 0
        for result in raw_results:
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
                "search_date_status": "unknown_year_only",
            }
            all_records.append(rec)
            count += 1

        log(f"    Retrieved {count} records")

        if not rate_limited:
            query_execution.append({
                "query_id": query_id,
                "complete": True,
                "status": "complete_at_protocol_cap" if capped else "complete",
                "records_retrieved": count,
                "max_per_query": max_per_query,
                "source_exhaustive": not capped,
            })

        time.sleep(5.0)

    log(f"  Google Scholar: {len(all_records)} total unique records")

    execution = (
        complete_execution(
            query_count=len(query_execution),
            source_exhaustive=all(row.get("source_exhaustive", True) for row in query_execution),
        )
        if len(query_execution) == len(queries)
        and all(row["complete"] for row in query_execution)
        else incomplete_execution(
            "one or more Google Scholar queries timed out, failed, or were skipped",
            query_execution=query_execution,
        )
    )
    return {
        "database": "Google Scholar",
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "queries": queries,
        "year_range": [year_low, year_high],
        "query_signature": query_signature(
            queries,
            [year_low, year_high],
            config["metadata"].get("date_from", ""),
            config["metadata"].get("date_to", ""),
            {"mode": "legacy_scholarly", "max_per_query": max_per_query},
        ),
        "date_precision": "year_only; cumulative deduplication is required",
        "records_fetched": len(all_records),
        "records": all_records,
        "query_execution": query_execution,
        "execution": execution,
    }


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
        "--file-date",
        default=None,
        help=(
            "Date suffix for exported filenames. Defaults to metadata.date_to so "
            "a delayed rerun keeps the protocol date instead of the wall-clock date."
        ),
    )
    parser.add_argument(
        "--databases",
        default=None,
        help="Comma-separated list of databases to search (default: all enabled). "
             "Options: pubmed,scopus,openalex,semantic_scholar,arxiv,biorxiv_medrxiv,springernature,google_scholar",
    )
    parser.add_argument(
        "--gs-fallback",
        default=None,
        help="Path to a cached Google Scholar JSON file. If GS is rate-limited and returns "
             "fewer results than this file, the cached results are used instead. "
             "Google Scholar has no official API and aggressively rate-limits scraping, "
             "so providing a fallback ensures reproducibility.",
    )
    parser.add_argument(
        "--s2-state-dir",
        default=None,
        help=(
            "Directory for resumable Semantic Scholar page artifacts and checkpoint. "
            "Defaults to <output-dir>/semantic_scholar_state."
        ),
    )
    parser.add_argument(
        "--gs-provider-export",
        default=None,
        help=(
            "Validated provider-mediated Google Scholar capture. Required when the "
            "incremental config declares google_scholar_acquisition=provider_export_required."
        ),
    )
    args = parser.parse_args()

    # Load config
    with open(args.config, "r") as f:
        config = json.load(f)
    file_date = args.file_date or config["metadata"]["date_to"]

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
    database_status = {}
    date_status_by_database = {}

    db_functions = {
        "pubmed": search_pubmed,
        "scopus": search_scopus,
        "openalex": search_openalex,
        "semantic_scholar": search_semantic_scholar,
        "arxiv": search_arxiv,
        "biorxiv_medrxiv": search_biorxiv,
        "springernature": search_springernature,
        "google_scholar": search_google_scholar,
    }
    unknown_selected = set(selected or []) - set(db_functions)
    if unknown_selected:
        parser.error("Unknown database names: " + ", ".join(sorted(unknown_selected)))
    requested_databases = [
        name
        for name in db_functions
        if config["databases"].get(name, {}).get("enabled", False)
        and (not selected or name in selected)
    ]

    for db_name, search_func in db_functions.items():
        db_config = config["databases"].get(db_name, {})
        if not db_config.get("enabled", False):
            continue
        if selected and db_name not in selected:
            continue

        log(f"\n{'='*60}")
        try:
            if db_name in {"springernature", "openalex"}:
                result, raw_records = search_func(config, keys)
                # Save raw records too
                raw_path = os.path.join(args.output_dir, f"{db_name}_raw_{file_date}.json")
                with open(raw_path, "w", encoding="utf-8") as f:
                    json.dump(raw_records, f, ensure_ascii=False, indent=2)
                log(f"  Saved raw records: {raw_path}")
            elif db_name == "google_scholar":
                result = search_func(config, keys, provider_export=args.gs_provider_export)
            elif db_name == "semantic_scholar":
                result = search_func(
                    config,
                    keys,
                    state_dir=args.s2_state_dir
                    or os.path.join(args.output_dir, "semantic_scholar_state"),
                )
            else:
                result = search_func(config, keys)

            if result is None:
                log(f"  {db_name}: Skipped (missing API key or error)")
                database_status[db_name] = incomplete_execution(
                    "search function returned no result"
                )
                summary[db_name] = 0
                date_status_by_database[db_name] = {
                    "retained_status_counts": {}, "excluded_out_of_range": 0
                }
                continue

            # Save results
            if db_name == "google_scholar":
                # Cached Scholar data is usable only when it carries the same
                # query signature and an explicit complete execution status.
                if args.gs_fallback and os.path.exists(args.gs_fallback):
                    with open(args.gs_fallback, "r", encoding="utf-8") as ff:
                        fallback_data = json.load(ff)
                    fallback_execution = (
                        fallback_data.get("execution", {})
                        if isinstance(fallback_data, dict)
                        else {}
                    )
                    signatures_match = (
                        isinstance(fallback_data, dict)
                        and fallback_data.get("query_signature") == result.get("query_signature")
                    )
                    if (
                        not result.get("execution", {}).get("complete")
                        and signatures_match
                        and fallback_execution.get("complete")
                    ):
                        log(f"  Using signature-matched complete fallback from {args.gs_fallback}")
                        result = fallback_data
                    elif not signatures_match:
                        log("  Ignoring Google Scholar fallback: query signature is absent or different")

                filepath = os.path.join(args.output_dir, f"google_scholar_{file_date}.json")
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                log(f"  Saved {filepath}")
                all_results[db_name] = result.get("records", [])
                summary[db_name] = result.get("records_fetched", len(result.get("records", [])))
            else:
                save_results(args.output_dir, db_name, result, file_date=file_date)
                all_results[db_name] = result.get("records", [])
                summary[db_name] = result.get("records_fetched", len(result.get("records", [])))
            database_status[db_name] = result.get(
                "execution",
                incomplete_execution("result did not declare execution completeness"),
            )
            status_counts = {}
            for record in all_results[db_name]:
                status = str(record.get("search_date_status") or "unreported")
                status_counts[status] = status_counts.get(status, 0) + 1
            date_status_by_database[db_name] = {
                "retained_status_counts": status_counts,
                "excluded_out_of_range": int(
                    ((result.get("date_audit") or {}).get("excluded_out_of_range")) or 0
                ),
            }

        except Exception as e:
            log(f"  ERROR in {db_name}: {e}")
            database_status[db_name] = {
                "status": "error",
                "complete": False,
                "reason": f"{type(e).__name__}: {e}",
            }
            summary[db_name] = 0
            date_status_by_database[db_name] = {
                "retained_status_counts": {}, "excluded_out_of_range": 0
            }
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
    if (
        all_results
        and config.get("ground_truth")
        and config.get("metadata", {}).get("run_historical_ground_truth_validation", True)
    ):
        validate_ground_truth(all_results, config["ground_truth"])

    # Save summary
    executed_at = datetime.now().isoformat()
    incomplete_databases = [
        name
        for name in requested_databases
        if not database_status.get(name, {}).get("complete", False)
    ]
    summary_path = os.path.join(args.output_dir, f"search_summary_{file_date}.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "search_date": file_date,
            "executed_at": executed_at,
            "config_file": args.config,
            "date_range": f"{config['metadata']['date_from']} to {config['metadata']['date_to']}",
            "requested_databases": requested_databases,
            "results_per_database": summary,
            "database_status": database_status,
            "date_status_by_database": date_status_by_database,
            "complete": not incomplete_databases,
            "incomplete_databases": incomplete_databases,
            "total_before_dedup": total,
        }, f, ensure_ascii=False, indent=2)
    log(f"\nSummary saved: {summary_path}")
    if incomplete_databases:
        log("INCOMPLETE databases: " + ", ".join(incomplete_databases))
        return 2
    log("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
