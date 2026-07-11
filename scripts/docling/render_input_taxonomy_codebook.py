#!/usr/bin/env python3
"""Render the adjudicated taxonomy proposal as codebook and figure specification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data/input_representation_taxonomy_2026-07-11"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxonomy", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    taxonomy = read_json(args.taxonomy)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tree = {
        "taxonomy_version": "input-representation-taxonomy-v1",
        "status": "frozen_after_three_independent_syntheses_and_llm_adjudication",
        **taxonomy,
    }
    (args.output_dir / "taxonomy_tree.json").write_text(
        json.dumps(tree, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Input-Representation Taxonomy v1",
        "",
        f"**Classification unit:** {taxonomy['classification_unit']}",
        "",
        taxonomy["organizing_principle"],
        "",
        "Unknown and unclear are annotation states, not taxonomy categories. A "
        "multimodal configuration contains several source-to-model routes and is not "
        "coded as a single hybrid route.",
        "",
        "## Operational decision boundary",
        "",
        "Classify the first model-facing carrier after semantic preprocessing but before "
        "routine embedding lookup or encoder processing. Ordinary text tokens remain "
        "text-native; native or learned biological token IDs remain discrete; pixels and "
        "patches remain visual; coordinates and noisy states remain geometric/diffusion. "
        "Use a dense continuous carrier only when an external encoder, projector, pooling "
        "operation, or learned soft-token mechanism produces continuous vectors that enter "
        "the generative backbone without the ordinary tokenizer, symbol, raster, or "
        "geometric-state interface.",
        "",
        "## Primary hierarchy",
        "",
    ]
    for family in taxonomy["families"]:
        lines.extend(
            [
                f"### `{family['family_id']}`: {family['name']}",
                "",
                family["definition"],
                "",
                f"**Structural criterion:** {family['structural_criterion']}",
                "",
            ]
        )
        for leaf in family.get("leaves") or []:
            lines.extend(
                [
                    f"#### `{leaf['leaf_id']}`: {leaf['name']}",
                    "",
                    leaf["definition"],
                    "",
                    "Include when: " + "; ".join(leaf.get("include_when") or ["not specified"]),
                    "",
                    "Exclude when: " + "; ".join(leaf.get("exclude_when") or ["not specified"]),
                    "",
                    "Positive route refs: "
                    + ", ".join(leaf.get("positive_route_refs") or ["none recorded"]),
                    "",
                    "Counterexample route refs: "
                    + ", ".join(leaf.get("counterexample_route_refs") or ["none recorded"]),
                    "",
                ]
            )
    lines.extend(["## Orthogonal dimensions", ""])
    for dimension in taxonomy.get("orthogonal_dimensions") or []:
        lines.extend(
            [
                f"### `{dimension['dimension_id']}`: {dimension['name']}",
                "",
                dimension["definition"],
                "",
                "Values: " + ", ".join(dimension.get("values") or ["open coding"]),
                "",
            ]
        )
    if taxonomy.get("category_errors_prevented"):
        lines.extend(["## Category errors prevented", ""])
        lines.extend(f"- {value}" for value in taxonomy["category_errors_prevented"])
        lines.append("")
    if taxonomy.get("unresolved_questions"):
        lines.extend(["## Unresolved questions", ""])
        lines.extend(f"- {value}" for value in taxonomy["unresolved_questions"])
        lines.append("")
    (args.output_dir / "taxonomy_codebook.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    figure = [
        "# Taxonomy Hierarchy Figure Specification",
        "",
        "The manuscript figure should show the primary model-visible-carrier hierarchy "
        "vertically and the orthogonal dimensions as a separate aligned panel. Biological "
        "modality must not be drawn as a parent of the carrier families.",
        "",
        "```mermaid",
        "flowchart TD",
        '  ROOT["Input representation route"]',
    ]
    for family_index, family in enumerate(taxonomy["families"], start=1):
        family_node = f"F{family_index}"
        figure.append(f'  ROOT --> {family_node}["{family["name"]}"]')
        for leaf_index, leaf in enumerate(family.get("leaves") or [], start=1):
            label = leaf["name"].replace('"', "'")
            figure.append(f'  {family_node} --> {family_node}L{leaf_index}["{label}"]')
    figure.extend(["```", ""])
    (args.output_dir / "taxonomy_figure_specification.md").write_text(
        "\n".join(figure), encoding="utf-8"
    )
    print(json.dumps({"families": len(taxonomy["families"]), "output": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
