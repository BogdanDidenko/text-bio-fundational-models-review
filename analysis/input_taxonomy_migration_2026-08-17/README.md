# Taxonomy migration ledger

This directory compares the original 52-record taxonomy with the corrected
55-record full-cohort classification. It addresses cross-version interpretability;
it does not modify either canonical input and does not invoke an LLM.

## Denominators

- Shared records: 52.
- Old routes in those records: 489.
- Current routes in those records: 549.
- Net route change: +60.
- Current-only records/routes: 3/37.
- Accepted conservative primary route links: 279.
- Mapped old/current models: 86/85.
- Mapped old/current configurations: 242/232.

## Interpretation contract

Study identity is compared exactly. Model and configuration ledgers preserve stable
IDs and aggregate support from accepted route links. Route IDs are regenerated
content hashes, so route lineage is estimated conservatively from controlled taxonomy
fields and normalized text. Maximum-weight assignment prevents a convenient new route
from being used as the primary match for several old routes. Low-scoring assignments
are not forced; top alternative candidates remain in `route_candidate_edges.csv` so
possible split/merge cases are visible.

The automated ledger establishes where versions are stable, reworded, structurally
changed, added, consolidated, or ambiguous. It cannot determine which annotation is
scientifically preferable and must not be reported as human validation.

## Reproduce

```bash
.venv-docling/bin/python scripts/build_taxonomy_migration_ledger.py \
  --created-at 2026-08-17T00:00:00+03:00 --force
```

## Files

- `study_migration.csv`: exact record/study continuity, including three new records.
- `model_migration.csv`: stable and route-supported model mappings.
- `configuration_migration.csv`: stable and route-supported configuration mappings.
- `route_migration.csv`: accepted primary links plus all unmatched routes.
- `route_candidate_edges.csv`: scored alternatives and split/merge degrees.
- `record_summary.csv`: per-record denominators and family/model changes.
- `record_review_packets.jsonl`: complete compact route evidence for manual review.
- `priority_review.md`: largest absolute count changes.
- `migration_summary.json`: source hashes, algorithm, thresholds, and aggregate counts.

See `largest_delta_review.md` for the separate analyst review of the largest changes.
