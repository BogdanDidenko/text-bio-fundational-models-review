#!/usr/bin/env python3
"""Run the Docling PDF pipeline from a JSON config file."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / "scripts/docling/run_docling_smoke.py"


def as_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO / path


def add_optional(cmd: list[str], flag: str, value: Any) -> None:
    if value is not None:
        cmd.extend([flag, str(value)])


def runner_command(
    settings: dict[str, Any], output_root: Path, items: list[Any], manifest_name: str
) -> list[str]:
    cmd = [
        sys.executable,
        str(RUNNER),
        "--out",
        str(output_root),
        "--manifest-name",
        manifest_name,
        "--picture-description-backend",
        settings.get("picture_description_backend", "none"),
    ]
    add_optional(cmd, "--openai-base-url", settings.get("openai_base_url"))
    add_optional(cmd, "--openai-model", settings.get("openai_model"))
    add_optional(cmd, "--picture-description-timeout", settings.get("picture_description_timeout"))
    add_optional(cmd, "--picture-description-concurrency", settings.get("picture_description_concurrency"))
    add_optional(cmd, "--picture-description-max-tokens", settings.get("picture_description_max_tokens"))
    add_optional(cmd, "--picture-description-temperature", settings.get("picture_description_temperature"))
    add_optional(cmd, "--picture-description-scale", settings.get("picture_description_scale"))
    add_optional(cmd, "--picture-description-area-threshold", settings.get("picture_description_area_threshold"))
    if prompt := settings.get("picture_description_prompt"):
        cmd.extend(["--picture-description-prompt", prompt])
    if settings.get("skip_chunks"):
        cmd.append("--skip-chunks")
    for item in items:
        source = item.get("path") if isinstance(item, dict) else item
        document_path = as_path(source)
        cmd.extend(["--document", str(document_path)])
        if isinstance(item, dict) and item.get("candidate_id"):
            cmd.extend(["--document-id", item["candidate_id"]])
    return cmd


def run_one(cmd: list[str]) -> tuple[list[str], int]:
    return cmd, subprocess.run(cmd, cwd=REPO).returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    settings = config.get("settings", {})
    output_root = as_path(config["output_root"])

    items = config.get("documents") or config.get("pdfs") or []
    max_workers = max(1, int(settings.get("max_workers") or 1))
    candidate_ids = [
        str(item.get("candidate_id") or "")
        for item in items
        if isinstance(item, dict)
    ]
    if len(candidate_ids) != len(items) or not all(candidate_ids):
        raise RuntimeError("Every configured Docling document requires a nonempty candidate_id")
    if len(set(candidate_ids)) != len(candidate_ids):
        raise RuntimeError("Configured Docling documents have duplicate candidate_id values")

    (output_root / "manifests").mkdir(parents=True, exist_ok=True)
    copied_config = output_root / "manifests" / "run_config.json"
    copied_config.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    final_manifest = output_root / "manifests" / "docling_smoke_manifest.json"
    final_manifest.unlink(missing_ok=True)

    if max_workers == 1:
        cmd = runner_command(settings, output_root, items, "docling_smoke_manifest.json")
        print(json.dumps({"command": cmd, "copied_config": str(copied_config)}, indent=2))
        return subprocess.run(cmd, cwd=REPO).returncode

    commands = [
        runner_command(settings, output_root, [item], f"worker_{index:04d}.json")
        for index, item in enumerate(items)
    ]
    for stale_manifest in (output_root / "manifests").glob("worker_*.json"):
        stale_manifest.unlink()
    results: list[tuple[list[str], int]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(run_one, cmd) for cmd in commands]
        for future in as_completed(futures):
            results.append(future.result())
    manifests = []
    for path in sorted((output_root / "manifests").glob("worker_*.json")):
        manifests.append(json.loads(path.read_text(encoding="utf-8")))
    rows = [row for manifest in manifests for row in manifest.get("results", [])]
    result_ids = [str(row.get("candidate_id") or "") for row in rows]
    if len(result_ids) != len(items) or set(result_ids) != set(candidate_ids):
        raise RuntimeError(
            "Parallel Docling manifests do not contain exactly one result for every configured candidate"
        )
    merged = {
        "generated_at": max((m.get("generated_at", "") for m in manifests), default=""),
        "source": "parallel config documents",
        "output_root": str(output_root),
        "count": len(rows),
        "worker_count": max_workers,
        "results": sorted(rows, key=lambda row: str(row.get("candidate_id", ""))),
    }
    temporary_manifest = final_manifest.with_suffix(".json.tmp")
    temporary_manifest.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary_manifest.replace(final_manifest)
    print(json.dumps({"commands": len(commands), "workers": max_workers, "results": len(rows)}, indent=2))
    return 0 if all(returncode == 0 for _, returncode in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
