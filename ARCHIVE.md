# Archive of removed run folders

On 2026-10-14 the units below were removed from the working tree because no code, configuration, site
page or current document depends on them. Apart from archived agent logs (stdout, stderr and event logs
of earlier runs), only two kept files named any of them, a README and a `.gitignore` rule; both were
updated (see "Reference updates").
Nothing was rewritten in Git history: every file is still available from the tag
`archive/pre-cleanup-2026-10-14` (commit a9506e67).

Removed: 21 units, 514.9 MB, 515 tracked files.

## Restore

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

## Removed units

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

## Kept on purpose

Three files that no code refers to were kept because they document the search iterations:
`data/search_log_2026-02-06.md` (v3.0 search log), `data/deduplicated_records_v31.json` (baseline
deduplicated set) and `data/records_for_screening.ris` (baseline screening set). Seven other
candidates were kept because current files refer to them: the conference abstract package
`data/health_intelligence_conference_2026_abstract_2026-07-11_v2` and the six
`data/docling_uncertain_*_2026-07-08` folders.

## Reference updates

- `analysis/codex_screening_run_artifacts_20260706/README.md` now names the tag for
  `analysis/screening_run_artifacts_after_prompt_update_20260511`.
- `.gitignore`: the rule for `analysis/atlas_exact_preview_revalidation_after_f6_2026-08-17/review_panels/`
  was removed with the folder.
