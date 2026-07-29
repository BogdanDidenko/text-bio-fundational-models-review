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
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/dedup_update_2026-06-10/new_records_screening_ready_crossref_checked.json"
DEFAULT_OUTDIR = ROOT / "data/screening_codex_2026-06-10"
PROMPT_DIR = ROOT / "protocol/screening_prompt_templates"

MODEL = "gpt-5.4-mini"

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
    return {
        "record_id": f"rec_{idx:06d}",
        "original_cluster_id": record.get("cluster_id"),
        "input_index": idx,
        "title": record.get("title", ""),
        "abstract": record.get("abstract", ""),
        "doi": record.get("doi", ""),
        "year": record.get("year", ""),
        "venue": record.get("venue", ""),
        "sources": record.get("sources", []),
    }


def chunks(items: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def strip_record_placeholder(prompt: str) -> str:
    return re.sub(r"\nRecord:\n\$\{item\}\$\s*$", "", prompt.strip(), flags=re.S)


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


def build_role_prompt(role: str, batch: list[dict[str, Any]], reviewer_context: dict[str, dict[str, Any]] | None = None) -> str:
    prompt_file = {
        "scope_reviewer": "scope_reviewer_prompt.txt",
        "architecture_reviewer": "architecture_reviewer_prompt.txt",
        "adjudicator": "adjudicator_prompt.txt",
    }[role]
    base = strip_record_placeholder((PROMPT_DIR / prompt_file).read_text(encoding="utf-8"))
    records = []
    for rec in batch:
        item = {
            "record_id": rec["record_id"],
            "title": rec["title"],
            "abstract": rec["abstract"],
            "doi": rec.get("doi", ""),
            "year": rec.get("year", ""),
            "venue": rec.get("venue", ""),
            "sources": rec.get("sources", []),
        }
        if reviewer_context:
            item["first_pass_outputs"] = reviewer_context.get(rec["record_id"], {})
        records.append(item)

    return (
        f"{base}\n\n"
        "Batch execution instructions:\n"
        "- Screen every record in the JSON array below independently.\n"
        "- Return exactly one JSON object with a `results` array, with one object per input record, in the same order.\n"
        "- Include `record_id` in every object exactly as provided.\n"
        "- Include `evidence_snippet`: a short quote or paraphrased phrase from the title/abstract that supports the criterion outputs.\n"
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


def codex_batch(
    *,
    role: str,
    batch_index: int,
    batch: list[dict[str, Any]],
    outdir: Path,
    schema: Path,
    reviewer_context: dict[str, dict[str, Any]] | None = None,
    model: str = MODEL,
) -> dict[str, Any]:
    role_dir = outdir / "role_logs" / role
    role_dir.mkdir(parents=True, exist_ok=True)
    batch_name = f"batch_{batch_index:04d}"
    parsed_path = role_dir / f"{batch_name}.parsed.json"
    meta_path = role_dir / f"{batch_name}.meta.json"
    if parsed_path.exists():
        return {"role": role, "batch_index": batch_index, "status": "skipped", "parsed_path": str(parsed_path)}

    prompt = build_role_prompt(role, batch, reviewer_context)
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
    proc = subprocess.run(cmd, input=prompt, text=True, capture_output=True)
    elapsed = round(time.time() - started, 2)
    raw_stdout_path.write_text(proc.stdout, encoding="utf-8")
    raw_stderr_path.write_text(proc.stderr, encoding="utf-8")
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
        got_ids = [str(r.get("record_id", "")) for r in parsed]
        if got_ids != expected_ids:
            raise ValueError(f"record_id order mismatch: expected {expected_ids}, got {got_ids}")
    except Exception as e:
        meta["status"] = "parse_error"
        meta["parse_error"] = str(e)
        write_json(meta_path, meta)
        raise

    write_json(parsed_path, parsed)
    meta["status"] = "ok"
    meta["parsed_path"] = str(parsed_path)
    write_json(meta_path, meta)
    return meta


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
) -> None:
    schema = schema_for_role(role, outdir)
    batches = chunks(records, batch_size)
    print(f"{now()} {role}: {len(records)} records, {len(batches)} batches")
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(
                codex_batch,
                role=role,
                batch_index=i,
                batch=batch,
                outdir=outdir,
                schema=schema,
                reviewer_context=reviewer_context,
                model=model,
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
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--start-at", choices=["scope", "architecture", "gate", "adjudicator", "final"], default="scope")
    args = parser.parse_args()

    input_path = Path(args.input)
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    source = load_json(input_path)
    records = [safe_record(r, i) for i, r in enumerate(source["records"], 1)]
    if args.limit:
        records = records[: args.limit]

    run_meta = {
        "created": now(),
        "input": str(input_path),
        "output_dir": str(outdir),
        "model": args.model,
        "batch_size": args.batch_size,
        "adjudicator_batch_size": args.adjudicator_batch_size,
        "max_workers": args.max_workers,
        "limit": args.limit,
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
        run_role("scope_reviewer", records, outdir, args.batch_size, args.max_workers, model=args.model)

    if args.start_at in {"scope", "architecture"}:
        run_role("architecture_reviewer", records, outdir, args.batch_size, args.max_workers, model=args.model)

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
