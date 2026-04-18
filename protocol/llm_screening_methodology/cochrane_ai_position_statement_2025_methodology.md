# Cochrane AI Position Statement (Flemyng et al., 2025)

## 1. Full citation

Flemyng E, Noel-Storr A, Macura B, Gartlehner G, Thomas J, Meerpohl JJ, Jordan Z, Minx J, Eisele-Metzger A, Hamel C, Jemioło P, Porritt K, Grainger M. *Position statement on artificial intelligence (AI) use in evidence synthesis across Cochrane, the Campbell Collaboration, JBI and the Collaboration for Environmental Evidence 2025*. Cochrane Database of Systematic Reviews. 2025;(11):ED000178. doi: [10.1002/14651858.ED000178](https://doi.org/10.1002/14651858.ED000178)

## 2. Why this paper matters for AI-assisted screening

This paper matters because it is not another model-performance paper. It is a cross-organization governance statement from four of the most methodologically conservative evidence-synthesis institutions: Cochrane, Campbell, JBI, and the Collaboration for Environmental Evidence. For an LLM-assisted title/abstract screening pipeline, that distinction is critical.

Empirical screening studies ask whether a tool appears accurate, efficient, or recall-preserving on a particular dataset. This paper asks a different question: under what conditions is AI use methodologically acceptable in evidence synthesis at all, who carries responsibility, what must be justified before use, and what must be reported after use. In other words, it does not tell us that our pipeline works; it tells us what burden of proof and documentation we must satisfy before claiming that its use is responsible.

For our project, this is especially important because the main open issues are not only technical. They are governance issues:

- what counts as an adequate validation basis for using an LLM in screening;
- what level of human oversight is required for exclusion-prone decisions;
- what error tolerance is acceptable for our review question;
- how to justify AI use as a protocol decision rather than an ad hoc convenience;
- how to report the pipeline transparently enough that others can audit it.

This paper is therefore best treated as a normative methodological anchor, not as evidence of screening accuracy.

## 3. Detailed summary of the paper

The article is an editorial position statement, published simultaneously across multiple evidence-synthesis journals, and explicitly aligned with the RAISE recommendations. Its core message is that AI and automation may be used in evidence synthesis, but only under conditions that preserve research integrity, methodological rigor, trustworthiness, and legal and ethical compliance.

The paper presents six headline messages.

- Evidence synthesists remain ultimately responsible for the synthesis, including the decision to use AI and the consequences of that use.
- The four organizations endorse the RAISE framework as the current basis for responsible AI use in evidence synthesis.
- AI use is acceptable only if authors can demonstrate that it does not compromise methodological rigor or integrity.
- AI should be used with human oversight.
- Any AI or automation that makes or suggests judgments should be transparently reported.
- AI tool developers should provide public, transparent information so that evidence synthesists can judge whether a system is fit for use.

The statement then operationalizes these principles in Table 1. This is the most methodologically useful part of the paper. It turns high-level principles into obligations for review authors.

First, the paper makes authors accountable not only for the synthesis content, methods, and findings, but also for the choice to use AI, the way it is used, and its impact on the review. This is an important shift away from the common implicit assumption that responsibility can be delegated to the software vendor, API provider, or model developer.

Second, it states that authors must be critical consumers of tool evaluation evidence. A tool is not acceptable merely because it exists, is popular, or is marketed for evidence synthesis. Authors are expected to examine whether it has been evaluated adequately, understand its limitations, and decide whether those evaluations are relevant to the specific synthesis context.

Third, the paper treats AI use as a protocol-level trade-off decision. Authors are asked to consider the context of the synthesis, who will use it, what it will be used for, how much error can be tolerated, and what risk-mitigation strategies are available. This is a much stronger position than "human-in-the-loop" rhetoric. It frames AI use as a methodological choice that must be justified in light of review stakes and acceptable risk.

Fourth, the statement specifies when AI use must be reported. The threshold is not "any use of software" but any AI use that makes or suggests judgments. The paper explicitly names eligibility decisions, risk-of-bias appraisal, data extraction, synthesis, certainty assessment, strength-of-evidence language, and plain-language summaries as examples. By contrast, routine language editing such as spelling or grammar correction usually does not require formal disclosure, subject to journal policy.

Fifth, the reporting expectations are concrete. Authors should report:

- the AI system, platform, version, and date used;
- the purpose of use and the synthesis stages affected;
- the justification for use, including evidence that the tool is methodologically sound and appropriate for the specific synthesis;
- how the tool was validated, piloted, or calibrated for the task;
- where practical, the relevant inputs, prompt development, outputs, datasets, and code;
- what steps were taken to verify AI-generated outputs;
- financial and non-financial interests related to the tool;
- limitations, including potential biases, and the likely impact of those limitations.

Sixth, the paper broadens the frame beyond technical performance. It explicitly includes plagiarism, provenance, copyright, intellectual property, jurisdiction, licensing, confidentiality, privacy, compliance, and data-protection obligations. It also notes social and environmental impacts of AI use, especially for large-scale language models.

Finally, the article gives a concrete example relevant to screening. It cites prior evidence that single-reviewer abstract screening can falsely exclude relevant studies at a meaningful rate and suggests that using AI as a second reviewer could, in some contexts, reduce that risk. Importantly, this is not presented as a blanket endorsement of AI screening. It is presented as an example of a context-sensitive trade-off in which AI might improve a known weak point in rapid review practice.

## 4. Methodological/governance contribution in detail

### 4.1 This is a governance paper, not an empirical accuracy paper

The most important methodological point is what the paper is not. It does not estimate LLM sensitivity, specificity, workload savings, prompt robustness, or false-exclusion rates on a benchmark corpus. It does not compare GPT-class systems against DistillerSR, Rayyan, ASReview, or human reviewers. It does not establish operating thresholds for safe deployment.

Its contribution is governance architecture. It defines the conditions under which AI-assisted review work can be regarded as acceptable and the evidentiary burden required before using such tools in consequential review tasks.

For our team, this means the paper should not be cited as support for pipeline accuracy. It should be cited as support for our governance model, justification structure, and reporting obligations.

### 4.2 Responsibility remains with the review team

The paper is unusually explicit that responsibility is not transferred to the AI tool. Authors remain accountable for:

- the content of the review;
- the methods used;
- the findings and conclusions;
- the decision to use AI;
- the way AI is used;
- the downstream impact of that use.

That responsibility model matters for screening because title/abstract decisions are not merely clerical. They are early gatekeeping judgments that can shape the review corpus. Under this framework, "the model excluded it" is not an acceptable explanation for a miss. If the pipeline excludes a relevant paper, the author team remains responsible for having chosen, validated, configured, and overseen that pipeline.

### 4.3 Acceptable AI use is conditional, not permissive by default

The statement does not prohibit AI use, but neither does it treat AI use as presumptively acceptable. The default standard is conditional permissibility: AI can be used only when the author team can demonstrate that the tool is methodologically sound, that its use is appropriate in the specific review context, and that it does not undermine the trustworthiness or reliability of the synthesis or its conclusions.

This is stronger than demonstrating raw task performance on a convenience dataset. It requires a contextual justification. A model can perform well on one benchmark and still be unjustified for another review if the topic, language mix, ambiguity profile, or consequence of false exclusions differs materially.

### 4.4 Justification is a methodological argument, not a product claim

One of the paper's strongest contributions is its treatment of justification. The authors frame the choice to use AI as an additional methodological trade-off during protocol development. The review team should explicitly consider:

- the purpose of the synthesis;
- the intended users of the synthesis;
- the consequences of errors;
- the review's risk tolerance;
- what mitigation measures are available if the tool fails.

This is directly relevant to our current issues.

- Validation basis: a benchmark or calibration set is not just a technical convenience; it is part of the justification for use.
- Human oversight policy: oversight is not satisfied by saying that humans exist somewhere downstream. It requires a defined supervisory structure for how AI decisions are checked, escalated, or overruled.
- Risk tolerance: acceptable automation in a rapid scoping context may be unacceptable in a high-sensitivity review where missing a mechanistically relevant text-bio foundation model would distort the evidence base.
- Transparent reporting: the justification must be visible to readers, not hidden in internal notes.

The paper also makes clear that relevance of prior evaluation matters. Validation evidence is more persuasive when the training, testing, and validation domains are similar to the target synthesis. Conversely, opaque models trained or evaluated on mismatched domains weaken the justification for use.

### 4.5 Human oversight is framed as active governance, not ceremonial review

The paper's language on human oversight is brief but consequential. Human oversight is not described as a superficial approval layer. It is the decision process by which authors choose whether to use AI, judge whether evidence is sufficient, calibrate or pilot the tool when needed, and verify outputs in context.

In practice, this implies several things for screening.

- Oversight begins before deployment, at protocol design and tool selection.
- Oversight includes local calibration or piloting if external evidence is insufficient.
- Oversight includes verification of AI outputs, especially where the AI makes or suggests eligibility judgments.
- Oversight must be proportional to risk. The higher the consequence of false exclusion, the more conservative the escalation policy should be.

This is fully consistent with a workflow in which `UNCERTAIN` is a deliberate manual-review state and ambiguous cases are escalated rather than forced into automated exclusion. It is much less consistent with an opaque auto-exclude pipeline that lacks a validated safety case.

### 4.6 Reporting expectations are much broader than naming the model

The paper is also methodologically important because it defines what transparent reporting should include. Reporting is not satisfied by writing "we used GPT-4 for screening." The statement expects a reproducible account of what tool was used, for what purpose, with what version/date, on which stage, with what justification, using what validation or piloting basis, under what verification procedures, and with what known limitations.

For LLM-based screening, that implies at minimum a documented trace of:

- model/provider/version and run date;
- prompts or decision schema used;
- intended role of the model in the workflow;
- benchmark or calibration basis for deployment;
- verification and adjudication steps;
- failure modes and residual risks;
- which decisions were made by AI, by humans, or by a hybrid process.

The paper does not specify a required schema, but it clearly implies that a bare methods sentence is insufficient for judgment-bearing AI use.

### 4.7 The tool-developer burden matters because tool opacity limits legitimate use

An underappreciated part of the paper is that it puts obligations on AI tool developers, not only on review authors. Developers are asked to provide public information on how tools work, their terms and conditions, the scope and domain of training/testing/validation data, and strengths, limitations, and biases.

This matters because many current LLM systems are commercially provided and partly opaque. The position statement does not excuse authors from the resulting uncertainty. Instead, it implies that if the tool is too opaque to evaluate adequately, that opacity itself weakens the case for using it in a judgment-bearing review stage.

For our project, this argues for conservative deployment unless we can compensate with strong local validation and careful documentation.

### 4.8 Ethical and legal governance is part of method, not an external add-on

The paper treats legal and ethical constraints as part of responsible evidence-synthesis method. This is not a separate compliance checklist after the fact. If abstracts, metadata, or full texts are sent to external systems, the review team must understand licensing, confidentiality, provenance, privacy, and jurisdiction implications.

For our workflow, this means model choice and hosting arrangement are themselves methodological decisions. A cloud API, a local model, and a vendor-managed screening platform are not interchangeable if they differ in auditability, data handling, or reproducibility.

## 5. Strengths

- The paper has high field-level legitimacy because it is a joint statement across major evidence-synthesis organizations rather than a single-team opinion piece.
- It correctly distinguishes responsible use questions from raw performance questions and therefore addresses the actual governance gap around LLM-assisted review methods.
- It puts responsibility unambiguously on the review team, which is methodologically clearer than narratives that treat AI as a neutral assistant.
- It gives concrete reporting elements rather than relying on vague calls for transparency.
- It treats justification as context-dependent, which is more realistic than assuming that a tool validated somewhere is automatically suitable everywhere.
- It includes legal, ethical, and data-governance issues that many technical screening papers treat superficially or ignore.
- It explicitly recognizes that human oversight requires upfront calibration, validation, and verification, not just retrospective confidence.

## 6. Limitations and what the paper does not establish

- It is not an empirical evaluation study and does not establish that any specific LLM-assisted screening workflow is accurate enough for deployment.
- It does not define quantitative acceptance thresholds for false exclusions, sensitivity, specificity, workload reduction, or agreement with human reviewers.
- It does not specify how large a calibration set should be, which metrics should govern deployment, or what minimum validation basis is sufficient for a particular screening task.
- It does not resolve how much human review is required for different risk classes of decisions. "Human oversight" is endorsed, but not converted into a precise operational policy.
- It does not provide domain-specific guidance for computational biology or multimodal foundation-model reviews, where abstracts are often technically ambiguous and architecture descriptions are underspecified.
- It does not tell us whether direct AI-driven exclusion is acceptable in our case; that depends on our own risk tolerance, validation evidence, and safeguards.
- It does not solve the reproducibility problems of proprietary LLMs; it only makes clear that such opacity must be considered in the justification.
- It relies heavily on the RAISE framework and points to future-evolving guidance, so it should be read as a current governance baseline rather than a complete final standard.

## 7. Concrete implications for our review workflow

The most important implication is that our LLM screening pipeline needs a formal safety case, not only a good prompt.

First, our current `validation_basis` problem should be treated as a governance gap. If we cannot show why a given prompt/model combination is acceptable for this review, then under the paper's logic we have not yet justified using it for judgment-bearing screening. Benchmark-first calibration is therefore not optional housekeeping. It is part of the methodological argument for deployment.

Second, our `UNCERTAIN -> manual review` rule should be treated as a core oversight control, not merely a convenience state. This paper strongly supports the idea that ambiguity should trigger escalation rather than overconfident automated exclusion. For our review topic, many records are borderline because abstracts may mention foundation models, multimodality, or LLM-like language without clearly establishing a genuine text-bio bridge or generative architecture. Those are exactly the cases where human oversight should be strongest.

Third, we need an explicit human oversight policy. At the moment, the repo contains conservative design ideas, but the governance statement implies we should formalize them. We should specify:

- whether the LLM acts as a first screener, second screener, triage tool, or advisory classifier;
- which records may be excluded automatically, if any;
- which conditions force manual review;
- who adjudicates disagreements or borderline cases;
- what verification is required before a prompt/model revision is used on the full corpus.

Fourth, the paper pushes us to state our risk tolerance explicitly. For this project, the cost of false exclusion is likely higher than the cost of extra manual review, because missing a small number of true in-scope text-bio foundation model papers could distort the final methodological map. That argues for a conservative operating point: prioritize recall, tolerate more `UNCERTAIN`, and require stronger evidence before allowing any automated exclusion path.

Fifth, our justification for AI use should be review-specific. The argument should not be "LLMs can screen papers." It should be something like: the corpus is large, title/abstract ambiguity is common, manual-only dual screening is resource-intensive, and we are using an LLM under a conservative escalation policy with local validation because the goal is to reduce workload without accepting unbounded false-exclusion risk.

Sixth, transparent reporting needs to be built into the workflow itself. If we only reconstruct prompts, versions, or oversight decisions after screening is complete, we will fail the standard this paper sets. Reporting fields must be captured during execution.

## 8. Specific repo/process changes we should consider

- Add an `AI use justification` subsection to [PRISMA_protocol.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/PRISMA_protocol.md) that states why LLM assistance is being used for title/abstract screening, what risks it introduces, why those risks are acceptable in this review, and what safeguards are in place.
- Add a formal `human oversight policy` to [screening_process.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/screening_process.md) defining the LLM's role, escalation triggers, manual adjudication rules, and whether any direct auto-exclusion is permitted.
- Expand the `data/screening_log.csv` schema described in [screening_process.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/screening_process.md) beyond final phase decisions to include model/provider/version, prompt version or hash, run date, decision source (`ai`, `human`, `hybrid`), AI rationale, human final rationale, reviewer/adjudicator identity or role, and verification status.
- Create a lightweight `validation note` or `run card` for each screening configuration documenting the benchmark set used, acceptance criteria, observed failure modes, unresolved risks, and the decision to deploy or not deploy that configuration.
- Treat [screening_benchmark_and_tiers.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/screening_benchmark_and_tiers.md) as part of the formal justification package rather than only an internal calibration note. It already encodes the most important task-specific ambiguity classes; the governance paper implies that such calibration artifacts should be cited in deployment decisions.
- Update [screening_prompt.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/screening_prompt.md) so that `UNCERTAIN` is explicitly framed as an oversight safeguard, not merely an output label.
- Add a prompt/model change-control rule: no silent model swap, provider change, or prompt rewrite should be used on the live corpus without a new validation entry and explicit sign-off.
- Add a short data-governance note describing what data are sent to the model, whether a cloud API is used, what reproducibility constraints follow from that choice, and which legal/licensing assumptions are being made.
- When writing the eventual methods section, report AI use as a judgment-bearing part of the screening process, with enough detail for external audit, rather than as a one-line tool mention.

## 9. Bottom-line assessment for our project

This is a high-value methodology paper for our repository, but its value is normative rather than empirical. It does not show that an LLM can safely screen our corpus. It shows that if we want to use an LLM for screening in a way that is defensible to the evidence-synthesis community, we need explicit justification, local validation, a documented human oversight policy, conservative risk management, and transparent reporting.

For our project, the paper supports a conservative design philosophy:

- benchmark before deployment;
- preserve `UNCERTAIN` as a real escalation state;
- make human accountability explicit;
- document why AI use is acceptable for this review rather than assuming it is;
- capture enough trace data that the workflow is auditable.

The practical takeaway is straightforward: this paper should constrain how we operationalize the pipeline and how we write the protocol. It should not be cited as evidence that the pipeline is accurate; it should be cited as evidence for the governance and reporting standard we are choosing to meet.
