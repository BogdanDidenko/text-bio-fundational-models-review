# Trad et al. (2025) on LLM-Assisted Systematic-Review Screening: Methodological Review for Our Pipeline

## 1. Full citation

Trad F, Yammine R, Charafeddine J, Chakhtoura M, Rahme M, El-Hajj Fuleihan G, Chehab A. *Streamlining systematic reviews with large language models using prompt engineering and retrieval augmented generation*. **BMC Medical Research Methodology**. 2025;25:130. doi: [10.1186/s12874-025-02583-5](https://doi.org/10.1186/s12874-025-02583-5).

Source: see citation above. Local PDF/TXT references removed for portability.

## 2. Why this paper matters for AI-assisted screening

This paper is important because it validates a screening pattern that is much closer to how serious review teams actually work than a naive one-shot LLM classifier. The key move is not "ask GPT-4 whether to include the paper," but "translate the human screening guide into a sequence of criterion-level questions, require structured answers, and preserve uncertain cases for human review." That design choice is directly relevant to our current problems.

For our project, the paper matters in five specific ways.

First, it is explicitly sensitivity-first. The model is allowed to be uncertain, and uncertainty is operationalized as retention rather than exclusion. That is the correct framing for a review pipeline where false exclusions are more damaging than extra manual workload.

Second, it treats screening as a criterion-evaluation problem rather than a document-level label problem. This is exactly the direction we need for handling Tier ambiguity and borderline cases in our text-bio foundation-model review. Our hard cases are rarely "obviously irrelevant." They are usually ambiguous along specific dimensions: whether the paper genuinely combines text and biology, whether the model is generative rather than encoder-only, whether the work is foundational rather than a thin wrapper, and whether the article is a model paper versus a benchmark or application paper. A criterion-level design is much more auditable than a single include/exclude label.

Third, it shows that thresholding is not a minor implementation detail. In Rayyan, changing the exclusion threshold from a looser to a more conservative setting moved false negatives from 5% to 0%, but at a large cost in articles left for manual review. That is directly analogous to our own threshold choices around `EXCLUDE` versus `UNCERTAIN`.

Fourth, it separates title/abstract screening from full-text assistance. The paper does not argue that full-text RAG should replace careful title/abstract workflow design. Instead, it uses RAG only in a second phase after a structured title/abstract pass. That is the correct order for us as well.

Fifth, it demonstrates the value of criterion-level logging. The paper logs every question outcome to a spreadsheet, which creates an audit trail. For our workflow, this is not optional. Without question-level outputs, we cannot debug disagreement, benchmark failure modes, or refine inclusion rules.

## 3. Detailed summary of the paper

The study uses a completed umbrella review on vitamin D and falls as its reference task. According to the paper, the original review retrieved 17,776 citations. Results for 430 excluded articles were inadvertently not saved, leaving 17,346 records in the study dataset. After duplicate removal in Rayyan, 14,439 articles remained for title/abstract screening. In the original manual workflow, 1,680 full texts were reviewed and 20 systematic reviews of randomized controlled trials were ultimately included.

The paper compares three approaches against the completed manual review as the gold standard:

1. Traditional manual screening.
2. Rayyan AI for title/abstract screening only.
3. An in-house GPT-4 pipeline using prompt engineering for title/abstract screening and retrieval-augmented generation for full-text screening.

### Rayyan setup

One reviewer manually screened 2,000 random articles in batches of 100 to train Rayyan. Rayyan then assigned unscreened articles to five classes:
- Most Likely To Exclude
- Likely To Exclude
- Undecided
- Likely To Include
- Most Likely To Include

The authors evaluate two operational thresholds:

- Threshold A: keep `Undecided` or higher for further manual screening; auto-exclude `Likely To Exclude` or `Most Likely To Exclude`.
- Threshold B: keep everything except `Most Likely To Exclude`; this is the more conservative threshold.

These thresholds produce materially different tradeoffs. Under Threshold A, Rayyan auto-excluded 72.1% of unscreened articles but missed 1 of the 20 ultimately included studies, corresponding to a 5% false negative rate. Under Threshold B, Rayyan reduced the false negative rate to 0% but auto-excluded only 50.7% of unscreened articles, leaving many more records for manual review.

This is not a side result; it is one of the paper's main methodological lessons. The safe operating point for a semi-automated screener depends on whether the team is optimizing for workload reduction or for near-zero risk of missed inclusions. In systematic review practice, the latter usually dominates.

### LLM title/abstract phase

For title/abstract screening, the authors call GPT-4 through the OpenAI API. The model is given a role-setting system prompt instructing it to act as a professional medical researcher performing title/abstract screening. The article title and abstract are then evaluated through a series of questions that are stated to be identical to the human screening guide used in the original review. For each question, the model must answer `yes`, `no`, or `unsure`.

The crucial rule is what happens when the model is not certain. The paper states that uncertain records are retained rather than excluded, explicitly to improve sensitivity. This is the core design principle of the system.

On 14,439 title/abstract records, the GPT-4 phase retained 3,298 records for phase 2, yielding an article exclusion rate of 77.2% with a false negative rate of 0%. The reported runtime for this automated phase was about 2 hours.

### LLM full-text phase with RAG

Articles that passed the title/abstract phase moved to a full-text screening stage. Full-text PDFs were obtained manually, then processed into a vector store with LlamaIndex. The paper describes this as a RAG setup in which the article full text becomes a retrievable document set for GPT-4.

The full-text stage again uses a question-based design aligned to the manual screening guide. The first five questions are answered with `yes`, `no`, or `unsure`. The final question asks the model to identify the outcome studied in the review: falls, fractures, or mortality. The paper states that a full-text article is included only if falls is one of the outcomes.

Among the 3,298 full texts entering this stage, only 78 remained for manual review, including all 20 studies retained in the gold-standard manual workflow. The reported runtime for the automated full-text stage was about 4 hours. For full-text screening alone, the paper reports article exclusion rate 97.63%, specificity 99.6%, positive predictive value 25.6%, and negative predictive value 100%.

### End-to-end result

End to end, the LLM pipeline reduced the manual set from 14,439 citations and 1,680 full texts to 78 final manual-review candidates, while keeping all 20 included studies. The paper reports:

- Title/abstract AER: 77.2%
- Full-text AER: 97.63%
- Overall AER: 99.5%
- Specificity: 99.6%
- PPV: 25.6%
- NPV: 100%
- False negative rate: 0%
- Total estimated screening time: 25.5 hours including manual review of the remaining 78 articles

This is compared against an estimated 564.4 hours for the traditional manual process and 54.7 to 81.3 hours for Rayyan title/abstract screening depending on threshold.

## 4. Methodological contribution in detail

The paper's real contribution is not simply "GPT-4 worked well." It is the operational design of the screening pipeline.

### Criterion-by-criterion prompting rather than one-shot classification

The central methodological contribution is the use of a question sequence that mirrors the human screening guide. This matters because the model is not asked to infer an opaque global decision from unstructured instructions. Instead, it is asked to evaluate explicit criteria. That design should improve consistency, make error analysis possible, and let the team inspect whether a wrong final decision arose from one specific criterion or from the aggregation policy.

For our purposes, this is the most transferable lesson in the paper. Our screening failures are largely criterion failures. We struggle with:
- Tier ambiguity
- whether a paper is truly text-bio rather than biology-only or text-only
- whether the model is generative versus encoder-only
- whether the work presents a foundation model versus an adaptation, wrapper, benchmark, or application

Those are exactly the kinds of distinctions that should be represented as separate questions with separate outputs.

### Explicit `unsure` as a designed state, not an error state

The paper treats `unsure` as part of the screening logic, not as a malformed answer. This is methodologically important. A large fraction of abstracts are underspecified relative to the screening question. If the pipeline forces a binary decision under partial information, false exclusions become inevitable.

The authors explicitly retain uncertain records for downstream review "just as we do with the traditional process." That is a strong argument for keeping `UNCERTAIN` in our own pipeline as a first-class state. In our context, `UNCERTAIN` should not be seen as prompt failure. It is often the correct outcome when the abstract does not resolve whether the paper meets our foundation-model definition or our multimodality requirement.

### Sensitivity-first aggregation logic

Although the local sources do not reproduce the exact appendix prompts, the aggregation logic is clear: articles are only excluded when the model is sufficiently certain on the relevant criterion decisions; otherwise they are retained. This is a conservative operating policy.

That matters for benchmark design. A screening benchmark that rewards aggressive auto-exclusion will incentivize the wrong behavior. Our benchmark should score sensitivity and false-exclusion control first, and only then measure workload reduction. The Rayyan comparison in this paper demonstrates why: more aggressive exclusion can look efficient while silently losing relevant studies.

### Criterion-level logging as audit infrastructure

The paper logs all question outcomes into an Excel sheet for every article in both phases. This is more important than the spreadsheet format itself. The methodological gain is the audit trail. Reviewers can trace a final decision back to the specific question responses that produced it.

For our project, question-level outputs are essential for three reasons:
- They let us diagnose which criterion is unstable.
- They let us distinguish "bad rule" from "bad model."
- They let us construct a benchmark that measures criterion-level accuracy, not just final label agreement.

This is especially relevant to our current manual benchmark construction problem. If we only store final include/exclude labels, we will not know whether disagreement comes from the data, the prompt, or ambiguity in the protocol itself.

### Separate treatment of title/abstract versus full-text evidence

The paper does not collapse title/abstract and full-text screening into one monolithic LLM call. It first uses prompt engineering over title/abstract text, then uses a separate RAG-assisted full-text phase. This separation is methodologically sound because the information regime is different in the two stages.

For our workflow, the implication is clear: full-text RAG should not be used to compensate for a poorly specified title/abstract protocol. It should be introduced only after the title/abstract criteria, outputs, and escalation logic are stable.

### RAG lesson: the value is not "more text," but recoverable evidence

The paper positions its RAG-based full-text phase against prior work that segmented articles and reportedly achieved poor sensitivity. The authors argue that segmentation can break context, whereas RAG allows the model to retrieve relevant evidence from the full document. Even if the paper does not provide enough engineering detail to replicate the setup, it makes one useful methodological point: for full-text screening, the model needs targeted access to evidence-bearing spans, not just arbitrary chunks.

For us, that means full-text RAG is potentially justified when the abstract leaves crucial screening criteria unresolved, but only if retrieval can surface the evidence relevant to those criteria. Using full text without evidence localization will not reliably solve ambiguity.

## 5. Strengths

- Large evaluation set relative to much of the prior screening literature: 14,439 title/abstract records is materially more convincing than small pilot datasets.
- Strong sensitivity-first result within the studied review: the LLM pipeline retained all 20 studies included by the gold-standard manual process.
- Clear operational comparison against a real semi-automated baseline, Rayyan, rather than only against fully manual screening.
- Direct demonstration that threshold choice changes the safety-efficiency tradeoff.
- Criterion-level structured outputs and automatic logging, which are more auditable than free-text reasoning or single-label predictions.
- Sensible separation between title/abstract and full-text stages.
- Useful practical message that the system depends more on prompt clarity and retrieval quality than on fine-tuning or large training sets.

## 6. Limitations and what the paper does not establish

The paper is promising, but it does not establish several things we should care about.

### It does not establish broad external validity

This is one completed review in one biomedical topic with only 20 final included studies. The authors themselves note that performance should be validated across diverse and more complex reviews. For our project, this is the main caution. A pipeline that performs well on a relatively structured medical question may not transfer cleanly to a conceptually messy review about text-bio foundation models, where category boundaries are more contested.

### It does not expose enough prompt detail in the provided local sources

The paper states that the prompts and question sets are in appendices, but the provided local PDF and TXT do not reproduce those appendices in full. So the paper validates the pattern of question-by-question prompting, but from the local sources alone we cannot fully audit:
- the exact question wording
- the decision aggregation rule
- whether reasons were requested per question
- how contradictions across questions were handled

This is a real limitation for reuse. We can adopt the design principle, but not simply copy their implementation.

### It does not solve benchmark-construction bias

The gold standard is a completed manual review, not an adjudicated benchmark explicitly built to stress model failure modes. That is acceptable for a proof of concept, but weaker than a benchmark designed around difficult borderline cases. For our project, manual benchmark construction remains essential.

### It does not show robustness to ambiguous taxonomy

Their domain appears to have comparatively concrete eligibility rules tied to intervention, study type, and outcomes. Our review has harder ontology problems: foundation model versus downstream model, genuine text-bio fusion versus superficial multimodality, generative versus encoder-only, paper type versus system type, and multiple plausible tiers. The paper therefore supports our use of structured criteria, but it does not prove that a similar pipeline will resolve our Tier ambiguity reliably.

### It does not justify replacing humans

The paper is explicit that human reviewers are still required. That point should remain central in our protocol. A sensitivity-first LLM screener is a triage and prioritization system with auditable criterion outputs, not an autonomous final arbiter.

### It does not fully characterize engineering requirements for full-text RAG

The paper mentions LlamaIndex and a vector store, but it does not provide the detail we would need to judge reproducibility or portability:
- PDF parsing quality
- chunking policy
- embedding model
- retrieval depth
- prompt template at retrieval time
- evidence citation behavior
- failure handling when the relevant answer is absent or conflicting

So the paper supports the idea of full-text RAG as a second-stage aid, but it does not establish an implementation recipe for us.

### It may undercount operational costs

The authors explicitly exclude the time required to collect and prepare full-text PDFs, and they also note that they do not count the iterative calibration needed to finalize the screening sheets. Those exclusions are fair for their internal comparison, but they matter for real deployment. For us, protocol design, benchmark construction, adjudication, and logging schema design will likely dominate early effort.

## 7. Concrete implications for our review workflow

### We should formalize a sensitivity-first policy

This paper strongly supports the rule that automatic exclusion should require criterion-level certainty on decisive exclusion conditions. If the abstract does not clearly resolve a key inclusion dimension, the correct outcome is `UNCERTAIN`, not `EXCLUDE`.

### We should decompose our screening guide into explicit questions

Our prompt should be built around separate questions for the specific failure modes we already observe. At minimum, those should include:
- biological modality present and central
- text modality present and central
- genuine text-biology connection rather than a loose multi-input setup
- generative or sequence-modeling status
- evidence that the work is foundational or pretraining-centric rather than a narrow task model
- paper type and review relevance
- confidence / uncertainty state

The point is not to maximize the number of questions. The point is to isolate the criteria that currently collapse into Tier ambiguity.

### We should treat `UNCERTAIN` as a valid benchmark outcome

The paper's handling of `unsure` is one of its most transferable lessons. Our benchmark should therefore distinguish:
- clear include
- clear exclude
- uncertain / requires manual review

If we force all ambiguous cases into binary labels during benchmark construction, we will contaminate the benchmark and train the pipeline toward overconfident exclusion.

### We should log criterion-level outputs, not just final decisions

At minimum, each screened record should store:
- the answer to each criterion question
- a short rationale or evidence snippet for each answer
- the final aggregation outcome
- the criterion that triggered exclusion or uncertainty

This is necessary for protocol iteration. Without it, we cannot tell whether a record was excluded because the model misread the abstract or because our criterion definitions are underspecified.

### Full-text RAG should be deferred and scoped carefully

This paper supports full-text RAG only as a second-stage tool. For us, that means:
- do not use full-text RAG to patch a vague title/abstract protocol
- first stabilize title/abstract criteria and question-level outputs
- add full-text RAG only for cases where the abstract systematically fails to resolve core criteria

Likely candidates for later full-text RAG in our domain are papers where the abstract does not make clear whether the model is foundational, whether text and biology are jointly modeled, or whether the generative component is central rather than peripheral.

## 8. Specific repo/process changes we should consider

- Replace any one-shot include/exclude screening prompt with a criterion-by-criterion schema that returns one field per question plus a final decision.
- Preserve `UNCERTAIN` as a first-class output in the protocol and make the default policy "manual review on uncertainty."
- Add criterion-level rationale fields to the structured output. The paper logs question outcomes; we should go one step further and require short evidence-grounded justifications.
- Build the manual benchmark around adjudicated borderline cases, especially Tier ambiguity cases, rather than only obvious positives and negatives.
- Store benchmark labels at both levels: per-criterion labels and final decision labels.
- Evaluate pipeline behavior with sensitivity-first metrics first: false exclusion count, recall on included papers, and workload reduction only second.
- Separate title/abstract benchmarking from any future full-text benchmarking. Do not combine them into one score.
- If we later add full-text RAG, create a dedicated benchmark slice for "abstract-insufficient" records and measure whether retrieval actually resolves the uncertainty.
- Track which criterion most often causes `UNCERTAIN`. That will tell us whether the bottleneck is protocol ambiguity, abstract insufficiency, or model weakness.
- Define an explicit policy for when a criterion conflict should force `UNCERTAIN` rather than allow automatic exclusion.

## 9. Bottom-line assessment for our project

This paper is one of the more useful methodological references for our screening pipeline, not because it proves that "GPT-4 can screen systematic reviews," but because it operationalizes a sensible conservative design: criterion-level prompting, explicit uncertainty handling, structured logging, and a clean separation between title/abstract screening and later full-text assistance.

For our project, the main takeaway is straightforward. We should not build a binary screening classifier. We should build an auditable, sensitivity-first decision process that asks criterion-level questions, preserves `UNCERTAIN`, and uses manual adjudication to resolve the cases that are genuinely ambiguous. The paper strongly supports that design choice.

At the same time, we should not overread the result. The paper does not establish that a similar pipeline will generalize to our much more taxonomy-heavy review problem, and it does not provide enough local-source detail to lift their prompts directly. Its most valuable contribution to us is therefore architectural rather than turnkey: use question-level screening, uncertainty-aware aggregation, and criterion-level logging as the backbone of the pipeline; treat full-text RAG as a later, explicitly benchmarked module rather than a default first-line solution.
