# Design-pattern taxonomy of text–biology input chains (v2, 2026-10-14)

Data: release 1.3.0 (route archetypes depend only on charted labels and are unchanged from 1.2.1). Unit: one charted input route (source object -> model-visible form) of the 50
agent-decomposed papers (532 routes, 101 models); the 4 pilot papers are coded at model level only
where route-indexed data exist (not yet). Each route carries its consensus operation chain, its
parameter status and the atlas labels (carrier family/subtype, fusion topology, text role).

## Two levels: design axes and motifs (revised 2026-10-14, release 1.3.0)

Correction. v1 of this spec argued that exact operation chains do not recur (252 distinct sequences in
532 routes, edit-distance silhouette at most 0.10). That statistic was largely an artefact of how the
route chains were built:
- one step per charted wording phrase, so granularity differs by paper (median 1-7 steps per route);
- provenance and identity steps were counted as operations (21% of steps);
- routes stop at the model-visible form.
After removing these artefacts, and with the 1.3.0 boundary fixes, recurring sub-chains appear. They
are collected in the motif library (`analysis/motif_library_2026-10-14/MOTIF_LIBRARY.md`).

The systematisation therefore has two complementary levels:
- Motifs: frequent role-aware operation sub-chains (15 motifs, 44 of 54 papers contain at least one;
  the most widespread, encoder then projector, occurs in 18 papers). They describe how input pipelines
  are built.
- Design axes and archetypes (below): where the carrier meets the language model and what happens to
  the values. They describe what kind of input a model receives.

The two levels agree. Of models whose motifs are all verbalisation motifs, 16 of 19 have the verbalised
token-stream archetype as primary. Of models whose motifs are all encoder motifs, 23 of 28 have an
encoder-based archetype (soft tokens, conditioning, attention bridge, latent alignment) as primary
(`analysis/motif_library_2026-10-14/motif_category_vs_archetype.csv`). No sub-chain is shared by all
architectures.

## Axes (route level)

A1 Carrier formation: how the source becomes something the model can read.
- `text_source`: the source is already text (prompt, question, annotation, metadata text).
- `verbalised`: non-text biology rendered as natural-language/text tokens (cell sentences, serialised
  profiles, structured biological prompts).
- `symbolic`: biology tokenised in its own alphabet (nucleotides, amino acids, k-mers, codebook ids).
- `embedded`: biology encoded into dense vectors by a learned encoder/projection.
- `perceptual`: raw images/patches or geometric/diffusion states passed to a modality encoder.

A2 Interface to the language model: where the carrier meets it.
- `token_stream`: shares the language model's token sequence (tokenizer sequence, interleaving;
  concatenation of text or symbol carriers into the prompt).
- `embedding_slot`: dense vectors inserted as soft tokens (prefix, placeholder replacement,
  concatenation of dense/visual carriers).
- `attention_bridge`: read through cross-attention or a query bottleneck (Q-Former, resampler).
- `latent_alignment`: aligned in a shared latent space (e.g. contrastive) without direct insertion.
- `conditioning`: conditions a generator or decoder (side/generative conditioning, encoder-decoder).
- `external_context`: supplied via retrieval or tools.
- `unresolved`: charting gave no clear interface.

A3 Information transformation (biological sources only): what the chain does to the measured values.
- `order_only`: ranking kept, magnitudes dropped (rank in the chain).
- `discretised`: values mapped to bins or learned codes (bin; quantised code tokens).
- `learned_compression`: an encoder/projection compresses the data (encode stage, no rank/bin).
- `verbatim`: data copied as symbols or text without rank, bin or encoder.
- `unresolved`: no library operation decided for the route.
Modifiers: `subset` (a select step), `normalised` (normalize/log_transform present).

A4 Text role: what text does on this route (instruction, context, payload, supervision, none).

A5 Transparency: whether the computation is reconstructable from the paper.
- opaque-step share = unexpanded computational steps (learned module, unspecified fusion, no-catalog
  computation, external generator, tie) over all computational steps (provenance and identity steps
  excluded); stated-parameter share over all declared parameters of the route's library calls.
- `transparent`: no opaque step and >= 2/3 parameters stated; `opaque`: no library call among the
  computational steps; `partial` otherwise; `no_computation` if the route has no computational step.

Decision rules: `scripts/build_design_taxonomy.py` (applied mechanically, no new LLM calls).

## Axis tests (`axis_tests.json`)

- Coverage: A1 100%, A2 96.1% (21 routes charted as unclear/other), A3 99.8%, A4 and A5 100%.
  A3 falls back on the atlas carrier subtype for 90 of 367 biological routes whose chain has no
  decided library operation (rule recorded per route).
- Independence: pairwise normalised mutual information 0.04-0.34 (highest A1-A3, Cramér's V 0.46).
  No axis is redundant; the associations are the expected design couplings.
- Robustness to decomposition noise: on the 20 papers with repeated runs (dev, heldout4), recoding
  from each individual run gives pairwise agreement A3 0.997, A3 modifiers 0.990, A5 0.955. A1, A2 and
  A4 are derived from charted labels and do not depend on decomposition runs.
- Relation to the existing five-family taxonomy: A1 refines it (Cramér's V 0.86 with carrier family);
  it adds the split of text-native carriers into original text and verbalised biology. The new
  information is in A2, A3 and A5, and in their combinations.

## Archetypes (A1 x A2; A3 as variant)

Each biological route (A1 != text_source) is assigned one archetype:
token_stream + verbalised -> VERB; token_stream + symbolic -> SYMB; embedding_slot -> SOFT;
attention_bridge -> XATT; conditioning -> COND; latent_alignment -> ALIGN; external_context -> TOOL;
unresolved interface -> UNRES; token_stream with an embedded/perceptual carrier -> OTHER_TOK (rare).
Models carry several archetypes when their biological routes differ (30 of 79 models with biological
routes); a model's primary archetype is the one used by most of its biological routes.

VERB, verbalisation into the language model's token stream. Biological data are written as text
(cell sentences, serialised profiles, structured prompts) and read by an unchanged language model.
Variants: verbatim rendering (91 routes) and rank-ordered gene lists (21 routes; order kept,
magnitudes dropped). Typical chain: select -> (normalize -> log_transform -> rank) -> serialize.
18 papers, 29 models, 115 routes; median opaque-step share 0.00, median stated-parameter share 0.67; transparency {'partial': 62, 'transparent': 39, 'no_computation': 12, 'opaque': 2}. Unspecified parameter slots 280/784 (36%). Trade-off: no new parameters and full
reuse of the language model, but values are discretised by text, and context length limits how much
of a profile fits.
Examples: C2S-Scale, Cell-o1, CellHermes, CellTosg2Sequence.

SYMB, biological alphabet in the token stream. Sequences are tokenised in their own alphabet
(nucleotides, k-mers, amino acids, codebook ids) and share the token sequence with text, usually
through an extended vocabulary. 8 papers, 11 models, 35 routes; median opaque-step share 0.00, median stated-parameter share 0.86; transparency {'partial': 11, 'transparent': 11, 'no_computation': 11, 'opaque': 2}. Unspecified parameter slots 37/144 (26%).
Trade-off: lossless for sequence data, but it needs vocabulary extension and pretraining on the
alphabet. Examples: Omni-DNA, OmniNA, GenNA, RVQ-Alpha.

SOFT, encoded soft tokens. A modality encoder (often frozen) produces vectors that a projection
inserts as soft tokens (prefix or placeholder replacement). Typical chain: learned module ->
project (-> placeholder update). 24 papers, 29 models, 84 routes; median opaque-step share 0.40, median stated-parameter share 0.67; transparency {'partial': 68, 'transparent': 10, 'opaque': 6}. Unspecified parameter slots 128/398 (32%).
Trade-off: keeps magnitudes and uses strong encoders, but the content is opaque and connector
training is needed. Examples: BioMedGPT-10B, BIOVERSE, ALTER.

XATT, attention bridge. The language model reads biological features through cross-attention or a
query bottleneck (Q-Former, resampler). 7 papers, 7 models, 29 routes; median opaque-step share 0.33, median stated-parameter share 0.63; transparency {'partial': 23, 'transparent': 5, 'opaque': 1}. Unspecified parameter slots 89/230 (39%).
Trade-off: fixed token budget for any input size, but more architecture and less transparency.
Examples: scMMGPT, scMIR, Bio-BLIP, scMOBA.

COND, conditioning a generator or decoder. Biological or text embeddings condition a generator
(diffusion, flow, encoder-decoder) instead of entering a language model's input sequence.
17 papers, 20 models, 49 routes; median opaque-step share 0.67, median stated-parameter share 0.62; transparency {'partial': 23, 'opaque': 18, 'transparent': 6, 'no_computation': 2}. Unspecified parameter slots 61/137 (45%). This is the least transparent archetype.
Examples: Cell2Text, Chroma, H2O, CaLMFlow.

ALIGN, shared latent alignment. Modalities are aligned in a shared space (e.g. contrastive), with
no direct insertion into the language model input. 7 papers, 9 models, 18 routes; median opaque-step share 0.50, median stated-parameter share 0.67; transparency {'partial': 15, 'transparent': 2, 'opaque': 1}. Examples: LEONINE, PROCYON, OCellus.

TOOL, retrieval or tool context. Biology enters as retrieved or tool-produced context.
3 papers, 3 models, 7 routes; median opaque-step share 0.00, median stated-parameter share 0.83; transparency {'no_computation': 4, 'opaque': 2, 'partial': 1}. Examples: OCellus-Agent, PROCYON.

UNRES: interface not resolvable from the charting (12 papers, 14 models, 18 routes; median opaque-step share 0.17, median stated-parameter share 0.57; transparency {'partial': 7, 'no_computation': 5, 'opaque': 4, 'transparent': 2}); listed in `unresolved_routes.csv`.
