# Operation parameter glossary (parameter pass, 2026-10-13)

One line per declared parameter: what a stated value answers. A value is **stated** only if the paper
text (any section, appendix, table or caption) states it for this data path. Naming a specific
resource counts ("the Llama-3 tokenizer" states the tokenizer vocabulary). A value that would only
follow from convention, code or a cited paper is **unspecified**.

| operation | parameter | stated value answers |
|---|---|---|
| normalize | method | which normalisation (library-size/CP10K, TPM, z-score, min-max, LayerNorm, L2 ...) |
| normalize | axes | over which axis or axes it is computed (per cell, per gene, per feature, per token ...) |
| normalize | scope | over which population the statistics are taken (each sample, whole dataset, training set ...) |
| log_transform | method | which transform (log, log1p ...) |
| log_transform | offset | the pseudocount added before the log (e.g. 1) |
| log_transform | base | the logarithm base (e, 2, 10) |
| bin | strategy | how bins are formed (equal-width, quantile, fixed thresholds, named levels ...) |
| bin | scope | over which population bins are computed (per cell, per gene, global) |
| bin | zero_handling | how zero values are treated (own bin, excluded ...) |
| bin | bin_edges | the number of bins or the explicit edges/levels |
| tokenize | vocabulary | which vocabulary or tokenizer (named tokenizer, gene-symbol vocabulary, k-mer set, codebook size ...) |
| tokenize | segmentation | how input is split into tokens (BPE, WordPiece, k-mer length and stride, one token per gene/residue/nucleotide ...) |
| tokenize | source_alphabet | the units being tokenised (natural-language text, gene symbols, amino acids, nucleotides, SMILES ...) |
| lookup | key_space | what the keys index (token ids, gene ids, value bins, positions ...) |
| lookup | resource_kind | what the table is (learned embedding matrix, pretrained embedding table, fixed feature table ...) |
| lookup | trainability | whether the table is trained, frozen or fine-tuned in this phase |
| project | method | the mapping (linear layer, n-layer MLP, convolutional or other learned projection) |
| project | activation | the nonlinearity (GELU, ReLU, none ...) |
| project | parameter_state | whether the projection weights are trained, frozen or fine-tuned in this phase |
| concatenate | axis | along which axis inputs are joined (sequence/token axis, feature axis, channel axis) |
| concatenate | order | the order of the joined parts (e.g. "[cell tokens] then [text tokens]") |
| partition | method | how the split is made (fixed windows, patches, chunks, groups by label ...) |
| partition | axis | which axis is split (sequence, spatial, cells ...) |
| partition | partition_rule | the size or rule (window length, patch size, grouping key ...) |
| select | criterion | what decides inclusion (highest expression, HVG, QC threshold, label ...) |
| select | method | how it is applied (top-k with k, threshold value, random subset of size n ...) |
| select | forced_inclusions | items always kept regardless of the criterion |
| rank | order | the direction (descending/ascending by what value) |
| rank | tie_handling | how ties are ordered |
| rank | scope | within what the ranking is done (per cell, per sample, dataset) |
| serialize | template | the text pattern or format (quoted template, "gene names separated by spaces", JSON fields ...) |
| serialize | order | the order of fields or items in the text |
| serialize | lexical_mapping | how values are rendered as words (symbols, numbers with k decimals, value words like "high" ...) |
| pad | side | where padding is added (left, right) |
| pad | value | the padding token or value |
| pad | target_length | the fixed length (maximum tokens, characters, base pairs) |
| add | alignment | which elements are summed with which (position-wise, per gene ...) |
| add | scaling | weights or scaling applied (weighted by expression, mean, sum ...) |
| sample | method | the sampling procedure (uniform random, nucleus, diffusion sampler, negative sampling ...) |
| sample | distribution | the distribution sampled from (Gaussian noise, model posterior, empirical pool ...) |
| sample | temperature | the temperature or equivalent control value |
| sample | origin | where the samples come from (prior, posterior, data pool, other cells ...) |
| cross_attention | method | the module (Q-Former, Perceiver resampler, cross-attention layers, number of queries/layers) |
| cross_attention | mask_semantics | which positions may attend to which |
| cross_attention | parameter_state | whether the module is trained, frozen or fine-tuned in this phase |
| self_attention | mask_semantics | the attention mask (causal, bidirectional, block ...) |
| self_attention | repeat_schedule | the number of layers or repetitions |
| impute | replacement | what replaces missing values (zero, mean, learned token ...) |
| impute | availability_source | how missingness is determined |
| clamp | lower | the lower bound |
| clamp | upper | the upper bound |
| update | method | what the update does (mask with [MASK], replace placeholder with embedding, overwrite ...) |
| update | preserve_unselected | whether positions not updated are kept unchanged |
| align | basis | what items are matched on (shared cell id, spatial coordinates, pairing in data ...) |
| align | method | how matching is done (exact id match, nearest neighbour, registration ...) |
| augment | policy | which perturbation (noise type and size, masking rate, cropping ...) |
| augment | phase | when it is applied (training only, also inference) |
| reshape | method | the rearrangement (flatten, reshape, broadcast ...) |
| reshape | axes | the input and output axes |
