# Pilot Smoke Task — Title/Abstract Screening Sanity Check

## Purpose

Run the criterion-by-criterion `LatteReview` workflow on a small, hand-curated
set of records that span all seven benchmark groups defined in
[`screening_benchmark_and_tiers.md`](screening_benchmark_and_tiers.md) §4.

This is **not** a deployment-grade benchmark gate. It is a fast sanity check
that:

- the runner does not crash on real records;
- the prompt templates produce parseable JSON;
- the gate logic correctly aggregates criterion answers into final decisions;
- the system handles each declared failure mode (review, bio-only, encoder-only,
  wrapper, benchmark/resource, borderline) at least once.

A full deployment-grade benchmark per
[`screening_benchmark_and_tiers.md`](screening_benchmark_and_tiers.md) §4
requires 36–48 manually adjudicated records and is a follow-up task.

## Scope of this pilot

| Group | Coverage | Picked count | Selection method |
|-------|----------|-------------:|------------------|
| P1 | Clear positives (NL + bio bridge) | 8 | Manual (ground truth) |
| P2 | Biological-token stress cases | 5 | Manual (ground truth) |
| N1 | Review/editorial papers | 5 | Heuristic on title (`"a review"`, `"a survey"`, `": review"`) |
| N2 | Bio-only multimodal | 4 | Manual seeding (MultiVI etc.) + heuristic on `"multi-omics integration"` |
| N3 | Encoder-only negatives | 3 | Manual (ground truth, scFoundation not found in corpus) |
| N4 | Wrapper/application papers | 5 | Heuristic on body (`"using chatgpt"`, `"gpt-4 for"`, etc.) |
| N5 | Benchmark/resource papers | 5 | Heuristic on title (`"benchmark"`, `"benchmarking"`) |
| **Total** | | **35** | |

The U1 "borderline uncertain" group is intentionally **omitted** from the pilot.
Picking U1 records correctly requires manual adjudication of borderline
abstracts and is therefore part of the full benchmark, not the smoke test.

## Input files

- [`data/pilot_smoke_input.csv`](../data/pilot_smoke_input.csv) — runner input
  (`title`, `abstract` columns; matches the
  [`data/screening_input_template.csv`](../data/screening_input_template.csv)
  schema)
- [`data/pilot_smoke_annotated.csv`](../data/pilot_smoke_annotated.csv) —
  evaluation key (`group`, `expected_decision`, `expected_paper_type`,
  `expected_exclusion_code`, `notes`, `model_or_label`, plus the same `title`,
  `doi`, `abstract`)

## How to run

```bash
# 1. Prepare LatteReview runtime (clones LatteReview, installs minimal deps)
bash scripts/setup_lattereview_runtime.sh

# 2. Start an OpenAI-compatible LLM endpoint (e.g. vLLM)
#    Model is a deployment variable, not part of the methodology.
#    Pilot runs may use any model that satisfies the smoke acceptance criteria.

# 3. Run the criterion-by-criterion pilot
python3 scripts/run_lattereview_guideline_pilot.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model <your-served-model-name> \
  --input-csv data/pilot_smoke_input.csv \
  --output-dir data/pilot_smoke_results/
```

## Acceptance criteria

The runner is considered to have passed the smoke test if all of the following
hold on the 35-record pilot:

### Mechanical

- All 35 records produce valid JSON for `scope_reviewer` and
  `architecture_reviewer`.
- No record causes a runner crash or empty output.
- Adjudicator runs only on records flagged by the gate logic, not on all
  records.

### Recall on must-include records

- All 9 must-include records produce `expected_final_decision = INCLUDE`.
- P2 is no longer uniformly must-include. Gene-token-only models without
  natural-language text or explicit text-bio alignment are expected to be
  excluded with `EC2_no_text_component`; X-Cell remains an expected include
  because its abstract describes natural-language-derived biological priors.

### Specificity on negative groups

- All 5 N1 records → `EXCLUDE` with `paper_type = review_editorial` and
  `primary_exclusion_code = review_editorial`.
- All 4 N2 records → `EXCLUDE` with
  `text_component_present = no` and
  `primary_exclusion_code = EC2_no_text_component`.
- All 4 gene-token-only P2 records → `EXCLUDE` with
  `text_component_present = no` and
  `primary_exclusion_code = EC2_no_text_component`.
- All 3 N3 records → `EXCLUDE` with
  `generative_model_present = no` and
  `primary_exclusion_code = EC3_not_generative`.
- All 5 N4 records → `EXCLUDE` with
  `paper_type = application_wrapper` and
  `primary_exclusion_code = application_wrapper`.
- All 5 N5 records → `EXCLUDE` with
  `paper_type = benchmark_resource` and
  `primary_exclusion_code = benchmark_resource`.

### Adjudication trigger correctness

- The records routed to round B (adjudicator) are exactly those where the
  scope and architecture reviewers either disagreed on a shared field or
  returned `unclear` on a decisive criterion. Any other adjudication trigger
  is a gate-logic bug.

## Known edge cases the smoke will surface

### 1. GenePT — must-include vs application_wrapper conflict

GenePT is listed as ground truth (must-include) but its abstract describes the
model as built **from ChatGPT**: gene description text is fed to OpenAI's
embedding API and the resulting vectors are reused for downstream cell tasks.

The operative `scope_reviewer_prompt.txt` says:

> If a paper only uses embeddings, prompts, metadata descriptions, or outputs
> from an existing external LLM as side information for a downstream bio task,
> treat it as `application_wrapper`, not as a substantive text-bio model.

This is a real protocol ambiguity that the smoke run should expose. Possible
outcomes:

- The model reads GenePT as `application_wrapper` and excludes it, contradicting
  ground truth. **Action**: refine the operative prompt to carve out the case
  where the wrapper itself is presented as a foundation model with broad
  transferability, or remove GenePT from must-include.
- The model preserves GenePT as a primary model paper. **Action**: confirm the
  prompt's wrapper rule is interpreted strictly (only excludes pure downstream
  applications) and document that decision.

This case is annotated explicitly in `pilot_smoke_annotated.csv` under
`notes`.

### 2. CellWhisperer — short abstract

The CellWhisperer record in our corpus has an abstract of only 217 characters
(it appears to be a press release rather than the original paper abstract).
The smoke will test whether the system correctly returns `unclear` on
underspecified criteria for short abstracts, rather than forcing a binary
decision.

### 3. scFoundation — not in corpus

scFoundation is listed in `ground_truth_models.md` as related-but-excluded
(N3) but does **not** appear in the deduplicated corpus. The smoke therefore
contains 3 N3 records, not 4. This is a search-completeness signal, separate
from the screening test.

### 4. Heuristic-picked negatives may include false positives

N1, N4, and N5 records were picked by simple title/abstract heuristics
without manual adjudication of every abstract. A heuristic miss means the
group label may be wrong, and the screening result for that record will be
"correct vs the heuristic label" but not necessarily "correct vs the actual
paper". Treat any disagreement on these groups as worth a manual look at the
abstract before assigning blame to the prompt.

## After smoke passes

The pilot's purpose is to confirm the pipeline is sound enough to invest
manual adjudication time in the full benchmark. Once smoke passes:

1. Replace heuristic-picked N1/N4/N5 with manually adjudicated records.
2. Add Group U1 (borderline uncertain) records — minimum 5–7.
3. Achieve the 36–48 record target from
   [`screening_benchmark_and_tiers.md`](screening_benchmark_and_tiers.md) §4.
4. Re-run, treating that as the **deployment gate**, not a smoke test.
5. Add the determinism probe per
   [`lattereview_screening_architecture.md`](lattereview_screening_architecture.md) §7.
6. Add the Cochrane safety case per
   [`llm_screening_system_guideline.md`](llm_screening_system_guideline.md) §10.

## File header conventions

`pilot_smoke_annotated.csv` columns:

| Column | Values |
|--------|--------|
| `group` | `P1` / `P2` / `N1` / `N2` / `N3` / `N4` / `N5` |
| `expected_decision` | `INCLUDE` / `EXCLUDE` |
| `expected_paper_type` | `primary_model_paper` / `review_editorial` / `benchmark_resource` / `application_wrapper` |
| `expected_exclusion_code` | `none` / `EC2_no_text_component` / `EC3_not_generative` / `review_editorial` / `benchmark_resource` / `application_wrapper` |
| `model_or_label` | model name (P1/P2/N3) or category label (others) |
| `notes` | edge case flags or selection caveats |
| `title` | from `deduplicated_records.json` |
| `doi` | from `deduplicated_records.json` |
| `abstract` | from `deduplicated_records.json` (post-enrichment) |

## Provenance

All 35 records were extracted from
[`data/deduplicated_records.json`](../data/deduplicated_records.json) (the
4,027-record corpus from search v3.1 + the 2026-04-14 update).

Selection script: see commit message and the heuristics described above.
This pilot is intentionally **not** a frozen artifact — it should be replaced
by the full benchmark before live deployment.
