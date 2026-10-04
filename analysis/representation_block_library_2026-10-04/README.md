# Operation library, release 1.0.0

Rebuilt 2026-10-05 following the author's clarified unit: one reusable data
transformation with defined operands and results. The failed 91-entry catalog,
its generated 0.1.0 release and obsolete steward descriptions were removed from
the active tree. Commit `a61f9c2b` preserves that development history.

The editable `operation_catalog.json` defines normalization, log transformation,
binning, tokenization, table lookup, learned projection, concatenation, partition,
selection, ranking, serialization, padding, addition, sampling, attention,
imputation, clamping, indexed updates, alignment, augmentation and reshaping.
Model/biological names, dimensions, intermediate representations and component
roles remain invocation/node metadata. They create no additional library types.

`pilot_input.jsonl` and `evidence_snapshot.json` are unchanged complete sources.
The four-paper/47-trajectory source inventory remains intact. Compiled chains
retain all original nodes, operands, steps, phases, recipients and uncertainty.
Every original trajectory is reconstructed exactly in a full equality check.

Explicit source composites are decomposed into primitive calls: lookup/LayerNorm,
projection/LayerNorm, scaling/log1p, projection/slot partition, query self-/cross-
attention and ranking/selection/serialization. Unknown fusion equations and
opaque generative modules remain unexpanded with their original evidence.

The complete selected OKR-Cell input-embedding section supplies a supplemental
log1p/HVG/binning/parallel-lookup/addition example. Its source is marked WITHDRAWN;
the example is displayed with that status and excluded from primary pilot counts.
`supplemental_examples.json` preserves that curated graph and exact source section.

The machine-generated validation report supplies current usage and cross-paper
reuse counts. Type reuse is measured by distinct primary record IDs. Repeated tasks,
phases and ablations within one paper increase invocation counts, separately.

The shared contract, guide and steward task are in the existing scripts/protocol
locations. The same Pages URL now serves the operation constructor. Tests and
desktop/mobile browser checks cover actual ports, branches, examples and reuse.

No new LLM batch, PDF conversion, VLM call, canonical taxonomy migration or
eligibility change was performed. Mechanical preservation does not certify all
source entailment; unexpanded boundaries remain source-review work.
