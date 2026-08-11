# Miniaturizing and modifying natural proteins with Raygun

- [Kapil Devkota](#auth-Kapil-Devkota-Aff1) [1](#Aff1) [na1](#na1) ,
- [Daichi Shonai](#auth-Daichi-Shonai-Aff2) [2](#Aff2) [na1](#na1) ,
- [Joey Mao](#auth-Joey-Mao-Aff2) [ORCID: orcid.org/0000-0001-5202-2648](https://orcid.org/0000-0001-5202-2648) [2](#Aff2) ,
- [Young Su Ko](#auth-Young_Su-Ko-Aff3) [ORCID: orcid.org/0009-0003-6004-6350](https://orcid.org/0009-0003-6004-6350) [3](#Aff3) ,
- [Wei Wang](#auth-Wei-Wang-Aff3) [ORCID: orcid.org/0000-0003-4377-5060](https://orcid.org/0000-0003-4377-5060) [3](#Aff3) ,
- [Scott Soderling](#auth-Scott-Soderling-Aff2) [ORCID: orcid.org/0000-0001-7808-197X](https://orcid.org/0000-0001-7808-197X) [2](#Aff2) &amp;
- ...
- [Rohit Singh](#auth-Rohit-Singh-Aff1-Aff2) [ORCID: orcid.org/0000-0002-4084-7340](https://orcid.org/0000-0002-4084-7340) [1](#Aff1) , [2](#Aff2)

Show authors

[*Nature*](/) ( 2026 ) [Cite this article](#citeas)

[Save article](/articles/s41586-026-10842-8/save-research?_csrf=WNPEXr-v93xUx-QQ1PpHVjqmIkYaChNX)

[View saved research](/saved-research)

- 42k Accesses
- 72 Altmetric
- [Metrics details](/articles/s41586-026-10842-8/metrics)

## Abstract

Proteins have evolved over billions of years through coordinated substitutions, insertions and deletions, yet computational protein design cannot fully replicate nature's ability to engineer new proteins from existing templates. Protein language models [1](#ref-CR1) , [2](#ref-CR2) , [3](/articles/s41586-026-10842-8#ref-CR3) generate informative per-residue representations, but harnessing them for large-scale, function-preserving sequence modifications has remained beyond reach. Here we introduce Raygun, a generative artificial intelligence framework that enables miniaturization, modification and augmentation of proteins, using a probabilistic encoding of protein sequences constructed from language model embeddings. Our key conceptual advance is to encode each protein not as a sequence of variable length in high-dimensional space, but as a probability distribution in fixed dimensions, making proteins of any length directly commensurable. Controlled by just two parameters governing substitutions and length changes, Raygun can shrink proteins by 10-25% (sometimes more than 50%), expand them beyond their natural size, and introduce extensive sequence diversity, all while preserving predicted structural integrity and functional sites. In cell-based validation, Raygun miniaturized fluorescent proteins (2 shorter than 96% of fluorescent proteins in FPbase) and TurboID, a synthetic biotin ligase that has been widely adopted for proteomics. It also expanded epidermal growth factor (EGF), generating variants with higher EGFR-binding affinity than the wild type. These results show that protein function can be faithfully captured in a length-agnostic representation, enabling the kind of coordinated, large-scale sequence modifications that characterize natural protein evolution.

### Similar content being viewed by others

<!-- image -->

### [Learning functional properties of proteins with language models](https://www.nature.com/articles/s42256-022-00457-9?fromPaywallRec=false)

Article 21 March 2022

<!-- image -->

### [Large language models generate functional protein sequences across diverse families](https://www.nature.com/articles/s41587-022-01618-2?fromPaywallRec=false)

Article 26 January 2023

<!-- image -->

### [Protein engineering using variational free energy approximation](https://www.nature.com/articles/s41467-024-54814-w?fromPaywallRec=false)

Article Open access 01 December 2024

### Explore related subjects

Discover the latest articles and news in related subjects.

- [Protein design](/subjects/protein-design)
- [Machine learning](/subjects/machine-learning)

## Main

Protein design has recently achieved major advances, particularly in de novo creation of proteins tailored to specific functions or structures [4](#ref-CR4) , [5](#ref-CR5) , [6](#ref-CR6) , [7](#ref-CR7) , [8](/articles/s41586-026-10842-8#ref-CR8) . Yet, evolution demonstrates an alternative strategy: building upon existing proteins-an approach that we call template-guided design (Fig. [1a-c](/articles/s41586-026-10842-8#Fig1) ). Like renovating a building rather than constructing from scratch, this strategy enables protein miniaturization, re-engineering of sensors and reporters while preserving function, and adaptation of gene payloads for viral delivery constraints. Current template-based methods rely mainly on substitutions, and become ineffective as changes become extensive: 25 substitution sites alone yield 10 32 possibilities, rendering computational prediction impractical. More fundamentally, natural evolution generates new proteins not only through substitutions but also via insertions and deletions (indels). Modifying proteins without indels is akin to renovating a building without the ability to add or remove entire rooms, yet no existing method can leverage such changes at scale while preserving the core structure of a protein. A design approach that could manage both combinatorial substitutions and large-scale insertions and deletions would vastly expand the universe of proteins derivable from a single template.

Fig. 1: Description of the Raygun model.

<!-- image -->

Protein language models (PLMs) encode proteins as rich, per-residue representations learned from evolutionary data [1](/articles/s41586-026-10842-8#ref-CR1) , [2](/articles/s41586-026-10842-8#ref-CR2) , [9](#ref-CR9) , [10](#ref-CR10) , [11](/articles/s41586-026-10842-8#ref-CR11) . These embeddings capture local and global context at each residue, and have powered predictions of protein interactions, structures, and functional properties [12](#ref-CR12) , [13](#ref-CR13) , [14](/articles/s41586-026-10842-8#ref-CR14) . From a design standpoint, PLM embeddings provide high-fidelity, computationally tractable representations: for point substitutions, sampling near a residue's embedding already generates function-preserving variants [15](/articles/s41586-026-10842-8#ref-CR15) . Bidirectional conversions between sequence and embedding spaces are now accurate enough that design operations can be performed entirely in the structurally aware embedding space. Here we use PLMs for template-guided design by reducing sequence-space design to embedding-space operations. However, PLM embeddings scale with sequence length, making representations of differently sized proteins incompatible. Our key insight is to represent each protein as a probability distribution in fixed dimensions, rather than a sequence of points in high-dimensional space. This renders proteins of any length directly comparable, enabling single-shot generation of diverse candidates without iterative refinement.

We introduce Raygun, a generative framework that implements this approach (Fig. [1](/articles/s41586-026-10842-8#Fig1) ). An encoder-decoder architecture, Raygun takes three inputs: a template sequence, a noise parameter controlling substitution rate and a target length controlling indels. We show that Raygun preserves predicted structure while generating miniaturized, modified and enlarged protein variants, enabling design possibilities that are inaccessible to existing methods. Applied to fluorescent proteins, we generated candidates with shorter sequences than 96% of known fluorescent proteins, with 6 out of 8 exhibiting fluorescence. Designed miniaturized variants of TurboID, a synthetic biotin ligase, showed ligase activity; enlarged variants of EGF achieved higher EGFR-binding affinity than wild type. These results demonstrate that protein function can be faithfully represented independent of sequence length, suggesting that the evolutionary capacity for coordinated insertions, deletions and substitutions can be computationally recapitulated from learned sequence representations.

## Proteins as probability distributions

PLMs encode proteins as variable-length embeddings derived from evolutionary data. We use ESM-2 (Evolutionary Scale Modeling 2), with 650 million parameters, for sequence-to-embedding transformation. For the reverse mapping, from embeddings to sequences, we trained a neural network, achieving over 99% validation accuracy; others report similarly high performance [16](/articles/s41586-026-10842-8#ref-CR16) , [17](/articles/s41586-026-10842-8#ref-CR17) . These bidirectional transformations enable design in embedding space while maintaining a clear path back to realizable sequences.

The critical challenge is that PLM embeddings have variable dimensionality: a protein of *n* residues maps to *n* high-dimensional vectors. This incompatibility prevents direct comparison across proteins of different lengths, rendering indel-based design intractable. However, PLM embeddings are statistically redundant: nearby residues encode overlapping contextual information, so contiguous stretches of the embedding can be summarized without significant information loss. We exploit this redundancy by representing each protein not as a set of points in embedding space but as a probability distribution in fixed dimensions, making proteins of any length directly comparable and enabling generation at arbitrary target lengths.

Specifically, we partition each protein's embedding into *K* = 50 contiguous stretches of residues (blocks), where the size of each block scales with the protein length (for example, 10 residues per block for a 500-residue template). By the central limit theorem, averaging the embedding vectors within each block yields values that approximate a multivariate Gaussian distribution [18](/articles/s41586-026-10842-8#ref-CR18) , [19](/articles/s41586-026-10842-8#ref-CR19) (Extended Data Fig. [1](/articles/s41586-026-10842-8#Fig5) ). We chose *K* = 50 after comparison with *K* = 25 (Extended Data Fig. [2](/articles/s41586-026-10842-8#Fig6) ). These block-level distributions collectively represent the full protein in a fixed 64,000-dimensional space (50 × 1,280), regardless of the original length. Crucially, the resulting Gaussian can be sampled directly, making the representation tractable for generation: by resampling from the template's distribution at different target lengths, we generate candidates of any length while preserving the structural principles encoded in the template.

Unlike diffusion-based methods [4](/articles/s41586-026-10842-8#ref-CR4) , [20](#ref-CR20) , [21](#ref-CR21) , [22](/articles/s41586-026-10842-8#ref-CR22) , which require iterative denoising, our fixed-length representation enables single-shot generation: the decoder acts as a one-shot denoiser, mapping a single noisy sample from the template's distribution directly to a candidate sequence. The user specifies noise (controlling substitution rate) and target length (controlling indels). Generation takes 0.3 s per iteration on an NVIDIA A100 graphics processing unit, approximately 100-fold faster than diffusion-based de novo approaches, while simultaneously controlling substitutions and indels. Ablation experiments probing the encoder and decoder contributions show that the decoder contributes more to reconstruction accuracy in the current model, although when training is scaled up with increased model capacity and dataset sizes, the relative importance of the encoder increases (Extended Data Fig. [3](/articles/s41586-026-10842-8#Fig7) and Supplementary Note [1](/articles/s41586-026-10842-8#MOESM1) ).

## The Raygun architecture

Raygun implements this representation within an auto-encoder operating on ESM-2 embeddings (Extended Data Fig. [4](/articles/s41586-026-10842-8#Fig8) and [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). Although PLM embeddings provide a rich starting point, they must be refined to maximize information retention during condensation and to support generative sampling. The architecture separates these two tasks-length transformation and feature refinement-using two length-transforming layers ('Reduction' and 'Repetition') and multiple length-preserving 'T-Block' layers. Reduction layers perform within-block averaging, generating fixed-length outputs describing the Gaussian distribution; Repetition layers accept a target length and fixed-length representation, producing variable-length embeddings at the desired size. T-Block layers combine transformer modules for global context with 1D-convolution blocks for local relationships; present in both encoder and decoder stages, they account for most of Raygun's 701 million trainable parameters.

Training is self-supervised: the model learns to compress and decompress sequences while maintaining fidelity in both embedding and sequence spaces. The training objective enforces consistency across three complementary axes: (1) a reconstruction loss in embedding space, penalizing deviations in the reconstructed embeddings; (2) a cross-entropy loss in sequence space, penalizing deviations after decoding through a pre-trained ESM-2 decoder; and (3) a size-invariance loss in the Raygun latent space, critical for stable generation across varying output lengths, which decodes the fixed-length representation to a shorter sequence, re-encodes it, and penalizes divergence between the two fixed-length representations ( [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). We present here results from a model trained on around 80,000 proteins from UniRef50 ( [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ); scaling to larger models and datasets further improves performance (Extended Data Fig. [3c](/articles/s41586-026-10842-8#Fig7) and Supplementary Note [1](/articles/s41586-026-10842-8#MOESM1) ).

The architecture can be customized at inference time to improve generation quality. Although Raygun performs single-shot generation, a one-step recycling iteration (passing a generated candidate back through the model as a new template) further improves quality and diversity ( [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). The encoder governs diversity and the decoder governs fidelity (Extended Data Fig. [3c,e](/articles/s41586-026-10842-8#Fig7) and Supplementary Note [2](/articles/s41586-026-10842-8#MOESM1) ); accordingly, fine-tuning the decoder on target protein families improves reconstruction fidelity (BLOSUM score &gt;0.99; [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). Fine-tuning does not diminish diversity: we verified this by generating candidates from 100 sequence-diverse human and mouse proteins using both baseline and fine-tuned models, and across varying noise levels, both versions produced comparable sequence diversity.

After generation, we apply a PLM-based pseudo log-likelihood metric (pLL) to rank candidates by predicted evolutionary fitness, retaining high-quality variants (see [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) for filtering guidelines). Because pLL scores scale with sequence length, we devised a length-adjusted version that enables fair comparison across candidates of different sizes, a necessary step for any design method that generates proteins of variable length ( [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). As is common in protein design, we recommend that task-agnostic generation by Raygun is combined with downstream task-specific algorithmic filters. We assessed whether function preservation arises from Raygun's generative process itself, or whether that load falls on downstream filtering. We compared unfiltered Raygun candidates against a greedy PLM-based baseline that iteratively shortens proteins by removing the least evolutionarily important residues. On eGFP, mCherry and RAS, unfiltered Raygun candidates retained functional sites (chromophore residues [23](/articles/s41586-026-10842-8#ref-CR23) and P-loop motifs [24](/articles/s41586-026-10842-8#ref-CR24) ) at substantially higher rates than the greedy baseline, while showing lower overall sequence identity to the template, indicating higher diversity with better functional preservation (Extended Data Fig. [3a](/articles/s41586-026-10842-8#Fig7) and [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ).

## Structure preservation across sizes

To understand Raygun's generative capabilities, we applied it to 4 proteins spanning a 17-fold size range: haemoglobin (147 amino acids), CCR1 (355 amino acids), lacZ (1,024 amino acids) and mTOR (2,549 amino acids), generating 2,000 candidates per protein at multiple target lengths with moderate noise (0.5) and retaining the top 5% by length-adjusted pLL ( [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). Figure [2](/articles/s41586-026-10842-8#Fig2) shows AlphaFold3 [25](/articles/s41586-026-10842-8#ref-CR25) predicted structures of representative candidates for each protein, along with pLDDT [26](/articles/s41586-026-10842-8#ref-CR26) , LDDT [27](/articles/s41586-026-10842-8#ref-CR27) and TM-scores [28](/articles/s41586-026-10842-8#ref-CR28) against the template. Structural preservation holds across the entire size range, with graceful degradation at larger modifications: The TM-score of CCR1 decreased to 0.68 when shortened by 17%, whereas mTOR accommodated a 25% reduction with a similar TM-score of 0.69. mTOR could be miniaturized by more than 500 residues (over 20%) while maintaining a TM-score of approximately 0.7, demonstrating that the fixed-length representation captures sufficient structural information even for multi-domain complexes that are far larger than typical design targets. Beyond moderate modifications, Raygun can generate large deviation-halving or doubling protein length, or substituting more than 50% of residues-while broadly preserving the predicted structure.

Fig. 2: Protein editing using Raygun for proteins of different sequence lengths.

<!-- image -->

We next investigated where Raygun places its insertions and deletions. The haemoglobin candidates (Fig. [2b](/articles/s41586-026-10842-8#Fig2) ) illustrate that gaps are distributed across the sequence rather than concentrated in a single region. More systematically, Raygun shows only a modest bias towards removing loop regions at small length changes, and this preference diminishes at greater reductions (Extended Data Fig. [5a](/articles/s41586-026-10842-8#Fig9) and [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). The relative propensity to remove α-helices versus β-sheets remains broadly unchanged, a notable property given that maintaining balance across secondary structure types remains challenging in de novo protein design. Raygun also preferentially conserves functionally important regions: across proteins with annotated active and binding sites, the ratio of preserved functional sites to overall sequence conservation exceeded 1.0 at all deletion rates (5%, 10% and 25%), indicating selective retention without explicit annotation (Extended Data Fig. [5b](/articles/s41586-026-10842-8#Fig9) and [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). We also assessed Raygun-generated magnified sequences, finding that they too were well-balanced in insertions across the three secondary structure categories (Extended Data Fig. [3b](/articles/s41586-026-10842-8#Fig7) and [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ).

Raygun's two parameters-noise and target length-offer independent, fine-grained control over protein generation. The noise parameter scales the covariance matrix of the Gaussian distribution, controlling sequence variability: as noise increases, sequence identity gradually decreases until an inflection point around 2.2, after which they decline more rapidly; structural metrics such as TM-score, pLDDT and LDDT, obtained from OmegaFold [29](/articles/s41586-026-10842-8#ref-CR29) -generated structures, follow similar trends. The length parameter determines indel extent, with structural similarity largely maintained within ±10% of template length (median TM-score approximately 0.78). Across the tested range (0.01 to 6), noise values near 0 enable minor edits while values approaching 2 produce greater sequence variability, with predictable trade-offs between diversity and structural preservation (Extended Data Figs. [5d,e](/articles/s41586-026-10842-8#Fig9) and [6a](/articles/s41586-026-10842-8#Fig10) and [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). We also evaluated structural preservation using Boltz-2 [30](/articles/s41586-026-10842-8#ref-CR30) , a diffusion-based folding method, observing concordant results (Extended Data Fig. [7](/articles/s41586-026-10842-8#Fig11) ). Additionally, to emphasize template preservation rather than exploration, the noise can be set to zero. Raygun then retains high sequence identity during miniaturization, averaging around 93% of the maximum achievable identity even at 20% length reduction (Extended Data Fig. [3f](/articles/s41586-026-10842-8#Fig7) and [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ).

We performed additional systematic assessments of functional preservation across protein families. Across Pfam [31](/articles/s41586-026-10842-8#ref-CR31) domains spanning all four major SCOP structural classes (α, β, α/β and α + β), 50.65% of candidates retained their annotated domains across broad length ranges (50-200% of median family length), with retention from 37% (α + β) to 63% (α/β). Raygun preserved Pfam domains 15% better than a random-sequence baseline with matched substitution and indel rates (Extended Data Figs. [3d](/articles/s41586-026-10842-8#Fig7) and [8](/articles/s41586-026-10842-8#Fig12) ). ProTrek-based functional annotation further confirmed that for 14 out of 19 templates, all candidates within ±10% of template length exceeded the recommended threshold for functional similarity (Extended Data Fig. [9a](/articles/s41586-026-10842-8#Fig13) and [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). We also tested specific preservation under aggressive miniaturization: protein tyrosine kinases miniaturized to 60-70% of original length retained enzyme commission (EC) classification substantially better than a random baseline (Extended Data Fig. [9c](/articles/s41586-026-10842-8#Fig13) and [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ), and AlphaFold3 predicted that Raygun-generated spCas9 variants (miniaturized to 65-75% of original length) maintained superior structural stability and preserved nucleic acid-binding interfaces relative to baseline sequences (Extended Data Fig. [10](/articles/s41586-026-10842-8#Fig14) ).

Discrete diffusion methods such as EvoDiff and Diffusion Protein Language Model (DPLM) offer an alternative paradigm, generating protein sequences through iterative denoising rather than template-guided design. We benchmarked Raygun against both in same-length comparisons using 60 enzymatic proteins ( [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). Matching sequence identity distributions across methods, Raygun achieved comparable structural preservation and functional retention, as assessed by CLEAN-based [32](/articles/s41586-026-10842-8#ref-CR32) EC number prediction and OmegaFold-computed metrics (Extended Data Figs. [5f](/articles/s41586-026-10842-8#Fig9) and [9b](/articles/s41586-026-10842-8#Fig13) ). Unlike in-painting methods that require pre-specified modification sites, Raygun autonomously determines where to modify and natively handles both substitutions and indels. Raygun's fixed-length representations also outperformed ESM-2 average-pooled embeddings in clustering proteins by CATH structural hierarchy (class, architecture, topology, homologous superfamily and sequence family), with the gap particularly pronounced at the higher architecture level, suggesting improved capture of global structural organization (Extended Data Fig. [5c](/articles/s41586-026-10842-8#Fig9) ).

## Miniaturized fluorescent proteins

Fluorescent proteins [33](/articles/s41586-026-10842-8#ref-CR33) enable direct visualization of protein dynamics in living cells, but their size can disrupt the function of smaller proteins they are fused to [34](#ref-CR34) , [35](#ref-CR35) , [36](/articles/s41586-026-10842-8#ref-CR36) . Extensive engineering has produced fluorescent protein variants with distinct chromatic properties, monomeric forms and maturation times [37](/articles/s41586-026-10842-8#ref-CR37) , [38](/articles/s41586-026-10842-8#ref-CR38) , but there has been less attention on reducing their size, a critical consideration when tagging small proteins. We tested the ability of Raygun to generate shorter fluorescent proteins while preserving fluorescence.

We applied Raygun to eGFP (238 amino acids) and mCherry (236 amino acids), generating 70,000 candidates per template at lengths of 195-235 amino acids. Filtering combined pLL scoring (removing 90%), hmmscan to retain sequences with the correct Pfam domain, and a custom brightness predictor trained on the GFP brightness dataset [39](/articles/s41586-026-10842-8#ref-CR39) , [40](/articles/s41586-026-10842-8#ref-CR40) , yielding 8 candidates: XFP01-04 (eGFP) and XFP05-08 (mCherry) (Fig. [3](/articles/s41586-026-10842-8#Fig3) and [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ).

Fig. 3: Eight Raygun-generated fluorescent protein candidates.

<!-- image -->

Our pipeline did not explicitly enforce the chromophore sequence motif (XYG, typically at positions 65-67 in GFP [41](/articles/s41586-026-10842-8#ref-CR41) ), nor did we scaffold chromophore-forming residues as in recent de novo approaches [2](/articles/s41586-026-10842-8#ref-CR2) . We specified only noise and target length and allowed Raygun to generate miniaturized candidates. This contrasts with the de novo GFP design by Hayes et al. [2](/articles/s41586-026-10842-8#ref-CR2) , which preserved the template length (229 amino acids), specified sequence and structure of 6 residues that are critical for chromophore formation, and constrained residues 58-71, which were deemed crucial for chromophore energetics. We imposed none of these constraints, yet most of our candidates preserved the chromophore spontaneously.

Codon-optimized cDNAs were cloned into expression vectors and transfected into HEK293 cells. Four days later, images were inspected for fluorescence over background, followed by quantitative image analysis. Six out of eight variants (XFP01, XFP02, XFP04, XFP05, XFP06 and XFP08) showed substantial fluorescence compared with negative controls; XFP03 and XFP07 lacked activity. The successful candidates fluoresced with the expected spectrum of their respective templates, although at lower intensity, consistent with the narrow fitness landscape of fluorescent proteins [39](/articles/s41586-026-10842-8#ref-CR39) . Raygun generated functional fluorescent proteins from evolutionarily distant sources: eGFP from jellyfish ( *Aequorea victoria* ) and mCherry from coral ( *Discosoma* ) diverged around 600 million years ago and have distinct fluorescence spectra. Despite this evolutionary distance, Raygun shortened eGFP by up to 25 amino acids (10.5%) and mCherry by 37 amino acids (15.6%), producing proteins with 199 and 206 amino acids, respectively, that are shorter than 96% of fluorescent proteins in FPbase [40](/articles/s41586-026-10842-8#ref-CR40) . In choosing candidates for experimental validation, we deliberately included several with non-canonical chromophores to test whether alternative chromophore sequences could also produce fluorescence. One candidate (199 amino acids) had a glycine deleted and a serine substitution in the chromophore, demonstrating the capacity of Raygun to explore designs beyond canonical constraints.

## Miniaturized TurboID proteins

BioID proximity-dependent assays using biotin ligases have become essential tools for studying protein-protein interactions, localization and cellular dynamics [42](/articles/s41586-026-10842-8#ref-CR42) , [43](/articles/s41586-026-10842-8#ref-CR43) . Originally accomplished using slow-acting bacterial BirA, engineering efforts have produced improved variants including BioID2 and TurboID. However, TurboID (approximately 335 amino acids) is large enough to complicate fusion tagging: about 36% of human proteins are smaller. A shorter sequence may produce a less intrusive sensor. UltraID (172 amino acids) was created by manually removing the DNA-binding domain of TurboID [44](/articles/s41586-026-10842-8#ref-CR44) . We explored whether Raygun could both moderately and dramatically miniaturize TurboID while preserving its enzymatic activity.

We generated 500,000 TurboID variants targeting moderate miniaturization (195-235 amino acids) and extreme miniaturization (150-180 amino acids). Screening combined sequence-level filters (pLL and hmmscan) and thermostability via TemStaPro [45](/articles/s41586-026-10842-8#ref-CR45) with structure-based metrics (pLDDT, TM-score), yielding 11 candidates: TurboID-1 through TurboID-10 for the moderate objective and TurboID-11 (165 amino acids) for the extreme objective ( [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). Notably, Raygun autonomously removed the DNA-binding domain-the same domain that was removed to create UltraID-to reduce the protein to 165 amino acids. No domain annotation was provided to the model, and UltraID was not in its training data.

Experimental validation of these 11 candidates involved cloning their codon-optimized sequences into expression vectors containing a haemagglutinin (HA) epitope tag for detection. Our screening confirmed that 6 out of 11 variants were successfully expressed in HEK cells, including the TurboID-11 sequence, which was reduced in size by approximately half. To assess enzymatic activity, we incubated transfected cells with biotin (overnight, 50 µM) and pulled down biotinylated proteins using streptavidin magnetic beads. Western blotting with an anti-biotin antibody revealed significant biotinylation activity for two variants: TurboID-1 (317 amino acids, 1% reduction) and TurboID-5 (304 amino acids, 6% reduction) (Fig. [4a-c](/articles/s41586-026-10842-8#Fig4) ). TurboID-11 was successfully expressed, but its ligase activity was not significant, indicating that although Raygun can perform large length modifications and autonomously identify redundant domains, maintaining catalytic efficiency for multi-domain proteins with highly specialized enzymatic functions may require additional optimization, potentially through directed evolution of the miniaturized candidates.

Fig. 4: TurboID and EGF binding results.

<!-- image -->

## EGFR binders via magnification

To evaluate Raygun as a general-purpose design tool, we participated in a protein design competition benchmarking computational approaches for EGFR binder design [46](/articles/s41586-026-10842-8#ref-CR46) . Inspired by the CASP (Critical Assessment of protein Structure Prediction) competitions, the goal was to benchmark computational protein binder design against EGFR, a target of many cancer therapies. All candidates had to be single-chain proteins, no longer than 250 amino acids, with a difference of at least 10 amino acids from any published sequence. The first round tested 201 submissions, with only 5 (2.5%) showing significant binding, establishing a demanding baseline. We participated in the second round, which was organized following these disappointing results.

We selected EGF (53 amino acids), the endogenous ligand of EGFR, as the template. Since the length of EGF was close to the minimum 50-amino-acid threshold of Raygun, we applied magnification (rather than miniaturization) to generate candidates with 55-57 amino acids. We fine-tuned Raygun on 5 EGF-like sequences ( [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ) and generated 10,000 candidates without explicit constraints to preserve wild-type binding sites, instead relying on Raygun's generative process to implicitly maintain critical interactions.

To estimate binding potential, we used ProTrek [47](/articles/s41586-026-10842-8#ref-CR47) , a tri-modal PLM trained on sequence, structure and function, to rank candidates by predicted EGFR-binding potential directly from sequence rather than structural metrics. Our choice to predict function directly from a PLM, rather than relying on predicted structural metrics such as iPTM (interface predicted template modelling) and iPAE (interface prediction score from aligned errors), also distinguished our approach from other competition entries.

Out of ten submitted candidates, four were selected for biological evaluation ( [Supplementary Methods](/articles/s41586-026-10842-8#MOESM1) ). All four were expressed successfully. Two demonstrated strong EGFR binding: EGF-Raygun-1 (dissociation constant ( *K* d ) = 0.274 µM) and EGF-Raygun-2 ( *K* d = 0.561 µM), both stronger than wild-type EGF ( *K* d = 0.759 µM; Fig. [4d](/articles/s41586-026-10842-8#Fig4) ). Among all EGF-based approaches in the competition, our designs yielded the best binding affinities. Even methods based on the same baseline PLM as Raygun (ESM-2) did not perform as well.

Raygun identified candidates with improved function and lower sequence identity from a vast combinatorial space, suggesting that it captures functional attributes beyond sequence conservation. The more successful candidates had lower sequence identities to wild type: EGF-Raygun-1 (70.7% identity) and EGF-Raygun-2 (76.8% identity) versus EGF-Raygun-3 (80.4% identity) and EGF-Raygun-4 (78.6% identity). The key modifications occurred at peripheral positions, presumably distant from the binding interface, yet substantially influenced binding affinity, indicating that function depends on global sequence context beyond direct binding-site residues.

## Discussion

Even though proteins evolve primarily residue by residue, natural selection does not evaluate them as such-it acts on holistic properties such as fold stability, binding affinity and catalytic activity, that emerge only at the level of the whole molecule. Raygun bridges this dichotomy by taking residue-level PLM embeddings and condensing them into a fixed-dimensional probabilistic space that allows reasoning across proteins of any size. Our representation of each protein as a Gaussian distribution, rooted in the central limit theorem rather than diffusion-based denoising, makes direct, single-shot sampling tractable, with generation roughly 100-fold faster than diffusion-based methods. More broadly, this principle of representing biological sequences of variable length in fixed-dimensional probabilistic spaces may extend to RNA families and genomic regulatory elements.

In protein design, the central challenge is staying on the manifold of feasible proteins while searching as broadly as possible across it. De novo methods [4](/articles/s41586-026-10842-8#ref-CR4) , [5](/articles/s41586-026-10842-8#ref-CR5) , [48](/articles/s41586-026-10842-8#ref-CR48) , [49](/articles/s41586-026-10842-8#ref-CR49) start far from this manifold and attempt to reach it. Since they fix protein length at generation time, post-generation modifications are tractable only for substitutions, limiting the accessible design space. Raygun complements these approaches by starting on the manifold and exploring outwards from it, making indel-based exploration as tractable as substitutions and expanding the search radius available to the designer. The two strategies can be combined: when a de novo design requires structural optimization (shortening a loop, removing a redundant domain), Raygun enables targeted length modifications while preserving favourable features. This becomes critical when a design has the correct properties but the wrong length, such as a candidate that exceeds adeno-associated virus (AAV) packaging limits for gene therapy.

Our experimental results suggest that template-guided approaches can enable greater design novelty than de novo methods. Raygun shortened eGFP and mCherry to as little as 199 and 206 amino acids, shorter than 96% of fluorescent proteins in FPbase [40](/articles/s41586-026-10842-8#ref-CR40) , and 6 out of 8 tested variants exhibited fluorescence above background. The de novo GFP design by Hayes et al. [2](/articles/s41586-026-10842-8#ref-CR2) , using ESM-3, preserved the template length (229 amino acids), specified sequence and structure of 6 residues critical for chromophore formation, and constrained residues 58-71 for chromophore energetics. We imposed none of these constraints, yet most candidates preserved the chromophore spontaneously, and one carried a non-canonical chromophore sequence (Supplementary Note [3](/articles/s41586-026-10842-8#MOESM1) ). Our designs and the ESM-3 GFP showed dim fluorescence and will require directed evolution to reach high fluorescence. Beyond the size reduction, the more notable finding was that a functional fluorescent protein could be obtained at all despite more than 40 coordinated indels and substitutions, given the well-known narrow fitness landscape of fluorescent proteins [39](/articles/s41586-026-10842-8#ref-CR39) . This suggests that Raygun's edits respect the functional grammar of the protein, and that compact Raygun-generated fluorescent proteins could serve as scaffolds for new, more powerful biosensors.

For naturally evolved proteins, the relationship between sequence and function is also less straightforward than direct conservation suggests. Hie et al. [50](/articles/s41586-026-10842-8#ref-CR50) have hypothesized that PLM-generated mutations, which follow evolutionary rules, should generally improve fitness, demonstrating this for specific antibodies. Our EGF results both support and complicate this view: using a sequence-focused approach without explicit structural optimization, we generated EGF variants with stronger EGFR binding than the native ligand, yet the key modifications occurred at peripheral positions that are presumably distant from the binding interface, indicating that function depends on global sequence context beyond direct binding-site residues.

A complementary lesson comes from the biotin ligase experiments. Moderate miniaturization preserved biotinylation activity, demonstrating Raygun-based optimization in a multi-domain setting. By contrast, extreme miniaturization-where Raygun autonomously identified and removed the DNA-binding domain to produce TurboID-11 (165 amino acids, approximately 50% reduction)-yielded a variant that was structurally stable and expressed in cells, but with weak biotinylation activity. Biotin ligation itself is a natural function that is well represented in PLM training data, but the high-strength activity of TurboID is an engineered, supra-evolutionary trait achieved through directed mutagenesis of BirA, and such supra-evolutionary functions may not be fully captured by evolutionary sequence statistics. Recovering them in aggressively miniaturized variants will likely require closing the loop with experimental feedback, such as directed evolution from Raygun candidates or function-specific assays to supplement PLM-based filters.

Future enhancements to Raygun could address scaling, multi-domain handling and directed domain manipulation. To assess the core conceptual contributions, we present results from a Raygun model trained on only 80,000 proteins from UniRef50, a data-efficient setup. Although this is already powerful, longer proteins challenged zero-shot reconstruction, suggesting limits to the expressiveness of a fixed-length representation; in such cases (for example, mTOR, with 2,549 amino acids) we recommend fine-tuning, and future work could explicitly account for multi-domain organization. Scaling to larger models and datasets continues to improve performance (Supplementary Note [1](/articles/s41586-026-10842-8#MOESM1) ), and integrating more powerful or structure-infused PLMs such as ESM-3 [2](/articles/s41586-026-10842-8#ref-CR2) and SaProt [3](/articles/s41586-026-10842-8#ref-CR3) could further enhance Raygun. Directed manipulation of protein domains, including both removal and addition, offers another frontier whereby computational approaches can be guided by functional constraints.

Finally, Raygun, like other generative protein design tools, raises important biosafety considerations. We are signatories to the Responsible AI for Biodesign principles ( [https://responsiblebiodesign.ai/](https://responsiblebiodesign.ai/) ) and believe that computational tools must be developed and deployed with appropriate safeguards, including for concerns such as immunogenicity in therapeutic applications. Our validation results with computational functional prediction tools (such as, Pfam, ProTrek and CLEAN) suggest that they can serve as effective filters for identifying potentially concerning Raygun-generated sequences.

### Reporting summary

Further information on research design is available in the [Nature Portfolio Reporting Summary](/articles/s41586-026-10842-8#MOESM2) linked to this article.

## Data availability

Sequences of Raygun-designed fluorescent proteins and biotin ligases are available in AddGene ( [https://www.addgene.org/browse/article/28275322/](https://www.addgene.org/browse/article/28275322/) ). The data used for training the Raygun model are provided as datasets in Zenodo ( [https://zenodo.org/records/19546626](https://zenodo.org/records/19546626) (ref. [51](/articles/s41586-026-10842-8#ref-CR51) )). All other data are available within the article and its [Supplementary Information](/articles/s41586-026-10842-8#MOESM1) .

## Code availability

The source code and documentation of Raygun, including the latest pre-trained checkpoints and reproducibility notebooks, are available at GitHub ( [https://github.com/rohitsinghlab/raygun](https://github.com/rohitsinghlab/raygun) ).

## References

1. Lin, Z. et al. Evolutionary-scale prediction of atomic-level protein structure with a language model. *Science* **379** , 1123-1130 (2023). [Article](https://doi.org/10.1126%2Fscience.ade2574) [MathSciNet](http://www.ams.org/mathscinet-getitem?mr=4567681) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB3sXls1ertrk%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=36927031) [ADS](http://adsabs.harvard.edu/cgi-bin/nph-data_query?link_type=ABSTRACT&bibcode=2023Sci...379.1123L) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Evolutionary-scale%20prediction%20of%20atomic-level%20protein%20structure%20with%20a%20language%20model&journal=Science&doi=10.1126%2Fscience.ade2574&volume=379&pages=1123-1130&publication_year=2023&author=Lin%2CZ)
2. Hayes, T. et al. Simulating 500 million years of evolution with a language model. *Science* **387** , 850-858 (2025). [Article](https://doi.org/10.1126%2Fscience.ads0018) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB2MXkslOqs7o%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=39818825) [ADS](http://adsabs.harvard.edu/cgi-bin/nph-data_query?link_type=ABSTRACT&bibcode=2025Sci...387..850H) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Simulating%20500%20million%20years%20of%20evolution%20with%20a%20language%20model&journal=Science&doi=10.1126%2Fscience.ads0018&volume=387&pages=850-858&publication_year=2025&author=Hayes%2CT)
3. Su, J. et al. Democratizing protein language model training, sharing and collaboration. *Nat. Biotechnol.* [https://doi.org/10.1038/s41587-025-02859-7](https://doi.org/10.1038/s41587-025-02859-7) (2025).
4. Watson, J. L. et al. De novo design of protein structure and function with RFdiffusion. *Nature* **620** , 1089-1100 (2023). [Article](https://doi.org/10.1038%2Fs41586-023-06415-8) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB3sXhslGrs73M) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=37433327) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC10468394) [ADS](http://adsabs.harvard.edu/cgi-bin/nph-data_query?link_type=ABSTRACT&bibcode=2023Natur.620.1089W) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=De%20novo%20design%20of%20protein%20structure%20and%20function%20with%20RFdiffusion&journal=Nature&doi=10.1038%2Fs41586-023-06415-8&volume=620&pages=1089-1100&publication_year=2023&author=Watson%2CJL)
5. Alamdari, S. et al. Protein generation with evolutionary diffusion: sequence is all you need. Preprint at *bioRxiv* [https://doi.org/10.1101/2023.09.11.556673](https://doi.org/10.1101/2023.09.11.556673) (2024).
6. Lin, Y. &amp; AlQuraishi, M. Generating novel, designable, and diverse protein structures by equivariantly diffusing oriented residue clouds. In *Proc. 40th International Conference on Machine Learning* 20978-21002 (JMLR, 2023).
7. Lin, Y., Lee, M., Zhang, Z. &amp; AlQuraishi, M. Out of many, one: designing and scaffolding proteins at the scale of the structural universe with Genie 2. Preprint at [https://doi.org/10.48550/arxiv.2405.15489](https://doi.org/10.48550/arxiv.2405.15489) (2024).
8. Lorch, M. in *Biochemistry: A Very Short Introduction* 34-51 (Oxford Univ. Press, 2021).
9. Madani, A. et al. Large language models generate functional protein sequences across diverse families. *Nat. Biotechnol.* **41** , 1099-1106 (2023). [Article](https://doi.org/10.1038%2Fs41587-022-01618-2) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB3sXitVeqt7k%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=36702895) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC10400306) [ADS](http://adsabs.harvard.edu/cgi-bin/nph-data_query?link_type=ABSTRACT&bibcode=2023NatBi..41.1099M) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Large%20language%20models%20generate%20functional%20protein%20sequences%20across%20diverse%20families&journal=Nat.%20Biotechnol.&doi=10.1038%2Fs41587-022-01618-2&volume=41&pages=1099-1106&publication_year=2023&author=Madani%2CA)
10. Pokharel, S., Pratyush, P., Heinzinger, M., Newman, R. H. &amp; Kc, D. B. Improving protein succinylation sites prediction using embeddings from protein language model. *Sci. Rep.* **12** , 16933 (2022). [Article](https://doi.org/10.1038%2Fs41598-022-21366-2) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB38XisF2mur7O) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=36209286) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC9547369) [ADS](http://adsabs.harvard.edu/cgi-bin/nph-data_query?link_type=ABSTRACT&bibcode=2022NatSR..1216933P) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Improving%20protein%20succinylation%20sites%20prediction%20using%20embeddings%20from%20protein%20language%20model&journal=Sci.%20Rep.&doi=10.1038%2Fs41598-022-21366-2&volume=12&publication_year=2022&author=Pokharel%2CS&author=Pratyush%2CP&author=Heinzinger%2CM&author=Newman%2CRH&author=Kc%2CDB)
11. Brandes, N., Ofer, D., Peleg, Y., Rappoport, N. &amp; Linial, M. ProteinBERT: a universal deep-learning model of protein sequence and function. *Bioinformatics* **38** , 2102-2110 (2022). [Article](https://doi.org/10.1093%2Fbioinformatics%2Fbtac020) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB38Xhslalu7%2FN) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=35020807) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC9386727) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=ProteinBERT%3A%20a%20universal%20deep-learning%20model%20of%20protein%20sequence%20and%20function&journal=Bioinformatics&doi=10.1093%2Fbioinformatics%2Fbtac020&volume=38&pages=2102-2110&publication_year=2022&author=Brandes%2CN&author=Ofer%2CD&author=Peleg%2CY&author=Rappoport%2CN&author=Linial%2CM)
12. Sledzieski, S., Singh, R., Cowen, L. &amp; Berger, B. D-SCRIPT translates genome to phenome with sequence-based, structure-aware, genome-scale predictions of protein-protein interactions. *Cell Syst.* **12** , 969-982.e6 (2021). [Article](https://doi.org/10.1016%2Fj.cels.2021.08.010) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB3MXitVGlsbjL) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=34536380) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC8586911) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=D-SCRIPT%20translates%20genome%20to%20phenome%20with%20sequence-based%2C%20structure-aware%2C%20genome-scale%20predictions%20of%20protein%E2%80%93protein%20interactions&journal=Cell%20Syst.&doi=10.1016%2Fj.cels.2021.08.010&volume=12&pages=969-982.e6&publication_year=2021&author=Sledzieski%2CS&author=Singh%2CR&author=Cowen%2CL&author=Berger%2CB)
13. Singh, R., Devkota, K., Sledzieski, S., Berger, B. &amp; Cowen, L. Topsy-Turvy: integrating a global view into sequence-based PPI prediction. *Bioinformatics* **38** , i264-i272 (2022). [Article](https://doi.org/10.1093%2Fbioinformatics%2Fbtac258) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=35758793) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC9235477) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Topsy-Turvy%3A%20integrating%20a%20global%20view%20into%20sequence-based%20PPI%20prediction&journal=Bioinformatics&doi=10.1093%2Fbioinformatics%2Fbtac258&volume=38&pages=i264-i272&publication_year=2022&author=Singh%2CR&author=Devkota%2CK&author=Sledzieski%2CS&author=Berger%2CB&author=Cowen%2CL)
14. Singh, R., Sledzieski, S., Bryson, B., Cowen, L. &amp; Berger, B. Contrastive learning in protein language space predicts interactions between drugs and protein targets. *Proc. Natl Acad. Sci. USA* **120** , e2220778120 (2023). [Article](https://doi.org/10.1073%2Fpnas.2220778120) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB3sXhsVChsbfI) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=37289807) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC10268324) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Contrastive%20learning%20in%20protein%20language%20space%20predicts%20interactions%20between%20drugs%20and%20protein%20targets&journal=Proc.%20Natl%20Acad.%20Sci.%20USA&doi=10.1073%2Fpnas.2220778120&volume=120&publication_year=2023&author=Singh%2CR&author=Sledzieski%2CS&author=Bryson%2CB&author=Cowen%2CL&author=Berger%2CB)
15. Bhat, S. et al. De novo design of peptide binders to conformationally diverse targets with contrastive language modeling. *Sci. Adv.* **11** , eadr8638 (2025). [Article](https://doi.org/10.1126%2Fsciadv.adr8638) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB2MXivVGks78%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=39841846) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC11753435) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=De%20novo%20design%20of%20peptide%20binders%20to%20conformationally%20diverse%20targets%20with%20contrastive%20language%20modeling&journal=Sci.%20Adv.&doi=10.1126%2Fsciadv.adr8638&volume=11&publication_year=2025&author=Bhat%2CS)
16. Frey, N. C. et al. Protein discovery with discrete walk-jump sampling. Preprint at [https://doi.org/10.48550/arxiv.2306.12360](https://doi.org/10.48550/arxiv.2306.12360) (2023).
17. Cohen, T. &amp; Schneidman-Duhovny, D. Epitope-specific antibody design using diffusion models on the latent space of ESM embeddings. In *Workshop on Generative and Experimental Perspectives for Biomolecular Design* [https://openreview.net/pdf?id=r561kIH4lE](https://openreview.net/pdf?id=r561kIH4lE) (ICLR, 2024).
18. Grimmett, G. R. &amp; Stirzaker, D. R. *Probability and Random Processes* (Oxford Univ. Press, 2001).
19. Serfling, R. J. Contributions to central limit theory for dependent variables. *Ann. Math. Statist.* **39** , 1158-1175 (1968). [Article](https://doi.org/10.1214%2Faoms%2F1177698240) [MathSciNet](http://www.ams.org/mathscinet-getitem?mr=228053) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Contributions%20to%20central%20limit%20theory%20for%20dependent%20variables&journal=Ann.%20Math.%20Statist.&doi=10.1214%2Faoms%2F1177698240&volume=39&pages=1158-1175&publication_year=1968&author=Serfling%2CRJ)
20. Song, J., Meng, C. &amp; Ermon, S. Denoising diffusion implicit models. In *International Conference on Learning Representations* [https://openreview.net/pdf?id=St1giarCHLP](https://openreview.net/pdf?id=St1giarCHLP) (ICLR, 2023).
21. Song, Y., Durkan, C., Murray, I. &amp; Ermon, S. Maximum likelihood training of score-based diffusion models. In *Proc. 35th International Conference on Neural Information Processing Systems* 1415-1428 (2021).
22. Lipman, Y., Chen, R. T. Q., Ben-Hamu, H., Nickel, M. &amp; Le, M. Flow matching for generative modeling. In *International Conference on Learning Representations* [https://openreview.net/pdf?id=PqvMRDCJT9t](https://openreview.net/pdf?id=PqvMRDCJT9t) (ICLR, 2023).
23. Shcherbakova, D. M. &amp; Verkhusha, V. V. Chromophore chemistry of fluorescent proteins controlled by light. *Curr. Opin. Chem. Biol.* **20** , 60-68 (2014). [Article](https://doi.org/10.1016%2Fj.cbpa.2014.04.010) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BC2cXhtFansb3L) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=24819887) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4096052) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Chromophore%20chemistry%20of%20fluorescent%20proteins%20controlled%20by%20light&journal=Curr.%20Opin.%20Chem.%20Biol.&doi=10.1016%2Fj.cbpa.2014.04.010&volume=20&pages=60-68&publication_year=2014&author=Shcherbakova%2CDM&author=Verkhusha%2CVV)
24. Jani, V., Sonavane, U. &amp; Joshi, R. Insight into structural dynamics involved in activation mechanism of full length KRAS wild type and P-loop mutants. *Heliyon* **10** , e36161 (2024). [Article](https://doi.org/10.1016%2Fj.heliyon.2024.e36161) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB2cXhslGiur3O) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=39247361) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC11379609) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Insight%20into%20structural%20dynamics%20involved%20in%20activation%20mechanism%20of%20full%20length%20KRAS%20wild%20type%20and%20P-loop%20mutants&journal=Heliyon&doi=10.1016%2Fj.heliyon.2024.e36161&volume=10&publication_year=2024&author=Jani%2CV&author=Sonavane%2CU&author=Joshi%2CR)
25. Abramson, J. et al. Accurate structure prediction of biomolecular interactions with AlphaFold 3. *Nature* **630** , 493-500 (2024). [Article](https://doi.org/10.1038%2Fs41586-024-07487-w) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB2cXhtlSntbjJ) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=38718835) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC11168924) [ADS](http://adsabs.harvard.edu/cgi-bin/nph-data_query?link_type=ABSTRACT&bibcode=2024Natur.630..493A) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Accurate%20structure%20prediction%20of%20biomolecular%20interactions%20with%20AlphaFold%203&journal=Nature&doi=10.1038%2Fs41586-024-07487-w&volume=630&pages=493-500&publication_year=2024&author=Abramson%2CJ)
26. Wilson, C. J., Choy, W.-Y. &amp; Karttunen, M. AlphaFold2: a role for disordered protein/region prediction? *IJMS* **23** , 4591 (2022). [Article](https://doi.org/10.3390%2Fijms23094591) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB38Xhtlemu7fN) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=35562983) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC9104326) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=AlphaFold2%3A%20a%20role%20for%20disordered%20protein%2Fregion%20prediction%3F&journal=IJMS&doi=10.3390%2Fijms23094591&volume=23&publication_year=2022&author=Wilson%2CCJ&author=Choy%2CW-Y&author=Karttunen%2CM)
27. Mariani, V., Biasini, M., Barbato, A. &amp; Schwede, T. lDDT: a local superposition-free score for comparing protein structures and models using distance difference tests. *Bioinformatics* **29** , 2722-2728 (2013). [Article](https://doi.org/10.1093%2Fbioinformatics%2Fbtt473) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BC3sXhs1CisrfK) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23986568) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3799472) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=lDDT%3A%20a%20local%20superposition-free%20score%20for%20comparing%20protein%20structures%20and%20models%20using%20distance%20difference%20tests&journal=Bioinformatics&doi=10.1093%2Fbioinformatics%2Fbtt473&volume=29&pages=2722-2728&publication_year=2013&author=Mariani%2CV&author=Biasini%2CM&author=Barbato%2CA&author=Schwede%2CT)
28. Zhang, Y. TM-align: a protein structure alignment algorithm based on the TM-score. *Nucleic Acids Res.* **33** , 2302-2309 (2005). [Article](https://doi.org/10.1093%2Fnar%2Fgki524) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BD2MXjsl2gsLY%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=15849316) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC1084323) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=TM-align%3A%20a%20protein%20structure%20alignment%20algorithm%20based%20on%20the%20TM-score&journal=Nucleic%20Acids%20Res.&doi=10.1093%2Fnar%2Fgki524&volume=33&pages=2302-2309&publication_year=2005&author=Zhang%2CY)
29. Wu, R. et al. High-resolution de novo structure prediction from primary sequence. Preprint at *bioRxiv* [https://doi.org/10.1101/2022.07.21.500999](https://doi.org/10.1101/2022.07.21.500999) (2022).
30. Passaro, S. et al. Boltz-2: towards accurate and efficient binding affinity prediction. Preprint at *bioRxiv* [https://doi.org/10.1101/2025.06.14.659707](https://doi.org/10.1101/2025.06.14.659707) (2025).
31. Bateman, A. The Pfam protein families database. *Nucleic Acids Res.* **32** , 138D-141D (2004). [Article](https://doi.org/10.1093%2Fnar%2Fgkh121) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=The%20Pfam%20protein%20families%20database&journal=Nucleic%20Acids%20Res.&doi=10.1093%2Fnar%2Fgkh121&volume=32&pages=138D-141D&publication_year=2004&author=Bateman%2CA)
32. Yu, T. et al. Enzyme function prediction using contrastive learning. *Science* **379** , 1358-1363 (2023). [Article](https://doi.org/10.1126%2Fscience.adf2465) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB3sXmslGksbY%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=36996195) [ADS](http://adsabs.harvard.edu/cgi-bin/nph-data_query?link_type=ABSTRACT&bibcode=2023Sci...379.1358Y) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Enzyme%20function%20prediction%20using%20contrastive%20learning&journal=Science&doi=10.1126%2Fscience.adf2465&volume=379&pages=1358-1363&publication_year=2023&author=Yu%2CT)
33. Shaner, N. C., Patterson, G. H. &amp; Davidson, M. W. Advances in fluorescent protein technology. *J. Cell Sci.* **120** , 4247-4260 (2007). [Article](https://doi.org/10.1242%2Fjcs.005801) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BD1cXns1GktQ%3D%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=18057027) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Advances%20in%20fluorescent%20protein%20technology&journal=J.%20Cell%20Sci.&doi=10.1242%2Fjcs.005801&volume=120&pages=4247-4260&publication_year=2007&author=Shaner%2CNC&author=Patterson%2CGH&author=Davidson%2CMW)
34. Rappoport, J. Z. &amp; Simon, S. M. A functional GFP fusion for imaging clathrin-mediated endocytosis. *Traffic* **9** , 1250-1255 (2008). [Article](https://doi.org/10.1111%2Fj.1600-0854.2008.00770.x) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BD1cXpslWhtL8%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=18498437) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2761611) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20functional%20GFP%20fusion%20for%20imaging%20clathrin-mediated%20endocytosis&journal=Traffic&doi=10.1111%2Fj.1600-0854.2008.00770.x&volume=9&pages=1250-1255&publication_year=2008&author=Rappoport%2CJZ&author=Simon%2CSM)
35. Skube, S. B., Chaverri, J. M. &amp; Goodson, H. V. Effect of GFP tags on the localization of EB1 and EB1 fragments in vivo. *Cytoskeleton* **67** , 1-12 (2010). [Article](https://doi.org/10.1002%2Fcm.20409) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BC3cXjtlGmtr4%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=19701929) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2909448) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Effect%20of%20GFP%20tags%20on%20the%20localization%20of%20EB1%20and%20EB1%20fragments%20in%20vivo&journal=Cytoskeleton&doi=10.1002%2Fcm.20409&volume=67&pages=1-12&publication_year=2010&author=Skube%2CSB&author=Chaverri%2CJM&author=Goodson%2CHV)
36. Zhou, Z. K., Hong, K. Huang, B. &amp; Narlikar, G. J. Understanding how genetically encoded tags affect phase separation by heterochromatin protein HP1α. *Cell Rep. Methods* **5** , 101029 (2025).
37. Cubitt, A. B. et al. Understanding, improving and using green fluorescent proteins. *Trends Biochem. Sci.* **20** , 448-455 (1995). [Article](https://doi.org/10.1016%2FS0968-0004%2800%2989099-4) [CAS](/articles/cas-redirect/1:CAS:528:DyaK2MXpsF2murw%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=8578587) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Understanding%2C%20improving%20and%20using%20green%20fluorescent%20proteins&journal=Trends%20Biochem.%20Sci&doi=10.1016%2FS0968-0004%2800%2989099-4&volume=20&pages=448-455&publication_year=1995&author=Cubitt%2CAB)
38. Rodriguez, E. A. et al. The growing and glowing toolbox of fluorescent and photoactive proteins. *Trends Biochem. Sci.* **42** , 111-129 (2017). [Article](https://doi.org/10.1016%2Fj.tibs.2016.09.010) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BC28XhslSitL7M) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=27814948) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=The%20growing%20and%20glowing%20toolbox%20of%20fluorescent%20and%20photoactive%20proteins&journal=Trends%20Biochem.%20Sci&doi=10.1016%2Fj.tibs.2016.09.010&volume=42&pages=111-129&publication_year=2017&author=Rodriguez%2CEA)
39. Sarkisyan, K. S. et al. Local fitness landscape of the green fluorescent protein. *Nature* **533** , 397-401 (2016). [Article](https://doi.org/10.1038%2Fnature17995) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BC28XotVWgtLg%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=27193686) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4968632) [ADS](http://adsabs.harvard.edu/cgi-bin/nph-data_query?link_type=ABSTRACT&bibcode=2016Natur.533..397S) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Local%20fitness%20landscape%20of%20the%20green%20fluorescent%20protein&journal=Nature&doi=10.1038%2Fnature17995&volume=533&pages=397-401&publication_year=2016&author=Sarkisyan%2CKS)
40. Lambert, T. J. FPbase: a community-editable fluorescent protein database. *Nat. Methods* **16** , 277-278 (2019). [Article](https://doi.org/10.1038%2Fs41592-019-0352-8) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BC1MXmslKgu7w%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=30886412) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=FPbase%3A%20a%20community-editable%20fluorescent%20protein%20database&journal=Nat.%20Methods&doi=10.1038%2Fs41592-019-0352-8&volume=16&pages=277-278&publication_year=2019&author=Lambert%2CTJ)
41. Barondeau, D. P., Putnam, C. D., Kassmann, C. J., Tainer, J. A. &amp; Getzoff, E. D. Mechanism and energetics of green fluorescent protein chromophore synthesis revealed by trapped intermediate structures. *Proc. Natl Acad. Sci. USA* **100** , 12111-12116 (2003). [Article](https://doi.org/10.1073%2Fpnas.2133463100) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BD3sXotlGlurg%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=14523232) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC218721) [ADS](http://adsabs.harvard.edu/cgi-bin/nph-data_query?link_type=ABSTRACT&bibcode=2003PNAS..10012111B) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Mechanism%20and%20energetics%20of%20green%20fluorescent%20protein%20chromophore%20synthesis%20revealed%20by%20trapped%20intermediate%20structures&journal=Proc.%20Natl%20Acad.%20Sci.%20USA&doi=10.1073%2Fpnas.2133463100&volume=100&pages=12111-12116&publication_year=2003&author=Barondeau%2CDP&author=Putnam%2CCD&author=Kassmann%2CCJ&author=Tainer%2CJA&author=Getzoff%2CED)
42. Kim, D. I. et al. An improved smaller biotin ligase for BioID proximity labeling. *Mol. Biol. Cell* **27** , 1188-1196 (2016). [Article](https://doi.org/10.1091%2Fmbc.E15-12-0844) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BC28Xhs1art7bP) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=26912792) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4831873) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=An%20improved%20smaller%20biotin%20ligase%20for%20BioID%20proximity%20labeling&journal=Mol.%20Biol.%20Cell&doi=10.1091%2Fmbc.E15-12-0844&volume=27&pages=1188-1196&publication_year=2016&author=Kim%2CDI)
43. Branon, T. C. et al. Efficient proximity labeling in living cells and organisms with TurboID. *Nat. Biotechnol.* **36** , 880-887 (2018). [Article](https://doi.org/10.1038%2Fnbt.4201) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BC1cXhsFChurbK) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=30125270) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC6126969) [ADS](http://adsabs.harvard.edu/cgi-bin/nph-data_query?link_type=ABSTRACT&bibcode=2018NatBi..36..880B) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Efficient%20proximity%20labeling%20in%20living%20cells%20and%20organisms%20with%20TurboID&journal=Nat.%20Biotechnol.&doi=10.1038%2Fnbt.4201&volume=36&pages=880-887&publication_year=2018&author=Branon%2CTC)
44. Kubitz, L. et al. Engineering of ultraID, a compact and hyperactive enzyme for proximity-dependent biotinylation in living cells. *Commun. Biol.* **5** , 657 (2022). [Article](https://doi.org/10.1038%2Fs42003-022-03604-5) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB38XhvVGmsrrN) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=35788163) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC9253107) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Engineering%20of%20ultraID%2C%20a%20compact%20and%20hyperactive%20enzyme%20for%20proximity-dependent%20biotinylation%20in%20living%20cells&journal=Commun.%20Biol.&doi=10.1038%2Fs42003-022-03604-5&volume=5&publication_year=2022&author=Kubitz%2CL)
45. Pudžiuvelytė, I. et al. TemStaPro: protein thermostability prediction using sequence representations from protein language models. *Bioinformatics* **40** , btae157 (2024). [Article](https://doi.org/10.1093%2Fbioinformatics%2Fbtae157) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=38507682) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC11001493) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=TemStaPro%3A%20protein%20thermostability%20prediction%20using%20sequence%20representations%20from%20protein%20language%20models&journal=Bioinformatics&doi=10.1093%2Fbioinformatics%2Fbtae157&volume=40&publication_year=2024&author=Pud%C5%BEiuvelyt%C4%97%2CI)
46. Cotet, T.-S. et al. Crowdsourced protein design: lessons From the Adaptyv EGFR binder competition. Preprint at *bioRxiv* [https://doi.org/10.1101/2025.04.17.648362](https://doi.org/10.1101/2025.04.17.648362) (2025).
47. Su, J. et al. A trimodal protein language model enables advanced protein searches. *Nat. Biotechnol.* [https://doi.org/10.1038/s41587-025-02836-0](https://doi.org/10.1038/s41587-025-02836-0) (2025). [Article](https://doi.org/10.1038%2Fs41587-025-02836-0) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=41136773) [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC12404177) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20trimodal%20protein%20language%20model%20enables%20advanced%20protein%20searches&journal=Nat.%20Biotechnol.&doi=10.1038%2Fs41587-025-02836-0&publication_year=2025&author=Su%2CJ)
48. Geffner, T. et al. La-Proteina: atomistic protein generation via partially latent flow matching. Preprint at [https://doi.org/10.48550/arxiv.2507.09466](https://doi.org/10.48550/arxiv.2507.09466) (2025).
49. Wang, X. et al. Diffusion language models are versatile protein learners. In *Proc. 41st International Conference on Machine Learning* 52309-52333 (JMLR, 2024).
50. Hie, B. L. et al. Efficient evolution of human antibodies from general protein language models. *Nat. Biotechnol.* **42** , 275-283 (2024). [Article](https://doi.org/10.1038%2Fs41587-023-01763-2) [CAS](/articles/cas-redirect/1:CAS:528:DC%2BB3sXosVKru74%3D) [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=37095349) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Efficient%20evolution%20of%20human%20antibodies%20from%20general%20protein%20language%20models&journal=Nat.%20Biotechnol.&doi=10.1038%2Fs41587-023-01763-2&volume=42&pages=275-283&publication_year=2024&author=Hie%2CBL)
51. Devkota, K. Raygun benchmarking + training dataset. *Zenodo* [https://doi.org/10.5281/zenodo.19546626](https://doi.org/10.5281/zenodo.19546626) (2026).

[Download references](https://citation-needed.springer.com/v2/references/10.1038/s41586-026-10842-8?format=refman&flavour=references)

## Acknowledgements

We thank L. Cowen and M. Erden for helpful feedback, and A. Parekh, A. Pratapa, H. Liang, P. Jolly, S. Ozbay, T. Fujiyama and Y. Liang for assistance in generating structures using the AlphaFold3 webserver. EGFR binding results were generated using the protein characterization platform by Adaptyv Bio.

## Funding

K.D. and R.S. acknowledge support of the Whitehead Scholarship at Duke University and NIH grant R01NS147042. D.S., J.M. and S.S. acknowledge support of NIH grants R01MH111684 and R01NS147042. Y.S.K. and W.W. acknowledge support of NIH grants R01AG098026 and R01AI150282.

## Author information

Author notes

1. These authors contributed equally: Kapil Devkota, Daichi Shonai

### Authors and Affiliations

1. Department of Biostatistics and Bioinformatics, Duke University, Durham, NC, USA Kapil Devkota &amp; Rohit Singh
2. Department of Cell Biology, Duke University, Durham, NC, USA Daichi Shonai, Joey Mao, Scott Soderling &amp; Rohit Singh
3. Department of Chemistry and Biochemistry, University of California San Diego, San Diego, CA, USA Young Su Ko &amp; Wei Wang

Authors

1. Kapil Devkota [View author publications](/search?author=Kapil%20Devkota) Search author on: [PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Kapil%20Devkota) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Kapil%20Devkota%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)
2. Daichi Shonai [View author publications](/search?author=Daichi%20Shonai) Search author on: [PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Daichi%20Shonai) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Daichi%20Shonai%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)
3. Joey Mao [View author publications](/search?author=Joey%20Mao) Search author on: [PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Joey%20Mao) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Joey%20Mao%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)
4. Young Su Ko [View author publications](/search?author=Young%20Su%20Ko) Search author on: [PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Young%20Su%20Ko) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Young%20Su%20Ko%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)
5. Wei Wang [View author publications](/search?author=Wei%20Wang) Search author on: [PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Wei%20Wang) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Wei%20Wang%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)
6. Scott Soderling [View author publications](/search?author=Scott%20Soderling) Search author on: [PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Scott%20Soderling) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Scott%20Soderling%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)
7. Rohit Singh [View author publications](/search?author=Rohit%20Singh) Search author on: [PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Rohit%20Singh) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Rohit%20Singh%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)

### Contributions

K.D., S.S. and R.S. conceived of the project. S.S. and R.S. supervised the overall project. K.D. and Y.S.K. led the software implementation, with inputs from R.S. The fluorescent protein and TurboID validation experiments were performed by D.S. and J.M. The first draft was written by K.D., D.S., S.S. and R.S. All authors edited the manuscript and subsequent revisions. W.W., S.S. and R.S. secured funding for the project.

### Corresponding authors

Correspondence to [Scott Soderling](mailto:scott.soderling@duke.edu) or [Rohit Singh](mailto:rohit.singh@duke.edu) .

## Ethics declarations

### Competing interests

The authors declare no competing interests.

## Peer review

### Peer review information

*Nature* thanks Yunan Luo, Martin Steinegger and the other, anonymous, reviewer for their contribution to the peer review of this work. [Peer reviewer reports](/articles/s41586-026-10842-8#MOESM3) are available.

## Additional information

**Publisher's note** Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

## Extended data figures and tables

### [Extended Data Fig. 1 Fixed-length embedding values exhibit unimodal distributions under sequence variation, with possible heavy tails.](/articles/s41586-026-10842-8/figures/5)

We analyzed how sequence variations affect the distribution of values at five randomly selected positions in the 50 × 280 Raygun fixed-length embedding. For each of three large proteins---CFTR (1480 aa), MTOR (2549 aa), and Huntingtin (3142 aa)---we performed 2000 independent trials where we randomly selected a substitution rate between 0 and 6.7% (100/1480 for CFTR), applied random substitutions, computed the Raygun representation, and extracted values at the specified positions. ShapiroWilk test statistics are shown for all 15 distributions (5 positions times 3 proteins). While the null hypothesis that these distributions are Gaussian is rejected (p &lt; 10 −4 ), the distributions are clearly unimodal and the median Shapiro-Wilk statistic is 0.96, suggesting only a mild deviation from normality (1 indicates normality). Despite these deviations from strict normality, the multivariate normal approximation used in Raygun's sampling procedure proves effective in practice.

### [Extended Data Fig. 2 Training, sampling and ablation results.](/articles/s41586-026-10842-8/figures/6)

(a) Graphical visualization of reconstruction, cross-entropy and replicate losses. (b) Training and validation BLOSUM scores for K = 25 and K = 50 on the Swissprot dataset. (c) Train and validation BLOSUM scores for epochs 1-15. (d) Diagram showing the computation of pLL score of a protein sequence. The process involves position-wide averaging of the ESM-2 650 M logit values of the correct residues, culminating in a fast and powerful metric for assessing protein fitness. (e) Plot of sequence length vs *pLL* scores observed for a sample of Uniref50 proteins.

### [Extended Data Fig. 3 Sequence and function-based evaluations.](/articles/s41586-026-10842-8/figures/7)

(a) Comparison of functional site preservation of three proteins (EGFP, mCherry and RAS) using Raygun and greedy *pLL* -maximizing strategies using ESM-C or ESM-2. We tested if the small-but-critical functional sites in each protein (EGFP: *TYG* , mCherry: *MYG* , RAS: *GxxxxGKS* ) are preserved even as sequence variability is introduced. Compared to the baselines, Raygun (under noise 0.05 and 0.5) was able to preserve the sites more consistently despite generating comparable or higher sequence variation. (b) Secondary structure insertion preference of Raygun generated candidates at different degrees of magnification. (c) The Raygun encoder's contribution to reconstruction accuracy increases with model scale. We show an ablation analysis comparing full Raygun models against encoder-ablated versions ("Decoder-Large" and "Decoder-Small") on 1,000 human and mouse proteins from SwissProt. "Naive" is a model that has neither the encoder nor the decoder, using only the reduction and repetition layers. For the smaller model trained on 100 K sequences (Raygun-Small), the decoder provides most reconstruction capability, as seen by the near-equal performance of the Raygun-Small and Decoder-Small models. However, for the larger model trained on 2.2 M sequences (Raygun-Large), the encoder becomes increasingly important, demonstrating that at scale, the encoder enriches fixed-length embeddings with functional information beyond what single-step reduction captures from baseline ESM-2 embeddings. Similar results are seen for CATH domain classification, though all models were able to preserve CATH domains with accuracy &gt;90%. (d) Average PFAM domain retention rates across four structural classes (α-only, β-only, α/β, and α + β) comparing Raygun-generated sequences against a random baseline with matched indel and substitution rates. Both sets were filtered using identical *pLL* -based selection. Raygun preserves PFAM domains 14.75% more effectively than the baseline across length modifications ranging from 50-200% of template length. (e) Comparison of sequence identity between template and generated sequences using baseline (unfinetuned) versus fine-tuned Raygun models on 100 randomly selected SwissProt proteins. We evaluated both same-length reconstruction and 20% length reduction across noise parameters from 0.1 to 2.0, quantifying diversity by measuring the proportion of sequence residues changed. Fine-tuning shows minimal impact on sequence diversity, with both models producing comparable increases in diversity with noise. The only notable difference occurs at very low noise (0.1), where fine-tuning improves reconstruction accuracy as expected. (f) Normalized sequence identity of Raygun-generated sequences at different levels of length reduction (noise = 0).

### [Extended Data Fig. 4 Raygun architecture.](/articles/s41586-026-10842-8/figures/8)

(a) The encoder takes ESM-2 protein language model (PLM) representations as input and processes them through a series of cascades, each consisting of an Encoder TransformerLayer (TE) block and a Reduction layer. After passing through the TE block, the variable-length representation is compressed into a fixed-length representation by the Reduction layer and then passed through the same TE block again (parameter sharing is indicated by the dashed line). The TE-processed variable-length representation also serves as the input to the next cascade. Fixed-length outputs from all cascades are aggregated and linearly projected to produce a final latent representation of dimensions 50 × 1280. The decoder comprises complementary cascades, each containing two Decoder TransformerLayer (TD) blocks and a Repetition layer, which expands the fixed-length latent representation to a user-specified output length. As in the encoder, outputs from all cascades are aggregated and linearly projected to produce a final reconstructed representation of dimensions *N* × 1280. (b) Schematic illustration of the Reduction and Repetition layers. (c) Overview of the length-modification and sampling workflow. The Raygun autoencoder accepts a PLM representation as input and generates a reconstruction at a specified target length. This reconstructed representation is subsequently passed through a separately trained ESM-2 decoder to produce the final length-modified protein sequence.

### [Extended Data Fig. 5 Evaluation of Raygun's template-guided design.](/articles/s41586-026-10842-8/figures/9)

(a) Deletion preference of Raygun for secondary structure elements (SSEs). Here, "loops" refers to all non α and β residues. Raygun operates equitably across SSEs, with a slight preference for deleting loops. (w.r.t. = with respect to). (b) Ratio of Raygun preserved functional sites to the overall sequence preservation, during deletion. The ratio is consistently greater than 1, indicating that Raygun preferentially preserves active and binding sites. (c) Clustering comparison between ESM-2 and Raygun's fixed-length embeddings. The ARI and NMI scores show that the fixedlength embeddings produce clusters that are better aligned with the CATH structural hierarchy. (d, e) Structural and sequence measures for Raygun candidates at different noise and lengthmodification regimes. (d) The noise parameter controls substitution rates. (e) Proteins can be expanded/shrunk by up to 10% with modest loss in predicted structural fidelity. (f) Same-length evaluation, where we benchmarked the Raygun pipeline against the in-painting design approaches of EvoDiff and DPLM. Raygun generated sequences show comparable structural properties to the existing in-painting methods.

### [Extended Data Fig. 6 Additional structural evaluations using Omegafold.](/articles/s41586-026-10842-8/figures/10)

(a) For the same candidates as in Extended Data Fig. [5](/articles/s41586-026-10842-8#Fig9) , we show pLDDT, perplexity, seq. identity and TMscore results, after changing candidates' lengths, for noise-factors 0.5 and 1.0. (b) LDDT measurements (against the template) of the Raygun generated candidates at two design settings: i) at different degrees of length-modifications, while keeping the noise input fixed at 0.1. ii) at different noise-regimes, while setting the target length same as the original.

### [Extended Data Fig. 7 Additional structural evaluations using Boltz-2.](/articles/s41586-026-10842-8/figures/11)

(a) For the same candidates as in Extended Data Fig. [5](/articles/s41586-026-10842-8#Fig9) , we show pTM, pLDDT and TM-score results after changing candidates' lengths, for noise-parameter 0.5. (b) pTM, pLDDT and TM-score results at different noise settings, while specifying the target length to be the same as the original.

### [Extended Data Fig. 8 Demonstrating Raygun's effectiveness in preserving diverse structural features, as indicated by PFAM domains.](/articles/s41586-026-10842-8/figures/12)

We evaluated across all four major SCOP classes: (a) α-only ( *PF00001* ), (b) β-only ( *PF10282* ), (c) α/β ( *PF04794* ), (d) α + β ( *PF01996* ). For each PFAM domain, we obtained 5 representative proteins of diverse sizes and used Raygun to generate 100 samples (per template) spanning a wide length interval (50-200% of median family length). After dividing the overall interval into 20 uniform length-bins, we report the number of Raygun candidates with retained PFAM domains across each bin. Additionally, for a selected number of candidates in each domain, we also provide their AlphaFold3-inferred structures and metrics (pLDDT and TM-score). The template protein's structure is shown as a gray background.

### [Extended Data Fig. 9 Enzymatic and functional analysis.](/articles/s41586-026-10842-8/figures/13)

(a) Raygun maintains functional similarity under moderate length modifications as assessed by protein language model predictions. We show ProTrek similarity scores comparing Gene Ontology (GO) annotations of templates versus ProTrek-predicted functional annotations for Raygun-generated sequences at length modifications from 50-200% of the original length. We evaluated 24 templates from the PFAM analysis spanning four SCOP classes (one protein excluded due to missing GO annotations). For 14 of 19 templates, all candidates within ±10% of template length achieved ProTrek scores &gt;10, indicating strong functional conservation. Scores decline with more extreme length modifications, as expected, but remain elevated for most templates even at 50% miniaturization. (b) Raygun achieves comparable functional retention to state-of-the-art inpainting methods in same-length sequence generation. We benchmarked Raygun against EvoDiff and DPLM using 60 enzymatic proteins (10 from each of six EC categories; we excluded Translocases 7.*.*.* because of the category's small size). For each template, we generated variants with comparable sequence identity distributions across methods: modulating sampling noise for Raygun and adjusting masked residue proportions for inpainting models. CLEAN-predicted EC labels were used to assess functional preservation across four sequence identity tiers (60-70%, 70-80%, 80-90%, 90-100%). Raygun shows comparable functional retention to existing inpainting methods. We note that this evaluation does not assess indels because EvoDiff and DPLM are unable to perform indel-based mutations. (c) We used CLEAN to predict enzyme commission (EC) numbers for miniaturized variants of 13 human protein tyrosine kinase templates (EC 2.7.10.1). For each Raygun candidate, we generated 10 baseline sequences with identical indel and substitution counts, selecting the highest *pLL* baseline. CLEAN prediction scores show that Raygun-generated sequences retain the correct EC classification substantially better than baselines at both 60% and 70% of original template length.

### [Extended Data Fig. 10 Raygun maintains protein-nucleic acid binding interfaces under aggressive miniaturization of spCas9, a multi-domain protein.](/articles/s41586-026-10842-8/figures/14)

We miniaturized spCas9 to 6575% of its original length (900-1000 residues) and used AlphaFold3 to predict ternary complex structures with DNA and RNA. Predicted interface quality metrics (iPTM and PTM scores) show that Raygun-generated candidates maintain superior structural stability and preserve nucleic acid binding interfaces compared to sequence-matched random baselines with identical indel and substitution rates.

## Supplementary information

### [Supplementary Information (download PDF )](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-026-10842-8/MediaObjects/41586_2026_10842_MOESM1_ESM.pdf)

Supplementary Methods and Notes

### [Reporting Summary (download PDF )](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-026-10842-8/MediaObjects/41586_2026_10842_MOESM2_ESM.pdf)

### [Peer Review file (download PDF )](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-026-10842-8/MediaObjects/41586_2026_10842_MOESM3_ESM.pdf)

## Rights and permissions

**Open Access** This article is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License, which permits any non-commercial use, sharing, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if you modified the licensed material. You do not have permission under this licence to share adapted material derived from this article or parts of it. The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit [http://creativecommons.org/licenses/by-nc-nd/4.0/](http://creativecommons.org/licenses/by-nc-nd/4.0/) .

[Reprints and permissions](https://s100.copyright.com/AppDispatchServlet?title=Miniaturizing%20and%20modifying%20natural%20proteins%20with%20Raygun&author=Kapil%20Devkota%20et%20al&contentID=10.1038%2Fs41586-026-10842-8&copyright=The%20Author%28s%29&publication=0028-0836&publicationDate=2026-07-29&publisherName=SpringerNature&orderBeanReset=true&oa=CC%20BY-NC-ND)

## About this article

Check for updates. Verify currency and authenticity via CrossMark

<!-- image -->

### Cite this article

Devkota, K., Shonai, D., Mao, J. *et al.* Miniaturizing and modifying natural proteins with Raygun. *Nature* (2026). https://doi.org/10.1038/s41586-026-10842-8

[Download citation](https://citation-needed.springer.com/v2/references/10.1038/s41586-026-10842-8?format=refman&flavour=citation)

- Received : 15 March 2025
- Accepted : 24 June 2026
- Published : 29 July 2026
- Version of record : 29 July 2026
- DOI : https://doi.org/10.1038/s41586-026-10842-8

[Download PDF](/articles/s41586-026-10842-8.pdf)

## Associated content

### [This AI Raygun can shrink and supersize proteins - opening the door to easy editing](https://www.nature.com/articles/d41586-026-02335-5)

- Gemma Conroy

Nature News

29 Jul 2026

Advertisement

## Explore content

- [Research articles](/nature/research-articles)
- [News](/news)
- [Opinion](/opinion)
- [Research Analysis](/research-analysis)
- [Careers](/careers)
- [Books &amp; Culture](/books-culture)
- [Podcasts](/nature/podcasts)
- [Videos](/nature/videos)
- [Current issue](/nature/current-issue)
- [Browse issues](/nature/browse-issues)
- [Collections](/nature/collections)
- [Subjects](/nature/browse-subjects)

- [Follow us on Facebook](https://www.facebook.com/Nature)
- [Follow us on Bluesky](https://bsky.app/profile/nature.com)
- [Follow us on X](https://twitter.com/nature)
- [Sign up for alerts](https://journal-alerts.springernature.com/subscribe?journal_id=41586)
- [RSS feed](https://www.nature.com/nature.rss)

## About the journal

- [Journal Staff](/nature/journal-staff)
- [About the Editors](/nature/editors)
- [Research Cross-Journal Editorial Team](/nature/research-cross-journal-editorial-team)
- [Journal Information](/nature/journal-information)
- [Journal Metrics](/nature/journal-impact)
- [Our publishing models](/nature/our-publishing-models)
- [Editorial Values Statement](/nature/editorial-values-statement)
- [Editorial policies](/nature/editorial-policies)
- [Journalistic Principles](/nature/journalistic-principles)
- [History of Nature](/nature/history-of-nature)
- [Awards](/nature/awards)
- [Contact](/nature/contact)
- [Send a news tip](/nature/send-a-news-tip)

## Publish with us

- [For Authors](/nature/for-authors)
- [For Referees](/nature/for-referees)
- [Language editing services](https://authorservices.springernature.com/go/sn/?utm_source=For+Authors&utm_medium=Website_Nature&utm_campaign=Platform+Experimentation+2022&utm_id=PE2022)
- [Open access funding](/nature/open-access-funding)
- [Submit manuscript](https://mts-nature.nature.com/)

## Search

Search articles by subject, keyword or author

q

Show results from

All journals

This journal

Search

[Advanced search](/search/advanced)

### Quick links

- [Explore articles by subject](/subjects)
- [Find a job](/naturecareers)
- [Guide to authors](/authors/index.html)
- [Editorial policies](/authors/editorial_policies)

## nature.com footer links

### About Nature Portfolio

- [About us](https://www.nature.com/npg_/company_info/index.html)
- [Press releases](https://www.nature.com/npg_/press_room/press_releases.html)
- [Press office](https://press.nature.com/)
- [Contact us](https://support.nature.com/support/home)

### Discover content

- [Journals A-Z](https://www.nature.com/siteindex)
- [Articles by subject](https://www.nature.com/subjects)
- [protocols.io](https://www.protocols.io/)
- [Nature Index](https://www.natureindex.com/)

### Publishing policies

- [Nature portfolio policies](https://www.nature.com/authors/editorial_policies)
- [Open access](https://www.nature.com/nature-research/open-access)

### Author &amp; Researcher services

- [Reprints &amp; permissions](https://www.nature.com/reprints)
- [Research data](https://www.springernature.com/gp/authors/research-data)
- [Language editing](https://authorservices.springernature.com/language-editing/)
- [Scientific editing](https://authorservices.springernature.com/scientific-editing/)
- [Nature Masterclasses](https://masterclasses.nature.com/)
- [Research Solutions](https://solutions.springernature.com/)

### Libraries &amp; institutions

- [Librarian service &amp; tools](https://www.springernature.com/gp/librarians/tools-services)
- [Librarian portal](https://www.springernature.com/gp/librarians/manage-your-account/librarianportal)
- [Open research](https://www.nature.com/openresearch/about-open-access/information-for-institutions)
- [Recommend to library](https://www.springernature.com/gp/librarians/recommend-to-your-library)

### Advertising &amp; partnerships

- [Advertising](https://partnerships.nature.com/product/digital-advertising/)
- [Partnerships &amp; Services](https://partnerships.nature.com/)
- [Media kits](https://partnerships.nature.com/media-kits/)
- [Branded content](https://partnerships.nature.com/product/branded-content-native-advertising/)

### Professional development

- [Nature Awards](https://www.nature.com/immersive/natureawards/index.html)
- [Nature Careers](https://www.nature.com/naturecareers/)
- [Nature Conferences](https://conferences.nature.com/)

### Regional websites

- [Nature Africa](https://www.nature.com/natafrica)
- [Nature China](http://www.naturechina.com/)
- [Nature India](https://www.nature.com/nindia)
- [Nature Japan](https://www.natureasia.com/ja-jp)
- [Nature Middle East](https://www.nature.com/nmiddleeast)

- [Privacy Policy](https://www.nature.com/info/privacy)
- [Use of cookies](https://www.nature.com/info/cookies)
- Your privacy choices/Manage cookies
- [Legal notice](https://www.nature.com/info/legal-notice)
- [Accessibility statement](https://www.nature.com/info/accessibility-statement)
- [Terms &amp; Conditions](https://www.nature.com/info/terms-and-conditions)
- [Your US state privacy rights](https://www.springernature.com/ccpa)

Springer Nature

<!-- image -->

© 2026 Springer Nature Limited

Close

Nature Briefing

<!-- image -->

Sign up for the *Nature Briefing* newsletter - what matters in science, free to your inbox daily.

Email address

e.g. jo.smith@university.ac.uk

Sign up

- [ ] I agree my information will be processed in accordance with the Nature and Springer Nature Limited Privacy Policy.

I agree my information will be processed in accordance with the *Nature* and Springer Nature Limited [Privacy Policy](https://www.nature.com/info/privacy) .

Close

Get the most important science stories of the day, free in your inbox. [Sign up for Nature Briefing](https://www.nature.com/briefing/signup/?brieferEntryPoint=MainBriefingBanner)