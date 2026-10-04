# Operation-constructor rebuild decisions

2026-10-05, coordinator-curated reconstruction using existing complete evidence.
The author's clarification sets the unit: a reusable computation with operands and
results. There is no new model call or provider integration in this rebuild.

| Decision | Source support and resulting representation |
| --- | --- |
| Remove the failed mixed-level catalog | Delete the 91 representation/component/composite entries and obsolete generated release. Preserve original pilot annotations/evidence unchanged. Previous development remains in commit a61f9c2b. |
| One lookup primitive | Existing embedding_lookup, token_embedding, vocabulary mapping, gene reference lookup and raw shared-output-row lookup all retrieve entries by keys. Give every call a concrete table operand and retain resource kind, biological content and trainability. Unknown table shape/sharing remains uncertain. |
| Separate lookup and normalization | X-Cell sec_0049 and identity-encoder evidence explicitly declare embedding lookup followed by LayerNorm. Introduce the intermediate and two calls; preserve all original source steps. |
| Parameterize normalization | MUPAD sec_0016 declares TPM; X-Cell sec_0095 declares CP10K then log1p. X-Cell parameter/feature encoders declare LayerNorm. Method and axes remain instance attributes; log1p has its own call. |
| Preserve dataset bypass | X-Cell sec_0095 explicitly skips scaling/log1p on pre-normalized datasets. Retain conditional calls and bypass edge. |
| Separate projection and output normalization | X-Cell sec_0051 declares source-specific LeakyReLU MLP plus LayerNorm; sec_0014 declares ReLU MLP plus LayerNorm. Keep activation on the MLP invocation and normalization as a following call. |
| Preserve attention ports and repeats | InstructCell sec_0021 declares query self-attention then cross-attention to cell keys/values in a repeated stack. ChatNT source-only resampling and X-Cell prior attention retain query/key-value/mask roles. Question-aware ChatNT internal schedule remains unexpanded. |
| Preserve unknown fusion | X-Cell selected text omits the gene/value/reveal combination equation. Retain the original boundary and its operands with no asserted add/concatenate primitive. |
| Preserve imputation semantics | X-Cell sec_0096 declares optional LayerNorm, zero-imputation for unavailable sources and availability mask. Keep conditional normalization, bypass and imputation. Actual zero values do not establish missingness. |
| Add a real binning example | The complete existing OKR-Cell sec_0022 explicitly declares log1p, HVG selection, per-cell nonzero equal-interval bins, two embedding layers and element-wise addition. Reconstruct the two branches and show WITHDRAWN source status. Keep it outside the four-record pilot denominator. |
| Retain unresolved modules | Every source step remains attached to its actual task/phase. Whole encoders, generative models and unproved internal transformations stay visible with operation_id null. Further reconstruction can refine them using the same primitives. |
| Audit type reuse independently | Count distinct primary record IDs per operation. Repeated calls within tasks/phases remain separate invocation counts. Supplemental section examples are excluded from this denominator. |

All original 47 trajectories have full equality restoration tests. Source quotations
are preserved in full. Added intermediate shapes are left unspecified when the
source does not establish them. Required-port and reference tests check graph
integrity. Source entailment and complete module decomposition remain review tasks.
