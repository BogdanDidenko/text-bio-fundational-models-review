# Parameter pass results (2026-10-13)

Design and predeclared gate: `GATE.md`. Model gpt-5.6-luna, reasoning high, full paper text, 3 runs per paper (held-out: 6).

| iteration | set | runs | all valid | single-run pair status agreement | consensus 1-3 vs 4-6 | max unspecified-share diff |
|---|---|---|---|---|---|---|
| p1 | dev | 3 | True | 0.936 |  |  |
| p2 | dev | 3 | True | 0.947 |  |  |
| p_h4 | heldout4 | 6 | True | 0.956 | 0.992 | 0.04 |
| p_rest30 | rest30 | 3 | True | 0.912 |  |  |

Held-out gate: P1 True, P2 0.992 over 377 slots (>= 0.90), P3 max 0.04 (<= 0.10); gate met: True.
P3 was computed per parameter name pooled across operations (deviation from the per-operation wording in GATE.md).
Normalised exact value agreement among slots stated in both halves: 0.368 (values are worded differently; analyses use status only).

Rules: tuned on dev in p1 -> p2 (specificity rules for values, serialize order/lexical mapping, rank order, per-sample scaling), frozen before p_h4 and p_rest30 (rules sha256 acc35b203981...).
One rest30 run (run_1, june_update_2026-06-10__rec_000133) failed validation after 4 repairs on one non-literal quote; it was restarted clean with the same rules (failed attempt kept as `.failed_attempt_1`).

Consensus over 2,383 slots: stated 1,559 (unanimous 1,381; 2 of 3: 178), unspecified 824 (unanimous 715; 2 of 3: 109). Published in library release 1.2.1 (operations identical to 1.2.0).
