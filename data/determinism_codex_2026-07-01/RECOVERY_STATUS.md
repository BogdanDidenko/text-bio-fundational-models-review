# Recovery Status

Recovered on 2026-07-29 after workstation migration.

## Recovered

- `input_random20_seed20260701.json`: reconstructed from the unchanged 4,027-record source corpus using the original seed, sampling code, record order, and timestamp. The 20 sampled title prefixes exactly match the historical command output.
- `determinism_summary.json`: recovered verbatim from the historical command output.
- `determinism_report.md`: recovered verbatim from the historical file-display output.
- `tgpt_failure_analysis.md`: recovered verbatim from the historical patch.

## Not Recovered

- `run_1/`, `run_2/`, and `run_3/`, including per-role request and response logs.
- `determinism_record_diff.csv`.

The missing run directories were not recreated by rerunning the model because a new run would not be the original nondeterminism experiment. The recovered report retains the final decision, code, and source for every record in each run. The original role-level evidence remains quoted in `tgpt_failure_analysis.md` for the investigated tGPT case.

