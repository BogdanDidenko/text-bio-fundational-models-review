# Canonical Docling Profiles

- Profiles: 2
- Source document conversions: 2 successful
- Extracted and described images: 29/29
- Scientific figures: 29
- Non-scientific images: 0
- Picture descriptions enabled: True
- VLM model: gpt-5.5
- Picture area threshold: 0.0
- VLM output-token cap: None
- RAG chunks: intentionally absent; HybridChunker was not run.

## Profile contents

Every profile has a full native `DoclingDocument` JSON, markdown export, extracted picture images, and a figure manifest. VLM-enabled runs store picture descriptions natively in those profiles. Each profile is produced by a fresh full-text conversion rather than by patching an older corpus.

## Artifacts

- `canonical_docling_profile_manifest.csv`
- `canonical_docling_profile_manifest.json`
- `docling_smoke_manifest.json`
