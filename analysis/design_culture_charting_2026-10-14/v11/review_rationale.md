
# T | quantitative_fidelity | limitation_of_own_choice (works 12)

## W_omnina
- R2: The quality and completeness of pretraining annotations can affect fine-tuning performance. || [sec_0022] finetuning performance can be influenced by the quality and completeness of annotations used during pretraining.

## full_2026-07-06__rec_001126
- R1: The text conversion strategy discards the original numerical values of biological measurements. || [sec_0012] a method that discards  actual  numerical  values  of  data.
- R2: Converting omics data into text discards the original numerical values. || [sec_0012] a method that discards  actual  numerical  values  of  data.
- R2: The transcriptomic representation retains ranked top genes rather than the complete expression profile. || [sec_0014] Next, we ranked the gene expression values for each cell and truncated the top 100 genes for each cell

## full_2026-07-06__rec_001773
- R1: The authors identify limited high-fidelity cross-modal translation and current tokenization/vector-quantization limitations. || [sec_0023] Additionally, while our model demonstrates the feasibility of mapping DNA to multi-dimensional outputs, such as structure or genomic assay signals, achieving high-fidelity cross-modality translation remains an open challenge. || [sec_0023] Future improvements in tokenization strategies (Li et al., 2024a; Pagnoni et al., 2024; Qiao et al., 2024), including more robust vector quantization (VQ-VAE) techniques, could potentially improve the model's ability to handle complex modalities with greater precision.
- R2: The authors identify high-fidelity cross-modal translation as an unresolved limitation. || [sec_0023] achieving high-fidelity cross-modality translation remains an open challenge.

## full_2026-07-06__rec_002517
- R1: The authors acknowledge that sorting genes and limiting cell sentences to 100 may omit biological complexity and relevant interactions. || [sec_0019] By representing gene expression matrices as cell sentences sorted by expression levels and limiting the length to 100, there might be inherent limitations. This simplification might overlook the complexity and nuances of cellular states and interactions, possibly impacting the accuracy and depth of analysis.
- R2: The ranked top-100 cell-sentence representation may omit cellular complexity, state, interactions, and relevant genes. || [sec_0019] By representing gene expression matrices as cell sentences sorted by expression levels and limiting the length to 100, there might be inherent limitations. This simplification might overlook the complexity and nuances of cellular states and interactions, possibly impacting the accuracy and depth of analysis.

## full_2026-07-06__rec_003008
- R1: The authors report that a smaller encoder has limited capacity to represent long, mechanism-rich profile text. || [sec_0022] under the smaller BioBERT encoder the absolute scores drop and BFT's relative gain over SFT shrinks (consistent with BioBERT's limited capacity to fully encode long, mechanism-rich profile text)

## full_2026-07-06__rec_003043
- R2: The GPT-3.5-only training-data choice does not accurately summarize non-protein-coding genes. || [sec_0020] The LLM based on GPT 3.5 to finetune does not accurately summarise the function of non-proteinencoding genes, as shown in Supplementary File 1.

## full_2026-07-06__rec_003131
- R2: The authors note that the current text representation may be insufficient when richer sequence features are needed. || [sec_0030] However, a from-scratch pre-training can be necessary for a better representation of genetics, genomics, and other levels of bio-factors, especially when more features from the sequence are involved.

## full_2026-07-06__rec_003206
- R1: The authors identify loss of explicit expression-level information as a limitation of representing profiles by ordered gene names. || [sec_0023] This approach results in the loss of specific quantitative information about the levels of gene expression, requiring the model to infer the strength of expression from gene order alone.
- R2: The rank-only representation loses explicit quantitative expression information. || [sec_0023] This approach results in the loss of specific quantitative information about the levels of gene expression, requiring the model to infer the strength of expression from gene order alone.

## full_2026-07-06__rec_003629
- R1: Transcriptomic representations do not directly encode downstream functional, physiological, or safety outcomes. || [sec_0010] while transcriptomic similarity provides a powerful proxy for phenotypic alignment, it does not directly encode downstream functional, physiological, or  safety -related outcomes

## june_update_2026-06-10__rec_000121
- R1: The authors acknowledge information loss from compressing the expression profile into a small number of discrete tokens. || [sec_0040] Compressing ∼ 20,000 gene dimensions into 8 discrete tokens inherently discards fine-grained expression information.
- R2: The authors acknowledge information loss for tasks requiring precise quantitative expression values. || [sec_0040] Compressing ∼ 20,000 gene dimensions into 8 discrete tokens inherently discards fine-grained expression information. Although this representation is sufficient for cell type classification, the loss of information may degrade performance on tasks that require precise quantitative expression values (e.g., differential expression fold-change prediction).

## june_update_2026-06-10__rec_000133
- R1: The BPE representation may lose local information needed for single-nucleotide resolution. || [sec_0011] it may still lose part of the local information required in settings  that  demand  single-nucleotide  resolution
- R2: The authors identify potential loss of local information at single-nucleotide resolution as a limitation of the BPE strategy. || [sec_0011] it may still lose part of the local information required in settings  that  demand  single-nucleotide  resolution

## june_update_2026-06-10__rec_000350
- R1: The authors hypothesize that the remaining remote-homology gap reflects a representation-level constraint rather than insufficient supervised fine-tuning. || [sec_0031] We hypothesize the remaining gap is a representation-level constraint rather than an SFT-scale constraint; testing requires controlled experiments with more CPT on distant-protein pairs.

# E | quantitative_fidelity | against_alternative (works 7)

## W_cell2text
- R2: Plain-text gene sentences provide shallow signals and do not let the language decoder fully exploit hidden biological patterns. || [sec_0006] However, representing cells as plain text gene sentences offers only shallow signals, since the language decoder is not pretrained on such inputs and cannot fully exploit hidden biological patterns encoded in the data.
- R2: The authors criticize the top-gene truncation used by text-based representations because it loses subtle interactions in lowly expressed genes. || [sec_0006] In addition, truncating sequences to this limit constrains the model's ability to capture subtle gene-gene interactions, particularly in lowly expressed regions.
- R2: Cell-level pooling is presented as an inferior alternative because it compresses away biological nuances. || [sec_0009] Instead of compressing each cell into a single embedding vector, which would lose important biological nuances, we extract individual embeddings for each gene within the cell.

## full_2026-07-06__rec_001074
- R1: The authors argue that raw DNA strings cause LLMs to miss genomic features, while DNA-only models primarily produce task-specific scores rather than interpretable language. || [sec_0008] LLMs treat S DNA as simple strings, thereby missing rich genomic features, while DNA Foundation Models ( f DNA) capture these features but primarily yield task-specific discriminative outputs (e.g., classification or regression scores) rather than interpretable natural language.

## full_2026-07-06__rec_001319
- R1: The authors criticize ranked gene-name representations for omitting lower-expressed genes. || [sec_0003] focusing exclusively on top-expressed genes overlooks important information from lower-expressed ones
- R1: The authors argue that textual conversion can lose numerical precision. || [sec_0003] converting quantitative gene expression data into text risks losing essential numerical precision.
- R2: The authors criticize ranked-gene text representations because they omit lower-expressed genes, increase context length when all genes are included, and lose numerical precision. || [sec_0003] However, focusing exclusively on top-expressed genes overlooks important information from lower-expressed ones, while incorporating all genes inflates context length and computational demands. Furthermore, converting quantitative gene expression data into text risks losing essential numerical precision.

## full_2026-07-06__rec_001381
- R1: The authors argue that cell sentences and reduced/ranked gene representations lose quantitative and low-abundance gene information and reduce annotation accuracy. || [sec_0003] Other methods represent cells using only the top 30-100 expressed genes [17, 18], or discard critical quantitative expression information and low-abundance genes [8, 19, 12]. They result in substantial information loss and reduced annotation accuracy || [sec_0037] the cell sentence representation leads to a significant increase in error rate
- R2: The authors argue that converting numerical expression levels into cell sentences loses cellular information. || [sec_0037] This finding highlights the non-negligible cellular information lost during the transformation from numerical expression levels to cell sentences, which limits the effectiveness of related models in downstream applications.

## full_2026-07-06__rec_001889
- R1: The authors criticize converting expression profiles into top-K gene-name text as lossy and vulnerable to hallucination. || [sec_0004] the inherent hallucination problem of LLMs raises concerns about the reliability and reproducibility of biologically meaningful representations and predictions. || [sec_0004] such a lossy text-based representation is fundamentally unable to capture the dynamic and context-dependent roles of genetic features and cells across different biological states.
- R2: The authors criticize top-gene textual representations because of hallucination concerns and reduced reliability and reproducibility. || [sec_0004] this framework converts scRNA-seq expression profiles into a textual format (selecting the top-K highly expressed genes and arranging their gene names), the inherent hallucination problem of LLMs raises concerns about the reliability and reproducibility of biologically meaningful representations and predictions.
- R2: The authors state that text-only top-gene representations lose dynamic and context-dependent biological information. || [sec_0004] such a lossy text-based representation is fundamentally unable to capture the dynamic and context-dependent roles of genetic features and cells across different biological states.

## june_update_2026-06-10__rec_000194
- R1: The authors argue that textification loses geometric and functional information encoded by biological foundation models. || [sec_0007] However, textualization discards rich geometric and functional representations of biology encoded by state-of-the-art foundation models
- R2: The authors criticize linear projection interfaces because they do not actively extract task-relevant biological information and can encourage reliance on prompt text. || [sec_0020] The linear projection layer provides no mechanism to actively distill task-relevant information from the biological embedding(s). || [sec_0016] This incentivizes such models to rely on textual prompt cues and impairs LLM reasoning.
- R2: The authors characterize converting heterogeneous biological entities into text as lossy. || [sec_0020] Textification of heterologous biological datasets is inherently lossy.

## june_update_2026-06-10__rec_000246
- R1: The authors criticize rank-ordered text representations for discarding expression magnitudes and consuming context. || [sec_0006] Cell2Sentence (C2S) [Levine et al., 2024], C2S-Scale [Rizvi et al., 2025], and Portraying Gene Language (PGL) [Choi et al., 2026] transform expression matrices into literal 'cell sentences'-plain-text strings of gene names ordered by descending abundance. || [sec_0006] these representations rapidly saturate context windows on full transcriptomes that span tens of thousands of expressed genes and discard the quantitative expression magnitudes that rank-only orderings cannot convey
- R2: The authors criticize text serialization for losing quantitative magnitudes and consuming context, which forces truncation. || [sec_0003] text-based biomedical LLMs serialize expression as gene-name sequences [Levine et al., 2024, Rizvi et al., 2025, Choi et al., 2026] at the cost of quantitative signal and context budget. || [sec_0006] discard the quantitative expression magnitudes that rank-only orderings cannot convey, forcing aggressive truncation of low-abundance transcripts.

# T | no_architecture_change | for_own_choice (works 9)

## full_2026-07-06__rec_000063
- R2: Textual spatial representations can be read and extended by an LLM without specialized model components. || [sec_0003] In effect, these representations let cells tell their tissue story in a form that LLMs can read and extend, without requiring specialized model components.

## full_2026-07-06__rec_000090
- R1: Representing expression as cell sentences avoids bespoke architectural changes and simplifies development and deployment. || [sec_0005] C2S-Scale avoids modifying the underlying architecture of LLMs, instead focusing on a data transformation approach. || [sec_0003] This data transformation strategy simplifies model development and deployment
- R2: The textual transformation avoids custom architectural and vocabulary modifications and supports application across LLM architectures. || [sec_0005] C2S-Scale avoids modifying the underlying architecture of LLMs, instead focusing on a data transformation approach. || [sec_0016] by avoiding architectural modifications, the C2S framework is immediately applicable to any LLM architecture or innovation

## full_2026-07-06__rec_001126
- R1: Textualization allows one LLM backbone to process multiple biological data types without separate modality-specific architectures. || [sec_0006] without a need for separate,  modality-specific  architectures.
- R2: The approach reuses an existing language model and adapts it to omics through textualization and fine-tuning. || [sec_0006] Instead  of  training  a  new  model,  we  unify  omics  data  with  natural  language

## full_2026-07-06__rec_002243
- R1: Sentence segmentation reuses the existing period token and avoids additional annotations or special tokens. || [sec_0019] Since the pre-trained model's data already includes punctuation marks such as periods (.), no additional annotation or introduction of new special tokens was necessary to handle sentence segmentation.
- R2: The authors format summarization examples for causal GPT-2 because GPT-2 does not directly support Seq2Seq problems. || [sec_0022] Since  GPT-2  does  not  directly  support Seq2Seq problems, we indirectly achieved this by formatting the training samples.
- R2: Existing punctuation in the pretraining data lets the sentence-segmentation method avoid additional annotations or special tokens. || [sec_0019] no additional annotation or introduction of new special tokens was necessary to handle sentence segmentation.

## full_2026-07-06__rec_003131
- R2: Converting structured and unstructured genomic sources into bio-text allows their integration into a general generative language-model framework. || [sec_0003] By converting the data into bio-text, we identified and categorized gene entities, gene functions, protein entities, protein functions, phenotype entities, genotype-phenotype association analysis, and related biological mechanisms. These components were then integrated into an informative context, which was subsequently used to develop the GP-GPT in the form of generative language models.

## full_2026-07-06__rec_003206
- R2: The representation allows pretrained causal language models to be fine-tuned on cell sequences. || [sec_0010] This allows any pretrained causal language model to be further fine-tuned on cell sequences.

## full_2026-07-06__rec_003434
- R1: The authors present use of the unmodified text-transformer architecture for DNAm processing as a benefit. || [sec_0014] It  is  especially  notable  that  LongevityLLM  features  no  architectural  augmentations  for  DNAm  data  processing,  such  as  dedicated  prediction  heads,  special  tokens,  or  separate  treatment  of  numeric  values.
- R2: The authors state that a standard natural-text Qwen3 architecture is sufficient for DNAm age prediction without dedicated biological-processing architecture. || [sec_0014] The  base  Qwen3 architecture, originally designed to process natural text, has proven fully sufficient for a task that previously required a dedicated statistical model.

## full_2026-07-06__rec_003629
- R1: The text representation fits the token-based operation of the language model. || [sec_0004] This representation aligns naturally with  the  token-based  operation  of  LLMs.
- R2: The textual representation fits the language model's native token-based interface. || [sec_0004] This representation aligns naturally with  the  token-based  operation  of  LLMs.

## june_update_2026-06-10__rec_000121
- R1: The authors favor direct vocabulary integration to avoid a separate cross-modal adapter and its bottleneck. || [sec_0012] cell tokens must enter the LLM through its native token embedding table rather than through a separately learned cross-modal adapter, which would relegate gene expression to a secondary modality and add a trainable bottleneck between cell identity and the reasoning path.

# T | leverage_llm_knowledge | for_own_choice (works 11)

## W_omnina
- R1: The authors motivate integrating nucleotide sequences with corresponding text annotations so the model can learn annotation semantics and support downstream tasks. || [sec_0003] Unlike previous works, our approach integrates nucleotide sequence and the corresponding text annotations into the learning process. || [sec_0003] By doing so, the model gains the capacity to understand semantic of text annotations, thereby empowering it to perform a wide range of downstream tasks.
- R1: Joint sequence-and-annotation modeling is intended to capture nucleotide grammar and annotation semantics. || [sec_0004] By jointly modeling both sequences and their associated annotations, our approach seeks to more fully capture the compositional grammar and semantic structure underlying genomic information, enabling robust generalization and interpretability across tasks.

## full_2026-07-06__rec_000063
- R1: The text-native formulation is intended to leverage LLM generative capacity for counterfactual tissue modeling. || [sec_0003] This formulation allows TISSUENARRATOR to unleash the generative capacity of LLMs for predicting new cells in diverse counterfactual tissue environments.
- R2: Explicit numerical tokens activate pretrained geometric priors and avoid de novo representation learning. || [sec_0005] For the latter, we demonstrate that explicit numerical tokens offer a superior alternative to learnable positional embeddings, bypassing the need for de novo representation learning by activating the LLM's pretrained geometric priors.

## full_2026-07-06__rec_000090
- R1: The authors use pretrained language-model knowledge and existing LLM infrastructure. || [sec_0005] This has the additional benefits of utilizing knowledge about biological concepts that the LLM picked up during pretraining, as well as utilizing the vast infrastructure developed around LLM training and inference.
- R1: Keeping gene names in the existing vocabulary lets the LLM use knowledge acquired during language pretraining. || [sec_0016] the LLM is able to recognize gene names and associate prior knowledge about that gene obtained during self-supervised pretraining on natural language data
- R2: The approach leverages biological concepts acquired by the language model during pretraining. || [sec_0005] This has the additional benefits of utilizing knowledge about biological concepts that the LLM picked up during pretraining

## full_2026-07-06__rec_001126
- R1: The authors motivate natural-language input because pretrained LLMs provide embedded world knowledge and reasoning skills. || [sec_0004] pretrained natural language-LLMs - with their embedded world knowledge and reasoning skills
- R2: Pretrained language models provide reasoning mechanisms and human-readable explanations. || [sec_0004] enabling  human-readable  explanations  of  system behaviors

## full_2026-07-06__rec_001773
- R2: The authors motivate an autoregressive transformer strategy by the success of LLM pretraining and post-training. || [sec_0003] The success of LLMs is pretraining transformer-based autoregressive models (Vaswani, 2017) on internet-scale data, followed by post-training to increase instruction-following abilities (Lambert et al., 2024). Inspired by this, we ask: is it possible to develop a generalist genomic foundation model for addressing diverse genomic tasks simultaneously?

## full_2026-07-06__rec_002243
- R1: The unified BPE tokenizer was selected to support transfer of language capabilities across English, DNA, and protein sequences. || [sec_0012] One important condition for achieving multilingual transfer ability is the use of a unied tokenizer, typically  based  on  the  Byte  Pair  Encoding  (BPE)  method.
- R2: The authors motivate a unified BPE tokenizer as a condition for transferring language capabilities across English, DNA, and protein sequences. || [sec_0012] One important condition for achieving multilingual transfer ability is the use of a unied tokenizer, typically  based  on  the  Byte  Pair  Encoding  (BPE)  method.

## full_2026-07-06__rec_002517
- R2: Vocabulary adaptation is motivated by the inadequacy of standard LLM vocabularies for gene names and specialized single-cell terminology. || [sec_0009] The default vocabularies of pre-trained LLMs often lack the specialized lexicon crucial for interpreting single-cell data, particularly gene names. || [sec_0009] Consequently, this adaptation enriches the LLM's lexicon with domain-specific terms and subword units, leveraging domain knowledge to improve its efficacy in single-cell analysis.

## full_2026-07-06__rec_003043
- R2: GPT-3.5-generated text is included to add knowledge about genes absent from NCBI and to provide more human-like, comprehensive functional information. || [sec_0018] The first advantage is that GPT 3.5 has specific knowledge of certain genes, thus helping our AI assistant answer questions related to genes that are not collected in the NCBI database. The other advantage is that GPT 3.5's output is more like human language and has more comprehensive functional information to enhance the quality of the model output.

## full_2026-07-06__rec_003131
- R1: The model uses bio-text linguistic knowledge within a prompt-based language-model framework. || [sec_0014] GP-GPT uses the Llama2 framework to establish an autonomous LLM-based framework with a prompt question-and-answer format.
- R2: The authors justify using biological text because language models can capture relationships and context relevant to genetic and phenotype data. || [sec_0003] The ability of LLMs to capture intricate relationships and context from text aligns well with the complexities inherent in genetic and phenotype data.

## full_2026-07-06__rec_003206
- R2: The text representation is motivated by leveraging pretrained language-model knowledge and language understanding for transcriptomics. || [sec_0010] Current methods in this domain rely on specialized neural networks that do not leverage the pretrained knowledge and language understanding of large language models.

## june_update_2026-06-10__rec_000121
- R1: Evidence-first gene-name prediction is used to align RVQ embeddings with pretrained gene-name representations through the language-model loss. || [sec_0013] Because gene-name tokens in E are predicted from RVQ input positions via the attention mechanism, the cross-entropy loss on these tokens provides a dense supervisory signal that pulls RVQ embeddings toward the pretrained gene-name representations, without requiring any explicit alignment module.
- R2: Evidence-first supervision uses the language-model objective to ground new biological tokens without a projection network. || [sec_0003] We develop scCoT-Synth , an evidence-grounded supervision engine that overcomes the coldstart problem of newly added biological tokens without requiring a cross-modal projector.
