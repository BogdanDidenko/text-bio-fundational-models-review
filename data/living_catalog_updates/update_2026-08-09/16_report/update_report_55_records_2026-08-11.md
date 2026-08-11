# Living Review Cumulative Update Through 2026-08-11

The frozen living-review pipeline added three eligible records to the
52-record baseline:

1. *OCellus: A Language-Model Framework for Single-Cell, Spatial, and
   Perturbation Biology with Natural-Language Reasoning*;
2. *scMIR: a vision-language foundation model for single-cell light microscopy
   image representation*;
3. *XunZi, an AI biologist, reveals disease-modifying targets*
   (`10.1038/s41551-026-01769-6`).

XunZi was recovered through a documented supplemental recall correction after
the pre-screen lexical validator was amended to recognize the explicit
`AI biologist` terminology. It then passed the frozen role-separated abstract
screening and full-text-section screening pipelines. The primary 41-page PDF,
no-VLM screening profile, Graph-selected sections, complete VLM profile, all
role logs, and eligibility decision are retained in sibling versioned stages.

## Cumulative corpus

- records: 55;
- studies: 54;
- models: 117;
- task/input configurations: 400;
- grounded input routes: 519;
- models with a validated source-figure crop: 85;
- models with an explicit no-suitable-figure disposition: 32.

## Aggregate reproducibility

The one-record XunZi sensitivity Jaccard is not used as a standalone acceptance
gate. The prespecified thresholds apply to the cumulative annotation corpus.
Recalculation from all 55 records in each of the three frozen direct runs gave:

| Pair | Intersection | Union | Jaccard |
|---|---:|---:|---:|
| r1-r2 | 484 | 504 | 0.9603 |
| r1-r3 | 482 | 510 | 0.9451 |
| r2-r3 | 492 | 508 | 0.9685 |

Carrier-family exact agreement was `0.9287`, and nominal Krippendorff alpha was
`0.8812`. All remain above the frozen acceptance thresholds (`0.80`, `0.90`,
and `0.80`, respectively). No prompt, schema, taxonomy definition, or
historical annotation was changed.

The immutable cumulative snapshot is
`../14_snapshot_55_records_2026-08-11/`; the corresponding browser-validated
atlas is `../15_atlas_55_records_2026-08-11/`.
