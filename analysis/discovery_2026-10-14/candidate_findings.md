# Candidate findings: discovery sweep, verification and screen (2026-10-14)

Scope: 54 records, which are 51 independent works once linked reports are merged (L10):
- Cell2Text 2025/2026;
- CellWhisperer bioRxiv/journal (rec_002105/rec_000827);
- OmniNA 2024/2026 (rec_002327/rec_003394).
All counts are at work level unless stated. Models are coded by role: proposed 84, component 7,
comparator 8, generator 7. Only proposed and component models enter the route statistics.

Sources:
- `candidate_numbers.json`
- `gene_budget_table.csv`
- `token_budget_table.csv`
- `synthetic_text_table.csv`
- `prescreen_controls_llm.json`
- `prescreen_synthetic_text_llm.json`
- the 1.3.0 release tables (`analysis/discovery_2026-10-14/*.parquet`)

Status labels:
- **verified**: numbers recomputed from the release and the source sentences read.
- **pre-screen, read**: found by a keyword scan over all full texts, coded by an LLM and then read by
  me. Sensitivity is limited by the keywords, so these are lower bounds.
- **needs charting**: the data needed are not in our charting; a targeted charting pass is required.

Scores (1–5) are my judgement: S = strength of evidence, N = novelty against existing reviews,
R = relevance to researchers and industry.

---

## A. What survives of the measurement (information-flow audit)

**A1. When transcriptomes are written as text, a cell becomes a short ranked list of gene names.**
- Text routes of proposed models (9 works):
  - genes kept: 5–1000, median 100 (8 works state K);
  - Cell-o1 does not state M in the main text;
  - examples: Cell2Sentence 100, CellHermes 100, ChatCell 100, TeamPath 100, CellTosg2Sequence 200,
    OCellus ~250 (and 5 marker genes per neighbour), GEMGen 50 signed DE genes, C2S-Scale "K = 1000
    often works well".
- Embedding routes (6 works): 331–20,541 features, median ~2,800 (Geneformer and scGPT 2,048,
  InstructCell 3,600 HVGs, X-Cell 4,000, OmicsLM 20,541, MUPAD 331 pathway scores).
- Values: all 9 text routes replace expression values by within-cell rank. Numbers are written as
  numbers in only 2 works (Longevity-LLM CpG beta values; P3GPT blood-biomarker values).
- Counter-evidence: Cell2Sentence calls the encoding "robust and reversible" because of a log-linear
  rank–expression relation; CellTosg2Sequence reports R² ≈ 0.90.
- What is really lost is therefore narrower:
  - every gene outside the top K (≥95% of ~20k genes);
  - cell-to-cell differences that a global rank→expression fit cannot represent;
  - ordering among tied low counts, for which tie handling is stated in 0/24 rank slots.
- Alternative explanation: context-length cost. Cell2Sentence needs about 350 tokens for prompt plus
  100 genes, and RVQ-Alpha estimates 40–80 tokens for 20 genes.
- Status: verified (quotes in `gene_budget_table.csv`). Scores S4 N3–4 R5.

**A2. Interface budgets: whatever the route, a cell reaches the language model through a small fixed budget.**
- Soft-token routes (11 works): 1–256 vectors per object, median 32.
  - 1: BIOVERSE, OmicsLM;
  - 8: InstructCell, Genolator;
  - 10 discrete codes: RVQ-Alpha;
  - 32: scMMGPT, SciCore-Omics, Bio-BLIP, scMIR;
  - 200: CellTosg2Sequence;
  - 256: scMOBA.
- Verbalised routes: about 350 tokens for 100 genes.
- Caveat: a 4,096-dimensional soft token can carry far more than one word, so token count is not
  information content. This is descriptive, not a proof of loss.
- Status: verified (`token_budget_table.csv`). Scores S3 N3 R3.

**A3. The same named method is run at different K, so cross-paper comparisons of cell sentences are not like for like.**
- Original setting: Cell2Sentence uses 100 genes; C2S-Scale recommends 1000.
- When other papers run these methods as comparators:
  - OmicsLM and X-Cell re-run C2S or Cell-o1 with 1,000 genes;
  - text-only LLM baselines receive 50 genes (OmicsLM) or 128 genes (BIOVERSE).
- Status: verified. Scores S3 N4 R4.

**A4. No complete recipe: the parameters that decide what biology the model sees are mostly unreported.**
- Fully specified routes: 52 of 262 biological routes (20%); per-work mean 23% (bootstrap 95% CI 14–33%).
- Works that fully specify every biological route: 4 of 43.
- Slots never stated:
  - rank tie handling 0/24;
  - select forced inclusions 0/105;
  - log base 0/13;
  - sampling temperature 1/28;
  - projection activation 15/76 stated.
- This extends the existing §3.5 result on unstated parameters.
- Status: verified (release 1.3.0). Scores S4 N3 R4.

**A5. Two channels for one object.**
- 11 works deliver the same modality through two carrier formations, for example embedding plus a
  verbalised gene list (PROCYON, P3GPT, OmniGene-4, GenNA, CellTosg2Sequence).
- Where the two are compared inside a paper:
  - CellWhisperer: adding a gene list to the embedding prompt gave "a mild beneficial effect";
  - OmicsLM: a text-only Cell2Sentence-like control (top 100 genes) "ranks last".
- Status: verified for the counts; the within-paper comparisons need charting (D4). Scores S3 N3 R3.

## B. The language side

**B1. Synthetic language: much of the text these models learn from was written by another LLM.**
- Overall: 20/51 works (39%, bootstrap CI 25–53%) train or evaluate on LLM-generated text.
- Kind of text:
  - 16 works: generated biological content (descriptions or captions, QA, conversations,
    interpretations, reasoning traces);
  - 3 works: generated or paraphrased instruction templates only;
  - 1 work: unclear.
- Reasoning traces distilled from frontier LLMs: 6 works, all 2025–26. Generators: o1, Claude 3.7
  and Sonnet 4.6, o4-mini, GPT-4, and a teacher LLM.
- Generators overall: the GPT-4 family appears in ≥12 works.
- Human verification is reported in 5/20.
- LLM-written text is also used for evaluation in 2 works (CellWhisperer, Genolator).
- By period: 2/10 works in 2023–24 versus 18/41 in 2025–26 (Fisher p = 0.28, so not a significant trend).
- Excluding the 4 pilot papers: 19/47.
- Status: pre-screen, read. All 20 cases were confirmed against source sentences, but the keyword
  scan may miss cases. Scores S4 N4 R5.
- Prior work: a scoping review of LLM-generated synthetic data in biomedicine (PMC13156355) reports
  missing prompts and versions and little hallucination evaluation. It covers clinical NLP, not
  text–biology foundation models. LLaVA-style GPT-4 instruction data is the known origin of the recipe.

**B2. At use time, language mostly tells the model what to do, not what the biology is.**
- Inference and evaluation (203 text-bearing routes):
  - 58% procedural (instructions and selectors);
  - 30% verbalised biology;
  - 12% descriptive or annotation text.
- Training: paired supervision is 28% and metadata 11% of 257 text-bearing routes.
- In 17 of 35 works, text at use time is procedural only.
- Status: verified (atlas text roles). Scores S3 N3 R3.

**B3. Biology enters language as names.**
- What verbalised routes carry: entity names (gene symbols, marker lists) in 13 works, sequence
  letters in 8, relations or triples in 5, numbers in 2.
- The bridge is the language model's prior over names. Cell-o1 states that ranked lists "approximate
  the differentially expressed genes used by experts".
- Status: verified (coarse coding of model-visible forms). Scores S3 N3 R4.

## C. How systems are composed

**C1. Stacked foundation models.**
- 41/51 works name at least one upstream pretrained model in their input chains:
  - biological encoders: ESM family 8 works, Geneformer 5, GenePT and text embeddings 5, scGPT 4, Evo 3;
  - language backbones: Llama 8, Qwen 6, Gemma 4.
- Status: route-chain mentions only, so incomplete. Scores S2–3 N2–3 R3.

**C2. Connectors are thin and frozen boundaries are unreported.**
- Projectors are stated as linear (14 slots) or 2–3-layer MLP; activation is unstated in 80%.
- Full-text pre-screen across 32 encoder-bridge works: LLM frozen 10, LoRA 14, full fine-tuning 4.
- Status: incomplete. Scores S2 N2 R3.

**C3. Carrier is a design choice, not a property of the modality.**
- Transcriptomics: verbalised 12 works, embedded 12, symbolic 5, perceptual 3.
- Nucleotide sequence: symbolic 7, verbalised 6, embedded 4, perceptual 1.
- Images: always perceptual (8) and never verbalised.
- This is already partly in the taxonomy. Scores S3 N2–3 R3.

## D. Evaluation (needs charting)

**D1. Is the biology used at all?**
- Keyword pre-screen: at most 18/51 works report any test of whether outputs depend on the
  biological input. Examples:
  - matched versus mismatched input: CellWhisperer, LEONINE;
  - removal or LLM-only baselines: BIOREASON, CellHermes, BioGPT rec_001519, CellTosg2Sequence, OmicsLM;
  - random embeddings: Bio-BLIP, CellTosg2Sequence.
- Several of the 18 are not true tests: shuffled annotations (OmniNA), component ablations, and
  scorer negatives (GEMGen).
- Bio-BLIP explicitly warns that textual cues such as variant IDs let an LLM answer without the embeddings.
- Expected after charting: about 70–80% of works never test this. Potential scores S5 N4 R5.

**D2. Generative models evaluated as classifiers.** About 37% of works mention multiple-choice,
candidate-label or yes/no formats (regex). Potential scores S4 N4 R4.

**D3. Likelihood scoring instead of generation.** 29% of works mention perplexity or log-likelihood
scoring. Potential scores S3 N3 R3.

**D4. Head-to-head contrasts of verbalised and embedded representations inside papers.**
- Examples: OmicsLM, where text-rendered expression ranks last, and CellWhisperer, where adding a gene
  list helps mildly.
- A charted set would be a small meta-analysis across papers. Potential scores S4 N5 R5.

## E. Corpus and trends

**E1. Linked reports.** Three pairs of reports describe the same study and should be linked in PRISMA,
giving 51 independent works.

**E2. Trends from 2023–24 (n = 10) to 2025–26 (n = 41):**
- verbalised routes 20% → 46%;
- symbolic tokens 0% → 29%;
- contrastive objectives 10% → 41%;
- RL or reasoning 20% → 41%.
The early group is small, so these are descriptive only.

## Rigor and novelty screen

Robustness:
- B1 holds without the pilot papers (19/47) and has a 95% CI of 25–53%. The year trend is not
  significant, so it is reported descriptively.
- A4 has a per-work CI of 14–33%. Fully specified shares by modality are 0–29%, so no single modality
  drives it. The parameter status comes from a 3-run consensus (held-out status agreement 0.992).
- A1 is descriptive (n = 9 works) and the median is unchanged without C2S-Scale.
- D1–D4 are pre-screens only.

Novelty against prior reviews:
- Recent surveys exist: ACL 2025 single-cell foundation language models; LLM4Cell (arXiv:2510.07793; abstract at https://arxiv.org/html/2510.07793v2: "first unified survey of 58 foundation and agentic models"; checked by web search 2026-10-14); LLMs
  meet virtual cell; the Nature 2025 perspective on multimodal foundation models in molecular cell
  biology; the 2026 Cell Systems compositional-FM review.
- These classify models by family and task. None measures what reaches the model, at operation level
  and across modalities.
- Some primary papers already state the trade-off qualitatively: OmicsLM ("at the cost of
  quantitative signal and context budget"), RVQ-Alpha, and arXiv 2507.10039 on order ablations.
- Synthetic biomedical data has been reviewed for clinical NLP (PMC13156355), but not for text–biology
  foundation models.
- The text-shortcut risk is known from vision–language models and is mentioned by Bio-BLIP, but it
  has not been quantified for this field.
- Every citation here was found by web search during this session. Each must be verified before it
  enters the manuscript.

Shortlist, ranked by S × N × R:

| Rank | Candidate | Score (S × N × R) |
|---|---|---|
| 1 | D1 Is the biology used? | needs charting; potential 5 × 4 × 5 |
| 2 | B1 Synthetic language | 4 × 4 × 5 |
| 3 | A1 + A3 A cell becomes ~100 names; not like for like across papers | 4 × 3.5 × 5 |
| 4 | A4 No complete recipe | 4 × 3 × 4 |
| 5 | D4 Within-paper verbalised vs embedded contrasts | needs charting; potential 4 × 5 × 5 |
| 6 | B2 + B3 Language at use time is procedural; biology enters as names | 3 × 3 × 4 |
| 7 | A2 Interface budgets | 3 × 3 × 3 |
| 8 | C1–C3, E2 Composition and trends | supporting context |

## Dropped or demoted during verification
- Text-only works (3 by the atlas modality field): an artefact. ChatCell's cell sentences come from
  measured data but are coded as "text".
- Evaluation-only carrier forms (12 models): mostly charting granularity, so dropped.
- Information-determining versus architecture parameters are unreported at the same rate (34% vs 37%,
  Wilcoxon p = 0.08), so there is no difference to report.
- The paper-level association sweep (351 pairs, BH-FDR) found only definitional associations with
  q < 0.1 (for example, embedded carrier with embedding slot, and perceptual carrier with images),
  plus one other: all 8 works that report human evaluation also mention multiple-choice or
  candidate-label formats (q = 0.014). This most likely marks evaluation-heavy papers, not a mechanism.
