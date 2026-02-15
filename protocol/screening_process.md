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

| Metric | Value |
|---|---|
| Missing before enrichment | 577 (16.2%) |
| Recovered via API (S2, CrossRef, PubMed) | +393 |
| Excluded (no abstract after all steps) | 184 (5.2%) |
| **Records for screening** | **3,371** |

Script: [scripts/enrich_abstracts.py](../scripts/enrich_abstracts.py)

### Search update history

| Version | Date | Changes | Total for screening |
|---------|------|---------|---------------------|
| v3.0 | 2026-02-06 | Initial search across 7 databases | 3,228 |
| v3.1 | 2026-02-15 | Added space variants: "RNA seq", "multi omics" (were missing without hyphens) | 3,371 |

## Output

Deduplication + enrichment output:
- `data/deduplicated_records.json` — 3,371 records with abstracts, ready for screening
- `data/excluded_no_abstract.json` — 184 records excluded for missing abstract (audit trail)
- `data/deduplication_log.csv` — every merge decision with action, reason, and cluster ID
- `data/deduplication_stats.json` — summary statistics
- `data/enrichment_log.json` — abstract enrichment details per record

Screening results logged to `data/screening_log.csv` with columns:
- record_id, database_source, doi, title, phase1_decision, phase1_code, phase2_decision, phase2_code, notes
