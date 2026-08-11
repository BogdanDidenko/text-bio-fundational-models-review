# Search Boundary Audit

**Run:** `update_2026-08-09`  
**Interval:** 2026-07-07 through 2026-08-09 (inclusive)  
**Boundary under test:** database query execution -> normalized source exports -> within-update deduplication

## Canonical status

The canonical eight-source search is **complete but unpublished**. All configured
source and pagination contracts passed. The search boundary may feed canonical
within-update deduplication, but the living-review date boundary advances only
after the complete run is reviewed and explicitly published.

| Source | Retained records | Completion evidence |
|---|---:|---|
| PubMed | 27 | API count and parsed export agree |
| Scopus | 16 | 501/501 year-filtered records fetched; 485 were outside the exact interval |
| OpenAlex | 100 | both scoped cursor queries reached API-reported counts |
| Semantic Scholar | 183 | both bulk-query pagination paths completed |
| arXiv | 14 | all four configured subqueries completed |
| Europe PMC bioRxiv/medRxiv | 20 | fetched count equals `hitCount` |
| SpringerNature | 27 | Meta 691/691 and OA 327/327 fetched before three-block validation |
| Google Scholar via SerpAPI | 252 | one combined query, 13 hashed raw pages, terminated at `no_next_page` |
| **Total before deduplication** | **639** | search summary reports `complete: true` |

Within-update deduplication produced 514 clusters and removed 125 duplicates:
103 DOI matches, 8 arXiv-ID matches, and 14 exact-title matches. Six exact-title
records with conflicting non-preprint DOIs were conservatively kept separate and
written to `01_dedup/deduplication_review_queue.json`.

The earlier seven-query Scholar capture is preserved as
`google_scholar_provider_export_seven_query_diagnostic.json`, with its summary
and `1,101 -> 957` deduplication under `diagnostic_seven_query_serpapi/`; these
are not canonical inputs. Cumulative matching removed 227 previously known records. Crossref then
queried 97 DOI-less candidates, enriched 53 DOI values with independent year or
author corroboration, removed two hidden duplicates, and produced 285 new records.

## Earlier diagnostic execution (superseded)

Before credentials and the provider export were restored, the partial diagnostic
package was stored in
`00_search/diagnostic_available_sources/core_api_v2/`. It intentionally requests
only three sources and therefore does not represent the canonical seven-source
update.

| Source | Protocol-complete | Fetched | Evidence |
|---|---:|---:|---|
| PubMed | yes | 27/27 | ESearch count equals parsed EFetch count |
| arXiv | yes | 14 unique | all four configured subqueries reached a natural pagination end |
| Europe PMC bioRxiv/medRxiv | yes | 20/20 | fetched count equals `hitCount` |

The three-source diagnostic deduplication is stored in
`01_dedup/diagnostic_partial_sources_v2/`: 61 source records became 60 exact
clusters, with one DOI merge, no missing abstracts, 14 records without DOI, and
no identifier-conflict rows. These counts are diagnostic only.

The cumulative diagnostic is stored in
`02_records/diagnostic_partial_sources_v4/`. Of the 60 clusters, 8 matched the
published master (3 by DOI and 5 by exact title/version evidence) and 52 remained
potentially new. Crossref queried 13 DOI-less candidates, added 2 DOI values only
after year or author corroboration, and found no additional hidden duplicate.

## Failures found and controls added

1. Every source export now carries `execution.complete`, status, reason, and
   pagination/query-level diagnostics. The search command exits non-zero if any
   requested source is incomplete.
2. PubMed count agreement, Europe PMC `hitCount` agreement, arXiv and Semantic
   Scholar subquery completion, both SpringerNature interface completions, and
   Google Scholar query completion are explicit invariants.
3. Semantic Scholar now uses a paced, five-attempt request controller with
   `Retry-After` support. It writes raw response pages, hashes, continuation
   tokens, query membership, and a non-secret checkpoint before advancing a
   page; a partial checkpoint cannot become a dedup export.
4. Google Scholar direct scraping remains diagnostic only. Canonical updates
   require a provider-mediated capture with exactly the signed configured query set,
   a review-interval-specific signature, and locally verifiable raw-response
   hashes. The template and contract are versioned in
   `protocol/google_scholar_provider_export_schema.md`.
5. Scopus and Semantic Scholar exact-date post-filtering now labels exact,
   out-of-range, missing, year-only, and unparseable dates. Uncertain-date records
   are retained for recall but remain visible; confirmed out-of-range records are
   separated.
6. Historical ground-truth model checks are disabled for incremental intervals;
   absence of an old model in a one-month update is not a search failure.
7. Deduplication validates the upstream search summary, expected source set,
   per-export completion, and source counts before reading records.
8. Date status and source-query provenance survive normalization and clustering.
   Conflicting published DOIs with an identical normalized title are kept
   separate and written to `deduplication_review_queue.json`; preprint/published
   title links remain permitted.
9. Set-derived DOI and identifier choices are sorted, removing output
   nondeterminism.
10. Cumulative exact-title matches now stop on ambiguous master titles or
   conflicting published DOIs. Research Square (`10.21203/rs.`) and openRxiv
   (`10.64898/`) were verified as `posted-content` preprint DOI families and are
   handled as version links. Unknown conflicts require a signed manual resolution.
11. Crossref title similarity alone no longer assigns a DOI. The title threshold
    must be accompanied by a compatible publication year or overlapping author
    surname; conflicts and insufficient corroboration remain visible in the audit.
12. Abstract title-search fallbacks now use the same independent corroboration
    rule. Accepted abstract replacements record candidate metadata and matching
    evidence; rejected candidates are logged without importing text. A bounded
    abstract-fetch probe cannot exclude records that it never attempted.
13. Full-text title-search discovery no longer follows a title-similarity-only
    candidate. The same corroboration rule records every accepted or rejected
    candidate before a document URL can be attempted.
14. The full-text-to-Docling handoff validates PDF signature/size and HTML
    body-text thresholds for automatic and manual payloads, preventing landing
    pages from becoming screening evidence.

## Protocol caveats retained

- Google Scholar supplies year-level candidates only. Exact interval membership
  depends on metadata and cumulative deduplication.
- PubMed retains the historical free-full-text query restriction. This is a
  protocol design choice and must remain visible in search reporting.
- SpringerNature uses broad retrieval followed by the historical three-block
  title/abstract validation. Raw and validated counts must both be retained.
- Records with uncertain source dates are recall candidates, not proven
  interval-dated records.

## Conditions for canonical continuation

Search, within-update deduplication, cumulative matching, the Crossref audit, and
abstract enrichment are complete. All 285 new records have usable abstracts; the
next boundary is title/abstract agent screening.
