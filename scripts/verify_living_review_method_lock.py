#!/usr/bin/env python3
"""Create or verify the immutable scientific-method lock for living-review runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = ROOT / "protocol/living_review_method_lock_v1.json"
DEFAULT_CONFIG = ROOT / "config/living_review_pipeline.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(path: str | Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def nested_value(payload: dict[str, Any], dotted_path: str) -> Any:
    value: Any = payload
    for key in dotted_path.split("."):
        if not isinstance(value, dict) or key not in value:
            raise KeyError(dotted_path)
        value = value[key]
    return value


def verify_method_lock(
    lock_path: str | Path = DEFAULT_LOCK,
    config_path: str | Path = DEFAULT_CONFIG,
    *,
    current_taxonomy_tree: str | Path | None = None,
) -> dict[str, Any]:
    lock_file = resolve(lock_path)
    config_file = resolve(config_path)
    issues: list[str] = []
    if not lock_file.is_file():
        return {"ok": False, "lock_path": str(lock_file), "issues": ["method lock is missing"]}
    lock = json.loads(lock_file.read_text(encoding="utf-8"))
    if lock.get("schema_version") != 1:
        issues.append("unsupported method-lock schema")
    if not str(lock.get("method_id") or "").strip():
        issues.append("method_id is missing")

    checked_files = []
    for row in lock.get("files") or []:
        relative = Path(str(row.get("path") or ""))
        if not str(relative) or relative.is_absolute() or ".." in relative.parts:
            issues.append(f"unsafe locked path: {relative}")
            continue
        path = ROOT / relative
        if not path.is_file():
            issues.append(f"missing locked file: {relative}")
            continue
        actual = sha256(path)
        expected = str(row.get("sha256") or "")
        checked_files.append(
            {"path": str(relative), "role": row.get("role"), "sha256": actual}
        )
        if actual != expected:
            issues.append(f"locked file changed: {relative}")

    config = json.loads(config_file.read_text(encoding="utf-8")) if config_file.is_file() else {}
    if not config:
        issues.append(f"pipeline config is missing: {config_file}")
    checked_parameters = []
    for dotted_path, expected in (lock.get("config_assertions") or {}).items():
        try:
            actual = nested_value(config, dotted_path)
        except KeyError:
            issues.append(f"missing configured method parameter: {dotted_path}")
            continue
        checked_parameters.append({"path": dotted_path, "value": actual})
        if actual != expected:
            issues.append(
                f"configured method parameter changed: {dotted_path}={actual!r}, expected {expected!r}"
            )

    taxonomy_sha = str(lock.get("frozen_taxonomy", {}).get("sha256") or "")
    if current_taxonomy_tree:
        path = resolve(current_taxonomy_tree)
        if not path.is_file():
            issues.append(f"current taxonomy tree is missing: {path}")
        elif sha256(path) != taxonomy_sha:
            issues.append("current taxonomy tree differs from the frozen taxonomy in the method lock")

    return {
        "ok": not issues,
        "method_id": lock.get("method_id"),
        "lock_path": str(lock_file),
        "lock_sha256": sha256(lock_file),
        "files_checked": len(checked_files),
        "parameters_checked": len(checked_parameters),
        "frozen_taxonomy_sha256": taxonomy_sha,
        "issues": issues,
    }


def refresh_lock(lock_path: Path) -> dict[str, Any]:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    rows = lock.get("files") or []
    for row in rows:
        path = resolve(row["path"])
        if not path.is_file():
            raise RuntimeError(f"Cannot lock missing file: {path}")
        row["sha256"] = sha256(path)
    taxonomy_path = resolve(lock["frozen_taxonomy"]["path"])
    lock["frozen_taxonomy"]["sha256"] = sha256(taxonomy_path)
    lock["refreshed_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    temporary = lock_path.with_suffix(lock_path.suffix + ".tmp")
    temporary.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(lock_path)
    return lock


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--current-taxonomy-tree", type=Path)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Recompute hashes after an explicitly reviewed method-version change.",
    )
    args = parser.parse_args()
    lock_path = resolve(args.lock)
    if args.refresh:
        refresh_lock(lock_path)
    result = verify_method_lock(
        lock_path,
        args.config,
        current_taxonomy_tree=args.current_taxonomy_tree,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
