#!/usr/bin/env python3
"""Download legally available full texts for screened review candidates.

The script is DOI-first and conservative: it records every attempted source,
downloads only openly exposed PDFs/HTML/XML, and does not attempt paywall
bypass. It is intended for parallel batch runs with disjoint input slices.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urljoin, urlsplit

import requests

from metadata_match import accept_title_candidate


USER_AGENT = "lpnu-review-fulltext-harvester/2026-07-07 (mailto:{email})"
PDF_MIN_BYTES = 5000
HTML_MIN_TEXT_CHARS = 3000
LOCAL_KEYS: dict[str, str] | None = None


def local_api_keys() -> dict[str, str]:
    global LOCAL_KEYS
    if LOCAL_KEYS is not None:
        return LOCAL_KEYS
    for path in (Path("api_keys.json"), Path("scripts/api_keys.json")):
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                LOCAL_KEYS = {str(k): str(v) for k, v in data.items() if v}
                return LOCAL_KEYS
            except Exception:
                pass
    LOCAL_KEYS = {}
    return LOCAL_KEYS


def configured_key(*names: str) -> str:
    keys = local_api_keys()
    for name in names:
        if os.environ.get(name):
            return os.environ[name]
        if keys.get(name):
            return keys[name]
        lower = name.lower()
        if keys.get(lower):
            return keys[lower]
    return ""


def openalex_params(email: str, **extra: Any) -> dict[str, Any]:
    params = {"mailto": email, **extra}
    api_key = configured_key("OPENALEX_API_KEY", "OPENALEX_CONTENT_API_KEY", "openalex")
    if api_key:
        params["api_key"] = api_key
    return params


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def redact_url(url: str) -> str:
    return re.sub(r"([?&](?:api_?key|key|token|x-api-key)=)[^&#]+", r"\1REDACTED", url, flags=re.I)


def slugify(value: str, limit: int = 80) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")
    return cleaned[:limit] or "untitled"


def normalize_doi(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value, flags=re.I)
    value = re.sub(r"^doi:\s*", "", value, flags=re.I)
    return value.strip()


def quote_doi_path(doi: str) -> str:
    return quote(doi, safe="")


def quote_doi_url(doi: str) -> str:
    return quote(doi, safe="/")


def arxiv_id_from_record(record: dict[str, Any]) -> str:
    haystack = " ".join(str(record.get(k, "")) for k in ("doi", "title", "abstract"))
    patterns = [
        r"arxiv[:\s./]+([0-9]{4}\.[0-9]{4,5})(?:v[0-9]+)?",
        r"\b([0-9]{4}\.[0-9]{4,5})(?:v[0-9]+)?\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, haystack, flags=re.I)
        if match:
            return match.group(1)
    return ""


def record_title_candidate_attempt(
    attempts: list[dict[str, Any]], source: str, candidate: dict[str, Any]
) -> bool:
    """Audit a title-derived location and return whether it is safe to follow."""
    candidate_metadata = dict(candidate)
    record = candidate_metadata.pop("record")
    accepted, reason, evidence = accept_title_candidate(record, candidate_metadata)
    attempts.append(
        {
            "time": now_iso(),
            "source": source,
            "candidate_identifier": candidate_metadata.get("doi") or candidate_metadata.get("paperId") or candidate_metadata.get("id") or "",
            "title_match_status": reason,
            "title_match_evidence": evidence,
        }
    )
    return accepted


def add_openalex_locations(work: dict[str, Any], urls: list[tuple[str, str]], prefix: str = "openalex") -> None:
    api_key = configured_key("OPENALEX_API_KEY", "OPENALEX_CONTENT_API_KEY", "openalex")
    for key, url in (work.get("content_urls") or {}).items():
        if url:
            if api_key and "api_key=" not in url:
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}api_key={quote(api_key)}"
            urls.append((f"{prefix}_content_{key}", url))
    for loc in [work.get("primary_location") or {}, work.get("best_oa_location") or {}]:
        for key in ("pdf_url", "landing_page_url"):
            if loc.get(key):
                urls.append((f"{prefix}_{key}", loc[key]))
    if (work.get("open_access") or {}).get("oa_url"):
        urls.append((f"{prefix}_oa_url", work["open_access"]["oa_url"]))
    for loc in work.get("locations") or []:
        for key in ("pdf_url", "landing_page_url"):
            if loc.get(key):
                urls.append((f"{prefix}_location_{key}", loc[key]))


def request_json(session: requests.Session, url: str, attempts: list[dict[str, Any]], source: str, **kwargs: Any) -> dict[str, Any] | None:
    started = now_iso()
    try:
        resp = session.get(url, timeout=kwargs.pop("timeout", 30), **kwargs)
        attempts.append(
            {
                "time": started,
                "source": source,
                "url": redact_url(url),
                "status_code": resp.status_code,
                "content_type": resp.headers.get("content-type", ""),
                "bytes": len(resp.content),
            }
        )
        if resp.ok:
            return resp.json()
    except Exception as exc:  # noqa: BLE001 - logged as audit evidence
        attempts.append({"time": started, "source": source, "url": redact_url(url), "error": repr(exc)})
    return None


def fetch_url(session: requests.Session, url: str, attempts: list[dict[str, Any]], source: str) -> tuple[bytes, str, int] | None:
    started = now_iso()
    try:
        resp = session.get(url, timeout=45, allow_redirects=True)
        content_type = resp.headers.get("content-type", "")
        attempts.append(
            {
                "time": started,
                "source": source,
                "url": redact_url(url),
                "final_url": redact_url(resp.url),
                "status_code": resp.status_code,
                "content_type": content_type,
                "bytes": len(resp.content),
            }
        )
        if resp.ok and resp.content:
            return resp.content, content_type, resp.status_code
    except Exception as exc:  # noqa: BLE001 - logged as audit evidence
        attempts.append({"time": started, "source": source, "url": redact_url(url), "error": repr(exc)})
    return None


def looks_like_pdf(payload: bytes, content_type: str) -> bool:
    # MIME headers are frequently wrong or point to HTML access-denied pages.
    return payload.lstrip().startswith(b"%PDF")


def payload_kind(payload: bytes, content_type: str) -> str:
    if looks_like_pdf(payload, content_type):
        return "pdf"
    head = payload[:4096].lstrip().lower()
    if b"<!doctype html" in head or b"<html" in head:
        return "html"
    if head.startswith(b"<?xml") or b"<article" in head:
        return "xml"
    lowered_type = content_type.casefold()
    if "html" in lowered_type:
        return "html"
    if "xml" in lowered_type:
        return "xml"
    return "unknown"


def technical_attempt_failures(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures = []
    for attempt in attempts:
        status = int(attempt.get("status_code") or 0)
        if attempt.get("error") or status in {408, 425, 429} or status >= 500:
            failures.append(attempt)
    return failures


def access_restriction_attempts(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        attempt for attempt in attempts
        if int(attempt.get("status_code") or 0) in {401, 403}
    ]


def html_text_len(payload: bytes) -> int:
    text = payload.decode("utf-8", errors="ignore")
    text = re.sub(r"(?is)<(script|style|nav|footer|header).*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def looks_like_full_text_html(payload: bytes) -> bool:
    if html_text_len(payload) < HTML_MIN_TEXT_CHARS:
        return False
    lowered = payload.decode("utf-8", errors="ignore").casefold()
    paywall_markers = (
        'id="access-options"',
        "id='access-options'",
        'data-test="buy-or-subscribe"',
        "data-test='buy-or-subscribe'",
        'class="buyboxsection"',
        "class='buyboxsection'",
        '<meta name="ncbi_app" content="pubmed"',
        "<meta name='ncbi_app' content='pubmed'",
        'name="citation_abstract_html_url"',
        "name='citation_abstract_html_url'",
    )
    return not any(marker in lowered for marker in paywall_markers)


def write_payload(out_dir: Path, name: str, payload: bytes, attempts: list[dict[str, Any]], content_type: str, source: str) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    path.write_bytes(payload)
    sha = hashlib.sha256(payload).hexdigest()
    return {
        "source": source,
        "file": str(path),
        "filename": name,
        "content_type": content_type,
        "bytes": len(payload),
        "sha256": sha,
    }


def try_download(session: requests.Session, url: str, out_dir: Path, stem: str, attempts: list[dict[str, Any]], source: str) -> dict[str, Any] | None:
    if not url:
        return None
    result = fetch_url(session, url, attempts, source)
    if not result:
        return None
    payload, content_type, _ = result
    kind = payload_kind(payload, content_type)
    if kind == "pdf" and len(payload) >= PDF_MIN_BYTES:
        return write_payload(out_dir, f"{stem}.pdf", payload, attempts, content_type, source)
    if kind == "html" and looks_like_full_text_html(payload):
        return write_payload(out_dir, f"{stem}.html", payload, attempts, content_type, source)
    if kind == "xml" and len(payload) >= HTML_MIN_TEXT_CHARS:
        return write_payload(out_dir, f"{stem}.xml", payload, attempts, content_type, source)
    return None


class FullTextLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): (value or "") for key, value in attrs}
        if tag.casefold() == "a":
            href = values.get("href", "")
            marker = " ".join((values.get("title", ""), values.get("class", ""))).casefold()
            if href and ("pdf" in marker or re.search(r"(?:\.pdf|/pdf|pdf/)", href, flags=re.I)):
                self.links.append(("landing_pdf_link", href))
            elif href and re.search(r"(?:/full|fulltext|full-text)", href, flags=re.I):
                self.links.append(("landing_fulltext_link", href))
        elif tag.casefold() in {"embed", "object"}:
            media_type = values.get("type", "").casefold()
            value = values.get("src", "") or values.get("data", "")
            if value and "pdf" in media_type:
                self.links.append(("landing_embedded_pdf", value))


def is_supplementary_url(url: str) -> bool:
    """Reject article-page assets that are not the primary report."""
    path = unquote(urlsplit(url).path).casefold()
    return any(
        marker in path
        for marker in (
            "/esm/",
            "moesm",
            "supplement",
            "suppinfo",
            "supporting-information",
            "reporting-summary",
            "source-data",
        )
    )


def fulltext_links_from_html(payload: bytes, base_url: str) -> list[tuple[str, str]]:
    parser = FullTextLinkParser()
    parser.feed(payload.decode("utf-8", errors="ignore"))
    deduped = []
    seen = set()
    for source, value in parser.links:
        url = urljoin(base_url, html.unescape(value)).split("#", 1)[0]
        if is_supplementary_url(url):
            continue
        if url not in seen:
            seen.add(url)
            deduped.append((source, url))
    return deduped[:8]


def candidate_urls_from_landing(session: requests.Session, doi: str, attempts: list[dict[str, Any]]) -> list[tuple[str, str]]:
    if not doi:
        return []
    result = fetch_url(session, f"https://doi.org/{quote_doi_url(doi)}", attempts, "doi_landing")
    if not result:
        return []
    payload, content_type, _ = result
    urls: list[tuple[str, str]] = []
    if looks_like_pdf(payload, content_type):
        return [("doi_landing_pdf", f"https://doi.org/{quote_doi_url(doi)}")]
    return fulltext_links_from_html(payload, f"https://doi.org/{quote_doi_url(doi)}")


def source_urls(record: dict[str, Any], session: requests.Session, email: str, attempts: list[dict[str, Any]]) -> list[tuple[str, str]]:
    doi = normalize_doi(record.get("doi"))
    title = str(record.get("title") or "")
    urls: list[tuple[str, str]] = []
    match_record = dict(record)

    explicit_urls = []
    for key in ("url", "pdf_url", "full_text_url"):
        value = str(record.get(key) or "").strip()
        if value.startswith(("http://", "https://")):
            explicit_urls.append((f"record_{key}", value))
    urls.extend(explicit_urls)
    for source, value in explicit_urls:
        probe = fetch_url(session, value, attempts, f"{source}_landing_probe")
        if probe and payload_kind(probe[0], probe[1]) == "html":
            urls.extend(fulltext_links_from_html(probe[0], value))

    arxiv_id = arxiv_id_from_record(record)
    if arxiv_id:
        urls.append(("arxiv_pdf", f"https://arxiv.org/pdf/{arxiv_id}.pdf"))
        urls.append(("arxiv_html", f"https://arxiv.org/html/{arxiv_id}"))

    if doi and re.search(r"10\.1101|10\.21203|10\.64898", doi, flags=re.I):
        doi_url = quote_doi_url(doi)
        urls.append(("biorxiv_medrxiv_pdf", f"https://www.biorxiv.org/content/{doi_url}.full.pdf"))
        urls.append(("biorxiv_medrxiv_html", f"https://www.biorxiv.org/content/{doi_url}.full"))
        urls.append(("medrxiv_pdf", f"https://www.medrxiv.org/content/{doi_url}.full.pdf"))
        urls.append(("medrxiv_html", f"https://www.medrxiv.org/content/{doi_url}.full"))

    if doi:
        crossref_doi = request_json(
            session,
            f"https://api.crossref.org/works/{quote_doi_path(doi)}",
            attempts,
            "crossref_doi_api",
        )
        crossref_message = (crossref_doi or {}).get("message") or {}
        if crossref_message.get("author"):
            match_record["authors"] = crossref_message["author"]
        for link in crossref_message.get("link") or []:
            if link.get("URL"):
                urls.append(("crossref_doi_link", link["URL"]))

        unpaywall = request_json(
            session,
            f"https://api.unpaywall.org/v2/{quote_doi_path(doi)}?email={quote(email)}",
            attempts,
            "unpaywall_api",
        )
        if unpaywall:
            locations = []
            if unpaywall.get("best_oa_location"):
                locations.append(unpaywall["best_oa_location"])
            locations.extend(unpaywall.get("oa_locations") or [])
            for loc in locations:
                for key in ("url_for_pdf", "url"):
                    if loc.get(key):
                        urls.append((f"unpaywall_{key}", loc[key]))

        openalex = request_json(
            session,
            f"https://api.openalex.org/works/doi:{quote_doi_path(doi)}",
            attempts,
            "openalex_api",
            params=openalex_params(email),
        )
        if openalex:
            add_openalex_locations(openalex, urls)

        s2_url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{quote_doi_path(doi)}?fields=title,isOpenAccess,openAccessPdf,url,externalIds"
        headers = {}
        s2_key = configured_key("S2_API_KEY", "semantic_scholar")
        if s2_key:
            headers["x-api-key"] = s2_key
        s2 = request_json(session, s2_url, attempts, "semantic_scholar_api", headers=headers)
        if s2 and isinstance(s2.get("openAccessPdf"), dict) and s2["openAccessPdf"].get("url"):
            urls.append(("semantic_scholar_openAccessPdf", s2["openAccessPdf"]["url"]))

        epmc = request_json(
            session,
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            attempts,
            "europepmc_search",
            params={"query": f'DOI:"{doi}"', "format": "json", "resultType": "core"},
        )
        if epmc:
            for item in (epmc.get("resultList") or {}).get("result") or []:
                pmcid = item.get("pmcid")
                if pmcid:
                    if not str(pmcid).upper().startswith("PMC"):
                        pmcid = f"PMC{pmcid}"
                    urls.append(("europepmc_fulltext_xml", f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"))
                    urls.append(("pmc_html", f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"))
                    urls.append(("pmc_pdf", f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/"))
                for link in ((item.get("fullTextUrlList") or {}).get("fullTextUrl") or []):
                    if link.get("url"):
                        urls.append((f"europepmc_{link.get('site','fulltext')}", link["url"]))

        urls.extend(candidate_urls_from_landing(session, doi, attempts))

    if title:
        openalex_search = request_json(
            session,
            "https://api.openalex.org/works",
            attempts,
            "openalex_title_search",
            params=openalex_params(email, search=title, **{"per-page": 5}),
        )
        if openalex_search:
            for work in openalex_search.get("results") or []:
                candidate = {
                    "record": match_record,
                    "id": work.get("id", ""),
                    "title": work.get("title") or work.get("display_name") or "",
                    "year": work.get("publication_year"),
                    "authors": [
                        ((authorship.get("author") or {}).get("display_name") or "")
                        for authorship in (work.get("authorships") or [])
                    ],
                    "doi": normalize_doi(work.get("doi")),
                }
                if record_title_candidate_attempt(attempts, "openalex_title_match", candidate):
                    add_openalex_locations(work, urls, "openalex_title")
                    found_doi = normalize_doi(work.get("doi"))
                    if found_doi and found_doi != doi:
                        urls.extend(candidate_urls_from_landing(session, found_doi, attempts))

        headers = {}
        s2_key = configured_key("S2_API_KEY", "semantic_scholar")
        if s2_key:
            headers["x-api-key"] = s2_key
        s2_search = request_json(
            session,
            "https://api.semanticscholar.org/graph/v1/paper/search",
            attempts,
            "semantic_scholar_title_search",
            params={"query": title, "limit": 5, "fields": "title,year,authors,paperId,externalIds,isOpenAccess,openAccessPdf,url"},
            headers=headers,
        )
        if s2_search:
            for paper in s2_search.get("data") or []:
                candidate = {"record": match_record, **paper}
                if record_title_candidate_attempt(attempts, "semantic_scholar_title_match", candidate):
                    pdf = paper.get("openAccessPdf") or {}
                    if pdf.get("url"):
                        urls.append(("semantic_scholar_title_openAccessPdf", pdf["url"]))
                    ext = paper.get("externalIds") or {}
                    for key in ("DOI", "ArXiv"):
                        if ext.get(key):
                            if key == "DOI":
                                urls.extend(candidate_urls_from_landing(session, normalize_doi(ext[key]), attempts))
                            if key == "ArXiv":
                                urls.append(("semantic_scholar_title_arxiv_pdf", f"https://arxiv.org/pdf/{ext[key]}.pdf"))

        crossref = request_json(
            session,
            "https://api.crossref.org/works",
            attempts,
            "crossref_title_search",
            params={"query.title": title, "rows": 5},
        )
        if crossref:
            for item in ((crossref.get("message") or {}).get("items") or []):
                cr_title = " ".join(item.get("title") or [])
                candidate = {
                    "record": match_record,
                    "title": cr_title,
                    "doi": normalize_doi(item.get("DOI")),
                    "year": next(
                        (parts[0][0] for key in ("published-print", "published-online", "issued")
                         if (parts := (item.get(key) or {}).get("date-parts")) and parts[0]), None
                    ),
                    "authors": item.get("author") or [],
                }
                if record_title_candidate_attempt(attempts, "crossref_title_match", candidate):
                    for link in item.get("link") or []:
                        if link.get("URL"):
                            urls.append(("crossref_title_link", link["URL"]))
                    found_doi = normalize_doi(item.get("DOI"))
                    if found_doi and found_doi != doi:
                        urls.extend(candidate_urls_from_landing(session, found_doi, attempts))

        epmc_title = request_json(
            session,
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            attempts,
            "europepmc_title_search",
            params={"query": f'TITLE:"{title}"', "format": "json", "resultType": "core", "pageSize": 5},
        )
        if epmc_title:
            for item in (epmc_title.get("resultList") or {}).get("result") or []:
                candidate = {
                    "record": match_record,
                    "title": item.get("title") or "",
                    "year": item.get("pubYear") or item.get("firstPublicationDate", ""),
                    "authors": item.get("authorString") or "",
                    "id": item.get("id") or "",
                }
                if record_title_candidate_attempt(attempts, "europepmc_title_match", candidate):
                    pmcid = item.get("pmcid")
                    if pmcid:
                        if not str(pmcid).upper().startswith("PMC"):
                            pmcid = f"PMC{pmcid}"
                        urls.append(("europepmc_title_fulltext_xml", f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"))
                        urls.append(("pmc_title_html", f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"))
                        urls.append(("pmc_title_pdf", f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/"))
                    for link in ((item.get("fullTextUrlList") or {}).get("fullTextUrl") or []):
                        if link.get("url"):
                            urls.append((f"europepmc_title_{link.get('site','fulltext')}", link["url"]))

        started = now_iso()
        try:
            arxiv_resp = session.get(
                "https://export.arxiv.org/api/query",
                params={"search_query": f'ti:"{title}"', "start": 0, "max_results": 3},
                timeout=30,
            )
            attempts.append(
                {
                    "time": started,
                    "source": "arxiv_title_search",
                    "url": redact_url(arxiv_resp.url),
                    "status_code": arxiv_resp.status_code,
                    "content_type": arxiv_resp.headers.get("content-type", ""),
                    "bytes": len(arxiv_resp.content),
                }
            )
            if arxiv_resp.ok:
                root = ET.fromstring(arxiv_resp.content)
                ns = {"a": "http://www.w3.org/2005/Atom"}
                for entry in root.findall("a:entry", ns):
                    arxiv_title = (entry.findtext("a:title", default="", namespaces=ns) or "").replace("\n", " ")
                    candidate = {
                        "record": match_record,
                        "title": arxiv_title,
                        "year": (entry.findtext("a:published", default="", namespaces=ns) or "")[:4],
                        "authors": [
                            author.findtext("a:name", default="", namespaces=ns) or ""
                            for author in entry.findall("a:author", ns)
                        ],
                    }
                    if record_title_candidate_attempt(attempts, "arxiv_title_match", candidate):
                        entry_id = entry.findtext("a:id", default="", namespaces=ns) or ""
                        match = re.search(r"/abs/([^/]+)$", entry_id)
                        if match:
                            urls.append(("arxiv_title_pdf", f"https://arxiv.org/pdf/{match.group(1)}.pdf"))
                        for link in entry.findall("a:link", ns):
                            href = link.attrib.get("href", "")
                            if href and (link.attrib.get("title") == "pdf" or href.endswith(".pdf")):
                                urls.append(("arxiv_title_link_pdf", href))
        except Exception as exc:  # noqa: BLE001 - logged as audit evidence
            attempts.append({"time": started, "source": "arxiv_title_search", "url": "https://export.arxiv.org/api/query", "error": repr(exc)})

    deduped: list[tuple[str, str]] = []
    seen = set()
    for source, url in urls:
        if url and url not in seen:
            seen.add(url)
            deduped.append((source, url))
    return deduped


def reusable_existing_result(out_dir: Path, candidate_id: str) -> dict[str, Any] | None:
    result_path = out_dir / "download_result.json"
    if not result_path.is_file():
        return None
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if str(result.get("candidate_id") or "") != str(candidate_id):
        return None
    valid_files = []
    for item in result.get("files") or []:
        path = Path(str(item.get("file") or ""))
        try:
            payload = path.read_bytes()
        except OSError:
            continue
        if len(payload) != int(item.get("bytes") or -1):
            continue
        if hashlib.sha256(payload).hexdigest() != item.get("sha256"):
            continue
        kind = payload_kind(payload, str(item.get("content_type") or ""))
        if kind == "pdf" and len(payload) >= PDF_MIN_BYTES:
            valid_files.append(item)
        elif kind == "html" and looks_like_full_text_html(payload):
            valid_files.append(item)
        elif kind == "xml" and len(payload) >= HTML_MIN_TEXT_CHARS:
            valid_files.append(item)
    if not valid_files:
        return None
    result["files"] = valid_files
    if any(str(row.get("filename", "")).endswith(".pdf") for row in valid_files):
        result["status"] = "pdf_downloaded"
    elif any(str(row.get("filename", "")).endswith(".html") for row in valid_files):
        result["status"] = "html_full_text_downloaded"
    else:
        result["status"] = "xml_full_text_downloaded"
    result["reused_existing"] = True
    return result


def process_record(record: dict[str, Any], out_root: Path, email: str, sleep_seconds: float) -> dict[str, Any]:
    candidate_id = record.get("candidate_id") or f"{record.get('source_run','run')}__{record.get('record_id')}"
    out_dir = out_root / f"{slugify(candidate_id, 40)}__{slugify(record.get('title', ''), 70)}"
    if existing := reusable_existing_result(out_dir, str(candidate_id)):
        return existing
    attempts: list[dict[str, Any]] = []
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT.format(email=email)})
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metadata.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    files: list[dict[str, Any]] = []
    for idx, (source, url) in enumerate(source_urls(record, session, email, attempts), start=1):
        kind = "full_text"
        if "pdf" in source.lower():
            kind = "full_text"
        elif "xml" in source.lower():
            kind = "full_text"
        file_info = try_download(session, url, out_dir, f"{kind}_{idx:02d}_{slugify(source, 30)}", attempts, source)
        if file_info:
            files.append(file_info)
            if file_info["filename"].endswith(".pdf"):
                break
        if sleep_seconds:
            time.sleep(sleep_seconds)

    status = "no_full_text_found"
    if any(f["filename"].endswith(".pdf") for f in files):
        status = "pdf_downloaded"
    elif any(f["filename"].endswith(".html") for f in files):
        status = "html_full_text_downloaded"
    elif any(f["filename"].endswith(".xml") for f in files):
        status = "xml_full_text_downloaded"
    elif technical_attempt_failures(attempts):
        status = "retrieval_incomplete"
    elif access_restriction_attempts(attempts):
        status = "access_restricted"

    result = {
        "candidate_id": candidate_id,
        "source_run": record.get("source_run"),
        "record_id": record.get("record_id"),
        "title": record.get("title"),
        "doi": normalize_doi(record.get("doi")),
        "decision": record.get("final_decision"),
        "status": status,
        "folder": str(out_dir),
        "files": files,
        "attempt_count": len(attempts),
        "technical_failure_count": len(technical_attempt_failures(attempts)),
        "access_restriction_count": len(access_restriction_attempts(attempts)),
    }
    (out_dir / "download_attempts.jsonl").write_text(
        "".join(json.dumps(a, ensure_ascii=False) + "\n" for a in attempts),
        encoding="utf-8",
    )
    (out_dir / "download_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def read_candidates(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "records" in data:
        return data["records"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported candidate file: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--email", default=os.environ.get("UNPAYWALL_EMAIL") or os.environ.get("GIT_AUTHOR_EMAIL") or "bogdan.didenko@example.com")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-existing", action="store_true", help="Skip records that already have existing_full_text_status in the input manifest.")
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()

    records = read_candidates(args.input)
    end = None if args.limit <= 0 else args.offset + args.limit
    records = records[args.offset:end]
    args.out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for i, record in enumerate(records, start=args.offset + 1):
        if args.skip_existing and record.get("existing_full_text_status"):
            result = {
                "candidate_id": record.get("candidate_id"),
                "source_run": record.get("source_run"),
                "record_id": record.get("record_id"),
                "title": record.get("title"),
                "doi": normalize_doi(record.get("doi")),
                "decision": record.get("final_decision"),
                "status": "skipped_existing",
                "folder": record.get("existing_full_text_folder", ""),
                "files": record.get("existing_full_text_files", []),
                "attempt_count": 0,
            }
            print(f"[{i}] skip existing {result['candidate_id']}", flush=True)
            results.append(result)
            continue
        print(f"[{i}] {record.get('candidate_id') or record.get('record_id')} {record.get('title','')[:100]}", flush=True)
        results.append(process_record(record, args.out_dir, args.email, args.sleep))

    summary = {
        "created": now_iso(),
        "input": str(args.input),
        "out_dir": str(args.out_dir),
        "offset": args.offset,
        "limit": args.limit,
        "processed": len(results),
        "pdf_downloaded": sum(1 for r in results if r["status"] == "pdf_downloaded"),
        "html_full_text_downloaded": sum(1 for r in results if r["status"] == "html_full_text_downloaded"),
        "xml_full_text_downloaded": sum(1 for r in results if r["status"] == "xml_full_text_downloaded"),
        "retrieval_incomplete": sum(1 for r in results if r["status"] == "retrieval_incomplete"),
        "access_restricted": sum(1 for r in results if r["status"] == "access_restricted"),
        "no_full_text_found": sum(1 for r in results if r["status"] == "no_full_text_found"),
        "skipped_existing": sum(1 for r in results if r["status"] == "skipped_existing"),
        "results": results,
    }
    (args.out_dir / "batch_manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    with (args.out_dir / "batch_manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["candidate_id", "source_run", "record_id", "decision", "status", "doi", "title", "folder", "attempt_count"])
        writer.writeheader()
        for row in results:
            writer.writerow({k: row.get(k, "") for k in writer.fieldnames})
    print(json.dumps({k: summary[k] for k in (
        "processed", "pdf_downloaded", "html_full_text_downloaded", "xml_full_text_downloaded",
        "retrieval_incomplete", "access_restricted", "no_full_text_found",
    )}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
