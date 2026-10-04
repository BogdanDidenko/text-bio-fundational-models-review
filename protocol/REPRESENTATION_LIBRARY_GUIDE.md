# Source-backed representation component library

## Research status and boundaries

This library provides reusable descriptions of representations, transformations,
computational components and documented compositions. The development release
adapts the supervised InstructCell, ChatNT, MUPAD and X-Cell pilot. The historical
55-record/585-route annotations, eligibility and public taxonomy remain unchanged.
The library does not implement neural-network computations or assert a final
taxonomy. Corpus-wide reconstruction and clustering are subsequent work.

Source review uses the complete available selected-section packets. Their recovered
Markdown IDs are scoped to document hashes. Native PDF item IDs, pages and geometry
are unavailable in these packets; never fabricate them. Unknown formulas,
supplements and source gaps remain review questions.

## Standard mechanisms

Reuse `scripts/docling_graph_templates/representation_library.py`, the existing
symbolic-trajectory contract and source auditors. Pydantic generates the JSON
Schema via its documented `model_json_schema()` API:
https://docs.pydantic.dev/latest/concepts/json_schema/ .
Docling Graph already accepts domain-specific Pydantic templates; retain its
existing extraction integration when extending reconstruction experiments:
https://docling-project.github.io/docling-graph/ .
The present release compiles completed source annotations without another LLM
extraction call. The domain library supplies scientific definitions and governance.

Static Pages use the existing configure/upload/deploy Actions workflow, as described
at https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages .
The atlas remains at the repository site's root; the catalog is `/component-library/`.

## Shared annotation contract

Each source-backed assembly pins the contract version, library release and hash,
record, input packet and original artifact hashes. Representations, operations and
receipts form a graph; task/phase contexts refer to graph IDs. A receiving operand
identifies the actual data node and its port role. Concrete model/module names stay
on instances; library definitions describe reusable mechanisms.

Representation descriptions retain information content, contextual role, symbolic
shape, axis semantics, evidence and uncertainty. Concrete architecture widths,
codebook sizes and layer counts remain in unchanged quotations. Axis equality is
asserted only when established by evidence. Matching dimensions establish neither
node identity nor shared parameters.

Operation definitions describe their supported input/output roles. Preserve the
paper's port names on instances. A normalized role needs source-backed matching;
the pilot leaves unreviewed normalized-role assignments empty. A generic projection
type can have a documented linear or MLP specialization. Preserve that instance's
operation description and evidence.

Only documented internal operations are expanded. A composite module can retain
unknown internals. Composition examples list actual steps and operand bindings;
reusing a motif does not assert that all instances share its implementation.

## Reconstruction-agent procedure

1. Read this guide, the pinned library release and the complete supplied evidence.
2. Establish model variant, task, one lifecycle phase and named receiving component.
3. Reconstruct each source-to-receiver use, preserving branches, joint operands,
   successive generators, evolving states and question-dependent transformations.
4. Search library definitions and aliases. Check mechanism, axis meanings and port
   semantics. Record `reuse` or `specialization` with an explicit rationale.
5. When a match is unsupported, keep the complete local instance and submit an
   extension proposal. Preserve missing transformations as unresolved links.
6. Preserve learned parameters, computed features, distribution parameters and
   sampled values as distinct objects. Distinguish actual model inputs, training
   supervision, auxiliary processing, ablations, baselines and generated outputs.
7. Cite unchanged quotations in their own source sections for every scientific
   assertion. VLM descriptions can locate evidence; corroboration is required for
   a final mechanism claim. Keep source conflict and uncertainty visible.
8. Reuse a node across contexts only with documented identity. Use an explicit
   evidence-backed identity link for shared values, shared weights or repeated
   computation. Preserve step-specific state updates and phase availability.
9. Return `AssemblyDocument`, extension proposals and the public decision record.
   Validate the schema, graph references and source quotations before delivery.

Do not apply size-dependent caps, shortening, source ratios, splitting or exclusions.
If a provider limit prevents processing, preserve the full input and request the
author's approval. Do not infer absence from incomplete evidence. Never force a
mechanism into the nearest available block.

## Library-steward procedure and authority

One steward owns the candidate seed. Reconstruction agents consume pinned releases
and submit proposals; they do not edit shared definitions concurrently.

For each proposal the steward records the compared IDs, source instances and one
decision: `reuse`, `alias`, `compatible_enrichment`, `new_block`, or `unresolved`.
Search by existing definition, input/output semantics, composition and aliases.
Similarity of words or tensor shapes alone cannot establish equivalence.

The steward may autonomously add source-backed examples, genuine aliases, compatible
descriptive enrichment and independently justified new blocks. Generalization must
be justified by the mechanism; one documented instance can support a rare block.
Retain precise specialization in instance metadata. A source label receives a
global mapping only when its applications have compatible meanings. Context-bound
meanings require explicit instance-level bindings in future extraction.

Changes to existing scientific meaning, port contracts, composition, mappings or
merges require author approval and an affected-instance review. Never silently widen
a definition to absorb a conflict. Deprecation/merging retains old IDs and lineage.
Run `review_representation_library_change.py` before approving a release.

Every published release is frozen in a version directory and pinned by hashes.
Existing assemblies retain their release. Reannotation creates a new artifact and
an explicit migration ledger. Keep visible prompts, responses, decisions, errors,
source hashes and validation; exclude hidden chain-of-thought.

## Build and checks

Run from the canonical repository root. Use any Python environment with Pydantic v2:

```bash
python scripts/build_representation_library.py
python scripts/build_representation_library.py --check
python -m unittest discover -s tests -p test_representation_library.py
```

`--capture-inputs` is the explicit initial snapshot operation. It verifies packet
hashes and every own-section quotation against local source packets, preserving the
complete original trajectories. Ordinary builds use the frozen input/evidence
snapshot and need no model endpoint. Snapshots contain full evidence quotations and
capture-time hashes/offsets; original PDF/Docling profiles remain in their existing
storage. A successful snapshot build does not revalidate unavailable originals.

Before release inspect: schema and reference integrity; source restoration equality;
phase boundaries; asymmetric attention ports; distribution/sample distinction;
shared resources; evolving states; and visible unresolved links. Review ChatNT,
MUPAD, X-Cell and InstructCell explicitly. Test desktop/mobile search, filters,
examples, source figures, assembly context selection and the extension queue.

## Extension sequence

Stabilize the four-paper descriptions first. Test further known hard cases against
the frozen definitions and log counterexamples. Extend to remaining selected packets
only after structural defects are addressed. Report each source-review disposition.
Catalog completeness and scientific entailment require continued source review;
passing mechanical checks does not settle them.
