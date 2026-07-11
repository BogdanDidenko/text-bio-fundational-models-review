# GitHub Artifact Policy

The complete immutable local artifact tree contains 4,216 files and about 6.54 GB.
`artifact_manifest.csv` hashes every file in that tree. GitHub stores the
analysis-ready outputs, codebook, protocol documentation, complete adjudication
logs, all three fixed-candidate runs, taxonomy-synthesis logs, and the discovery
and dense runs' prompts/responses, configurations, summaries, and provenance.

The Git commit intentionally excludes repeated copies of canonical Docling
documents, rendered graph HTML, and failed-pilot document payloads. Those files
are byte-redundant with the read-only canonical corpus or are large intermediate
Graph representations. Their paths, sizes, timestamps, and SHA-256 hashes remain
in `artifact_manifest.csv`; the full local tree remains the canonical execution
archive.

This policy does not remove model responses, validation errors, retries, replay
manifests, or final evidence decisions from the GitHub audit subset.
