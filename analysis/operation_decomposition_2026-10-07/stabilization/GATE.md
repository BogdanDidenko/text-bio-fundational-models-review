# Decomposition stabilization: predeclared gate (2026-10-09)

Declared before the first v2 run. Development set: the 10 length-stratified papers of the replicate
study (`replicates/agreement.json`). Each protocol iteration runs every paper 3 times independently
(same model `gpt-5.6-luna`, reasoning `high`); measurement uses the extraction + mechanical repair
output (reviewer loop excluded while iterating; reinstated for the final confirmation).

The protocol is stable when, over all 3 run pairs of all 10 papers:

- G1 coverage: every run returns exactly one trajectory per atlas configuration and every atlas route's
  chain elements as steps (100%).
- G2 route agreement: at least 90% of route x run-pair comparisons have an identical ordered sequence
  of step operations (operation IDs; unexpanded boundary counted as its own symbol).
- G3 paper agreement: per-paper library-operation set Jaccard, median >= 0.90 and minimum >= 0.75.

Baseline (protocol v1, 3 runs incl. reviewer loop): G1 not met (trajectory counts e.g. 2/20/14),
paper operation-set Jaccard median 0.667, minimum 0.0.

Overfitting note: the gate is evaluated on the development set; the final protocol is applied to all
papers and its stability on a held-out subset is reported separately.
