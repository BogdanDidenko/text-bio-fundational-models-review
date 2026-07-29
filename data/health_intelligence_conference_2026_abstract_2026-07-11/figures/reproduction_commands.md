# Figure reproduction

## Canonical figures

The selected figures are deterministic and generated directly from the final route annotations and screening summaries:

```bash
PY=/Users/bogdan.didenko/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PY scripts/build_health_intelligence_conference_abstract.py
```

Inputs:

- `data/input_representation_taxonomy_2026-07-11/route_annotations.jsonl`
- `data/input_representation_taxonomy_2026-07-11/agreement_metrics.json`
- `data/input_representation_taxonomy_2026-07-11/registry_summary.json`
- screening summaries asserted in `scripts/build_health_intelligence_conference_abstract.py`

The builder writes the exact content contract to `analysis/figure_fact_contract.json`, validates required text/counts in `analysis/figure_validation.json`, and produces canonical SVG plus PNG in `figures/deterministic/`.

## Exploratory generators

PaperBanana and AutoFigure were evaluated against the same fact contract through the local OpenAI-compatible wrapper over `codex exec` with `gpt-5.4-mini`.

```bash
git clone https://github.com/llmsresearch/paperbanana /tmp/paperbanana-eval
git -C /tmp/paperbanana-eval checkout 8b4745ad302439eded5884c9ec77412d99931047

git clone https://github.com/ResearAI/AutoFigure /tmp/autofigure-eval
git -C /tmp/autofigure-eval checkout 454ee868b9e253d2dbf990b42c4e964b93e498fd
```

PaperBanana produced a DiagramIR/Graphviz structural candidate retained in `figures/candidates/paperbanana/`. AutoFigure generated an initial SVG and one logged critique-driven refinement retained in `figures/candidates/autofigure/`; `generation_report.json` records the endpoint, model, dimensions, iterations, and internal scores. These candidates are comparison evidence, not production dependencies.

The selection and iteration rationale is in `figures/figure_comparison.md`.

