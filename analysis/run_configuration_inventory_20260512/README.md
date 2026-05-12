# Run configuration inventory

This inventory summarizes saved configuration metadata for LatteReview guideline pilot runs.

Important interpretation:

- Request-level sampling parameters are fixed by `scripts/run_lattereview_guideline_pilot.py`: `temperature=0.7`, `top_p=1.0`, `n=1`, `seed=0`, and `max_tokens` from the run CLI. These values are not all duplicated in each `guideline_pilot_summary.json`, but are reconstructable from the pipeline code used for these runs.
- `guideline_pilot_summary.json` records model, input, max_concurrent, max_tokens, thinking/reasoning flags, and decision counts.
- `server_info.env` records server-side seed when the submit script wrote it. Full current watchdog jobs record `SEED=0`. GPT-OSS regression repeats did not write a server-side seed in the sbatch script, but request-level seed was still `0`.
- vLLM server launch settings such as max model length and max batched tokens are in the submit scripts rather than every per-job summary. Current full runs used 32768 max model length and 32768 max batched tokens.

Files:

- `guideline_run_configuration_inventory.csv/parquet`: one row per `guideline_pilot_summary.json`.
- `guideline_run_configuration_compact.csv/parquet`: grouped compact view.
