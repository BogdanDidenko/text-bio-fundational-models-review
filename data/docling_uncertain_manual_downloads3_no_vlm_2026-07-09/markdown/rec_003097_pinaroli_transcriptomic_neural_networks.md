####### UNIVERSITÀ DEGLI STUDI DI PADOVA

##### DIPARTIMENTO DI BIOLOGIA

Corso di Laurea in Biologia Molecolare

<!-- image -->

###### ELABORATO DI LAUREA

### Transcriptomic Neural Networks Architecture and Applications to Functional and Aging Research

Tutor:

Prof.ssa Sofia Pavanello

Dipartimento di Scienze Cardio-Toraco-Vascolari e Sanità Pubblica

Laureando:

Andrea Pinaroli

ANNO ACCADEMICO 2024/2025

#### Table of Contents

| Riassunto Esteso.........................................................................................4     |                                                                                                          |
|----------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Abstract                                                                                                       | .......................................................................................................6 |
| 1. Introduction............................................................................................6   |                                                                                                          |
| 1.1 ANNs in Biology.................................................................................7          |                                                                                                          |
| 1.2 Single-cell Transcriptomic ANNs.......................................................8                    |                                                                                                          |
| 2. Methods................................................................................................10   |                                                                                                          |
| 2.1 The Transformer Architecture..........................................................10                   |                                                                                                          |
| 2.2 scFoundation...................................................................................12          |                                                                                                          |
| 2.3 Downstream applications                                                                                    | ................................................................15                                       |
| 2.3.1 Read-depth enhancement........................................................15                         |                                                                                                          |
| 2.3.2 Drug response prediction                                                                                 | .........................................................16                                              |
| 2.3.3 Gene perturbation response prediction                                                                    | ....................................17                                                                   |
| 2.3.4 Cell type annotation..................................................................18                 |                                                                                                          |
| 2.3.5 Gene module and GRN inference                                                                            | ............................................18                                                           |
| 3. Results..................................................................................................19 |                                                                                                          |
| 3.1 Read-depth enhancement...............................................................19                    |                                                                                                          |
| 3.2 Drug response prediction                                                                                   | ................................................................21                                       |
| 3.3 Gene perturbation response prediction                                                                      | ...........................................22                                                            |
| 3.4 Cell type annotation.........................................................................23            |                                                                                                          |
| 3.5 Gene module and GRN inference                                                                              | ...................................................24                                                    |
| 4. Discussion                                                                                                  | ...........................................................................................24            |
| References                                                                                                     | ................................................................................................25       |
| Appendix 3 TFM-enhanced aging clocks                                                                           | ..................................................28                                                     |
| Appendix 3 References.............................................................................29           |                                                                                                          |

#### Riassunto Esteso

I foundational  models di  intelligenza  artificiale  sono  diventati  la  base metodica di importanti avanzamenti tecnologici sia nell9ambito del processamento del linguaggio naturale che in ambiti biologici. Questi sono grandi modelli di reti neurali artificiali che processano informazioni mimando la struttura dei circuiti neurali umani. L9input fornito, trasformato in un vettore con alta multidimensionalità ( embedding ), viene sottoposto a molte operazioni matriciali semplici in successione, trasformandolo in un output utile.  L9entità  della  modifica  operata  ad  ogni  passaggio  matematico  è determinata dai parametri del modello, calcolati durante l9addestramento.

I foundational models sono pre-addestrati su una grande quantità di dati, sfruttando l9abbondanza di testo su internet o l9esponenzialmente sempre maggiore disponibilità di dati biologici derivanti da tecnologie omiche. Una tendenza chiave del settore è la costruzione di modelli sempre più grandi. Questo è dovuto alla legge di potenza delle reti neurali, un9osservazione empirica  di  come  le  capacità  performative  dei  modelli  possano  essere affidabilmente  migliorate  semplicemente  aumentandone  il  numero  di parametri, indipendentemente da quello corrente.

Questa tecnologia è stata applicata ai dati di sequenziamento dell9RNA a singola cellula (scRNAseq), e qui gli autori presentano il foundational model per scRNA più grande mai costruito, scFoundation. Questo è composto da 100 milioni di parametri addestrati su 50 milioni di cellule, con una strategia di  addestramento  sensibile  alla  profondità  di  sequenziamento  al  fine  di operare il de-masking . A tal fine, dati sintetici derivanti da riduzioni variabili della  profondità  di  sequenziamento  (dati  sotto-campionati)  sono  stati impiegati  per  l9allenamento  invece  che  quelli  originali.  Il  modello  prende come input il 70% dei valori di espressione sotto-campionati, mentre il 30% rimane mascherato, ed impara a fornire un output che predica accuratamente  l9intero  profilo,  incluso  il  30%  dei  geni  che  era  stato mascherato, ad una profondità di sequenziamento maggiore di quella dei dati sotto-campionati. Il modello mostra ottime capacità predittive in tutte le applicazioni testate, validando la sua struttura simil-transformer asimmetrica di encoder-decoder.

Le  applicazioni  validate  sono  molteplici.  Quella  nativa  al  modello  è l9inferenza di un profilo di espressione con profondità di sequenziamento maggiore di quella fornita in input. È stata dimostrata una maggiore capacità di scFoundation di predire i corretti livelli di espressione genica rispetto ai dati  sotto-campionati  non  processati.  Il  modello  è  poi  stato  comparato  a soluzioni alternative di imputazione, risultando il più efficace se impostato per migliorare anche la profondità genica.

Predire la risposta cellulare ai composti chimici è cruciale nel settore del processamento  di dati  scRNAseq. È stata indagata la capacità di scFoundation di migliorare la predittività di metodi già esistenti integrandolo in  DeepCDR  e  SCAD,  e  queste  architetture  modificate  sono  state comparate a quelle tipiche degli stessi modelli. I dati mostrano miglioramenti quasi ubiquitari nella capacità predittiva di riposta cellulare.

L9effetto  di  perturbazioni  geniche  può  essere  simulato  con  il  modello GEARS,  che  gli  autori  hanno  adattato  a  sfruttare  gli  embeddings  di scFoundation.  Gli  esperimenti  mostrano  miglioramenti  predittivi  sia  per perturbazioni  su  un  gene,  sia  per  perturbazioni  su  due  geni.  Inoltre,  il modello  GEARS  integrante  scFoundation  mostra  una  predizione  più accurata  delle  interazioni  geniche  sinergistiche  o  soppressive,  indicando una maggiore comprensione funzionale della relazione tra geni.

Al fine di annotazione del tipo cellulare, una piccola head neurale è stata posta dopo l9encoder di scFoundation e addestrata. Il metodo ha mostrato di  performare  meglio  di  tutti  gli  altri  testati,  principalmente  grazie  al discernimento più accurato di tipi cellulari rari.

Infine, nonostante l9impiego di metodi molto semplici, è stato mostrato come gli  embeddings  di  scFoundation  possano  identificare  moduli  di  geni  coregolati,  la  loro  cellulo-specificità,  e  relazioni  inter-geniche  intra-modulo funzionalmente rilevanti.

Alla luce della legge di potenza, è opportuna la costruzione di foundational models per scRNA più grandi e architetture efficienti. Le evidenze fornite indicano che  tali foundational models  possono  fornire miglioramenti predittivi  in  tutte  le  applicazioni  valutate.  Si  suggerisce  quindi  la  loro implementazione  in  altre  applicazioni,  come  test  di  diagnosi  precoce  e orologi dell9invecchiamento biologico.

#### Abstract

Foundation  models  have  become  key  to  Large  Language  Model  (LLM) architectures, leveraging the great corpus of text available on the internet. Advances in transcriptomic  foundation  models  (TFMs)  and  exponentially increasing data availability are contributing to the same trend in biology. Here  the  authors  describe  scFoundation,  the  largest  TFM  in  literature, having been pretrained on 50 million single-cell transcriptomic profiles and totalling  100  million  parameters.  A  transformer-like  asymmetric  encoderdecoder architecture was trained on a read-depth aware (RDA) de-masking task. The model has been applied to several downstream tasks, showing that its improved generalization yields better performance across gene, cell, and cell line  domains. State-of-the-art performance was shown for readdepth enhancement, drug response prediction, cell type annotation, gene perturbation response prediction, gene module and GRN inference.

### 1. Introduction

Recent  advances  in  Artificial  Neural  Network  (ANN)  design  have  led  to artificial  intelligence  breakthroughs  in  multiple  fields,  the  most  sizable  of which has been in natural language processing, with the advent of LLMs.

ANNs are designed to accurately synthesize the salient features of complex phenomena, such as natural language, protein folding, and gene expression profiles, by mimicking the biological neural networks that make up the brain. A vast, multilayered network of &lt;neurons= sequentially modifies the input via stacked, simple mathematical operations, resulting in a useful output, such as the answer to a question, a correctly folded protein, and an accurate cell-type annotation. Each neuron applies such simple mathematical transformations based on the current values of its specific parameters ,  which  are  computed  during  the  training  stage  and  are responsible for synthesizing meaning.

LLM  architectures  have  been  scaled  to  hundreds  of  billions  of  total parameter count by training on the great corpus of text available on the internet. This is to leverage the scaling power law [1], which has been shown to  robustly  remain  true  even  through  great  scale:  it  is  an  empirical observation  that  model  performance  can  be  reliably  improved  by  simply increasing total parameter count, independently of scale magnitude [Figure 1].  To  this  aim,  training  data  needs  to  be  scaled  accordingly,  as  does computational investment, which is measured in floating point operations per second (FLOPS).

Figure 1. The scaling power law in LLMs. Test loss decreases, improving performance,  at  a  constant  rate,  proportionally  to  increases  in  FLOPS, training tokens, and model parameters. From Kaplan J. et al. [1]

<!-- image -->

The power law is one of the crucial reasons why the LLM field has been consolidating on the pretraining of computationally expensive models with a very large parameter count, so called Foundational Models ,  which  are subsequently adapted to a variety of downstream tasks by lightly training them  further,  employing  much  less  incremental  compute  than  what9s required  during  pretraining.  This  benefits  the  model  by  providing  it  very nuanced, wide-reaching context on how language is structured and then adapting it to a specific task, such as reasoning or coding.

#### 1.1 ANNs in Biology

Modern omics are producing a never-before-seen scale of data, with the corpus of currently available data being in the trillions of tokens, the same magnitude of natural language data used for training LLMs [2]. This surfaces the possibility of using ANNs to process this data more effectively than how algorithmic methods could. To this aim, two strategies have been broadly investigated.

The first one involves the training of models by employing very high quality, labelled data for a specific downstream task. Homogenously labelled data is  inherently  scarce,  which  limits  model  size  drastically.  Many  single-cell downstream applications currently employ such models.

The  second  strategy  available  is  the  training  of  very  large  foundational models  on  unlabelled,  heterogeneous  data,  and  subsequently  adapting such model to disparate downstream tasks. The foundational model can therefore build internal representations of a broad biological phenomenon, such  as  gene  expression  networks,  by  processing  drastically  more abundant and rich data, which leads to increased parameter count, and exposure to more unique examples, improving performance and nuanced understanding.  Scarce,  high  quality  labelled  data  is  then  leveraged  to translate the nuanced internal representations that the model built into taskoptimised outputs.

In recent years, great advances for leveraging the latter strategy have been made in the field of scRNAseq data processing.

Cells are the fundamental functional units of gene transcription and gene expression regulation. As such, scRNAseq data offers granular insights into the  highly  complex  web  of  interactions  that  make  up  gene  regulatory networks (GRNs). Cells9 transcriptomic profiles are indeed a consequence of  complex  interactions  between  gene  products  and  other  regulatory factors,  which  means  that  the  very  observable  existence  of  any  given transcriptomic profile is in and of itself meaningful and informative. This is substantiated by the recent advances in genomic ANNs, namely Evo1 and Evo2, which were trained on existing genomic sequences of many species. These genomic models can predict how deleterious a given mutation is, based on how unlikely the model deems the mutation to be an existing allele in that species9 genome [3]. Indeed, a mutation is particularly unlikely if it is underrepresented  in  the  training  dataset,  which  means  that  it  has  been selected against by evolution due  to its  deleterious  consequences. Similarly, any given cell9s transcriptomic profile would be deemed likely by a transcriptomic model only if it follows all combinatorial logic that regulate GRNs. This implicitly models all interactions between gene products that would have any consequence on RNA.

Moreover, specific downstream tasks leveraging transcriptomic data, such as drug response tasks, currently leverage labelled bulk RNA sequencing (bulkRNAseq) data because it9s more abundant than scRNAseq data, but struggle to consider tissue cell heterogeneity, limiting predictive performance.

This makes scRNAseq data highly insightful for foundational and medical research applications.

#### 1.2 Single-cell Transcriptomic ANNs

Even  though  no  unified  scRNAseq  database  has  been  devised,  data  is increasing exponentially, as is the performance of ANN-based approaches to scRNA tasks [4, 5, 6]. Such models have been applied to a variety of downstream tasks.

One such task is the prediction of cancer drug response in single cells. A framework used to this aim is the SCAD model [4], which leverages an ANN

to combine unlabelled scRNAseq and labelled bulkRNAseq drug response data to produce single cell drug sensibility predictions in the form of the expected half-maximal inhibitory concentration ( !" )  of  that  drug for that cell, which is the drug concentration at which half of the cancer cells can9t proliferate.  Leveraging labelled bulkRNAseq allows the model to transfer drug  response  learnings  to  unlabelled,  generic  scRNAseq  data,  and focusing  on  single  cell  predictions  improves  performance  for  genetically heterogeneous cancers.

Other methods, such as DeepCDR [5], are designed to process multi-omics and a graph-based representation of the drug with a unified ANN to achieve better results, but the transcriptomic data used is from bulkRNAseq. This paper investigates whether such model could be improved by leveraging unlabelled scRNAseq  data, by processing it with a transcriptomic foundational model and subsequently feeding the output to the DeepCDR model.

Another  crucial  task  that  scRNAseq  data  granularity  can  aid  to  is  gene perturbation prediction. State-of-the-art performance in multi-gene perturbations  has  been  achieved  by  the  ANN  GEARS  model  [6],  which combines Gene Ontology (GO) data and labelled scRNAseq data to predict the transcriptomic profile that would result from knockout or knockdown of one or more genes. Perturbation-labelled scRNAseq data is very rare, which limits  parameter  size  and  data  heterogeneity.  To  solve  this,  the  paper investigates whether pre-processing such rare data with a transcriptomic foundational model, trained on much more abundant unlabelled scRNAseq data, can improve performance.

ANNs are increasingly being applied to cell type annotation too, yet until the release of this paper some algorithms based on statistical methods were still outperforming ANNs, most notably CellTypist [7].

Further downstream applications of RNA-based ANNs are proposed and investigated  in  this  study.  These  include  cell  clustering,  gene  module inference, and read depth enhancement, defined as imputation , which are currently widely performed with algorithmic and statistical methods.

As described, these downstream tasks can be performed by first training a very  large  foundation  model  rather  than  a  smaller,  task-specific  one.  In recent  years  many  such  TFMs  have  been  devised,  with  ever-increasing parameter count and training dataset size.

The  authors  of  the  paper  set  out  to  pretrain  the  largest  ever  TFM  for scRNAseq data, scFoundation, and subsequently applied such foundational model  to  downstream  tasks  by  employing  very  light  further  training, investigating potential performance increases over traditional methods.

### 2. Methods

The foundational model here described is an asymmetric transformer-like encoder-decoder  architecture,  trained  with  a  de-masking  task  in  a  read depth aware (RDA) manner.

Other than for these two tasks, scFoundation can be adapted to complete many  other  downstream  ones.  This  is  done  by  feeding  embeddings produced by the model into traditional methods, replacing typical inputs.

#### 2.1 The Transformer Architecture

The transformer [8] revolutionized the ANNs field, solving parallelization, which recurrent neural networks can9t provide, and long-range dependencies, which convolutional networks struggle with. This design was made  for  natural  language  processing,  which  is  sequential  in  nature, requiring positional context of the input elements, achieved via additional positional encodings. Such context is not needed for non-sequential data, such  as  transcriptomic  profiles,  a  pure  transformer  architecture  can therefore be leveraged to effectively model transcriptomic and other omics data, subsequently to solving the sparsity problem of transcriptomic profiles, as discussed later.

In the traditional transformer architecture [Figure 2], which processes words and other grammatical elements, tokens , that is the units of information that the  model  processes  and  produces,  are  discrete.  Each  unique  word, fraction of a word, or grammatical element can therefore be encoded to a value that is specific to it. Such unique values are termed embeddings and are defined mathematically as multidimensional vectors of #$%&amp;' dimensions obtained via a learned matrix, which makes up a small portion of the parameters of the model. All tokens are embedded parallelly and then passed to the encoder.

The encoder processes  the  embeddings  parallelly  into  contextualized representations of the input sequence. This is done by gradually modifying the values of these embeddings as they are passed through N layers, where simple matrix operations are performed. Each layer applies two different sequential sets of operations.

The first sublayer applies a multi-head self-attention mechanism. Here, h heads  are  computed  by  shrinking  the #$%&amp;' -dimensional  vectors  into h distinct ( #$%&amp;' //) -dimensional  vectors  via  a  matrix  multiplication  with h triplets of learned weight matrices. This produces three matrices per each h head,  termed  Q,  K  and  V.  Such ( #$%&amp;' //) -  dimensional  matrices  are used to quantify how much two given input tokens relate to each other (Q and K) and embeddings are modified based on their features V, with the following formula:

<!-- formula-not-decoded -->

where is  a  mathematical  function  that  transforms  the  similarity between each token ( ( ) into a probability distribution across all possible tokens.

This results in h ( #$%&amp;' //) -dimensional embeddings, which are concatenated  to  produce  the  final  attention  output,  which  is #$%&amp;' -dimensional. The final attention output is added back to the vectors that had originally entered the sublayer and normalized to stabilize training.

The second set of operations is a simple feed forward network (FFN). It applies the following mathematical transformation to all vectors:

<!-- formula-not-decoded -->

where and are trained parameters.

The  resulting  values  are  added  back  to  the  vectors  that  had  originally entered this sublayer, and normalization is applied.

Vectors are then fed to the next encoder layer, or, if finished, are passed to the decoder.

The decoder works similarly to the encoder, with M layers each applying three  sets  of  operations  parallelly  to  all  tokens.  In  natural  language processing, it is autoregressive, which means that it outputs tokens one by one, factoring into the next-token prediction also all previously outputted tokens.

The first sublayer performs the same attention mechanism of the encoder on the output tokens that have already been generated (if any). The second sublayer is unique to the decoder and performs multi-head cross-attention, where already-outputted tokens have their Q computed, and attend to each input token through the input tokens9 K and V values. The resulting attention matrix is added back to the vector that had originally entered the sublayer, and normalization is applied. The third sublayer is a typical FFN.

The vectors are then passed to the next decoder layer. When the last one is reached, a simple linear transformation projects the resulting tokens into vocabulary  size,  which  is  the  totality  of  discrete  tokens  that  the  initial embeddings matrix allows for. After being normalized via softmax, these values represent the predicted likelihood for every possible token to be the correct output. Generally, the most likely token, or one of the most likely, is selected as the final output. In natural language processing, this is repeated autoregressively until the response is complete, while for omics applications, such as TFMs, the output tokens (gene expression values) are computed all at once.

<!-- image -->

#### 2.2 scFoundation

Single-cell  transcriptomic  data  was  collected  from  public  databases  and further processed for quality control and data homogeneity. Only cells that showed more than 200 genes as expressed were kept. Raw mapping read

Figure 2. A typical transformer architecture. On  the  left:  one  encoder layer is represented, with a multi-head self-attention sublayer and an FFN sublayer. On the right: one decoder layer, with a multihead self-attention sublayer, a multi-head cross-attention sublayer, and  an  FFN.  A  final  linear projection is computed, then  softmax  probabilities are produced and the nexttoken  prediction  is  made. From Ashish Vaswani et al. [8

counts  were  selected,  and  where  not  available,  normalized  counts  were extracted and converted back into raw counts. Normalized counts that could not be converted into raw counts were left unchanged and kept.

The model was trained  to  predict  masked  genes9  expression  values,  by randomly masking 30% of the expression profile in every training example. In addition to this task, which is typical for TFMs, the model was also trained to  be  read-depth  aware.  To  this  aim,  binomial  sampling  was  used  to decrease the read depth of random datapoints in the training dataset, and the model was trained to predict the correct, original expression values for each gene from the downsampled data. For this, the model was provided two special tokens, T, which is the original, total count of reads, and S, which is the total count of reads of the downsampled data. The hidden dimension was set as #$%&amp;' = 768 .

The general transformer architecture as presented in Ashish Vaswani et al . [8] was broadly maintained in the design of scFoundation, with some key differences [Figure 3].

Firstly, the authors introduced non discrete tokens. Prior TFMs discretized tokens by binning them based on expression values, rather, scFoundation treats each gene9s expression as a continuous scalar, preserving accuracy. Scalars representing expression values of each gene are transformed into an -dimensional vector by matrix multiplications with learned parameters. The  resulting  vectors  are  further  transformed  into #$%&amp;' -dimensional vectors via matrix multiplication with a learned ( #$%&amp;' × # ) -dimensional matrix.  Input  embeddings  are  obtained  from  these  vectors  by  adding learned  encodings  specific  to  each  gene,  which  can  be  thought  of  as contextualizing the expression values to a specific gene and its characteristic features, such as biological process and cellular localization.

Secondly,  the  encoder  and  decoder  architectures  were  modified.  The encoder  was  designed  to  only  process  expressed  genes  (200-4000 vectors),  while  the  decoder9s  input  is  made  up  of  the  expressed  genes9 vectors coming from the encoder, zero-count and masked genes, which are represented  by  one  learned  embedding,  and  special  tokens  S  and  T (19264+2 vectors). As the vectors are passed through the decoder, insights uncovered by the encoder are implicitly  used  to  contextualize  all  genes9 interactions, producing a prediction of expression for all genes, including for the masked ones, at the read-depth selected. Gene expression values are predicted by passing each output vector through the same final layer and the same trained parameters, collapsing its dimensionality from #$%&amp;' to 1.

Figure 3. Model architecture of scFoundation. On the left: general outline of  the  model.  On  the  right,  from  top  to  bottom:  one  decoder  block,  one encoder block, the shared embedding block. From Hao M. et al. [2]

<!-- image -->

The asymmetric design of the encoder relative to the decoder allows to solve a fundamental issue of transcriptomic data, which is sparsity. At any given  time,  most  of  a  genome9s  potentially  transcriptionally  active  open reading frames are not transcribed or are transcribed but to a small enough extent to lead to zero reads, which makes zero values the most common datapoint in an expression profile. Feeding all such 19264 protein-coding genes to the encoder would increase computational needs exponentially, which  is  why  only  non-zero-count  genes  are  fed  to  the  encoder.  The decoder  is  instead  fed  all  19264  genes  to  reason  through  the  entire expression  space  and  ameliorate  dropout  inaccuracies,  but  the  typical transformer  calculations  are  approximated  to  limit  computational  needs through a Performer block architecture.

#### 2.3 Downstream applications

The TFM has been implemented into several already existing downstream task  frameworks.  Here,  I9ll  describe  how  such  frameworks  have  been adapted to process scFoundation embeddings for improved performance. I9ll  further  describe  read-depth  enhancement  applications,  which  can  be performed by the model natively, with no need for integration with other existing methods.

scFoundation embeddings were extracted at inference from different steps of the architecture, contextually to each downstream application.

Cell embeddings were extracted for cell-level analyses, by constructing the following 4 #$%&amp;' -dimensional vector. Expressed genes, S and T were run through the encoder, and the resulting vectors were extracted. Expressed genes9  mean  and  maximal  values  were  pooled,  per  each  dimension, resulting in two #$%&amp;' -dimensional vectors, one for max-pooling to extract salient features, and one for mean-pooling to extract a general representation of the cell9s state. The pooling-derived vectors and the S and T ones were concatenated, resulting in the final 4 #$%&amp;' -dimensional cell embedding.

Gene  embeddings  were  used  for  gene-level  analyses,  by  extracting decoder outputs before the final layer, which would otherwise collapse the 19624 #$%&amp;' -dimensional  vectors  into  19624  scalar  predictions  of  gene expression values. This approach was used to maintain richer representations of genes and co-expression profiles.

##### 2.3.1 Read-depth enhancement

To investigate the upscaling capacity of scFoundation, 10000 high readdepth  cells  were  selected  from  the  validation  dataset  and  downscaled following a binomial distribution, to 1%, 5%, 10%, and 20% (S) of the original reading depth (T). scFoundation was then used to upscale the expression profiles from S to T. Mean Relative Error (MRE) and Pearson Correlation Coefficient (PCC) were computed between the original expression values and  the  scFoundation-upscaled  ones  and  compared  to  raw  downscaled values.

The  enrichment  capabilities  of  the  model  were  further  investigated  by analysing how well its outputs could be used to cluster cells. A pancreatic islet dataset with 8500 cells with low and high read-depth data was used.

Several  imputation  methods,  namely  MAGIC  [9],  SAVER  [10],  scImpute [11], and scVI [12] were compared to scFoundation performance, clustering cells by applying to each method9s outputs Leiden9s algorithm. All methods but scFoundation were trained on downsampled data, and T was set to be 1,  2,  3,  4,  and  5  -fold  of  S.  Clustering  performance  was  measured  by Normalized Mutual Information (NMI) between ground truth and predicted clusters, Adjusted Rand Index (ARI) measuring pairwise agreement, and Silhouette Coefficient (SIL) measuring cluster separation quality.

Low  read-depth  handling  capability  were  compared  to  scVI  by  UMAP clustering the two models9 cell embeddings. The cells were obtained from the Zheng68K dataset. Notably, while scFoundation wasn9t trained on the dataset, scVI was. NMI, ARI and SIL were calculated.

##### 2.3.2 Drug response prediction

Bulk level and single-cell level drug response prediction performance was investigated.

Cell line (bulk level) Cancer Drug Response (CDR) prediction performance was  evaluated  on  the  two  datasets  Cancer  Cell  Line  Encyclopedia  and Genomics of Drug Sensitivity in Cancer, covering 223 drugs, 561 cell lines, and  31  cancer  types.  This  was  done  by  feeding  a  simplified  version  of scFoundation  cell  embeddings  to  an  existing  method,  DeepCDR.  The method is designed to merge MLPs-derived omics embeddings and Graph Neural  Network  -derived  drug  embeddings  to  predict !" values.  Drug structure representation was maintained, while the original transcriptomic MLP-derived output was replaced by scFoundation simplified cell embeddings.  These  were  derived  by  feeding  scFoundation  the  cell  line expression values, and subsequently max-pooling each dimension of the encoder-generated gene embeddings. No other omic data was used. T was set  as  equal  to  S,  and  MRE  between  predicted  and  actual !" was calculated. Low !" was interpreted as the cell line having sensitivity for the drug.

Drug-blind tests were performed by excluding all datapoints relating to a given drug. PCC was calculated for each drug and cancer type, as was PCC difference  between  standard  DeepCDR  predictions  and  scFoundationenhanced DeepCDR predictions.

Domain-shift to single-cell analysis was investigated through the method SCAD,  which combines drug-response labelled bulkRNA data and unlabelled scRNA data. It performs adversarial learning: a feature extractor produces  representations  of  both  bulkRNA  and  scRNA  data,  while  a discriminator  is  trained  to  recognize  whether  the  input  that  the  feature extractor received was from a single cell or a cell line. Extractor embeddings are processed by a predictor subnetwork to infer drug-response data. This means  that  the  training  task  that  SCAD  optimizes  for  is  drug  response prediction based on inter-domain features shared by bulkRNA and scRNA data,  given  that  bulkRNA-specific  features  would  be  recognized  by  the discriminator.

Cell embeddings from the scFoundation encoder were fed to the extractor module instead of raw gene expression values. Such cell embeddings were obtained by setting  both  T  and  S  as  the  total  read  count  in  the  case  of bulkRNA data, and by setting T as the maximal empirically measured total count, which is 10000. Model performance of the scFoundation-enhanced SCAD  was  quantified  on  four  drugs,  namely  sorafenib,  NVP-TAE684, PLX4720, and etoposide. Labelled bulkRNA data was available for all four, and  single-cell  labels  were  obtained  in  two  ways.  Sorafenib  and  NVPTAE6849s sensitivity was determined from EpiSen [13] scores, which were shown to correlate with drug responses. PLX4720 and etoposide sensitivity labels were assigned to untreated cell lines, while cells alive post-treatment were  assigned  the  resistance  label.  AUC  and  Spearman  correlation between predicted sensitivity and EpiSen scores were calculated. Lastly, the data was clustered relatively to the sensitivity label, and performance was measured with Clinski-Harabasz and SIL.

##### 2.3.3 Gene perturbation response prediction

scFoundation was also leveraged for single-cell gene perturbation response predictions,  by  feeding  decoder-derived  gene  embeddings  to  the  model GEARS. It uses a GO knowledge graph, a static gene co-expression graph, and  a  graph  encoding  perturbation  information.  The  static  gene  coexpression graph9s nodes were replaced by scFoundation gene embeddings, making the co-expression  graph  cell  specific.  Performance was evaluated on three different datasets, by calculating MSE on the 20 genes that had their expression values changes the most post-perturbation. This analysis was also performed for two-gene perturbations, with 0, 1, or 2 of these having been fed at the training stage.

Two-gene  perturbations  may  lead  to  non-linear  effects  due  to  gene interactions (GI). This was measured through magnitude, defined as:

<!-- formula-not-decoded -->

where + and , are coefficients that measure deviations from the purely combinatorial scenario of the expression changes , with error :

<!-- formula-not-decoded -->

PCC between real and predicted magnitude scores was calculated, both for the  default  and  the  scFoundation-enhanced  models.  The  20  two-gene perturbations  having  the  highest  magnitude  scores  were  predicted  to  be synergistic, while the lowest 20 were predicted to be suppressive.

##### 2.3.4 Cell type annotation

The performance of scFoundation in the cell annotation task was compared to the following methods: CellTypist, scBERT [14], scANVI [15], ACTINN [16], Scanpy [17], and SingleCellNet [18]. All methods were applied to the two separate datasets Zheng68K and Segerstolpe.

The last layer of the scFoundation encoder was fine-tuned, and two MLP layers with ReLU activation function were added to produce the cell type annotation.  A  weighted  cross  entropy  loss  was  used  to  handle  cell  type imbalances in the training dataset, where given cell types, and . cells per cell type , each cell type had a weight . defined as:

<!-- formula-not-decoded -->

where a maximum value of 50 avoids overcorrecting for rare cell types. Macro  F1  scores  were  computed  for  all  models,  and  scFoundation  and CellTypist embeddings were used to produce clusters that were observed on UMAP.

##### 2.3.5 Gene module and GRN inference

Gene embeddings from the scFoundation decoder were used for multiple functional analyses.

Gene  module  inference  was  performed  on  100  monocytes,  100  CD8+ cytotoxic  T  cells  and  100  B  cells  from  the  Zheng68K  dataset.  Gene embeddings were produced for each cell for the 495 most variable genes in the dataset. Each gene embedding was mean-pooled across all 300 cells. Leiden  algorithm  was  used  to  produce  clusters  by  setting  the  gene embeddings as nodes and similarity scores between them as edges. This yielded 34 modules. Marker modules were subsequently defined based on their  cell-type  -dependent  differential  expression  compared  to  averaged expression  values,  and  further  corroborated  through  gene  enrichment analysis via EnrichR [19].

Gene  network  representation  within  scFoundation  were  investigated  by selecting  the  most  differentially  expressed  gene  module  in  T  cells  and connecting each gene to the 5 genes with embeddings having the highest cosine similarity.

Gene  regulatory  network  (GRN)  inference  was  performed  on  SCENICderived  transcription  factor  (TF)  to  target-gene  pairs.  Gene  embeddings from scFoundation were produced for each pair, and cosine similarity was calculated. For each TF, the 1000 most similar pairs were kept and further filtered  for  TF-motif  enrichment  in  target  genes  via  SCENIC  module RcisTarget. TF differentially high activity was evaluated via SCENIC module auc\_cell, which performs AUC analyses of TF-targets enrichment in cells. Top-ranked  TFs  were  inferred  to  be  cell-specific  and  were  corroborated through previous research.

### 3. Results

The authors developed the largest pre-trained TFM in literature at the time of writing. It was trained with a masked-genes prediction and RDA task, and several  downstream  applications  were  performed  with  no  to  light  finetuning.

Scaling  laws  proved  to  persist  through  increased  scale,  with  MSE  loss steadily decreasing proportionately to parameter count (3M, 10M, 100M) and  logarithmically  to  FLOPS  [Figure  4a].  The  larger  model,  100M scFoundation, achieved the lowest MSE (0.30), and the best performance in cell type annotation (macro-F1 score 0.89) among the three models.

#### 3.1 Read-depth enhancement

Upscaling capabilities of scFoundation were investigated by operating on a 10000 cells dataset, which was excluded from training. Expression data for these  cells  was  downsampled  to  1%,  5%,  10%  and  20%  of  the  original value,  and  the  downsampled  data  was  passed  through  the  model  to produce upscaled predictions. Upscaled data showed considerably lower MRE and higher PCC compared to raw downsampled data, especially so for  very  low  count  samples  (at  1%  downsampling,  scFoundation  almost halved MRE and more than doubled PCC) [Figure 4b].

Imputation  performance  was  compared  to  many  other  methods,  see methods 2.3.1. A fold-increase of 1, 2, 3, 4, and 5 of T to S was tested in scFoundation [Figure 4c]. Despite no fine-tuning, scFoundation outperformed  all  methods  from  T/S  &gt;  2,  with  no  measurable  additional benefits  for  T/S  &gt;  3.5.  UMAP  visualization  of  Leiden  clustering  for  all methods and scFoundation T/S = 5 showed improved distinctive clustering, and  colour-matching  cells  to  clustering  performed  on  non-downsampled data  showed  scFoundation  predictions  mapped  substantially  better  to reference cell clusters [Figure 4d]. Finally, scFoundation cell embeddings improved clustering over using raw expression values on low-read depth cells from the Zheng68K dataset. This was achieved by better clustering of rare cell types, namely by discerning memory T cells from other T cells, and CD14 monocytes from CD34 cells [Figure 4e]. It outperformed scVI on the same task [Figure 4f].

<!-- image -->

Figure 4. Read-depth enhancement clustering. a) FLOPS scaling law. b) Enhancement performance compared to raw downscaled data. c) Imputation performances. d) UMAP  cluster visualization, annotation mapping to reference. e) UMAP cluster on Zheng68K cells. F) Clustering performance on Zheng68K. From Hao M. et al. [2]

<!-- image -->

#### 3.2 Drug response prediction

The typical bulk-level DeepCDR method was enhanced with scFoundation cell embeddings. Most drugs and all cancer types showed improved PCC values over typical DeepCDR (mean increase of 0.5), and drug-blind PCC increases were as high as 0.66 (for drug PHA-793887), showing considerable  generalization  capabilities.  It  was  observed  that  targeted therapies -related drugs had lower PCC increases, potentially due to their mechanism of action being related to specific mutation states, which are less well represented by expression profiles. GSEA on drugs that were not in  the  training  set  was  performed,  showing  that  scFoundation-enhanced DeepCDR  correctly  associated  doxorubicin  sensitivity  to sphingolipid signalling pathway enrichment, and vorinostat sensitivity to  mTOR signalling pathway enrichment.

SCAD  single-cell  drug  response  was  enhanced  with  scFoundation  cell embeddings  too.  Four  challenging  drugs  were  selected  from  a  previous study, namely sorafenib, NVP-TAE684, PLX4720, and etoposide. All but etoposide  showed  drastic  increases  in  AUC  over  baseline  (0.2  to  0.3) [Figure  5b].  Sensitivity  ground-truth  in  sorafenib  and  NVP-TAE684  was quantified via the EpiSen score (see methods 2.3.2). Spearman correlation between scFoundation-ranked probabilities and EpiSen-ranked scores was considerably higher than baseline (0.24 to 0.56 for NVP-TAE684, and -0.06 to  -0.55  for  sorafenib)  [Figure  5c].  Interestingly,  PCA  was  performed  on scFoundation embeddings  and raw data, with the former showing decreased  linearity,  indicating  richer  representations  [Figure  5d].  Lastly, clustering  was performed by setting sensitivity as the label, on both raw expression data and scFoundation embeddings. The latter  showed improved CH and SIL scores [Figure 5e].

Figure  5. Drug  response  prediction  tasks. b)  AUC  performance  for scFoundation  and  baseline  on  the  four  drugs.  c)  Spearman  correlation between  scFoundation  or  baseline  rank  to  EpiSen  rank.  d)  PCA  on scFoundation and baseline. e) Sensitivity clustering scores for scFoundation and baseline. From Hao M. et al. [2]

<!-- image -->

#### 3.3 Gene perturbation response prediction

Gene  embeddings  from  scFoundation  were  integrated  into  the  gene perturbation  response  GEARS  model.  Performance  was  tested  on  three perturbation datasets, and MSE on the top 20 differentially expressed genes was calculated. The scFoundation-enhanced model achieved lower MSE on  one-gene  perturbations  and  two-gene  perturbations  compared  to baseline [Figure 6b]. Furthermore, a higher proportion of predictions fell in the 45 th to 55 th percentile of real observations compared to baseline GEARS [Figure 6c], indicating more balanced, plausible results.

GI classification was performed by calculating magnitude score ranking, see methods 2.3.3.  PCC between predicted and true magnitude scores was higher in scFoundation compared to baseline GEARS (0.18 vs 0.01) [Figure 6e]. Two-perturbation predictions were ranked by magnitude scores, and the  top  20  pairs  were  defined  as  synergistic,  and  the  bottom  20  as suppressive.  A  Venn  diagram  was  constructed  to  represent  the  data, showing improved predictive performance of scFoundation over baseline GEARS, for both synergistic and suppressive perturbations [Figure 6f].

Figure  6. Perturbation  prediction  tasks. b)  GEARS  gene  perturbation performances  for  scFoundation  and  baseline.  c)  GEARS  perturbation predictions within 45 th to 55 th percentile of real predictions, for scFoundation and baseline. e) GI magnitude scores. f) GEARS synergy and suppressor label prediction for scFoundation and baseline, compared to ground truth. From Hao M. et al. [2]

<!-- image -->

#### 3.4 Cell type annotation

Cell  type  annotation  was  performed  by  adding  a  2-layer  head  after  the scFoundation  encoder.  Performance  was  tested  on  the  Zheng68K  and Segerstolpe datasets, and compared to several models, see methods 2.3.4. Higher macro F1 scores were achieved by scFoundation on both datasets (0.736 and 0.914 on Zheng68K and Segerstolpe respectively, compared to second-best scores by CellTypist being 0.725 and 0.812), benefitting from improved  performance  on  rare  cell  types  and  improved  recall  (correctly identified more true positives), despite decreased precision (predicted more false positives), over CellTypist.

#### 3.5 Gene module and GRN inference

Gene module and regulatory network inference was investigated on 300 immune cells from the Zheng68K dataset. Gene embeddings of the 495 most  variable genes  were  inferred, and  their cosine similarity  was computed.  Leiden  clustering  was  then  performed,  resulting  in  34  gene modules. Differentially expressed gene modules were enriched, showing that some were cell-type specific. This suggests that the gene embeddings correctly model functional information. A T-cell -specific gene module was identified  and  further  analysed,  showing  that  gene  embeddings  of  CD8 protein chains CD8A and CD8B had great similarity, while myeloid-specific S100A8 showed low similarity. This suggests that gene embeddings further model functionally relevant within-network gene relations.

GRN inference was implemented by post-processing SCENIC model output with scFoundation embedding  similarity, motif-enrichment,  and  AUC analyses (see methods 2.3.5). Cell-type -specific transcription factors were correctly identified for all three cell groups (KLF6 for monocytes [20], SPIB for B-cells [21], MXD4 for CD8+ T-cells [22]) .

### 4. Discussion

The RDA nature of scFoundation9s training task proved to be effective in tackling  batch-size  effects  and  aiding  in  generalization,  as  shown  by improved  performance  on  clustering  cells  from  diverse  batches  and imputation  tasks.  Additionally,  power  law  performance  increases  were maintained despite unprecedented TFM scale, suggesting bigger models should be trained in the future to further leverage scaling laws.

The asymmetric encoder-decoder architecture was validated for effectively handling sparsity in a computationally efficient yet minimally lossy manner, given  state-of-the-art  performances  across  all  downstream  applications tested.

Notably, no to little fine tuning was required for all downstream tasks, and zero-shot implementations of scFoundation still showed superior performance to methods trained on the validation dataset. For downstream task applications, the authors suggest that gene and cell embeddings be used, as they are more informative than inferred expression profiles.

Substantial  evidence  was  produced  for  single-cell  TFMs  to  accurately model bulkRNA data, given state-of-the-art performance of scFoundationaugmented  SCAD  and  DeepCDR  cell  line  representation,  suggesting further  research  in  inter-domain  analyses  is  advisable.  Furthermore,  the authors suggest the implementation of other multi-omics data, specifically citing ATAC-sequencing.

The state-of-the-art performance and lack of dataset-specific training needs strongly suggest that the improved generalization that TFMs benefit from outperforms  task-specific  models,  informing  future  research.  I  suggest TFMs applications to additional downstream tasks should be investigated, including  for  early  diagnosis  testing  and  age  prediction  through  aging clocks.

#### References

1.  Kaplan J, McCandlish S, Henighan T, et al. Scaling laws for neural language models. arXiv. Preprint posted online January 23, 2020. doi:10.48550/arXiv.2001.08361
2.  Hao  M,  Gong  J,  Zeng  X,  et  al.  Large-scale  foundation  model  on single-cell  transcriptomics.  Nat  Methods.  2024;21(8):1481-1491. doi:10.1038/s41592-024-02305-7
3.  Brixi G, Durrant MG, Ku J, et al. Genome modeling and design across all  domains  of  life  with  Evo  2.  bioRxiv.  Preprint  posted  online February 21, 2025. doi:10.1101/2025.02.18.638918
4.  Zheng Z, Chen J, Chen X, et al. Enabling Single-Cell Drug Response Annotations  from  Bulk  RNA-Seq  Using  SCAD.  Adv  Sci  (Weinh). 2023;10(11):e2204113. doi:10.1002/advs.202204113
5.  Liu  Q,  Hu  Z,  Jiang  R,  Zhou  M.  DeepCDR:  a  hybrid  graph convolutional network for predicting cancer drug response. Bioinformatics. 2020;36(Suppl\_2):i911-i918. doi:10.1093/bioinformatics/btaa822
6.  Roohani Y, Huang K, Leskovec J. Predicting transcriptional outcomes  of  novel multigene  perturbations  with  GEARS.  Nat Biotechnol. 2024;42(6):927-935. doi:10.1038/s41587-023-01905-6
7.  Domínguez Conde C, Xu C, Jarvis LB, et al. Cross-tissue immune cell  analysis  reveals  tissue-specific  features  in  humans.  Science. 2022;376(6594):eabl5197. doi:10.1126/science.abl5197

8.  Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need. arXiv. Preprint posted online June 12, 2017. doi:10.48550/arXiv.1706.03762
9.  van Dijk D, Sharma R, Nainys J, et al. Recovering Gene Interactions from Single-Cell Data Using Data Diffusion. Cell. 2018;174(3):716729.e27. doi:10.1016/j.cell.2018.05.061
10.  Huang M, Wang J, Torre E, et al. SAVER: gene expression recovery for single-cell RNA sequencing. Nat Methods. 2018;15(7):539-542. doi:10.1038/s41592-018-0033-z
11.  Li WV, Li JJ. An accurate and robust imputation method scImpute for single-cell  RNA-seq  data.  Nat  Commun.  2018;9(1):997.  Published 2018 Mar 8. doi:10.1038/s41467-018-03405-7
12.  Lopez R, Regier J, Cole MB, Jordan MI, Yosef N. Deep generative modeling for single-cell transcriptomics. Nat Methods. 2018;15(12):1053-1058. doi:10.1038/s41592-018-0229-2
13.  Kinker GS, Greenwald AC, Tal R, et al. Pan-cancer single-cell RNAseq  identifies  recurring  programs  of  cellular  heterogeneity.  Nat Genet. 2020;52(11):1208-1218. doi:10.1038/s41588-020-00726-6
14.  Wang W, Yang F, Fang Y, et al. scBERT: a large-scale pretrained deep language model for cell type annotation of single-cell RNA-seq data. bioRxiv. Preprint posted online December 7, 2021. doi:10.1101/2021.12.05.471261
15.  Xu  C,  Lopez  R,  Mehlman  E,  Regier  J,  Jordan  MI,  Yosef  N. Probabilistic harmonization and annotation of single-cell transcriptomics  data  with  deep  generative  models.  Mol  Syst  Biol. 2021;17(1):e9620. doi:10.15252/msb.20209620
16.  Ma F, Pellegrini M. ACTINN: automated identification of cell types in single  cell  RNA  sequencing.  Bioinformatics.  2020;36(2):533-538. doi:10.1093/bioinformatics/btz592
17.  Wolf FA, Angerer P, Theis FJ. SCANPY: large-scale single-cell gene expression  data  analysis.  Genome  Biol.  2018;19(1):15.  Published 2018 Feb 6. doi:10.1186/s13059-017-1382-0
18.  Tan  Y,  Cahan  P.  SingleCellNet:  A  Computational  Tool  to  Classify Single  Cell  RNA-Seq Data Across Platforms and Across Species. Cell Syst. 2019;9(2):207-213.e2. doi:10.1016/j.cels.2019.06.004
19.  Chen EY, Tan CM, Kou Y, et al. Enrichr: interactive and collaborative HTML5  gene  list  enrichment  analysis  tool.  BMC  Bioinformatics. 2013;14:128.  Published  2013  Apr  15.  doi:10.1186/1471-2105-14128
20.  Date D, Das R, Narla G, Simon DI, Jain MK, Mahabeleshwar GH. Kruppel-like transcription factor 6 regulates inflammatory macrophage polarization. J Biol Chem. 2014;289(15):10318-10329. doi:10.1074/jbc.M113.526749

21.  Willis SN, Tellier J, Liao Y, et al. Environmental sensing by mature B cells  is  controlled  by  the  transcription  factors  PU.1  and  SpiB.  Nat Commun. 2017;8(1):1426. Published 2017 Nov 10. doi:10.1038/s41467-017-01605-1
22.  Vasilevsky NA, Ruby CE, Hurlin PJ, Weinberg AD. OX40 engagement  stabilizes  Mxd4  and  Mnt  protein  levels  in  antigenstimulated  T  cells  leading  to  an  increase  in  cell  survival.  Eur  J Immunol. 2011;41(4):1024-1034. doi:10.1002/eji.201040449

## Appendix 3 TFM-enhanced aging clocks

A substantial research gap emerged for transcriptomic aging clocks.

Methylomic aging clocks have been shown to benefit from training taskspecific  heads  attached  to  a  pre-trained  epigenetic  foundational  model, rather than directly training a task-specific model [23]. No scientific study has been published yet to investigate whether the same benefits can be accessed for transcriptomic aging clocks, be it bulk or single cell data.

Methylomic data fundamentally measures a portion of cellular transcriptomic regulation. Additionally, age prediction is a continuous scalar cell  annotation  prediction  problem,  which  this  and  other  studies  showed TFM integration to improve performance for. I therefore argue that TFMs should be investigated in their capacity to improve age prediction beyond the  limits  of  methylomic  clocks,  both  in  the  case  of  scRNA  data  and bulkRNA data.

To this aim, an MLP head may be introduced after the TFM encoder, or just before the gene expression prediction layer of the decoder.

Each #$%&amp;' dimension value would be pooled across all vectors, resulting in a single #$%&amp;' -dimensional vector. A ReLU-activated layer would reduce dimensionality to h dimensions, with a ( #$%&amp;' ×/) -dimensional learnable matrix, then an additional linear transformation would produce a continuous scalar predicting age, with a (/ × 1) -dimensional learnable matrix. Furthermore, the last layer before the MLP head may not be frozen, to finetune it to the task. This description is analogous to what the authors did for the cell-type annotation task described.

Both the TFM-enhanced model and other task-specific models available in literature, such as scImmuAging [24] and DeepQA [25], would be trained on the same age-labelled dataset. I would expect improved performance over the non-TFM-enhanced model, especially for challenging samples, given that TFM embeddings would supposedly provide increased generalization and nuanced understanding. Tissue-specific and cross-tissue clocks may be  investigated,  and  more  complex  Mixture  of  Experts  (MoE)  head architectures  may  be  appropriate,  given  recent  works  showing  improved performance [25].

The implementation of TFMs for age prediction may represent a turning point in aging clock research. Transcriptomic aging clocks are currently less performant than methylomic ones in predicting chronological age [26], yet in principle transcriptomic data implicitly encodes all methylomic data. Such methylome-derived  data  is  partially  obscured  by  concurrent  short-term regulatory processes, which are less defining of the age identity of a cell and  therefore  introduce  noise  into  the  transcriptomic  profile.  It  may  be argued that a sizeable enough TFM could discern such patterns, providing implicit yet comparable information clarity on the methylomic state of the cell.  In  such  a  scenario,  the  TFM  would  further  benefit  from  modelling regulatory processes that define the age identity of a cell without acting on the methylome, providing higher quality, more granular internal representations of the age state, hence improved prediction performance.

## Appendix 3 References

23.  Ying K, Song J, Cui H, et al. MethylGPT: a foundation model for the DNA methylome. bioRxiv. Preprint posted online November 3, 2024. doi:10.1101/2024.10.30.621013
24.  Li  W,  Zhang  Z,  Kumar  S,  et  al.  Single-cell  immune  aging  clocks reveal inter-individual heterogeneity during infection and vaccination. Nat Aging. 2025;5(4):607-621. doi:10.1038/s43587-025-00819-z
25.  Qi H, Zhao H, Li E, et al. DeepQA: A Unified Transcriptome-Based Aging Clock Using Deep Neural Networks. Aging Cell. 2025;24(5):e14471. doi:10.1111/acel.14471
26.  Jansen R, Han LK, Verhoeven JE, et al. An integrative study of five biological clocks in somatic and mental health. Elife. 2021;10:e59479. Published 2021 Feb 9. doi:10.7554/eLife.59479

### nature methods

## Article

[https://doi.org/10.1038/s41592-024-02305-7](https://doi.org/10.1038/s41592-024-02305-7)

## Large-scale foundation model on single-cell transcriptomics

Received: 2 June 2023

Accepted: 10 May 2024

Published online: 6 June 2024

Check for updates

Minsheng Hao 1,2 , Jing Gong 2 , Xin Zeng 2 , Chiming Liu 2 , Yucheng Guo 2 , Xingyi Cheng 2 , Taifeng Wang 2 , Jianzhu Ma 3,4 , Xuegong Zhang 1,5 &amp; Le Song 2,6

Large pretrained models have become foundation models leading to breakthroughs in natural language processing and related fields. Developing foundation models for deciphering the 'languages' of cells and facilitating biomedical research is promising yet challenging. Here we developed a large pretrained model scFoundation, also named 'xTrimoscFoundation α ' , with 100 million parameters covering about 20,000 genes, pretrained on over 50 million human single-cell transcriptomic profiles. scFoundation is a large-scale model in terms of the size of trainable parameters, dimensionality of genes and volume of training data. Its asymmetric transformer-like architecture and pretraining task design empower effectively capturing complex context relations among genes in a variety of cell types and states. Experiments showed its merit as a foundation model that achieved state-of-the-art performances in a diverse array of single-cell analysis tasks such as gene expression enhancement, tissue drug response prediction, single-cell drug response classification, single-cell perturbation prediction, cell type annotation and gene module inference.

<!-- image -->

Large-scale pretrained models are revolutionizing research in natural language processing related fields and becoming a new paradigm toward general artificial intelligence. These models trained on huge corpora become foundation models due to their fundamental roles in leading breakthroughs in many downstream tasks and their ability in discerning patterns and entity relationships within language 1 . In life sciences, living organisms have their underlying 'languages'. Cells, the basic structural and functional units of the human body, constitute 'sentences' composed of a myriad of 'words' such as DNA, RNA, proteins and gene expression values. An intriguing question is: Can we develop foundation models of cells based on massive cell 'sentences'?

gene-gene co-expression and interaction within cells. With the efforts of the Human Cell Atlas (HCA) 3 and many other studies 4-8 , the data scale is exponentially growing 9 . With about 20,000 protein-coding genes across millions of cells, the observed gene expression values scale to a magnitude of trillion 'tokens' (Supplementary Table 1), which is comparable to the volume of natural language texts used to train large language models (LLMs) such as generative pretrained transformers. This provides the foundation for us to pretrain a large-scale model to extract complex, multifaceted internal patterns of cells in a manner similar to LLMs learning human knowledge from huge archives of natural language texts.

Single-cell RNA sequencing (scRNA-seq) data, also known as single-cell transcriptomics, offer high-throughput observations into cellular systems 2 , providing massive archives of transcriptomic sentences of all types of cells for developing foundation models. In transcriptomic data, gene expression profiles depict complex systems of In the LLM pretraining 10,11 , the growth in both model and data scale is critical for constructing foundation models that can effectively mine intricate multilevel internal relationships. Recently, progress has been made in pretraining models on single-cell data 12-15 , but creating large-scale foundation models still presents unique challenges. First, the

1 MOE Key Laboratory of Bioinformatics and Bioinformatics Division, BNRIST, Department of Automation, Tsinghua University, Beijing, China. 2 BioMap, Beijing, China. 3 Department of Electrical Engineering, Tsinghua University, Beijing, China. 4 Institute for AI Industry Research, Tsinghua University, Beijing, China. 5 School of Life Sciences and School of Medicine, Center for Synthetic and Systems Biology, Tsinghua University, Beijing, China. 6 Mohamed bin Zayed University of Artificial Intelligence, Abu Dhabi, UAE. e-mail: majianzhu@tsinghua.edu.cn; zhangxg@tsinghua.edu.cn; songle@biomap.com gene expression pretraining data need to encompass a landscape of cells across different statuses and types. Currently, most scRNA-seq data are loosely organized, and a comprehensive and complete database is still lacking. Second, when modeling each cell as a sentence and each gene expression value as a word, the nearly 20,000 protein-coding genes make the 'sentence' exceptionally long, a scenario that traditional transformers struggle to handle 16,17 . Existing work often had to restrict their models to a small list of selected genes. Third, scRNA-seq data across different techniques and laboratories exhibit high variance in sequencing read depth. Unlike random noises due to technical effects such as contamination that would be reduced by training on large-volume data, read depth is not random and its variation hinders models from learning uniform and meaningful cell and gene representations.

In this Article, we addressed these challenges and designed a large-scale foundational model scFoundation of 100 million parameters working on ~20,000 genes. We collected the scRNA-seq dataset with over 50 million gene expression profiles for pretraining. We developed an asymmetric architecture for scRNA-seq data to accelerate the training process and improve model scalability. We designed a read-depth-aware (RDA) modeling pretraining task that enables scFoundation to not only model the gene co-expression patterns within a cell but also link the cells with different read depths.

To verify the ability of scFoundation, we conducted experiments on multiple downstream tasks, including cell clustering, drug response prediction on bulk data, single-cell drug response classification, single-cell perturbation prediction and cell type annotation. Recognizing the computational burden for users to fine-tune the large-scale models, we achieved advanced performance by adapting non-fine-tuned or light-fine-tuned scFoundation's context embeddings to the corresponding downstream models. We also showcased using gene embeddings from scFoundation to infer the gene modules and gene regulation networks. All results demonstrated the power and value of scFoundation for transcriptomics data analyses and as foundation functions in facilitating biology and medical task learning. The work explored and pushed the boundaries of foundation models in the single-cell field.

####### Results

####### The scFoundation pretraining framework

We developed scFoundation to model 19,264 genes with ~100 million parameters pretrained on over 50 million scRNA-seq data. This is a large-scale model of large parameter size, gene coverage and data scale in the single-cell field. The ability to efficiently train such a model was empowered by three key parts in our pretraining frameworks: model design, pretraining tasks and data collection (Fig. 1a).

We developed xTrimoGene, a scalable transformer-based model with strategies for both algorithmic efficiency and engineering acceleration 18 . It included an embedding module and an asymmetric encoderdecoder structure. The embedding module converted continuous gene expression scalars into learnable high-dimensional vectors ensuring full retention of raw expression values, which was a notable improvement over the discretized values used in previous models 13,19 . The asymmetric encoder-decoder architecture had a similar form to the masked autoencoder 20 model in computer vision but was designed to accommodate the high sparsity of scRNA-seq data, achieving efficient learning of all gene relationships without any selection. Moreover, we incorporated a variety of large-scale model training optimization techniques in the model deployment to ensure efficient training (Methods).

We designed a pretraining task called the RDA modeling, an extension of masked language modeling 21 , by considering the high variance of read depth in large-scale data. In RDA modeling, the model predicted the masked gene expression of a cell on the basis of its context genes. The context was from a duplication or a low-read-depth variant of that cell's gene expression profile (Methods). We treated the total count as one cell's read depth and defined two total counts indicators: T ('target') and S ('source'), for the total counts of the raw and the input samples, respectively. We randomly masked both zero- and nonzero-expressed genes in the input sample and recorded their index. Then the model took the masked input sample and two indicators to predict the expression value of the raw sample at the masked index (Fig. 1b). This enabled the pretrained model not only to capture the gene-gene relationship within the cell but also to harmonize the cell with different read depths. When used for inference, we feed the cell's raw gene expression to the pretraining model and set the T higher than its total counts S to generate gene expression values with enhanced read-depth. We conducted several ablation experiments with cell clustering performance as an evaluation to show the advantage of our model architecture and pretraining task design (Methods and Supplementary Note 1).

We constructed a comprehensive single-cell dataset by collecting data from all publicly available single-cell resources, including Gene Expression Omnibus (GEO) 22 , Single Cell Portal, HCA 3 , human Ensemble Cell Atlas (hECA) 4 , Deeply Integrated human Single-Cell Omics data (DISCO) 7 , European Molecular Biology Laboratory-European Bioinformatics Institute database (EMBL-EBI) 8 and so on. We aligned all data to a gene list composed of 19,264 protein-coding and common mitochondrial genes, as identified by the HUGO Gene Nomenclature Committee 23 . After data quality control (Methods), we got over 50 million human scRNA-seq data for pretraining. The abundant data sources made the pretraining dataset rich in biological patterns. Anatomically, it spans over 100 tissue types across various diseases, tumors and normal states (Fig. 1a), encompassing almost all known human cell types and states.

After pretraining, we applied the scFoundation model to multiple downstream tasks (Fig. 1c). The outputs of the scFoundation encoder were pooled into cell-level embeddings, which were used for cell-level tasks including clustering (within and across datasets), bulk and single-cell level drug response prediction and cell type annotation. The outputs of the scFoundation decoder were gene-level context embeddings, which were used for gene-level tasks such as perturbation prediction and gene module inference.

####### Scalable read-depth enhancement model without fine-tuning

In our study, we found a power-law decline in validation loss correlating with increased model size and computation, which is called 'scaling law' 10,24 in LLMs. We trained three models with parameter sizes of 3, 10 and 100 million, respectively, and recorded their losses on the validation dataset. As the model parameters and the total number of floating-point operations (FLOPs) increased, the loss on the validation dataset exhibited a power-law decline. We then estimated the performance of various scale xTrimoGene architecture models with parameter sizes equivalent to previous transformer-based models 13-15 , and compared with scVI 25 (Supplementary Note 2). The scFoundation model with 100 million parameters surpassed all other models (Fig. 2a). We further evaluated our three models on a cell-type annotation task and observed the trend that the performance was improved as the model size increased (Supplementary Table 2).

The RDA modeling enables scFoundation to enhance the read depth of the input cell by setting T as a higher number than S . We assessed this ability on independent test data of 10,000 cells randomly sampled from the validation dataset. We downsampled the total counts to 1%, 5%, 10% and 20% of the original profiles, generating four corresponding datasets with varying total count fold changes. For each dataset, we utilized non-fine-tuned scFoundation to enhance the cells with low total counts by setting the desired total counts T as the reciprocal of the sampling rate. We measured the mean absolute error (MAE), mean relative error (MRE) and Pearson correlation coefficient (PCC) between predicted and actual nonzero gene expressions. As shown in Fig. 2b and Supplementary Fig. 1, scFoundation demonstrated a notable reduction of half the MAE and MRE from the downsampled data even when the downsampling rate was below 10%. These observations showed the ability of scFoundation to enhance gene expressions in scenarios even with extremely low total counts.

a

Fig. 1 | The schematic overview of the pretraining framework. a , Fifty million single-cell gene expression profiles were collected, covering tumor and nontumor cells from various tissues. These data were used for the RDA modeling task to pretrain the model. In the RDA task, the input consists of the masked gene expression vector and two total count indicators ( T and S ). The output is the predicted expression value for all genes, and the loss is computed at the masked positions. b , Outline of the pretraining process. A raw gene expression vector serves as a training sample. A hierarchical Bayesian downsampling strategy generates the input sample. The gene expression total counts ( T and S ) of the raw and input samples are computed. Values in the input sample are randomly masked. The scalar expression values are converted into embeddings. Only

<!-- image -->

We then compared scFoundation with imputation methods including MAGIC 26 , SAVER 27 , scImpute 28 and scVI 25 on a human pancreatic islet dataset processed by SAVER. This dataset contained manually generated downsampled gene expression profiles and their corresponding reference data. For scFoundation, we obtained five sets of cell embeddings from the non-fine-tuned encoder by setting T as the different folds of S ranging from 1 to 5. For other methods, we first used the downsampled data to train the methods, and then got imputed cell embeddings and gene expression from scVI and other methods, respectively. The ground truth cluster labels were obtained from the reference data (Methods). For evaluating clustering accuracy, we employed metrics including normalized mutual information (NMI), adjusted Rand index (ARI) and silhouette coefficient (SIL) (Supplementary Note 3). The clustering performance obtained from the downsampled data was used as the baseline.

scFoundation outperformed both the baseline and scImpute in all metrics when T was set equal to S (fold change of 1; Fig. 2c) but it exhibited lower performance compared with smaller models like SAVER. This phenomenon wherein the read depth is unaltered has also been reported in a recent work 29 . As the T / S fold increased, we observed a quick jump in scFoundation's performance that surpassed all other methods. Its performance reached a plateau on higher T / S folds, indicating the cell embeddings were not sensitive to the value of T higher than 3.5 S . We visualized the scFoundation embedding results at fold change 5 and results from other methods (Fig. 2d). Notably, scFoundation's cell embeddings exhibited more distinctive cluster boundaries compared with the baselines and other methods. Furthermore, we clustered the results of all methods and applied the cluster labels back onto the reference Uniform Manifold Approximation and Projection (UMAP). Other methods showed mixed labels, especially for cluster 0 in the ground truth. scFoundation was the only method that aligned all cell cluster assignments consistently with the reference results.

embeddings corresponding to nonzero and nonmasked values (including T and S ) are fed into the model encoder. The output embeddings of the encoder are then combined with mask and zero embeddings and fed into the decoder. Also, the encoder output can be pooled to generate a cell embedding for downstream usage. The decoder output embeddings are projected to the gene expression value via a shared MLP layer. The regression loss between the predicted and raw sample's gene expression values is computed. c , The pretraining embeddings can be leveraged as substitutes for the gene expression profiles, facilitating downstream tasks such as cell clustering, drug response prediction, single-cell level perturbation prediction, cell-type annotation, gene module inference and so on.

We then applied scFoundation to the Zheng68K dataset 30 , comprising about 60,000 human peripheral blood mononuclear cells sequenced on an early 10x Chromium platform. Each cell had about 500 expressed genes and fewer than 2,000 total reads, making cell type distinction challenging 13,31 (Supplementary Fig. 2). scFoundation was used without fine-tuning to enhance cell embeddings by setting the T value as 10,000. The resulting UMAP plots showed that scFoundation effectively separated memory T cells from other T cells and distinguished CD14 monocytes and CD34 cells better (Fig. 2e). We compared our results with scVI trained on the same dataset. Both methods outperformed the raw data in clustering. While their NMI and ARI metrics were similar, scFoundation had a higher SIL score, showing its generalization ability in non-fine-tuning mode (Fig. 2f).

Fig. 2 | Performance of read-depth enhanced clustering results. a , Training loss under different parameter sizes and FLOPs. The dots noted as other models' names were the performance of various scale xTrimoGene architecture models with parameter sizes equivalent to other models. The scVI model achieved an MSE of 0.98. Since it was not a transformer-based model and not applicable to plot on the figure. b , Evaluation of read-depth enhancement performance on the unseen dataset. MREs of nonzero genes and PCCs of all genes were used to evaluate the recovered gene expression performance. Lower MREs and higher PCCs indicate better performance. c , Comparison of the scFoundation model with other imputation methods based on cell clustering metrics. The x axis represents the fold change between the desired total counts and the input total

<!-- image -->

counts, and the y axis represents the score. d , UMAP plots of cell embeddings generated by different methods. The left plot shows the reference UMAP plot obtained using raw gene expression, with colors indicating cell clusters. The upper-right plots display clustering results obtained by different methods: downsample (no imputation), SAVER, scImpute, scVI and scFoundation. The numbers of clusters are aligned. The lower-right plots depict the clustering results of each method mapped onto the reference UMAP plot. e , UMAP plot comparing raw gene expression and scFoundation-imputed cell embeddings on the Zheng68K dataset. f , Comparison of clustering performance among scFoundation, scVI and raw data on the Zheng68K dataset.

scFoundation also showcased its capability to facilitate read depth enhanced clustering across different batches. Note that merely aligning the read depth would not eliminate the entire batch effect since batch effects can involve other variations such as donor gender, experiment treatment, cell cycle and so on 32 . We mapped single-cell data from different batches together by feeding the read-depth-enhanced cell embeddings into a nontrainable downstream header BBKNN 33 . Results on simulated data and on data collected from organoid and in vivo experiments showed that scFoundation can achieve better cell mapping while slightly reducing the dispersion of different cell types (Supplementary Table 3 and Supplementary Figs. 3 and 4; details in Supplementary Note 4).

These results demonstrated that scFoundation possessed the capability to enhance the read-depth of cells. Notably, an important distinction between scFoundation and other imputation methods was that scFoundation could achieve the best performance without the need for dataset-specific fine-tuning.

####### Improving cancer drug response prediction

Cancer drug responses (CDRs) study tumor cells' responses upon drug intervention. Computationally predicting CDR is critical to guiding anticancer drug design and understanding cancer biology 34 . We combined scFoundation with the CDR prediction method DeepCDR 35 to predict the half-maximal inhibitory concentration IC 50 values of drugs across several cell line data. This experiment served as a validation of whether scFoundation could provide informative embeddings for bulk-level gene expression data, despite being trained on single cells.

The original DeepCDR model used drug structural information and multiomics data as input and outputted the predicted IC 50 . Here, we focused on gene expression data and replaced the transcriptome multilayer perceptron (MLP) subnetwork in DeepCDR with scFoundation (Fig. 3a). We used the Cancer Cell Line Encyclopedia 36 and Genomics of Cancer Drug Sensitivity 37 datasets to obtain the input cell line gene expression data, the input drugs and IC 50 labels (Methods).

We evaluated the performance of scFoundation-based results with gene expression-based results across multiple drugs and cancer cell lines (Fig. 3b). Most drugs and all cancer types achieved a higher PCC by using scFoundation embeddings. We visualized the best prediction case of drug and cancer types (Fig. 3c). Regardless of high or low lC 50 , the scFoundation-based DeepCDR model could predict accurate values and achieved a PCC above 0.93. In a drug-blind test that left out one drug at a time from the dataset, scFoundation-based models consistently outperformed the original model (Fig. 3d). The top 1 PCC-gaining drug PHA793887, a potent ATP-competitive CDK inhibitor, improved the PCC from 0.07 to 0.73. Even for the 200th-ranked drug zobotentan used for blocking endothelin A receptor activity, its PCC improved from 0.49 to 0.64.

We further grouped drugs into different therapy types to examine whether the IC 50 prediction performance was related to their intrinsic mechanisms. Based on scFoundation-predicted results, drugs belonging to chemotherapy such as antitumor antibiotics and topoisomerase inhibitors tend to have higher PCC than drugs belonging to targeted therapy such as ataxia telangiectasia mutated (ATM) and poly(ADP-ribose) polymerase (PARP) inhibitors (Fig. 3d). This may be due to the fact that specific gene mutations often have important impacts on targeted therapy 34 but such information is hardly revealed in gene expression data, while chemotherapy drugs were widely reported to be related to gene expression 38,39 so their IC 50 is easier to predict. As for the gene expression-based results, they had an overall lower PCC, and we did not observe a performance difference between therapy types.

Then we used our model to predict unknown CDR in the data. To validate these predictions, we performed a gene set enrichment analysis

(GSEA) 40 on the new predictions with relatively low IC 50 , which indicated that the cell line is sensitive to the drug (Fig. 3e). For instance, the sphingolipid signaling pathway was enriched in doxorubicin-sensitive cell lines. According to the Kyoto Encyclopedia of Genes and Genome database 41 , this pathway was related to sphingomyelin and its metabolism. Sphingomyelin was reported to interact synergistically with doxorubicin by altering cell membrane permeability resulting in a lower IC 50 of the drug in these cell lines 42 . The mTOR signaling pathway was enriched in vorinostat-sensitive cell lines. Previous studies have shown that vorinostat inhibits carcinoma growth by dampening the mTOR signaling pathway 43 . Other clinical studies have also shown that mTOR inhibitors were often used in conjunction with vorinostat 44,45 , suggesting a relationship between vorinostat and the mTOR pathway. These examples supported the validity of our predictions.

Although scFoundation was pretrained on single-cell transcriptomics data, the learned gene relationships were transferable to bulk-level expression data to produce condensed embeddings, facilitating more accurate IC 50 prediction. These findings illustrated the potential of scFoundation in expanding the understanding of drug responses in cancer biology and possibly guiding the design of more effective anticancer treatments.

####### Transferring bulk drug response to single cells

Inference of drug sensitivities at the single-cell level can help identify specific cell subtypes that exhibit different drug resistance characteristics, offering valuable insights into underlying mechanisms and potential new therapies 46 . We applied scFoundation to the crucial task of single-cell-level drug response classification based on a downstream model called SCAD 47 . Due to the limited single-cell drug response data, SCAD used domain adaption to eliminate the single-cell and bulk differences, and transferred knowledge learned on bulk data to infer the drug sensitivity of single cells. The process took both bulk and singlecell data as input and output predicted the sensitivity for each cell. In our setting, we used non-fine-tuned scFoundation to obtain unified embeddings of bulk and single-cell data, and used these embeddings to train SCAD models (Fig. 4a).

We focused on the four drugs (sorafenib, NVP-TAE684, PLX4720 and etoposide) that exhibited lower area under the receiver operating characteristic curve (AUC) values in the original study. These drugs had drug-sensitive labels of bulk data in the Genomics of Cancer Drug Sensitivity 37 database, and the true cell-level drug-sensitive labels were obtained in different ways. For drug PLX4720 and etoposide-affected single cells, cells from untreated cell lines were considered sensitive, while cells that survived after drug exposure were considered resis  tant 48 . For drug sorafenib and NVP-TAE684-affected cells, the cells' sensitive labels were determined by the value of senescence-related (EpiSen) program scores that were proven to have a relation with drug responses previously 49 (Methods).

We compared the scFoundation-based model with the baseline SCAD model that took all genes' expression values as input. The scFoundation-based model achieved higher AUC values for all drugs, with notable improvements for NVP-TAE684 and sorafenib, exceeding a 0.2 increase in AUC. Baseline results for all four drugs were at best 0.66, with one result even worse than random, highlighting the task's difficulty (Fig. 4b). We used the Spearman correlation to assess the relationship between predicted drug sensitivity and EpiSen scores. For NVP-TAE684 and sorafenib, there should be a positive and negative correlation with EpiSen scores, respectively. The scFoundation model showed Spearman correlations of 0.56 and -0.55 for these drugs, while the baseline model achieved only 0.24 and -0.06 (Fig. 4c), indicating that using scFoundation embeddings had the potential to capture the signal of drug sensitivity biomarkers. These results further motivated us to investigate whether the embeddings were more informative than gene expression without the necessity for extracting the signal. We conducted principal component analysis (PCA) on embeddings of single-cell dataset SSC47 and visualized the first two principal components. Results showed less linear correlation compared with raw data PCA, suggesting richer information captured by the embeddings (Fig. 4d). Furthermore, we computed the clustering performance based on the embeddings and gene expression of both bulk and single-cell data, using drug sensitivity as the label. The results of higher CalinskiHarabasz (CH) and SIL scores (Fig. 4e and Supplementary Fig. 5) demonstrated that the scFoundation better-grouped cells or bulk cell lines with the same drug response, compared with the gene expression baseline.

Fig. 3 | Drug response prediction using scFoundation embeddings.

<!-- image -->

a , Illustration of the scFoundation-based CDR prediction model. b , PCC between all drugs and cancer types in the test set. Each dot represents a drug or cancer type, with the x axis and y axis showing PCCs obtained by the baseline CDR model and scFoundation-based model, respectively. c , Comparison of predicted and observed IC 50 values for the drug WZ-1-84 on the cancer-type low-grade gliomas. Each dot represents a drug and cell-line combination. d , Leave-one-drug-out blind test performance. The Pearson gain plot shows the PCC gain obtained by replacing gene expression with embeddings. Each dot represents a drug, with the y axis indicating the gained PCC values and the x axis representing the rank. Higher-ranked drugs have a higher PCC gain. In the PCC plot, each dot

These findings highlighted that the unified embedding obtained from scFoundation aligned bulk and single-cell data into a unified representation space. This condensed representation produced a clear distinction between data with sensitive and resistant states, facilitating the downstream model to better transfer pharmacogenomics information from bulk cell lines to single-cell data.

####### Facilitating perturbation response prediction

Understanding cellular responses to perturbations is crucial for biomedical applications and drug design, as it helps identify gene-gene interactions across different cell types and potential drug targets 50 . Using Perturb-seq 51,52 data resources to train models for modeling cellular response to perturbations is a key task of computational biology 53-55 . We combined the scFoundation with an advanced model called GEARS 53 for predicting the single-cell-resolution perturbation. The original GEARS model used a Gene Ontology knowledge graph to represent unseen gene perturbations by learning from a combination of previously observed gene perturbation nodes, and a gene co-expression graph combined with perturbation information to predict the post-perturbation gene expression. Each node in the co-expression graph represented a gene with initially randomized embeddings, and edges connected to co-expressed genes. This graph was shared across all cells. In our method, we obtained gene context embeddings for each cell from the scFoundation decoder and set these embeddings as the nodes in the graph (Methods), resulting in a cell-specific gene co-expression graph for predicting perturbations (Fig. 5a).

represents a drug, with the y axis indicating the PCC between predicted and ground truth IC 50 and the x axis representing four drug types. The first two belong to chemotherapy and the last two belong to targeted therapy. The dashed line showed the mean PCC within each therapy type. e , GSEA results on cell-line data with lower predicted IC 50 values. The Sphingolipid signaling pathway was enriched in doxorubicin-sensitive cell lines, while the mTOR signaling pathway was enriched in vorinostat-sensitive cell lines. The P value is one-sided and calculated from the standard GSEA permutation test. For the false discovery rate (FDR) value, adjustments were made for multiple comparisons. NES, normalized enrichment score.

We trained and tested models on three perturbation datasets following the original study (Supplementary Note 5). Since there was no single-cell-level ground truth in the perturbed data, we computed the averaged mean square error (MSE) of the top 20 differentially expressed (DE) genes between pre- and post-gene expression profiles for evaluation. The scFoundation-based model achieved lower MSE values compared with the original GEARS baseline model. On the more challenging two-gene perturbations predictions, the model achieved the lowest averaged MSE in the 0/2 unseen case and outperformed GEARS and another baseline called CPA 56 model across all cases (Fig. 5b and Supplementary Fig. 6). For each two-gene perturbation in the test set, we further examined the proportion of the top 20 DE genes with mean predicted values falling in the 45-55% quantile of the true expression distribution interval. The scFoundation-based model exhibited a higher percentage compared with the baseline (Fig. 5c), indicating it predicted a more reasonable distribution of post-gene expression values. Figure 5d showcased the top 20 genes' expression changes of two-gene perturbation ETS2 + CEBPE.

Fig. 4 | Single-cell drug response classification tasks based on scFoundation cell embeddings. a , Illustration of the scFoundation-based single-cell response classification model. b , Receiver operating characteristic (ROC) curves for the four drugs. The red and blue lines represent the performance of the scFoundationbased model and the baseline SCAD model, respectively. AUC, area under the receiver operating characteristic curve. c , The correlation between drug-sensitivity

<!-- image -->

One application for predicting two-gene perturbations was to classify two-gene perturbation into different genetic interaction (GI) types. We identified synergy and suppressor GI types by using the magnitude score (Methods). We first computed the PCC of magnitude score between predicted and ground truth magnitude scores of all two-gene perturbations in test set, and we found that the scFoundation-based model achieved a higher PCC compared with the baseline (Fig. 5e). Then, we ranked two-gene perturbations by predicted magnitude scores, considering the top 20 as potential synergy and the bottom 20 as suppressor GIs. The Venn plot in Fig. 5f revealed that the scFoundation-based model identified a higher number of true perturbations for both synergy and suppressor types.

probability and normalized EpiSen score. Each row corresponds to a model, and each column represents a drug. d , PCA plots of cells in the SSC47 single-cell dataset drawn with scFoundation embeddings and with raw data. Color denotes the reference EpiSen score. Cells with different EpiSen scores exhibit distinct responses to drugs. e , The clustering performance on all three drug-related bulk datasets. Each bulk dataset has two types of label: sensitive and resistant.

These results highlighted that the cell-specific gene context embeddings obtained from scFoundation served as valuable foundational representations for perturbation prediction. The analysis of two-gene perturbations underscored the model's capability to accurately classify different types of GI.

####### Annotating cell types

Cell type annotation is crucial in single-cell studies, and various methods have been developed for this purpose. To assess the performance of scFoundation, we conducted experiments using the Zheng68K dataset 30 and the Segerstolpe dataset 57 that were shown to be challenging in the previous study 13 . We fine-tuned only a single layer of the scFoundation encoder and added an MLP head for predicting labels.

Fig. 5 | Perturbation prediction tasks using scFoundation gene context embeddings. a , An illustration of the perturbation prediction model based on cell-specific gene embeddings of scFoundation. b , MSE between predicted and ground truth post-gene expressions. Results given by the scFoundation-based GEARS model and baseline GEARS model are shown in red and blue, respectively. c , The average proportion of predicted values of the top 20 DE genes falling within 45-55% quantile of the corresponding true expression distribution interval. The dashed black lines represent the expected percentage (10%). d , The predicted gene expression over control for the top 20 most DE genes after a combinatorial perturbation (ETS2 + CEBPE). The red and blue boxes indicate gene prediction results by the scFoundation-based GEARS model and the baseline GEARS model, respectively. The green boxes represent the ground

<!-- image -->

We benchmarked scFoundation against the methods CellTypist 58 , scBERT 13 , scANVI 59 , ACTINN 60 , Scanpy 61 and SingleCellNet 62 (Methods). Supplementary Table 4 shows that scFoundation achieved the highest macro F1 score on both datasets. Compared with the second-place method CellTypist, the higher performance of scFoundation came perturbation set.

truth post-gene distribution. For each gene, n = 313 cells were examined. The two edges of a box and horizontal bars inside a box indicate the interquartile and median of all values, respectively. The length of the whiskers extends to 1.5 times the interquartile range (IQR) from the quartiles. e , Magnitude scores computed for all test perturbing combinations on the Norman dataset. Each dot represents a specific perturbing combination. The y axis shows the magnitude score computed from the prediction results, while the x axis represents the ground truth magnitude score computed using real post-gene expression. f , Top 20 perturbations with synergistic and suppressor gene interaction types identified using scFoundation and baseline methods. The Venn plot illustrates the relationship between the identified perturbation set and the verified

from improvements in rare cell types such as CD4 + T helper 2 and CD34 + (Supplementary Table 5). We visualized scFoundation and CellTypist predictions on the UMAP obtained from latent embeddings and PCA components, respectively. Supplementary Figs. 7 and 8 showed that scFoundation had clear separations between different cell types.

These results indicated that scFoundation's ability to utilize the entire gene set as input could lead to more accurate annotations, compared with other methods that unavoidably lose information by using a gene subset or discretized gene expression.

####### Inferring gene modules and gene regulation networks

One advantage of scFoundation is that it extends gene expression values into context embeddings, compared with other architectures such as the vanilla MLP model (Supplementary Note 6). These embeddings could not only facilitate graph-based downstream methods such as GEARS, but also be used to infer gene-gene networks. Here, we used the gene embeddings from three immune cell types (monocytes, cytotoxic CD8 + T cells and B cells) for validation and exploration of this usage (Methods).

We clustered genes into modules based on their embeddings' similarity. Results showed that scFoundation could identify the differential expressed gene modules of each cell type (Supplementary Figs. 9 and 10). Gene enrichment analysis validated that the identified gene modules were enriched in their respective cell types (Supplementary Fig. 11), indicating that the gene embeddings have learned functional relations among genes. Further, we explored the gene network constructed within the top 1 DE gene module of T cells (Supplementary Fig. 12). Genes CD8A and CD8B encoding chains of the CD8 molecule exhibited strong similarities, while the S100A8 gene showed limited correlation with other T cell markers as expected. This suggested that the embeddings could provide insights into gene relations within modules. Additionally, we conducted experiments on gene regulatory network (GRN) inference with the downstream model SCENIC 63 (Methods). We identified cell-specific regulators such as KLF6, SPIB and MXD4, which were confirmed by the previous work as the regulators for monocyte 64 , B cell 65 and CD8 + T cell 66 , respectively (Supplementary Fig. 13). These examples underscored the potential of scFoundation gene embeddings for inferring GRNs.

####### Discussion

Recent breakthroughs in LLMs motivated us to explore whether large-scale models can also be effective for learning the cellular and molecular 'languages' of biology from single-cell transcriptomic data, which exhibit large data scales, complex biological patterns, diversity and technical noises. Combining the xTrimoGene architecture with the RDA pretraining task, we developed scFoundation, a large-scale foundation model with 100 million parameters pretrained on over 50 million single-cell data. Ablation experiments and applications on downstream tasks showed the advantage of its design of the pretraining task and the model. Supplementary Table 1 provides a comparison of the major features with the released similar models.

scFoundation was pretrained as a general-purpose foundation model for many downstream tasks: it achieved superior performance in read-depth enhancement, drug response prediction, single-cell drug sensitivity prediction, perturbation predictions and cell type annotation tasks. It also showed high potential in gene module inference and in better facilitating cell mapping by cooperating with downstream batch removal headers like BBKNN 33 .

The scFoundation model does not need further fine-tuning on most tasks. This design reduced computational and time costs for users and offered flexibility in downstream model design, allowing scFoundation to better serve as a foundational model for a variety of downstream tasks in the field of single-cell biology.

We recommend using scFoundation to extract embeddings from datasets without explicit batch-effect or modality differences. Given that batch effects or modality differences may encompass a range of variations, we took the strategy in scFoundation to consider only read depth and leave other possible differences to cooperative methods on downstream tasks, such as BBKNN and SCAD. Furthermore, we suggest using cell and gene embeddings instead of the predicted gene expression values because the current data used as pretraining labels suffered from a high dropout rate and the model pretraining loss was not optimized to zero.

scFoundation still faces some limitations. Although the pretraining data contained virtually all human scRNA-seq data publicly available at the time of our curation, they may still not be sufficient to fully reflect the complexity of human organ development and health states. The pretraining demands substantial computational resources, requiring further optimization for efficiency. The current model focused on transcriptomic data only, and did not include genomic or epigenomic data. Also, its unsupervised pretraining process had the advantage of not relying on human annotation of the massive data but overlooked the rich information in metadata. Including cells' metadata with transcriptomic data in the model may have the potential to link cells' molecular features with phenotypes.

In the future, we will pretrain models with more parameters and larger datasets using our effective pretraining framework, and we believe several works could be developed on the basis of the insights from scFoundation. For instance, designing more effective pretraining tasks could potentially improve the model's performance 29 . The effect of various dataset characteristics on training performance also remains to be explored 29 . Furthermore, the emerging field of single-cell multiomics data 67,68 presents opportunities for developing models that can delineate multilevel complex laws of cells. One doable case can be to predict gene expression values based on assay for transposase-accessible chromatin with sequencing (ATAC-seq) context and vice versa (Supplementary Note 7).

The general applicability of scFoundation shown in the variety of tasks indicates that it has succeeded in learning underlying relations among genes in their expressions in different types of cell. We expect that the pretraining architecture and the pretrained scFoundation model can serve as fundamental contributions supporting both studies on large biological models and a variety of downstream research. This work as well as other recent reports suggest that large biological models pretrained on high-throughput single-cell data are opening a new route to deciphering and modeling complex molecular systems.

####### Online content

Any methods, additional references, Nature Portfolio reporting summaries, source data, extended data, supplementary information, acknowledgements, peer review information; details of author contributions and competing interests; and statements of data and code availability are available at https://doi.org/10.1038/s41592-024-02305-7.

####### References

1. Srivastava, A. et al. Beyond the imitation game: quantifying and extrapolating the capabilities of language models. Preprint at arXiv https://doi.org/10.48550/arXiv.2206.04615 (2023).
2. Jovic, D. et al. Single-cell RNA sequencing technologies and applications: a brief overview. Clin. Transl. Med. 12 , e694 (2022).
3. Regev, A. et al. The Human Cell Atlas. eLife 6 , e27041 (2017).
4. Chen, S. et al. hECA: the cell-centric assembly of a cell atlas. iScience 25 , 104318 (2022).
5. Snyder, M. P. et al. The human body at cellular resolution: the NIH Human Biomolecular Atlas Program. Nature 574 , 187-192 (2019).
6. The Tabula Sapiens Consortium. The Tabula Sapiens: a multiple-organ, single-cell transcriptomic atlas of humans. Science 376 , eabl4896 (2022).
7. Li, M. et al. DISCO: a database of deeply integrated human single-cell omics data. Nucleic Acids Res. 50 , D596-D602 (2022).
8. Papatheodorou, I. et al. Expression Atlas update: from tissues to
9. single cells. Nucleic Acids Res. 48 , D77-D83 (2020).
9. Svensson, V., Vento-Tormo, R. &amp; Teichmann, S. A. Exponential scaling of single-cell RNA-seq in the past decade. Nat. Protoc. 13 , 599-604 (2018).

10. Brown, T. B. et al. Language models are few-shot learners. Adv. Neural Inf. Process. Syst. 33 , 1877-1901 (2020).
11. Zhao, W. X. et al. A survey of large language models. Preprint at arXiv https://doi.org/10.48550/arXiv.2303.18223 (2023).
12. Zhang, R., Luo, Y., Ma, J., Zhang, M. &amp; Wang, S. scPretrain: multi-task self-supervised learning for cell-type classification. Bioinformatics 38 , 1607-1614 (2022).
13. Yang, F. et al. scBERT as a large-scale pretrained deep language model for cell type annotation of single-cell RNA-seq data. Nat. Mach. Intell. 4 , 852-866 (2022).
14. Cui, H., Wang, C., Maan, H. &amp; Wang, B. scGPT: towards building a foundation model for single-cell multi-omics using generative AI. Nat Methods https://doi.org/10.1038/s41592-024-02201-0 (2024).
15. Theodoris, C. V. et al. Transfer learning enables predictions in network biology. Nature https://doi.org/10.1038/s41586-02306139-9 (2023).
16. Choromanski, K. et al. Rethinking attention with performers. Preprint at arXiv https://doi.org/10.48550/arXiv.2009.14794 (2022).
17. Ma, X. et al. Luna: Linear Unified Nested Attention. Adv. Neural Inf. Process. Syst. 34 , 2441-2453 (2021).
18. Gong, J. et al. xTrimoGene: an efficient and scalable representation learner for single-cell RNA-seq data. Preprint at bioRxiv https://doi.org/10.1101/2023.03.24.534055 (2023).
19. Chen, J. et al. Transformer for one stop interpretable cell type annotation. Nat. Commun. 14 , 223 (2023).
20. He, K. et al. in Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition 16000-16009 (IEEE, 2022).
21. Devlin, J., Chang, M.-W., Lee, K. &amp; Toutanova, K. in Proc. 2019 Conference of the North American Chapter of the Association for Computational Linguistics 4171-4186 (ACL, 2019).
22. Edgar, R., Domrachev, M. &amp; Lash, A. E. Gene Expression Omnibus: NCBI gene expression and hybridization array data repository. Nucleic Acids Res. 30 , 207-210 (2002).
23. Seal, R. L. et al. Genenames.org: the HGNC resources in 2023. Nucleic Acids Res. 51 , D1003-D1009 (2023).
24. Kaplan, J. et al. Scaling laws for neural language models. Preprint at arXiv https://doi.org/10.48550/arXiv.2001.08361 (2020).
25. Lopez, R., Regier, J., Cole, M. B., Jordan, M. I. &amp; Yosef, N. Deep generative modeling for single-cell transcriptomics. Nat. Methods 15 , 1053-1058 (2018).
26. van Dijk, D. et al. Recovering gene interactions from single-cell data using data diffusion. Cell 174 , 716-729.e27 (2018).
27. Huang, M. et al. SAVER: gene expression recovery for single-cell RNA sequencing. Nat. Methods 15 , 539-542 (2018).
28. Li, W. V. &amp; Li, J. J. An accurate and robust imputation method scImpute for single-cell RNA-seq data. Nat. Commun. 9 , 997 (2018).
29. Kedzierska, K. Z., Crawford, L., Amini, A. P. &amp; Lu, A. X. Assessing the limits of zero-shot foundation models in single-cell biology. Preprint at bioRxiv https://doi.org/10.1101/2023.10.16.561085 (2023).
30.  Zheng, G. X. Y. et al. Massively parallel digital transcriptional profiling of single cells. Nat. Commun. 8 , 14049 (2017).
31. Abdelaal, T. et al. A comparison of automatic cell identification methods for single-cell RNA sequencing data. Genome Biol. 20 , 194 (2019).
32. Luecken, M. D. et al. Benchmarking atlas-level data integration in single-cell genomics. Nat. Methods 19 , 41-50 (2022).
33. Polański, K. et al. BBKNN: fast batch alignment of single cell transcriptomes. Bioinformatics 36 , 964-965 (2020).
34.  Unger, F. T., Witte, I. &amp; David, K. A. Prediction of individual response to anticancer therapy: historical and future perspectives. Cell. Mol. Life Sci. 72 , 729-757 (2015).
35. Liu, Q., Hu, Z., Jiang, R. &amp; Zhou, M. DeepCDR: a hybrid graph convolutional network for predicting cancer drug response. Bioinformatics 36 , i911-i918 (2020).
36.  Barretina, J. et al. The Cancer Cell Line Encyclopedia enables predictive modelling of anticancer drug sensitivity. Nature 483 , 603-607 (2012).
37. Iorio, F. et al. A landscape of pharmacogenomic interactions in cancer. Cell 166 , 740-754 (2016).
38.  Bellamy, D., Celi, L. &amp; Beam, A. L. Evaluating progress on machine learning for longitudinal electronic healthcare data. Preprint at arXiv https://doi.org/10.48550/arXiv.2010.01149 (2020).
39. Geeleher, P., Cox, N. J. &amp; Huang, R. Clinical drug response can be predicted using baseline gene expression levels and in vitro drug sensitivity in cell lines. Genome Biol. 15 , R47 (2014).
40.  Subramanian, A. et al. Gene set enrichment analysis: a knowledge-based approach for interpreting genome-wide expression profiles. Proc. Natl Acad. Sci. USA 102 , 15545-15550 (2005).
41. Kanehisa, M. &amp; Goto, S. KEGG: Kyoto Encyclopedia of Genes and Genomes. Nucleic Acids Res. 28 , 27-30 (2000).
42. Saddoughi, S. A., Song, P. &amp; Ogretmen, B. in Lipids in Health and Disease (eds Quinn, P. J. &amp; Wang, X.) 413-440 (Springer, 2008).
43.  Kurundkar, D. et al. Vorinostat, an HDAC inhibitor attenuates epidermoid squamous cell carcinoma growth by dampening mTOR signaling pathway in a human xenograft murine model. Toxicol. Appl. Pharmacol. 266 , 233-244 (2013).
44.  Park, H. et al. Phase I dose-escalation study of the mTOR inhibitor sirolimus and the HDAC inhibitor vorinostat in patients with advanced malignancy. Oncotarget 7 , 67521-67531 (2016).
45. Zibelman, M. et al. Phase I study of the mTOR inhibitor ridaforolimus and the HDAC inhibitor vorinostat in advanced renal cell carcinoma and other solid tumors. Invest. N. Drugs 33 , 1040-1047 (2015).
46.  Vasudevan, S. et al. Drug-induced resistance and phenotypic switch in triple-negative breast cancer can be controlled via resolution and targeting of individualized signaling signatures. Cancers 13 , 5009 (2021).
47. Zheng, Z. et al. Enabling single-cell drug response annotations from bulk RNA-seq using SCAD. Adv. Sci. 10 , e2204113 (2023).
48.  Ho, Y.-J. et al. Single-cell RNA-seq analysis identifies markers of resistance to targeted BRAF inhibitors in melanoma cell populations. Genome Res. 28 , 1353-1363 (2018).
49. Kinker, G. S. et al. Pan-cancer single-cell RNA-seq identifies recurring programs of cellular heterogeneity. Nat. Genet. 52 , 1208-1218 (2020).
50.  Rood, J. E., Maartens, A., Hupalowska, A., Teichmann, S. A. &amp; Regev, A. Impact of the Human Cell Atlas on medicine. Nat. Med. 28 , 2486-2496 (2022).
51. Adamson, B. et al. A multiplexed single-cell CRISPR screening platform enables systematic dissection of the unfolded protein response. Cell 167 , 1867-1882 (2016).
52. Dixit, A. et al. Perturb-Seq: dissecting molecular circuits with scalable single-cell RNA profiling of pooled genetic screens. Cell 167 , 1853-1866 (2016).
53. Roohani, Y., Huang, K. &amp; Leskovec, J. Predicting transcriptional outcomes of novel multigene perturbations with GEARS. Nat. Biotechnol. https://doi.org/10.1038/s41587-023-01905-6 (2023).
54. Lotfollahi, M., Wolf, F. A. &amp; Theis, F. J. scGen predicts single-cell perturbation responses. Nat. Methods 16 , 715-721 (2019).
55. Lotfollahi, M. et al. Learning interpretable cellular responses to complex perturbations in high-throughput screens. Preprint at bioRxiv https://doi.org/10.1101/2021.04.14.439903 (2021).

56. Lotfollahi, M. et al. Predicting cellular responses to complex perturbations in high-throughput screens. Mol. Syst. Biol. 19 , e11517 (2023).
57. Segerstolpe, Å. et al. Single-cell transcriptome profiling of human pancreatic islets in health and type 2 diabetes. Cell Metab. 24 , 593-607 (2016).
58.  Domínguez Conde, C. et al. Cross-tissue immune cell analysis reveals tissue-specific features in humans. Science 376 , eabl5197 (2022).
59. Xu, C. et al. Probabilistic harmonization and annotation of single-cell transcriptomics data with deep generative models. Mol. Syst. Biol. 17 , e9620 (2021).
60.  Ma, F. &amp; Pellegrini, M. ACTINN: automated identification of cell types in single cell RNA sequencing. Bioinformatics 36 , 533-538 (2020).
61. Wolf, F. A., Angerer, P. &amp; Theis, F. J. SCANPY: large-scale single-cell gene expression data analysis. Genome Biol. 19 , 15 (2018).
62. Tan, Y. &amp; Cahan, P. SingleCellNet: a computational tool to classify single cell RNA-seq data across platforms and across species. Cell Syst. 9 , 207-213 (2019).
63.  Aibar, S. et al. SCENIC: single-cell regulatory network inference and clustering. Nat. Methods 14 , 1083-1086 (2017).
64.  Date, D. et al. Kruppel-like transcription factor 6 regulates inflammatory macrophage polarization. J. Biol. Chem. 289 , 10318-10329 (2014).
65. Willis, S. N. et al. Environmental sensing by mature B cells is controlled by the transcription factors PU.1 and SpiB. Nat. Commun. 8 , 1426 (2017).
66.  Vasilevsky, N. A., Ruby, C. E., Hurlin, P. J. &amp; Weinberg, A. D. OX40 engagement stabilizes Mxd4 and Mnt protein levels in antigen-stimulated T cells leading to an increase in cell survival. Eur. J. Immunol. 41 , 1024-1034 (2011).
67. Ma, S. et al. Chromatin potential identified by shared single-cell profiling of RNA and chromatin. Cell 183 , 1103-1116 (2020).
68.  Chen, S., Lake, B. B. &amp; Zhang, K. High-throughput sequencing of the transcriptome and chromatin accessibility in the same cell. Nat. Biotechnol. 37 , 1452-1457 (2019).

Publisher's note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

Springer Nature or its licensor (e.g. a society or other partner) holds exclusive rights to this article under a publishing agreement with the author(s) or other rightsholder(s); author self-archiving of the accepted manuscript version of this article is solely governed by the terms of such publishing agreement and applicable law.

- © The Author(s), under exclusive licence to Springer Nature America, Inc. 2024

####### Methods

####### Pretraining data collection and preprocessing

Data collection . Many human scRNA-seq data were deposited in the Gene Expression Omnibus (GEO) repository, HCA, Single Cell Portal, EMBL-EBI and so on. There were also several studies to integrate human single cells from multiple resources, such as hECA 4 , DISCO 7 and so on. Each dataset in these databases was linked to a published study and thus had a corresponding DOI ID. We manually collected scRNA-seq data from these databases and removed the dataset with a duplicated ID. Most of the datasets provided the raw count matrix. For the dataset with normalized expression profiles, we converted them back to the raw count form: we treated the smallest nonzero value in the original matrix as a raw count value of 1, all remaining nonzero values were divided by this smallest value and the integer part was taken. For the dataset with transcripts per million (TPM) or fragments per kilobase of transcript per million fragments mapped (FKPM) expression profiles that cannot be converted back to raw counts, we kept them unchanged.

Our data collection comprises over 50 million single cells of diverse organs and tissues from samples of healthy donors and of various diseases and cancer types, representing a full spectrum of human single-cell transcriptomes. We split all data into training and validation datasets. The validation dataset was randomly sampled and contained 100,000 single cells, and remained consistent for all test models.

Gene symbol unification . We unified the gene symbols of all raw count gene expression matrices by using the gene symbol mapping reference provided by HUGO Gene Nomenclature Committee. We included human protein-coding genes and common mitochondrial genes, constituting a total of 19,264 genes. If some symbols were missing, we padded them with zero values.

Quality control . To filter contaminated empty droplets, extremely low-quality cells and damaged cells, we kept cells with over 200 genes expressed (that is, expression vector with nonzero value count &gt;200) for pretraining by using the Seurat 69 and Scanpy 61 packages.

####### scFoundation model architecture

We developed the xTrimoGene model as the backbone model of scFoundation. It had three modules: the embedding module converted scalar value into embeddings that were required for the transformer block; the encoder took the nonzero and nonmasked expressed genes as input, used the vanilla transformer block and had large parameter size; and the decoder took all genes as input, used the performer block and had a relatively small parameter size. Ablation experiments showed that such asymmetric design reduced the computational and memory challenges compared with other architectures (Supplementary Table 6).

Embedding module . Given a cell's gene expression value vector X input ∈ ℝ n = 19 , 264 , the expression value x input i of gene i was a continuous scalar greater than or equal to zero. Unlike the previous language or recently developed single-cell transformer-based model, for each gene i the embedding module directly converted the expression scalar into a learnable value embedding E i without any discretization. Then, the value embedding was added with gene name embeddings T G i to form the final input embeddings E input i .  The value embeddings were a weighted summarization of a set of embeddings, where the weights were learned from the gene expression scalar values. The gene name embeddings were retrieved from a look-up table, where the embeddings in the table are randomly initialized and can be learned during pretraining (Supplementary Note 8). The ablation of continuous embeddings  scheme  showed  that  the  benefit  of  our  design compared with other value discretization methods (Supplementary Fig. 14).

Encoder . The encoder only processed the embeddings of nonzero and nonmasked values (that is, the expressed genes and two total count numbers) so the input length of the encoder was about 10% of the full gene length. Denoting S E = { S E 0 , S E 1 , … , S E K } as the index set of nonzero and nonmasked values with K elements, the input of encoder was defined as

<!-- formula-not-decoded -->

1

0

The design of encoder greatly reduced the required computational resources, making it possible for the encoder to employ a series of vanilla transformer blocks to capture gene dependency without any kernel or low-rank approximation. The outputs of encoder were intermediate embeddings X inter :

<!-- formula-not-decoded -->

where Trm represents a series of transformer blocks and the core function in these blocks is the attention mechanism that can be formulated as

<!-- formula-not-decoded -->

where Q = XWq , K = XWk and V = XWv are linear transformation of the input X , and W ⋅ are training parameters. 1 K is the all-ones vector of length K , and diag(·) is a diagonal matrix with the input vector as the diagonal.

The intermediate embeddings X inter had two usages: (1) they were sent into the decoder with the zero and mask embeddings, and (2) they were pooled as cell embeddings for downstream usages.

Decoder . To establish a transcriptome-wide gene regulation relationship, the zero-expressed genes should also be considered for recovering expression values at mask positions. The intermediate embeddings from encoder were concatenated with the zero and mask embeddings to form a decoder input tensor X Dec -input with full gene length

<!-- formula-not-decoded -->

where K 0 and K m were the number of zero and masked embeddings, respectively. We used the kernel-based approximation transformer variant Performer 16 as the backbone in the decoder, since the attention calculation was challenging for long sequences 16,70 . In Performer, the kernelizable attention mechanism is used:

̂

<!-- formula-not-decoded -->

̂

where ∅(·) is a kernel function that used for approximating the A matrix in the original attention equation.

The output of decoder is X Out , where

<!-- formula-not-decoded -->

For predicting the expression value, the embeddings of T and S were dropped and an MLP was followed to project X Out to scalars. These scalars formed a prediction vector P , where

<!-- formula-not-decoded -->

All parameters Θ = { E i , T G i , ΘEncoder , ΘDecoder , ΘMLP } were optimized during the pretraining. The detailed hyperparameter setting of different models can be found in Supplementary Table 7.

####### RDA pretraining task

We trained the model with an RDA gene expression prediction task. For each raw pretraining single-cell gene expression vector, we used a hierarchical Bayesian downsampling strategy to generate its low total counts variant or unchanged profiles as the input vector. We normalized and log-transformed the raw and input gene expression, and set the total counts of the raw and input vectors as two total count indicators T and S , respectively. After normalizing gene expression, the original total count value of cells is removed. By reintroducing this information through tokens, we believe it can enhance the model's pretraining performance since the dropout in cells is usually correlated with the total count value. Please refer to Supplementary Notes 9 and 10 for details of the sampling strategy and count indicators calculation.

Then we randomly masked the genes' expressions of the input vector. In this study, we used 30% as the masking ratio for both zero and nonzero values. Then the masked input vector was concatenated with two total count indicators T and S and fed into the model. After getting the model-predicted raw gene expression, we conducted the regression loss on the masked genes between the predicted and the raw values (Supplementary Note 11). If the input vector was unchanged, the model learned to capture the relation between genes within a single cell. If the input vector was the low-total-count variant, the model learned the relationship between cells with different read depths. The ablation studies (Supplementary Note 1) of taking downsampling strategy (Supplementary Table 8) and regression loss (Supplementary Fig. 15) showed that the current setting could facilitate learning cell characteristics.

The overall model architecture of scFoundation is shown in Supplementary Fig. 16. For the model and pretraining implementation, please refer to Supplementary Note 12.

####### Read-depth enhancement analysis

For the gene expression prediction evaluation, we sampled 10,000 cells with high total counts (higher than 1,000) from 50 million single-cell data as the validation dataset. These 10,000 cells were excluded at the training stage. Then, we used a binomial distribution to generate the low total counts gene expression vector and fed it into our model. We only evaluate nonzero gene expression values considering that 0 expression values do not change in value after downsampling. In addition to using MSE as the evaluation metric, we also used the MRE, which can reflect the relative error

<!-- formula-not-decoded -->

i

=

0

For the clustering analysis, we got the cell embeddings from scFoundation and scVI encoder. For others, we got the imputed gene expression profiles. All methods were used with the default parameter setting. Then, we followed the SCANPY pbmc3k tutorial and got the cell cluster by the function 'sc.tl.leiden'.

For the evaluation of the clustering results, we first used ARI and NMI (scikit-learn 71 package) as indicators to evaluate the degree of consistency between the clustering results obtained by different methods and the actual cell type labels. Considering that the acquisition of cluster labels will also be affected by the choice of the clustering algorithm, we used SIL as another evaluation indicator, which measures the aggregation degree of true cell type labels on the cell neighborhood maps given by different methods and, thus, is independent of the choice of clustering algorithm, reflecting the intrinsic properties of cell representation.

####### Downstream methods

All  baseline  models  were  trained  with  default  parameters.  We dumped the cell embeddings for DeepCDR and SCAD tasks, and gene embeddings for the GEARS task. As for cell embeddings, we found that concatenating the embeddings obtained by max-pooling and mean-pooling the embeddings of all genes, and the embeddings of the S token and T token, achieved the best performance (Supplementary Note 13 and Supplementary Tables 9 and 10). The concatenation of the four embeddings built the new cell embeddings with 3,072 dimensions, and we trained the downstream model based on these cell embeddings.

DeepCDR . We used the cell line and drug-paired data preprocessed by DeepCDR. The cell line data contain 697 gene expression profiles, and we aligned these genes with our unified gene symbol list. The drugs were represented as graphs with consistent feature matrices and adjacent matrix sizes. In total, 223 drugs and 561 cell lines data from 31 cancer types were considered. We followed the original study to randomly split 5% of data as the test set, resulting in 89,585 and 4,729 cell line-drug samples for training and testing, respectively. For each cell line, we set both indicators S and T equal to the sum of all gene expression values. And we fed the nonzero gene expression values and two indicators into the model encoder and got the context embedding for each gene. The bulk-level cell-line embedding was obtained by the max-pooling operation for each embedding dimension across all genes.

We trained the baseline DeepCDR model by setting parameters '-use\_gexp' as True and '-use\_mut' and '-use\_methy' as False. Then for the scFoundation-based model, we directly replaced the gene expression with the cell-line embedding and trained the DeepCDR with the same setting. For each gene, we computed the PCC between predicted IC 50 and truth IC 50 across all cell lines. For each cell line, we computed the PCC across all drugs conducted on this cell line.

SCAD . We followed the same experimental setting as the original SCAD study, conducting fivefold cross-validation. For each split, four folds of the bulk and single-cell data were used to train the model, and the other fold was left for prediction, and we merged all split results to get the prediction for all cells. We used all genes and conducted the weighted sampling in the model training process. For training the baseline model, gene expression values were transformed into the z score in their provided processed data.

For training the scFoundation-based model, we used the normalized gene expression data. For bulk data, we set both S and T to the sum of all gene expression values to maintain original cell line features. For single-cell data, we set token S to the sum of gene expression values and token T to 10,000, the empirically maximum sequencing depth per cell. Then, the nonzero values of each sample and two indicators were fed into the encoder of the pretrained model. The outputs were the context embeddings of genes for each sample and then condensed into the cell embeddings.

Perturbation prediction . We unified the gene symbol list to 19,264 and generated the gene co-expression network on each dataset. Following the original GEARS study, for one-gene perturbations, we randomly assigned 75% of perturbations as training data. For two-gene perturbations, 75% of perturbations where both genes were in the seen set (0/2 unseen) were designated as the training set, while all other combinations (1/2 and 2/2 unseen) were held out for testing. Then, we trained the GEARS baseline model by setting epoch to 15 and batch size to 30. The CPA model does not have gene embeddings, and it takes the drug or gene perturbation embeddings as the input model. We trained the CPA model with the same parameter setting used in the GEARS study. Gene perturbations were encoded as one-hot vectors, and two-gene perturbations were represented by the addition of two one-gene perturbation vectors. In the embedding-based model, each cell's T and S values equaled its total counts, with gene expression and indicators fed into the model. The scFoundation's last MLP layer was dropped to extract gene context embeddings from the decoder, serving as node features for the co-expression graph. We froze scFoundation and solely trained the downstream GEARS model, employing gradient accumulation to maintain consistent batch size with the baseline during training.

We followed the definition and metrics used in GEARS. We focused on the synergy and suppression gene intersection types since they were the most basic types. Identification of these two types was based on the magnitude score, which measured the similarity between the two-gene perturbation and combining two single-gene perturbations. Specifically, let the mean change between post- and pre-A perturbed cells as δ g a . A linear model was used to fit the effect of δ g a , δ g b and δ g a + b :

<!-- formula-not-decoded -->

where /epsilonlunatesymbol captures the error in the model fit. We used the robust regression with a Theil-Sen estimator following the same procedure used in previous study 72 . Using the values of the coefficients, magnitude was defined as

<!-- formula-not-decoded -->

All test two-gene perturbations were ranked by magnitude score, with the top- and bottom-ranked being considered synergistic and repressive types, respectively.

Cell  type  annotation . We  randomly  split  each  dataset  into train:valid:test of 8:1:1. For scFoundation, we added a two-layer MLP with ReLU as the activation function after the encoder. The output of MLP is the predicted label. Considering the imbalanced cell numbers of different cell types, we used a weighted cross entropy loss. Given in total C cell types, and cell type i has A i cells, the weight of each cell type wi in the loss was defined as

<!-- formula-not-decoded -->

where B i was the scaled number. We set the learning rate as 0.001, the gradient accumulation step as 5 and the batch size in each step was 64. We got the model with highest F1 score on the validation dataset as the best model for testing.

For scBERT, we converted the gene expression matrix to match their input required gene symbol list and fine-tuned their pretrained model. We used the validation dataset to select the best model. For methods CellTypist, scANVI, ACTINN and SingleCellNet, we fed the training and valid dataset into models and trained them with default parameter settings. We got the prediction results of test data from the corresponding function such as 'celltypist.annotate' of CellTypist. As for Scanpy, we used the 'sc.tl.ingest' function to transfer the cell type label into the test data based on the PCA components, and treated the transferred label as the prediction. For each method on the test split, we computed the average macro F1 score of the top three performed model replicates.

Gene module and gene regulation inference . We randomly selected 100 cells from the three cell types (Monocytes, CD8 + cytotoxic T cells, and B cell) in Zheng68K data, resulting in a total of 300 cells. These data were processed through scFoundation to obtain the context embedding for all genes, resulting in a matrix o f dimensions 300 × 19,264 × 512. After selecting the highly variable genes and averaging the gene embeddings across cells, we derived 495 gene embeddings, each of 512 dimensions and used the Leiden clustering method to get 34 gene modules based on embeddings. We then computed the average expression of each gene module across the 300 cells using the 8scanpy.tl.score\_genes9 function, producing a scoring matrix of 300 × 34. We conducted differential analysis on this score matrix to identify marker gene modules for each cell type. Then, we did the enrichment analysis on the differential expressed gene modules via the online EnrichR 73 tools. We used the 8PanglaoDB Augmented 20219 dataset and selected the term with the lowest adjusted P value to interpret gene modules. As for gene network, we computed the similarity of gene embeddings with a module, and marked the top 5 edges with the highest value.

As for gene regulation inference, we got all known transcription factor (TF)-target gene pairs from SCENIC and quantified their relationships based on the similarity of their gene embeddings. For each TF, we selected the top 1,000 pairs with high similarity as the candidate pairs. Since transcriptomic data do not provide direct insights into TF-gene binding at the sequence level, we used RcisTarget module of SCENIC to refine our selected pairs. Using the auc\_cell module of SCENIC, we then derived the TF enrichment scores in cell types and identified the top-ranked cell-specific TFs. However, we would like to point out that directly calculating similarity from embeddings is a simplistic approach that may not fully harness the rich information within the vectors. Future endeavors could explore algorithms that leverage context embeddings for more sophisticated GRN inference, such as those employing graph neural networks.

####### Reporting summary

Further information on research design is available in the Nature Portfolio Reporting Summary linked to this article.

####### Data availability

All data used in this study are publicly available and the usages are illustrated in the Methods. The pretraining datasets were mainly downloaded from GEO (https://www.ncbi.nlm.nih.gov/geo/), Single Cell Portal (https://singlecell.broadinstitute.org/single\_cell), HCA (https://data.humancellatlas.org/) and EMBL-EBI (https://www.ebi. ac.uk/), and the detailed dataset list we used is in Supplementary Data 1 and 2. The datasets used for downstream tasks can be downloaded from the following links: Baron dataset (https://github.com/ mohuangx/SAVER-paper); Zheng68K dataset (https://www.dropbox. com/sh/w3yg2nucnng5v1u/AAAM8Ym\_KU9XF4z51RT81eNEa?dl=0); Segerstolpe dataset (https://zenodo.org/records/3357167); CDR dataset (https://github.com/kimmo1019/DeepCDR); Single cell drug response classification dataset (https://github.com/CompBioT/ SCAD); Perturbation dataset (https://github.com/snap-stanford/ GEARS); Simulated reference and query dataset used for cell mapping (https://doi.org/10.6084/m9.figshare.21456645.v4); and Organoid and in vivo data used for cell mapping (https://doi.org/10.17632/ sm67hr5bpm.1). The processed gene expression data and the embeddings generated by scFoundation can be found in our GitHub repository (https://github.com/biomap-research/scFoundation) and figshare (https://doi.org/10.6084/m9.figshare.24049200) (ref. 74).

####### Code availability

The code for using the online API, the model codes and weight, a demonstration of inferring embeddings, codes of producing the results for the downstream tasks are at the GitHub repository at https://github. com/biomap-research/scFoundation or Zenodo 75 . A summary of all code and data information is in Supplementary Data 3.

####### References

69. Hao, Y. et al. Integrated analysis of multimodal single-cell data. Cell 184 , 3573-3587 (2021).
70. Beltagy, I., Peters, M. E. &amp; Cohan, A. Longformer: the long-document transformer. Preprint at arXiv https://doi. org/10.48550/arXiv.2004.05150 (2020).
71. Pedregosa, F. et al. Scikit-learn: machine learning in Python. J. Mach. Learn. Res. 12 , 2825-2830 (2011).
72. Norman, T. M. et al. Exploring genetic interaction manifolds constructed from rich single-cell phenotypes. Science 365 , 786-793 (2019).

73. Chen, E. Y. et al. Enrichr: interactive and collaborative HTML5 gene list enrichment analysis tool. BMC Bioinf. 14 , 128 (2013).
74. Hao, M. scFoundation: large scale foundation model on single-cell transcriptomics - processed dat asets. figshare. https://doi.org/10.6084/m9.figshare.24049200.v3 (2023).
75. Hao, M. code of scFoundation: large scale foundation model on single-cell transcriptomics. Zenodo https://doi.org/10.5281/ zenodo.8330924 (2023).

####### Acknowledgements

We thank Q. Yin, L. Chao and Z. He from Biomap and Y. Chen, C. Li, H. Bian, J. Li, T . Ma, L. Wei and R. Jiang from Bioinfo Division, Tsinghua University for discussions and comments. This work was partially supported by the National Key R&amp;D Program of China (grant 2021YFF1200901), National Natural Science Foundation of China (NSFC) (grants 62250005 and 61721003) and Tsinghua-Fuzhou Institute for Data Technology (TFIDT2021005).

####### Author contributions

M.H., J.M., L.S. and X. Zhang conceived the study. M.H. X. Zeng and Y.G. collected the downstream datasets involved in this article. Y.G. and L.S. developed data collection criteria and strategies for pretraining. M.H., J.G., X. Zeng, C.L., T.W. and X.C. proposed the pretraining framework. M.H., J.G., X. Zeng and C.L. implemented and pretrained the models. M.H. and J.G. benchmarked all methods.

J.G., X. Zeng, C.L., T .W., X.C., J.M., L.S. and X. Zhang provided advice on pretraining framework design and downstream tasks. M.H., J.G., J.M., L.S. and X. Zhang wrote the manuscript. All authors read and approved the final manuscript.

####### Competing interests

J.G., X.Ze., C.L, Y .G., X.C., T .W. and L.S. are employees of BioMap. M.H. contributed to this work while part-time interning at BioMap. The remaining authors declare no competing interests.

####### Additional information

Supplementary information The online version contains supplementary material available at https://doi.org/10.1038/s41592-024-02305-7.

Correspondence and requests for materials should be addressed to Jianzhu Ma, Xuegong Zhang or Le Song.

Peer review information Nature Methods thanks the anonymous reviewers for their contribution to the peer review of this work. Primary Handling Editor: Lin Tang, in collaboration with the Nature Methods team. Peer reviewer reports are available.

Reprints and permissions information is available at www.nature.com/reprints.