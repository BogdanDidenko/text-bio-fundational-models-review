# Screening Benchmark And Criterion Schema

## Purpose

This note defines how to build the **manual benchmark set** and the
**criterion-level labeling schema** for our LLM-assisted title/abstract
screening workflow.

It has been rewritten to align the benchmark design more closely with the best
supported pattern in the literature:

- criterion-by-criterion screening;
- explicit uncertainty retention;
- conservative exclusion policy;
- structured logging and traceability.

This choice is based primarily on the BMC screening paper, and secondarily on
PRISMA-trAIce and the Cochrane/RAISE-style governance position.

Sources:

- [Trad et al. (2025)](https://doi.org/10.1186/s12874-025-02583-5):
  [bmc_streamlining_sr_llm_2025_methodology.md](llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)
- [Holst et al. (2025)](https://doi.org/10.2196/80247):
  [jmir_prisma_trace_2025_methodology.md](llm_screening_methodology/jmir_prisma_trace_2025_methodology.md)
- [Flemyng et al. (2025)](https://doi.org/10.1002/14651858.ED000178):
  [cochrane_ai_position_statement_2025_methodology.md](llm_screening_methodology/cochrane_ai_position_statement_2025_methodology.md)

---

## 1. Why The Benchmark Must Be Criterion-Based

### Recommendation

The benchmark should not contain only `INCLUDE / EXCLUDE` labels.

It should contain criterion-level labels for the main decision dimensions used
by the screening system.

### Why

This is the best match to the BMC-style screening design, where the model is
asked a sequence of explicit questions rather than asked for one global label.

For our task, this matters because hard records fail for different reasons:

- review vs primary model paper;
- real biology vs biomedical text only;
- real text-bio bridge vs superficial language mention;
- generative vs encoder-only;
- foundational vs wrapper/application.

If the benchmark stores only final decisions, we will not know which criterion
is unstable or whether the protocol itself is underspecified.

### Source support

- BMC paper: explicit question-by-question screening and structured logging.
  Source:
  [bmc_streamlining_sr_llm_2025_methodology.md](llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)
- PRISMA-trAIce: validation basis and auditable outputs must be reportable.
  Source:
  [jmir_prisma_trace_2025_methodology.md](llm_screening_methodology/jmir_prisma_trace_2025_methodology.md)

---

## 2. Recommended Benchmark Label Schema

Each benchmark record should have the following labels.

### Core labels

- `expected_final_decision`
- `expected_paper_type`
- `expected_bio_modality_present`
- `expected_text_component_present`
- `expected_text_bio_bridge_present`
- `expected_generative_model_present`
- `expected_foundation_model_evidence`
- `expected_primary_exclusion_code`
- `expected_uncertainty_reason`
- `adjudication_notes`

### Recommended values

#### `expected_final_decision`

- `INCLUDE`
- `EXCLUDE`
- `UNCERTAIN`

#### `expected_paper_type`

- `primary_model_paper`
- `review_editorial`
- `benchmark_resource`
- `application_wrapper`
- `unclear`

#### `expected_bio_modality_present`

- `yes`
- `no`
- `unclear`

#### `expected_text_component_present`

- `yes`
- `no`
- `unclear`

#### `expected_text_bio_bridge_present`

- `yes`
- `no`
- `unclear`

#### `expected_generative_model_present`

- `yes`
- `no`
- `unclear`

#### `expected_foundation_model_evidence`

- `yes`
- `no`
- `unclear`

#### `expected_primary_exclusion_code`

- `EC1`
- `EC2`
- `EC3`
- `EC4`
- `EC5`
- `EC6`
- `EC7`
- `EC8`
- optional internal operational tag:
  `benchmark_resource_not_candidate_model`

#### `expected_uncertainty_reason`

- `architecture_ambiguous`
- `paper_type_ambiguous`
- `text_bio_relation_ambiguous`
- `foundation_status_ambiguous`
- `abstract_insufficient`
- `multi_criterion_conflict`
- blank if not uncertain

---

## 3. Position On `Tier A / Tier B / Tier C`

### Recommendation

The benchmark should **not** be organized primarily around `Tier A / B / C`.

If we keep the tier language at all, it should only survive as a private mental
mapping to the single field `expected_text_bio_bridge_present`.

### Why

The tier framing helped us reason about IC2, but it is not what the literature
supports most directly.

The stronger literature-supported pattern is:

- explicit criterion questions;
- explicit uncertainty handling;
- structured reasoning per criterion.

That is the BMC-like logic we should align to.

### Practical translation

Instead of asking:

- "Is this Tier A, Tier B, or Tier C?"

The system should ask:

- "Is there a real text component?"
- "Is there a substantive text-bio bridge?"
- "Is the architecture generative?"

This is more transparent and easier to audit.

---

## 4. Recommended Benchmark Composition

### Target size

- `36-48` papers for the first stable benchmark

### Composition

#### Group P1 — Clear in-scope positives

- explicit text-bio bridge papers
- strong natural-language and biology interaction

Goal:

- ensure recall on the most canonical in-scope cases

#### Group P2 — Protocol-exception positives

- biological-token generative model papers

Goal:

- ensure the system preserves the explicit protocol exception rather than
  collapsing it into generic exclusion

#### Group N1 — Review/editorial negatives

Goal:

- test whether the pipeline can reject non-primary literature early

#### Group N2 — Bio-only negatives

Examples:

- multimodal omics papers with no text component
- bio-only foundation models

Goal:

- test EC2 cleanly

#### Group N3 — Encoder-only negatives

Examples:

- scBERT
- Geneformer
- scFoundation
- UCE

Goal:

- test EC3 cleanly

#### Group N4 — Wrapper/application negatives

Examples:

- papers that apply an external LLM to biology questions without introducing a
  genuine in-scope model

Goal:

- test EC4 and paper-type ambiguity

#### Group N5 — Benchmark/resource negatives

Examples:

- GeneTuring
- DART-Eval

Goal:

- test whether the system confuses evaluation papers with candidate model papers

#### Group U1 — Borderline uncertain cases

Examples:

- papers whose abstracts mention LLMs, metadata generation, or multimodal links
  but do not resolve architecture or scope cleanly

Goal:

- stress-test whether the system preserves uncertainty instead of over-excluding

---

## 5. Ground Truth Philosophy

### Recommendation

`ground_truth_models.md` should be treated as a **must-include recall anchor**,
not as a complete definition of scope.

### Why

The benchmark should be shaped by the review question and the screening
criteria, not only by a list of known positives.

### Practical implication

The benchmark must contain:

- known must-include papers;
- known must-exclude papers from multiple exclusion families;
- genuinely hard borderline records.

---

## 6. Acceptance Logic For The Benchmark

### Recommendation

The system should be accepted or rejected primarily on **false exclusion
control**, not on raw workload reduction.

### Primary evaluation criteria

- false exclusion count
- recall on must-include papers
- stability on borderline cases
- criterion-level consistency

### Secondary evaluation criteria

- agreement on clear negatives
- rate of `UNCERTAIN`
- expected manual workload

### Why

This follows directly from:

- BMC's sensitivity-first logic;
- Cochrane's requirement for context-specific risk tolerance;
- PRISMA-trAIce's requirement that validation basis be explicit.

---

## 7. How To Use This Benchmark In Practice

### Step 1

Manually adjudicate the benchmark before prompt tuning.

### Step 2

Run each prompt/model configuration on the benchmark and store:

- criterion outputs;
- final decision;
- reasons;
- disagreements.

### Step 3

Review failures by criterion, not only by final label.

### Step 4

Update prompt wording, criteria wording, or exclusion logic only after a
criterion-level review of the failures.

### Step 5

Promote a prompt/model configuration to pilot-corpus testing only if benchmark
behavior is acceptable under the sensitivity-first policy.

---

## 8. Bottom-Line Recommendation

The benchmark for this review should be built around the same core logic as the
recommended screening system:

- criterion-by-criterion;
- uncertainty-aware;
- conservative about exclusion;
- explicit about paper type and architecture;
- auditable.

This is a stronger and more literature-aligned foundation than a benchmark
organized primarily around our internal `Tier A / B / C` terminology.
