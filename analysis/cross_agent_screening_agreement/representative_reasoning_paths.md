# Representative Reasoning Paths

This note extracts qualitative mechanisms behind decision instability in the 116-case regression experiment. It is meant as a compact source for a future research section on cross-agent agreement in LLM-assisted screening.

## GeneGPT: Wrapper Boundary Drift

Observed decisions across available runs: mostly `EXCLUDE`, with one GPT-OSS run flipping to `INCLUDE`.

The conservative reasoning path treats GeneGPT as a tool-augmented application wrapper: an existing code/text LLM is connected to NCBI APIs and biomedical tools, but the paper is not primarily proposing a new text-bio generative foundation model.

The liberal reasoning path emphasizes augmented decoding, biomedical question answering, and API-triggering generation. Under that reading, the model is credited as a generative biomedical system rather than a wrapper.

Methodological signal: tool use and retrieval/API augmentation can be over-credited as primary model contribution unless wrapper boundaries are explicitly audited.

## GEM-1: Text-Derived Metadata Boundary

Observed decisions: `EXCLUDE`, `UNCERTAIN`, and `INCLUDE` across models/runs.

The conservative reasoning path treats the LLM metadata agent as preprocessing or side information. The core contribution is a generative genomics model, but the text component is not clearly central to conditioning or generation.

The liberal reasoning path treats LLM-processed experimental metadata and foundation-model embeddings as a substantive text-bio bridge. The paper is then read as a text-conditioned generative genomics model.

Methodological signal: text-derived metadata is an unstable category. The same abstract can support multiple plausible interpretations when it does not state whether text is core model input, conditioning, or detached preprocessing.

## Med-PRSIMD: Generative Training vs Predictive Eligibility

Observed decisions: DeepSeek excludes; GPT-OSS includes.

The conservative reasoning path focuses on the final task: disease risk prediction. Even if the model uses a causal language-model objective over medical history records, the screened contribution is still predictive rather than generative in the review sense.

The liberal reasoning path treats causal LM pretraining over clinical records, plus text/clinical integration, as enough evidence for a generative text-bio model.

Methodological signal: prompts need to distinguish generative architecture evidence from generative review eligibility. A generative training objective alone may not imply that generation is central to the paper's reviewed contribution.

## Cell2Sentence: Biological Tokenization vs Natural Language

Observed decisions: DeepSeek varies between `UNCERTAIN` and `EXCLUDE`; GPT-OSS includes.

The conservative reasoning path treats "cell sentences" as biological token sequences. Under this reading, language is metaphorical or tokenization-based rather than natural-language text-bio alignment.

The liberal reasoning path credits the textualization of transcriptomic profiles and GPT-style modeling as a text-bio bridge.

Methodological signal: this is a domain-specific ambiguity, not just model noise. The literature often uses "language" to describe biological sequences, but some methods intentionally convert biological data into textual forms for LLMs. Boundary cases need explicit reporting.

## BiomedGPT, ADAM-1, Gp-gpt: Thin Abstract Inference

Observed decisions: models vary between `INCLUDE`, `UNCERTAIN`, and `EXCLUDE` when the abstract is short, truncated, or title-heavy.

The conservative reasoning path requires explicit abstract-level evidence for text component, text-bio bridge, and generative model. If one criterion is underspecified, it moves to `UNCERTAIN` or `EXCLUDE`.

The liberal reasoning path infers eligibility from model names, broad foundation-model claims, or known-sounding framing.

Methodological signal: title/abstract screening is especially unstable when abstracts are thin. A model may either refuse to infer missing criteria or fill gaps from priors. This should be reported as a source of uncertainty in automated screening.

## Genolator, CellHermes, OpticalDNA: Generative Mechanism Interpretation

Observed decisions: mixed across models and repeats.

The conservative reasoning path asks whether generation is central and explicitly evidenced: decoder, autoregressive generation, diffusion, sequence generation, or natural-language answer generation tied to the text-bio task.

The liberal reasoning path treats terms such as LLM, QA, explanation, decoder, or masked span completion as enough to establish a generative mechanism.

Methodological signal: "uses an LLM" and "has a decoder" are not stable proxy criteria. The pipeline should separately record generative mechanism, generated output type, and whether generation is central to the paper.

## Overall Pattern

The disagreement is structured rather than random. Runs disagree because models operationalize eligibility boundaries differently:

- wrapper vs primary model contribution;
- text-derived metadata vs central text conditioning;
- generative training objective vs generative paper contribution;
- biological language metaphor vs natural-language text;
- strict abstract evidence vs inference from title/model name;
- broad LLM framing vs explicit generative mechanism.

This supports a research framing where LLM screening is evaluated as a multi-agent measurement process, not as a single deterministic classifier.
