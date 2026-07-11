# Input-Representation Taxonomy Artifacts

This directory contains the post-eligibility taxonomy of model input routes for
the 52 accepted records. Canonical Docling profiles are read-only inputs and are
not copied or modified here.

## Denominators

- Accepted screening records: 52
- Primary study units after exact-PDF deduplication: 51
- Sensitivity study units if the OmniNA version pair is linked: 50

## Final validated result

- Models: 111
- Task/input configurations: 376
- Accepted grounded input routes: 489
- Dense coverage candidates dispositioned: 2,208/2,208
- Dense-only accepted candidates: 21
- Minimum pairwise route-detection Jaccard: 0.948
- Carrier-family exact agreement: 0.925
- Carrier-family Krippendorff alpha: 0.875
- Prespecified acceptance checks: passed

## Main artifacts

- `study_model_registry.csv`: record-to-study registry; model IDs are finalized after extraction.
- `registry_summary.json`: duplicate/version accounting.
- `taxonomy_synthesis/`: independent proposals, adjudication, prompts, and frozen taxonomy.
- `runs/`: open discovery, failed pilots retained for audit, three fixed-candidate
  direct classifications, and dense Docling Graph coverage artifacts.
- `adjudication/`: blinded per-record route reconciliation.
- `route_annotations.jsonl` and `.csv`: final accepted input routes.
- `route_candidates_all.jsonl`: accepted and explicitly excluded non-input candidates.
- `evidence_ledger.jsonl`: page/item/quote provenance for accepted routes.
- `uncertainty_cases.jsonl`: unresolved, weakly grounded, figure-only, or schema-conflict cases.
- `adjudication_resolution_manifest.csv`: the selected successful adjudication
  artifact and SHA-256 for every record, plus any superseded successful retries.
- `special_cases.jsonl` and `special_cases_report.md`: explicit duplicate,
  version-linkage, figure-only, lifecycle/input-status, and unmatched-candidate audit.
- `agreement_metrics.json` and `agreement_report.md`: prespecified validation results.
- `manuscript_methods.md`, `manuscript_taxonomy_tables.md`, and
  `failure_mode_report.md`: manuscript-ready reporting outputs.
- `logging_timestamp_audit.md` and `validator_change_audit.md`: transparent
  run-time methodology amendments and their scope.

The methodological protocol is `protocol/input_representation_taxonomy_2026-07-11.md`.
