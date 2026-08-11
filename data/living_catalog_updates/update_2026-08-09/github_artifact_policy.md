# GitHub Artifact Policy

The complete immutable local update tree contains 3,068 files and
2,267,732,779 bytes. `artifact_manifest.csv` records the relative path, size,
mtime, and SHA-256 of every local file; `artifact_manifest_summary.json` records
the manifest hash.

GitHub stores the reproducible search and deduplication evidence, enriched
metadata, both screening rounds, role-separated prompts and responses,
eligibility decisions, canonical profile manifests, section-selection
provenance, all taxonomy prompts/responses/configurations/summaries,
adjudication logs, final route/evidence ledgers, crop decisions, cumulative
snapshot, browser-ready atlas, QA report, and protocol/code changes.

The Git commit intentionally excludes article PDF/HTML/XML payloads, canonical
`.docling.json` files, repeated Graph `docling/document.json` and `chunks.json`
copies, rendered Graph HTML, the complete extracted source-figure sets, and
transient Semantic Scholar pagination state containing opaque continuation
tokens. The completed Semantic Scholar export and search summary remain
included. These excluded files are large, byte-redundant, or session-specific
execution payloads. Their hashes remain in the complete manifest, and the
canonical local tree remains the execution archive. Validated crops and the
atlas figure assets are included in GitHub.

Invalidated and failed attempts remain visible through their logs, schemas,
responses, summaries, and manifests. Excluding a large payload does not remove
the associated model response, retry, validation error, or final disposition.
