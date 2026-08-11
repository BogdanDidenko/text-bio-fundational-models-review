#!/usr/bin/env python3
"""Create a signed skeleton for a provider-mediated Google Scholar capture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reproduce_search import query_signature


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--pagination-policy", required=True)
    parser.add_argument("--locale", default="en")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    metadata = config["metadata"]
    scholar = config["databases"]["google_scholar"]
    acquisition = {
        "provider": args.provider,
        "locale": args.locale,
        "pagination_policy": args.pagination_policy,
    }
    bundle = {
        "queries": scholar["queries"],
        "year_range": scholar["year_range"],
        "date_from": metadata["date_from"],
        "date_to": metadata["date_to"],
        "acquisition": acquisition,
    }
    payload = {
        "schema_version": 1,
        "query_bundle": bundle,
        "query_signature": query_signature(
            bundle["queries"],
            bundle["year_range"],
            bundle["date_from"],
            bundle["date_to"],
            bundle["acquisition"],
        ),
        "raw_response_manifest": [],
        "query_execution": [
            {
                "query_id": f"gs_q{index}",
                "execution_complete": False,
                "retrieval_complete": False,
                "termination": "not_started",
                "pages_retrieved": 0,
                "records_retrieved": 0,
                "source_exhaustive": "unknown",
            }
            for index in range(1, len(scholar["queries"]) + 1)
        ],
        "records": [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "query_signature": payload["query_signature"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
