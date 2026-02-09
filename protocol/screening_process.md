# Screening Process

## Overview
Two-phase screening following PRISMA 2020 guidelines.

## Phase 1: Title/Abstract Screening

Apply the decision tree from [eligibility_criteria.md](eligibility_criteria.md):

1. Is it about single-cell data? (NO -> EC1)
2. Does it involve 2+ modalities? (NO -> EC2, note if FM)
3. Does it have FM characteristics? (NO -> EC3)
4. Is it a primary research article/preprint? (NO -> EC5/EC6)
5. Is it in English? (NO -> EC8)

**Action**: Mark each record as INCLUDE, EXCLUDE (with code), or UNCERTAIN.
UNCERTAIN records proceed to Phase 2.

## Phase 2: Full-Text Screening

For records marked INCLUDE or UNCERTAIN in Phase 1:
1. Obtain full text (OA requirement — EC9 if not available)
2. Verify multi-modal integration (IC2)
3. Verify FM characteristics (IC3) — pretraining >100K cells, transferable
4. Check for duplicate publications (EC7) — keep most recent/peer-reviewed version
5. Confirm computational contribution (EC4)

## Exclusion Codes

| Code | Reason | Phase |
|------|--------|-------|
| EC1 | Not single-cell data | 1 |
| EC2 | Single-modality only | 1 or 2 |
| EC3 | No foundation model component | 1 or 2 |
| EC4 | Non-computational | 1 or 2 |
| EC5 | Non-scholarly source | 1 |
| EC6 | Review article | 1 |
| EC7 | Duplicate publication | 2 |
| EC8 | Not English | 1 |
| EC9 | Not Open Access | 2 |

## Deduplication Strategy

Conservative exact-matching approach (no fuzzy matching to avoid accidental removals):

1. **Normalization**: DOI (strip URL prefix, lowercase), arXiv ID (strip version suffix), title (NFC unicode, lowercase, strip punctuation, collapse whitespace)
2. **Exact DOI matching**: Normalized DOI comparison
3. **Exact PMID matching**: For records with PubMed IDs (available from PubMed, Semantic Scholar, EuropePMC)
4. **Exact arXiv ID matching**: Normalized arXiv ID comparison (available from arXiv, Semantic Scholar)
5. **Exact normalized title matching**: After full title normalization
6. **Preprint→published linking**: If a cluster contains both a preprint DOI (10.1101/*, 10.48550/arXiv.*) and a publisher DOI, the published version is kept as representative and the preprint DOI is noted

Records are added in metadata-quality order (PubMed → Scopus → S2 → bioRxiv → SN → arXiv → GS), so the representative record in each cluster has the best available metadata.

### Deduplication Results (2026-02-06 data)

| Metric | Value |
|---|---|
| Records before dedup | 5,271 |
| Unique records after dedup | 3,407 |
| Duplicates removed | 1,864 (35.4%) |
| DOI matches | 1,047 |
| Exact title matches | 651 |
| PMID matches | 89 |
| arXiv ID matches | 77 |
| Preprint→published links | 146 |

Script: [scripts/deduplicate.py](../scripts/deduplicate.py)

## Output

Deduplication output:
- `data/deduplicated_records.json` — unique records with source tracking and cluster metadata
- `data/deduplication_log.csv` — every merge decision with action, reason, and cluster ID
- `data/deduplication_stats.json` — summary statistics

Screening results logged to `data/screening_log.csv` with columns:
- record_id, database_source, doi, title, phase1_decision, phase1_code, phase2_decision, phase2_code, notes
