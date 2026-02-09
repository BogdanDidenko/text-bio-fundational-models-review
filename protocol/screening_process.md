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

1. **Primary**: Match by DOI (exact)
2. **Secondary**: Fuzzy title matching (Levenshtein distance < 5 or cosine similarity > 0.95)
3. **Tertiary**: First author + year + first 5 title words
4. **Preprint-to-publication**: If both preprint and published version exist, keep the published version but note the preprint DOI

## Output

All screening results logged to `data/logs/screening_log.csv` with columns:
- record_id, database_source, doi, title, phase1_decision, phase1_code, phase2_decision, phase2_code, notes
