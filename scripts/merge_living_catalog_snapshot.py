#!/usr/bin/env python3
"""Merge a validated taxonomy update into a new immutable living-catalog snapshot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def resolve_artifact(value: str, artifact_roots: list[Path] | None = None) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        if path.exists():
            return path
        for anchor in ("data", "analysis", "docs"):
            if anchor not in path.parts:
                continue
            suffix = Path(*path.parts[path.parts.index(anchor) :])
            candidate = next(
                (
                    root / suffix
                    for root in (artifact_roots or [])
                    if (root / suffix).exists()
                ),
                None,
            )
            if candidate is not None:
                return candidate
        return path
    candidates = [REPO / path, *((root / path) for root in (artifact_roots or []))]
    return next((candidate for candidate in candidates if candidate.exists()), candidates[0])


def profile_manifest_for(root: Path) -> Path | None:
    for relative in (
        "manifests/canonical_docling_profile_manifest.csv",
        "canonical_docling_profile_manifest.csv",
        "final_docling_manifest.csv",
    ):
        path = root / relative
        if path.is_file():
            return path
    return None


def corpus_inventory(
    root: Path,
    require_complete_profile_artifacts: bool,
    artifact_roots: list[Path] | None = None,
) -> dict[str, Any]:
    """Capture external profile provenance without copying an entire source corpus."""
    root = root.resolve()
    manifest = profile_manifest_for(root)
    result: dict[str, Any] = {
        "root": str(root),
        "required_for_this_update": require_complete_profile_artifacts,
    }
    if manifest is None:
        if require_complete_profile_artifacts:
            raise RuntimeError(f"Update corpus has no canonical Docling manifest: {root}")
        return {**result, "status": "profile_manifest_unavailable"}

    rows = [
        row for row in read_csv(manifest)
        if not row.get("profile_status") or row.get("profile_status") == "complete"
    ]
    profile_artifacts: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []
    for row in rows:
        candidate_id = str(row.get("candidate_id") or "")
        if not candidate_id:
            raise RuntimeError(f"Docling profile manifest has an empty candidate_id: {manifest}")
        for field in ("docling_json", "markdown", "figures_manifest", "source_document"):
            value = str(row.get(field) or "")
            path = resolve_artifact(value, artifact_roots) if value else None
            if path is None or not path.is_file():
                missing.append({"candidate_id": candidate_id, "field": field, "path": value})
                continue
            profile_artifacts.append(
                {
                    "candidate_id": candidate_id,
                    "field": field,
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    if require_complete_profile_artifacts and missing:
        raise RuntimeError(
            "Update corpus profile artifact inventory is incomplete: "
            + json.dumps(missing, ensure_ascii=False)
        )
    return {
        **result,
        "status": "complete" if not missing else "profile_artifacts_incomplete",
        "profile_manifest": str(manifest),
        "profile_manifest_sha256": sha256(manifest),
        "complete_profile_count": len(rows),
        "profile_artifacts": profile_artifacts,
        "missing_profile_artifacts": missing,
    }


def merge_unique(
    old: list[dict[str, Any]], new: list[dict[str, Any]], key: str
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for row in [*old, *new]:
        value = str(row.get(key) or "")
        if not value:
            raise RuntimeError(f"Missing {key} in snapshot row")
        if value in merged and merged[value] != row:
            raise RuntimeError(f"Conflicting {key}: {value}")
        merged[value] = row
    return [merged[value] for value in sorted(merged)]


def validate_grounded_evidence(
    routes: list[dict[str, Any]], evidence: list[dict[str, Any]]
) -> None:
    """Reject a snapshot unless every accepted route has a verified ledger row."""
    route_ids = {str(row.get("route_id") or "") for row in routes}
    evidence_ids = {str(row.get("route_id") or "") for row in evidence}
    if "" in route_ids or "" in evidence_ids:
        raise RuntimeError("Snapshot route/evidence ledger contains an empty route_id")
    if route_ids != evidence_ids:
        raise RuntimeError(
            "Snapshot route/evidence route_id mismatch; "
            f"missing_evidence={sorted(route_ids - evidence_ids)}, "
            f"orphan_evidence={sorted(evidence_ids - route_ids)}"
        )
    route_by_id = {str(row["route_id"]): row for row in routes}
    for row in evidence:
        route_id = str(row["route_id"])
        route = route_by_id[route_id]
        if row.get("record_id") != route.get("record_id"):
            raise RuntimeError(f"Evidence record_id differs from route for {route_id}")
        if not (route.get("final_grounding_valid") and row.get("final_grounding_valid")):
            raise RuntimeError(f"Unvalidated grounding for {route_id}")
        if not str(row.get("quote") or "").strip():
            raise RuntimeError(f"Evidence quote is empty for {route_id}")
        if not (row.get("pages") or row.get("doc_item_refs")):
            raise RuntimeError(f"Evidence has no page or Docling item reference for {route_id}")
        if not (
            row.get("quote_verified_in_canonical_markdown")
            or row.get("quote_verified_in_native_items")
        ):
            raise RuntimeError(f"Evidence quote is not verified in canonical source for {route_id}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior-taxonomy-root", type=Path, required=True)
    parser.add_argument("--update-taxonomy-root", type=Path, required=True)
    parser.add_argument("--prior-crop-ledger", type=Path, required=True)
    parser.add_argument("--update-crop-ledger", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--corpus-root", action="append", type=Path, default=[])
    parser.add_argument(
        "--artifact-root",
        action="append",
        type=Path,
        default=[],
        help="Additional filesystem base for immutable repository-relative profile paths.",
    )
    parser.add_argument(
        "--update-corpus-root",
        type=Path,
        required=True,
        help="New VLM corpus whose native profile artifacts must all be hash-verified.",
    )
    args = parser.parse_args()

    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"Refusing to overwrite non-empty snapshot: {output}")
    output.mkdir(parents=True, exist_ok=True)

    taxonomy_tree = read_json(args.prior_taxonomy_root / "taxonomy_tree.json")
    update_tree = args.update_taxonomy_root / "taxonomy_tree.json"
    if update_tree.exists() and read_json(update_tree) != taxonomy_tree:
        raise RuntimeError("Update taxonomy tree differs from frozen prior taxonomy")
    write_json(output / "taxonomy_tree.json", taxonomy_tree)
    for name in ("taxonomy_codebook.md",):
        source = args.prior_taxonomy_root / name
        if source.exists():
            shutil.copy2(source, output / name)

    routes = merge_unique(
        read_jsonl(args.prior_taxonomy_root / "route_annotations.jsonl"),
        read_jsonl(args.update_taxonomy_root / "route_annotations.jsonl"),
        "route_id",
    )
    evidence = merge_unique(
        read_jsonl(args.prior_taxonomy_root / "evidence_ledger.jsonl"),
        read_jsonl(args.update_taxonomy_root / "evidence_ledger.jsonl"),
        "route_id",
    )
    registry = merge_unique(
        read_csv(args.prior_taxonomy_root / "study_model_registry.csv"),
        read_csv(args.update_taxonomy_root / "study_model_registry.csv"),
        "record_id",
    )
    crops = merge_unique(
        read_json(args.prior_crop_ledger),
        read_json(args.update_crop_ledger),
        "model_id",
    )
    validate_grounded_evidence(routes, evidence)

    route_models = {row["model_id"] for row in routes}
    crop_models = {row["model_id"] for row in crops}
    if missing := route_models - crop_models:
        raise RuntimeError(f"Missing crop disposition for models: {sorted(missing)}")

    update_corpus = args.update_corpus_root.resolve()
    roots = [path.resolve() for path in args.corpus_root]
    artifact_roots = [path.resolve() for path in args.artifact_root]
    if update_corpus not in roots:
        roots.append(update_corpus)
    source_corpus_inventory = [
        corpus_inventory(
            root,
            require_complete_profile_artifacts=root == update_corpus,
            artifact_roots=artifact_roots,
        )
        for root in roots
    ]

    write_jsonl(output / "route_annotations.jsonl", routes)
    write_csv(output / "route_annotations.csv", routes)
    write_jsonl(output / "evidence_ledger.jsonl", evidence)
    write_csv(output / "study_model_registry.csv", registry)
    write_json(output / "crop_ledger.json", crops)

    family_counts = Counter(row["carrier_family"] for row in routes)
    subtype_counts = Counter(row["carrier_subtype"] for row in routes)
    summary = {
        "schema_version": 1,
        "created": now_iso(),
        "run_id": args.run_id,
        "taxonomy_version": taxonomy_tree.get("taxonomy_version"),
        "prior_taxonomy_root": str(args.prior_taxonomy_root),
        "update_taxonomy_root": str(args.update_taxonomy_root),
        "corpus_roots": [str(path) for path in roots],
        "artifact_roots": [str(path) for path in artifact_roots],
        "source_corpus_inventory": source_corpus_inventory,
        "records": len(registry),
        "studies": len({row["study_id"] for row in registry}),
        "models": len(route_models),
        "configurations": len({row["configuration_id"] for row in routes}),
        "routes": len(routes),
        "routes_by_family": dict(sorted(family_counts.items())),
        "routes_by_subtype": dict(sorted(subtype_counts.items())),
        "models_with_crop": sum(row.get("status") == "cropped_source_figure" for row in crops),
        "models_without_suitable_figure": sum(row.get("status") == "no_suitable_figure" for row in crops),
    }
    write_json(output / "snapshot_manifest.json", summary)
    artifact_paths = sorted(path for path in output.rglob("*") if path.is_file())
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
    (output / "README.md").write_text(
        "\n".join(
            [
                f"# Living Input-Representation Catalog Snapshot {args.run_id}",
                "",
                "This immutable snapshot merges the frozen taxonomy with one validated",
                "incremental review cohort. Historical source artifacts are referenced, not",
                "overwritten.",
                "",
                f"- Records: {summary['records']}",
                f"- Studies: {summary['studies']}",
                f"- Models: {summary['models']}",
                f"- Configurations: {summary['configurations']}",
                f"- Grounded input routes: {summary['routes']}",
                "",
                "See `snapshot_manifest.json` and `artifact_hashes.json` for the exact build.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
