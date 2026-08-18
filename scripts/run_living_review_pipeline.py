#!/usr/bin/env python3
"""Run resumable search-to-atlas updates for the living review catalog."""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.util
import json
import math
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

from verify_living_review_method_lock import verify_method_lock


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config/living_review_pipeline.json"

STAGES = [
    "search",
    "deduplicate",
    "prepare-records",
    "enrich-abstracts",
    "abstract-screening",
    "fulltext-candidates",
    "fulltext-download",
    "docling-screening",
    "graph-sections",
    "fulltext-screening",
    "eligibility-resolution",
    "docling-vlm",
    "taxonomy-discovery",
    "taxonomy-classification",
    "crop-validation",
    "snapshot",
    "atlas",
    "report",
]


class ManualGate(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atlas_tree_manifest(root: Path) -> dict[str, Any]:
    """Hash every deployable atlas file except the self-describing release manifest."""
    excluded = {(root / "data/deployment.json").resolve()}
    files = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.resolve() in excluded:
            continue
        files.append(
            {
                "path": str(path.relative_to(root)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    canonical = json.dumps(files, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return {
        "file_count": len(files),
        "total_bytes": sum(row["bytes"] for row in files),
        "manifest_sha256": hashlib.sha256(canonical).hexdigest(),
        "files": files,
    }


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def resolve(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def playwright_node_path() -> str | None:
    configured = os.environ.get("NODE_PATH")
    candidates = [
        ROOT / "node_modules",
        Path.home()
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules",
    ]
    if configured:
        candidates[:0] = [
            Path(item) for item in configured.split(os.pathsep) if item
        ]
    for candidate in candidates:
        if (candidate / "playwright").exists():
            return str(candidate)
    return None


def record_count(path: Path) -> int:
    value = read_json(path)
    rows = value.get("records", []) if isinstance(value, dict) else value
    return len(rows)


def records_from(path: Path) -> list[dict[str, Any]]:
    value = read_json(path)
    rows = value.get("records", []) if isinstance(value, dict) else value
    if not isinstance(rows, list):
        raise ValueError(f"Unsupported record artifact: {path}")
    return rows


def decision_counts(path: Path) -> dict[str, int]:
    value = read_json(path)
    rows = value.get("records", []) if isinstance(value, dict) else value
    counts: dict[str, int] = {}
    for row in rows:
        decision = str(row.get("final_decision") or row.get("eligibility_decision") or "")
        counts[decision] = counts.get(decision, 0) + 1
    return counts


def date_precision_rollup(search_summary: dict[str, Any]) -> dict[str, Any]:
    """Separate confirmed source-filtered hits from uncertain-date recall candidates."""
    by_database = search_summary.get("date_status_by_database") or {}
    counts: dict[str, int] = {}
    excluded_out_of_range = 0
    for row in by_database.values():
        for status, count in (row.get("retained_status_counts") or {}).items():
            counts[str(status)] = counts.get(str(status), 0) + int(count)
        excluded_out_of_range += int(row.get("excluded_out_of_range") or 0)
    retained = sum(counts.values())
    expected = int(search_summary.get("total_before_dedup") or 0)
    if retained != expected:
        raise RuntimeError(
            "Search date-status rollup does not equal retained raw hits: "
            f"{retained} != {expected}"
        )
    uncertain = sum(
        count for status, count in counts.items()
        if status.startswith("unknown") or status == "unreported"
    )
    return {
        "retained_raw_hits": retained,
        "confirmed_by_source_date_filter": retained - uncertain,
        "uncertain_date_recall_candidates": uncertain,
        "retained_status_counts": counts,
        "excluded_confirmed_out_of_range_before_export": excluded_out_of_range,
    }


def retrieval_disposition_table(
    candidates: list[dict[str, Any]], download_manifest: dict[str, Any], missing_documents: list[dict[str, Any]]
) -> dict[str, Any]:
    """Produce a mutually exclusive full-text disposition and Docling overlap audit."""
    candidate_ids = {
        str(row.get("candidate_id") or row.get("record_id") or "") for row in candidates
    }
    if "" in candidate_ids or len(candidate_ids) != len(candidates):
        raise RuntimeError("Full-text candidates have duplicate or empty candidate_id")
    downloads = download_manifest.get("results") or []
    by_id = {str(row.get("candidate_id") or row.get("record_id") or ""): row for row in downloads}
    if "" in by_id or len(by_id) != len(downloads) or set(by_id) != candidate_ids:
        raise RuntimeError("Download manifest must contain exactly one result for every full-text candidate")
    category_by_status = {
        "pdf_downloaded": "pdf_retrieved",
        "html_full_text_downloaded": "html_full_text_retrieved",
        "non_pdf_full_text_downloaded": "html_full_text_retrieved",
        "xml_full_text_downloaded": "xml_full_text_retrieved_unsupported",
        "retrieval_incomplete": "technical_retrieval_failure",
        "access_restricted": "not_retrieved_access_restricted",
        "no_full_text_found": "not_retrieved",
        "skipped_existing": "preexisting_retrieval_reused",
    }
    rows = []
    for candidate_id in sorted(candidate_ids):
        result = by_id[candidate_id]
        status = str(result.get("status") or "")
        if status not in category_by_status:
            raise RuntimeError(f"Unknown download status for {candidate_id}: {status}")
        rows.append(
            {
                "candidate_id": candidate_id,
                "download_status": status,
                "disposition": category_by_status[status],
                "terminal_retrieval_evidence": status
                in {
                    "pdf_downloaded",
                    "html_full_text_downloaded",
                    "non_pdf_full_text_downloaded",
                    "access_restricted",
                    "no_full_text_found",
                    "skipped_existing",
                },
                "manual_gate_required": status
                in {"retrieval_incomplete", "xml_full_text_downloaded"},
                "attempt_count": int(result.get("attempt_count") or 0),
                "technical_failure_count": int(result.get("technical_failure_count") or 0),
                "access_restriction_count": int(result.get("access_restriction_count") or 0),
                "retrieved_files": result.get("files") or [],
                "attempt_ledger": str(result.get("folder") or ""),
            }
        )
    missing_ids = {
        str(row.get("candidate_id") or row.get("record_id") or "") for row in missing_documents
    }
    if not missing_ids <= candidate_ids:
        raise RuntimeError("Docling missing-documents artifact contains an unknown candidate")
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["disposition"]] = counts.get(row["disposition"], 0) + 1
    if sum(counts.values()) != len(candidates):
        raise RuntimeError("Retrieval dispositions do not partition full-text candidates")
    missing_by_disposition: dict[str, int] = {}
    for candidate_id in missing_ids:
        disposition = next(row["disposition"] for row in rows if row["candidate_id"] == candidate_id)
        missing_by_disposition[disposition] = missing_by_disposition.get(disposition, 0) + 1
    return {
        "candidate_count": len(candidates),
        "disposition_counts": counts,
        "rows": rows,
        "docling_missing_count": len(missing_ids),
        "docling_missing_by_retrieval_disposition": missing_by_disposition,
    }


def retrieved_candidate_subset(
    candidates: list[dict[str, Any]], documents: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Select the one-to-one candidate subset with validated Docling inputs."""
    candidate_index = {
        str(row.get("candidate_id") or row.get("record_id") or ""): row
        for row in candidates
    }
    if "" in candidate_index or len(candidate_index) != len(candidates):
        raise RuntimeError("Full-text candidates have duplicate or empty candidate_id")
    document_ids = [
        str(row.get("candidate_id") or row.get("record_id") or "") for row in documents
    ]
    if not all(document_ids) or len(set(document_ids)) != len(document_ids):
        raise RuntimeError("Docling config has duplicate or empty candidate_id")
    unknown = sorted(set(document_ids) - set(candidate_index))
    if unknown:
        raise RuntimeError(f"Docling config contains unknown full-text candidates: {unknown}")
    return [candidate_index[candidate_id] for candidate_id in document_ids]


@dataclass
class Paths:
    root: Path
    date_to: str

    @property
    def search(self) -> Path:
        return self.root / "00_search"

    @property
    def dedup(self) -> Path:
        return self.root / "01_dedup"

    @property
    def records(self) -> Path:
        return self.root / "02_records"

    @property
    def abstracts(self) -> Path:
        return self.root / "03_abstracts"

    @property
    def abstract_screening(self) -> Path:
        return self.root / "04_abstract_screening"

    @property
    def fulltext(self) -> Path:
        return self.root / "05_fulltext"

    @property
    def docling_screen(self) -> Path:
        return self.root / "06_docling_screening"

    @property
    def graph_sections(self) -> Path:
        return self.root / "07_graph_sections"

    @property
    def section_input(self) -> Path:
        return self.root / "08_section_input"

    @property
    def fulltext_screening(self) -> Path:
        return self.root / "09_fulltext_screening"

    @property
    def eligibility(self) -> Path:
        return self.root / "10_eligibility"

    @property
    def docling_vlm(self) -> Path:
        return self.root / "11_docling_vlm"

    @property
    def taxonomy(self) -> Path:
        return self.root / "12_taxonomy"

    @property
    def crops(self) -> Path:
        return self.root / "13_crops"

    @property
    def snapshot(self) -> Path:
        return self.root / "14_snapshot"

    @property
    def atlas(self) -> Path:
        return self.root / "15_atlas"

    @property
    def report(self) -> Path:
        return self.root / "16_report"

    @property
    def search_config(self) -> Path:
        return self.search / "search_config.json"

    @property
    def search_exports(self) -> Path:
        return self.search / "exports"

    @property
    def abstract_input(self) -> Path:
        return self.abstracts / "abstract_screening_input.json"

    @property
    def fulltext_candidates(self) -> Path:
        return self.fulltext / "fulltext_candidates.json"

    @property
    def download_manifest(self) -> Path:
        return self.fulltext / "fulltext_download_manifest.json"

    @property
    def retrieval_dispositions(self) -> Path:
        return self.fulltext / "fulltext_retrieval_dispositions.json"

    @property
    def no_vlm_manifest(self) -> Path:
        return self.docling_screen / "profiles/manifests/canonical_docling_profile_manifest.csv"

    @property
    def retrieved_fulltext_candidates(self) -> Path:
        return self.docling_screen / "retrieved_fulltext_candidates.json"

    @property
    def section_screening_input(self) -> Path:
        return self.section_input / "fulltext_screening_input.json"

    @property
    def accepted_records(self) -> Path:
        return self.eligibility / "accepted_records.json"

    @property
    def vlm_manifest(self) -> Path:
        return self.docling_vlm / "profiles/manifests/canonical_docling_profile_manifest.csv"


class Pipeline:
    def __init__(self, args: argparse.Namespace, config: dict[str, Any]) -> None:
        self.args = args
        self.config = config
        self.publish_journal_path = resolve(config["updates_root"]) / ".publish_journal.json"
        self.recover_interrupted_publication()
        self.current = self.load_current_state()
        if (
            getattr(args, "command", "")
            in {"plan", "preflight", "run", "scholar-capture", "scholar-validate"}
            and not args.date_to
            and (
                not args.run_id
                or not (
                    resolve(config["updates_root"])
                    / str(args.run_id)
                    / "run_manifest.json"
                ).is_file()
            )
        ):
            raise ValueError(
                "A new routine run requires explicit --date-to; use the last fully elapsed local day"
            )
        requested_date_to = args.date_to or date.today().isoformat()
        self.run_id = args.run_id or f"update_{requested_date_to}"
        self.run_root = resolve(config["updates_root"]) / self.run_id
        self.manifest_path = self.run_root / "run_manifest.json"
        if self.manifest_path.exists():
            self.manifest = read_json(self.manifest_path)
            self.date_from = self.manifest["date_from"]
            self.date_to = self.manifest["date_to"]
            if args.date_from and args.date_from != self.date_from:
                raise RuntimeError("Existing run_id has a different date_from")
            if args.date_to and args.date_to != self.date_to:
                raise RuntimeError("Existing run_id has a different date_to")
        else:
            self.date_to = requested_date_to
            prior_end = date.fromisoformat(self.current["search_end"])
            self.date_from = args.date_from or (prior_end + timedelta(days=1)).isoformat()
            if date.fromisoformat(self.date_from) > date.fromisoformat(self.date_to):
                raise ValueError("The requested update range is empty or reversed")
            self.manifest = self.new_manifest()
        self.paths = Paths(self.run_root, self.date_to)
        self._active_log_attempts: dict[str, Path] = {}
        self._repository_external_artifacts_cache: dict[str, dict[str, Any]] | None = None
        self._repository_artifact_ledger_summary: dict[str, Any] | None = None
        self._artifact_roots_cache: list[Path] | None = None

    def recover_interrupted_publication(self) -> None:
        """Rollback a crash between atlas promotion and state/manifest finalization."""
        if not self.publish_journal_path.is_file():
            return
        journal = read_json(self.publish_journal_path)
        if journal.get("schema_version") != 1:
            raise RuntimeError(f"Unsupported publish journal: {self.publish_journal_path}")
        state_path = Path(str(journal["state_path"]))
        prior_state = journal["prior_state"]
        if journal.get("state_existed"):
            write_json(state_path, prior_state)
        else:
            state_path.unlink(missing_ok=True)
        atlas = journal.get("atlas") or {}
        target = Path(str(atlas["target"])) if atlas.get("target") else None
        backup = Path(str(atlas["backup"])) if atlas.get("backup") else None
        temporary = Path(str(atlas["temporary"])) if atlas.get("temporary") else None
        if target and backup and backup.exists():
            if target.exists():
                shutil.rmtree(target)
            backup.replace(target)
        elif target and not atlas.get("target_existed", False) and target.exists():
            shutil.rmtree(target)
        if temporary and temporary.exists():
            shutil.rmtree(temporary)
        self.publish_journal_path.unlink()

    def load_current_state(self) -> dict[str, Any]:
        state_path = resolve(self.config["living_state"])
        if state_path.exists():
            return read_json(state_path)
        prisma_history = []
        if baseline_facts := self.config.get("baseline_prisma_facts"):
            prisma_history.append(
                {
                    "run_id": "baseline_through_2026-07-06",
                    "date_from": "2018-01-01",
                    "date_to": self.config["baseline_search_end"],
                    "facts": baseline_facts,
                }
            )
        return {
            "schema_version": 1,
            "search_end": self.config["baseline_search_end"],
            "master_record_files": self.config["master_record_files"],
            "taxonomy_root": self.config["baseline_taxonomy_root"],
            "docling_corpus_roots": self.config["baseline_docling_corpus_roots"],
            "crop_ledger": self.config["baseline_crop_ledger"],
            "atlas_output": self.config["atlas_output"],
            "last_run_id": None,
            "prisma_update_history": prisma_history,
        }

    def artifact_roots(self) -> list[Path]:
        """Return declared filesystem bases for immutable artifacts outside the checkout."""
        if self._artifact_roots_cache is not None:
            return self._artifact_roots_cache

        values: list[str | Path] = []
        configured = self.config.get("artifact_roots") or []
        values.extend(configured if isinstance(configured, list) else [configured])
        environment = os.environ.get("REVIEW_ARTIFACT_ROOT", "")
        values.extend(value for value in environment.split(os.pathsep) if value)
        current_roots = self.current.get("artifact_roots") or []
        values.extend(current_roots if isinstance(current_roots, list) else [current_roots])

        taxonomy_root = resolve(self.current["taxonomy_root"])
        snapshot_manifest = taxonomy_root / "snapshot_manifest.json"
        if snapshot_manifest.is_file():
            payload = read_json(snapshot_manifest)
            manifest_roots = payload.get("artifact_roots") or []
            values.extend(
                manifest_roots if isinstance(manifest_roots, list) else [manifest_roots]
            )

        roots: list[Path] = []
        seen: set[Path] = set()
        for value in values:
            path = Path(value).expanduser()
            path = path if path.is_absolute() else ROOT / path
            path = path.resolve()
            if path not in seen:
                seen.add(path)
                roots.append(path)
        self._artifact_roots_cache = roots
        return roots

    def resolve_artifact(self, value: str | Path) -> Path:
        """Resolve a repository-relative immutable path through declared artifact roots."""
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
                        for root in self.artifact_roots()
                        if (root / suffix).exists()
                    ),
                    None,
                )
                if candidate is not None:
                    return candidate
            return path
        candidates = [ROOT / path, *((root / path) for root in self.artifact_roots())]
        return next((candidate for candidate in candidates if candidate.exists()), candidates[0])

    def artifact_root_arguments(self) -> list[str]:
        arguments: list[str] = []
        for root in self.artifact_roots():
            arguments.extend(["--artifact-root", str(root)])
        return arguments

    def new_manifest(self) -> dict[str, Any]:
        manifest = {
            "schema_version": 1,
            "run_id": self.run_id,
            "created": now_iso(),
            "date_from": self.date_from,
            "date_to": self.date_to,
            "config": rel(self.args.config),
            "prior_state": self.current,
            "stages": {},
            "published": False,
        }
        if self.config.get("method_lock"):
            lock_path = resolve(self.config["method_lock"])
            if lock_path.is_file():
                lock = read_json(lock_path)
                manifest["method_lock"] = {
                    "method_id": lock.get("method_id"),
                    "path": rel(lock_path),
                    "sha256": sha256(lock_path),
                }
        return manifest

    def method_lock_status(self, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.config.get("method_lock"):
            return {"ok": False, "issues": ["pipeline config does not declare method_lock"]}
        taxonomy_tree = self.resolve_artifact(self.current["taxonomy_root"]) / "taxonomy_tree.json"
        result = verify_method_lock(
            self.config["method_lock"],
            self.args.config,
            current_taxonomy_tree=taxonomy_tree,
        )
        binding = (manifest or self.manifest).get("method_lock")
        if not binding:
            result["ok"] = False
            result.setdefault("issues", []).append("run manifest is not bound to a method lock")
        else:
            if binding.get("sha256") != result.get("lock_sha256"):
                result["ok"] = False
                result.setdefault("issues", []).append(
                    "run manifest method-lock hash differs from the current lock"
                )
            if binding.get("method_id") != result.get("method_id"):
                result["ok"] = False
                result.setdefault("issues", []).append(
                    "run manifest method_id differs from the current lock"
                )
        return result

    def assert_method_lock(self) -> dict[str, Any]:
        result = self.method_lock_status()
        if not result["ok"]:
            raise RuntimeError("Method lock failed: " + "; ".join(result["issues"]))
        return result

    def save_manifest(self) -> None:
        self.run_root.mkdir(parents=True, exist_ok=True)
        self.manifest["updated"] = now_iso()
        write_json(self.manifest_path, self.manifest)

    def log_dir(self, stage: str) -> Path:
        return self.run_root / "logs" / stage

    def begin_log_attempt(self, stage: str) -> None:
        """Create an append-only command-log namespace for a stage execution."""
        root = self.log_dir(stage)
        previous = [
            int(path.name.removeprefix("attempt_"))
            for path in root.glob("attempt_*")
            if path.is_dir() and path.name.removeprefix("attempt_").isdigit()
        ] if root.exists() else []
        attempt = root / f"attempt_{max(previous, default=0) + 1:03d}"
        attempt.mkdir(parents=True, exist_ok=False)
        self._active_log_attempts[stage] = attempt

    def command_log_dir(self, stage: str) -> Path:
        return self._active_log_attempts.get(stage, self.log_dir(stage))

    @staticmethod
    def reset_generated_path(path: Path) -> None:
        """Remove only rerunnable stage output, never a human input declaration."""
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)

    def preserve_expensive_generated_path(self, stage: str, path: Path) -> Path | None:
        """Rotate an existing expensive stage output into an append-only attempt store."""
        if not path.exists():
            return None
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
            return None
        try:
            relative = path.resolve().relative_to(self.run_root.resolve())
        except ValueError as exc:
            raise RuntimeError(
                f"Refusing to preserve an expensive output outside the run root: {path}"
            ) from exc
        stage_root = self.run_root / "preserved_stage_outputs" / stage
        attempts = [
            int(candidate.name.removeprefix("attempt_"))
            for candidate in stage_root.glob("attempt_*")
            if candidate.is_dir()
            and candidate.name.removeprefix("attempt_").isdigit()
        ] if stage_root.exists() else []
        attempt = stage_root / f"attempt_{max(attempts, default=0) + 1:03d}"
        preserved = attempt / relative
        preserved.parent.mkdir(parents=True, exist_ok=False)
        path.rename(preserved)
        file_count = 1
        total_size = preserved.stat().st_size
        if preserved.is_dir():
            files = [candidate for candidate in preserved.rglob("*") if candidate.is_file()]
            file_count = len(files)
            total_size = sum(candidate.stat().st_size for candidate in files)
        ledger = self.run_root / "preserved_stage_outputs" / "preservation_ledger.jsonl"
        append_jsonl(
            ledger,
            {
                "preserved_at": now_iso(),
                "stage": stage,
                "original_path": rel(path),
                "preserved_path": rel(preserved),
                "file_count": file_count,
                "total_size_bytes": total_size,
                "reason": "existing expensive output rotated before a new stage attempt",
            },
        )
        return preserved

    def artifact(self, path: Path) -> dict[str, Any]:
        return {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256(path)}

    def artifact_archive_status(
        self,
        source_root: Path | None = None,
        *,
        require_independent: bool = False,
    ) -> dict[str, Any]:
        source = (source_root or self.run_root).resolve()
        manifest = source / "artifact_manifest.csv"
        summary = source / "artifact_manifest_summary.json"
        issues: list[str] = []
        if not manifest.is_file() or not summary.is_file():
            return {
                "ok": False,
                "source_root": str(source),
                "issues": ["artifact manifest and summary have not been generated"],
            }
        summary_payload = read_json(summary)
        manifest_sha = sha256(manifest)
        if summary_payload.get("manifest_sha256") != manifest_sha:
            issues.append("artifact manifest does not match its summary")
        receipt_root = resolve(
            self.config.get("archive_receipts_root", "data/living_catalog/archives")
        )
        matching: list[tuple[Path, dict[str, Any]]] = []
        for path in sorted(receipt_root.glob("*.json")) if receipt_root.is_dir() else []:
            try:
                receipt = read_json(path)
                receipt_source = Path(str(receipt.get("source_root") or "")).resolve()
            except (OSError, RuntimeError, TypeError, ValueError):
                continue
            if receipt_source == source and receipt.get("source_manifest_sha256") == manifest_sha:
                matching.append((path, receipt))
        if require_independent:
            matching = [
                item for item in matching if item[1].get("storage_class") == "independent_backup"
            ]
        valid: list[tuple[Path, dict[str, Any]]] = []
        for path, receipt in matching:
            archive = Path(str(receipt.get("archive_path") or ""))
            verification = receipt.get("verification") or {}
            if (
                verification.get("ok")
                and archive.is_file()
                and archive.stat().st_size == int(receipt.get("archive_size_bytes") or -1)
            ):
                valid.append((path, receipt))
        if not valid:
            scope = "independent verified" if require_independent else "verified"
            issues.append(f"no {scope} archive receipt matches the current artifact manifest")
        selected = valid[-1] if valid else None
        return {
            "ok": not issues,
            "source_root": str(source),
            "source_manifest_sha256": manifest_sha,
            "receipt": rel(selected[0]) if selected else None,
            "archive": selected[1].get("archive_path") if selected else None,
            "storage_class": selected[1].get("storage_class") if selected else None,
            "verified_at": (selected[1].get("verification") or {}).get("verified_at") if selected else None,
            "issues": issues,
        }

    def repository_external_artifacts(self) -> dict[str, dict[str, Any]]:
        """Return hash-ledger artifacts intentionally omitted from a Git checkout."""
        if self._repository_external_artifacts_cache is not None:
            return self._repository_external_artifacts_cache

        manifest_path = self.run_root / "artifact_manifest.csv"
        summary_path = self.run_root / "artifact_manifest_summary.json"
        if not manifest_path.is_file() or not summary_path.is_file():
            raise RuntimeError(
                "repository-checkout validation requires artifact_manifest.csv and "
                "artifact_manifest_summary.json in the selected run root"
            )
        summary = read_json(summary_path)
        if summary.get("manifest_sha256") != sha256(manifest_path):
            raise RuntimeError("artifact_manifest.csv does not match its committed summary hash")

        ledger: dict[str, dict[str, Any]] = {}
        total_size = 0
        with manifest_path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            required = {"relative_path", "size_bytes", "sha256"}
            if not required.issubset(reader.fieldnames or []):
                raise RuntimeError("artifact_manifest.csv is missing required columns")
            for row in reader:
                relative = Path(str(row["relative_path"]))
                if relative.is_absolute() or ".." in relative.parts:
                    raise RuntimeError(f"unsafe artifact ledger path: {relative}")
                path = rel(self.run_root / relative)
                if path in ledger:
                    raise RuntimeError(f"duplicate artifact ledger path: {path}")
                try:
                    size = int(row["size_bytes"])
                except (TypeError, ValueError) as exc:
                    raise RuntimeError(f"invalid artifact size for {path}") from exc
                digest = str(row["sha256"])
                if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                    raise RuntimeError(f"invalid artifact SHA-256 for {path}")
                ledger[path] = {"path": path, "bytes": size, "sha256": digest}
                total_size += size

        if int(summary.get("file_count", -1)) != len(ledger):
            raise RuntimeError("artifact ledger file count does not match its summary")
        if int(summary.get("total_size_bytes", -1)) != total_size:
            raise RuntimeError("artifact ledger byte count does not match its summary")

        tracked_result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if tracked_result.returncode:
            raise RuntimeError(f"cannot inspect tracked files: {tracked_result.stderr.strip()}")
        tracked = {path for path in tracked_result.stdout.split("\0") if path}
        for required_path in (rel(manifest_path), rel(summary_path)):
            if required_path not in tracked:
                raise RuntimeError(f"repository artifact ledger is not tracked: {required_path}")

        candidates = sorted(path for path in ledger if path not in tracked)
        ignored: set[str] = set()
        if candidates:
            ignored_result = subprocess.run(
                ["git", "-C", str(ROOT), "check-ignore", "--no-index", "-z", "--stdin"],
                input="\0".join(candidates) + "\0",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if ignored_result.returncode not in {0, 1}:
                raise RuntimeError(f"cannot inspect ignored files: {ignored_result.stderr.strip()}")
            ignored = {path for path in ignored_result.stdout.split("\0") if path}

        self._repository_external_artifacts_cache = {
            path: ledger[path] for path in candidates if path in ignored
        }
        self._repository_artifact_ledger_summary = {
            "manifest": rel(manifest_path),
            "manifest_sha256": summary["manifest_sha256"],
            "ledger_files": len(ledger),
            "declared_external_files": len(self._repository_external_artifacts_cache),
        }
        return self._repository_external_artifacts_cache

    def repository_artifact_is_external(self, artifact: dict[str, Any]) -> bool:
        expected = self.repository_external_artifacts().get(str(artifact.get("path") or ""))
        return bool(
            expected
            and expected["bytes"] == artifact.get("bytes")
            and expected["sha256"] == artifact.get("sha256")
        )

    def human_input_paths(self, stage: str) -> list[Path]:
        paths = {
            "search": [self.paths.search / "google_scholar_provider_export.json"],
            "prepare-records": [
                self.paths.records / "manual_cross_dedup_resolutions.json",
                self.paths.records / "supplemental_recall_records.json",
            ],
            "fulltext-download": [self.paths.fulltext / "manual_fulltexts.json"],
            "fulltext-screening": [self.paths.section_input / "manual_section_overrides.json"],
            "eligibility-resolution": [self.paths.eligibility / "manual_resolution.csv"],
        }.get(stage, [])
        if stage == "fulltext-candidates" and self.manifest.get("method_lock"):
            paths = [
                self.paths.fulltext / "postscreen_dedup/duplicate_resolutions.json"
            ]
        return paths

    def human_input_fingerprints(self, stage: str) -> list[dict[str, Any]]:
        fingerprints = []
        for path in self.human_input_paths(stage):
            row: dict[str, Any] = {"path": rel(path), "present": path.is_file()}
            if path.is_file():
                row.update({"bytes": path.stat().st_size, "sha256": sha256(path)})
            fingerprints.append(row)
        return fingerprints

    def stage_data_roots(self, stage: str) -> list[Path]:
        taxonomy_final_files = [
            "adjudication_resolution_manifest.csv",
            "route_annotations.jsonl",
            "route_annotations.csv",
            "route_candidates_all.jsonl",
            "evidence_ledger.jsonl",
            "uncertainty_cases.jsonl",
            "model_registry.csv",
            "analysis_run_metadata.json",
            "agreement_metrics.json",
            "agreement_report.md",
            "manuscript_methods.md",
            "manuscript_taxonomy_tables.md",
            "failure_mode_report.md",
            "special_cases.jsonl",
            "special_cases_report.md",
        ]
        return {
            "search": [self.paths.search],
            "deduplicate": [self.paths.dedup],
            "prepare-records": [self.paths.records],
            "enrich-abstracts": [self.paths.abstracts],
            "abstract-screening": [self.paths.abstract_screening],
            "fulltext-candidates": [
                self.paths.fulltext_candidates,
                self.paths.fulltext_candidates.with_suffix(".csv"),
            ],
            "fulltext-download": [
                self.paths.fulltext / "workers",
                self.paths.fulltext / "manual_files",
                self.paths.download_manifest,
                self.paths.download_manifest.with_suffix(".csv"),
                self.paths.fulltext / "manual_fulltexts.json",
                self.paths.fulltext / "manual_fulltexts.template.json",
                self.paths.fulltext / "retrieval_manual_gate.json",
                self.paths.retrieval_dispositions,
            ],
            "docling-screening": [self.paths.docling_screen],
            "graph-sections": [
                self.paths.graph_sections,
                self.paths.section_screening_input,
                self.paths.section_screening_input.with_suffix(".jsonl"),
                self.paths.section_input / "section_selection_provenance.json",
                self.paths.section_input / "fulltext_section_audit.csv",
                self.paths.section_input / "run_metadata.json",
            ],
            "fulltext-screening": [
                self.paths.fulltext_screening,
                self.paths.section_input / "manual_section_overrides.json",
                self.paths.section_input / "manual_section_overrides.template.json",
                self.paths.section_input / "manual_section_override_audit.json",
                self.paths.section_input / "fulltext_screening_input_with_overrides.json",
            ],
            "eligibility-resolution": [self.paths.eligibility],
            "docling-vlm": [self.paths.docling_vlm],
            "taxonomy-discovery": [
                self.paths.taxonomy / "runs/discovery",
                self.paths.taxonomy / "taxonomy_synthesis",
                self.paths.taxonomy / "study_model_registry.csv",
                self.paths.taxonomy / "registry_summary.json",
                self.paths.taxonomy / "no_new_eligible_records.json",
            ],
            "taxonomy-classification": [
                self.paths.taxonomy / "runs/classification_fixed_r1",
                self.paths.taxonomy / "runs/classification_fixed_r2",
                self.paths.taxonomy / "runs/classification_fixed_r3",
                self.paths.taxonomy / "runs/classification_dense",
                self.paths.taxonomy / "adjudication",
                self.paths.taxonomy / "semantic_sufficiency",
                self.paths.taxonomy / "semantic_correction_decisions",
                self.paths.taxonomy / "semantic_correction_applied",
                self.paths.taxonomy / "semantic_sufficiency_revalidation",
                self.paths.taxonomy / "tables",
                self.paths.taxonomy / "no_new_eligible_records.json",
                self.paths.taxonomy / "authoritative_taxonomy.json",
                self.paths.taxonomy / "taxonomy_tree.json",
                self.paths.taxonomy / "taxonomy_codebook.md",
                *[self.paths.taxonomy / name for name in taxonomy_final_files],
            ],
            "crop-validation": [self.paths.crops],
            "snapshot": [self.paths.snapshot],
            "atlas": [self.paths.atlas],
            "report": [self.paths.report],
        }[stage]

    def write_stage_inventory(self, stage: str) -> Path:
        inventory = self.log_dir(stage) / "artifact_inventory.json"
        files: dict[str, Path] = {}
        for root in [*self.stage_data_roots(stage), self.log_dir(stage)]:
            if root.is_file():
                files[str(root.resolve())] = root
            elif root.is_dir():
                for path in root.rglob("*"):
                    if path.is_file() and path.resolve() != inventory.resolve():
                        files[str(path.resolve())] = path
        rows = [self.artifact(files[key]) for key in sorted(files)]
        write_json(
            inventory,
            {"created": now_iso(), "stage": stage, "file_count": len(rows), "files": rows},
        )
        return inventory

    def stage_validation_issues(
        self,
        stage: str,
        repository_checkout: bool = False,
        repository_omissions: list[str] | None = None,
    ) -> list[str]:
        row = self.manifest["stages"].get(stage, {})
        if row.get("status") not in {"complete", "skipped_no_new_records"}:
            return [f"status={row.get('status', 'not_started')}"]
        issues: list[str] = []
        expected_inputs = row.get("human_input_fingerprints", [])
        expected_paths = {item.get("path") for item in expected_inputs}
        observed_inputs = [
            item
            for item in self.human_input_fingerprints(stage)
            if item.get("present") or item.get("path") in expected_paths
        ]
        if expected_inputs != observed_inputs:
            issues.append("human input fingerprints changed")
        for artifact in row.get("artifacts", []):
            path = self.resolve_artifact(artifact["path"])
            if not path.exists():
                if repository_checkout and self.repository_artifact_is_external(artifact):
                    if repository_omissions is not None:
                        repository_omissions.append(artifact["path"])
                else:
                    issues.append(f"missing declared artifact: {artifact['path']}")
            elif sha256(path) != artifact["sha256"]:
                issues.append(f"changed declared artifact: {artifact['path']}")
        inventory_path = row.get("artifact_inventory")
        if inventory_path:
            resolved_inventory = self.resolve_artifact(inventory_path)
            if not resolved_inventory.exists():
                issues.append(f"missing artifact inventory: {inventory_path}")
            elif sha256(resolved_inventory) != row.get("artifact_inventory_sha256"):
                issues.append(f"changed artifact inventory: {inventory_path}")
            else:
                inventory = read_json(resolved_inventory)
                for artifact in inventory.get("files", []):
                    path = self.resolve_artifact(artifact["path"])
                    if not path.exists():
                        if repository_checkout and self.repository_artifact_is_external(artifact):
                            if repository_omissions is not None:
                                repository_omissions.append(artifact["path"])
                        else:
                            issues.append(f"missing inventoried file: {artifact['path']}")
                    elif sha256(path) != artifact["sha256"]:
                        issues.append(f"changed inventoried file: {artifact['path']}")
        return issues

    def stage_is_complete(self, stage: str) -> bool:
        return not self.stage_validation_issues(stage)

    def run_command(
        self,
        stage: str,
        name: str,
        command: list[str],
        timeout: int | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> None:
        root = self.command_log_dir(stage) / name
        root.mkdir(parents=True, exist_ok=True)
        write_json(root / "command.json", {"command": command, "cwd": str(ROOT)})
        started = time.monotonic()
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env={**os.environ, "NO_COLOR": "1", **(extra_env or {})},
        )
        (root / "stdout.log").write_text(result.stdout, encoding="utf-8")
        (root / "stderr.log").write_text(result.stderr, encoding="utf-8")
        write_json(
            root / "result.json",
            {
                "returncode": result.returncode,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "finished": now_iso(),
            },
        )
        if result.returncode:
            tail = "\n".join(result.stderr.splitlines()[-20:])
            raise RuntimeError(f"{stage}/{name} failed ({result.returncode}): {tail}")

    def run_parallel(
        self,
        stage: str,
        commands: list[tuple[str, list[str]]],
        max_workers: int | None = None,
    ) -> None:
        configured = max_workers or int(self.config.get("graph_workers", 1))
        max_workers = min(len(commands), max(1, configured))
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {
                pool.submit(self.run_command, stage, name, command, None): name
                for name, command in commands
            }
            errors = []
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    errors.append((futures[future], exc))
            if errors:
                raise RuntimeError(
                    "; ".join(f"{name}: {exc}" for name, exc in errors)
                )

    def mark(self, stage: str, status: str, outputs: list[Path], note: str = "") -> None:
        missing = [path for path in outputs if not path.exists()]
        if status == "complete" and missing:
            raise RuntimeError(f"Stage {stage} did not produce: {missing}")
        inventory = self.write_stage_inventory(stage)
        self.manifest["stages"][stage] = {
            "status": status,
            "finished": now_iso(),
            "note": note,
            "artifacts": [self.artifact(path) for path in outputs if path.is_file()],
            "artifact_inventory": rel(inventory),
            "artifact_inventory_sha256": sha256(inventory),
            "human_input_fingerprints": self.human_input_fingerprints(stage),
        }
        self.save_manifest()

    def execute_stage(self, stage: str, callback: Callable[[], list[Path]]) -> None:
        if self.stage_is_complete(stage) and not self.args.force:
            print(f"skip complete: {stage}")
            return
        self.begin_log_attempt(stage)
        self.manifest["stages"][stage] = {"status": "running", "started": now_iso()}
        self.save_manifest()
        print(f"run: {stage}", flush=True)
        try:
            outputs = callback()
            self.mark(stage, "complete", outputs)
        except ManualGate as exc:
            self.manifest["stages"][stage] = {
                "status": "needs_manual_resolution",
                "finished": now_iso(),
                "note": str(exc),
            }
            self.save_manifest()
            raise
        except Exception as exc:
            self.manifest["stages"][stage] = {
                "status": "failed",
                "finished": now_iso(),
                "error": repr(exc),
            }
            self.save_manifest()
            raise

    def invalidate_from(self, stage: str, include_stage: bool, reason: str) -> None:
        start = STAGES.index(stage) + (0 if include_stage else 1)
        history = self.manifest.setdefault("invalidation_history", [])
        invalidated = []
        for name in STAGES[start:]:
            previous = self.manifest["stages"].pop(name, None)
            if previous is not None:
                invalidated.append({"stage": name, "previous": previous})
        if invalidated:
            history.append(
                {
                    "at": now_iso(),
                    "trigger_stage": stage,
                    "include_trigger_stage": include_stage,
                    "reason": reason,
                    "invalidated": invalidated,
                }
            )
            self.save_manifest()

    def python(self) -> str:
        return sys.executable

    def docling_python(self) -> str:
        path = self.resolve_artifact(self.config["docling_python"])
        if not path.exists():
            raise RuntimeError(
                f"Docling environment is missing: {path}. Install scripts/docling/requirements-docling.txt first."
            )
        return str(path)

    def enabled_databases(self) -> list[str]:
        config = read_json(self.paths.search_config)
        return [name for name, value in config["databases"].items() if value.get("enabled")]

    def ensure_search_config(self) -> None:
        if self.paths.search_config.is_file():
            config = read_json(self.paths.search_config)
            metadata = config.get("metadata") or {}
            if metadata.get("date_from") != self.date_from or metadata.get("date_to") != self.date_to:
                raise RuntimeError("Existing search config does not match the run interval")
            return
        self.begin_log_attempt("search-provider")
        self.run_command(
            "search-provider",
            "build-config",
            [
                self.python(),
                "scripts/build_search_update_config.py",
                "--template",
                str(resolve(self.config["search_config_template"])),
                "--date-from",
                self.date_from,
                "--date-to",
                self.date_to,
                "--output",
                str(self.paths.search_config),
            ],
        )

    def scholar_validate(self) -> int:
        if not self.manifest_path.is_file():
            self.save_manifest()
        self.ensure_search_config()
        export = self.paths.search / "google_scholar_provider_export.json"
        if not export.is_file():
            raise RuntimeError(
                f"Google Scholar provider export is missing: {export}. Run scholar-capture first."
            )
        from reproduce_search import load_google_scholar_provider_export

        validated = load_google_scholar_provider_export(read_json(self.paths.search_config), export)
        validation = {
            "schema_version": 1,
            "validated_at": now_iso(),
            "run_id": self.run_id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "provider_export": self.artifact(export),
            "query_signature": validated["query_signature"],
            "query_count": len(validated["query_execution"]),
            "records_fetched": validated["records_fetched"],
            "raw_response_count": len(validated["raw_response_manifest"]),
            "execution": validated["execution"],
        }
        output = self.paths.search / "google_scholar_validation.json"
        if not self.manifest.get("published"):
            write_json(output, validation)
            validation["validation_artifact"] = rel(output)
        else:
            validation["validation_artifact"] = "read_only_validation_of_published_run"
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return 0

    def scholar_capture(self) -> int:
        if self.manifest.get("published"):
            raise RuntimeError("A published run's search evidence is immutable")
        if not self.manifest_path.is_file():
            self.save_manifest()
        self.ensure_search_config()
        keys = self.resolve_artifact(self.config["api_keys_file"])
        if not keys.is_file():
            raise RuntimeError(f"Missing ignored API key file: {keys}")
        self.begin_log_attempt("search-provider")
        self.run_command(
            "search-provider",
            "serpapi-capture",
            [
                self.python(),
                "scripts/capture_google_scholar_serpapi.py",
                "--config",
                str(self.paths.search_config),
                "--api-keys",
                str(keys),
                "--output",
                str(self.paths.search / "google_scholar_provider_export.json"),
                "--retries",
                str(self.args.retries),
                "--delay",
                str(self.args.delay),
            ],
        )
        return self.scholar_validate()

    def register_supplemental(self) -> int:
        if self.manifest.get("published"):
            raise RuntimeError(
                "Cannot mutate a published run. Record a post-publication correction and use "
                "the reconciliation path instead."
            )
        source = resolve(self.args.record_file)
        if not source.is_file():
            raise RuntimeError(f"Supplemental source record file is missing: {source}")
        payload = read_json(source)
        if isinstance(payload, dict) and isinstance(payload.get("records"), list):
            records = payload["records"]
        elif isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict):
            records = [payload]
        else:
            raise RuntimeError("Supplemental record file must contain a record or records list")
        if not records:
            raise RuntimeError("Supplemental record file is empty")
        declared_at = self.args.declared_at or now_iso()
        declarations = []
        for record in records:
            title = str(record.get("title") or record.get("title_original") or "").strip()
            source_url = str(self.args.source_url or record.get("url") or "").strip()
            if not title or not source_url:
                raise RuntimeError("Every supplemental record requires a title and source URL")
            declarations.append(
                {
                    "record": record,
                    "reason": self.args.reason,
                    "source_url": source_url,
                    "resolver": self.args.resolver,
                    "declared_at": declared_at,
                    "source_artifact": self.artifact(source),
                }
            )
        target = self.paths.records / "supplemental_recall_records.json"
        existing = read_json(target) if target.is_file() else {
            "schema_version": 1,
            "run_id": self.run_id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "declarations": [],
        }
        existing["declarations"].extend(declarations)
        existing["updated"] = now_iso()
        write_json(target, existing)
        self.invalidate_from(
            "prepare-records",
            include_stage=True,
            reason="A declared supplemental recall record entered before cumulative deduplication.",
        )
        self.save_manifest()
        result = {
            "registered": len(declarations),
            "target": rel(target),
            "resume_command": (
                f"python3 scripts/run_living_review_pipeline.py run --run-id {self.run_id} "
                "--from-stage prepare-records --manage-server"
            ),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    def taxonomy_rerun_preflight(self) -> int:
        command = [
            self.python(),
            "scripts/prepare_full_cohort_taxonomy_rerun.py",
            "--state",
            str(resolve(self.config["living_state"])),
            "--pipeline-config",
            str(self.args.config),
            "--output-dir",
            str(resolve(self.args.output_dir)),
        ]
        return subprocess.run(command, cwd=ROOT).returncode

    def release_manifest(self) -> int:
        atlas_root = resolve(self.config["atlas_output"])
        if not (atlas_root / "data/atlas.json").is_file():
            raise RuntimeError(f"Atlas is incomplete: {atlas_root}")
        tree = atlas_tree_manifest(atlas_root)
        payload = {
            "schema_version": 1,
            "created": now_iso(),
            "commit": self.args.commit,
            "run_id": self.current.get("last_run_id"),
            "living_state": self.artifact(resolve(self.config["living_state"])),
            "atlas_json": self.artifact(atlas_root / "data/atlas.json"),
            "atlas_tree": tree,
        }
        output = atlas_root / "data/deployment.json"
        write_json(output, payload)
        print(json.dumps({**payload, "atlas_tree": {key: value for key, value in tree.items() if key != "files"}}, ensure_ascii=False, indent=2))
        return 0

    def record_incident(self) -> int:
        root = resolve(
            self.config.get("release_records_root", "data/living_catalog/releases")
        ) / self.run_id / "incidents"
        root.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        output = root / f"{timestamp}.json"
        payload = {
            "schema_version": 1,
            "created": now_iso(),
            "run_id": self.run_id,
            "phase": self.args.phase,
            "summary": self.args.summary,
            "commit": self.args.commit or "",
            "workflow_run_id": self.args.workflow_run_id or "",
            "recovery_commit": self.args.recovery_commit or "",
            "operator": self.args.operator,
            "run_manifest": self.artifact(self.manifest_path) if self.manifest_path.is_file() else None,
            "living_state": self.artifact(resolve(self.config["living_state"]))
            if resolve(self.config["living_state"]).is_file()
            else None,
        }
        write_json(output, payload)
        print(json.dumps({"incident": rel(output), **payload}, ensure_ascii=False, indent=2))
        return 0

    def stage_search(self) -> list[Path]:
        self.paths.search.mkdir(parents=True, exist_ok=True)
        completion_gate = self.paths.search / "search_completion_gate.json"
        self.reset_generated_path(completion_gate)
        self.run_command(
            "search",
            "build-config",
            [
                self.python(), "scripts/build_search_update_config.py",
                "--template", str(resolve(self.config["search_config_template"])),
                "--date-from", self.date_from, "--date-to", self.date_to,
                "--output", str(self.paths.search_config),
            ],
        )
        keys = self.resolve_artifact(self.config["api_keys_file"])
        if not keys.exists():
            raise RuntimeError(f"Missing ignored API key file: {keys}")
        command = [
            self.python(), "scripts/reproduce_search.py", "--config", str(self.paths.search_config),
            "--keys", str(keys), "--output-dir", str(self.paths.search_exports),
            "--file-date", self.date_to,
        ]
        scholar_export = self.paths.search / "google_scholar_provider_export.json"
        if scholar_export.is_file():
            command.extend(["--gs-provider-export", str(scholar_export)])
        search_error: RuntimeError | None = None
        try:
            self.run_command("search", "database-search", command)
        except RuntimeError as exc:
            search_error = exc
        summary = self.paths.search_exports / f"search_summary_{self.date_to}.json"
        if not summary.is_file():
            if search_error:
                raise search_error
            raise RuntimeError(f"Search did not produce its completeness summary: {summary}")
        search_summary = read_json(summary)
        found = set(search_summary.get("results_per_database", {}))
        missing = set(self.enabled_databases()) - found
        if missing:
            search_summary.setdefault("incomplete_databases", []).extend(sorted(missing))
        incomplete = search_summary.get("incomplete_databases", [])
        if not search_summary.get("complete", False) or incomplete:
            incomplete = sorted(set(incomplete))
            write_json(
                completion_gate,
                {
                    "created": now_iso(),
                    "incomplete_databases": incomplete,
                    "database_status": {
                        name: (search_summary.get("database_status") or {}).get(name, {})
                        for name in incomplete
                    },
                    "summary": rel(summary),
                    "resolution": (
                        "Supply missing credentials/provider export or resolve the reported "
                        "provider failure, then rerun search. Completed source exports remain "
                        "auditable but cannot enter dedup until all enabled sources complete."
                    ),
                },
            )
            raise ManualGate(
                "Search captured available sources but remains incomplete for: "
                + ", ".join(incomplete)
                + f". See {completion_gate}."
            )
        if search_error:
            raise search_error
        return [self.paths.search_config, summary]

    def stage_deduplicate(self) -> list[Path]:
        self.run_command(
            "deduplicate", "within-update",
            [
                self.python(), "scripts/deduplicate.py", "--exports-dir", str(self.paths.search_exports),
                "--date", self.date_to, "--output-dir", str(self.paths.dedup),
                "--search-summary",
                str(self.paths.search_exports / f"search_summary_{self.date_to}.json"),
            ],
        )
        return [
            self.paths.dedup / "deduplicated_records.json",
            self.paths.dedup / "deduplication_stats.json",
            self.paths.dedup / "deduplication_review_queue.json",
        ]

    def stage_prepare_records(self) -> list[Path]:
        update_records = self.paths.dedup / "deduplicated_records.json"
        supplemental = self.paths.records / "supplemental_recall_records.json"
        supplemental_audit = self.paths.records / "supplemental_recall_merge_audit.json"
        if supplemental.is_file():
            update_records = self.paths.records / "deduplicated_records_with_supplemental.json"
            self.run_command(
                "prepare-records",
                "merge-supplemental-recall",
                [
                    self.python(),
                    "scripts/merge_supplemental_recall_records.py",
                    "--canonical",
                    str(self.paths.dedup / "deduplicated_records.json"),
                    "--declarations",
                    str(supplemental),
                    "--output",
                    str(update_records),
                    "--audit-output",
                    str(supplemental_audit),
                ],
            )
        command = [
            self.python(), "scripts/prepare_incremental_records.py",
            "--update-records", str(update_records),
            "--output-dir", str(self.paths.records), "--run-id", self.run_id,
        ]
        for path in self.current["master_record_files"]:
            command.extend(["--master-records", str(self.resolve_artifact(path))])
        manual_resolutions = self.paths.records / "manual_cross_dedup_resolutions.json"
        if manual_resolutions.is_file():
            command.extend(
                ["--manual-cross-dedup-resolutions", str(manual_resolutions)]
            )
        try:
            self.run_command("prepare-records", "cross-dedup-crossref", command)
        except RuntimeError as exc:
            queue_path = self.paths.records / "cross_dedup_review_queue.json"
            queue = records_from(queue_path) if queue_path.is_file() else []
            if queue:
                template = self.paths.records / "manual_cross_dedup_resolutions.template.json"
                write_json(
                    template,
                    {
                        "schema_version": 1,
                        "records": [
                            {
                                "update_cluster_id": str(
                                    (row.get("update") or {}).get("cluster_id") or ""
                                ),
                                "decision": "",
                                "rationale": "",
                                "resolver": "",
                                "resolved_at": "",
                            }
                            for row in queue
                        ],
                    },
                )
                raise ManualGate(
                    f"{len(queue)} cumulative dedup conflicts require exact resolutions. "
                    f"Complete {manual_resolutions} from {template}."
                ) from exc
            raise
        outputs = [
            self.paths.records / "new_records_after_cross_dedup_crossref_checked.json",
            self.paths.records / "cross_dedup_stats.json",
            self.paths.records / "cross_dedup_review_queue.json",
            self.paths.records / "crossref_duplicate_audit.json",
            self.paths.records / "crossref_checked_stats.json",
        ]
        if supplemental.is_file():
            outputs.extend([update_records, supplemental_audit])
        return outputs

    def stage_enrich_abstracts(self) -> list[Path]:
        source = self.paths.records / "new_records_after_cross_dedup_crossref_checked.json"
        missing_enriched = self.paths.abstracts / "missing_abstracts_enriched.json"
        short_enriched = self.paths.abstracts / "short_abstracts_enriched.json"
        missing_log = self.paths.abstracts / "missing_enrichment_log.json"
        short_log = self.paths.abstracts / "short_enrichment_log.json"
        keys = self.resolve_artifact(self.config["api_keys_file"])
        self.paths.abstracts.mkdir(parents=True, exist_ok=True)

        def reusable(output: Path, log: Path, input_path: Path) -> bool:
            if not output.is_file() or not log.is_file():
                return False
            try:
                log_payload = read_json(log)
                finished = bool(log_payload.get("finished"))
                current_version = log_payload.get("enrichment_version") == 2
            except (OSError, ValueError, AttributeError):
                return False
            return (
                finished
                and current_version
                and output.stat().st_mtime >= input_path.stat().st_mtime
            )

        if not reusable(missing_enriched, missing_log, source):
            self.run_command(
                "enrich-abstracts", "missing",
                [
                    self.python(), "scripts/enrich_abstracts.py", "--keys", str(keys),
                    "--input", str(source), "--output", str(missing_enriched),
                    "--excluded-output", str(self.paths.abstracts / "excluded_no_abstract_initial.json"),
                    "--log-output", str(missing_log),
                ],
            )
        if not reusable(short_enriched, short_log, missing_enriched):
            self.run_command(
                "enrich-abstracts", "short",
                [
                    self.python(), "scripts/enrich_short_abstracts.py", "--keys", str(keys),
                    "--input", str(missing_enriched), "--output", str(short_enriched),
                    "--log-output", str(short_log),
                    "--max-len", "250",
                ],
            )
        self.run_command(
            "enrich-abstracts", "screening-cohort",
            [
                self.python(), "scripts/build_living_review_cohorts.py", "abstract-input",
                "--input", str(short_enriched), "--output", str(self.paths.abstract_input),
                "--excluded-output", str(self.paths.abstracts / "excluded_no_usable_abstract.json"),
                "--minimum-chars", str(self.config["minimum_abstract_chars"]),
            ],
        )
        return [self.paths.abstract_input, self.paths.abstracts / "excluded_no_usable_abstract.json"]

    def empty_screening(self, output: Path, evidence_mode: str) -> None:
        output.mkdir(parents=True, exist_ok=True)
        write_json(output / "input_records.json", [])
        write_json(output / "final_screening_results.json", {"metadata": {"evidence_mode": evidence_mode}, "records": []})
        write_json(output / "summary.json", {"total_records": 0, "decision_counts": {}, "adjudicated": 0})

    def write_abstract_screening_crosswalk(self) -> Path:
        """Bind legacy positional screening IDs back to stable catalog IDs."""
        canonical = records_from(self.paths.abstract_input)
        screened = records_from(self.paths.abstract_screening / "input_records.json")
        if len(canonical) != len(screened):
            raise RuntimeError(
                "Legacy abstract screening input does not preserve the canonical cohort size"
            )
        rows = []
        for position, (source, legacy) in enumerate(zip(canonical, screened), 1):
            stable_id = str(source.get("record_id") or "")
            legacy_id = str(legacy.get("record_id") or "")
            if not stable_id or not legacy_id:
                raise RuntimeError("Abstract screening crosswalk contains an empty record ID")
            for field in ("title", "abstract", "doi"):
                if str(source.get(field) or "") != str(legacy.get(field) or ""):
                    raise RuntimeError(
                        f"Legacy abstract screening changed {field} at position {position}"
                    )
            rows.append(
                {
                    "legacy_record_id": legacy_id,
                    "stable_record_id": stable_id,
                    "candidate_id": str(source.get("candidate_id") or stable_id),
                    "input_position": position,
                }
            )
        if len({row["legacy_record_id"] for row in rows}) != len(rows):
            raise RuntimeError("Legacy abstract screening IDs are not unique")
        if len({row["stable_record_id"] for row in rows}) != len(rows):
            raise RuntimeError("Canonical abstract screening IDs are not unique")
        output = self.paths.abstract_screening / "record_id_crosswalk.json"
        write_json(
            output,
            {
                "schema_version": 1,
                "created": now_iso(),
                "canonical_input": rel(self.paths.abstract_input),
                "legacy_input": rel(self.paths.abstract_screening / "input_records.json"),
                "records": rows,
            },
        )
        return output

    def screening_command(self, input_path: Path, output: Path, evidence_mode: str) -> list[str]:
        if evidence_mode == "title_abstract":
            legacy = self.config["legacy_abstract_screening"]
            runner = ROOT / legacy["runner"]
            expected_files = {runner: legacy["runner_sha256"]}
            prompt_dir = ROOT / legacy["prompt_dir"]
            expected_files.update(
                {prompt_dir / name: expected for name, expected in legacy["prompt_sha256"].items()}
            )
            mismatches = [
                f"{rel(path)}: expected {expected}, got {sha256(path) if path.exists() else 'missing'}"
                for path, expected in expected_files.items()
                if not path.exists() or sha256(path) != expected
            ]
            if mismatches:
                raise RuntimeError(
                    "Frozen title/abstract screening artifacts failed integrity checks:\n"
                    + "\n".join(mismatches)
                )
            return [
                self.python(), str(runner), "--input", str(input_path),
                "--output-dir", str(output), "--model", self.config["models"]["screening"],
                "--batch-size", str(self.config["screening_batch_size"]),
                "--adjudicator-batch-size", str(self.config["adjudicator_batch_size"]),
                "--max-workers", str(legacy["max_workers"]),
            ]
        return [
            self.python(), "scripts/run_codex_screening_pipeline.py", "--input", str(input_path),
            "--output-dir", str(output), "--model", self.config["models"]["screening"],
            "--batch-size", str(self.config["screening_batch_size"]),
            "--adjudicator-batch-size", str(self.config["adjudicator_batch_size"]),
            "--max-workers", str(self.config["screening_workers"]),
            "--batch-attempts", str(self.config["screening_batch_attempts"]),
            "--codex-timeout", str(self.config["codex_timeout_seconds"]),
            "--evidence-mode", evidence_mode,
        ]

    def stage_abstract_screening(self) -> list[Path]:
        self.reset_generated_path(self.paths.abstract_screening)
        if record_count(self.paths.abstract_input) == 0:
            self.empty_screening(self.paths.abstract_screening, "title_abstract")
        else:
            self.run_command(
                "abstract-screening", "codex-pipeline",
                self.screening_command(self.paths.abstract_input, self.paths.abstract_screening, "title_abstract"),
            )
        crosswalk = self.write_abstract_screening_crosswalk()
        return [
            self.paths.abstract_screening / "final_screening_results.json",
            self.paths.abstract_screening / "summary.json",
            crosswalk,
        ]

    def stage_fulltext_candidates(self) -> list[Path]:
        duplicate_resolutions = (
            self.paths.fulltext / "postscreen_dedup/duplicate_resolutions.json"
        )
        command = [
            self.python(), "scripts/build_living_review_cohorts.py", "fulltext-candidates",
            "--screening-results", str(self.paths.abstract_screening / "final_screening_results.json"),
            "--screening-input", str(self.paths.abstract_screening / "input_records.json"),
            "--record-id-crosswalk", str(self.paths.abstract_screening / "record_id_crosswalk.json"),
            "--canonical-input", str(self.paths.abstract_input),
            "--output", str(self.paths.fulltext_candidates),
        ]
        if duplicate_resolutions.is_file():
            command[command.index("--output"):command.index("--output")] = [
                "--duplicate-resolutions", str(duplicate_resolutions)
            ]
        self.run_command(
            "fulltext-candidates", "select",
            command,
        )
        return [self.paths.fulltext_candidates]

    def stage_fulltext_download(self) -> list[Path]:
        # Validated worker payloads are cumulative: retries must not discard a
        # previously retrieved full text because a provider is temporarily down.
        self.reset_generated_path(self.paths.fulltext / "manual_files")
        self.reset_generated_path(self.paths.fulltext / "retrieval_manual_gate.json")
        count = record_count(self.paths.fulltext_candidates)
        if count == 0:
            write_json(self.paths.download_manifest, {"created": now_iso(), "processed": 0, "results": []})
            template = self.paths.fulltext / "manual_fulltexts.template.json"
            write_json(template, {"records": []})
            write_json(
                self.paths.retrieval_dispositions,
                {
                    "schema_version": 1,
                    "created": now_iso(),
                    "candidate_count": 0,
                    "disposition_counts": {},
                    "rows": [],
                },
            )
            return [self.paths.download_manifest, template, self.paths.retrieval_dispositions]
        workers = min(count, int(self.config["download_workers"]))
        batch_size = math.ceil(count / workers)
        commands = []
        for worker in range(workers):
            offset = worker * batch_size
            if offset >= count:
                break
            limit = min(batch_size, count - offset)
            out = self.paths.fulltext / "workers" / f"worker_{worker:02d}"
            commands.append(
                (
                    f"worker-{worker:02d}",
                    [
                        self.python(), "scripts/download_full_texts.py", "--input", str(self.paths.fulltext_candidates),
                        "--out-dir", str(out), "--offset", str(offset), "--limit", str(limit),
                    ],
                )
            )
        self.run_parallel(
            "fulltext-download", commands, max_workers=int(self.config["download_workers"])
        )
        consolidate = [self.python(), "scripts/build_living_review_cohorts.py", "consolidate-downloads"]
        for worker, _ in commands:
            number = worker.split("-")[1]
            consolidate.extend(["--manifest", str(self.paths.fulltext / "workers" / f"worker_{number}" / "batch_manifest.json")])
        manual_manifest = self.paths.fulltext / "manual_fulltexts.json"
        if manual_manifest.exists():
            consolidate.extend(["--manual-manifest", str(manual_manifest)])
        consolidate.extend(["--output", str(self.paths.download_manifest)])
        self.run_command("fulltext-download", "consolidate", consolidate)
        consolidated = read_json(self.paths.download_manifest)
        candidates = records_from(self.paths.fulltext_candidates)
        retrieval = retrieval_disposition_table(candidates, consolidated, [])
        write_json(
            self.paths.retrieval_dispositions,
            {
                "schema_version": 1,
                "created": now_iso(),
                "candidate_count": retrieval["candidate_count"],
                "disposition_counts": retrieval["disposition_counts"],
                "rows": retrieval["rows"],
                "definitions": {
                    "terminal_retrieval_evidence": (
                        "A validated payload was retrieved or the complete attempt ledger supports "
                        "a terminal not-retrieved/access-restricted disposition."
                    ),
                    "manual_gate_required": (
                        "The attempt ended in a transport/provider failure or unsupported XML-only "
                        "payload and cannot be interpreted as negative retrieval evidence."
                    ),
                },
            },
        )
        template = self.paths.fulltext / "manual_fulltexts.template.json"
        write_json(
            template,
            {
                "records": [
                    {
                        "candidate_id": row.get("candidate_id"),
                        "current_status": row.get("status"),
                        "file": "",
                        "source_url": "",
                        "retriever": "",
                        "retrieved_at": "",
                    }
                    for row in consolidated.get("results", [])
                    if row.get("status") not in {"pdf_downloaded", "skipped_existing"}
                ]
            },
        )
        blocked = [
            row
            for row in consolidated.get("results", [])
            if row.get("status") in {"retrieval_incomplete", "xml_full_text_downloaded"}
        ]
        if blocked:
            gate = self.paths.fulltext / "retrieval_manual_gate.json"
            write_json(
                gate,
                {
                    "created": now_iso(),
                    "records": blocked,
                    "reason": (
                        "Transport/provider failures are not negative retrieval evidence, "
                        "and XML-only payloads are not validated Docling screening inputs."
                    ),
                },
            )
            raise ManualGate(
                f"{len(blocked)} full-text candidates require retrieval retry or an authorized "
                f"PDF/HTML declaration in {self.paths.fulltext / 'manual_fulltexts.json'}. "
                f"See {gate}."
            )
        return [self.paths.download_manifest, template, self.paths.retrieval_dispositions]

    def build_docling_config(self, stage: str, records: Path, profile_root: Path, vlm: bool) -> Path:
        config_path = profile_root.parent / "run_config.json"
        missing = profile_root.parent / "missing_documents.json"
        command = [
            self.python(), "scripts/build_living_review_cohorts.py", "docling-config",
            "--records", str(records), "--download-manifest", str(self.paths.download_manifest),
            "--output", str(config_path), "--missing-output", str(missing),
            "--profile-root", str(profile_root), "--name", f"{self.run_id}_{stage}",
            "--max-workers", str(self.config["docling_workers"]),
            "--openai-base-url", self.config["openai_compatible_endpoint"].rstrip("/") + "/chat/completions",
            "--vlm-model", self.config["models"]["vlm"],
        ]
        if vlm:
            command.append("--vlm")
        self.run_command(stage, "build-config", command)
        return config_path

    @contextlib.contextmanager
    def codex_server(
        self, stage: str, model: str, timeout_seconds: int | None = None
    ) -> Iterator[None]:
        codex_model = model.removeprefix("openai/")
        endpoint = self.config["openai_compatible_endpoint"].rstrip("/") + "/models"
        try:
            with urllib.request.urlopen(endpoint, timeout=2) as response:
                advertised = {
                    str(row.get("id") or "")
                    for row in json.loads(response.read()).get("data", [])
                }
                if codex_model not in advertised:
                    raise RuntimeError(
                        f"Codex wrapper model mismatch: requested {codex_model}, advertised {sorted(advertised)}"
                    )
                yield
                return
        except RuntimeError:
            raise
        except Exception:
            pass
        if not self.args.manage_server:
            raise RuntimeError(
                f"OpenAI-compatible Codex wrapper is not available at {endpoint}; use --manage-server"
            )
        log_root = self.command_log_dir(stage) / "codex-server"
        log_root.mkdir(parents=True, exist_ok=True)
        stdout = (log_root / "stdout.log").open("w", encoding="utf-8")
        stderr = (log_root / "stderr.log").open("w", encoding="utf-8")
        process = subprocess.Popen(
            [
                self.python(), "scripts/docling/codex_openai_compat_server.py",
                "--port", str(self.config["openai_compatible_port"]),
                "--model", codex_model,
                "--timeout", str(timeout_seconds or self.config["codex_timeout_seconds"]),
                "--cwd", str(ROOT),
            ],
            cwd=ROOT,
            stdout=stdout,
            stderr=stderr,
            text=True,
        )
        try:
            for _ in range(60):
                if process.poll() is not None:
                    raise RuntimeError("Codex wrapper exited during startup")
                try:
                    with urllib.request.urlopen(endpoint, timeout=2):
                        break
                except Exception:
                    time.sleep(0.5)
            else:
                raise RuntimeError("Timed out waiting for Codex wrapper")
            yield
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            stdout.close()
            stderr.close()

    def stage_docling_screening(self) -> list[Path]:
        profile_root = self.paths.docling_screen / "profiles"
        self.preserve_expensive_generated_path("docling-screening", profile_root)
        config_path = self.build_docling_config("docling-screening", self.paths.fulltext_candidates, profile_root, False)
        documents = read_json(config_path).get("documents", [])
        retrieved = retrieved_candidate_subset(
            records_from(self.paths.fulltext_candidates), documents
        )
        write_json(
            self.paths.retrieved_fulltext_candidates,
            {
                "schema_version": 1,
                "created": now_iso(),
                "fulltext_candidate_count": record_count(self.paths.fulltext_candidates),
                "retrieved_supported_count": len(retrieved),
                "records": retrieved,
            },
        )
        if not documents:
            self.paths.no_vlm_manifest.parent.mkdir(parents=True, exist_ok=True)
            self.paths.no_vlm_manifest.write_text(
                "candidate_id,source_record_id,title,doi,profile_status,docling_json,markdown,source_document\n",
                encoding="utf-8",
            )
            return [
                self.paths.no_vlm_manifest,
                self.paths.docling_screen / "missing_documents.json",
                self.paths.retrieved_fulltext_candidates,
            ]
        self.run_command(
            "docling-screening", "convert",
            [self.docling_python(), "scripts/docling/run_docling_from_config.py", "--config", str(config_path)],
        )
        self.run_command(
            "docling-screening", "manifest",
            [self.python(), "scripts/docling/build_canonical_vlm_profile_manifest.py", "--profile-root", str(profile_root), "--expected-records", str(len(documents))],
        )
        return [
            self.paths.no_vlm_manifest,
            self.paths.docling_screen / "missing_documents.json",
            self.paths.retrieved_fulltext_candidates,
        ]

    def sharded_commands(
        self,
        base: list[str],
        output_root: Path,
        workers: int,
        name_prefix: str = "shard",
    ) -> list[tuple[str, list[str]]]:
        return [
            (
                f"{name_prefix}-{index:02d}",
                [*base, "--output-dir", str(output_root / f"shard_{index:02d}"), "--shard-index", str(index), "--shard-count", str(workers)],
            )
            for index in range(workers)
        ]

    def stage_graph_sections(self) -> list[Path]:
        self.preserve_expensive_generated_path("graph-sections", self.paths.graph_sections)
        for path in (
            self.paths.section_screening_input,
            self.paths.section_screening_input.with_suffix(".jsonl"),
            self.paths.section_input / "section_selection_provenance.json",
            self.paths.section_input / "fulltext_section_audit.csv",
            self.paths.section_input / "run_metadata.json",
            self.paths.section_input / "fulltext_screening_input_with_overrides.json",
            self.paths.section_input / "manual_section_override_audit.json",
        ):
            self.reset_generated_path(path)
        count = sum(1 for _ in csv.DictReader(self.paths.no_vlm_manifest.open(encoding="utf-8")))
        if count == 0:
            write_json(self.paths.section_screening_input, [])
            write_json(
                self.paths.section_input / "run_metadata.json",
                {
                    "created": now_iso(),
                    "records": 0,
                    "source_records_before_filter": 0,
                    "excluded_records": [],
                    "note": "No retrieved Docling profiles were available for section extraction.",
                },
            )
            return [self.paths.section_screening_input, self.paths.section_input / "run_metadata.json"]
        workers = min(count, int(self.config["graph_workers"]))
        base = [
            self.docling_python(), "scripts/docling/run_docling_graph_screening_evidence.py",
            "--canonical-manifest", str(self.paths.no_vlm_manifest), "--limit", "0",
            "--base-url", self.config["openai_compatible_endpoint"],
            "--model", self.config["models"]["graph"], "--timeout", str(self.config["codex_timeout_seconds"]),
            "--extraction-contract", "direct", "--provenance", "detailed",
        ]
        with self.codex_server("graph-sections", self.config["models"]["graph"]):
            self.run_parallel(
                "graph-sections",
                self.sharded_commands(base, self.paths.graph_sections, workers, "sections"),
            )
        self.run_command(
            "graph-sections", "build-screening-input",
            [
                self.python(), "scripts/docling/build_docling_graph_pipeline_input.py",
                "--graph-output", str(self.paths.graph_sections),
                "--base-records", str(self.paths.retrieved_fulltext_candidates),
                "--expected-profile-manifest", str(self.paths.no_vlm_manifest),
                "--output-dir", str(self.paths.section_input), "--require-both-targets",
                "--screening-fields-only",
            ],
        )
        return [
            self.paths.section_screening_input,
            self.paths.section_input / "section_selection_provenance.json",
            self.paths.section_input / "run_metadata.json",
        ]

    def stage_fulltext_screening(self) -> list[Path]:
        self.reset_generated_path(self.paths.fulltext_screening)
        metadata_path = self.paths.section_input / "run_metadata.json"
        section_metadata = read_json(metadata_path)
        excluded = section_metadata.get("excluded_records", [])
        if excluded:
            overrides = self.paths.section_input / "manual_section_overrides.json"
            if not overrides.exists():
                template = self.paths.section_input / "manual_section_overrides.template.json"
                write_json(
                    template,
                    {
                        "schema_version": 2,
                        "records": [
                            {
                                "record_id": row.get("record_id"),
                                "candidate_id": row.get("candidate_id"),
                                "source_markdown": "",
                                "source_markdown_sha256": "",
                                "sections": [
                                    {
                                        "target_section_types": ["data_source"],
                                        "heading_path": [],
                                    },
                                    {
                                        "target_section_types": ["input_representation"],
                                        "heading_path": [],
                                    },
                                ],
                                "rationale": "",
                                "resolver": "",
                                "resolved_at": "",
                            }
                            for row in excluded
                        ]
                    },
                )
                raise ManualGate(
                    f"{len(excluded)} retrieved reports lack a valid Graph-selected "
                    f"data-source/input-representation pair. Complete {overrides} from {template}."
                )
            merged = self.paths.section_input / "fulltext_screening_input_with_overrides.json"
            self.run_command(
                "fulltext-screening",
                "apply-section-overrides",
                [
                    self.python(), "scripts/build_living_review_cohorts.py", "apply-section-overrides",
                    "--input", str(self.paths.section_screening_input),
                    "--source-records", str(self.paths.retrieved_fulltext_candidates),
                    "--run-metadata", str(metadata_path), "--overrides", str(overrides),
                    "--profile-manifest", str(self.paths.no_vlm_manifest),
                    "--output", str(merged),
                    "--audit-output", str(self.paths.section_input / "manual_section_override_audit.json"),
                ],
            )
            screening_input = merged
        else:
            screening_input = self.paths.section_screening_input
        if record_count(screening_input) == 0:
            self.empty_screening(self.paths.fulltext_screening, "full_text_sections")
            return [self.paths.fulltext_screening / "final_screening_results.json", self.paths.fulltext_screening / "summary.json"]
        self.run_command(
            "fulltext-screening", "codex-pipeline",
            self.screening_command(screening_input, self.paths.fulltext_screening, "full_text_sections"),
        )
        outputs = [
            self.paths.fulltext_screening / "input_records.json",
            self.paths.fulltext_screening / "final_screening_results.json",
            self.paths.fulltext_screening / "summary.json",
        ]
        override_audit = self.paths.section_input / "manual_section_override_audit.json"
        if override_audit.exists():
            outputs.append(override_audit)
        return outputs

    def stage_eligibility_resolution(self) -> list[Path]:
        manual = self.paths.eligibility / "manual_resolution.csv"
        command = [
            self.python(), "scripts/build_living_review_cohorts.py", "accepted-records",
            "--screening-results", str(self.paths.fulltext_screening / "final_screening_results.json"),
            "--screening-input", str(self.paths.fulltext_screening / "input_records.json"),
            "--source-records", str(self.paths.retrieved_fulltext_candidates),
            "--profile-manifest", str(self.paths.no_vlm_manifest),
            "--output", str(self.paths.accepted_records),
            "--excluded-output", str(self.paths.eligibility / "excluded_records.json"),
            "--unresolved-output", str(self.paths.eligibility / "unresolved_records.json"),
        ]
        if manual.exists():
            command.extend(["--manual-resolution", str(manual)])
        try:
            self.run_command("eligibility-resolution", "resolve", command)
        except RuntimeError as exc:
            unresolved = self.paths.eligibility / "unresolved_records.json"
            if unresolved.exists() and record_count(unresolved):
                raise ManualGate(
                    f"Create {manual} with record_id,manual_decision,rationale,resolver,resolved_at"
                ) from exc
            raise
        return [self.paths.accepted_records, self.paths.eligibility / "excluded_records.json"]

    def stage_docling_vlm(self) -> list[Path]:
        self.preserve_expensive_generated_path(
            "docling-vlm", self.paths.docling_vlm / "profiles"
        )
        self.reset_generated_path(self.paths.docling_vlm / "no_new_eligible_records.json")
        accepted = record_count(self.paths.accepted_records)
        if not accepted:
            marker = self.paths.docling_vlm / "no_new_eligible_records.json"
            write_json(marker, {"created": now_iso(), "accepted_records": 0})
            return [marker]
        accepted_rows = records_from(self.paths.accepted_records)
        non_pdf = [
            {
                "record_id": row.get("record_id"),
                "candidate_id": row.get("candidate_id"),
                "title": row.get("title"),
                "source_document": row.get("source_document"),
                "source_document_kind": row.get("source_document_kind"),
            }
            for row in accepted_rows
            if str(row.get("source_document_kind") or "").casefold() != "pdf"
        ]
        if non_pdf:
            audit = self.paths.docling_vlm / "accepted_without_pdf.json"
            write_json(
                audit,
                {
                    "created": now_iso(),
                    "records": non_pdf,
                    "reason": (
                        "HTML is valid for section screening, but Docling uses its SimplePipeline "
                        "for HTML and does not provide the validated PDF picture-description "
                        "enrichment contract required by the living taxonomy corpus."
                    ),
                },
            )
            raise ManualGate(
                f"{len(non_pdf)} newly accepted reports have no PDF for the canonical VLM "
                f"profile. See {audit}; declare authorized PDFs in "
                f"{self.paths.fulltext / 'manual_fulltexts.json'} and rerun from fulltext-download."
            )
        profile_root = self.paths.docling_vlm / "profiles"
        config_path = self.build_docling_config("docling-vlm", self.paths.accepted_records, profile_root, True)
        with self.codex_server("docling-vlm", self.config["models"]["vlm"]):
            self.run_command(
                "docling-vlm", "convert",
                [self.docling_python(), "scripts/docling/run_docling_from_config.py", "--config", str(config_path)],
            )
        self.run_command(
            "docling-vlm", "manifest",
            [self.python(), "scripts/docling/build_canonical_vlm_profile_manifest.py", "--profile-root", str(profile_root), "--expected-records", str(accepted)],
        )
        return [self.paths.vlm_manifest]

    def taxonomy_base(
        self,
        script: str,
        manifest: Path,
        expected: int,
        timeout_seconds: int | None = None,
    ) -> list[str]:
        return [
            self.docling_python(), script, "--canonical-manifest", str(manifest),
            "--expected-records", str(expected), "--base-url", self.config["openai_compatible_endpoint"],
            "--model", self.config["models"]["graph"],
            "--timeout", str(timeout_seconds or self.config["codex_timeout_seconds"]),
        ]

    def stage_taxonomy_discovery(self) -> list[Path]:
        self.preserve_expensive_generated_path(
            "taxonomy-discovery", self.paths.taxonomy / "runs/discovery"
        )
        for path in (
            self.paths.taxonomy / "taxonomy_synthesis",
            self.paths.taxonomy / "study_model_registry.csv",
            self.paths.taxonomy / "registry_summary.json",
            self.paths.taxonomy / "no_new_eligible_records.json",
        ):
            self.reset_generated_path(path)
        expected = record_count(self.paths.accepted_records)
        if not expected:
            marker = self.paths.taxonomy / "no_new_eligible_records.json"
            write_json(marker, {"created": now_iso(), "records": 0})
            return [marker]
        discovery = self.paths.taxonomy / "runs/discovery"
        workers = min(expected, int(self.config["graph_workers"]))
        base = [
            *self.taxonomy_base("scripts/docling/run_docling_graph_input_taxonomy.py", self.paths.vlm_manifest, expected),
            "--stage", "discovery", "--replicate-id", "incremental_open_r1",
            "--extraction-contract", "direct", "--limit", "0",
        ]
        with self.codex_server("taxonomy-discovery", self.config["models"]["graph"]):
            self.run_parallel(
                "taxonomy-discovery",
                self.sharded_commands(base, discovery, workers, "discovery"),
            )
        synthesis = self.paths.taxonomy / "taxonomy_synthesis"
        self.run_command(
            "taxonomy-discovery", "inventory",
            [
                self.docling_python(), "scripts/docling/synthesize_input_representation_taxonomy.py",
                "--mode", "inventory", "--discovery-root", str(discovery),
                "--output-dir", str(synthesis), "--expected-records", str(expected),
            ],
        )
        prior_registry = self.resolve_artifact(self.current["taxonomy_root"]) / "study_model_registry.csv"
        self.run_command(
            "taxonomy-discovery", "registry",
            [
                self.python(), "scripts/docling/build_input_taxonomy_registry.py",
                "--canonical-manifest", str(self.paths.vlm_manifest), "--output-dir", str(self.paths.taxonomy),
                "--expected-records", str(expected), "--prior-registry", str(prior_registry),
            ],
        )
        return [synthesis / "open_route_inventory.json", self.paths.taxonomy / "study_model_registry.csv"]

    def run_semantic_sufficiency_gate(
        self,
        taxonomy_root: Path,
        output_dir: Path,
        command_prefix: str,
    ) -> list[dict[str, str]]:
        common = [
            "--taxonomy-root", str(taxonomy_root),
            "--profile-manifest", str(self.paths.vlm_manifest),
            "--source-root", str(ROOT),
            "--output-dir", str(output_dir),
            "--model", self.config["models"].get("semantic_review", "gpt-5.4-mini"),
            "--max-workers", str(self.config.get("semantic_review_workers", 6)),
            "--timeout", str(self.config.get("semantic_review_timeout_seconds", 3600)),
        ]
        script = "scripts/run_taxonomy_semantic_sufficiency_audit.py"
        self.run_command(
            "taxonomy-classification",
            f"{command_prefix}-prepare",
            [self.python(), script, "prepare", *common],
        )
        for role in ("semantic_reviewer", "adversarial_reviewer"):
            self.run_command(
                "taxonomy-classification",
                f"{command_prefix}-{role}",
                [self.python(), script, "review", "--role", role, *common],
            )
        for command in ("compare", "adjudicate", "finalize"):
            self.run_command(
                "taxonomy-classification",
                f"{command_prefix}-{command}",
                [self.python(), script, command, *common],
            )
        action_queue = output_dir / "semantic_sufficiency_action_queue.csv"
        with action_queue.open(newline="", encoding="utf-8") as stream:
            action_rows = list(csv.DictReader(stream))
        gate = {
            "created": now_iso(),
            "status": "pass" if not action_rows else "correction_required",
            "action_count": len(action_rows),
            "action_queue": rel(action_queue),
            "taxonomy_root": rel(taxonomy_root),
            "route_annotations_sha256": sha256(
                taxonomy_root / "route_annotations.jsonl"
            ),
            "rule": (
                "Every non-retain F6 disposition enters the versioned semantic "
                "correction and complete-document revalidation path."
            ),
        }
        write_json(output_dir / "semantic_sufficiency_gate.json", gate)
        return action_rows

    def authoritative_taxonomy_root(self) -> Path:
        marker = self.paths.taxonomy / "authoritative_taxonomy.json"
        if not marker.is_file():
            return self.paths.taxonomy
        payload = read_json(marker)
        root = self.resolve_artifact(payload["authoritative_taxonomy_root"])
        required = (
            "route_annotations.jsonl",
            "evidence_ledger.jsonl",
            "study_model_registry.csv",
            "taxonomy_tree.json",
            "agreement_metrics.json",
        )
        missing = [name for name in required if not (root / name).is_file()]
        if missing:
            raise RuntimeError(
                f"Authoritative taxonomy root is incomplete: {root}; missing={missing}"
            )
        if sha256(root / "route_annotations.jsonl") != payload["route_annotations_sha256"]:
            raise RuntimeError("Authoritative taxonomy route hash changed")
        return root

    def stage_taxonomy_classification(self) -> list[Path]:
        for path in (
            self.paths.taxonomy / "runs/classification_fixed_r1",
            self.paths.taxonomy / "runs/classification_fixed_r2",
            self.paths.taxonomy / "runs/classification_fixed_r3",
            self.paths.taxonomy / "runs/classification_dense",
            self.paths.taxonomy / "adjudication",
            self.paths.taxonomy / "semantic_sufficiency",
            self.paths.taxonomy / "semantic_correction_decisions",
            self.paths.taxonomy / "semantic_correction_applied",
            self.paths.taxonomy / "semantic_sufficiency_revalidation",
        ):
            self.preserve_expensive_generated_path("taxonomy-classification", path)
        for path in (
            self.paths.taxonomy / "tables",
            self.paths.taxonomy / "no_new_eligible_records.json",
            self.paths.taxonomy / "authoritative_taxonomy.json",
        ):
            self.reset_generated_path(path)
        for name in (
            "adjudication_resolution_manifest.csv",
            "route_annotations.jsonl",
            "route_annotations.csv",
            "route_candidates_all.jsonl",
            "evidence_ledger.jsonl",
            "uncertainty_cases.jsonl",
            "model_registry.csv",
            "analysis_run_metadata.json",
            "agreement_metrics.json",
            "agreement_report.md",
            "manuscript_methods.md",
            "manuscript_taxonomy_tables.md",
            "failure_mode_report.md",
            "special_cases.jsonl",
            "special_cases_report.md",
        ):
            self.reset_generated_path(self.paths.taxonomy / name)
        expected = record_count(self.paths.accepted_records)
        if not expected:
            marker = self.paths.taxonomy / "no_new_eligible_records.json"
            write_json(marker, {"created": now_iso(), "records": 0})
            return [marker]
        workers = min(expected, int(self.config["graph_workers"]))
        inventory = self.paths.taxonomy / "taxonomy_synthesis/open_route_inventory.json"
        taxonomy_tree = self.resolve_artifact(self.current["taxonomy_root"]) / "taxonomy_tree.json"
        direct_roots = []
        adjudication_timeout = int(
            self.config.get(
                "taxonomy_adjudication_timeout_seconds",
                self.config["codex_timeout_seconds"],
            )
        )
        with self.codex_server(
            "taxonomy-classification",
            self.config["models"]["graph"],
            timeout_seconds=adjudication_timeout,
        ):
            for replicate in ("r1", "r2", "r3"):
                output = self.paths.taxonomy / f"runs/classification_fixed_{replicate}"
                direct_roots.append(output)
                base = [
                    *self.taxonomy_base("scripts/docling/classify_fixed_input_taxonomy_candidates.py", self.paths.vlm_manifest, expected),
                    "--inventory", str(inventory), "--taxonomy", str(taxonomy_tree),
                    "--replicate-id", replicate, "--prompt-version", "v3-interface-boundary",
                ]
                self.run_parallel(
                    "taxonomy-classification",
                    self.sharded_commands(base, output, workers, f"fixed-{replicate}"),
                )
            dense_root = self.paths.taxonomy / "runs/classification_dense"
            dense_base = [
                *self.taxonomy_base("scripts/docling/run_docling_graph_input_taxonomy.py", self.paths.vlm_manifest, expected),
                "--stage", "coded", "--replicate-id", "coverage", "--extraction-contract", "dense",
                "--dense-fill-context", "scoped", "--dense-dedupe", "standard", "--limit", "0",
            ]
            self.run_parallel(
                "taxonomy-classification",
                self.sharded_commands(dense_base, dense_root, workers, "dense"),
            )
            adjudication = self.paths.taxonomy / "adjudication"
            adjudicate_base = [
                *self.taxonomy_base(
                    "scripts/docling/adjudicate_input_taxonomy.py",
                    self.paths.vlm_manifest,
                    expected,
                    timeout_seconds=adjudication_timeout,
                ),
                "--dense-run", str(dense_root), "--taxonomy", str(taxonomy_tree),
                "--inventory", str(inventory),
            ]
            for root in direct_roots:
                adjudicate_base.extend(["--direct-run", str(root)])
            self.run_parallel(
                "taxonomy-classification",
                self.sharded_commands(
                    adjudicate_base, adjudication, workers, "adjudication"
                ),
            )
        analyze = [
            self.python(), "scripts/docling/analyze_input_taxonomy_runs.py",
            "--dense-run", str(dense_root), "--adjudication", str(adjudication),
            "--registry", str(self.paths.taxonomy / "study_model_registry.csv"),
            "--output-dir", str(self.paths.taxonomy), "--expected-records", str(expected),
            "--cohort-label", self.run_id,
            "--protocol-mode", "incremental_frozen_taxonomy",
            "--taxonomy-version", "v1",
        ]
        for root in direct_roots:
            analyze.extend(["--direct-run", str(root)])
        self.run_command("taxonomy-classification", "analyze", analyze)

        frozen_taxonomy_root = self.resolve_artifact(self.current["taxonomy_root"])
        for name in ("taxonomy_tree.json", "taxonomy_codebook.md"):
            source = frozen_taxonomy_root / name
            if not source.is_file():
                raise RuntimeError(f"Frozen taxonomy artifact is missing: {source}")
            shutil.copy2(source, self.paths.taxonomy / name)

        f6 = self.paths.taxonomy / "semantic_sufficiency"
        action_rows = self.run_semantic_sufficiency_gate(
            self.paths.taxonomy, f6, "f6"
        )
        authoritative_root = self.paths.taxonomy
        authoritative_f6 = f6
        if action_rows:
            correction = self.paths.taxonomy / "semantic_correction_decisions"
            corrected = self.paths.taxonomy / "semantic_correction_applied"
            revalidation = self.paths.taxonomy / "semantic_sufficiency_revalidation"
            self.run_command(
                "taxonomy-classification",
                "f6-correct",
                [
                    self.python(),
                    "scripts/run_taxonomy_semantic_correction.py",
                    "--taxonomy-root", str(self.paths.taxonomy),
                    "--f6-root", str(f6),
                    "--output-dir", str(correction),
                    "--model", self.config["models"].get(
                        "semantic_review", "gpt-5.4-mini"
                    ),
                    "--timeout", str(
                        self.config.get("semantic_correction_timeout_seconds", 3600)
                    ),
                    "--retries", str(
                        self.config.get("semantic_correction_retries", 1)
                    ),
                    "--max-workers", str(
                        self.config.get("semantic_correction_workers", 4)
                    ),
                    "--max-routes-per-call", str(
                        self.config.get("semantic_correction_max_routes_per_call", 4)
                    ),
                ],
            )
            self.run_command(
                "taxonomy-classification",
                "f6-apply-correction",
                [
                    self.python(),
                    "scripts/apply_taxonomy_semantic_correction.py",
                    "--source-taxonomy-root", str(self.paths.taxonomy),
                    "--correction-root", str(correction),
                    "--output-dir", str(corrected),
                    "--profile-manifest", str(self.paths.vlm_manifest),
                    "--profile-source-root", str(ROOT),
                    "--correction-id", f"{self.run_id}:F6_semantic_correction_v1",
                ],
            )
            remaining = self.run_semantic_sufficiency_gate(
                corrected, revalidation, "f6-revalidate"
            )
            if remaining:
                raise ManualGate(
                    "F6 semantic correction failed complete-document revalidation; "
                    "preserve this run and use `taxonomy-rerun-preflight` for a declared "
                    "whole-cohort bridge instead of patching routine outputs"
                )
            authoritative_root = corrected
            authoritative_f6 = revalidation
        marker = self.paths.taxonomy / "authoritative_taxonomy.json"
        write_json(
            marker,
            {
                "schema_version": 1,
                "created": now_iso(),
                "run_id": self.run_id,
                "mode": (
                    "versioned_f6_semantic_correction"
                    if action_rows
                    else "original_classification_f6_pass"
                ),
                "original_taxonomy_root": rel(self.paths.taxonomy),
                "authoritative_taxonomy_root": rel(authoritative_root),
                "initial_f6_action_count": len(action_rows),
                "final_f6_root": rel(authoritative_f6),
                "route_annotations_sha256": sha256(
                    authoritative_root / "route_annotations.jsonl"
                ),
                "evidence_ledger_sha256": sha256(
                    authoritative_root / "evidence_ledger.jsonl"
                ),
            },
        )
        return [
            authoritative_root / "route_annotations.jsonl",
            authoritative_root / "agreement_metrics.json",
            authoritative_f6 / "semantic_sufficiency_report.json",
            authoritative_f6 / "semantic_sufficiency_gate.json",
            marker,
        ]

    def stage_crop_validation(self) -> list[Path]:
        self.preserve_expensive_generated_path("crop-validation", self.paths.crops)
        expected = record_count(self.paths.accepted_records)
        if not expected:
            ledger = self.paths.crops / "crop_ledger.json"
            write_json(ledger, [])
            return [ledger]
        self.run_command(
            "crop-validation", "two-selectors-adjudicator-cropper",
            [
                self.python(), "scripts/run_incremental_atlas_crop_pipeline.py",
                "--taxonomy-root", str(self.authoritative_taxonomy_root()),
                "--corpus-root", str(self.paths.docling_vlm / "profiles"),
                "--output-dir", str(self.paths.crops), "--model", self.config["models"]["crop"],
                "--max-workers", str(self.config["crop_workers"]),
                "--timeout", str(self.config["codex_timeout_seconds"]),
                "--exclude-model-ledger", str(self.resolve_artifact(self.current["crop_ledger"])),
            ],
        )
        crop_ledger = self.paths.crops / "crop_ledger.json"
        initial_ledger = self.paths.crops / "initial_crop_ledger.json"
        shutil.copy2(crop_ledger, initial_ledger)

        f7 = self.paths.crops / "exact_preview_validation"
        f7_script = "scripts/run_atlas_exact_preview_validation.py"
        validation_model = self.config["models"].get(
            "preview_validation", self.config["models"]["crop"]
        )
        f7_common = [
            "--taxonomy-root", str(self.authoritative_taxonomy_root()),
            "--crop-ledger", str(initial_ledger),
            "--source-root", str(ROOT),
            "--output-dir", str(f7),
            "--model", validation_model,
            "--max-workers", str(self.config.get("preview_validation_workers", 8)),
            "--timeout", str(self.config.get("preview_validation_timeout_seconds", 2700)),
        ]
        self.run_command(
            "crop-validation", "f7-prepare",
            [self.python(), f7_script, "prepare", *f7_common],
        )
        for role in ("exact_preview_validator", "input_role_validator"):
            self.run_command(
                "crop-validation", f"f7-{role}",
                [self.python(), f7_script, "review", "--role", role, *f7_common],
            )
        for command in ("compare", "adjudicate", "adjusted"):
            self.run_command(
                "crop-validation", f"f7-{command}",
                [self.python(), f7_script, command, *f7_common],
            )

        replacement_script = "scripts/run_atlas_replacement_validation.py"
        replacement_common = [
            "--output-dir", str(f7),
            "--profile-manifest", str(self.paths.vlm_manifest),
            "--source-root", str(ROOT),
            "--model", validation_model,
            "--timeout", str(self.config.get("preview_validation_timeout_seconds", 2700)),
        ]
        for command in ("prepare", "run"):
            self.run_command(
                "crop-validation", f"f7-replacement-{command}",
                [self.python(), replacement_script, command, *replacement_common],
            )
        self.run_command(
            "crop-validation", "f7-replacement-preview",
            [
                self.python(), f7_script, "review", "--role",
                "replacement_preview_validator", *f7_common,
            ],
        )
        self.run_command(
            "crop-validation", "f7-replacement-round2",
            [self.python(), replacement_script, "round2", *replacement_common],
        )
        for role in (
            "replacement_preview_validator_round2",
            "replacement_input_role_validator",
        ):
            self.run_command(
                "crop-validation", f"f7-{role}",
                [self.python(), f7_script, "review", "--role", role, *f7_common],
            )
        self.run_command(
            "crop-validation", "f7-replacement-finalize",
            [self.python(), replacement_script, "finalize", *replacement_common],
        )
        self.run_command(
            "crop-validation", "f7-finalize",
            [self.python(), f7_script, "finalize", *f7_common],
        )

        report_path = f7 / "exact_preview_validation_report.json"
        report = read_json(report_path)
        if report.get("unresolved_models"):
            raise ManualGate(
                f"F7 has {report['unresolved_models']} unresolved model previews; "
                f"inspect {rel(report_path)} before snapshot creation"
            )
        proposed = f7 / "proposed_crossvalidated_crop_ledger.json"
        shutil.copy2(proposed, crop_ledger)
        return [
            crop_ledger,
            self.paths.crops / "run_summary.json",
            initial_ledger,
            report_path,
            f7 / "tool_isolation_audit.json",
        ]

    def stage_snapshot(self) -> list[Path]:
        self.reset_generated_path(self.paths.snapshot / "no_catalog_change.json")
        if record_count(self.paths.accepted_records) == 0:
            marker = self.paths.snapshot / "no_catalog_change.json"
            write_json(marker, {"created": now_iso(), "prior_taxonomy_root": self.current["taxonomy_root"]})
            return [marker]
        working = self.paths.snapshot.with_name(self.paths.snapshot.name + ".building")
        if working.exists():
            shutil.rmtree(working)
        command = [
            self.python(), "scripts/merge_living_catalog_snapshot.py",
            "--prior-taxonomy-root", str(self.resolve_artifact(self.current["taxonomy_root"])),
            "--update-taxonomy-root", str(self.authoritative_taxonomy_root()),
            "--prior-crop-ledger", str(self.resolve_artifact(self.current["crop_ledger"])),
            "--update-crop-ledger", str(self.paths.crops / "crop_ledger.json"),
            "--output-dir", str(working), "--run-id", self.run_id,
            "--update-corpus-root", str(self.paths.docling_vlm / "profiles"),
            *self.artifact_root_arguments(),
        ]
        for root in [*self.current["docling_corpus_roots"], rel(self.paths.docling_vlm / "profiles")]:
            command.extend(["--corpus-root", str(self.resolve_artifact(root))])
        self.run_command("snapshot", "merge", command)
        if self.paths.snapshot.exists():
            shutil.rmtree(self.paths.snapshot)
        working.replace(self.paths.snapshot)
        return [self.paths.snapshot / "snapshot_manifest.json", self.paths.snapshot / "crop_ledger.json"]

    def stage_atlas(self) -> list[Path]:
        self.reset_generated_path(self.paths.atlas / "no_catalog_change.json")
        if record_count(self.paths.accepted_records) == 0:
            marker = self.paths.atlas / "no_catalog_change.json"
            write_json(marker, {"created": now_iso()})
            return [marker]
        if self.paths.atlas.exists():
            shutil.rmtree(self.paths.atlas)
        shutil.copytree(resolve(self.current["atlas_output"]), self.paths.atlas)
        command = [
            self.python(), "scripts/build_input_representation_atlas.py",
            "--taxonomy-root", str(self.paths.snapshot), "--crop-ledger", str(self.paths.snapshot / "crop_ledger.json"),
            "--output-dir", str(self.paths.atlas),
            "--prior-atlas-root", str(resolve(self.current["atlas_output"])),
            *self.artifact_root_arguments(),
        ]
        for root in [*self.current["docling_corpus_roots"], rel(self.paths.docling_vlm / "profiles")]:
            command.extend(["--corpus-root", str(self.resolve_artifact(root))])
        self.run_command("atlas", "build", command)
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        server_root = self.log_dir("atlas") / "static-server"
        server_root.mkdir(parents=True, exist_ok=True)
        stdout = (server_root / "stdout.log").open("w", encoding="utf-8")
        stderr = (server_root / "stderr.log").open("w", encoding="utf-8")
        server = subprocess.Popen(
            [self.python(), "-m", "http.server", str(port), "--bind", "127.0.0.1"],
            cwd=self.paths.atlas,
            stdout=stdout,
            stderr=stderr,
            text=True,
        )
        try:
            url = f"http://127.0.0.1:{port}/"
            for _ in range(40):
                try:
                    with urllib.request.urlopen(url, timeout=1):
                        break
                except Exception:
                    time.sleep(0.25)
            self.run_command(
                "atlas", "browser-qa",
                [
                    "node", "scripts/qa_input_representation_atlas.mjs", url,
                    str(self.paths.atlas / "data/browser_qa.json"),
                ],
                extra_env={"NODE_PATH": playwright_node_path() or ""},
            )
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
            stdout.close()
            stderr.close()
        return [
            self.paths.atlas / "data/atlas.json",
            self.paths.atlas / "data/build_report.json",
            self.paths.atlas / "data/browser_qa.json",
        ]

    def stage_report(self) -> list[Path]:
        self.reset_generated_path(self.paths.report)
        self.paths.report.mkdir(parents=True, exist_ok=True)
        search_summary = read_json(self.paths.search_exports / f"search_summary_{self.date_to}.json")
        dedup = read_json(self.paths.dedup / "deduplication_stats.json")
        cross = read_json(self.paths.records / "cross_dedup_stats.json")
        crossref = read_json(self.paths.records / "crossref_checked_stats.json")
        abstract_summary = read_json(self.paths.abstract_screening / "summary.json")
        downloads = read_json(self.paths.download_manifest)
        section_meta = read_json(self.paths.section_input / "run_metadata.json")
        fulltext_summary = read_json(self.paths.fulltext_screening / "summary.json")
        fulltext_candidate_artifact = read_json(self.paths.fulltext_candidates)
        fulltext_candidates = records_from(self.paths.fulltext_candidates)
        fulltext_candidate_meta = fulltext_candidate_artifact.get("metadata") or {}
        missing_document_rows = records_from(self.paths.docling_screen / "missing_documents.json")
        date_precision = date_precision_rollup(search_summary)
        retrieval = retrieval_disposition_table(
            fulltext_candidates, downloads, missing_document_rows
        )
        retrieval_rows_path = self.paths.report / "fulltext_retrieval_dispositions.json"
        write_json(
            retrieval_rows_path,
            {
                "run_id": self.run_id,
                "created": now_iso(),
                "candidate_count": retrieval["candidate_count"],
                "disposition_counts": retrieval["disposition_counts"],
                "rows": retrieval["rows"],
            },
        )
        retrieval_csv_path = self.paths.report / "fulltext_retrieval_dispositions.csv"
        with retrieval_csv_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=[
                    "candidate_id",
                    "download_status",
                    "disposition",
                    "terminal_retrieval_evidence",
                    "manual_gate_required",
                    "attempt_count",
                    "technical_failure_count",
                    "access_restriction_count",
                    "attempt_ledger",
                ],
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(retrieval["rows"])
        unusable_abstracts = record_count(self.paths.abstracts / "excluded_no_usable_abstract.json")
        override_audit = self.paths.section_input / "manual_section_override_audit.json"
        manual_section_overrides = (
            read_json(override_audit).get("manual_section_overrides", 0)
            if override_audit.exists()
            else 0
        )
        accepted = record_count(self.paths.accepted_records)
        taxonomy_counts = {}
        metrics_path = self.authoritative_taxonomy_root() / "agreement_metrics.json"
        if metrics_path.exists():
            taxonomy_counts = read_json(metrics_path).get("final_counts", {})
        if accepted:
            prior = read_json(self.paths.snapshot / "snapshot_manifest.json")
        else:
            prior_root = resolve(self.current["taxonomy_root"])
            prior_snapshot = prior_root / "snapshot_manifest.json"
            prior_metrics = prior_root / "agreement_metrics.json"
            prior_build = resolve(self.current["atlas_output"]) / "data/build_report.json"
            if prior_snapshot.exists():
                prior = read_json(prior_snapshot)
            elif prior_metrics.exists():
                final = read_json(prior_metrics).get("final_counts", {})
                prior = {
                    "records": final.get("screening_records"),
                    "studies": final.get("primary_studies"),
                    "models": final.get("models"),
                    "configurations": final.get("configurations"),
                    "routes": final.get("accepted_input_routes"),
                }
            else:
                prior = read_json(prior_build) if prior_build.exists() else {}
        catalog_after_update = {
            "records": prior.get("records"),
            "studies": prior.get("studies"),
            "models": prior.get("models"),
            "configurations": prior.get("configurations"),
            "routes": prior.get("routes"),
        }
        facts = {
            "schema_version": 2,
            "run_id": self.run_id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "databases": self.enabled_databases(),
            "raw_hits": search_summary.get("total_before_dedup", 0),
            "date_precision": date_precision,
            "late_indexing_lookback": {
                "automated": False,
                "policy": (
                    "No retrospective lookback is automated; the update includes records "
                    "returned by providers for the declared interval at search execution time."
                ),
            },
            "within_update_unique": dedup.get("total_after_dedup", 0),
            "within_update_duplicates_removed": dedup.get("duplicates_removed", 0),
            "already_in_cumulative_master": cross.get("already_in_master", 0),
            "crossref_hidden_duplicates": crossref.get("hidden_duplicates_removed_by_crossref", 0),
            "new_records": crossref.get("truly_new_after_crossref_audit", 0),
            "abstracts_screened": abstract_summary.get("total_records", 0),
            "records_without_usable_abstract": unusable_abstracts,
            "abstract_decisions": abstract_summary.get("decision_counts", {}),
            "raw_fulltext_candidates": fulltext_candidate_meta.get(
                "raw_screening_candidates", retrieval["candidate_count"]
            ),
            "postscreen_duplicates_removed": fulltext_candidate_meta.get(
                "postscreen_duplicates_removed", 0
            ),
            "fulltext_candidates": retrieval["candidate_count"],
            "retrieval_disposition": {
                "counts": retrieval["disposition_counts"],
                "artifact": rel(retrieval_rows_path),
            },
            "fulltext_pdf_downloaded": retrieval["disposition_counts"].get("pdf_retrieved", 0),
            "fulltext_non_pdf_downloaded": retrieval["disposition_counts"].get("html_full_text_retrieved", 0),
            "reports_not_retrieved_access_restricted": retrieval["disposition_counts"].get(
                "not_retrieved_access_restricted", 0
            ),
            "reports_not_retrieved": (
                retrieval["disposition_counts"].get("not_retrieved", 0)
                + retrieval["disposition_counts"].get("not_retrieved_access_restricted", 0)
            ),
            "preexisting_fulltext_retrieval_reused": retrieval["disposition_counts"].get(
                "preexisting_retrieval_reused", 0
            ),
            "docling_input_availability_overlap": {
                "missing_count": retrieval["docling_missing_count"],
                "by_retrieval_disposition": retrieval["docling_missing_by_retrieval_disposition"],
                "definition": "Technical overlap audit; not a mutually exclusive PRISMA retrieval branch.",
            },
            "docling_profiles": sum(1 for _ in csv.DictReader(self.paths.no_vlm_manifest.open(encoding="utf-8"))),
            "section_screening_input": section_meta.get("records", 0) + manual_section_overrides,
            "automatic_section_selection_failures": len(section_meta.get("excluded_records", [])),
            "manual_section_overrides": manual_section_overrides,
            "unresolved_section_failures": max(
                0,
                len(section_meta.get("excluded_records", [])) - manual_section_overrides,
            ),
            "fulltext_decisions": fulltext_summary.get("decision_counts", {}),
            "accepted_records": accepted,
            "taxonomy": taxonomy_counts,
            "catalog_after_update": catalog_after_update,
        }
        write_json(self.paths.report / "prisma_update_facts.json", facts)
        lines = [
            f"# Living Review Update {self.run_id}", "",
            f"- Search interval: {self.date_from} to {self.date_to}",
            "- Late-indexing lookback: not automated; records indexed after this closed interval may require a later supplemental recall declaration.",
            f"- Databases: {', '.join(facts['databases'])}",
            f"- Raw hits: {facts['raw_hits']}",
            f"- Confirmed source-date-filtered hits: {facts['date_precision']['confirmed_by_source_date_filter']}",
            f"- Uncertain-date recall candidates retained: {facts['date_precision']['uncertain_date_recall_candidates']}",
            f"- Unique within update: {facts['within_update_unique']}",
            f"- Already present in cumulative master: {facts['already_in_cumulative_master']}",
            f"- New records after Crossref audit: {facts['new_records']}",
            f"- Title/abstract screened: {facts['abstracts_screened']} {facts['abstract_decisions']}",
            f"- Records without a usable abstract: {facts['records_without_usable_abstract']}",
            f"- Raw full-text candidates: {facts['raw_fulltext_candidates']}",
            f"- Post-screen duplicates removed: {facts['postscreen_duplicates_removed']}",
            f"- Full-text candidates: {facts['fulltext_candidates']}",
            f"- Retrieved PDF/HTML full text: {facts['fulltext_pdf_downloaded']}/{facts['fulltext_non_pdf_downloaded']}",
            f"- Pre-existing full texts reused: {facts['preexisting_fulltext_retrieval_reused']}",
            f"- Reports not retrieved: {facts['reports_not_retrieved']}",
            "- Reports not retrieved because access was restricted: "
            f"{facts['reports_not_retrieved_access_restricted']}",
            "- Docling input availability overlap (not a PRISMA branch): "
            f"{facts['docling_input_availability_overlap']['missing_count']} "
            f"{facts['docling_input_availability_overlap']['by_retrieval_disposition']}",
            f"- Valid dual-section screening inputs: {facts['section_screening_input']}",
            f"- Manual section overrides: {facts['manual_section_overrides']}",
            f"- Full-text decisions: {facts['fulltext_decisions']}",
            f"- Newly accepted records: {facts['accepted_records']}",
            f"- Incremental taxonomy counts: {facts['taxonomy']}",
            f"- Cumulative catalog after update: {facts['catalog_after_update']}", "",
            "All prompts, schemas, responses, retries, command logs, and stage hashes are retained",
            f"under `{rel(self.run_root)}`. The update uses the frozen taxonomy and does not rewrite",
            "the historical 52-record baseline.",
        ]
        report = self.paths.report / "update_report.md"
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return [
            self.paths.report / "prisma_update_facts.json",
            retrieval_rows_path,
            retrieval_csv_path,
            report,
        ]

    def callbacks(self) -> dict[str, Callable[[], list[Path]]]:
        return {
            "search": self.stage_search,
            "deduplicate": self.stage_deduplicate,
            "prepare-records": self.stage_prepare_records,
            "enrich-abstracts": self.stage_enrich_abstracts,
            "abstract-screening": self.stage_abstract_screening,
            "fulltext-candidates": self.stage_fulltext_candidates,
            "fulltext-download": self.stage_fulltext_download,
            "docling-screening": self.stage_docling_screening,
            "graph-sections": self.stage_graph_sections,
            "fulltext-screening": self.stage_fulltext_screening,
            "eligibility-resolution": self.stage_eligibility_resolution,
            "docling-vlm": self.stage_docling_vlm,
            "taxonomy-discovery": self.stage_taxonomy_discovery,
            "taxonomy-classification": self.stage_taxonomy_classification,
            "crop-validation": self.stage_crop_validation,
            "snapshot": self.stage_snapshot,
            "atlas": self.stage_atlas,
            "report": self.stage_report,
        }

    def run(self) -> int:
        self.assert_method_lock()
        start = STAGES.index(self.args.from_stage) if self.args.from_stage else 0
        end = STAGES.index(self.args.through_stage) if self.args.through_stage else len(STAGES) - 1
        if start > end:
            raise ValueError("--from-stage occurs after --through-stage")
        self.save_manifest()
        if self.args.force:
            self.invalidate_from(
                STAGES[start],
                include_stage=True,
                reason="Explicit --force rerun invalidates this stage and all downstream stages.",
            )
        for stage in STAGES[start : end + 1]:
            if not self.stage_is_complete(stage):
                self.invalidate_from(
                    stage,
                    include_stage=False,
                    reason="Upstream stage is being recomputed or its declared artifact hash changed.",
                )
            self.execute_stage(stage, self.callbacks()[stage])
        return 0

    def publish(self) -> int:
        if self.manifest.get("published"):
            print(json.dumps(self.manifest.get("published_state", {}), ensure_ascii=False, indent=2))
            return 0
        incomplete = [
            stage
            for stage in STAGES[: STAGES.index("report") + 1]
            if not self.stage_is_complete(stage)
        ]
        if incomplete:
            raise RuntimeError(
                "Publication requires a hash-valid completed stage closure through report; "
                f"incomplete_or_mutated={', '.join(incomplete)}"
            )
        if self.manifest.get("method_lock"):
            archive_status = self.artifact_archive_status(require_independent=True)
            if not archive_status["ok"]:
                raise RuntimeError(
                    "Publication requires an independently stored and fully verified artifact "
                    "archive: " + "; ".join(archive_status["issues"])
                )
        live_state = self.load_current_state()
        prior_state = self.manifest["prior_state"]
        for field in (
            "search_end",
            "master_record_files",
            "taxonomy_root",
            "docling_corpus_roots",
            "crop_ledger",
            "atlas_output",
        ):
            if live_state.get(field) != prior_state.get(field):
                raise RuntimeError(
                    f"Living state changed after this run started ({field}); "
                    "rebase the update on the newly published state instead of publishing stale results"
                )
        accepted = record_count(self.paths.accepted_records)
        taxonomy_root = rel(self.paths.snapshot) if accepted else self.current["taxonomy_root"]
        crop_ledger = rel(self.paths.snapshot / "crop_ledger.json") if accepted else self.current["crop_ledger"]
        corpus_roots = list(self.current["docling_corpus_roots"])
        atlas_target: Path | None = None
        backup: Path | None = None
        temporary: Path | None = None
        target_existed = False
        if accepted:
            corpus_roots.append(rel(self.paths.docling_vlm / "profiles"))
            atlas_target = resolve(self.config["atlas_output"])
            temporary = atlas_target.with_name(atlas_target.name + ".next")
            if temporary.exists():
                shutil.rmtree(temporary)
            shutil.copytree(self.paths.atlas, temporary)
            backup = atlas_target.with_name(atlas_target.name + ".previous")
            target_existed = atlas_target.exists()
        master_files = [
            *self.current["master_record_files"],
            rel(self.paths.records / "new_records_after_cross_dedup_crossref_checked.json"),
        ]
        prisma_report = rel(self.paths.report / "prisma_update_facts.json")
        prisma_history = list(live_state.get("prisma_update_history", []))
        if not any(
            isinstance(entry, dict) and entry.get("run_id") == self.run_id
            for entry in prisma_history
        ):
            prisma_history.append(
                {
                    "run_id": self.run_id,
                    "date_from": self.date_from,
                    "date_to": self.date_to,
                    "facts": prisma_report,
                }
            )
        state = {
            "schema_version": 1,
            "updated": now_iso(),
            "search_end": self.date_to,
            "master_record_files": master_files,
            "taxonomy_root": taxonomy_root,
            "docling_corpus_roots": corpus_roots,
            "crop_ledger": crop_ledger,
            "atlas_output": self.config["atlas_output"],
            "last_run_id": self.run_id,
            "last_run_manifest": rel(self.manifest_path),
            "last_prisma_update": prisma_report,
            "prisma_update_history": prisma_history,
        }
        state_path = resolve(self.config["living_state"])
        state_existed = state_path.exists()
        write_json(
            self.publish_journal_path,
            {
                "schema_version": 1,
                "run_id": self.run_id,
                "created": now_iso(),
                "phase": "prepared",
                "state_path": str(state_path),
                "state_existed": state_existed,
                "prior_state": live_state,
                "atlas": {
                    "target": str(atlas_target) if atlas_target else "",
                    "backup": str(backup) if backup else "",
                    "temporary": str(temporary) if temporary else "",
                    "target_existed": target_existed,
                },
            },
        )
        try:
            if accepted and atlas_target is not None and backup is not None and temporary is not None:
                if backup.exists():
                    shutil.rmtree(backup)
                if target_existed:
                    atlas_target.replace(backup)
                    journal = read_json(self.publish_journal_path)
                    journal["phase"] = "atlas_backed_up"
                    write_json(self.publish_journal_path, journal)
                temporary.replace(atlas_target)
                journal = read_json(self.publish_journal_path)
                journal["phase"] = "atlas_promoted"
                write_json(self.publish_journal_path, journal)
            write_json(state_path, state)
            journal = read_json(self.publish_journal_path)
            journal["phase"] = "state_written"
            write_json(self.publish_journal_path, journal)
            self.manifest["published"] = True
            self.manifest["published_at"] = now_iso()
            self.manifest["published_state"] = state
            self.save_manifest()
            self.publish_journal_path.unlink()
        except Exception:
            if state_existed:
                write_json(state_path, live_state)
            else:
                state_path.unlink(missing_ok=True)
            if accepted and atlas_target is not None and backup is not None and backup.exists():
                if atlas_target.exists():
                    shutil.rmtree(atlas_target)
                backup.replace(atlas_target)
            elif accepted and atlas_target is not None and not target_existed and atlas_target.exists():
                shutil.rmtree(atlas_target)
            if temporary is not None and temporary.exists():
                shutil.rmtree(temporary)
            self.manifest["published"] = False
            self.manifest.pop("published_at", None)
            self.manifest.pop("published_state", None)
            self.publish_journal_path.unlink(missing_ok=True)
            raise
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0

    def doctor(self) -> int:
        """Report control-plane drift and the exact next safe operation."""
        repository_checkout_requested = bool(getattr(self.args, "repository_checkout", False))
        state_path = resolve(self.config["living_state"])
        atlas_root = resolve(self.config["atlas_output"])
        atlas_data = atlas_root / "data/atlas.json"
        atlas_meta: dict[str, Any] = {}
        if atlas_data.is_file():
            payload = read_json(atlas_data)
            atlas_meta = payload.get("meta", {}) if isinstance(payload, dict) else {}

        manifests = list(resolve(self.config["updates_root"]).glob("update_*/run_manifest.json"))
        published_manifest = self.current.get("last_run_manifest") if state_path.is_file() else None
        if published_manifest and resolve(published_manifest).is_file():
            latest = read_json(resolve(published_manifest))
        else:
            payloads = [read_json(path) for path in manifests]
            latest = max(
                payloads,
                key=lambda row: (str(row.get("date_to") or ""), str(row.get("updated") or "")),
                default=None,
            )
        selected = self.manifest if self.manifest_path.is_file() else latest
        stage_rows: list[dict[str, Any]] = []
        first_blocking_stage: str | None = None
        repository_ledger_error: str | None = None
        repository_omission_count = 0
        if selected:
            selected_run_id = str(selected.get("run_id") or "")
            selected_path = resolve(self.config["updates_root"]) / selected_run_id / "run_manifest.json"
            selected_pipeline = self
            if selected_path != self.manifest_path and selected_path.is_file():
                probe_args = argparse.Namespace(**vars(self.args))
                probe_args.run_id = selected_run_id
                probe_args.date_from = None
                probe_args.date_to = None
                selected_pipeline = Pipeline(probe_args, self.config)
            repository_checkout = repository_checkout_requested
            if repository_checkout:
                try:
                    selected_pipeline.repository_external_artifacts()
                except RuntimeError as exc:
                    repository_ledger_error = str(exc)
                    repository_checkout = False
            acknowledged_mutations: set[str] = set()
            reconciliation_ref = selected.get("publication_reconciliation")
            if reconciliation_ref and resolve(reconciliation_ref).is_file():
                reconciliation = read_json(resolve(reconciliation_ref))
                acknowledged_mutations = set(
                    reconciliation.get("acknowledged_post_run_mutations", {})
                )
            for stage in STAGES:
                row = selected.get("stages", {}).get(stage, {})
                declared = row.get("status", "not_started")
                repository_omissions: list[str] = []
                validation_issues = (
                    selected_pipeline.stage_validation_issues(
                        stage,
                        repository_checkout=repository_checkout,
                        repository_omissions=repository_omissions,
                    )
                    if row
                    else []
                )
                valid = not validation_issues if row else False
                effective = declared if declared not in {"complete", "skipped_no_new_records"} or valid else "invalidated"
                if effective == "invalidated" and stage in acknowledged_mutations:
                    effective = "acknowledged_post_run_mutation"
                repository_omission_count += len(set(repository_omissions))
                stage_rows.append(
                    {
                        "stage": stage,
                        "declared_status": declared,
                        "status": effective,
                        "note": row.get("note", ""),
                        "validation_issues": validation_issues,
                        "repository_external_omissions": len(set(repository_omissions)),
                    }
                )
                if first_blocking_stage is None and effective not in {
                    "complete",
                    "skipped_no_new_records",
                    "acknowledged_post_run_mutation",
                }:
                    first_blocking_stage = stage

        issues: list[dict[str, str]] = []
        actions: list[str] = []
        method_lock = self.method_lock_status(selected) if selected else self.method_lock_status()
        if self.config.get("method_lock") and not method_lock["ok"]:
            severity = "critical" if selected and selected.get("method_lock") else "warning"
            issues.append(
                {
                    "severity": severity,
                    "code": "METHOD_LOCK_FAILED" if severity == "critical" else "LEGACY_RUN_NOT_METHOD_LOCKED",
                    "detail": "; ".join(method_lock["issues"]),
                }
            )
        if repository_ledger_error:
            issues.append(
                {
                    "severity": "critical",
                    "code": "INVALID_REPOSITORY_ARTIFACT_LEDGER",
                    "detail": repository_ledger_error,
                }
            )
        if not state_path.is_file():
            issues.append(
                {
                    "severity": "critical",
                    "code": "MISSING_LIVING_STATE",
                    "detail": f"{rel(state_path)} is absent; planning falls back to {self.config['baseline_search_end']}.",
                }
            )
        declared_complete = bool(stage_rows) and all(
            row["declared_status"] in {"complete", "skipped_no_new_records"}
            for row in stage_rows
        )
        if latest and not latest.get("published") and declared_complete:
            issues.append(
                {
                    "severity": "critical",
                    "code": "COMPLETE_RUN_UNPUBLISHED" if first_blocking_stage is None else "COMPLETED_RUN_HAS_POSTRUN_MUTATIONS",
                    "detail": (
                        f"{latest['run_id']} completed all stages but is not represented as published."
                        if first_blocking_stage is None
                        else f"{latest['run_id']} was completed, then one or more stage-owned files changed."
                    ),
                }
            )
        if selected and selected.get("published") and first_blocking_stage:
            issues.append(
                {
                    "severity": "critical",
                    "code": "PUBLISHED_RUN_HAS_UNACKNOWLEDGED_MUTATIONS",
                    "detail": (
                        f"Published run {selected['run_id']} has a hash-invalid or incomplete "
                        f"stage beginning at {first_blocking_stage}."
                    ),
                }
            )
        atlas_snapshot = str(atlas_meta.get("generated_from") or "")
        state_snapshot = str(self.current.get("taxonomy_root") or "")
        if atlas_snapshot and atlas_snapshot != state_snapshot:
            issues.append(
                {
                    "severity": "critical",
                    "code": "ATLAS_STATE_DIVERGENCE",
                    "detail": f"Public atlas uses {atlas_snapshot}, while control state points to {state_snapshot}.",
                }
            )
        if selected and first_blocking_stage and declared_complete:
            changed = ", ".join(row["stage"] for row in stage_rows if row["status"] == "invalidated")
            actions.append(
                f"Audit the listed mutations ({changed}); reconcile the published supplemental snapshot with explicit mutation acknowledgements."
            )
        elif selected and first_blocking_stage:
            row = next(item for item in stage_rows if item["stage"] == first_blocking_stage)
            command = (
                f"python3 scripts/run_living_review_pipeline.py run --run-id {selected['run_id']} "
                f"--from-stage {first_blocking_stage} --manage-server"
            )
            actions.append(row["note"] or command)
            if row["note"]:
                actions.append(command)
        elif selected and not selected.get("published"):
            actions.append(
                f"Publish or reconcile {selected['run_id']}; do not start the next date interval first."
            )
        elif state_path.is_file():
            next_date = (date.fromisoformat(self.current["search_end"]) + timedelta(days=1)).isoformat()
            actions.append(
                f"Next update begins {next_date}. Run `plan`, then `preflight`, then `run --manage-server`."
            )

        result = {
            "healthy": not any(issue["severity"] == "critical" for issue in issues),
            "validation_mode": {
                "name": "repository_checkout" if repository_checkout_requested else "complete_local_archive",
                "external_omissions_accepted": repository_omission_count,
                "artifact_ledger": (
                    selected_pipeline._repository_artifact_ledger_summary
                    if selected and repository_checkout_requested and not repository_ledger_error
                    else None
                ),
            },
            "living_state": {"path": rel(state_path), "present": state_path.is_file(), "search_end": self.current["search_end"]},
            "method_lock": method_lock,
            "public_atlas": {
                "path": rel(atlas_root),
                "present": atlas_data.is_file(),
                "generated_from": atlas_snapshot,
                "records": atlas_meta.get("record_count"),
                "models": atlas_meta.get("model_count"),
                "routes": atlas_meta.get("route_count"),
            },
            "run": {
                "run_id": selected.get("run_id") if selected else None,
                "published": selected.get("published") if selected else None,
                "first_blocking_stage": first_blocking_stage,
                "stages": stage_rows,
            },
            "issues": issues,
            "next_actions": actions,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["healthy"] else 2

    def reconcile(self) -> int:
        """Adopt an already built supplemental snapshot without replacing the live atlas."""
        incomplete = [stage for stage in STAGES if not self.stage_is_complete(stage)]
        allowed_mutations = set(getattr(self.args, "allow_mutated_stage", []))
        undeclared = [stage for stage in incomplete if stage not in allowed_mutations]
        if undeclared:
            raise RuntimeError(
                "Reconciliation requires the primary run's complete hash-valid closure; "
                f"incomplete_or_mutated={', '.join(undeclared)}. Inspect with `doctor` and "
                "explicitly acknowledge documented post-run mutations with --allow-mutated-stage."
            )
        noncomplete = [
            stage
            for stage in incomplete
            if self.manifest.get("stages", {}).get(stage, {}).get("status")
            not in {"complete", "skipped_no_new_records"}
        ]
        if noncomplete:
            raise RuntimeError(f"Mutation exceptions cannot waive incomplete stages: {', '.join(noncomplete)}")
        if self.manifest.get("published"):
            raise RuntimeError("Run is already published")
        live_state = self.load_current_state()
        for field in ("search_end", "master_record_files", "taxonomy_root", "docling_corpus_roots", "crop_ledger", "atlas_output"):
            if live_state.get(field) != self.manifest["prior_state"].get(field):
                raise RuntimeError(f"Living state changed after this run started ({field})")

        snapshot_root = resolve(self.args.snapshot_root)
        atlas_root = resolve(self.args.atlas_root or self.config["atlas_output"])
        snapshot_manifest_path = snapshot_root / "snapshot_manifest.json"
        atlas_data_path = atlas_root / "data/atlas.json"
        if not snapshot_manifest_path.is_file() or not atlas_data_path.is_file():
            raise RuntimeError("Reconciliation requires snapshot_manifest.json and atlas data/atlas.json")
        snapshot = read_json(snapshot_manifest_path)
        atlas = read_json(atlas_data_path)
        atlas_meta = atlas.get("meta", {})
        count_fields = {
            "records": "record_count",
            "studies": "study_count",
            "models": "model_count",
            "configurations": "configuration_count",
            "routes": "route_count",
        }
        mismatches = {
            source: {"snapshot": snapshot.get(source), "atlas": atlas_meta.get(target)}
            for source, target in count_fields.items()
            if snapshot.get(source) != atlas_meta.get(target)
        }
        if mismatches:
            raise RuntimeError(f"Snapshot/atlas count mismatch: {mismatches}")
        if str(atlas_meta.get("generated_from") or "") != rel(snapshot_root):
            raise RuntimeError("Atlas generated_from does not point to the supplied snapshot")

        supplemental_files = [resolve(path) for path in self.args.supplemental_record_file]
        for path in supplemental_files:
            if not path.is_file() or record_count(path) < 1:
                raise RuntimeError(f"Invalid supplemental record file: {path}")
        corpus_roots = [rel(resolve(path)) for path in snapshot.get("corpus_roots", [])]
        for root in corpus_roots:
            if not resolve(root).is_dir():
                raise RuntimeError(f"Snapshot corpus root is unavailable: {root}")

        primary_facts = self.paths.report / "prisma_update_facts.json"
        reconciliation_path = self.paths.report / f"publication_reconciliation_{snapshot['records']}_records.json"
        reconciliation = {
            "schema_version": 1,
            "kind": "supplemental_recall_publication_reconciliation",
            "created": now_iso(),
            "run_id": self.run_id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "reason": self.args.reason,
            "acknowledged_post_run_mutations": {
                stage: self.stage_validation_issues(stage) for stage in sorted(allowed_mutations)
            },
            "primary_prisma_facts": rel(primary_facts),
            "supplemental_record_files": [rel(path) for path in supplemental_files],
            "snapshot": rel(snapshot_root),
            "atlas": rel(atlas_root),
            "catalog_after_reconciliation": {source: snapshot[source] for source in count_fields},
            "note": "Primary PRISMA facts remain immutable; this ledger makes the post-search supplemental recall correction explicit.",
        }
        write_json(reconciliation_path, reconciliation)

        master_files = list(self.current["master_record_files"])
        for path in [self.paths.records / "new_records_after_cross_dedup_crossref_checked.json", *supplemental_files]:
            value = rel(path)
            if value not in master_files:
                master_files.append(value)
        history = list(live_state.get("prisma_update_history", []))
        history.append(
            {
                "run_id": self.run_id,
                "date_from": self.date_from,
                "date_to": self.date_to,
                "facts": rel(reconciliation_path),
                "publication_mode": "supplemental_recall_reconciliation",
            }
        )
        state = {
            "schema_version": 1,
            "updated": now_iso(),
            "search_end": self.date_to,
            "master_record_files": master_files,
            "taxonomy_root": rel(snapshot_root),
            "docling_corpus_roots": corpus_roots,
            "crop_ledger": rel(snapshot_root / "crop_ledger.json"),
            "atlas_output": self.config["atlas_output"],
            "last_run_id": self.run_id,
            "last_run_manifest": rel(self.manifest_path),
            "last_prisma_update": rel(reconciliation_path),
            "prisma_update_history": history,
        }
        state_path = resolve(self.config["living_state"])
        write_json(state_path, state)
        self.manifest["published"] = True
        self.manifest["published_at"] = now_iso()
        self.manifest["publication_mode"] = "supplemental_recall_reconciliation"
        self.manifest["publication_reconciliation"] = rel(reconciliation_path)
        self.manifest["published_state"] = state
        self.save_manifest()
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0

    def verify_live(self) -> int:
        atlas_root = resolve(self.config["atlas_output"])
        local_path = atlas_root / "data/atlas.json"
        if not local_path.is_file():
            raise RuntimeError(f"Local atlas is missing: {local_path}")
        base_url = str(self.args.url or self.config.get("public_atlas_url") or "").rstrip("/")
        if not base_url:
            raise RuntimeError("Configure public_atlas_url or pass --url")
        import requests

        cache_token = int(time.time())
        headers = {"Cache-Control": "no-cache", "User-Agent": "living-review-verifier/2"}

        def fetch(path: str) -> bytes:
            encoded = urllib.parse.quote(path, safe="/")
            url = f"{base_url}/{encoded}?verify={cache_token}"
            last_error: Exception | None = None
            for attempt in range(1, 5):
                try:
                    response = requests.get(url, timeout=60, headers=headers)
                    response.raise_for_status()
                    return response.content
                except requests.RequestException as exc:
                    last_error = exc
                    if attempt < 4:
                        time.sleep(attempt)
            assert last_error is not None
            raise last_error

        url = f"{base_url}/data/atlas.json"
        remote_bytes = fetch("data/atlas.json")
        local_bytes = local_path.read_bytes()
        local = json.loads(local_bytes)
        remote = json.loads(remote_bytes)
        fields = ("generated_from", "record_count", "study_count", "model_count", "configuration_count", "route_count")
        local_meta = local.get("meta", {})
        remote_meta = remote.get("meta", {})
        differences = {
            field: {"local": local_meta.get(field), "remote": remote_meta.get(field)}
            for field in fields
            if local_meta.get(field) != remote_meta.get(field)
        }
        exact_bytes_match = local_bytes == remote_bytes
        expected_commit = str(getattr(self.args, "expected_commit", "") or "")
        check_assets = bool(getattr(self.args, "check_assets", False))
        deployment: dict[str, Any] | None = None
        deployment_error = ""
        try:
            deployment = json.loads(fetch("data/deployment.json"))
        except Exception as exc:
            deployment_error = repr(exc)
        commit_match = bool(deployment and deployment.get("commit") == expected_commit) if expected_commit else None
        local_tree = atlas_tree_manifest(atlas_root)
        tree_match = bool(
            deployment
            and (deployment.get("atlas_tree") or {}).get("manifest_sha256")
            == local_tree["manifest_sha256"]
        )
        asset_failures: list[dict[str, Any]] = []
        checked_assets = 0
        if check_assets:
            if not deployment:
                asset_failures.append({"path": "data/deployment.json", "error": deployment_error})
            else:
                remote_rows = (deployment.get("atlas_tree") or {}).get("files") or []
                remote_by_path = {str(row.get("path") or ""): row for row in remote_rows}
                local_by_path = {row["path"]: row for row in local_tree["files"]}
                if set(remote_by_path) != set(local_by_path):
                    asset_failures.append(
                        {
                            "path": "<tree>",
                            "missing_remote": sorted(set(local_by_path) - set(remote_by_path)),
                            "extra_remote": sorted(set(remote_by_path) - set(local_by_path)),
                        }
                    )
                for path, expected in sorted(local_by_path.items()):
                    try:
                        content = fetch(path)
                        checked_assets += 1
                        digest = hashlib.sha256(content).hexdigest()
                        if digest != expected["sha256"]:
                            asset_failures.append(
                                {"path": path, "expected_sha256": expected["sha256"], "remote_sha256": digest}
                            )
                    except Exception as exc:
                        asset_failures.append({"path": path, "error": repr(exc)})
        release_checks_ok = (
            (not expected_commit or commit_match is True)
            and (not check_assets or (tree_match and not asset_failures))
        )
        result = {
            "ok": not differences and exact_bytes_match and release_checks_ok,
            "url": url,
            "local": rel(local_path),
            "local_sha256": hashlib.sha256(local_bytes).hexdigest(),
            "remote_sha256": hashlib.sha256(remote_bytes).hexdigest(),
            "semantic_differences": differences,
            "exact_bytes_match": exact_bytes_match,
            "deployment_manifest_present": deployment is not None,
            "deployment_manifest_error": deployment_error,
            "expected_commit": expected_commit,
            "deployed_commit": deployment.get("commit") if deployment else None,
            "commit_match": commit_match,
            "local_tree_sha256": local_tree["manifest_sha256"],
            "remote_tree_sha256": (deployment.get("atlas_tree") or {}).get("manifest_sha256")
            if deployment
            else None,
            "tree_match": tree_match if deployment else None,
            "assets_checked": checked_assets,
            "asset_failures": asset_failures,
        }
        if getattr(self.args, "record_completion", False):
            if not result["ok"]:
                raise RuntimeError("Cannot write a completion record for a failed remote verification")
            if not expected_commit or not check_assets:
                raise RuntimeError(
                    "--record-completion requires --expected-commit and --check-assets"
                )
            if not self.args.workflow_run_id or not self.args.operator:
                raise RuntimeError(
                    "--record-completion requires --workflow-run-id and --operator"
                )
            screenshot_paths = [resolve(path) for path in self.args.screenshot]
            if len(screenshot_paths) < 2:
                raise RuntimeError(
                    "--record-completion requires at least desktop and mobile screenshots"
                )
            missing = [str(path) for path in screenshot_paths if not path.is_file()]
            if missing:
                raise RuntimeError(f"Completion screenshots are missing: {missing}")
            browser_qa_arg = str(
                getattr(self.args, "browser_qa_report", "") or ""
            ).strip()
            if not browser_qa_arg:
                raise RuntimeError(
                    "--record-completion requires --browser-qa-report from the deployed URL"
                )
            browser_qa_path = resolve(browser_qa_arg)
            if not browser_qa_path.is_file():
                raise RuntimeError(f"Remote browser QA report is missing: {browser_qa_path}")
            browser_qa_payload = read_json(browser_qa_path)
            if browser_qa_payload.get("status") != "ok":
                raise RuntimeError("Remote browser QA report does not have status=ok")
            completed_run_id = self.args.run_id or self.current.get("last_run_id")
            completed_root = resolve(self.config["updates_root"]) / str(completed_run_id)
            completed_manifest = completed_root / "run_manifest.json"
            completed_manifest_payload = read_json(completed_manifest)
            method_lock = self.method_lock_status(completed_manifest_payload)
            if not method_lock["ok"]:
                raise RuntimeError(
                    "Completion requires the run-bound method lock to verify: "
                    + "; ".join(method_lock["issues"])
                )
            archive_status = self.artifact_archive_status(
                completed_root, require_independent=True
            )
            if not archive_status["ok"]:
                raise RuntimeError(
                    "Completion requires an independently verified pre-publication archive: "
                    + "; ".join(archive_status["issues"])
                )
            archive_receipt = resolve(str(archive_status.get("receipt") or ""))
            if not archive_receipt.is_file():
                raise RuntimeError(
                    f"Completion archive receipt is missing: {archive_receipt}"
                )
            archive_contract = {
                **archive_status,
                "receipt_artifact": self.artifact(archive_receipt),
            }
            search_config = completed_root / "00_search/search_config.json"
            prisma_facts_path = completed_root / "16_report/prisma_update_facts.json"
            prisma_facts = read_json(prisma_facts_path)
            catalog_count_fields = (
                "record_count",
                "study_count",
                "model_count",
                "configuration_count",
                "route_count",
            )
            completion = {
                "schema_version": 2,
                "completed_at": now_iso(),
                "run_id": completed_run_id,
                "operator": self.args.operator,
                "commit": expected_commit,
                "workflow_run_id": str(self.args.workflow_run_id),
                "search_interval": {
                    "date_from": completed_manifest_payload.get("date_from"),
                    "date_to": completed_manifest_payload.get("date_to"),
                    "search_completed_at": (
                        completed_manifest_payload.get("stages", {})
                        .get("search", {})
                        .get("finished")
                        or completed_manifest_payload.get("stages", {})
                        .get("search", {})
                        .get("ended")
                    ),
                },
                "method": {
                    "method_id": method_lock["method_id"],
                    "method_lock": self.artifact(Path(method_lock["lock_path"])),
                    "method_lock_sha256": method_lock["lock_sha256"],
                    "frozen_taxonomy_sha256": method_lock[
                        "frozen_taxonomy_sha256"
                    ],
                },
                "artifact_archive": archive_contract,
                "run_manifest": self.artifact(completed_manifest),
                "stage_statuses": {
                    stage: row.get("status")
                    for stage, row in completed_manifest_payload.get("stages", {}).items()
                },
                "search_config": self.artifact(search_config),
                "prisma_facts": self.artifact(prisma_facts_path),
                "prisma_counts": prisma_facts,
                "catalog_counts": {
                    field: local_meta.get(field) for field in catalog_count_fields
                },
                "living_state": self.artifact(resolve(self.config["living_state"])),
                "atlas_json": self.artifact(local_path),
                "remote_verification": result,
                "local_browser_qa": self.artifact(atlas_root / "data/browser_qa.json"),
                "remote_browser_qa": self.artifact(browser_qa_path),
                "screenshots": [self.artifact(path) for path in screenshot_paths],
                "next_search_date": (
                    date.fromisoformat(self.current["search_end"]) + timedelta(days=1)
                ).isoformat(),
            }
            completion_root = resolve(
                self.config.get("release_records_root", "data/living_catalog/releases")
            ) / str(completed_run_id)
            completion_path = completion_root / "completion_record.json"
            if completion_path.exists():
                existing = read_json(completion_path)
                completion["completed_at"] = existing.get("completed_at")
                if existing != completion:
                    raise RuntimeError(
                        f"Completion record already exists and is immutable: {completion_path}"
                    )
            else:
                write_json(completion_path, completion)
            result["completion_record"] = rel(completion_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 2

    def preflight(self) -> int:
        checks: list[dict[str, Any]] = []
        target_stage = getattr(self.args, "through_stage", None) or "report"
        target_index = STAGES.index(target_stage)

        def add(
            name: str,
            ok: bool,
            detail: str,
            required: bool = True,
            needed_at: str | None = None,
        ) -> None:
            needed = (
                required
                and (needed_at is None or STAGES.index(needed_at) <= target_index)
            )
            checks.append(
                {
                    "name": name,
                    "ok": ok,
                    "required": needed,
                    "detail": detail,
                    "needed_at": needed_at,
                }
            )

        method_lock = self.method_lock_status()
        add(
            "method_lock",
            method_lock["ok"],
            (
                f"{method_lock.get('method_id')} ({method_lock.get('files_checked', 0)} files verified)"
                if method_lock["ok"]
                else "; ".join(method_lock["issues"])
            ),
            needed_at="search",
        )
        git_root = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--show-toplevel"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        actual_git_root = Path(git_root.stdout.strip()).resolve() if git_root.returncode == 0 else None
        add(
            "canonical_repository_root",
            actual_git_root == ROOT.resolve(),
            str(actual_git_root) if actual_git_root else git_root.stderr.strip() or "not a Git checkout",
            needed_at="search",
        )
        for artifact_root in self.artifact_roots():
            add(
                f"artifact_root:{artifact_root}",
                artifact_root.is_dir(),
                "present" if artifact_root.is_dir() else "missing",
                needed_at="snapshot",
            )

        executable_stages = {
            "codex": "abstract-screening",
            "node": "atlas",
            "magick": "crop-validation",
        }
        for executable, needed_at in executable_stages.items():
            location = shutil.which(executable)
            add(
                f"executable:{executable}",
                bool(location),
                location or "not found",
                needed_at=needed_at,
            )
        for module in ("requests",):
            available = importlib.util.find_spec(module) is not None
            add(
                f"python_module:{module}",
                available,
                "importable" if available else "not importable in the orchestrator Python",
                needed_at="search",
            )
        node_path = playwright_node_path()
        add(
            "node_module:playwright",
            bool(node_path),
            node_path or "not found in NODE_PATH, local node_modules, or Codex runtime",
            needed_at="atlas",
        )
        docling_python = self.resolve_artifact(self.config["docling_python"])
        docling_importable = False
        docling_detail = (
            f"missing; create from {ROOT / 'scripts/docling/requirements-docling.txt'}"
        )
        if docling_python.is_file():
            requirements = ROOT / "scripts/docling/requirements-docling.txt"
            expected_versions = {}
            for line in requirements.read_text(encoding="utf-8").splitlines():
                if "==" in line and not line.lstrip().startswith("#"):
                    package, version = line.split("==", 1)
                    expected_versions[package.strip()] = version.strip()
            probe_code = "\n".join(
                [
                    "import json",
                    "from importlib.metadata import version",
                    "import numpy as np",
                    "import torch",
                    "import docling, docling_graph",
                    f"expected = {expected_versions!r}",
                    "actual = {name: version(name) for name in expected}",
                    "assert actual == expected, (actual, expected)",
                    "tensor = torch.tensor([1.0, 2.0])",
                    "assert np.allclose(tensor.numpy(), np.array([1.0, 2.0]))",
                    "print(json.dumps(actual, sort_keys=True))",
                ]
            )
            try:
                probe = subprocess.run(
                    [str(docling_python), "-c", probe_code],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=180,
                )
                dependency_probe = subprocess.run(
                    [str(docling_python), "-m", "pip", "check"],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=60,
                )
                docling_importable = probe.returncode == 0 and dependency_probe.returncode == 0
                error_lines = (probe.stderr + dependency_probe.stdout + dependency_probe.stderr).strip().splitlines()
                docling_detail = (
                    f"{docling_python}; pinned versions, imports, dependency graph, and Torch/NumPy bridge verified"
                    if docling_importable
                    else (
                        f"{docling_python}; runtime probe failed: "
                        f"{error_lines[-1] if error_lines else f'return code {probe.returncode}/{dependency_probe.returncode}'}"
                    )
                )
            except subprocess.TimeoutExpired:
                docling_detail = f"{docling_python}; runtime probe exceeded 180 seconds"
        add(
            "docling_environment",
            docling_importable,
            docling_detail,
            needed_at="docling-screening",
        )
        keys_path = self.resolve_artifact(self.config["api_keys_file"])
        key_names = set(read_json(keys_path)) if keys_path.is_file() else set()
        add("api_keys_file", keys_path.is_file(), str(keys_path), needed_at="search")
        scholar_provider_export = self.paths.search / "google_scholar_provider_export.json"
        add(
            "artifact:google_scholar_provider_export",
            scholar_provider_export.is_file(),
            str(scholar_provider_export) if scholar_provider_export.is_file() else (
                "missing; see protocol/google_scholar_provider_export_schema.md"
            ),
            needed_at="search",
        )
        for label, alternatives, required in (
            ("Scopus", {"scopus"}, True),
            ("Semantic Scholar", {"semantic_scholar", "S2_API_KEY"}, True),
            ("SpringerNature Meta API", {"springernature_Meta_API"}, True),
            ("SpringerNature Open Access API", {"springernature_Open_Access_API"}, True),
            ("OpenAlex", {"openalex", "OPENALEX_API_KEY"}, True),
        ):
            add(
                f"api_key:{label}",
                bool(key_names & alternatives),
                "configured" if key_names & alternatives else "missing",
                required,
                "search" if required else None,
            )
        required_paths = [
            (resolve(self.config["search_config_template"]), "search"),
            (self.resolve_artifact(self.current["taxonomy_root"]) / "taxonomy_tree.json", "taxonomy-classification"),
            (self.resolve_artifact(self.current["taxonomy_root"]) / "route_annotations.jsonl", "taxonomy-classification"),
            (self.resolve_artifact(self.current["crop_ledger"]), "crop-validation"),
            (resolve(self.current["atlas_output"]) / "index.html", "atlas"),
            *[(self.resolve_artifact(path), "prepare-records") for path in self.current["master_record_files"]],
        ]
        if self.config.get("baseline_prisma_facts"):
            required_paths.append((resolve(self.config["baseline_prisma_facts"]), "report"))
        for path, needed_at in required_paths:
            add(
                f"artifact:{rel(path)}",
                path.is_file(),
                "present" if path.is_file() else "missing",
                needed_at=needed_at,
            )
        for root in self.current["docling_corpus_roots"]:
            path = self.resolve_artifact(root) / "manifests/canonical_docling_profile_manifest.csv"
            add(
                f"archival_artifact:{rel(path)}",
                path.is_file(),
                "present" if path.is_file() else "missing; restore the immutable Docling corpus before snapshot creation",
                needed_at="snapshot",
            )
        payload = {
            "run_id": self.run_id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "through_stage": target_stage,
            "ready": all(row["ok"] or not row["required"] for row in checks),
            "checks": checks,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ready"] else 2


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    root.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    sub = root.add_subparsers(dest="command", required=True)
    for name in (
        "plan",
        "preflight",
        "run",
        "status",
        "doctor",
        "scholar-capture",
        "scholar-validate",
        "register-supplemental",
        "taxonomy-rerun-preflight",
        "publish",
        "reconcile",
        "release-manifest",
        "verify-live",
        "incident",
    ):
        command = sub.add_parser(name)
        command.add_argument("--run-id")
        command.add_argument("--date-from")
        command.add_argument("--date-to")
        if name == "preflight":
            command.add_argument("--through-stage", choices=STAGES, default="report")
        if name == "doctor":
            command.add_argument("--repository-checkout", action="store_true")
        if name == "run":
            command.add_argument("--from-stage", choices=STAGES)
            command.add_argument("--through-stage", choices=STAGES)
            command.add_argument("--force", action="store_true")
            command.add_argument("--manage-server", action="store_true")
        if name == "reconcile":
            command.add_argument("--snapshot-root", required=True)
            command.add_argument("--atlas-root")
            command.add_argument("--supplemental-record-file", action="append", default=[])
            command.add_argument("--reason", required=True)
            command.add_argument("--allow-mutated-stage", action="append", choices=STAGES, default=[])
        if name == "scholar-capture":
            command.add_argument("--retries", type=int, default=5)
            command.add_argument("--delay", type=float, default=1.0)
        if name == "register-supplemental":
            command.add_argument("--record-file", required=True)
            command.add_argument("--reason", required=True)
            command.add_argument("--source-url")
            command.add_argument("--resolver", required=True)
            command.add_argument("--declared-at")
        if name == "taxonomy-rerun-preflight":
            command.add_argument("--output-dir", required=True)
        if name == "release-manifest":
            command.add_argument("--commit", required=True)
        if name == "verify-live":
            command.add_argument("--url")
            command.add_argument("--expected-commit")
            command.add_argument("--check-assets", action="store_true")
            command.add_argument("--record-completion", action="store_true")
            command.add_argument("--workflow-run-id")
            command.add_argument("--operator")
            command.add_argument("--browser-qa-report")
            command.add_argument("--screenshot", action="append", default=[])
        if name == "incident":
            command.add_argument(
                "--phase",
                required=True,
                choices=["search", "processing", "publication", "deployment", "rollback"],
            )
            command.add_argument("--summary", required=True)
            command.add_argument("--operator", required=True)
            command.add_argument("--commit")
            command.add_argument("--workflow-run-id")
            command.add_argument("--recovery-commit")
        command.set_defaults(
            from_stage=None,
            through_stage=None,
            force=False,
            manage_server=False,
            retries=5,
            delay=1.0,
            repository_checkout=False,
        )
    return root


def main() -> int:
    args = parser().parse_args()
    config = read_json(args.config)
    pipeline = Pipeline(args, config)
    if args.command == "plan":
        print(
            json.dumps(
                {
                    "run_id": pipeline.run_id,
                    "date_from": pipeline.date_from,
                    "date_to": pipeline.date_to,
                    "run_root": rel(pipeline.run_root),
                    "repository_root": str(ROOT),
                    "artifact_roots": [str(path) for path in pipeline.artifact_roots()],
                    "docling_python": pipeline.docling_python(),
                    "stages": STAGES,
                    "prior_state": pipeline.current,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.command == "status":
        print(json.dumps(pipeline.manifest, ensure_ascii=False, indent=2))
        return 0
    if args.command == "doctor":
        return pipeline.doctor()
    if args.command == "preflight":
        return pipeline.preflight()
    if args.command == "scholar-capture":
        return pipeline.scholar_capture()
    if args.command == "scholar-validate":
        return pipeline.scholar_validate()
    if args.command == "register-supplemental":
        return pipeline.register_supplemental()
    if args.command == "taxonomy-rerun-preflight":
        return pipeline.taxonomy_rerun_preflight()
    if args.command == "publish":
        return pipeline.publish()
    if args.command == "reconcile":
        return pipeline.reconcile()
    if args.command == "verify-live":
        return pipeline.verify_live()
    if args.command == "release-manifest":
        return pipeline.release_manifest()
    if args.command == "incident":
        return pipeline.record_incident()
    try:
        return pipeline.run()
    except ManualGate as exc:
        print(f"MANUAL GATE: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
