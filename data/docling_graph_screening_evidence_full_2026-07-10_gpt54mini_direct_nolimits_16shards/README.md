# Public Docling Graph Evidence Audit

This run completed detailed-provenance Docling Graph extraction for 235
full-text records using `gpt-5.4-mini`, `extraction_contract=direct`, and 16
parallel shards. See `parallel_run_summary.json` for shard-level completion
status and `logs/` for each shard's execution log.

For public audit, this repository tracks every per-record
`screening_evidence_summary.json`. Each summary contains the structured Graph
extraction, evidence quotes, provenance-grounded chunk information, heading
trails, and derived complete section boundaries used to build the later
screening input.

The complete local Docling Graph artifact, including raw Docling documents and
intermediate rendered documents, is approximately 8 GB and is intentionally not
committed. Those large source artifacts can be regenerated from the documented
Docling corpus and the versioned runner/template code. The tracked summaries
are the evidence-selection audit needed to inspect why a particular section was
or was not chosen.

The downstream clean input and final screening run are documented in
`protocol/full_text_section_screening_2026-07-10.md`.
