# Input-Representation Taxonomy Protocol

## Purpose

This post-eligibility stage describes how biological and textual source objects
are transformed into model-visible inputs in the accepted corpus of generative
multimodal biological foundation models. It does not change eligibility
decisions or the PRISMA screening funnel.

The classification unit is:

`study -> model -> lifecycle phase -> task/input configuration -> input route`

An input route begins with exactly one source object and follows its ordered
transformations to the representation received by the generative component.
Multimodal configurations therefore contain multiple routes rather than one
catch-all `hybrid` route.

## Source corpus and denominators

- Canonical evidence: `data/docling_include_vlm_52_2026-07-10_nolimits/`
- Final screening evidence: `data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10/`
- Taxonomy artifacts: `data/input_representation_taxonomy_2026-07-11/`
- Screening denominator: 52 accepted records.
- Primary study denominator: 51 after collapsing one exact Cell2Text PDF duplicate.
- Sensitivity denominator: 50 if the possible OmniNA preprint/journal pair is linked.

All 52 source record identifiers remain available as version-level provenance.
Study-, model-, configuration-, and route-level counts are reported separately.

## Extraction contracts

Four versioned Pydantic contracts are used:

1. `InputRouteDiscoveryDocument` performs open extraction using verbatim source
   objects, transformation chains, model-visible forms, fusion descriptions,
   lifecycle phases, configurations, and evidence. It does not expose the
   proposed carrier taxonomy to the extractor.
2. `TaxonomyCodedDocument` is the Docling Graph dense coverage contract.
3. `FixedCandidateClassificationDocument` classifies the same immutable open
   discovery candidates in every direct replicate. Every discovery `route_ref`
   must be accepted or explicitly excluded; combined candidates can be split
   into several source-specific routes, and discovery duplicates can be merged.
4. `FinalAdjudicatedTaxonomyDocument` reconciles the three blinded fixed-candidate
   replicates and gives every dense candidate an explicit disposition.

Docling Graph direct mode receives the complete canonical Docling Markdown,
including tables, captions, appendices, and native VLM picture descriptions.
No API-level `max_tokens`, context limit, or source-text truncation is supplied.
Dense mode uses the standard 768-token structural chunks, 1,536-token skeleton
batches, scoped fill, and standard deduplication as coverage work units; these
budgets partition rather than delete source content.

All LLM roles use `gpt-5.4-mini` through the local OpenAI-compatible Codex
wrapper at temperature 0. Discovery, taxonomy synthesis, fixed-candidate
classification, dense coverage, and adjudication are separate prompt roles of
the same model. This is repeated
computational annotation with LLM adjudication, not human-validated ground
truth.

## Procedure

1. Build an immutable record/study registry and preserve duplicate/version links.
2. Run open direct extraction over all 52 complete VLM-enriched profiles.
3. Produce three independent taxonomy proposals from the grounded route inventory.
4. Reconcile the proposals against route evidence and freeze taxonomy v1.
5. Freeze the 583 open-discovery candidates and run three independent
   full-corpus direct classifications over those identical candidate units.
6. Run one full-corpus dense classification as a coverage audit.
7. Apply objective dense eligibility gates. Candidates that are not simultaneously
   marked as input candidates, grounded, taxonomy-consistent, and non-picture-only
   receive logged deterministic exclusions. Send every remaining potentially valid
   dense route to blinded LLM adjudication.
8. Blindly adjudicate the anonymized candidate sets against each complete canonical document.
9. Assign stable study, model, configuration, and route identifiers.
10. Export accepted routes, all non-input candidates, evidence, uncertainties,
   agreement metrics, taxonomy tables, and manuscript-ready methods.

If the prompt, Pydantic contract, model, or normalization policy changes, the
configuration receives a new version and all 52 records are rerun. Outputs from
different schema versions are never mixed into one agreement estimate.

## Evidence policy

Every accepted route must have:

- one contiguous verbatim supporting quote matched in canonical Markdown or in
  a cited native Docling item;
- provenance inherited from its cited discovery/dense candidate, with source
  pages and native Docling item references;
- a carrier family/subtype combination permitted by the frozen taxonomy;
- explicit lifecycle phase, task/configuration, text role, and input status.

VLM picture descriptions are locator or supporting evidence. A figure-only
claim cannot establish a final accepted route unless a caption, body passage,
table, or architecture description corroborates it. Training-only targets,
generated outputs, baseline inputs, and ablation inputs remain visible in the
candidate ledger but are excluded from accepted-input frequency tables.

## Reproducibility and logs

Each run stores:

- exact Pydantic JSON Schema;
- exact LLM prompts and responses;
- model, endpoint, temperature, timeout, and no-limit settings;
- selected record list and source hashes;
- Docling Graph nodes, edges, chunks, provenance, debug trace, and metadata for
  Graph discovery/dense runs, plus fixed candidate references for direct runs;
- attempts, failures, retries, timings, and final status.

Logs contain model outputs and evidence rationales, not hidden chain-of-thought.
Failed runs remain clearly labeled and are not reused as successful artifacts.
When an LLM quote is not verbatim, a logged deterministic repair may replace it
with a cited candidate support field or cited native Docling item. The raw model
response is retained unchanged, and the repaired quote must pass the same
candidate-link and non-picture provenance checks.
A second logged normalization mirrors an explicitly returned dense disposition
link onto the named accepted route, or an existing route citation back into the
dense disposition, when the LLM omitted the reciprocal reference. It does not
infer a new route, decision, or linkage.
Immutable `dense::` and discovery candidate namespaces are also used to move a
reference into the correct schema field when the LLM placed it in the reciprocal
field; the reference itself and its route association are unchanged.

## Validation criteria

The final configuration passes only when:

- every direct replicate contains 52 successful records;
- every accepted route has verified provenance;
- every carrier family/subtype pair is valid;
- minimum pairwise route-detection Jaccard is at least 0.80;
- carrier-family exact agreement is at least 0.90;
- nominal Krippendorff alpha for carrier family is at least 0.80;
- every dense candidate has either an objective gate exclusion or an explicit
  LLM adjudication disposition;
- duplicate/version, figure-only, lifecycle-conflict, non-input, and unmatched
  cases remain visible in the audit artifacts.

Failure of any threshold requires a documented schema/prompt revision and a
complete rerun rather than selective replacement of records.

## Final execution note

The accepted final set uses four replay-validated adjudication artifacts for
`rec_000090`, `rec_001187`, `rec_003517`, and `rec_000148`. Each is derived from
an already logged full fourth-annotator response, not a hand-authored decision.
`adjudication_resolution_manifest.csv` identifies the selected artifact and hash;
each replay directory records the source LLM log, response line, request index,
normalizations, and validation result.
