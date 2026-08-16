# Input-Representation Taxonomy v1

**Classification unit:** One grounded route: a single source object carried through its transformation chain to the model-visible carrier consumed by the model.

Partition routes by the model-visible carrier mechanism. Biological modality, lifecycle phase, text role, and fusion topology are orthogonal dimensions; they do not decide the family unless they change the carrier that reaches the model.

Unknown and unclear are annotation states, not taxonomy categories. A multimodal configuration contains several source-to-model routes and is not coded as a single hybrid route.

## Operational decision boundary

Classify the first model-facing carrier after semantic preprocessing but before routine embedding lookup or encoder processing. Ordinary text tokens remain text-native; native or learned biological token IDs remain discrete; pixels and patches remain visual; coordinates and noisy states remain geometric/diffusion. Use a dense continuous carrier only when an external encoder, projector, pooling operation, or learned soft-token mechanism produces continuous vectors that enter the generative backbone without the ordinary tokenizer, symbol, raster, or geometric-state interface.

## Primary hierarchy

### `F1`: Text-native token streams

Routes whose visible carrier is ordinary text tokens, including free-form prompts, structured task scaffolds, and serialized biological context rendered as text. The biologic content is carried by language tokens rather than dense vectors, images, or geometric states.

**Structural criterion:** The generative backbone consumes standard text tokens, even when the text is biologically specialized or template-driven.

#### `F1.L1`: Plain language prompts and questions

Natural-language prompts, questions, instructions, or conversational turns that reach the model as ordinary text without a specialized biological serialization step.

Include when: The visible carrier is plain prose, a question, or an instruction.; The route does not require a domain-specific serializer before model intake.

Exclude when: The source is first converted into a gene list, cell sentence, ranked profile, or other biological serialization.; The visible carrier is a dense embedding, an image, or a diffusion state.

Positive route refs: full_2026-07-06__rec_000086::route_003, full_2026-07-06__rec_000086::route_006, full_2026-07-06__rec_000827::route_004, full_2026-07-06__rec_000090::route_032, full_2026-07-06__rec_000090::route_015, full_2026-07-06__rec_000950::route_010, full_2026-07-06__rec_000771::route_002

Counterexample route refs: full_2026-07-06__rec_000090::route_001, full_2026-07-06__rec_000086::route_002, full_2026-07-06__rec_000950::route_001, june_update_2026-06-10__rec_000121::route_003

#### `F1.L2`: Structured biological prompts and task scaffolds

Text prompts that encode explicit biological slots, metadata fields, retrieval directives, benchmark scaffolds, or relation-context prompts.

Include when: The text contains explicit biological fields, slots, or template-like task structure.; The prompt functions as a structured control frame rather than free-form conversation.

Exclude when: The input is only plain conversational text with no task scaffolding.; The carrier is a biological sentence serialization or a dense embedding prefix.

Positive route refs: full_2026-07-06__rec_000086::route_010, full_2026-07-06__rec_000086::route_012, full_2026-07-06__rec_000086::route_015, full_2026-07-06__rec_000090::route_021, full_2026-07-06__rec_000090::route_022, full_2026-07-06__rec_000090::route_023, full_2026-07-06__rec_000090::route_024, full_2026-07-06__rec_000090::route_025, full_2026-07-06__rec_000090::route_033, full_2026-07-06__rec_000090::route_034, full_2026-07-06__rec_000090::route_035

Counterexample route refs: full_2026-07-06__rec_000827::route_004, full_2026-07-06__rec_000090::route_001, full_2026-07-06__rec_000086::route_002, full_2026-07-06__rec_000950::route_002

#### `F1.L3`: Serialized biological context and ordered profiles

Text-token sequences produced by serializing cells, genes, neighborhoods, ranked profiles, or multi-cell contexts into language-like sentences or ordered lists before model intake.

Include when: The route converts biological objects into cell sentences, spatial sentences, gene lists, ranked expression profiles, or comparable serialized text.; The visible carrier is a textual summary of biological context, often across multiple nearby entities or samples.

Exclude when: The route is a simple question or instruction with no biological serialization.; The route is a fixed slot template rather than a serialized biological narrative.; The carrier is a dense vector, image, or diffusion state.

Positive route refs: full_2026-07-06__rec_000063::route_001, full_2026-07-06__rec_000063::route_002, full_2026-07-06__rec_000063::route_003, full_2026-07-06__rec_000063::route_004, full_2026-07-06__rec_000063::route_005, full_2026-07-06__rec_000063::route_006, full_2026-07-06__rec_000090::route_001, full_2026-07-06__rec_000090::route_002, full_2026-07-06__rec_000090::route_003, full_2026-07-06__rec_000090::route_004, full_2026-07-06__rec_000090::route_005, full_2026-07-06__rec_000090::route_006, full_2026-07-06__rec_000090::route_007, full_2026-07-06__rec_000090::route_008, full_2026-07-06__rec_000090::route_009, full_2026-07-06__rec_000090::route_010, full_2026-07-06__rec_000090::route_011, full_2026-07-06__rec_000090::route_012, full_2026-07-06__rec_000090::route_013, full_2026-07-06__rec_000090::route_014, full_2026-07-06__rec_000090::route_016, full_2026-07-06__rec_000090::route_017, full_2026-07-06__rec_000090::route_018, full_2026-07-06__rec_000090::route_019, full_2026-07-06__rec_000090::route_020, full_2026-07-06__rec_000090::route_028, full_2026-07-06__rec_000090::route_029, full_2026-07-06__rec_000090::route_030, full_2026-07-06__rec_000090::route_031, full_2026-07-06__rec_000827::route_005, full_2026-07-06__rec_000827::route_006, full_2026-07-06__rec_000827::route_007

Counterexample route refs: full_2026-07-06__rec_000827::route_004, full_2026-07-06__rec_000086::route_002, full_2026-07-06__rec_000950::route_001, june_update_2026-06-10__rec_000121::route_003

### `F2`: Discrete biological symbol streams

Routes whose biological source is represented as a discrete symbol stream native to or added to the tokenizer, rather than as prose text or dense embeddings. This includes biological BPE streams, multi-track structural alphabets, and learned quantized codebook IDs.

**Structural criterion:** The model-visible carrier is a tokenized biological sequence or structured biological symbol stream.

#### `F2.L1`: Native biological token streams

DNA, RNA, or protein corpora rendered as discrete biological tokens through an extended tokenizer or chunking protocol.

Include when: The route uses tokenized DNA, RNA, protein, or comparable biological sequence corpora.; The visible form is a chunked biological token stream rather than a prose prompt or embedding.

Exclude when: The route is an ordinary text prompt or instruction.; The route is a dense embedding prefix or an image patch input.

Positive route refs: june_update_2026-06-10__rec_000350::route_001, june_update_2026-06-10__rec_000350::route_002, june_update_2026-06-10__rec_000350::route_003

Counterexample route refs: full_2026-07-06__rec_000090::route_001, full_2026-07-06__rec_000086::route_002, full_2026-07-06__rec_000950::route_001, june_update_2026-06-10__rec_000121::route_003

#### `F2.L2`: Multi-track structural symbol streams

A token stream that explicitly preserves multiple structural tracks or aligned alphabets, such as sequence plus secondary-structure or tertiary-structure tracks.

Include when: The route preserves several aligned structural tracks in one discrete token stream.; The visible carrier is a structured symbolic alphabet, not an embedding.

Exclude when: The route is a single-track tokenized corpus.; The route is a continuous prefix, image patch, or diffusion state.

Positive route refs: june_update_2026-06-10__rec_000350::route_005, june_update_2026-06-10__rec_000350::route_006

Counterexample route refs: june_update_2026-06-10__rec_000350::route_001, full_2026-07-06__rec_000950::route_002, full_2026-07-06__rec_000086::route_002, june_update_2026-06-10__rec_000121::route_003

#### `F2.L3`: Learned quantized IDs and codebook tokens

Routes whose biological content is rendered as learned discrete IDs from VQ, RVQ, or codebook-style tokenizers. These are discrete symbols, not continuous embeddings and not native tokenizer words.

Include when: The route uses VQ, RVQ, or codebook IDs as model-visible inputs.; The discrete IDs are embedded into the LLM vocabulary or otherwise treated as symbol tokens.; The route is not just a continuous latent prefix.

Exclude when: The route is a continuous embedding or resampler output.; The route is ordinary prose text or a native biological token corpus.

Positive route refs: june_update_2026-06-10__rec_000121::route_003, june_update_2026-06-10__rec_000121::route_004, june_update_2026-06-10__rec_000121::route_006

Counterexample route refs: full_2026-07-06__rec_000086::route_002, full_2026-07-06__rec_000090::route_001, full_2026-07-06__rec_000950::route_001, june_update_2026-06-10__rec_000350::route_001

### `F3`: Dense continuous carriers

Routes whose model-visible form is a learned dense vector, soft-token block, prefix embedding, resampled latent, or similar continuous carrier inserted into a generative backbone. The biological source is encoded rather than discretely tokenized.

**Structural criterion:** The source is converted into continuous embeddings, soft tokens, or learned latent blocks before reaching the generator.

#### `F3.L1`: Direct projected embeddings

A continuous embedding projected from a biological encoder into the language or multimodal backbone, typically via a linear layer, projector, or latent-space mapping.

Include when: The route explicitly projects biological inputs into an embedding space or unified latent space.; The visible carrier is a dense vector block rather than text tokens or image patches.

Exclude when: The carrier is a fixed prefix block of learned virtual tokens.; The carrier is an image patch sequence or a discrete biological token stream.; The carrier is a diffusion state or geometric constraint.

Positive route refs: full_2026-07-06__rec_000086::route_002, full_2026-07-06__rec_000086::route_004, full_2026-07-06__rec_000086::route_005, full_2026-07-06__rec_000086::route_007, full_2026-07-06__rec_000086::route_008, full_2026-07-06__rec_000086::route_009, full_2026-07-06__rec_000086::route_013, full_2026-07-06__rec_000827::route_010, full_2026-07-06__rec_000827::route_011, full_2026-07-06__rec_000827::route_012, full_2026-07-06__rec_000827::route_013, june_update_2026-06-10__rec_000248::route_003, june_update_2026-06-10__rec_000248::route_005, june_update_2026-06-10__rec_000248::route_009

Counterexample route refs: full_2026-07-06__rec_000090::route_001, full_2026-07-06__rec_000950::route_001, full_2026-07-06__rec_000827::route_004, june_update_2026-06-10__rec_000121::route_003

#### `F3.L2`: Virtual-token prefixes

A fixed-length block of learned virtual tokens or multimodal prefix tokens that stands in for the biological source before being concatenated or inserted into the backbone.

Include when: The route uses a fixed prefix, placeholder-bearing virtual-token block, or multimodal prefix.; The biological source is not passed as ordinary text but as a learned prefix-like embedding bundle.

Exclude when: The route uses direct projection into a latent space without a dedicated prefix block.; The carrier is a pooled embedding, an image patch set, or a diffusion state.

Positive route refs: june_update_2026-06-10__rec_000148::route_001, june_update_2026-06-10__rec_000148::route_003, june_update_2026-06-10__rec_000148::route_005, june_update_2026-06-10__rec_000148::route_006, june_update_2026-06-10__rec_000148::route_008, june_update_2026-06-10__rec_000148::route_010, june_update_2026-06-10__rec_000148::route_017, june_update_2026-06-10__rec_000148::route_018, june_update_2026-06-10__rec_000152::route_001, june_update_2026-06-10__rec_000152::route_002, june_update_2026-06-10__rec_000152::route_004, june_update_2026-06-10__rec_000152::route_005, june_update_2026-06-10__rec_000152::route_006, june_update_2026-06-10__rec_000152::route_008, june_update_2026-06-10__rec_000152::route_009, june_update_2026-06-10__rec_000152::route_010

Counterexample route refs: full_2026-07-06__rec_000086::route_002, full_2026-07-06__rec_000090::route_001, full_2026-07-06__rec_000950::route_002, june_update_2026-06-10__rec_000121::route_003

#### `F3.L3`: Connector-mediated embeddings

A dense carrier that reaches the backbone through a learned connector such as cross-attention, a resampler, a query-former, an adapter layer, or a query connector.

Include when: The route explicitly uses cross-attention, a resampler, a query-former, a query connector, or an adapter.; The biological content is converted to dense tokens before fusion with the backbone.

Exclude when: The route is a fixed virtual-token prefix.; The route is a direct embedding projection without a separate mediator.; The route is a raw image or a discrete biological token stream.

Positive route refs: full_2026-07-06__rec_000771::route_001, full_2026-07-06__rec_000771::route_003, full_2026-07-06__rec_000827::route_001, full_2026-07-06__rec_000827::route_002, full_2026-07-06__rec_000827::route_003, full_2026-07-06__rec_000827::route_004, full_2026-07-06__rec_000827::route_008, full_2026-07-06__rec_000827::route_009, june_update_2026-06-10__rec_000248::route_001, june_update_2026-06-10__rec_000248::route_002, june_update_2026-06-10__rec_000248::route_004, june_update_2026-06-10__rec_000248::route_006

Counterexample route refs: full_2026-07-06__rec_000090::route_001, full_2026-07-06__rec_000086::route_002, full_2026-07-06__rec_000950::route_001, june_update_2026-06-10__rec_000121::route_003

#### `F3.L4`: Pooled or aggregated embeddings

A continuous carrier formed by aggregating multiple inputs into one embedding before model intake, such as averaging selected-cell embeddings or similar pooling operations.

Include when: The route compresses multiple biological items into one embedding before downstream use.; The visible form is a pooled representation rather than a single-source projection.

Exclude when: The route keeps separate tokens for each instance in the prompt.; The route uses raw images, discrete tokens, or a diffusion state.

Positive route refs: full_2026-07-06__rec_000827::route_003

Counterexample route refs: full_2026-07-06__rec_000827::route_001, full_2026-07-06__rec_000090::route_014, full_2026-07-06__rec_000950::route_002, june_update_2026-06-10__rec_000121::route_004

### `F4`: Visual raster carriers

Routes whose visible carrier is an image, patch grid, slide tile, or other rasterized visual carrier processed by a vision encoder or equivalent visual front end.

**Structural criterion:** The source is presented as pixels, patches, or visual tokens rather than language tokens or dense embeddings alone.

#### `F4.L1`: Raw slide or patch input

A histology or similar biomedical image presented directly as a raster image, patch, or patch set to a vision encoder.

Include when: The route starts from a raw image patch or whole-slide image.; The visible carrier is an image tensor or patch grid.

Exclude when: The route is a projected embedding or text prompt.; The route is a diffusion state or discrete biological token stream.

Positive route refs: full_2026-07-06__rec_000060::route_002, full_2026-07-06__rec_000060::route_003, june_update_2026-06-10__rec_000148::route_001, june_update_2026-06-10__rec_000148::route_003, june_update_2026-06-10__rec_000148::route_005, june_update_2026-06-10__rec_000148::route_006, june_update_2026-06-10__rec_000148::route_007, june_update_2026-06-10__rec_000148::route_008, june_update_2026-06-10__rec_000148::route_009, june_update_2026-06-10__rec_000148::route_010, june_update_2026-06-10__rec_000148::route_011, june_update_2026-06-10__rec_000148::route_013, june_update_2026-06-10__rec_000148::route_016, june_update_2026-06-10__rec_000148::route_018, june_update_2026-06-10__rec_000152::route_001, june_update_2026-06-10__rec_000152::route_002

Counterexample route refs: full_2026-07-06__rec_000827::route_008, full_2026-07-06__rec_000086::route_002, full_2026-07-06__rec_000950::route_001, june_update_2026-06-10__rec_000121::route_003

#### `F4.L2`: Patch-context or case-level visual reasoning

A visual route where multiple patches or registered sections are combined into a case-level image context before prediction or reasoning.

Include when: The route uses neighboring patches, serial sections, or case-level visual context.; The visible carrier is still visual, but the unit is a patch set or contextualized slide view.

Exclude when: The route uses only a single raw patch without contextual aggregation.; The route is text-only or embedding-only.

Positive route refs: june_update_2026-06-10__rec_000148::route_015, june_update_2026-06-10__rec_000148::route_017, june_update_2026-06-10__rec_000152::route_004, june_update_2026-06-10__rec_000152::route_005, june_update_2026-06-10__rec_000152::route_006, june_update_2026-06-10__rec_000152::route_007, june_update_2026-06-10__rec_000152::route_008

Counterexample route refs: full_2026-07-06__rec_000060::route_002, full_2026-07-06__rec_000086::route_002, full_2026-07-06__rec_000950::route_002, june_update_2026-06-10__rec_000121::route_003

### `F5`: Geometric and diffusion-state carriers

Routes whose model-visible form is a geometric constraint, coordinate state, or noisy latent state used by a diffusion or structure-generation model. These routes are structurally distinct from ordinary embeddings because the carrier is organized by geometry or diffusion time.

**Structural criterion:** The model-visible carrier is a coordinate, constraint object, or time-indexed noisy latent state rather than a token sequence or patch grid.

#### `F5.L1`: Noisy diffusion state

A time-indexed noisy latent state or training state used directly in a diffusion process.

Include when: The route exposes noisy coordinates or another diffusion-time latent state to the model.; The carrier is part of forward or reverse diffusion dynamics.

Exclude when: The route is a static coordinate constraint or a text prompt.; The route is an image, token stream, or dense embedding prefix.

Positive route refs: full_2026-07-06__rec_000950::route_001, full_2026-07-06__rec_000950::route_011

Counterexample route refs: full_2026-07-06__rec_000950::route_002, full_2026-07-06__rec_000086::route_002, full_2026-07-06__rec_000090::route_001, june_update_2026-06-10__rec_000121::route_003

#### `F5.L2`: Coordinate, backbone, or shape conditioning

A geometric conditioning route in which the model receives coordinates, backbones, substructures, or point-cloud-derived geometry as the visible carrier.

Include when: The route conditions on backbone coordinates, substructures, or point clouds.; The model-visible form is geometric rather than textual.

Exclude when: The route is an abstract symbolic label or a free-form text prompt.; The route is a noisy diffusion state rather than a stable geometric condition.

Positive route refs: full_2026-07-06__rec_000950::route_002, full_2026-07-06__rec_000950::route_004, full_2026-07-06__rec_000950::route_005, full_2026-07-06__rec_000950::route_006, full_2026-07-06__rec_000950::route_007

Counterexample route refs: full_2026-07-06__rec_000950::route_001, full_2026-07-06__rec_000950::route_011, full_2026-07-06__rec_000086::route_003, june_update_2026-06-10__rec_000121::route_003

#### `F5.L3`: Symbolic structural constraints

A non-textual or lightly symbolic structural condition such as symmetry, class labels, or other geometry-level control signals supplied to the generator.

Include when: The route conditions generation with symbolic structural labels or abstract geometry constraints.; The carrier is a constraint signal rather than a language prompt or a dense embedding.

Exclude when: The route is a free-form natural-language caption or question.; The route is a coordinate/backbone carrier or noisy diffusion state.

Positive route refs: full_2026-07-06__rec_000950::route_003, full_2026-07-06__rec_000950::route_008

Counterexample route refs: full_2026-07-06__rec_000950::route_002, full_2026-07-06__rec_000950::route_001, full_2026-07-06__rec_000086::route_010, june_update_2026-06-10__rec_000121::route_003

## Orthogonal dimensions

### `D1`: Biological modality

The underlying source domain, treated separately from carrier mechanism because the same modality can be serialized, embedded, rasterized, or diffused.

Values: text, DNA, RNA, protein/peptide, small molecule, histology/slide image, spatial omics, multi-omic composite, graph/network, mixed

### `D2`: Lifecycle phase

The stage at which the route is used. This prevents training-only targets, generated outputs, baselines, and inference inputs from being conflated.

Values: pretraining, continued pretraining, instruction tuning, supervised fine-tuning, parameter-efficient fine-tuning, fine-tuning, inference, evaluation, generation, training

### `D3`: Text role / route status

The role played by text or symbolic material in the route, independent of the representation mechanism.

Values: actual model input, paired training input, training input, training-only target, generated output, baseline input, auxiliary prompt input, conditioning input, inference input, evaluation input, not used

### `D4`: Fusion topology

How the carrier is inserted into or combined with the generative model. This is orthogonal to the carrier type itself.

Values: direct prompt insertion, prompt prefix, concatenation into unified prompt, projection into latent space, cross-attention, resampler, adapter, retrieval connector, decoder conditioning, classification head, diffusion conditioner, prompt template, placeholder insertion, postprocessing

### `D5`: Source-to-carrier transformation

The dominant transformation applied to the source object before it becomes model-visible.

Values: none/direct, serialization, tokenization, projection, rasterization, aggregation, diffusion/noise process, structural constraint, prompt templating

## Category errors prevented

- Collapsing free-form text prompts, serialized biological sentences, and dense embeddings into one broad bucket.
- Treating biological sequence tokenization as if it were ordinary prose.
- Treating images or slide patches as if they were just another embedding prefix.
- Treating diffusion-time noisy states as if they were static coordinate embeddings.
- Folding training-only targets, generated outputs, baselines, and actual inputs into the same class.
- Using biological source modality as the primary axis when the visible carrier mechanism is the relevant structural criterion.
- Collapsing learned VQ/RVQ/codebook IDs into continuous embeddings or native tokenizer text.

## Unresolved questions

- A few routes combine a prompt with a dense biological carrier; this frozen taxonomy classifies them by the carrier that actually reaches the model and keeps prompt status orthogonal, but some future corpora may need an explicit secondary annotation for the auxiliary prompt.
- Some biological text routes sit near the boundary between structured prompts and serialized biological context; the current split keeps slot-filled task scaffolds separate from sentence-like cell or gene serializations.
- If future corpora add more codebook-based or RVQ-style routes, the learned-quantized-ID leaf may need further subdivision by whether the discrete IDs are used as input symbols, conditioning codes, or reconstruction targets.
