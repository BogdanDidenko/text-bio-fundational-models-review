# Research plan, paper 2: "Language is a narrow, lossy and increasingly synthetic interface to biology"

Status: saved for later (user decision, 2026-10-14). Paper 1 uses storyline (3), the two design
cultures. This plan keeps the storyline (1) findings so that the second paper can start from them.

## Central claim
In current generative models that combine text with biological data, language and biology meet
through a narrow channel:
- measurements reach the language model as about a hundred names or a few dozen soft tokens;
- language at use time is mostly instructions;
- the paired text is increasingly written by other LLMs;
- few works test whether outputs depend on the biological input at all.
Claims of grounded multimodal understanding therefore rest on untested assumptions. We propose
controls and a reporting card.

## Evidence already in hand (candidate_findings.md, 2026-10-14)
- B1 Synthetic language:
  - 20/51 works (39%, CI 25–53%) train or evaluate on LLM-written text; 16 of them generate biological content;
  - reasoning traces are distilled from frontier LLMs in 6 works;
  - human checks are reported in 5/20.
- A1 A cell becomes about 100 names:
  - text routes keep 5–1000 genes (median 100) and replace values by ranks;
  - numbers are written as numbers in only 2 works;
  - encoder routes keep 331–20,541 features.
- A3 Non-comparable reuse: the same method is run with 100 vs 1000 genes, and baselines receive 50 or 128 genes.
- A2 Interface budgets: 1–256 soft vectors per object (median 32).
- B2/B3 Language at use time is procedural:
  - 58% of text routes at inference and evaluation are instructions;
  - in 17/35 works the use-time text is instructions only;
  - biology enters text as names.
- A4 No complete recipe: 52/262 biological routes are fully specified, and 4/43 works fully specify all of theirs.

## Analyses to add
1. D1 biology-dependence controls, from the design-culture charting pass (2026-10-14): share of works
   with any control, by type, and reported effect sizes.
2. Text-shortcut audit: prompts that already contain identifiers which reveal the answer (variant IDs,
   gene or cell-type names). Requires charting prompt templates for the evaluation sets.
3. Provenance chain of synthetic text: generator, version, prompt and decoding disclosure, and
   verification (synthetic_text_generators field of the same pass).
4. Information-budget figure: features kept (x) against LM tokens per object (y), by route culture.
5. Optional empirical probe, outside the scoping-review protocol and reported separately: re-run one
   open verbalised model with K ∈ {50, 100, 200, 1000} and with name-scrambled genes to show
   sensitivity. This would make it a research article, not a review.

## Recommendations to develop
- A minimum reporting card for input representations: the operation chain with every parameter
  stated (operation library 1.3.0 as vocabulary), K, ordering and tie rule, normalisation, and
  generator prompts and versions.
- Required controls:
  - remove or mismatch the biological input;
  - text-only baseline with the same backbone;
  - name scrambling for verbalised inputs;
  - like-for-like K when comparing with cell-sentence methods.

## Risks
- B1 and D1 currently rely on keyword pre-screens confirmed by reading; the charting pass will
  replace them.
- The year trend in synthetic text (2/10 → 18/41) is not significant (p = 0.28) and must be reported
  as descriptive.
- Novelty against general reviews of synthetic biomedical data (PMC13156355) and against
  vision–language "blindness" studies must be positioned explicitly. Every citation must be verified.
