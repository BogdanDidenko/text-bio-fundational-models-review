# Supplemental Recall Record Contract

A record discovered after the ordinary search capture but before publication
must enter the same run before cumulative deduplication:

```bash
python3 scripts/run_living_review_pipeline.py register-supplemental \
  --run-id update_YYYY-MM-DD \
  --record-file /absolute/path/record.json \
  --reason "Documented recall correction" \
  --source-url "https://publisher.example/article" \
  --resolver "operator name"
```

The command writes
`02_records/supplemental_recall_records.json`, invalidates `prepare-records`
and every downstream stage, and prints the exact resume command. The declared
record is merged with the within-update cohort and then passes ordinary
cumulative DOI/PMID/arXiv/title and Crossref checks. It receives no screening,
retrieval, eligibility, taxonomy, or publication bypass.

Each declaration contains the complete source record, reason, source URL,
resolver, timestamp, and the hash of the source artifact. A title plus DOI,
PMID, arXiv ID, or source URL is required.

Published run inputs are immutable. A record discovered after publication uses
the explicit reconciliation ledger; it must still produce the complete
downstream evidence chain before reconciliation.
