# Atlas QA Record

## Data integrity

- Families: 5
- Operational subtypes: 15
- Model entities: 111/111
- Configurations: 376/376
- Grounded routes: 489/489
- Models with an original-paper figure: 111/111
- Deduplicated source figures: 77
- Routes without final grounding: 0

## Browser verification

The static site was exercised with Playwright against local Google Chrome at:

- desktop: 1440 × 1000;
- mobile: 390 × 844.

Verified behaviors:

- all five taxonomy lanes render;
- all 111 unique models occur on the carrier map;
- all 15 subtype examples render;
- the catalog contains 111 architecture cards;
- family and subtype filters update catalog counts;
- search resolves a specific architecture;
- architecture dialogs load their source figure and complete route inventory;
- the evidence view exposes 489 routes with 50-row pagination;
- no page or dialog horizontal overflow occurs at either viewport;
- no browser console or page errors occur;
- all 77 copied figure assets exist and have nonzero source dimensions.

The generated screenshots used for visual inspection are local QA artifacts and
are not part of the published site.
