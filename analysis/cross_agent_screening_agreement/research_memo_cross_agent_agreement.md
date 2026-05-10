# Cross-Agent and Cross-Model Agreement: Research Memo

## Why This Matters

The regression experiment shows that LLM-assisted screening is not simply a deterministic label assignment problem. Even with the same input records, same prompt stack, same model family, and fixed operational settings, repeated runs can disagree on eligibility. More importantly, different LLMs can move the inclusion frontier in systematic ways.

This is methodologically important for evidence synthesis because the main failure mode is not random formatting error. The disagreement concentrates around eligibility boundaries that are already scientifically meaningful:

- application wrapper vs primary model paper;
- biological-token-only "language" model vs natural-language text-bio model;
- generative model vs predictive, classificatory, or retrieval model;
- text-derived metadata or embeddings as core conditioning vs preprocessing side features;
- thin or truncated abstracts with insufficient evidence.

These are exactly the cases where an automated reviewer can shape the final corpus.

## Current Quantitative Signal

On the 116-record regression set:

- DeepSeek V4 Flash, repeat 1 vs repeat 2:
  - mismatch: 21/116 = 18.1%;
  - INCLUDE Jaccard: 0.868;
  - stable INCLUDE: 33, include union: 38.
- GPT-OSS 120B, repeat 1 vs repeat 2:
  - mismatch: 8/116 = 6.9%;
  - INCLUDE Jaccard: 0.920;
  - stable INCLUDE: 46, include union: 50.
- DeepSeek repeat 1 vs GPT-OSS repeat 1:
  - mismatch: 24/116 = 20.7%;
  - INCLUDE Jaccard: 0.694.
- DeepSeek repeat 2 vs GPT-OSS repeat 2:
  - mismatch: 28/116 = 24.1%;
  - INCLUDE Jaccard: 0.647.

The interpretation is not "GPT-OSS is better" in a simple sense. GPT-OSS is more repeatable here, but also more liberal: it produces many more INCLUDE decisions and fewer UNCERTAIN decisions. DeepSeek is more conservative, but less repeatable, especially across EXCLUDE/UNCERTAIN boundaries.

## Reasoning-Path Patterns

### 1. Wrapper Boundary Drift

**Example: GeneGPT**

Decisions: `EXCLUDE | EXCLUDE | EXCLUDE | INCLUDE`.

DeepSeek and GPT-OSS repeat 1 treat GeneGPT as an application wrapper: it augments an existing LLM with NCBI API calls and tool use rather than proposing a primary text-bio foundation model.

GPT-OSS repeat 2 flips to INCLUDE by emphasizing the augmented decoding algorithm and question-answering capability. The reasoning path shifts from "wrapper around Codex/tools" to "novel method with generative answering and biomedical tasks."

This is a clear example where a model can over-credit tool-augmented LLM usage as a primary model contribution. For the review, this suggests wrapper boundaries must be explicitly audited, not only prompt-specified.

### 2. Text-Derived Metadata Boundary

**Example: GEM-1 / "Generative genomics accurately predicts cancer gene expression"**

Decisions: `EXCLUDE | UNCERTAIN | INCLUDE | INCLUDE`.

DeepSeek repeat 1 excludes because it treats the LLM metadata agent as preprocessing, not as a substantive text component. DeepSeek repeat 2 becomes UNCERTAIN because the abstract does not clearly establish whether LLM-processed metadata is core text conditioning.

GPT-OSS includes in both runs by treating LLM-processed experimental metadata and foundation-model embeddings as a substantive text-bio bridge.

This is one of the strongest methodological findings: "text-derived metadata" is not a stable category. The same abstract can be read as:

- a biological generative model with metadata preprocessing;
- a text-conditioned generative genomics model;
- an underspecified case requiring UNCERTAIN.

This boundary should likely be discussed as a distinct source of screening uncertainty.

### 3. Generative-vs-Predictive Ambiguity

**Example: Med-PRSIMD**

Decisions: `EXCLUDE | EXCLUDE | INCLUDE | INCLUDE`.

DeepSeek excludes because the final task is disease risk prediction and the model output is not generative. GPT-OSS includes because the model uses causal language-model pretraining over medical history records and integrates text with bio/clinical data.

This shows a disagreement over whether a generative training objective is enough when the operational task is predictive. DeepSeek applies the review scope more strictly: prediction remains prediction unless generation is central to the candidate model. GPT-OSS is more willing to treat causal LM pretraining as sufficient generative evidence.

This is a candidate subsection in the paper: "generative architecture evidence vs generative review eligibility."

### 4. Biological Tokenization vs Natural Language

**Example: Cell2Sentence**

Decisions: `UNCERTAIN | EXCLUDE | INCLUDE | INCLUDE`.

DeepSeek treats "cell sentences" as biological token sequences, not necessarily natural-language text. GPT-OSS interprets conversion into sentences and GPT-2 fine-tuning as a text-bio bridge.

This is a central ambiguity for our review domain. The literature itself uses language metaphors for genes, cells, and omics tokens. Screening prompts must distinguish metaphorical language modeling from natural-language text-bio alignment. However, some methods deliberately put biological data into textualized forms for LLMs, so over-strict exclusion can also miss relevant papers.

### 5. Title/Abstract Thinness and Truncation

**Examples: BiomedGPT, ADAM-1, Gp-gpt**

DeepSeek often moves between INCLUDE, UNCERTAIN, and EXCLUDE when the title suggests a relevant model but the abstract is short or truncated. GPT-OSS is more willing to infer missing details from model names or broad claims.

This is a reproducibility risk: one model uses title-level signals as enough evidence, while another demands explicit abstract-level support. For a defensible review workflow, thin abstracts should probably be handled as UNCERTAIN unless the title and abstract jointly resolve all decisive criteria.

### 6. Generative Mechanism Interpretation

**Examples: Genolator, CellHermes, OpticalDNA**

These records fluctuate because "LLM", "decoder", "QA", "masked span completion", or "explanation" can be interpreted either as evidence of generative modeling or as insufficient without explicit generation.

GPT-OSS sometimes includes on the basis of a broad LLM framing and answer generation. DeepSeek sometimes demands explicit decoder/autoregressive/generation evidence, or treats the task as annotation/prediction/explanation rather than generative modeling.

This suggests that architecture-review prompts should separate:

- generative mechanism present;
- generative output central to the paper;
- downstream task is predictive/classificatory;
- foundation-model evidence.

## Emerging Methodological Claim

The experiment supports a broader claim:

> LLM screening decisions are sensitive not only to stochastic generation, but to unstable interpretation of eligibility boundaries. Repeated runs and different models may operationalize the same written criteria differently, especially for papers near conceptual boundaries.

For reporting, we should distinguish:

1. **Within-model repeatability**: same model, same prompt, same records.
2. **Cross-model agreement**: different models, same prompt and records.
3. **Include-set stability**: Jaccard similarity over INCLUDE records.
4. **Safety behavior**: whether ambiguous records move to UNCERTAIN or are forced into INCLUDE/EXCLUDE.
5. **Boundary-specific instability**: wrapper, text component, generative status, thin abstract.

## Practical Implications for Our Pipeline

The current evidence suggests:

- A single LLM run is not enough for a defensible automated screening claim.
- INCLUDE decisions are more stable than the overall three-way label space for DeepSeek, but still model-dependent.
- GPT-OSS may be useful as a high-recall second reader, but it needs a stricter wrapper/generative adjudication layer.
- DeepSeek may be useful as a conservative reviewer, but its EXCLUDE/UNCERTAIN instability means false exclusion risk should be monitored.
- UNCERTAIN should be treated as a deliberate safety state, not a failure mode.
- A consensus strategy could be:
  - INCLUDE if both models or repeated runs consistently include;
  - UNCERTAIN if models disagree between INCLUDE and EXCLUDE;
  - EXCLUDE only when repeated/model-diverse evidence is stable and exclusion rationale is criterion-grounded.

## Suggested Paper Section Structure

1. **Motivation: LLM screening is not deterministic evidence selection**
2. **Experimental setup: 116-record regression set, repeated runs, two models**
3. **Within-model repeatability**
4. **Cross-model corpus drift**
5. **Qualitative analysis of unstable reasoning paths**
6. **Mitigation strategies: UNCERTAIN, consensus, adjudication, boundary-specific prompts**
7. **Reporting recommendation: include repeatability and model-dependence metrics**

## Candidate Metrics to Report

- Overall three-way decision mismatch rate.
- INCLUDE Jaccard similarity.
- Stable INCLUDE count.
- Include-any vs include-all count.
- Transition matrix for EXCLUDE/INCLUDE/UNCERTAIN.
- Boundary-case counts by model/run.
- Disagreement rate by regression group.
- Qualitative case examples for each boundary failure mode.
