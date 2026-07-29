#!/usr/bin/env python3
"""Extract grounded author-stated motivation claims from the 52-paper corpus."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import datetime as dt
import hashlib
import json
import re
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / (
    "data/docling_include_vlm_52_2026-07-10_nolimits/manifests/"
    "canonical_docling_profile_manifest.csv"
)
DEFAULT_OUTPUT = ROOT / "data/health_intelligence_conference_2026_abstract_2026-07-11"


CLAIM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["record_id", "claims", "paper_summary"],
    "properties": {
        "record_id": {"type": "string"},
        "paper_summary": {"type": "string"},
        "claims": {
            "type": "array",
            "maxItems": 4,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "theme_label",
                    "claim_summary",
                    "limitation_addressed",
                    "why_text",
                    "why_multimodal",
                    "claimed_capability",
                    "evidence_quote",
                    "section_heading",
                ],
                "properties": {
                    "theme_label": {"type": "string"},
                    "claim_summary": {"type": "string"},
                    "limitation_addressed": {"type": "string"},
                    "why_text": {"type": "string"},
                    "why_multimodal": {"type": "string"},
                    "claimed_capability": {"type": "string"},
                    "evidence_quote": {"type": "string"},
                    "section_heading": {"type": "string"},
                },
            },
        },
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def canonical_with_map(text: str) -> tuple[str, list[int]]:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
    }
    chars: list[str] = []
    mapping: list[int] = []
    previous_space = False
    for index, original in enumerate(text):
        normalized = replacements.get(original, unicodedata.normalize("NFKC", original)).casefold()
        for char in normalized:
            if char.isspace():
                if previous_space:
                    continue
                char = " "
                previous_space = True
            else:
                previous_space = False
            chars.append(char)
            mapping.append(index)
    return "".join(chars).strip(), mapping


def recover_quote(markdown: str, quote: str) -> tuple[str, bool]:
    if quote in markdown:
        return quote, True
    tokens = re.split(r"\s+", quote.strip())
    if not tokens:
        return quote, False
    pattern = r"\s+".join(re.escape(token) for token in tokens)
    match = re.search(pattern, markdown, flags=re.MULTILINE)
    if match:
        return match.group(0), True
    trimmed = quote.strip().strip('"\'“”‘’')
    canonical_markdown, mapping = canonical_with_map(markdown)
    canonical_quote, _ = canonical_with_map(trimmed)
    position = canonical_markdown.find(canonical_quote)
    if position >= 0 and mapping:
        start = mapping[position]
        end = mapping[position + len(canonical_quote) - 1] + 1
        return markdown[start:end], True
    return quote, False


def native_provenance(docling: dict[str, Any], quote: str) -> tuple[list[str], list[int]]:
    qnorm = normalize_ws(quote)
    refs: list[str] = []
    pages: set[int] = set()
    for collection in ("texts", "tables", "pictures"):
        for item in docling.get(collection, []) or []:
            text = normalize_ws(str(item.get("text") or item.get("orig") or ""))
            if qnorm and (qnorm in text or text in qnorm) and min(len(qnorm), len(text)) >= 40:
                ref = item.get("self_ref")
                if ref:
                    refs.append(str(ref))
                for prov in item.get("prov") or []:
                    page = prov.get("page_no")
                    if isinstance(page, int):
                        pages.add(page)
    return sorted(set(refs)), sorted(pages)


def prompt_for(record: dict[str, str], markdown: str) -> str:
    return f"""You are extracting author-stated research motivation from one biomedical paper.

Record ID: {record['candidate_id']}
Title: {record['title']}

Read the complete paper below. Identify at most four distinct, explicit motivation claims stated by the authors in the abstract, introduction, discussion, or conclusion. Focus on why text is used, why multimodal biological grounding is needed, which prior limitation is addressed, and which capability the integration is expected to enable.

Rules:
- Do not impose a predefined taxonomy of motivations.
- Do not infer benefits that the authors do not state.
- Each evidence_quote must be a single contiguous verbatim passage from the supplied paper, preferably one sentence and no more than 60 words.
- Use the nearest exact section heading visible in the paper.
- Distinguish a limitation, the role of text, the role of multimodality, and the claimed capability in separate fields.
- If the paper does not explicitly motivate one of these aspects, use an empty string for that field.
- Return only schema-valid JSON.

COMPLETE DOCLING MARKDOWN
-------------------------
{markdown}
"""


def post_json(url: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"content-type": "application/json", "authorization": "Bearer local"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_one(
    record: dict[str, str],
    output: Path,
    endpoint: str,
    model: str,
    timeout: int,
    retries: int,
) -> dict[str, Any]:
    record_id = record["candidate_id"]
    markdown_path = ROOT / record["markdown"]
    docling_path = ROOT / record["docling_json"]
    markdown = markdown_path.read_text(encoding="utf-8")
    docling = json.loads(docling_path.read_text(encoding="utf-8"))
    prompt = prompt_for(record, markdown)
    log_dir = output / "motivation_extraction" / "records" / record_id
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "MotivationEvidenceDocument", "schema": CLAIM_SCHEMA},
        },
    }
    started = time.time()
    last_error = ""
    for attempt in range(1, retries + 2):
        try:
            raw = post_json(endpoint, payload, timeout)
            content = raw["choices"][0]["message"]["content"]
            (log_dir / f"response_attempt_{attempt}.txt").write_text(content, encoding="utf-8")
            parsed = json.loads(content)
            if parsed.get("record_id") != record_id:
                parsed["record_id"] = record_id
            grounded_claims = []
            for idx, claim in enumerate(parsed.get("claims") or [], start=1):
                repaired_quote, matched = recover_quote(markdown, str(claim["evidence_quote"]))
                refs, pages = native_provenance(docling, repaired_quote)
                grounded = dict(claim)
                grounded.update(
                    {
                        "claim_id": f"{record_id}::motivation_{idx:02d}",
                        "evidence_quote": repaired_quote,
                        "quote_verified_in_markdown": matched,
                        "heading_verified_in_markdown": (
                            str(claim["section_heading"]) in markdown
                            if claim.get("section_heading")
                            else False
                        ),
                        "doc_item_refs": refs,
                        "pages": pages,
                    }
                )
                grounded_claims.append(grounded)
            parsed["claims"] = grounded_claims
            parsed.update(
                {
                    "candidate_id": record_id,
                    "source_record_id": record["source_record_id"],
                    "title": record["title"],
                    "doi": record["doi"],
                    "markdown": record["markdown"],
                    "docling_json": record["docling_json"],
                    "markdown_sha256": sha256(markdown_path),
                    "docling_sha256": sha256(docling_path),
                    "model": model,
                    "attempt": attempt,
                    "elapsed_seconds": round(time.time() - started, 3),
                    "status": "success",
                }
            )
            (log_dir / "grounded.json").write_text(
                json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            return parsed
        except Exception as exc:  # logged and retried without hiding the original failure
            last_error = repr(exc)
            (log_dir / f"error_attempt_{attempt}.txt").write_text(last_error + "\n", encoding="utf-8")
    return {
        "candidate_id": record_id,
        "source_record_id": record["source_record_id"],
        "title": record["title"],
        "status": "error",
        "error": last_error,
        "elapsed_seconds": round(time.time() - started, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--base-url", default="http://127.0.0.1:8877/v1")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument(
        "--reground-only",
        action="store_true",
        help="Recompute exact quote and native-item provenance from an existing extraction without LLM calls.",
    )
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with args.manifest.open(newline="", encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    if len(records) != 52:
        raise SystemExit(f"Expected 52 canonical profiles, found {len(records)}")
    endpoint = args.base_url.rstrip("/") + "/chat/completions"
    started = dt.datetime.now(dt.timezone.utc)
    existing_path = output / "motivation_extraction" / "motivation_evidence_by_paper.jsonl"
    if args.reground_only:
        if not existing_path.exists():
            raise SystemExit(f"Existing extraction not found: {existing_path}")
        results = [
            json.loads(line)
            for line in existing_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(
                    extract_one,
                    record,
                    output,
                    endpoint,
                    args.model,
                    args.timeout,
                    args.retries,
                ): record["candidate_id"]
                for record in records
            }
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                print(
                    json.dumps(
                        {
                            "record_id": result["candidate_id"],
                            "status": result["status"],
                            "claims": len(result.get("claims") or []),
                            "elapsed_seconds": result.get("elapsed_seconds"),
                        }
                    ),
                    flush=True,
                )
    results.sort(key=lambda x: x["candidate_id"])
    for result in results:
        if result.get("status") != "success":
            continue
        markdown = (ROOT / result["markdown"]).read_text(encoding="utf-8")
        docling = json.loads((ROOT / result["docling_json"]).read_text(encoding="utf-8"))
        for claim in result.get("claims") or []:
            repaired_quote, matched = recover_quote(markdown, str(claim["evidence_quote"]))
            refs, pages = native_provenance(docling, repaired_quote)
            claim["evidence_quote"] = repaired_quote
            claim["quote_verified_in_markdown"] = matched
            claim["doc_item_refs"] = refs
            claim["pages"] = pages
        record_dir = output / "motivation_extraction" / "records" / result["candidate_id"]
        (record_dir / "grounded.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    extraction_dir = output / "motivation_extraction"
    with (extraction_dir / "motivation_evidence_by_paper.jsonl").open("w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
    claims = []
    for result in results:
        for claim in result.get("claims") or []:
            claims.append(
                {
                    "candidate_id": result["candidate_id"],
                    "source_record_id": result["source_record_id"],
                    "title": result["title"],
                    **claim,
                }
            )
    with (extraction_dir / "motivation_evidence_ledger.jsonl").open("w", encoding="utf-8") as f:
        for claim in claims:
            f.write(json.dumps(claim, ensure_ascii=False) + "\n")
    summary = {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "started_utc": started.isoformat(),
        "manifest": str(args.manifest),
        "manifest_sha256": sha256(args.manifest),
        "model": args.model,
        "endpoint": args.base_url,
        "workers": args.workers,
        "records": len(results),
        "successful_records": sum(r["status"] == "success" for r in results),
        "failed_records": sum(r["status"] != "success" for r in results),
        "claims": len(claims),
        "quotes_verified_in_markdown": sum(c["quote_verified_in_markdown"] for c in claims),
        "claims_with_native_item_refs": sum(bool(c["doc_item_refs"]) for c in claims),
    }
    summary_name = "reground_summary.json" if args.reground_only else "run_summary.json"
    summary["reground_only"] = args.reground_only
    (extraction_dir / summary_name).write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if summary["failed_records"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
