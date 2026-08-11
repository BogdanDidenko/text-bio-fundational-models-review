### nature biomedical engineering

Article

## XunZi, an AI biologist, reveals disease-modifying targets

Received: 11 January 2026

Accepted: 8 July 2026

Published online: xx xx xxxx

<!-- image -->

Check for updates Xinhe Huang 1,6 , Junhong Qin 2,6 , Fei Tang 3,6 , Chenyu Yang 1 , Linhua Xu 2 , Junfen Wei 3 , Dan Liu 1 , Kang Chen 3 , Chi Zhang 1 , Miaomiao Chen 1 , Yujie Gou 1 , Jiayi Zhang 1 , Yongze Ma 1 , Lin Zhao 2 , Yingfeng Tu 2 , Peng Lei 3 , Yu Xue 1,4,5 &amp; Da Jia 2

Hypothesis generation in biomedicine is constrained by human cognitive limitations in synthesizing insights from fragmented biomedical knowledge and multimodal data sources. Here we introduce XunZi, an AI biologist that integrates logical reasoning and multimodal data fusion to autonomously generate de novo therapeutic target hypotheses with testable mechanisms. XunZi has been trained on 24.4 million publications and 613.6 TB of multisource data spanning 21,008 human genes and 5,850 diseases, and outperforms existing methods in both accuracy and interpretability across diverse disease contexts. In Parkinson's disease (PD), where complex mechanisms and limited targets hamper therapy development, XunZi identifies aberrant activation of CHK2 and IRAK4 kinases across multiple models. Pharmacological or genetic inhibition of Chk2 rescues dopaminergic neuron loss and motor deficits in PD mice. We further demonstrate XunZi's broad versatility in diseases such as non-small-cell lung cancer. XunZi establishes a paradigm-shifting framework to translate fragmented biomedical knowledge and data into actionable therapeutics.

The formulation of de novo, well-grounded hypotheses is essential for biomedical research, ranging from deciphering underlying mechanisms of human diseases to discovering therapeutic targets to informing therapeutic interventions 1 . These hypotheses are traditionally formed through cognitive processes of biologists, who propose testable research directions on the basis of logical reasoning from biomedical knowledge and integrating insights from empirical data 1-4 . Currently, tens of millions of open-access biomedical publications have become available, alongside a huge volume of public multimodal datasets associated with diverse diseases 5-13 . Due to cognitive constraints of human biologists, it has been a daunting challenge to synthesize insights from these heterogeneous sources.

In recent years, the advent of advanced artificial intelligence (AI) technologies, particularly large language models (LLMs) and multimodal foundation models (MFMs), offers transformative potential for accelerating scientific innovations 14-17 . LLM-based reasoning agents have been proposed as tools for analysing large datasets, comprehending open-access literature, producing creative hypotheses and ultimately empowering de novo biomedical discovery. As a proof-of-concept, Google developed the AI co-scientist, a multi-agent

1 Key Laboratory of Molecular Biophysics of Ministry of Education, Hubei Bioinformatics and Molecular Imaging Key Laboratory, Center for Artificial Intelligence Biology, College of Life Science and Technology, Huazhong University of Science and Technology, Wuhan, Hubei, China. 2 Key Laboratory of Birth Defects and Related Diseases of Women and Children, Department of Pediatrics, West China Second University Hospital, State Key Laboratory of Biotherapy, Sichuan University, Chengdu, China. 3 Department of Neurology and State Key Laboratory of Biotherapy, National Clinical Research Center for Geriatrics, West China Hospital, Sichuan University, Chengdu, China.  4 Hubei Hongshan Laboratory, Wuhan, China. 5 College of Informatics, Huazhong Agricultural University, Wuhan, China. 6 These authors contributed equally: Xinhe Huang, Junhong Qin, Fei Tang.

e-mail: peng.lei@scu.edu.cn; xueyu@hust.edu.cn; Jiada@scu.edu.cn

[https://doi.org/10.1038/s41551-026-01769-6](https://doi.org/10.1038/s41551-026-01769-6)

system capable of processing text to generate research proposals from open-access publications 18,19 . However, LLMs frequently generate 'AI hallucinations' 20,21 , such as false or fictional content, while lacking the ability to integrate insights from multimodal empirical data. On the contrary, general-purpose MFMs, such as Contrastive Language-Image Pretraining (CLIP) 22 and OpenAI Sora 23 , demonstrate strong capabilities for multimodal data fusion, but show limitations in interpretability due to lack of transparent logical reasoning. These constraints undermine the utility of LLMs and MFMs in hypothesis derivation. It remains unclear whether the integration of logical reasoning with multimodal data fusion could mitigate hallucinations while enhancing interpretability. It is also unknown to what extent such a unified AI system could facilitate de novo hypothesis generation.

In this study, we develop XunZi, an AI biologist inspired by the hybrid architecture of human brain, which can efficiently integrate logical reasoning from the left hemisphere with holistic thinking from the right hemisphere 24,25 . Analogously, XunZi comprises two modules: (1) an LLM-based reasoning module, XunZi-R, and (2) a graph convolutional network (GCN)-based multimodal data fusion module, XunZi-M. XunZi synergizes the output of the two modules and enables de novo hypothesis generation together with testable mechanistic interpretations for understanding the involvement of disease-modifying targets, as well as development of targeting therapeutics. To capture contextual relations between 21,008 human genes and 5,850 disease entities, XunZi has been trained on multisource knowledge and data, including 24 million biomedical publications, 2 million structured biological corpora, 336,108 chain-of-thought (CoT) 26 mechanistic interpretations, 613.2 TB of multi-omics data, 2.8 million protein-protein interactions (PPIs) and over 47,000 biological process annotations. Compared with other methods, including the leading LLM GPT-4o, deep neural networks (DNNs) and support vector machines (SVMs), XunZi outperforms in both accuracy and interpretability to formulate and substantiate de novo hypotheses under various disease contexts. We next evaluated the predictive power of XunZi in multiple contexts, encompassing pathologically distinct non-small-cell lung cancer (NSCLC) and Parkinson's disease (PD). We identified two protein kinases (PKs), Chk2 and Irak4, as potential therapeutic targets for PD. Pharmacological inhibition or genetic ablation of Chk2 markedly attenuated motor deficits and prevented dopaminergic neurodegeneration in PD mice. Taken together, we establish an AI biologist that integrates logical reasoning with multimodal data fusion, and demonstrate its paradigm-shifting potential to drive innovation in biomedical research.

### Results

#### Construction of XunZi to predict disease-modifying targets with mechanistic interpretations

To generate innovative and testable hypotheses, fragmented biomedical knowledge in open-access literature needs to be unbiasedly integrated with the insights derived from multimodal empirical data 15,16 . Currently, neither LLM-based reasoning agents nor general-purpose MFMs are able to synthesize these complementary knowledge sources 17 . To overcome these limitations, we develop XunZi, an AI biologist grounded in human-like cognitive processes 24,25 (Fig. 1a). As an AI biologist, XunZi integrates the two biomimetic modules, XunZi-M and XunZi-R, to assign unified confidence scores to individual genes

####### Fig. 1 | Construction of XunZi, an AI biologist integrating logical reasoning

with multimodal data fusion. a , Schematic of XunZi's integrative architecture. XunZi combines a logical reasoning module (XunZi-R) with a multimodal data fusion module (XunZi-M) to prioritize candidate disease regulators and provide mechanistic insights. b , The top 6 disease categories with the largest number of curated gene-disease associations among 26 MeSH disease classes. c , Confusion matrices comparing reasoning accuracy between XunZi-R and GPT-4o in fivefold cross-validation on gene-disease functional relevance inference. d , Radar plots showing reasoning performance of XunZi-R and GPT-4o for the neoplasms within specific disease contexts. Moreover, XunZi provides testable mechanistic interpretations for each association.

To enable XunZi-R to perform biologist-like logical reasoning, we first selected a leading 7.3-B-parameter LLM, Mistral 7B 27 , as the initial model. Then, continual pretraining was performed using 24,411,924 curated biomedical publications and 2,054,130 structured biological corpus data, such as gene functional descriptions, Disease Ontology (DO) definitions 11 and Gene Ontology (GO) definitions 28 (Supplementary Table 1a-d). The procedure enables XunZi to internalize core biological concepts and domain knowledge. To further enable the model to imitate reasoning patterns of human biologists and acquire domain-specific inference capabilities, we constructed a CoT instruction-based corpus containing 336,108 high-quality mechanistic interpretation entries (Supplementary Table 2a,b). These entries were generated using structured prompts with GPT-4 to transform raw gene-disease associations from databases, including DisGeNET 10 and the Comparative Toxicogenomics Database (CTD) 13 , into detailed mechanistic interpretations based on literature evidence. To ensure data quality, we manually checked each entry and corrected errors if necessary. The errors included unfounded fabrication, factual inaccuracies, logical inconsistencies introduced and incomplete summary 29 (Extended Data Fig. 1). The corpus covers all 26 major Medical Subject Headings (MeSH) disease categories 30 , including widely occurring diseases such as neoplasms, congenital abnormalities and nervous system diseases (Fig. 1b), as well as a broad range of rare disorders (Extended Data Fig. 2).

We then fine-tuned XunZi-R on this curated mechanistic interpretations corpus. To test the performance of this procedure, we used the DisGeNET dataset for XunZi-R fine-tuning, evaluated the model by fivefold cross-validation as well as on a non-overlapping dataset from CTD and vice versa. By comparison, XunZi-R achieved superior performance versus state-of-the-art LLMs 31,32 , including GPT-4o, GPT-5, GPT-4, o3, DeepSeek-V3, DeepSeek-R1, BioGPT and the Claude Sonnet series, indicating robust reasoning capabilities despite having far fewer parameters (7.3 B vs up to 1,750 B) (Fig. 1c, Extended Data Fig. 3a-c and Supplementary Table 3a-d). We further evaluated XunZi-R across all 26 MeSH disease categories. Compared with GPT-4o, XunZi-R achieved higher reasoning accuracy with much fewer parameters after domain-specific optimization, while accurately capturing known functional gene-disease associations (Fig. 1d). It consistently produced biologically meaningful inferences across diverse disease types, maintaining robust performance even in rare conditions with limited previous knowledge (Extended Data Fig. 4a-x).

To further assess the mechanistic reasoning abilities of XunZi-R, we evaluated its generated interpretations against curated mechanistic descriptions using three standard natural language processing (NLP) metrics, including BERTScore, Bilingual Evaluation Understudy (BLEU) and Recall-Oriented Understudy for Gisting Evaluation (ROUGE) 33,34 . Through fivefold cross-validation and the reciprocal test mentioned above, XunZi-R achieved higher performance values than other LLMs, indicating a strong semantic alignment with known mechanistic knowledge (Extended Data Fig. 5a-h).

Implemented in GCNs 35 , XunZi-M integrates three different types of dataset, including 2,813,799 PPIs, 47,922 GO terms of biological processes and 613.2 TB of publicly available multi-omics datasets,

and nervous system disease categories. Outer green bars represent the recall (true positive rate) of XunZi-R in assessing gene functional relevance across subtypes within each disease category. e , Summary of sample sizes and data volumes for pan-cancer and neurodegenerative disease multi-omics datasets used by XunZi-M. f , g , Receiver operating characteristic (ROC) curves and AUC values from fivefold cross-validation of XunZi, its individual modules and other methods, illustrating model performance in identifying disease-relevant regulators in pan-cancer ( f ) and neurodegenerative disease ( g ) tasks.

a

<!-- image -->

diseases Fig. 2 | XunZi demonstrates superior accuracy in identifying functional regulators of NSCLC and PD. a , ROC curves and AUC values from fivefold crossvalidation showing performance of XunZi and baseline methods in identifying disease-relevant regulators in NSCLC. b , t -SNE visualization of gene-level prediction outcomes in NSCLC. Orange dots represent reported regulators, red dots indicate candidate genes predicted by XunZi, and grey dots denote all other genes. c , A549 cells were transfected with control or a mixture of two siRNAs targeting indicated genes, and cell viability was assessed using the MTT assay after 48 h. d , Reasoning output by XunZi-R for MYO1B in lung cancer, including inferred mechanism, impacted genes and pathways. e -h , A549 cells were transfected with control or siRNA targeting MYO1B. After 48 h, the cells were lysed for immunoblotting to detect the levels of indicated proteins ( e ). MYO1B ( f ), p-Erk/Erk ( g ) and p-AKT/AKT ( h ) levels were quantified by densitometry using ImageJ software. i , Experimental scheme for MPTP-injected mouse model of PD. i.p., intraperitoneal injections. j , Experimental scheme for PFF-injected mouse model of PD. k , ROC curves and AUC values from fivefold cross-validation such as transcriptomes, proteomes and phosphoproteomes (Fig. 1e and Supplementary Table 4). This module predicts potential regulators within specific disease contexts, by learning complementary contextual information from multimodal data (Extended Data Fig. 6). By integrating XunZi-M and XunZi-R, XunZi prioritizes candidate disease-modifying targets with mechanistic interpretations, enabling de novo, well-grounded hypothesis generation for further consideration. To test the performance of XunZi, we performed fivefold cross-validation and the reciprocal test mentioned above for cancer and neurodegenerative disease models, by calculating area under the curve (AUC) and area under the precision-recall curve (AUPRC) values, respectively. The results demonstrated that XunZi significantly outperformed both its individual components (XunZi-M and XunZi-R) and multiple established methods (Fig. 1f,g and Extended Data Fig. 7a-l). Furthermore, XunZi exhibited broad extensibility across diverse disease contexts (Extended Data Figs. 8-10).

<!-- image -->

#### XunZi outperforms existing methods in predicting regulators underlying NSCLC and PD

To evaluate the utility of XunZi, we selected two complex diseases: NSCLC and PD. Novel therapeutic targets are urgently required for both diseases due to their substantially unmet clinical needs 36-39 . High-quality multi-omics datasets of the two diseases are available from public databases and/or published literature. Focusing on NSCLC, we integrated the gene-level representations derived from the pretrained pan-cancer model of XunZi-M with NSCLC-specific multi-omics datasets, to fine-tune a model for the prediction of NSCLC-specific regulators. Using fivefold cross-validation, XunZi achieved a higher AUC value of 0.86, compared with AUC values of 0.65, 0.72 and 0.70 for GPT-4o, DNNs and SVMs (Fig. 2a). XunZi also achieved a higher AUPRC value than other methods (Supplementary Fig. 1a) and showed superior performance in the reciprocal test (Supplementary Fig. 1b-f). The t -distributed

Fig. 3 | Experimental validation of Chk2 as a pathogenic mediator in PD following XunZi's identification. a , XunZi predicts CHK2's mechanistic role in PD, including associated pathways, regulated genes and disease mechanisms. GPT-4o fails to generate these insights. b , Immunoblot analysis of p-Irak4, total Irak4, p-Chk2, total Chk2 and Stk33 protein levels in the SN of mice. Animals were treated with saline (control) or MPTP as depicted in i . n = 3 per group, all males. c , Quantification of p-Chk2/Chk2 levels in the SN of mice shown in b . n = 3 per group, all males. d , Immunoblot analysis of p-Irak4, total Irak4, p-Chk2, total Chk2 and Stk33 protein levels in the SN of mice. Animals were injected with PBS or α-syn PFFs as depicted in Fig. 2j. n = 3 per group, all males. e , Quantification of p-Chk2/Chk2 levels in the SN of mice shown in d . n = 3 per group, all males. f , Experimental scheme for data shown in g -m . Stereotaxic AAV injection (day 1), MPTP administration (day 28), behavioural studies (days 46-48) and tissue collection for immunoblotting/IHC (day 49). g , Pole test performance. The turning time of mice at the top of the wooden pole was showing performance of XunZi and baseline methods in identifying diseaserelevant regulators in PD. l , Uniform manifold approximation and projection visualization of gene embeddings generated by XunZi in PD. Orange dots represent reported regulators, green dots indicate candidate genes predicted by XunZi, and grey dots denote all other genes. Kinases are highlighted with diamond shapes. m , ROC curves and AUC values from fivefold cross-validation showing the performance of XunZi and baseline methods in identifying diseaserelevant kinases in PD. n , t -SNE visualization of kinase-level prediction outcomes in PD. Orange dots represent reported functional kinases, red dots indicate kinase candidates predicted by XunZi, and grey dots denote other kinases. o , N2a cells were transfected with control or a mixture of two siRNAs targeting indicated kinase genes. At 24 h after transfection, cells were treated with 2 mM MPP + for 24 h; then cell viability was assessed using the MTT assay. Experiments were performed in triplicate ( c , e -h , o ). Statistical data are presented as mean ± s.e.m, with P values calculated using unpaired two-tailed t -test ( c , o ) or one-way ANOVA, followed by Dunnett's test ( f -h ).

stochastic neighbour embedding ( t -SNE) analysis of the learned gene representations revealed that known NSCLC regulators were closely clustered together, showing distinct characteristics compared to other genes (Fig. 2b). Both GPT-4o and XunZi correctly identified the causal association between NSCLC and epidermal growth factor receptor (EGFR), a well-established lung cancer gene (Supplementary Fig. 2a). To test whether XunZi can predict previously unrecognized regulators of NSCLC, we selected 20 unreported genes with top scores for further functional screening (Supplementary Table 5). In commonly used NSCLC A549 cells, RNA interference-mediated knockdown experiments identified 5 potential regulators, including MYO1B, NAA30, BRCC3, GFPT1 and PGAM5, whose depletion markedly decreased cell viability (Fig. 2c). Interestingly, XunZi, but not GPT-4o, identified the association between MYO1B and lung cancer, which was not reported previously (Fig. 2d and Supplementary Fig. 2b). XunZi further proposed that MYO1B might influence lung cancer progression by regulating downstream signalling pathways, such as PI3K/AKT and MAPK/ERK (Fig. 2d). Subsequent experiments demonstrated that knockdown of MYO1B in A549 cells led to decreased phosphorylation of both AKT and ERK, validating the mechanisms proposed by XunZi (Fig. 2e-h).

To evaluate the robustness and disease-context specificity of XunZi predictions, we extended functional validation of the same 20 XunZi-prioritized candidates (Supplementary Table 5) to additional cancer cell lines. In a related NSCLC cell line (NCI-H520), knockdown of two additional genes resulted in a marked reduction in cell viability (Supplementary Fig. 3a). Notably, only one of these genes affected viability in a biologically distinct lung cancer lineage, small-cell lung cancer (SCLC; SW1271), and none showed a significant effect in a liver cancer model (HepG2) (Supplementary Fig. 3b,c). To compare XunZi with the conventional expression-based prioritization strategy, we selected 20 differentially expressed but previously uncharacterized genes from the Gene Expression Profiling Interactive Analysis

recorded. Groups: AAV-control + saline ( n = 9), AAV-control + MPTP ( n = 8) and AAVChk2 KD + MPTP ( n = 5). All male mice. h , Rotarod test performance. Mice were placed on the rotating cylinder and the time at which the mice dropped was recorded. Maximum time was set to 360 s. Groups: AAV-control + saline ( n = 9), AAV-control + MPTP ( n = 9) and AAVChk2 KD + MPTP ( n = 5). All male mice. i , Immunoblot analysis of p-Chk2, total Chk2 and TH levels in the SN of mice. Groups: AAV-control + saline ( n = 3), AAV-control + MPTP ( n = 3) and AAVChk2 KD + MPTP ( n = 3). All male mice. j , k , Quantification of p-Chk2/Chk2 ( j ) and TH ( k ) levels shown in i . The levels were quantified by densitometry using ImageJ software. n = 3 per group, all males. l , m , Representative images ( l top), magnified images ( l bottom) and quantification ( m ) of TH-positive neurons in the SN in each group using immunohistochemistry staining. Scale bars, 200 μm ( l top), 600 μm ( l bottom). n = 3 per group. Statistical data are presented as mean ± s.e.m. P values were determined using unpaired two-tailed t -test ( c , e ) or one-way ANOVA followed by Dunnett's test ( g -k , m ).

a

<!-- image -->

(GEPIA) 33 and subjected them to the same viability assay in A549 cells. Within this set, only a single gene significantly reduced cell viability (Supplementary Fig. 3d). Collectively, these results demonstrate that XunZi outperforms expression-based approaches in identifying context-specific regulators underlying NSCLC.

Subsequently, we evaluated the utility of XunZi for PD, a neurodegenerative disorder lacking curative therapies. PD is known to involve multiple functional pathways, operating both independently and synergistically 40 . This complexity poses a major obstacle to traditional drug discovery paradigms. Two PD mouse models were established, including one with systemic toxicity of 1-methyl-4-phenyl-1,2 ,3,6-tetrahydropyridine (MPTP) and another with the inoculation of α-synuclein (α-syn) preformed fibrils (PFFs) (Fig. 2i,j). Motor deficits were confirmed by the pole test and rotarod test (Supplementary Fig. 4). We first performed transcriptomic, proteomic and phosphoproteomic profiling of the substantia nigra (SN) and cerebellum in PD and control mice. The SN is the primary site of dopaminergic neuronal loss in PD, whereas the cerebellum remains relatively spared by PD pathology and is employed as a control region. The multi-omics datasets were processed and subjected to conventional differential expression and enrichment analyses, and results were subsequently compared to those generated by XunZi (Supplementary Fig. 5a-d and Supplementary Table 6a-f). Leveraging gene-level representations from a pretrained neurodegenerative disease model that was integrated with PD-specific multi-omics data, XunZi demonstrated superior discriminative capacity for PD-associated genes, achieving higher performance than other methods in both fivefold cross-validation and the reciprocal test (Fig. 2k and Supplementary Fig. 6a-f). Whereas conventional statistical analyses identified biological processes (for example, transcriptional regulation, intracellular transport) distantly related to PD pathogenesis (Supplementary Fig. 5a,c), XunZi revealed core pathological mechanisms, including mitochondrial dysfunction, kinase dysregulation and α-syn aggregation (Supplementary Fig. 5b,d).

Notably,  the  top-scored  hits  from  XunZi  included  two well-characterized PD-associated PKs (LRRK2 and PINK1) 41 and several of their phosphorylation substrates (Fig. 2l). Since aberrant phosphorylation manifests as an important cause of PD, we next focused on the involvement of PKs in PD. We therefore refined our PD model to predict PD-associated PKs. XunZi achieved substantially higher accuracy (AUC = 0.92) than existing methods, including GPT-4o (AUC = 0.52), DNNs (AUC = 0.69) and SVMs (AUC = 0.70) (Fig. 2m). The confusion matrices supported robust concordance between predicted and reported PD-associated PKs under different thresholds (Supplementary Fig. 6g). t -SNE visualization further showed clustering of XunZi-prioritized kinases with known PD-associated kinases

### Fig. 4 | Pharmacological inhibition of Chk2 alleviates PD phenotypes in

mouse models. a , Pole test performance. The turning time of mice at the top of the wooden pole was recorded. Groups: sham ( n = 10), sham + 2 μg CCT ( n = 9), MPTP ( n = 12), MPTP + DNL-201 ( n = 7), MPTP + 0.2 μg CCT ( n = 14) and MPTP + 2 μg CCT ( n = 10). All male mice. b , Rotarod test performance. Mice were placed on the rotating cylinder and the time at which the mice dropped was recorded. Maximum time was set to 360 s. Groups: sham ( n = 11), sham + 2 μg CCT ( n = 12), MPTP ( n = 13), MPTP + DNL-201 ( n = 8), MPTP + 0.2 μg CCT ( n = 12) and MPTP + 2 μg CCT ( n = 12). All male mice. NS, not significant. c , Immunoblot analysis of indicated protein levels in the SN of mice. Groups: sham ( n = 3), MPTP ( n = 3), MPTP + 0.2 μg CCT ( n = 3) and MPTP + 2 μg CCT ( n = 3). All male mice. d , Quantification of p-Chk2/Chk2 levels shown in c . The levels were quantified by densitometry using ImageJ software. n = 3 per group, all males. e , Quantification of p-Lrrk2/Lrrk2 levels shown in c . The levels were quantified by densitometry using ImageJ software. n = 3 per group, all males. f , g , Representative images ( f top), magnified images ( f bottom) and quantification ( g ) of TH-positive neurons in the SN in each group using immunohistochemistry staining. Scale bars, 200 μm ( f top), 600 μm ( f bottom). n = 3 per group. h , Pole test performance. The turning time of mice at the top of the wooden pole was recorded. Groups: sham ( n = 9),

(Fig. 2n). To identify functionally relevant kinases in PD pathogenesis, we systematically prioritized all protein kinases for their potential involvement in PD by predicting functional relevance and inferring downstream mechanisms using XunZi. On the basis of their prioritization scores and the presence of downstream mechanistic inference by XunZi, we selected the top 20 kinases and examined their contribution in MPP + -induced cell death (Supplementary Table 7). Knockdown of PK genes Chk2 , Irak4 and Stk33 significantly attenuated MPP + -induced cell death in N2a cells, whereas knockdown of kinase genes Dapk2 and Grk5 increased cell death (Fig. 2o and Supplementary Fig. 6h-j). Thus, these PKs may play distinct pathogenic or protective roles in PD (Fig. 2o). Among these candidate PKs, we selected STK33 for further validation in two PD-relevant cell models. Notably, XunZi, rather than general-purpose LLMs such as GPT-5.3 or Claude Opus 4.6, identified STK33 as a putative PD-associated kinase and suggested a potential link to MAPK signalling (Supplementary Fig. 7a-c). In MPP + -treated N2a cells, knockdown of Stk33 partially rescued the reduction in cell viability (Supplementary Fig. 7d), concomitant with decreased levels of cleaved caspase-3 and phosphorylated MAPK1/3 (Supplementary Fig. 7e-h). On the other hand, total MAPK1/MAPK3 level remained largely unchanged (Supplementary Fig. 7e). Similarly, in the A53T α-syn overexpression model, silencing of Stk33 reduced MAPK1/3 phosphorylation and markedly decreased pS129 α-syn levels, with minimal effect on total α-syn (Supplementary Fig. 7i-m). Together, these findings suggest that STK33 contributes to PD-associated cellular phenotypes, potentially through modulation of MAPK signalling and regulation of pathological α-syn phosphorylation, which supported the capacity of XunZi to identify pathophysiologically relevant PKs and their downstream mechanistic pathways.

#### XunZi identifies CHK2 as a potent therapeutic target for PD

Next, we tested whether CHK2, IRAK4 and STK33, which suppress MPP + -induced neurotoxicity in vitro, also have a role in PD pathology in vivo, by using established PD mouse models. Notably, although both XunZi and GPT-4o suggested the potential associations of IRAK4 with PD pathogenesis, only XunZi predicted CHK2 and STK33 (Fig. 3a).

To test the hypothesis generated by XunZi, we performed experimental validations using SN and cerebellum tissues of PD and control mice. In MPTP-intoxicated mice, the levels of phosphorylated Chk2 T68 (p-Chk2), Irak4 and phosphorylated Irak4 T345/S346 (p-Irak4) were significantly elevated in the SN compared to controls. Total protein expression levels of Chk2 and Stk33 remained unchanged in the SN (Fig. 3b,c and Supplementary Fig. 8a-c). No alterations in these targets were observed in the cerebellum (Supplementary Fig. 8d-g). Consistently, injection of α-syn PFFs also resulted in selective upregulation

α-syn PFFs ( n = 9) and α-syn PFFs + 2 μg CCT ( n = 10). All male mice. i , Rotarod test performance. Mice were placed on the rotating cylinder and the time at which the mice dropped was recorded. Maximum time was set to 360 s. Groups: sham ( n = 6), α-syn PFFs ( n = 5) and α-syn PFFs + 2 μg CCT ( n = 5). All male mice. j , Immunoblot analysis of indicated protein levels in the SN of mice. Groups: sham ( n = 4), α-syn PFFs ( n = 4) and α-syn PFFs + 2 μg CCT ( n = 4). All male mice. k , l , Quantification of p-α-syn/α-syn ( k ) and p-Chk2/Chk2 ( l ) levels shown in j . The levels were quantified by densitometry using ImageJ software. n = 4 per group, all males. m , n Representative images ( m top), magnified images ( m bottom) and quantification ( n ) of TH-positive neurons in the SN in each group using immunohistochemistry staining. Scale bars, 200 μm ( m top), 600 μm ( m bottom). n = 3 per group. o , Functional network of reported and XunZi-predicted PD-associated PKs and their associated genes. Hexagons, known (orange) or XunZi-predicted PD-associated PKs (red); green circles, PK-interacting or downstream genes; green lines with arrow, XunZi-predicted associations; blue dashed lines, known PPIs. The network visualization was generated using Cytoscape. Statistical data are presented as mean ± s.e.m. P values were determined using one-way ANOVA followed by Dunnett's test

( a , b , d , e , g -i , k , l , n ).

<!-- image -->

of p-Chk2 and p-Irak4 in the SN, confirming region-specific dysregulation of Chk2 and Irak4 activity in PD pathogenesis (Fig. 3d,e and Supplementary Fig. 8h-n).

Because Chk2 was consistently activated in two independent PD models and prioritized by XunZi, we tested whether reducing Chk2 could be therapeutically beneficial. Adeno-associated virus (AAV) vectors carrying Chk2 -targeting guide RNA (gRNA), AAVChk2 KD, were injected into one side of the SN, reducing Chk2 protein levels by ~50% compared to control AAV (Supplementary Fig. 9a-c). Lower Chk2 levels did not affect normal movement, as no differences in open field test (total distance moved, speed of movement) or rotarod performance were observed (Supplementary Fig. 9d-f).

Four weeks after AAV injection, MPTP was administered to AAV-control or AAVChk2 KD mice (Fig. 3f). MPTP caused severe motor impairment in AAV-control mice, as these mice took longer to turn downward in the pole test (Fig. 3g) and stayed on the rotarod for a shorter time in the rotarod test (Fig. 3h). In contrast, AAVChk2 KD mice showed much milder deficits (Fig. 3g,h). We also measured Chk2 activity in the SN and found that Chk2 depletion suppressed Chk2 activation (p-Chk2/Chk2 ratio) following MPTP intoxication (Fig. 3i,j). Importantly, reducing Chk2 also protected dopamine neurons, since more tyrosine hydroxylase (TH) protein in the SN (Fig. 3i,k) and more TH-positive neurons were identified in these mice upon MPTP treatment (Fig. 3l,m). These results establish CHK2 as a therapeutically targetable kinase driving dopaminergic neurodegeneration in PD.

#### Pharmacological inhibition of Chk2 attenuates Parkinsonian phenotypes

Given the elevated Chk2 activity in PD mouse models, we evaluated the therapeutic potential of CCT241533 (hereafter CCT), a potent and selective Chk2 inhibitor (IC 50 = 3 nM), previously developed for oncology applications 42-44 (Supplementary Fig. 10a,b). We used the LRRK2 inhibitor DNL-201, which was evaluated in clinical trials for the treatment of PD, as a control 45 . In the MPTP-induced PD mouse model, CCT (0.2 µg or 2 µg, administered every other day for 21 days post-MPTP treatment) significantly ameliorated motor deficits, analogous to that of DNL-201 treatment (Fig. 4a,b and Supplementary Fig. 10a). Both doses reduced latency to turn in the pole test (Fig. 4a), while 2 µg CCT restored rotarod performance to near-baseline levels (Fig. 4b). Critically, CCT (2 µg) did not alter behavioural performance in control mice, indicating a safe profile (Fig. 4a,b). Immunoblot analysis revealed that MPTP treatment increased the p-Chk2/Chk2 ratio alongside reduced TH in the SN. Both doses of CCT effectively reversed these effects (Fig. 4c,d and Supplementary Fig. 11a). No changes in p-Chk1/Chk1 were observed (Fig. 4c and Supplementary Fig. 11b).

Consistent with the established mechanistic understanding that Chk2 phosphorylates and stabilizes p53 in response to DNA damage, XunZi correctly predicted Chk2-mediated regulation of p53 activity (Fig. 3a). Indeed, treatment with the Chk2 inhibitor CCT significantly reduced the p-p53/p53 ratio (Fig. 4c and Supplementary Fig. 11c). Notably, XunZi further identified Chk2 as a putative upstream regulator of LRRK2, a major genetic determinant of both sporadic and familial PD 46 (Figs. 3a and 4c). This prediction was unexpected, as no previous association was documented in PubMed or predicted by other leading AI agents. Subsequently, we found that CHK2 inhibition in the MPTP mouse model significantly suppressed LRRK2 activation, evidenced by reduced p-LRRK2/LRRK2 ratios (Fig. 4c,e and Supplementary Fig. 11d,e). Stereological quantification confirmed that CCT prevented dopaminergic neuronal loss in the SN, comparable to the LRRK2 inhibitor DNL-201 (ref. 45; Fig. 4f,g). These results confirm XunZi's capacity to generate mechanistically grounded hypotheses beyond conventional biological inference.

To further investigate how CHK2 inhibition may influence LRRK2-associated biology, we first examined whether CHK2 physically associates with LRRK2 in cells. Co-immunoprecipitation assays revealed a robust interaction since GFP-CHK2, but not GFP-alone, was readily detected in Myc-LRRK2 pulldowns (Supplementary Fig. 12a). We next performed RNA sequencing of SN tissue and compared transcriptional profiles between MPTP + CCT versus MPTP alone (set A) and MPTP + DNL-201 versus MPTP alone (set B). Differential expression analysis revealed a substantial overlap in differentially expressed genes (DEGs) between sets A and B (Supplementary Fig. 12b,c and Supplementary Table 8a,b). GO enrichment analysis of the shared DEGs indicated significant enrichment for biological processes related to nerve development, neuron differentiation, neuron fate commitment and the neuropeptide signalling pathway (Supplementary Fig. 12d and Supplementary Table 8c). Collectively, these convergent transcriptomic signatures indicate that CHK2 inhibition and LRRK2 inhibition modulate partially overlapping downstream biological programmes in the MPTP-injured SN.

We next assessed CCT (2 µg, every other day for 3 months) in the α-syn PFF-injection mouse model (Supplementary Fig. 10b). Treatment significantly improved motor performance in pole and rotarod tests (Fig. 4h,i). CCT also attenuated α-syn PFF-induced elevations in pathogenic p-α-syn/α-syn, p-Chk2/Chk2 and p-p53/p53 ratios (Fig. 4j-l and Supplementary Fig. 13a). Furthermore, CTT restored nigral TH expression and mitigated the loss of dopaminergic neurons (Fig. 4m,n and Supplementary Fig. 13b). No alteration was detected in p-Chk1/ Chk1 levels (Supplementary Fig. 13c). Thus, pharmacological inhibition of Chk2 by CCT rescues motor deficits, dopaminergic neuron survival and molecular pathology in two distinct PD models.

On the basis of the results generated by XunZi, we reconstructed a regulatory network incorporating seven PD-associated PKs, including two reported PKs (LRRK2 and PINK1), CHK2 and four additional PKs regulating MPP + -induced neurotoxicity in vitro, along with their downstream effectors (Fig. 4o). The resulting integrated network showed that these PKs are highly interconnected. Furthermore, the network demonstrated significant convergence onto core pathways known to be dysfunctional in PD, including dopaminergic neuronal degeneration, mitochondrial dysfunction, disruption of proteostasis, oxidative stress, the DNA damage response and apoptotic signalling. Importantly, PKs prioritized by XunZi, such as CHK2, showed significant connections within the network (Fig. 4o). This network structure indicates that these PKs may coordinate several different pathological processes in PD. Collectively, this systems-level analysis underscores the biological relevance of the prioritized PKs and supports their potential as targets for mechanism-based therapeutic discovery in PD.

### Discussion

The generation of de novo, mechanistically grounded hypotheses is the foundation for biomedical research, but has been greatly limited by human cognitive constraints in dealing with the huge volume of biomedical knowledge and data. Recently, LLM-based reasoning agents and MFMs have been proposed to facilitate scientific knowledge navigation and multimodal data fusion, respectively 14-17 . Several LLMs have emerged for biomedical text mining, medical knowledge question-answering and molecular property prediction, such as BioGPT 32 , Med-PaLM 47 and MolXPT 48 , demonstrating potential in processing domain-specific information. Meanwhile, graph-learning approaches have gained traction in target discovery, with methods such as DTI-GAT 49 , GraphDTA 50 and MGNN 51 effectively capturing complex biological network structures for drug repurposing and drug-target interaction prediction. The former frequently generates hallucinative responses, whereas the latter lacks transparent interpretability. To simultaneously reduce AI hallucinations and improve interpretability, we developed XunZi that combines logical reasoning and multimodal data fusion. The dual-module architecture allowed XunZi to consistently outperform other leading methods.

Using XunZi, we identified MYO1B as a previously unrecognized NSCLC regulator, and discovered CHK2 and IRAK4 as pathogenic PKs in PD. Importantly, previous efforts, including multiple genome-wide association meta-analyses, had not established a causal or mechanistic link between CHK2/IRAK4 and PD pathogenesis 52-54 . These results demonstrate how the integration of logical reasoning and multimodal data fusion can generate de novo insights inaccessible to single-modality systems. A notable finding is the identification of CHK2 as a putative regulator of LRRK2 by XunZi, which was subsequently validated by our experiments. Several kinases, including protein kinase A (PKA) 55 , casein kinase 1α (CK1α) 56 and IκB kinases 57 , are known to phosphorylate and activate LRRK2. Currently, it is unclear whether CHK2 directly phosphorylates LRRK2, or modulates LRRK2 activity indirectly via these known kinases. Critically, these results demonstrate that XunZi effectively establishes informative functional connections between findings not readily inferable from existing literature.

Although XunZi has demonstrated great potential in generation of de novo, well-grounded hypothesis for uncovering therapeutic targets in various human disease contexts, several limitations need to be considered in the future. First, gene functions in physiological contexts could be integrated to facilitate the identification of key regulators of cellular homeostasis. Second, incorporating temporal and spatial single-cell and multi-omics data could provide deep insights into intra- and intercellular heterogeneity in dynamics of human diseases. Third, integrating additional data types, such as sequences, structures, imaging data and electronic health records, could further enhance XunZi's mechanistic and clinical relevance. Finally, autonomous testing of scientific hypotheses could be realized by connecting XunZi with robotic laboratory systems.

Despite rigorous data curation and literature-based validation, fundamental biases in our training data are inevitable. The vast majority of gene-disease pairs remain unexplored due to current knowledge boundaries, creating an implicit bias where uncharacterized associations are treated as negatives. Currently, there exists no fully accurate dataset capturing gene-disease functional relationships, or any approach that can completely avoid such uncertainty. While our current training data have proven sufficient to achieve high predictive accuracy and successfully identify therapeutic targets, the inherent uncertainty in negative labels may introduce unavoidable biases into the training labels. While XunZi, together with its individual modules XunZi-R and XunZi-M, demonstrated strong predictive and reasoning performance on unseen data through cross-validation and independent test sets, risks of overfitting and limited generalization remain. These risks are particularly pronounced in disease contexts with sparse data availability or limited previous knowledge, such as rare diseases or emerging conditions, where the model may struggle to provide reliable predictions. Furthermore, although our mechanistic interpretations underwent extensive manual review to ensure biological plausibility and correct AI-generated errors, human curation inevitably introduces subjective biases that may affect data balance and representation despite our structured review protocols. These inherent limitations underscore why experimental validation, as demonstrated through our functional screening in NSCLC and PD models, remains crucial for verifying computational predictions. Future work will focus on expanding data coverage across a broader spectrum of diseases and gene targets not represented during training, developing more sophisticated strategies to define negative associations, and iteratively refining the model as biomedical knowledge expands.

In  conclusion,  XunZi  represents  a  critical  step  towards AI-augmented biomedical discovery. It turns disconnected, fragmented knowledge and data into testable hypotheses. Its success in finding treatable disease mechanisms shows how combining logical reasoning with multimodal data fusion accelerates therapy development. As future versions include more biological and clinical details, systems such as XunZi could move from helping scientists to working more independently. This would reshape the landscape of discovery and lower barriers to innovation.

### Methods

#### Preparation of the biomedical knowledge data

To build a comprehensive knowledge base for expert-level biomedical research, we constructed a pretraining corpus for XunZi-R by integrating diverse biological knowledge sources. First, we retrieved all available abstracts from published papers in PubMed before 2025, resulting in a corpus of over 24,411,924 biomedical publications. This corpus serves as the foundation for capturing scientific language patterns, terminologies and hypothesis structures commonly used in biological research.

Also, we incorporated 2,054,130 structured biological corpora to enhance the domain-specific understanding of XunZi-R. We extracted 297,098 gene entries from the gene\_info dataset and 1,694,980 literature-derived functional descriptions from the GeneRIF dataset, both of which were obtained from the National Center for Biotechnology Information (NCBI) 58 . These datasets provide concise insights into gene identity, function, related pathways and biological roles across a wide range of organisms. Furthermore, we incorporated disease definitions from the DO database (https://disease-ontology.org/) 11 , which provides hierarchically structured vocabularies for diseases. A total of 14,132 disease terms were collected, each containing standardized identifiers, synonyms, hierarchical classifications and curated descriptions of disease characteristics and underlying mechanisms. We also integrated the texts of 47,920 GO definitions on biological processes, molecular functions and cellular components from the GO knowledgebase (https://geneontology.org/) 28 .

#### Construction and curation of the gene-disease mechanistic corpus

To confer XunZi-R with expert-level biological reasoning, we constructed a structured gene-disease mechanism dataset from curated biomedical knowledge. We first collected all available gene-disease associations from two data resources, including 47,576 entries from DisGeNET 10 and 34,166 entries from CTD 13 . After redundancy clearance, we obtained 77,118 unique gene-disease pairs, each linked to one or more supporting PubMed entries. The details are shown as follows.

Mechanistic interpretation generation . For each gene-disease pair, we retrieved the corresponding abstracts from PubMed using the literature PMIDs provided by DisGeNET and CTD. In addition, we utilized the PubMed API through the research function from the NCBI Entrez module (Entrez.esearch(db = 'pubmed', term=query, retmax=retmax, sort = 'relevance', usehistory = 'y')) to download the three most relevant articles for each gene-disease relationship (Supplementary Table 2a). We designed the following prompt template to ensure consistent and comprehensive outputs:

Prompt template:

 'Based on the provided abstract below and existing biological knowledge, analyse the functional role of a specific gene in a given disease.

Abstract:

{Abstract}

Task:

 Describe how the gene {gene\_name} ({gene\_symbol}) influences the disease {disease\_name}. Your answer should consider both direct and indirect biological effects, including potential regulatory impacts on other genes and involvement in signalling pathways.

###### Output Format:

Return your response strictly in the following JSON structure:  {'mechanism\_description': '[Provide a concise description within 2-3 sentences describing the gene's functional mechanism in the disease context.]',

'impacted\_genes': ['Gene1', 'Gene2',…], 'impacted\_pathways': ['Pathway1', 'Pathway2',…]}'

Manual verification and error correction . To ensure data quality and avoid AI hallucinations, six students, including X.H., J.Q., F.T., C.Y., D.L. and Y.T. manually checked each entry of GPT-4-summarized interpretations. Each interpretation was validated against the source abstracts and cross-referenced with established biological knowledge. During this process, we identified and corrected four major categories of errors: (1) Unfounded fabrications: Spurious associations that violated established biological principles or described mechanisms contradicting confirmed knowledge were removed. (2) Factual inaccuracies: Errors in gene functions, pathway assignments or disease mechanism attributions were corrected through cross-referencing with functional annotations and literature. (3) Logical inconsistencies: Descriptions were restructured to ensure causation in all mechanistic explanations, eliminating contradictory statements within the same interpretation. (4) Incomplete summary: Oversimplified mechanisms were augmented with critical intermediate steps, regulatory factors and tissue-specific elements necessary for accurate representation.

Dataset construction and formatting . Following manual curation, we formatted the verified interpretations into a CoT mechanistic interpretation corpus. Each instance comprises three components:

- (1) A natural language instruction prompt (for example, 'Is gene LRRK2 involved in Parkinson's disease in a functional way?');
- (2) A binary label (Yes or No) indicating whether the gene is functionally implicated;
- (3) A reasoning trace, combining literature-derived explanations with the inferred mechanism (for example, altered function, affected pathways and downstream targets).

For functionally relevant gene-disease pairs, at least one detailed CoT annotation was provided. After manual curation, a total of 116,301 positive samples were retained. To enable robust discrimination between functional and non-functional associations, we also included 219,807 negative samples for gene-disease pairs lacking supporting evidence or functional relevance. These negative instances were annotated with explicit statements indicating the absence of functional involvement (for example, 'No evidence supports the functional involvement of this gene in the specified disease'), teaching the model to recognize and reject spurious or indirect associations. As a result, we curated a total of 336,108 CoT-style annotated instances, covering 27,188 unique genes across 7,744 distinct diseases.

#### Collection of publicly available multi-omics datasets

We curated 613.2 TB of multi-omics datasets, including transcriptomic, proteomic and phosphoproteomic data, for pan-cancer and neurodegenerative diseases from established biomedical repositories and literature sources. For pan-cancer datasets, we mainly retrieved data from the Cancer Genome Atlas (TCGA) 5 and the Clinical Proteomic Tumor Analysis Consortium (CPTAC) 6 , which provide comprehensive molecular profiles across 33 cancer types. To supplement RNA-level data, we also curated additional transcriptomic datasets from GEO 12 using disease-specific terms (for example, 'lung adenocarcinoma', 'bladder carcinoma' and so on) as search keywords. Meanwhile, we searched PubMed by combining cancer names with terms such as 'transcriptomics', 'proteomics' and 'phosphoproteomics' to collect multi-omics datasets from the literature. For neurodegenerative diseases, we focused on large-scale, multicohort studies available through the AMP-AD Knowledge Portal 9 , a comprehensive repository for AD and aging-related omics data. Multi-omics datasets were downloaded from landmark projects including the Mount Sinai Brain Bank (MSBB) 8 and the Religious Orders Study and Memory and Aging Project (ROSMAP) 7 . Additional transcriptomic datasets were retrieved from GEO using terms such as 'Alzheimer's disease', 'Parkinson's disease' and 'Huntington's disease'. We further searched PubMed to include literature-based multi-omics datasets covering a broader range of neurodegenerative disorders. All datasets were subsequently deduplicated, standardized and reformatted to ensure compatibility for downstream integrative modelling and computational analysis. Raw FASTQ files from multiple studies were processed using a uniform RNA-seq workflow. Sequencing reads were trimmed with fastp 59 and aligned to the appropriate GENCODE reference genome using STAR 60 . Gene-level quantification was performed with featureCounts 61 , which supports both single-end and paired-end libraries. For datasets from publicly released gene-level expression matrices, raw counts or normalized values were used. For datasets from publicly available gene-level expression matrices (raw counts or normalized values), we harmonized them to a common reference annotation, mapped to consistent gene identifiers (Ensembl IDs to gene symbols) and normalized for integration with uniformly processed datasets. For proteomic and phosphoproteomic datasets, data from data-dependent acquisition (DDA) and isobaric labelling experiments were processed using MaxQuant 62 , Proteome Discoverer 63 or FragPipe 64 . Data from data-independent acquisition (DIA) and PASEF-based experiments 65 were primarily processed with Spectronaut 66 or related DIA workflows 67,68 . Across all platforms, database searches were standardized with trypsin specificity, canonical fixed and variable modifications, and a stringent 1% false discovery rate (FDR) at the peptide-spectrum match (PSM), peptide, and protein or site levels to ensure comparability. For studies with restricted raw data access, provided quantification matrices were harmonized with reprocessed datasets through standardized identifier mapping, intensity normalization and alignment to a unified protein reference database, ensuring integration without study-specific biases.

#### Construction of a knowledge graph for protein interactions and their involved biological processes

To capture the molecular connectivity and functional landscape of the biological system, we constructed a large-scale protein-function knowledge graph by integrating protein identity with molecular interactions and functional annotations. We first collected 573,230 protein entries from UniProt 69 , which were mapped to standardized gene identifiers to establish the corresponding gene nodes. To capture physical and functional relationships between proteins, we compiled 2,813,799 PPI edges from seven public databases, including BioGRID 70 , iRefIndex 71 , PINA 72 , HINT 73 , mentha 74 , IID 75 and BioMap 76 . Meanwhile, we retrieved 47,922 GO terms from the GO database. On the basis of biological process annotations from UniProt, each protein was connected to one or more relevant GO terms, forming protein-GO associations. Using NetworkX v.2.5 (https://networkx.org/documentation/networkx-2.5/news.html), we constructed the complete knowledge graph comprising 621,152 nodes and 6,094,282 edges. In the entire graph, each node was embedded in a 4,096-dimensional vector to represent biological entities, including proteins and GO-defined functional terms, and edges capture either physical protein-protein interactions or functional annotations connecting proteins to their GO terms. This graph serves as the foundation for downstream knowledge representation and graph-based model training, enabling multimodal data fusion and integrated learning over both molecular structure and biological semantics.

#### Implementation of the reasoning module of XunZi

To equip XunZi with expert-level mechanistic reasoning capabilities, we implemented the reasoning module, XunZi-R, on the basis of continual pretraining using domain-specific biomedical knowledge, followed by instruction fine-tuning with our CoT-style mechanistic corpus.

- (1) Continual pretraining for biomedical language modelling . We adopted Mistral-7B as the backbone model. Mistral-7B is a high-performance, open-weight LLM featuring sliding-window attention and grouped-query attention, optimized for efficient inference with smaller parameters 27 . Continual pretraining was implemented in a causal language modelling (CLM) framework 77 ,

where the model learns to predict the next token xt given the previous context x&lt;t , updating parameters to minimize the negative log-likelihood loss:

<!-- formula-not-decoded -->

where x = ( x 1 , x 2 , …, xT ) is a tokenized sequence from our biomedical knowledge data, and θ denotes the model parameters. Training was conducted with a sequence length of 1,024 tokens, using AdamW optimizer with a linear learning rate scheduler of 1 × 10 -5 and a cosine learning rate schedule with 10% warmup for 2 epochs of training the model.

- (2) Instruction fine-tuning using CoT-style gene-disease mechanistic corpus . Each training instance was formatted as a structured input-output pair, where the input is a natural language instruction (for example, 'Is gene TP53 involved in lung cancer in a functional way?'), and the output contains a binary label (Yes/No) followed by a multistep reasoning trace, including the gene's function, regulatory context and downstream pathway impact. Fine-tuning was conducted using the supervised fine-tuning (SFT) strategy, which minimizes the cross-entropy loss between the predicted output tokens and the gold-standard response:

<!-- formula-not-decoded -->

where x is the instruction prompt, y = ( y 1 , y 2 , …, yT ) is the target CoT-style response, and θ represents the model parameter after continual pretraining. Training was performed by a per-device batch size of 16 and gradient accumulation steps of 8, resulting in an effective batch size of 128. Optimization was also carried out using the AdamW optimizer with a learning rate of 1 × 10 -5 , a cosine learning rate schedule and a warmup ratio of 10%. Mixed-precision training with bfloat16 (bf16) was enabled for computation efficiency.

#### Benchmarking

To systematically evaluate XunZi-R's ability to reason gene involvement in disease pathogenesis with mechanistic interpretations, we conducted a comprehensive benchmarking framework using the gene-disease mechanism dataset described above. We employed fivefold cross-validation and the reciprocal test (training on DisGeNET and testing on CTD and vice versa) to ensure robust assessment of generalization capability and eliminate data leakage. For fivefold cross-validation, the dataset was divided into five equal subsets, with four subsets used for training and the remaining subset as an unseen validation set, and the evaluation process was repeated five times. For the reciprocal test, we trained the model on the DisGeNET dataset and tested it on the non-overlapping CTD dataset and vice versa. XunZi-R was benchmarked against multiple representative language models as baselines: GPT-o3, GPT-5, DeepSeek-R1, DeepSeek-V3, GPT4, Claude Sonnet 4, Claude 3.7 Sonnet, Claude Sonnet 4.5, GPT-4o and BioGPT, which represent diverse architectural designs and parameter scales.

Classification of functional gene-disease associations task . Models were evaluated on their ability to determine whether a gene is functionally involved in a given disease. In this task, models received a standardized prompt to ensure consistency and enable extraction of binary predictions (Yes/No) for accuracy assessment:

'Is gene [X] involved in disease [Y] in a functional way? Start with Yes or No.'

This uniform prompting protocol allowed systematic comparison of classification performance across all state-of-the-art evaluated models. The following metrics were used to evaluate classification performance:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

In these metrics, TP (true positive) represents correctly predicted functional gene-disease associations, TN (true negative) represents correctly predicted non-functional associations, FP (false positive) represents incorrectly predicted functional associations, and FN (false negative) represents incorrectly predicted non-functional associations.

Precision indicates the proportion of positive predictions that are correct. Recall assesses the proportion of actual positives that are correctly identified. Specificity measures the proportion of actual negatives that are correctly identified. F 1 is the harmonic mean of Precision and Recall, balancing both metrics. MCC is a balanced metric that accounts for all four outcomes, particularly useful for imbalanced datasets.

Mechanistic interpretation generation task . To evaluate XunZi-R's quality of mechanistic interpretations and its ability to generate biologically plausible explanations including downstream genes and pathways, a structured evaluation framework was developed. To standardize the free-form responses from other general-purpose large language models and enable direct comparison, we designed a standardized prompt template to elicit structured mechanistic interpretations and facilitate systematic evaluation:

The prompt template was as follows:

'Is Gene [X] involved in disease [Y] in a functional way? Start your answer with 'Yes' or 'No'. Then describe in two sentences how the gene influences the disease, including direct and indirect biological effects. Finally, list the 'Impacted Genes' and 'Impacted Pathways' as shown below:

Example format:

Yes/No. [Mechanism description]

Impacted Genes: [list]

Impacted Pathways: [list]'

This structured prompting strategy was applied uniformly across all other evaluated models to standardize output format, minimize response variability and ensure extraction of key biological components for quantitative assessment. We evaluated the generated interpretations using semantic similarity metrics and lexical overlap measures against expert-verified reference interpretations with biological knowledge.

BERTScore was computed using SciBERT embeddings 78 to assess contextual alignment between generated and reference texts. This metric captures whether biological explanations maintain scientific accuracy beyond surface-level matching. This metric captures semantic accuracy of biological mechanisms and validates the contextual relevance of predicted genes and pathways.

Precision measures the proportion of relevant tokens in generated text appearing in reference, Recall measures the proportion of reference content captured in generated text, and F 1 provides a balanced measure of both Precision and Recall. BLEU scores were calculated on the basis of N -gram overlap from unigrams to 4-grams, quantifying the precision of specific biological terminology and phrase-level accuracy in mechanistic descriptions, particularly for exact matches of gene names and pathway components. ROUGE metrics were employed to assess content coverage through recall-oriented evaluation. ROUGE-1 measures unigram overlap, capturing individual biological terms. ROUGE-2 evaluates bigram overlap, measuring biological relationships. ROUGE-L identifies the longest common subsequence, preserving explanation structure.

#### Implementation of XunZi-M

Building on the curated multi-omics datasets and the constructed knowledge graph, we developed disease-specific molecular pretrain models for pan-cancer and neurodegenerative diseases through graph-based representation learning. In both contexts, each node in the graph, representing a gene, was embedded with an expression vector derived from the corresponding transcriptomic, proteomic or phosphoproteomic measurements under different biological conditions. For each molecule identified in omics analyses, we calculated the following features: normalized transcriptomic expression denoted by fragments per kilobase of transcript per million mapped reads (FPKM) or transcripts per million (TPM) values for RNA sequencing (RNA-seq), normalized proteomic intensity (mass spectrometry-based protein quantification), mean phosphosite intensities (in cases where multiple p-sites were mapped to the same protein).

- a. For pan-cancer, each gene node was embedded with a feature vector derived from its expression profiles across 33 cancer types. For each cancer type, we obtained transcriptomic, proteomic and phosphoproteomic measurements under both tumour and matched normal conditions. Expression values were standardized within each study and averaged across samples under the same condition. Let x i ∈ ℝ d denote the feature vector of gene i , where each dimension corresponds to the averaged expression value under a specific cancer type and condition. Specifically, for gene i , its expression in one cancer type is represented as:

<!-- formula-not-decoded -->

where e cancer ij and e normal ik denote the normalized expression values of gene i in tumour and normal samples, respectively, and nc , nn are the number of samples per condition. The final feature vector x i is constructed by concatenating such vectors across all cancer types.Next, we conducted semantic embeddings for GO term nodes. Specifically, each GO term was input into XunZi-M for token-level representations. The final hidden state of the last token from the output layer (dimension = 4,096) was extracted and used as the semantic feature vector.After initializing the feature vectors for all nodes, we employed a GCN to propagate features across the heterogeneous graph structure. Given a graph G = ( V , E ), where V denotes the set of nodes and E the edges, and the initial node features X ∈ ℝ | V |× d , the GCN layer updates node representations as follows:

̂

<!-- formula-not-decoded -->

̂

̂

̂

̂

where A = A + I is the adjacency matrix with added self-loops, D is the degree matrix of A , H Ⴞ l Ⴟ is the hidden representation at layer l, with H Ⴞ Š Ⴟ = X. W Ⴞ l Ⴟ is the trainable weight matrix of layer l , σ is the nonlinear activation function, ReLU, which is defined as follows:

̂

<!-- formula-not-decoded -->

We stacked two GCN layers to allow for two-hop message aggregation. To construct training labels, we collected all gene-cancer relevance annotations from DisGeNET and the CTD for positive labels. The graph model was trained as a binary classifier, predicting whether each gene plays a functional role in cancer. The final model was optimized using the binary cross-entropy loss over labelled gene nodes:

̂

<!-- formula-not-decoded -->

̂

̂

where ėi ∈ { Š , š } is the true label, ė i is the predicted probability from the GCN model, and γ is the set of labelled nodes.To construct a disease-specific model for NSCLC, we fine-tuned the pretrained graph representation on a task-specific subgraph. Specifically, we extracted the final-layer node embedding from the pan-cancer pretrained GCN model as generalized molecular representations. These were then concatenated with NSCLC-specific multi-omics expression vectors. Formally, for each gene i , the final input representation in the NSCLC model is defined as:

<!-- formula-not-decoded -->

where h pretrained i ∈ ℝ d š is the final hidden state from the pretrained model, and x lung i ∈ ℝ d Ţ is the multi-omics feature vector from lung cancer. Finally, we used these features to train a tow-layer GCN for NSCLC.

- b. For neurodegenerative disease, we adopted the same graph-based learning framework. For each gene node, the feature vector was derived from its expression across distinct brain regions under different disease states. Specifically, for each brain region r , we calculated the averaged expression under case and control conditions:

<!-- formula-not-decoded -->

where e case ij and e control ik represent the normalized expression of gene i in case and control samples within region r , respectively. The full feature vector xi for each gene was constructed by concatenating these region-specific vectors across multiple brain regions.

To identify functional regulators in PD, we constructed a PD-specific subgraph by combining the pretrained node embeddings with PD-specific omics features. We then trained a two-layer GCN to classify PD-relevant genes and kinases, using curated labels from DisGeNET and CTD. The model was optimized using binary cross-entropy loss, using the AdamW optimizer.

#### Development of the AI biologist, XunZi

To integrate logical reasoning with multimodal data fusion, we designed a hybrid framework that integrates the outputs of XunZi-R and XunZi-M. Specifically, we leveraged XunZi-R to perform structured mechanistic reasoning for each gene-disease query using CoT prompting. To capture confidence in the reasoning outcome, we appended an explicit instruction asking for a self-assessed certainty score:

'Is gene SHBG involved in Endometrial Neoplasm in a functional way? In addition, please provide your confidence level for this answer on a scale from 0 to 10.'

This confidence level was then normalized to the range [0, 1] and treated as a scalar feature s i for each gene node i . To incorporate this value into our molecular network model, we extended the graph-based predictor by modifying the final classification layer to perform feature-level fusion. Formally, for each gene node i , let h i ∈ ℝ d denote the hidden representation obtained from the last GCN layer, and let s i ∈ ℝ d be the corresponding normalized confidence score. We constructed a fused input vector by concatenation:

<!-- formula-not-decoded -->

̂

The final  prediction ė i ∈ℝ was  then  computed  via  a  linear transformation:

̂

<!-- formula-not-decoded -->

This hybrid strategy enables XunZi to harness both the semantic reasoning capacity of large language models and the contextual molecular knowledge embedded in omics-informed biological graphs. It allows the system to refine its predictions by balancing statistically grounded omics patterns with interpretive insights drawn from the biomedical literature. XunZi was trained on NVIDIA A800 GPUs (80 GB), with a cumulative compute time of ~3,600 GPU hours (8 GPUs over 450 h).

#### Cell culture and viability assay

N2a, A549, SW1271 and HepG2 cells (American Type Culture Collection, ATCC) were cultured in Dulbecco's modified Eagle's medium (DMEM; Gibco, Thermo Fisher) supplemented with 10% fetal bovine serum (FS301, TransGen Biotech) and 1% penicillin-streptomycin at 37 °C in a humidified incubator with 5% CO 2 . NCI-H520 were maintained in RPMI1640 medium. For small interfering RNA (siRNA)-mediated knockdown experiments, A549, NCI-H520, SW1271 and HepG2 cells were seeded in 24-well plates for 24 h and transfected with siRNAs targeting the indicated genes for 48 h. N2a cells were transfected with siRNAs for 24 h and subsequently treated with 2 mM MPP + for 24 h. Cell viability was measured using the 3-(4,5-dimethylthiazol-2-yl)-2,5-diphenyltetrazolium bromide (MTT) assay. Briefly, 50 µl of MTT solution (5 mg ml -1 ; Sigma, D048) was added to each well and incubated for 4 h. Formazan crystals were then dissolved in 600 µl of dimethyl sulfoxide, and absorbance was measured at 490 nm. To provide an expression-based comparator, 20 DEGs selected from the GEPIA database were evaluated in A549 cells using the same siRNA transfection and MTT assay workflow.

#### RNA interference experiments

siRNAs were synthesized by GenePharma. The nucleotide sequences of all siRNA oligonucleotides are provided in Supplementary Tables 9-11. N2a or human cancer cell lines (A549, NCI-H520, SW1271 and HepG2) were transfected with mixed siRNAs using the RNAFit transfection reagent (HANBIO, HB-RF-1000) following manufacturer instructions.

#### Animals

Male C57BL/6 mice (2 months old) were purchased from Chongqing Ensiweier. All animals were maintained under standardized environmental conditions, including a 12-h light/dark cycle, and controlled temperature (20-22 °C) and relative humidity (45-66%). Food and water were provided ad libitum throughout the study. All animal procedures were performed in compliance with the Guide for the Care and Use of Laboratory Animals and was approved by the Animal Investigation Committee of West China Hospital, Sichuan University.

#### Open field test

The open field test was conducted following established protocols from previous studies. The open field apparatus comprised a white acrylic enclosure measuring 50 × 50 × 50 cm, illuminated by LED lights positioned 60 cm above its base. Each mouse was gently introduced into a corner of the arena, and its activity over a 10-min period was recorded using an overhead infrared camera. Behavioural parameters, including total distance travelled and mean moving velocity, were analysed with SuperMaze software (Xinruan Information Technology).

#### Pole test

The pole test was performed similarly to previous studies 79 . The pole test apparatus consisted of a 70-cm-high wooden pole with a diameter of 1 cm and a ball affixed to its top. The day before the official test, the animals received five consecutive trainings. During the assessment, the turning time of mice at the top of the wooden pole was recorded by digital video, with a maximum cut-off time of 10 s. To eliminate olfactory cues, the apparatus was sanitized with 75% ethanol between trials.

#### Rotarod test

Mice were placed on the rod of a rotarod apparatus to assess motor coordination and fatigue. The rod accelerated from 4 r.p.m. to 40 r.p.m. over 300 s at an acceleration of 7.2 r.p.m. min -2 , after which it maintained a constant speed of 40 r.p.m. for the remainder of the 60-s test. One day before testing, animals were habituated to the apparatus through three training sessions spaced 20 min apart. During the formal assessment, the latency to fall was recorded for each of three consecutive trials spaced 20 min apart, and the average of these trials was used for subsequent analysis.

#### Immunohistochemical analyses of nigral dopaminergic neurons and stereoscopic estimation of their numbers

Procedures were performed as previously described 79 . Under deep anaesthesia, mice were perfused with ice-cold phosphate-buffered saline (PBS, pH 7.4). Brains were extracted and post fixed in 4% paraformaldehyde for 24 h, followed by cryoprotection in 30% sucrose for another 48 h. The tissues were then frozen on dry ice, and coronal brain sections (30-μm thick) were obtained using a temperature-controlled cryostat (CM1860, Leica). Brain sections were first blocked with 6% normal goat serum (Solarbio, SL038) for 1 h at room temperature, followed by overnight incubation at 4 °C with a primary antibody targeting tyrosine hydroxylase (TH; 1:1,000, Merck, ab152). The next day, sections were incubated for 2 h at room temperature with an HRP-conjugated goat anti-rabbit secondary antibody, then briefly developed using a diaminobenzidine solution (1:50, Abcam, ab64238) for 30 s. After mounting with coverslips, the staining process was completed 80 . TH-positive neurons within the SN pars compacta (SNpc) were quantified using an automated stereological method previously reported 81 . In brief, the procedure utilized Stereo Investigator software (version 2017, MicroBrightField) to delineate the SNpc under a ×10 objective (numerical aperture 0.25) with a superimposed sampling grid covering the region of interest. TH + immunoreactive cells were then identified at a higher magnification (×40 objective, numerical aperture 0.8), and only these cells were included in the final count.

#### Immunoprecipitation

The cDNA encoding human CHK2 (residues 1-543) was PCR amplified and cloned into pCMV-EGFP. The cDNA encoding human LRRK2 (residues 1-2,526) was cloned into pCMV-3Myc. All mutants were generated by site-directed mutagenesis (MCLAB). HEK293T cells were transfected using Hieff Trans Liposomal Transfection Reagent (Yeasen, 40802ES03) following manufacturer instructions. After transfection, cells were treated with 25 nM rotenone for 24 h before immunoprecipitation.

Cells were collected and lysed on ice in lysis buffer (100 mM Tris-HCl pH 7.5, 150 mM NaCl, 0.5 mM EDTA, 0.5% NP-40, 1% Triton X-100) supplemented with phosphatase inhibitors and a protease inhibitor cocktail and kept at 4 °C for 30 min. The lysates were spun at 13,400 g for 10 min at 4 °C to pellet insoluble debris, after which the supernatants were transferred to fresh tubes. The cleared extracts were incubated overnight at 4 °C with agarose beads coupled to the indicated antibodies. Beads were washed three times at 4 °C with wash buffer (150 mM Tris-HCl pH 7.5, 150 mM NaCl, 0.5 mM EDTA in PBS) to minimize non-specific binding. The bead-bound proteins were then collected for analyses.

#### Immunoblotting

Immunoblotting was performed similarly to previous studies 82 . Mice were deeply anaesthetized and transcardially perfused with ice-cold PBS pH 7.4. Mouse brains were promptly extracted, and the cerebellum and SN regions were carefully dissected on ice. Tissue samples were homogenized in RIPA lysis buffer (Solarbio, B0010) supplemented with a protease inhibitor cocktail (TargetMol, C0001) and a phosphatase inhibitor cocktail (Selleck, B15001).

Cells were collected and lysed using RIPA buffer, phosphatase inhibitors II and III (diluted 1:100), and phenylmethylsulfonyl fluoride (PMSF, diluted 1:100) as a protease inhibitor. The resulting lysates were centrifuged at 13,400 g for 25 min at 4 °C, and the supernatants were mixed with an equal volume of 1× SDS loading buffer, followed by boiling at 98 °C for 15 min. Subsequent immunoblotting analyses were conducted in accordance with previously described protocols 83,84 . The primary and secondary antibodies utilized in this study are detailed in Supplementary Table 12.

#### sgRNA design and AAV construction

The Chk2 sgRNA sequence (5'-ACTGTCATGAGCCTTCGAGG-3') was cloned into the pAAV-U6-spgRNA (NC)-CMV-EGFP-WPRE vector. The resulting vector, the Cas9 vector (pAAV-tCMV-spCas9-NLS-Flag), or a control plasmid encoding EGFP, were utilized to produce recombinant AAV serotype 9 (rAAV9) vectors. All AAVs were produced, purified and titrated following established protocols (Obio), then aliquoted and stored at -80 °C until further use.

#### Chk2 AAV injection

C57BL/6 mice (3 months old) were anaesthetized and positioned in a stereotaxic apparatus (RWD, 68037). Following scalp sterilization and cranial drilling, a glass micropipette loaded with either 1 μl ssAAV9-mChk2 (1 × 10 13 GC ml -1 ) and 1 μl ssAAV9-Cas9 (1 × 10 13 GC ml -1 ), or 2 μl ssAAV9-control (1 × 10 13 GC ml -1 ) was stereotactically injected into the left SN (coordinates: AP -3.1 mm, ML -1.2 mm, DV -4.0 mm from the dura). Injections were performed at a flow rate of 100 nl min -1 . Upon completion, the glass electrode was held in place for an additional 5 min to prevent backflow before being slowly withdrawn. The incision was then sutured, and animals received appropriate postoperative care until recovery. Behavioural performance was assessed at 45 days post-AAV injection using the open field test and rotarod test. Chk2 protein level in the SN was tested by immunoblotting.

#### MPTP mouse model construction and drug treatment

To construct the MPTP mouse model, 3-month-old C57BL/6 mice received four intraperitoneal injections of either saline or MPTP (20 mg kg -1 , Selleck, S4732) at 2-h intervals on day 1. Behavioural performance was assessed at 18 days post-MPTP administration using the pole test and rotarod test.

For drug treatment, mice were first injected with saline or MPTP on day 1. Beginning on day 2, mice were treated with 0.2 μg CCT241533 (intranasal, MedChemExpress, HY-14715B), 2 μg CCT241533 or LRRK2 inhibitor DNL-201 (intraperitoneal, MedChemExpress, HY-15796) every other day for 20 consecutive days. The dosing concentrations of CCT241533 and DNL-201 were based on previous research reports 45,85 . Behavioural studies, immunoblotting and immunohistochemistry (IHC) were conducted starting on day 19 to assess the efficacy of drug treatment.

#### α-Syn PFF preparation

α-Syn PFF construction was conducted in accordance with a previous study 86 . The synthesized mouse-derived α-syn monomers were dissolved in sterile PBS at a concentration of 5 mg ml -1 and continuously shaken at 37 °C and 1,400 r.p.m. for 7 days. The morphology of α-syn fibres was observed using an electron microscope. Once the aggregation state of α-syn met the experimental requirements, polymerization was carried out. α-Syn PFFs were aliquoted and stored at -80 °C.

#### α-Syn PFF mouse model construction and drug treatment

To construct an α-syn PFF mouse model of PD, 12-month-old C57BL/6 mice were anaesthetized and positioned in a stereotaxic apparatus (RWD, 68037). Following scalp sterilization and cranial drilling, a glass micropipette loaded with 2 μl PBS or α-syn PFFs (2.5 μg μl -1 ) was stereotactically injected into the left striatum (coordinates: AP +0.2 mm, ML +2.0 mm and DV -2.6 mm). The syringe was held in place for 5 min post-injection to minimize backflow, after which it was slowly withdrawn. The scalp was sutured, antibiotic ointment was applied to the incision site, and animals were placed in a recovery chamber before returning to their home cages 87 . Behavioural performance was assessed at 90 days post-PFF administration using the pole test and rotarod test.

For drug treatment, mice were first injected with PBS or α-syn PFFs on day 1. Beginning on day 2, mice were treated with 2 μg CCT241533 (intranasal, MedChemExpress, HY-14715B) every other day for 90 consecutive days. Behavioural studies, immunoblotting and IHC were conducted starting on day 91 to assess the efficacy of drug treatment.

#### RNA quantification and qualification

RNA degradation and contamination was monitored on 1% agarose gels. RNA purity was assessed using the NanoPhotometer spectrophotometer (IMPLEN). The concentration of RNA was measured using a Qubit RNA Assay kit in a Qubit 2.0 Flurometer (Life Technologies). RNA integrity was examined using the RNA Nano 6000 Assay kit of the Bioanalyzer 2100 system (Agilent).

#### RNA-seq library preparation and sequencing

A total amount of 1 μg RNA per sample was used as input material for the RNA sample preparations. Sequencing libraries were generated using NEBNext UltraTM RNA Library Prep kit for Illumina (NEB) following manufacturer recommendations, and index codes were added to attribute sequences to each sample. mRNA was purified from total RNA using poly-T oligo which attached magnetic beads, then fragmented using divalent cations at elevated temperatures in NEBNext First Strand Synthesis Reaction Buffer (5×). Remaining overhangs were converted into blunt ends via exonuclease/polymerase activities, followed by adenylation of 3' ends of DNA fragments. NEBNext Adaptor with hairpin loop structures were ligated, and cDNA fragments of preferentially 250 ~ 300 bp length were size selected using the AMPure XP system (Beckman Coulter). Adapter-ligated cDNA was treated with 3 μl USER Enzyme (NEB) at 37 °C for 15 min, followed by 5 min at 95 °C before PCR. PCR was conducted with Phusion High-Fidelity DNA polymerase, Universal PCR primers and Index (X) Primer. Finally, the PCR products were purified with the AMPure XP system and library quality was assessed on the Agilent Bioanalyzer 2100 system. The cDNA libraries were sequenced on the lllumina sequencing platform by Metware Biotechnology.

#### Preparation of protein extracts

To extract proteins, frozen mouse brain was ground in liquid nitrogen, mixed 1:4 (w/v) with lysis buffer (8 M urea, 1% protease inhibitors) and sonicated on ice (three bursts). After centrifuging at 12,000 g for 10 min at 4 °C, the supernatant was quantified by bicinchoninic acid assay. For digestion, proteins were reduced with 5 mM dithiothreitol at 56 °C for 30 min, alkylated with 11 mM iodoacetamide in the dark for 15 min, then diluted with 100 mM TEAB buffer to &lt;2 M urea. Trypsin was added at 1:50 (w/w) overnight, followed by a 4 h 1:100 boost. Peptides were desalted using C18 solid-phase extraction (SPE) cartridges.

For tandem mass tag (TMT) labelling, peptides in 0.5 M TEAB were tagged following Thermo Fisher's protocol for 2 h at room temperature. A 5-μl pool was checked by MS, then 5% hydroxylamine quenched the reaction. Labelled peptides were combined, desalted using Strata C18-E SPE cartridges and vacuum dried.

#### Phosphopeptide enrichment

Samples were separated by high-pH RP-HPLC (Agilent 300 Extend C18, 5 μm, 4.6 × 250 mm) using an 8-32% acetonitrile (ACN) gradient in 10 mM NH4HCO3 (pH 9) over 60 min into 60 fractions, which were pooled into 8 and vacuum dried. Peptides were bound to IMAC beads in 50% ACN/0.5% acetic acid (AcOH), washed sequentially with 50% ACN/0.5% AcOH and 30% ACN/0.1% trifluoroacetic acid, then eluted with 10% NH4OH, and the supernatant was lyophilised for LC-MS/MS.

#### LC-MS/MS analysis

Tryptic peptides were loaded in solvent A (0.1% formic acid, 2% ACN in water) onto a 25 cm × 100 μm home-made C18 column and eluted on an EASY-nLC 1200 system at 500 nl min -1 with solvent B (0.1% formic acid, 90% ACN) using a 60-min gradient: 7-10% B (0-4 min), 10-32% B (4-53 min), 32-80% B (53-57 min), 80% B (57-60 min). Eluted peptides were analysed on an Orbitrap Exploris 480 mass spectrometer with nano-ESI (2.3 kV) and FAIMS (-45 V). Full MS ( m / z 400-1,200) was acquired at 60,000 resolution, and MS/MS scans (first mass 110 m / z ) at 15,000 resolution with TurboTMT enabled. The top 25 precursors were fragmented by higher-energy collisional dissociation at a normalized collision energy of 35%, with the automatic gain control at 100%, a 50,000-ion threshold, 'Auto' max injection and 30 s dynamic exclusion.

#### Database search

The resulting MS/MS data were processed using the Proteome Discoverer search engine (v.2.4.1.15). Tandem mass spectra were searched against Mus\_musculus\_10090\_SP\_20210721.fasta (17,089 entries) concatenated with a reverse decoy and contaminants database. Trypsin (full) was specified as a cleavage enzyme allowing up to 2 missing cleavages. Minimum peptide length was set as 6. The number of modifications per peptide was set as 3. Mass error was set to 10 ppm for precursor ions and 0.02 Da for fragment ions. Carbamidomethyl on Cys, TMT-10plex (peptide N terminus) and TMT-10plex (K) were specified as fixed modifications. Oxidation on Met, acetylation on protein N terminal, Met-loss on Met and Met-loss + acetyl on Met were specified as variable modifications. TMT-10plex quantification was performed. FDR of protein, peptide and PSM was adjusted to &lt;1%.

#### Performance evaluation and comparison

For the evaluation of XunZi, XunZi-M, XunZi-R and other methods, the TP, TN, FP and FN values were calculated for each model. Then, four measurements of the sensitivity (Sn), specificity (Sp), accuracy (Ac) and Mathew correlation coefficient (MCC) were calculated as below:

<!-- formula-not-decoded -->

#### Functional enrichment analysis

For GO-based enrichment analysis of differentially regulated proteins, GO annotation files were downloaded on 12 February 2025 from the Gene Ontology Resource (http://geneontology.org/) 28 . For each GO term t , we defined the following:

N = number of proteins annotated by at least one GO term. n = number of proteins annotated by GO term t .

 M = number of differentially regulated proteins annotated by at least one GO term.

 m = number of differentially regulated proteins annotated by GO term t .

Then the enrichment ratio ( E -ratio) was computed, and the p value was calculated with the hypergeometric distribution as below:

<!-- formula-not-decoded -->

#### Quantification and statistical analysis

All animals and data points were retained for analysis, and no exclusions were made. Statistical analyses were performed in GraphPad Prism 9.0. Each experiment was conducted in at least 3 independent replicates, with no predetermined sample size and no data excluded from the analyses. Most experiments were not randomized, whereas animals were randomly allocated to experimental groups. Results are reported as mean ± s.e.m. Group comparisons employed unpaired two-tailed t -test, one-way analysis of variance (ANOVA) or two-way ANOVA, considering P &lt; 0.05 as statistically significant. Final figures, schematic illustrations and figure layouts were prepared and assembled by the authors using Adobe Illustrator.

#### Reporting summary

Further information on research design is available in the Nature Portfolio Reporting Summary linked to this article.

#### Data availability

The complete molecular datasets used in this study were obtained from public multi-omics datasets available at TCGA (https://portal. gdc.cancer.gov), CPTAC (https://proteomics.cancer.gov/data-portal) and Synapse (https://www.synapse.org/). All biomedical abstracts used for model training were retrieved from PubMed (https://pubmed.ncbi. nlm.nih.gov), and additional curated annotations are provided in the supplementary tables. The RNA-seq data generated from the MPTP and α-syn PFF mouse models of Parkinson's disease have been deposited in the National Genomics Data Center (https://ngdc.cncb.ac.cn/) under accession number CRA033901 and CRA033526. The corresponding proteomics and phosphoproteomics MS/MS data are available at iProX (https://www.iprox.org/) under dataset identifier PXD065072. The complete ranked target lists for all diseases provided by XunZi are in Supplementary Table 13. All benchmarking results are publicly available via Zenodo at https://doi.org/10.5281/zenodo.17927526 (ref. 88). Source data are provided with this paper.

#### Code availability

The source code for XunZi and other custom code have been uploaded in GitHub (https://github.com/biocuckooHXH/XunZi) 89 .

#### References

1. Glass, D. J. &amp; Hall, N. A brief history of the hypothesis. Cell 134 , 378-381 (2008).
2. Tanford, C. Data and hypothesis. Science 146 , 1635-1636 (1964).
3. Ozanne, S. E. &amp; Constância, M. Mechanisms of disease: the developmental origins of disease and the role of the epigenotype. Nat. Clin. Pract. Endocrinol. Metab. 3 , 539-546 (2007).
4. Defining the scientific method. Nat. Methods 6 , 237 (2009)
5. Chang, K. et al. The Cancer Genome Atlas Pan-Cancer analysis project. Nat. Genet. 45 , 1113-1120 (2013).

6. Roth, J. et al. A description of the Clinical Proteomics Tumor Analysis Consortium (CPTAC) common data analysis pipeline. J. Proteome Res. 15 , 1023-1032 (2016).
7. De Jager, P. L. et al. A multi-omic atlas of the human frontal cortex for aging and Alzheimer's disease research. Sci. Data 5 , 180142 (2018).
8. Wang, M. et al. The Mount Sinai cohort of large-scale genomic, transcriptomic and proteomic data in Alzheimer's disease. Sci. Data 5 , 180185 (2018).
9. Greenwood, A. K. et al. The AD Knowledge Portal: a repository for multi-omic data on Alzheimer's disease and aging. Curr. Protoc. Hum. Genet. 108 , e105 (2020).
10. Piñero, J. et al. The DisGeNET knowledge platform for disease genomics: 2019 update. Nucleic Acids Res. 48 , D845-D855 (2020).
11. Schriml, L. M. et al. The Human Disease Ontology 2022 update. Nucleic Acids Res. 50 , D1255-D1261 (2021).
12. Clough, E. et al. NCBI GEO: archive for gene expression and epigenomics data sets: 23-year update. Nucleic Acids Res. 52 , D138-D144 (2023).
13. Davis, A. P. et al. Comparative Toxicogenomics Database (CTD): update 2023. Nucleic Acids Res. 51 , D1257-D1262 (2023).
14. Li, C. et al. Multimodal foundation models: from specialists to general-purpose assistants. Preprint at https://doi.org/10.48550/ arXiv.2309.10020 (2023).
15. Gao, S. et al. Empowering biomedical discovery with AI agents. Cell 187 , 6125-6151 (2024).
16. Cui, H. et al. Towards multimodal foundation models in molecular cell biology. Nature 640 , 623-633 (2025).
17. Fahrner, L. J., Chen, E., Topol, E. &amp; Rajpurkar, P. The generative era of medical AI. Cell 188 , 3648-3660 (2025).
18. Gottweis, J. et al. Accelerating scientific discovery with Co-Scientist. Nature 655 , 487-496 (2026).
19. Penadés, J. R. et al. AI mirrors experimental science to uncover a novel mechanism of gene transfer crucial to bacterial evolution. Cell 188 , 6654-6665.e2 (2025).
20. Ji, Z. et al. Survey of hallucination in natural language generation. ACM Comput. Surv. 55 , 248 (2023).
21. Farquhar, S., Kossen, J., Kuhn, L. &amp; Gal, Y. Detecting hallucinations in large language models using semantic entropy. Nature 630 , 625-630 (2024).
22. Radford, A. et al. Learning transferable visual models from natural language supervision. In Proc. 38th International Conference on Machine Learning (eds Meila, M. &amp; Zhang, T.) Vol 139, 8748-8763 (PMLR, 2021).
23. Liu, Y . et al. Sora: a review on background, technology, limitations, and opportunities of large vision models. Preprint at https://doi.org/ 10.48550/arXiv.2402.17177 (2024).
24. Sperry, R. W. Hemisphere deconnection and unity in conscious awareness. Am. Psychol. 23 , 723-733 (1968).
25. Trevarthen, C. Hemispheric modes of consciousness in the human brain. Nature 294 , 112-113 (1981).
26. Chu, Z. et al. Navigate through enigmatic labyrinth a survey of chain of thought reasoning: advances, frontiers and future. In Proc. 62nd Annual Meeting of the Association for Computational Linguistics (eds Ku, L.-W. et al.) 1173-1203 (Association for Computational Linguistics, 2024).
27. Jiang, A. Q. et al. Mistral 7B. Preprint at https://doi.org/10.48550/ arXiv.2310.06825 (2023).
28. Gene Ontology Consortium et al. The Gene Ontology Knowledgebase in 2023. Genetics 224 , iyad031 (2023).
29. Sun, Y., Sheng, D., Zhou, Z. &amp; Wu, Y. AI hallucination: towards a comprehensive classification of distorted information in artificial intelligence-generated content. Humanit. Soc. Sci. Commun. 11 , 1278 (2024).
30.  Rogers, F. B. Medical subject headings. Bull. Med. Libr. Assoc. 51 , 114-116 (1963).
31. Guo, D. et al. DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning. Nature 645 , 633-638 (2025).
32. Luo, R. et al. BioGPT: generative pre-trained transformer for biomedical text generation and mining. Brief. Bioinform. 23 , bbac409 (2022).
33. Du, H,, Li, R. &amp; Gehringer, E. Objective metrics for evaluating large language models using external data sources. Preprint at https://doi.org/10.48550/arXiv.2508.08277 (2025).
34.  Fraile Navarro, D. et al. Expert evaluation of large language models for clinical dialogue summarization. Sci. Rep. 15 , 1195 (2025).
35. Wu, Z. et al. A comprehensive survey on graph neural networks. IEEE Trans. Neural Netw. Learn. Syst. 32 , 4-24 (2021).
36.  Ittner, L. M. et al. Parkinsonism and impaired axonal transport in a mouse model of frontotemporal dementia. Proc. Natl Acad. Sci. USA 105 , 15997-16002 (2008).
37. Ivashko-Pachima, Y., Seroogy, K. B., Sharabi, Y. &amp; Gozes, I. Parkinson disease-modification encompassing rotenone and 6-hydroxydopamine neurotoxicity by the microtubule-protecting drug candidate SKIP. J. Mol. Neurosci. 71 , 1515-1524 (2021).
38. Thai, A. A., Solomon, B. J., Sequist, L. V., Gainor, J. F. &amp; Heist, R. S. Lung cancer. Lancet 398 , 535-554 (2021).
39. Wu, K.-M. et al. Neuronal FAM171A2 mediates α-synuclein fibril uptake and drives Parkinson's disease. Science 387 , 892-900 (2025).
40.  Jankovic, J. &amp; Tan, E. K. Parkinson's disease: etiopathogenesis and treatment. J. Neurol. Neurosurg. Psychiatry 91 , 795 (2020).
41. Panicker, N., Ge, P., Dawson, V. L. &amp; Dawson, T. M. The cell biology of Parkinson's disease. J. Cell Biol. 220 , e202012095 (2021).
42. Lou, Z., Minter-Dykhouse, K., Wu, X. &amp; Chen, J. MDC1 is coupled to activated CHK2 in mammalian DNA damage response pathways. Nature 421 , 957-961 (2003).
43.  Anderson, V. E. et al. CCT241533 is a potent and selective inhibitor of CHK2 that potentiates the cytotoxicity of PARP inhibitors. Cancer Res. 71 , 463-472 (2011).
44.  Chen, Y. et al. CHK2-FOXK axis promotes transcriptional control of autophagy programs. Sci. Adv. 6 , eaax5819 (2020).
45. Jennings, D. et al. Preclinical and clinical evaluation of the LRRK2 inhibitor DNL201 for Parkinson's disease. Sci. Transl. Med. 14 , eabj2658 (2022).
46.  Tolosa, E., Vila, M., Klein, C. &amp; Rascol, O. LRRK2 in Parkinson disease: challenges of clinical trials. Nat. Rev. Neurol. 16 , 97-107 (2020).
47. Singhal, K. et al. Toward expert-level medical question answering with large language models. Nat. Med. 31 , 943-950 (2025).
48.  Liu, Z. et al. MolXPT: wrapping molecules with text for generative pre-training. Preprint at https://doi.org/10.48550/ arXiv.2305.10688 (2023).
49. Wang, H., Zhou, G., Liu, S., Jiang, J.-Y. &amp; Wang, W. Drug-target interaction prediction with graph attention networks. Preprint at https://doi.org/10.48550/arXiv.2107.06099 (2021).
50.  Nguyen, T. et al. GraphDTA: predicting drug-target binding affinity with graph neural networks. Bioinformatics 37 , 1140-1147 (2021).
51. Chang, J. &amp; Zhu, S. MGNN: Moment Graph Neural Network for universal molecular potentials. npj Comput. Mater. 11 , 55 (2025).
52. Nalls, M. A. et al. Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. Lancet Neurol. 18 , 1091-1102 (2019).
53. Kisielewska, M. et al. Investigation into the neuroprotective and therapeutic potential of plant-derived Chk2 inhibitors. Int. J. Mol. Sci. 25 , 7725 (2024).

54.  Kim, J. J. et al. Multi-ancestry genome-wide association metaanalysis of Parkinson's disease. Nat. Genet. 56 , 27-36 (2024).
55. Li, X. et al. Phosphorylation-dependent 14-3-3 binding to LRRK2 is impaired by common mutations of familial Parkinson's disease. PLoS ONE 6 , e17153 (2011).
56. Chia, R. et al. Phosphorylation of LRRK2 by casein kinase 1α regulates trans-Golgi clustering via differential interaction with ARHGEF7. Nat. Commun. 5 , 5827 (2014).
57. Dzamko, N. et al. The IkappaB kinase family phosphorylates the Parkinson's disease kinase LRRK2 at Ser935 and Ser910 during toll-like receptor signaling. PLoS ONE 7 , e39132 (2012).
58. Sayers, E. W. et al. Database resources of the National Center For Biotechnology Information. Nucleic Acids Res. 50 , D20-D26 (2021).
59. Chen, S., Zhou, Y., Chen, Y. &amp; Gu, J. fastp: an ultra-fast allin-one FASTQ preprocessor. Bioinformatics 34 , i884-i890 (2018).
60.  Dobin, A. et al. STAR: ultrafast universal RNA-seq aligner. Bioinformatics 29 , 15-21 (2013).
61. Liao, Y., Smyth, G. K. &amp; Shi, W. featureCounts: an efficient general purpose program for assigning sequence reads to genomic features. Bioinformatics 30 , 923-930 (2014).
62.  Cox, J. &amp; Mann, M. MaxQuant enables high peptide identification rates, individualized p.p.b.-range mass accuracies and proteome-wide protein quantification. Nat. Biotechnol. 26 , 1367-1372 (2008).
63.  Orsburn, B. C. Proteome Discoverer-a community enhanced data processing suite for protein informatics. Proteomes 9 , 15 (2021).
64.  da Veiga Leprevost, F. et al. Philosopher: a versatile toolkit for shotgun proteomics data analysis. Nat. Methods 17 , 869-870 (2020).
65. Meier, F. et al. Parallel Accumulation-Serial Fragmentation (PASEF): multiplying sequencing speed and sensitivity by synchronized scans in a trapped ion mobility device. J. Proteome Res. 14 , 5378-5387 (2015).
66.  Bruderer, R. et al. Extending the limits of quantitative proteome profiling with data-independent acquisition and application to acetaminophen-treated three-dimensional liver microtissues. Mol. Cell. Proteomics 14 , 1400-1410 (2015).
67. Gillet, L. C. et al. Targeted data extraction of the MS/MS spectra generated by data-independent acquisition: a new concept for consistent and accurate proteome analysis. Mol. Cell. Proteomics 11 , O111.016717 (2012).
68. Liao, C.-C., Kau, Y.-C., Ting, P.-C., Tsai, S.-C. &amp; Wang, C.-J. The Effects of volume-controlled and pressure-controlled ventilation on lung mechanics, oxidative stress, and recovery in gynecologic laparoscopic surgery. J. Minim. Invasive Gynecol. 23 , 410-417 (2016).
69.  UniProt Consortium. UniProt: the Universal Protein Knowledge­ base in 2023. Nucleic Acids Res. 51 , D523-D531 (2022).
70. Oughtred, R. et al. The BioGRID database: a comprehensive biomedical resource of curated protein, genetic, and chemical interactions. Protein Sci. 30 , 187-200 (2021).
71. Razick, S., Magklaras, G. &amp; Donaldson, I. M. iRefIndex: a consolidated protein interaction database with provenance. BMC Bioinformatics 9 , 405 (2008).
72. Du, Y. et al. PINA 3.0: mining cancer interactome. Nucleic Acids Res. 49 , D1351-D1357 (2020).
73. Das, J. &amp; Yu, H. HINT: high-quality protein interactomes and their applications in understanding human disease. BMC Syst. Biol. 6 , 92 (2012).
74. Calderone, A., Castagnoli, L. &amp; Cesareni, G. mentha: a resource for browsing integrated protein-interaction networks. Nat. Methods 10 , 690-691 (2013).
75. Kotlyar, M. et al. IID 2021: towards context-specific protein interaction analyses by increased coverage, enhanced annotation and enrichment analysis. Nucleic Acids Res. 50 , D640-D647 (2021).
76. Li, T . et al. A scored human protein-protein interaction network to catalyze genomic interpretation. Nat. Methods 14 , 61-64 (2017).
77. Shah, K., Dikkala, N., Wang, X. &amp; Panigrahy, R. Causal language modeling can elicit search and reasoning capabilities on logic puzzles. Preprint at https://doi.org/10.48550/arXiv.2409.10502 (2024).
78. Beltagy, I., Lo, K. &amp; Cohan, A. SciBERT: a pretrained language model for scientific text. In Proc. 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP) (eds Inui, K. et al.) 3615-3620 (Association for Computational Linguistics, 2019).
79. Chen, K. et al. Leucine-rich repeat kinase 2 (LRRK2) inhibition upregulates microtubule-associated protein 1B to ameliorate lysosomal dysfunction and parkinsonism. MedComm 4 , e429 (2023).
80.  Yadav, S. K., Rai, S. N. &amp; Singh, S. P. Mucuna pruriens reduces inducible nitric oxide synthase expression in Parkinsonian mice model. J. Chem. Neuroanat. 80 , 1-10 (2017).
81. Lei, P. et al. Tau deficiency induces parkinsonism with dementia by impairing APP-mediated iron export. Nat. Med. 18 , 291-295 (2012).
82. Qin, J. et al. Ketogenic diet reshapes cancer metabolism through lysine β-hydroxybutyrylation. Nat. Metab. 6 , 1505-1528 (2024).
83.  Yong, X. et al. Cryo-EM structure of the BLOC-3 complex provides insights into the pathogenesis of Hermansky-Pudlak syndrome. Nat. Commun. 16 , 2967 (2025).
84.  Tang, M. et al. β-hydroxybutyrate facilitates mitochondrial-derived vesicle biogenesis and improves mitochondrial functions. Mol. Cell 85 , 1395-1410.e5 (2025).
85. Taylor, M. J., Thompson, A. M., Alhajlah, S., Tuxworth, R. I. &amp; Ahmed, Z. Inhibition of Chk2 promotes neuroprotection, axon regeneration, and functional recovery after CNS injury. Sci. Adv. 8 , eabq2611 (2022).
86. Xu, Q. et al. α-Synuclein amyloid fibril directly binds to LC3B and suppresses SQSTM1/p62-mediated selective autophagy. Cell Res. 35 , 72-75 (2025).
87. Karuppagounder, S. S. et al. The c-Abl inhibitor IkT-148009 suppresses neurodegeneration in mouse models of heritable and sporadic Parkinson's disease. Sci. Transl. Med. 15 , eabp9352 (2023).
88. Huang, X. XunZi, a brain-inspired AI biologist, reveals novel disease-modifying targets (dataset). Zenodo https://doi.org/ 10.5281/zenodo.17927526 (2025).
89. Huang, X. et al. XunZi, a brain-inspired AI biologist, reveals novel disease-modifying targets (source code). GitHub https://github.com/ biocuckooHXH/XunZi (2025).

### Acknowledgements

We acknowledge the Chinese philosopher Xunzi (c. 310-235 BCE ), renowned for his emphasis on rigorous reasoning, as the inspiration for our approach. We name this framework in his honour. We thank Q. Ma (Huazhong University of Science and Technology) for helpful discussions and C. Liu (Interdisciplinary Research Center on Biology and Chemistry, Shanghai Institute of Organic Chemistry, Chinese Academy of Sciences) for generously providing the α-syn PFFs used in this study.

#### Author contributions

D.J., Y .X. and P.L. conceived of and designed the research. F.T., J.Q. and J.W. performed the animal studies with assistance from K.C. J.Q. performed the cellular studies with assistance from L.X., L.Z. and Y. T . X.H. carried out the dataset collection, corpus curation, XunZi model training, multi-omics analysis and other computational work, with the help of and discussion with J.Q., C.Y., D.L., C.Z., M.C., Y.G., J.Z. and Y.M. D.J., Y .X., P.L., X.H., J.Q. and F. T . wrote the paper with input from all authors. All authors reviewed and approved the paper before submission.

#### Funding

This work was supported by the National Natural Science Foundation of China (32341020, 92254302, 92578201 and 32430027), the National Key R&amp;D Program of China (2022YFA1105200, 2024YFA1108500 and 2024YFC3407300), the Scientific Research Innovation Capability Support Project for Young Faculty (ZYGXQNJSKYCXNLZCXM-H14), the National Science Fund for Distinguished Young Scholars (32125012), the Wuhan Key R&amp;D Program (2025021102020384), the construction project of the Fujiang Laboratory Nuclear Medicine Artificial Intelligence Research Center (2023ZYDF074), Sichuan Science and Technology Program (2025NSFTD0028, 2025ZYD0165, 2026NSFSC1052), the Postdoctoral Fellowship Program of China Postdoctoral Science Foundation (GZB20250628, GZC20241145), the China Postdoctoral Science Foundation (2025M782729), the Postdoctor Research Fund of West China Hospital, Sichuan University (2024HXBH126), Sichuan University Interdisciplinary Innovation Fund and the Research Core Facilities for Life Science (HUST). The funders had no role in the conceptualization, design, data collection, analysis, decision to publish or preparation of the manuscript.

#### Competing interests

The authors declare no competing interests.

#### Additional information

[Extended data is available for this paper at https://doi.org/10.1038/s41551-026-01769-6.](https://doi.org/10.1038/s41551-026-01769-6)

Supplementary information The online version contains supplementary material available at https://doi.org/10.1038/s41551-026-01769-6.

Correspondence and requests for materials should be addressed to Peng Lei, Yu Xue or Da Jia.

Peer review information Nature Biomedical Engineering thanks the anonymous reviewers for their contribution to the peer review of this work.

Reprints and permissions information is available at www.nature.com/reprints.

Publisher's note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

Springer Nature or its licensor (e.g. a society or other partner) holds exclusive rights to this article under a publishing agreement with the author(s) or other rightsholder(s); author self-archiving of the accepted manuscript version of this article is solely governed by the terms of such publishing agreement and applicable law.

- © The Author(s), under exclusive licence to Springer Nature Limited 2026

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

Extended Data Fig. 1 | Four major categories of LLM-generated errors and expert-verified corrections. Typical cases illustrating different types of errors, including ( a ) unfounded fabrication, ( b ) logic errors, ( c ) factual errors and ( d ) incomplete summary, for each case, the response generated from GPT-4 (top) is compared with the expert-reviewed and corrected interpretation (bottom).

<!-- image -->

Extended Data Fig. 2 | Distribution of complete gene-disease associations across 26 MeSH disease categories. Bar chart showing the number of curated genedisease associations across 26 disease categories defined by the MeSH ontology. Categories are ranked by descending association count on a log scale.

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

Extended Data Fig. 3 | See next page for caption.

<!-- image -->

## Article

Extended Data Fig. 3 | Performance of XunZi-R and other LLMs in gene-disease classification. a Performance evaluation of XunZi-R on DisGeNET using 5-fold cross-validation compared to other LLMs. The evaluation metrics include Accuracy, Recall, Specificity, F1 Score, and MCC. b Performance evaluation of XunZi-R trained on DisGeNET with testing on an independent dataset from CTD. The evaluation metrics include Accuracy, Recall, Specificity, F1 Score, and MCC. c Performance evaluation of XunZi-R trained on CTD with testing on an independent dataset from DisGeNET. The evaluation metrics include Accuracy, Recall, Specificity, F1 Score, and MCC.

Extended Data Fig. 4 | Comparative evaluation of logical reasoning capabilities between XunZi-R and GPT-4o. a -x Radar plots showing reasoning performance across 24 MeSH disease categories, excluding neoplasms and nervous system diseases. Outer green bars indicate the recall of XunZi-R for each individual disease subtype within a category.

<!-- image -->

Extended Data Fig. 5 | See next page for caption.

<!-- image -->

### Extended Data Fig. 5 | Performance of XunZi-R and other LLMs in mechanistic

reasoning. a Comparison of BERTScore F1 values between XunZi-R and other LLMs for mechanistic interpretation generation b Comparison of BERTScore Precision values between XunZi-R and other LLMs for mechanistic interpretation generation c . Comparison of BERTScore Recall values between XunZi-R and other LLMs for mechanistic interpretation generation. d Comparison of BLEU and ROUGE scores between XunZi-R and other LLMs for mechanistic interpretation generation e BERTScore evaluation for XunZi-R trained on DisGeNET and tested on a non-overlapping dataset from CTD, comparing performance with other LLMs across Precision, Recall, and F1 score metrics. f BERTScore evaluation for XunZi-R trained on CTD and tested on a non-overlapping dataset from DisGeNET, comparing performance with other LLMs across Precision, Recall, and F1 score metrics. g Comparison of BLEU and ROUGE scores between XunZi-R and other LLMs for mechanistic interpretation generation, trained on DisGeNET and tested on an independent dataset from CTD. h Comparison of BLEU and ROUGE scores between XunZi-R and other LLMs for mechanistic interpretation generation, trained on CTD and tested on an independent dataset from DisGeNET.

<!-- image -->

Extended Data Fig. 6 | Distribution of multi-omics molecular features across cancer and neurodegenerative diseases. Stacked bar chart showing the number of genes covered by transcriptomic (blue), proteomic (green), and phosphoproteomic (orange) datasets for each disease. Cancer types are shown on the left, and neurodegenerative diseases on the right.

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

Extended Data Fig. 7 | See next page for caption.

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

Extended Data Fig. 7 | AUC and AUPR evaluation of XunZi in Pan-cancer and Neurodegenerative diseases. a AUPR comparison for pan-cancer prediction under 5-fold cross-validation b Distribution of positive samples in DisGeNET and CTD under pan-cancer by Venn diagram. c ROC curves and AUC values for pan-cancer prediction, with DisGeNET used for training and non-overlapping CTD data for testing. d AUPR values for pan-cancer prediction, with DisGeNET used for training and non-overlapping CTD data for testing. e ROC curves and AUC values for pan-cancer prediction, with CTD used for training and nonoverlapping DisGeNET data for testing. f AUPR values for pan-cancer prediction, with CTD used for training and non-overlapping DisGeNET data for testing.

g AUPR comparison for neurodegenerative disease prediction under 5-fold cross-validation. h Distribution of positive samples in DisGeNET and CTD under neurodegenerative diseases by Venn diagram. i ROC curves and AUC values for neurodegenerative disease prediction, with DisGeNET used for training and non-overlapping CTD data for testing. j AUPR values for neurodegenerative disease prediction, with DisGeNET used for training and non-overlapping CTD data for testing. k ROC curves and AUC values for neurodegenerative disease prediction, with CTD used for training and non-overlapping DisGeNET data for testing. l AUPR values for neurodegenerative disease prediction, with CTD used for training and non-overlapping DisGeNET data for testing.

Extended Data Fig. 8 | ROC performance of XunZi across different cancer types. a -o ROC curves and AUC values from fivefold cross-validation showing the performance of XunZi in identifying disease-relevant regulators across 15 cancer types.

<!-- image -->

Extended Data Fig. 9 | ROC performance of XunZi across different cancer types (continued from Extended Data Fig. 8). a -i ROC curves and AUC values from fivefold cross-validation showing the performance of XunZi in identifying disease-relevant regulators across 9 cancer types.

<!-- image -->

Extended Data Fig. 10 | ROC performance of XunZi across different neurodegenerative diseases. a -d ROC curves and AUC values from fivefold cross-validation showing the performance of XunZi in predicting functional gene relevance in Alzheimer's disease, Huntington's disease, Lewy body-related disease, and progressive supranuclear palsy.

<!-- image -->

α

α α α

α

α

α