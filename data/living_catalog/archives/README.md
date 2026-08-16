# Living Review Artifact Archive Receipts

These JSON receipts bind a complete source artifact manifest to a verified
`.tar.zst` archive. The archive payloads are intentionally stored outside Git.
Use `scripts/archive_living_review_artifacts.py verify` before relying on a
receipt and `restore` only into an empty directory.

The two archives created on 2026-08-16 are marked `local_secondary`: they are
verified recoverable copies outside the repository, but they remain on the same
physical system disk and therefore do not protect against device loss. Copy
them to independent storage and verify the copied path. Future method-locked
runs cannot be published until a matching receipt is created with
`storage_class: independent_backup`.
