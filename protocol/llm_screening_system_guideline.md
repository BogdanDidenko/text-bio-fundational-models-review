# Guideline for Building the LLM-Assisted Screening System for This Review

## Purpose

This guideline translates the methodological lessons from three papers in
`protocol/llm_screening_methodology/` into a concrete system design for our
review:

- `jmir_prisma_trace_2025_methodology.md`
- `bmc_streamlining_sr_llm_2025_methodology.md`
- `cochrane_ai_position_statement_2025_methodology.md`

It is not a generic note on AI-assisted screening. It is a task-specific design
recommendation for this review of **text-bio foundational models**.

The core problem is not just "screen many papers faster." The core problem is
to reduce manual workload **without creating an unacceptable risk of false
exclusion** in a domain where title/abstract ambiguity is common and category
boundaries are unusually unstable.

---

## 1. What The System Must Optimize For

The system should optimize for the following priorities, in this order:

1. **Protect recall**
- Missing a true in-scope text-bio foundation model paper is more damaging than
  retaining extra papers for manual review.

2. **Make decisions auditable**
- Every screening outcome must be reconstructable from prompt version, model
  version, criterion-level outputs, and human adjudication records.

3. **Separate ambiguity from irrelevance**
- Many difficult records in our domain are not truly negative; they are
  ambiguous at title/abstract level.
- The system must not collapse ambiguity into automatic exclusion.

4. **Support protocol-grade reporting**
- The system should be designed so that its use can be reported credibly under a
  PRISMA-trAIce-style logic and defended under a Cochrane/RAISE-style
  governance standard.

5. **Enable iterative improvement**
- The system must produce enough structured evidence to improve criteria,
  prompts, and benchmark design over time.

---

## 2. What The System Should Not Be

The screening system should **not** be built as:

- a one-shot `INCLUDE / EXCLUDE` classifier over title + abstract;
- an aggressive auto-exclusion engine optimized for workload reduction;
- a hidden prompt embedded only in code;
- a model-only workflow with vague "human in the loop" language;
- a full-text RAG system introduced before the title/abstract protocol is
  stable.

For this review, those designs are too brittle and too difficult to justify.

---

## 3. Recommended Overall Operating Model

The best operating model for this review is:

- **LLM-assisted, sensitivity-first, criterion-level screening**
- with **explicit `UNCERTAIN` retention**
- under **human oversight**
- backed by a **manual benchmark set**
- and governed by **prompt/version control and structured logging**

In practical terms, the system should behave more like a structured
decision-support workflow than a classifier.

---

## 4. Recommended Role Of The LLM

The LLM should be treated as:

- a **criterion evaluator**
- a **triage assistant**
- and, in some cases, a **second reviewer**

It should **not** be treated as a fully autonomous final decision-maker.

For our review, the safest initial framing is:

- The LLM may propose `INCLUDE`, `EXCLUDE`, or `UNCERTAIN`.
- `UNCERTAIN` always routes to manual review.
- `EXCLUDE` should be trusted only if the exclusion is criterion-specific and
  strongly evidenced from the abstract.
- borderline or disagreement cases should never be silently auto-excluded.

---

## 5. Recommended Decision Architecture

### 5.1 Criterion-First, Not Label-First

The prompt should ask the model to evaluate separate screening criteria rather
than directly output a single global label.

At minimum, the system should make the model answer these questions:

1. `paper_type`
- Is this a primary model/preprint paper, or a review/editorial/benchmark/
  application/resource paper?

2. `bio_modality_present`
- Does the paper actually work with biological data, not only biomedical text?

3. `text_component_present`
- Is there a genuine text/language component relevant to the review scope?

4. `text_bio_bridge_type`
- Does the paper show:
  - `Tier A`: explicit natural-language <-> biology bridge
  - `Tier B`: biological-token generative exception
  - `Tier C`: language-adjacent but not sufficient
  - `unclear`

5. `architecture_type`
- Is the architecture generative, encoder-only, wrapper-like, or unclear?

6. `foundation_model_evidence`
- Does the abstract provide evidence of broad pretraining, reusable
  representations, or foundation-model positioning?

7. `administrative_flags`
- English, duplicate, obvious review article, etc.

8. `final_decision`
- `INCLUDE`, `EXCLUDE`, or `UNCERTAIN`

9. `decision_reason`
- Short evidence-grounded explanation

10. `primary_exclusion_code`
- `EC1`-`EC8`, and optionally an internal operational tag for
  `benchmark/resource paper`

### 5.2 Why This Structure Fits Our Task

This architecture is recommended because our difficult cases usually fail on one
specific dimension:

- no real text-bio bridge;
- encoder-only token model;
- wrapper around an existing LLM;
- benchmark/resource rather than model paper;
- insufficient evidence of foundation-model status.

A one-label decision hides these distinctions. A criterion-level design exposes
them.

---

## 6. Recommended Uncertainty Policy

`UNCERTAIN` should be a deliberate and protected state.

### 6.1 When To Use `UNCERTAIN`

The system should return `UNCERTAIN` when:

- the abstract does not clearly resolve whether the model is generative or
  encoder-only;
- the paper may be a wrapper or application paper rather than a candidate model
  paper;
- the abstract suggests relevance but does not establish the text-bio bridge;
- the paper might satisfy the `Tier B` exception but evidence is too weak;
- the title/abstract is short, truncated, metadata-like, or otherwise
  insufficient.

### 6.2 What `UNCERTAIN` Means Operationally

`UNCERTAIN` should mean:

- retain the record;
- send to manual review or adjudication;
- log the uncertainty type;
- do not treat it as prompt failure.

This is the correct policy for our domain because many hard cases are genuinely
abstract-insufficient.

---

## 7. Recommended Benchmark Design

The benchmark set should be built **before** trusting any model/prompt on the
live corpus.

### 7.1 Benchmark Purpose

The benchmark is not only for measuring performance. It is also for:

- clarifying protocol ambiguities;
- testing whether the prompt operationalizes the protocol correctly;
- identifying which criteria are most unstable;
- justifying the use of AI in the first place.

### 7.2 Recommended Benchmark Structure

The benchmark should contain:

- clear `Tier A` positives;
- clear `Tier B` positives;
- clear review/editorial negatives;
- clear bio-only or text-only negatives;
- clear encoder-only negatives;
- wrapper/application negatives;
- benchmark/resource negatives;
- deliberately selected borderline `UNCERTAIN` cases.

### 7.3 What To Label

Each benchmark record should have:

- `expected_final_decision`
- `expected_paper_type`
- `expected_text_bio_bridge_type`
- `expected_architecture_type`
- `expected_foundation_model_status`
- `expected_primary_exclusion_code` if excluded
- `notes_for_adjudication`

### 7.4 Acceptance Logic

The system should be evaluated first on:

- false exclusion count
- recall on must-include papers
- agreement on clear negatives
- behavior on borderline papers

Workload reduction should be a secondary metric, not the primary gate.

---

## 8. Recommended Prompt Design

### 8.1 Prompt Format

The prompt should be:

- criterion-by-criterion;
- structured;
- explicit about the meaning of `Tier A`, `Tier B`, `Tier C`, and `UNCERTAIN`;
- explicit about strong exclusion signals and strong inclusion signals;
- explicit that ambiguity should favor retention, not exclusion.

### 8.2 Prompt Content Requirements

The prompt should include:

- the exact review scope;
- clear interpretation of IC2 for this review;
- explicit handling of `Tier B` as a protocol exception;
- explicit negative heuristics:
  - review/survey/editorial
  - benchmark/resource
  - encoder-only/MLM/BERT-style
  - bio-only multimodal
  - wrapper around an existing LLM
- explicit uncertainty rules;
- a structured JSON schema for outputs.

### 8.3 Prompt Governance

Every prompt version should have:

- `prompt_version`
- `prompt_hash`
- full prompt text
- few-shot examples if used
- model/provider
- inference parameters
- validation basis
- approval date

The operative prompt should not live only inside a script.

---

## 9. Recommended Reviewer Topology

For this review, the best near-term architecture is not a single reviewer.

### 9.1 Recommended Three-Role Topology

1. **Scope reviewer**
- focus: paper type, biological modality, text component, text-bio bridge tier

2. **Architecture reviewer**
- focus: generative vs encoder-only vs wrapper; FM evidence

3. **Adjudicator**
- only for disagreements or high-ambiguity cases

### 9.2 Why This Is Better Than One Reviewer

This separation matches the structure of our problem:

- one set of failures is about scope and paper type;
- another set is about architecture and FM status.

Splitting those tasks improves interpretability and should reduce brittle
all-at-once reasoning.

### 9.3 Conservative Aggregation Rule

Recommended aggregation:

- both reviewers clearly support inclusion -> `INCLUDE`
- both reviewers clearly support exclusion on compatible grounds -> `EXCLUDE`
- disagreement or weak evidence -> `UNCERTAIN` or adjudicator review

The aggregation policy should be conservative by design.

---

## 10. Recommended Logging And Audit Trail

The system should log more than the final decision.

### 10.1 Minimum Recommended Fields

- `record_id`
- title/abstract snapshot
- `llm_model`
- `llm_provider`
- `model_version`
- `run_id`
- `prompt_version`
- `prompt_hash`
- `reviewer_role`
- criterion-level outputs
- criterion-level rationales
- `final_ai_decision`
- `final_ai_exclusion_code`
- `confidence`
- `uncertainty_type`
- `raw_output_path`
- `postprocess_version`
- `human1_decision`
- `human2_decision`
- `consensus_decision`
- `adjudicator_decision`
- `disagreement_type`
- `validation_basis`

### 10.2 Why This Matters

This level of logging is required for:

- debugging failures;
- prompt comparison;
- benchmark analysis;
- PRISMA-style reporting;
- post hoc audit of exclusions.

---

## 11. Recommended Governance And Safety Case

Before deployment on the live corpus, the repo should contain an explicit
justification for AI use.

### 11.1 What Must Be Justified

- why AI is being used at all;
- why this prompt/model is suitable for this review;
- what benchmark/calibration evidence supports deployment;
- what the main failure modes are;
- what the oversight policy is;
- what the acceptable risk level is.

### 11.2 Human Oversight Policy

The protocol should explicitly define:

- whether the LLM is first reviewer, second reviewer, or advisory tool;
- whether any records can be directly auto-excluded;
- which conditions force manual review;
- who resolves disagreements;
- when a prompt/model change requires revalidation.

### 11.3 Current Best Recommendation For Our Review

At the current stage, the safest policy is:

- no fully autonomous exclusion path for ambiguous records;
- `UNCERTAIN` and reviewer disagreement both route to manual review;
- prompt/model revisions require benchmark re-evaluation;
- all live screening runs must be reproducible from stored artifacts.

---

## 12. Recommended Use Of Full-Text RAG

Full-text RAG should **not** be part of the first stable version of this
system.

### 12.1 Why Not Yet

The title/abstract layer is still where our main ambiguity lives:

- Tier interpretation
- architecture identification
- paper-type discrimination
- wrapper vs model distinction

Adding full-text RAG now would increase complexity before the first-stage logic
is stable.

### 12.2 When It Becomes Justified

Full-text RAG should be considered only if:

- title/abstract screening is stable and benchmarked;
- we can identify a recurring class of abstract-insufficient papers;
- we create a separate benchmark for those cases;
- retrieval can surface evidence relevant to our criteria, not just arbitrary
  chunks.

So full-text RAG is a **second-stage module**, not a default foundation for the
system.

---

## 13. Recommended Rollout Plan

### Phase 1 — Protocol Stabilization

- finalize Tier interpretation and criterion wording;
- finalize benchmark schema;
- formalize `UNCERTAIN` policy;
- formalize logging schema.

### Phase 2 — Prompt And Reviewer Design

- implement criterion-level prompt;
- implement structured output schema;
- implement two-reviewer + adjudicator topology;
- add prompt versioning and run manifests.

### Phase 3 — Benchmark Validation

- run on curated benchmark set;
- inspect false exclusions first;
- refine criteria and prompt;
- document acceptance decision.

### Phase 4 — Limited Pilot On Corpus

- run on a small real subset;
- audit disagreement patterns;
- inspect criterion-level failure modes;
- confirm logging and reproducibility.

### Phase 5 — Full Screening

- deploy only after benchmark acceptance;
- preserve manual review path for `UNCERTAIN` and disagreements;
- report the system as an AI-assisted, human-supervised workflow.

---

## 14. Final Recommendation

For this review, the correct system is:

- **not** a binary title/abstract classifier,
- **not** an aggressive auto-exclusion tool,
- **not** a full-text-first RAG pipeline.

It should be:

- a **criterion-based**
- **sensitivity-first**
- **human-supervised**
- **benchmark-validated**
- **fully logged and reportable**
screening system.

In practice, that means:

- criterion-level prompts;
- explicit `Tier A / Tier B / Tier C / unclear` handling;
- explicit `UNCERTAIN` retention;
- separate scope and architecture review logic;
- strong prompt/version governance;
- benchmark-first deployment;
- no silent exclusions under ambiguity.

That is the design most consistent with the empirical screening literature, the
reporting literature, and the governance literature we have reviewed, and it is
the design best matched to the unusually ambiguous taxonomy of this review.
