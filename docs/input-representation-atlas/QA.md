# Atlas QA Record

## Data integrity

- Taxonomy root: 1
- Carrier families: 5
- Operational subtypes: 15
- Exact subtype-membership groups: 51
- Unique model nodes: 117/117
- Canonical family nodes in render: 5
- Mirrored subtype ports: 28
- Configurations: 400/400
- Grounded routes: 519/519
- Models with a validated source crop: 85
- Explicit no-suitable-figure cases: 32
- Routes without final grounding: 0

The baseline crop audit covers its 111 model IDs exactly once. Two blind
reviewers checked those baseline decisions. Exact rendered previews were then subjected to
an adversarial input-role check that distinguishes target-model input from
graders, outputs, downstream consumers, and mismatched routes. Every non-pass
was resolved by a scope-aware `gpt-5.4` adjudicator. The six newly integrated
model entries passed the incremental grounding and crop-selection checks. The
combined atlas retains crops for 85 models; the remaining 32 are explicitly
excluded from figure display.

## Browser verification

The static site was exercised with Playwright against local Google Chrome at:

- desktop: 1440 x 1000;
- mobile: 390 x 844.

Verified behaviors:

- one root, 51 membership-group, and 117 unique model nodes render;
- each carrier family appears once on the central taxonomy spine;
- subtype layout ports appear on both sides of the central family spine;
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
- the `2026-08-09` collection filter isolates 3 records, 6 models, and 30 routes;
- no page horizontal overflow occurs at either viewport;
- no browser console or page errors occur;
- Open Graph and Twitter Card metadata reference the absolute public preview;
- the rendered social preview is a nonblank 1200 x 630 PNG;
- screenshots are nonblank and were visually inspected in all-model, subtype,
  model-focus, and mobile states.

Re-run locally after starting a static server:

```bash
NODE_PATH=/path/to/node_modules node scripts/qa_input_representation_atlas.mjs \
  http://127.0.0.1:8765/
```
