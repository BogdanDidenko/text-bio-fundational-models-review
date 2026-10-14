# Operation library 1.3.0: decision memo (2026-10-14)

Scope: definitions and decision rules only. No operation is added, removed or merged.

## Merge criterion

Two operations are duplicates only when the difference between them says nothing about how
biology enters the text model. Identical mathematics is not sufficient.

| Candidate merge | Same math? | Kept separate because | Calls (agent corpus 1.2.1) |
|---|---|---|---|
| self_attention + cross_attention | yes (key/value source differs) | cross-attention is where modalities meet (Q-Former, resamplers) | 12 / 43 |
| impute -> update | yes (update at missing positions) | marks missing data / missing modality | 0 (pilot: X-Cell) |
| augment -> sample + add | composite | marks training-only perturbation (train vs inference input differ) | 4 |

Merging all three changes the number of distinct collapsed operation sequences only from 107 to 105
(418 routes with a library operation), so the merges would buy almost nothing and lose meaning.

## Fuzzy boundaries fixed

Evidence: disagreements between independent v3.1 runs (dev v3_i8, heldout4 v3_h4, rest30) and the
1.2.1 definitions.

1. partition / select. The 1.2.1 definition of partition ("into selected positions, channels, patches
   or feature slots") overlapped select. Runs split on "ROI extraction" (select 5, partition 1) and
   "extracted identity fields..." (select 2, partition 1). New rule: partition divides into parts that
   are all kept; keeping one part and discarding the rest (ROI extraction, cropping, centring a window,
   field extraction) is select.
2. concatenate / serialize. Runs split on "merge prompt with the specified biological metadata /
   cell type" and "combine the prompt with the cell sentence" (serialize 3, unspecified fusion 2,
   concatenate 1; rec_003206, the only paper with consensus ties). New rule: concatenate only when
   every part already exists as its own token or embedding sequence; writing data or fields into a
   prompt, including "merge/combine the prompt with X" and "attach metadata", is serialize.
3. align. Runs used align for "align to natural language" (project 5, align 1), "centered on the
   region of interest" (select 2, align 1) and "attach biological metadata" (serialize 4, align 1).
   New definition: an explicit correspondence between items of data collections (pairing samples,
   mapping identifiers, registering coordinates). Mapping into an embedding space is project,
   centring/cropping is select, attaching metadata to text is serialize, contrastive objectives are
   not catalog operations. The 14 consensus align calls in 1.2.1 all fit the new definition.
4. serialize / update (minor). Structural marker tokens inserted into text are serialize; masking or
   overwriting positions for training is update.

Protocol: operation-decomposition-v3.2 (rules in scripts/operation_decomposition_v3.py). The corpus is
re-decomposed under v3.2 (3 runs per paper, consensus) and split-half stability is re-measured on
heldout4 before 1.3.0 is published.

## Test scope

`tests/test_representation_library.py::test_every_lookup_call_declares_its_key_space` checks that the key
space of each lookup matches the representation type of its input nodes only for the 4 author-curated
pilot assemblies. For the 50 agent-decomposed assemblies it checks only that a key space is stated,
because their node representation types are not curated (agents copy the key space from the paper).
The scope was narrowed when the agent assemblies were added; it was not disclosed at the time.
