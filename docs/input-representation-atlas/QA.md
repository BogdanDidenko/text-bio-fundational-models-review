# Atlas QA Record

## Data integrity

- Taxonomy root: 1
- Carrier families: 5
- Operational subtypes: 15
- Exact subtype-membership groups: 48
- Single-subtype groups: 9
- Combination groups: 39
- Unique model nodes: 111/111
- Canonical graph nodes: 180
- Canonical graph edges: 257
- Full mirrored render nodes: 198
- Full mirrored render edges: 275
- Mirrored family ports: 10
- Mirrored subtype ports: 28
- Configurations: 376/376
- Grounded routes: 489/489
- Models with a cross-validated source crop: 79
- Explicit no-suitable-figure cases: 32
- Routes without final grounding: 0

The crop audit covers all 111 model IDs exactly once. Two blind reviewers each
checked all 111 model decisions. Exact rendered previews were then subjected to
an adversarial input-role check that distinguishes target-model input from
graders, outputs, downstream consumers, and mismatched routes. Every non-pass
was resolved by a scope-aware `gpt-5.4` adjudicator. The 79 retained crops have
no unresolved validation finding; the remaining 32 are explicitly excluded
from figure display.

## Browser verification

The static site was exercised with Playwright against local Google Chrome at:

- desktop: 1440 x 1000;
- mobile: 390 x 844.

Verified behaviors:

- one root, 48 membership-group, and 111 unique model nodes render;
- mirrored family and subtype layout ports appear on both sides of the root;
- every model has exactly one incoming membership-group edge;
- every group has exactly the subtype-parent edges and model-child edges stated
  in the canonical graph artifact;
- all 48 groups are split across both sides while remaining unique identities;
- all SVG node rectangles are non-overlapping in graph coordinates;
- a multi-subtype model remains a single identity node;
- family and subtype focus recompute a readable graph neighborhood;
- model focus highlights its ancestry and exposes crop, example, and all routes;
- model nodes visually separate the original-paper crop from the illustrative
  input example;
- the secondary model index and evidence table remain filterable;
- no page horizontal overflow occurs at either viewport;
- no browser console or page errors occur;
- screenshots are nonblank and were visually inspected in all-model, subtype,
  model-focus, and mobile states.

Re-run locally after starting a static server:

```bash
NODE_PATH=/path/to/node_modules node scripts/qa_input_representation_atlas.mjs \
  http://127.0.0.1:8765/
```
