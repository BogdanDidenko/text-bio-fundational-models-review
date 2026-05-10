# LLM Screening Agreement and Nondeterminism Analysis

This folder summarizes repeat-run and cross-model agreement for the 116-case prompt regression set.
The purpose is to support a methods/results section on nondeterminism in LLM-assisted title/abstract screening.

## Pairwise Agreement

### deepseek_rep1 vs deepseek_rep2
- Matched records: 116
- Decision mismatches: 21 (0.181)
- Include Jaccard: 0.868
- Stable INCLUDE: 33 / include union 38
- A counts: `{'EXCLUDE': 62, 'INCLUDE': 34, 'UNCERTAIN': 20}`
- B counts: `{'EXCLUDE': 61, 'INCLUDE': 37, 'UNCERTAIN': 18}`

### gptoss_rep1 vs gptoss_rep2
- Matched records: 116
- Decision mismatches: 8 (0.069)
- Include Jaccard: 0.920
- Stable INCLUDE: 46 / include union 50
- A counts: `{'EXCLUDE': 63, 'INCLUDE': 49, 'UNCERTAIN': 4}`
- B counts: `{'EXCLUDE': 64, 'INCLUDE': 47, 'UNCERTAIN': 5}`

### deepseek_rep1 vs gptoss_rep1
- Matched records: 116
- Decision mismatches: 24 (0.207)
- Include Jaccard: 0.694
- Stable INCLUDE: 34 / include union 49
- A counts: `{'EXCLUDE': 62, 'INCLUDE': 34, 'UNCERTAIN': 20}`
- B counts: `{'EXCLUDE': 63, 'INCLUDE': 49, 'UNCERTAIN': 4}`

### deepseek_rep2 vs gptoss_rep2
- Matched records: 116
- Decision mismatches: 28 (0.241)
- Include Jaccard: 0.647
- Stable INCLUDE: 33 / include union 51
- A counts: `{'EXCLUDE': 61, 'INCLUDE': 37, 'UNCERTAIN': 18}`
- B counts: `{'EXCLUDE': 64, 'INCLUDE': 47, 'UNCERTAIN': 5}`

## Consensus Summaries

### DeepSeek repeats
- Stable decisions: 95 / 116 (0.819)
- INCLUDE in any run: 38
- INCLUDE in every run: 33
- UNCERTAIN in any run: 29

### GPT-OSS repeats
- Stable decisions: 108 / 116 (0.931)
- INCLUDE in any run: 50
- INCLUDE in every run: 46
- UNCERTAIN in any run: 7

### All available runs
- Stable decisions: 79 / 116 (0.681)
- INCLUDE in any run: 52
- INCLUDE in every run: 31
- UNCERTAIN in any run: 31

## Main Observations

- GPT-OSS 120B was more repeatable across two runs than DeepSeek V4 Flash on the same 116 records.
- GPT-OSS was also more liberal: it produced substantially more INCLUDE decisions and fewer UNCERTAIN decisions.
- DeepSeek was more conservative but less stable, especially for EXCLUDE/UNCERTAIN boundary cases.
- Cross-model disagreement was larger than within-model GPT-OSS disagreement, showing that model choice materially changes the screened corpus.
- The recurring unstable mechanisms are thin abstracts, wrapper-vs-primary-model ambiguity, text-derived metadata/embedding ambiguity, and generative-vs-predictive ambiguity.

## Artifacts

- `pairwise_agreement.json`: numeric pairwise agreement summaries.
- `cross_model_decisions.csv`: all decisions and rationales merged across runs.
- `deepseek_consensus.csv`: DeepSeek repeat consensus for available repeats.
- `gptoss_consensus.csv`: GPT-OSS repeat consensus.
- `all_run_consensus.csv`: decision stability across every available run.
- `unstable_reasoning_cases.csv`: case-level rationales for all records with any disagreement.
- `boundary_case_counts.csv`: emitted boundary labels by run.
- `issue_tag_counts.csv`: heuristic tags for disagreement mechanisms.
- `representative_reasoning_paths.md`: compact qualitative case studies for paper writing.

## Draft Research Framing

These results suggest that LLM screening should not be treated as a deterministic classifier, even when prompts, inputs, and decoding settings are held constant. The same pipeline can produce different eligibility decisions across repeated runs, and different LLMs can shift the inclusion frontier. For evidence synthesis, the most important risk is not just random label noise, but unstable boundary interpretation: wrapper papers, biological-token-only language models, text-conditioned generative models, and truncated abstracts are especially sensitive to model and run variation. A defensible automated screening workflow should therefore report repeat-run agreement, include-set stability, model-dependence, and the treatment of UNCERTAIN records.
