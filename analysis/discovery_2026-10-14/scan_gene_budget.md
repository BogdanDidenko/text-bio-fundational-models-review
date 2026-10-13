
## full_2026-07-06__rec_000060
- Using this PCA embedding, we constructed a k-nearest neighbor graph (k=20) and subsequently performed Leiden clustering (resolution=0.

## full_2026-07-06__rec_000063
- ## TISSUENARRATOR enables interactive Q&amp;A about spatial regions  To evaluate TISSUENARRATOR's ability to apply biological prior knowledge and learned spatial knowledge in a Q&amp;A setting, we constructed a proof-of-concept dataset covering three tasks: given the name of an anatomical structure, (1) return the top 5 most abundant cell types, (2) list the top 20 highly expressed genes, and (3) generate a natural-language description of the structure.
- We report results at k = 10 , 30 , and 50 , corresponding to NDCG@ k and Overlap@ k using the top k genes.

## full_2026-07-06__rec_000090
- For predictive tasks such as cell type annotation on single cells, we find that K = 1000 often works well for cell annotation, achieving performance competitive or better than baseline models.
- We retained the 5000 most highly variable genes to prioritize high-signal features and align with established benchmarks in perturbation modeling, which typically utilize between 1000 and 7000 genes [4, 70, 71, 72, 73], and evaluated models in the scGPT embedding space [4] using maximum mean discrepancy (MMD), Wasserstein distance, and scFID (Section 4.
- We employed the 2,000-gene feature set established in ChemCPA, comprising the 978 landmark genes plus the 1,022 highest variable genes not present in the landmark set.

## full_2026-07-06__rec_000827

## full_2026-07-06__rec_001126
- We identified the top 10 genes that with the largest  changes  in  node  degree  between  the  two  cell  types  (Fig.
- - **b**: Text-based reasoning workflow: input prompt with top 100 ranked genes and predicted phenotype class, CellHermes predictor, and natural-language output explaining marker/pathway evidence.
- Next, we ranked the gene expression values for each cell and truncated the top 100 genes for each cell  , denoted as 𝑖 .
- For  comparison,  we  also constructed co-expression networks by  computing  the  Pearson  correlation  coefficient between every gene pair and connecting each gene to its k =15 most correlated neighbors using the same KNN procedure.

## full_2026-07-06__rec_001187

## full_2026-07-06__rec_001319
- For most cell types, more than half of the top 10 genes identified by the model are found in the CellMarker2.
- To standardize gene features across all datasets, we identify the top 3,600 highly variable genes for each dataset's cell-by-gene matrix using Seurat [87, 88].

## full_2026-07-06__rec_001381
- <!-- formula-not-decoded -->  To mitigate data sparsity, we retain the top 2,048 most expressed genes per cell, which captures the majority of meaningful signals.

## full_2026-07-06__rec_001617

## full_2026-07-06__rec_001838
- , 2025) pioneer in this direction by converting gene expression data into a natural language sentence where names of top-100 expressed genes are ordered by their expression level in that cell.

## full_2026-07-06__rec_001889
- ##### Protein interaction analysis  For each cell type, we selected the top 300 genes ranked by gene attention weights, and then predicted the protein-protein interaction network using STRING (v.
- The same set of 2,000 highly variable genes (HVGs) was selected for all methods; however, for scVI, we provided the unnormalized count data of these HVGs instead of the processed values used for the other methods.
- Both methods uniformly selected 2000 highly variable genes (HVGs): scmap achieved this through its built-in selectFeatures function, and SciBet used the 'SelectGene\_R' function from its package for gene selection.

## full_2026-07-06__rec_002049
- Given a query q , bio embeddings ˜ z b injected at a  1 For notational simplicity, we assume k = 1 and omit the token index in most equations from here onward; the framework naturally extends to k &gt; 1 when multiple embeddings are injected  [BIO] marker, and paired target text t b = ( t 1 , .
- , 2022) under zero-shot generation: (1) random and majority baseline (2) open-domain LLMs given a list of the 128 most expressed genes (sorted by expression count) as input.

## full_2026-07-06__rec_002105
- Specifically, the transcriptomes were sorted by gene expression levels, and the top 2048 most highly expressed genes were tokenized with a dictionary of human gene symbols (Theodoris et al.
- For each transcriptome, we generated a chat-like conversation using one of two LLMs (GPT-4 or Mixtral) on the basis of the transcriptome's top 50 most highly expressed genes, the top 50 GSVA-derived gene sets, and the transcriptome's textual annotation.

## full_2026-07-06__rec_002517
- To capture the most significant expression patterns, we prioritize the top 100 most expressed genes, since lower-ranked genes tend to have more consistent expression values.
- |                              | /sort-amount-up Quality   | /sort-amount-up Quality   | /sort-amount-up Quality   | /sort-amount-up Quality   | /sort-amount-up Quality   | /sort-amount-up Quality   | /sort-amount-up Quality   | /sort-amount-up Quality   | /sort-amount-up Discriminability   | /sort-amount-up Discriminability   | /sort-amount-up Discriminability   | /sort-amount-up Discriminability   | /sort-amount-up Discriminability   | /sort-amount-up Discriminability   | /sort-amount-up Discriminability   | /sort-amount-up Discriminability   | |------------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|------------------------------------|------------------------------------|------------------------------------|------------------------------------|------------------------------------|------------------------------------|------------------------------------|------------------------------------| | Model                        | K=5                       | K=5                       | K=10                      | K=10                      | K=25                      | K=25                      | K=50                      | K=50                      | K=5                                | K=5                                | K=10                               | K=10                               | K=25                               | K=25                               | K=50                               | K=50                               | |                              | Expr.
- Panel (b) contains four line plots versus Expanded Vocab Size (0, 7, 14, 21), with legend values K=5, K=10, K=25, K=50.

## full_2026-07-06__rec_003188

## full_2026-07-06__rec_003206
- The UMAP plots in Figure 4 show how much separation can be achieved by representing cells with the 100 highest expressed genes.
- These heatmaps compare the differentially expressed genes for each cell type in both the generated and ground-truth cells, with the differential genes sourced from the top 100 genes in the ground truth dataset.
- | Model                      | K=5   | K=5   | K=10   | K=10   | K=25   | K=25   | K=50   | K=50   | |----------------------------|-------|-------|--------|--------|--------|--------|--------|--------| |                            | Expr.
- | Model                   | K=5   | K=5   | K=10   | K=10   | K=25   | K=25   | K=50   | K=50   | |-------------------------|-------|-------|--------|--------|--------|--------|--------|--------| |                         | Expr.
- 95 and top\_k = 50 to promote diversity in cell generation.
- The metrics are computed across all 35 cell types seen during training with 500 cells generated per cell type and then averaged across all generated cells (top 100 genes).
- On average, the number of tokens in the prompts and top 100 genes combined was around 350.

## full_2026-07-06__rec_003323
- To transfer the information in gene expression space to text space, we first rank the genes of each spot based on their expression profiles and select the top 100 genes to formulate them in natural language.

## full_2026-07-06__rec_003434

## full_2026-07-06__rec_003517
- 7), which introduces a distributional shift towards essential gene knockdowns across four cell lines (K562, RPE1, HepG2, and Jurkat) and 2,000 highly variable genes.
- This focus is biologically corroborated by the significant enrichment of the top 1,000 genes prioritized by these modalities in the KEGG TCR signaling pathway (hsa04660) [56].
- Gene expression matrices were log1p-normalized and converted into cell sentences consisting of the top 1,000 expressed genes per cell.
- The processed dataset contains normalized gene expression for 643,413 cells across 2,000 highly variable genes.
- We identified 2,000 highly variable genes from 18,308 feature space using scanpy.
- To quantify the phenotypic shift induced by perturbations, we projected the transcriptional profiles into a low-dimensional space using Principal Component Analysis (PCA) derived from the 2,000 most highly variable genes.
- <!-- formula-not-decoded -->  where the 4 × accounts for 1 × forward + 1 × activation checkpoint recompute + 2 × backward, and F peak = 989 TFLOP/s (H200 bf16).
- We used the top 1,000 most highly expressed genes per cell ( top k genes=1000 ), providing substantially more gene coverage than the 200-gene default in the C2S tutorial.

## full_2026-07-06__rec_003629
- In this case, we utilized the top 2000 highly variable genes.
- Main visible finding: hit rate increases as the candidate set is restricted to smaller top-K groups, especially at `Top K = 100`; the effect is visible in both L1000 and Tahoe-100M test sets, with larger spread and higher outliers in the distribution plots at smaller K.

## july_update_2026-07-06__rec_000060
- Raw scRNA-seq expression profiles are ranked into a Cell Sentence (topK =200 HGNC gene symbols in descending expression order).
- For a cell with normalised expression X ∈ R G we sort genes by expression magnitude and keep the topK ( K =200 ) HGNC symbols:  <!-- formula-not-decoded -->  Rank correlates almost linearly with log-expression ( R 2 ≈ 0 .
- Each prompt has four blocks: (1) KG virtual tokens [KG\_VT] : one virtual token per input gene (block length K =200 ), aligned one-to-one with the Cell Sentence; (2) Biological metadata [Meta] : short natural-language fields (tissue, compartment, disease, optional KG triples); (3) Cell Sentence [CellSentence] : the ranked gene list as HGNC symbols; (4) Task instruction [Task] : one short line specifying the output format.
- 500 genes per cell, &lt; 20% mitochondrial reads), log-normalisation to library size 10 4 , and conversion to ranked Cell Sentences of topK =200 HGNC gene symbols, we apply a deterministic hash-based partition:  <!-- formula-not-decoded -->  where s i is the shard index and c i the intra-shard cell index.
- The K =200 virtual tokens are length-matched to the cell sentence - the i -th virtual token carries graph context for exactly the i -th ranked gene - and prepended to the textual prompt, separated by a single learnable [KG\_SEP] token.
- A gene-level alignment loss aligns the last-layer context embedding z i,k at each gene position with the frozen embed\_tokens embedding of the corresponding gene name:  <!-- formula-not-decoded -->  where z i,k is the mean last-layer hidden state at the k -th gene position for sample i , e gene g is the frozen embed\_tokens embedding for gene g , K =200 is the cell-sentence length, and G is the gene vocabulary.
- 1 Task B1: Cell-Type Prediction  The model reads the top-200 ranked genes of a cell and generates its cell type as free text (e.

## june_update_2026-06-10__rec_000121
- However, these approaches introduce a different fundamental trade-off: ranked gene lists discard quantitative expression precision and produce token-inefficient representations (40-80 tokens per cell for the top-20 genes), whereas structured descriptions scale poorly to population-level multi-cell reasoning [28].
- Starting from the shared Stage 2 SFT checkpoint π 0, we train K domain-specific expert models { π ( k ) } K k = 1 independently.
- 95, topk = 20); individual scores therefore carry sampling noise that the top-5 merge attenuates.
- 8 pp from k = 1 to k = 16).
- Final points at `k=16` are highlighted with diamond markers.
- Final ranking at k = 16: Tissue Type (90.

## june_update_2026-06-10__rec_000148
- The prediction targets were the top 50 genes with the highest expression in the training set, and performance was evaluated on the held-out spots from the test sections.

## june_update_2026-06-10__rec_000194
- It does so via a set of K learnable query vectors Q = { q k } K k =1 , which are randomly initialized and updated during training.

## june_update_2026-06-10__rec_000246
- Candidate class labels are provided in text to OmicsLM, C2S-Scale-27B, and Cell-o1 during constrained likelihood scoring, matching the closed label set available to CLIP-like contrastive scoring; C2S-Scale and Cell-o1 receive the top-1000 expressed genes as text input.
- Text-only baselines receive the 50 highest-expressed genes per sample, with sample identifiers replaced by dummy labels ( sample\_1 , sample\_2 , .

## june_update_2026-06-10__rec_000248
- , 2025) pioneer in this direction by converting gene expression data into a natural language sentence where names of top-100 expressed genes are ordered by their expression level in that cell.

## june_update_2026-06-10__rec_000350
- - Experts per layer : 128 FFN experts, with a shared top- k softmax router where k = 8.

## update_2026-08-09__rec_000138
- - Caption beneath heatmap: `Primary metric (Balanced accuracy / Recall / Cosine)`  Visible task labels include: - SC core: `perturbation`, `cell_gmppi`, `cell_phenotype`, `gene2disease`, `t-cellmetabase`, `CellMix` - SC extended: `virus_response`, `perturbation_rank` - SC cross-domain: `cross_species_celltype`, `development_stage`, `gene_knock-stripe`, `cell_state_transfer` - Spatial core: `spatial_celltype`, `spatial_neighborhood`, `spatial_tissue_region`, `spatial_celltype`, `spatial_lamination` - Spatial extended: `spatial_vz`, `spatial_domain`, `spatial_density`, `spatial_colocalization`, `spatial_comp_gene`  Bottom panel: - Three grouped bar charts:   - `KNN accuracy (k=5)`   - `Linear probe accuracy`   - `NMI (clustering)` - X-axis biological datasets/tissues:   - `pancreas`   - `lung`   - `pbmc`   - `atora`   - `Average` - Y-axis ranges from 0.
- (b) Encoder benchmark across 14 foundation models: kNN 3 accuracy (k=5), linear probe accuracy, and NMI (clustering) across four datasets -pancreas, lung, 4 PBMC, aorta -with an Average summary group.
- (a) Pearson correlation on top-20 differentially expressed genes per perturbation: 8 OCellus-GNN 0.
