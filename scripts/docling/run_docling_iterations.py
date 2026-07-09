#!/usr/bin/env python3
"""Run several Docling/Codex VLM parameter iterations over the same PDFs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SMOKE_RUNNER = REPO / "scripts/docling/run_docling_smoke.py"
QA_RUNNER = REPO / "scripts/docling/analyze_docling_quality.py"


def as_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO / path


def add_optional(cmd: list[str], flag: str, value: Any) -> None:
    if value is not None:
        cmd.extend([flag, str(value)])


def merged_config(iteration_config: dict[str, Any], iteration: dict[str, Any]) -> dict[str, Any]:
    base_config: dict[str, Any] = {}
    if iteration_config.get("base_config"):
        base_path = as_path(iteration_config["base_config"])
        base_config = json.loads(base_path.read_text(encoding="utf-8"))

    settings = {}
    settings.update(base_config.get("settings", {}))
    settings.update(iteration_config.get("common_settings", {}))
    settings.update(iteration.get("settings", {}))

    pdfs = iteration.get("pdfs") or iteration_config.get("pdfs") or base_config.get("pdfs")
    if not pdfs:
        raise ValueError("No PDFs found in iteration, iteration config, or base config")

    return {
        "name": iteration.get("name"),
        "description": iteration.get("description", iteration_config.get("description", "")),
        "output_root": iteration["output_root"],
        "settings": settings,
        "pdfs": pdfs,
    }


def build_smoke_command(config: dict[str, Any]) -> list[str]:
    settings = config.get("settings", {})
    output_root = as_path(config["output_root"])
    cmd = [
        sys.executable,
        str(SMOKE_RUNNER),
        "--out",
        str(output_root),
        "--picture-description-backend",
        settings.get("picture_description_backend", "none"),
    ]
    add_optional(cmd, "--openai-base-url", settings.get("openai_base_url"))
    add_optional(cmd, "--openai-model", settings.get("openai_model"))
    add_optional(
        cmd,
        "--picture-description-timeout",
        settings.get("picture_description_timeout"),
    )
    add_optional(
        cmd,
        "--picture-description-concurrency",
        settings.get("picture_description_concurrency"),
    )
    add_optional(
        cmd,
        "--picture-description-max-tokens",
        settings.get("picture_description_max_tokens"),
    )
    add_optional(
        cmd,
        "--picture-description-temperature",
        settings.get("picture_description_temperature"),
    )
    add_optional(
        cmd,
        "--picture-description-scale",
        settings.get("picture_description_scale"),
    )
    add_optional(
        cmd,
        "--picture-description-area-threshold",
        settings.get("picture_description_area_threshold"),
    )
    prompt = settings.get("picture_description_prompt")
    if prompt:
        cmd.extend(["--picture-description-prompt", prompt])
    for item in config["pdfs"]:
        pdf_path = as_path(item["path"] if isinstance(item, dict) else item)
        cmd.extend(["--pdf", str(pdf_path)])
    return cmd


def write_effective_config(config: dict[str, Any]) -> Path:
    output_root = as_path(config["output_root"])
    manifest_dir = output_root / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    path = manifest_dir / "iteration_config.json"
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def run_qa(output_root: Path) -> int:
    return subprocess.run(
        [sys.executable, str(QA_RUNNER), "--out", str(output_root)], cwd=REPO
    ).returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    iteration_config = json.loads(args.config.read_text(encoding="utf-8"))
    wanted = set(args.only)
    failures = 0

    for iteration in iteration_config["iterations"]:
        name = iteration["name"]
        if wanted and name not in wanted:
            continue
        effective = merged_config(iteration_config, iteration)
        output_root = as_path(effective["output_root"])
        manifest_path = output_root / "manifests" / "docling_smoke_manifest.json"
        copied_config = write_effective_config(effective)
        print(
            json.dumps(
                {
                    "iteration": name,
                    "output_root": str(output_root),
                    "effective_config": str(copied_config),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if args.skip_existing and manifest_path.exists():
            print(json.dumps({"iteration": name, "status": "skipped_existing"}), flush=True)
        else:
            cmd = build_smoke_command(effective)
            print(json.dumps({"iteration": name, "command": cmd}, ensure_ascii=False), flush=True)
            rc = subprocess.run(cmd, cwd=REPO).returncode
            if rc != 0:
                failures += 1
                continue
        if manifest_path.exists():
            failures += run_qa(output_root)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
