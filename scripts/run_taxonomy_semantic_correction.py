#!/usr/bin/env python3
"""Apply a narrow, taxonomy-aware correction to routes flagged by the F6 audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import signal
import shutil
import subprocess
import tempfile
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TAXONOMY_ROOT = (
    ROOT
    / "data/living_catalog/taxonomy_rerun_preflight_2026-08-12"
    / "taxonomy_derived_correction_2026-08-16"
)
DEFAULT_F6_ROOT = ROOT / "analysis/taxonomy_semantic_sufficiency_audit_2026-08-17"
DEFAULT_OUTPUT = ROOT / "analysis/taxonomy_semantic_correction_2026-08-17"
DEFAULT_MODEL = "gpt-5.4-mini"

EDITABLE_FIELDS = [
    "route_label",
    "lifecycle_phase",
    "task_or_configuration_verbatim",
    "source_object_verbatim",
    "source_object_normalized",
    "source_modality_normalized",
    "transformation_chain_verbatim",
    "transformation_chain_normalized",
    "model_visible_form_verbatim",
    "carrier_family",
    "carrier_subtype",
    "insertion_or_fusion_verbatim",
    "fusion_topology",
    "text_role",
    "input_status",
    "evidence_quote",
    "section_heading",
    "supporting_figure_or_table",
    "evidence_status",
    "uncertainty",
]

FAMILIES = [
    "dense_continuous_carrier",
    "discrete_biological_symbol_stream",
    "geometric_or_diffusion_state_carrier",
    "text_native_token_stream",
    "visual_raster_carrier",
]
SUBTYPES = [
    "connector_mediated_embedding",
    "coordinate_backbone_or_shape_conditioning",
    "direct_projected_embedding",
    "learned_quantized_id_or_codebook_token",
    "multi_track_structural_symbol_stream",
    "native_biological_token_stream",
    "noisy_diffusion_state",
    "patch_context_or_case_level_visual_reasoning",
    "plain_language_prompt_or_question",
    "pooled_or_aggregated_embedding",
    "raw_slide_or_patch_input",
    "serialized_biological_context_or_ordered_profile",
    "structured_biological_prompt_or_task_scaffold",
    "symbolic_structural_constraint",
    "virtual_token_prefix",
]
FUSION = [
    "concatenation",
    "cross_attention",
    "encoder_decoder",
    "interleaving",
    "other_explicit",
    "placeholder_replacement",
    "prefix",
    "query_bottleneck",
    "retrieval_or_tool_context",
    "shared_latent_alignment",
    "side_or_generative_conditioning",
    "tokenizer_sequence",
    "unclear",
]
TEXT_ROLES = [
    "biological_payload",
    "generated_output",
    "instruction_or_query",
    "metadata_or_context",
    "modality_or_task_selector",
    "no_text_on_this_route",
    "paired_alignment_supervision",
    "semantic_annotation",
]
LIFECYCLE = ["evaluation", "fine_tuning", "inference", "pretraining", "unclear"]
INPUT_STATUS = ["actual_model_input", "paired_alignment_input"]
EVIDENCE_STATUS = ["explicit_text", "inferred", "text_plus_figure"]


def corrected_route_schema() -> dict[str, Any]:
    string = {"type": "string"}
    nullable_string = {"type": ["string", "null"]}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": EDITABLE_FIELDS,
        "properties": {
            "route_label": string,
            "lifecycle_phase": {"type": "string", "enum": LIFECYCLE},
            "task_or_configuration_verbatim": string,
            "source_object_verbatim": string,
            "source_object_normalized": string,
            "source_modality_normalized": string,
            "transformation_chain_verbatim": {"type": "array", "items": string},
            "transformation_chain_normalized": {"type": "array", "items": string},
            "model_visible_form_verbatim": string,
            "carrier_family": {"type": "string", "enum": FAMILIES},
            "carrier_subtype": {"type": "string", "enum": SUBTYPES},
            "insertion_or_fusion_verbatim": string,
            "fusion_topology": {"type": "string", "enum": FUSION},
            "text_role": {"type": "string", "enum": TEXT_ROLES},
            "input_status": {"type": "string", "enum": INPUT_STATUS},
            "evidence_quote": string,
            "section_heading": string,
            "supporting_figure_or_table": nullable_string,
            "evidence_status": {"type": "string", "enum": EVIDENCE_STATUS},
            "uncertainty": nullable_string,
        },
    }


DECISION_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["reviewer_role", "decisions"],
    "properties": {
        "reviewer_role": {"type": "string"},
        "decisions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "route_id",
                    "decision",
                    "corrected_route",
                    "changed_fields",
                    "supporting_quotes",
                    "rationale",
                    "confidence",
                ],
                "properties": {
                    "route_id": {"type": "string"},
                    "decision": {
                        "type": "string",
                        "enum": ["retain_as_is", "revise_fields", "remove_route"],
                    },
                    "corrected_route": corrected_route_schema(),
                    "changed_fields": {
                        "type": "array",
                        "items": {"type": "string", "enum": EDITABLE_FIELDS},
                    },
                    "supporting_quotes": {"type": "array", "items": {"type": "string"}},
                    "rationale": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                },
            },
        },
    },
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize(value: str) -> str:
    value = " ".join(html.unescape(value).split())
    value = re.sub(r"\s+([.,;:!?])", r"\1", value)
    return value.casefold().strip("\"'“”‘’ ")


def editable_view(route: dict[str, Any]) -> dict[str, Any]:
    return {field: route.get(field) for field in EDITABLE_FIELDS}


def build_manifest(
    taxonomy_root: Path,
    f6_root: Path,
    output: Path,
    max_routes_per_call: int,
) -> list[dict[str, Any]]:
    routes = {row["route_id"]: row for row in read_jsonl(taxonomy_root / "route_annotations.jsonl")}
    dispositions = read_jsonl(f6_root / "semantic_sufficiency_dispositions.jsonl")
    f6_manifest = {row["record_id"]: row for row in read_json(f6_root / "audit_manifest.json")}
    flagged = [
        row
        for row in dispositions
        if row["final_review"]["recommended_action"] != "retain_as_is"
    ]
    by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in flagged:
        route = routes[row["route_id"]]
        by_record[route["record_id"]].append(
            {
                "current_route": route,
                "semantic_reviewer": row["reviewer_comparison"]["semantic_reviewer"],
                "adversarial_reviewer": row["reviewer_comparison"]["adversarial_reviewer"],
                "f6_adjudicator": row["final_review"],
            }
        )
    manifest = []
    selected_run_routes: dict[str, set[str]] = {}
    for selected_path in sorted((output / "runs").glob("*/selected_response.json")):
        response = read_json(selected_path)
        selected_run_routes[selected_path.parent.name] = {
            str(decision["route_id"]) for decision in response.get("decisions") or []
        }

    for record_id, items in sorted(by_record.items()):
        source = f6_manifest[record_id]
        markdown = Path(source["canonical_markdown_local_path"])
        if not markdown.is_file() or sha256(markdown) != source["canonical_markdown_sha256"]:
            raise RuntimeError(f"Canonical Markdown unavailable or changed: {record_id}")
        items = sorted(items, key=lambda item: item["current_route"]["route_id"])
        item_by_id = {item["current_route"]["route_id"]: item for item in items}
        covered: set[str] = set()
        run_chunks: list[tuple[str, list[dict[str, Any]]]] = []
        for run_key, route_ids in sorted(selected_run_routes.items()):
            matching = sorted(route_ids & set(item_by_id))
            if not matching:
                continue
            if covered & set(matching):
                raise RuntimeError(f"Duplicate selected correction routes for {record_id}")
            covered.update(matching)
            run_chunks.append((run_key, [item_by_id[route_id] for route_id in matching]))
        remaining = [item for item in items if item["current_route"]["route_id"] not in covered]
        for start in range(0, len(remaining), max_routes_per_call):
            chunk = remaining[start : start + max_routes_per_call]
            route_suffix = "_".join(
                item["current_route"]["route_id"].removeprefix("route_") for item in chunk
            )
            run_chunks.append((f"{record_id}__routes_{route_suffix}", chunk))
        for run_key, chunk in run_chunks:
            manifest.append(
                {
                    "run_key": run_key,
                    "record_id": record_id,
                    "title": source["title"],
                    "canonical_markdown_local_path": str(markdown),
                    "canonical_markdown_sha256": source["canonical_markdown_sha256"],
                    "routes": chunk,
                }
            )
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "correction_manifest.json", manifest)
    write_json(
        output / "correction_population.json",
        {
            "created_at": utc_now(),
            "taxonomy_root": str(taxonomy_root),
            "taxonomy_sha256": sha256(taxonomy_root / "route_annotations.jsonl"),
            "f6_root": str(f6_root),
            "f6_dispositions_sha256": sha256(f6_root / "semantic_sufficiency_dispositions.jsonl"),
            "records": len(by_record),
            "run_units": len(manifest),
            "reused_selected_run_units": sum(
                (output / "runs" / record["run_key"] / "selected_response.json").is_file()
                for record in manifest
            ),
            "max_routes_per_call": max_routes_per_call,
            "routes": len(flagged),
            "selection_rule": "F6 final action != retain_as_is",
            "unchanged_routes_outside_population": len(routes) - len(flagged),
            "text_policy": "complete canonical Docling Markdown; no truncation",
        },
    )
    return manifest


def prompt(record: dict[str, Any], codebook: str, document: str) -> str:
    return f"""You are the final taxonomy-aware correction reviewer for a biomedical evidence map.

Review only the listed routes against the COMPLETE canonical paper. The prior reviews were produced by a stricter audit whose rubric sometimes incorrectly required the paper to use our analytical taxonomy labels verbatim. Correct that error here.

Rules:
- A normalized carrier family, subtype, fusion topology, text role, or source-modality label is analyst coding. It is supported when the paper explicitly describes the underlying mechanism and the frozen codebook maps that mechanism to the label; the paper need not print the label itself.
- By contrast, the existence of the route, actual source object, named model, lifecycle phase, task/configuration, and actual-input status must be established for that model/configuration. A benchmark label, output, target, downstream consumer, baseline, or adjacent figure label does not establish a separate input route.
- Use model-level architecture evidence for multiple routes only when the document makes clear that the same interface applies to those routes.
- Preserve a real route and make the narrowest field correction. Remove it only if the document does not establish a distinct source-to-model input route.
- Do not invent a route, split one route into several, change stable IDs, or use external knowledge.
- Return the complete corrected field set. For retained fields, copy the current value exactly. `changed_fields` must exactly name values that differ from the current route; use an empty list for `retain_as_is` and for `remove_route`.
- `evidence_quote` and every `supporting_quotes` item must be a short verbatim excerpt from the enclosed Markdown. Use the strongest route-specific quote. Empty strings are not allowed.
- `inferred` is allowed only for normalized analytical coding derived directly from explicit mechanism evidence; core route existence and input status cannot rest on inference alone.
- Give concise evidence-based rationales. Do not provide hidden chain-of-thought.

Record: {record['record_id']}
Title: {record['title']}
Canonical Markdown SHA-256: {record['canonical_markdown_sha256']}

CURRENT ROUTES AND PRIOR BLIND REVIEWS
{json.dumps(record['routes'], ensure_ascii=False, indent=2)}

FROZEN TAXONOMY CODEBOOK
{codebook}

COMPLETE CANONICAL DOCLING MARKDOWN
--- BEGIN DOCUMENT ---
{document}
--- END DOCUMENT ---
"""


def run_codex(prompt_text: str, output_dir: Path, model: str, timeout: int) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = output_dir / "prompt.txt"
    schema_path = output_dir / "output_schema.json"
    response_path = output_dir / "response.json"
    prompt_path.write_text(prompt_text, encoding="utf-8")
    write_json(schema_path, DECISION_SCHEMA)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="taxonomy-semantic-correction-") as workspace:
        command = [
            "codex", "exec", "--model", model, "--cd", workspace, "--sandbox", "read-only",
            "--skip-git-repo-check", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json",
            "--disable", "shell_tool", "--disable", "unified_exec", "--strict-config",
            "--disable", "apps", "--disable", "plugins", "--disable", "enable_mcp_apps",
            "--disable", "browser_use", "--disable", "computer_use", "--disable", "plugin_sharing",
            "--disable", "tool_suggest", "--disable", "workspace_dependencies",
            "--output-last-message", str(response_path), "--output-schema", str(schema_path), "-",
        ]
        process = subprocess.Popen(
            command,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=workspace,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(input=prompt_text, timeout=timeout)
            (output_dir / "stdout.jsonl").write_text(stdout, encoding="utf-8")
            (output_dir / "stderr.log").write_text(stderr, encoding="utf-8")
            status = "ok" if process.returncode == 0 and response_path.is_file() else "failed"
            error = "" if status == "ok" else stderr[-4000:]
            returncode = process.returncode
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
            (output_dir / "stdout.jsonl").write_text(stdout, encoding="utf-8")
            (output_dir / "stderr.log").write_text(stderr, encoding="utf-8")
            status, error, returncode = "timeout", f"Timed out after {timeout}s", None
    metadata = {
        "status": status,
        "model": model,
        "command": command,
        "duration_seconds": round(time.monotonic() - started, 3),
        "returncode": returncode,
        "error": error,
        "agent_workspace": "isolated_empty_temporary_directory",
        "agent_tool_policy": "shell_exec_apps_plugins_browser_computer_and_workspace_tools_disabled",
        "repository_checkout_available_as_working_context": False,
        "prompt_sha256": sha256(prompt_path),
        "schema_sha256": sha256(schema_path),
    }
    write_json(output_dir / "metadata.json", metadata)
    return metadata


def validate_response(
    response: dict[str, Any], record: dict[str, Any], document: str
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    response = json.loads(json.dumps(response))
    current = {item["current_route"]["route_id"]: item["current_route"] for item in record["routes"]}
    decisions = response.get("decisions") or []
    if {row.get("route_id") for row in decisions} != set(current) or len(decisions) != len(current):
        raise ValueError("Route coverage mismatch")
    normalized_document = normalize(document)
    normalization_log = []
    for decision in decisions:
        route_id = decision["route_id"]
        corrected = decision["corrected_route"]
        evidence_quote = corrected["evidence_quote"]
        if not evidence_quote.strip() or normalize(evidence_quote) not in normalized_document:
            matching_support = next(
                (
                    quote
                    for quote in decision["supporting_quotes"]
                    if quote.strip() and normalize(quote) in normalized_document
                ),
                None,
            )
            current_quote = str(current[route_id].get("evidence_quote") or "")
            replacement = matching_support or (
                current_quote
                if current_quote.strip() and normalize(current_quote) in normalized_document
                else None
            )
            if replacement is None:
                raise ValueError(f"Unmatched or empty primary evidence quote: {route_id}")
            corrected["evidence_quote"] = replacement
            normalization_log.append(
                {
                    "route_id": route_id,
                    "normalization": "primary_evidence_quote_replaced_with_verified_quote",
                    "unmatched_quote": evidence_quote,
                    "replacement_quote": replacement,
                }
            )
        actual_changed = sorted(
            field
            for field in EDITABLE_FIELDS
            if corrected.get(field) != current[route_id].get(field)
        )
        claimed = sorted(set(decision["changed_fields"]))
        if decision["decision"] == "retain_as_is" and actual_changed:
            provenance_only = {"evidence_quote", "section_heading", "supporting_figure_or_table"}
            if not set(actual_changed) <= provenance_only:
                raise ValueError(f"Retained route changed material fields: {route_id} {actual_changed}")
            decision["decision"] = "revise_fields"
            normalization_log.append(
                {
                    "route_id": route_id,
                    "normalization": "retain_with_provenance_change_recast_as_revision",
                    "changed_fields": actual_changed,
                }
            )
        if decision["decision"] == "revise_fields" and not actual_changed:
            decision["decision"] = "retain_as_is"
            normalization_log.append(
                {
                    "route_id": route_id,
                    "normalization": "empty_revision_recast_as_retain",
                    "changed_fields": [],
                }
            )
        if decision["decision"] == "remove_route" and claimed:
            normalization_log.append(
                {
                    "route_id": route_id,
                    "normalization": "removed_route_changed_fields_cleared",
                    "claimed_changed_fields": claimed,
                }
            )
            actual_changed = []
        if claimed != actual_changed:
            normalization_log.append(
                {
                    "route_id": route_id,
                    "normalization": "changed_fields_recomputed",
                    "claimed_changed_fields": claimed,
                    "actual_changed_fields": actual_changed,
                }
            )
        decision["changed_fields"] = actual_changed
        matched_supporting = [
            quote
            for quote in decision["supporting_quotes"]
            if quote.strip() and normalize(quote) in normalized_document
        ]
        unmatched_supporting = [
            quote for quote in decision["supporting_quotes"] if quote not in matched_supporting
        ]
        if unmatched_supporting:
            normalization_log.append(
                {
                    "route_id": route_id,
                    "normalization": "unmatched_optional_supporting_quotes_removed",
                    "quotes": unmatched_supporting,
                }
            )
        decision["supporting_quotes"] = matched_supporting
    return response, normalization_log


def run_record(
    record: dict[str, Any], codebook: str, output: Path, model: str, timeout: int, retries: int
) -> dict[str, Any]:
    target = output / "runs" / record["run_key"]
    selected = target / "selected_response.json"
    document = Path(record["canonical_markdown_local_path"]).read_text(encoding="utf-8")
    if selected.is_file():
        response, normalization_log = validate_response(read_json(selected), record, document)
        write_json(selected, response)
        write_json(target / "selected_response_normalization_log.json", normalization_log)
        return {"run_key": record["run_key"], "record_id": record["record_id"], "status": "ok", "reused": True}
    prompt_text = prompt(record, codebook, document)
    attempts = []
    existing_attempts = sorted(target.glob("attempt_[0-9][0-9]"))
    for attempt_dir in reversed(existing_attempts):
        response_path = attempt_dir / "response.json"
        if not response_path.is_file():
            continue
        try:
            response, normalization_log = validate_response(
                read_json(response_path), record, document
            )
        except Exception:
            continue
        write_json(attempt_dir / "validated_response.json", response)
        write_json(attempt_dir / "normalization_log.json", normalization_log)
        shutil.copy2(attempt_dir / "validated_response.json", selected)
        write_json(
            target / "run_summary.json",
            {"status": "ok", "recovered_attempt": attempt_dir.name, "new_llm_call": False},
        )
        return {"run_key": record["run_key"], "record_id": record["record_id"], "status": "ok", "reused": True}
    first_attempt = max(
        [int(path.name.removeprefix("attempt_")) for path in existing_attempts],
        default=0,
    ) + 1
    for attempt in range(first_attempt, first_attempt + retries + 1):
        attempt_dir = target / f"attempt_{attempt:02d}"
        metadata = run_codex(prompt_text, attempt_dir, model, timeout)
        attempts.append(metadata)
        if metadata["status"] != "ok":
            continue
        try:
            response, normalization_log = validate_response(
                read_json(attempt_dir / "response.json"), record, document
            )
        except Exception as exc:
            metadata["status"] = "invalid_response"
            metadata["error"] = repr(exc)
            write_json(attempt_dir / "metadata.json", metadata)
            continue
        write_json(attempt_dir / "validated_response.json", response)
        write_json(attempt_dir / "normalization_log.json", normalization_log)
        shutil.copy2(attempt_dir / "validated_response.json", selected)
        write_json(target / "run_summary.json", {"status": "ok", "attempts": attempts})
        return {"run_key": record["run_key"], "record_id": record["record_id"], "status": "ok", "reused": False}
    write_json(target / "run_summary.json", {"status": "failed", "attempts": attempts})
    return {"run_key": record["run_key"], "record_id": record["record_id"], "status": "failed", "reused": False}


def collect(output: Path, manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decisions = []
    for record in manifest:
        selected = output / "runs" / record["run_key"] / "selected_response.json"
        document = Path(record["canonical_markdown_local_path"]).read_text(encoding="utf-8")
        response, normalization_log = validate_response(read_json(selected), record, document)
        write_json(selected, response)
        write_json(selected.parent / "selected_response_normalization_log.json", normalization_log)
        for decision in response["decisions"]:
            decisions.append({"record_id": record["record_id"], **decision})
    decisions.sort(key=lambda row: row["route_id"])
    write_jsonl(output / "correction_decisions.jsonl", decisions)
    return decisions


def artifact_hashes(output: Path) -> None:
    files = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "artifact_hashes.json")
    write_json(
        output / "artifact_hashes.json",
        [{"path": str(path.relative_to(output)), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in files],
    )


def audit_tool_isolation(output: Path) -> dict[str, Any]:
    events = []
    for path in sorted(output.rglob("stdout.jsonl")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            item = row.get("item") or {}
            if row.get("type") != "item.completed" or item.get("type") not in {
                "command_execution",
                "mcp_tool_call",
                "web_search",
            }:
                continue
            events.append(
                {
                    "path": str(path.relative_to(output)),
                    "type": item.get("type"),
                    "server": item.get("server"),
                    "tool": item.get("tool"),
                    "status": item.get("status"),
                    "error": (item.get("error") or {}).get("message"),
                }
            )
    metadata_only_tools = {"list_mcp_resources", "list_mcp_resource_templates"}
    successful = [
        row for row in events if row["status"] == "completed" and not row["error"]
    ]
    evidence_bearing = [
        row
        for row in successful
        if not (row["type"] == "mcp_tool_call" and row["tool"] in metadata_only_tools)
    ]
    report = {
        "status": "pass" if not evidence_bearing else "fail",
        "completed_tool_events": len(events),
        "failed_tool_events": sum(bool(row["error"]) for row in events),
        "metadata_only_successes": sum(
            row["type"] == "mcp_tool_call" and row["tool"] in metadata_only_tools
            for row in successful
        ),
        "evidence_bearing_successes": evidence_bearing,
        "acceptance_rule": (
            "No successful shell command, resource read, web search, or other evidence-bearing "
            "tool call. MCP resource-name listing is recorded as metadata-only."
        ),
    }
    write_json(output / "tool_isolation_audit.json", report)
    if evidence_bearing:
        raise RuntimeError("Semantic correction used an external evidence-bearing tool")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxonomy-root", type=Path, default=DEFAULT_TAXONOMY_ROOT)
    parser.add_argument("--f6-root", type=Path, default=DEFAULT_F6_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--max-routes-per-call", type=int, default=4)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()

    if args.max_routes_per_call < 1:
        raise ValueError("--max-routes-per-call must be positive")
    manifest = build_manifest(
        args.taxonomy_root,
        args.f6_root,
        args.output_dir,
        args.max_routes_per_call,
    )
    if args.prepare_only:
        return 0
    codebook = (args.taxonomy_root / "taxonomy_codebook.md").read_text(encoding="utf-8")
    results = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = [
            pool.submit(
                run_record, record, codebook, args.output_dir, args.model, args.timeout, args.retries
            )
            for record in manifest
        ]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: row["run_key"])
    write_json(args.output_dir / "run_summary.json", {"model": args.model, "results": results})
    if any(row["status"] != "ok" for row in results):
        raise RuntimeError("Semantic correction is incomplete")
    decisions = collect(args.output_dir, manifest)
    counts = Counter(row["decision"] for row in decisions)
    report = {
        "status": "complete",
        "created_at": utc_now(),
        "model": args.model,
        "records": len({record["record_id"] for record in manifest}),
        "llm_calls": len(manifest),
        "routes": len(decisions),
        "decision_counts": dict(sorted(counts.items())),
        "supporting_quotes_verified": True,
        "canonical_taxonomy_mutated": False,
    }
    report["tool_isolation"] = audit_tool_isolation(args.output_dir)
    write_json(args.output_dir / "correction_report.json", report)
    artifact_hashes(args.output_dir)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
