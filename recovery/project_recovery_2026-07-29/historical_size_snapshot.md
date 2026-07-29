# Historical Size Snapshot

The last available pre-migration inspection recorded approximately:

| Path/group | Historical size |
|---|---:|
| Repository worktree including `.git` | 48 GB |
| `data/` | 31 GB |
| `.git/` before later garbage collection | 15 GB |
| `.venv-docling/` | 1.4 GB |
| Canonical VLM Docling corpus | 1.9 GB |
| Full-text downloads | 1.4 GB |
| No-VLM Docling corpus | 5.4 GB |
| Full Graph/native working copies | 8.0 GB |
| Taxonomy working tree | 6.1 GB |

These totals included multiple copies of PDFs, rendered page images, native Docling documents, complete Markdown embedded in Graph requests, temporary model outputs, and Python environments. They do not represent 48 GB of unique irreplaceable evidence.

The recovery therefore prioritizes:

1. versioned scientific outputs and logs;
2. canonical text and provenance;
3. one verified PDF per accepted record;
4. exact assets with recorded hashes;
5. manifests sufficient to identify what is absent or reproducible.

