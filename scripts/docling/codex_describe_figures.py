#!/usr/bin/env python3
"""Describe Docling-extracted figures with Codex.

This is intentionally outside Docling's native picture-description pipeline.
Docling extracts page/figure/caption/provenance; Codex 5.5 is used as a
separate enrichment agent and the results are stored as auditable JSONL.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
DEFAULT_DOC_ROOT = REPO / "data/docling_corpus_2026-07-08"


PROMPT = """You are describing one figure from a biomedical/scientific paper for downstream retrieval.

Return concise JSON only with these fields:
- figure_type: chart, microscopy, workflow, model architecture, table-like, other
- visual_summary: what is shown
- axes_or_panels: axes, panel labels, legends, or key visual components if visible
- biological_or_model_finding: the main finding or claim visible in the figure
- retrieval_keywords: 5-12 useful keywords
- uncertainty: low, medium, or high

Use the provided caption if it helps. Do not invent details that are not visible or in the caption.
"""


def run_codex(image_path: Path, caption: str | None, model: str, timeout: int) -> dict:
    prompt = PROMPT
    if caption:
        prompt += f"\n\nCaption:\n{caption}\n"
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tmp:
        output_path = Path(tmp.name)
    try:
        cmd = [
            "codex",
            "exec",
            "--model",
            model,
            "--sandbox",
            "read-only",
            "--output-last-message",
            str(output_path),
            "--image",
            str(image_path),
            "-",
        ]
        proc = subprocess.run(
            cmd,
            cwd=REPO,
            text=True,
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        final_message = output_path.read_text(encoding="utf-8").strip()
        stderr_lines = proc.stderr.strip().splitlines()
        return {
            "returncode": proc.returncode,
            "final_message": final_message,
            "stdout_tail": "\n".join(proc.stdout.strip().splitlines()[-10:]),
            "stderr_tail": "\n".join(stderr_lines[-20:]),
        }
    finally:
        output_path.unlink(missing_ok=True)


def iter_figures(doc_root: Path):
    for manifest_path in sorted((doc_root / "figures").glob("*/figures_manifest.json")):
        figures = json.loads(manifest_path.read_text())
        for figure in figures:
            image_rel = figure.get("image_path")
            if not image_rel:
                continue
            image_path = REPO / image_rel
            if image_path.exists():
                yield manifest_path, figure, image_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc-root", type=Path, default=DEFAULT_DOC_ROOT)
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    out_dir = args.doc_root / "codex_descriptions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"figure_descriptions_{time.strftime('%Y%m%d_%H%M%S')}.jsonl"

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for manifest_path, figure, image_path in iter_figures(args.doc_root):
            if count >= args.limit:
                break
            started = time.time()
            result = {
                "candidate_id": figure.get("candidate_id"),
                "figure_index": figure.get("figure_index"),
                "image_path": str(image_path.relative_to(REPO)),
                "caption": figure.get("caption"),
                "source_figures_manifest": str(manifest_path.relative_to(REPO)),
                "model": args.model,
                "status": "started",
            }
            try:
                codex_result = run_codex(
                    image_path=image_path,
                    caption=figure.get("caption"),
                    model=args.model,
                    timeout=args.timeout,
                )
                result.update(
                    {
                        "status": "ok" if codex_result["returncode"] == 0 else "failed",
                        "codex_result": codex_result,
                    }
                )
            except Exception as exc:
                result.update({"status": "failed", "error": repr(exc)})
            result["elapsed_sec"] = round(time.time() - started, 2)
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
            print(json.dumps(result, ensure_ascii=False), flush=True)
            count += 1

    print(f"descriptions={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
