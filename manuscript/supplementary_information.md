# Supplementary Information

Translate or encode? Two design cultures for coupling language and omics data in generative foundation
models: a scoping review.

Supplementary items are numbered by type in the order in which the article first cites them. Numbers
in square brackets refer to the article's reference list. Data files are listed at the end with their
column dictionary.

## Supplementary Notes

### [[S:search_strings]] Search strategies as executed

Every query string as executed, by round and source, with the execution date and the number of records
retained from each source. The strings are reproduced verbatim from the search configurations.

{{include:search_strategies}}

### [[S:search]] Search: rounds, dates and source-specific details

The five rounds retained 5,534, 867, 933, 197 and 639 records (8,170).

**Dates as executed.** PubMed, arXiv, Europe PMC, Springer Nature and OpenAlex were queried with exact
dates. Scopus and Semantic Scholar were queried by year, and records outside the window were then
removed by exact date. Records removed (Scopus/Semantic Scholar): 18/1 in the baseline, then 165/226,
292/462, 389/766 and 485/914 in the top-ups. In round 5, 39 Semantic Scholar records without a
publication date were kept. Google Scholar was queried by year only. The baseline ran on 2026-02-15, so
no date-bounded query covered records dated 2026-02-16 to 2026-02-28.

**Springer Nature.** The free API searches full text and cannot be restricted to title and abstract.
Retrieved records were therefore kept only if a term from each concept block appeared in the title or
abstract. Raw to validated, by round: 17,130 to 272, 1,185 to 33, 1,129 to 27, 510 to 20 and 691 to 27.
The flow counts the validated records.

**Google Scholar completeness.** The April and June rounds were rate-limited after 5 of 7 queries, and
the July round returned no records. The baseline completion log was overwritten by a later Springer
Nature-only rerun; the retained baseline records are preserved.

**Gap between search windows.** On 2026-10-14 the baseline queries of PubMed, arXiv, Europe PMC and
Semantic Scholar were re-run for the window 2026-02-16 to 2026-02-28. They returned 51 unique records.
17 had already been retrieved and 34 had not; none of the 34 met the eligibility criteria in an
indicative single-pass LLM title/abstract triage. Scopus and Springer Nature were not re-run.

### [[S:decomposition]] Operation-level decomposition: rules, runs and stability

**Library.** Each documented input path is reconstructed as a directed graph of calls to a library of
22 reusable operations (normalisation, log transform, binning, tokenisation, table lookup, projection,
concatenation, attention and others) with named ports and instance parameters, following the
operation guide and the catalog definitions of release 1.3.0. Steps whose internal computation the
paper does not state remain unexpanded boundaries. A four-paper pilot (ChatNT, InstructCell, X-Cell,
MUPAD; 47 trajectories, 509 operation calls) was curated by the authors.

**Agent decomposition.** The remaining 50 papers were decomposed by agents (Codex CLI, gpt-5.6-luna,
reasoning effort high; the earlier gpt-5.4-mini is no longer available through Codex) under version 3.2
of the decomposition protocol, which sharpens the boundaries between align, concatenate and serialize,
and between partition and select, after run-to-run disagreements under version 3.1. The structure is fixed by the charted
routes: one trajectory per charted configuration and one step per element of each route's verbatim
transformation chain. For each step the agent returns only a decision, a closed category plus the
library operation(s) named in the element text, with stated parameter values, verbatim evidence and
the echoed chain element. A predefined rule set decides the category (for example unexpanded learned
module, data provenance, external text generator, unspecified fusion). Routes without a recorded chain
get a mechanical decision. Nodes, ports and data flow are compiled from these decisions, and the
result is checked mechanically for verbatim evidence, catalog ports and declared parameters. The full
paper text is supplied without truncation. Each paper was decomposed in three independent runs (up to
four mechanical repairs each), and the published decision per step is the majority label. Steps
without a majority remain unresolved boundaries and are listed for the library steward, as are steps
decided 2 of 3.

**Parameter pass.** A separate parameter pass then read the whole paper again, with the operations
fixed. For every declared parameter of every library call (2,433 slots in 1.3.0, defined in the
operation parameter glossary) it decided whether the paper states the value for that data path, with
verbatim evidence checked mechanically. Values that only follow from convention, released code or
cited papers do not count. This pass also used three runs per paper and the majority status; its rules
were tuned on the ten development papers (two iterations) and then frozen. Before the first run we
fixed its gate: on ten held-out papers, consensus status agreement between runs 1-3 and 4-6 of at least
0.90. The result was library release 1.2.1. Under version 3.2, 39 of 1,468 steps changed operation; the
parameter pass was repeated for the 16 affected papers (three runs), and slots of unchanged calls were
carried over. The result is library release 1.3.0. No reviewer-agent pass was run on it.

**Development and stability.** The protocol was developed iteratively on ten length-stratified papers
and evaluated on held-out papers with the rules frozen. Stability was measured as agreement between
the consensus of runs 1-3 and of runs 4-6 against a predeclared gate. Of the 1,468 agent-decomposed
steps, 1,394 (95.0%) were decided identically in all three runs and 74 (5.0%) by two of three; every
step had a majority. Under version 3.1 with frozen rules, the consensus of runs 1–3 and of runs 4–6 on ten
unseen papers agreed on 95.6% of steps and 85.4% of complete routes. After the boundary fixes of version 3.2,
the same papers agree on 99.6% and 98.8%. That second figure is in-sample, because these papers
informed the fixes. Across the three production runs under version 3.2 on all 50 agent-decomposed papers, 90.9% of route ×
run-pair comparisons had identical operation sequences (gate: at least 90%) and the median paper-level
operation-set Jaccard was 1.0, but five papers fell below the predeclared minimum of 0.75 (lowest 0.0
for Chroma, where one run produced a disjoint set). The full-corpus gate was therefore not met;
release decisions use the per-step majority of the three runs. For the parameter pass, 88% of slot
decisions were unanimous across runs, and held-out consensus status agreement was 0.992. The withdrawn
OKR-Cell preprint is not included.

### [[S:motifs]] Motifs, design axes and archetypes

**Model-level paths.** For each model configuration, the decomposed routes (agent-decomposed papers) or the
author-curated graphs (pilot papers, all root-to-model paths) were turned into paths of role-aware
operation tokens. Provenance and identity steps were dropped and repeated identical operations
collapsed. Each operation's role follows from its inputs: biological only, text only, or joining
biological and text inputs. Unexpanded learned modules were kept as typed tokens.

**Motifs.** Closed frequent sub-chains (contiguous and gapped) were mined at the operation and family
levels, with support counted in papers (at least 4 papers; no length limit). Supported, interpretable
sub-chains were named as motifs with templates, members, parameter reporting and evidence-quoted
examples (Supplementary Table [[S:motif_library]]). Stability: mining was repeated on each single
decomposition run.

**Design axes.** Each route was also coded on five axes along one canonical pipeline (source, curation,
value transformation, carrier formation, interface): carrier formation, interface to the language
model, transformation of measured values (order only, discretised, learned compression, verbatim; with
subset and normalisation modifiers), text role and transparency. Coding rules are deterministic over
the chains and the charted atlas labels (Supplementary Table [[S:codebook]]). We tested coverage,
independence (normalised mutual information) and robustness to decomposition runs. Archetypes are
carrier x interface combinations; a model can carry several.

**Earlier analysis.** An earlier version of this analysis compared exact route chains and reported no
recurring recipes. That result was an artefact of chain construction (uneven wording granularity,
non-computational steps counted as operations, fragmentary routes) and is withdrawn.

### [[S:ai]] Use of AI tools, reported by PRISMA-trAIce item

**Tasks and tools.** LLMs were run through the Codex command-line agent (Codex CLI; the version of the
agent was not recorded with the runs). gpt-5.4-mini was used for title and abstract screening,
full-text screening and route charting; gpt-5.6-luna with reasoning effort high was used for the
operation-level decomposition, the parameter pass and the targeted charting pass, because the earlier
gpt-5.4-mini is no longer available through Codex. Full texts were converted with Docling (version
2.110.0), and Docling Graph (version 1.7.0) reconstructed the complete data-source and
input-representation sections that full-text screening used.

**Screening.** Title/abstract screening applied the eligibility decision tree with two role-separated
LLM reviewers (scope and architecture) and an adjudicator for conflicts; prompts and schemas were
hash-pinned. Full-text screening (baseline run on 2026-07-10) used Docling conversions; Docling Graph
provenance reconstructed the
complete data-source and input-representation sections, which were screened with the title and
abstract. Records still uncertain after adjudication were resolved by the review lead from the full
sections, keeping the automated decision alongside. The roles are prompts executed by the same model,
not independent human reviewers.

**Route charting.** Routes were extracted from the full text with three frozen direct runs plus
dense-coverage candidates. Agreement across the three runs on the 55-record corpus: route Jaccard
0.945–0.969; carrier-family exact agreement 0.929; Krippendorff's alpha 0.881 (acceptance thresholds
0.80, 0.90, 0.80). Dated author-led amendments are recorded in the atlas metadata.

**Decomposition and parameter pass.** Supplementary Note [[S:decomposition]] gives the rules, runs and
stability.

**Targeted charting pass.** The pass followed a frozen protocol (design-culture charting, version 1.1).
Every item required verbatim evidence. Quotes were checked mechanically against the paper, with up to
three repairs per run; all 108 runs passed validation. One quote broken by PDF line numbers was
corrected by the steward. Run agreement was high for comparison presence (κ 0.92), LLM-generated text
(κ 0.96) and dependence tests (Jaccard 0.91), but lower for evaluation formats (0.57) and rationales
(0.60).

**Adjudication and human involvement.** The library steward is an agent-assisted role: an AI assistant,
directed by the review lead, applies written rules to the verbatim evidence and records each decision
with its reason. The steward adjudicated the rationale items, the single-run dependence tests and the
cross-representation comparison units, and assigned each work to a culture. The charting runs returned
217 comparison items, which adjudication merged into 31 comparison units in 20 works; three further
units were set aside as within-culture or not about representation form. A second human coder for the
31 comparison units and the culture assignment, with a recall audit of comparisons, is planned. The
review lead approved the targeted charting pass and resolved the records left uncertain by automated
full-text screening, and the authors curated the four pilot decompositions.

**Prompts, schemas and run records.** The prompts, output schemas, rule sets, run configurations and
run outputs of every step are in the project repository; the supplementary file index lists their
locations.

### [[S:coverage]] Coverage of protein and nucleotide models

A coverage check found that 12 protein and biomolecular text–generative models (ProteinDT, BioT5,
BioT5+, NatureLM, Evolla, Galactica, InstructProtein, ProtLLM, Prot2Text, ProtT3, ProLLaMA, TxGemma)
were never retrieved. None has a term of the biological-data block in its title or abstract. In the
PubMed query for 2018-01-01 to 2026-08-09, a protein block in place of the biological-data block adds
1,140 records that the original block does not match (the original query returns 939), and a
nucleotide block adds 508. In Europe PMC preprints the additions are 1,130 and 633 (hit counts on
2026-10-15).

## Supplementary Tables

### [[S:deviations]] Deviations from the protocol

Amendments of the protocol after its first version under version control (version 3.0), and further
changes that the protocol did not foresee. "Made after results were seen" records whether the change
was decided after results of the review (or, where stated, after procedural results) were known.

{{table:deviations}}

### [[S:search_runs]] Search runs by round and source

Execution date, limits as executed, the number of hits reported by the source's interface and the
records retained, for each round and source; "not searched" marks a source that was not searched in a
round. The interface, the records fetched, the Springer Nature counts before validation and the export
file of each run are in the data file.

{{table:search_runs}}

### [[S:exclusions]] Reports excluded at full text, with reasons

One main reason per report, as recorded at full-text screening.

{{table:exclusions}}

### [[S:models]] Charted models

One row per charted model ({{rows:charted_models}} models): the record, paper title, DOI and year, the number of routes and
configurations, the input-carrier families, the primary carrier subtype, fusion topologies, text roles,
lifecycle phases and biological modalities. Data file only.

### [[S:works]] Included works: design culture and charted variables

One row per independent work. Dependence test: whether the work reports any test of whether outputs
depend on the biological input (found by both charting runs, or by one run and confirmed at
adjudication). LLM-written text: whether text written by an LLM was used for training or evaluation.
Language-model adaptation: how the language model is trained, where both charting runs agree (LoRA,
low-rank adaptation; "none recorded" when no category was found by both runs). Cross-culture units:
comparison units between arms of different cultures. Opaque steps: median share of the work's
biological route steps that are learned modules left unexpanded. Unstated slots: share of the parameter
slots of the proposed and component models whose value the paper does not state. A dash marks a work
without a decomposed biological route or without parameter slots.

{{table:works}}

### [[S:motif_library]] Motif library

Motifs are closed frequent sub-chains of role-aware operations supported by at least 4 papers.
Operations: library operations in order. Input: whether the operations act on biological input, on text
input, or join the two. Contiguous: whether the operations must be adjacent. Papers and models: support.
The reporting of each motif's parameters and an example with its verbatim evidence are in the data file.

{{table:motifs}}

### [[S:comparisons]] Cross-culture comparison units

One row per comparison unit after adjudication: one comparison between arms of different cultures, per
work and task family. Design: a controlled ablation within one system, the same backbone given the data
as text, or different systems. Opponent arm: its culture and how it was obtained. Values reported: as
quoted in the charting; a dash marks a unit without values in the text. Image rendering is the
DNA-as-image arm of OpticalDNA.

{{table:comparisons}}

### [[S:budgets]] Gene and token budgets stated in the papers

Values as stated in the papers. (a) Genes or features kept per cell or object when a profile is written
as text or passed to an encoder; "not stated" marks a route whose number the paper does not give. (b)
Vectors, discrete codes or text tokens per object passed to the language model.

{{table:budgets}}

### [[S:synthetic]] Text written by LLMs and used for training or evaluation

Works that train or evaluate on text written or rewritten by another LLM. What was written: training or
evaluation content, or instruction templates only. Human check: whether the paper reports a human check
of the generated text. Reasoning traces: whether the generated text includes reasoning traces. Used in
evaluation: whether LLM-written text enters the evaluation.

{{table:synthetic}}

### [[S:codebook]] Route-level design-pattern codebook

One row per charted route of the 50 agent-decomposed papers ({{rows:route_codebook}} routes): the
model and configuration, lifecycle phase, source
modality, carrier family and subtype, fusion topology, text role, the operation chain, the value of each
design axis with the rule that assigned it, the share of opaque steps, the share of stated parameters
and the archetype. Data file only.

## Supplementary Figures

### [[S:flow]] Full PRISMA 2020 flow, with the records identified per database

Records identified per source and round, records removed before screening, records screened and
excluded, reports sought, not retrieved and assessed, and studies included. Reasons for exclusion at
full text are given in Supplementary Table [[S:exclusions]].

{{figure:flow}}

## Data files and column dictionary

{{datafiles}}
