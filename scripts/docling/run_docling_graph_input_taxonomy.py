#!/usr/bin/env python3
"""Run evidence-grounded input-route extraction on canonical Docling profiles."""

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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.docling.docling_graph_litellm_client import LiteLLMEndpointClient
from scripts.docling_graph_templates.input_representation_taxonomy import (
    InputRouteDiscoveryDocument,
    TaxonomyCodedDocument,
)


DEFAULT_MANIFEST = (
    ROOT
    / "data/docling_include_vlm_52_2026-07-10_nolimits/manifests"
    / "canonical_docling_profile_manifest.csv"
)
DEFAULT_OUTPUT = ROOT / "data/input_representation_taxonomy_2026-07-11"


def resolve(path: str | Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def rel(path: str | Path | None) -> str:
    if not path:
        return ""
    value = resolve(path)
    try:
        return str(value.relative_to(ROOT))
    except ValueError:
        return str(value)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream) if row.get("profile_status") == "complete"]
    if len(rows) != 52:
        raise RuntimeError(f"Expected 52 complete canonical profiles, found {len(rows)}")
    return rows


def select_rows(rows: list[dict[str, str]], args: argparse.Namespace) -> list[dict[str, str]]:
    selected = list(rows)
    if args.record_id:
        requested = set(args.record_id)
        selected = [row for row in selected if row["candidate_id"] in requested]
        missing = requested - {row["candidate_id"] for row in selected}
        if missing:
            raise RuntimeError(f"Unknown record IDs: {sorted(missing)}")
    if args.sample_size:
        selected = random.Random(args.sample_seed).sample(
            selected, min(args.sample_size, len(selected))
        )
    if args.limit:
        selected = selected[: args.limit]
    if args.shard_count > 1:
        selected = selected[args.shard_index :: args.shard_count]
    return selected


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value)[:160]


def graph_payload(context: Any) -> dict[str, Any]:
    nodes = []
    for node_id, attrs in context.knowledge_graph.nodes(data=True):
        nodes.append({"node_id": str(node_id), **dict(attrs)})
    edges = [
        {"source": str(source), "target": str(target), **dict(attrs)}
        for source, target, attrs in context.knowledge_graph.edges(data=True)
    ]
    return {"node_count": len(nodes), "edge_count": len(edges), "nodes": nodes, "edges": edges}


def extracted_models(context: Any) -> list[dict[str, Any]]:
    return [
        value.model_dump(mode="json") if hasattr(value, "model_dump") else dict(value)
        for value in (context.extracted_models or [])
    ]


def normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())


def normalize_verbatim(value: str) -> str:
    return "".join(char for char in value.casefold() if char.isalnum())


FAMILY_SUBTYPES = {
    "text_native_token_stream": {
        "plain_language_prompt_or_question",
        "structured_biological_prompt_or_task_scaffold",
        "serialized_biological_context_or_ordered_profile",
    },
    "discrete_biological_symbol_stream": {
        "native_biological_token_stream",
        "multi_track_structural_symbol_stream",
        "learned_quantized_id_or_codebook_token",
    },
    "dense_continuous_carrier": {
        "direct_projected_embedding",
        "virtual_token_prefix",
        "connector_mediated_embedding",
        "pooled_or_aggregated_embedding",
    },
    "visual_raster_carrier": {
        "raw_slide_or_patch_input",
        "patch_context_or_case_level_visual_reasoning",
    },
    "geometric_or_diffusion_state_carrier": {
        "noisy_diffusion_state",
        "coordinate_backbone_or_shape_conditioning",
        "symbolic_structural_constraint",
    },
    "other_evidence_grounded": {"other_evidence_grounded"},
}


def route_evidence(graph: dict[str, Any], markdown: str) -> list[dict[str, Any]]:
    routes = []
    route_classes = {"InputRouteDiscovery", "TaxonomyCodedRoute"}
    normalized_markdown = normalize_text(markdown)
    verbatim_markdown = normalize_verbatim(markdown)
    for node in graph["nodes"]:
        if node.get("__class__") not in route_classes:
            continue
        provenance = node.get("__provenance__") or {}
        quote = str(node.get("evidence_quote") or "")
        refs = [str(value) for value in provenance.get("refs") or []]
        ref_kinds = sorted(
            {
                ref.split("/", 2)[1]
                for ref in refs
                if ref.startswith("#/") and len(ref.split("/", 2)) >= 2
            }
        )
        quote_verified = bool(
            quote
            and (
                normalize_text(quote) in normalized_markdown
                or normalize_verbatim(quote) in verbatim_markdown
            )
        )
        family = node.get("carrier_family")
        subtype = node.get("carrier_subtype")
        taxonomy_consistent = (
            True
            if not family and not subtype
            else bool(family in FAMILY_SUBTYPES and subtype in FAMILY_SUBTYPES[family])
        )
        input_status = node.get("input_status") or node.get("input_status_verbatim") or ""
        accepted_input_candidate = input_status in {
            "actual_model_input",
            "paired_alignment_input",
            "actual model input",
            "paired alignment input",
        }
        routes.append(
            {
                "graph_node_id": node.get("node_id"),
                "route_label": node.get("route_label"),
                "model_name": node.get("model_name"),
                "evidence_quote": quote,
                "section_heading": node.get("section_heading"),
                "pages": provenance.get("pages") or [],
                "doc_item_refs": refs,
                "provenance_match": provenance.get("match"),
                "provenance_spans": provenance.get("spans") or [],
                "provenance_ref_kinds": ref_kinds,
                "quote_verified_in_canonical_markdown": quote_verified,
                "picture_only_provenance": bool(ref_kinds and set(ref_kinds) <= {"pictures"}),
                "grounding_valid": bool(quote_verified and refs and provenance.get("match")),
                "taxonomy_consistent": taxonomy_consistent,
                "accepted_input_candidate": accepted_input_candidate,
                "route": {
                    key: value
                    for key, value in node.items()
                    if key not in {"node_id", "__provenance__", "label", "type", "__class__"}
                },
            }
        )
    return routes


def find_provenance(context: Any) -> Path | None:
    manager = getattr(context, "output_manager", None)
    if manager is None:
        return None
    candidates = [
        manager.get_docling_graph_dir() / "provenance.json",
        manager.get_debug_dir() / "dense_provenance.json",
    ]
    return next((path for path in candidates if path.exists()), None)


def run_record(
    row: dict[str, str], args: argparse.Namespace, client: LiteLLMEndpointClient
) -> dict[str, Any]:
    template = InputRouteDiscoveryDocument if args.stage == "discovery" else TaxonomyCodedDocument
    source = resolve(row["docling_json"])
    markdown_path = resolve(row["markdown"])
    markdown = markdown_path.read_text(encoding="utf-8")
    record_output = args.output_dir / "records" / safe_name(row["candidate_id"])
    generation: dict[str, Any] = {"temperature": args.temperature}
    overrides: dict[str, Any] = {
        "generation": generation,
        "reliability": {"timeout_s": args.timeout},
    }
    if args.max_tokens is not None:
        generation["max_tokens"] = args.max_tokens
        overrides["max_output_tokens"] = args.max_tokens
    if args.context_limit is not None:
        overrides["context_limit"] = args.context_limit

    config = PipelineConfig(
        source=str(source),
        template=template,
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
        provenance="detailed",
        debug=True,
        dump_to_disk=True,
        output_dir=str(record_output),
        llm_overrides=overrides,
    )
    started = time.time()
    context = run_pipeline(config)
    graph = graph_payload(context)
    routes = route_evidence(graph, markdown)
    provenance_path = find_provenance(context)
    summary = {
        "status": "ok",
        "stage": args.stage,
        "taxonomy_version": "open-discovery-v1"
        if args.stage == "discovery"
        else "input-representation-taxonomy-v1",
        "replicate_id": args.replicate_id,
        "record_id": row["candidate_id"],
        "source_record_id": row.get("source_record_id", ""),
        "title": row.get("title", ""),
        "doi": row.get("doi", ""),
        "source_docling_json": rel(source),
        "source_docling_sha256": sha256(source),
        "source_markdown": rel(markdown_path),
        "source_markdown_sha256": hashlib.sha256(markdown.encode()).hexdigest(),
        "source_markdown_chars": len(markdown),
        "output_dir": rel(record_output),
        "elapsed_seconds": round(time.time() - started, 2),
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
        "extracted_models": extracted_models(context),
        "routes": routes,
        "route_count": len(routes),
        "grounded_route_count": sum(route["grounding_valid"] for route in routes),
        "unverified_route_count": sum(not route["grounding_valid"] for route in routes),
        "picture_only_route_count": sum(route["picture_only_provenance"] for route in routes),
        "taxonomy_inconsistent_route_count": sum(
            not route["taxonomy_consistent"] for route in routes
        ),
        "graph": graph,
        "provenance_path": rel(provenance_path),
    }
    write_json(record_output / "taxonomy_extraction_summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["discovery", "coded"], required=True)
    parser.add_argument("--canonical-manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT / "runs" / "smoke")
    parser.add_argument("--replicate-id", default="r1")
    parser.add_argument("--record-id", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sample-size", type=int, default=0)
    parser.add_argument("--sample-seed", type=int, default=20260711)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765/v1")
    parser.add_argument("--api-key", default="local-codex")
    parser.add_argument("--model", default="openai/gpt-5.4-mini")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--context-limit", type=int, default=None)
    parser.add_argument("--structured-output", action="store_true")
    parser.add_argument("--extraction-contract", choices=["direct", "dense"], default="direct")
    parser.add_argument("--chunk-max-tokens", type=int, default=768)
    parser.add_argument("--dense-skeleton-batch-tokens", type=int, default=1536)
    parser.add_argument("--dense-fill-nodes-cap", type=int, default=4)
    parser.add_argument("--dense-fill-context", choices=["scoped", "full"], default="scoped")
    parser.add_argument("--dense-dedupe", choices=["off", "standard", "aggressive"], default="standard")
    parser.add_argument("--parallel-workers", type=int, default=1)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    if args.shard_count < 1 or not 0 <= args.shard_index < args.shard_count:
        parser.error("shard index/count are inconsistent")
    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = select_rows(load_manifest(args.canonical_manifest), args)
    write_json(args.output_dir / "selected_records.json", rows)
    write_json(
        args.output_dir / "run_config.json",
        {
            "stage": args.stage,
            "replicate_id": args.replicate_id,
            "record_count": len(rows),
            "model": args.model,
            "base_url": args.base_url,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "context_limit": args.context_limit,
            "extraction_contract": args.extraction_contract,
            "provenance": "detailed",
            "debug": True,
            "structured_output": args.structured_output,
            "chunk_max_tokens": args.chunk_max_tokens,
            "dense_skeleton_batch_tokens": args.dense_skeleton_batch_tokens,
            "dense_fill_nodes_cap": args.dense_fill_nodes_cap,
            "dense_fill_context": args.dense_fill_context,
            "dense_dedupe": args.dense_dedupe,
            "parallel_workers": args.parallel_workers,
            "shard_index": args.shard_index,
            "shard_count": args.shard_count,
        },
    )
    template = InputRouteDiscoveryDocument if args.stage == "discovery" else TaxonomyCodedDocument
    write_json(args.output_dir / "schema.json", template.model_json_schema())
    client = LiteLLMEndpointClient(
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        timeout_s=args.timeout,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        log_path=args.output_dir / "llm_calls.jsonl",
    )
    summaries: list[dict[str, Any]] = []
    event_log = args.output_dir / "events.jsonl"
    for row in rows:
        last_error = ""
        for attempt in range(1, args.retries + 2):
            append_jsonl(event_log, {"event": "start", "record_id": row["candidate_id"], "attempt": attempt})
            print(f"[{args.stage}] {row['candidate_id']} attempt={attempt}", flush=True)
            try:
                summary = run_record(row, args, client)
                summaries.append(summary)
                append_jsonl(
                    event_log,
                    {
                        "event": "complete",
                        "record_id": row["candidate_id"],
                        "attempt": attempt,
                        "route_count": summary["route_count"],
                        "elapsed_seconds": summary["elapsed_seconds"],
                    },
                )
                break
            except Exception as exc:
                last_error = repr(exc)
                append_jsonl(
                    event_log,
                    {"event": "error", "record_id": row["candidate_id"], "attempt": attempt, "error": last_error},
                )
        else:
            summaries.append(
                {
                    "status": "error",
                    "stage": args.stage,
                    "replicate_id": args.replicate_id,
                    "record_id": row["candidate_id"],
                    "title": row.get("title", ""),
                    "error": last_error,
                }
            )
    write_json(args.output_dir / "run_summary.json", summaries)
    ok = sum(row.get("status") == "ok" for row in summaries)
    print(json.dumps({"selected": len(rows), "ok": ok, "errors": len(rows) - ok, "output": rel(args.output_dir)}))
    return 0 if ok == len(rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
