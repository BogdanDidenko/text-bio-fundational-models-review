# Google Scholar Provider Export Contract

Google Scholar is a supplementary, year-bounded discovery source in each living
review update. The canonical pipeline does not scrape it directly. Instead it
accepts one provider-mediated capture at:

`data/living_catalog_updates/update_<date>/00_search/google_scholar_provider_export.json`

The capture may come from an approved provider or a documented institutional
workflow, but it must contain all configured queries and preserve raw-response
provenance. It does not claim a day-precise or exhaustive Google Scholar index.

Create the signed skeleton before acquisition; do not edit its query bundle after
collecting records:

```bash
python3 scripts/build_google_scholar_provider_template.py \
  --config data/living_catalog_updates/update_2026-08-09/00_search/search_config.json \
  --provider "provider name" \
  --pagination-policy "retrieve every provider-visible page" \
  --output data/living_catalog_updates/update_2026-08-09/00_search/google_scholar_provider_export.json
```

The repository includes a SerpAPI collector that creates the same contract
directly and resumes from already hashed raw pages:

```bash
python3 scripts/capture_google_scholar_serpapi.py \
  --config data/living_catalog_updates/update_2026-08-09/00_search/search_config.json \
  --api-keys api_keys.json \
  --output data/living_catalog_updates/update_2026-08-09/00_search/google_scholar_provider_export.json
```

Store the credential as `serpapi` in ignored `api_keys.json`. The collector uses
the configured `as_ylo`/`as_yhi` year bounds, follows every provider-returned
pagination link until `no_next_page`, hashes every raw response, merges repeated
results while preserving query membership, and redacts the credential from
provider-returned metadata. A provider error, pagination cycle, or incomplete
query prevents the export from entering deduplication.

```json
{
  "schema_version": 1,
  "query_bundle": {
    "queries": ["exact configured query 1", "..."],
    "year_range": [2026, 2026],
    "date_from": "2026-07-07",
    "date_to": "2026-08-09",
    "acquisition": {
      "provider": "provider name",
      "provider_version": "optional version",
      "locale": "en",
      "pagination_policy": "retrieve every provider-visible page"
    }
  },
  "query_signature": "sha256 of query bundle as computed by reproduce_search.py",
  "raw_response_manifest": [
    {"artifact": "raw/gs_q1/page_000.json", "sha256": "..."}
  ],
  "query_execution": [
    {
      "query_id": "gs_q1",
      "execution_complete": true,
      "retrieval_complete": true,
      "termination": "no_next_page",
      "pages_retrieved": 1,
      "records_retrieved": 0,
      "source_exhaustive": "unknown"
    }
  ],
  "records": [
    {
      "title": "...",
      "authors": ["..."],
      "year": "2026",
      "abstract": "...",
      "url": "...",
      "query_ids": ["gs_q1"],
      "raw_artifact": "raw/gs_q1/page_000.json",
      "raw_response_sha256": "..."
    }
  ]
}
```

The import rejects an export unless it has exactly the configured query strings,
year range, review interval, one completion row per configured query, and a non-empty hashed
raw-response manifest. Every query must declare both `execution_complete` and
`retrieval_complete`; reaching a provider cap or a provider error is not a
complete capture. The provider remains a supplementary, `year_only` source.
