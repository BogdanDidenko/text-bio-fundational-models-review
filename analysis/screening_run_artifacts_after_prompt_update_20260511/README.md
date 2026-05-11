# Screening Run Artifacts After Prompt Update (2026-05-11)

This directory contains a curated, Git-safe artifact bundle for the post-prompt-update screening experiments. It intentionally does not mirror the whole `runs/` tree, because that tree contains smoke tests, temporary continuation inputs, model-server scratch logs, and unrelated experiments.

## Contents

- `full_runs/`: full 4,027-record runs after prompt/schema refinement for DeepSeek V4 Flash, GPT-OSS 120B, and Nemotron 3 Super 120B A12B FP8.
- `regression_runs/`: 116-record regression repeats for DeepSeek V4 Flash and GPT-OSS 120B.
- `prompt_iteration_runs/`: high-signal prompt-iteration experiments used while refining wrapper, text-component, text-bio bridge, generative, and thin-abstract boundaries.
- `inputs/`: input CSVs used for the full, regression, and prompt-iteration experiments.
- `prompt_templates/`: operative runtime prompt templates used by the current pipeline.
- `manifest.csv`: SHA-256 manifest for all files in this bundle.

## Per-run files

Each run directory contains `agent_outputs_dedup.parquet`, a deduplicated row-level table keyed by `cluster_id`. This parquet preserves the full per-stage agent outputs in columns such as `round-A_scope_reviewer_output`, `round-A_architecture_reviewer_output`, and `round-B_adjudicator_output`, together with criterion fields, gate decisions, final verdicts, and exclusion/uncertainty rationales.

Where available, the bundle also includes original `guideline_pilot_raw_completed.jsonl` / `.csv` files and `runner.log` files from each job or repeat. These are the pipeline traces showing how records were processed and why final decisions were assigned. Watchdog summaries and server metadata are included for full runs.

## Notes

Git LFS is not installed on the cluster login environment, so files were kept below GitHub's single-file size limit. Large model-server logs and transient continuation input files were not included because they do not contain agent decision rationales.
