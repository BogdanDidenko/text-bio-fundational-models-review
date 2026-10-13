# Motif library: frequent operation sub-chains (release 1.3.0, 2026-10-14)

A motif is a named, recurring sub-chain of role-aware operations, the next level up from the 22-operation library.
Tokens are `<role>:<operation>`: role B = biological input only, T = text only, X = joins biological and text inputs.
`LM` is an unexpanded learned module and `NOCAT` a computation outside the catalog.
Templates are gapped: other operations may sit between template tokens, unless marked contiguous.
Support is counted in papers (54 papers: 50 agent-decomposed and 4 author-curated pilots). Data: `motifs.json`; mining: `subchains.json`.

## How the motifs were found

1. Release 1.3.0 chains: three-run consensus per step under protocol v3.2. Boundaries are fixed for align, concatenate/serialize and partition/select.
2. Model-level paths (`model_paths.json`): 532 agent routes, plus 314 root-to-receipt paths of the pilot graphs.
   Provenance and identity steps are dropped; repeated identical operations are collapsed; every operation carries the role defined by its inputs.
3. Closed frequent sub-chains are mined at the operation and family levels, contiguous and gapped, with paper-level support of at least 4 papers and no length limit.
   The supported, interpretable patterns were then named (`scripts/build_motif_library.py`).
4. Stability: re-mining from each single decomposition run reproduces the pattern sets with Jaccard 0.808 (operations) and 0.923 (families).
   Per-motif support across the three runs is listed below.

## Main findings

- No sub-chain is shared by all architectures. The most widespread motif (M08, encoder then projector) occurs in 18 of 54 papers.
- 44 of 54 papers contain at least one motif.
  Of the 10 papers without a motif, 5 build their inputs with a single serialise step, which is too short to be a motif;
  the single-step serialise is the most common chain overall. The other 5 use pipelines whose parts are rare in the corpus:
  - InstructCell: projector, then partition, then cross-attention;
  - rec_000950: diffusion conditioning;
  - rec_000194: attention stacks;
  - rec_001343: projections and lookups without a shared encoder;
  - RVQ-Alpha: tokenisers.
- Motifs are archetype-specific building blocks:
  - verbalised-text inputs are built from M01/M02/M04 (subset, rank or sample, then serialise);
  - soft-token, attention-bridge and conditioning inputs from M08-M10 (encoders and projectors);
  - images and long sequences from M07 (tile, then encode).
- Reporting gaps follow the motifs:
  - projector activation is unstated in 82% of M08 projections;
  - concatenation order is unstated in 95% of M13 joins;
  - lookup-table trainability is unstated in 80-88% of M05/M06 lookups;
  - rank tie handling is never stated (M02).

## Library

### Carrier formation

**M01 Subset then verbalise**: `B:select → B:serialize`
- Keep part of the biological record (top genes, fields, cells) and write it as text.
- Support: 10 papers (18%), 17 models, 1 pilot; per single run [11, 10, 10].
- Archetypes of member routes: {'VERB': 32, 'COND': 1}; charted interfaces: {'token_stream': 32, 'conditioning': 1}.
- Unstated parameters: select.criterion 17%, select.forced_inclusions 100%, select.method 28%, serialize.lexical_mapping 24%, serialize.order 74%, serialize.template 24%.
- Example: C2S-Scale (full_2026-07-06__rec_000090): B:select "remove genes expressed in fewer than three cells and cells that express fewer than 100 genes" | B:serialize "convert expression profiles into cell sentences". Evidence: "we preprocess raw scRNA-seq data by removing genes that are expressed in fewer than three cells and cells that express fewer than 100 genes" (sec_0015).
- Models: C2S-Scale, C2S-Scale-Gemma-2-2B, Cell-o1, CellHermes, CellTosg2Sequence, GEMGen, GPT-2 Medium, GPT-2 Small, GPT-4o, GPT-4o-mini, GenNA, Llama3.1-8B-Instruct, Mistral 7B, P3GPT, Qwen2.5-7B-Instruct, o1, o3-mini.

**M02 Ranked gene sentence**: `B:rank → B:serialize`
- Order features by value and write the ordered identifiers as text; magnitudes are dropped.
- Support: 5 papers (9%), 12 models, 1 pilot; per single run [5, 5, 5].
- Archetypes of member routes: {'VERB': 18, 'COND': 1}; charted interfaces: {'token_stream': 18, 'conditioning': 1}.
- Unstated parameters: rank.order 0%, rank.scope 0%, rank.tie_handling 100%, serialize.lexical_mapping 25%, serialize.order 60%, serialize.template 10%.
- Example: CellHermes (full_2026-07-06__rec_001126): B:rank "ranked gene expression values" | B:serialize "serialized into a gene-expression 'sentence'". Evidence: "Next, we ranked the gene expression values for each cell" (sec_0014).
- Models: C2S-Scale-Gemma-2-2B, CellHermes, GEMGen, GPT-2 Medium, GPT-2 Small, GPT-4o, GPT-4o-mini, Llama3.1-8B-Instruct, OpenAI's o1, Qwen2.5-7B-Instruct, o1, o3-mini.

**M03 Expression normalisation**: `B:normalize → B:log_transform` (contiguous)
- Library-size or similar normalisation followed by a log transform of expression values.
- Support: 5 papers (9%), 7 models, 1 pilot; per single run [5, 5, 6].
- Archetypes of member routes: {'VERB': 8, 'XATT': 4}; charted interfaces: {'token_stream': 8, 'attention_bridge': 4}.
- Unstated parameters: log_transform.base 100%, log_transform.method 0%, log_transform.offset 57%, normalize.axes 42%, normalize.method 0%, normalize.scope 42%.
- Example: C2S-Scale (full_2026-07-06__rec_000090): B:normalize "normalize counts to 1 × 10 4 and log-transform" | B:log_transform "normalize counts to 1 × 10 4 and log-transform". Evidence: "followed by normalizing counts to 1 × 10 4 and log-transforming the data" (sec_0015).
- Models: C2S-Scale, CellHermes, GPT-2 Medium, GPT-2 Small, X-Cell, X-Cell-Ultra, scMOBA.

**M04 Sample then verbalise**: `B:sample → B:serialize`
- Randomly draw cells, examples or negatives and write them into text.
- Support: 4 papers (7%), 5 models, 0 pilot; per single run [4, 4, 4].
- Archetypes of member routes: {'VERB': 8}; charted interfaces: {'token_stream': 8}.
- Unstated parameters: sample.distribution 75%, sample.method 38%, sample.origin 12%, sample.temperature 100%, serialize.lexical_mapping 22%, serialize.order 44%, serialize.template 33%.
- Example: C2S-Scale (full_2026-07-06__rec_000090): B:sample "sample multiple cells from the same donor sample" | B:serialize "convert each cell into a cell sentence". Evidence: "For multi-cell tasks, multiple cells are sampled from the same donor sample with the same tissue label." (sec_0023).
- Models: C2S-Scale, GPT-2 Medium, GPT-2 Small, OmniGene-4, OpenAI's o1.

**M05 Biological alphabet embedding**: `B:tokenize → B:lookup`
- Tokenise a sequence in its own alphabet and look the tokens up in an embedding table.
- Support: 5 papers (9%), 5 models, 0 pilot; per single run [5, 5, 5].
- Archetypes of member routes: {'XATT': 1, 'SOFT': 1, 'TOOL': 1, 'VERB': 1, 'SYMB': 1}; charted interfaces: {'attention_bridge': 1, 'embedding_slot': 1, 'external_context': 1, 'token_stream': 2}.
- Unstated parameters: lookup.key_space 40%, lookup.resource_kind 20%, lookup.trainability 80%, tokenize.segmentation 0%, tokenize.source_alphabet 0%, tokenize.vocabulary 0%.
- Example: BioGPT (full_2026-07-06__rec_001519): B:tokenize "tokenized into overlapping k-mers" | B:lookup "independently embedded". Evidence: "Genomic sequences are tokenized into k-mers:" (sec_0009).
- Models: BioGPT, CaLMFlow, OmniNA, gpt2-gene-eng-ft, scGPT-FT.

**M06 Text token embedding**: `T:tokenize → T:lookup`
- Standard text channel: tokenise text and look the tokens up in the language model's embedding table.
- Support: 6 papers (11%), 7 models, 1 pilot; per single run [6, 6, 6].
- Archetypes of member routes: {'TEXT': 8}; charted interfaces: {'attention_bridge': 1, 'embedding_slot': 1, 'token_stream': 6}.
- Unstated parameters: lookup.key_space 38%, lookup.resource_kind 12%, lookup.trainability 88%, tokenize.segmentation 12%, tokenize.source_alphabet 0%, tokenize.vocabulary 25%.
- Example: BioGPT (full_2026-07-06__rec_001519): T:tokenize "encoded using Byte Pair Encoding (BPE)" | T:lookup "independently embedded". Evidence: "Clinical text is processed using byte pair encoding (BPE):" (sec_0009).
- Models: BioGPT, CaLMFlow, ChatNT: Nucleotide Transformer v2 + English-aware Perceiver + Vicuna-7b, ChatNT: Nucleotide Transformer v2 + unconditioned Perceiver + Vicuna-7b, OmicsLM, OmniNA, Qwen3.

**M07 Tile then encode**: `B:partition → B:LM`
- Split an image, genome or sequence into patches/windows/chunks and encode them with a learned module.
- Support: 7 papers (13%), 8 models, 1 pilot; per single run [8, 6, 7].
- Archetypes of member routes: {'SOFT': 13, 'SYMB': 1, 'UNRES': 2, 'COND': 4}; charted interfaces: {'embedding_slot': 13, 'token_stream': 1, 'unresolved': 2, 'conditioning': 4}.
- Unstated parameters: partition.axis 25%, partition.method 20%, partition.partition_rule 20%.
- Example: ALTER (full_2026-07-06__rec_001218): B:partition "decompose W into non-overlapping patches" | B:LM "extract patch features with UNI". Evidence: "we first decompose W into non-overlapping patches { p 1 , p 2 , . . . , p N h }" (sec_0006).
- Models: ALTER, MUPAD ORION mIF dual H&E conditioning, MUPAD ST-conditioned histology, OpticalDNA, Qwen3, TeamPath-7B, gene_eng_gpt2_para_seg, in-house DINO-V2-based histopathology FM.

### Encoding

**M08 Encoder then projector**: `B:LM → B:project`
- A learned (often pretrained, frozen) biological encoder followed by a projection into the receiving model's space.
- Support: 18 papers (33%), 23 models, 1 pilot; per single run [18, 17, 18].
- Archetypes of member routes: {'SOFT': 32, 'ALIGN': 7, 'VERB': 1, 'COND': 8, 'XATT': 12}; charted interfaces: {'embedding_slot': 32, 'latent_alignment': 7, 'token_stream': 1, 'conditioning': 8, 'attention_bridge': 12}.
- Unstated parameters: project.activation 82%, project.method 23%, project.parameter_state 16%.
- Example: BioMedGPT-10B (full_2026-07-06__rec_003214): B:LM "encode with GraphMVP" | B:project "project with an independent modality adaptor". Evidence: "The molecule encoder is a 5-layer GIN [Xu et al., 2018] with 1.8M parameters pre-trained by GraphMVP [Liu et al., 2022], which shows promising results in comprehending 2D molecular graphs." (sec_0007).
- Models: BIOVERSE, BioMedGPT-10B, C2S-Scale perturbation model, Cell2Text, Cell2Text-Gemma-4B, Cell2Text-Llama-1B, Cell2Text-Llama-1B-LoRA, CellTosg2Sequence, LEONINE, LEONINE-GPT-2, Mistral 7B, OCellus-GNN, OpticalDNA, P3GPT, PROCYON-SPLIT, Qwen3, Qwen3-1.7B, Qwen3-1.7B and Qwen3-4B, Qwen3-1.7B and Qwen3-4B-Thinking, Qwen3-1.7B, Qwen3-4B, and Gemma 4 E2B, SciCore-Omics, X-Cell-Ultra, scMOBA.

**M09 Projector into the model**: `B:LM → B:project → B:LM`
- Encoder output projected and then consumed by another learned module (typically the language model).
- Support: 6 papers (11%), 8 models, 1 pilot; per single run [6, 6, 6].
- Archetypes of member routes: {'SOFT': 12, 'COND': 3, 'XATT': 12}; charted interfaces: {'embedding_slot': 12, 'conditioning': 3, 'attention_bridge': 12}.
- Unstated parameters: project.activation 100%, project.method 22%, project.parameter_state 7%.
- Example: BioMedGPT-10B (full_2026-07-06__rec_003214): B:LM "encode protein sequences with ESM-2-3B" | B:project "project with an independent modality adaptor" | B:LM "align to the feature space of BioMedGPT-LM-7B". Evidence: "The protein encoder is ESM-2-3B [Lin et al., 2022], a 36-layer transformer [Vaswani et al., 2023] specialized in processing protein sequences." (sec_0007).
- Models: BioMedGPT-10B, Cell2Text-Gemma-4B, Cell2Text-Llama-1B, Cell2Text-Llama-1B-LoRA, OpticalDNA, Qwen3, X-Cell-Ultra, scMOBA.

**M10 Stacked learned modules**: `B:LM → B:LM`
- Two or more unexpanded learned modules in sequence (e.g. frozen foundation model then trainable encoder).
- Support: 12 papers (22%), 14 models, 1 pilot; per single run [12, 11, 12].
- Archetypes of member routes: {'SOFT': 19, 'COND': 8, 'TOOL': 1, 'XATT': 14}; charted interfaces: {'embedding_slot': 19, 'conditioning': 8, 'external_context': 1, 'attention_bridge': 14}.
- Unstated parameters: n/a (boundary steps).
- Example: ALTER (full_2026-07-06__rec_001218): B:LM "extract patch features with UNI" | B:LM "modality-specific decoupling". Evidence: "Each patch is then processed using a pretrained feature extractor Θ . In this study, we adopt UNI [6], a foundation model for computational pathology, as the extractor." (sec_0006).
- Models: ALTER, BioMedGPT-10B, Cell2Text-Gemma-4B, Cell2Text-Llama-1B, Cell2Text-Llama-1B-LoRA, H2O, OCellus-Agent, OpticalDNA, Qwen3, TissueCraftAI, X-Cell-Ultra, scMIR, scMMGPT, scMOBA.

**M11 Domain computation then encoder**: `B:NOCAT → B:LM`
- A computation outside the operation catalog (graph convolution, physics terms, clustering) before a learned encoder.
- Support: 10 papers (18%), 10 models, 0 pilot; per single run [9, 9, 9].
- Archetypes of member routes: {'SOFT': 2, 'COND': 8, 'TOOL': 1, 'SYMB': 1, 'XATT': 1, 'UNRES': 1}; charted interfaces: {'embedding_slot': 2, 'conditioning': 8, 'external_context': 1, 'token_stream': 1, 'attention_bridge': 1, 'unresolved': 1}.
- Unstated parameters: n/a (boundary steps).
- Example: BioMedGPT-10B (full_2026-07-06__rec_003214): B:NOCAT "generate 2D molecular graphs" | B:LM "encode with GraphMVP". Evidence: "We remove molecules that cannot be processed by RDKit [Landrum et al., 2021] to generate 2D molecular graphs." (sec_0007).
- Models: BioMedGPT-10B, CellTosg2Sequence, H2O, OCellus-Agent, OmniNA-1.7B, Shusi, TeamPath-7B, XunZi-M, scMOBA, text LLM.

### Joining

**M12 Verbalised biology read by a model**: `B:serialize → B:LM`
- Biology written as text and consumed by a learned language model.
- Support: 9 papers (17%), 17 models, 0 pilot; per single run [9, 6, 8].
- Archetypes of member routes: {'COND': 3, 'VERB': 12, 'SOFT': 9}; charted interfaces: {'conditioning': 3, 'token_stream': 12, 'embedding_slot': 9}.
- Unstated parameters: serialize.lexical_mapping 4%, serialize.order 17%, serialize.template 4%.
- Example: Cell2Text-Gemma-4B (full_2026-07-06__rec_001838): B:serialize "instruction-following prompt structure" | B:LM "Gemma3-4B-it decoder". Evidence: "we adopted a specific instruction-following prompt structure that integrates a system message and the contextualized gene embeddings:" (sec_0013).
- Models: Cell2Text-Gemma-4B, Cell2Text-Llama-1B, Cell2Text-Llama-1B-LoRA, GPT-4o, GPT-4o-mini, Llama3.1-8B-Instruct, Med-PaLM M, OCellus, Omni-DNA, OmniNA, OpticalDNA, Qwen2.5-7B-Instruct, Qwen3-1.7B, Qwen3-1.7B and Qwen3-4B, TISSUENARRATOR, o1, o3-mini.

**M13 Encode then join**: `B:LM → B:concatenate`
- Encoded biological representation concatenated with other inputs (text tokens, [CLS], other modalities).
- Support: 6 papers (11%), 6 models, 2 pilot; per single run [6, 7, 7].
- Archetypes of member routes: {'SOFT': 6, 'COND': 1, 'XATT': 12}; charted interfaces: {'embedding_slot': 6, 'conditioning': 1, 'attention_bridge': 12}.
- Unstated parameters: concatenate.axis 74%, concatenate.order 95%.
- Example: ALTER (full_2026-07-06__rec_001218): B:LM "extract patch features with UNI" | B:concatenate "concatenate with the [CLS] token". Evidence: "Each patch is then processed using a pretrained feature extractor Θ . In this study, we adopt UNI [6], a foundation model for computational pathology, as the extractor." (sec_0006).
- Models: ALTER, H2O, MUPAD ORION mIF dual H&E conditioning, Shusi, X-Cell-Ultra, scMOBA.

**M14 Encode then add**: `B:LM → B:add`
- Encoded representation summed with another representation (positional, prior or other modality).
- Support: 5 papers (9%), 5 models, 0 pilot; per single run [5, 5, 5].
- Archetypes of member routes: {'SOFT': 9, 'UNRES': 1, 'COND': 1}; charted interfaces: {'embedding_slot': 9, 'unresolved': 1, 'conditioning': 1}.
- Unstated parameters: add.alignment 27%, add.scaling 27%.
- Example: ALTER (full_2026-07-06__rec_001218): B:LM "extract patch features with UNI" | B:add "region-wise aggregation". Evidence: "Each patch is then processed using a pretrained feature extractor Θ . In this study, we adopt UNI [6], a foundation model for computational pathology, as the extractor." (sec_0006).
- Models: ALTER, BIOVERSE, CellHermes, Genolator, OCellus-GNN.

**M15 Text tokens into the model**: `T:tokenize → T:LM`
- Tokenised text read by a learned module.
- Support: 7 papers (13%), 9 models, 1 pilot; per single run [7, 7, 7].
- Archetypes of member routes: {'TEXT': 14}; charted interfaces: {'token_stream': 12, 'embedding_slot': 1, 'attention_bridge': 1}.
- Unstated parameters: tokenize.segmentation 56%, tokenize.source_alphabet 0%, tokenize.vocabulary 56%.
- Example: ALTER (full_2026-07-06__rec_001218): T:tokenize "tokenize R into a sequence T" | T:LM "use BioBERT as text encoder". Evidence: "tokenize R into a sequence T ∈ R N t" (sec_0006).
- Models: ALTER, ChatNT: Nucleotide Transformer v2 + English-aware Perceiver + Vicuna-7b, ChatNT: Nucleotide Transformer v2 + unconditioned Perceiver + Vicuna-7b, Qwen3, TeamPath-7B, XunZi-R, o4-mini, scMMGPT, scMOBA.
