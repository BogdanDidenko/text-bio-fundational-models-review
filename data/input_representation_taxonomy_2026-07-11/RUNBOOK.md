# Reproduction Runbook

Run from `/Users/bogdan.didenko/lpnu/review` using `.venv-docling`.

## Registry and local endpoint

```bash
.venv-docling/bin/python scripts/docling/build_input_taxonomy_registry.py

.venv-docling/bin/python scripts/docling/codex_openai_compat_server.py \
  --host 127.0.0.1 --port 8765 --model gpt-5.4-mini --timeout 1800
```

## Open discovery

Run eight shards with `--stage discovery`, `--replicate-id open_r1`,
`--extraction-contract direct`, `--shard-count 8`, and shard indices 0-7.
Write each shard to:

`data/input_representation_taxonomy_2026-07-11/runs/discovery_open_r1/shard_XX/`

No `--max-tokens` or `--context-limit` argument is supplied.

## Taxonomy synthesis

Run three independent proposals:

```bash
.venv-docling/bin/python scripts/docling/synthesize_input_representation_taxonomy.py \
  --mode propose \
  --discovery-root data/input_representation_taxonomy_2026-07-11/runs/discovery_open_r1 \
  --replicate-id r1
```

Repeat with `r2` and `r3`, then run `--mode adjudicate` with the three generated
`taxonomy.json` paths. Render the result with:

```bash
.venv-docling/bin/python scripts/docling/render_input_taxonomy_codebook.py \
  --taxonomy data/input_representation_taxonomy_2026-07-11/taxonomy_synthesis/adjudicated_v1/taxonomy.json
```

## Repeated classification

The three direct replicates classify the immutable open-discovery inventory.
They do not ask the model to enumerate routes again:

```bash
.venv-docling/bin/python scripts/docling/classify_fixed_input_taxonomy_candidates.py \
  --replicate-id r1 --shard-count 4 --shard-index 0 \
  --output-dir data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1/shard_00
```

Repeat for shard indices 0-3 and replicate IDs r1-r3. The dense coverage pass
uses standard Docling Graph scoped fill:

| Run | Runner | Contract | Replicate |
|---|---|---|---|
| `classification_fixed_r1` | fixed-candidate | direct | r1 |
| `classification_fixed_r2` | fixed-candidate | direct | r2 |
| `classification_fixed_r3` | fixed-candidate | direct | r3 |
| `classification_dense_coverage` | Docling Graph coded | dense | coverage |

All runs use temperature 0 and no configured API-level context/output cap.
Graph runs additionally retain detailed provenance, debug artifacts, standard
dense deduplication, and scoped dense fill. Fixed runs retain exact candidate
references, prompts, responses, exclusions, retries, and source hashes.

## Adjudication and analysis

Run `scripts/docling/adjudicate_input_taxonomy.py` in eight shards with the
three direct roots, dense root, and frozen `taxonomy_tree.json`. Then run:

```bash
.venv-docling/bin/python scripts/docling/analyze_input_taxonomy_runs.py \
  --direct-run data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r1 \
  --direct-run data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r2 \
  --direct-run data/input_representation_taxonomy_2026-07-11/runs/classification_fixed_r3 \
  --dense-run data/input_representation_taxonomy_2026-07-11/runs/classification_dense_coverage \
  --adjudication data/input_representation_taxonomy_2026-07-11/adjudication
```

The analyzer exits nonzero when any prespecified acceptance threshold fails.
Its outputs remain valid audit evidence but cannot be described as a passed
taxonomy configuration until a versioned full-corpus rerun meets all thresholds.

When an already logged LLM response needs only the protocol-defined deterministic
normalizations, replay it without a new model invocation using
`scripts/docling/replay_input_taxonomy_adjudication.py`. The replay artifact records
the source JSONL path, source line and request index, and SHA-256 before validation.
Use `--request-index N` when a later correction regressed and an earlier logged
response is the schema-valid, policy-valid artifact.
