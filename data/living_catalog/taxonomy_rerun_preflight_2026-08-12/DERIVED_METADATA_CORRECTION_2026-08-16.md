# Derived Metadata Correction, 2026-08-16

This correction re-aggregates the completed 55-record frozen-taxonomy rerun. It
does not invoke an LLM, change screening eligibility, alter taxonomy v1, or
change any accepted route or evidence row.

## Cause

`build_input_taxonomy_registry.py` treated the presence of the same `record_id`
in the prior registry as evidence of an exact duplicate. In the full-cohort
rerun, this marked 38 records as duplicates and left only 17 records canonical.
The analysis generator then computed the OmniNA-linked sensitivity denominator
from those 17 flags and reused baseline-development Methods prose for a
frozen-taxonomy rerun.

## Correction

- Registry rows: 55 in both versions.
- Primary studies: 54 in both versions.
- Canonical records: 17 -> 54.
- Exact-duplicate flags: 38 -> 2.
- Exact duplicate groups: 37 malformed groups -> 1 real Cell2Text group.
- OmniNA-linked sensitivity studies: 17 -> 53.
- Models/configurations/routes: unchanged at 109/468/586.
- Analysis mode: explicitly `full_cohort_frozen_taxonomy`.
- Methods counts and wording are now generated from current run artifacts.

The old and corrected route/evidence files are byte-identical:

- `route_annotations.jsonl`: `2de2247daab48875268a97fb182f38861a504b815ef3c834db71873d37422bb9`
- `evidence_ledger.jsonl`: `42f35a45119af42bb8cb958124249ea04b5a263e9619eb4f62f3913be2bf40df`

Changed derived artifacts:

- old registry: `c3949d30d580705f879921d24597277a1b279ac0c06380e6e6418fcb5e56fa3d`
- corrected registry: `d6125027bf6e8f6f32e5d83eb2fad6bf87b0f8a69e71273649f88197d0fbba1d`
- old agreement metrics: `78856624b9ffbe5a64b022f54d06793dfe01902536580e0139abab89f2da80f6`
- corrected agreement metrics: `02cffcf346b3136d774239054742410178fe5b65a1d2c4b5e03a39831ac14244`

The original artifacts remain under `taxonomy/` and `snapshot_full_55/`.
Corrected artifacts are under `taxonomy_derived_correction_2026-08-16/` and
`snapshot_full_55_derived_correction_2026-08-16/`. The atlas was rebuilt from
the corrected snapshot and passed desktop/mobile browser QA with unchanged
scientific counts and route content.
