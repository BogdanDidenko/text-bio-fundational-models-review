# Number check: rewritten manuscript against the previous version

Old version: commit `4c4db9f0` (Markdown master, abstract and Key Points of main.tex).
New version: `manuscript/build/manuscript.md`, `manuscript/build/supplementary_information.md`.

- Distinct numbers in the new text: 217; in the old text: 238.
- New numbers not in the old text and not allowed: **0**.
- New numbers allowed as intentional additions: 6.
- Occurrences with a dissimilar best old context (for reading): 26.
- Old numbers that no longer occur in the new text: 27.

## Intentional additions

| Number | Reason | New sentence |
|---|---|---|
| 1.1 | Version of the targeted charting protocol; the earlier text named it design-culture-charting-v1.1 inside a code span | **Targeted charting pass.** The pass followed a frozen protocol (design-culture charting, version 1.1). |
| 1.7.0 | Docling Graph version recorded as pipeline_version in the run metadata; tool versions are asked for by PRISMA-trAIce | Full texts were converted with Docling (version 2.110.0) and their sections reconstructed with Docling Graph (version 1.7.0). |
| 2.110.0 | Docling version from requirements-docling.txt; tool versions are asked for by PRISMA-trAIce | Full texts were converted with Docling (version 2.110.0) and their sections reconstructed with Docling Graph (version 1.7.0). |
| 2026-02-09 | Date of the first commit of the protocol (version 3.0) in the Git history of the repository; added to report the protocol record (PRISMA-ScR item 5) | Its first version under version control (version 3.0) was committed to the project repository on 2026-02-09, after a first search execution on 2026-02-06, and the protocol with all later amendments is deposited retrospectively on Zenodo . |
| 5.4 | Part of the model name gpt-5.4-mini; the earlier text wrote it inside a code span | LLMs were run through the Codex command-line agent: gpt-5.4-mini for title and abstract screening, full-text screening and route charting, and gpt-5.6-luna (reasoning effort high) for the operation-level decomposition, the parameter pass and the targeted charting pass, because the earlier model is no longer available through Codex. |
| 5.6 | Part of the model name gpt-5.6-luna; the earlier text wrote it inside a code span | LLMs were run through the Codex command-line agent: gpt-5.4-mini for title and abstract screening, full-text screening and route charting, and gpt-5.6-luna (reasoning effort high) for the operation-level decomposition, the parameter pass and the targeted charting pass, because the earlier model is no longer available through Codex. |

## Dissimilar contexts (read and confirm)

| Number | Best similarity | New sentence |
|---|---:|---|
| 0.019 | 0.1 | BLEU-2 0.344 vs 0.019), and an embedding stack vs a Cell2Sentence-like control (OmicsLM; average relative rank .740 vs .090). |
| 0.344 | 0.1 | BLEU-2 0.344 vs 0.019), and an embedding stack vs a Cell2Sentence-like control (OmicsLM; average relative rank .740 vs .090). |
| 1.3.0 | 0.1 | The search configurations and exports, screening and charting outputs, the operation library (version 1.3.0), the analysis code and the source data of every figure panel are available at (this version: commit ). gives the repository path of every supplementary item, and the earlier version of this manuscript, with its internal labels, is (commit ). |
| 11 | 0.08 | **Evaluation formats** (works, both runs / either run): closed-set classification 31 / 42; open-text generation scored by automatic text metrics 29 / 43; likelihood or perplexity scoring 9 / 13; candidate-label selection 6 / 11; open text judged by an LLM 6 / 7, or by humans 6 / 8; wet-lab validation in 1 work. |
| 13 | 0.12 | **Evaluation formats** (works, both runs / either run): closed-set classification 31 / 42; open-text generation scored by automatic text metrics 29 / 43; likelihood or perplexity scoring 9 / 13; candidate-label selection 6 / 11; open text judged by an LLM 6 / 7, or by humans 6 / 8; wet-lab validation in 1 work. |
| 17 | 0.08 | Biological routes fall into six main carrier × interface archetypes: encoded soft tokens (24 papers), verbalised text in the token stream (18), generator conditioning (17), biological alphabets in the token stream (8), attention bridges (7) and shared latent alignment (7). |
| 18 | 0.09 | The most widespread are text serialisation (38 papers), selection (26), tokenisation (25), learned projection (23), concatenation (18) and partition (18). |
| 18 | 0.09 | The most widespread are text serialisation (38 papers), selection (26), tokenisation (25), learned projection (23), concatenation (18) and partition (18). |
| 2026-02-06 | 0.05 | Its first version under version control (version 3.0) was committed to the project repository on 2026-02-09, after a first search execution on 2026-02-06, and the protocol with all later amendments is deposited retrospectively on Zenodo . |
| 2026-02-16 | 0.05 | **Gap between search windows.** On 2026-10-14 the baseline queries of PubMed, arXiv, Europe PMC and Semantic Scholar were re-run for the window 2026-02-16 to 2026-02-28. |
| 2026-02-28 | 0.11 | **Gap between search windows.** On 2026-10-14 the baseline queries of PubMed, arXiv, Europe PMC and Semantic Scholar were re-run for the window 2026-02-16 to 2026-02-28. |
| 2026-07-10 | 0.12 | Full-text screening (baseline run on 2026-07-10) used Docling conversions; |
| 25 | 0.09 | The most widespread are text serialisation (38 papers), selection (26), tokenisation (25), learned projection (23), concatenation (18) and partition (18). |
| 26 | 0.09 | The most widespread are text serialisation (38 papers), selection (26), tokenisation (25), learned projection (23), concatenation (18) and partition (18). |
| 26 | 0.12 | Among parameters with at least 45 calls, papers left unstated the projection activation in 80% of 76 calls, the concatenation order in 71% of 48, the serialisation order in 42% of 268, the lexical rendering of values in 40% of 268 and the token vocabulary in 26% of 73. |
| 3.0 | 0.05 | Its first version under version control (version 3.0) was committed to the project repository on 2026-02-09, after a first search execution on 2026-02-06, and the protocol with all later amendments is deposited retrospectively on Zenodo . |
| 3.0 | 0.0 | Amendments of the protocol after its first version under version control (version 3.0), and further changes that the protocol did not foresee. "Made after results were seen" records whether the change was decided after results of the review (or, where stated, after procedural results) were known. |
| 31 | 0.08 | **Evaluation formats** (works, both runs / either run): closed-set classification 31 / 42; open-text generation scored by automatic text metrics 29 / 43; likelihood or perplexity scoring 9 / 13; candidate-label selection 6 / 11; open text judged by an LLM 6 / 7, or by humans 6 / 8; wet-lab validation in 1 work. |
| 42 | 0.12 | Among parameters with at least 45 calls, papers left unstated the projection activation in 80% of 76 calls, the concatenation order in 71% of 48, the serialisation order in 42% of 268, the lexical rendering of values in 40% of 268 and the token vocabulary in 26% of 73. |
| 42 | 0.08 | **Evaluation formats** (works, both runs / either run): closed-set classification 31 / 42; open-text generation scored by automatic text metrics 29 / 43; likelihood or perplexity scoring 9 / 13; candidate-label selection 6 / 11; open text judged by an LLM 6 / 7, or by humans 6 / 8; wet-lab validation in 1 work. |
| 48 | 0.12 | Among parameters with at least 45 calls, papers left unstated the projection activation in 80% of 76 calls, the concatenation order in 71% of 48, the serialisation order in 42% of 268, the lexical rendering of values in 40% of 268 and the token vocabulary in 26% of 73. |
| 50 | 0.1 | The remaining 50 papers were decomposed by an LLM agent in three independent runs per paper, with the structure fixed by the charted routes (one step per element of each route's transformation chain); the published decision for each step is the majority of the three runs, and every decision was checked mechanically for verbatim evidence, valid operation inputs and outputs, and declared parameters. |
| 50 | 0.05 | One row per charted route of the 50 agent-decomposed papers ( routes): the model and configuration, lifecycle phase, source modality, carrier family and subtype, fusion topology, text role, the operation chain, the value of each design axis with the rule that assigned it, the share of opaque steps, the share of stated parameters and the archetype. |
| 54 | 0.09 | Input paths decompose into reusable operations and recurring motifs.** (a) Papers using each of the 22 library operations (54 papers). |
| 71 | 0.12 | Among parameters with at least 45 calls, papers left unstated the projection activation in 80% of 76 calls, the concatenation order in 71% of 48, the serialisation order in 42% of 268, the lexical rendering of values in 40% of 268 and the token vocabulary in 26% of 73. |
| 73 | 0.12 | Among parameters with at least 45 calls, papers left unstated the projection activation in 80% of 76 calls, the concatenation order in 71% of 48, the serialisation order in 42% of 268, the lexical rendering of values in 40% of 268 and the token vocabulary in 26% of 73. |

## Old numbers absent from the new text

0.4, 0.5.1, 2.1, 2.10, 2.11, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2510.07793, 3.10, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.2, 4.3, 4.4, 4.5, 4.6
