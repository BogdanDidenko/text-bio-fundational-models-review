# XunZi incremental input-representation taxonomy run

This directory contains the complete incremental taxonomy audit for:

- record: `update_2026-08-09__manual_recall_xunzi`;
- title: *XunZi, an AI biologist, reveals disease-modifying targets*;
- DOI: `10.1038/s41551-026-01769-6`;
- canonical VLM Docling markdown SHA-256:
  `08b674c84f6fd8c474d89913990e1d0db0890e419b10f1e8cd4a4781dc912515`.

## Run sequence

1. Open direct Docling Graph discovery produced 13 raw candidates. Twelve were
   carried into fixed classification after the provenance gate.
2. Three independent fixed-candidate direct classifications used
   `gpt-5.4-mini`, temperature 0, prompt version `v3-interface-boundary`, and no
   configured context or output cap. They accepted 9, 10, and 10 final routes.
3. Standard Docling Graph dense coverage used scoped fill and standard
   deduplication. It produced 96 grounded provisional candidates; 61 failed the
   deterministic eligibility gate before LLM adjudication.
4. A separate blinded `gpt-5.4-mini` adjudicator accounted for all remaining
   candidates and produced 14 grounded final routes, including three valid
   dense-only routes.
5. The protocol analyzer generated the route tables, evidence ledger,
   agreement metrics, uncertainty ledger, and failure-mode report.

## Acceptance disposition

The one-record diagnostic analyzer reports a minimum pairwise Jaccard of
`0.750`. This is retained as a sensitivity result, but it is not the
prespecified corpus-level acceptance test: a single candidate-reference
disagreement has disproportionate weight when the denominator is one paper.

- minimum pairwise route-detection Jaccard: `0.750` (required `>= 0.80`);
- carrier-family exact agreement: `1.0`;
- carrier-family Krippendorff alpha: `1.0`;
- final grounded routes: `14/14`;
- dense candidates explicitly accounted for: `96/96`;
- unresolved dense candidates: `0`.

The one-record Jaccard result reflects route-granularity disagreement: replicates
differed in whether aggregate multi-omics discovery candidates and their
pan-cancer/neurodegenerative configuration-specific children were retained as
supporting candidate references. Carrier-family coding was otherwise
identical.

No prompt, schema, taxonomy, or historical annotation was changed. When this
record is appended to the frozen 52-record baseline and the two other records
from the 2026-08-09 update, the route-detection Jaccards are `0.960`, `0.945`,
and `0.969`; the aggregate minimum remains above the prespecified `0.80`
threshold. The 14 grounded adjudicated routes are therefore eligible for the
versioned cumulative snapshot. Aggregate metrics, rather than the standalone
one-record `acceptance_passed` field, govern integration.

## Principal artifacts

- `taxonomy_synthesis/open_route_inventory.json`: grounded discovery inventory;
- `runs/classification_fixed_r1` through `r3`: independent direct runs and logs;
- `runs/classification_dense`: complete dense coverage run and Graph artifacts;
- `adjudication/`: blinded reconciliation input, response, and dispositions;
- `route_annotations.jsonl`: 14 adjudicated route records;
- `evidence_ledger.jsonl`: route-level canonical provenance;
- `agreement_metrics.json` and `agreement_report.md`: acceptance checks;
- `failure_mode_report.md` and `uncertainty_cases.jsonl`: retained limitations.

No hidden chain-of-thought is stored or claimed. Logs contain prompts, schemas,
model/configuration metadata, responses, errors, retries, and provenance.
