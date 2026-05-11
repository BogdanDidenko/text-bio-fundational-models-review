# Reproducibility and Cross-Agent Agreement in LLM-Assisted Title/Abstract Screening for Generative Text-Bio Foundation Models

## Abstract

Large language models are increasingly used as screening assistants in evidence synthesis, but their outputs should not be assumed to be deterministic screening decisions. We evaluated repeated-run and cross-model stability in an LLM-assisted title/abstract screening pipeline for a scoping review of generative text-bio foundation models. The pipeline used two first-pass reviewers, one focused on topical scope and one on model architecture, followed by an adjudicator for unresolved or conflicting cases. We tested stability on a full 4,027-record corpus, a high-signal 25-record prompt-iteration set, and a 116-record regression set enriched for benchmark examples, stable includes, and previously unstable boundary cases. Across the original 4,027-record DeepSeek V4 Flash replicate experiment, overall decision mismatch was 7.3%, but INCLUDE-set Jaccard was only 0.587. After prompt and schema refinement, DeepSeek V4 Flash reached INCLUDE Jaccard 0.825-0.868 across three pairwise comparisons on the 116-record regression set, but overall three-way decision mismatch remained 15.5-18.1% because many records moved between EXCLUDE and UNCERTAIN. GPT-OSS 120B was more internally stable on the same regression set, with 6.9% mismatch and INCLUDE Jaccard 0.920, but it was more liberal, producing substantially more INCLUDE decisions and fewer UNCERTAIN decisions. Cross-model mismatch was 19.8-24.1%, showing that model choice materially shifts the inclusion frontier. The main instability mechanisms were not random formatting failures; they reflected recurring interpretive boundaries: wrapper versus primary model contribution, biological-token language metaphors versus natural-language text components, generative architecture versus predictive task framing, text-derived metadata versus central text conditioning, and thin abstract inference. These findings support treating LLM screening as a probabilistic triage and measurement process rather than a deterministic classifier.

## 1. Background

Title and abstract screening is a high-impact step in evidence synthesis because early false exclusions can remove relevant studies before full-text review. The reproducibility brief `Reproducibility of LLM-Assisted Title and Abstract Screening in Evidence Synthesis.pdf` summarizes a growing methods concern: LLM screening studies often report single-run accuracy, sensitivity, specificity, or workload savings, but much less often estimate test-retest stability under repeated identical runs.

The brief identifies one directly relevant primary preprint, **Beyond Accuracy: LLM Variability in Evidence Screening for Software Engineering SLRs** (`https://arxiv.org/html/2604.27006v1`), which screened the same evidence sets repeatedly with fixed settings and temperature zero. The key methodological lesson is directly aligned with our observations: deterministic decoding settings do not guarantee stable screening labels. The brief also emphasizes that repeated-run evaluations should report not only accuracy, but also percent agreement, chance-corrected agreement, set-level overlap such as Jaccard similarity for included records, false exclusion or Lost Evidence risk, and explicit handling of uncertain or unstable outputs.

Our review setting is especially vulnerable to this issue. The eligibility boundary is not a simple keyword match. A relevant paper must plausibly be a primary model paper, involve biological modalities, include a natural-language or text-derived component, bridge text and biological modalities substantively, and involve a genuinely generative model rather than only a predictive, classificatory, retrieval, or wrapper system. These criteria create scientifically meaningful boundary cases. For example, "language model" can mean natural-language alignment, but it can also be a metaphor for gene tokens, cell sentences, DNA sequence modeling, or omics tokenization. Likewise, an LLM can be a primary model component, a frozen side feature generator, or merely an application wrapper around an existing model.

## 2. Review Task

The screening task was to identify candidate papers for a review of **generative text-bio foundation models**. The target concept was not "any AI in biology" and not "any biological foundation model." We aimed to retain papers where the abstract supports all of the following:

- a primary candidate model or framework rather than a review/editorial, benchmark/resource paper, or application wrapper;
- a biological modality such as genes, cells, proteins, omics, histology, clinical-biological records, or related biomedical data;
- a substantive natural-language or text-derived component, rather than only biological tokenization or language-model metaphors;
- a text-bio bridge, meaning that text and biological data are aligned, conditioned, generated across, or otherwise central to the candidate model;
- a generative model contribution, not only classification, risk prediction, survival prediction, annotation, retrieval, or encoder-only representation learning.

The pipeline produced one of three final verdicts:

- `INCLUDE`: all decisive criteria are supported from the title/abstract.
- `EXCLUDE`: at least one decisive criterion is clearly not met.
- `UNCERTAIN`: the title/abstract is insufficient, ambiguous, thin, or internally mixed on a decisive criterion.

We intentionally preserved `UNCERTAIN` as a safety state. It is not a soft exclusion. This aligns with conservative title/abstract screening practice and with the reproducibility brief's conclusion that unstable or unclassifiable outputs should be surfaced rather than hidden behind a single binary decision.

## 3. Pipeline

The pipeline structure was preserved throughout the experiments:

1. **Round A: scope reviewer**
   - Assesses paper type, biological modality, text component, and text-bio bridge.
   - Handles exclusions such as review/editorial, benchmark/resource, application wrapper, no biological modality, no text component, or no substantive text-bio bridge.

2. **Round A: architecture reviewer**
   - Assesses whether the paper describes a genuinely generative model and whether foundation-model evidence is present.
   - Handles exclusions such as application wrapper or not generative.

3. **Round B: adjudicator**
   - Runs only when first-pass reviewers produce unresolved, conflicting, or uncertain criterion-level outputs.
   - Resolves criterion-level disagreement conservatively and emits the final selected fields used for `INCLUDE`, `EXCLUDE`, or `UNCERTAIN`.

Thus, the number of agents remained fixed: **two first-pass reviewers plus one adjudicator**. The prompt files also remained fixed in number: `scope_reviewer_prompt.txt`, `architecture_reviewer_prompt.txt`, and `adjudicator_prompt.txt`.

The main changes were not architectural. They were changes in **prompt specificity**, **eligibility boundaries**, and **output schema**. We added explicit audit fields:

- `evidence_for_text_component`;
- `evidence_for_text_bio_bridge`;
- `evidence_for_generative_model`;
- `boundary_case`.

These fields are not additional eligibility criteria. They force each agent to expose the evidence used for decisive criteria and make disagreement analysis possible.

## 4. Experimental Design

We summarize four linked experiments.

### 4.1 Full-Corpus DeepSeek Baseline

We ran DeepSeek V4 Flash twice on the full 4,027-record abstract corpus using the earlier pipeline state. This established the original nondeterminism signal.

### 4.2 High-Signal Prompt Iteration Set

We then used a compact 25-record high-signal set enriched for cases that exposed prompt weaknesses. This set was used to test targeted changes before larger regression runs. Two important iterations were:

- **iter3**: bridge/thin-abstract refinements.
- **iter4**: text-conditioning refinements, especially clarifying when text-derived priors, summaries, descriptions, or embeddings count as a text-bio bridge.

This middle phase is important because the final pipeline was not produced by an opaque rewrite. We changed the prompt boundary language in small steps while keeping the agent structure fixed. The goal was to reduce false-positive INCLUDE drift without collapsing all ambiguous records into EXCLUDE. Each iteration was evaluated on a deliberately high-signal subset, so the absolute INCLUDE/UNCERTAIN proportions should not be interpreted as corpus prevalence. They should be interpreted as stress tests of boundary behavior.

| iteration | records | main prompt change tested | EXCLUDE | INCLUDE | UNCERTAIN | observed effect |
|---|---:|---|---:|---:|---:|---|
| stability/current smoke | 3 | Initial stability check on records that had exposed early inconsistency. | 3 | 0 | 0 | Confirmed that some clear excludes were stable under the current execution stack. |
| iter1 current high-signal | 25 | Current prompt before targeted boundary refinement. | 17 | 3 | 5 | Conservative but too narrow; several known relevant or near-relevant records were excluded or left uncertain. |
| iter2 wrapper relaxation | 25 | Clarified that use of pretrained LLM components is not automatically a wrapper when the abstract presents a new multimodal text-bio model or generator. | 13 | 8 | 4 | Increased INCLUDE recovery on benchmark-like records without eliminating uncertainty. |
| iter3 bridge/thin-abstract | 25 | Added clearer handling of text-bio bridges and thin abstracts; repeated once to inspect stability. | 13 / 14 | 8 / 7 | 4 / 4 | INCLUDE remained high and pairwise INCLUDE Jaccard was 0.875; remaining disagreement was concentrated in boundary cases. |
| iter4 text-conditioning | 25 | Clarified when text-derived priors, summaries, descriptions, or embeddings count as a text component and bridge. | 14 / 15 | 9 / 8 | 2 / 2 | Reduced UNCERTAIN count and produced INCLUDE Jaccard 0.889, but shifted some instability to EXCLUDE/UNCERTAIN. |
| iter5 ambiguous tie-break | 3 | Targeted unstable records where ambiguous language-model/foundation-model claims had been over-inferred. | 0 | 1 | 2 | Preserved uncertainty when the abstract did not resolve decisive criteria, rather than forcing inclusion. |

The qualitative review of these runs identified five recurring failure modes that motivated the final prompt wording:

- external LLM wrappers being mistaken for primary candidate models;
- biological-token "language" metaphors being mistaken for natural-language text components;
- predictive systems being credited as generative because they used language-model-style pretraining;
- text-derived metadata, labels, or embeddings being treated inconsistently as a text-bio bridge;
- thin abstracts causing the model to infer eligibility from names such as "GPT", "LLM", or "foundation model".

The final prompt stack therefore added explicit boundary examples and audit fields, while preserving the same three agents. The complete operative prompts are reproduced in **Appendix C** and are versioned in `protocol/screening_prompt_templates/`.

### 4.3 116-Record Regression Set

We built a 116-record regression set from four groups:

- benchmark boundary cases;
- stable INCLUDE cases;
- previously INCLUDE-unstable cases;
- previously EXCLUDE/UNCERTAIN-unstable cases.

This set is deliberately harder than the full corpus because it is enriched for records near conceptual boundaries.

We ran:

- DeepSeek V4 Flash three times;
- GPT-OSS 120B twice.

### 4.4 New Full-Corpus Rerun With Current Pipeline

We then repeated the full 4,027-record DeepSeek V4 Flash screening on the current pipeline after the prompt and schema changes. The purpose was to test whether the improvements observed on the regression set translated back to the complete corpus.

Both current full reruns completed all 4,027 records:

| current rerun | completed records | EXCLUDE | INCLUDE | UNCERTAIN |
|---|---:|---:|---:|---:|
| DeepSeek current full rerun rep1 | 4,027 | 3,489 | 32 | 506 |
| DeepSeek current full rerun rep2 | 4,027 | 3,498 | 33 | 496 |

The rerun used the same three-agent pipeline structure, DeepSeek thinking mode, `reasoning_effort=high`, 32k model context, 16k max generated tokens, MTP/speculative decoding, and streaming concurrency. Operationally, the full run required watchdog-style continuation jobs because the 2-hour cluster wall-time was shorter than the full-corpus processing time. Temporary cluster-memory constraints interrupted continuation once, but no records were lost; the watchdog resumed from deduplicated completed records.

## 5. Metrics

We report:

- **decision mismatch rate**: proportion of records whose final three-way verdict differs between two runs;
- **class-specific Jaccard similarity**: for each class, the size of the intersection divided by the size of the union across two runs;
- **stable class count**: records assigned the same class in both runs;
- **multi-run all-stable count**: records assigned the same verdict across all repeated runs in a set;
- **any-class count**: records assigned a class in at least one run;
- **unstable union count**: any-class count minus all-class count, representing records whose membership in that class is not stable.

For the most important screening class, `INCLUDE` Jaccard is:

```text
INCLUDE Jaccard = |INCLUDE_run_a intersect INCLUDE_run_b| / |INCLUDE_run_a union INCLUDE_run_b|
```

This is stricter and more useful than raw counts when inclusion sets are small.

## 6. Results

### 6.1 Pairwise Stability Across Experiments

| comparison | n | mismatches | mismatch rate | INCLUDE Jaccard | EXCLUDE Jaccard | UNCERTAIN Jaccard |
|---|---:|---:|---:|---:|---:|---:|
| Full 4,027 DeepSeek baseline | 4,027 | 295 | 0.073 | 0.587 | 0.919 | 0.605 |
| Full 4,027 DeepSeek current pipeline | 4,027 | 234 | 0.058 | 0.806 | 0.936 | 0.627 |
| High-signal 25 iter3 DeepSeek | 25 | 2 | 0.080 | 0.875 | 0.929 | 0.600 |
| High-signal 25 iter4 DeepSeek | 25 | 3 | 0.120 | 0.889 | 0.812 | 0.333 |
| Regression 116 DeepSeek r1/r2 | 116 | 21 | 0.181 | 0.868 | 0.757 | 0.310 |
| Regression 116 DeepSeek r1/r3 | 116 | 19 | 0.164 | 0.842 | 0.786 | 0.370 |
| Regression 116 DeepSeek r2/r3 | 116 | 18 | 0.155 | 0.825 | 0.797 | 0.400 |
| Regression 116 GPT-OSS r1/r2 | 116 | 8 | 0.069 | 0.920 | 0.896 | 0.286 |
| Cross-model DS r1 vs GPT r1 | 116 | 24 | 0.207 | 0.694 | 0.761 | 0.200 |
| Cross-model DS r2 vs GPT r2 | 116 | 28 | 0.241 | 0.647 | 0.712 | 0.150 |
| Cross-model DS r3 vs GPT r1 | 116 | 23 | 0.198 | 0.700 | 0.775 | 0.167 |

The full-corpus baseline had a relatively low overall mismatch rate, 7.3%, because the corpus was dominated by clear EXCLUDE records. However, the INCLUDE set was unstable: only 37 papers were included by both full-corpus runs, while 63 papers were included by at least one run, giving INCLUDE Jaccard 0.587. This is the key reason raw agreement is insufficient: class imbalance makes the full run look stable while the included corpus drifts.

The completed current full-corpus rerun showed a clear improvement. Overall decision mismatch decreased from 295/4,027 (7.3%) to 234/4,027 (5.8%). More importantly, INCLUDE-set stability improved from 0.587 to 0.806. The current pipeline included 32 papers in the first rerun and 33 in the second; 29 papers were included by both, and 36 were included by at least one run. Thus, unstable INCLUDE membership fell from 26 records in the original full-corpus replicate to 7 records in the current full-corpus replicate. Most remaining disagreement moved to the EXCLUDE/UNCERTAIN boundary rather than the INCLUDE boundary.

The high-signal 25-record prompt iterations showed that targeted prompt refinements improved INCLUDE stability on boundary cases. Iter3 produced 8% mismatch and INCLUDE Jaccard 0.875. Iter4 produced 12% mismatch and INCLUDE Jaccard 0.889. The higher mismatch in iter4 reflects that some records moved between EXCLUDE and UNCERTAIN after the prompt became more explicit about text conditioning and thin abstracts. This is not necessarily worse for screening validity: moving unresolved records into UNCERTAIN can be preferable to overconfident exclusion.

The 116-record DeepSeek regression set showed higher three-way mismatch rates, 15.5-18.1%, because the set was intentionally enriched for boundary cases. Nevertheless, INCLUDE Jaccard was much higher than in the original full-corpus baseline, ranging from 0.825 to 0.868 across three DeepSeek pairwise comparisons. This suggests that prompt and schema refinement improved stability of the included set, even though overall three-way stability remained limited by the EXCLUDE/UNCERTAIN boundary.

GPT-OSS was more internally stable than DeepSeek on the 116-record regression set, with 6.9% mismatch and INCLUDE Jaccard 0.920. However, GPT-OSS also produced more INCLUDE decisions and fewer UNCERTAIN decisions, indicating a more liberal decision frontier.

Cross-model agreement was lower than within-model GPT-OSS agreement and comparable to or worse than within-model DeepSeek agreement. Cross-model mismatch ranged from 19.8% to 24.1%, and INCLUDE Jaccard ranged from 0.647 to 0.700. This demonstrates that model choice materially affects which papers enter the candidate corpus.

### 6.2 Detailed Pairwise Class Counts

| comparison | INCLUDE a | INCLUDE b | stable INCLUDE | INCLUDE union | EXCLUDE a | EXCLUDE b | stable EXCLUDE | EXCLUDE union | UNCERTAIN a | UNCERTAIN b | stable UNCERTAIN | UNCERTAIN union |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Full 4,027 DeepSeek baseline | 50 | 50 | 37 | 63 | 3,424 | 3,410 | 3,273 | 3,561 | 553 | 567 | 422 | 698 |
| Full 4,027 DeepSeek current pipeline | 32 | 33 | 29 | 36 | 3,489 | 3,498 | 3,378 | 3,609 | 506 | 496 | 386 | 616 |
| High-signal 25 iter3 DeepSeek | 8 | 7 | 7 | 8 | 13 | 14 | 13 | 14 | 4 | 4 | 3 | 5 |
| High-signal 25 iter4 DeepSeek | 9 | 8 | 8 | 9 | 14 | 15 | 13 | 16 | 2 | 2 | 1 | 3 |
| Regression 116 DeepSeek r1/r2 | 34 | 37 | 33 | 38 | 62 | 61 | 53 | 70 | 20 | 18 | 9 | 29 |
| Regression 116 DeepSeek r1/r3 | 34 | 36 | 32 | 38 | 62 | 63 | 55 | 70 | 20 | 17 | 10 | 27 |
| Regression 116 DeepSeek r2/r3 | 37 | 36 | 33 | 40 | 61 | 63 | 55 | 69 | 18 | 17 | 10 | 25 |
| Regression 116 GPT-OSS r1/r2 | 49 | 47 | 46 | 50 | 63 | 64 | 60 | 67 | 4 | 5 | 2 | 7 |
| Cross-model DS r1 vs GPT r1 | 34 | 49 | 34 | 49 | 62 | 63 | 54 | 71 | 20 | 4 | 4 | 20 |
| Cross-model DS r2 vs GPT r2 | 37 | 47 | 33 | 51 | 61 | 64 | 52 | 73 | 18 | 5 | 3 | 20 |
| Cross-model DS r3 vs GPT r1 | 36 | 49 | 35 | 50 | 63 | 63 | 55 | 71 | 17 | 4 | 3 | 18 |

This table shows the class-specific pattern clearly. `EXCLUDE` is often numerically dominant and therefore inflates overall agreement. `INCLUDE` can be relatively stable after prompt refinement but remains model-dependent. `UNCERTAIN` is the least stable class by Jaccard because it sits between strict exclusion and conservative retention.

### 6.3 Multi-Run Consensus on the 116-Record Regression Set

| set | n | stable all verdicts | unstable any verdict | stable rate | INCLUDE all | INCLUDE any | INCLUDE unstable union | EXCLUDE all | EXCLUDE any | EXCLUDE unstable union | UNCERTAIN all | UNCERTAIN any | UNCERTAIN unstable union |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek 116, 3 repeats | 116 | 88 | 28 | 0.759 | 32 | 41 | 9 | 50 | 73 | 23 | 6 | 32 | 26 |
| GPT-OSS 116, 2 repeats | 116 | 108 | 8 | 0.931 | 46 | 50 | 4 | 60 | 67 | 7 | 2 | 7 | 5 |
| All 116, 5 runs | 116 | 76 | 40 | 0.655 | 30 | 52 | 22 | 44 | 78 | 34 | 2 | 34 | 32 |

Across three DeepSeek repeats, 88/116 records had stable verdicts. The stable INCLUDE core was 32 records, but 41 records were included in at least one DeepSeek run. Therefore, 9 records had unstable DeepSeek INCLUDE membership. For EXCLUDE, 50 records were excluded in all three DeepSeek runs, but 73 were excluded in at least one run. For UNCERTAIN, only 6 were uncertain in all three DeepSeek runs, but 32 were uncertain in at least one run. This confirms that UNCERTAIN is a boundary state rather than a stable class.

Across two GPT-OSS repeats, 108/116 records were stable. GPT-OSS had a larger stable INCLUDE core, 46 records, and only 4 records with unstable INCLUDE membership. However, this increased stability came with a more liberal inclusion frontier.

Across all five runs, only 76/116 records had the same verdict across every model/run. Only 30 records were included by every run, while 52 were included by at least one run. This indicates that a single-run or single-model included corpus is not methodologically robust in this boundary-heavy setting.

## 7. Qualitative Disagreement Mechanisms

The unstable records were not random failures. They clustered around repeated conceptual boundaries.

### 7.1 Wrapper Boundary

Papers such as GeneGPT can be read either as application wrappers around existing LLM/tool systems or as primary biomedical generative systems. Conservative runs excluded them because the central contribution was tool/API augmentation of an external model. More liberal runs included them by emphasizing augmented decoding and biomedical question answering.

This boundary matters because many biomedical LLM papers use existing models, prompts, tools, or embeddings. Without explicit wrapper rules, the pipeline can over-credit downstream applications as primary model papers.

### 7.2 Text-Derived Metadata Boundary

GEM-1-type records exposed instability around LLM-processed metadata. Conservative runs treated metadata processing as side information or preprocessing. Liberal runs treated LLM-processed experimental metadata, text summaries, or foundation-model embeddings as a substantive text-bio bridge.

The prompt update clarified that text-derived priors, summaries, report descriptions, or embeddings count when they condition, guide, or are cross-attended by the candidate generative model itself. They do not count when detached as side features for a downstream classifier or predictor.

### 7.3 Generative Objective Versus Predictive Task

Med-PRSIMD-type records showed disagreement over whether causal language-model pretraining over clinical or biomedical records is sufficient when the final task is risk prediction. Conservative runs focused on the operational task and excluded predictive systems unless the abstract clearly stated generation. Liberal runs treated generative pretraining as enough.

This motivated more explicit architecture prompts requiring evidence of decoder, autoregressive generation, sequence-to-sequence generation, diffusion, VAE/GAN, natural-language generation, or biological output generation.

### 7.4 Biological Tokenization Versus Natural Language

Cell2Sentence-type records exposed a domain-specific ambiguity: biological data can be represented as "sentences" or "tokens" without involving natural-language text. Conservative runs treated "cell sentences" and similar phrases as biological tokenization unless the abstract described natural-language text, prompts, documents, captions, descriptions, or explicit text-bio alignment. More liberal runs credited textualization or GPT-style modeling as a text-bio bridge.

The updated scope prompt now explicitly distinguishes biological-token language metaphors from natural-language text components.

### 7.5 Thin Abstract Inference

BiomedGPT, ADAM-1, Gp-gpt, and similar title-heavy records showed that models differ in how much they infer from names and broad claims. Conservative runs required title/abstract evidence for each decisive criterion. Liberal runs inferred details from the model name or prior-like expectations.

The updated prompts instruct reviewers to use `thin_abstract_boundary` only when missing evidence blocks a decisive criterion and to avoid forcing yes/no decisions when terms such as "LLM", "foundation model", "metadata", or "embeddings" do not resolve text-bio or generative status.

## 8. Effect of Pipeline Detail and Scope Restrictions on Agreement

### 8.1 More Detailed Prompts Improved Auditability More Than Raw Determinism

Adding explicit boundary cases and evidence fields did not make the pipeline deterministic. DeepSeek still had 15.5-18.1% three-way mismatch on the 116-record hard set. However, the changes made disagreement interpretable. Instead of opaque label flips, we can identify whether the disagreement concerns wrapper status, text component, text-bio bridge, generative mechanism, or thin abstract evidence.

This is a substantial methodological improvement. In evidence synthesis, knowing why a record is unstable is as important as knowing that it is unstable, because instability can trigger human adjudication or full-text retrieval.

### 8.2 Scope Restrictions Shifted Instability From INCLUDE to UNCERTAIN/EXCLUDE Boundaries

The original full-corpus baseline had INCLUDE Jaccard 0.587 despite only 7.3% overall mismatch. After scope refinements, DeepSeek's INCLUDE Jaccard on the enriched 116-record regression set rose to 0.825-0.868. The completed current full-corpus rerun confirmed the same direction of effect on the complete corpus: INCLUDE Jaccard increased to 0.806, while overall mismatch decreased to 5.8%.

The improvement is most visible in unstable INCLUDE membership. In the original full-corpus replicate, 63 records were included by at least one run but only 37 were included by both, leaving 26 unstable include-union records. In the current full-corpus replicate, 36 records were included by at least one run and 29 were included by both, leaving only 7 unstable include-union records. This suggests that detailed scope boundaries helped stabilize what counts as a positive include.

However, disagreement did not disappear. It moved mostly to the EXCLUDE/UNCERTAIN boundary. This is expected when the prompt becomes more conservative: instead of over-including or over-excluding underspecified abstracts, the model exposes uncertainty.

### 8.3 The UNCERTAIN Class Is Methodologically Useful but Statistically Unstable

UNCERTAIN Jaccard was low across all experiments:

- current full-corpus DeepSeek UNCERTAIN Jaccard: 0.627;
- DeepSeek 116 pairwise UNCERTAIN Jaccard: 0.310-0.400;
- GPT-OSS 116 UNCERTAIN Jaccard: 0.286;
- cross-model UNCERTAIN Jaccard: 0.150-0.200.

This does not mean UNCERTAIN is useless. It means UNCERTAIN is a safety state at the decision boundary. The class is sensitive to how much evidence a model demands before excluding or including. Therefore, UNCERTAIN should not be used as a final automatic exclusion. It should be treated as a routing signal for manual review, full-text retrieval, or consensus adjudication.

### 8.4 Agent Role Separation Helps Diagnose Disagreement

Keeping the scope reviewer and architecture reviewer separate was valuable. Many disagreements were criterion-local:

- scope-positive but architecture-unclear;
- text-bio bridge unclear but generative evidence positive;
- primary model paper but wrapper risk;
- generative model claimed but final task predictive.

A monolithic single-agent classifier would collapse these distinctions into a final label. The multi-agent format allowed us to distinguish label instability from criterion instability.

### 8.5 Cross-Model Differences Are Larger Than Some Within-Model Differences

GPT-OSS was more stable internally than DeepSeek, but it was more liberal. DeepSeek was more conservative and used UNCERTAIN more often. Cross-model mismatch reached 19.8-24.1%, and cross-model INCLUDE Jaccard was only 0.647-0.700.

This means model choice is itself a review design parameter. Reporting only one model's screening output would hide a material source of corpus drift.

## 9. Recommended Reporting Package for Our Review

Based on the reproducibility brief and our experiments, the review should report:

- exact model identifiers and serving stack;
- dates of runs;
- full prompt files and response schema;
- temperature, seed, max tokens, context length, max batched tokens, and max sequences;
- whether thinking/reasoning mode was enabled;
- local backend details, including vLLM version, hardware, GPU count, MTP/speculative decoding, and reasoning parser;
- repeated-run counts;
- pairwise mismatch rates;
- class-specific Jaccard for INCLUDE, EXCLUDE, and UNCERTAIN;
- transition matrices;
- stable INCLUDE and include-union counts;
- unstable record tables with agent rationales;
- full handling policy for UNCERTAIN and unstable records.

## 10. Conclusion

Our experiments support the central claim of the reproducibility brief: LLM-assisted title/abstract screening should not be treated as a deterministic classifier, even with fixed prompts, fixed seed, and deterministic-style settings. In our review, repeated DeepSeek runs and cross-model comparisons produced materially different screening decisions, especially around scientifically meaningful boundaries.

The strongest practical finding is class-specific. `INCLUDE` stability improved substantially after prompt and schema refinement. In the full 4,027-record corpus, DeepSeek INCLUDE Jaccard increased from 0.587 in the original replicate to 0.806 in the current pipeline replicate, while overall mismatch decreased from 7.3% to 5.8%. The harder 116-record regression set showed the same pattern at a boundary-enriched scale: DeepSeek INCLUDE Jaccard was 0.825-0.868 across three pairwise repeat comparisons. However, overall three-way stability remained limited because `UNCERTAIN` is inherently unstable and sits between strict exclusion and conservative retention. GPT-OSS was more repeatable but more liberal, while DeepSeek was more conservative but less stable around EXCLUDE/UNCERTAIN decisions.

The pipeline should therefore be framed as a reproducibility-aware triage system. Stable INCLUDE records can be treated with higher confidence. Stable EXCLUDE records are plausible exclusions only when the exclusion rationale is criterion-grounded. Records that are included, uncertain, or unstable in any run should be retained for human adjudication or full-text inspection. This design is more scientifically defensible than relying on a single LLM run, and it turns nondeterminism from a hidden validity threat into a measurable property of the screening process.

## Appendix A. Artifact Locations

- Extracted reproducibility brief text: `runs/reproducibility_llm_screening_paper.txt`
- Current 3-DeepSeek/2-GPT agreement analysis: `analysis/cross_agent_screening_agreement_current_3ds_2gpt/`
- Prompt appendix with the complete operative prompt stack: `analysis/cross_agent_screening_agreement_current_3ds_2gpt/manuscript_appendix_c_prompts.md`
- Current full-corpus DeepSeek replicate agreement: `analysis/current_full_deepseek_replicate_agreement/`
- Pairwise metrics table: `analysis/screening_reproducibility_pairwise_metrics.csv`
- Consensus metrics table: `analysis/screening_reproducibility_consensus_metrics.csv`
- Original cross-agent analysis: `analysis/cross_agent_screening_agreement/`
- Regression cases: `protocol/screening_prompt_regression_cases.csv`
- Operative runtime prompt templates: `protocol/screening_prompt_templates/`

## Appendix B. Key Sources From the Brief

- Beyond Accuracy: LLM Variability in Evidence Screening for Software Engineering SLRs. `https://arxiv.org/html/2604.27006v1`
- Evaluating the effectiveness of large language models in abstract screening: a comparative analysis. `https://link.springer.com/article/10.1186/s13643-024-02609-x`
- PRISMA 2020. `https://www.prisma-statement.org/prisma-2020`
- Cochrane MECIR standards for study selection. `https://www.cochrane.org/authors/handbooks-and-manuals/mecir-manual/standards-conduct-new-cochrane-intervention-reviews-c1-c75/performing-review-c24-c75/selecting-studies-include-review-c39-c42`
