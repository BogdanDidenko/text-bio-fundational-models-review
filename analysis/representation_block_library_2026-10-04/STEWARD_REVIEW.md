# Steward Review: Representation Block Library 0.1.0

## Status and Ownership

This release is a source-backed development candidate for InstructCell, ChatNT, MUPAD and X-Cell. The input inventory contains four record IDs and 47 reviewed trajectories, including task/phase variants, ablations, auxiliary boundaries and the C2S baseline within the X-Cell record. These trajectories are supervised reconstructions with visible uncertainty. The library provides reusable candidate types and motifs; scientific validation of the complete architectures remains open.

The seed contains 91 blocks: 34 representation types, 29 operation types, 20 functional component types and eight composite motifs. It contains 117 explicit exact-label mappings and 18 steward decisions. Every block has a source example. Mappings cover reviewed semantic boundaries; other labels remain available to the builder as extension proposals.

Steward ownership is confined to catalog_seed.json and this review. The pilot, selected sections, schemas, builder, Pages assets and canonical taxonomy are untouched by this work. No new LLM or Docling call, provider endpoint or canonical migration was performed.

## Existing Mechanisms

The current symbolic_trajectories.py contract distinguishes representation nodes, transformations, operand port roles, receiving components and lifecycle contexts. The coordinator's representation_library.py adds typed block definitions, exact mappings, source example references and explicit unresolved bindings.

The official [Pydantic model documentation](https://docs.pydantic.dev/latest/concepts/models/) supports BaseModel-based typed validation and explicit extra-field policies. The existing CatalogSeed contract is reused through model_validate_json; its inherited extra="forbid" policy remains intact. No alternate validator, proxy, wrapper or rendering mechanism is introduced. Static Pages compilation stays with the coordinator's existing builder.

The strict ExampleRef contract has element IDs and a rationale, with no dedicated binding field. Composite examples therefore store ordered real step IDs in element_ids and full step-to-port/library bindings in rationale. Builder-expanded examples retain the unchanged historical steps and their evidence. A future structured binding field would require a coordinator-owned schema decision.

## Type and Instance Rules

A representation block describes information semantics and admissible symbolic axes. Its source node supplies actual shape symbols, axis meanings, information content, contextual role, evidence and uncertainty. A type binding supplies no assertion of identical tensors or shared parameter values across trajectories.

Unavailable internals are instance-level evidence uncertainty. They supply no reusable physical representation form. Coordinator review removed representation.unresolved_condition_boundary; the original RNA boundary instance and its unresolved producer linkage remain unchanged.

Operation types describe transformations and functional port roles. Concrete linear projection, dense-network projection and source-specific nonlinear MLP projection can specialize the general feature-projection boundary. Their activation, normalization and architecture declarations remain distinct. No exact-synonym aliases were established; alias arrays are empty.

Components describe functional module boundaries. Exact historical step.component or recipient labels select the reviewed mappings. Each use retains its original component name, architecture variant, lifecycle phase and uncertainty. Functional compatibility establishes no shared parameter identity.

Composite composition arrays list constituent types in pedagogical motifs, including parallel branches. Render these constituent types without sequential arrows: array order supplies no sequential dependency. Source examples carry real ordered step IDs and their bindings, including null library bindings for unresolved operations/components. Parallel branches keep their original operand edges. Mechanism quotations support the reconstruction; formal graph-structure proof and cross-context identity require separate evidence.

Numeric architecture widths are absent from block definitions. Original source elements and quotations preserve the paper's reported values unchanged. Symbolic axes distinguish token positions, gene identities, biological pathways, learned query parameter slots, updated output slots, modality/prior-source positions, learned coordinates, cells and spatial regions. Unknown layout remains unknown.

## Source Evidence and Boundaries

Source root:
`/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/analysis/nickerson_taxonomy_2026-09-20/object_unit_reassessment_2026-09-22/section_id_corpus_55_2026-10-04/records`

Pilot:
`/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/analysis/nickerson_taxonomy_2026-09-20/object_unit_reassessment_2026-09-22/symbolic_trajectory_supervised_2026-10-04/trajectories.reviewed.jsonl`

### InstructCell: full_2026-07-06__rec_001319

- sec_0020: "All input embeddings, whether derived from text tokens or single cells, are then concatenated in sequence". This supports ordered embedding assembly; the full node/step quotations preserve the surrounding description.
- sec_0021: "a multi-layer perceptron (MLP) that encodes raw input cells into keys and values". The profile-to-slot encoder produces abstract latent slots. Initial learned query parameters and computed cell features retain separate representation types.
- sec_0021: "the query vectors first interact with each other through a self-attention layer". The complete step evidence also documents the subsequent cross-attention to U and repeated stack. The library keeps the stack aggregate.
- sec_0022: "During training, the encoder encodes the current condition c and the corresponding single-cell s to produce a posterior distribution." Posterior parameters, base random noise and realized latent operands have distinct roles.
- sec_0025: "The resulting output serves as a conditioning vector for the cell reconstruction module." The fully connected layer specializes general feature projection.

Remaining source issues: separate z_s and ell posterior samples retain distinct decoder ports. sec_0022 identifies a Gaussian z_s prior and a separate log-normal ell prior; sec_0005 describes inference sampling conditioned on the LM state. Their precise reconciliation, ell inference receipt, latent-specific sampling equations and decoder packing remain unresolved. The LM SIGNAL hidden-state producer is preserved as a historical aggregate; broad hidden_state and conditioning_vector labels remain globally unmapped.

### ChatNT: full_2026-07-06__rec_000771

- sec_0013: "each DNA sequence is processed independently by the DNA encoder". Independent processing supplies no evidence of shared versus separate learnable query collections.
- sec_0013: "an additional cross-attention step between the learnable queries and the English question". This supports a question-aware resampling boundary. The exact question representation and port in the pilot remain provisional.
- sec_0013: "inserted in place of the DNA sequence placeholder tokens". Placeholder substitution retains sequence-to-placeholder correspondence.
- sec_0005: "independently of the question asked". This describes the classical resampler variant and motivates a distinct source-only operation/component boundary.

The label resampled_nucleotide_embeddings is shared across question-conditioned and source-only variants. It receives no global mapping. Each variant has a source-backed representation example with its own question-dependence boundary. Initial query parameter slots and output resampling slots retain independent cardinalities. The unresolved multi-sequence query collection remains unmapped.

The fine-tuning example supports the documented prompt-side boundary. Answer-prefix/teacher-forcing serialization, turn delimiters, role/system tokens and masks remain unresolved. Vocabulary probabilities, sampled token values and attention cache are separate types in inference.

### MUPAD: full_2026-07-06__rec_003852

- sec_0016: "pathway-level enrichment scores using established pan-cancer gene signatures". Biological pathway axes remain distinct from learned feature coordinates.
- sec_0017: "independent parallel attention streams, all queried by the intermediate image representation". This supports whole-stream modality boundaries with a shared image-query role; missing equations preserve unresolved internal projections and gates.
- sec_0013: "fusing modality-specific contributions additively before the subsequent feed-forward block". Additive fusion preserves its declared receiving boundary.
- sec_0017: "Images are encoded into latents via a frozen VAE". This supports a VAE encoding branch separately from MUSK semantic condition encoding.
- sec_0023: "spatial concatenation of the H&amp;E VAE latent". The complete passage also documents semantic cross-attention using MUSK patch embeddings and independently encoded marker subsets.

The pathway_scores to rna_attention_condition conversion is an explicit gap. No learned RNA projection, attention-ready key/value representation or connecting edge is manufactured. The retained boundary example is node rna_attention_condition in full_2026-07-06__rec_003852 / pretrain_multimodal_dca, consumed by attend_rna at port rna_stream_condition_boundary. Its original node, evidence, uncertainty and operand binding remain unchanged and globally unmapped. Unavailable RNA condition internals remain uncertainty on this instance. Decision D10 preserves the rationale and references the pathway-score representation, modality-stream operation/component and parallel-fusion composite.

Clean VAE latents, current noisy marker states and MUSK semantic embeddings retain distinct roles. The dual-conditioning motif includes the actual structure/semantic/concat_t steps and preserves the noisy-state boundary input. Augmentation branch placement, noising/interpolant producer, concatenation axis, sampling updates, independent subset decoding and inference persistence remain unresolved. Shared-attention ablation, DDIM attention injection and IHC continuous-flow translation remain separate pilot material with pending library review.

### X-Cell: full_2026-07-06__rec_003517

- sec_0014: "projecting the scalar expression value through a two-layer MLP with ReLU activation and LayerNorm". Identity, value and reveal status remain separately computed contributions.
- sec_0049: "The binary perturbation mask is embedded through a learned embedding table followed by LayerNorm". Gene-position reveal semantics differ from prior-source availability.
- sec_0050: "independent of gene, value, and mask encoders". The initial learned CLS parameter and final computed cell summary have separate roles.
- sec_0051: "flagged via a boolean mask" and "passed as key padding mask to cross-attention". Context-source positions retain their alignment with availability flags.
- sec_0056: "raw (un-normalized) gene embeddings shared with the encoder". Indexed output rows retain raw parameter provenance; normalized sample identity features remain separate.
- sec_0014: "Previously revealed predictions remain fixed". Cumulative updates preserve earlier accepted values.
- sec_0072: "as the final prediction". The algorithm returns its terminal full-profile prediction; accumulated feedback state retains a separate identity.
- sec_0075: "bypassing all 11 cross-attention blocks". TTA bypasses prior attention and freezes its parameters. The independent second NTC set supplies loss-side supervision; the generative receipt contains the control input and zero reveal status.

The identity/value/mask combiner remains an opaque aggregate because its equation is absent from selected text. The source-specific prior context motif preserves every loading, availability, projection and assembly step, including the learned gene condition with unresolved internals. Missingness follows source availability; a valid zero-valued feature supplies no missingness proof.

X-Cell and Ultra architecture variants remain separate historical components. Scalar and tied output-head receipts remain unmapped pending review of missing equations and divergent source scaling wording. Cumulative inference and single-step TTA retain distinct contexts. Post-TTA inference re-enables prior attention under the adapted checkpoint.

## Remaining Library Design Decisions

1. Context-aware bindings: the seed contract supports global exact labels. Context-dependent resampled features use examples without global mappings. Future context-aware binding support belongs to the coordinator and requires source-backed rules.
2. Normalized roles: input_roles/output_roles are descriptive type roles. Original port_role strings remain authoritative instance bindings; no automatic role-renaming migration is introduced.
3. Identity links: shared parameters, repeated computations and same-value links require explicit scientific evidence. Library type reuse supplies none of these links.
4. Composite matching: the documented motifs are exemplars. Automatic subgraph recognition and formal structure validation remain outside this seed. Missing edges and opaque aggregate operations survive unchanged.
5. Alias review: no alias equivalence is asserted. New aliases require matching semantic, role and boundary evidence.
6. Long-tail review: tokenizer recipes, dataset filtering/normalization and collation, training-mask selection, generic hidden/generative states, RNA embeddings, inversion, IHC translation, architecture internals and C2S baseline labels remain proposals unless explicitly mapped. No source label is forced into a convenient broad block to increase coverage.
7. Cohort extension: global exact-label mappings are scoped to the four pilot records and are not transferable automatically beyond them. Each additional record requires fresh source-backed semantic and context-collision review before applying the same release mappings.
8. Source entailment: literal quotation matching and schema validation are mechanical checks. Source entailment, unresolved equations, phase availability and complete biological interpretation remain scientific review responsibilities.

## Verification and Scope

The complete JSONL was loaded intact using standard JSON parsing. Source examples resolve against the original record/trajectory/element IDs. Referenced selected section bodies are read intact and quotations checked for literal containment. Original pilot elements remain the builder's evidence source.

The initial seed passed the existing CatalogSeed model with 129 example references and 241 matched quotation occurrences. Coordinator review removed the unresolved-condition candidate block and its library-only references, retaining all original source evidence. Revised validation is recorded below. Every composite example follows its actual pilot step order, and every noncomposite has an empty composition array. Exact-label inventory leaves 85 representation labels, 42 operation labels and 65 component labels unmapped, yielding 192 distinct extension-review labels. The context-dependent resampled_nucleotide_embeddings label remains unmapped.

The revised seed passes CatalogSeed validation with 128 source examples and 238 literal quotation matches across the same 28 complete selected section bodies. The RNA instance and its actual attend_rna operand are present; the score-to-condition producer gap remains open. Read-only invocation of the coordinator's existing compile_release passes assembly validation and lossless round trips for all four records and 47 trajectories, retaining 89 unique evidence entries and 192 extension proposals. No generated artifacts were written during this check.

The terminal display imposed an output limit during exploratory reads. The original files were preserved; no source document or field was size-modified. Subsequent reads selected fields and motifs by scientific role and source identity, with complete selected section bodies and complete referenced pilot elements retained for validation.

The system Python's Pydantic core has an architecture mismatch. The existing review/.venv-docling runtime successfully imports Pydantic and is used for the coordinator's unmodified CatalogSeed validation. No dependency installation or runtime patch is needed.

Only the two steward-owned files are authored. Generated release artifacts, static Pages publication, broader pilot extension and canonical migration remain coordinator-owned work.

Pages QA and generated release publication remain with the coordinator. Steward verification uses the existing release compiler in memory and validates the seed, source references and quotations without writing generated artifacts outside the ownership boundary.
