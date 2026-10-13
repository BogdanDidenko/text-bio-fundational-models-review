
## full_2026-07-06__rec_000090
- 3 Cell embedding  Task Setup and Datasets To evaluate the quality of learned representations without task-specific fine-tuning, we benchmarked models on the Immune 1 , Pancreas , and Lung datasets, utilizing the identical train/test splits described in Section 4.

## full_2026-07-06__rec_000827
- - **d**: Violin/strip plot showing number of papers per gene versus expression enrichment groups for the “heart” query, highlighting “26 new marker genes.

## full_2026-07-06__rec_000950
- Importantly, these structures are unique with respect to the PDB, with the top PDB hit to UNC\_079 (PDB entry 4NH2, chain E) having query and target TM scores of 0.
- 3, respectively, and the top hit to UNC\_239 (PDB entry 6AFV, chain A) having query and target TM scores of 0.

## full_2026-07-06__rec_001074
- Concurrently, the user's tokenized query Q TEXT = ( w 1 , .

## full_2026-07-06__rec_001319
- Furthermore, since the Q-Former's query embeddings aggregate information via attention mechanisms, we explore how varying the number of queries (1, 2, 4, 8, and 16) affects performance.
- ### Q-Former module  The Q-Former module comprises three primary components: a set of learnable d -dimensional query vectors Q (0) = ( q 1 , q 2 , · · · , q k ), a multi-layer perceptron (MLP) that encodes raw input cells into keys and values, and a transformer model [49] that connects the outputs of the MLP to the query vectors.
- For the Q-Former module, L cell is set to 4, the number of query tokens k is 8, and the number of key-value pairs t is 6.

## full_2026-07-06__rec_001381
- - The cell-to-text projector is implemented with a Query Transformer (Q-Former) [33] with 32 learnable queries, which maps high-dimensional cell embeddings from the scLLM into the token embedding space of the Text LLM.

## full_2026-07-06__rec_002105
- - The trained CellWhisperer model can be prompted with free-text queries to search for transcriptomes that 115 match the search query.

## full_2026-07-06__rec_002304
- As a result, Genolator can address both  open-ended  queries  (see  Figure  1)  and  confirmatory  or  denial  questions  (see  Figure  2) relating to genome functionality.
- For  model  input,  each  embedding  modality  was  mapped  to  8  virtual  tokens  of  size  4096.

## full_2026-07-06__rec_003323
- Supervised finetuning (SFT), which collects paired data with images and queries as inputs and answers as outputs; 2.

## full_2026-07-06__rec_003517
- 4 Cell Embedding and Decoder  The CLS token output h CLS = H ( L ) 0 ∈ R d serves as a cell-level embedding.

## july_update_2026-07-06__rec_000060
- Each prompt has four blocks: (1) KG virtual tokens [KG\_VT] : one virtual token per input gene (block length K =200 ), aligned one-to-one with the Cell Sentence; (2) Biological metadata [Meta] : short natural-language fields (tissue, compartment, disease, optional KG triples); (3) Cell Sentence [CellSentence] : the ranked gene list as HGNC symbols; (4) Task instruction [Task] : one short line specifying the output format.
- The K =200 virtual tokens are length-matched to the cell sentence - the i -th virtual token carries graph context for exactly the i -th ranked gene - and prepended to the textual prompt, separated by a single learnable [KG\_SEP] token.
- Positional encodings assign indices 1-200 to the KG virtual tokens and 201+ to the textual tokens; this is consistent with established prefix-tuning and soft-prompt practice [Liu et al.
- Transformation of node vectors into projector MLP virtual tokens matching LLM dimension, with dimensions labeled 256, 1024, GELU, 2048, GELU, and output 4096 virtual tokens.
- The '32B LoRA (no KG)' baseline (same backbone, same LoRA config, no virtual tokens) further confirms this: it achieves 0.

## june_update_2026-06-10__rec_000133
- The attention module used grouped query attention (GQA) 49 ,  with 32 query heads and 8 key/value heads.

## june_update_2026-06-10__rec_000194
- It does so via a set of K learnable query vectors Q = { q k } K k =1 , which are randomly initialized and updated during training.
- At each forward pass the meta-query tokens and the tokenised instruction are concatenated into a single sequence; the query tokens cross-attend with both the instruction tokens and self-attend with each other (mimicking the InstructBLIP concatenation trick), and cross-attend to the layer-normalised Stage 1 visual tokens every two transformer layers.
- The Alphagenome Q-former has 32 query vectors, while the GenePT Q-former and ESM Q-former are trained with 8 query vectors each.

## update_2026-08-09__rec_000106
- In our implementation, we use 32 learnable query embeddings, each with a hidden dimension of 768.
- The  compact  query  outputs  (32  ×  768)  act  as  a  bottleneck,  focusing representation  capacity  on  semantically  informative  visual  content  while  reducing computational cost.
- The masked features are input into the QFormer to produce query embeddings 𝑍 DEAFG# ∈ ℝ 0×H×B " , where 𝑄 is the number of learnable queries and 𝐷 I is the hidden dimension of the Q-Former.
- The Q-Former outputs a fixed set of 32 query embeddings for each image,  each  with  a dimensionality  of  768.
- To  obtain  a  compact  image-level representation, we compute the mean of the query embeddings, resulting in a single 768-dimensional  feature  vector  per  image.
- For each query treatment, a 2 × 2 contingency table is constructed by counting treatments with the same versus different mechanisms of action or pathways above and below a predefined similarity threshold (top 1%).

## update_2026-08-09__rec_000138
- On the three-track OCellus-Agent-Bench benchmark (Table 3), pipeline accuracy on eighty trials -twenty natural-language queries times four datasets -reaches 75.
- 22  | Track             | Metric                                 | Dataset                                | OCellus-Agent   | Baseline                    | |-------------------|----------------------------------------|----------------------------------------|-----------------|-----------------------------| | Pipeline accuracy | Task success rate (Verifier-L3 ACCEPT) | 20 NL queries × 4 datasets (80 trials) | 75.
- 18 Current models require users to navigate complex computational pipelines -preprocessing data, 19 selecting parameters, running inference, and interpreting outputs -whereas OCellus-Agent 20 collapses these steps into a natural-language dialogue in which a researcher describes what they 21 want to know, and the trained Planner decomposes the query into an executable directed acyclic 22  13  14  15  16  graph, the rule-based Router dispatches each step to the appropriate expert, and the three-layer 1 Verifier provides biological plausibility checks before any result reaches the user.
