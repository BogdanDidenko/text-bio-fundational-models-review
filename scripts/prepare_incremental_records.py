#!/usr/bin/env python3
"""Cross-deduplicate a search update and audit DOI-less records with Crossref."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import requests

from deduplicate import is_preprint_doi, normalize_arxiv_id, normalize_doi, normalize_title


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return payload["records"]
    if isinstance(payload, list):
        return payload
    raise ValueError(f"Unsupported record artifact: {path}")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record_dois(record: dict[str, Any]) -> set[str]:
    values: list[Any] = [record.get("doi"), record.get("doi_normalized"), record.get("preprint_doi")]
    values.extend(record.get("all_dois") or [])
    return {value for item in values if (value := normalize_doi(str(item or "")))}


def record_title(record: dict[str, Any]) -> str:
    return str(record.get("title") or record.get("title_original") or "").strip()


def record_pmid(record: dict[str, Any]) -> str:
    return str(record.get("pmid") or "").strip()


def record_arxiv(record: dict[str, Any]) -> str:
    return normalize_arxiv_id(
        str(record.get("arxiv_id") or record.get("arxiv_id_normalized") or "")
    )


def record_year(record: dict[str, Any]) -> int | None:
    match = re.search(r"\b(19|20)\d{2}\b", str(record.get("year") or record.get("date") or ""))
    return int(match.group()) if match else None


def author_surnames(value: Any) -> set[str]:
    if isinstance(value, list):
        parts = [
            str(item.get("family") or item.get("name") or item)
            if isinstance(item, dict)
            else str(item)
            for item in value
        ]
    else:
        parts = re.split(r"[;,]", str(value or ""))
    surnames = set()
    for part in parts:
        tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ'’-]+", part.lower())
        if tokens:
            surnames.add(tokens[-1])
    return surnames


class MasterIndex:
    def __init__(self, records: list[dict[str, Any]]) -> None:
        self.doi: dict[str, dict[str, Any]] = {}
        self.pmid: dict[str, dict[str, Any]] = {}
        self.arxiv: dict[str, dict[str, Any]] = {}
        self.title: dict[str, list[dict[str, Any]]] = {}
        self.review_queue: list[dict[str, Any]] = []
        for record in records:
            for doi in record_dois(record):
                self.doi.setdefault(doi, record)
            if pmid := record_pmid(record):
                self.pmid.setdefault(pmid, record)
            if arxiv := record_arxiv(record):
                self.arxiv.setdefault(arxiv, record)
            if title := normalize_title(record_title(record)):
                self.title.setdefault(title, []).append(record)

    def match(self, record: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
        for doi in sorted(record_dois(record)):
            if doi in self.doi:
                return self.doi[doi], f"DOI match: {doi}"
        if (pmid := record_pmid(record)) and pmid in self.pmid:
            return self.pmid[pmid], f"PMID match: {pmid}"
        if (arxiv := record_arxiv(record)) and arxiv in self.arxiv:
            return self.arxiv[arxiv], f"arXiv ID match: {arxiv}"
        title = normalize_title(record_title(record))
        if title and title in self.title:
            candidates = self.title[title]
            if len(candidates) != 1:
                self.review_queue.append(
                    {
                        "reason": "exact title matches multiple master records",
                        "update": master_ref(record),
                        "master_candidates": [master_ref(item) for item in candidates],
                        "automatic_action": "kept_as_new_pending_review",
                    }
                )
                return None, ""
            candidate = candidates[0]
            update_dois = record_dois(record)
            master_dois = record_dois(candidate)
            if update_dois and master_dois and update_dois.isdisjoint(master_dois):
                version_pair = all(
                    is_preprint_doi(update_doi) != is_preprint_doi(master_doi)
                    for update_doi in update_dois
                    for master_doi in master_dois
                )
                if not version_pair:
                    self.review_queue.append(
                        {
                            "reason": "exact title but conflicting published DOIs",
                            "update": master_ref(record),
                            "master_candidates": [master_ref(candidate)],
                            "automatic_action": "kept_as_new_pending_review",
                        }
                    )
                    return None, ""
                return candidate, "Exact title match: preprint/published version link"
            return candidate, "Exact title match"
        return None, ""


def master_ref(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": record.get("record_id"),
        "cluster_id": record.get("cluster_id"),
        "title": record_title(record),
        "doi": record.get("doi") or record.get("doi_normalized") or "",
    }


def crossref_lookup(
    session: requests.Session, title: str, email: str, retries: int = 3
) -> dict[str, Any] | None:
    headers = {
        "User-Agent": f"lpnu-living-review/1.0 (mailto:{email})",
        "Accept": "application/json",
    }
    params = {"query.bibliographic": title[:500], "rows": 5, "mailto": email}
    for attempt in range(retries):
        try:
            response = session.get(
                "https://api.crossref.org/works",
                params=params,
                headers=headers,
                timeout=45,
            )
            if response.status_code == 429:
                time.sleep(2**attempt)
                continue
            response.raise_for_status()
            items = (response.json().get("message") or {}).get("items") or []
            best: dict[str, Any] | None = None
            for item in items:
                candidate_title = " ".join(item.get("title") or [])
                left = normalize_title(title)
                right = normalize_title(candidate_title)
                score = SequenceMatcher(None, left, right).ratio() if left and right else 0.0
                if best is None or score > best["score"]:
                    best = {
                        "score": round(score, 6),
                        "title": candidate_title,
                        "doi": normalize_doi(str(item.get("DOI") or "")),
                        "type": item.get("type"),
                        "publisher": item.get("publisher"),
                        "year": next(
                            (
                                parts[0][0]
                                for key in ("published-print", "published-online", "issued")
                                if (parts := (item.get(key) or {}).get("date-parts"))
                                and parts[0]
                            ),
                            None,
                        ),
                        "authors": [
                            " ".join(
                                part
                                for part in (author.get("given", ""), author.get("family", ""))
                                if part
                            )
                            for author in (item.get("author") or [])
                        ],
                    }
            return best
        except requests.RequestException:
            if attempt + 1 == retries:
                return None
            time.sleep(2**attempt)
    return None


def crossref_acceptance(record, best, title_threshold):
    """Require title similarity plus independent year or author corroboration."""
    if not best:
        return False, "no_crossref_match", {}
    if best.get("score", 0.0) < title_threshold:
        return False, "below_title_threshold", {}
    if not best.get("doi"):
        return False, "crossref_match_without_doi", {}

    source_year = record_year(record)
    candidate_year = best.get("year")
    year_checked = source_year is not None and candidate_year is not None
    year_agrees = year_checked and abs(source_year - int(candidate_year)) <= 1
    if year_checked and not year_agrees:
        return False, "crossref_year_conflict", {
            "source_year": source_year,
            "candidate_year": candidate_year,
        }

    source_authors = author_surnames(record.get("authors"))
    candidate_authors = author_surnames(best.get("authors"))
    authors_checked = bool(source_authors and candidate_authors)
    author_overlap = sorted(source_authors & candidate_authors)
    if authors_checked and not author_overlap:
        return False, "crossref_author_conflict", {
            "source_author_surnames": sorted(source_authors),
            "candidate_author_surnames": sorted(candidate_authors),
        }
    corroborated = year_agrees or bool(author_overlap)
    evidence = {
        "source_year": source_year,
        "candidate_year": candidate_year,
        "author_overlap": author_overlap,
    }
    if not corroborated:
        return False, "crossref_insufficient_corroboration", evidence
    return True, "accepted_title_match", evidence


def assign_ids(records: list[dict[str, Any]], run_id: str) -> list[dict[str, Any]]:
    assigned = []
    for index, source in enumerate(records, start=1):
        record = dict(source)
        source_record_id = f"rec_{index:06d}"
        record.update(
            {
                "record_id": f"{run_id}__{source_record_id}",
                "candidate_id": f"{run_id}__{source_record_id}",
                "source_record_id": source_record_id,
                "source_run": run_id,
                "source_corpus": run_id,
            }
        )
        assigned.append(record)
    return assigned


def apply_cross_dedup_resolutions(new_records, matches, review_queue, path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("records", []) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("Manual cumulative dedup resolutions must be records[]")
    queue_ids = {
        str((item.get("update") or {}).get("cluster_id") or "")
        for item in review_queue
    }
    if "" in queue_ids:
        raise ValueError("Cumulative dedup review queue contains an empty cluster_id")
    by_cluster: dict[str, dict[str, Any]] = {}
    for row in rows:
        cluster_id = str(row.get("update_cluster_id") or "")
        if not cluster_id or cluster_id in by_cluster:
            raise ValueError(
                "Manual cumulative dedup resolutions have duplicate or empty update_cluster_id"
            )
        if cluster_id not in queue_ids:
            raise ValueError(
                f"Manual cumulative dedup resolution is not in the review queue: {cluster_id}"
            )
        decision = str(row.get("decision") or "")
        if decision not in {"keep_new", "exclude_as_duplicate"}:
            raise ValueError(f"Invalid cumulative dedup decision for cluster {cluster_id}")
        for field in ("rationale", "resolver", "resolved_at"):
            if not str(row.get(field) or "").strip():
                raise ValueError(f"Resolution {cluster_id} requires {field}")
        try:
            datetime.fromisoformat(str(row["resolved_at"]))
        except ValueError as exc:
            raise ValueError(f"Resolution {cluster_id} has invalid resolved_at") from exc
        by_cluster[cluster_id] = row
    unresolved = []
    kept = list(new_records)
    for item in review_queue:
        cluster_id = str((item.get("update") or {}).get("cluster_id"))
        resolution = by_cluster.get(cluster_id)
        if not resolution:
            unresolved.append(cluster_id)
            continue
        decision = resolution["decision"]
        item["resolution"] = resolution
        if decision == "exclude_as_duplicate":
            kept = [row for row in kept if str(row.get("cluster_id")) != cluster_id]
            matches.append(
                {
                    "update_cluster_id": cluster_id,
                    "update_title": (item.get("update") or {}).get("title", ""),
                    "update_doi": (item.get("update") or {}).get("doi", ""),
                    "reason": "Manual cumulative duplicate resolution",
                    "master": resolution.get("master") or (
                        (item.get("master_candidates") or [{}])[0]
                    ),
                    "manual_resolution": resolution,
                }
            )
    if unresolved:
        raise ValueError(
            "Missing cumulative dedup resolutions for clusters: " + ", ".join(unresolved)
        )
    return kept, matches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-records", type=Path, required=True)
    parser.add_argument("--master-records", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--crossref", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--crossref-title-threshold", type=float, default=0.88)
    parser.add_argument("--email", default="bohdan.didenko.asp.2025@lpnu.ua")
    parser.add_argument("--sleep", type=float, default=0.1)
    parser.add_argument("--manual-cross-dedup-resolutions", type=Path)
    args = parser.parse_args()

    update_records = read_records(args.update_records)
    master_records: list[dict[str, Any]] = []
    master_sources = []
    for path in args.master_records:
        rows = read_records(path)
        master_records.extend(rows)
        master_sources.append({"path": str(path), "records": len(rows)})
    index = MasterIndex(master_records)

    new_records = []
    matches = []
    reasons: Counter[str] = Counter()
    for record in update_records:
        matched, reason = index.match(record)
        if matched is None:
            new_records.append(dict(record))
            continue
        reason_type = reason.split(":", 1)[0]
        reasons[reason_type] += 1
        matches.append(
            {
                "update_cluster_id": record.get("cluster_id"),
                "update_title": record_title(record),
                "update_doi": record.get("doi", ""),
                "reason": reason,
                "master": master_ref(matched),
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    review_path = args.output_dir / "cross_dedup_review_queue.json"
    if index.review_queue:
        write_json(
            review_path,
            {
                "created": now_iso(),
                "count": len(index.review_queue),
                "records": index.review_queue,
            },
        )
        if not args.manual_cross_dedup_resolutions:
            print(
                json.dumps(
                    {
                        "status": "manual_resolution_required",
                        "review_queue": str(review_path),
                        "count": len(index.review_queue),
                    }
                )
            )
            return 3
        new_records, matches = apply_cross_dedup_resolutions(
            new_records,
            matches,
            index.review_queue,
            args.manual_cross_dedup_resolutions,
        )
    else:
        write_json(
            review_path,
            {"created": now_iso(), "count": 0, "records": []},
        )

    crossref_audit = []
    hidden_duplicates = []
    checked_records = []
    update_doi_owners: dict[str, dict[str, Any]] = {}
    for record in new_records:
        for doi in record_dois(record):
            update_doi_owners.setdefault(doi, record)
    session = requests.Session()
    for index_no, record in enumerate(new_records, start=1):
        row = dict(record)
        audit = {
            "update_cluster_id": row.get("cluster_id"),
            "title": record_title(row),
            "doi_before": row.get("doi", ""),
            "queried": False,
            "status": "existing_doi_not_queried" if record_dois(row) else "not_queried",
        }
        if args.crossref and not record_dois(row) and record_title(row):
            audit["queried"] = True
            best = crossref_lookup(session, record_title(row), args.email)
            audit["best_match"] = best
            accepted, status, corroboration = crossref_acceptance(
                row, best, args.crossref_title_threshold
            )
            audit["status"] = status
            audit["corroboration"] = corroboration
            if accepted:
                doi = best["doi"]
                audit["doi_after"] = doi
                if doi in index.doi:
                    audit["status"] = "hidden_master_duplicate"
                    audit["master"] = master_ref(index.doi[doi])
                    hidden_duplicates.append({**audit, "record": row})
                    crossref_audit.append(audit)
                    continue
                if doi in update_doi_owners and update_doi_owners[doi] is not record:
                    audit["status"] = "hidden_update_duplicate"
                    audit["update_match"] = master_ref(update_doi_owners[doi])
                    hidden_duplicates.append({**audit, "record": row})
                    crossref_audit.append(audit)
                    continue
                row["doi"] = doi
                row["doi_enriched_from"] = "crossref_title"
                row["doi_enrichment_title_score"] = best["score"]
                row["doi_enrichment_corroboration"] = corroboration
                update_doi_owners.setdefault(doi, record)
            if args.sleep:
                time.sleep(args.sleep)
        checked_records.append(row)
        crossref_audit.append(audit)

    assigned = assign_ids(checked_records, args.run_id)
    write_json(args.output_dir / "cross_dedup_matches.json", matches)
    write_json(
        review_path,
        {
            "created": now_iso(),
            "count": len(index.review_queue),
            "records": index.review_queue,
            "all_resolved": all("resolution" in row for row in index.review_queue),
        },
    )
    write_json(
        args.output_dir / "cross_dedup_stats.json",
        {
            "created": now_iso(),
            "new_update_unique_records": len(update_records),
            "master_records_loaded": len(master_records),
            "truly_new_after_cross_dedup": len(new_records),
            "already_in_master": len(matches),
            "cross_dedup_match_reasons": dict(reasons),
            "title_conflicts_kept_for_review": len(index.review_queue),
            "master_sources": master_sources,
            "matching_strategy": (
                "Exact cumulative cross-dedup by DOI/all_dois -> PMID -> arXiv ID "
                "-> normalized title"
            ),
        },
    )
    write_json(args.output_dir / "crossref_duplicate_audit.json", crossref_audit)
    write_json(
        args.output_dir / "new_records_after_cross_dedup_crossref_checked.json",
        {
            "metadata": {
                "created": now_iso(),
                "run_id": args.run_id,
                "source_update_records": str(args.update_records),
                "records_before_crossref_audit": len(new_records),
                "hidden_duplicates_removed_by_crossref": len(hidden_duplicates),
                "records_after_crossref_audit": len(assigned),
                "crossref_title_threshold": args.crossref_title_threshold,
            },
            "records": assigned,
        },
    )
    write_json(
        args.output_dir / "crossref_checked_stats.json",
        {
            "created": now_iso(),
            "truly_new_before_crossref_audit": len(new_records),
            "hidden_duplicates_removed_by_crossref": len(hidden_duplicates),
            "hidden_master_duplicates_removed_by_crossref": sum(
                row.get("status") == "hidden_master_duplicate" for row in crossref_audit
            ),
            "hidden_within_update_duplicates_removed_by_crossref": sum(
                row.get("status") == "hidden_update_duplicate" for row in crossref_audit
            ),
            "truly_new_after_crossref_audit": len(assigned),
            "crossref_doi_enriched": sum(
                bool(row.get("doi_enriched_from")) for row in assigned
            ),
            "crossref_queries": sum(bool(row["queried"]) for row in crossref_audit),
        },
    )
    hidden_csv = args.output_dir / "crossref_hidden_duplicates.csv"
    with hidden_csv.open("w", newline="", encoding="utf-8") as stream:
        fields = [
            "update_cluster_id", "title", "doi_before", "doi_after", "status",
            "master", "update_match",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for item in hidden_duplicates:
            writer.writerow({key: json.dumps(item.get(key), ensure_ascii=False) if isinstance(item.get(key), dict) else item.get(key, "") for key in fields})

    print(
        json.dumps(
            {
                "update_unique": len(update_records),
                "already_in_master": len(matches),
                "hidden_crossref_duplicates": len(hidden_duplicates),
                "new_records": len(assigned),
                "output_dir": str(args.output_dir),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
