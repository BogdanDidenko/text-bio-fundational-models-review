# Full-Cohort Taxonomy and Atlas Rerun

This directory contains the auditable whole-cohort rerun prepared on
2026-08-12 through 2026-08-14. The validated snapshot and atlas supersede the
prior published taxonomy output without altering its immutable artifacts.

## Cohort and Docling evidence

- Canonical denominator: 55 records representing 54 studies.
- Canonical profile manifest: `canonical_docling_profile_manifest.csv`.
- All 55 records have complete native Docling JSON, Markdown, source-document
  hashes, figure manifests, and VLM-enriched picture descriptions.
- The regenerated 52-record baseline contains 506 extracted images: 453
  scientific figures and 53 non-scientific images. The combined 55-record
  manifest exposes 577 figure/image items.
- The baseline picture-description backend was the local OpenAI-compatible
  Codex wrapper over `gpt-5.5`; historical update profiles retain their logged
  original enrichment metadata.

## Docling Graph and taxonomy

- Open discovery: 55/55 records, 595 grounded route candidates.
- Direct classification: three complete `gpt-5.4-mini` replicates at
  temperature 0, with no configured text, token, or context truncation.
- Dense coverage: standard Docling Graph scoped fill and deduplication over
  all 55 profiles; 768-token chunks and a 1,536-token batch budget are Graph
  traversal units, not document truncation.
- Adjudication: a blinded fourth `gpt-5.4-mini` invocation reconciled all three
  direct replicates, discovery inventory, dense coverage, and canonical
  documents. Failed responses and point retries remain in `taxonomy/adjudication/`.
- Final taxonomy: 109 models, 468 configurations, and 586 grounded input
  routes. No accepted route lacks canonical text or native-item provenance.
- Agreement: minimum pairwise Jaccard 0.937, carrier-family exact agreement
  0.925, and nominal Krippendorff alpha 0.881.
- Dense audit: 2,893/2,893 candidates explicitly dispositioned; 68 yielded
  dense-only accepted evidence. Two candidates remain explicitly reasoned
  `unresolved` cases rather than being forced into a category.

Canonical taxonomy outputs are in `taxonomy/`. The acceptance decision and all
thresholds are in `taxonomy/agreement_metrics.json`.

## Figures, crops, and atlas

- Crop validation covered 109/109 models using two blind selectors, an
  adjudicator, and a cropper over native Docling source figures.
- Final crop dispositions: 98 validated source-figure crops and 11 explicit
  `no_suitable_figure` decisions. One invalid route-reference response was
  rejected and rerun under the same contract.
- The canonical combined crop ledger is `crops_final/crop_ledger.json`.
- `snapshot_full_55/` is an immutable full-cohort snapshot, not an incremental
  merge. It hashes every referenced Docling profile and source document.
- `atlas/` is the retained pre-publication UI build. Browser QA passed at 1440x1000
  and 390x844 with 109 model nodes, 47 exact-membership groups, 267 rendered
  edges, 196 crop viewports, zero node overlaps, zero horizontal overflow, and
  zero console errors.

The deployable copy is `docs/input-representation-atlas/`; living-review state
and the atlas both point to `snapshot_full_55/`.

## Important operational findings

- Large full-document adjudication calls can exceed 60 minutes. The successful
  repair wrapper used a 14,400-second transport timeout without adding content
  or output limits.
- A stopped HTTP client can leave a wrapper-owned `codex exec` child running;
  orphan processes must be audited before a retry.
- The atlas builder consumes actual corpus `figures/` directories and expects
  an existing UI shell. A combined manifest alone is insufficient for atlas
  asset discovery.
- `unresolved` is a transparent adjudication state. It counts as accounted
  only when both a reason and uncertainty explanation are present.
