## Aligning foundation models on encoded synthetic omic data for patient stratification

Nikita Janakarajan 1 Accelerated Discovery IBM Research Europe R¨ uschlikon, Switzerland nja@zurich.ibm.com 2 D-INFK ETH Z¨ urich Z¨ urich, Switzerland jnikita@inf.ethz.ch Antonio Foncubierta Rodr´ ıguez Accelerated Discovery IBM Research Europe R¨ uschlikon, Switzerland fra@zurich.ibm.com

Abstract -The use of real world health data for Foundation Model training often comes with concerns due to the potential sharing of sensitive information. Synthetic data may prove to be one of the best assets to limit such concerns. In this manuscript, we introduce a new paradigm of training Foundation Models generate synthetic data, encode it with a compression method and frequency-based mapping, and use these encoded data to align a Foundation Model. We demonstrate our pipeline on the task of colorectal cancer patient stratification into consensus molecular subtypes (CMS) using a decoder-only model. Evaluation of the aligned model on real data results in a balanced accuracy and F1 score of approximately 91%, competitive with baselines established by prior work leveraging real data as well as with models trained directly on synthetic data. Code to reproduce results is available at https://github.com/IBM/unified-lookup-tables.

Matteo Manica Accelerated Discovery IBM Research Europe R¨ uschlikon, Switzerland tte@zurich.ibm.com

Synthetic data may prove to be a valid alternative to mitigate such concerns.

## I. INTRODUCTION

The use of Large Language Models (LLMs) on tasks extending beyond natural language processing has seen tremendous success [1]-[5]. Primarily driven by data scarcity and the need for a 'one stop shop' model, this extended success has led to the development of Foundation Models (FMs) - large models trained on large amounts of data to perform a variety of downstream tasks [6]. While this presents an advantage for FMs as opposed to a task specific neural network, the performance levels can vary by task. Tasks directly relating to the 'foundational' information learned from the data often have better metrics compared to those that require some extrapolation from the information [6]. In such cases, fine-tuning FMs on such tasks leads to better results [7]. Nevertheless, FMs are being envisioned as the future of many, especially niche, domains [6], [7] as they present opportunities for a streamlined and high-performing learning process.

One domain that can benefit greatly from the use of FMs is biology. Research, especially on sequences and single cells, has seen a quick turnover of FMs [8]-[13]. Bulk omics data, on the other hand, have seen a slower adoption [14]-[16], which we hypothesise is primarily due to a scarcity of data. Moreover, due to the sensitive nature of these data, concerns regarding training data extraction [17]-[19] create a barrier to the development and adoption of FMs in clinical settings.

We propose a paradigm, outlined in Figure 1A, wherein an FM that has not been pre-trained on biological or sequencing data is aligned entirely on synthetically generated data from this domain to learn representations that will help it evaluate real data. To obfuscate the synthetic data, we encode them into strings on which the FM is aligned. To demonstrate the applicability of this paradigm, we use colorectal cancer (CRC) subtyping from RNA-Sequencing (RNA-Seq) data as our case study. Disease subtyping is an important task as it is commonly used to decide on the personalised treatment strategy and provides insights into prognosis of the patient. The proposed paradigm creates opportunities for models developed outside of a clinical facility, entirely trained on encoded synthetic data, to be utilised for inference by clinical experts within the facility without the need to share real data, as illustrated in Figure 1B. Our contributions are as follows:

- 1) Training a model entirely on synthetic biological data does not hinder learning.
- 2) Training a model on encoded synthetic data does not deteriorate performance.
- 3) Aligning a generic pre-trained language model on encoded domain-specific textual representations shows competitive performance.

## II. METHODS

We detail the different aspects of our pipeline in the following sections.

### A. Synthetic data generation

We construct a synthetic dataset from the RNA-Seq gene expression data from TCGA-COAD (Colon Adenocarcinoma) and TCGA-READ (Rectal Adenocarcinoma) projects [21]. The genes are filtered based on the findings of [22] from ≈ 60 , 000 to 40 signature genes associated with the consensus molecular subtypes (CMS). Of the 625 patients recorded, 506 have assigned CMS labels [23]. The distribution of CMS labels is highly imbalanced making learning a challenging process.

ffi ffi

π

ffi

Fig. 1. Overview of our proposed pipeline. A. Generating synthetic data from proprietary data circumvents the need to expose it to any external language model. Further encoding the synthetic data using a ULT [20] allows such data to leave the data producing facility to the external world where technical experts can align pre-trained FMs on this data. B. The aligned FM is then returned to the data producing facility for evaluation on real encoded data. The output of this aligned model can be successfully decoded using the right LUT and applied to various downstream tasks.

<!-- image -->

Training models, especially large ones, requires a substantial amount of data. Although technological advances have enabled high throughput omics data generation, their accessibility remains restricted. With the limited number of publicly available samples, overfitting and lack of generalisability becomes a serious cause for concern. In our study on CRC subtyping, the limited sample size coupled with high class imbalance makes synthetic data generation an essential step to facilitate large model training.

To this end, we follow the modified Gamma-Poisson approach proposed by [24] to sample new data for training by directly acting on count data. In this distribution-based sampling method, a reference class-specific subset of size 5

is chosen for every new sample of that class to estimate the distribution parameters. In summary, the mean and standard deviation of this subset are used to initialise a Gamma distribution. From this distribution, the rate parameter of the Poisson distribution is sampled, which generates a new observation. By directly working on count data, we reduce any statistical noise that may accompany the generation process while still maintaining the fidelity of the original data. To balance the classes while generating a sizeable dataset, we sample 50,000 new observations per class, resulting in a dataset of size 200,000. The generation step is followed by a normalisation step where all samples are log 2 -FPKM normalised following standard data processing for RNA-Seq data [25], [26]. For details on the implementation, see algorithm 1.

### Algorithm 1: Synthetic Sample Generation

Input : Dataset D with samples from multiple classes, number of synthetic samples per class ( N ), number of features/genes in the signature ( g )

Output: Set of synthetic samples S

Initialize S ←∅ ;

Set reference set size r ← 5 ;

### foreach class c in the dataset do

Let D c ⊂ D be the set of samples belonging to class c ;

<!-- formula-not-decoded -->

Randomly sample a reference set

size

r

;

Compute mean vector µ ← 1 r ∑ x ∈ R s c x ; Compute standard deviation vector

<!-- formula-not-decoded -->

Initialize synthetic sample vector s ∈ R g with same dimension as samples in D ;

<!-- formula-not-decoded -->

S FPKM = log 2 (FPKM( S ));

return S FPKM;

### B. Unified lookup tables to encode data

Recent work on limiting extraction of training data leverages a pre-processing strategy that maps patterns in the data to strings using a frequency-based mapping function before FM alignment [20]. This method, called Unified Lookup Table (ULT), efficiently tokenises data relying on compression methods. Herein we extend this method to a series of numeric values, i.e., RNA-Seq data. Inspired by compression methods for audio-signal processing [27], we apply µ -law compansion to 1-D patches extracted from expression arrays. This allows to efficiently represent signals by optimising the dynamic range and quantising the numerical values. By doing so, the quantisation error can be minimised while controlling the sequence size.

To extend ULT to RNA-Seq data, after splitting the samples into fixed-size patches, we normalise values using the maximum desired companding value, c m , which limits the dynamic range of the values and minimises the quantisation error. These normalised values are then compressed using a logarithmic function, followed by non-linear quantisation. The non-linear quantisation results in higher precision for smaller

s

R

c

⊂

D

c

of values and lower precision for larger values, thus amplifying any variations in smaller values. The size of the patches ( d ), c m and µ are all hyperparameters that can be tuned to the task and data. Equation 1 formalises the method for a given patch vector x ∈ R d .

<!-- formula-not-decoded -->

Following the lead of [20], patterns arising postcompression are then sorted by frequency of appearance and mapped to Unicode characters, which are stored in a Lookup Table (LUT). The stable sorting of patterns by frequency enables the FM to learn by 'reasoning' on relative frequencies without needing to know the actual mapping. This LUT is the key to encoding and decoding the data.

### C. Decoder-only foundation models

Decoder-only models are the de-facto standard for language modelling and foundation models [28]-[31]. Their popularity comes from lower training efforts and costs, and being empirically proven as the best choice for zero-shot generalisation [32]. This feature is particularly important for biomedical tasks due to low availability of good task representative data. Moreover, the causal modelling aspect ensures the model sees the entire input, thus enabling it to learn the complex interdependencies between elements, common in biomedical data, for predictive and generative tasks.

In our experiments, we consider HuggingFace's SmolLM1.7B [33], a 1.7 billion parameter decoder-only model. This model has a context length of 2048 tokens and has been pretrained on 1T tokens from a corpus spanning natural language samples in English and Python code. It is important to note that this model has not been pre-trained on RNA-Seq data or expression arrays of any sort.

## III. RESULTS

To demonstrate our contributions, we consider the task of CRC subtyping - classifying a CRC patient into one of four consensus molecular subtypes (CMS1-4) using RNA-Seq gene expression data.

### A. Experimental setting

The experiments are structured to demonstrate our three contributions. Given the TCGA-COAD and TCGA-READ RNA-Seq count datasets, henceforth called 'real', we apply the modified Gamma-Poisson sampling to generate a synthetic dataset of size 200,000, henceforth referred to as 'synthetic', such that each subtype has 50,000 samples. This synthetic dataset acts as our training dataset and the real dataset is the hold out test set.

To demonstrate that training on synthetic data does not hinder learning, we train two classifier models, specifically K-nearest neighbours (KNN) and random forest (RF), on the synthetic dataset and evaluate them on the real dataset. The KNN is selected to minimise the inductive bias due to modelling assumptions, while the RF is the algorithm used to define CMS labels from RNA-Seq data [23]. We use the default scikit-learn [34] implementations of both models.

To determine whether encoding the data affects performance on downstream tasks, we use the method described in Section II-B to build a LUT using the synthetic dataset. For hyperparameters, we select the following ranges: patch size d = { 10 , 20 , 40 } , c m = { 0 . 5 , 1 . 0 , 1 . 5 , 2 . 0 , 2 . 5 , 3 . 0 } and µ = { 1 , 64 , 128 , 256 } for maximising correlations of euclidean distance between vectors in the input space and Levenshtein distance between the same vectors encoded in the string space. Tuning resulted in patch size d = 10 , c m = 1 and µ = 256 as being optimal. The LUT is then used to encode the synthetic data into unicode strings. The unicode strings are tokenised using the pre-trained SmolLM-1.7B's tokeniser. Since we use causal modelling for classification, the four CMS classes are also assigned a token and passed to the tokeniser as additional tokens. The training input prompt to the decoder-only model is the tokenised unicode string followed by a separator token and the CMS token. At inference time, only the tokenised unicode string followed by a separator token is passed and the decoder is expected to output the predicted class token for that sample. The model is trained for 20 epochs with early stopping after 8 steps. The model is trained with bf16 mixed precision training at a learning rate of 1 e -4 and batch size 32. The trained model is then evaluated on the real dataset.

The experiment is repeated 10 times by varying the seed to generate synthetic data while keeping the model seed fixed. For each repetition, the real dataset, which is the holdout test set, is standardised using the training synthetic data's parameters.

### B. Training on synthetic data does not hinder learning

Training KNN and RF classifier models on synthetic data achieves 90.8% and 90.49% average balanced accuracy, and 91.3% and 90.39% average F1-score on the real test data as seen in Table I, respectively. The balanced accuracy scores are in line with what has been reported in literature in independent studies on CMS classification [23], [35], which have been trained and evaluated on real data. A 5x5 repeated stratified cross-validation experiment conducted by [24] found that training and testing only on real data using the 40 signature genes proposed by [22] resulted in an average balanced accuracy of 84.1% for the KNN and 86.1% for the RF models. Comparing these results from prior works to our experimental results suggests that synthetic data plays an important role in learning.

### C. Training on encoded data shows competitive performance

Aligning a language model, pre-trained on English text and Python code, to synthetic RNA-Seq data, encoded as unicode strings, results in a comparable balanced accuracy compared to baseline models trained directly on synthetic data and significantly outperforms baselines trained exclusively on real data. The aligned FM achieves an average balanced accuracy of 90.82% and an average F1-score of 90.98%. We additionally report the confusion matrix from the aligned FM (Figure 2) to detail per class performance. These results demonstrate that encoding the data does not deteriorate performance and that aligning an FM, that is not pre-trained on any biological data, on these encoded representations leads to performance that is competitive with the baselines.

Fig. 2. Confusion matrix of the aligned FM in stratifying patients into the four CMS classes. These results show that pre-training an FM on an unrelated domain followed by encoded synthetic data alignment for the desired task retains performance relative to baselines.

<!-- image -->

## IV. DISCUSSION

Generating synthetic data for training addresses the data scarcity and class imbalance problem, while removing the need for sharing real patient data. Based on the results in Table I, we see that training on synthetic data does not have any negative effects on learning, as evidenced by the models' performance on real data during evaluation. This is a crucial finding, as it supports the use of synthetic data for training in a data-scarce field, especially one where maintaining the fidelity of the data is of utmost importance due its potential clinical implications. However, it is to be noted that the fidelity is directly controlled by the method for data generation, which must be chosen carefully. In our experiments, we use a modification of the Gamma-Poisson distribution, which has been proven to accurately approximate RNA-Seq count data distribution [24].

We encode the data using a ULT [20] into a form that is obfuscated. Machine learning models rely on patterns in the data to learn statistical relationships between the input and output. We exploit this core fundamental feature of machine learning to encode the data in such a way that relationships are preserved, while original patterns are not immediately evident. This is primarily done by a suitable compression method which reduces data to a set of recurring patterns. By using a LUT to map these patterns to unicode characters, the data is encoded in a string space that can be processed by any language model. Knowledge of the LUT is required in order to successfully decode the data. As described by [20], a successful encoding stems from choosing the right compression method as it influences pattern regularities. The compression method becomes a hyperparameter in itself and should be chosen depending on the data type being compressed and the desired signal-to-noise ratio. In this work we have used µ -law compansion as a way to compress numerical sequences.

TABLE I PERFORMANCE COMPARISON OF DIFFERENT MODELS

| Model      | Synthetic   | Encoded   | Balanced Accuracy   | F1-Score          |
|------------|-------------|-----------|---------------------|-------------------|
| KNN [24]   | ✗           | ✗         | 0 . 841 ± 0 . 035   | -                 |
| RF [24]    | ✗           | ✗         | 0 . 861 ± 0 . 034   | -                 |
| KNN        | ✓           | ✗         | 0 . 908 ± 0 . 006   | 0 . 913 ± 0 . 005 |
| RF         | ✓           | ✗         | 0 . 905 ± 0 . 007   | 0 . 904 ± 0 . 006 |
| Aligned FM | ✓           | ✓         | 0 . 908 ± 0 . 015   | 0 . 910 ± 0 . 012 |

Transforming inputs into the string space makes it processable by any language model. Since biological data are especially known for complex non-linear dependencies between different measured elements, for the task of CMS classification, a decoder-only model is the best choice. This model processes the entire input sequence with auto-regressive attention, enabling it to learn contextual information from input sequences to generate the sample class. By fine-tuning or aligning an LLM, not pre-trained on any biological or sequencing data, to classify CMS using only encoded synthetic data, we create an FM for patient stratification. Evaluating this FM on real data resulted in a competitive performance with models trained on un-encoded data (Table I). The aligned FM also performed better than the baselines in CMS3 and CMS4 classification (Figure 2). These results prove that the encoding step did not hinder learning. This marks a critical advancement in biomedical data analysis - training FMs on encoded synthetic data can still perform competitively on real data.

Although the proposed paradigm has its advantages, limitations exist. First, there are multiple hyperparameters involved that require careful selection. The choice of data generation and data compression methods are major influencing factors in the success of this pipeline. Second, depending on the complexity of the data and/or task, a larger pre-trained model may be better suited to learn inter-dependencies in the data, which could be a computational burden.

This work proves that FMs aligned on encoded synthetic data are successful in real world patient stratification tasks. Future work could evaluate this pipeline on other tasks such as missing modality or value imputation, cross-modality translation, and learning embeddings for downstreams tasks. Other areas of future research include analysing the effect of model size on performance for different data and task complexities, and the impact of using pre-trained models versus training from scratch on the learning process.

### REFERENCES

- [1] H. Liu, C. Li, Q. Wu, and Y. J. Lee, 'Visual instruction tuning,' Advances in neural information processing systems , vol. 36, pp. 34 89234 916, 2023.
- [2] P. Agrawal, S. Antoniak, E. B. Hanna, B. Bout, D. Chaplot, J. Chudnovsky, D. Costa, B. De Monicault, S. Garg, T. Gervet et al. , 'Pixtral 12b,' arXiv preprint arXiv:2410.07073 , 2024.
- [3] R. Huang, M. Li, D. Yang, J. Shi, X. Chang, Z. Ye, Y. Wu, Z. Hong, J. Huang, J. Liu et al. , 'Audiogpt: Understanding and generating speech, music, sound, and talking head,' in Proceedings of the AAAI Conference on Artificial Intelligence , vol. 38, no. 21, 2024, pp. 23 802-23 804.
- [4] Z. Kong, A. Goel, R. Badlani, W. Ping, R. Valle, and B. Catanzaro, 'Audio flamingo: A novel audio language model with few-shot learning and dialogue abilities,' arXiv preprint arXiv:2402.01831 , 2024.
- [5] Z. Pan, Y. Jiang, S. Garg, A. Schneider, Y. Nevmyvaka, and D. Song, ' s 2 ip-llm: Semantic space informed prompt learning with llm for time series forecasting,' in Forty-first International Conference on Machine Learning , 2024.
- [6] R. Bommasani, D. A. Hudson, E. Adeli, R. Altman, S. Arora, S. von Arx, M. S. Bernstein, J. Bohg, A. Bosselut, E. Brunskill et al. , 'On the opportunities and risks of foundation models,' arXiv preprint arXiv:2108.07258 , 2021.
- [7] K. Lu, A. Grover, P. Abbeel, and I. Mordatch, 'Frozen pretrained transformers as universal computation engines,' in Proceedings of the AAAI conference on artificial intelligence , vol. 36, no. 7, 2022, pp. 76287636.
- [8] Z. Lin, H. Akin, R. Rao, B. Hie, Z. Zhu, W. Lu, N. Smetanin, R. Verkuil, O. Kabeli, Y. Shmueli et al. , 'Evolutionary-scale prediction of atomiclevel protein structure with a language model,' Science , vol. 379, no. 6637, pp. 1123-1130, 2023.
- [9] E. Nguyen, M. Poli, M. G. Durrant, B. Kang, D. Katrekar, D. B. Li, L. J. Bartie, A. W. Thomas, S. H. King, G. Brixi et al. , 'Sequence modeling and design from molecular to genome scale with evo,' Science , vol. 386, no. 6723, p. eado9336, 2024.
- [10] H. Cui, C. Wang, H. Maan, K. Pang, F. Luo, N. Duan, and B. Wang, 'scgpt: toward building a foundation model for single-cell multi-omics using generative ai,' Nature Methods , vol. 21, no. 8, pp. 1470-1480, 2024.
- [11] M. Hao, J. Gong, X. Zeng, C. Liu, Y. Guo, X. Cheng, T. Wang, J. Ma, X. Zhang, and L. Song, 'Large-scale foundation model on single-cell transcriptomics,' Nature methods , vol. 21, no. 8, pp. 1481-1491, 2024.
- [12] F. Yang, W. Wang, F. Wang, Y. Fang, D. Tang, J. Huang, H. Lu, and J. Yao, 'scbert as a large-scale pretrained deep language model for cell type annotation of single-cell rna-seq data,' Nature Machine Intelligence , vol. 4, no. 10, pp. 852-866, 2022.
- [13] X. Yang, G. Liu, G. Feng, D. Bu, P. Wang, J. Jiang, S. Chen, Q. Yang, H. Miao, Y. Zhang et al. , 'Genecompass: deciphering universal gene regulatory mechanisms with a knowledge-informed cross-species foundation model,' Cell Research , vol. 34, no. 12, pp. 830-845, 2024.
- [14] A. Waqas, A. Tripathi, S. Ahmed, A. Mukund, H. Farooq, M. B. Schabath, P. Stewart, M. Naeini, and G. Rasool, 'Self-normalizing foundation model for enhanced multi-omics data analysis in oncology,' arXiv preprint arXiv:2405.08226 , 2024.
- [15] W. Zhu, Y. Chen, S. Nie, and H. Yang, 'Samms: Multi-modality deep learning with the foundation model for the prediction of cancer patient survival,' in 2023 IEEE International Conference on Bioinformatics and Biomedicine (BIBM) . IEEE, 2023, pp. 3662-3668.

- [16] H. Wang, Y. Yang, Z. Zhao, P. Gu, N. Sapkota, and D. Z. Chen, 'Pathgptomic: A balanced multi-modal learning framework for survival outcome prediction,' in 2024 IEEE International Symposium on Biomedical Imaging (ISBI) . IEEE, 2024, pp. 1-5.
- [17] B. Murdoch, 'Privacy and artificial intelligence: challenges for protecting health information in a new era,' BMC medical ethics , vol. 22, pp. 1-5, 2021.
- [18] N. Carlini, F. Tramer, E. Wallace, M. Jagielski, A. Herbert-Voss, K. Lee, A. Roberts, T. Brown, D. Song, U. Erlingsson et al. , 'Extracting training data from large language models,' in 30th USENIX security symposium (USENIX Security 21) , 2021, pp. 2633-2650.
- [19] M. Nasr, J. Rando, N. Carlini, J. Hayase, M. Jagielski, A. F. Cooper, D. Ippolito, C. A. Choquette-Choo, F. Tram` er, and K. Lee, 'Scalable extraction of training data from aligned, production language models,' in The Thirteenth International Conference on Learning Representations , 2025. [Online]. Available: https://openreview.net/forum?id=vjel3nWP2a
- [20] N. Janakarajan, I. E. Morales, M. Alberts, A. Giovannini, M. Manica, and A. Foncubierta-Rodr´ ıguez, 'Unified lookup tables: Privacypreserving foundation models,' in Workshop on Machine Learning and Compression, NeurIPS 2024 , 2024.
- [21] C. G. A. Network et al. , 'Comprehensive molecular characterization of human colon and rectal cancer,' Nature , vol. 487, no. 7407, p. 330, 2012.
- [22] S. A. Buechler, M. T. Stephens, A. B. Hummon, K. Ludwig, E. Cannon, T. C. Carter, J. Resnick, Y. G¨ okmen-Polar, and S. S. Badve, 'Colotype: a forty gene signature for consensus molecular subtyping of colorectal cancer tumors using whole-genome assay or targeted rna-sequencing,' Scientific reports , vol. 10, no. 1, p. 12123, 2020.
- [23] J. Guinney, R. Dienstmann, X. Wang, A. De Reynies, A. Schlicker, C. Soneson, L. Marisa, P. Roepman, G. Nyamundanda, P. Angelino et al. , 'The consensus molecular subtypes of colorectal cancer,' Nature medicine , vol. 21, no. 11, pp. 1350-1356, 2015.
- [24] N. Janakarajan, M. Graziani, and M. R. Mart´ ınez, 'Phenotype driven data augmentation methods for transcriptomic data,' Bioinformatics Advances , p. vbaf124, 05 2025. [Online]. Available: https://doi.org/10. 1093/bioadv/vbaf124
- [25] M.-A. Dillies, A. Rau, J. Aubert, C. Hennequet-Antier, M. Jeanmougin, N. Servant, C. Keime, G. Marot, D. Castel, J. Estelle et al. , 'A comprehensive evaluation of normalization methods for illumina highthroughput rna sequencing data analysis,' Briefings in bioinformatics , vol. 14, no. 6, pp. 671-683, 2013.
- [26] S. Zhao, Z. Ye, and R. Stanton, 'Misuse of rpkm or tpm normalization when comparing across samples and sequencing protocols,' Rna , vol. 26, no. 8, pp. 903-909, 2020.
- [27] C. Recommendation, 'Pulse code modulation (pcm) of voice frequencies,' in ITU , 1988.
- [28] J. Achiam, S. Adler, S. Agarwal, L. Ahmad, I. Akkaya, F. L. Aleman, D. Almeida, J. Altenschmidt, S. Altman, S. Anadkat et al. , 'Gpt-4 technical report,' arXiv preprint arXiv:2303.08774 , 2023.
- [29] I. Granite Team, 'Granite 3.0 language models,' 2024.
- [30] H. Touvron, T. Lavril, G. Izacard, X. Martinet, M.-A. Lachaux, T. Lacroix, B. Rozi` ere, N. Goyal, E. Hambro, F. Azhar et al. , 'Llama: Open and efficient foundation language models,' arXiv preprint arXiv:2302.13971 , 2023.
- [31] Anthropic, 'The claude 3 model family: Opus, sonnet, haiku.' [Online]. Available: https://api.semanticscholar.org/CorpusID:268232499
- [32] T. Wang, A. Roberts, D. Hesslow, T. Le Scao, H. W. Chung, I. Beltagy, J. Launay, and C. Raffel, 'What language model architecture and pretraining objective works best for zero-shot generalization?' in International Conference on Machine Learning . PMLR, 2022, pp. 22 964-22 984.
- [33] L. B. Allal, A. Lozhkov, E. Bakouch, L. von Werra, and T. Wolf, 'Smollm - blazingly fast and remarkably powerful,' 2024.
- [34] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg et al. , 'Scikit-learn: Machine learning in python,' the Journal of machine Learning research , vol. 12, pp. 2825-2830, 2011.
- [35] P. W. Eide, J. Bruun, R. A. Lothe, and A. Sveen, 'Cmscaller: an r package for consensus molecular subtyping of colorectal cancer preclinical models,' Scientific reports , vol. 7, no. 1, p. 16618, 2017.