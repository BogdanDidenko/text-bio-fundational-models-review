#!/usr/bin/env python3
"""Select full-text screening sections with a Codex LLM pass.

This is the LLM-based replacement for heading-regex section selection. It keeps
Docling markdown as the source document, but asks Codex to choose the evidence
sections from candidate headings plus short section snippets. The resulting
artifacts are intentionally similar to build_fulltext_screening_context.py so
the downstream screening runner can consume the generated input JSON directly.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

from build_fulltext_screening_context import (
    DEFAULT_INCLUDE,
    DEFAULT_UNCERTAIN,
    ROOT,
    clean_text,
    parse_markdown_sections,
    read_manifest,
    rel,
    trim,
)


MODEL = "gpt-5.4-mini"
SECTION_TYPES = [
    "data_source",
    "input_representation",
]
MAX_BY_TYPE = {
    "data_source": 1,
    "input_representation": 1,
}


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def schema_path(outdir: Path) -> Path:
    schema = {
        "type": "object",
        "properties": {
            "record_id": {"type": "string"},
            "selected_sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "section_id": {"type": "integer"},
                        "section_type": {"type": "string", "enum": SECTION_TYPES},
                        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                        "reason": {"type": "string"},
                    },
                    "required": ["section_id", "section_type", "confidence", "reason"],
                    "additionalProperties": False,
                },
            },
            "missing_targets": {
                "type": "array",
                "items": {"type": "string", "enum": SECTION_TYPES},
            },
            "selection_notes": {"type": "string"},
        },
        "required": ["record_id", "selected_sections", "missing_targets", "selection_notes"],
        "additionalProperties": False,
    }
    path = outdir / "schemas" / "section_selector.schema.json"
    write_json(path, schema)
    return path


def row_identity(row: dict[str, str], corpus: str, idx: int) -> str:
    candidate = row.get("candidate_id", "")
    rec = row.get("record_id", "")
    if candidate and rec:
        return f"{corpus}__{candidate}"
    if candidate:
        return f"{corpus}__{candidate}"
    if rec:
        return f"{corpus}__{rec}"
    return f"{corpus}__row_{idx:06d}"


def load_records(include_manifest: Path, uncertain_manifest: Path, limit: int) -> list[dict[str, str]]:
    records = []
    for corpus, path in [("include", include_manifest), ("uncertain", uncertain_manifest)]:
        for idx, row in enumerate(read_manifest(path, corpus), 1):
            records.append(
                {
                    **row,
                    "source_corpus": corpus,
                    "selector_record_id": row_identity(row, corpus, idx),
                }
            )
    if limit:
        records = records[:limit]
    return records


def candidate_sections(row: dict[str, str], snippet_chars: int) -> tuple[list[dict[str, Any]], list[Any], Path | None]:
    markdown = ROOT / row["markdown"] if row.get("markdown") else None
    if not markdown or not markdown.exists():
        return [], [], markdown
    sections = parse_markdown_sections(markdown)
    candidates: list[dict[str, Any]] = []
    for idx, section in enumerate(sections, 1):
        candidates.append(
            {
                "section_id": idx,
                "heading": section.heading,
                "heading_level": section.level,
                "line_start": section.start_line,
                "line_end": section.end_line,
                "original_chars": len(section.body),
                "snippet": trim(section.body, snippet_chars),
            }
        )
    return candidates, sections, markdown


def build_prompt(row: dict[str, str], candidates: list[dict[str, Any]]) -> str:
    prompt_record = {
        "record_id": row["selector_record_id"],
        "candidate_id": row.get("candidate_id", ""),
        "source_record_id": row.get("record_id", ""),
        "source_corpus": row.get("source_corpus", ""),
        "title": row.get("title", ""),
        "doi": row.get("doi", ""),
        "docling_markdown": row.get("markdown", ""),
        "sections": candidates,
    }
    return (
        "You are selecting evidence sections from a Docling-converted scientific paper.\n"
        "Do not decide whether the paper is included or excluded. Only choose source sections for a later screening pipeline.\n\n"
        "Select exact section_id values from the provided candidate list. Do not invent headings or line numbers.\n\n"
        "Target section types:\n"
        "- data_source: the best section describing the actual source data used by the paper: datasets, corpus, cohort, benchmark data, training/pretraining data, biological modalities, data collection, data curation, or data preprocessing. Prefer specific dataset/data sections over generic Methods. Exclude Data availability, Code availability, references, acknowledgements, author contributions, and supplementary-file availability unless they contain the substantive dataset description.\n"
        "- input_representation: the best section describing how the model represents or consumes the data: model inputs, tokenization, prompts, feature construction, sequence/cell/gene representation, embeddings, text-bio pairing, image/omics representation, or input-output formulation. Do not select architecture, objective, supervised training, or generic methods sections unless the snippet directly states the input representation. If an architecture section is selected, the reason must identify the exact input-representation evidence.\n\n"
        "Selection limits:\n"
        "- data_source: at most 1 section.\n"
        "- input_representation: at most 1 section.\n\n"
        "Use the heading and snippet together. A nonstandard heading can still be selected if the snippet clearly contains the target evidence.\n"
        "Be precision-heavy: for this screening round we only need data_source and input_representation, not abstract, introduction, discussion, general architecture, objective, or training evidence.\n"
        "If a target is absent, list it in missing_targets. Keep reasons brief and evidence-grounded.\n\n"
        "Return only JSON matching the provided schema.\n\n"
        "Record JSON:\n"
        f"{json.dumps(prompt_record, ensure_ascii=False, separators=(',', ':'))}\n"
    )


def parse_json_response(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\{[\s\S]*\})", text)
        if not match:
            raise
        parsed = json.loads(match.group(1))
    if not isinstance(parsed, dict):
        raise ValueError("selector response is not a JSON object")
    return parsed


def normalize_selection(parsed: dict[str, Any], expected_id: str, candidate_ids: set[int]) -> dict[str, Any]:
    if parsed.get("record_id") != expected_id:
        parsed["record_id_returned"] = parsed.get("record_id", "")
        parsed["record_id"] = expected_id

    selected = []
    seen: set[tuple[int, str]] = set()
    counts: Counter[str] = Counter()
    invalid: list[Any] = []
    over_limit: list[Any] = []
    for item in parsed.get("selected_sections", []):
        try:
            sid = int(item.get("section_id"))
        except (TypeError, ValueError):
            invalid.append(item)
            continue
        stype = str(item.get("section_type", ""))
        if sid not in candidate_ids or stype not in SECTION_TYPES:
            invalid.append(item)
            continue
        if counts[stype] >= MAX_BY_TYPE[stype]:
            over_limit.append(item)
            continue
        key = (sid, stype)
        if key in seen:
            continue
        seen.add(key)
        counts[stype] += 1
        selected.append(
            {
                "section_id": sid,
                "section_type": stype,
                "confidence": item.get("confidence", "low"),
                "reason": clean_text(str(item.get("reason", "")))[:500],
            }
        )
    parsed["selected_sections"] = selected
    parsed["missing_targets"] = [x for x in parsed.get("missing_targets", []) if x in SECTION_TYPES]
    if invalid:
        parsed["invalid_selections_removed"] = invalid
    if over_limit:
        parsed["over_limit_selections_removed"] = over_limit
    return parsed


def run_selector(
    *,
    row: dict[str, str],
    candidates: list[dict[str, Any]],
    outdir: Path,
    schema: Path,
    model: str,
) -> dict[str, Any]:
    record_id = row["selector_record_id"]
    log_dir = outdir / "llm_section_selector_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", record_id)[:180]
    prompt_path = log_dir / f"{safe_name}.prompt.txt"
    response_path = log_dir / f"{safe_name}.response.txt"
    stdout_path = log_dir / f"{safe_name}.stdout.log"
    stderr_path = log_dir / f"{safe_name}.stderr.log"
    parsed_path = log_dir / f"{safe_name}.parsed.json"
    meta_path = log_dir / f"{safe_name}.meta.json"
    if parsed_path.exists():
        parsed = json.loads(parsed_path.read_text(encoding="utf-8"))
        return {"record_id": record_id, "status": "skipped", "parsed": parsed}

    prompt = build_prompt(row, candidates)
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
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    response_text = out_msg_path.read_text(encoding="utf-8") if out_msg_path.exists() else ""
    response_path.write_text(response_text, encoding="utf-8")
    try:
        out_msg_path.unlink(missing_ok=True)
    except OSError:
        pass

    meta = {
        "created": now(),
        "record_id": record_id,
        "candidate_id": row.get("candidate_id", ""),
        "source_record_id": row.get("record_id", ""),
        "source_corpus": row.get("source_corpus", ""),
        "model": model,
        "returncode": proc.returncode,
        "elapsed_seconds": elapsed,
        "candidate_section_count": len(candidates),
        "prompt_path": str(prompt_path),
        "response_path": str(response_path),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }
    if proc.returncode != 0:
        meta["status"] = "error_returncode"
        write_json(meta_path, meta)
        raise RuntimeError(f"section selector failed for {record_id} with returncode {proc.returncode}")

    parsed = normalize_selection(parse_json_response(response_text), record_id, {c["section_id"] for c in candidates})
    write_json(parsed_path, parsed)
    meta["status"] = "ok"
    meta["parsed_path"] = str(parsed_path)
    write_json(meta_path, meta)
    return {"record_id": record_id, "status": "ok", "parsed": parsed}


def build_screening_payload(
    row: dict[str, str],
    selection: dict[str, Any],
    candidates: list[dict[str, Any]],
    sections: list[Any],
    markdown: Path | None,
    max_section_chars: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    by_id = {c["section_id"]: (c, sections[c["section_id"] - 1]) for c in candidates}
    selected = []
    for item in selection.get("selected_sections", []):
        pair = by_id.get(item["section_id"])
        if not pair:
            continue
        cand, section = pair
        selected.append(
            {
                "section_type": item["section_type"],
                "heading": section.heading,
                "heading_level": section.level,
                "line_start": section.start_line,
                "line_end": section.end_line,
                "text": trim(section.body, max_section_chars),
                "original_chars": len(section.body),
                "selector_section_id": item["section_id"],
                "selector_confidence": item.get("confidence", ""),
            }
        )

    context = "\n\n".join(f"[{item['section_type']}: {item['heading']}]\n{item['text']}" for item in selected)
    abstract_text = ""
    for section in sections:
        if section.heading.strip().lower() in {"abstract", "summary"}:
            abstract_text = trim(section.body, max_section_chars)
            break
    record_id = row["selector_record_id"]
    payload = {
        "record_id": record_id,
        "candidate_id": row.get("candidate_id", ""),
        "source_record_id": row.get("record_id", ""),
        "source_corpus": row.get("source_corpus", ""),
        "title": row.get("title", ""),
        "abstract": abstract_text,
        "doi": row.get("doi", ""),
        "year": row.get("year", ""),
        "venue": row.get("venue", ""),
        "sources": [],
        "full_text_context": context,
        "section_evidence": selected,
        "docling_markdown": rel(markdown) if markdown else "",
        "docling_chunks": row.get("chunks", ""),
        "docling_status": row.get("final_docling_status", ""),
        "section_selector_model": selection.get("model", ""),
    }
    audit = {
        "record_id": record_id,
        "candidate_id": row.get("candidate_id", ""),
        "source_record_id": row.get("record_id", ""),
        "source_corpus": row.get("source_corpus", ""),
        "title": row.get("title", ""),
        "status": "ok" if selected else "no_selected_sections",
        "markdown": rel(markdown) if markdown else "",
        "selected": [{k: v for k, v in item.items() if k != "text"} for item in selected],
        "missing_targets": selection.get("missing_targets", []),
        "selection_notes": selection.get("selection_notes", ""),
        "all_headings": [s.heading for s in sections],
    }
    return payload, audit


def write_audit_markdown(outdir: Path, rows: list[dict[str, Any]], summary: dict[str, Any], model: str) -> None:
    lines = [
        "# LLM Full-Text Section Selection Audit",
        "",
        "This run replaces heading-regex section selection with a schema-enforced Codex selector.",
        "Docling markdown remains the source document. The LLM receives title, DOI, every parsed section heading, line range, and a short section snippet; it returns exact section ids for the downstream screening context.",
        "",
        "## Configuration",
        "",
        f"- Model: `{model}`",
        "- Selector output schema: `schemas/section_selector.schema.json`",
        "- Per-record logs: `llm_section_selector_logs/*.prompt.txt`, `*.response.txt`, `*.parsed.json`, `*.meta.json`",
        "- Downstream input: `fulltext_screening_input.json`",
        "- Section audit: `fulltext_section_audit.jsonl` and `fulltext_section_audit.csv`",
        "",
        "## Summary",
        "",
        f"- Records processed: **{summary['records']}**",
        f"- Records with selected sections: **{summary['records_with_selected_sections']}**",
        f"- Fallback document openings: **{summary['fallback_document_opening']}**",
        "",
        "## Section Type Counts",
        "",
        "| Section type | Instances | Records with type |",
        "|---|---:|---:|",
    ]
    for item in summary["section_type_counts"]:
        lines.append(f"| `{item['section_type']}` | {item['instances']} | {item['records']} |")
    lines.extend(
        [
            "",
            "## Top Headings",
            "",
            "| Section type | Heading | Occurrences |",
            "|---|---|---:|",
        ]
    )
    for item in summary["top_headings"][:40]:
        lines.append(f"| `{item['section_type']}` | {item['heading']} | {item['occurrences']} |")
    lines.append("")
    (outdir / "LLM_SECTION_SELECTION_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-manifest", default=str(DEFAULT_INCLUDE))
    parser.add_argument("--uncertain-manifest", default=str(DEFAULT_UNCERTAIN))
    parser.add_argument("--output-dir", default=str(ROOT / "data/fulltext_screening_context_2026-07-09_llm_sections"))
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--snippet-chars", type=int, default=700)
    parser.add_argument(
        "--max-section-chars",
        type=int,
        default=0,
        help="Maximum characters per selected section; 0 keeps full selected sections.",
    )
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    schema = schema_path(outdir)
    rows = load_records(Path(args.include_manifest), Path(args.uncertain_manifest), args.limit)
    for generated in [
        outdir / "llm_section_selections.jsonl",
        outdir / "fulltext_section_audit.jsonl",
    ]:
        generated.unlink(missing_ok=True)

    prepared: dict[str, tuple[dict[str, str], list[dict[str, Any]], list[Any], Path | None]] = {}
    for row in rows:
        candidates, sections, markdown = candidate_sections(row, args.snippet_chars)
        prepared[row["selector_record_id"]] = (row, candidates, sections, markdown)

    print(f"{now()} selector: {len(rows)} records, model={args.model}, workers={args.max_workers}")
    selections: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = []
        for row in rows:
            candidates = prepared[row["selector_record_id"]][1]
            if not candidates:
                selections[row["selector_record_id"]] = {
                    "record_id": row["selector_record_id"],
                    "selected_sections": [],
                    "missing_targets": SECTION_TYPES,
                    "selection_notes": "No Docling markdown sections were available.",
                }
                continue
            futures.append(
                pool.submit(
                    run_selector,
                    row=row,
                    candidates=candidates,
                    outdir=outdir,
                    schema=schema,
                    model=args.model,
                )
            )
        for fut in as_completed(futures):
            result = fut.result()
            parsed = result["parsed"]
            parsed["model"] = args.model
            selections[result["record_id"]] = parsed
            print(f"{now()} selector: {result['record_id']} {result['status']} sections={len(parsed.get('selected_sections', []))}")

    input_records = []
    audit_rows = []
    audit_csv_rows = []
    section_instances = []
    for row in rows:
        rid = row["selector_record_id"]
        original_row, candidates, sections, markdown = prepared[rid]
        selection = selections[rid]
        payload, audit = build_screening_payload(original_row, selection, candidates, sections, markdown, args.max_section_chars)
        input_records.append(payload)
        audit_rows.append(audit)
        append_jsonl(outdir / "llm_section_selections.jsonl", selection)
        append_jsonl(outdir / "fulltext_section_audit.jsonl", audit)
        selected = audit.get("selected", [])
        by_type: dict[str, list[str]] = {}
        for item in selected:
            by_type.setdefault(item["section_type"], []).append(item["heading"])
            section_instances.append(
                {
                    "record_id": rid,
                    "candidate_id": row.get("candidate_id", ""),
                    "source_record_id": row.get("record_id", ""),
                    "source_corpus": row.get("source_corpus", ""),
                    **item,
                }
            )
        audit_csv_rows.append(
            {
                "record_id": rid,
                "candidate_id": row.get("candidate_id", ""),
                "source_record_id": row.get("record_id", ""),
                "source_corpus": row.get("source_corpus", ""),
                "title": row.get("title", ""),
                "status": audit["status"],
                "selected_section_count": len(selected),
                "data_source_headings": " | ".join(by_type.get("data_source", [])),
                "input_representation_headings": " | ".join(by_type.get("input_representation", [])),
                "document_opening_headings": " | ".join(by_type.get("document_opening", [])),
                "missing_targets": " | ".join(audit.get("missing_targets", [])),
                "markdown": audit.get("markdown", ""),
            }
        )

    write_json(outdir / "fulltext_screening_input.json", input_records)
    write_json(outdir / "run_metadata.json", {
        "created": now(),
        "model": args.model,
        "records": len(input_records),
        "include_manifest": rel(args.include_manifest),
        "uncertain_manifest": rel(args.uncertain_manifest),
        "snippet_chars": args.snippet_chars,
        "max_section_chars": args.max_section_chars,
    })
    write_csv(
        outdir / "fulltext_section_audit.csv",
        audit_csv_rows,
        [
            "record_id",
            "candidate_id",
            "source_record_id",
            "source_corpus",
            "title",
            "status",
            "selected_section_count",
            "data_source_headings",
            "input_representation_headings",
            "document_opening_headings",
            "missing_targets",
            "markdown",
        ],
    )
    write_csv(
        outdir / "section_instances.csv",
        section_instances,
        [
            "record_id",
            "candidate_id",
            "source_record_id",
            "source_corpus",
            "section_type",
            "heading",
            "heading_level",
            "line_start",
            "line_end",
            "original_chars",
            "selector_section_id",
            "selector_confidence",
            "selector_reason",
        ],
    )

    type_instances: Counter[str] = Counter()
    type_records: dict[str, set[str]] = {k: set() for k in [*SECTION_TYPES, "document_opening"]}
    heading_counter: Counter[tuple[str, str]] = Counter()
    for inst in section_instances:
        stype = str(inst["section_type"])
        type_instances[stype] += 1
        type_records.setdefault(stype, set()).add(str(inst["record_id"]))
        heading_counter[(stype, str(inst["heading"]))] += 1
    summary = {
        "records": len(input_records),
        "records_with_selected_sections": sum(1 for row in audit_rows if row.get("selected")),
        "fallback_document_opening": sum(1 for row in audit_rows if row.get("status") == "fallback_document_opening"),
        "section_type_counts": [
            {"section_type": stype, "instances": type_instances[stype], "records": len(type_records.get(stype, set()))}
            for stype in sorted(type_instances)
        ],
        "top_headings": [
            {"section_type": stype, "heading": heading, "occurrences": count}
            for (stype, heading), count in heading_counter.most_common(80)
        ],
    }
    write_json(outdir / "summary.json", summary)
    write_audit_markdown(outdir, audit_rows, summary, args.model)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
