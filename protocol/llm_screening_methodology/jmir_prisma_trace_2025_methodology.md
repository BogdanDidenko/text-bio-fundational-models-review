# PRISMA-trAIce (Holst et al., 2025)

## 1. Full citation

Holst D, Moenck K, Koch J, Schmedemann O, Schuppstuhl T. *Transparent Reporting of AI in Systematic Literature Reviews: Development of the PRISMA-trAIce Checklist*. **JMIR AI**. 2025;4:e80247. doi: [10.2196/80247](https://doi.org/10.2196/80247)

## 2. Why this paper matters for AI-assisted screening

This paper matters because it addresses a gap that is directly relevant to our pipeline: not whether AI can help with systematic reviews, but how AI-assisted review work must be documented if the resulting review is supposed to remain reproducible, auditable, and methodologically defensible.

For our project, that is a first-order issue. We are not only trying to improve title/abstract screening efficiency; we are also creating a review process that may later need to justify why a given record was excluded, which prompt version was used, which model produced the output, how humans verified it, and what happened when the model and reviewers disagreed. PRISMA-trAIce is valuable because it converts those concerns from vague "good practice" into a reporting structure tied to the familiar PRISMA workflow.

Its main importance is governance and traceability, not screening performance. The paper does not show that any LLM is accurate enough for safe exclusion in our domain. What it does provide is a concrete specification of what we would need to record and report if we want an LLM-assisted screening workflow to be credible.

## 3. Detailed summary of the paper

The paper proposes PRISMA-trAIce, a reporting extension for systematic literature reviews in which AI is used as a methodological tool. The authors position it against a clear gap: existing AI reporting guidance mainly covers studies in which AI is the object of study or intervention, whereas AI-assisted systematic review workflows need guidance for reporting AI as part of the review process itself.

The checklist was not generated de novo through a Delphi process. Instead, the authors used a targeted literature review of established AI reporting guidelines, primarily from the EQUATOR ecosystem and related consensus-style frameworks. The core sources they selected for adaptation were CONSORT-AI, SPIRIT-AI, TRIPOD-AI, TRIPOD-LLM, DECIDE-AI, and GAMER. They then extracted reporting items, performed qualitative content analysis, and retained items that were relevant to reproducibility, feasibility, and adaptation to systematic review practice. Items that were not relevant to AI as a review tool, such as patient-safety items for clinical interventions, were excluded. The retained concepts were thematically synthesized and mapped onto the PRISMA 2020 structure.

The main outputs are:

- a PRISMA-trAIce checklist covering title, abstract, introduction, methods, results, and discussion;
- an adapted PRISMA flow diagram that separates AI-driven and human-driven screening decisions;
- a proposal to treat PRISMA-trAIce as a living, community-refined standard rather than a static one-off publication.

The checklist logic is the core contribution. It asks authors to report, at minimum:

- whether AI materially contributed to the review and where;
- which AI tools were used, how they were accessed, and in what exact stages/tasks;
- what inputs were provided to the tools and what outputs they produced;
- the actual prompts and generation settings used for LLMs or GenAI systems;
- how humans interacted with, validated, and overrode AI outputs;
- how AI performance was evaluated for the specific task in the review;
- how data governance, privacy, security, and copyright issues were handled;
- how AI-related limitations and implications affected the review.

The adapted flow diagram is especially relevant for screening. The authors argue that "automation tools" in the default PRISMA 2020 flow is too broad, because it conflates administrative automation such as deduplication with evaluative AI systems that participate in study selection. Their adapted diagram therefore distinguishes records screened or excluded by AI systems from those screened or excluded by human reviewers.

The paper is explicit that this is a proposal, not a validated final standard. The authors acknowledge that it has not undergone a broad Delphi consensus process or formal user testing. They therefore frame PRISMA-trAIce as a pragmatic, immediately usable starting point that should evolve through open, version-controlled community governance.

One practical note for reading the article carefully: the prose says the checklist "comprises 14 items," but the published table labels a larger set of reporting elements across T1, A1, I1, M1-M10, R1-R2, and D1-D2. For operational use, the labeled elements in Table 1 are more important than the headline count.

## 4. Methodological contribution in detail

The paper's real methodological contribution is not a new screening algorithm. It is a reporting architecture for AI-assisted evidence synthesis. That contribution is important precisely because AI-assisted screening often fails at the level of traceability before it fails at the level of model quality.

### 4.1 Reporting and governance contribution

PRISMA-trAIce extends PRISMA 2020 in a way that forces the review team to make hidden workflow assumptions explicit.

First, it formalizes protocol-level accountability. Under P-trAIce M1, AI use should be prespecified in the protocol where possible, and deviations from the original plan should be reported. For our project, this means prompt changes, model substitutions, or moving from single-model to dual-model adjudication should not be treated as silent implementation details.

Second, it requires exact tool identification and access information under M2. That includes name, version, provider, and access pathway. This is more demanding than saying "we used an LLM." For a screening pipeline, reproducibility depends on whether the run used, for example, a hosted API model, a local checkpoint, or a wrapper service with its own transformations.

Third, it separates purpose and stage of use under M3. This matters because the methodological risk profile differs across tasks. Deduplication, title/abstract triage, full-text extraction, and draft writing should not be reported as a single undifferentiated "AI-assisted review" activity.

Fourth, it makes prompting and post-processing first-class protocol artifacts. M4 through M7 require authors to report the data fed to the model, the output format, any automated post-processing, the full prompt or prompt structure, key generation parameters, and iterative prompt refinement. This is directly relevant to our current prompt workflow: a summarized prompt description is not enough if the actual operational prompt changes over time.

Fifth, and most importantly for review governance, M8 requires explicit reporting of human-AI interaction and oversight. The paper does not treat human review as a generic safety blanket. It asks who validated AI outputs, whether reviewers worked independently, what training or qualifications they had, how outputs were presented, what fraction of outputs were manually verified, how discrepancies were resolved, and whether there was calibration.

Sixth, M10 extends the methodology into data governance and ethics. The authors require explicit reporting of how AI input, output, and intermediate data were stored and governed, especially when third-party cloud systems are used.

### 4.2 Performance and evaluation contribution

The paper is careful to include performance evaluation, but only as task-specific evaluation of the AI component inside the review workflow. That distinction is important.

Under M9 and R2, teams should report:

- the reference standard used to evaluate the AI component;
- the metrics used;
- analyses of erroneous outputs or bias;
- pilot or validation phases before full deployment;
- quantitative results and agreement with human reviewers.

This is methodologically useful because it prevents teams from claiming "AI assistance" without specifying whether the system was ever validated for the task it performed. However, the paper deliberately stops short of telling teams what thresholds are acceptable. It does not define the minimum recall required before AI can exclude records, the acceptable false-exclusion rate, or the size of a sufficient validation set. Those decisions remain the responsibility of the review team.

### 4.3 Screening-flow contribution

The adapted flow diagram contributes a specific logic that is directly actionable for title/abstract screening. It says the review should be able to report not just how many records were screened, but how many were processed by AI, how many were excluded on the AI side versus the human side, and how the screening path differed when AI participated in decision-making. This is not a cosmetic diagram change. It forces the pipeline to preserve provenance for each decision.

## 5. Strengths

- It fills a real methodological gap: AI as a review tool is different from AI as a study object, and existing guidelines do not adequately cover that distinction.
- It maps cleanly onto PRISMA 2020, which makes it easier to integrate into existing systematic review workflows instead of inventing a parallel reporting system.
- It treats prompt engineering, model configuration, post-processing, and access pathway as reproducibility-critical details rather than informal implementation notes.
- It gives unusually strong attention to human-AI interaction, reviewer independence, calibration, and discrepancy resolution, which are exactly the weak points in many LLM-assisted screening setups.
- It separates governance/reporting requirements from performance reporting. That is useful because teams often mix "we logged the run" with "the system is safe to use"; this paper clearly implies those are different questions.
- The adapted flow diagram is practically valuable because it aligns reporting logic with how screening pipelines actually fail or drift: at the level of exclusions, overrides, and provenance.

## 6. Limitations and what the paper does not establish

- It is a proposal, not a consensus standard. The authors explicitly state that it was not produced through a formal Delphi or similar large-scale consensus process.
- It is not empirically validated through user studies across multiple review settings, disciplines, or software environments.
- It does not benchmark screening performance. There is no evidence here that a particular model, prompt structure, or human-AI configuration is accurate enough for our title/abstract task.
- It does not specify operational thresholds. It tells us to report the reference standard and metrics, but not what recall, sensitivity, or false-exclusion rate should be considered acceptable.
- It does not solve prompt design. It requires prompt disclosure and refinement reporting, but it does not tell us how to construct a high-recall screening prompt for borderline multimodal computational-biology papers.
- It does not resolve disagreement policy. It requires that disagreements be reported and the process described, but it does not say whether AI-human disagreement should trigger second review, consensus discussion, or automatic escalation.
- It does not provide a ready-made schema for data storage, prompt registry, or audit-log design. Those have to be implemented locally.
- The checklist count is editorially unclear in the published article. That does not invalidate the framework, but it reinforces that teams should use the actual reporting elements rather than relying on the headline summary.

For our team, the main implication is that PRISMA-trAIce should be treated as a governance and reporting scaffold, not as evidence that our current screening configuration is validated.

## 7. Concrete implications for our review workflow

### Prompt versioning

This paper implies that prompt versioning must move from informal documentation to controlled protocol metadata. In the current repo, [screening_prompt.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/screening_prompt.md) summarizes the logic of prompt `v0.1`, but it also states that the actual system prompt is embedded in `scripts/screen_test.py`. Under PRISMA-trAIce M6, that is not enough. We need the operative prompt text, prompt version, prompt hash, few-shot examples, generation parameters, and refinement history to be accessible as review artifacts.

### Audit trail

The paper strongly supports a much richer screening trace than our current output schema. [screening_process.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/screening_process.md) currently describes `data/screening_log.csv` with only `record_id`, source metadata, phase decisions, codes, and notes. That is too thin for PRISMA-trAIce. A defensible audit trail should preserve at least the input record snapshot, AI raw output, parsed output, post-processing version, final human decision, and discrepancy reason.

### Human-AI interaction

PRISMA-trAIce M8 is directly relevant to our workflow design. We need to define who reviews AI outputs, whether they review independently, whether they see the AI rationale before or after making their own judgment, and when adjudication is required. Without that, "human oversight" remains too vague to be credible.

### Validation basis

The paper does not validate our pipeline, but it makes validation basis non-optional. Our current prompt note proposes a calibration set of about 30 records, which is a good start for prompt iteration. Under PRISMA-trAIce logic, however, that pilot must be described explicitly as the reference standard for validation, along with the sampling logic, performance metrics, known weak subtypes, and the decision rule for accepting or rejecting a prompt/model revision.

### Disagreement handling

The paper makes discrepancy handling a reporting obligation. That means AI-human disagreement and human-human disagreement both need explicit procedural rules. In our context, the safest interpretation is: AI disagreement should never silently collapse into an exclusion. It should produce either `UNCERTAIN` or formal adjudication, with the final decision and disagreement category logged.

### Transparency in PRISMA reporting

Our current [prisma_flow_template.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/prisma_flow_template.md) is still essentially a standard PRISMA template. If title/abstract screening is materially AI-assisted, the flow representation should distinguish:

- records screened by AI;
- records excluded by AI at title/abstract stage;
- records reviewed or overridden by humans;
- records escalated to `UNCERTAIN` and sent to manual review.

### Data governance

The paper also matters for how we use external model providers. If we screen via a hosted API or routing service, we should document what data leave the repo, whether only title/abstract text are transmitted, how outputs are stored, and what terms-of-service or retention assumptions apply. This is especially relevant if we later extend beyond abstracts to full-text screening.

## 8. Specific repo/process changes we should consider

- Upgrade [screening_prompt.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/screening_prompt.md) from a descriptive note into a versioned prompt record. Each version should include full prompt text, model, provider, parameters, few-shot examples, prompt hash, validation basis, and approval date.
- Add an explicit AI-assisted screening subsection to [screening_process.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/screening_process.md) describing reviewer roles, independence, visibility of AI output, escalation rules for `UNCERTAIN`, and adjudication procedure.
- Expand the screening log schema beyond final labels. Recommended additional columns include `llm_model`, `llm_provider`, `model_version`, `prompt_version`, `prompt_hash`, `run_id`, `raw_output_path`, `postprocess_version`, `ai_decision`, `ai_code`, `ai_confidence`, `ai_reason`, `human1_decision`, `human2_decision`, `consensus_decision`, `disagreement_type`, `adjudicator`, and `validation_basis`.
- Add a dedicated validation note or manifest for screening runs. This should state the calibration set used, who labeled it, what counts as the reference standard, which metrics were checked, and what acceptance rule justified deployment.
- Treat prompt revisions and model substitutions as protocol deviations unless prespecified. Those changes should be reflected in [PRISMA_protocol.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/PRISMA_protocol.md), not only in implementation notes.
- Update [prisma_flow_template.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/prisma_flow_template.md) so the title/abstract stage can separate AI-assisted exclusions from human exclusions and record how many items moved into manual review because of uncertainty or disagreement.
- Add a short data-governance note covering what text is sent to external services, whether identifiers are included, where raw outputs are stored, and which retention/security assumptions apply.
- Formalize disagreement taxonomy for this review. At minimum, distinguish `ai_vs_human`, `human_vs_human`, `model_vs_model`, and `insufficient_abstract_information`. This is a practical extension of the paper's requirement to describe discrepancy handling.
- Preserve `UNCERTAIN` as an intentional review state rather than a residual error class. PRISMA-trAIce does not prescribe this label, but its human-oversight logic strongly supports using it as the default sink for ambiguity rather than forcing confident exclusion.

## 9. Bottom-line assessment for our project

This is one of the most important methodological papers in our screening-methodology folder, but not because it proves LLM screening works. It matters because it defines what a serious, review-grade AI-assisted screening pipeline must be able to explain after the fact.

For our project, PRISMA-trAIce should shape the infrastructure around screening more than the classifier itself. It tells us that prompt versioning, audit trail depth, human-AI interaction design, validation basis, disagreement handling, and PRISMA-level transparency are not optional polish. They are part of the method. If we follow that logic, our pipeline becomes much more defensible even before we finish optimizing prompt quality.

The right operational reading is therefore: use this paper as the reporting and governance backbone for the repo, then combine it with empirical screening papers and our own calibration results to decide what the model is actually allowed to do.
