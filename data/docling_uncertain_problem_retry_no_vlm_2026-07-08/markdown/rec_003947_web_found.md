age

age

age Breast cancer is a heterogeneous disease, comprising multiple entities associated with to therapy.

clinical presentations and behaviours and responses

distinctive histological and biological features,

-

Microarray

based technologies have unravel ed the

molecular underpinning of several characteristics of

breast cancer, including metastatic propensity and

histological grade, and have led to the identification of

prognostic and predictive gene expression signatures.

Breast cancer is a heterogeneous disease,

comprising multiple entities associated with

to therapy.

clinical presentations and behaviours and responses

distinctive histological and biological features,

-

Microarray

based technologies have unravel ed the

molecular underpinning of several characteristics of

breast cancer, including metastatic propensity and

histological grade, and have led to the identification of

prognostic and predictive gene expression signatures.

Breast cancer is a heterogeneous disease,

comprising multiple entities associated with

I

mage

to therapy.

T

distinctive histological and biological features,

-

Microarray

ext

prognostic and predictive gene expression signatures.

clinical presentations and behaviours and responses

based technologies have unravel ed the

molecular underpinning of several characteristics of

breast cancer, including metastatic propensity and

histological grade, and have led to the identification of Breast cancer is a heterogeneous disease, comprising multiple entities associated with to therapy.

<!-- image -->

<!-- image -->

This WACV paper is the Open Access version, provided by the Computer Vision Foundation. Except for this watermark, it is identical to the accepted version; the final published version of the proceedings is available on IEEE Xplore.

Breast cancer is a heterogeneous disease,

comprising multiple entities associated with

distinctive histological and biological features,

clinical presentations and behaviours and responses

to therapy.

#### to therapy. Microarray -based technologies have unravel ed the molecular underpinning of several characteristics of breast cancer, including metastatic propensity and histological grade, and have led to the identification of prognostic and predictive gene expression signatures. to therapy. Microarray molecular underpinning of several characteristics of breast cancer, including metastatic propensity and histological grade, and have led to the identification of prognostic and predictive gene expression signatures. Breast cancer is a heterogeneous disease, comprising multiple entities associated with distinctive histological and biological features, clinical presentations and behaviours and responses -based technologies have unravel ed the Breast cancer is a heterogeneous disease, comprising multiple entities associated with distinctive histological and biological features, clinical presentations and behaviours and responses CLIP-IT : CLIP-based Pairing of Histology Images with Privileged Textual Information

clinical presentations and behaviours and responses

distinctive histological and biological features,

-

Microarray

based technologies have unravel ed the

molecular underpinning of several characteristics of

breast cancer, including metastatic propensity and

histological grade, and have led to the identification of Microarray molecular underpinning of several characteristics of breast cancer, including metastatic propensity and histological grade, and have led to the identification of clinical presentations and behaviours and responses Breast cancer is a heterogeneous disease, comprising multiple entities associated with distinctive histological and biological features,

-

to therapy.

based technologies have unravel ed the

based technologies have unravel ed the

Microarray

-

molecular underpinning of several characteristics of

breast cancer, including metastatic propensity and

histological grade, and have led to the identification of

Breast cancer is a heterogeneous disease, comprising multiple entities associated with distinctive histological and biological features, clinical presentations and behaviours and responses to therapy. Microarray -based technologies have unravel ed the molecular underpinning of several characteristics of breast cancer, including metastatic propensity and histological grade, and have led to the identification of prognostic and predictive gene expression signatures. Breast cancer is a heterogeneous disease, comprising multiple entities associated with distinctive histological and biological features, clinical presentations and behaviours and responses to therapy. Microarray -based technologies have unravel ed the molecular underpinning of several characteristics of breast cancer, including metastatic propensity and histological grade, and have led to the identification of prognostic and predictive gene expression signatures. Breast cancer is a heterogeneous disease, comprising multiple entities associated with distinctive histological and biological features, clinical presentations and behaviours and responses to therapy. Microarray -based technologies have unravel ed the molecular underpinning of several characteristics of breast cancer, including metastatic propensity and histological grade, and have led to the identification of prognostic and predictive gene expression signatures. I mage T ext I mage T ext I mage T ext Banafsheh Karimian 1 Giulia Avanzato 2 * Soufiane Belharbi 1 * Alexis Guichemerre 1 * Luke McCaffrey 3 Mohammadhadi Shateri 1 Eric Granger 1 1 LIVIA, ILLS, Dept. of Systems Engineering, ETS Montreal, Canada 2 Dept. of Computer Engineering, University of Cagliari, Italy 3 Goodman Cancer Institute, Dept. of Oncology, McGill University, Canada

prognostic and predictive gene expression signatures.

prognostic and predictive gene expression signatures.

prognostic and predictive gene expression signatures.

1 { banafsheh.karimian.1, alexis.guichemerre.1, soufiane.belharbi, mohammadhadi.shateri, eric.granger } @etsmtl.ca, 2 g.avanzato@studenti.unica.it, 3 luke.mccaffrey@mcgill.ca

## Abstract

Multimodal learning has shown promise in medical imaging, combining complementary modalities like images and text. Vision-language models (VLMs) capture rich diagnostic cues but often require large paired datasets and promptor text-based inference. Their practicality is therefore limited due to annotation cost, privacy, and compute demands. Unpaired external text, like pathology reports, can still provide complementary diagnostic cues if semantically relevant content is retrievable per image. To address this, we introduce CLIP-IT , a novel framework that relies on rich unpaired text reports. Specifically, CLIP-IT uses a CLIP model pre-trained on histology image-text pairs from a separate dataset to retrieve the most relevant unpaired textual report for each image in the downstream unimodal dataset. These reports, sourced from the same disease domain and tissue type, form pseudo-pairs that reflect shared clinical semantics rather than exact alignment. Knowledge from these texts is distilled into the vision model during training, while LoRA-based adaptation mitigates the semantic gap between unaligned modalities. At inference, only the vision model is used, maintaining low overhead while still benefiting from multimodal training without requiring paired data in the downstream dataset. Experiments 1 show that CLIP-IT consistently improves classification accuracy over both unimodal and multimodal CLIP-based baselines in most cases, without requiring paired annotations per dataset or incurring additional inference-time complexity.

* Equal contribution

1 https://github.com/BanafshehKarimian/ModalityPairing/tree/main

## 1. Introduction

Cancer diagnosis is among the most critical and challenging tasks [17]. To ensure a comprehensive understanding of cancer, medical professionals rely on the results of multiple modalities, such as histology images, genomic profiles, and pathology reports. Although machine and deep learning (ML/DL) models have shown great potential in advancing cancer analysis, unimodal models have limited ability to capture the complex, multifaceted nature of cancer, reducing model accuracy, robustness, and generalizability [1, 10, 11]. Multimodal learning addresses these limitations by using the complementary strengths of each modality to improve performance [27]. For instance, histology images have fine-grained morphological details, while pathology reports capture high-level clinical context. Combining these complementary modalities improves predictive accuracy, interpretability, and robustness, making models more resilient to noise and missing information [4].

Recent works [1, 18, 25] have shown that multimodal approaches have great potential for cancer detection and diagnosis, significantly pushing the boundaries of what ML can achieve in this field. A prominent class of recent multimodal models is vision-language models (VLMs), which jointly learn from paired image-text data to capture spatial and semantic information. These models, such as CLIP [26] and its medical variants, such as CONCH [20], which are trained on paired image-text datasets to jointly capture spatial and semantic information. Although their inference is often unimodal or prompt-based, these models depend on large-scale datasets with image-text pairs during training. However, in histopathology, obtaining such pairs for each dataset is expensive and time-consuming and requires strict privacy compliance and institutional approvals. Most publicly available datasets, such as PCAM [28, 29], BACH [2], and CRC [24], contain only histology images, lacking the paired textual annotations needed for such training, which limits the scalability of these approaches.

In contrast, prompt-based methods [22] use short texts, handcrafted or template prompts at both training and inference time, bypassing the need for real reports altogether. While this approach reduces data collection costs, it is inherently limited in expressiveness and fails to reflect the nuanced, case-specific insights present in authentic pathology reports. Furthermore, these models are shown to be highly sensitive to minor changes in phrasing for pathology [3], leading to instability in clinical applications. Generative language models offer an alternative by synthesizing full reports given an image, but they are often proprietary, and expensive to run. Thus, both approaches face critical barriers in terms of scalability, reliability, and clinical applicability.

To address these challenges, we propose CLIP-IT a method that enables multimodal training for unimodal image classification. CLIP-IT uses freely available resources, i.e., unpaired textual reports from other datasets together with existing pretrained models, thus avoiding the need for paired annotations in each downstream dataset. This is especially beneficial in domains like pathology, where aligned datasets are scarce. The core idea is to consider unpaired but semantically relevant textual information as a form of privileged supervision, only available during training. Using a CLIP-based retrieval model, it automatically pairs each histology image with the most relevant textual report from another dataset of the same disease domain and tissue type. This forms pseudo-pairs that capture shared semantics rather than exact correspondence, enabling us to enrich unimodal datasets with complementary high-level information from text. Knowledge distillation is then used to transfer information from the text modality into the vision model, allowing efficient unimodal inference without requiring the text or text models at test time. Figure 1 illustrates how CLIP-IT setting compares to other paradigms: unlike traditional unimodal or fully paired multimodal models, and unlike CLIP-based approaches that rely on paired data during training and prompts at inference, CLIP-IT performs multimodal training with unpaired data and enables efficient unimodal deployment without requiring paired annotations in the downstream dataset.

This work studies how multimodal learning can be used even when only unimodal datasets are available, an important direction for data-scarce domains like pathology, where collecting aligned multimodal samples is costly, time-consuming, and restricted by privacy regulations. By relying on semantically relevant external data as privileged information during training, our method enables the integration of diverse and heterogeneous data sources into medical AI pipelines. The contributions of this paper are as follows: (1) We introduce CLIP-IT to improve histology classification, through multimodal learning, without the need for manually curated paired annotations of all the downstream datasets. It extends unimodal histology datasets by pairing them with histology reports from external datasets, creating a pseudo-paired multimodal dataset that includes potentially complementary textual information.

(2) CLIP-IT uses complementary text from another dataset as privileged information, using knowledge distillation to transfer information from the text modality to the vision model during training. This enables the use of multimodal information without requiring text or text-related models at test time, allowing for efficient unimodal inference. A LoRA-based adaptation is used to handle noise and misalignment in the pseudo-paired training signals.

(3) Our extensive experiments show the effectiveness of CLIP-IT in improving histology image classification of unimodal datasets. On the unimodal front, CLIP-IT improves accuracy by up to 4 . 4% , 3 . 6% , and 1 . 5% on PCAM, BACH, and CRC, respectively, all with minimal additional inference overhead. Notably, CLIP-IT is a flexible framework that can be integrated with a variety of unimodal vision architectures, without requiring architectural modifications. This makes it broadly adaptable across standard vision backbones commonly used in histopathology. Furthermore, compared to state-of-the-art multimodal models specific to histology, such as CONCH [20] and QUILTNet [15], CLIP-IT achieves a higher accuracy across most cases, while maintaining comparable performance in the rest, and without requiring paired annotations for the downstream dataset or dual-modality inference.

## 2. Related Work

Wesummarize key trends and limitations of multimodal approaches for histopathology in following subsections.

(a) Integration of Histology Images with Other Modalities: One commonly used modality alongside histology images is genomic data [5, 18, 21, 25, 31, 32, 35, 36]. However, it is costly, often unavailable, and difficult to integrate due to high dimensionality and preprocessing demands, with studies using WSIs and genomic profiles [5, 36] facing major data and compute challenges. Another increasingly explored modality is text, in the form of clinical reports or structured annotations derived from medical records [16]. Recent works align histology images with such textual information to improve performance, especially for survival analysis with missing modalities [25]. For example, PathM3 [37] uses limited paired WSI-caption data to enhance MIL-based classification. Building on these efforts, contrastive VLMs have emerged as powerful frameworks that align histology images and text through large-scale pretraining. Prominent examples such as CONCH [20] and QUILTNet [15] are trained on extensive paired datasets and demonstrate strong performance across a wide range of pathology tasks, including classification, segmentation, and retrieval. However, their reliance on curated image-text pairs limits training scalability, and their zero-shot promptbased performance remains suboptimal, motivating using unpaired data when per-dataset pairing is unavailable.

Figure 1. Overview of four learning approaches: (a) unimodal setting (image-only), (b) paired multimodal setting, requiring aligned image-text pairs at both training and inference, (c) Prompt-based CLIP-style VLMs (e.g., CONCH), trained on paired data and needing text prompts at inference, and (d) the proposed CLIP-IT setting that uses unpaired external reports for multimodal supervision during training, but supports lightweight unimodal inference of downstream dataset.

<!-- image -->

(b) Histology Image to Text Translation: Recent work has explored generating textual descriptions from histology images, either to summarize WSIs [7, 12] or extract structured visual features aligned with pathology hierarchies [30]. These methods require paired image-text datasets, which are costly to produce due to the need for expert annotation and validation. Moreover, training such generative models is computationally intensive, especially with large vision-language architectures [14].

(c) Prompt-based Vision-Language Models: Among VLMs, short description or prompt-based methods stand out for their simplicity and effectiveness. They have been applied to tasks like WSI-based genetic biomarker prediction [34], data augmentation [23], adaptation of foundation models to pathology with task-specific visual and textual prompts [19], and detection of rare or novel diseases using disease-informed prompts and prototype learning [33]. A related method [22] was proposed that generates keywordbased short sentences, selecting top-k prompts to derive more interpretable embeddings, which improves model explainability. However, prompt-based models rely heavily on handcrafted templates or keyword phrases, which may fail to capture the nuanced language and reasoning found in real clinical reports. Moreover, they are highly sensitive to prompt phrasing and offer limited coverage over complex diagnostic scenarios. Prior work [3] also highlights prompt sensitivity to phrasing, showing that minor variations can significantly impact model performance, espe- cially in pathology. Thus, prompt-based tuning may fall short when trying to encode the full range of pathological descriptions necessary for robust diagnosis.

In summary, current multimodal approaches in histopathology often face significant limitations: textgeneration models require paired annotations and introduce computational costs, and prompt-based VLMs are constrained by prompt sensitivity. Large-scale VLMs such as CONCH have demonstrated strong performance across multiple tasks, but rely on extensive paired training data and impose significant inference overhead due to large text encoders. These limitations motivate the need for CLIP-IT , a lightweight alternative that still uses rich textual knowledge, via unpaired rich clinical data, but without requiring annotations for each downstream dataset or the high cost of a language backbone at inference time.

## 3. Proposed CLIP-IT Method

CLIP-IT is proposed to enhance unimodal histology image classification using an external unpaired text modality, containing reports from the same domain, as privileged information during training. Although these reports are not aligned with the downstream dataset, they carry complementary domain knowledge, such as diagnostic terminology, patterns of disease progression, and clinical reasoning, that help the model learn richer semantic representations and improve generalization. CLIP-IT retrieves the most semantically relevant external report for each image using an off-the-shelf CLIP-based model trained elsewhere on paired data. Importantly, this requires no paired annotations for the downstream dataset, since the pairing is performed automatically at retrieval time. Knowledge from these pseudo-pairs is distilled into the vision model, enabling it to learn from text during training while requiring only images at inference time. Figure 2 shows an overview of the CLIP-IT pipeline, including image-text modality pairing, multimodal distillation, and unimodal inference. The remainder of this section details CLIP-IT component.

### 3.1. Image-Text Modality Pairing

Let us consider a unimodal histology dataset D I = { ( I i , y i ) } N i =1 , composed of N images and the corresponding image class label y i for each image, I i . We consider an external text dataset, D T = { T j } j M =1 , composed of M histology medical reports, providing diagnostic observations and other clinical insights. The only assumption that we have for the two datasets, D T and D I , is that they are relevant histology data, meaning they originate from the same organ type or disease domain (e.g., breast, colorectal), without the need to be explicitly paired at the sample level. Using the external dataset D T , we augment our image dataset D I from unimodal into a new multimodal dataset D ′ , containing vision-text-label pairs. To this end, an off-the-shelf CLIP model is used, pre-trained on paired histology images and text, composed of a vision encoder, f v , and a text encoder, f t . While these pretrained models depend on paired data at their origin, our contribution lies in showing that once trained, they can be reused as one-time resources to enable pseudo-pairing across many downstream unimodal datasets without further paired annotations. We define vision embeddings as v i = f v ( I i ) for I i ∈ D I over images, and text embeddings as: t j = f t ( T j ) for T j ∈ D T over the external text dataset.

Given a vision embedding v i of an image I i from D I , we use the CLIP-model capacity of pairing image-text to find the most relevant text T j ∗ , with j ∗ defined as follows, from the external dataset D T to be paired with I i . This is achieved by finding the text with the highest cosine similarity with the image in their feature space using ψ :

<!-- formula-not-decoded -->

A pseudo-paired dataset is constructed with the paired vision-text modality noted as D ′ = { ( I i , T ψ ( i ) , y i ) } N i =1 . This pairing procedure is illustrated in Figure 2 (part a).

### 3.2. CLIP-IT Multimodal Distillation

Akey challenge in leveraging unpaired text is how to transfer its information into a vision model, trained on an unpaired image-only dataset. To address this, we fine-tune the text encoder f t with a classification head h t on top, using the paired text-label data ( T ψ ( i ) , y i ) N i =1 . This supervision guides the transformer's attention to focus on class-relevant regions within the text. The text classifier h t ( · ) is trained to minimize the Cross-Entropy loss:

<!-- formula-not-decoded -->

where ˆ y i = h t ( t i ) , and C is the total number of classes.

After fine-tuning the text encoder on paired reports, this textual supervision must be effectively transferred into the vision model. Since the text and image data originate from different datasets, they are not paired manually. Therefore, early fusion techniques, i.e., combine modalities at the input or feature level, are not the best option [27]. We instead adopt a late fusion technique that processes each modality separately and merges output predictions at the decision level. In particular, we employ a logit fusion module, g , that combines the class logits from the image model, h v ( f ′ v ( I )) , and the text model, h t ( f t ( T )) , requiring no modification to the vision backbones. This makes CLIP-IT applicable to any vision model with any architecture.

While this multimodal training uses complementary information from both modalities to potentially enhance performance over unimodal baselines, the resulting model still depends on the text modality at inference time, introducing additional computational and architectural complexity. To bypass this, we propose to use knowledge distillation at the feature level between both modalities. In particular, we consider distilling the features of text modality into a branch of the vision model. This is achieved by training a module h d ( v i ) = ˆ t i to predict text features ˆ t i from vision features v i as shown in Figure 2 (part b). This module is trained by minimizing the following loss function:

<!-- formula-not-decoded -->

Overall, our model is trained using the following loss:

<!-- formula-not-decoded -->

where λ is a weighting coefficient. The full multimodal model is denoted as M θ M = { f t , f ′ v , h t , h v , h d , g } . Given the lack of alignment between modalities, freezing pretrained encoders limits adaptation to the target task. However, full fine-tuning is expensive and sensitive to hyperparameters. To balance adaptability and efficiency, we adopt LoRA [13], which enables low-cost tuning by using lightweight trainable layers into the backbone.

### 3.3. Unimodal Inference

Once the multimodal distillation is complete, CLIP-IT discards the text encoder, f t , during inference by relying only on the image-based components of the trained model (see Figure 2, part c). Specifically, the final model M θ U = { f ′ v , h d , h t , h v , g } uses the distilled knowledge from the text modality, embedded in the auxiliary module h d . This approximates text features from image embeddings. At test time, only an image I is input through the vision encoder to obtain features v = f ′ v ( I ) , which are transformed by h d into an estimated textual representation ˆ t = h d ( v ) . These representations are then fused at the logit level using the fusion module g ( h t ( ˆ t ) , h v ( v )) to generate the final prediction ˆ y . This design ensures efficient unimodal inference while benefiting from the rich semantics learned from text during training (Detailed algorithm in the Suppl. Material).

Figure 2. Illustration of our CLIP-IT method: a) Image-Text Modality Pairing: Each histology image is paired with the most semantically similar text report from an external unpaired dataset using a pretrained CLIP-based model, b) CLIP-IT Multimodal Distillation: A joint model is trained using both vision and text encoders with a logit fusion mechanism and feature-level distillation. c) Unimodal Inference: only the vision encoder and the learned projection modules are used, enabling a lightweight and unimodal prediction pipeline.

<!-- image -->

## 4. Results and Discussion

### 4.1. Experimental Methodology

Methods were evaluated using three challenging histology image datasets: PCAM [28], BACH [2], and CRC [24]. PCAM includes 327,680 breast lymph node patches ( 96 × 96 at 10 × magnification, 0 . 97 , µm/px ), labeled as tumor or normal. BACH contains 400 breast tissue patches ( 2048 × 1536 at 20 × , 0 . 42 , µm/px ) labeled as normal, benign, in situ, or invasive carcinoma. CRC provides 107,180 colorec- tal tissue patches ( 224 × 224 at 20 × , 0 . 50 , µm/px ) across 9 tissue types, including stroma and lymphocytes. For external text pairing, we use pathology reports from the TCGA dataset [6], due to its wide tissue and cancer-type coverage and public accessibility. We filter TCGA reports by organ terms (e.g., 'breast', 'colorectal') to restrict domain overlap. For the modality pairing step, we use the CONCH model [20]. While CONCH was pretrained on paired histopathology data, we reuse it here as a one-time resource to retrieve semantically relevant reports for unpaired downstream datasets. Its domain-specific training and contrastive objectives empirically yield reliable pairings without additional manual annotations in the downstream datasets. For the text model, the text encoder of CONCH is used, and for the vision model, the best backbones introduced in [9] were used, i.e., the self-supervised pretrained DINO-L/14 and the supervised vanilla Vision Transformers (ViT-B/16, ViT-B/8, ViT-S/16, ViT-S/8), along with UNI [8]. The average accuracy is reported across three different vision backbone runs from [9] passed through our setting. Details of the models, datasets, evaluation metrics, used hardware, and hyperparameters are in the Supplementary Material.

### 4.2. Comparison with State-of-the-Art Methods

Table 1 presents the average classification accuracy across several state-of-the-art vision backbones, trained either as a unimodal baseline, or with the proposed CLIP-IT method. Evaluation is performed on 3 histology datasets: PCAM, BACH and CRC. CLIP-IT improves the unimodal baselines in most settings and maintains performance in a few other settings. For example, on PCAM, CLIP-IT yields gains as high as +4 . 4% for ViT-B/8. On BACH, performance improvements are most notable for models like UNI and ViT-S/16, with gains up to +2 . 9% . The variance in BACH stems from the base vision model's instability on this small dataset. Our method consistently improves or matches performance despite this variance, showing robustness to backbone fluctuations. Although CRC has strong unimodal baselines (e.g., ViT-B/16 with 95 . 9% ), CLIP-IT still offers modest improvements or preserves parity in most cases. No unimodal backbone experiences significant performance degradation when enhanced with CLIP-IT . Results have a combined p-value of 2 . 65 × 10 -5 , indicating a highly significant overall effect.

Table 2 compares CLIP-IT with multimodal baselines such as CONCH and QUILTNet, both of which rely on paired image-text data and dual-modality inference. For a controlled evaluation, we isolate the vision encoder from each model and assess three variants: (i) a standalone classification head trained on image data only, (ii) a contrastively fine-tuned prompt-based multimodal model, and (iii) the same vision encoder enhanced by CLIP-IT . Details of the setting, including the used prompts, are in the Supplementary Material. Despite using only unpaired data and supporting unimodal inference, CLIP-IT surpasses contrastive multimodal approaches in most configurations, despite using unpaired text during training and unimodal inference. For instance, on BACH, CLIP-IT outperforms the full contrastive version of CONCH by a large margin ( 85 . 05% vs. 60 . 78% ) and shows better performance than QUILTNet and CONCH in both PCAM and BACH. These results illustrate that unpaired textual supervision, when leveraged with CLIP-IT , can be effective.

Interestingly, the performance gains vary by dataset. CRC, which has fewer relevant reports (only 376 colon reports vs. over 1000 breast reports), exhibits smaller improvements. Cosine similarity histograms between images and their retrieved reports are in the Supplementary Material, further supporting this observation. This highlights one limitation of our approach: performance is sensitive to the relevance and richness of the external textual data, even when unpaired. Overall, these results show that CLIP-IT is robust across datasets and architectures, and it enables efficient integration of unpaired textual supervision without increasing inference-time complexity, given semantically rich and clinically meaningful text.

### 4.3. Performance vs. Efficiency Trade-Off

To understand the trade-off between model complexity and accuracy, we analyze the parameter size versus performance across all models and configurations. Figure 3 presents Pareto frontier plots for PCAM, BACH, and CRC, comparing the three setting: ● ) the vision encoder enhanced with CLIP-IT , ✚ ) the same encoder with a standalone classification head trained on image data, and ✖ ) a contrastively fine-tuned multimodal model. Across datasets, CLIP-IT models lie on or near the Pareto frontier, indicating that it achieves the best trade-off between model size and classification accuracy compared to other models of similar complexity. In particular, CLIP-IT outperforms larger unimodal baselines and approaches and mainly surpasses the performance of heavier multimodal models, all while maintaining a significantly smaller parameter size.

### 4.4. Complementarity of Text Supervision

CLIP-IT results were further analyzed by inspecting the source of performance gain in Table 1. To this end, the following Ω measure is considered to capture the impact of text modality in terms of classification accuracy, defined as:

̸

where Y V = { y v i } N i =1 , Y T = { y t i } N i =1 , with y i , y v i , and y t i are the i th true label, prediction of the vision model, and that of the text model, while ✶ {·} is the indicator function, which is equal to one if the condition inside is true, and zero otherwise. This measure captures the complementary, class-discriminative signals that the text modality contributes. It counts the number of samples the text model can correctly classify, while the vision model fails. Figure 4 shows the value of Ω for the different datasets and backbones. We can see that for all the models, there is a notable number of cases where the text modality can provide the correct class to the vision model. However, we observe a performance gap across backbones and datasets, with CLIP-IT providing the most benefit on PCAM. This dataset contains a large number of training samples and exhibits high intra-class variability, which increases the difficulty of distinguishing between certain classes using visual features alone. In such cases, visual features alone may be ambiguous, and the external text reports provide complementary clinical cues that help disambiguate similar classes.

<!-- formula-not-decoded -->

Table 1. Classification accuracy ( ± std) averaged over three runs for unimodal vision backbones and their CLIP-IT -enhanced counterparts across PCAM, BACH, and CRC datasets. Backbone naming follows [9] (DINO: self-supervised ViT-L/14, and ViT-B/S: supervised ViT with patch sizes 16 or 8). The ∆ columns indicate the relative accuracy gain of CLIP-IT over the unimodal baseline.

| Unimodal Backbone   | PCAM             | PCAM             | PCAM    | BACH             | BACH             | BACH    | CRC              | CRC              | CRC     |
|---------------------|------------------|------------------|---------|------------------|------------------|---------|------------------|------------------|---------|
|                     | Unimodal         | CLIP-IT          | ∆       | Unimodal         | CLIP-IT          | ∆       | Unimodal         | CLIP-IT          | ∆       |
| UNI [8]             | 94 . 24 ± 0 . 14 | 95 . 49 ± 0 . 27 | + 1 . 3 | 78 . 89 ± 1 . 56 | 81 . 79 ± 1 . 98 | + 2 . 9 | 94 . 66 ± 0 . 41 | 95 . 92 ± 0 . 07 | + 1 . 3 |
| DINO [9]            | 88 . 88 ± 0 . 75 | 92 . 32 ± 0 . 84 | + 3 . 4 | 84 . 26 ± 2 . 30 | 86 . 11 ± 3 . 21 | + 1 . 8 | 94 . 40 ± 0 . 40 | 95 . 91 ± 0 . 06 | + 1 . 6 |
| VITB-16 [9]         | 88 . 13 ± 1 . 09 | 91 . 42 ± 1 . 28 | + 3 . 3 | 80 . 78 ± 2 . 14 | 82 . 94 ± 4 . 52 | + 2 . 1 | 95 . 86 ± 0 . 25 | 95 . 67 ± 0 . 18 | - 0 . 2 |
| VITS-16 [9]         | 88 . 43 ± 0 . 26 | 90 . 93 ± 1 . 12 | + 2 . 5 | 82 . 90 ± 5 . 56 | 84 . 64 ± 6 . 68 | + 1 . 7 | 93 . 77 ± 0 . 29 | 95 . 34 ± 0 . 20 | + 1 . 7 |
| VITB-8 [9]          | 87 . 54 ± 0 . 71 | 91 . 92 ± 0 . 87 | + 4 . 4 | 86 . 90 ± 2 . 32 | 87 . 06 ± 1 . 22 | + 0 . 2 | 95 . 71 ± 0 . 11 | 95 . 66 ± 0 . 53 | - 0 . 1 |
| VITS-8 [9]          | 87 . 90 ± 0 . 61 | 90 . 24 ± 0 . 90 | + 2 . 3 | 81 . 01 ± 3 . 04 | 82 . 55 ± 1 . 57 | + 1 . 5 | 95 . 03 ± 0 . 13 | 94 . 80 ± 0 . 60 | - 0 . 2 |

Table 2. Comparison of CLIP-IT with other multimodal backbones (CONCH, QUILTNet) and only their vision models.

| Multimodal Backbone   | PCAM             | PCAM             | PCAM             | BACH             | BACH             | BACH             | CRC              | CRC              | CRC              |
|-----------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|
| Multimodal Backbone   | CLIP-IT          | Contrastive      | Vision           | CLIP-IT          | Contrastive      | Vision           | CLIP-IT          | Contrastive      | Vision           |
| CONCH [20]            | 93 . 61 ± 0 . 44 | 92 . 67 ± 1 . 40 | 91 . 75 ± 2 . 57 | 85 . 05 ± 0 . 64 | 60 . 78 ± 0 . 29 | 67 . 25 ± 4 . 34 | 94 . 89 ± 0 . 61 | 95 . 58 ± 0 . 40 | 95 . 12 ± 0 . 47 |
| QUILTNet [15]         | 91 . 83 ± 2 . 37 | 89 . 82 ± 0 . 62 | 90 . 44 ± 0 . 65 | 65 . 50 ± 1 . 84 | 55 . 82 ± 5 . 86 | 63 . 81 ± 2 . 16 | 94 . 83 ± 0 . 94 | 95 . 37 ± 0 . 17 | 94 . 60 ± 0 . 65 |

This is supported by higher Ω values, indicating a stronger contribution from the text modality on PCAM. These results suggest that CLIP-IT is especially beneficial in settings where visual features are ambiguous and textual cues can serve as discriminative signals.

### 4.5. Ablation Studies

To understand each component in CLIP-IT , we conduct a series of ablation studies summarized in Figure 5.

-Impact of LoRA: First, we assess the impact of LoRA fine-tuning by removing it from the training setup. The performance drops from 95.49% to 93.86%. This gap highlights that LoRA is essential for adapting the model to noisy pseudo-pairs without disrupting pretrained representations. Unlike full fine-tuning, which can destabilize large vision and text encoders, LoRA applies low-rank updates to selected layers, allowing efficient adaptation while preserving the robustness of the original pretrained weights.

- -Comparing late vs. early fusion: We compared the performance of our late fusion approach against an early fusion strategy, using a fully connected layer. As shown in Figure 5, early fusion achieves 94.87% accuracy on PCAM with UNI, whereas our late-fusion design, CLIP-IT, reaches 95.49%. This difference results from early fusion being most suitable for aligned modalities [27], while in our setting the modalities are not perfectly aligned.

-Text-to-vision distillation: To assess the impact of having a dual branch, we evaluated a simplified configuration where the textual embedding is distilled directly into the vision embedding, removing the additional text branch (see Figure 5). This setting achieves 94.44% accuracy, slightly higher than the unimodal baseline (94.24%) but still below our dual-branch framework (95.49%). The gap can be explained by the fact that pseudo-pairs introduce noise into the image embeddings, which may confuse the model when text features are injected directly into the vision backbone. By maintaining separate branches, the vision encoder preserves the main discriminative features, while the text branch adds complementary cues when beneficial.

-Impact of architectural modifications: We test whether improvements stem from architecture alone by training with the added modules but without text or distillation (see Figure 5). This setup yields 94.31%, nearly identical to the vision backbone (94.24%) yet well below full CLIP-IT , showing that the gains are driven by textual supervision rather than structural changes.

- -Robustness to input noise: We randomly remove a fraction (from 0 to 50%) of words from each report during training. Up to 30% word dropout, the model maintains high accuracy (e.g., 94.95% at 30%), showing resilience to moderate textual degradation. Beyond this threshold, accuracy declines more noticeably, approaching the unimodal baseline, suggesting that while CLIP-IT can extract value from partial supervision, it still requires a meaningful portion of the text to deliver improvements.

-Impact of pairing quality and irrelevant text: We also study the effect of pairing quality. In particular, we evaluate performance using the 2nd to 5th most similar reports (based on cosine similarity), as well as entirely random pairings. Accuracy gradually declines as we move from topranked to lower-ranked reports, confirming that better semantic alignment between images and text results in better supervision. Notably, when using random text pairings, the performance drops to unimodal (94.34%), showing the

Figure 3. Pareto frontier plots showing the trade-off between model accuracy and parameter size across three histology datasets. Each point style represents a model configuration (Unimodal, CLIP-IT , or Multimodal), with color indicating the architecture. CLIP-IT consistently pushes unimodal models closer to or onto the frontier, offering an efficient alternative to heavier multimodal baselines.

<!-- image -->

Ω

Figure 4. Histogram of Ω scores (Equation 5) across datasets and backbones, showing the % of samples correctly classified by text but missed by vision, i.e., the complementary info of text. Bars denote models, with numeric values (Ω × 100) above each. Higher scores indicate greater potential benefit from textual supervision.

<!-- image -->

importance of semantically relevant matches. These results show that the gains of CLIP-IT stem from informative text and its lightweight distillation design 2 .

### 4.6. Test-Time Computational Cost

We compared CLIP-IT 's efficiency to CONCH and its unimodal vision encoder. The unimodal baseline costs 17 GFLOPs per forward pass, CLIP-IT adds only 0.001 GFLOPs, whereas CONCH costs 505 GFLOPs. On an RTX A6000 (batch=1), latency is 33.3 ms (unimodal), 43.1 ms for CLIP-IT (+29%), and 158.5 ms for CONCH (+376%). Thus, CLIP-IT delivers multimodal gains at near-unimodal compute, supporting real-time deployment.

## 5. Conclusion

We introduced CLIP-IT , a multimodal framework that improves histology image classification, by aligning each image with a semantically relevant external report using a pretrained CLIP-based retrieval model. CLIP-IT forms pseudo-pairs and distills textual knowledge into the vision model, thus manually curated image-text pairs for each downstream dataset are not needed. This enables effective multimodal training and lightweight unimodal inference. Experiments show that CLIP-IT can improve unimodal baselines and often improves fully multimodal models, all with negligible overhead at inference time. In this way, CLIP-IT offers a cost-effective alternative for domains where collecting paired annotations is infeasible.

2 Further analyses (visualizations, generalization, retrieval, text supervision, and distillation) are provided in the Supplementary Material.

Figure 5. Ablation study results showing the classification accuracy of various configurations on UNI and PCAM. The bars represent modifications, including pairing strategies (2nd-5th top), text corruption by k% word removal, early fusion, full fine-tuning, and component removals. The dashed line is the unimodal baseline.

<!-- image -->

Limitations and Future Work: Despite its strong performance, CLIP-IT has smaller gains for datasets with sparse or noisy reports (e.g., CRC). Mainly tested for classification, extending CLIP-IT to tasks like segmentation is an important future direction. Also, using other modalities, such as genomic data, could further enhance multimodal computational pathology.

Acknowledgements This work was supported by the Natural Sciences and Engineering Research Council of Canada, and the Digital Research Alliance of Canada.

## References

- [1] Faseela Abdullakutty, Younes Akbari, Somaya Al-Maadeed, Ahmed Bouridane, Iman M Talaat, and Rifat Hamoudi. Histopathology in focus: a review on explainable multimodal approaches for breast cancer diagnosis. Frontiers in Medicine , 11:1450103, 2024.
- [2] Guilherme Aresta, Teresa Ara´ ujo, Scotty Kwok, Sai Saketh Chennamsetty, Mohammed Safwan, Varghese Alex, Bahram Marami, Marcel Prastawa, Monica Chan, Michael Donovan, et al. Bach: Grand challenge on breast cancer histology images. Medical image analysis , 56:122-139, 2019.
- [3] Cagla Deniz Bahadir, Gozde B. Akar, and Mert R. Sabuncu. Llm-generated rewrite and context modulation for enhanced vision language models in digital pathology. In 2025 IEEE/CVF Winter Conference on Applications of Computer Vision (WACV) , pages 327-336, 2025.
- [4] Tadas Baltruˇ saitis, Chaitanya Ahuja, and Louis-Philippe Morency. Multimodal machine learning: A survey and taxonomy. IEEE Transactions on Pattern Analysis and Machine Intelligence , 41(2):423-443, 2019.
- [5] Shangyan Cai, Weitian Huang, Weiting Yi, Bin Zhang, Yi Liao, Qiu Wang, Hongmin Cai, Luonan Chen, and Weifeng Su. Survival analysis of histopathological image based on a pretrained hypergraph model of spatial transcriptomics data . In MICCAI 2024 . Springer, 2024.
- [6] Cancer Genome Atlas Research Network, J N Weinstein, E A Collisson, G B Mills, K R Shaw, B A Ozenberger, K Ellrott, I Shmulevich, C Sander, and J M Stuart. The cancer genome atlas pan-cancer analysis project. Nat Genet , 45 (10):1113-1120, 2013.
- [7] Pingyi Chen, Honglin Li, Chenglu Zhu, Sunyi Zheng, Zhongyi Shui, and Lin Yang. WsiCaption: Multiple Instance Generation of Pathology Reports for Gigapixel Whole-Slide Images . In MICCAI 2024 . Springer, 2024.
- [8] Richard J. Chen, Tong Ding, Ming Y. Lu, Drew F. K. Williamson, Guillaume Jaume, Andrew H. Song, Bowen Chen, Andrew Zhang, Daniel Shao, Muhammad Shaban, Mane Williams, Lukas Oldenburg, Luca L. Weishaupt, Judy J. Wang, Anurag Vaidya, Long Phi Le, Georg Gerber, Sharifa Sahai, Walt Williams, and Faisal Mahmood. Towards a general-purpose foundation model for computational pathology. Nature Medicine , 30(3):850-862, 2024.
- [9] Ioannis Gatopoulos, Nicolas K¨ anzig, Roman Moser, Sebastian Ot´ alora, et al. eva: Evaluation framework for pathology foundation models. In Medical Imaging with Deep Learning , 2024.
- [10] A. Guichemerre, S. Belharbi, T. Mayet, S. Murtaza, P. Shamsolmoali, L. McCaffrey, and E. Granger. Source-free domain adaptation of weakly-supervised object localization models for histology. In CVPRw , 2024.
- [11] A. Guichemerre, S. Belharbi, M. Shateri, L. McCaffrey, and E. Granger. Pixelcam: Pixel class activation mapping for histology image classification and roi localization. In MIDL , 2025.
- [12] Zhengrui Guo, Jiabo Ma, Yingxue Xu, Yihui Wang, Liansheng Wang, and Hao Chen. HistGen: Histopathology Report Generation via Local-Global Feature Encoding
13. and Cross-modal Context Interaction . In MICCAI 2024 . Springer, 2024.
- [13] Edward J Hu, Yelong Shen, Phillip Wallis, Zeyuan AllenZhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen, et al. Lora: Low-rank adaptation of large language models. ICLR , 1(2):3, 2022.
- [14] Lei Huang, Weijiang Yu, Weitao Ma, Weihong Zhong, Zhangyin Feng, Haotian Wang, Qianglong Chen, Weihua Peng, Xiaocheng Feng, Bing Qin, et al. A survey on hallucination in large language models: Principles, taxonomy, challenges, and open questions. ACM Transactions on Information Systems , 43(2):1-55, 2025.
- [15] Wisdom Oluchi Ikezogwo, Mehmet Saygin Seyfioglu, Fatemeh Ghezloo, Dylan Stefan Chan Geva, Fatwir Sheikh Mohammed, Pavan Kumar Anand, Ranjay Krishna, and Linda Shapiro. Quilt-1m: One million image-text pairs for histopathology. arXiv preprint arXiv:2306.11207 , 2023.
- [16] Kyungwon Kim, Yongmoon Lee, Doohyun Park, Taejoon Eo, Daemyung Youn, Hyesang Lee, and Dosik Hwang. LLM-guided Multi-modal Multiple Instance Learning for 5year Overall Survival Prediction of Lung Cancer . In MICCAI 2024 . Springer, 2024.
- [17] Eelandula Kumaraswamy. Key challenges in the diagnosis of cancer using artificial intelligence methods. In AIP Conference Proceedings . AIP Publishing, 2022.
- [18] Lifan Long, Jiaqi Cui, Pinxian Zeng, Yilun Li, Yuanjun Liu, and Yan Wang. MuGI: Multi-Granularity Interactions of Heterogeneous Biomedical Data for Survival Prediction . In MICCAI 2024 . Springer, 2024.
- [19] Jiaxuan Lu, Fang Yan, Xiaofan Zhang, Yue Gao, and Shaoting Zhang. PathoTune: Adapting Visual Foundation Model to Pathological Specialists . In MICCAI 2024 . Springer, 2024.
- [20] Ming Y Lu, Bowen Chen, Drew FK Williamson, Richard J Chen, Ivy Liang, Tong Ding, Guillaume Jaume, Igor Odintsov, Long Phi Le, Georg Gerber, et al. A visuallanguage foundation model for computational pathology. Nature Medicine , 30:863-874, 2024.
- [21] Gabriel Mejia, Daniela Ruiz, Paula C´ ardenas, Leonardo Manrique, Daniela Vega, and Pablo Arbel´ aez. Enhancing Gene Expression Prediction from Histology Images with Spatial Transcriptomics Completion . In MICCAI 2024 . Springer, 2024.
- [22] Anh Tien Nguyen, Trinh Thi Le Vuong, and Jin Tae Kwak. Towards a text-based quantitative and explainable histopathology image analysis . In MICCAI 2024 . Springer, 2024.
- [23] Hyun-Jic Oh and Won-Ki Jeong. Controllable and efficient multi-class pathology nuclei data augmentation using textconditioned diffusion models. In MICCAI , pages 36-46. Springer, 2024.
- [24] Sara P. Oliveira, Pedro C. Neto, Jo˜ ao Fraga, Diana Montezuma, Ana Monteiro, Jo˜ ao Monteiro, Liliana Ribeiro, Sofia Gonc ¸alves, Isabel M. Pinto, and Jaime S. Cardoso. Cad systems for colorectal cancer from wsi are still not ready for clinical acceptance. Scientific Reports , 11(1), 2021.

- [25] Linhao Qu, Dan Huang, Shaoting Zhang, and Xiaosong Wang. Multi-modal data binding for survival analysis modeling with incomplete data and annotations. In MICCAI , pages 501-510. Springer, 2024.
- [26] Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, et al. Learning transferable visual models from natural language supervision. In ICML . PmLR, 2021.
- [27] Dhanesh Ramachandram and Graham W Taylor. Deep multimodal learning: A survey on recent advances and trends. IEEE signal processing magazine , 34(6):96-108, 2017.
- [28] Bastiaan S Veeling, Jasper Linmans, Jim Winkens, Taco Cohen, and Max Welling. Rotation equivariant CNNs for digital pathology. arXiv preprint , 2018.
- [29] Bastiaan S Veeling, Jasper Linmans, Jim Winkens, Taco Cohen, and Max Welling. Rotation equivariant cnns for digital pathology. In MICCAI , pages 210-218. Springer, 2018.
- [30] Hasindri Watawana, Kanchana Ranasinghe, Tariq Mahmood, Muzammal Naseer, Salman Khan, and Fahad Shahbaz Khan. Hierarchical Text-to-Vision Self Supervised Alignment for Improved Histopathology Representation Learning . In MICCAI 2024 . Springer, 2024.
- [31] Conghao Xiong, Hao Chen, Hao Zheng, Dong Wei, Yefeng Zheng, Joseph J. Y. Sung, and Irwin King. MoME: Mixture of Multimodal Experts for Cancer Survival Prediction . In MICCAI 2024 . Springer, 2024.
- [32] Yan Yang, Md Zakir Hossain, Xuesong Li, Shafin Rahman, and Eric Stone. Spatial transcriptomics analysis of zeroshot gene expression prediction. In MICCAI , pages 492-502. Springer, 2024.
- [33] Jiajin Zhang, Ge Wang, Mannudeep K. Kalra, and Pingkun Yan. Disease-informed adaptation of vision-language models. IEEE Transactions on Medical Imaging , pages 1-1, 2024.
- [34] Ling Zhang, Boxiang Yun, Xingran Xie, Qingli Li, Xinxing Li, and Yan Wang. Prompting whole slide image based genetic biomarker prediction. In MICCAI , pages 407-417. Springer, 2024.
- [35] Yuan Zhang, Yaolei Qi, Xiaoming Qi, Yongyue Wei, and Guanyu Yang. DSCENet: Dynamic Screening and ClinicalEnhanced Multimodal Fusion for MPNs Subtype Classification . In MICCAI 2024 . Springer, 2024.
- [36] Yupei Zhang, Xiaofei Wang, Fangliangzi Meng, Jin Tang, and Chao Li. Knowledge-driven Subspace Fusion and Gradient Coordination for Multi-modal Learning . In MICCAI 2024 . Springer, 2024.
- [37] Qifeng Zhou, Wenliang Zhong, Yuzhi Guo, Michael Xiao, Hehuan Ma, and Junzhou Huang. PathM3: A Multimodal Multi-Task Multiple Instance Learning Framework for Whole Slide Image Classification and Captioning . In MICCAI 2024 . Springer, 2024.