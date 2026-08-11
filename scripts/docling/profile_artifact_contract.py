"""Validate immutable native Docling artifacts before downstream LLM use."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def resolve_artifact(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_profile_artifacts(row: dict[str, Any]) -> tuple[Path, Path]:
    candidate_id = str(row.get("candidate_id") or "")
    if not candidate_id:
        raise RuntimeError("Canonical Docling profile has an empty candidate_id")
    if row.get("profile_status") != "complete":
        raise RuntimeError(f"Docling profile is not complete: {candidate_id}")
    if row.get("document_identity_status") != "verified":
        raise RuntimeError(f"Docling document identity is not verified: {candidate_id}")
    resolved: dict[str, Path] = {}
    for field, hash_field in (
        ("docling_json", "docling_json_sha256"),
        ("markdown", "markdown_sha256"),
    ):
        path = resolve_artifact(str(row.get(field) or ""))
        expected_hash = str(row.get(hash_field) or "")
        if not path.is_file() or not expected_hash:
            raise RuntimeError(
                f"Canonical Docling artifact is missing or unbound for {candidate_id}: {field}"
            )
        if file_sha256(path) != expected_hash:
            raise RuntimeError(f"Canonical Docling artifact hash mismatch for {candidate_id}: {field}")
        resolved[field] = path
    return resolved["docling_json"], resolved["markdown"]
