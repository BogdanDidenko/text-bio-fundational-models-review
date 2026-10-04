# Operation constructor for model input reconstruction

## Unit and purpose

The library entry is a reusable operation with input and output ports: normalization,
binning, lookup, projection, concatenation, sampling, selection and other documented
data transformations. Gene expression, token IDs, embedding matrices and computed
vectors are data/resource instances in the graph. Biological names and module names
stay on the instances. Each task/phase chain assembles calls from shared operations.

`operation_catalog.json` is the one editable catalog. The strict Pydantic contracts
are in `scripts/docling_graph_templates/representation_library.py`. Validation,
JSON Schema and static Pages retain the existing official Pydantic/GitHub Actions
mechanisms. These are descriptive operation graphs; no neural computation is run.

Official references used to define the basic interfaces:
- https://docs.pydantic.dev/latest/concepts/models/
- https://docs.pytorch.org/docs/stable/generated/torch.nn.Embedding.html
- https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.KBinsDiscretizer.html
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## Agent procedure

Read the complete evidence and the pinned operation catalog. Establish record,
model variant, task, one lifecycle phase and receiving component. Preserve the
source descriptions, evidence, task-specific paths, state updates and uncertainty.

For each documented transformation:
1. Search existing operations by computation and port signature.
2. Reuse the operation ID. Put method, biological source, axes, vocabulary, table
   learning/freeze status and other documented choices on its actual invocation.
3. Connect concrete input node IDs to named ports and concrete output IDs to results.
4. Decompose a multi-operation source step only when the source states the operations
   and their order. Preserve the original step and cite evidence for the decomposition.
5. Introduce a documented intermediate node when necessary. Leave unknown shape and
   axes unspecified. Mark an implicit component parameter separately from measured
   data and computed features.
6. Preserve conditional bypasses, parallel branches, aligned indices and repeated
   motifs. Shared operation type establishes no shared tensor or weight identity.
7. Retain opaque module boundaries with `operation_id: null` when internal computation
   cannot be established. Submit a scientific decomposition question rather than
   creating a model-specific operation name.

Return an `OperationAssembly`. Its nodes, operation calls, original source steps,
conditional bypasses and receiving operands form one evidence-backed graph. Every
call pins the release, refers to its source step and carries unchanged evidence.

## Granularity examples

- Numerical normalization method is an invocation property. TPM, CP10K and LayerNorm
  have explicit method/axis semantics. Log1p is a separate operation.
- Numeric binning yields interval IDs. Strategy, scope and zero handling are explicit.
- Lookup requires keys and a table operand. A trainable embedding matrix, frozen
  matrix, vocabulary map and precomputed feature table reuse the lookup interface.
  Preserve their distinct resources and training status.
- `lookup followed by LayerNorm` produces two calls and an intermediate data node.
- A documented MLP followed by normalization yields projection then normalization.
  Preserve activation and other known details in the MLP invocation. Expand layers
  further only when their documented interfaces/order are recoverable.
- Unknown gene/value/mask fusion algebra stays an unexpanded boundary. Never assign
  addition or concatenation from a plausible architectural convention.
- Pre-normalized datasets preserve the explicitly documented bypass of scaling/log
  preprocessing. Missing reference features preserve imputation and availability.

Use symbolic dimensions with meaningful axes. Concrete architecture widths remain
in source quotations. No source/prompt/response caps, size filters or shortening.
Preserve full data and request author approval when a provider limit blocks access.
Recovered Markdown headings/section hashes retain their actual provenance; native
PDF coordinates are unavailable here. VLM-only observations require corroboration.

## Steward and extension

One library steward owns catalog changes. Before adding an operation compare its
input/output behavior with every plausible existing primitive. Reuse and instance
parameters are the default for equivalent computations. Different math justifies
different operations even when present in a single paper. Frequency is an audit
measure; it is never an acceptance quota.

The steward may add a source-backed new operation autonomously. It records the
compared operation IDs, evidence, definition, ports and decision. Changes of existing
scientific meaning/signature or merges require author approval and affected-call
review. Frozen releases and previous identities remain in Git history. Freeze new
releases with hashes; existing annotated chains retain their own release.

Never create a separate block merely for a gene name, a modality, a vector width,
a named model, an initial/intermediate state label or a task-specific role. These
are graph-instance properties. Traceability logs contain visible decisions,
responses and tool events; hidden reasoning is excluded.

## Build and verification

```bash
python scripts/build_representation_library.py
python scripts/build_representation_library.py --check
python -m unittest discover -s tests -p test_representation_library.py
```

The builder adapts the complete frozen four-paper pilot. Source restoration checks
verify every original trajectory field. Port checks verify IDs, required arguments,
results and graph references. Tests cover shared lookup, separate normalization/log
steps, conditional bypasses and unresolved fusion algebra. Source entailment remains
a scientific review responsibility.

The supplemental OKR-Cell expression-binning example was reconstructed from a
complete existing selected section. Its inventory title is marked WITHDRAWN. The
page retains that status and keeps this section example outside the four-record
assembly/reuse denominator. No eligibility or taxonomy count changes are made.

The failed 91-entry description catalog is removed from the active tree. It remains
recoverable through commit `a61f9c2b`. Canonical atlas data and source evidence are
unchanged. Further papers must be reconstructed with this operation-level guide
and independently reviewed before corpus-wide use.
