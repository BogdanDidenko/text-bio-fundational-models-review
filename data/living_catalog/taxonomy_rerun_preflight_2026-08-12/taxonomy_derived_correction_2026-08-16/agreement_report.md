# Input-Representation Taxonomy Agreement Report

- Unit for route detection: fixed open-discovery route_ref.
- Unit for carrier agreement: exact carrier-family set assigned to a
  candidate accepted in both compared runs; split routes remain visible.
- Screening records: 55
- Accepted final input routes: 586
- Minimum pairwise route-detection Jaccard: 0.937
- Carrier-family exact agreement: 0.9252525252525252
- Carrier-family Krippendorff alpha: 0.8813738381736066
- Dense-only accepted candidates: 68
- Acceptance passed: True

## Pairwise route detection

| pair | intersection | union | Jaccard |
|---|---:|---:|---:|
| r1-r2 | 496 | 529 | 0.938 |
| r1-r3 | 495 | 521 | 0.950 |
| r2-r3 | 494 | 527 | 0.937 |

## Acceptance checks

- all_direct_runs_complete: True
- dense_run_complete: True
- adjudication_complete: True
- all_adjudicated_routes_grounded: True
- all_adjudicated_routes_taxonomy_consistent: True
- no_non_input_or_other_accepted: True
- output_derived_inputs_explicit: True
- pairwise_jaccard_ge_0_80: True
- carrier_agreement_ge_0_90: True
- krippendorff_alpha_ge_0_80_or_not_applicable: True
- every_dense_candidate_accounted: True
- unresolved_dense_candidates_explicit: True
