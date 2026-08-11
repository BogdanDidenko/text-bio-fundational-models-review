# CellDuality : Unlocking Biological Reasoning in LLMs with Self-Supervised RLVR

[Yuhang Chen](https://pubmed.ncbi.nlm.nih.gov/?term=%22Chen%20Y%22[Author]) 1 , [Zhen Tan](https://pubmed.ncbi.nlm.nih.gov/?term=%22Tan%20Z%22[Author]) 2 , [Ruichen Zhang](https://pubmed.ncbi.nlm.nih.gov/?term=%22Zhang%20R%22[Author]) 1 , [Mufan Qiu](https://pubmed.ncbi.nlm.nih.gov/?term=%22Qiu%20M%22[Author]) 1 , [Tianlong Chen](https://pubmed.ncbi.nlm.nih.gov/?term=%22Chen%20T%22[Author]) 1

- Author information
- Copyright and License information

PMCID: PMC13441433 NIHMSID: NIHMS2176134 PMID: [42559559](https://pubmed.ncbi.nlm.nih.gov/42559559/)

## Abstract

Developing generalist large language models (LLMs) capable of complex biological reasoning is a central challenge in computational biology. While existing LLMs excel at predictive tasks like cell type annotation and logically-constrained problems, enabling open-ended and mechanistic reasoning remains a challenge. A promising direction is Reinforcement Learning from Verifiable Rewards (RLVR), which has been shown to significantly enhance complex reasoning in general domains like mathematics and code synthesis. However, its application in biology is hindered, as most biological outcomes are non-verifiable. For example, verifying a generated gene sequence is usually infeasible. In this paper, we introduce `CellDuality` , a self-supervised framework that enables LLM agents for robust reasoning in single-cell biology. Our framework is built on the principle of complementary task duality, a self-verification process that leverages a bidirectional reasoning loop. First, the model performs a forward reasoning task by predicting a biological outcome (e.g., a cell's response to a drug). Then, in a complementary inverse task, it must reason backward from its own prediction to reconstruct the initial conditions (e.g., the original drug perturbation). The fidelity of this reconstruction serves as an intrinsic reward signal, creating a feedback loop that enforces logical and biological consistency. We use these intrinsic rewards to align the base LLM via reinforcement learning, without requiring ground-truth verification labels. We demonstrate that `CellDuality` achieves state-of-the-art performance and provides coherent biological explanations across a diverse suite of single-cell reasoning tasks. Critically, on the challenging out-of-distribution perturbation prediction benchmark, our self-supervised approach significantly outperforms the standard fine-tuning baseline and narrows the performance gap to a supervised RLVR baseline. Our work showcases a new path toward scalable training of biological foundation models.

## 1. Introduction

Developing generalist large language models (LLMs) capable of biological reasoning is a central goal of computational biology ( [Fang et al., 2025b](#R8) ; [Istrate et al., 2025](#R11) ; [Lotfollahi et al., 2019](#R14) ). This reasoning ability involves inferring complex, mechanistic principles from cellular data ( [Fang et al., 2025b](#R8) ; [Matsumoto et al., 2025](#R17) ). This capability is paramount in single-cell biology, where understanding causal chains, such as how a cell responds to a drug, is key to therapeutic discovery ( [Fang et al., 2025a](#R7) ). However, achieving robust biological reasoning is fundamentally challenging due to the stochastic nature of cellular systems and the intricate, high-dimensional dependencies between biological entities. This complexity creates a significant hurdle for current methods, especially the foundation models ( [Hao et al., 2024](#R9) ; [Cui et al., 2024](#R5) ), which we categorize into three limitations.

First, most models are optimized for *prediction* , not *mechanistic reasoning* . Architectures like scGPT ( [Cui et al., 2024](#R5) ) and C2S-Scale ( [Rizvi et al., 2025](#R20) ) excel at learning correlational patterns for tasks like cell type annotation but are not explicitly trained to generate the coherent, explanatory steps that capture underlying biological pathways. Second, existing reasoning-aware models often operate in *logically-constrained paradigms* . For instance, Cell-o1 ( [Fang et al., 2025b](#R8) ) models a deductive puzzle-solving process rather than the open-ended, hypothesis-driven inquiry of scientific exploration. Finally, there exists a trade-off between *depth and generality* . Specialized models achieve deep reasoning in a single task, while versatile, multi-task agents like InstructCell ( [Fang et al., 2025a](#R7) ) currently lack the same level of mechanistic insight. Therefore, developing a framework that takes a step toward deep reasoning across diverse tasks remains an open challenge. Such a framework must achieve generality over two core biological themes: cell identity and cell dynamics.

A promising direction is Reinforcement Learning from Verifiable Rewards (RLVR), a paradigm that has successfully enhanced LLMs' general reasoning ability, such as mathematics and code synthesis ( [Shao et al., 2024](#R22) ; [Rafailov et al., 2023](#R19) ; [Lee et al., 2023](#R12) ). However, its application in biology is severely limited because most biological reasoning tasks are inherently non-verifiable. For example, a specific gene sequence output of conditional cell generation has no single correct version for a given cell type, making simple verification infeasible. This data-dependency fundamentally constrains the training of more ambitious, unified models on the open-ended, cause-and-effect scenarios that would foster biological understanding.

To address this challenge, we introduce `CellDuality` , an agent for open-ended biological reasoning. It operates within a structured framework of four core tasks designed to span the fundamental biological themes of cell identity and cell dynamics (details in [Sec. 3.1](#S6) ). Crucially, `CellDuality` is trained via a self-supervised paradigm inspired by DuPO ( [She et al., 2025](#R24) ), built on the principle of *Complementary Task Duality* . This framework leverages a bidirectional reasoning loop to generate its own supervisory signals: first, the model performs a forward reasoning task (e.g., predicting a cell's response to a drug); then, in a complementary inverse task, given generated results and known input conditions, it will reason backward to reconstruct the unknown input conditions. The reward is then determined by directly comparing the reconstructed input with the original. This consistency score becomes the intrinsic reward signal, compelling the model to produce forward predictions that are accurate and logically reversible, without needing ground-truth labels for the predictions themselves.

We implement this principle in a two-stage training paradigm. An initial Supervised Fine-Tuning (SFT) stage on a small, curated set of examples, containing both forward and inverse reasoning traces. This stage serves to cold-start the model, teaching it the language and format of biological reasoning. This is followed by a large-scale, self-supervised Reinforcement Learning (RL) stage, where the model is aligned using these intrinsic rewards on vast unlabeled data. This stage refines the model's ability to produce outputs that are not only stylistically correct but also biologically and logically coherent.

Empirical evaluations demonstrate that `CellDuality` , despite being trained without any ground-truth verification during its RL phase, substantially outperforms its SFT-only counterpart. Critically, on the challenging OOD perturbation benchmark, our self-supervised approach closes 35-56% of the performance gap to a fully-supervised RLVR model that was trained with ground-truth rewards. This showcases the sample efficiency and generalization potential of our framework. Our main contributions are:

- We propose a structured framework that organizes complex biological inquiry into four core reasoning tasks spanning both cell identity and cell dynamics. This provides a promising step toward developing and evaluating agents with broader capabilities in single-cell biology.
- We introduce the principle of *Complementary Task Duality* , a new mechanism for generating annotation-free rewards. This framework incentivizes LLMs to learn the intrinsic mechanistic consistency of biological processes by rewarding the fidelity of a bidirectional reasoning loop, eliminating the need for ground-truth labels during the RL phase.
- We show empirically that the generalist model significantly outperforms standard SFT baselines and narrows the performance gap to a fully-supervised oracle model on the challenging out-of-distribution perturbation prediction benchmark.

## 2. Related Work

### Foundation Models in Single-Cell Biology.

Foundation models are revolutionizing single-cell biology by learning representations from massive transcriptomic data ( [Cui et al., 2024](#R5) ; [Theodoris et al., 2023](#R27) ). The field has rapidly progressed from models focused on predictive tasks, such as scGPT ( [Cui et al., 2024](#R5) ) for annotation and C2S-Scale ( [Rizvi et al., 2025](#R20) ) for multi-task generality, to those attempting explicit reasoning. However, these reasoning-aware models often operate in narrow paradigms; for instance, Cell-o1 ( [Fang et al., 2025b](#R8) ) frames reasoning as a logically-constrained puzzle, while agentic frameworks like ESCARGOT ( [Matsumoto et al., 2025](#R17) ) rely on external knowledge graphs. A key challenge remains in developing a single, generalist agent that can perform open-ended, mechanistic reasoning directly from cellular data. Our work addresses this gap, aiming for the generality of models like InstructCell ( [Fang et al., 2025a](#R7) ) but with a training objective that explicitly fosters deep, intrinsic reasoning.

### Reinforcement Learning from Verifiable Rewards .

Reinforcement learning is increasingly used to refine LLMs beyond standard SFT, with paradigms evolving to reduce reliance on external supervision ( [Ouyang et al., 2022](#R18) ; [Shao et al., 2024](#R22) ). A particularly scalable paradigm is Reinforcement Learning from Verifiable Rewards (RLVR), which replaces subjective feedback ( [Bai et al., 2022](#R2) ) with objective, ground-truth-based rewards from deterministic verifiers ( [Shao et al., 2024](#R22) ). However, the prerequisite of a verifiable output severely limits RLVR's application in biology, where outcomes are inherently stochastic. Recent work has sought to address this by generating self-supervised rewards through task duality. For instance, the DuPO ( [She et al., 2025](#R24) ) framework introduced a generalized duality for non-invertible tasks, such as mathematical reasoning, by reconstructing input components to create a reward signal. Inspired by DuPO, our work adapts this duality principle to the unique challenges of biology (detailed in [Sec. 3.2](#S7) ). We introduce Complementary Task Duality to generate intrinsic, self-verifiable rewards from the internal consistency of cellular processes, thus extending the RLVR paradigm to the non-verifiable biological domain.

## 3. Methodology

This section delineates the methodology for training our single-cell biological reasoning model. An overview of our entire framework is presented in [Figure 1](#F1) . We first define the concepts and the task formulation. We then introduce the generalized framework for self-supervision. Finally, we detail our training pipeline: an initial cold start stage, followed by a self-supervised Reinforcement Learning stage that uses our duality principle to enhance the model for deeper reasoning.

An overview of the CellDuality framework. Single-cell expression profiles are first converted into ranked "Cell Sentences," which are inputs to our task formulation covering four reasoning tasks. A high-quality CoT dataset is generated using a teacher model and Reject Sampling. This dataset is used for a Stage 1 SFT cold start of an LLaMA model. The model is then further aligned in Stage 2 via self-supervised RL (GRPO) on large-scale unlabeled data. The core innovation is our duality-based reward mechanism, which replaces the need for external Ground Truth by rewarding the consistency between a Primal Task and its complementary Dual Task.

<!-- image -->

### 3.1. Preliminaries and Task Formulation

We denote the LLM policy as π θ , parameterized by θ . Let 𝒱 be the global vocabulary of all considered gene names. Our work addresses a structured set of four core single-cell reasoning tasks, organized into a 2x2 matrix spanning two fundamental biological themes: *Cell Identity* and *Cell Dynamics* . The core data structures for these tasks are defined as follows:

- **Cell Representation** : A cell c = { g 1 , g 2 , ... , g K } is represented as an descending order sequence of its top K expressed genes, where each gene g i ∈ 𝒱 .
- **Perturbation** : A perturbation p is a structured tuple describing an intervention, e.g., p = { operation , target } , where operation ∈ {knockdown, overexpression} and target ∈ 𝒱 .
- **Cell Type and Sensitivity Labels** : A cell type t , is a categorical label from a predefined set 𝒯 . Similarly, a drug sensitivity label, s , is a categorical label from a set 𝒮 .

All inputs to the LLM are constructed as textual prompts x that combine these components. The model's output is a textual response y , generated autoregressively according to the policy y ∼ π θ ( ⋅ ∣ x ) . A response may include a reasoning trace z and a final answer a , i.e., y = { z , a } .

### 3.2. The Principle of Complementary Task Duality

A primary obstacle to applying Reinforcement Learning (RL) to the four tasks defined above is the absence of a scalable reward source. In single-cell biology, obtaining ground-truth signals from experiments is prohibitively expensive and slow. Our work is motivated by a **central question:** Can we generate a reliable, intrinsic reward signal directly from the structure of these biological problems themselves, thus enabling RL without external supervision?

To achieve this, inspired by DuPO ( [She et al., 2025](#R24) ), we introduce a self-supervised reward generation framework. Adapting the duality principle from well-structured domains (e.g., mathematics) to biology is non-trivial: biological outputs are inherently stochastic and high-dimensional, requiring the design of domain-specific task formulations, such as conditional gene inpainting ( [Sec. 3.4](#S14) ), to produce stable reward signals. The core idea is to reframe a single biological question into a pair of mutually-verifying tasks, a primal task and a complementary dual task. This creates an internal logic loop that the model must satisfy, providing a natural source for an RL reward.

### **Definition 3.1 (Complementary Task Duality).**

Let the input space 𝒳 of a primal task 𝒯 p be decomposed into disjoint subspaces: 𝒳 k (known components) and 𝒳 u (unknown components), such that 𝒳 = 𝒳 u ∪ 𝒳 u . The *primal task* 𝒯 p is a mapping from 𝒯 p : 𝒳 → 𝒴 . Its *complementary dual task* 𝒯 c d is a mapping that leverages the primal output y and the known component x k to reconstruct the unknown component x ^ u :

| 𝒯  c  d  :  (  y  ,  x  k  )  ↦  x  ^  u  .   |
|-----------------------------------------------|

Pair ( 𝒯 p , 𝒯 c d ) forms a *generalized dual pair* if it satisfies the *complementary consistency principle* :

| ∀  x  ∈  𝒳  ,  y  =  𝒯  p  (  x  )  :  d  (  x  u  ,  𝒯  c  d  (  y  ,  x  k  )  )  ≤  ϵ  ,   |
|-----------------------------------------------------------------------------------------------|

where d ( ⋅ , ⋅ ) : 𝒳 u × 𝒳 u is a domain-specific distance metric, and ϵ ≥ 0 is a tolerance threshold.

The power of this framework lies in its ability to transform an unsupervised problem into a self-verifying one. The consistency principle defined above provides the mechanism to generate rewards: the fidelity of the dual task's reconstruction, d ( x u , x ^ u ) , serves as a direct, intrinsic measure of the logical and biological coherence of the primal task's output y . This approach elegantly sidesteps the challenges of classical dual learning (irreversibility and asymmetry) by leveraging the known component x k as a contextual anchor, ensuring the dual task is well-posed.

### 3.3. Training Stage 1: Supervised Fine-Tuning for Capability Cold-Start

Before RL Training, we first initialize the base LLM with foundational biological knowledge and reasoning patterns through Supervised Fine-Tuning (SFT). This essential cold-start phase ensures the model can effectively engage with the complex, self-supervised tasks in the subsequent alignment stage. The process involves two key steps: generating a high-quality Chain-of-Thought dataset, and then using it to train the model.

#### 3.3.1. Chain-of-Thought Reasoning Dataset Generation

We construct a comprehensive SFT dataset, 𝒟 SFT , by leveraging powerful teacher models (e.g., GPT-4o, Gemini 2.5 Pro) to generate Chain-of-Thought (CoT) reasoning traces. A critical aspect of our approach is that 𝒟 SFT must equip our model with capabilities for both the primal (forward) reasoning and the complementary dual (inverse) reasoning required in our RL stage. Therefore, we generate and curate distinct data subsets for each direction.

##### Primal Task SFT Data.

For each of our four core tasks, we generate primal task data. Given an input prompt x i , we prompt a teacher model π teacher to generate N candidate responses { y i , k = ( z i , k , a i , k ) } k = 1 N . We then apply task-specific filtering to select high-quality instances for our primal SFT set, 𝒟 SFT primal .

- **For Classification Tasks (Annotation &amp; Sensitivity)** : We use a strict *Rejection Sampling* protocol. A candidate y i , k is accepted if its final answer a i , k exactly matches the ground-truth label a i ∗ . We define an indicator for correctness as ϵ i , k = I ( a i , k = a i ∗ ) . The accepted set for prompt x i is { y i , k ∣ ϵ i , k = 1 } . This ensures all training examples are factually correct.
- **For Generative Tasks (Cell &amp; Response Generation)** : As no single, unique ground-truth sequence exists for these tasks, a simple exact match is infeasible. Instead, we adopt a *Rank-Aware Filtering* protocol. For each prompt x i with a corresponding ground-truth cell sequence a i ∗ , the teacher model generates a candidate response ( z i , a i ). The candidate is accepted into 𝒟 SFT only if the generated cell sequence a i demonstrates high fidelity to the ground truth in terms of both gene overlap and expression ranking. We quantify this using our proposed Rank-Weighted Jaccard Similarity metric ( [Eq. 3](#FD5) ). A candidate is accepted only if its similarity score exceeds a predefined threshold.

##### Dual Task SFT Data.

To explicitly teach the model the inverse reasoning required for our duality framework, we construct a corresponding dual task SFT set, 𝒟 SFT dual . For each instance in our curated primal set, we formulate its complementary dual problem.

- For a primal instance ( x = ( x k , x u ) , y ∗ ), we construct a dual prompt x dual = ( y ∗ , x k ) . The ground-truth answer for this dual task is the original unknown component, y dual ∗ = x u .
- For example, for a perturbation response instance where x k = c pre , x u = p , and y ∗ = c post ∗ , the dual SFT sample would be: prompt ( c post ∗ , c pre ) paired with the ground-truth answer p .

The teacher model is then prompted to generate CoT reasoning for these dual problems. The final SFT dataset is the union 𝒟 SFT = 𝒟 SFT primal ∩ 𝒟 SFT dual . This hybrid strategy ensures the model is proficient in both forward and inverse reasoning before entering the RL stage.

#### 3.3.2. Supervised Fine-tuning Objective

The model is then trained on 𝒟 SFT by minimizing the standard negative log-likelihood loss ℒ SFT ( θ ) over the complete reasoning trajectories:

| ℒ  SFT  (  θ  )  =  −  E  (  x  i  ,  y  i  ∗  )  ∼  𝒟  SFT  [  ∑  j  =  1  ∣  y  i  ∗  ∣  log  π  θ  (  y  i  ,  j  ∗  ∣  x  i  ,  y  i  ,  &lt;  j  ∗  )  ]  .   | (1)   |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|

The resulting model, π SFT , possesses the baseline capabilities required for the subsequent self-supervised alignment.

### 3.4. Stage 2: Self-Supervised Duality-Guided Reinforcement Learning

This stage constitutes the core of our self-supervised methodology. We refine the capabilities of the SFT-initialized model, π SFT , by aligning it with the principle of complementary consistency. This is achieved through a Reinforcement Learning (RL) framework that operates on a large, unlabeled dataset 𝒟 RL and is guided by intrinsic rewards, eliminating the need for any ground-truth data.

#### 3.4.1. Self-Supervised Reward Generation

The cornerstone of our alignment stage is the generation of intrinsic rewards derived from the complementary duality principle. For any prompt x = ( x k , u u ) and a model-generated primal output y , we compute a reward by executing the complementary dual task and measuring its reconstruction fidelity. We employ two types of rewards, categorical and sequence-based, tailored to the nature of our core tasks.

##### Categorical Rewards from Inverse Task Consistency.

For generative tasks such as Perturbation Response Generation and Conditional Cell Generation, the duality provides a clean, categorical reward signal. In both cases, the primal task generates a high-dimensional cell sequence ( c post or c ), and the complementary dual task attempts to reconstruct a categorical input label (the sensitivity s or the cell type t ). The reward is a binary signal based on the exact reconstruction of this label:

| r  (  y  ∣  x  )  =  I  (  x  ^  u  =  x  u  )  ,   | (2)   |
|-----------------------------------------------------|-------|

where x u is the original categorical input (e.g., t ) and x ^ u is its reconstruction (e.g., t ^ ). This reward directly measures the logical consistency of the generated output: a biologically plausible cell sequence should unambiguously encode the conditions that generated it.

##### Continuous Rewards from Conditional Inpainting.

For classification tasks such as Cell Type Annotation and Drug Sensitivity Prediction, where the primal output is a low-information label, we design a reward based on a conditional gene inpainting objective. Here, the input cell sequence is artificially decomposed into an observed part c obs and a hidden part c hid , which serves as the unknown component x u . The dual task is to reconstruct c ^ hid conditioned on both the observed genes c obs and the model's predicted primal label ( t ^ or s ^ ). The reward is a continuous score reflecting the quality of this reconstruction: r ( t ^ ∣ c ) = RWJS ( c hid , c ^ hid ) . The Rank-Weighted Jaccard Similarity (RWJS) extends the standard Jaccard index by weighting each gene by its reciprocal rank, w ( g , c ) = 1 ∕ rank ( g , c ) , so that higher-expressed genes contribute more. For a ground-truth sequence c ∗ and a generated sequence c gen , it is defined as:

| RWJS  (  c  ∗  ,  c  gen  )  =  ∑  g  ∈  S  ∗  ∩  S  gen  w  (  g  ,  c  ∗  )  +  w  (  g  ,  c  gen  )  2  ∑  g  ∈  S  ∗  w  (  g  ,  c  ∗  )  +  ∑  g  ∈  S  gen  ∖  S  ∗  w  (  g  ,  c  gen  )  ,   | (3)   |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|

where S ∗ = Set ( c ∗ ) and S gen = Set ( c gen ) . RWJS ranges from 0 (no overlap) to 1 (identical), providing a biologically meaningful measure that prioritizes high-expression genes. This reward incentivizes the model to base its classification on a deep understanding of the cell's underlying gene signature, as a correct label should provide the necessary context for accurate gene inpainting.

#### 3.4.2. Policy Optimization with GRPO

We optimize the policy π θ to maximize the expected self-supervised reward 𝒥 ( θ ) = E x ∼ 𝒟 RL [ r ( y ∣ x ) ] . We employ Group Relative Policy Optimization (GRPO), a memory-efficient and stable critic-free RL algorithm. The optimization follows an iterative, online process: for each prompt, the current policy π θ generates a group of G candidate responses, each of which is then assigned a self-supervised reward based on its dual-task performance. This group of responses and rewards is then used to update the policy as follows.

##### Advantage Estimation.

For each prompt, after generating a group of G responses and their corresponding rewards { r k } k = 1 G , we compute the advantage for each candidate. This is achieved by normalizing the rewards relative to the group's performance, which serves as an empirical baseline, thus obviating the need for a separate value function:

| A  k  =  r  k  −  mean  (  {  r  j  }  j  =  1  G  )  std  (  {  r  j  }  j  =  1  G  )  +  ϵ  .   | (4)   |
|----------------------------------------------------------------------------------------------------|-------|

##### Objective Function.

The policy is updated by maximizing the GRPO objective, which includes a clipped surrogate objective to stabilize training and a KL penalty to prevent large deviations from a reference policy π ref (typically the initial SFT model π SFT ):

| 𝒥  GRPO  (  θ  )  =  E  [  min  (  ρ  t  (  θ  )  A  t  ,  clip  (  ρ  t  (  θ  )  ,  1  −  ϵ  c  ,  1  +  ϵ  c  )  A  t  )  −  β  D  KL  (  π  θ  ∥  π  ref  )  ]  ,   | (5)   |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|

where ρ t ( θ ) = π θ ( y t ∣ x ) ∕ π θ old ( y t ∣ x ) is the probability ratio, A t is the advantage at token t (in our case, A k is applied to all tokens of response k , ϵ c is the clipping ratio, and β is the KL coefficient. This iterative, multi-task training process progressively refines the model's ability to generate biologically coherent and logically consistent responses.

## 4. Experiment

### 4.1. Experimental Setup

#### Tasks and Datasets.

Our evaluation is centered around the four core single-cell reasoning tasks introduced in our framework. To ensure fair and direct comparison with state-of-the-art models, we adopt the exact datasets and train/test splits used in seminal works, including C2S-Scale ( [Rizvi et al., 2025](#R20) ) and InstructCell ( [Fang et al., 2025a](#R7) ). Our training strategy involves fine-tuning a single base model on a designated primary training set for each task theme, and then evaluating its performance on both in-distribution (ID) and out-of-distribution (OOD) test sets.

- Cell Identity Tasks (Annotation &amp; Generation):
    - **Training Dataset:** To build a robust multi-task model for cell identity, we construct a mixed training dataset by combining the training splits of four diverse public benchmarks: [He-2020](#R10) -Liver ( [He et al., 2020](#R10) ), Segerstolpe-2016 ( [Segerstolpe et al., 2016](#R21) ), Xin-2016 ( [Xin et al., 2016](#R28) ), and Human Immune Tissue Dataset ( [Domínguez Conde et al., 2022](#R6) ). This mixed dataset serves as the sole source of supervision for our model on all identity tasks.
    - **ID Test Set:** For the cell type annotation task, we use the held-out test splits of the three datasets included in our training mix (He-2020-Liver, Segerstolpe-2016, Xin-2016). For cell generation, we use the held-out test splits of Human Immune Datasets.
    - **OOD Test Set:** We use two datasets entirely unseen during training: Ma-2020 ( [Ma et al., 2020](#R16) ) and Bastidas-Ponce-2019 ( [Bastidas-Ponce et al., 2019](#R3) ).
- Cell Dynamics Tasks (Sensitivity Prediction &amp; Response Generation):
    - **Training Dataset:** We construct a comprehensive mixed training dataset by combining three distinct perturbation benchmarks: the L1000 dataset ( [Subramanian et al., 2017](#R26) ), which covers two human drug response datasets, [GSE149383](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE149383) (Lung) ( [Aissa et al., 2021](#R1) ) and [GSE117872](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE117872) (Oral Cavity) ( [Sharma et al., 2018](#R23) ). This diverse dataset, containing examples for both response generation and sensitivity classification, serves as the sole source of supervision for our model on all dynamics-related tasks.
    - **ID Test Sets:** The held-out test splits of the two datasets explicitly included for the classification task: [GSE149383](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE149383) and [GSE117872](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE117872) .
    - **OOD Test Sets:** We use two benchmarks entirely unseen during training. For cross-species classification, we use the complete [GSE110894](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE110894) (Mouse Bone Marrow) dataset ( [Bell et al., 2019](#R4) ). For generative causal reasoning, we use the OOD splits of the sci-Plex3 Human Perturbation dataset ( [Srivatsan et al., 2020](#R25) ).

#### Evaluation Metrics.

- For Classification Tasks (Cell Type Annotation, Drug Sensitivity): We report *Accuracy* as the primary metric. We also include the *Macro F1-score* to account for class imbalance.
- For Generative Tasks (Conditional Generation, Perturbation Response): For Perturbation Response Generation, we follow C2S-Scale ( [Rizvi et al., 2025](#R20) ) and report distribution-based metrics (scFID and MMD) calculated in a pre-trained embedding space (scGPT ( [Cui et al., 2024](#R5) )) to assess the quality and realism of generated cell populations. For Conditional Cell Generation, we follow Cell2Sentence ( [LeVine et al., 2024](#R13) ) and report Gromov-Wasserstein (GW) Distance and k-NN Accuracy. The k-NN classifier is evaluated with multiple neighbor values ( k ∈ { 3 , 5 , 10 , 25 } ).

#### Baseline Models.

We benchmark `CellDuality` against a comprehensive set of state-of-the-art models, with all performance metrics cited directly from the original publications for fair comparison. For classification tasks (Annotation and Sensitivity), we compare against domain-specific foundation models such as **scGPT** ( [Cui et al., 2024](#R5) ) and **Geneformer** ( [Theodoris et al., 2023](#R27) ), as well as LLM-based agents like **InstructCell** ( [Fang et al., 2025a](#R7) ). For generative tasks (Cell and Response Generation), baselines include specialized generative models like **scGen** ( [Lotfollahi et al., 2019](#R14) ) and **scDiffusion** ( [Luo et al., 2024](#R15) ), and the powerful LLM-based framework **C2S-Scale** ( [Rizvi et al., 2025](#R20) ).

#### Implementation Details.

Our `CellDuality` model is based on the Llama-3.2-3B architecture. The SFT stage is conducted for 3 epochs with a learning rate of 1 e − 5 . The subsequent self-supervised RL alignment is performed using GRPO with a group size of G = 8 , a train batch size of 512, a mini-batch size of 32, and is run for 200 optimization steps. All experiments are conducted on 8x A6000 GPUs. All our scores are shown as mean ± std over 5 runs.

### 4.2. Main Results

Across all four reasoning tasks, our self-supervised framework, `Cell-Duality` , demonstrates highly competitive performance against a wide range of state-of-the-art baselines. As detailed in [Tables 2](#T2) through [5](#T5) , our multi-task model, trained on mixed datasets, consistently matches or surpasses specialist models that were trained on individual benchmarks. This is particularly evident in the classification tasks (Cell Type Annotation and Drug Sensitivity), where `CellDuality` shows robust generalization to out-of-distribution and even cross-species datasets.

#### Table 2:

Performance comparison on the Cell Type Annotation task. Baselines are trained on each dataset individually. We report Accuracy (Acc.) and Macro F1-score (F1) for all five benchmarks, differentiating between ID and OOD evaluation for our model.

| Model                    | In-Distribution (ID) Evaluation   | In-Distribution (ID) Evaluation   | In-Distribution (ID) Evaluation   | In-Distribution (ID) Evaluation   | In-Distribution (ID) Evaluation   | In-Distribution (ID) Evaluation   | Out-of-Distribution (OOD) Evaluation   | Out-of-Distribution (OOD) Evaluation   | Out-of-Distribution (OOD) Evaluation   | Out-of-Distribution (OOD) Evaluation   |
|--------------------------|-----------------------------------|-----------------------------------|-----------------------------------|-----------------------------------|-----------------------------------|-----------------------------------|----------------------------------------|----------------------------------------|----------------------------------------|----------------------------------------|
| Model                    | He-2020-Liver                     | He-2020-Liver                     | Segerstolpe-2016                  | Segerstolpe-2016                  | Xin-2016                          | Xin-2016                          | Ma-2020                                | Ma-2020                                | Bastidas-Ponce-2019                    | Bastidas-Ponce-2019                    |
|                          | Acc. (%)                          | F1 (%)                            | Acc. (%)                          | F1 (%)                            | Acc. (%)                          | F1 (%)                            | Acc. (%)                               | F1 (%)                                 | Acc. (%)                               | F1 (%)                                 |
| scBERT                   | 95.28                             | 94.08                             | 99.52                             | 99.64                             | 99.25                             | 98.79                             | 82.92                                  | 81.73                                  | 86.67                                  | 79.60                                  |
| scGPT                    | 94.88                             | 91.75                             | 98.09                             | 97.82                             | 99.10                             | 98.40                             | 82.84                                  | 79.40                                  | **91.43**                              | 87.01                                  |
| Geneformer               | 96.06                             | 92.57                             | 99.52                             | 99.49                             | **99.70**                         | **99.39**                         | **85.79**                              | **84.89**                              | 88.50                                  | 83.81                                  |
| Cell2Sentence            | 94.88                             | 94.42                             | 99.52                             | 99.64                             | 99.35                             | 98.77                             | 82.40                                  | 81.05                                  | 80.59                                  | 76.82                                  |
| InstructCell-instruct    | 96.06                             | 95.24                             | **100.00**                        | **100.00**                        | 99.30                             | 98.89                             | 85.59                                  | 84.56                                  | 91.10                                  | **88.69**                              |
| `CellDuality` (SFT-only) | 94.83 ±0.21                       | 94.67 ±0.18                       | 98.76 ±0.08                       | 98.73 ±0.09                       | 99.45 ±0.12                       | 99.01 ±0.15                       | 80.22 ±0.34                            | 74.95 ±0.41                            | 72.87 ±0.28                            | 57.24 ±0.33                            |
| `CellDuality`            | **96.34**  ±0.19                  | **95.41**  ±0.16                  | 99.81  ±0.07                      | 99.78  ±0.08                      | 99.52  ±0.11                      | 99.08  ±0.13                      | 82.03 ±0.32                            | 81.78 ±0.39                            | 88.45 ±0.26                            | 78.12 ±0.31                            |

[Open in a new tab](table/T2)

#### Table 5:

Performance on Conditional Cell Generation on the Human Immune dataset (InDistribution). Baseline results are cited from Cell2Sentence ( [LeVine et al., 2024](#R13) ). k-NN Accuracy is reported for multiple values of k.

| Model                    | k-NN Accuracy (%) ↑   | k-NN Accuracy (%) ↑   | k-NN Accuracy (%) ↑   | k-NN Accuracy (%) ↑   | GW Distance (↓)    |
|--------------------------|-----------------------|-----------------------|-----------------------|-----------------------|--------------------|
| Model                    | k=3                   | k=5                   | k=10                  | k=25                  | GW Distance (↓)    |
| scVI                     | 24.36 ±0.0062         | 24.00 ±0.0064         | 24.25 ±0.0034         | 23.48 ±0.0032         | 302.13 ±0.9338     |
| scGen                    | 23.76 ±0.0112         | 23.30 ±0.0093         | 23.77 ±0.0053         | 23.35 ±0.0041         | 315.95 ±1.2431     |
| scDiffusion              | 23.35 ±0.0125         | 22.88 ±0.0111         | 23.68 ±0.0067         | 23.06 ±0.0049         | 72.02 ±0.3937      |
| scGPT                    | 18.38 ±0.0086         | 17.88 ±0.0169         | 18.11 ±0.0149         | 18.82 ±0.0071         | 2989.81 ±4.9229    |
| Cell2Sentence-160M       | 25.88  ±0.0061        | 25.65  ±0.0060        | **27.46**  ±0.0073    | **27.15**  ±0.0070    | **54.30**  ±0.3410 |
| `CellDuality` (SFT-only) | 24.92 ±0.0058         | 24.71 ±0.0055         | 25.83 ±0.0062         | 25.49 ±0.0059         | 63.87 ±0.0421      |
| `CellDuality`            | **26.34**  ±0.0056    | **25.92**  ±0.0053    | 26.21  ±0.0060        | 25.98  ±0.0057        | 61.45  ±0.0408     |

[Open in a new tab](table/T5)

The most significant impact of our self-supervised approach is observed in the generative tasks requiring deep mechanistic reasoning. For Perturbation Response Generation, the duality-guided RL stage provides a substantial performance boost over the already strong SFT baseline. Critically, our self-supervised model successfully narrows the performance gap to a fully-supervised oracle that requires ground-truth labels for alignment, proving the efficacy of our annotation-free strategy. While our model also demonstrates strong performance on Conditional Cell Generation by outperforming most classical and deep learning-based generative models, its primary strength lies in its ability to learn the intrinsic, mechanistic consistency of biological processes, showcasing a new path toward scalable and robust scientific reasoning agents. The central value of our self-supervised approach lies in eliminating the dependence on expensive, often unavailable ground-truth labels during the RL alignment phase. Our framework achieves competitive performance without any such supervision, providing a practical and scalable path to strong reasoning capabilities in data-scarce biological domains.

### 4.3. Ablation Study

#### Self-Supervised vs. Ground-Truth Supervised RL

To rigorously quantify the efficacy of our self-supervised alignment strategy, we conduct a head-to-head comparison against a standard supervised RL approach. We evaluate three key models on their respective in-distribution test sets: (1) the SFT-only baseline, (2) a supervised RL oracle trained with ground-truth rewards, and (3) our self-supervised `CellDuality` model. As shown in [Table 6](#T6) , our self-supervised RL approach consistently and significantly boosts performance over the SFT-only baseline across all tasks. Critically, our annotation-free method substantially narrows the performance gap to the fully-supervised oracle, and even surpasses the oracle's Macro F1-score on the He-2020-Liver annotation task, suggesting it learns more robust decision boundaries.

##### Table 6:

Core ablation study comparing Self-Supervised RL against a Ground-Truth Supervised oracle. All models are initialized from the same SFT checkpoint and evaluated on their respective **in-distribution (ID)** test sets.

| Method Configuration          | He-2020-Liver    | He-2020-Liver    | [GSE149383](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE149383) (Lung)   |                  | sci-Plex3         | sci-Plex3         |
|-------------------------------|------------------|------------------|------------------------------------------------------------------------------------|------------------|-------------------|-------------------|
| Method Configuration          | Acc. (↑)         | F1 (↑)           | Acc. (↑)                                                                           | F1 (↑)           | scFID (↓)         | MMD (↓)           |
| Llama-3.2-3B-Instruct         | 22.45 ±1.23      | 52.82 ±1.45      | 29.67 ±0.89                                                                        | 61.34 ±1.12      | -                 | -                 |
| SFT-only                      | 95.83 ±0.21      | 94.67 ±0.18      | 98.91 ±0.15                                                                        | 98.89 ±0.16      | 0.045 ±0.003      | 0.028 ±0.002      |
| RL with Ground-Truth          | **97.21**  ±0.16 | 94.85  ±0.14     | **99.34**  ±0.12                                                                   | **99.31**  ±0.13 | **0.025**  ±0.001 | **0.012**  ±0.001 |
| **Ours (Self-Supervised RL)** | 96.34  ±0.19     | **95.41**  ±0.16 | 99.12  ±0.13                                                                       | 99.10  ±0.14     | 0.038  ±0.002     | 0.019  ±0.001     |

[Open in a new tab](table/T6)

## 5. Conclusion

We introduced `CellDuality` , an agent that learns complex biological reasoning through a novel self-supervised framework. Our core contribution, the principle of complementary task duality, enables reinforcement learning alignment on non-verifiable single-cell tasks by generating intrinsic rewards from a bidirectional reasoning loop. Trained via our sample-efficient, two-stage paradigm, `CellDuality` achieves state-of-the-art performance across four distinct reasoning tasks, providing coherent biological explanations. Critically, our self-supervised approach demonstrates its efficacy by narrowing the performance gap to a supervised RLVR baseline. This work presents a promising step toward scalable foundation models in biology, offering a new paradigm that learns to reason from the intrinsic logical structure of scientific problems, rather than from external labels.

### Limitations

Our framework is validated on four representative transcriptomic tasks and has not yet been extended to other omics modalities such as ATAC-seq or proteomics. The cell sentence representation discards absolute expression magnitudes, trading encoding precision for compatibility with off-the-shelf LLMs. While our duality-based reward enforces logical consistency, it does not guarantee biological correctness. Mutually consistent yet biologically implausible predictions remain possible, and direct interpretability evaluation at the pathway level is left for future work. The RL gains are most pronounced for generative tasks and comparatively modest for classification tasks where SFT alone already achieves strong performance. Finally, our experiments use a 3B-parameter model, which may limit reasoning depth. Exploring the scaling behavior of our approach is an important future direction.

The plots show the moving average of (a) the categorical accuracy-based reward for generative tasks and (b) the continuous RWJS-based reward for classification tasks.

<!-- image -->

## Table 1:

Task Formulation for Single-Cell Reasoning.

| Theme             | Classification Tasks                                                | Generative Tasks                                                            |
|-------------------|---------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **Cell Identity** | **Cell Type Annotation** (Input: Cell, Output: Label)               | **Conditional Cell Generation** (Input: Label, Output: Cell)                |
| **Cell Dynamics** | **Drug Sensitivity Prediction** (Input: Cell + Drug, Output: Label) | **Perturbation Response Generation** (Input: Cell + Drug, Output: New Cell) |

[Open in a new tab](table/T1)

## Table 3:

Performance comparison on the Drug Sensitivity Classification task. Baselines are trained on each dataset individually. We report Accuracy (Acc.) and Macro F1-score (F1).

| Model                    | In-Distribution (ID) Evaluation                                                        | In-Distribution (ID) Evaluation   | In-Distribution (ID) Evaluation                                                        | In-Distribution (ID) Evaluation   | Out-of-Distribution (OOD) Evaluation                                                   | Out-of-Distribution (OOD) Evaluation   |
|--------------------------|----------------------------------------------------------------------------------------|-----------------------------------|----------------------------------------------------------------------------------------|-----------------------------------|----------------------------------------------------------------------------------------|----------------------------------------|
| Model                    | [GSE149383](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE149383) (Human Lung) |                                   | [GSE117872](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE117872) (Human Oral) |                                   | [GSE110894](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE110894) (Mouse Bone) |                                        |
|                          | Acc. (%)                                                                               | F1 (%)                            | Acc. (%)                                                                               | F1 (%)                            | Acc. (%)                                                                               | F1 (%)                                 |
| scBERT                   | **99.56**                                                                              | **99.56**                         | 95.42                                                                                  | 96.01                             | 95.80                                                                                  | 95.79                                  |
| scGPT                    | 97.79                                                                                  | 97.79                             | 82.44                                                                                  | 84.76                             | 95.80                                                                                  | 95.79                                  |
| Geneformer               | 98.23                                                                                  | 98.23                             | 94.66                                                                                  | 95.27                             | 93.01                                                                                  | 92.91                                  |
| Cell2Sentence            | 93.36                                                                                  | 93.36                             | 90.84                                                                                  | 90.72                             | 95.10                                                                                  | 95.08                                  |
| InstructCell-instruct    | 97.35                                                                                  | 97.34                             | **100.00**                                                                             | **100.00**                        | **97.20**                                                                              | **97.19**                              |
| `CellDuality` (SFT-only) | 98.91 ±0.15                                                                            | 98.89 ±0.16                       | 96.78 ±0.22                                                                            | 97.12 ±0.19                       | 96.45  ±0.18                                                                           | 96.42  ±0.20                           |
| `CellDuality`            | 99.12  ±0.13                                                                           | 99.10  ±0.14                      | 97.23  ±0.20                                                                           | 97.58  ±0.17                      | 96.12 ±0.21                                                                            | 96.08 ±0.23                            |

[Open in a new tab](table/T3)

## Table 4:

Performance on Perturbation Response Generation (sci-Plex3 benchmark). Our model was trained on a separate perturbation dataset, while baselines were trained on the in-distribution splits of sci-Plex3. Lower scores are better for distribution-based metrics.

| Model                    | Supervision Type    | scFID (↓L)    | MMD (↓)       | Wasserstein (↓)   |
|--------------------------|---------------------|---------------|---------------|-------------------|
| scGen                    | Supervised          | 0.95          | 1.05          | 0.98              |
| CellOT                   | Supervised          | 0.88          | 1.03          | 0.95              |
| scGPT                    | Supervised          | 0.29          | 0.42          | 0.54              |
| C2S-Scale 1B (SFT)       | Supervised          | **0.02**      | **0.01**      | 0.21              |
| C2S-Scale (GRPO w/ GT)   | **Ground-Truth RL** | **0.02**      | **0.01**      | **0.21**          |
| `CellDuality` (SFT-only) | Supervised          | 0.045 ±0.003  | 0.028 ±0.002  | 0.267 ±0.012      |
| `CellDuality`            | **Self-Supervised** | 0.038  ±0.002 | 0.019  ±0.001 | 0.245  ±0.011     |

[Open in a new tab](table/T4)

## Acknowledgements

This research was partially funded by the National Institutes of Health (NIH) under award 1R01EB03710101. The views and conclusions contained in this document are those of the authors and should not be interpreted as representing the official policies, either expressed or implied, of the NIH. This research was also partially supported by the Amazon Research Award.

## Footnotes

The Use of Large Language Models

We utilized Google's Gemini Pro 2.5 as a writing assistant in the preparation of this manuscript. Its function was strictly limited to language refinement tasks, such as enhancing clarity, correcting grammar, and rephrasing sentences to improve readability within an academic context. All scientific content, including the core ideas, experimental design, and interpretation of results, was generated exclusively by the human authors.

## References

1. Aissa Alexandre F, Islam Abul BMMK, Ariss Majd M, Go Cammille C, Rader Alexandra E, Conrardy Ryan D, Gajda Alexa M, Rubio-Perez Carlota, Valyi-Nagy Klara, Pasquinelli Mary, et al. Single-cell transcriptional changes associated with drug tolerance and response to combination therapies in cancer. Nature communications, 12(1):1628, 2021. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Nature%20communications&title=Single-cell%20transcriptional%20changes%20associated%20with%20drug%20tolerance%20and%20response%20to%20combination%20therapies%20in%20cancer&author=Alexandre%20F%20Aissa&author=Abul%20BMMK%20Islam&author=Majd%20M%20Ariss&author=Cammille%20C%20Go&author=Alexandra%20E%20Rader&volume=12&issue=1&publication_year=2021&pages=1628&) ]
2. Bai Yuntao, Kadavath Saurav, Kundu Sandipan, Askell Amanda, Kernion Jackson, Jones Andy, Chen Anna, Goldie Anna, Mirhoseini Azalia, McKinnon Cameron, et al. Constitutional ai: Harmlessness from ai feedback. arXiv preprint arXiv:2212.08073, 2022. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=arXiv%20preprint%20arXiv:2212.08073&title=Constitutional%20ai:%20Harmlessness%20from%20ai%20feedback&author=Yuntao%20Bai&author=Saurav%20Kadavath&author=Sandipan%20Kundu&author=Amanda%20Askell&author=Jackson%20Kernion&publication_year=2022&) ]
3. Bastidas-Ponce Aimée, Tritschler Sophie, Dony Leander, Scheibner Katharina, Tarquis-Medina Marta, Salinno Ciro, Schirge Silvia, Burtscher Ingo, Böttcher Anika, Theis Fabian J, et al. Comprehensive single cell mrna profiling reveals a detailed roadmap for pancreatic endocrinogenesis. Development, 146(12):dev173849, 2019. [ [DOI](https://doi.org/10.1242/dev.173849) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/31160421/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Development&title=Comprehensive%20single%20cell%20mrna%20profiling%20reveals%20a%20detailed%20roadmap%20for%20pancreatic%20endocrinogenesis&author=Aim%C3%A9e%20Bastidas-Ponce&author=Sophie%20Tritschler&author=Leander%20Dony&author=Katharina%20Scheibner&author=Marta%20Tarquis-Medina&volume=146&issue=12&publication_year=2019&pages=dev173849&pmid=31160421&doi=10.1242/dev.173849&) ]
4. Bell Charles C, Fennell Katie A, Chan Yih-Chih, Rambow Florian, Yeung Miriam M, Vassiliadis Dane, Lara Luis, Yeh Paul, Martelotto Luciano G, Rogiers Aljosja, et al. Targeting enhancer switching overcomes non-genetic drug resistance in acute myeloid leukaemia. Nature communications, 10(1):2723, 2019. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Nature%20communications&title=Targeting%20enhancer%20switching%20overcomes%20non-genetic%20drug%20resistance%20in%20acute%20myeloid%20leukaemia&author=Charles%20C%20Bell&author=Katie%20A%20Fennell&author=Yih-Chih%20Chan&author=Florian%20Rambow&author=Miriam%20M%20Yeung&volume=10&issue=1&publication_year=2019&pages=2723&) ]
5. Cui Haotian, Wang Chloe, Maan Hassaan, Pang Kuan, Luo Fengning, Duan Nan, and Wang Bo. scgpt: toward building a foundation model for single-cell multi-omics using generative ai. Nature Methods, pp. 1-11, 2024. [ [DOI](https://doi.org/10.1038/s41592-023-02158-6) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/38212549/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Nature%20Methods&title=scgpt:%20toward%20building%20a%20foundation%20model%20for%20single-cell%20multi-omics%20using%20generative%20ai&author=Haotian%20Cui&author=Chloe%20Wang&author=Hassaan%20Maan&author=Kuan%20Pang&author=Fengning%20Luo&publication_year=2024&pages=1-11&pmid=38212549&doi=10.1038/s41592-023-02158-6&) ]
6. Domínguez Conde C, Xu Chao, Jarvis Louie B, Rainbow Daniel B, Wells Sara B, Gomes Tamir, Howlett SK, Suchanek O, Polanski K, King HW, et al. Cross-tissue immune cell analysis reveals tissue-specific features in humans. Science, 376(6594):eabl5197, 2022. [ [DOI](https://doi.org/10.1126/science.abl5197) ] [ [PMC free article](/articles/PMC7612735) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/35549406/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Science&title=Cross-tissue%20immune%20cell%20analysis%20reveals%20tissue-specific%20features%20in%20humans&author=C%20Dom%C3%ADnguez%20Conde&author=Chao%20Xu&author=Louie%20B%20Jarvis&author=Daniel%20B%20Rainbow&author=Sara%20B%20Wells&volume=376&issue=6594&publication_year=2022&pages=eabl5197&pmid=35549406&doi=10.1126/science.abl5197&) ]
7. Fang Yin, Deng Xinle, Liu Kangwei, Zhang Ningyu, Qian Jingyang, Yang Penghui, Fan Xiaohui, and Chen Huajun. A multi-modal ai copilot for single-cell analysis with instruction following. arXiv preprint arXiv:2501.08187, 2025a. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=arXiv%20preprint%20arXiv:2501.08187&title=A%20multi-modal%20ai%20copilot%20for%20single-cell%20analysis%20with%20instruction%20following&author=Yin%20Fang&author=Xinle%20Deng&author=Kangwei%20Liu&author=Ningyu%20Zhang&author=Jingyang%20Qian&publication_year=2025a&) ]
8. Fang Yin, Jin Qiao, Xiong Guangzhi, Jin Bowen, Zhong Xianrui, Ouyang Siru, Zhang Aidong, Han Jiawei, and Lu Zhiyong. Cell-o1: Training llms to solve single-cell reasoning puzzles with reinforcement learning. arXiv preprint arXiv:2506.02911, 2025b. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=arXiv%20preprint%20arXiv:2506.02911&title=Cell-o1:%20Training%20llms%20to%20solve%20single-cell%20reasoning%20puzzles%20with%20reinforcement%20learning&author=Yin%20Fang&author=Qiao%20Jin&author=Guangzhi%20Xiong&author=Bowen%20Jin&author=Xianrui%20Zhong&publication_year=2025b&) ]
9. Hao Minsheng, Gong Jing, Zeng Xin, Liu Chiming, Guo Yucheng, Cheng Xingyi, Wang Taifeng, Ma Jianzhu, Zhang Xuegong, and Song Le. Large-scale foundation model on single-cell transcriptomics. Nature Methods, pp. 1-11, 2024. [ [DOI](https://doi.org/10.1038/s41592-023-02158-6) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/38212549/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Nature%20Methods&title=Large-scale%20foundation%20model%20on%20single-cell%20transcriptomics&author=Minsheng%20Hao&author=Jing%20Gong&author=Xin%20Zeng&author=Chiming%20Liu&author=Yucheng%20Guo&publication_year=2024&pages=1-11&pmid=38212549&doi=10.1038/s41592-023-02158-6&) ]
10. He Shuai, Wang Lin-He, Liu Yang, Li Yi-Qi, Chen Hai-Tian, Xu Jing-Hong, Peng Wan, Lin Guo-Wang, Wei Pan-Pan, Li Bo, et al. Single-cell transcriptome profiling of an adult human cell atlas of 15 major organs. Genome biology, 21:1-34, 2020. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Genome%20biology&title=Single-cell%20transcriptome%20profiling%20of%20an%20adult%20human%20cell%20atlas%20of%2015%20major%20organs&author=Shuai%20He&author=Lin-He%20Wang&author=Yang%20Liu&author=Yi-Qi%20Li&author=Hai-Tian%20Chen&volume=21&publication_year=2020&pages=1-34&) ]
11. Istrate Ana-Maria, Milletari Fausto, Castrotorres Fabrizio, Tomczak Jakub M, Torkar Michaela, Li Donghui, and Karaletsos Theofanis. rbio1-training scientific reasoning llms with biological world models as soft verifiers. bioRxiv, pp. 2025-08, 2025. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=bioRxiv&title=rbio1-training%20scientific%20reasoning%20llms%20with%20biological%20world%20models%20as%20soft%20verifiers&author=Ana-Maria%20Istrate&author=Fausto%20Milletari&author=Fabrizio%20Castrotorres&author=Jakub%20M%20Tomczak&author=Michaela%20Torkar&publication_year=2025&pages=2025-08&) ]
12. Lee Harrison, Phatale Samrat, Mansoor Hassan, Lu Kellie Ren, Mesnard Thomas, Ferret Johan, Bishop Colton, Hall Ethan, Carbune Victor, and Rastogi Abhinav. Rlaif: Scaling reinforcement learning from human feedback with ai feedback. 2023. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Rlaif:%20Scaling%20reinforcement%20learning%20from%20human%20feedback%20with%20ai%20feedback&author=Harrison%20Lee&author=Samrat%20Phatale&author=Hassan%20Mansoor&author=Kellie%20Ren%20Lu&author=Thomas%20Mesnard&publication_year=2023&) ]
13. LeVine Daniel, Rizvi Syed Asad, Lévy Sacha, Pallikkavaliyaveetil Nazreen, Zhang David, Chen Xingyu, Ghadermarzi Sina, Wu Ruiming, Zheng Zihe, Vrkic Ivan, Zhong Anna, Raskin Daphne, Han Insu, de Oliveira Fonseca Antonio Henrique, Caro Josue Ortega, Karbasi Amin, Dhodapkar Rahul Madhav, and van Dijk David. Cell2sentence: Teaching large language models the language of biology. In ICML. [OpenReview.net](http://openreview.net/) , 2024. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=ICML&title=Cell2sentence:%20Teaching%20large%20language%20models%20the%20language%20of%20biology&author=Daniel%20LeVine&author=Syed%20Asad%20Rizvi&author=Sacha%20L%C3%A9vy&author=Nazreen%20Pallikkavaliyaveetil&author=David%20Zhang&publication_year=2024&) ]
14. Lotfollahi Mohammad, Alexander Wolf F, and Theis Fabian J. scgen predicts single-cell perturbation responses. Nature methods, 16(8):715-721, 2019. [ [DOI](https://doi.org/10.1038/s41592-019-0494-8) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/31363220/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Nature%20methods&title=scgen%20predicts%20single-cell%20perturbation%20responses&author=Mohammad%20Lotfollahi&author=F%20Alexander%20Wolf&author=Fabian%20J%20Theis&volume=16&issue=8&publication_year=2019&pages=715-721&pmid=31363220&doi=10.1038/s41592-019-0494-8&) ]
15. Luo Erpai, Hao Minsheng, Wei Lei, and Zhang Xuegong. scdiffusion: conditional generation of high-quality single-cell data using diffusion model. Bioinformatics, 40(9):btae518, 2024. [ [DOI](https://doi.org/10.1093/bioinformatics/btae518) ] [ [PMC free article](/articles/PMC11368386) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/39171840/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Bioinformatics&title=scdiffusion:%20conditional%20generation%20of%20high-quality%20single-cell%20data%20using%20diffusion%20model&author=Erpai%20Luo&author=Minsheng%20Hao&author=Lei%20Wei&author=Xuegong%20Zhang&volume=40&issue=9&publication_year=2024&pages=btae518&pmid=39171840&doi=10.1093/bioinformatics/btae518&) ]
16. Ma Sai, Zhang Bing, LaFave Lindsay M, Earl Andrew S, Chiang Zachary, Hu Yan, Ding Jiarui, Brack Alison, Kartha Vinay K, Tay Tristan, et al. Chromatin potential identified by shared single-cell profiling of rna and chromatin. Cell, 183(4):1103-1116, 2020. [ [DOI](https://doi.org/10.1016/j.cell.2020.09.056) ] [ [PMC free article](/articles/PMC7669735) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/33098772/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Cell&title=Chromatin%20potential%20identified%20by%20shared%20single-cell%20profiling%20of%20rna%20and%20chromatin&author=Sai%20Ma&author=Bing%20Zhang&author=Lindsay%20M%20LaFave&author=Andrew%20S%20Earl&author=Zachary%20Chiang&volume=183&issue=4&publication_year=2020&pages=1103-1116&pmid=33098772&doi=10.1016/j.cell.2020.09.056&) ]
17. Matsumoto Nicholas, Choi Hyunjun, Moran Jay, Hernandez Miguel E, Venkatesan Mythreye, Li Xi, Chang Jui-Hsuan, Wang Paul, and Moore Jason H. Escargot: an ai agent leveraging large language models, dynamic graph of thoughts, and biomedical knowledge graphs for enhanced reasoning. Bioinformatics, 41(2):btaf031, 2025. [ [DOI](https://doi.org/10.1093/bioinformatics/btaf031) ] [ [PMC free article](/articles/PMC11796095) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/39842860/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Bioinformatics&title=Escargot:%20an%20ai%20agent%20leveraging%20large%20language%20models,%20dynamic%20graph%20of%20thoughts,%20and%20biomedical%20knowledge%20graphs%20for%20enhanced%20reasoning&author=Nicholas%20Matsumoto&author=Hyunjun%20Choi&author=Jay%20Moran&author=Miguel%20E%20Hernandez&author=Mythreye%20Venkatesan&volume=41&issue=2&publication_year=2025&pages=btaf031&pmid=39842860&doi=10.1093/bioinformatics/btaf031&) ]
18. Ouyang Long, Wu Jeffrey, Jiang Xu, Almeida Diogo, Wainwright Carroll L., Mishkin Pamela, Zhang Chong, Agarwal Sandhini, Slama Katarina, Ray Alex, Schulman John, Hilton Jacob, Kelton Fraser, Miller Luke, Simens Maddie, Askell Amanda, Welinder Peter, Christiano Paul F., Leike Jan, and Lowe Ryan. Training language models to follow instructions with human feedback. In NeurIPS, 2022. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=NeurIPS&title=Training%20language%20models%20to%20follow%20instructions%20with%20human%20feedback&author=Long%20Ouyang&author=Jeffrey%20Wu&author=Xu%20Jiang&author=Diogo%20Almeida&author=Carroll%20L.%20Wainwright&publication_year=2022&) ]
19. Rafailov Rafael, Sharma Archit, Mitchell Eric, Manning Christopher D, Ermon Stefano, and Finn Chelsea. Direct preference optimization: Your language model is secretly a reward model. Advances in neural information processing systems, 36:53728-53741, 2023. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Advances%20in%20neural%20information%20processing%20systems&title=Direct%20preference%20optimization:%20Your%20language%20model%20is%20secretly%20a%20reward%20model&author=Rafael%20Rafailov&author=Archit%20Sharma&author=Eric%20Mitchell&author=Christopher%20D%20Manning&author=Stefano%20Ermon&volume=36&publication_year=2023&pages=53728-53741&) ]
20. Rizvi Syed Asad, Levine Daniel, Patel Aakash, Zhang Shiyang, Wang Eric, He Sizhuang, Zhang David, Tang Cerise, Lyu Zhuoyang, Darji Rayyan, et al. Scaling large language models for nextgeneration single-cell analysis. bioRxiv, pp. 2025-04, 2025. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=bioRxiv&title=Scaling%20large%20language%20models%20for%20nextgeneration%20single-cell%20analysis&author=Syed%20Asad%20Rizvi&author=Daniel%20Levine&author=Aakash%20Patel&author=Shiyang%20Zhang&author=Eric%20Wang&publication_year=2025&pages=2025-04&) ]
21. Segerstolpe Åsa, Palasantza Athanasia, Eliasson Pernilla, Andersson Eva-Marie, Andréasson Anne-Christine, Sun Xiaoyan, Picelli Simone, Sabirsh Alan, Clausen Maryam, Bjursell Magnus K, et al. Single-cell transcriptome profiling of human pancreatic islets in health and type 2 diabetes. Cell metabolism, 24(4):593-607, 2016. [ [DOI](https://doi.org/10.1016/j.cmet.2016.08.020) ] [ [PMC free article](/articles/PMC5069352) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/27667667/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Cell%20metabolism&title=Single-cell%20transcriptome%20profiling%20of%20human%20pancreatic%20islets%20in%20health%20and%20type%202%20diabetes&author=%C3%85sa%20Segerstolpe&author=Athanasia%20Palasantza&author=Pernilla%20Eliasson&author=Eva-Marie%20Andersson&author=Anne-Christine%20Andr%C3%A9asson&volume=24&issue=4&publication_year=2016&pages=593-607&pmid=27667667&doi=10.1016/j.cmet.2016.08.020&) ]
22. Shao Zhihong, Wang Peiyi, Zhu Qihao, Xu Runxin, Song Junxiao, Bi Xiao, Zhang Haowei, Zhang Mingchuan, Li YK, Wu Yang, et al. Deepseekmath: Pushing the limits of mathematical reasoning in open language models. arXiv preprint arXiv:2402.03300, 2024. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=arXiv%20preprint%20arXiv:2402.03300&title=Deepseekmath:%20Pushing%20the%20limits%20of%20mathematical%20reasoning%20in%20open%20language%20models&author=Zhihong%20Shao&author=Peiyi%20Wang&author=Qihao%20Zhu&author=Runxin%20Xu&author=Junxiao%20Song&publication_year=2024&) ]
23. Sharma Ankur, Cao Elaine Yiqun, Kumar Vibhor, Zhang Xiaoqian, Leong Hui Sun, Wong Angeline Mei Lin, Ramakrishnan Neeraja, Hakimullah Muhammad, Vivian Teo Hui Min, Chong Fui Teen, et al. Longitudinal single-cell rna sequencing of patient-derived primary cells reveals drug-induced infidelity in stem cell hierarchy. Nature communications, 9(1):4931, 2018. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Nature%20communications&title=Longitudinal%20single-cell%20rna%20sequencing%20of%20patient-derived%20primary%20cells%20reveals%20drug-induced%20infidelity%20in%20stem%20cell%20hierarchy&author=Ankur%20Sharma&author=Elaine%20Yiqun%20Cao&author=Vibhor%20Kumar&author=Xiaoqian%20Zhang&author=Hui%20Sun%20Leong&volume=9&issue=1&publication_year=2018&pages=4931&) ]
24. She Shuaijie, Bao Yu, Lu Yu, Xu Lu, Li Tao, Zhu Wenhao, Huang Shujian, Cheng Shanbo, Lu Lu, and Wang Yuxuan. Dupo: Enabling reliable llm self-verification via dual preference optimization. arXiv preprint arXiv:2508.14460, 2025. [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=arXiv%20preprint%20arXiv:2508.14460&title=Dupo:%20Enabling%20reliable%20llm%20self-verification%20via%20dual%20preference%20optimization&author=Shuaijie%20She&author=Yu%20Bao&author=Yu%20Lu&author=Lu%20Xu&author=Tao%20Li&publication_year=2025&) ]
25. Srivatsan Sanjay R, McFaline-Figueroa José L, Ramani Vijay, Saunders Lauren, Cao Junyue, Packer Jonathan, Pliner Hannah A, Jackson Dana L, Daza Riza M, Christiansen Lena, et al. Massively multiplex chemical transcriptomics at single-cell resolution. Science, 367(6473):45-51, 2020. [ [DOI](https://doi.org/10.1126/science.aax6234) ] [ [PMC free article](/articles/PMC7289078) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/31806696/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Science&title=Massively%20multiplex%20chemical%20transcriptomics%20at%20single-cell%20resolution&author=Sanjay%20R%20Srivatsan&author=Jos%C3%A9%20L%20McFaline-Figueroa&author=Vijay%20Ramani&author=Lauren%20Saunders&author=Junyue%20Cao&volume=367&issue=6473&publication_year=2020&pages=45-51&pmid=31806696&doi=10.1126/science.aax6234&) ]
26. Subramanian Aravind, Narayan Rajiv, Corsello Steven M, Peck David D, Natoli Ted E, Lu Xiaodong, Gould Joshua, Davis John F, Tubelli Andrew A, Asiedu Jacob K, et al. A next generation connectivity map: L1000 platform and the first 1,000,000 profiles. Cell, 171(6):1437-1452, 2017. [ [DOI](https://doi.org/10.1016/j.cell.2017.10.049) ] [ [PMC free article](/articles/PMC5990023) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/29195078/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Cell&title=A%20next%20generation%20connectivity%20map:%20L1000%20platform%20and%20the%20first%201,000,000%20profiles&author=Aravind%20Subramanian&author=Rajiv%20Narayan&author=Steven%20M%20Corsello&author=David%20D%20Peck&author=Ted%20E%20Natoli&volume=171&issue=6&publication_year=2017&pages=1437-1452&pmid=29195078&doi=10.1016/j.cell.2017.10.049&) ]
27. Theodoris Christina V, Xiao Ling, Chopra Anant, Chaffin Mark D, Al Sayed Zeina R, Hill Matthew C, Mantineo Helene, Brydon Elizabeth M, Zeng Zexian, Liu X Shirley, et al. Transfer learning enables predictions in network biology. Nature, 618(7965):616-624, 2023. [ [DOI](https://doi.org/10.1038/s41586-023-06139-9) ] [ [PMC free article](/articles/PMC10949956) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/37258680/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Nature&title=Transfer%20learning%20enables%20predictions%20in%20network%20biology&author=Christina%20V%20Theodoris&author=Ling%20Xiao&author=Anant%20Chopra&author=Mark%20D%20Chaffin&author=Zeina%20R%20Al%20Sayed&volume=618&issue=7965&publication_year=2023&pages=616-624&pmid=37258680&doi=10.1038/s41586-023-06139-9&) ]
28. Xin Yurong, Kim Jinrang, Okamoto Haruka, Ni Min, Wei Yi, Adler Christina, Murphy Andrew J, Yancopoulos George D, Lin Calvin, and Gromada Jesper. Rna sequencing of single human islet cells reveals type 2 diabetes genes. Cell metabolism, 24(4):608-615, 2016. [ [DOI](https://doi.org/10.1016/j.cmet.2016.08.018) ] [ [PubMed](https://pubmed.ncbi.nlm.nih.gov/27667665/) ] [ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Cell%20metabolism&title=Rna%20sequencing%20of%20single%20human%20islet%20cells%20reveals%20type%202%20diabetes%20genes&author=Yurong%20Xin&author=Jinrang%20Kim&author=Haruka%20Okamoto&author=Min%20Ni&author=Yi%20Wei&volume=24&issue=4&publication_year=2016&pages=608-615&pmid=27667665&doi=10.1016/j.cmet.2016.08.018&) ]

Close

<!-- image -->

## ACTIONS

- [PDF (635.7 KB)](pdf/nihms-2176134.pdf)
Download PDF icon

<!-- image -->
- Cite
Cite icon

<!-- image -->
- Collections
- Permalink
Permalink icon

<!-- image -->

## RESOURCES

### Similar articles

### Cited by other articles

### Links to NCBI Databases

Back to Top

back to top icon

<!-- image -->