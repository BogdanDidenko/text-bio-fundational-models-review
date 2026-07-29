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
from difflib import SequenceMatcher
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin

import requests


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


def title_score(a: str, b: str) -> float:
    def norm(s: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

    aa, bb = norm(a), norm(b)
    if not aa or not bb:
        return 0.0
    if aa in bb or bb in aa:
        return 0.95
    return SequenceMatcher(None, aa, bb).ratio()


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
    return payload.startswith(b"%PDF") or "pdf" in content_type.lower()


def html_text_len(payload: bytes) -> int:
    text = payload.decode("utf-8", errors="ignore")
    text = re.sub(r"(?is)<(script|style|nav|footer|header).*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


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
    if looks_like_pdf(payload, content_type) and len(payload) >= PDF_MIN_BYTES:
        return write_payload(out_dir, f"{stem}.pdf", payload, attempts, content_type, source)
    if "html" in content_type.lower() and html_text_len(payload) >= HTML_MIN_TEXT_CHARS:
        return write_payload(out_dir, f"{stem}.html", payload, attempts, content_type, source)
    if "xml" in content_type.lower() and len(payload) >= HTML_MIN_TEXT_CHARS:
        return write_payload(out_dir, f"{stem}.xml", payload, attempts, content_type, source)
    return None


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
    text = payload.decode("utf-8", errors="ignore")
    for match in re.finditer(r"""href=["']([^"']+(?:\.pdf|/pdf|pdf/[^"']*))["']""", text, flags=re.I):
        urls.append(("landing_pdf_link", urljoin(f"https://doi.org/{quote(doi)}", match.group(1))))
    for match in re.finditer(r"""href=["']([^"']+(?:/full|fulltext|full-text)[^"']*)["']""", text, flags=re.I):
        urls.append(("landing_fulltext_link", urljoin(f"https://doi.org/{quote(doi)}", match.group(1))))
    return urls[:8]


def source_urls(record: dict[str, Any], session: requests.Session, email: str, attempts: list[dict[str, Any]]) -> list[tuple[str, str]]:
    doi = normalize_doi(record.get("doi"))
    title = str(record.get("title") or "")
    urls: list[tuple[str, str]] = []

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
                if title_score(title, work.get("title") or work.get("display_name") or "") >= 0.82:
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
            params={"query": title, "limit": 5, "fields": "title,externalIds,isOpenAccess,openAccessPdf,url"},
            headers=headers,
        )
        if s2_search:
            for paper in s2_search.get("data") or []:
                if title_score(title, paper.get("title") or "") >= 0.82:
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
                if title_score(title, cr_title) >= 0.82:
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
                if title_score(title, item.get("title") or "") >= 0.82:
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
                    if title_score(title, arxiv_title) >= 0.82:
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


def process_record(record: dict[str, Any], out_root: Path, email: str, sleep_seconds: float) -> dict[str, Any]:
    candidate_id = record.get("candidate_id") or f"{record.get('source_run','run')}__{record.get('record_id')}"
    out_dir = out_root / f"{slugify(candidate_id, 40)}__{slugify(record.get('title', ''), 70)}"
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
    elif files:
        status = "non_pdf_full_text_downloaded"

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
        "non_pdf_full_text_downloaded": sum(1 for r in results if r["status"] == "non_pdf_full_text_downloaded"),
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
    print(json.dumps({k: summary[k] for k in ("processed", "pdf_downloaded", "non_pdf_full_text_downloaded", "no_full_text_found")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
