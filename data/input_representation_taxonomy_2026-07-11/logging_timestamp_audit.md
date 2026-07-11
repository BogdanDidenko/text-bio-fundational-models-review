# Logging Timestamp Audit

The initial open-discovery, taxonomy-synthesis, and first fixed-classification
shards logged exact prompt, schema, prompt SHA-256, model, endpoint,
temperature, response, duration, usage object, request order, errors, and
retries, but their per-call JSONL records did not include an explicit UTC wall
clock field. The wrapper's HTTP access stream contained wall-clock timestamps,
but that stream is not used as record-level evidence because it cannot be
unambiguously joined to concurrent requests.

During the run, `LiteLLMEndpointClient` was amended to add `timestamp_utc` to
every request, response, and error record. This logging-only change did not
alter prompts, schemas, model settings, candidate inventories, or validation.
It is present in the parallel fixed retries and all subsequently started dense
and adjudication calls. Earlier call ordering and elapsed durations are retained
as originally recorded; no retrospective timestamps were invented.

The final artifact manifest records UTC filesystem modification time, byte
size, and SHA-256 for every artifact. Source Markdown and Docling hashes are
also retained in per-record summaries. These fields support integrity and run
ordering but are not misrepresented as missing original request timestamps.
