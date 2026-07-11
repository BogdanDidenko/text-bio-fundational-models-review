# Input-Representation Taxonomy Agreement Report

- Unit for route detection: fixed open-discovery route_ref.
- Unit for carrier agreement: exact carrier-family set assigned to a
  candidate accepted in both compared runs; split routes remain visible.
- Screening records: 52
- Accepted final input routes: 489
- Minimum pairwise route-detection Jaccard: 0.948
- Carrier-family exact agreement: 0.9248554913294798
- Carrier-family Krippendorff alpha: 0.8752078848922206
- Dense-only accepted candidates: 21
- Acceptance passed: True

## Pairwise route detection

| pair | intersection | union | Jaccard |
|---|---:|---:|---:|
| r1-r2 | 460 | 478 | 0.962 |
| r1-r3 | 458 | 483 | 0.948 |
| r2-r3 | 466 | 481 | 0.969 |

## Acceptance checks

- all_direct_runs_52_of_52: True
- dense_run_52_of_52: True
- adjudication_52_of_52: True
- all_adjudicated_routes_grounded: True
- all_adjudicated_routes_taxonomy_consistent: True
- no_non_input_or_other_accepted: True
- output_derived_inputs_explicit: True
- pairwise_jaccard_ge_0_80: True
- carrier_agreement_ge_0_90: True
- krippendorff_alpha_ge_0_80: True
- every_dense_candidate_accounted: True
