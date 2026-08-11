#!/usr/bin/env python3
"""
Run the protocol screening pipeline with Codex CLI reviewers.

This runner mirrors the protocol topology:
  1. scope_reviewer
  2. architecture_reviewer
  3. Python gate logic
  4. adjudicator only for unresolved/conflict cases

It keeps an audit trail of prompts, raw CLI output, parsed role outputs,
gate decisions, adjudication inputs, and final decisions. It intentionally
asks for brief evidence-grounded rationales, not hidden chain-of-thought.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Literal


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/dedup_update_2026-06-10/new_records_screening_ready_crossref_checked.json"
DEFAULT_OUTDIR = ROOT / "data/screening_codex_2026-06-10"
PROMPT_DIR = ROOT / "protocol/screening_prompt_templates"

MODEL = "gpt-5.4-mini"
EVIDENCE_MODE = "title_abstract"

EvidenceMode = Literal["title_abstract", "full_text_sections"]

EVIDENCE_MODE_CONFIG: dict[EvidenceMode, dict[str, str]] = {
    "title_abstract": {
        "record_kind": "title/abstract record",
        "evidence_record": "provided title/abstract record",
        "evidence_scope": "title/abstract",
        "evidence_source": "title/abstract",
        "evidence_unit": "abstract",
        "short_evidence_subject": "an abstract",
        "screening_strategy": "title/abstract",
        "insufficient_evidence_phrase": "thin abstracts",
        "adjudicator_evidence_record": "provided title/abstract record plus the structured outputs from the first-pass reviewers",
        "adjudicator_evidence_scope": "title/abstract evidence",
        "adjudicator_evidence_phrase": "title/abstract or reviewer outputs",
        "adjudicator_source": "abstract and reviewer outputs",
        "full_text_mode_block": "",
    },
    "full_text_sections": {
        "record_kind": "title/abstract/full-text-section record",
        "evidence_record": "provided title, abstract, and selected full-text sections",
        "evidence_scope": "provided title, abstract, and selected full-text sections",
        "evidence_source": "provided title, abstract, and selected full-text sections",
        "evidence_unit": "provided evidence",
        "short_evidence_subject": "the provided evidence",
        "screening_strategy": "full-text-section",
        "insufficient_evidence_phrase": "insufficient selected full-text evidence",
        "adjudicator_evidence_record": "provided title, abstract, selected full-text sections, and structured outputs from the first-pass reviewers",
        "adjudicator_evidence_scope": "provided title, abstract, selected full-text sections, and reviewer outputs",
        "adjudicator_evidence_phrase": "provided title, abstract, selected full-text sections, or reviewer outputs",
        "adjudicator_source": "provided evidence and reviewer outputs",
        "full_text_mode_block": (
            "\n\nFull-text evidence mode:\n"
            "- Each record includes complete `selected_full_text_sections` extracted from Docling markdown.\n"
            "- Treat the title, abstract, and selected full-text sections as the provided record; do not use outside knowledge.\n"
            "- Use the selected full-text sections when they clarify criteria.\n"
            "- When full-text sections contradict or refine the abstract, prefer the more specific full-text section evidence and mention that section in `evidence_snippet`.\n"
            "- Do not infer from the paper title alone when the selected full-text sections do not support the criterion.\n"
        ),
    },
}

ROLE_FIELDS = {
    "scope_reviewer": [
        "paper_type",
        "bio_modality_present",
        "text_component_present",
        "text_bio_bridge_present",
        "primary_exclusion_code",
        "uncertainty_reason",
        "decision_rationale",
        "evidence_snippet",
    ],
    "architecture_reviewer": [
        "paper_type",
        "generative_model_present",
        "foundation_model_evidence",
        "primary_exclusion_code",
        "uncertainty_reason",
        "decision_rationale",
        "evidence_snippet",
    ],
    "adjudicator": [
        "paper_type",
        "bio_modality_present",
        "text_component_present",
        "text_bio_bridge_present",
        "generative_model_present",
        "foundation_model_evidence",
        "primary_exclusion_code",
        "uncertainty_reason",
        "decision_rationale",
        "evidence_snippet",
    ],
}

ALLOWED = {
    "paper_type": ["primary_model_paper", "review_editorial", "benchmark_resource", "application_wrapper", "unclear"],
    "bio_modality_present": ["yes", "no", "unclear"],
    "text_component_present": ["yes", "no", "unclear"],
    "text_bio_bridge_present": ["yes", "no", "unclear"],
    "generative_model_present": ["yes", "no", "unclear"],
    "foundation_model_evidence": ["yes", "no", "unclear"],
    "scope_exclusion": [
        "review_editorial",
        "benchmark_resource",
        "application_wrapper",
        "EC1_no_bio_modality",
        "EC2_no_text_component",
        "EC2_no_substantive_text_bio_bridge",
        "none",
    ],
    "architecture_exclusion": [
        "review_editorial",
        "benchmark_resource",
        "application_wrapper",
        "EC3_not_generative",
        "EC4_no_foundation_model_evidence",
        "none",
    ],
    "adjudicator_exclusion": [
        "review_editorial",
        "benchmark_resource",
        "application_wrapper",
        "EC1_no_bio_modality",
        "EC2_no_text_component",
        "EC2_no_substantive_text_bio_bridge",
        "EC3_not_generative",
        "EC4_no_foundation_model_evidence",
        "none",
    ],
    "scope_uncertainty": [
        "paper_type_unclear",
        "bio_modality_unclear",
        "text_component_unclear",
        "text_bio_bridge_unclear",
        "mixed_signals",
        "none",
    ],
    "architecture_uncertainty": [
        "paper_type_unclear",
        "generative_status_unclear",
        "foundation_model_evidence_unclear",
        "mixed_signals",
        "none",
    ],
    "adjudicator_uncertainty": [
        "paper_type_unclear",
        "bio_modality_unclear",
        "text_component_unclear",
        "text_bio_bridge_unclear",
        "generative_status_unclear",
        "foundation_model_evidence_unclear",
        "mixed_signals",
        "none",
    ],
}


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def safe_record(record: dict[str, Any], idx: int) -> dict[str, Any]:
    safe = {
        "record_id": record.get("record_id") or f"rec_{idx:06d}",
        "candidate_id": record.get("candidate_id", ""),
        "source_record_id": record.get("source_record_id", ""),
        "source_corpus": record.get("source_corpus", ""),
        "original_cluster_id": record.get("cluster_id"),
        "input_index": idx,
        "title": record.get("title", ""),
        "abstract": record.get("abstract", ""),
        "doi": record.get("doi", ""),
        "year": record.get("year", ""),
        "venue": record.get("venue", ""),
        "sources": record.get("sources", []),
    }
    if "selected_full_text_sections" in record:
        safe["selected_full_text_sections"] = record.get("selected_full_text_sections")
    elif "full_text_context" in record:
        # Backward compatibility for historical inputs created before the rename.
        safe["selected_full_text_sections"] = record.get("full_text_context")
    for key in ["section_evidence", "docling_markdown", "docling_chunks", "docling_status"]:
        if key in record:
            safe[key] = record.get(key)
    return safe


def chunks(items: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def strip_record_placeholder(prompt: str) -> str:
    return re.sub(r"\nRecord:\n\$\{item\}\$\s*$", "", prompt.strip(), flags=re.S)


def render_prompt_template(template: str, evidence_mode: EvidenceMode) -> str:
    values = EVIDENCE_MODE_CONFIG[evidence_mode]
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    leftover = sorted(set(re.findall(r"{{([a-zA-Z0-9_]+)}}", rendered)))
    if leftover:
        raise ValueError(f"unresolved prompt template placeholders for {evidence_mode}: {leftover}")
    return rendered


def schema_for_role(role: str, outdir: Path) -> Path:
    fields = ROLE_FIELDS[role]
    props: dict[str, Any] = {
        "record_id": {"type": "string"},
    }
    required = ["record_id"]
    for field in fields:
        if field == "primary_exclusion_code":
            if role == "scope_reviewer":
                props[field] = {"type": "string", "enum": ALLOWED["scope_exclusion"]}
            elif role == "architecture_reviewer":
                props[field] = {"type": "string", "enum": ALLOWED["architecture_exclusion"]}
            else:
                props[field] = {"type": "string", "enum": ALLOWED["adjudicator_exclusion"]}
        elif field == "uncertainty_reason":
            if role == "scope_reviewer":
                props[field] = {"type": "string", "enum": ALLOWED["scope_uncertainty"]}
            elif role == "architecture_reviewer":
                props[field] = {"type": "string", "enum": ALLOWED["architecture_uncertainty"]}
            else:
                props[field] = {"type": "string", "enum": ALLOWED["adjudicator_uncertainty"]}
        elif field in ALLOWED:
            props[field] = {"type": "string", "enum": ALLOWED[field]}
        else:
            props[field] = {"type": "string"}
        required.append(field)

    schema = {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": props,
                    "required": required,
                    "additionalProperties": False,
                },
            }
        },
        "required": ["results"],
        "additionalProperties": False,
    }
    path = outdir / "schemas" / f"{role}.schema.json"
    write_json(path, schema)
    return path


def build_role_prompt(
    role: str,
    batch: list[dict[str, Any]],
    reviewer_context: dict[str, dict[str, Any]] | None = None,
    evidence_mode: EvidenceMode = "title_abstract",
) -> str:
    prompt_file = {
        "scope_reviewer": "scope_reviewer_prompt.txt",
        "architecture_reviewer": "architecture_reviewer_prompt.txt",
        "adjudicator": "adjudicator_prompt.txt",
    }[role]
    template = strip_record_placeholder((PROMPT_DIR / prompt_file).read_text(encoding="utf-8"))
    base = render_prompt_template(template, evidence_mode)
    base += EVIDENCE_MODE_CONFIG[evidence_mode]["full_text_mode_block"]
    records = []
    for rec in batch:
        item = {
            "record_id": rec["record_id"],
            "candidate_id": rec.get("candidate_id", ""),
            "source_record_id": rec.get("source_record_id", ""),
            "source_corpus": rec.get("source_corpus", ""),
            "title": rec["title"],
            "abstract": rec["abstract"],
            "doi": rec.get("doi", ""),
            "year": rec.get("year", ""),
            "venue": rec.get("venue", ""),
            "sources": rec.get("sources", []),
        }
        if evidence_mode == "full_text_sections" and rec.get("selected_full_text_sections"):
            item["selected_full_text_sections"] = rec.get("selected_full_text_sections", "")
        if reviewer_context:
            item["first_pass_outputs"] = reviewer_context.get(rec["record_id"], {})
        records.append(item)

    return (
        f"{base}\n\n"
        "Batch execution instructions:\n"
        "- Screen every record in the JSON array below independently.\n"
        "- Return exactly one JSON object with a `results` array, with one object per input record, in the same order.\n"
        "- Include `record_id` in every object exactly as provided.\n"
        "- Include `evidence_snippet`: a short quote or paraphrased phrase from the provided evidence that supports the criterion outputs.\n"
        "- Do not include hidden chain-of-thought, step-by-step reasoning, markdown, commentary, or code fences.\n"
        "- Keep `decision_rationale` brief and evidence-grounded.\n\n"
        "Records JSON:\n"
        f"{json.dumps(records, ensure_ascii=False, separators=(',', ':'))}\n"
    )


def parse_json_response(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\{[\s\S]*\})", text)
        if not match:
            raise
        parsed = json.loads(match.group(1))
    if isinstance(parsed, dict) and isinstance(parsed.get("results"), list):
        return parsed["results"]
    if isinstance(parsed, list):
        return parsed
    raise ValueError("response is neither a JSON object with results[] nor a JSON array")


def normalize_batch_results(parsed: list[dict[str, Any]], expected_ids: list[str]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Remove repeated rows for the same record while preserving strict batch order."""
    by_id: dict[str, dict[str, Any]] = {}
    duplicate_ids: list[str] = []
    unexpected_ids: list[str] = []

    for row in parsed:
        rid = str(row.get("record_id", ""))
        if rid not in expected_ids:
            unexpected_ids.append(rid)
            continue
        if rid in by_id:
            duplicate_ids.append(rid)
            continue
        by_id[rid] = row

    normalized = [by_id[rid] for rid in expected_ids if rid in by_id]
    got_ids = [str(r.get("record_id", "")) for r in normalized]
    if got_ids != expected_ids:
        original_ids = [str(r.get("record_id", "")) for r in parsed]
        raise ValueError(f"record_id order mismatch: expected {expected_ids}, got {original_ids}")

    return normalized, duplicate_ids, unexpected_ids



def codex_batch(
    *,
    role: str,
    batch_index: int,
    batch: list[dict[str, Any]],
    outdir: Path,
    schema: Path,
    reviewer_context: dict[str, dict[str, Any]] | None = None,
    model: str = MODEL,
    evidence_mode: EvidenceMode = "title_abstract",
    timeout_s: int | None = None,
) -> dict[str, Any]:
    role_dir = outdir / "role_logs" / role
    role_dir.mkdir(parents=True, exist_ok=True)
    batch_name = f"batch_{batch_index:04d}"
    parsed_path = role_dir / f"{batch_name}.parsed.json"
    meta_path = role_dir / f"{batch_name}.meta.json"
    if parsed_path.exists():
        return {"role": role, "batch_index": batch_index, "status": "skipped", "parsed_path": str(parsed_path)}

    prompt = build_role_prompt(role, batch, reviewer_context, evidence_mode=evidence_mode)
    prompt_path = role_dir / f"{batch_name}.prompt.txt"
    raw_stdout_path = role_dir / f"{batch_name}.stdout.log"
    raw_stderr_path = role_dir / f"{batch_name}.stderr.log"
    raw_response_path = role_dir / f"{batch_name}.response.txt"
    prompt_path.write_text(prompt, encoding="utf-8")

    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as out_msg:
        out_msg_path = Path(out_msg.name)

    cmd = [
        "codex",
        "-a",
        "never",
        "exec",
        "-m",
        model,
        "--cd",
        str(ROOT),
        "--sandbox",
        "read-only",
        "--ignore-user-config",
        "--ignore-rules",
        "--ephemeral",
        "--output-schema",
        str(schema),
        "--output-last-message",
        str(out_msg_path),
        "-",
    ]
    started = time.time()
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(input=prompt, timeout=timeout_s)
    except subprocess.TimeoutExpired as exc:
        # `codex` launches a native child; terminate the whole session so a
        # timed-out batch cannot leave an orphaned model process behind.
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            # A native child can keep the inherited pipes open even after the
            # wrapper is killed. Do not wait on those pipes indefinitely.
            for stream in (proc.stdin, proc.stdout, proc.stderr):
                if stream is not None:
                    try:
                        stream.close()
                    except OSError:
                        pass
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            stdout, stderr = "", ""
        meta = {
            "created": now(),
            "role": role,
            "batch_index": batch_index,
            "record_ids": [r["record_id"] for r in batch],
            "model": model,
            "evidence_mode": evidence_mode,
            "timeout_seconds": timeout_s,
            "status": "timeout",
            "prompt_path": str(prompt_path),
        }
        write_json(meta_path, meta)
        raise RuntimeError(f"{role} {batch_name} timed out after {timeout_s}s") from exc
    elapsed = round(time.time() - started, 2)
    raw_stdout_path.write_text(stdout, encoding="utf-8")
    raw_stderr_path.write_text(stderr, encoding="utf-8")
    response_text = out_msg_path.read_text(encoding="utf-8") if out_msg_path.exists() else ""
    raw_response_path.write_text(response_text, encoding="utf-8")
    try:
        out_msg_path.unlink(missing_ok=True)
    except OSError:
        pass

    meta = {
        "created": now(),
        "role": role,
        "batch_index": batch_index,
        "record_ids": [r["record_id"] for r in batch],
        "model": model,
        "evidence_mode": evidence_mode,
        "returncode": proc.returncode,
        "elapsed_seconds": elapsed,
        "prompt_path": str(prompt_path),
        "stdout_path": str(raw_stdout_path),
        "stderr_path": str(raw_stderr_path),
        "response_path": str(raw_response_path),
    }
    if proc.returncode != 0:
        meta["status"] = "error_returncode"
        write_json(meta_path, meta)
        raise RuntimeError(f"{role} {batch_name} failed with returncode {proc.returncode}")

    try:
        parsed = parse_json_response(response_text)
        expected_ids = [r["record_id"] for r in batch]
        parsed, duplicate_ids, unexpected_ids = normalize_batch_results(parsed, expected_ids)
    except Exception as e:
        meta["status"] = "parse_error"
        meta["parse_error"] = str(e)
        write_json(meta_path, meta)
        raise

    write_json(parsed_path, parsed)
    meta["status"] = "ok"
    meta["parsed_path"] = str(parsed_path)
    if duplicate_ids:
        meta["duplicate_record_ids_removed"] = duplicate_ids
    if unexpected_ids:
        meta["unexpected_record_ids_removed"] = unexpected_ids
    write_json(meta_path, meta)
    return meta


def archive_failed_batch_attempt(outdir: Path, role: str, batch_index: int, attempt: int) -> list[str]:
    """Preserve every failed prompt/response before retrying the canonical batch path."""
    role_dir = outdir / "role_logs" / role
    batch_name = f"batch_{batch_index:04d}"
    archived: list[str] = []
    for suffix in ("prompt.txt", "stdout.log", "stderr.log", "response.txt", "meta.json"):
        source = role_dir / f"{batch_name}.{suffix}"
        if not source.exists():
            continue
        target = role_dir / f"{batch_name}.attempt_{attempt:02d}.{suffix}"
        source.replace(target)
        archived.append(str(target))
    return archived


def recover_complete_batch_by_split(
    *, max_attempts: int, failures: list[dict[str, Any]], **kwargs: Any
) -> dict[str, Any]:
    """Recover an incomplete batch without accepting any partial model response."""
    batch = list(kwargs["batch"])
    if len(batch) < 2:
        raise RuntimeError("Cannot split a one-record batch")
    midpoint = (len(batch) + 1) // 2
    parts = [batch[:midpoint], batch[midpoint:]]
    outdir = Path(kwargs["outdir"])
    role = str(kwargs["role"])
    batch_index = int(kwargs["batch_index"])
    batch_name = f"batch_{batch_index:04d}"
    recovery_root = outdir / ".batch_recovery" / role / batch_name
    recovery_root.mkdir(parents=True, exist_ok=True)
    combined: list[dict[str, Any]] = []
    recovery_logs: list[str] = []

    try:
        for part_index, part in enumerate(parts, 1):
            part_out = recovery_root / f"part_{part_index:02d}"
            part_kwargs = {
                **kwargs,
                "outdir": part_out,
                "batch": part,
                "batch_index": 1,
            }
            codex_batch_with_retries(
                max_attempts=max_attempts,
                allow_split=False,
                **part_kwargs,
            )
            part_dir = part_out / "role_logs" / role
            part_parsed = load_json(part_dir / "batch_0001.parsed.json")
            combined.extend(part_parsed)
            destination_dir = outdir / "role_logs" / role
            destination_dir.mkdir(parents=True, exist_ok=True)
            for source in sorted(part_dir.glob("batch_0001.*")):
                suffix = source.name.removeprefix("batch_0001.")
                target = destination_dir / f"recovery_{batch_name}_part_{part_index:02d}.{suffix}"
                shutil.copy2(source, target)
                recovery_logs.append(str(target))

        expected_ids = [str(row["record_id"]) for row in batch]
        combined, duplicate_ids, unexpected_ids = normalize_batch_results(combined, expected_ids)
        role_dir = outdir / "role_logs" / role
        parsed_path = role_dir / f"{batch_name}.parsed.json"
        response_path = role_dir / f"{batch_name}.response.txt"
        meta_path = role_dir / f"{batch_name}.meta.json"
        write_json(parsed_path, combined)
        response_path.write_text(json.dumps(combined, ensure_ascii=False), encoding="utf-8")
        meta = {
            "created": now(),
            "role": role,
            "batch_index": batch_index,
            "record_ids": expected_ids,
            "model": kwargs.get("model", MODEL),
            "evidence_mode": kwargs.get("evidence_mode", "title_abstract"),
            "status": "ok_recovered_by_split",
            "parsed_path": str(parsed_path),
            "response_path": str(response_path),
            "response_kind": "deterministic_merge_of_recovery_part_responses",
            "failed_full_batch_attempts": failures,
            "recovery_part_sizes": [len(part) for part in parts],
            "recovery_logs": recovery_logs,
        }
        if duplicate_ids:
            meta["duplicate_record_ids_removed"] = duplicate_ids
        if unexpected_ids:
            meta["unexpected_record_ids_removed"] = unexpected_ids
        write_json(meta_path, meta)
        return meta
    finally:
        shutil.rmtree(recovery_root, ignore_errors=True)


def codex_batch_with_retries(
    *, max_attempts: int, allow_split: bool = True, **kwargs: Any
) -> dict[str, Any]:
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    failures: list[dict[str, Any]] = []
    for attempt in range(1, max_attempts + 1):
        try:
            meta = codex_batch(**kwargs)
            if failures:
                meta_path = (
                    Path(kwargs["outdir"])
                    / "role_logs"
                    / str(kwargs["role"])
                    / f"batch_{int(kwargs['batch_index']):04d}.meta.json"
                )
                persisted = load_json(meta_path)
                persisted["attempts_total"] = attempt
                persisted["failed_attempts"] = failures
                write_json(meta_path, persisted)
                meta = persisted
            return meta
        except Exception as exc:
            archived = archive_failed_batch_attempt(
                Path(kwargs["outdir"]),
                str(kwargs["role"]),
                int(kwargs["batch_index"]),
                attempt,
            )
            failures.append({
                "attempt": attempt,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "archived_paths": archived,
            })
            if attempt == max_attempts:
                if allow_split and len(kwargs["batch"]) > 1:
                    return recover_complete_batch_by_split(
                        max_attempts=max_attempts,
                        failures=failures,
                        **kwargs,
                    )
                raise RuntimeError(
                    f"{kwargs['role']} batch_{int(kwargs['batch_index']):04d} "
                    f"failed after {max_attempts} attempts"
                ) from exc
    raise AssertionError("unreachable")


def collect_role_outputs(outdir: Path, role: str) -> dict[str, dict[str, Any]]:
    outputs: dict[str, dict[str, Any]] = {}
    for path in sorted((outdir / "role_logs" / role).glob("batch_*.parsed.json")):
        for row in load_json(path):
            outputs[str(row["record_id"])] = row
    return outputs


def provisional_from_reviewers(scope: dict[str, Any], arch: dict[str, Any]) -> dict[str, Any]:
    criteria = {
        "paper_type": scope.get("paper_type") if scope.get("paper_type") != "unclear" else arch.get("paper_type"),
        "bio_modality_present": scope.get("bio_modality_present"),
        "text_component_present": scope.get("text_component_present"),
        "text_bio_bridge_present": scope.get("text_bio_bridge_present"),
        "generative_model_present": arch.get("generative_model_present"),
        "foundation_model_evidence": arch.get("foundation_model_evidence"),
    }
    codes = [scope.get("primary_exclusion_code"), arch.get("primary_exclusion_code")]
    uncertainties = [scope.get("uncertainty_reason"), arch.get("uncertainty_reason")]
    explicit_codes = [c for c in codes if c and c != "none"]
    has_unclear = any(v == "unclear" for v in criteria.values())
    has_uncertainty = any(u and u != "none" for u in uncertainties)
    paper_types = {scope.get("paper_type"), arch.get("paper_type")} - {None, "unclear"}
    paper_type_conflict = len(paper_types) > 1

    if paper_type_conflict or has_unclear or has_uncertainty:
        return {
            "provisional_decision": "ADJUDICATE",
            "provisional_code": explicit_codes[0] if explicit_codes else "none",
            "adjudication_reason": "criterion_unclear_or_reviewer_conflict",
            **criteria,
        }
    if explicit_codes:
        return {
            "provisional_decision": "EXCLUDE",
            "provisional_code": explicit_codes[0],
            "adjudication_reason": "none",
            **criteria,
        }
    if all(v == "yes" for k, v in criteria.items() if k != "paper_type") and criteria.get("paper_type") == "primary_model_paper":
        return {
            "provisional_decision": "INCLUDE",
            "provisional_code": "none",
            "adjudication_reason": "none",
            **criteria,
        }
    return {
        "provisional_decision": "ADJUDICATE",
        "provisional_code": "none",
        "adjudication_reason": "fallback_unresolved",
        **criteria,
    }


def final_from_criteria(row: dict[str, Any]) -> tuple[str, str, str]:
    code = row.get("primary_exclusion_code") or "none"
    uncertainty = row.get("uncertainty_reason") or "none"
    if code != "none":
        return "EXCLUDE", code, uncertainty
    criteria_keys = [
        "bio_modality_present",
        "text_component_present",
        "text_bio_bridge_present",
        "generative_model_present",
        "foundation_model_evidence",
    ]
    if row.get("paper_type") == "primary_model_paper" and all(row.get(k) == "yes" for k in criteria_keys):
        return "INCLUDE", "none", uncertainty
    if any(row.get(k) == "unclear" for k in ["paper_type", *criteria_keys]) or uncertainty != "none":
        return "UNCERTAIN", "none", uncertainty
    return "UNCERTAIN", "none", "mixed_signals"


def run_role(
    role: str,
    records: list[dict[str, Any]],
    outdir: Path,
    batch_size: int,
    max_workers: int,
    reviewer_context: dict[str, dict[str, Any]] | None = None,
    model: str = MODEL,
    evidence_mode: EvidenceMode = "title_abstract",
    timeout_s: int | None = None,
    max_attempts: int = 1,
) -> None:
    schema = schema_for_role(role, outdir)
    batches = chunks(records, batch_size)
    print(f"{now()} {role}: {len(records)} records, {len(batches)} batches")
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(
                codex_batch_with_retries,
                max_attempts=max_attempts,
                role=role,
                batch_index=i,
                batch=batch,
                outdir=outdir,
                schema=schema,
                reviewer_context=reviewer_context,
                model=model,
                evidence_mode=evidence_mode,
                timeout_s=timeout_s,
            )
            for i, batch in enumerate(batches, 1)
        ]
        for fut in as_completed(futures):
            meta = fut.result()
            print(f"{now()} {role}: batch {meta['batch_index']} {meta['status']}")


def write_jsonl_from_outputs(outdir: Path, role: str, outputs: dict[str, dict[str, Any]]) -> None:
    path = outdir / f"{role}.jsonl"
    if path.exists():
        path.unlink()
    for rid in sorted(outputs, key=lambda x: int(x) if x.isdigit() else x):
        append_jsonl(path, outputs[rid])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTDIR))
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--adjudicator-batch-size", type=int, default=6)
    parser.add_argument("--max-workers", type=int, default=2)
    parser.add_argument(
        "--batch-attempts",
        type=int,
        default=3,
        help="Maximum attempts for a malformed, failed, or timed-out batch; every failed attempt is logged.",
    )
    parser.add_argument(
        "--codex-timeout",
        type=int,
        default=600,
        help="Per-batch timeout in seconds; 0 disables the timeout.",
    )
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--evidence-mode",
        choices=list(EVIDENCE_MODE_CONFIG),
        default=EVIDENCE_MODE,
        help="Evidence profile for prompt wording and record fields.",
    )
    parser.add_argument("--start-at", choices=["scope", "architecture", "gate", "adjudicator", "final"], default="scope")
    args = parser.parse_args()
    timeout_s = args.codex_timeout or None

    input_path = Path(args.input)
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    source = load_json(input_path)
    source_records = source["records"] if isinstance(source, dict) and "records" in source else source
    if not isinstance(source_records, list):
        raise ValueError("input must be a JSON array of records or an object with records[]")
    records = [safe_record(r, i) for i, r in enumerate(source_records, 1)]
    if args.limit:
        records = records[: args.limit]
    full_text_record_count = sum(1 for r in records if r.get("selected_full_text_sections") or r.get("section_evidence"))
    if args.evidence_mode == "full_text_sections" and full_text_record_count == 0:
        raise ValueError("--evidence-mode full_text_sections requires records with selected_full_text_sections or section_evidence")

    run_meta = {
        "created": now(),
        "input": str(input_path),
        "output_dir": str(outdir),
        "model": args.model,
        "evidence_mode": args.evidence_mode,
        "batch_size": args.batch_size,
        "adjudicator_batch_size": args.adjudicator_batch_size,
        "max_workers": args.max_workers,
        "batch_attempts": args.batch_attempts,
        "codex_timeout": timeout_s,
        "limit": args.limit,
        "full_text_record_count": full_text_record_count,
        "evidence_mode_config": EVIDENCE_MODE_CONFIG[args.evidence_mode],
        "protocol_files": {
            "scope_prompt": str(PROMPT_DIR / "scope_reviewer_prompt.txt"),
            "architecture_prompt": str(PROMPT_DIR / "architecture_reviewer_prompt.txt"),
            "adjudicator_prompt": str(PROMPT_DIR / "adjudicator_prompt.txt"),
            "screening_process": str(ROOT / "protocol/screening_process.md"),
            "architecture": str(ROOT / "protocol/lattereview_screening_architecture.md"),
        },
        "note": "Logs preserve prompts, raw outputs, structured criterion answers, evidence snippets, and brief rationales; prompts explicitly avoid hidden chain-of-thought.",
    }
    write_json(outdir / "run_metadata.json", run_meta)
    write_json(outdir / "input_records.json", records)

    if args.start_at == "scope":
        run_role(
            "scope_reviewer",
            records,
            outdir,
            args.batch_size,
            args.max_workers,
            model=args.model,
            evidence_mode=args.evidence_mode,
            timeout_s=timeout_s,
            max_attempts=args.batch_attempts,
        )

    if args.start_at in {"scope", "architecture"}:
        run_role(
            "architecture_reviewer",
            records,
            outdir,
            args.batch_size,
            args.max_workers,
            model=args.model,
            evidence_mode=args.evidence_mode,
            timeout_s=timeout_s,
            max_attempts=args.batch_attempts,
        )

    scope_outputs = collect_role_outputs(outdir, "scope_reviewer")
    arch_outputs = collect_role_outputs(outdir, "architecture_reviewer")
    write_jsonl_from_outputs(outdir, "scope_reviewer", scope_outputs)
    write_jsonl_from_outputs(outdir, "architecture_reviewer", arch_outputs)

    gate_rows = []
    adjudication_records = []
    reviewer_context: dict[str, dict[str, Any]] = {}
    by_id = {r["record_id"]: r for r in records}
    for rec in records:
        rid = rec["record_id"]
        scope = scope_outputs.get(rid)
        arch = arch_outputs.get(rid)
        if not scope or not arch:
            raise RuntimeError(f"missing reviewer output for record_id={rid}")
        gate = provisional_from_reviewers(scope, arch)
        row = {
            "record_id": rid,
            "title": rec["title"],
            "doi": rec.get("doi", ""),
            **gate,
            "scope": scope,
            "architecture": arch,
        }
        gate_rows.append(row)
        reviewer_context[rid] = {"scope_reviewer": scope, "architecture_reviewer": arch, "python_gate": gate}
        if gate["provisional_decision"] == "ADJUDICATE":
            adjudication_records.append(by_id[rid])
    write_json(outdir / "python_gate_outputs.json", {"records": gate_rows})
    write_json(outdir / "adjudication_queue.json", {"records": adjudication_records, "count": len(adjudication_records)})
    print(f"{now()} gate: adjudication queue {len(adjudication_records)}/{len(records)}")

    if args.start_at in {"scope", "architecture", "gate", "adjudicator"} and adjudication_records:
        run_role(
            "adjudicator",
            adjudication_records,
            outdir,
            args.adjudicator_batch_size,
            args.max_workers,
            reviewer_context=reviewer_context,
            model=args.model,
            evidence_mode=args.evidence_mode,
            timeout_s=timeout_s,
            max_attempts=args.batch_attempts,
        )

    adjudicator_outputs = collect_role_outputs(outdir, "adjudicator")
    if adjudicator_outputs:
        write_jsonl_from_outputs(outdir, "adjudicator", adjudicator_outputs)

    final_rows = []
    for row in gate_rows:
        rid = row["record_id"]
        if rid in adjudicator_outputs:
            source_row = adjudicator_outputs[rid]
            decision, code, uncertainty = final_from_criteria(source_row)
            final_source = "adjudicator"
            final_rationale = source_row.get("decision_rationale", "")
            evidence = source_row.get("evidence_snippet", "")
        elif row["provisional_decision"] == "EXCLUDE":
            decision = "EXCLUDE"
            code = row["provisional_code"]
            uncertainty = "none"
            final_source = "python_gate"
            final_rationale = "First-pass reviewers gave a decisive exclusion criterion without unresolved uncertainty."
            evidence = ""
        elif row["provisional_decision"] == "INCLUDE":
            decision = "INCLUDE"
            code = "none"
            uncertainty = "none"
            final_source = "python_gate"
            final_rationale = "All first-pass criteria were positive without unresolved uncertainty."
            evidence = ""
        else:
            decision = "UNCERTAIN"
            code = row.get("provisional_code", "none")
            uncertainty = row.get("adjudication_reason", "mixed_signals")
            final_source = "python_gate_no_adjudication"
            final_rationale = "Unresolved first-pass criteria remained without adjudicator output."
            evidence = ""
        final_rows.append({
            "record_id": rid,
            "candidate_id": by_id[rid].get("candidate_id", ""),
            "source_record_id": by_id[rid].get("source_record_id", ""),
            "source_corpus": by_id[rid].get("source_corpus", ""),
            "docling_markdown": by_id[rid].get("docling_markdown", ""),
            "title": row["title"],
            "doi": row.get("doi", ""),
            "final_decision": decision,
            "final_code": code,
            "uncertainty_reason": uncertainty,
            "final_source": final_source,
            "final_rationale": final_rationale,
            "evidence_snippet": evidence,
            "scope_primary_exclusion_code": row["scope"].get("primary_exclusion_code"),
            "scope_uncertainty_reason": row["scope"].get("uncertainty_reason"),
            "architecture_primary_exclusion_code": row["architecture"].get("primary_exclusion_code"),
            "architecture_uncertainty_reason": row["architecture"].get("uncertainty_reason"),
        })

    write_json(outdir / "final_screening_results.json", {"metadata": run_meta, "records": final_rows})
    csv_path = outdir / "final_screening_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(final_rows[0].keys()) if final_rows else [])
        writer.writeheader()
        writer.writerows(final_rows)

    counts: dict[str, int] = {}
    for row in final_rows:
        counts[row["final_decision"]] = counts.get(row["final_decision"], 0) + 1
    summary = {
        "created": now(),
        "total_records": len(final_rows),
        "decision_counts": counts,
        "adjudicated": len(adjudicator_outputs),
        "output_files": {
            "final_json": str(outdir / "final_screening_results.json"),
            "final_csv": str(csv_path),
            "scope_jsonl": str(outdir / "scope_reviewer.jsonl"),
            "architecture_jsonl": str(outdir / "architecture_reviewer.jsonl"),
            "adjudicator_jsonl": str(outdir / "adjudicator.jsonl"),
            "role_logs": str(outdir / "role_logs"),
        },
    }
    write_json(outdir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
