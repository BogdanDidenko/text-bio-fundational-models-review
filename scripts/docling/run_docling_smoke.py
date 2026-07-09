#!/usr/bin/env python3
"""Run a small Docling smoke pass over downloaded review PDFs.

Outputs are intentionally separate from the full-text download tree:

  data/docling_corpus_2026-07-08/
    documents/*.docling.json
    markdown/*.md
    chunks/*.jsonl
    figures/<candidate_id>/*.png
    manifests/docling_smoke_manifest.json

By default this pass does not call a VLM for figure descriptions. If
`--picture-description-backend openai-api` is set, Docling's native picture
description stage calls an OpenAI-compatible API during conversion and stores
the descriptions inside the DoclingDocument.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    PictureDescriptionVlmEngineOptions,
    ResponseFormat,
    TableFormerMode,
)
from docling.datamodel.stage_model_specs import ApiModelConfig, VlmModelSpec
from docling.datamodel.vlm_engine_options import ApiVlmEngineOptions, VlmEngineType
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker


REPO = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO / "data/full_text_downloads_2026-07-07"
DEFAULT_OUT = REPO / "data/docling_corpus_2026-07-08"


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def candidate_id_from_path(path: Path) -> str:
    for part in path.parts:
        if "__rec_" in part:
            return part.split("__", 2)[0] + "__" + part.split("__", 2)[1]
        if part.startswith("june_update_") or part.startswith("july_update_"):
            pieces = part.split("__")
            if len(pieces) >= 2 and pieces[1].startswith("rec_"):
                return pieces[0] + "__" + pieces[1]
    return slug(path.stem, 80)


def slug(text: str, limit: int = 96) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")
    return value[:limit] or "document"


def pick_pdfs(source: Path, limit: int) -> list[Path]:
    pdfs = sorted(
        [p for p in source.rglob("*.pdf") if p.is_file() and p.stat().st_size > 100_000],
        key=lambda p: (p.stat().st_size, str(p)),
    )
    # Keep the smoke representative but bounded: include small/medium PDFs and
    # skip very large theses or image-heavy PDFs for the first pass.
    bounded = [p for p in pdfs if p.stat().st_size <= 6_000_000]
    return bounded[:limit]


SCIENTIFIC_FIGURE_PROMPT = (
    "This is a figure from a biomedical or scientific paper. Describe it for "
    "retrieval. Include: figure type; visible axes, panels, labels, or legend; "
    "what biological/model quantity is measured or shown; and the main finding "
    "visible in the figure. Be precise and concise. Do not invent details."
)


def make_converter(args: argparse.Namespace) -> DocumentConverter:
    opts = PdfPipelineOptions()
    opts.do_ocr = False
    opts.enable_remote_services = args.picture_description_backend != "none"
    opts.do_table_structure = True
    opts.table_structure_options.mode = TableFormerMode.ACCURATE
    opts.table_structure_options.do_cell_matching = True
    opts.generate_page_images = True
    opts.generate_picture_images = True
    opts.images_scale = 2.0
    opts.do_picture_classification = False
    opts.do_picture_description = args.picture_description_backend != "none"
    if args.picture_description_backend == "openai-api":
        api_key = os.environ.get("OPENAI_API_KEY")
        parsed_url = urlparse(args.openai_base_url)
        is_local_url = parsed_url.hostname in {"127.0.0.1", "localhost", "::1"}
        if not api_key and not is_local_url:
            raise RuntimeError(
                "OPENAI_API_KEY is required for --picture-description-backend openai-api"
            )
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        model_spec = VlmModelSpec(
            name=f"Codex via OpenAI-compatible API ({args.openai_model})",
            default_repo_id="codex-openai-compatible",
            prompt=args.picture_description_prompt or SCIENTIFIC_FIGURE_PROMPT,
            response_format=ResponseFormat.PLAINTEXT,
            supported_engines={VlmEngineType.API_OPENAI},
            api_overrides={
                VlmEngineType.API_OPENAI: ApiModelConfig(
                    params={"model": args.openai_model}
                )
            },
            temperature=args.picture_description_temperature,
            max_new_tokens=args.picture_description_max_tokens,
        )
        opts.picture_description_options = PictureDescriptionVlmEngineOptions(
            engine_options=ApiVlmEngineOptions(
                engine_type=VlmEngineType.API_OPENAI,
                url=args.openai_base_url,
                headers=headers,
                params={
                    "model": args.openai_model,
                    "temperature": args.picture_description_temperature,
                    "max_tokens": args.picture_description_max_tokens,
                    "usage_response_key": "usage",
                },
                timeout=args.picture_description_timeout,
                concurrency=args.picture_description_concurrency,
            ),
            model_spec=model_spec,
            prompt=args.picture_description_prompt or SCIENTIFIC_FIGURE_PROMPT,
            generation_config={
                "max_new_tokens": args.picture_description_max_tokens,
                "do_sample": False,
                "temperature": args.picture_description_temperature,
            },
            scale=args.picture_description_scale,
            picture_area_threshold=args.picture_description_area_threshold,
            batch_size=args.picture_description_concurrency,
        )
    opts.do_formula_enrichment = False
    opts.generate_parsed_pages = True
    opts.heading_hierarchy_options.enabled = True
    opts.heading_hierarchy_options.use_bookmarks = True
    opts.heading_hierarchy_options.use_numbering = True
    opts.heading_hierarchy_options.use_style = True

    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )


def safe_model_dump(obj: Any) -> Any:
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, list):
        return [safe_model_dump(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): safe_model_dump(v) for k, v in obj.items()}
    return repr(obj)


def extract_figures(doc: Any, candidate_id: str, figures_dir: Path) -> list[dict[str, Any]]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for i, pic in enumerate(getattr(doc, "pictures", []) or [], start=1):
        row: dict[str, Any] = {
            "figure_index": i,
            "candidate_id": candidate_id,
            "caption": None,
            "page_no": None,
            "bbox": None,
            "image_path": None,
            "annotations": safe_model_dump(getattr(pic, "annotations", [])),
            "meta": safe_model_dump(getattr(pic, "meta", None)),
        }
        try:
            row["caption"] = pic.caption_text(doc=doc)
        except Exception:
            row["caption"] = None
        try:
            if getattr(pic, "prov", None):
                row["page_no"] = pic.prov[0].page_no
                row["bbox"] = safe_model_dump(pic.prov[0].bbox)
        except Exception:
            pass
        try:
            image = pic.get_image(doc)
            if image is not None:
                image_path = figures_dir / f"figure_{i:03d}.png"
                image.save(image_path)
                row["image_path"] = str(image_path.relative_to(REPO))
        except Exception as exc:
            row["image_error"] = repr(exc)
        rows.append(row)
    return rows


def write_chunks(doc: Any, candidate_id: str, path: Path) -> int:
    chunker = HybridChunker(merge_peers=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for count, chunk in enumerate(chunker.chunk(dl_doc=doc), start=1):
            headings = getattr(getattr(chunk, "meta", None), "headings", None)
            doc_items = getattr(getattr(chunk, "meta", None), "doc_items", None)
            pages = []
            for item in doc_items or []:
                for prov in getattr(item, "prov", []) or []:
                    page = getattr(prov, "page_no", None)
                    if page is not None:
                        pages.append(page)
            row = {
                "candidate_id": candidate_id,
                "chunk_index": count,
                "text": getattr(chunk, "text", ""),
                "contextualized_text": chunker.contextualize(chunk=chunk),
                "headings": headings,
                "pages": sorted(set(pages)),
                "meta": safe_model_dump(getattr(chunk, "meta", None)),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--pdf", action="append", type=Path, default=[])
    parser.add_argument(
        "--pdf-id",
        action="append",
        default=[],
        help=(
            "Explicit candidate id for each --pdf, in the same order. "
            "Falls back to deriving ids from paths when omitted."
        ),
    )
    parser.add_argument(
        "--picture-description-backend",
        choices=["none", "openai-api"],
        default="none",
        help="Run Docling native picture-description enrichment during conversion.",
    )
    parser.add_argument(
        "--openai-base-url",
        default=os.environ.get(
            "OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions"
        ),
    )
    parser.add_argument("--openai-model", default="gpt-5.5")
    parser.add_argument("--picture-description-timeout", type=float, default=120.0)
    parser.add_argument("--picture-description-concurrency", type=int, default=1)
    parser.add_argument("--picture-description-max-tokens", type=int, default=500)
    parser.add_argument("--picture-description-temperature", type=float, default=0.0)
    parser.add_argument("--picture-description-scale", type=float, default=2.0)
    parser.add_argument("--picture-description-area-threshold", type=float, default=0.05)
    parser.add_argument("--picture-description-prompt", default="")
    args = parser.parse_args()

    out = args.out.resolve()
    for name in ["documents", "markdown", "chunks", "figures", "manifests", "logs"]:
        (out / name).mkdir(parents=True, exist_ok=True)

    pdfs = args.pdf or pick_pdfs(args.source, args.limit)
    if args.pdf_id and len(args.pdf_id) != len(pdfs):
        raise ValueError("--pdf-id count must match --pdf count")
    converter = make_converter(args)
    manifest_rows: list[dict[str, Any]] = []

    for index, pdf in enumerate(pdfs):
        pdf = pdf.resolve()
        candidate_id = args.pdf_id[index] if args.pdf_id else candidate_id_from_path(pdf)
        started = time.time()
        row: dict[str, Any] = {
            "candidate_id": candidate_id,
            "source_pdf": str(pdf.relative_to(REPO) if pdf.is_relative_to(REPO) else pdf),
            "pdf_bytes": pdf.stat().st_size,
            "pdf_sha256": sha256_path(pdf),
            "picture_description_backend": args.picture_description_backend,
            "picture_description_model": (
                args.openai_model
                if args.picture_description_backend == "openai-api"
                else None
            ),
            "status": "started",
        }
        try:
            result = converter.convert(pdf)
            doc = result.document
            stem = slug(candidate_id)
            doc_json = out / "documents" / f"{stem}.docling.json"
            markdown = out / "markdown" / f"{stem}.md"
            chunks = out / "chunks" / f"{stem}.jsonl"
            figures_dir = out / "figures" / stem

            doc.save_as_json(doc_json)
            markdown.write_text(doc.export_to_markdown(), encoding="utf-8")
            chunk_count = write_chunks(doc, candidate_id, chunks)
            figures = extract_figures(doc, candidate_id, figures_dir)
            (figures_dir / "figures_manifest.json").write_text(
                json.dumps(figures, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            row.update(
                {
                    "status": "ok",
                    "docling_json": str(doc_json.relative_to(REPO)),
                    "markdown": str(markdown.relative_to(REPO)),
                    "chunks": str(chunks.relative_to(REPO)),
                    "chunk_count": chunk_count,
                    "figure_count": len(figures),
                    "figures_manifest": str(
                        (figures_dir / "figures_manifest.json").relative_to(REPO)
                    ),
                }
            )
        except Exception as exc:
            row.update({"status": "failed", "error": repr(exc)})
        finally:
            row["elapsed_sec"] = round(time.time() - started, 2)
            manifest_rows.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)

    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source": str(args.source),
        "output_root": str(out),
        "count": len(manifest_rows),
        "results": manifest_rows,
    }
    manifest_path = out / "manifests" / "docling_smoke_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"manifest={manifest_path}")
    return 0 if all(r["status"] == "ok" for r in manifest_rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
