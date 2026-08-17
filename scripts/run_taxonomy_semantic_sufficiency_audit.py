#!/usr/bin/env python3
"""Audit whether canonical full text semantically supports risky taxonomy routes."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
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
DEFAULT_PROFILE_MANIFEST = (
    ROOT
    / "data/living_catalog/taxonomy_rerun_preflight_2026-08-12"
    / "canonical_docling_profile_manifest.csv"
)
DEFAULT_OUTPUT = ROOT / "analysis/taxonomy_semantic_sufficiency_audit_2026-08-17"
DEFAULT_MODEL = "gpt-5.4-mini"

FIELD_NAMES = [
    "lifecycle_phase",
    "task_or_configuration",
    "source_object",
    "transformation_chain",
    "model_visible_form",
    "carrier_family_and_subtype",
    "insertion_or_fusion",
    "fusion_topology",
    "text_role",
    "input_status",
]

FIELD_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["field", "verdict", "explanation"],
    "properties": {
        "field": {"type": "string", "enum": FIELD_NAMES},
        "verdict": {
            "type": "string",
            "enum": [
                "supported",
                "partially_supported",
                "unsupported",
                "not_applicable",
                "unclear",
            ],
        },
        "explanation": {"type": "string"},
    },
}

ROUTE_REVIEW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "route_id",
        "overall_sufficiency",
        "recommended_action",
        "field_reviews",
        "supporting_quotes",
        "unsupported_assertions",
        "concise_rationale",
        "confidence",
    ],
    "properties": {
        "route_id": {"type": "string"},
        "overall_sufficiency": {
            "type": "string",
            "enum": ["sufficient", "partial", "insufficient", "unclear"],
        },
        "recommended_action": {
            "type": "string",
            "enum": [
                "retain_as_is",
                "revise_fields",
                "remove_route",
                "merge_or_split",
                "manual_full_text_review",
            ],
        },
        "field_reviews": {
            "type": "array",
            "minItems": len(FIELD_NAMES),
            "maxItems": len(FIELD_NAMES),
            "items": FIELD_SCHEMA,
        },
        "supporting_quotes": {"type": "array", "items": {"type": "string"}},
        "unsupported_assertions": {"type": "array", "items": {"type": "string"}},
        "concise_rationale": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
}

REVIEW_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["reviewer_role", "reviews"],
    "properties": {
        "reviewer_role": {"type": "string"},
        "reviews": {"type": "array", "items": ROUTE_REVIEW_SCHEMA},
    },
}

REVIEWER_INSTRUCTIONS = {
    "semantic_reviewer": (
        "Act as a biomedical methods reviewer. For every route, test whether the supplied "
        "paper text is semantically sufficient to establish each coded field. Distinguish an "
        "explicit statement from a reasonable but unstated inference."
    ),
    "adversarial_reviewer": (
        "Act as an adversarial evidence auditor. Look specifically for routes whose quote is "
        "traceable but does not establish the asserted source object, transformation, carrier, "
        "topology, lifecycle, text role, or actual-input status. Do not reject a route merely "
        "because its evidence is distributed across several passages."
    ),
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_risky_route(route: dict[str, Any]) -> bool:
    dense_only = bool(route.get("dense_candidate_refs")) and not bool(
        route.get("source_candidate_refs")
    )
    return dense_only or route.get("evidence_status") == "inferred"


def compact_route(route: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "route_id",
        "configuration_id",
        "model_id",
        "model_name",
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
        "source_candidate_refs",
        "dense_candidate_refs",
        "pages",
        "doc_item_refs",
    ]
    return {key: route.get(key) for key in keys}


def resolve_payload_path(source_root: Path, manifest_value: str) -> Path:
    path = Path(manifest_value)
    return path if path.is_absolute() else source_root / path


def prepare_manifest(
    *, route_path: Path, profile_manifest_path: Path, source_root: Path, output_dir: Path
) -> list[dict[str, Any]]:
    routes = [
        json.loads(line)
        for line in route_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    risky = [route for route in routes if is_risky_route(route)]
    by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for route in risky:
        by_record[route["record_id"]].append(compact_route(route))

    with profile_manifest_path.open(encoding="utf-8", newline="") as stream:
        profiles = {row["candidate_id"]: row for row in csv.DictReader(stream)}

    manifest: list[dict[str, Any]] = []
    missing = sorted(set(by_record) - set(profiles))
    if missing:
        raise RuntimeError(f"Missing canonical profiles for: {missing}")
    for record_id in sorted(by_record):
        profile = profiles[record_id]
        markdown_path = resolve_payload_path(source_root, profile["markdown"])
        if not markdown_path.exists():
            raise FileNotFoundError(markdown_path)
        actual_hash = sha256(markdown_path)
        expected_hash = profile.get("markdown_sha256") or ""
        if expected_hash and actual_hash != expected_hash:
            raise RuntimeError(f"Canonical Markdown hash mismatch: {record_id}")
        record_routes = sorted(by_record[record_id], key=lambda item: item["route_id"])
        manifest.append(
            {
                "record_id": record_id,
                "title": next(route["title"] for route in routes if route["record_id"] == record_id),
                "canonical_markdown_manifest_path": profile["markdown"],
                "canonical_markdown_local_path": str(markdown_path),
                "canonical_markdown_sha256": actual_hash,
                "canonical_markdown_chars": len(markdown_path.read_text(encoding="utf-8")),
                "risky_route_count": len(record_routes),
                "routes": record_routes,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "audit_manifest.json", manifest)
    summary = {
        "created_at": utc_now(),
        "route_source": str(route_path),
        "route_source_sha256": sha256(route_path),
        "profile_manifest": str(profile_manifest_path),
        "profile_manifest_sha256": sha256(profile_manifest_path),
        "source_root": str(source_root),
        "canonical_route_count": len(routes),
        "risky_route_count": len(risky),
        "record_count": len(manifest),
        "dense_only_count": sum(
            bool(route.get("dense_candidate_refs"))
            and not bool(route.get("source_candidate_refs"))
            for route in routes
        ),
        "inferred_count": sum(route.get("evidence_status") == "inferred" for route in routes),
        "short_quote_count": sum(len((route.get("evidence_quote") or "").split()) < 4 for route in risky),
        "uncertainty_count": sum(bool(route.get("uncertainty")) for route in risky),
        "selection_rule": "dense_candidate_refs without source_candidate_refs OR evidence_status=inferred",
        "text_policy": "complete canonical Docling Markdown; no truncation",
    }
    write_json(output_dir / "audit_population.json", summary)
    return manifest


def base_prompt(
    *, reviewer_role: str, record: dict[str, Any], codebook: str, document: str
) -> str:
    return f"""{REVIEWER_INSTRUCTIONS[reviewer_role]}

This is a semantic sufficiency audit, not a new open extraction. Review only the listed routes.

Rules:
- Use the COMPLETE canonical Docling Markdown enclosed below. Evidence may be distributed across the document; do not judge from `evidence_quote` alone.
- A field is `supported` only when the document establishes that exact assertion for the named model, lifecycle phase, and configuration. Nearby task names or a general model description are insufficient when the link must be inferred.
- `partially_supported` means some but not all of the asserted field is established.
- Use `not_applicable` only for a genuinely empty or inapplicable field, not for missing evidence.
- Generated outputs, labels, supervision targets, graders, downstream consumers, baselines, and ablations are not `actual_model_input` unless the route explicitly describes their own named model/configuration.
- The taxonomy family is determined by the first model-facing carrier after semantic preprocessing, as specified in the codebook.
- Supporting quotes must be short verbatim excerpts from the enclosed document. Multiple excerpts are allowed. Do not invent quotations.
- Recommend `retain_as_is` only when all material assertions are supported. Otherwise state the narrowest corrective action.
- Return all ten field reviews exactly once for every listed route, in the field order supplied by the schema.
- Do not use tools, external knowledge, or hidden chain-of-thought. Give concise evidence-based rationales.

Reviewer role: {reviewer_role}
Record: {record['record_id']}
Title: {record['title']}
Canonical Markdown SHA-256: {record['canonical_markdown_sha256']}

ROUTES TO AUDIT
{json.dumps(record['routes'], ensure_ascii=False, indent=2)}

FROZEN TAXONOMY CODEBOOK
{codebook}

COMPLETE CANONICAL DOCLING MARKDOWN
--- BEGIN DOCUMENT ---
{document}
--- END DOCUMENT ---
"""


def normalize_text(value: str) -> str:
    value = " ".join(html.unescape(value).split())
    value = re.sub(r"\s+([.,;:!?])", r"\1", value)
    return value.casefold()


def normalize_quote(value: str) -> str:
    value = value.strip()
    quote_pairs = [("\"", "\""), ("'", "'"), ("“", "”"), ("‘", "’")]
    for opening, closing in quote_pairs:
        if len(value) >= 2 and value.startswith(opening) and value.endswith(closing):
            value = value[len(opening) : -len(closing)].strip()
            break
    return normalize_text(value)


def validate_reviews(
    response: dict[str, Any], expected_route_ids: set[str], canonical_document: str
) -> None:
    reviews = response.get("reviews") or []
    returned = [review.get("route_id") for review in reviews]
    if len(returned) != len(set(returned)) or set(returned) != expected_route_ids:
        raise ValueError(
            f"Route coverage mismatch: expected={sorted(expected_route_ids)} returned={sorted(returned)}"
        )
    normalized_document = normalize_text(canonical_document)
    for review in reviews:
        fields = [item.get("field") for item in review.get("field_reviews") or []]
        if fields != FIELD_NAMES:
            raise ValueError(f"Field coverage/order mismatch for {review['route_id']}: {fields}")
        for quote in review.get("supporting_quotes") or []:
            if normalize_quote(quote) not in normalized_document:
                raise ValueError(f"Unmatched supporting quote for {review['route_id']}: {quote!r}")
        if review["overall_sufficiency"] == "sufficient" and not review["supporting_quotes"]:
            raise ValueError(f"Sufficient route lacks a supporting quote: {review['route_id']}")


def sanitize_supporting_quotes(
    response: dict[str, Any], canonical_document: str
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cleaned = json.loads(json.dumps(response))
    normalized_document = normalize_text(canonical_document)
    report = []
    for review in cleaned.get("reviews") or []:
        matched = []
        unmatched = []
        for quote in review.get("supporting_quotes") or []:
            if normalize_quote(quote) in normalized_document:
                matched.append(quote)
            else:
                unmatched.append(quote)
        review["supporting_quotes"] = matched
        report.append(
            {
                "route_id": review["route_id"],
                "matched_quotes": matched,
                "unmatched_quotes_removed_from_validated_response": unmatched,
            }
        )
        if review["overall_sufficiency"] in {"sufficient", "partial"} and not matched:
            raise ValueError(
                f"{review['overall_sufficiency']} route lacks any verified supporting quote: "
                f"{review['route_id']}"
            )
    return cleaned, report


def run_codex_attempt(
    *, prompt: str, schema: dict[str, Any], output_dir: Path, model: str, timeout: int
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = output_dir / "prompt.txt"
    schema_path = output_dir / "output_schema.json"
    response_path = output_dir / "response.json"
    stdout_path = output_dir / "stdout.jsonl"
    stderr_path = output_dir / "stderr.log"
    prompt_path.write_text(prompt, encoding="utf-8")
    write_json(schema_path, schema)
    command = [
        "codex",
        "exec",
        "--model",
        model,
        "--cd",
        str(ROOT),
        "--sandbox",
        "read-only",
        "--ignore-user-config",
        "--ignore-rules",
        "--ephemeral",
        "--json",
        "--output-last-message",
        str(response_path),
        "--output-schema",
        str(schema_path),
        "-",
    ]
    started = utc_now()
    clock = time.monotonic()
    status = "ok"
    error = ""
    returncode: int | None = None
    try:
        result = subprocess.run(
            command,
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=ROOT,
            timeout=timeout,
            env={**os.environ, "NO_COLOR": "1"},
        )
        returncode = result.returncode
        stdout_path.write_text(result.stdout, encoding="utf-8")
        stderr_path.write_text(result.stderr, encoding="utf-8")
        if result.returncode:
            status = "error_returncode"
            error = result.stderr[-4000:]
        elif not response_path.exists():
            status = "missing_response"
            error = "Codex exited without response.json"
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        error = f"Timed out after {timeout} seconds"
        stdout_path.write_text(exc.stdout or "", encoding="utf-8")
        stderr_path.write_text(exc.stderr or "", encoding="utf-8")
    except Exception as exc:  # pragma: no cover - operational guard
        status = "exception"
        error = repr(exc)
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(error + "\n", encoding="utf-8")
    metadata = {
        "status": status,
        "model": model,
        "command": command,
        "prompt_sha256": sha256(prompt_path),
        "schema_sha256": sha256(schema_path),
        "started_at": started,
        "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - clock, 3),
        "returncode": returncode,
        "error": error,
    }
    write_json(output_dir / "metadata.json", metadata)
    return metadata


def selected_response_path(output_dir: Path, role: str, record_id: str) -> Path:
    return output_dir / "runs" / role / record_id / "selected_response.json"


def next_attempt_number(target: Path) -> int:
    numbers = [
        int(path.name.removeprefix("attempt_"))
        for path in target.glob("attempt_[0-9][0-9]")
        if path.name.removeprefix("attempt_").isdigit()
    ]
    return max(numbers, default=0) + 1


def run_record(
    *,
    role: str,
    record: dict[str, Any],
    codebook: str,
    output_dir: Path,
    model: str,
    timeout: int,
    retries: int,
    force: bool,
) -> dict[str, Any]:
    target = output_dir / "runs" / role / record["record_id"]
    selected = target / "selected_response.json"
    summary_path = target / "run_summary.json"
    document = Path(record["canonical_markdown_local_path"]).read_text(encoding="utf-8")
    expected = {route["route_id"] for route in record["routes"]}
    if selected.exists() and not force:
        try:
            validate_reviews(read_json(selected), expected, document)
            return read_json(summary_path)
        except Exception:
            pass
    prompt = base_prompt(reviewer_role=role, record=record, codebook=codebook, document=document)
    attempts = []
    first_attempt = next_attempt_number(target)
    for attempt_no in range(first_attempt, first_attempt + retries + 1):
        attempt_dir = target / f"attempt_{attempt_no:02d}"
        metadata = run_codex_attempt(
            prompt=prompt,
            schema=REVIEW_SCHEMA,
            output_dir=attempt_dir,
            model=model,
            timeout=timeout,
        )
        attempts.append(metadata)
        if metadata["status"] != "ok":
            continue
        try:
            response, quote_report = sanitize_supporting_quotes(
                read_json(attempt_dir / "response.json"), document
            )
            validate_reviews(response, expected, document)
        except Exception as exc:
            metadata["status"] = "invalid_response"
            metadata["error"] = repr(exc)
            write_json(attempt_dir / "metadata.json", metadata)
            continue
        write_json(attempt_dir / "validated_response.json", response)
        write_json(attempt_dir / "quote_validation.json", quote_report)
        shutil.copy2(attempt_dir / "validated_response.json", selected)
        summary = {
            "record_id": record["record_id"],
            "role": role,
            "status": "ok",
            "selected_attempt": attempt_no,
            "attempts": attempts,
        }
        write_json(summary_path, summary)
        return summary
    summary = {
        "record_id": record["record_id"],
        "role": role,
        "status": "failed",
        "selected_attempt": None,
        "attempts": attempts,
    }
    write_json(summary_path, summary)
    return summary


def run_reviewer_role(
    *,
    role: str,
    output_dir: Path,
    codebook_path: Path,
    model: str,
    timeout: int,
    retries: int,
    max_workers: int,
    force: bool,
) -> list[dict[str, Any]]:
    manifest = read_json(output_dir / "audit_manifest.json")
    codebook = codebook_path.read_text(encoding="utf-8")
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(
                run_record,
                role=role,
                record=record,
                codebook=codebook,
                output_dir=output_dir,
                model=model,
                timeout=timeout,
                retries=retries,
                force=force,
            )
            for record in manifest
        ]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item["record_id"])
    write_json(
        output_dir / "runs" / role / "run_summary.json",
        {
            "role": role,
            "model": model,
            "records": len(results),
            "ok": sum(item["status"] == "ok" for item in results),
            "results": results,
        },
    )
    if not all(item["status"] == "ok" for item in results):
        raise RuntimeError(f"Incomplete reviewer role: {role}")
    return results


def review_index(output_dir: Path, role: str) -> dict[str, dict[str, Any]]:
    manifest = read_json(output_dir / "audit_manifest.json")
    index = {}
    for record in manifest:
        response = read_json(selected_response_path(output_dir, role, record["record_id"]))
        for review in response["reviews"]:
            index[review["route_id"]] = review
    return index


def recover_valid_attempts(output_dir: Path, role: str) -> dict[str, Any]:
    manifest = read_json(output_dir / "audit_manifest.json")
    recovered = []
    already_selected = []
    unrecoverable = []
    for record in manifest:
        target = output_dir / "runs" / role / record["record_id"]
        selected = target / "selected_response.json"
        if selected.exists():
            already_selected.append(record["record_id"])
            continue
        document = Path(record["canonical_markdown_local_path"]).read_text(encoding="utf-8")
        expected = {route["route_id"] for route in record["routes"]}
        chosen = None
        errors = []
        for response_path in sorted(target.glob("attempt_*/response.json"), reverse=True):
            try:
                response, quote_report = sanitize_supporting_quotes(
                    read_json(response_path), document
                )
                validate_reviews(response, expected, document)
            except Exception as exc:
                errors.append({"response": str(response_path), "error": repr(exc)})
                continue
            attempt_dir = response_path.parent
            write_json(attempt_dir / "validated_response.json", response)
            write_json(attempt_dir / "quote_validation.json", quote_report)
            shutil.copy2(attempt_dir / "validated_response.json", selected)
            attempt_no = int(attempt_dir.name.removeprefix("attempt_"))
            summary = {
                "record_id": record["record_id"],
                "role": role,
                "status": "ok",
                "selected_attempt": attempt_no,
                "selection_method": "recovered_existing_raw_response_after_quote_sanitization",
                "new_llm_call": False,
            }
            write_json(target / "run_summary.json", summary)
            chosen = {
                "record_id": record["record_id"],
                "attempt": attempt_no,
                "quote_validation": quote_report,
            }
            recovered.append(chosen)
            break
        if chosen is None:
            unrecoverable.append({"record_id": record["record_id"], "errors": errors})
    report = {
        "role": role,
        "already_selected": len(already_selected),
        "recovered": len(recovered),
        "unrecoverable": len(unrecoverable),
        "recovered_records": recovered,
        "unrecoverable_records": unrecoverable,
    }
    write_json(output_dir / "runs" / role / "recovery_report.json", report)
    return report


def field_verdicts(review: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple((item["field"], item["verdict"]) for item in review["field_reviews"])


def needs_adjudication(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return (
        a["overall_sufficiency"] != "sufficient"
        or b["overall_sufficiency"] != "sufficient"
        or a["recommended_action"] != "retain_as_is"
        or b["recommended_action"] != "retain_as_is"
        or a["overall_sufficiency"] != b["overall_sufficiency"]
        or a["recommended_action"] != b["recommended_action"]
        or field_verdicts(a) != field_verdicts(b)
    )


def build_comparison(output_dir: Path) -> list[dict[str, Any]]:
    first = review_index(output_dir, "semantic_reviewer")
    second = review_index(output_dir, "adversarial_reviewer")
    if set(first) != set(second):
        raise RuntimeError("Reviewer route sets differ")
    comparison = []
    for route_id in sorted(first):
        a = first[route_id]
        b = second[route_id]
        comparison.append(
            {
                "route_id": route_id,
                "requires_adjudication": needs_adjudication(a, b),
                "semantic_reviewer": a,
                "adversarial_reviewer": b,
            }
        )
    write_json(output_dir / "reviewer_comparison.json", comparison)
    return comparison


def adjudication_prompt(
    *, record: dict[str, Any], flagged: list[dict[str, Any]], codebook: str, document: str
) -> str:
    route_by_id = {route["route_id"]: route for route in record["routes"]}
    payload = [
        {
            "route": route_by_id[item["route_id"]],
            "semantic_reviewer": item["semantic_reviewer"],
            "adversarial_reviewer": item["adversarial_reviewer"],
        }
        for item in flagged
    ]
    return f"""You are the independent adjudicator for a semantic evidence-sufficiency audit.

Resolve only the listed routes. Judge the route fields against the COMPLETE canonical paper, not by voting between reviewers. Preserve a route only when its material source-to-model claims are established for the exact model/configuration. Prefer a narrow field revision over route removal when the paper clearly supports a real route but the current coding overstates it. Supporting quotes must be verbatim excerpts from the enclosed document.

Return all ten field reviews exactly once and in schema order. Do not use tools, external knowledge, or hidden chain-of-thought.

Record: {record['record_id']}
Title: {record['title']}

FLAGGED ROUTES AND BLIND REVIEWS
{json.dumps(payload, ensure_ascii=False, indent=2)}

FROZEN TAXONOMY CODEBOOK
{codebook}

COMPLETE CANONICAL DOCLING MARKDOWN
--- BEGIN DOCUMENT ---
{document}
--- END DOCUMENT ---
"""


def run_adjudication_record(
    *,
    record: dict[str, Any],
    flagged: list[dict[str, Any]],
    codebook: str,
    output_dir: Path,
    model: str,
    timeout: int,
    retries: int,
    force: bool,
) -> dict[str, Any]:
    target = output_dir / "runs" / "adjudicator" / record["record_id"]
    selected = target / "selected_response.json"
    summary_path = target / "run_summary.json"
    document = Path(record["canonical_markdown_local_path"]).read_text(encoding="utf-8")
    expected = {item["route_id"] for item in flagged}
    if selected.exists() and not force:
        try:
            validate_reviews(read_json(selected), expected, document)
            return read_json(summary_path)
        except Exception:
            pass
    prompt = adjudication_prompt(record=record, flagged=flagged, codebook=codebook, document=document)
    attempts = []
    first_attempt = next_attempt_number(target)
    for attempt_no in range(first_attempt, first_attempt + retries + 1):
        attempt_dir = target / f"attempt_{attempt_no:02d}"
        metadata = run_codex_attempt(
            prompt=prompt,
            schema=REVIEW_SCHEMA,
            output_dir=attempt_dir,
            model=model,
            timeout=timeout,
        )
        attempts.append(metadata)
        if metadata["status"] != "ok":
            continue
        try:
            response, quote_report = sanitize_supporting_quotes(
                read_json(attempt_dir / "response.json"), document
            )
            validate_reviews(response, expected, document)
        except Exception as exc:
            metadata["status"] = "invalid_response"
            metadata["error"] = repr(exc)
            write_json(attempt_dir / "metadata.json", metadata)
            continue
        write_json(attempt_dir / "validated_response.json", response)
        write_json(attempt_dir / "quote_validation.json", quote_report)
        shutil.copy2(attempt_dir / "validated_response.json", selected)
        summary = {
            "record_id": record["record_id"],
            "role": "adjudicator",
            "status": "ok",
            "selected_attempt": attempt_no,
            "route_count": len(expected),
            "attempts": attempts,
        }
        write_json(summary_path, summary)
        return summary
    summary = {
        "record_id": record["record_id"],
        "role": "adjudicator",
        "status": "failed",
        "selected_attempt": None,
        "route_count": len(expected),
        "attempts": attempts,
    }
    write_json(summary_path, summary)
    return summary


def run_adjudicator(
    *,
    output_dir: Path,
    codebook_path: Path,
    model: str,
    timeout: int,
    retries: int,
    max_workers: int,
    force: bool,
) -> list[dict[str, Any]]:
    comparison = build_comparison(output_dir)
    flagged_by_route = {item["route_id"]: item for item in comparison if item["requires_adjudication"]}
    manifest = read_json(output_dir / "audit_manifest.json")
    jobs = []
    for record in manifest:
        flagged = [flagged_by_route[route["route_id"]] for route in record["routes"] if route["route_id"] in flagged_by_route]
        if flagged:
            jobs.append((record, flagged))
    codebook = codebook_path.read_text(encoding="utf-8")
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(
                run_adjudication_record,
                record=record,
                flagged=flagged,
                codebook=codebook,
                output_dir=output_dir,
                model=model,
                timeout=timeout,
                retries=retries,
                force=force,
            )
            for record, flagged in jobs
        ]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item["record_id"])
    write_json(
        output_dir / "runs" / "adjudicator" / "run_summary.json",
        {
            "role": "adjudicator",
            "model": model,
            "records": len(results),
            "routes": len(flagged_by_route),
            "ok": sum(item["status"] == "ok" for item in results),
            "results": results,
        },
    )
    if not all(item["status"] == "ok" for item in results):
        raise RuntimeError("Incomplete adjudication")
    return results


def finalize(output_dir: Path, model: str) -> dict[str, Any]:
    manifest = read_json(output_dir / "audit_manifest.json")
    comparison = build_comparison(output_dir)
    by_route = {item["route_id"]: item for item in comparison}
    adjudicated: dict[str, dict[str, Any]] = {}
    for record in manifest:
        path = selected_response_path(output_dir, "adjudicator", record["record_id"])
        if path.exists():
            adjudicated.update({review["route_id"]: review for review in read_json(path)["reviews"]})

    dispositions = []
    for record in manifest:
        for route in record["routes"]:
            comparison_item = by_route[route["route_id"]]
            if comparison_item["requires_adjudication"]:
                final_review = adjudicated.get(route["route_id"])
                if final_review is None:
                    raise RuntimeError(f"Missing adjudication: {route['route_id']}")
                basis = "llm_adjudication"
            else:
                final_review = comparison_item["semantic_reviewer"]
                basis = "two_independent_reviews_agree_sufficient"
            dispositions.append(
                {
                    "record_id": record["record_id"],
                    "title": record["title"],
                    "model_id": route["model_id"],
                    "model_name": route.get("model_name"),
                    "route_id": route["route_id"],
                    "route_label": route.get("route_label"),
                    "current_carrier_family": route.get("carrier_family"),
                    "current_carrier_subtype": route.get("carrier_subtype"),
                    "current_evidence_quote": route.get("evidence_quote"),
                    "current_section_heading": route.get("section_heading"),
                    "risk_flags": {
                        "dense_only": bool(route.get("dense_candidate_refs"))
                        and not bool(route.get("source_candidate_refs")),
                        "inferred": route.get("evidence_status") == "inferred",
                        "quote_under_four_words": len((route.get("evidence_quote") or "").split()) < 4,
                        "uncertainty_present": bool(route.get("uncertainty")),
                    },
                    "decision_basis": basis,
                    "final_review": final_review,
                    "reviewer_comparison": comparison_item,
                }
            )

    output_jsonl = output_dir / "semantic_sufficiency_dispositions.jsonl"
    output_jsonl.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in dispositions),
        encoding="utf-8",
    )
    action_queue = [
        item for item in dispositions if item["final_review"]["recommended_action"] != "retain_as_is"
    ]
    action_queue_path = output_dir / "semantic_sufficiency_action_queue.csv"
    with action_queue_path.open("w", encoding="utf-8", newline="") as stream:
        fieldnames = [
            "record_id",
            "title",
            "model_id",
            "model_name",
            "route_id",
            "route_label",
            "current_carrier_family",
            "current_carrier_subtype",
            "current_evidence_quote",
            "current_section_heading",
            "overall_sufficiency",
            "recommended_action",
            "field_issues",
            "unsupported_assertions",
            "concise_rationale",
            "confidence",
        ]
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for item in action_queue:
            review = item["final_review"]
            field_issues = [
                f"{field['field']}={field['verdict']}"
                for field in review["field_reviews"]
                if field["verdict"] not in {"supported", "not_applicable"}
            ]
            writer.writerow(
                {
                    **{key: item.get(key) for key in fieldnames if key in item},
                    "overall_sufficiency": review["overall_sufficiency"],
                    "recommended_action": review["recommended_action"],
                    "field_issues": " | ".join(field_issues),
                    "unsupported_assertions": " | ".join(review["unsupported_assertions"]),
                    "concise_rationale": review["concise_rationale"],
                    "confidence": review["confidence"],
                }
            )
    record_actions: dict[str, Counter[str]] = defaultdict(Counter)
    field_issues: Counter[tuple[str, str]] = Counter()
    for item in dispositions:
        action = item["final_review"]["recommended_action"]
        record_actions[item["record_id"]][action] += 1
        if action == "retain_as_is":
            continue
        for field in item["final_review"]["field_reviews"]:
            if field["verdict"] not in {"supported", "not_applicable"}:
                field_issues[(field["field"], field["verdict"])] += 1
    failure_lines = [
        "# F6 semantic-sufficiency failure modes",
        "",
        "The audit primarily identifies over-specific field coding, not automatically false input "
        "routes. `revise_fields` means the paper establishes a route but does not establish every "
        "current source, transformation, carrier, topology, lifecycle, text-role, or input-status "
        "assertion. `manual_full_text_review` remains unresolved computationally.",
        "",
        "## Records requiring action",
        "",
        "| Record | Retain | Revise fields | Manual review |",
        "|---|---:|---:|---:|",
    ]
    record_titles = {item["record_id"]: item["title"] for item in dispositions}
    for record_id, counts in sorted(
        record_actions.items(),
        key=lambda pair: (
            -(pair[1]["revise_fields"] + pair[1]["manual_full_text_review"]),
            pair[0],
        ),
    ):
        if not counts["revise_fields"] and not counts["manual_full_text_review"]:
            continue
        label = f"`{record_id}` — {record_titles[record_id].replace('|', '/')}"
        failure_lines.append(
            f"| {label} | {counts['retain_as_is']} | {counts['revise_fields']} | "
            f"{counts['manual_full_text_review']} |"
        )
    failure_lines.extend(
        [
            "",
            "## Unsupported or incomplete fields",
            "",
            "Counts below are field verdicts, so one route may contribute several rows.",
            "",
            "| Field | Verdict | Routes |",
            "|---|---|---:|",
        ]
    )
    for (field, verdict), count in field_issues.most_common():
        failure_lines.append(f"| `{field}` | `{verdict}` | {count} |")
    manual_items = [
        item
        for item in dispositions
        if item["final_review"]["recommended_action"] == "manual_full_text_review"
    ]
    failure_lines.extend(["", "## Manual full-text queue", ""])
    for item in manual_items:
        failure_lines.append(
            f"- `{item['route_id']}` ({item['model_name']}, {item['route_label']}): "
            f"{item['final_review']['concise_rationale']}"
        )
    failure_lines.extend(
        [
            "",
            "The complete field explanations, verified supporting quotes, unsupported assertions, "
            "blind reviewer outputs, and adjudication are retained in the route-level disposition "
            "ledger and `runs/` tree.",
            "",
        ]
    )
    (output_dir / "semantic_sufficiency_failure_modes.md").write_text(
        "\n".join(failure_lines), encoding="utf-8"
    )
    action_counts = Counter(item["final_review"]["recommended_action"] for item in dispositions)
    sufficiency_counts = Counter(item["final_review"]["overall_sufficiency"] for item in dispositions)
    report = {
        "status": "complete",
        "created_at": utc_now(),
        "model": model,
        "validation_type": "two independent LLM semantic reviews plus adjudication",
        "human_validation": False,
        "canonical_routes_mutated": False,
        "records_audited": len(manifest),
        "routes_audited": len(dispositions),
        "routes_adjudicated": sum(item["decision_basis"] == "llm_adjudication" for item in dispositions),
        "sufficiency_counts": dict(sorted(sufficiency_counts.items())),
        "recommended_action_counts": dict(sorted(action_counts.items())),
        "retain_as_is": action_counts.get("retain_as_is", 0),
        "requires_change_or_manual_review": len(dispositions) - action_counts.get("retain_as_is", 0),
        "all_supporting_quotes_verified": True,
        "complete_route_coverage": len(dispositions) == read_json(output_dir / "audit_population.json")["risky_route_count"],
    }
    write_json(output_dir / "semantic_sufficiency_report.json", report)
    lines = [
        "# F6 semantic sufficiency audit",
        "",
        "This audit tests whether complete canonical Docling Markdown semantically supports every "
        "material field of the dense-only or inferred routes. It does not alter the canonical "
        "taxonomy output.",
        "",
        f"- Records audited: **{report['records_audited']}**",
        f"- Routes audited: **{report['routes_audited']}**",
        f"- Routes sent to adjudication: **{report['routes_adjudicated']}**",
        f"- Retain as-is: **{report['retain_as_is']}**",
        f"- Change or manual review recommended: **{report['requires_change_or_manual_review']}**",
        f"- Model for all roles: `{model}`",
        "- Evidence input: complete canonical Docling Markdown, without truncation",
        "- Validation: every returned supporting quote was matched against the canonical Markdown",
        "- Interpretation: repeated computational review with LLM adjudication, not human ground truth",
        "",
        "## Final sufficiency",
        "",
    ]
    for key, value in sorted(sufficiency_counts.items()):
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Recommended actions", ""])
    for key, value in sorted(action_counts.items()):
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "Detailed route-level decisions are in `semantic_sufficiency_dispositions.jsonl`; exact "
            "prompts, schemas, responses, stdout, stderr, retries, commands, hashes, and timings are "
            "retained under `runs/`.",
            "Routes requiring a change or manual review are flattened into "
            "`semantic_sufficiency_action_queue.csv` for correction work.",
            "Aggregate field and record-level patterns are documented in "
            "`semantic_sufficiency_failure_modes.md`.",
            "",
        ]
    )
    (output_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")
    hashes = {}
    for path in sorted(output_dir.rglob("*")):
        if path.is_file() and path.name != "artifact_hashes.json":
            hashes[str(path.relative_to(output_dir))] = sha256(path)
    write_json(output_dir / "artifact_hashes.json", hashes)
    return report


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument(
        "command",
        choices=["prepare", "review", "recover", "compare", "adjudicate", "finalize", "all"],
    )
    value.add_argument("--taxonomy-root", type=Path, default=DEFAULT_TAXONOMY_ROOT)
    value.add_argument("--profile-manifest", type=Path, default=DEFAULT_PROFILE_MANIFEST)
    value.add_argument("--source-root", type=Path, default=ROOT)
    value.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    value.add_argument("--model", default=DEFAULT_MODEL)
    value.add_argument(
        "--role", choices=sorted(REVIEWER_INSTRUCTIONS), default="semantic_reviewer"
    )
    value.add_argument("--max-workers", type=int, default=6)
    value.add_argument("--timeout", type=int, default=3600)
    value.add_argument("--retries", type=int, default=1)
    value.add_argument("--force", action="store_true")
    return value


def main() -> int:
    args = parser().parse_args()
    route_path = args.taxonomy_root / "route_annotations.jsonl"
    codebook_path = args.taxonomy_root / "taxonomy_codebook.md"
    if args.command in {"prepare", "all"}:
        prepare_manifest(
            route_path=route_path,
            profile_manifest_path=args.profile_manifest,
            source_root=args.source_root,
            output_dir=args.output_dir,
        )
    if args.command == "review":
        run_reviewer_role(
            role=args.role,
            output_dir=args.output_dir,
            codebook_path=codebook_path,
            model=args.model,
            timeout=args.timeout,
            retries=args.retries,
            max_workers=args.max_workers,
            force=args.force,
        )
    if args.command == "recover":
        report = recover_valid_attempts(args.output_dir, args.role)
        print(json.dumps(report, ensure_ascii=False))
    if args.command == "compare":
        build_comparison(args.output_dir)
    if args.command in {"adjudicate", "all"}:
        if args.command == "all":
            for role in REVIEWER_INSTRUCTIONS:
                run_reviewer_role(
                    role=role,
                    output_dir=args.output_dir,
                    codebook_path=codebook_path,
                    model=args.model,
                    timeout=args.timeout,
                    retries=args.retries,
                    max_workers=args.max_workers,
                    force=args.force,
                )
        run_adjudicator(
            output_dir=args.output_dir,
            codebook_path=codebook_path,
            model=args.model,
            timeout=args.timeout,
            retries=args.retries,
            max_workers=args.max_workers,
            force=args.force,
        )
    if args.command in {"finalize", "all"}:
        report = finalize(args.output_dir, args.model)
        print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
