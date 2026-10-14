# Stress test of the paper-1 story (2026-10-14)

Manuscript: `manuscript/review_manuscript_draft.md` (draft v0.4). Numbers:
`analysis/design_culture_charting_2026-10-14/v11/design_culture_numbers.json`
(`scripts/build_design_culture_synthesis.py`).

## 1. Arc review (paper-narrative handling-editor pass)

Input: the v0.3 abstract and one claim per planned figure (no rendered deck yet). Output:
`narrative_review_v1.json`. Verdict: would send for review "weak", because the arc opened with the
PRISMA flow and the evidence figure existed only as text.

| Suggestion | Action |
|---|---|
| Open with the two-cultures contrast, not the PRISMA flow | Adopted: new Figure 1 (concept and budgets); PRISMA becomes Figure 2a plus Supplementary Figure S1 (PRISMA-ScR still needs the flow in the paper) |
| Merge operation reuse and motif library | Adopted: Figure 3 (a) operations, (b) motifs, (c) archetype–motif–culture correspondence |
| Show budgets per work, not only medians | Adopted as Figure 4 specification; per-culture values added to the text and to `budget_by_culture` |
| Make the evidence a full figure | Adopted: Figure 5 (rationales, supervision and dependence, 31 units with opponent class, per-work count) |
| Give the reporting card a visual anchor | Adopted as Box 1 |
| Demote the corpus landscape | Kept as Figure 2b–d next to the flow |

The reviewer's own Fig. 1 suggestion described "a 32-dim vector"; the data are 1–256 vectors per object
(median 32), not dimensions. The figure specification uses the correct quantity.

### Second pass (revised abstract and arc; `narrative_review_v2.json`)

Verdict again "weak", for a different reason: the new Figure 1 showed the two cultures but not the
finding that the published comparisons cannot choose between them.

| Suggestion | Action |
|---|---|
| Put the evidence result on page 1 | Adopted: Figure 1b shows the 31 comparisons as proposer × winner by opponent provenance |
| Stratify comparisons by task | Done: within every task family the winner followed the proposer; non-wins only in categorical tasks (2 of 10) and embedding quality (1 of 4) |
| Stratify dependence tests by whether the work made a comparison claim | Done: 10 of 20 vs 12 of 31 (Fisher p = 0.56), no difference |
| Model win/loss on opponent type, parameter ratio and pretraining-data ratio | Not done: with 3 non-wins in 31 units the model is not estimable (separation); the exceptions are described individually |
| Re-run one matched comparison under the Box 1 protocol | Not done: needs new experiments; candidate companion benchmark study |
| Demote the five-group enumeration | Abstract now uses one sentence; the table stays in §3.4 |
| Move operation inventory and full PRISMA counts out of the main figures | Figure 3a shows reuse and unreported parameters only; full flow is Supplementary Figure S1 |

The reviewer's wording ("rigged", "artifacts") is stronger than the data allow. The manuscript keeps
the claim that the published comparisons cannot rank the cultures, not that they are wrong.

## 2. Claim audit

Each abstract and Results claim was traced to a table or the numbers file. Corrections:

| Claim in v0.3 | Problem | v0.4 |
|---|---|---|
| "Encoder-mediated works pass 331–20,541 input features ... as 1–256 vectors (median 32)" | Ranges pooled across cultures (6 and 11 works include hybrid, language-conditioned, alignment-only and one token-native work) and juxtapose different works | "Works that inject encoder outputs" with denominators; per-culture values in §3.5 (encoder-mediated: 1–256 vectors, median 32, 7 works; 2,048–20,541 features, 3 works) |
| "Values appear as numbers in only 2 works" placed under token-native | One of the two (P3GPT) is hybrid | "in only 2 of the 51 works" |
| "The opponent was usually the other culture's weakest form" | Value judgement; 11 of 31 opponents were trained by the proposers | "released, unadapted form"; proposer won all 11 self-built and 16 of 19 released units |
| "external frozen models with simple heads (7 of 10)" | One of the seven (CellWhisperer) was used as published | "released encoder-based models used frozen or as published" |
| "only 4 of the 16 encoder-mediated works" test dependence; "the culture where a language model can most easily ignore its input" | Not different from other cultures (Fisher p = 0.13 vs rest; 0.46 vs token-native); mechanism is speculation | Reported in parentheses; §3.8 states no detectable difference; mechanism attributed to Bio-BLIP's authors |
| "trained on far more single-cell text" (C2S-Scale exception) | Our inference | Attributed to the CellTosg2Sequence authors (about 8,000 annotation examples in their reinforcement stage vs C2S-Scale's pretraining corpus) |
| GPT-OSS-120B exception | An 8B general model lost in the same comparison | Added (0.369) |
| "When raw sequence letters were given to a general LLM, encoders won 5 of 7" | Two of the seven token-native arms were trained models, not general LLMs | "When the token-native arm read raw sequence letters" |
| "the loss that cannot be recovered is therefore ..." | Overstated; rank–expression fit is population-level | Conditional wording; adds cell-specific departures from the fit |
| "Encoder-mediated inputs keep magnitudes" (Discussion) | Retention inside encoders is untested in most works | "pass values and structure to learned modules, so what survives is not visible and is rarely tested" |
| "the field already agrees on the trade-off" | 7 of 17 and 7 of 16 works state it | "Where authors discuss the choice ..." |
| Implications: "magnitude- and sequence-level tasks favour encoders; hybrids are the natural default" | Contradicts §4.2 (evidence cannot rank cultures) | Recast as working hypotheses testable with Box 1 |
| "These reviews classify models by family and task" | Needed a verified example | LLM4Cell (arXiv:2510.07793): 58 methods, five families, eight tasks; other citations still [CITE] |
| "No cross-paper account asks ..." | Unverifiable negative | "We are not aware of ..." |

## 3. Added analyses

- Units are nested in works. Per work, the proposer won every unit in 17 of 20 works (sign test
  p = 0.0026) and every between-system unit in 14 of 17 (p = 0.013).
- Opponent class: released (prompted LLMs, external embeddings or pretrained models) 19 units, proposer
  won 16; trained by the proposing team 11 units, proposer won 11; one unit without a model. All three
  exceptions (U16, U26, U33) had released opponents.
- Opponent type by proposing culture: prompted LLMs 8 of 13 encoder-paper units vs 0 of 10 token-native
  (Fisher p = 0.0027); released encoder models 7 of 10 vs 0 of 13 (p = 4.9 × 10⁻⁴). Partly by
  construction.
- By task family and by comparison status: see the second-pass table above.
- Culture contrasts (exploratory, unadjusted): dependence tests T vs E p = 0.46, E vs rest p = 0.13;
  LLM-written text T vs E p = 0.73, language-conditioned vs rest p = 0.024 (1 of 9 vs 24 of 42); frozen
  LLM E vs T p = 0.10.
- What makes the groups "cultures" (§3.4): justifications and opponent choice co-vary with the input
  route; LLM-written text, dependence tests and fine-tuning practice do not. Budgets and motif families
  follow from the definition.

## 4. Known gaps that remain

- Charting recall: a Tahoe-100M comparison of CellTosg2Sequence against C2S-Scale-27B (proposer won),
  shown only in a figure, was missed by both runs and is not counted (found while checking exception
  U26; not a systematic audit). A recall audit belongs to the second-coder check.
- Second human coder for the 31 units and the culture assignment.
- Figures 1, 3, 4 and 5 are drawn (`scripts/build_design_culture_figures.py`, outputs and per-panel
  source data in `analysis/design_culture_charting_2026-10-14/v11/figures/`). Figure 2 still needs the
  culture breakdown; Box 1 is to typeset.
- Culture check for the second coder: four encoder-mediated works carry verbalisation motifs (Cell2Text,
  Med-PaLM M, OpticalDNA, `july_update_2026-07-06__rec_000050`) and four token-native works carry encoder
  motifs (OmniNA, C2S-Scale, CellHermes, Human Genome Book). Confirm that the coded culture follows the
  main route by which biology reaches the generative model.
- All [CITE] entries to add and verify.
