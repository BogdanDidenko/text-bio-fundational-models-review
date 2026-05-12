# Nemotron current prompt full-corpus replicate 2

This folder contains the second full-corpus current-prompt run for
NVIDIA Nemotron-3-Super-120B-A12B-FP8.

The run completed in two watchdog jobs:

- `job_11594`: processed the first 2222 records and wrote a continuation input.
- `job_11609`: processed the remaining 1805 records.

Final deduplicated result:

- Records: 4027
- EXCLUDE: 3547
- UNCERTAIN: 393
- INCLUDE: 87

Compact parquet exports were added for downstream analysis:

- `guideline_pilot_results_all_completed_dedup.parquet`: final deduplicated decisions.
- `guideline_pilot_results_all_jobs.parquet`: concatenated per-job pipeline outputs with `source_job`.
- `guideline_pilot_raw_completed_all_jobs.parquet`: concatenated per-job raw agent outputs with `source_job`.

Per-job runner/server logs and summary JSON files are retained to document the
watchdog continuation and runtime behavior.
