# GitHub Artifact Policy

The immutable local full-cohort archive contains 7,486 files and approximately
7.02 GB. `artifact_manifest.csv` records the relative path, byte
size, modification time, and SHA-256 digest of every file; its own digest and
category counts are frozen in `artifact_manifest_summary.json`.

The Git commit retains:

- the complete 55-record immutable snapshot and final route/evidence ledgers;
- taxonomy codebook, agreement, uncertainty, failure-mode, registry, and
  analysis tables;
- direct, dense, and adjudication prompts/responses, schemas, run summaries,
  retry evidence, and crop-role logs;
- the canonical Docling profile manifest, exact commands, run configuration,
  readiness evidence, and complete artifact manifest;
- the deployable atlas under `docs/input-representation-atlas/`.

Git intentionally excludes repeated native Docling document payloads inside
Graph record directories, regenerated baseline profile binaries, crop contact
sheets, staged/failed atlas copies, and failed payload-heavy pilot runs. These
objects remain in the immutable local archive and are addressable by their
manifest paths and hashes. The exclusions do not remove final decisions,
accepted evidence, LLM responses, validation errors, retries, or the source
profile hash contract.
