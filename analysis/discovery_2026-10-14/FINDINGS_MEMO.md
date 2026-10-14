# Findings memo, paper 1: "Translate or encode? Two design cultures for coupling language and biology"

Date: 2026-10-14.
Corpus: 54 included records, which are 51 independent works after linking report pairs (Cell2Text,
CellWhisperer, OmniNA). Every number below is per work unless stated and is traced to a file.

Sources:
- the 1.3.0 operation release;
- the design-culture charting pass (protocol `design-culture-charting-v1.1`: 54 records × 2
  independent Codex runs, every quote verified mechanically, run agreement in
  `analysis/design_culture_charting_2026-10-14/v11/agreement.json`);
- steward adjudication files: `comparison_units_adjudicated.csv`, `work_culture_table.csv`,
  `review_rationale.md`, `synthetic_text_table.csv`.

The storyline-1 findings go to `RESEARCH_PLAN_PAPER2.md`.

---

## Definitions (operational and reproducible)

A work's culture is decided by how biological data reach the generative model in its proposed system.
The coding uses the archetypes of the operation-level atlas, plus the host network from the charting
pass (`work_culture_table.csv`).

| Culture | Rule | Works |
|---|---|---|
| **T, token-native** ("translate") | Biology reaches a text-pretrained language model only as tokens in its own stream: natural-language names, sequence letters or new symbolic tokens. | 17 |
| **E, encoder-mediated** ("encode") | Biology reaches a text-pretrained language model only as continuous vectors from a biological encoder (soft tokens, Q-Former, cross-attention, conditioning). | 16 |
| **H, hybrid** | The same system delivers biology through both channels. | 8 |
| **C, language-conditioned biology model** | The generative host is a biology model; language enters as conditioning (diffusion, flow, graph or sequence generators). | 9 |
| **A, alignment-only** | Dual-encoder alignment without a generative host. | 1 |

Each culture spans the same modalities (transcriptomics occurs in T, E, H and C), so the culture is a
design choice, not a property of the data.

## F1. Each culture keeps a different part of the measurement

- **T keeps identities and drops magnitudes.**
  - Transcriptomes written as text keep 50–1000 genes per work (median 100 over 8 works stating K),
    ordered by rank. OCellus' spatial prefix keeps 5 marker genes per neighbour.
  - Values are written as numbers in only 2 of the 51 works (CpG beta values in token-native
    Longevity-LLM; blood biomarkers in hybrid P3GPT).
  - Sequences are kept letter by letter.
  - The pipelines are transparent: the median share of opaque steps per work is 0.
- **E passes magnitudes to learned modules and hides what survives.**
  - Works that inject encoder outputs deliver 1–256 vectors per object (median 32; 11 works, all
    cultures) from 331–20,541 input features where stated (6 works). Encoder-mediated works alone:
    1–256 vectors (median 32, 7 works) from 2,048–20,541 features (3 works).
  - The median share of opaque, learned steps per encoder-mediated work is 0.33.
- Unreported parameters do not differ between the two (median unstated share 0.35 vs 0.26, Mann–Whitney
  p = 0.89). The difference lies in what is lost and what is hidden, not in reporting discipline.
- Sources: `gene_budget_table.csv`, `token_budget_table.csv`, release 1.3.0.

## F2. Where authors discuss the choice, both cultures describe the same trade-off

From the charting pass, adjudicated by reading every quote (`review_rationale.md`):

| Statement | T works (n = 17) | E works (n = 16) |
|---|---|---|
| The architecture stays unchanged (for own choice) | 9 (53%) | 0/16 in both runs |
| Pretrained LLM knowledge is used (for own choice) | ~9 (53%) | — |
| Own representation loses quantitative or fine-grained information (conceded) | 7 (41%) | — |
| Text rendering loses quantitative information (criticism of the alternative) | — | 7 (44%) |

The E criticisms come from Cell2Text, BIOREASON, InstructCell, scMMGPT, scMOBA, Bio-BLIP and OmicsLM.

In short, T trades measurement fidelity for access to what the LLM already knows about named
entities; E trades transparency for fidelity. Both cultures say so in their own words.

Run agreement on the rationale field is moderate (mean Jaccard 0.60), so these counts are steward-adjudicated.

## F3. Different supervision and adaptation, the same reliance on LLM-written text

- **LLM-generated text** is used in 25/51 works (49%):
  - T 10/17, E 8/16, H 6/8, C 1/9;
  - in 20 works it is biological content, in 4 templates only, and 1 is unclear;
  - 7 works distill reasoning traces;
  - 5 report a human check;
  - in 4 works the LLM-written text also enters evaluation.
- So synthetic language is a property of LLM-hosted designs (T, E and H), not of either culture alone.
- **Adaptation** (works, both runs / either run):
  - T: full fine-tuning 9/9, LoRA 6/7, training from scratch 3/3, vocabulary extended 4/5;
  - E: frozen LLM 3/3 (T 0), full fine-tuning 7/9, LoRA 6/6;
  - E encoders are frozen in 6 works and fine-tuned in 6.
- Sources: `synthetic_text_table.csv`, `agreement.json` (κ for LLM state 0.64–1.0).

## F4. Few works test whether the biology is used, in every culture

- A test of whether outputs depend on the biological input is reported in 22/51 works (43%): removal,
  mismatch or shuffling, random input, or content perturbation.
- By culture: T 7/17 (41%), **E 4/16 (25%)**, H 5/8 (63%), C 6/9 (67%).
- The culture differences are not detectable (E vs rest Fisher p = 0.13; T vs E p = 0.46). The finding
  is the low overall rate. Bio-BLIP's authors argue that linear projections encourage reliance on prompt
  text, which would make such tests most informative for E designs (their argument, not our result).
- Works that made cross-culture comparisons tested dependence no more often (10/20 vs 12/31, p = 0.56).
- Run agreement: Jaccard 0.91. Three disagreements were adjudicated: TissueCraftAI excluded (noise
  robustness only); X-Cell (embedding randomisation) and GEMGen (unguided sampling) included.

## F5. The evidence gap: every culture wins on its home turf

31 cross-culture comparison units in 20 works were adjudicated from 217 charted items
(`comparison_units_adjudicated.csv`). Three units were set aside as within-culture or not about
representation form (`comparison_units_removed.csv`).

- **Home advantage.** The authors' own representation wins 28 of 31.
  - Between-system comparisons: 20/23 (87%; binomial p = 4.9 × 10⁻⁴ against 50%).
  - Controlled ablations: 7/7. Same-backbone baseline: 1/1.
  - Winners across papers split T 10, E 9, H 2, mixed 2, so no culture dominates.
  - Within every task family the winner followed the proposer; the non-wins fell in categorical tasks
    (2 of 10) and embedding quality (1 of 4).
- **Per work.** Units are nested in works (C2S-Scale has four). The proposer won every unit in 17 of 20
  works (sign test p = 0.0026) and every between-system unit in 14 of 17 (p = 0.013).
- **Each culture benchmarks mostly against released, unadapted forms of the other.**
  - E papers mostly compare with *prompted general LLMs reading raw text* (8 of 13 units: GPT-4.1, GPT-4o
    or Llama2-Chat given sequences, SMILES or gene lists without adaptation).
  - T papers mostly compare with *released encoder-based models*, usually frozen embeddings plus simple
    heads (scGPT, Geneformer, ESM-2, Nicheformer) or a model used as published (CellWhisperer): 7 of 10.
  - Opponent type by proposing culture: prompted LLMs 8/13 vs 0/10 (Fisher p = 0.0027); released encoder
    models 0/13 vs 7/10 (p = 4.9 × 10⁻⁴). Partly by construction.
  - Opponents trained by the proposing team are a minority (2 of 10 units for T, 5 of 13 for E). Across
    cultures the proposer won all 11 such units and 16 of 19 against released opponents (one unit had no
    model). All three exceptions had released opponents.
- **What the comparisons do show.**
  - When the T arm reads raw sequence letters, the encoder arm wins 5 of 7. The exceptions are a
    perceptual rendering (OpticalDNA) and a vocabulary trained on biological tokens (OmniGene-4).
  - For gene-name lists, outcomes split by who runs the comparison: T 8, E 7, H 3, mixed 2.
  - Of the three exceptions, two are cell-annotation tasks won by text-reading models:
    - GPT-OSS-120B reading 128 gene names beats the 8B hybrid BIOVERSE (accuracy 0.779 vs 0.614).
      An 8B general model lost (0.369), so this one is plausibly a scale effect.
    - C2S-Scale-27B beats the 32B hybrid CellTosg2Sequence on immune annotation (exact 85.6% vs 24.1%).
      C2S-Scale is not larger; the CellTosg2Sequence authors attribute the gap to its much larger
      pretraining corpus (their reinforcement stage used about 8,000 annotation examples).
    - The third: OCellus wins the linear probe but not NMI.
- **Controlled ablations, where only the representation changes, all favour the authors' configuration:**

  | Comparison | Works | Example |
  |---|---|---|
  | E over T | scMMGPT, BioMedGPT, OmicsLM, BIOREASON | annotation error 0.76% vs 6.42%; BLEU-2 0.344 vs 0.019; relative rank .740 vs .090 |
  | H over a single channel | CellWhisperer, CellTosg2Sequence | mild; 0.385 vs 0.268 |
  | Perceptual over T | OpticalDNA | AUROC 0.626 vs 0.558 |
  | T over E | TISSUENARRATOR (coordinates) | qualitative only |

## F6. Hybrids are the convergence point, but they are also untested by neutral evaluation

- 8 works combine both channels; 11 works deliver one modality through two carrier formations.
- In both controlled tests, the hybrid beat its single-channel part (CellWhisperer, CellTosg2Sequence).
  In both cases the hybrid is the proposed configuration.
- Within the token-native culture, RVQ-Alpha gains 8.3 pp by adding gene evidence in text to learned codes.
- Hybrids appear from 2024 on.

## What the paper can claim

1. Generative text–biology models fall into two design cultures and a growing hybrid.
2. The two cultures preserve complementary parts of biological data (identity vs magnitude) and are
   transparent in complementary ways (form vs parameters).
3. Where authors discuss the choice, both cultures state the same trade-off.
4. The field's evidence about which culture works better cannot settle the question:
   - comparisons favour the proposer 28 of 31 times (90%);
   - comparisons are run mostly against released, unadapted forms of the other culture, and opponents
     built by the proposers lost every time;
   - dependence tests are rare in every culture (22 of 51 works).
5. This motivates a neutral protocol:
   - the same backbone and training budget;
   - a matched information budget;
   - both identity-level and magnitude-level tasks;
   - dependence controls;
   - a reporting card for input representations.

## Robustness and limitations

Stress test of the story and claim audit: `STRESS_TEST.md`.

- Charting is by two runs of one model family, adjudicated by one steward.
  - Agreement: synthetic text κ 0.96, comparison presence κ 0.92, dependence tests Jaccard 0.91,
    outputs 0.89, LLM state 0.89.
  - Evaluation formats (Jaccard 0.57) and rationale (0.60) are weaker. Headline uses of both were
    adjudicated from quotes.
  - A second human coder for the 31 comparison units and the culture assignment is recommended before
    submission.
- The culture assignment for mixed-collection works is a steward judgement. Geneverse is coded T
  although its LLaVA models are E.
- n is small (17/16/8/9). The year trend (2023–24 vs 2025–26) is descriptive only.
- Publication bias inflates home advantage; this is part of the finding, not only a limitation.
- Charting recall is imperfect: one comparison shown only in a figure (CellTosg2Sequence vs C2S-Scale-27B
  on Tahoe-100M, won by the proposer) was missed by both runs and is not counted.
- The earlier keyword pre-screens skipped appendices after the reference list. The charting pass used
  the complete text, and its counts supersede the pre-screen counts.

## Novelty against prior reviews

- Recent surveys classify models by family and task: ACL 2025 single-cell foundation language models;
  LLM4Cell (58 models, "text-bridge" family); LLMs meet virtual cell; Nature 2025 multimodal-foundation-
  model perspective; 2026 Cell Systems compositional-FM review.
- None measures what each design keeps of the measurement, how designs justify themselves, or how
  cross-design comparisons are constructed.
- Individual papers state the trade-off (OmicsLM, InstructCell, scMMGPT, Bio-BLIP, Cell2Sentence).
  The cross-corpus synthesis and the home-advantage and baseline-asymmetry analysis are new.
- Every citation must be verified before the manuscript uses it.
