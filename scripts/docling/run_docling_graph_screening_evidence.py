#!/usr/bin/env python3
"""Run Docling Graph screening-evidence extraction on existing Docling JSON files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

from docling_graph import PipelineConfig, run_pipeline

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.docling.docling_graph_grounding import build_section_grounding, find_provenance
from scripts.docling.docling_graph_litellm_client import LiteLLMEndpointClient
from scripts.docling_graph_templates.biomedical_screening_evidence import (
    BiomedicalScreeningEvidence,
)


DEFAULT_INCLUDE = REPO / "data/docling_include_final_coverage_2026-07-09/final_docling_manifest.csv"
DEFAULT_UNCERTAIN = REPO / "data/docling_uncertain_final_coverage_2026-07-09/final_docling_manifest.csv"
DEFAULT_CANONICAL = (
    REPO
    / "data/docling_include_vlm_52_2026-07-10_nolimits/manifests"
    / "canonical_docling_profile_manifest.csv"
)
DEFAULT_OUT = REPO / "data/docling_graph_screening_evidence_2026-07-09"


def rel(path: Path | str | None) -> str:
    if not path:
        return ""
    value = Path(path)
    if not value.is_absolute():
        value = REPO / value
    try:
        return str(value.relative_to(REPO))
    except ValueError:
        return str(value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_manifest(path: Path, corpus: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("final_docling_status") != "docling_ok":
                continue
            rows.append({**row, "source_corpus": corpus})
    return rows


def read_canonical_manifest(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("profile_status") != "complete":
                continue
            rows.append(
                {
                    **row,
                    "record_id": row.get("source_record_id", ""),
                    "source_corpus": "canonical_vlm_include",
                }
            )
    return rows


def load_records(
    include_manifest: Path,
    uncertain_manifest: Path,
    canonical_manifest: Path | None,
    limit: int,
    sample_size: int,
    sample_seed: int,
    shard_index: int,
    shard_count: int,
) -> list[dict[str, str]]:
    if canonical_manifest is not None:
        rows = read_canonical_manifest(canonical_manifest)
    else:
        rows = [
            *read_manifest(include_manifest, "include"),
            *read_manifest(uncertain_manifest, "uncertain"),
        ]
    if sample_size:
        rng = random.Random(sample_seed)
        rows = rng.sample(rows, min(sample_size, len(rows)))
    if limit:
        rows = rows[:limit]
    if shard_count > 1:
        rows = rows[shard_index::shard_count]
    return rows


def safe_name(row: dict[str, str]) -> str:
    candidate = str(row.get("candidate_id") or row.get("record_id") or "")
    if not candidate:
        raise ValueError("Graph record has no candidate_id or record_id")
    readable = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in candidate)[:120]
    return f"{readable}_{hashlib.sha256(candidate.encode('utf-8')).hexdigest()[:12]}"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def source_markdown_chars(row: dict[str, str]) -> int | None:
    markdown = row.get("markdown")
    if not markdown:
        return None
    path = Path(markdown)
    if not path.is_absolute():
        path = REPO / path
    if not path.exists():
        return None
    return len(path.read_text(encoding="utf-8"))


def graph_summary(context: Any) -> dict[str, Any]:
    graph = context.knowledge_graph
    nodes = []
    for node_id, data in graph.nodes(data=True):
        row = {"node_id": str(node_id), **dict(data)}
        nodes.append(row)
    edges = []
    for source, target, data in graph.edges(data=True):
        edges.append({"source": str(source), "target": str(target), **dict(data)})
    return {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "nodes": nodes,
        "edges": edges,
    }


def run_one(row: dict[str, str], args: argparse.Namespace, client: LiteLLMEndpointClient) -> dict[str, Any]:
    source = REPO / row["docling_json"]
    markdown_path = Path(row["markdown"])
    if not markdown_path.is_absolute():
        markdown_path = REPO / markdown_path
    record_out = args.output_dir / safe_name(row)
    started = time.time()
    generation: dict[str, Any] = {"temperature": args.temperature}
    llm_overrides: dict[str, Any] = {
        "generation": generation,
        "reliability": {"timeout_s": args.timeout},
    }
    if args.context_limit is not None:
        llm_overrides["context_limit"] = args.context_limit
    if args.max_tokens is not None:
        generation["max_tokens"] = args.max_tokens
        llm_overrides["max_output_tokens"] = args.max_tokens
    config = PipelineConfig(
        source=str(source),
        template=BiomedicalScreeningEvidence,
        backend="llm",
        llm_client=client,
        structured_output=args.structured_output,
        processing_mode="many-to-one",
        extraction_contract=args.extraction_contract,
        use_chunking=True,
        chunk_max_tokens=args.chunk_max_tokens,
        dense_skeleton_batch_tokens=args.dense_skeleton_batch_tokens,
        dense_fill_nodes_cap=args.dense_fill_nodes_cap,
        dense_fill_context=args.dense_fill_context,
        dense_dedupe=args.dense_dedupe,
        parallel_workers=args.parallel_workers,
        provenance=args.provenance,
        debug=args.debug,
        dump_to_disk=True,
        output_dir=str(record_out),
        llm_overrides=llm_overrides,
    )
    context = run_pipeline(config)
    elapsed = round(time.time() - started, 2)
    models = [
        model.model_dump(mode="json") if hasattr(model, "model_dump") else repr(model)
        for model in (context.extracted_models or [])
    ]
    provenance_path = find_provenance(context)
    provenance = None
    if provenance_path and provenance_path.exists():
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    section_grounding = build_section_grounding(row, models, context, provenance)
    summary = {
        "record_id": row.get("record_id"),
        "candidate_id": row.get("candidate_id"),
        "source_corpus": row.get("source_corpus"),
        "title": row.get("title"),
        "doi": row.get("doi"),
        "source_docling_json": rel(source),
        "source_docling_sha256": sha256_file(source),
        "source_markdown": rel(row.get("markdown")),
        "source_markdown_sha256": sha256_file(markdown_path),
        "source_markdown_chars": source_markdown_chars(row),
        "output_dir": rel(record_out),
        "elapsed_seconds": elapsed,
        "extraction_contract": args.extraction_contract,
        "llm_execution": {
            "client": client.__class__.__name__,
            "model": args.model,
            "base_url": args.base_url,
            "temperature": args.temperature,
            "structured_output": args.structured_output,
            "max_tokens": args.max_tokens,
            "context_limit": args.context_limit,
            "timeout_seconds": args.timeout,
        },
        "models": models,
        "section_grounding": section_grounding,
        "graph": graph_summary(context),
        "provenance_path": rel(provenance_path) if provenance_path else "",
        "provenance_bind_stats": (provenance or {}).get("bind_stats", {}),
        "provenance_resolution": (provenance or {}).get("resolution"),
    }
    write_json(record_out / "screening_evidence_summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-manifest", type=Path, default=DEFAULT_INCLUDE)
    parser.add_argument("--uncertain-manifest", type=Path, default=DEFAULT_UNCERTAIN)
    parser.add_argument(
        "--canonical-manifest",
        type=Path,
        default=None,
        help=(
            "Use a canonical VLM profile manifest instead of the historical "
            "include/uncertain manifests."
        ),
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--sample-size", type=int, default=0)
    parser.add_argument("--sample-seed", type=int, default=20260709)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765/v1")
    parser.add_argument("--api-key", default="local-codex")
    parser.add_argument("--model", default="openai/gpt-5.4-mini")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--context-limit", type=int, default=None)
    parser.add_argument(
        "--structured-output",
        action="store_true",
        help=(
            "Try API-level JSON schema. Default is off because Codex strict schemas "
            "reject some Docling Graph generated schemas."
        ),
    )
    parser.add_argument("--extraction-contract", choices=["direct", "dense", "auto"], default="direct")
    parser.add_argument("--provenance", choices=["off", "standard", "detailed"], default="detailed")
    parser.add_argument("--chunk-max-tokens", type=int, default=768)
    parser.add_argument("--dense-skeleton-batch-tokens", type=int, default=1536)
    parser.add_argument("--dense-fill-nodes-cap", type=int, default=4)
    parser.add_argument("--dense-fill-context", choices=["scoped", "full"], default="scoped")
    parser.add_argument("--dense-dedupe", choices=["off", "standard", "aggressive"], default="standard")
    parser.add_argument("--parallel-workers", type=int, default=1)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.shard_count < 1:
        parser.error("--shard-count must be >= 1")
    if args.shard_index < 0 or args.shard_index >= args.shard_count:
        parser.error("--shard-index must satisfy 0 <= shard-index < shard-count")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_records(
        args.include_manifest,
        args.uncertain_manifest,
        args.canonical_manifest,
        args.limit,
        args.sample_size,
        args.sample_seed,
        args.shard_index,
        args.shard_count,
    )
    candidate_ids = [str(row.get("candidate_id") or row.get("record_id") or "") for row in rows]
    if not all(candidate_ids) or len(set(candidate_ids)) != len(candidate_ids):
        raise RuntimeError("Selected Graph records must have unique nonempty candidate_id values")
    write_json(
        args.output_dir / "selected_records.json",
        [
            {
                "record_id": row.get("record_id"),
                "candidate_id": row.get("candidate_id"),
                "source_corpus": row.get("source_corpus"),
                "title": row.get("title"),
                "doi": row.get("doi"),
                "docling_json": row.get("docling_json"),
                "markdown": row.get("markdown"),
                "source_markdown_chars": source_markdown_chars(row),
            }
            for row in rows
        ],
    )
    client = LiteLLMEndpointClient(
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        timeout_s=args.timeout,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )
    summaries = []
    for row in rows:
        print(f"Docling Graph evidence: {row.get('record_id')} {row.get('title')}", flush=True)
        summaries.append(run_one(row, args, client))
    write_json(args.output_dir / "run_summary.json", summaries)
    print(json.dumps({
        "records": len(summaries),
        "output_dir": rel(args.output_dir),
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
