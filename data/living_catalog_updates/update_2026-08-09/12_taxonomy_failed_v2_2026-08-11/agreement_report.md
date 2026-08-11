# Input-Representation Taxonomy Agreement Report

- Unit for route detection: fixed open-discovery route_ref.
- Unit for carrier agreement: exact carrier-family set assigned to a
  candidate accepted in both compared runs; split routes remain visible.
- Screening records: 2
- Accepted final input routes: 17
- Minimum pairwise route-detection Jaccard: 1.000
- Carrier-family exact agreement: 0.7333333333333333
- Carrier-family Krippendorff alpha: 0.5463917525773196
- Dense-only accepted candidates: 2
- Acceptance passed: False

## Pairwise route detection

| pair | intersection | union | Jaccard |
|---|---:|---:|---:|
| r1-r2 | 15 | 15 | 1.000 |
| r1-r3 | 15 | 15 | 1.000 |
| r2-r3 | 15 | 15 | 1.000 |

## Acceptance checks

- all_direct_runs_complete: True
- dense_run_complete: True
- adjudication_complete: True
- all_adjudicated_routes_grounded: True
- all_adjudicated_routes_taxonomy_consistent: True
- no_non_input_or_other_accepted: True
- output_derived_inputs_explicit: True
- pairwise_jaccard_ge_0_80: True
- carrier_agreement_ge_0_90: False
- krippendorff_alpha_ge_0_80_or_not_applicable: False
- every_dense_candidate_accounted: True
