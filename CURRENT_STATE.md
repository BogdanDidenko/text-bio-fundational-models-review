# Current state of the review (canonical pointer)

Last updated: 2026-10-14. Git tag: `operation-library-1.3.0`.

This file says which outputs are current. The repository also keeps earlier runs for provenance;
anything not listed under "Current" below is history and must not be cited as a result.

## Current

| What | Version | Location |
|---|---|---|
| Included corpus, PRISMA flow | 55 records / 54 studies (search closed 2026-08-09) | `analysis/prisma_flow_2026-10-07/` |
| Input-route atlas (charting, 5-family taxonomy) | 109 models, 585 routes | `docs/input-representation-atlas/data/atlas.json` |
| Operation catalog (22 operations) | release 1.3.0 | `analysis/representation_block_library_2026-10-04/operation_catalog.json`, frozen in `releases/1.3.0/`, changes in `DECISION_MEMO_1.3.0.md` |
| Decomposition protocol | v3.2 (atlas-anchored per-step decisions, 3-run majority) | `scripts/operation_decomposition_v3.py`, `scripts/run_decomposition_stabilization.py`, `scripts/decomposition_consensus.py`, `scripts/build_consensus_release.py` |
| Decomposed corpus (50 agent papers + 4 author pilots) | release 1.3.0 | `analysis/operation_decomposition_v32_2026-10-14/` (records, corpus, steward queue) |
| Source runs of 1.3.0 | v32_all (50 papers x 3), v32_h4 (heldout4 runs 1-6) | `analysis/operation_decomposition_2026-10-07/stabilization/v32_all/`, `v32_h4/` |
| Parameter pass (stated / unstated per parameter) | 1.2.1 slots carried over; 16 changed papers re-run (p32) | `analysis/operation_decomposition_v32_2026-10-14/parameter_pass/consensus/`; design in `analysis/operation_decomposition_v31_2026-10-12/parameter_pass/GATE.md` |
| Component-library website | release 1.3.0 | https://bogdandidenko.github.io/text-bio-fundational-models-review/component-library/ (source `docs/input-representation-atlas/component-library/`) |
| Operation synthesis numbers | release 1.3.0 | `analysis/review_synthesis_2026-10-07/operation_synthesis.json` |
| Motif library (frequent sub-chains) | v1 on 1.3.0 | `analysis/motif_library_2026-10-14/` (`MOTIF_LIBRARY.md`, `motifs.json`, Figure 5) |
| Design-pattern taxonomy (axes, archetypes) | spec v2; codebook on 1.3.0 | `analysis/design_taxonomy_2026-10-13/TAXONOMY_SPEC.md`, `taxonomy_codebook.csv` |
| Manuscript draft | 2026-10-14 | `manuscript/review_manuscript_draft.md` |

Key numbers (1.3.0): 54 papers, 475 input paths, 1,348 library calls, 819 unexpanded steps;
1,468 agent steps: 1,394 unanimous, 74 decided 2 of 3, 0 ties; 2,433 parameter slots: 1,589 stated;
15 motifs in 44 of 54 papers.

Stability, reported honestly in the manuscript:
- v3.1 on heldout4 (unseen at the time): 0.956 step agreement, 0.854 route agreement.
- v3.2 on the same papers: 0.996 / 0.988. This is in-sample, because heldout4 informed the v3.2 fixes.

## Pending (known stale items)

- Figure 3 (`analysis/review_synthesis_2026-10-07/operation_reuse.png`) is still drawn from release
  1.1.0. It must be redrawn from 1.3.0 before submission.
- Figure 4 and `pattern_crosstabs.csv` / `axis_tests.json` (`analysis/design_taxonomy_2026-10-13/`)
  were computed on 1.2.1. Archetype labels are unchanged, and the shares differ by 2 points or less.
  They should still be redrawn from 1.3.0.
- 74 two-of-three steps and 75 operation proposals await steward review
  (`analysis/operation_decomposition_v32_2026-10-14/STEWARD_QUEUE.md`).

## Superseded (history, do not cite)

| Location | What it was | Superseded by |
|---|---|---|
| `analysis/operation_decomposition_2026-10-07/records/`, `corpus_assemblies.json`, `STEWARD_QUEUE.md`, `corpus_status.json` | release 1.1.0, protocol v1 (single extractor + reviewer, free graph structure) | 1.3.0 |
| `analysis/operation_decomposition_2026-10-07/replicates/` | v1 run-to-run study that showed instability (op-set Jaccard 0.667) | stabilization work below |
| `analysis/operation_decomposition_2026-10-07/stabilization/v2_i1`, `v3_i1`, `v3_h3diag` | protocol development iterations (v3_i2-v3_h3 run data lost; values in `STABILIZATION_REPORT.md`) | v3.2 |
| `analysis/operation_decomposition_2026-10-07/stabilization/v3_i8`, `v3_h4`, `v31_rest30` | source runs of releases 1.2.0/1.2.1 (protocol v3.1) | `v32_all`, `v32_h4` |
| `analysis/operation_decomposition_v31_2026-10-12/` (records, corpus, steward queue) | releases 1.2.0 and 1.2.1 | `analysis/operation_decomposition_v32_2026-10-14/` |
| `analysis/design_taxonomy_2026-10-13/chain_profile_exploratory.png`, `chain_profile_summary.json`, `motif_table.csv` | exact-chain diversity analysis ("no recurring recipes"); withdrawn as an artefact of chain construction | motif library |
| `analysis/representation_block_library_2026-10-04/releases/1.0.0` ... `1.2.1` | earlier frozen catalog releases | `releases/1.3.0` |
