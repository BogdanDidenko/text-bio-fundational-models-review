# Screening Process

## Overview

Two-phase screening aligned to the formal protocol in
[eligibility_criteria.md](eligibility_criteria.md).

The title/abstract phase is now implemented as a **criterion-by-criterion,
sensitivity-first** workflow:

- `scope_reviewer`
- `architecture_reviewer`
- Python gate logic
- `adjudicator` only for unresolved or criterion-conflict cases

The title/abstract phase is intentionally conservative. `UNCERTAIN` is a valid
state and should preserve records for further review rather than force early
exclusion.

## Phase 1: Title/Abstract Screening

### Criterion logic

Apply the decision logic from [eligibility_criteria.md](eligibility_criteria.md)
through the current workflow:

1. Does the record work with biological data?  
   `NO -> EXCLUDE (EC1)`
2. Does it contain a **substantive** text/language component as part of the
   candidate model?  
   `NO -> EXCLUDE (EC2)`
3. Does it show a substantive text-bio bridge rather than a wrapper around an
   existing model?  
   `NO -> EXCLUDE (EC2/EC4)`
4. Is the model generative rather than encoder-only or purely predictive?  
   `NO -> EXCLUDE (EC3)`
5. Does it show foundation-model evidence?  
   `NO -> EXCLUDE (EC4)`
6. Is it a primary research paper/preprint rather than review/editorial,
   benchmark/resource, or application-wrapper paper?  
   `NO -> EXCLUDE (EC6/EC7/EC4 depending on failure mode)`
7. If one or more decisive criteria remain unresolved at title/abstract stage:  
   `-> UNCERTAIN`

### Metadata checks during phase 1

The following are protocol-level inclusion requirements but may be implemented
as metadata filters or downstream checks rather than semantic prompt questions:

- date range (`IC6`)
- language (`IC7`)
- Open Access / full-text availability (`IC8`)

### Output of phase 1

For each record, produce:

- `INCLUDE`
- `EXCLUDE` with exclusion code
- `UNCERTAIN` with uncertainty reason

`UNCERTAIN` records proceed to phase 2.

## Phase 2: Targeted Full-Text Evidence Screening

For records marked `INCLUDE` or `UNCERTAIN` in phase 1:

1. obtain and convert full text with Docling;
2. use Docling Graph provenance to locate `data_source` and
   `input_representation` evidence and reconstruct the complete bounded source
   sections;
3. reject document-level or duplicate evidence sections and require both target
   types before this machine-assisted pass;
4. verify that the text/language role is substantive rather than incidental;
5. verify that any claimed text-bio bridge is actually supported by the paper;
6. verify generative architecture and foundation-model evidence from the
   selected methods/model evidence;
7. confirm publication type, duplication status, language, OA/full-text status,
   and computational contribution where phase-1 evidence was weak.

The reviewer prompt receives title, abstract, and complete selected sections,
not raw PDFs or whole-document markdown. Structured Docling provenance remains
in the audit artifact but is not duplicated in the reviewer input. The executed
2026-07-10 run, input quality controls, log layout, and counts are documented
in [full_text_section_screening_2026-07-10.md](full_text_section_screening_2026-07-10.md).

## Exclusion Code Use In Screening

| Code | Reason | Typical phase |
|------|--------|---------------|
| `EC1` | No biological data modality | 1 or 2 |
| `EC2` | No substantive text/language component | 1 or 2 |
| `EC3` | Encoder-only / non-generative architecture | 1 or 2 |
| `EC4` | No foundation-model component / wrapper-only logic | 1 or 2 |
| `EC5` | Non-computational | 1 or 2 |
| `EC6` | Non-scholarly source | 1 |
| `EC7` | Review article / non-primary literature | 1 |
| `EC8` | Duplicate publication | 1 or 2 |

`IC6-IC8` may also trigger exclusion at metadata/full-text validation if the
record falls outside date range, language, or OA/full-text requirements.

## Deduplication Strategy

Conservative exact-matching approach (no fuzzy matching to avoid accidental removals):

1. **Normalization**: DOI (strip URL prefix, lowercase), arXiv ID (strip version suffix), title (NFC unicode, lowercase, strip punctuation, collapse whitespace)
2. **Exact DOI matching**: Normalized DOI comparison
3. **Exact PMID matching**: For records with PubMed IDs (available from PubMed, Semantic Scholar, EuropePMC)
4. **Exact arXiv ID matching**: Normalized arXiv ID comparison (available from arXiv, Semantic Scholar)
5. **Exact normalized title matching**: After full title normalization
6. **Preprint→published linking**: If a cluster contains both a preprint DOI (10.1101/*, 10.48550/arXiv.*) and a publisher DOI, the published version is kept as representative and the preprint DOI is noted

Records are added in metadata-quality order (PubMed → Scopus → S2 → bioRxiv → SN → arXiv → GS), so the representative record in each cluster has the best available metadata.

### Deduplication Results (2026-02-15 data, query v3.1)

| Metric | Value |
|---|---|
| Records before dedup | 5,534 |
| Unique records after dedup | 3,555 |
| Duplicates removed | 1,979 (35.8%) |
| DOI matches | 1,486 |
| Exact title matches | 345 |
| PMID matches | 34 |
| arXiv ID matches | 114 |
| Preprint→published links | 91 |

Script: [scripts/deduplicate.py](../scripts/deduplicate.py)

### Abstract Enrichment and Exclusion

After deduplication, many records (primarily from Scopus Search API which does not return abstracts) lacked abstracts. A two-step enrichment + exclusion pipeline ensures all records entering screening have abstracts for reliable LLM-based classification:

1. **Cluster-level abstract selection**: During dedup, the longest abstract from any record in a duplicate cluster is kept (not just the representative's abstract). This recovers abstracts from lower-priority sources in the same cluster.
2. **API enrichment**: For remaining records without abstracts, fetch from Semantic Scholar (by DOI), CrossRef (by DOI), PubMed Entrez (by PMID), and S2 title search (fallback).
3. **Exclusion**: Records still lacking an abstract after enrichment are excluded with code `EC_NO_ABSTRACT` and saved to a separate audit file.

| Metric | v3.1 (2026-02-15) | Update (2026-04-14) |
|---|---|---|
| Missing before enrichment | 577 (16.2%) | 41 of 668 new records |
| Recovered via API (S2, CrossRef, PubMed) | +393 | +29 |
| Excluded (no abstract after all steps) | 184 (5.2%) | 12 |
| **Records for screening** | **3,371** | **+656 new → 4,027 total** |

A second enrichment pass also replaced 335 truncated Google Scholar snippet
abstracts with full abstracts via CrossRef/S2 title search and stripped HTML
tags from 211 records. After this pass, 88.3% of the 4,027 screening records
have full abstracts (≥250 chars).

Scripts:
- [scripts/enrich_abstracts.py](../scripts/enrich_abstracts.py) — enrichment
  for records with no abstract (drops below the EC_NO_ABSTRACT bar)
- [scripts/enrich_short_abstracts.py](../scripts/enrich_short_abstracts.py) —
  enrichment for records with short snippet-style abstracts

### Search update history

| Version | Date | Changes | Total for screening |
|---------|------|---------|---------------------|
| v3.0 | 2026-02-06 | Initial search across 7 databases | 3,228 |
| v3.1 | 2026-02-15 | Added space variants: "RNA seq", "multi omics" (were missing without hyphens) | 3,371 |
| update | 2026-04-14 | Top-up search 2026-03-01 → 2026-04-14 across 7 DBs; +668 new records after cross-dedup; short-abstract enrichment | 4,027 |

## Output

Deduplication + enrichment output:
- `data/deduplicated_records.json` — 4,027 records with abstracts, ready for screening
- `data/excluded_no_abstract.json` — records excluded for missing abstract (audit trail)
- `data/deduplication_log.csv` — every merge decision with action, reason, and cluster ID
- `data/deduplication_stats.json` — summary statistics
- `data/enrichment_log.json` — abstract enrichment details per record

Screening results logged to `data/screening_log.csv` with columns such as:
- `record_id`
- `doi`
- `title`
- `phase1_decision`
- `phase1_code`
- `phase1_uncertainty_reason`
- `phase2_decision`
- `phase2_code`
- `notes`
