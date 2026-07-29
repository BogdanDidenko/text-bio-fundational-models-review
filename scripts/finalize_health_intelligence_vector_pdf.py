#!/usr/bin/env python3
"""Replace the DOCX-rendered raster figure with selectable vector PDF content."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pdfplumber
from PIL import Image
from pypdf import PdfReader, PdfWriter, Transformation


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def convert_svg_to_pdf(svg: Path, output: Path) -> None:
    executable = shutil.which("rsvg-convert") or "/usr/local/bin/rsvg-convert"
    if not Path(executable).exists():
        raise RuntimeError("rsvg-convert is required for SVG-to-PDF conversion")
    result = subprocess.run(
        [executable, "-f", "pdf", "-o", str(output), str(svg)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def largest_image_bbox(pdf: Path) -> tuple[float, float, float, float]:
    with pdfplumber.open(pdf) as document:
        if len(document.pages) != 1:
            raise ValueError("Expected a one-page conference PDF")
        images = document.pages[0].images
        if not images:
            raise ValueError("No raster figure found in the DOCX-rendered PDF")
        image = max(images, key=lambda item: item["width"] * item["height"])
        if image["width"] < 300 or image["height"] < 100:
            raise ValueError(f"Largest image is not the expected manuscript figure: {image}")
        return image["x0"], image["y0"], image["x1"], image["y1"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-pdf", type=Path, required=True)
    parser.add_argument("--figure-svg", type=Path, required=True)
    parser.add_argument("--output-pdf", type=Path, required=True)
    parser.add_argument("--audit-json", type=Path)
    args = parser.parse_args()

    input_pdf = args.input_pdf.resolve()
    figure_svg = args.figure_svg.resolve()
    output_pdf = args.output_pdf.resolve()
    if input_pdf == output_pdf:
        raise ValueError("Input and output PDF paths must differ")

    bbox = largest_image_bbox(input_pdf)
    with tempfile.TemporaryDirectory(prefix="hic-vector-") as tmp:
        figure_pdf = Path(tmp) / "figure.pdf"
        convert_svg_to_pdf(figure_svg, figure_pdf)
        figure_page = PdfReader(figure_pdf).pages[0]

        writer = PdfWriter(clone_from=input_pdf)
        page = writer.pages[0]
        if not page.images:
            raise ValueError("The cloned PDF contains no replaceable image")
        largest_image = max(
            page.images,
            key=lambda item: item.image.width * item.image.height,
        )
        largest_image.replace(Image.new("RGB", (1, 1), "white"))

        x0, y0, x1, y1 = bbox
        transform = (
            Transformation()
            .scale(
                (x1 - x0) / float(figure_page.mediabox.width),
                (y1 - y0) / float(figure_page.mediabox.height),
            )
            .translate(x0, y0)
        )
        page.merge_transformed_page(figure_page, transform, over=True, expand=False)
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        with output_pdf.open("wb") as handle:
            writer.write(handle)

    extracted_text = subprocess.run(
        ["pdftotext", "-layout", str(output_pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    required_terms = [
        "Carrier family",
        "Text-native token streams",
        "Multimodality by denominator",
        "Krippendorff",
    ]
    missing_terms = [term for term in required_terms if term not in extracted_text]
    if missing_terms:
        raise ValueError(f"Vector figure text is not selectable: {missing_terms}")

    audit = {
        "input_pdf": str(input_pdf),
        "input_pdf_sha256": sha256(input_pdf),
        "figure_svg": str(figure_svg),
        "figure_svg_sha256": sha256(figure_svg),
        "figure_bbox_pdf_points": {
            "x0": bbox[0],
            "y0": bbox[1],
            "x1": bbox[2],
            "y1": bbox[3],
        },
        "output_pdf": str(output_pdf),
        "output_pdf_sha256": sha256(output_pdf),
        "selectable_figure_terms": required_terms,
        "missing_selectable_terms": missing_terms,
        "passed": not missing_terms,
    }
    audit_path = args.audit_json.resolve() if args.audit_json else output_pdf.with_suffix(".vector_audit.json")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
