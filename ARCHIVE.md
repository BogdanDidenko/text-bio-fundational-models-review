# Archive of removed run folders

## 2026-10-15: superseded, failed, pilot and unrelated units

On 2026-10-15 the units below were removed from the working tree because no current result, site page,
configuration or check needs them: they are superseded runs, failed or invalidated attempts, pilots, or
material unrelated to the review. Before removal, every group was removed in a scratch worktree and the
CI checks were run (living-review contract tests, method lock, library check and tests, input-path test,
`run_living_review_pipeline.py doctor --repository-checkout`, amendment check). All passed with the same
doctor stage states as before. The paper-1 build scripts (`build_prisma_flow.py`,
`build_operation_synthesis.py`, `build_integrated_dataset.py`, `build_design_culture_synthesis.py`,
`build_design_culture_figures.py`, `build_motif_library.py`, `build_design_taxonomy.py`) gave the same
outputs with and without the removed units; only the creation dates embedded in PDF and SVG files differed.
Nothing was rewritten in Git history: every file is still available from the tag
`archive/pre-cleanup-2026-10-15` (commit e77be5dd).

Removed: 191 paths, 509.0 MB, 8563 tracked files.

### Restore

```bash
git fetch origin tag archive/pre-cleanup-2026-10-15
git restore --source archive/pre-cleanup-2026-10-15 -- <path>
```

Browse without restoring: `git show archive/pre-cleanup-2026-10-15:<path>` or
https://github.com/BogdanDidenko/text-bio-fundational-models-review/tree/archive/pre-cleanup-2026-10-15

### Kept on purpose

- `analysis/operation_decomposition_v31_2026-10-12/` (releases 1.2.0/1.2.1), although superseded: its
  parameter pass supplies the parameter slots carried into release 1.3.0, and `scripts/run_parameter_pass.py`
  and `scripts/build_chain_table.py` read it.
- Frozen catalog releases 1.0.0 to 1.2.1 in `analysis/representation_block_library_2026-10-04/releases/`:
  tests and scripts read them.
- The conference abstract packages `data/health_intelligence_conference_2026_*` (a separate deliverable).

### Removed groups

#### Superseded decomposition runs (2706 files, 86.0 MB)

Superseded decomposition runs (listed under "Superseded" in `CURRENT_STATE.md`): release 1.1.0 records and corpus files (protocol v1), the v1 run-to-run replicate study, protocol-development iterations `v2_i1`, `v3_i1` and `v3_h3diag`, and the protocol v3.1 source runs `v3_i8`, `v3_h4` and `v31_rest30` of releases 1.2.0/1.2.1. Release 1.3.0 is built from `v32_all` and `v32_h4`, which are kept.

| Path | MB | Files |
|---|---:|---:|
| `analysis/operation_decomposition_2026-10-07/records` | 52.97 | 2097 |
| `analysis/operation_decomposition_2026-10-07/corpus_assemblies.json` | 9.05 | 1 |
| `analysis/operation_decomposition_2026-10-07/STEWARD_QUEUE.md` | 0.06 | 1 |
| `analysis/operation_decomposition_2026-10-07/corpus_status.json` | 0.09 | 1 |
| `analysis/operation_decomposition_2026-10-07/replicates` | 0.02 | 1 |
| `analysis/operation_decomposition_2026-10-07/stabilization/v2_i1` | 0.00 | 1 |
| `analysis/operation_decomposition_2026-10-07/stabilization/v3_i1` | 0.00 | 1 |
| `analysis/operation_decomposition_2026-10-07/stabilization/v3_h3diag` | 4.24 | 56 |
| `analysis/operation_decomposition_2026-10-07/stabilization/v3_i8` | 2.49 | 92 |
| `analysis/operation_decomposition_2026-10-07/stabilization/v3_h4` | 6.04 | 183 |
| `analysis/operation_decomposition_2026-10-07/stabilization/v31_rest30` | 11.03 | 272 |

#### Withdrawn analyses and replaced figures (14 files, 1.4 MB)

Withdrawn or replaced analyses and figures: the exact-chain diversity analysis (`chain_profile_*`, `motif_table.csv`), the earlier Figures 3, 4 and 5 (`operation_reuse.png`, `figure4_design_patterns.*`, `figure5_motif_library.*`) and the keyword pre-screens of the discovery dossier (`prescreen_*`, `scan_*.md`).

| Path | MB | Files |
|---|---:|---:|
| `analysis/design_taxonomy_2026-10-13/chain_profile_exploratory.png` | 0.05 | 1 |
| `analysis/design_taxonomy_2026-10-13/chain_profile_summary.json` | 0.00 | 1 |
| `analysis/design_taxonomy_2026-10-13/motif_table.csv` | 0.00 | 1 |
| `analysis/design_taxonomy_2026-10-13/figure4_design_patterns.png` | 0.39 | 1 |
| `analysis/design_taxonomy_2026-10-13/figure4_design_patterns.pdf` | 0.09 | 1 |
| `analysis/review_synthesis_2026-10-07/operation_reuse.png` | 0.23 | 1 |
| `analysis/motif_library_2026-10-14/figure5_motif_library.png` | 0.26 | 1 |
| `analysis/motif_library_2026-10-14/figure5_motif_library.pdf` | 0.08 | 1 |
| `analysis/discovery_2026-10-14/prescreen_controls_llm.json` | 0.02 | 1 |
| `analysis/discovery_2026-10-14/prescreen_synthetic_text_llm.json` | 0.01 | 1 |
| `analysis/discovery_2026-10-14/scan_gene_budget.md` | 0.01 | 1 |
| `analysis/discovery_2026-10-14/scan_input_controls.md` | 0.10 | 1 |
| `analysis/discovery_2026-10-14/scan_synthetic_text.md` | 0.16 | 1 |
| `analysis/discovery_2026-10-14/scan_token_budget.md` | 0.01 | 1 |

#### Failed taxonomy runs (2026-07-11) (355 files, 53.3 MB)

Failed runs of the 2026-07-11 taxonomy (pilots, smoke tests, a run with a logging-serialization fault and an unstructured synthesis attempt). No result was taken from them.

| Path | MB | Files |
|---|---:|---:|
| `data/input_representation_taxonomy_2026-07-11/runs/failed_adjudication_smoke_pre_timeout_fix` | 0.44 | 3 |
| `data/input_representation_taxonomy_2026-07-11/runs/failed_adjudication_smoke_quote_selection` | 0.40 | 3 |
| `data/input_representation_taxonomy_2026-07-11/runs/failed_discovery_open_r1_logging_serialization` | 2.02 | 40 |
| `data/input_representation_taxonomy_2026-07-11/runs/failed_pilot_free_extraction` | 39.72 | 272 |
| `data/input_representation_taxonomy_2026-07-11/runs/failed_pilot_quote_gate` | 9.03 | 36 |
| `data/input_representation_taxonomy_2026-07-11/failed_synthesis_r1_unstructured` | 1.74 | 1 |

#### Failed attempts inside the 2026-08-09 update (283 files, 17.0 MB)

Failed or invalidated attempts inside the 2026-08-09 update: the abstract screening invalidated with the configurable runner, the failed complete-batch full-text retries and the failed taxonomy v2. The accepted stage outputs of the update are kept; the doctor check reports the same stage states as before.

| Path | MB | Files |
|---|---:|---:|
| `data/living_catalog_updates/update_2026-08-09/04_abstract_screening_invalidated_configurable_runner_2026-08-10` | 2.50 | 113 |
| `data/living_catalog_updates/update_2026-08-09/09_fulltext_screening_failed_complete_batch_retries_2026-08-11` | 3.02 | 58 |
| `data/living_catalog_updates/update_2026-08-09/12_taxonomy_failed_v2_2026-08-11` | 11.48 | 112 |

#### Failed crop retry (27 files, 0.2 MB)

A failed crop retry attempt in the full-cohort rerun; the accepted crops are in `crops_final/`.

| Path | MB | Files |
|---|---:|---:|
| `data/living_catalog/taxonomy_rerun_preflight_2026-08-12/crops_retry_model_699b7d92d927_attempt_02` | 0.15 | 26 |
| `data/living_catalog/taxonomy_rerun_preflight_2026-08-12/crops_retry_model_699b7d92d927_attempt_02.log` | 0.00 | 1 |

#### Charting pilot and unrelated material (11 files, 0.1 MB)

The pilot of the design-culture charting pass (replaced by `v11/`) and material unrelated to the review: the UNESCO AI Lab application documents and the script that built them.

| Path | MB | Files |
|---|---:|---:|
| `analysis/design_culture_charting_2026-10-14/pilot` | 0.05 | 5 |
| `analysis/design_culture_charting_2026-10-14/pilot_records.json` | 0.00 | 1 |
| `data/unesco_application` | 0.08 | 4 |
| `scripts/build_unesco_application_docs.py` | 0.02 | 1 |

#### Superseded baseline taxonomy runs (2026-07-11) (1738 files, 272.5 MB)

Raw classification and adjudication runs of the 2026-07-11 baseline taxonomy (fixed-taxonomy replicates r1-r3, dense coverage, adjudication shards and their logs). The full-cohort rerun of 2026-08-12 (`data/living_catalog/taxonomy_rerun_preflight_2026-08-12/taxonomy/`) repeated discovery, classification, dense coverage and adjudication for all 55 records and supersedes them. Kept from the baseline: the method-locked taxonomy tree, the codebook, the open-discovery run, the synthesis and the root files that serve as the pipeline's fallback state.

| Path | MB | Files |
|---|---:|---:|
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage` | 140.14 | 690 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1` | 24.06 | 179 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2` | 25.32 | 171 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3` | 25.29 | 171 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_resume_shard_00.log` | 0.01 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_resume_shard_01.log` | 0.01 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_resume_shard_02.log` | 0.01 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_resume_shard_03.log` | 0.03 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_resume_shard_04.log` | 0.01 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_resume_shard_05.log` | 0.03 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_resume_shard_06.log` | 0.01 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_resume_shard_07.log` | 0.02 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_shard_00.log` | 0.03 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_shard_01.log` | 0.06 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_shard_02.log` | 0.04 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage_shard_03.log` | 0.02 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_parallel_v1_000.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_parallel_v1_001.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_parallel_v1_002.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_parallel_v1_003.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_parallel_v1_004.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_parallel_v1_005.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_parallel_v1_006.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_parallel_v1_007.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_parallel_v1_008.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_parallel_v1_009.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_parallel_v1_010.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_retry_001200.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_shard_00.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_shard_01.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_shard_02.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_shard_03.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_validator_v1_1_rec000090.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1_validator_v1_2_rec000090.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_parallel_v1_011.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_parallel_v1_012.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_parallel_v1_013.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_parallel_v1_014.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_parallel_v1_015.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_parallel_v1_016.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_parallel_v1_017.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_parallel_v1_018.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_parallel_v1_019.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_parallel_v1_020.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_shard_00.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_shard_01.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_shard_02.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_shard_03.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_validator_v1_1_rec000090.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2_validator_v1_2_rec000090.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_parallel_v1_021.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_parallel_v1_022.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_parallel_v1_023.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_parallel_v1_024.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_parallel_v1_025.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_parallel_v1_026.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_parallel_v1_027.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_parallel_v1_028.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_parallel_v1_029.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_retry_000090.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_shard_00.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_shard_01.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_shard_02.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_shard_03.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_validator_v1_1_rec000090.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3_validator_v1_2_rec000090.log` | 0.00 | 1 |
| `data/input_representation_taxonomy_2026-07-11/adjudication` | 57.39 | 396 |
| `data/input_representation_taxonomy_2026-07-11/adjudication_*.log` (69 logs) | 0.01 | 69 |

#### Superseded compact full-text screening (2026-07-09) (3346 files, 57.0 MB)

The superseded compact full-text screening of 2026-07-09 and its compact context. Kept: `data/screening_codex_fulltext_2026-07-09/input_records.json`, the base record list of the current 2026-07-10 full-text screening.

| Path | MB | Files |
|---|---:|---:|
| `data/screening_codex_fulltext_2026-07-09/AUDIT.md` | 0.01 | 1 |
| `data/screening_codex_fulltext_2026-07-09/adjudication_queue.json` | 1.29 | 1 |
| `data/screening_codex_fulltext_2026-07-09/adjudicator.jsonl` | 0.09 | 1 |
| `data/screening_codex_fulltext_2026-07-09/architecture_reviewer.jsonl` | 0.43 | 1 |
| `data/screening_codex_fulltext_2026-07-09/final_screening_results.csv` | 0.15 | 1 |
| `data/screening_codex_fulltext_2026-07-09/final_screening_results.json` | 0.27 | 1 |
| `data/screening_codex_fulltext_2026-07-09/python_gate_outputs.json` | 0.83 | 1 |
| `data/screening_codex_fulltext_2026-07-09/role_logs` | 48.50 | 3324 |
| `data/screening_codex_fulltext_2026-07-09/run_metadata.json` | 0.00 | 1 |
| `data/screening_codex_fulltext_2026-07-09/schemas` | 0.01 | 3 |
| `data/screening_codex_fulltext_2026-07-09/scope_reviewer.jsonl` | 0.22 | 1 |
| `data/screening_codex_fulltext_2026-07-09/section_input_stats` | 0.47 | 6 |
| `data/screening_codex_fulltext_2026-07-09/summary.json` | 0.00 | 1 |
| `data/fulltext_screening_context_2026-07-09_compact_v2` | 4.77 | 3 |

#### Staged atlas copy (83 files, 21.4 MB)

The pre-publication atlas build of the 2026-08-17 semantic correction. The deployed atlas is `docs/input-representation-atlas/`; no file refers to the staged copy.

| Path | MB | Files |
|---|---:|---:|
| `data/living_catalog/taxonomy_rerun_preflight_2026-08-12/atlas_semantic_correction_2026-08-17` | 21.40 | 83 |

### Reference updates

- `scripts/build_operation_synthesis.py` pointed the steward queue at the review rounds of release 1.1.0;
  it now names the records of the run it reads (`analysis/operation_decomposition_v32_2026-10-14/records/`),
  and `STEWARD_QUEUE.md` there was regenerated.
- `manuscript/review_manuscript_draft.md`: Table S3 now points to the current steward queue
  (`analysis/operation_decomposition_v32_2026-10-14/STEWARD_QUEUE.md`).
- `data/screening_codex_fulltext_2026-07-09/README.md` and the README of
  `analysis/operation_decomposition_2026-10-07/` say what was removed; `CURRENT_STATE.md` and `README.md`
  name the tag.

## 2026-10-14: unreferenced units

On 2026-10-14 the units below were removed from the working tree because no code, configuration, site
page or current document depends on them. Apart from archived agent logs (stdout, stderr and event logs
of earlier runs), only two kept files named any of them, a README and a `.gitignore` rule; both were
updated (see "Reference updates").
Nothing was rewritten in Git history: every file is still available from the tag
`archive/pre-cleanup-2026-10-14` (commit a9506e67).

Removed: 21 units, 514.9 MB, 515 tracked files.

### Restore

One unit:

```bash
git fetch origin tag archive/pre-cleanup-2026-10-14
git restore --source archive/pre-cleanup-2026-10-14 -- <path>
```

Everything:

```bash
git restore --source archive/pre-cleanup-2026-10-14 -- \
  analysis/atlas_exact_preview_revalidation_after_f6_2026-08-17 \
  analysis/cross_agent_screening_agreement_current_3ds_2gpt \
  analysis/current_full_deepseek_replicate_agreement \
  analysis/fulltext_uncertain_disagreement_current_llm_20260512 \
  analysis/git_branch_reconciliation_2026-08-15.md \
  analysis/living_review_runbook_subagent_audit_2026-08-12.md \
  analysis/living_review_update_postmortem_2026-08-12.md \
  analysis/run_configuration_inventory_20260512 \
  analysis/screening_reproducibility_consensus_metrics.csv \
  analysis/screening_reproducibility_pairwise_metrics.csv \
  analysis/screening_run_artifacts_after_prompt_update_20260511 \
  analysis/taxonomy_agent_trace_audit_2026-08-14.json \
  analysis/taxonomy_agent_trace_audit_2026-08-14.md \
  data/determinism_codex_2026-07-01 \
  data/living_review_runbook_agent_audit_2026-08-16 \
  data/living_review_runbook_agent_audit_2026-08-18 \
  data/living_review_runbook_agent_audit_2026-08-18_postfix \
  recovery/project_recovery_2026-07-29 \
  runs/deepseek_v4_review_pipeline_all4027_foundation_metadata_rerun_watchdog \
  runs/fulltext_uncertain_disagreement_current5_20260512 \
  runs/nemotron3_super_120b_fp8_review_pipeline_all4027_current_rep2_watchdog_20260511T2040Z
```

Browse without restoring: `git show archive/pre-cleanup-2026-10-14:<path>` or
https://github.com/BogdanDidenko/text-bio-fundational-models-review/tree/archive/pre-cleanup-2026-10-14

### Removed units

| Unit | MB | Files | Mentioned in archived agent logs |
|---|---:|---:|---:|
| `analysis/atlas_exact_preview_revalidation_after_f6_2026-08-17` | 0.34 | 41 | 0 |
| `analysis/cross_agent_screening_agreement_current_3ds_2gpt` | 2.00 | 11 | 26 |
| `analysis/current_full_deepseek_replicate_agreement` | 2.30 | 3 | 7 |
| `analysis/fulltext_uncertain_disagreement_current_llm_20260512` | 25.05 | 14 | 20 |
| `analysis/git_branch_reconciliation_2026-08-15.md` | 0.00 | 1 | 0 |
| `analysis/living_review_runbook_subagent_audit_2026-08-12.md` | 0.01 | 1 | 3 |
| `analysis/living_review_update_postmortem_2026-08-12.md` | 0.01 | 1 | 3 |
| `analysis/run_configuration_inventory_20260512` | 0.05 | 5 | 2 |
| `analysis/screening_reproducibility_consensus_metrics.csv` | 0.00 | 1 | 3 |
| `analysis/screening_reproducibility_pairwise_metrics.csv` | 0.00 | 1 | 2 |
| `analysis/screening_run_artifacts_after_prompt_update_20260511` | 412.93 | 356 | 35 |
| `analysis/taxonomy_agent_trace_audit_2026-08-14.json` | 0.03 | 1 | 0 |
| `analysis/taxonomy_agent_trace_audit_2026-08-14.md` | 0.02 | 1 | 0 |
| `data/determinism_codex_2026-07-01` | 0.06 | 5 | 15 |
| `data/living_review_runbook_agent_audit_2026-08-16` | 0.14 | 9 | 0 |
| `data/living_review_runbook_agent_audit_2026-08-18` | 0.05 | 5 | 0 |
| `data/living_review_runbook_agent_audit_2026-08-18_postfix` | 0.06 | 6 | 0 |
| `recovery/project_recovery_2026-07-29` | 0.04 | 8 | 1 |
| `runs/deepseek_v4_review_pipeline_all4027_foundation_metadata_rerun_watchdog` | 4.28 | 2 | 6 |
| `runs/fulltext_uncertain_disagreement_current5_20260512` | 27.35 | 15 | 31 |
| `runs/nemotron3_super_120b_fp8_review_pipeline_all4027_current_rep2_watchdog_20260511T2040Z` | 40.21 | 28 | 16 |

### Kept on purpose

Three files that no code refers to were kept because they document the search iterations:
`data/search_log_2026-02-06.md` (v3.0 search log), `data/deduplicated_records_v31.json` (baseline
deduplicated set) and `data/records_for_screening.ris` (baseline screening set). Seven other
candidates were kept because current files refer to them: the conference abstract package
`data/health_intelligence_conference_2026_abstract_2026-07-11_v2` and the six
`data/docling_uncertain_*_2026-07-08` folders.

### Reference updates

- `analysis/codex_screening_run_artifacts_20260706/README.md` now names the tag for
  `analysis/screening_run_artifacts_after_prompt_update_20260511`.
- `.gitignore`: the rule for `analysis/atlas_exact_preview_revalidation_after_f6_2026-08-17/review_panels/`
  was removed with the folder.
