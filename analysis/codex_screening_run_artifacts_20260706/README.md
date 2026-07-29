# Codex Screening Run Artifacts (2026-07-06)

This directory contains a curated, Git-safe artifact bundle for the July 2026
Codex `gpt-5.4-mini` screening runs. It follows the same repository pattern as
`analysis/screening_run_artifacts_after_prompt_update_20260511`: compact run
directories, operative prompt/config copies, and a SHA-256 manifest instead of
an unstructured dump of the whole local `data/` tree.

## Contents

- `full_runs/codex_gpt54mini_all4027_20260706/`: full 4,027-record title/abstract rerun.
- `update_runs/codex_gpt54mini_update431_20260610/`: June update cohort run.
- `update_runs/codex_gpt54mini_update155_20260706/`: July update cohort run.
- `inputs/`: June and July 2026 search exports, deduplication, Crossref audit, and screening-ready inputs.
- `prompt_templates/`: operative role prompts used by the Codex runner.
- `pipeline_code/`: copy of the `run_codex_screening_pipeline.py` runner used for these artifacts.
- `search_configs/`: June and July 2026 update search configurations.
- `manifest.csv`: SHA-256 manifest for all files in this bundle.

## Run Summary

Full 4,027-record rerun:

- Records: 4,027
- EXCLUDE: 3,805
- UNCERTAIN: 88
- INCLUDE: 134
- Adjudicated: 1,338

June update cohort:

- Raw records retrieved: 933
- Update-unique records after within-update deduplication: 785
- Truly new records after cross-corpus deduplication and Crossref audit: 445
- New title/abstract records screened: 431
- New screened EXCLUDE: 409
- New screened UNCERTAIN: 7
- New screened INCLUDE: 15
- Adjudicated: 158

July update cohort:

- Raw records retrieved: 197
- Update-unique records before cross-dedup: 155
- New title/abstract records screened: 119
- Already present in the master corpus/full rerun: 21
- Not screened because abstract is empty: 15
- New screened EXCLUDE: 113
- New screened INCLUDE: 6
- Adjudicated: 40

## Per-run Files

Each run directory contains:

- `final_screening_results.json` / `.csv`: final row-level decisions.
- `scope_reviewer.jsonl`, `architecture_reviewer.jsonl`, `adjudicator.jsonl`: structured per-record role outputs.
- `python_gate_outputs.json` and `adjudication_queue.json`: gate and adjudication trace artifacts.
- `pipeline.log`: runner progress and timing log.
- `artifact_summary.json`: compact metadata and decision-count summary.
- `role_logs.tar.gz`: compressed per-batch role logs.

The `role_logs.tar.gz` archives preserve the per-batch audit trail:

- `batch_*.prompt.txt`
- `batch_*.response.txt`
- `batch_*.parsed.json`
- `batch_*.meta.json`
- `batch_*.stdout.log`
- `batch_*.stderr.log`

These logs preserve prompts, raw model responses, parsed outputs, metadata, and
brief evidence-grounded rationales. Hidden model chain-of-thought is not
available and is not included.

## Notes

The role logs are archived rather than committed as thousands of loose files.
This keeps the bundle aligned with the repository's existing curated artifact
format while still preserving the audit material needed to trace each decision.

The current PRISMA search/screening log is maintained in
`protocol/prisma_search_screening_log_2026-07-07.md`.
