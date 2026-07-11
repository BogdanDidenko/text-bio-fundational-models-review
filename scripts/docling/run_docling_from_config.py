#!/usr/bin/env python3
"""Run the Docling PDF pipeline from a JSON config file."""

from __future__ import annotations

import argparse
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    settings = config.get("settings", {})
    output_root = as_path(config["output_root"])

    cmd = [
        sys.executable,
        str(RUNNER),
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
    if settings.get("skip_chunks"):
        cmd.append("--skip-chunks")

    for item in config["pdfs"]:
        pdf_path = as_path(item["path"] if isinstance(item, dict) else item)
        cmd.extend(["--pdf", str(pdf_path)])
        if isinstance(item, dict) and item.get("candidate_id"):
            cmd.extend(["--pdf-id", item["candidate_id"]])

    (output_root / "manifests").mkdir(parents=True, exist_ok=True)
    copied_config = output_root / "manifests" / "run_config.json"
    copied_config.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps({"command": cmd, "copied_config": str(copied_config)}, indent=2))
    return subprocess.run(cmd, cwd=REPO).returncode


if __name__ == "__main__":
    raise SystemExit(main())
