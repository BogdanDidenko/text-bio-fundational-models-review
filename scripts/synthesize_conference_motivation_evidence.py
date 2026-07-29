#!/usr/bin/env python3
"""Synthesize corpus motivations from the verified 52-paper evidence ledger."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data/health_intelligence_conference_2026_abstract_2026-07-11"

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["corpus_synthesis", "themes", "limitations"],
    "properties": {
        "corpus_synthesis": {"type": "string"},
        "limitations": {"type": "array", "items": {"type": "string"}},
        "themes": {
            "type": "array",
            "minItems": 3,
            "maxItems": 6,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "theme_id",
                    "label",
                    "synthesis",
                    "role_of_text",
                    "role_of_multimodality",
                    "supporting_claim_ids",
                ],
                "properties": {
                    "theme_id": {"type": "string"},
                    "label": {"type": "string"},
                    "synthesis": {"type": "string"},
                    "role_of_text": {"type": "string"},
                    "role_of_multimodality": {"type": "string"},
                    "supporting_claim_ids": {
                        "type": "array",
                        "minItems": 2,
                        "items": {"type": "string"},
                    },
                },
            },
        },
    },
}


def post_json(url: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"content-type": "application/json", "authorization": "Bearer local"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--base-url", default="http://127.0.0.1:8877/v1")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    output = args.output_dir.resolve()
    extraction = output / "motivation_extraction"
    ledger_path = extraction / "motivation_evidence_ledger.jsonl"
    claims = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    verified = [c for c in claims if c.get("quote_verified_in_markdown")]
    if not verified:
        raise SystemExit("No verified claims found")
    compact = [
        {
            "claim_id": c["claim_id"],
            "record_id": c["candidate_id"],
            "title": c["title"],
            "theme_label": c["theme_label"],
            "claim_summary": c["claim_summary"],
            "limitation_addressed": c["limitation_addressed"],
            "why_text": c["why_text"],
            "why_multimodal": c["why_multimodal"],
            "claimed_capability": c["claimed_capability"],
            "evidence_quote": c["evidence_quote"],
            "section_heading": c["section_heading"],
        }
        for c in verified
    ]
    prompt = f"""Synthesize author-stated motivations across a corpus of 52 papers on generative multimodal biological foundation models in which text is a modality.

Derive three to six themes from the evidence below. Do not begin from a predefined motivation taxonomy. Explain the distinct role of text and the distinct role of biological multimodality where the evidence supports them. Use only supplied claim IDs as support. A theme may cite multiple claims from one paper, but prefer support across papers. Do not convert our review-level intuitions into author claims. Be concise enough to inform a one-page conference abstract.

VERIFIED CLAIM LEDGER
{json.dumps(compact, ensure_ascii=False)}
"""
    synthesis_dir = output / "motivation_synthesis"
    synthesis_dir.mkdir(parents=True, exist_ok=True)
    (synthesis_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "MotivationSynthesisDocument", "schema": SCHEMA},
        },
    }
    raw = post_json(args.base_url.rstrip("/") + "/chat/completions", payload, args.timeout)
    content = raw["choices"][0]["message"]["content"]
    (synthesis_dir / "response.txt").write_text(content, encoding="utf-8")
    parsed = json.loads(content)
    claim_by_id = {c["claim_id"]: c for c in verified}
    for theme in parsed["themes"]:
        requested = list(dict.fromkeys(theme["supporting_claim_ids"]))
        unknown = sorted(set(requested) - set(claim_by_id))
        if unknown:
            raise ValueError(f"Unknown claim IDs in {theme['theme_id']}: {unknown}")
        records = sorted({claim_by_id[cid]["candidate_id"] for cid in requested})
        theme["supporting_claim_ids"] = requested
        theme["supporting_record_ids"] = records
        theme["supporting_record_count"] = len(records)
    parsed["run_metadata"] = {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "model": args.model,
        "endpoint": args.base_url,
        "verified_claim_count": len(verified),
        "records_with_verified_claims": len({c["candidate_id"] for c in verified}),
    }
    (synthesis_dir / "motivation_synthesis.json").write_text(
        json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = ["# Corpus-grounded motivation synthesis", "", parsed["corpus_synthesis"], ""]
    for theme in parsed["themes"]:
        lines.extend(
            [
                f"## {theme['label']}",
                "",
                theme["synthesis"],
                "",
                f"- Role of text: {theme['role_of_text']}",
                f"- Role of multimodality: {theme['role_of_multimodality']}",
                f"- Supporting records: {theme['supporting_record_count']}",
                f"- Claim IDs: {', '.join(theme['supporting_claim_ids'])}",
                "",
            ]
        )
    lines.extend(["## Limitations", ""] + [f"- {x}" for x in parsed["limitations"]])
    (synthesis_dir / "motivation_synthesis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(parsed["run_metadata"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
