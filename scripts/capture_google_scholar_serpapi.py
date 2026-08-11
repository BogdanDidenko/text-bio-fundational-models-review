#!/usr/bin/env python3
"""Capture a complete, auditable Google Scholar provider export via SerpAPI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import certifi

from reproduce_search import query_signature


API_URL = "https://serpapi.com/search.json"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def load_api_key(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    key = payload.get("serpapi") or payload.get("SERPAPI_API_KEY")
    if not key:
        raise RuntimeError(f"SerpAPI key is missing from {path}")
    return str(key)


def scrub_secret(value: Any, secret: str) -> Any:
    """Remove credentials from provider-returned URLs before artifact storage."""
    if isinstance(value, dict):
        return {
            key: ("[REDACTED]" if key.lower() in {"api_key", "apikey"} else scrub_secret(item, secret))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [scrub_secret(item, secret) for item in value]
    if isinstance(value, str):
        return value.replace(secret, "[REDACTED]")
    return value


def request_page(
    params: dict[str, Any] | None,
    api_key: str,
    retries: int,
    next_url: str | None = None,
) -> dict[str, Any]:
    if next_url:
        parsed = urllib.parse.urlsplit(next_url)
        query = dict(urllib.parse.parse_qsl(parsed.query))
        query["api_key"] = api_key
        url = urllib.parse.urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), "")
        )
    else:
        request_params = {**(params or {}), "api_key": api_key}
        url = f"{API_URL}?{urllib.parse.urlencode(request_params)}"
    for attempt in range(retries + 1):
        try:
            tls_context = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(url, timeout=90, context=tls_context) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("error") == "Google hasn't returned any results for this query.":
                return payload
            if payload.get("error"):
                raise RuntimeError(f"SerpAPI error: {payload['error']}")
            return payload
        except urllib.error.HTTPError as exc:
            if exc.code not in RETRYABLE_STATUS or attempt == retries:
                body = exc.read().decode("utf-8", errors="replace")[:500]
                raise RuntimeError(f"SerpAPI HTTP {exc.code}: {body}") from exc
            retry_after = exc.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else min(2 ** attempt, 30)
            time.sleep(delay)
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == retries:
                raise RuntimeError(f"SerpAPI transport failure: {exc}") from exc
            time.sleep(min(2 ** attempt, 30))
    raise AssertionError("unreachable")


def publication_year(result: dict[str, Any]) -> str:
    summary = str((result.get("publication_info") or {}).get("summary") or "")
    match = re.search(r"\b(19|20)\d{2}\b", summary)
    return match.group(0) if match else ""


def normalize_result(
    result: dict[str, Any], query_id: str, raw_artifact: str, raw_sha256: str
) -> dict[str, Any]:
    publication = result.get("publication_info") or {}
    authors = [
        str(author.get("name") or "").strip()
        for author in publication.get("authors") or []
        if isinstance(author, dict) and author.get("name")
    ]
    return {
        "title": str(result.get("title") or "").strip(),
        "authors": authors,
        "year": publication_year(result),
        "abstract": str(result.get("snippet") or "").strip(),
        "url": str(result.get("link") or "").strip(),
        "result_id": str(result.get("result_id") or "").strip(),
        "publication_info": str(publication.get("summary") or "").strip(),
        "query_ids": [query_id],
        "raw_artifact": raw_artifact,
        "raw_response_sha256": raw_sha256,
        "search_date_status": "unknown_year_only",
    }


def record_key(record: dict[str, Any]) -> str:
    title = re.sub(r"\W+", " ", record.get("title", "").casefold()).strip()
    return record.get("result_id") or title or record.get("url", "")


def write_json(path: Path, payload: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(body)
    os.replace(temporary, path)
    return hashlib.sha256(body).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--api-keys", type=Path, default=Path("api_keys.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--page-size", type=int, default=20)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    metadata = config["metadata"]
    scholar = config["databases"]["google_scholar"]
    api_key = load_api_key(args.api_keys)
    year_low, year_high = scholar["year_range"]
    acquisition = {
        "provider": "SerpAPI Google Scholar API",
        "provider_version": "search.json",
        "locale": "en",
        "pagination_policy": "retrieve every provider-visible page; no local result cap accepted",
    }
    bundle = {
        "queries": scholar["queries"],
        "year_range": scholar["year_range"],
        "date_from": metadata["date_from"],
        "date_to": metadata["date_to"],
        "acquisition": acquisition,
    }
    signature = query_signature(
        bundle["queries"], bundle["year_range"], bundle["date_from"],
        bundle["date_to"], acquisition
    )
    payload: dict[str, Any] = {
        "schema_version": 1,
        "query_bundle": bundle,
        "query_signature": signature,
        "raw_response_manifest": [],
        "query_execution": [],
        "records": [],
    }
    records_by_key: dict[str, dict[str, Any]] = {}
    raw_root = (
        args.output.parent / "raw" / "google_scholar_serpapi" / signature[:16]
    )

    for query_index, query in enumerate(scholar["queries"], start=1):
        query_id = f"gs_q{query_index}"
        page_index = 0
        query_occurrences = 0
        termination = "not_started"
        next_url: str | None = None
        seen_next_urls: set[str] = set()
        while True:
            start = page_index * args.page_size
            raw_path = raw_root / query_id / f"page_{page_index:03d}.json"
            if raw_path.is_file():
                response = json.loads(raw_path.read_text(encoding="utf-8"))
                raw_sha256 = hashlib.sha256(raw_path.read_bytes()).hexdigest()
            else:
                response = request_page(
                    {
                        "engine": "google_scholar",
                        "q": query,
                        "as_ylo": year_low,
                        "as_yhi": year_high,
                        "hl": "en",
                        "num": args.page_size,
                        "start": start,
                    },
                    api_key,
                    args.retries,
                    next_url=next_url,
                )
                raw_sha256 = write_json(raw_path, scrub_secret(response, api_key))
            raw_artifact = str(raw_path.relative_to(args.output.parent))
            payload["raw_response_manifest"].append(
                {
                    "query_id": query_id,
                    "page": page_index,
                    "artifact": raw_artifact,
                    "sha256": raw_sha256,
                }
            )
            organic = response.get("organic_results") or []
            for result in organic:
                record = normalize_result(result, query_id, raw_artifact, raw_sha256)
                key = record_key(record)
                if key in records_by_key:
                    existing = records_by_key[key]
                    if query_id not in existing["query_ids"]:
                        existing["query_ids"].append(query_id)
                    existing.setdefault("occurrences", []).append(
                        {"query_id": query_id, "raw_artifact": raw_artifact, "raw_response_sha256": raw_sha256}
                    )
                else:
                    record["occurrences"] = [
                        {"query_id": query_id, "raw_artifact": raw_artifact, "raw_response_sha256": raw_sha256}
                    ]
                    records_by_key[key] = record
                query_occurrences += 1

            pagination = response.get("serpapi_pagination") or {}
            next_url = pagination.get("next")
            if not next_url:
                termination = "no_next_page"
                break
            if next_url in seen_next_urls:
                termination = "pagination_cycle"
                break
            seen_next_urls.add(next_url)
            page_index += 1
            time.sleep(args.delay)

        complete = termination == "no_next_page"
        payload["query_execution"].append(
            {
                "query_id": query_id,
                "execution_complete": complete,
                "retrieval_complete": complete,
                "termination": termination,
                "pages_retrieved": page_index + 1,
                "records_retrieved": query_occurrences,
                "source_exhaustive": "unknown",
            }
        )
        payload["records"] = list(records_by_key.values())
        write_json(args.output, payload)
        if not complete:
            raise RuntimeError(
                f"{query_id} did not exhaust provider-visible pages: {termination}"
            )
        time.sleep(args.delay)

    print(
        json.dumps(
            {
                "output": str(args.output),
                "queries": len(payload["query_execution"]),
                "raw_pages": len(payload["raw_response_manifest"]),
                "unique_records": len(payload["records"]),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
