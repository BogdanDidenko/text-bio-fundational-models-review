# Atlas QA Record

## Data integrity

- Taxonomy root: 1
- Carrier families: 5
- Operational subtypes: 15
- Unique model nodes: 111/111
- Graph nodes: 132
- Graph edges: 234
- Configurations: 376/376
- Grounded routes: 489/489
- Models with a model-specific source crop: 103
- Explicit no-suitable-figure cases: 8
- Deduplicated copied source figures: 68
- Routes without final grounding: 0

The crop audit covers all 111 model IDs exactly once. It contains 98 suitable,
five partially suitable, and eight explicit unsuitable/no-figure outcomes. The
second pass reselected and recropped 29 models after the original automatic
figure selector was rejected by vision review.

## Browser verification

The static site was exercised with Playwright against local Google Chrome at:

- desktop: 1440 x 1000;
- mobile: 390 x 844.

Verified behaviors:

- one root, five family, 15 subtype, and 111 unique model nodes render;
- all 234 directed taxonomy links render;
- a multi-parent model remains a single identity node;
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
