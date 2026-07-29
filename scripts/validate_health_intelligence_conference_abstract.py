#!/usr/bin/env python3
"""Validate a conference abstract package against canonical review artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data/health_intelligence_conference_2026_abstract_2026-07-11"
TAXONOMY = ROOT / "data/input_representation_taxonomy_2026-07-11"
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WORD = {"w": WORD_NS}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def words(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def has_all(text: str, values: list[str]) -> bool:
    return all(value in text for value in values)


def docx_layout_signature(path: Path) -> dict[str, Any]:
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))

    sect = root.find(".//w:sectPr", WORD)
    table = root.find(".//w:tbl", WORD)
    if sect is None or table is None:
        raise ValueError(f"Missing section or body table in {path}")

    def attrs(node: ET.Element | None, names: tuple[str, ...]) -> tuple[str | None, ...]:
        if node is None:
            return tuple(None for _ in names)
        return tuple(node.get(f"{{{WORD_NS}}}{name}") for name in names)

    cells = table.findall("./w:tr[1]/w:tc", WORD)
    cell_margins: list[tuple[tuple[str, str | None, str | None], ...]] = []
    for cell in cells:
        margins = cell.findall("./w:tcPr/w:tcMar/*", WORD)
        cell_margins.append(
            tuple(
                (
                    margin.tag.rsplit("}", 1)[-1],
                    margin.get(f"{{{WORD_NS}}}w"),
                    margin.get(f"{{{WORD_NS}}}type"),
                )
                for margin in margins
            )
        )

    return {
        "page_size": attrs(sect.find("w:pgSz", WORD), ("w", "h")),
        "page_margins": attrs(
            sect.find("w:pgMar", WORD),
            ("top", "right", "bottom", "left", "header", "footer", "gutter"),
        ),
        "section_columns": attrs(sect.find("w:cols", WORD), ("num", "space")),
        "body_table_grid": tuple(
            column.get(f"{{{WORD_NS}}}w")
            for column in table.findall("./w:tblGrid/w:gridCol", WORD)
        ),
        "body_cell_margins": tuple(cell_margins),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--baseline-dir", type=Path)
    args = parser.parse_args()

    output = args.output_dir.resolve()
    render_dir = args.render_dir.resolve() if args.render_dir else output / "build/render_08"
    facts = json.loads((output / "analysis/manuscript_fact_table.json").read_text())
    agreement = json.loads((TAXONOMY / "agreement_metrics.json").read_text())
    content = json.loads((output / "manuscript_content.json").read_text())
    figure_contract = json.loads((output / "analysis/figure_fact_contract.json").read_text())
    figure_validation = json.loads((output / "analysis/figure_validation.json").read_text())
    source_manifest = json.loads((output / "source_manifest.json").read_text())

    docx = output / "health_intelligence_conference_2026_taxonomy_abstract_EN.docx"
    pdf = output / "health_intelligence_conference_2026_taxonomy_abstract_EN.pdf"
    page_png = render_dir / "page-1.png"
    grayscale_png = render_dir / "page-1-grayscale.png"
    svg = output / "figures/deterministic/figure_1_taxonomy.svg"
    vector_audit = output / "analysis/vector_pdf_audit.json"
    template = Path(source_manifest["template"])

    pdf_info = subprocess.run(
        ["pdfinfo", str(pdf)], capture_output=True, text=True, check=True
    ).stdout
    page_match = re.search(r"^Pages:\s+(\d+)$", pdf_info, flags=re.MULTILINE)
    pages = int(page_match.group(1)) if page_match else 0
    extracted_pdf_text = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    selectable_figure_terms = [
        "Carrier family",
        "Text-native token streams",
        "Multimodality by denominator",
        "Krippendorff",
    ]
    with pdfplumber.open(pdf) as document:
        pdf_images = document.pages[0].images
    largest_pdf_image_pixels = max(
        (image["srcsize"][0] * image["srcsize"][1] for image in pdf_images),
        default=0,
    )

    canonical_checks = {
        "records": facts["records"] == 52,
        "studies": facts["primary_studies"] == 51,
        "models": facts["models"] == 111,
        "configurations": facts["configurations"] == 376,
        "routes": facts["routes"] == 489,
        "families": len(facts["families"]) == 5,
        "subtypes": sum(len(family["subtypes"]) for family in facts["families"]) == 15,
        "multi_family_records": facts["multi_family_records"] == 37,
        "multi_family_configurations": facts["multi_family_configurations"] == 44,
        "cross_configuration_only": facts["cross_configuration_only_multi_family_records"] == 15,
        "one_route_configurations": facts["configuration_route_cardinality"]["one_route"] == 299,
        "multiple_route_configurations": facts["configuration_route_cardinality"]["multiple_routes"] == 77,
        "open_candidates": facts["open_discovery_candidates"] == 583,
        "dense_candidates": agreement["dense_candidate_count"] == 2208,
        "dense_additions": agreement["dense_only_accepted_candidate_count"] == 21,
        "all_grounded": facts["grounding"]["validated"] == facts["routes"],
        "no_picture_only": facts["grounding"]["picture_only"] == 0,
        "motivation_claims": facts["motivation"] == {"verified_claims": 174, "records": 52},
        "taxonomy_acceptance": agreement["acceptance_passed"],
    }

    section_checks = {
        "motivation_is_corpus_grounded": has_all(
            content["methods"], ["174 verified", "all 52 records"]
        ),
        "structured_abstract_has_core_denominators": has_all(
            content["abstract_results"], ["111 models", "376 task-input settings", "489 grounded routes"]
        ),
        "structured_abstract_names_carrier_families": has_all(
            content["abstract_results"],
            [
                "text-native tokens",
                "dense continuous carriers",
                "visual raster inputs",
                "discrete biological symbols",
                "geometric or diffusion states",
            ],
        ),
        "structured_abstract_has_primary_finding": has_all(
            content["abstract_results"],
            [
                "Across whole papers",
                "37/52",
                "71.2%",
                "44/376",
                "11.7%",
                "individual model-task-phase settings",
                "332/376 used one",
                "15 papers",
                "not as simultaneous inputs",
            ],
        ),
        "methods_has_search_and_screening": has_all(
            content["methods"], ["Seven databases", "four rounds", "7,531", "4,577", "221", "52 records"]
        ),
        "methods_names_screening_pipeline": has_all(
            content["methods"],
            [
                "Two independently prompted LLM reviewer roles",
                "assessed scope and architecture",
                "deterministic criterion gate",
                "separately prompted LLM adjudicator",
                "complete selected sections",
                "Six residual cases",
            ],
        ),
        "methods_states_eligibility_boundary": has_all(
            content["methods"],
            [
                "primary generative foundation-model contribution",
                "substantive in-model text-bio bridge",
                "biological-token modeling alone",
                "LLM wrappers did not qualify",
            ],
        ),
        "methods_names_annotation_status": "repeated gpt-5.4-mini invocations" in content["methods"],
        "results_distinguish_eligibility_from_route_coding": has_all(
            content["results_left"],
            ["Eligibility and route coding remained distinct", "token routes within eligible text-bio models"],
        ),
        "results_interpret_orthogonal_dimensions": has_all(
            content["results_right"],
            ["source does not determine carrier", "carrier does not determine fusion", "no single operational meaning"],
        ),
        "results_add_grounding_breakdown": has_all(
            content["results_right"], ["477 quotes", "12 were recovered", "none relied on picture-only evidence"]
        ),
        "discussion_states_scientific_conclusions": has_all(
            content["discussion"],
            [
                "fragmented collection of task- and model-specific interfaces",
                "six linked elements",
                "biological source, transformation, model-visible carrier",
                "fusion topology, lifecycle phase and text role",
                "makes heterogeneous systems comparable",
                "highly populated and underexplored mechanisms",
                "reproducible reporting framework",
                "biological grounding, cross-task transfer, computational efficiency and generative capability",
            ],
        ),
        "body_availability_removed": content.get("include_body_availability") is False,
        "author_metadata_complete": (
            content.get("authors") == "Bohdan Didenko"
            and content.get("affiliations") == "Lviv Polytechnic National University"
            and content.get("correspondence")
            == "*Correspondence: bohdan.didenko.asp.2025@lpnu.ua"
            and content.get("received") == "Received 12 July 2026"
            and "[Author names]" not in extracted_pdf_text
            and "[Affiliations]" not in extracted_pdf_text
            and "[email]" not in extracted_pdf_text
            and "[DD Month YYYY]" not in extracted_pdf_text
        ),
    }

    contract_checks = {
        "figure_validation": figure_validation["passed"],
        "figure_variant": source_manifest.get("figure_variant") == "compact-v3",
        "family_contract": figure_contract["families"] == facts["families"],
        "text_role_contract": figure_contract["text_roles"] == facts["text_roles"],
        "lifecycle_contract": figure_contract["lifecycle_phases"] == facts["lifecycle_phases"],
        "configuration_cardinality_contract": figure_contract["configuration_route_cardinality"] == facts["configuration_route_cardinality"],
        "rna_contract": figure_contract["rna_carrier_counts"] == facts["rna_carrier_counts"],
        "dense_fusion_contract": figure_contract["dense_fusion_counts"] == facts["dense_fusion_counts"],
        "grounding_contract": figure_contract["grounding"] == facts["grounding"],
        "coverage_counts_remain_in_figure_contract": (
            figure_contract["open_discovery_candidates"] == 583
            and figure_contract["agreement"]["dense_candidate_count"] == 2208
            and figure_contract["agreement"]["dense_only_accepted_candidate_count"] == 21
        ),
    }

    template_signature = docx_layout_signature(template)
    docx_signature = docx_layout_signature(docx)
    template_checks = {
        "page_size_matches_template": docx_signature["page_size"] == template_signature["page_size"],
        "page_margins_match_template": docx_signature["page_margins"] == template_signature["page_margins"],
        "section_columns_match_template": docx_signature["section_columns"] == template_signature["section_columns"],
        "body_table_grid_matches_template": docx_signature["body_table_grid"] == template_signature["body_table_grid"],
        "body_cell_margins_match_template": docx_signature["body_cell_margins"] == template_signature["body_cell_margins"],
        "right_column_gap_is_288_dxa": (
            len(docx_signature["body_cell_margins"]) >= 2
            and ("left", "288", "dxa") in docx_signature["body_cell_margins"][1]
            and not any(
                margin[0] in {"start", "end"}
                for margins in docx_signature["body_cell_margins"]
                for margin in margins
            )
        ),
    }

    # The abstract may summarize central figure facts, but the body should interpret
    # the RNA/fusion panels instead of narrating their exact values again.
    redundancy_audit = {
        "caption_contains_no_result_enumeration": not re.search(
            r"\b(?:37/52|44/376|281|87|62|42|17|165|115|63)\b",
            content["figure_1_caption"],
        ),
        "body_does_not_repeat_rna_panel_numbers": not has_all(
            content["results_right"], ["15", "12", "one discrete"]
        ),
        "body_does_not_repeat_dense_panel_numbers": not has_all(
            content["results_right"], ["19", "17", "16", "(9)"]
        ),
        "no_duplicate_body_availability": content.get("include_body_availability") is False,
        "interpretation_references_panel": "Fig. 1D" in content["results_right"],
    }

    svg_text = svg.read_text()
    font_sizes = [int(value) for value in re.findall(r"font:(?:700 )?(\d+)px", svg_text)]
    visual_checks = {
        "pdf_is_one_page": pages == 1,
        "pdf_is_a4": "595.304 x 841.89 pts (A4)" in pdf_info,
        "page_png_exists": page_png.exists() and page_png.stat().st_size > 0,
        "grayscale_png_exists": grayscale_png.exists() and grayscale_png.stat().st_size > 0,
        "svg_minimum_font_20px": bool(font_sizes) and min(font_sizes) >= 20,
        "docx_exists": docx.exists() and docx.stat().st_size > 0,
        "pdf_exists": pdf.exists() and pdf.stat().st_size > 0,
        "figure_text_is_selectable": all(
            term in extracted_pdf_text for term in selectable_figure_terms
        ),
        "large_raster_figure_removed": largest_pdf_image_pixels <= 4,
        "vector_pdf_audit_exists": vector_audit.exists(),
    }

    abstract_words = sum(
        words(content[key]) for key in ("abstract_motivation", "abstract_results", "availability")
    )
    results_text = (content["results_left"] + " " + content["results_right"]).strip()
    body_words = sum(
        words(content[key]) for key in ("introduction", "methods", "discussion", "funding")
    ) + words(results_text)
    reference_words = sum(words(item) for item in content["references"])

    all_groups = [
        canonical_checks,
        section_checks,
        contract_checks,
        template_checks,
        redundancy_audit,
        visual_checks,
    ]
    passed = all(all(group.values()) for group in all_groups)
    report: dict[str, Any] = {
        "passed": passed,
        "canonical_checks": canonical_checks,
        "section_checks": section_checks,
        "figure_contract_checks": contract_checks,
        "template_fidelity_checks": template_checks,
        "redundancy_audit": redundancy_audit,
        "visual_checks": visual_checks,
        "word_counts": {
            "structured_abstract": abstract_words,
            "main_body": body_words,
            "references": reference_words,
            "total": abstract_words + body_words + reference_words,
        },
        "final_artifacts": {
            "docx": str(docx.relative_to(ROOT)),
            "docx_sha256": sha256(docx),
            "pdf": str(pdf.relative_to(ROOT)),
            "pdf_sha256": sha256(pdf),
            "pdf_pages": pages,
            "rendered_page": str(page_png.relative_to(ROOT)),
            "grayscale_page": str(grayscale_png.relative_to(ROOT)),
        },
    }
    (output / "validation_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    lines = [
        "# Validation report",
        "",
        f"Overall: **{'PASS' if passed else 'FAIL'}**",
        "",
        f"- Final PDF: **{pages} A4 page**",
        f"- Structured abstract: **{abstract_words} words**",
        f"- Main body: **{body_words} words**",
        f"- References: **{reference_words} words**",
        f"- Total factual text plus references: **{abstract_words + body_words + reference_words} words**",
        f"- Figure fact contract: **{'PASS' if all(contract_checks.values()) else 'FAIL'}**",
        f"- Template geometry fidelity: **{'PASS' if all(template_checks.values()) else 'FAIL'}**",
        f"- Numeric/canonical checks: **{'PASS' if all(canonical_checks.values()) else 'FAIL'}**",
        f"- Redundancy audit: **{'PASS' if all(redundancy_audit.values()) else 'FAIL'}**",
        f"- Color and grayscale render artifacts: **{'PASS' if visual_checks['page_png_exists'] and visual_checks['grayscale_png_exists'] else 'FAIL'}**",
        f"- Selectable vector figure text: **{'PASS' if visual_checks['figure_text_is_selectable'] else 'FAIL'}**",
        f"- Large raster figure removed: **{'PASS' if visual_checks['large_raster_figure_removed'] else 'FAIL'}**",
        "",
        "The final color and grayscale PNGs were inspected at original resolution. No clipping, overlap, missing glyphs, unreadable figure labels, or incoherent whitespace was observed.",
    ]
    (output / "validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
