# tGPT Failure Analysis

Date: 2026-07-01

Record: `rec_000003`, original cluster `2680`

Title: Generative pretraining from large-scale transcriptomes: Implications for single-cell deciphering and clinical translation

Expected status: `INCLUDE` as protocol-exception positive (`P2`) in `data/pilot_smoke_annotated.csv` and `protocol/ground_truth_models.md`.

Observed status in the 3-run determinism check:

| Run | Final decision | Final code | Final source |
|---|---|---|---|
| run_1 | EXCLUDE | EC2_no_text_component | python_gate |
| run_2 | EXCLUDE | EC2_no_substantive_text_bio_bridge | python_gate |
| run_3 | EXCLUDE | EC2_no_text_component | python_gate |

## What The Logs Show

The architecture reviewer behaved correctly in all three runs:

- `generative_model_present = yes`
- `foundation_model_evidence = yes`
- `primary_exclusion_code = none`

The failure came from the scope reviewer:

- run_1: `text_component_present = no`, `text_bio_bridge_present = no`
- run_2: `text_component_present = yes`, `text_bio_bridge_present = no`
- run_3: `text_component_present = no`, `text_bio_bridge_present = no`

The Python gate then treated the scope reviewer EC2 code as decisive because there was no `unclear`, no uncertainty reason, and no paper-type conflict. Therefore tGPT never reached the adjudicator.

## Why It Happened

The operative runtime prompt is `protocol/screening_prompt_templates/scope_reviewer_prompt.txt`. It contains the rule:

> Gene-token or other biological-token modeling counts as a text/language component only when the abstract clearly describes generative language-model-style token modeling as part of the candidate model.

The tGPT abstract says:

> modeling gene expression rankings as generative pretraining task

and:

> autoregressively models the ranking of a gene in the context of its preceding neighbors

That is generative biological-token language modeling under the protocol, but the prompt does not explicitly name gene-expression rankings / gene-rank sequences as covered by the exception. The reviewer interpreted "gene expression rankings" as expression-only biology rather than as gene-token sequence modeling.

The stricter gate amplified this error: a confident EC2 from the scope reviewer overrides the architecture reviewer even when architecture reviewer says the model is generative and foundation-model-like.

## Root Cause

This is not primarily a model-capability failure. It is a prompt/gate mismatch with the protocol exception:

1. The protocol says biological-token generative models such as tGPT are in scope.
2. The runtime scope prompt only gives a generic gene-token exception.
3. The abstract uses "gene expression rankings" rather than the exact phrase "gene tokens".
4. The gate does not escalate this pattern to adjudication.

## Recommended Fix

Before a full rerun, update the scope/adjudicator prompts and gate:

1. Add explicit positive examples to the scope prompt:
   - gene identifiers, gene-order/ranking sequences, expression-rank tokens, cell sentences, or other biological-token sequences count as `text_component_present = yes` when modeled by GPT-style, decoder, autoregressive, or other generative language-model objectives.
2. Add an anti-collapse rule:
   - do not set EC2 solely because the model lacks natural language if the abstract describes generative/autoregressive modeling over gene or biological-token sequences.
3. Change Python gate so scope EC2 is not decisive when architecture reviewer says both:
   - `generative_model_present = yes`
   - `foundation_model_evidence = yes`
   and the abstract contains terms such as `autoregressive`, `generative pretraining`, `gene ranking`, `gene expression rankings`, `gene tokens`, or `cell sentences`.
   In that case, route to adjudicator or apply the protocol exception.

