#!/usr/bin/env python3
"""Create, verify, and restore immutable living-review artifact archives."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPTS = ROOT / "data/living_catalog/archives"
MANIFEST = "artifact_manifest.csv"
SUMMARY = "artifact_manifest_summary.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stream_sha256(stream: BinaryIO) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
        size += len(block)
    return digest.hexdigest(), size


def safe_label(value: str) -> str:
    normalized = "".join(char if char.isalnum() or char in "-_" else "-" for char in value)
    return normalized.strip("-") or "living-review-artifacts"


def load_source_manifest(source_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    manifest_path = source_root / MANIFEST
    summary_path = source_root / SUMMARY
    if not manifest_path.is_file() or not summary_path.is_file():
        raise RuntimeError(
            f"{source_root} requires {MANIFEST} and {SUMMARY}; generate them before archiving"
        )
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    manifest_sha = sha256(manifest_path)
    if summary.get("manifest_sha256") != manifest_sha:
        raise RuntimeError("artifact manifest does not match its summary hash")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    total = 0
    with manifest_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        required = {"relative_path", "size_bytes", "sha256"}
        if not required.issubset(reader.fieldnames or []):
            raise RuntimeError("artifact manifest is missing required columns")
        for raw in reader:
            relative = Path(str(raw["relative_path"]))
            if relative.is_absolute() or ".." in relative.parts or str(relative) in seen:
                raise RuntimeError(f"unsafe or duplicate manifest path: {relative}")
            path = source_root / relative
            if not path.is_file():
                raise RuntimeError(f"manifest payload is missing: {relative}")
            size = int(raw["size_bytes"])
            digest = str(raw["sha256"])
            if path.stat().st_size != size or sha256(path) != digest:
                raise RuntimeError(f"manifest payload changed: {relative}")
            rows.append({"relative_path": str(relative), "size_bytes": size, "sha256": digest})
            seen.add(str(relative))
            total += size
    if len(rows) != int(summary.get("file_count", -1)):
        raise RuntimeError("artifact manifest file count does not match its summary")
    if total != int(summary.get("total_size_bytes", -1)):
        raise RuntimeError("artifact manifest byte count does not match its summary")

    actual = {
        str(path.relative_to(source_root))
        for path in source_root.rglob("*")
        if path.is_file() and path.name not in {MANIFEST, SUMMARY}
    }
    declared = {row["relative_path"] for row in rows}
    if actual != declared:
        raise RuntimeError(
            "artifact manifest is stale; regenerate it before archiving: "
            f"unlisted={sorted(actual - declared)[:10]}, absent={sorted(declared - actual)[:10]}"
        )
    return rows, summary


def archive_members(source_root: Path, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    members = [*rows]
    for name in (MANIFEST, SUMMARY):
        path = source_root / name
        members.append(
            {"relative_path": name, "size_bytes": path.stat().st_size, "sha256": sha256(path)}
        )
    return sorted(members, key=lambda row: row["relative_path"])


def create_archive(args: argparse.Namespace) -> dict[str, Any]:
    source_root = args.source_root.resolve()
    archive_root = args.archive_root.resolve()
    receipt_root = args.receipt_dir.resolve()
    rows, summary = load_source_manifest(source_root)
    members = archive_members(source_root, rows)
    manifest_sha = str(summary["manifest_sha256"])
    label = safe_label(args.label or source_root.name)
    archive_id = f"{label}__{manifest_sha[:12]}"
    archive_path = archive_root / f"{archive_id}.tar.zst"
    receipt_path = receipt_root / f"{archive_id}.json"
    if archive_path.exists() or receipt_path.exists():
        raise RuntimeError(
            f"immutable archive or receipt already exists for {archive_id}; verify it instead"
        )
    zstd = shutil.which("zstd")
    if not zstd:
        raise RuntimeError("zstd executable is required")
    archive_root.mkdir(parents=True, exist_ok=True)
    receipt_root.mkdir(parents=True, exist_ok=True)
    temporary = archive_path.with_suffix(archive_path.suffix + ".tmp")
    process = subprocess.Popen(
        [zstd, "-T0", f"-{args.compression_level}", "-q", "-o", str(temporary)],
        stdin=subprocess.PIPE,
    )
    if process.stdin is None:
        raise RuntimeError("failed to open zstd input stream")
    prefix = source_root.name
    try:
        with tarfile.open(fileobj=process.stdin, mode="w|", format=tarfile.PAX_FORMAT) as archive:
            for row in members:
                path = source_root / row["relative_path"]
                archive.add(path, arcname=f"{prefix}/{row['relative_path']}", recursive=False)
        process.stdin.close()
        returncode = process.wait()
        if returncode:
            raise RuntimeError(f"zstd failed with return code {returncode}")
        temporary.replace(archive_path)
    except Exception:
        process.kill()
        process.wait()
        temporary.unlink(missing_ok=True)
        raise

    receipt = {
        "schema_version": 1,
        "archive_id": archive_id,
        "created_at": now_iso(),
        "storage_class": args.storage_class,
        "source_root": str(source_root),
        "source_root_name": prefix,
        "source_manifest": str(source_root / MANIFEST),
        "source_manifest_sha256": manifest_sha,
        "source_file_count": int(summary["file_count"]),
        "source_total_size_bytes": int(summary["total_size_bytes"]),
        "archive_path": str(archive_path),
        "archive_size_bytes": archive_path.stat().st_size,
        "archive_sha256": sha256(archive_path),
        "archive_member_count": len(members),
        "archive_members": members,
        "verification": None,
    }
    temporary_receipt = receipt_path.with_suffix(".json.tmp")
    temporary_receipt.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary_receipt.replace(receipt_path)
    return verify_archive(receipt_path, archive_override=None, update_receipt=True)


def verify_archive(
    receipt_path: Path,
    archive_override: Path | None,
    *,
    update_receipt: bool,
) -> dict[str, Any]:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    archive_path = (archive_override or Path(receipt["archive_path"])).resolve()
    issues: list[str] = []
    if not archive_path.is_file():
        issues.append(f"archive is missing: {archive_path}")
    elif sha256(archive_path) != receipt.get("archive_sha256"):
        issues.append("archive SHA-256 differs from receipt")
    expected = {
        f"{receipt['source_root_name']}/{row['relative_path']}": row
        for row in receipt.get("archive_members") or []
    }
    observed: set[str] = set()
    zstd = shutil.which("zstd")
    if not zstd:
        issues.append("zstd executable is required")
    elif archive_path.is_file() and not issues:
        process = subprocess.Popen([zstd, "-dc", str(archive_path)], stdout=subprocess.PIPE)
        if process.stdout is None:
            raise RuntimeError("failed to open zstd output stream")
        try:
            with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
                for member in archive:
                    if not member.isfile():
                        issues.append(f"unexpected non-file archive member: {member.name}")
                        continue
                    if member.name not in expected or member.name in observed:
                        issues.append(f"unexpected or duplicate archive member: {member.name}")
                        continue
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        issues.append(f"cannot read archive member: {member.name}")
                        continue
                    digest, size = stream_sha256(extracted)
                    row = expected[member.name]
                    if size != int(row["size_bytes"]) or digest != row["sha256"]:
                        issues.append(f"archive member failed hash validation: {member.name}")
                    observed.add(member.name)
            process.stdout.close()
            returncode = process.wait()
            if returncode:
                issues.append(f"zstd verification failed with return code {returncode}")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
    missing = sorted(set(expected) - observed)
    if missing:
        issues.append(f"archive is missing {len(missing)} declared member(s)")
    result = {
        "ok": not issues,
        "verified_at": now_iso(),
        "receipt": str(receipt_path.resolve()),
        "archive": str(archive_path),
        "archive_sha256": receipt.get("archive_sha256"),
        "members_verified": len(observed),
        "issues": issues,
    }
    if update_receipt and result["ok"] and archive_override is None:
        receipt["verification"] = result
        temporary = receipt_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        temporary.replace(receipt_path)
    return result


def restore_archive(args: argparse.Namespace) -> dict[str, Any]:
    receipt_path = args.receipt.resolve()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    archive_path = (args.archive or Path(receipt["archive_path"])).resolve()
    verification = verify_archive(receipt_path, archive_path, update_receipt=False)
    if not verification["ok"]:
        raise RuntimeError("Archive verification failed: " + "; ".join(verification["issues"]))
    destination = args.destination.resolve()
    if destination.exists() and any(destination.iterdir()):
        raise RuntimeError(f"restore destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    expected_prefix = receipt["source_root_name"] + "/"
    zstd = shutil.which("zstd")
    process = subprocess.Popen([str(zstd), "-dc", str(archive_path)], stdout=subprocess.PIPE)
    if process.stdout is None:
        raise RuntimeError("failed to open zstd output stream")
    with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
        for member in archive:
            if not member.isfile() or not member.name.startswith(expected_prefix):
                raise RuntimeError(f"unsafe archive member: {member.name}")
            relative = Path(member.name.removeprefix(expected_prefix))
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"unsafe archive path: {relative}")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError(f"cannot restore archive member: {member.name}")
            with target.open("wb") as stream:
                shutil.copyfileobj(source, stream, 1024 * 1024)
            os.chmod(target, member.mode & 0o777)
    process.stdout.close()
    if process.wait():
        raise RuntimeError("zstd restore failed")
    rows, summary = load_source_manifest(destination)
    return {
        "ok": True,
        "destination": str(destination),
        "files_restored": len(rows) + 2,
        "source_manifest_sha256": summary["manifest_sha256"],
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("--source-root", type=Path, required=True)
    create.add_argument("--archive-root", type=Path, required=True)
    create.add_argument("--receipt-dir", type=Path, default=DEFAULT_RECEIPTS)
    create.add_argument("--label")
    create.add_argument(
        "--storage-class",
        choices=["local_secondary", "independent_backup"],
        required=True,
    )
    create.add_argument("--compression-level", type=int, default=6)
    verify = sub.add_parser("verify")
    verify.add_argument("--receipt", type=Path, required=True)
    verify.add_argument("--archive", type=Path)
    restore = sub.add_parser("restore")
    restore.add_argument("--receipt", type=Path, required=True)
    restore.add_argument("--archive", type=Path)
    restore.add_argument("--destination", type=Path, required=True)
    return root


def main() -> int:
    args = parser().parse_args()
    if args.command == "create":
        result = create_archive(args)
    elif args.command == "verify":
        result = verify_archive(args.receipt.resolve(), args.archive, update_receipt=False)
    else:
        result = restore_archive(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
