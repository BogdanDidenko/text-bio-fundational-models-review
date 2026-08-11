"""Conservative metadata corroboration for title-based retrieval fallbacks."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

from deduplicate import normalize_title


def record_year(record: dict[str, Any]) -> int | None:
    value = str(record.get("year") or record.get("date") or "")
    match = re.search(r"\b(19|20)\d{2}\b", value)
    return int(match.group()) if match else None


def author_surnames(value: Any) -> set[str]:
    if isinstance(value, list):
        values = [
            str(item.get("family") or item.get("name") or item)
            if isinstance(item, dict)
            else str(item)
            for item in value
        ]
    else:
        values = re.split(r"[;,]", str(value or ""))
    surnames: set[str] = set()
    for value in values:
        tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ'’-]+", value.lower())
        if tokens:
            surnames.add(tokens[-1])
    return surnames


def accept_title_candidate(
    record: dict[str, Any], candidate: dict[str, Any], minimum_title_similarity: float = 0.92
) -> tuple[bool, str, dict[str, Any]]:
    """Accept a title search result only with independent metadata corroboration."""
    source_title = str(record.get("title") or record.get("title_original") or "")
    candidate_title = str(candidate.get("title") or "")
    left, right = normalize_title(source_title), normalize_title(candidate_title)
    similarity = SequenceMatcher(None, left, right).ratio() if left and right else 0.0
    exact_title = bool(left and left == right)
    evidence: dict[str, Any] = {
        "source_title": source_title,
        "candidate_title": candidate_title,
        "title_similarity": round(similarity, 6),
        "exact_normalized_title": exact_title,
    }
    if similarity < minimum_title_similarity:
        return False, "below_title_similarity_threshold", evidence

    source_year, candidate_year = record_year(record), candidate.get("year")
    try:
        candidate_year = int(candidate_year) if candidate_year not in (None, "") else None
    except (TypeError, ValueError):
        candidate_year = None
    year_checked = source_year is not None and candidate_year is not None
    year_agrees = year_checked and abs(source_year - candidate_year) <= 1
    evidence.update(
        {
            "source_year": source_year,
            "candidate_year": candidate_year,
            "year_agrees_within_one_year": year_agrees,
        }
    )
    if year_checked and not year_agrees:
        return False, "year_conflict", evidence

    source_authors = author_surnames(record.get("authors"))
    candidate_authors = author_surnames(candidate.get("authors"))
    authors_checked = bool(source_authors and candidate_authors)
    author_overlap = sorted(source_authors & candidate_authors)
    evidence.update(
        {
            "source_author_surnames": sorted(source_authors),
            "candidate_author_surnames": sorted(candidate_authors),
            "author_overlap": author_overlap,
        }
    )
    if authors_checked and not author_overlap:
        return False, "author_conflict", evidence
    if not (year_agrees or author_overlap):
        return False, "insufficient_independent_corroboration", evidence
    return True, "accepted_title_match", evidence
