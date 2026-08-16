#!/usr/bin/env python3
"""Prepare and audit a complete living-catalog taxonomy rerun."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve(path: str | Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream) if row.get("profile_status") == "complete"]
    ids = [str(row.get("candidate_id") or "") for row in rows]
    if not all(ids) or len(set(ids)) != len(ids):
        raise RuntimeError(f"Duplicate or empty candidate IDs in {path}")
    return rows


def prepare_baseline_regeneration(
    recovery_root: Path,
    pdf_manifest_path: Path,
    output_root: Path,
    config: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    recovered = json.loads((recovery_root / "recovery_manifest.json").read_text(encoding="utf-8"))
    recovered_by_id = {row["record_id"]: row for row in recovered}
    pdf_rows = json.loads(pdf_manifest_path.read_text(encoding="utf-8"))
    documents = []
    pdf_status_counts: dict[str, int] = {}
    for row in pdf_rows:
        candidate_id = str(row.get("candidate_id") or "")
        pdf = resolve(str(row.get("canonical_pdf") or ""))
        if candidate_id not in recovered_by_id or not pdf.is_file():
            raise RuntimeError(f"Baseline recovery input is incomplete for {candidate_id}")
        status = str(row.get("recovery_status") or "unknown")
        pdf_status_counts[status] = pdf_status_counts.get(status, 0) + 1
        source = recovered_by_id[candidate_id]
        documents.append(
            {
                "path": str(pdf),
                "kind": "pdf",
                "candidate_id": candidate_id,
                "source_record_id": source.get("source_record_id", ""),
                "title": source.get("title", ""),
                "doi": source.get("doi", ""),
                "recovery_status": status,
                "source_document_sha256": sha256(pdf),
                "historical_source_document_sha256": row.get("historical_sha256", ""),
            }
        )
    profile_root = output_root / "baseline_vlm_profiles"
    run_config = {
        "name": f"full_cohort_taxonomy_rerun_baseline_regeneration_{output_root.name}",
        "created": now_iso(),
        "output_root": str(profile_root),
        "source_records": rel(recovery_root / "recovery_manifest.json"),
        "source_download_manifest": rel(pdf_manifest_path),
        "records_total": len(documents),
        "documents_total": len(documents),
        "missing_documents_total": 0,
        "settings": {
            "picture_description_backend": "openai-api",
            "openai_base_url": config["openai_compatible_endpoint"].rstrip("/") + "/chat/completions",
            "openai_model": config["models"]["vlm"],
            "picture_description_timeout": 600,
            "picture_description_concurrency": 1,
            "picture_description_max_tokens": None,
            "picture_description_temperature": 0,
            "picture_description_scale": 2,
            "picture_description_area_threshold": 0.0,
            "picture_description_prompt": (
                "Classify this extracted image as SCIENTIFIC_FIGURE or NON_SCIENTIFIC_IMAGE. "
                "For a scientific figure, describe visible panels, labels, biological source "
                "objects, transformations, model interfaces, and findings precisely for retrieval. "
                "Do not invent details."
            ),
            "skip_chunks": True,
            "max_workers": int(config.get("docling_workers", 4)),
            "do_ocr": False,
            "do_table_structure": True,
            "table_former_mode": "ACCURATE",
            "do_cell_matching": True,
            "generate_page_images": True,
            "generate_picture_images": True,
            "images_scale": 2.0,
            "do_formula_enrichment": False,
            "heading_hierarchy": {
                "enabled": True,
                "use_bookmarks": True,
                "use_numbering": True,
                "use_style": True,
            },
        },
        "documents": documents,
        "pdfs": documents,
    }
    config_path = output_root / "baseline_docling_regeneration_config.json"
    write_json(config_path, run_config)
    return config_path, {
        "records": len(documents),
        "pdf_recovery_status_counts": pdf_status_counts,
        "exact_historical_pdf_count": pdf_status_counts.get("exact_historical_pdf", 0),
        "version_or_hash_different_count": len(documents)
        - pdf_status_counts.get("exact_historical_pdf", 0),
        "planned_profile_root": rel(profile_root),
    }


def combine_manifests(paths: list[Path], output: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    owners: dict[str, Path] = {}
    fields: list[str] = []
    for path in paths:
        for row in manifest_rows(path):
            candidate_id = row["candidate_id"]
            if candidate_id in owners:
                raise RuntimeError(
                    f"Candidate {candidate_id} occurs in both {owners[candidate_id]} and {path}"
                )
            owners[candidate_id] = path
            row = {**row, "cohort_manifest_source": rel(path)}
            rows.append(row)
            for field in row:
                if field not in fields:
                    fields.append(field)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: row["candidate_id"]))
    return rows


def rerun_commands(
    manifest: Path, output_root: Path, taxonomy_root: Path, config: dict[str, Any], expected: int
) -> list[str]:
    py = str(config["docling_python"])
    model = config["models"]["graph"]
    endpoint = config["openai_compatible_endpoint"]
    workers = min(expected, int(config.get("graph_workers", 8)))
    timeout = int(config.get("taxonomy_adjudication_timeout_seconds", 3600))
    inventory = output_root / "taxonomy_synthesis/open_route_inventory.json"
    taxonomy = taxonomy_root / "taxonomy_tree.json"
    registry = output_root / "study_model_registry.csv"
    codex_model = model.removeprefix("openai/")
    commands = [
        f"mkdir -p {rel(output_root)}",
        f"python3 scripts/docling/codex_openai_compat_server.py --port {config['openai_compatible_port']} "
        f"--model {codex_model} --timeout {timeout} --cwd {ROOT} "
        f"> {rel(output_root / 'codex_wrapper.log')} 2>&1 &",
        "SERVER_PID=$!",
        "trap 'kill ${SERVER_PID} 2>/dev/null || true' EXIT",
        "SERVER_READY=0",
        "for attempt in {1..60}; do",
        f"  if python3 -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:{config['openai_compatible_port']}/health', timeout=2).read()\" >/dev/null 2>&1; then SERVER_READY=1; break; fi",
        "  if ! kill -0 ${SERVER_PID} 2>/dev/null; then break; fi",
        "  sleep 1",
        "done",
        "if [ \"${SERVER_READY}\" != 1 ]; then echo 'Codex wrapper did not become ready' >&2; exit 1; fi",
        "PIDS=()",
    ]
    for shard in range(workers):
        commands.append(
            f"{py} scripts/docling/run_docling_graph_input_taxonomy.py --stage discovery "
            f"--canonical-manifest {rel(manifest)} --expected-records {expected} "
            f"--output-dir {rel(output_root / f'runs/discovery/shard_{shard:02d}')} "
            f"--replicate-id full_cohort_open_r1 --extraction-contract direct --limit 0 "
            f"--base-url {endpoint} --model {model} --timeout {timeout} "
            f"--shard-index {shard} --shard-count {workers} &\nPIDS+=($!)"
        )
    commands.append('for pid in "${PIDS[@]}"; do wait "$pid"; done')
    commands.extend(
        [
            f"{py} scripts/docling/synthesize_input_representation_taxonomy.py --mode inventory "
            f"--discovery-root {rel(output_root / 'runs/discovery')} "
            f"--output-dir {rel(output_root / 'taxonomy_synthesis')} --expected-records {expected}",
            f"python3 scripts/docling/build_input_taxonomy_registry.py --canonical-manifest {rel(manifest)} "
            f"--output-dir {rel(output_root)} --expected-records {expected} "
            f"--prior-registry {rel(taxonomy_root / 'study_model_registry.csv')}",
        ]
    )
    direct_roots = [output_root / f"runs/classification_fixed_{replicate}" for replicate in ("r1", "r2", "r3")]
    for replicate, direct_root in zip(("r1", "r2", "r3"), direct_roots):
        commands.append("PIDS=()")
        for shard in range(workers):
            commands.append(
                f"{py} scripts/docling/classify_fixed_input_taxonomy_candidates.py "
                f"--canonical-manifest {rel(manifest)} --expected-records {expected} "
                f"--inventory {rel(inventory)} --taxonomy {rel(taxonomy)} "
                f"--output-dir {rel(direct_root / f'shard_{shard:02d}')} --replicate-id {replicate} "
                f"--prompt-version v3-interface-boundary --base-url {endpoint} --model {model} "
                f"--timeout {timeout} --shard-index {shard} --shard-count {workers} &\nPIDS+=($!)"
            )
        commands.append('for pid in "${PIDS[@]}"; do wait "$pid"; done')
    dense_root = output_root / "runs/classification_dense"
    commands.append("PIDS=()")
    for shard in range(workers):
        commands.append(
            f"{py} scripts/docling/run_docling_graph_input_taxonomy.py --stage coded "
            f"--canonical-manifest {rel(manifest)} --expected-records {expected} "
            f"--output-dir {rel(dense_root / f'shard_{shard:02d}')} --replicate-id coverage "
            f"--extraction-contract dense --dense-fill-context scoped --dense-dedupe standard "
            f"--limit 0 --base-url {endpoint} --model {model} --timeout {timeout} "
            f"--shard-index {shard} --shard-count {workers} &\nPIDS+=($!)"
        )
    commands.append('for pid in "${PIDS[@]}"; do wait "$pid"; done')
    adjudication = output_root / "adjudication"
    direct_flags = " ".join(f"--direct-run {rel(root)}" for root in direct_roots)
    commands.append("PIDS=()")
    for shard in range(workers):
        commands.append(
            f"{py} scripts/docling/adjudicate_input_taxonomy.py {direct_flags} "
            f"--dense-run {rel(dense_root)} --taxonomy {rel(taxonomy)} --inventory {rel(inventory)} "
            f"--canonical-manifest {rel(manifest)} --expected-records {expected} "
            f"--output-dir {rel(adjudication / f'shard_{shard:02d}')} --base-url {endpoint} "
            f"--model {model} --timeout {timeout} --shard-index {shard} --shard-count {workers} &\nPIDS+=($!)"
        )
    commands.append('for pid in "${PIDS[@]}"; do wait "$pid"; done')
    commands.append(
        f"python3 scripts/docling/analyze_input_taxonomy_runs.py {direct_flags} "
        f"--dense-run {rel(dense_root)} --adjudication {rel(adjudication)} "
        f"--registry {rel(registry)} --output-dir {rel(output_root)} "
        f"--expected-records {expected} --cohort-label full_living_catalog_{expected}_records "
        f"--protocol-mode full_cohort_frozen_taxonomy --taxonomy-version v1"
    )
    commands.extend(["kill ${SERVER_PID}", "wait ${SERVER_PID} 2>/dev/null || true", "trap - EXIT"])
    return commands


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, default=ROOT / "data/living_catalog/current.json")
    parser.add_argument("--pipeline-config", type=Path, default=ROOT / "config/living_review_pipeline.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--baseline-pdf-manifest",
        type=Path,
        default=ROOT / "data/source_pdf_recovery_52_2026-07-29/final_pdf_recovery_manifest.json",
    )
    args = parser.parse_args()

    state = json.loads(args.state.read_text(encoding="utf-8"))
    config = json.loads(args.pipeline_config.read_text(encoding="utf-8"))
    output_root = args.output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    checks = []
    manifest_paths: list[Path] = []
    baseline_rebuild = None
    baseline_root = resolve(state["docling_corpus_roots"][0])
    planned_baseline_manifest = output_root / "baseline_vlm_profiles/manifests/canonical_docling_profile_manifest.csv"
    for index, raw_root in enumerate(state["docling_corpus_roots"]):
        corpus_root = resolve(raw_root)
        manifest = corpus_root / "manifests/canonical_docling_profile_manifest.csv"
        if index == 0 and not manifest.is_file() and planned_baseline_manifest.is_file():
            manifest = planned_baseline_manifest
        present = manifest.is_file()
        rows = manifest_rows(manifest) if present else []
        checks.append(
            {
                "corpus_root": rel(corpus_root),
                "manifest": rel(manifest),
                "native_manifest_present": present,
                "complete_profiles": len(rows),
            }
        )
        if present:
            manifest_paths.append(manifest)

    if not checks[0]["native_manifest_present"]:
        config_path, baseline_rebuild = prepare_baseline_regeneration(
            baseline_root, args.baseline_pdf_manifest, output_root, config
        )
        checks[0]["regeneration_config"] = rel(config_path)

    snapshot_manifest = resolve(state["taxonomy_root"]) / "snapshot_manifest.json"
    expected = int(json.loads(snapshot_manifest.read_text(encoding="utf-8")).get("records") or 0)
    if expected < 1:
        raise RuntimeError(f"Snapshot has no positive record denominator: {snapshot_manifest}")
    combined = output_root / "canonical_docling_profile_manifest.csv"
    ready = len(manifest_paths) == len(state["docling_corpus_roots"])
    combined_rows: list[dict[str, str]] = []
    if ready:
        combined_rows = combine_manifests(manifest_paths, combined)
        ready = len(combined_rows) == expected
    commands = []
    if baseline_rebuild:
        commands.extend(
            [
                f"mkdir -p {rel(output_root)}",
                f"python3 scripts/docling/codex_openai_compat_server.py --port {config['openai_compatible_port']} "
                f"--model {config['models']['vlm']} --timeout 1800 --cwd {ROOT} "
                f"> {rel(output_root / 'baseline_vlm_wrapper.log')} 2>&1 &",
                "SERVER_PID=$!",
                "trap 'kill ${SERVER_PID} 2>/dev/null || true' EXIT",
                "SERVER_READY=0",
                "for attempt in {1..60}; do",
                f"  if python3 -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:{config['openai_compatible_port']}/health', timeout=2).read()\" >/dev/null 2>&1; then SERVER_READY=1; break; fi",
                "  if ! kill -0 ${SERVER_PID} 2>/dev/null; then break; fi",
                "  sleep 1",
                "done",
                "if [ \"${SERVER_READY}\" != 1 ]; then echo 'Codex wrapper did not become ready' >&2; exit 1; fi",
                f"{config['docling_python']} scripts/docling/run_docling_from_config.py "
                f"--config {rel(output_root / 'baseline_docling_regeneration_config.json')}",
                "kill ${SERVER_PID}",
                "wait ${SERVER_PID} 2>/dev/null || true",
                "trap - EXIT",
                f"python3 scripts/docling/build_canonical_vlm_profile_manifest.py "
                f"--profile-root {rel(output_root / 'baseline_vlm_profiles')} --expected-records 52",
                f"python3 scripts/prepare_full_cohort_taxonomy_rerun.py --output-dir {rel(output_root)}",
            ]
        )
    if ready:
        commands.extend(
            rerun_commands(combined, output_root / "taxonomy", resolve(state["taxonomy_root"]), config, expected)
        )
    (output_root / "commands.sh").write_text("set -euo pipefail\n\n" + "\n".join(commands) + "\n", encoding="utf-8")
    readiness = {
        "schema_version": 1,
        "created": now_iso(),
        "state": rel(args.state),
        "taxonomy_source": state["taxonomy_root"],
        "expected_records": expected,
        "ready_for_full_taxonomy_rerun": ready,
        "combined_manifest": rel(combined) if combined.is_file() else "",
        "combined_profiles": len(combined_rows),
        "corpora": checks,
        "baseline_regeneration": baseline_rebuild,
        "commands": rel(output_root / "commands.sh"),
        "blocking_reason": (
            "" if ready else "The recovered 52-record baseline lacks native Docling JSON and must be regenerated from the prepared PDF config."
        ),
    }
    write_json(output_root / "readiness.json", readiness)
    print(json.dumps(readiness, ensure_ascii=False, indent=2))
    return 0 if ready else 4


if __name__ == "__main__":
    raise SystemExit(main())
