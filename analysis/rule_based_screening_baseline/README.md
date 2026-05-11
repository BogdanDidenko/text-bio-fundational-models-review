# Rule-based Screening Baseline

This directory contains a deterministic lexical baseline for the three-way
screening task: `INCLUDE`, `UNCERTAIN`, and `EXCLUDE`.

The baseline is intentionally not tuned to article titles or article-specific
phrases discovered by the LLM screen.  Its rules are written at the task level:

- biological domain evidence;
- natural-language/text evidence;
- explicit text-biology bridge evidence;
- generative or foundation-model evidence;
- broad exclusions for reviews, tool wrappers, biological-token-only modeling,
  and predictive-only tasks.

The LLM runs are used only for post-hoc comparison, not for defining
article-specific detection rules.

## Files

- `rule_based_baseline_results.csv`: per-record rule outputs, keyword evidence,
  and LLM comparison labels.
- `rule_based_baseline_results.parquet`: same table in parquet format.
- `rule_based_baseline_iterations.csv`: summary metrics for each rule version.
- `rule_based_baseline_iterations.parquet`: compact parquet copy of the
  iteration summary.
- `rule_based_baseline_run_log.parquet`: one-row-per-rule-version execution log
  with timestamp, command, input path, LLM comparison runs, and metrics.
- `rule_based_baseline_summary.json`: machine-readable configuration and
  metrics.
- `v5_mismatches_vs_llm_majority.csv`: records where the final rule version
  disagrees with the five-run LLM majority label.
- `v5_mismatches_vs_llm_majority.parquet`: compact parquet copy of the final
  mismatch log.

## Iterations

| version | INCLUDE | UNCERTAIN | EXCLUDE | stable INCLUDE recall | any-LLM INCLUDE recall | INCLUDE precision vs any-LLM INCLUDE | INCLUDE overlap with stable EXCLUDE | majority agreement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v0_broad_keywords | 981 | 2165 | 881 | 0.960 | 0.912 | 0.105 | 685 | 0.233 |
| v1_bridge_required | 237 | 1761 | 2029 | 0.600 | 0.398 | 0.190 | 137 | 0.479 |
| v2_precision_guards | 199 | 1670 | 2158 | 0.600 | 0.398 | 0.226 | 102 | 0.509 |
| v3_conservative_final | 237 | 1347 | 2443 | 0.600 | 0.398 | 0.190 | 137 | 0.576 |
| v4_precision_text_bio_final | 59 | 1516 | 2452 | 0.680 | 0.221 | 0.424 | 31 | 0.581 |
| v5_high_precision_final | 39 | 1509 | 2479 | 0.760 | 0.204 | 0.590 | 16 | 0.588 |

## Interpretation

The final rule set is precision-oriented but still limited.  It includes 39 of
4027 records and recovers 76% of records that all five LLM runs included.  Its
low recall against the broader union of LLM includes shows that a simple lexical
baseline misses many plausible boundary cases.  This makes it useful as a
conservative non-LLM comparator rather than as a replacement for the multi-agent
screening pipeline.
