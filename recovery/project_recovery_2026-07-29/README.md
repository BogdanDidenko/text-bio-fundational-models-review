# Project Recovery Audit

Recovery date: 2026-07-29

Cause: migration to a new workstation left the Git repository available, but several large untracked research corpora and generated artifacts were absent.

This audit distinguishes four states:

- `exact`: byte-identical Git objects or files recovered from recorded hashes/tool outputs;
- `reconstructed`: deterministically rebuilt from unchanged inputs and historical commands;
- `partial`: scientifically useful content is present, but some native payloads are absent;
- `not_recovered`: no trustworthy source was found, so no substitute was fabricated.

## Recovery Summary

| Artifact group | Status | Recovery evidence |
|---|---|---|
| Git history and remote branches | exact | all advertised remote branches fetched; a full Git bundle is produced separately |
| CRABS 2026 abstract package | exact/reconstructed | committed in `7d256bc8`; DOCX and PDF visually verified during recovery |
| July screening archive | exact | 100 paths restored from `origin/codex/july-2026-screening-artifacts`; Git blob hashes verified |
| Taxonomy, final screening, PRISMA, and protocol artifacts | exact | retained in Git history from `origin/codex/fulltext-section-screening-audit` |
| Canonical VLM Docling Markdown | exact | 52/52 documents extracted from committed complete-document Graph prompts; character counts and SHA-256 hashes match historical run summaries |
| Canonical VLM figure files | partial | 59/506 source PNGs restored byte-for-byte from atlas copies and verified against recorded hashes |
| Accepted-paper source PDFs | exact/valid recovery | 52/52 open as PDFs; 28 exact historical hashes, 13 current versions from historical URLs, 9 previously unhashed valid PDFs, 2 valid alternate-repository copies |
| Determinism experiment | partial | sample, summary, report, and tGPT analysis recovered; original three run directories and role logs are absent |
| Full-text downloader | exact | uncommitted historical patches replayed in order; Python compilation verified |
| UNESCO document builder | exact/reconstructed | script recovered from historical patches; four DOCX/PDF outputs regenerated |
| Atlas crop finalizer | exact | recovered from historical patch and Python compilation verified |
| API credentials | local only | restored to ignored `api_keys.json`, mode `0600`; never committed or copied to the public backup |

## Canonical Locations

- VLM Markdown and recovered figures: `data/docling_include_vlm_52_2026-07-10_nolimits/`
- Recovered accepted-paper PDFs: `data/source_pdf_recovery_52_2026-07-29/canonical_pdfs/`
- PDF provenance: `data/source_pdf_recovery_52_2026-07-29/final_pdf_recovery_manifest.csv`
- Determinism recovery: `data/determinism_codex_2026-07-01/`
- Conference package: `data/health_intelligence_conference_2026_abstract_2026-07-11_v2/`
- Detailed artifact inventory: `artifact_status.csv`

Large binary PDFs are intentionally excluded from Git and included in a separate checksummed archive. Git retains their manifests and retrieval logs.

