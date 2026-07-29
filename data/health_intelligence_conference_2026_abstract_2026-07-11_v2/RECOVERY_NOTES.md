# Recovery notes

Recovered on 29 July 2026 after the original untracked conference directory
was deleted.

## Recovery sources

- Codex session log:
  `/Users/bogdan.didenko/.codex/sessions/2026/07/11/rollout-2026-07-11T15-30-08-019f5128-1090-7600-99b1-d3ad6984b522.jsonl`
- Git audit branch:
  `origin/codex/fulltext-section-screening-audit` at `5ca5f152`
- Codex screening bundle:
  `origin/codex/july-2026-screening-artifacts`
- Original conference template:
  `/Users/bogdan.didenko/Downloads/Smith-Doe-Bloggs (2).docx`

## Recovered exactly from logs

- Final `manuscript_content.json`, including title, authorship, affiliation,
  correspondence, received date, Motivation, Results, Methods, Discussion,
  Funding, Availability, caption, and references.
- Build, validation, vector-PDF finalization, motivation extraction, and
  motivation synthesis scripts.
- The complete corpus-level motivation synthesis JSON and Markdown.
- README and comparison/source notes that were stored through patch calls.
- The template binary. Its SHA-256 is
  `093e3f6a4e79b717d836032b6a994b121523cf801658b2d4074333c4e851b946`.

## Regenerated deterministically

- Submission DOCX and one-page A4 PDF.
- Compact taxonomy SVG and PNG.
- Figure fact contract, manuscript fact table, source manifest, and validation
  reports.
- Color and grayscale page renders.
- The earlier v1 baseline package.

The recovered taxonomy SVG has SHA-256
`8ec5575297f73aae221a9087940e913249c7a1143ec21b7cdd0fa48212e8cebc`,
identical to the hash recorded before deletion. The regenerated DOCX and PDF
are not byte-identical because OOXML/PDF build metadata and the renderer run
changed. The original final hashes recorded in the session were:

- DOCX: `742b6fa9971dffa6de906a67f9ab5ecc030bde3b827a70964fcb27907d93ae4d`
- PDF: `3fd0190de596789b7ab03ef658b8e363b611aecb7f812717818e623d1a80c8a5`

The recovered files pass the same scientific, layout, provenance,
template-fidelity, redundancy, and vector-figure validation checks.

## Unrecoverable raw intermediates

The original 208-row motivation evidence ledger and its per-record extraction
responses were untracked files and were not present in Trash, Spotlight,
accessible APFS snapshots, Git objects, or caches. Their exact corpus-level
synthesis and run counts were recoverable from the Codex log, but the full raw
ledger was not.
