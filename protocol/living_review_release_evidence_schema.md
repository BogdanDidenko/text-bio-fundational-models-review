# Living Review Release Evidence

GitHub Pages deployment creates an ephemeral
`docs/input-representation-atlas/data/deployment.json` before upload. It binds
the deployed payload to `GITHUB_SHA`, the living-state hash, `atlas.json` hash,
and a SHA-256 manifest of every deployed file. The file is not part of its own
tree hash.

Remote verification requires:

```bash
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit COMMIT_SHA --check-assets
```

This checks semantic atlas counts, exact `atlas.json` bytes, commit identity,
tree identity, and every remote asset hash.

After the workflow and visual checks succeed, create the immutable operator
record outside stage-owned run artifacts:

```bash
python3 scripts/run_living_review_pipeline.py verify-live \
  --run-id update_YYYY-MM-DD \
  --expected-commit COMMIT_SHA --check-assets \
  --record-completion --workflow-run-id GITHUB_RUN_ID \
  --operator "operator name" \
  --screenshot /absolute/path/desktop.png \
  --screenshot /absolute/path/mobile.png
```

The result is stored at
`data/living_catalog/releases/<run_id>/completion_record.json` and includes the
run manifest, state, atlas, browser QA, screenshots, workflow, commit, complete
remote verification, and next search date. Completion recording requires the
expected commit, full remote asset verification, and at least two screenshots
covering desktop and mobile QA. Repeating the same command is idempotent; changing
any recorded evidence is rejected.

The completion record is created after deployment and therefore belongs in a
small follow-up provenance commit. That path does not trigger the Pages workflow.

Failures are append-only incident records:

```bash
python3 scripts/run_living_review_pipeline.py incident \
  --run-id update_YYYY-MM-DD --phase deployment \
  --summary "Exact failure and recovery decision" \
  --operator "operator name" --commit COMMIT_SHA \
  --workflow-run-id GITHUB_RUN_ID
```
