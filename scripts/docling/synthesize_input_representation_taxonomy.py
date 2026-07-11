#!/usr/bin/env python3
"""Synthesize and reconcile a taxonomy from open route-discovery outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.docling.docling_graph_litellm_client import (
    LiteLLMEndpointClient,
    strict_json_schema,
)


DEFAULT_OUTPUT = ROOT / "data/input_representation_taxonomy_2026-07-11"


class TaxonomyLeaf(BaseModel):
    leaf_id: str
    name: str
    definition: str
    include_when: list[str] = Field(default_factory=list)
    exclude_when: list[str] = Field(default_factory=list)
    positive_route_refs: list[str] = Field(default_factory=list)
    counterexample_route_refs: list[str] = Field(default_factory=list)


class TaxonomyFamily(BaseModel):
    family_id: str
    name: str
    definition: str
    structural_criterion: str
    leaves: list[TaxonomyLeaf] = Field(default_factory=list)


class TaxonomyDimension(BaseModel):
    dimension_id: str
    name: str
    definition: str
    values: list[str] = Field(default_factory=list)


class TaxonomyProposal(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str
    classification_unit: str
    organizing_principle: str
    families: list[TaxonomyFamily]
    orthogonal_dimensions: list[TaxonomyDimension]
    category_errors_prevented: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def discover_summaries(root: Path) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("**/taxonomy_extraction_summary.json")):
        payload = read_json(path)
        if payload.get("status") != "ok" or payload.get("stage") != "discovery":
            continue
        selected[payload["record_id"]] = payload
    return [selected[key] for key in sorted(selected)]


def route_inventory(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    inventory = []
    for summary in summaries:
        for index, item in enumerate(summary.get("routes") or [], start=1):
            route = item.get("route") or {}
            inventory.append(
                {
                    "route_ref": f"{summary['record_id']}::route_{index:03d}",
                    "record_id": summary["record_id"],
                    "paper_title": summary.get("title"),
                    "grounding_valid": item.get("grounding_valid"),
                    "picture_only_provenance": item.get("picture_only_provenance"),
                    **route,
                    "grounding": {
                        "pages": item.get("pages") or [],
                        "doc_item_refs": item.get("doc_item_refs") or [],
                        "provenance_match": item.get("provenance_match"),
                    },
                }
            )
    return inventory


def synthesis_prompt(inventory: list[dict[str, Any]], schema: dict[str, Any]) -> str:
    return f"""You are developing a scientific taxonomy from an exhaustively extracted corpus.

The unit is one input route: a path from a biological/textual source object through transformations to the form visible to a generative multimodal biological foundation model. Do not classify whole papers with one label. Do not use 'hybrid' as a catch-all. Distinguish actual inputs from training-only targets, generated outputs, baselines, and ablations. Preserve rare but structurally distinct mechanisms.

Independently derive the smallest hierarchy that cleanly explains the grounded routes. The primary hierarchy should describe model-visible representation mechanisms, while biological modality, transformation chain, fusion topology, text role, lifecycle phase, and configuration may remain orthogonal dimensions. Do not adopt familiar categories merely because they are familiar. Every family and leaf must cite route_ref values from the inventory. Unknown or unclear states are not taxonomy categories.

Return JSON conforming to this schema:
{json.dumps(schema, ensure_ascii=False)}

Grounded route inventory:
{json.dumps(inventory, ensure_ascii=False)}
"""


def adjudication_prompt(
    inventory: list[dict[str, Any]], proposals: list[dict[str, Any]], schema: dict[str, Any]
) -> str:
    return f"""Reconcile three independent candidate taxonomies for the same corpus.

Produce one frozen taxonomy. Resolve differences by returning to route-level evidence, not by majority vote alone. Keep a family or leaf when it represents a distinct model-visible mechanism supported by evidence, even if rare. Merge wording variants that use the same structural criterion. Do not use hybrid, unknown, or unclear as categories. Biological source modality is orthogonal unless it changes how the generative model receives the input.

Perform an explicit coverage challenge before finalizing: every grounded actual-input route in the inventory must fit one family and leaf without erasing its model-visible mechanism. In particular, inspect routes that use learned VQ, RVQ, or codebook IDs. Learned quantized IDs are not native tokenizer symbols and are not continuous embeddings; preserve them as a distinct leaf or family when the evidence supports that distinction. Also test whether ordinary text prompts, deterministic biological textualizations, native biological symbol sequences, continuous embeddings, raster/patch inputs, and geometric or noisy generative states remain distinguishable. These are coverage checks, not a required predefined hierarchy.

Return JSON conforming to this schema:
{json.dumps(schema, ensure_ascii=False)}

Route inventory:
{json.dumps(inventory, ensure_ascii=False)}

Independent proposals:
{json.dumps(proposals, ensure_ascii=False)}
"""


def invoke(
    client: LiteLLMEndpointClient, prompt: str, schema: dict[str, Any], retries: int
) -> dict[str, Any]:
    last_error: Exception | None = None
    for _ in range(retries + 1):
        try:
            raw = client.get_json_response(
                prompt,
                json.dumps(schema),
                structured_output=True,
                response_schema_name="input_representation_taxonomy",
            )
            return TaxonomyProposal.model_validate(raw).model_dump(mode="json")
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Taxonomy synthesis failed: {last_error!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["propose", "adjudicate"], required=True)
    parser.add_argument("--discovery-root", type=Path, required=True)
    parser.add_argument("--proposal", action="append", type=Path, default=[])
    parser.add_argument("--replicate-id", default="r1")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT / "taxonomy_synthesis")
    parser.add_argument("--base-url", default="http://127.0.0.1:8765/v1")
    parser.add_argument("--api-key", default="local-codex")
    parser.add_argument("--model", default="openai/gpt-5.4-mini")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    summaries = discover_summaries(args.discovery_root)
    if len(summaries) != 52:
        raise RuntimeError(f"Expected discovery for 52 records, found {len(summaries)}")
    inventory = route_inventory(summaries)
    if not inventory:
        raise RuntimeError("Discovery inventory is empty")
    schema = strict_json_schema(TaxonomyProposal.model_json_schema())
    proposals = [read_json(path) for path in args.proposal]
    if args.mode == "adjudicate" and len(proposals) != 3:
        raise RuntimeError("Adjudication requires exactly three --proposal files")
    prompt = (
        synthesis_prompt(inventory, schema)
        if args.mode == "propose"
        else adjudication_prompt(inventory, proposals, schema)
    )
    run_dir = args.output_dir / (
        f"proposal_{args.replicate_id}" if args.mode == "propose" else "adjudicated_v1"
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    client = LiteLLMEndpointClient(
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        timeout_s=args.timeout,
        max_tokens=None,
        temperature=0.0,
        log_path=run_dir / "llm_calls.jsonl",
    )
    started = time.time()
    result = invoke(client, prompt, schema, args.retries)
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    write_json(run_dir / "schema.json", schema)
    write_json(run_dir / "taxonomy.json", result)
    write_json(
        run_dir / "run_metadata.json",
        {
            "mode": args.mode,
            "replicate_id": args.replicate_id,
            "model": args.model,
            "temperature": 0.0,
            "max_tokens": None,
            "context_limit": None,
            "record_count": len(summaries),
            "route_count": len(inventory),
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "elapsed_seconds": round(time.time() - started, 2),
            "proposal_paths": [str(path) for path in args.proposal],
        },
    )
    write_json(args.output_dir / "open_route_inventory.json", inventory)
    print(json.dumps({"records": len(summaries), "routes": len(inventory), "output": str(run_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
