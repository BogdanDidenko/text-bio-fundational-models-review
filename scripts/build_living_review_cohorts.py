#!/usr/bin/env python3
"""Build deterministic hand-off artifacts between living-review pipeline stages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import mimetypes
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.docling.docling_graph_grounding import (
    heading_key,
    parse_markdown_sections_for_derivation,
)


PDF_MIN_BYTES = 5000
HTML_MIN_TEXT_CHARS = 3000


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def records_from(path: Path) -> list[dict[str, Any]]:
    value = read_json(path)
    if isinstance(value, dict) and isinstance(value.get("records"), list):
        return value["records"]
    if isinstance(value, list):
        return value
    raise ValueError(f"Unsupported records artifact: {path}")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")[:160] or "record"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def strict_index(
    records: Iterable[dict[str, Any]], key: str, artifact: str
) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for record in records:
        value = str(record.get(key) or "")
        if not value or value in index:
            raise RuntimeError(f"{artifact} has duplicate or empty {key}")
        index[value] = record
    return index


def abstract_input(args: argparse.Namespace) -> int:
    records = records_from(args.input)
    kept, excluded = [], []
    for record in records:
        abstract = str(record.get("abstract") or "").strip()
        if len(abstract) >= args.minimum_chars:
            kept.append(record)
        else:
            excluded.append(
                {
                    **record,
                    "exclusion_code": "EC_NO_USABLE_ABSTRACT",
                    "abstract_chars": len(abstract),
                }
            )
    write_json(
        args.output,
        {
            "metadata": {
                "created": now_iso(),
                "source": str(args.input),
                "minimum_abstract_chars": args.minimum_chars,
                "records_for_screening": len(kept),
                "excluded_no_usable_abstract": len(excluded),
            },
            "records": kept,
        },
    )
    write_json(
        args.excluded_output,
        {
            "metadata": {
                "created": now_iso(),
                "reason": f"Abstract shorter than {args.minimum_chars} characters",
                "exclusion_code": "EC_NO_USABLE_ABSTRACT",
            },
            "records": excluded,
        },
    )
    print(json.dumps({"screening": len(kept), "excluded": len(excluded)}))
    return 0


def fulltext_candidates(args: argparse.Namespace) -> int:
    decisions = records_from(args.screening_results)
    source = records_from(args.screening_input)
    source_index = strict_index(source, "record_id", "Abstract screening input")
    crosswalk_index: dict[str, dict[str, Any]] = {}
    if getattr(args, "record_id_crosswalk", None):
        crosswalk_index = strict_index(
            records_from(args.record_id_crosswalk),
            "legacy_record_id",
            "Screening record ID crosswalk",
        )
        if set(crosswalk_index) != set(source_index):
            raise RuntimeError("Screening record ID crosswalk does not exactly cover the screening input")

    duplicate_resolutions: dict[str, dict[str, Any]] = {}
    if getattr(args, "duplicate_resolutions", None):
        duplicate_resolutions = strict_index(
            records_from(args.duplicate_resolutions),
            "duplicate_screening_record_id",
            "Post-screening duplicate resolutions",
        )
        for duplicate_id, resolution in duplicate_resolutions.items():
            if resolution.get("resolution") != "duplicate_of":
                raise RuntimeError(f"Unsupported post-screening resolution for {duplicate_id}")
            missing_provenance = [
                field
                for field in ("rationale", "resolver", "resolved_at")
                if not str(resolution.get(field) or "").strip()
            ]
            if missing_provenance:
                raise RuntimeError(
                    f"Post-screening duplicate resolution lacks provenance for {duplicate_id}: "
                    + ", ".join(missing_provenance)
                )
            canonical_id = str(resolution.get("canonical_screening_record_id") or "")
            if duplicate_id not in source_index or canonical_id not in source_index:
                raise RuntimeError(f"Duplicate resolution references an unknown screening record: {duplicate_id}")

    canonical_index: dict[str, dict[str, Any]] = {}
    if getattr(args, "canonical_input", None):
        canonical_index = strict_index(
            records_from(args.canonical_input), "record_id", "Canonical abstract screening source"
        )
        expected_stable_ids = {
            str(row.get("stable_record_id") or legacy_id)
            for legacy_id, row in crosswalk_index.items()
        }
        if set(canonical_index) != expected_stable_ids:
            raise RuntimeError("Canonical source does not exactly cover the screening ID crosswalk")

    selected = []
    removed_duplicates = []
    for decision in decisions:
        if decision.get("final_decision") not in {"INCLUDE", "UNCERTAIN"}:
            continue
        record_id = str(decision.get("record_id") or "")
        base = source_index.get(record_id, {})
        if not base:
            raise RuntimeError(f"No source record for screening decision {decision.get('record_id')}")
        if record_id in duplicate_resolutions:
            removed_duplicates.append(
                {
                    "screening_record_id": record_id,
                    "final_decision": decision["final_decision"],
                    **duplicate_resolutions[record_id],
                }
            )
            continue
        if decision.get("candidate_id") and str(decision["candidate_id"]) != str(base.get("candidate_id") or ""):
            raise RuntimeError(f"Candidate mismatch for screening decision {record_id}")
        mapping = crosswalk_index.get(record_id, {})
        stable_id = str(mapping.get("stable_record_id") or record_id)
        candidate_id = str(mapping.get("candidate_id") or base.get("candidate_id") or stable_id)
        canonical = canonical_index.get(stable_id, {})
        if canonical and canonical.get("title", "") != base.get("title", ""):
            raise RuntimeError(f"Canonical source title mismatch for screening decision {record_id}")
        record = {
            **base,
            **canonical,
            "record_id": stable_id,
            "candidate_id": candidate_id,
            "screening_record_id": record_id,
            "final_decision": decision["final_decision"],
            "final_code": decision.get("final_code", ""),
            "uncertainty_reason": decision.get("uncertainty_reason", ""),
            "screening_source": str(args.screening_results),
        }
        selected.append(record)
    write_json(
        args.output,
        {
            "metadata": {
                "created": now_iso(),
                "screening_results": str(args.screening_results),
                "candidate_rule": "title/abstract INCLUDE or UNCERTAIN",
                "raw_screening_candidates": len(selected) + len(removed_duplicates),
                "postscreen_duplicates_removed": len(removed_duplicates),
                "candidate_count": len(selected),
            },
            "records": selected,
            "removed_duplicates": removed_duplicates,
        },
    )
    write_csv(args.output.with_suffix(".csv"), selected)
    print(json.dumps({"fulltext_candidates": len(selected), "output": str(args.output)}))
    return 0


def download_rank(row: dict[str, Any]) -> tuple[int, int]:
    status_rank = {
        "pdf_downloaded": 5,
        "html_full_text_downloaded": 4,
        "xml_full_text_downloaded": 3,
        "non_pdf_full_text_downloaded": 2,
        "skipped_existing": 2,
        "retrieval_incomplete": 1,
        "access_restricted": 0,
        "no_full_text_found": 0,
    }
    return status_rank.get(str(row.get("status")), -1), len(row.get("files") or [])


def normalized_download_status(row: dict[str, Any]) -> str:
    status = str(row.get("status") or "")
    if status != "non_pdf_full_text_downloaded":
        return status
    suffixes = {Path(str(item.get("file") or item.get("filename") or "")).suffix.casefold() for item in row.get("files") or []}
    if ".html" in suffixes or ".htm" in suffixes:
        return "html_full_text_downloaded"
    if ".xml" in suffixes:
        return "xml_full_text_downloaded"
    return "retrieval_incomplete"


def consolidate_downloads(args: argparse.Namespace) -> int:
    selected: dict[str, dict[str, Any]] = {}
    inputs = []
    for path in args.manifest:
        payload = read_json(path)
        rows = payload.get("results", []) if isinstance(payload, dict) else payload
        inputs.append({"path": str(path), "records": len(rows)})
        for source_row in rows:
            row = {**source_row, "status": normalized_download_status(source_row)}
            key = str(row.get("candidate_id") or row.get("record_id") or "")
            if not key:
                continue
            if key not in selected or download_rank(row) > download_rank(selected[key]):
                selected[key] = row
    manual_rows = []
    if args.manual_manifest and args.manual_manifest.exists():
        declarations = records_from(args.manual_manifest)
        for declaration in declarations:
            candidate_id = str(declaration.get("candidate_id") or "")
            if not candidate_id or candidate_id not in selected:
                raise RuntimeError(f"Unknown candidate_id in manual full-text manifest: {candidate_id}")
            source = Path(str(declaration.get("file") or "")).expanduser().resolve()
            kind = sniff_kind(source)
            usable, detail = document_usability(source, kind)
            if not usable:
                raise RuntimeError(
                    f"Manual full text for {candidate_id} is not a usable PDF/HTML payload "
                    f"({detail}): {source}"
                )
            target_dir = args.output.parent / "manual_files" / safe_name(candidate_id)
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / f"manual_full_text{source.suffix.casefold()}"
            shutil.copy2(source, target)
            file_info = {
                "source": "manual_declaration",
                "file": str(target.resolve()),
                "filename": target.name,
                "content_type": "application/pdf" if kind == "pdf" else "text/html",
                "bytes": target.stat().st_size,
                "sha256": file_sha256(target),
                "source_url": declaration.get("source_url", ""),
                "retriever": declaration.get("retriever", ""),
                "retrieved_at": declaration.get("retrieved_at", ""),
            }
            result = {
                **selected[candidate_id],
                "status": "pdf_downloaded" if kind == "pdf" else "html_full_text_downloaded",
                "folder": str(target_dir.resolve()),
                "files": [file_info],
                "manual_ingest": True,
            }
            selected[candidate_id] = result
            manual_rows.append({"candidate_id": candidate_id, **file_info})
    rows = [selected[key] for key in sorted(selected)]
    summary = {
        "created": now_iso(),
        "inputs": inputs,
        "manual_manifest": str(args.manual_manifest) if args.manual_manifest else "",
        "manual_full_texts_ingested": len(manual_rows),
        "manual_full_texts": manual_rows,
        "processed": len(rows),
        "pdf_downloaded": sum(row.get("status") == "pdf_downloaded" for row in rows),
        "html_full_text_downloaded": sum(row.get("status") == "html_full_text_downloaded" for row in rows),
        "xml_full_text_downloaded": sum(row.get("status") == "xml_full_text_downloaded" for row in rows),
        "retrieval_incomplete": sum(row.get("status") == "retrieval_incomplete" for row in rows),
        "access_restricted": sum(row.get("status") == "access_restricted" for row in rows),
        "no_full_text_found": sum(row.get("status") == "no_full_text_found" for row in rows),
        "results": rows,
    }
    # Compatibility field for older consumers; XML is deliberately excluded.
    summary["non_pdf_full_text_downloaded"] = summary["html_full_text_downloaded"]
    write_json(args.output, summary)
    write_csv(args.output.with_suffix(".csv"), rows)
    print(json.dumps({key: summary[key] for key in (
        "processed", "pdf_downloaded", "html_full_text_downloaded",
        "xml_full_text_downloaded", "retrieval_incomplete", "access_restricted",
        "no_full_text_found",
    )}))
    return 0


def sniff_kind(path: Path) -> str:
    if not path.is_file():
        return "missing"
    head = path.read_bytes()[:1024].lstrip()
    if head.startswith(b"%PDF"):
        return "pdf"
    lowered = head.lower()
    if b"<html" in lowered or b"<!doctype html" in lowered:
        return "html"
    if lowered.startswith(b"<?xml") or b"<article" in lowered:
        return "xml"
    guessed = mimetypes.guess_type(path.name)[0] or ""
    if "html" in guessed:
        return "html"
    if "xml" in guessed:
        return "xml"
    return "unknown"


def document_usability(path: Path, kind: str) -> tuple[bool, str]:
    """Apply the same content floor to automatic and manual Docling inputs."""
    if kind == "pdf":
        size = path.stat().st_size
        return size >= PDF_MIN_BYTES, f"pdf_bytes={size}"
    if kind == "html":
        text = path.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"(?is)<(script|style|nav|footer|header).*?</\1>", " ", text)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", html.unescape(text)).strip()
        return len(text) >= HTML_MIN_TEXT_CHARS, f"html_text_chars={len(text)}"
    return False, f"unsupported_kind={kind}"


def classify_pdf_text_role(text: str) -> str:
    head = re.sub(r"\s+", " ", text[:5000]).casefold()
    supplementary_markers = (
        "supplementary information",
        "supplementary note",
        "supporting information",
        "supplemental information",
    )
    return "supplementary" if any(marker in head for marker in supplementary_markers) else "main_or_unknown"


def pdf_document_role(path: Path) -> str:
    try:
        reader = PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages[:3])
    except Exception:
        return "main_or_unknown"
    return classify_pdf_text_role(text)


def best_document(download: dict[str, Any]) -> tuple[Path | None, str, list[str]]:
    ranked = []
    unsupported = []
    for item in download.get("files") or []:
        path = Path(str(item.get("file") or ""))
        kind = sniff_kind(path)
        usable, detail = document_usability(path, kind) if kind in {"pdf", "html"} else (False, "")
        # The configured Docling converter accepts PDF and HTML. Preserve XML/JATS
        # retrievals in the audit, but do not fail the whole conversion batch by
        # passing an unsupported payload to it.
        role = pdf_document_role(path) if kind == "pdf" and usable else "main_or_unknown"
        rank = {"pdf": 4, "html": 3}.get(kind, 0)
        if role == "supplementary":
            rank = 2
        if rank and usable:
            ranked.append((rank, path.stat().st_size, path, kind))
        elif kind not in {"missing", "unknown"}:
            unsupported.append(f"{kind}:{path}:{detail}")
    if not ranked:
        return None, "", unsupported
    _, _, path, kind = max(ranked, key=lambda item: (item[0], item[1]))
    return path.resolve(), kind, unsupported


def docling_config(args: argparse.Namespace) -> int:
    records = records_from(args.records)
    downloads_payload = read_json(args.download_manifest)
    downloads = downloads_payload.get("results", downloads_payload)
    download_index = strict_index(downloads, "candidate_id", "Full-text download manifest")
    documents, missing = [], []
    for record in records:
        candidate_id = str(record.get("candidate_id") or "")
        download = download_index.get(candidate_id, {})
        path, kind, unsupported = best_document(download)
        if path is None:
            missing.append(
                {
                    "record_id": record.get("record_id"),
                    "candidate_id": record.get("candidate_id"),
                    "title": record.get("title"),
                    "download_status": download.get("status", "missing_manifest_row"),
                    "retrieved_but_unsupported_documents": unsupported,
                }
            )
            continue
        documents.append(
            {
                "path": str(path),
                "kind": kind,
                "candidate_id": record.get("candidate_id") or record.get("record_id"),
                "source_record_id": record.get("source_record_id") or record.get("record_id"),
                "title": record.get("title", ""),
                "doi": record.get("doi", ""),
            }
        )
    settings = {
        "picture_description_backend": "openai-api" if args.vlm else "none",
        "openai_base_url": args.openai_base_url,
        "openai_model": args.vlm_model,
        "picture_description_timeout": args.vlm_timeout,
        "picture_description_concurrency": args.vlm_concurrency,
        "picture_description_max_tokens": None,
        "picture_description_temperature": 0,
        "picture_description_scale": 2,
        "picture_description_area_threshold": 0.0,
        "picture_description_prompt": args.picture_prompt if args.vlm else "",
        "skip_chunks": True,
        "max_workers": args.max_workers,
        "do_ocr": False,
        "do_table_structure": True,
        "table_former_mode": "ACCURATE",
        "do_cell_matching": True,
        "generate_page_images": True,
        "generate_picture_images": True,
        "images_scale": 2.0,
        "do_formula_enrichment": False,
        "heading_hierarchy": {
            "enabled": True,
            "use_bookmarks": True,
            "use_numbering": True,
            "use_style": True,
        },
    }
    config = {
        "name": args.name,
        "created": now_iso(),
        "output_root": str(args.profile_root),
        "source_records": str(args.records),
        "source_download_manifest": str(args.download_manifest),
        "records_total": len(records),
        "documents_total": len(documents),
        "missing_documents_total": len(missing),
        "settings": settings,
        "documents": documents,
        "pdfs": [item for item in documents if item["kind"] == "pdf"],
    }
    write_json(args.output, config)
    write_json(args.missing_output, {"created": now_iso(), "records": missing})
    print(json.dumps({"records": len(records), "documents": len(documents), "missing": len(missing), "vlm": args.vlm}))
    return 0


def accepted_records(args: argparse.Namespace) -> int:
    decisions = records_from(args.screening_results)
    source = records_from(args.screening_input)
    source_index = strict_index(source, "record_id", "Full-text screening input")
    metadata_index: dict[str, dict[str, Any]] = {}
    source_records_path = getattr(args, "source_records", None)
    if source_records_path:
        metadata_index = strict_index(
            records_from(source_records_path), "record_id", "Full-text candidate metadata"
        )
        if set(metadata_index) != set(source_index):
            raise RuntimeError(
                "Full-text candidate metadata does not exactly cover the screening input"
            )
    manual: dict[str, dict[str, str]] = {}
    uncertain_ids = {
        str(row.get("record_id") or "")
        for row in decisions
        if str(row.get("final_decision") or "") == "UNCERTAIN"
    }
    if args.manual_resolution and args.manual_resolution.exists():
        with args.manual_resolution.open(newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                record_id = str(row.get("record_id") or "").strip()
                if not record_id or record_id in manual:
                    raise RuntimeError("manual_resolution.csv has a duplicate or empty record_id")
                if record_id not in uncertain_ids:
                    raise RuntimeError(
                        f"manual_resolution.csv declares a non-UNCERTAIN record: {record_id}"
                    )
                if str(row.get("manual_decision") or "") not in {"INCLUDE", "EXCLUDE"}:
                    raise RuntimeError(f"Manual resolution {record_id} needs INCLUDE or EXCLUDE")
                for field in ("rationale", "resolver", "resolved_at"):
                    if not str(row.get(field) or "").strip():
                        raise RuntimeError(f"Manual resolution {record_id} has empty {field}")
                try:
                    datetime.fromisoformat(str(row["resolved_at"]))
                except ValueError as exc:
                    raise RuntimeError(f"Manual resolution {record_id} has invalid resolved_at") from exc
                manual[record_id] = row
    profile_rows = []
    with args.profile_manifest.open(newline="", encoding="utf-8") as stream:
        profile_rows = list(csv.DictReader(stream))
    profile_index = strict_index(profile_rows, "candidate_id", "Docling profile manifest")
    accepted, excluded, unresolved = [], [], []
    for decision in decisions:
        record_id = str(decision.get("record_id") or "")
        final = str(decision.get("final_decision") or "")
        resolution = manual.get(record_id)
        if final == "UNCERTAIN":
            if not resolution or resolution.get("manual_decision") not in {"INCLUDE", "EXCLUDE"}:
                unresolved.append(decision)
                continue
            final = resolution["manual_decision"]
        base = source_index.get(record_id, {})
        metadata = metadata_index.get(record_id, {})
        if metadata and str(metadata.get("candidate_id") or record_id) != str(
            base.get("candidate_id") or record_id
        ):
            raise RuntimeError(f"Full-text candidate metadata mismatch for {record_id}")
        merged_base = {**metadata, **base}
        for field, value in metadata.items():
            if merged_base.get(field) in (None, "", []):
                merged_base[field] = value
        profile = profile_index.get(str(decision.get("candidate_id") or record_id), {})
        row = {
            **merged_base,
            **decision,
            "record_id": record_id,
            "candidate_id": decision.get("candidate_id") or base.get("candidate_id") or record_id,
            "eligibility_decision": final,
            "manual_resolution_applied": bool(resolution),
            "manual_resolution": resolution or {},
            "source_document": profile.get("source_document") or profile.get("source_pdf") or "",
            "source_document_kind": profile.get("source_document_kind") or "pdf",
        }
        for field, value in metadata.items():
            if row.get(field) in (None, "", []):
                row[field] = value
        (accepted if final == "INCLUDE" else excluded).append(row)
    write_json(args.output, {"metadata": {"created": now_iso(), "accepted": len(accepted), "excluded": len(excluded), "unresolved": len(unresolved)}, "records": accepted})
    write_json(args.excluded_output, {"created": now_iso(), "records": excluded})
    write_json(args.unresolved_output, {"created": now_iso(), "records": unresolved})
    if unresolved:
        raise RuntimeError(
            f"{len(unresolved)} full-text UNCERTAIN records require manual_resolution.csv"
        )
    print(json.dumps({"accepted": len(accepted), "excluded": len(excluded), "unresolved": 0}))
    return 0


def apply_section_overrides(args: argparse.Namespace) -> int:
    automatic = records_from(args.input)
    source = records_from(args.source_records)
    source_index = strict_index(source, "record_id", "Manual-section source records")
    metadata = read_json(args.run_metadata)
    excluded = metadata.get("excluded_records", [])
    excluded_ids = {
        str(row.get("record_id") or row.get("candidate_id") or "") for row in excluded
    }
    with args.profile_manifest.open(newline="", encoding="utf-8") as stream:
        profile_rows = [row for row in csv.DictReader(stream) if row.get("profile_status") == "complete"]
    profiles = {str(row.get("candidate_id") or ""): row for row in profile_rows}
    if "" in profiles or len(profiles) != len(profile_rows):
        raise RuntimeError("Profile manifest has duplicate or empty candidate_id")

    override_payload = read_json(args.overrides)
    if isinstance(override_payload, dict) and override_payload.get("schema_version") != 2:
        raise RuntimeError("manual_section_overrides.json must declare schema_version: 2")
    overrides = override_payload.get("records", override_payload)
    if not isinstance(overrides, list):
        raise ValueError("Section overrides must be an array or an object with records[]")
    by_id: dict[str, dict[str, Any]] = {}
    for row in overrides:
        record_id = str(row.get("record_id") or "")
        if not record_id or record_id in by_id:
            raise RuntimeError("Section overrides contain a duplicate or empty record_id")
        by_id[record_id] = row
    missing = sorted(excluded_ids - set(by_id))
    unexpected = sorted(set(by_id) - excluded_ids)
    if missing or unexpected:
        raise RuntimeError(
            f"Section override membership mismatch; missing={missing}, unexpected={unexpected}"
        )

    resolved = []
    audit_records = []
    for record_id in sorted(excluded_ids):
        override = by_id[record_id]
        if "selected_full_text_sections" in override:
            raise RuntimeError(
                f"Manual override {record_id} must not supply selected_full_text_sections; "
                "use canonical section selectors"
            )
        for field in ("rationale", "resolver", "resolved_at", "source_markdown", "source_markdown_sha256"):
            if not str(override.get(field) or "").strip():
                raise RuntimeError(f"Manual override {record_id} has empty {field}")
        try:
            datetime.fromisoformat(str(override["resolved_at"]))
        except ValueError as exc:
            raise RuntimeError(f"Manual override {record_id} has invalid resolved_at") from exc
        base = source_index.get(record_id)
        if not base:
            raise RuntimeError(f"No source record for section override {record_id}")
        candidate_id = str(override.get("candidate_id") or "")
        if candidate_id != str(base.get("candidate_id") or ""):
            raise RuntimeError(f"Manual override candidate_id mismatch for {record_id}")
        profile = profiles.get(candidate_id)
        if not profile:
            raise RuntimeError(f"No complete Docling profile for manual override {record_id}")
        if str(profile.get("source_record_id") or "") != str(base.get("source_record_id") or record_id):
            raise RuntimeError(f"Manual override profile record mismatch for {record_id}")
        markdown = Path(str(profile.get("markdown") or ""))
        if not markdown.is_absolute():
            markdown = ROOT / markdown
        markdown = markdown.resolve()
        declared_markdown = Path(str(override["source_markdown"])).expanduser()
        if not declared_markdown.is_absolute():
            declared_markdown = ROOT / declared_markdown
        if declared_markdown.resolve() != markdown or not markdown.is_file():
            raise RuntimeError(f"Manual override source_markdown mismatch for {record_id}")
        markdown_sha = file_sha256(markdown)
        if str(override["source_markdown_sha256"]).casefold() != markdown_sha:
            raise RuntimeError(f"Manual override source_markdown_sha256 mismatch for {record_id}")
        declarations = override.get("sections")
        if not isinstance(declarations, list) or not declarations:
            raise RuntimeError(f"Manual override {record_id} must declare nonempty sections")
        parsed = parse_markdown_sections_for_derivation(markdown)
        markdown_chars = len(markdown.read_text(encoding="utf-8", errors="replace"))
        heading_count = sum(1 for line in markdown.read_text(encoding="utf-8", errors="replace").splitlines() if re.match(r"^#{1,8}\s+", line))
        chosen: dict[tuple[int, int], dict[str, Any]] = {}
        role_union: set[str] = set()
        for declaration in declarations:
            roles = declaration.get("target_section_types")
            trail = declaration.get("heading_path")
            if not isinstance(roles, list) or not set(roles) or not set(roles) <= {"data_source", "input_representation"}:
                raise RuntimeError(f"Manual override {record_id} has invalid target_section_types")
            if not isinstance(trail, list) or not trail or not all(isinstance(item, str) and item.strip() for item in trail):
                raise RuntimeError(f"Manual override {record_id} has invalid heading_path")
            target_keys = [heading_key(item) for item in trail]
            matches = [
                (section, section_trail)
                for section, section_trail in parsed
                if [heading_key(item) for item in section_trail] == target_keys
            ]
            if len(matches) != 1:
                raise RuntimeError(
                    f"Manual override {record_id} heading_path must resolve exactly once: {trail}"
                )
            section, section_trail = matches[0]
            coverage = len(section.body) / markdown_chars if markdown_chars else 1.0
            if coverage >= 0.90 or (len(section_trail) == 1 and heading_count > 1 and coverage >= 0.80):
                raise RuntimeError(f"Manual override {record_id} selects a document-level section: {trail}")
            key = (section.start_line, section.end_line)
            entry = chosen.setdefault(
                key,
                {
                    "heading_path": section_trail,
                    "heading": section.heading,
                    "line_start": section.start_line,
                    "line_end": section.end_line,
                    "text": section.body,
                    "target_section_types": set(),
                },
            )
            entry["target_section_types"].update(roles)
            role_union.update(roles)
        if role_union != {"data_source", "input_representation"}:
            raise RuntimeError(f"Manual override {record_id} must cover both target section types")
        ordered = sorted(chosen.values(), key=lambda item: (item["line_start"], item["line_end"]))
        section_blocks = []
        audited_sections = []
        for section in ordered:
            roles = sorted(section["target_section_types"])
            heading = " > ".join(section["heading_path"])
            section_blocks.append(f"[{', '.join(roles)}: {heading}]\n{section['text']}")
            audited_sections.append(
                {
                    **{key: section[key] for key in ("heading_path", "heading", "line_start", "line_end")},
                    "target_section_types": roles,
                    "text_sha256": hashlib.sha256(section["text"].encode()).hexdigest(),
                    "text_chars": len(section["text"]),
                }
            )
        sections = "\n\n".join(section_blocks)
        resolved.append(
            {
                "record_id": record_id,
                "candidate_id": base.get("candidate_id") or record_id,
                "source_record_id": base.get("source_record_id") or record_id,
                "source_corpus": base.get("source_corpus", ""),
                "title": base.get("title", ""),
                "abstract": base.get("abstract", ""),
                "selected_full_text_sections": sections,
            }
        )
        excluded_row = next(row for row in excluded if str(row.get("record_id") or row.get("candidate_id") or "") == record_id)
        audit_records.append(
            {
                "record_id": record_id,
                "candidate_id": candidate_id,
                "profile_markdown": str(markdown),
                "source_markdown_sha256": markdown_sha,
                "sections": audited_sections,
                "rationale": override["rationale"],
                "resolver": override["resolver"],
                "resolved_at": override["resolved_at"],
                "graph_failure": excluded_row,
                "validation_status": "validated_canonical_section_selectors",
            }
        )

    merged = [*automatic, *resolved]
    ids = [str(row.get("record_id")) for row in merged]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate record_id after applying section overrides")
    merged.sort(key=lambda row: str(row.get("record_id")))
    write_json(args.output, merged)
    write_json(
        args.audit_output,
        {
            "created": now_iso(),
            "automatic_records": len(automatic),
            "manual_section_overrides": len(resolved),
            "schema_version": 2,
            "records": audit_records,
        },
    )
    print(json.dumps({"automatic": len(automatic), "overrides": len(resolved), "total": len(merged)}))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command", required=True)

    abstract = sub.add_parser("abstract-input")
    abstract.add_argument("--input", type=Path, required=True)
    abstract.add_argument("--output", type=Path, required=True)
    abstract.add_argument("--excluded-output", type=Path, required=True)
    abstract.add_argument("--minimum-chars", type=int, default=50)
    abstract.set_defaults(func=abstract_input)

    fulltext = sub.add_parser("fulltext-candidates")
    fulltext.add_argument("--screening-results", type=Path, required=True)
    fulltext.add_argument("--screening-input", type=Path, required=True)
    fulltext.add_argument("--record-id-crosswalk", type=Path)
    fulltext.add_argument("--canonical-input", type=Path)
    fulltext.add_argument("--duplicate-resolutions", type=Path)
    fulltext.add_argument("--output", type=Path, required=True)
    fulltext.set_defaults(func=fulltext_candidates)

    downloads = sub.add_parser("consolidate-downloads")
    downloads.add_argument("--manifest", type=Path, action="append", required=True)
    downloads.add_argument("--manual-manifest", type=Path)
    downloads.add_argument("--output", type=Path, required=True)
    downloads.set_defaults(func=consolidate_downloads)

    config = sub.add_parser("docling-config")
    config.add_argument("--records", type=Path, required=True)
    config.add_argument("--download-manifest", type=Path, required=True)
    config.add_argument("--output", type=Path, required=True)
    config.add_argument("--missing-output", type=Path, required=True)
    config.add_argument("--profile-root", type=Path, required=True)
    config.add_argument("--name", required=True)
    config.add_argument("--vlm", action="store_true")
    config.add_argument("--openai-base-url", default="http://127.0.0.1:8765/v1/chat/completions")
    config.add_argument("--vlm-model", default="gpt-5.5")
    config.add_argument("--vlm-timeout", type=int, default=600)
    config.add_argument("--vlm-concurrency", type=int, default=1)
    config.add_argument("--max-workers", type=int, default=1)
    config.add_argument(
        "--picture-prompt",
        default=(
            "Classify this extracted image as SCIENTIFIC_FIGURE or NON_SCIENTIFIC_IMAGE. "
            "For a scientific figure, describe visible panels, labels, biological source "
            "objects, transformations, model interfaces, and findings precisely for retrieval. "
            "Do not invent details."
        ),
    )
    config.set_defaults(func=docling_config)

    accepted = sub.add_parser("accepted-records")
    accepted.add_argument("--screening-results", type=Path, required=True)
    accepted.add_argument("--screening-input", type=Path, required=True)
    accepted.add_argument("--source-records", type=Path)
    accepted.add_argument("--profile-manifest", type=Path, required=True)
    accepted.add_argument("--manual-resolution", type=Path)
    accepted.add_argument("--output", type=Path, required=True)
    accepted.add_argument("--excluded-output", type=Path, required=True)
    accepted.add_argument("--unresolved-output", type=Path, required=True)
    accepted.set_defaults(func=accepted_records)

    overrides = sub.add_parser("apply-section-overrides")
    overrides.add_argument("--input", type=Path, required=True)
    overrides.add_argument("--source-records", type=Path, required=True)
    overrides.add_argument("--run-metadata", type=Path, required=True)
    overrides.add_argument("--profile-manifest", type=Path, required=True)
    overrides.add_argument("--overrides", type=Path, required=True)
    overrides.add_argument("--output", type=Path, required=True)
    overrides.add_argument("--audit-output", type=Path, required=True)
    overrides.set_defaults(func=apply_section_overrides)
    return root


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
