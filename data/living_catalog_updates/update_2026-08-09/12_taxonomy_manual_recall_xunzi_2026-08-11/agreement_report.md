# Input-Representation Taxonomy Agreement Report

- Unit for route detection: fixed open-discovery route_ref.
- Unit for carrier agreement: exact carrier-family set assigned to a
  candidate accepted in both compared runs; split routes remain visible.
- Screening records: 1
- Accepted final input routes: 14
- Minimum pairwise route-detection Jaccard: 0.750
- Carrier-family exact agreement: 1.0
- Carrier-family Krippendorff alpha: 1.0
- Dense-only accepted candidates: 3
- Acceptance passed: False

## Pairwise route detection

| pair | intersection | union | Jaccard |
|---|---:|---:|---:|
| r1-r2 | 9 | 11 | 0.818 |
| r1-r3 | 9 | 12 | 0.750 |
| r2-r3 | 11 | 12 | 0.917 |

## Acceptance checks

- all_direct_runs_complete: True
- dense_run_complete: True
- adjudication_complete: True
- all_adjudicated_routes_grounded: True
- all_adjudicated_routes_taxonomy_consistent: True
- no_non_input_or_other_accepted: True
- output_derived_inputs_explicit: True
- pairwise_jaccard_ge_0_80: False
- carrier_agreement_ge_0_90: True
- krippendorff_alpha_ge_0_80_or_not_applicable: True
- every_dense_candidate_accounted: True
