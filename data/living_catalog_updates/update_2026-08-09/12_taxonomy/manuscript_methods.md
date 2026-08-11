# Manuscript-Ready Methods: Post-Eligibility Input-Representation Taxonomy

This incremental post-eligibility cohort comprised 2 newly accepted
screening records represented by complete VLM-enriched Docling profiles.
The carrier-family hierarchy and leaf definitions were held fixed at taxonomy v1;
the update did not re-synthesize or silently revise the baseline taxonomy.
Exact source-document duplicates inherited the prior study identifier and remained
explicit in the registry.

Open route discovery used Docling Graph direct extraction over each complete new
document, including body text, tables, captions, appendices, and native VLM picture
descriptions. Its 17 candidates formed the fixed inventory
for this update.

Each of three repeated classifications received the same fixed per-paper candidate
inventory and complete canonical Markdown. Separate routes represented source
objects within each model, lifecycle phase, and task/input configuration. Runs used
gpt-5.4-mini, temperature 0, strict JSON schemas, no configured output-token cap,
no configured context cap, and the local OpenAI-compatible Codex wrapper. A separate
Docling Graph dense scoped-fill pass audited coverage. A blinded fourth invocation
reconciled the three repeated classifications and explicitly dispositioned every
dense candidate.

Final routes required a verbatim match in canonical Markdown or a cited native
Docling item, Docling item references,
non-figure-only provenance, a valid frozen family/subtype pair, and an actual-input
or paired-alignment status. VLM descriptions could locate evidence but could not
independently establish a route. Targets, outputs, baselines, and ablations were
explicitly excluded. Non-verbatim quotations were deterministically rebound only
to cited candidate support or native Docling items. Reciprocal candidate links and
immutable candidate namespaces were normalized without changing model decisions.
Four already logged full-adjudication responses were replayed through the final
validator after these normalization rules were frozen; the source response line,
request index, and log hash are retained. This is repeated computational annotation with LLM
adjudication, not human-validated ground truth.

Agreement was calculated on fixed discovery candidate references. Route detection
used pairwise Jaccard; carrier agreement used exact family-set agreement and nominal
Krippendorff alpha. All prompts, schemas, responses, retries, hashes, provenance,
and errors were retained in the versioned output directory.

The final corpus contained 16 accepted input routes across
3 models and
14 configurations.
The minimum pairwise route-detection Jaccard was 1.000;
carrier-family exact agreement was 1.000,
and nominal Krippendorff alpha was 1.000.
All 202 dense candidates were dispositioned, with
0 accepted as dense-only evidence and no unresolved dense candidates.
0 output-derived textual objects were retained only where the paper explicitly
reused them as inputs to a downstream verifier or corrector stage.
