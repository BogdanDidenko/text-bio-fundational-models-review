#!/usr/bin/env python3
"""Freeze a validated whole-cohort taxonomy rerun as an immutable snapshot."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

from merge_living_catalog_snapshot import (
    REPO,
    corpus_inventory,
    now_iso,
    read_csv,
    read_json,
    read_jsonl,
    resolve_artifact,
    sha256,
    validate_grounded_evidence,
    write_csv,
    write_json,
    write_jsonl,
)


def require_unique(rows: list[dict[str, Any]], key: str, label: str) -> None:
    values = [str(row.get(key) or "") for row in rows]
    if "" in values:
        raise RuntimeError(f"{label} contains an empty {key}")
    duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
    if duplicates:
        raise RuntimeError(f"{label} contains duplicate {key} values: {duplicates}")


def validate_crops(
    crops: list[dict[str, Any]], routes: list[dict[str, Any]]
) -> tuple[int, int]:
    require_unique(crops, "model_id", "Crop ledger")
    routes_by_model: dict[str, set[str]] = {}
    for route in routes:
        routes_by_model.setdefault(str(route["model_id"]), set()).add(str(route["route_id"]))
    crop_models = {str(row["model_id"]) for row in crops}
    if crop_models != set(routes_by_model):
        raise RuntimeError(
            "Crop/model mismatch; "
            f"missing={sorted(set(routes_by_model) - crop_models)}, "
            f"orphan={sorted(crop_models - set(routes_by_model))}"
        )

    cropped = no_suitable = 0
    for row in crops:
        model_id = str(row["model_id"])
        status = row.get("status")
        if status == "no_suitable_figure":
            no_suitable += 1
            continue
        if status != "cropped_source_figure":
            raise RuntimeError(f"Invalid crop status for {model_id}: {status}")
        cropped += 1
        figure = row.get("figure") or {}
        source = resolve_artifact(str(figure.get("image_path") or ""))
        if not source.is_file():
            raise RuntimeError(f"Missing crop source image for {model_id}: {source}")
        box = row.get("crop_box") or {}
        x, y = float(box.get("x", -1)), float(box.get("y", -1))
        width, height = float(box.get("width", -1)), float(box.get("height", -1))
        if not (
            0 <= x <= 1
            and 0 <= y <= 1
            and 0.03 <= width <= 1
            and 0.03 <= height <= 1
            and x + width <= 1.000001
            and y + height <= 1.000001
        ):
            raise RuntimeError(f"Invalid crop bounds for {model_id}: {box}")
        cited = set(map(str, row.get("route_ids_supported") or []))
        if not cited or not cited <= routes_by_model[model_id]:
            raise RuntimeError(
                f"Invalid crop route references for {model_id}: "
                f"{sorted(cited - routes_by_model[model_id])}"
            )
    return cropped, no_suitable


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxonomy-root", type=Path, required=True)
    parser.add_argument("--frozen-taxonomy-root", type=Path, required=True)
    parser.add_argument("--crop-ledger", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--corpus-root", action="append", type=Path, required=True)
    args = parser.parse_args()

    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"Refusing to overwrite non-empty snapshot: {output}")
    output.mkdir(parents=True, exist_ok=True)

    metrics_path = args.taxonomy_root / "agreement_metrics.json"
    metrics = read_json(metrics_path)
    if not metrics.get("acceptance_passed"):
        raise RuntimeError(f"Taxonomy acceptance did not pass: {metrics_path}")

    taxonomy_tree = read_json(args.frozen_taxonomy_root / "taxonomy_tree.json")
    rerun_tree = args.taxonomy_root / "taxonomy_tree.json"
    if rerun_tree.is_file() and read_json(rerun_tree) != taxonomy_tree:
        raise RuntimeError("Whole-cohort rerun taxonomy differs from the frozen taxonomy")

    routes = read_jsonl(args.taxonomy_root / "route_annotations.jsonl")
    evidence = read_jsonl(args.taxonomy_root / "evidence_ledger.jsonl")
    registry = read_csv(args.taxonomy_root / "study_model_registry.csv")
    crops = read_json(args.crop_ledger)
    require_unique(routes, "route_id", "Route annotations")
    require_unique(evidence, "route_id", "Evidence ledger")
    require_unique(registry, "record_id", "Study/model registry")
    validate_grounded_evidence(routes, evidence)
    cropped, no_suitable = validate_crops(crops, routes)

    corpus_roots = [path.resolve() for path in args.corpus_root]
    if len(set(corpus_roots)) != len(corpus_roots):
        raise RuntimeError("Duplicate --corpus-root values")
    source_corpus_inventory = [
        corpus_inventory(root, require_complete_profile_artifacts=True)
        for root in corpus_roots
    ]

    write_json(output / "taxonomy_tree.json", taxonomy_tree)
    codebook = args.frozen_taxonomy_root / "taxonomy_codebook.md"
    if codebook.is_file():
        shutil.copy2(codebook, output / "taxonomy_codebook.md")
    write_jsonl(output / "route_annotations.jsonl", routes)
    write_csv(output / "route_annotations.csv", routes)
    write_jsonl(output / "evidence_ledger.jsonl", evidence)
    write_csv(output / "study_model_registry.csv", registry)
    write_json(output / "crop_ledger.json", crops)
    shutil.copy2(metrics_path, output / "aggregate_agreement_metrics.json")

    family_counts = Counter(str(row["carrier_family"]) for row in routes)
    subtype_counts = Counter(str(row["carrier_subtype"]) for row in routes)
    summary = {
        "schema_version": 1,
        "created": now_iso(),
        "run_id": args.run_id,
        "build_mode": "full_cohort_rerun",
        "taxonomy_version": taxonomy_tree.get("taxonomy_version"),
        "taxonomy_root": str(args.taxonomy_root.resolve()),
        "frozen_taxonomy_root": str(args.frozen_taxonomy_root.resolve()),
        "corpus_roots": [str(path) for path in corpus_roots],
        "source_corpus_inventory": source_corpus_inventory,
        "records": len(registry),
        "studies": len({str(row["study_id"]) for row in registry}),
        "models": len({str(row["model_id"]) for row in routes}),
        "configurations": len({str(row["configuration_id"]) for row in routes}),
        "routes": len(routes),
        "routes_by_family": dict(sorted(family_counts.items())),
        "routes_by_subtype": dict(sorted(subtype_counts.items())),
        "models_with_crop": cropped,
        "models_without_suitable_figure": no_suitable,
        "taxonomy_acceptance_passed": True,
    }
    write_json(output / "snapshot_manifest.json", summary)
    (output / "README.md").write_text(
        "\n".join(
            [
                f"# Living Input-Representation Catalog Snapshot {args.run_id}",
                "",
                "This immutable snapshot freezes one validated whole-cohort taxonomy rerun;",
                "it is not an incremental merge with a prior taxonomy output.",
                "",
                f"- Records: {summary['records']}",
                f"- Studies: {summary['studies']}",
                f"- Models: {summary['models']}",
                f"- Configurations: {summary['configurations']}",
                f"- Grounded input routes: {summary['routes']}",
                f"- Models with validated source crops: {cropped}",
                f"- Models with no suitable source figure: {no_suitable}",
                "",
                "See `snapshot_manifest.json`, `aggregate_agreement_metrics.json`, and",
                "`artifact_hashes.json` for the exact build and acceptance evidence.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    artifact_paths = sorted(
        path for path in output.rglob("*")
        if path.is_file() and path.name != "artifact_hashes.json"
    )
    write_json(
        output / "artifact_hashes.json",
        [
            {
                "path": str(path.relative_to(output)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in artifact_paths
        ],
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
