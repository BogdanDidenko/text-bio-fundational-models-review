## Lineage-Independent Structural Risk Detection in SARSCoV-2 Spike Protein via Zero-Shot Protein Language Modeling

###### Richard Armuelles

Telos Genomics · Veraguas, Panama

Correspondence: richard.armuelles@telosgenomics.bio

## Abstract

Genomic surveillance pipelines typically classify SARS-CoV-2 variants against curated lineage dictionaries, creating a structural 'blind window' of days to weeks between a variant's public sequence deposition and formal risk characterization. Here we present a zero-shot structural risk quantification framework that applies the protein language model ESM-2, without fine-tuning on epidemiological outcome labels, to estimate destabilization at functionally weighted positions (receptor-binding motif, receptor-binding domain, furin cleavage site) of the SARS-CoV-2 spike protein, yielding a composite Aggression Score. We retrospectively evaluated this framework against four GenBank isolates spanning distinct evolutionary periods and lineage-dictionary coverage: Delta (B.1.617.2), Omicron BA.1 (the first confirmed B.1.1.529 genome detected in Europe), BF.11.3, and a 2026 isolate externally designated XFG.5.1.7. Two of these isolates (BF.11.3 and XFG.5.1.7) lack dedicated entries in the reference signature dictionary, yet both were correctly flagged with elevated Aggression Scores; the latter was analyzed five days after its public release on GenBank. Independent isolates of Omicron BA.1 and BF.11.3 additionally converged on structurally equivalent forecasts at the furin cleavage site despite substantial genomic and temporal separation. These results indicate that structural risk quantification via masked-token log-likelihood ratios can operate independently of lineage-dictionary coverage, in contrast to approaches reliant on curated reference signatures or supervised fitness models. We interpret these findings as retrospective consistency rather than prospective predictive validation, and outline the isolate-level evaluation required to establish this class of metric as a genuine earlywarning signal.

## 1. Introduction

### 1.1 The Problem: The High Cost of Reactive Surveillance

Current genomic surveillance systems operate fundamentally in a retrospective mode. Standard pipelines, such as Pangolin or Nextclade, are designed for lineage assignment based on established reference patterns. While effective for tracking, these systems function as a genomic autopsy: they characterize the pathogen only after it has achieved significant community transmission.

This reactive paradigm creates a 'blind window' between initial sequence deposition and formal variant characterization. For example, the World Health Organization's risk evaluation of BA.2.86 - the ancestral lineage of JN.1 - reports an earliest collected sample dated July 24, 2023, with the lineage and its then-emerging descendants formally classified as a Variant of Interest on November 21, 2023 (World Health Organization, 2023): an interval of approximately four months. During such intervals, variants with high structural fitness or immune evasion potential can establish transmission chains before containment efforts are informed by formal lineage characterization.

In contrast, this work evaluates the capacity of high-capacity protein language models to autonomously map viral fitness landscapes without prior epidemiological outcome labels. By operating in a strictly zero-shot regime, the proposed framework leverages the intrinsic structural heuristics embedded within ESM-2 to quantify mutational constraints at critical functional domains before phenotypic data aggregates in public registries.

### 1.2 The Opportunity: Structural Biology as Early Warning

Recent advances in protein language models (PLMs) have demonstrated that transformer architectures trained on large evolutionary datasets encode implicit knowledge of thermodynamic constraints and mutational fitness landscapes. ESM-2 (Lin et al., 2023) represents a widely used implementation of this class of model, achieving structural insight directly from primary sequences without explicit structural input.

This study applies ESM-2 not as a classifier, but as a zero-shot thermodynamic probe: by assigning log-likelihood ratios to amino acid substitutions within their structural context, mutations under evolutionary pressure can be identified directly from primary sequence data, independent of curated lineage classification. We evaluate whether this approach can identify structurally consequential mutations in retrospective SARS-CoV-2 isolates, including isolates for which no dedicated lineage signature exists in a reference dictionary.

## 2. Methods

### 2.1 System Architecture

The framework evaluated in this study (Telos-S) is implemented as a modular pipeline comprising four stages relevant to this work: (i) sequence ingestion and quality control, (ii) biological coordinate anchoring, (iii) the Aggression Score engine, and (iv) an evolutionary forecasting module (Telos Prophet). A fifth module translates Aggression Score outputs into exploratory geospatial projections; as this component has not undergone empirical validation against epidemiological data, it is discussed only briefly in §4.5 as a direction for future work and is excluded from the results reported here.

### 2.2 Sequence Ingestion and Quality Control

Each query sequence is classified at the residue level into three tiers: Trusted ( 𝑀𝑇 ), residues outside any exclusion zone and eligible for scoring; Suspicious ( 𝑀𝑆 ), valid residues within a ±5residue buffer of an ambiguous ('X') position, excluded from scoring because ESM-2's selfattention mechanism requires a clean local context window, nearby ambiguity contaminates loglikelihood estimates; and Invalid ( 𝑀𝐼 ), positions containing 'X' directly. Overall sequencing quality is quantified as the ratio of Trusted to total mutation counts:

<!-- formula-not-decoded -->

Only mutations classified as Trusted contribute to the Aggression Score.

### 2.3 Biological Coordinate Anchoring

To resolve coordinate drift from insertions and deletions, each query sequence is aligned against the Wuhan-Hu-1 reference (NC\_045512.2) via pairwise global alignment (gap open: -10, gap extend: -0.5), enforcing strict 1,273-residue indexing: deletions are represented as gap characters to preserve reference numbering, while insertions lacking a canonical reference position are discarded. This ensures consistent indexing of functional sites (receptor-binding motif, furin cleavage site) across variants of differing length.

### 2.4 Aggression Score

The composite Aggression Score formulated here is not an arbitrary software output but an interpretable, biologically grounded proxy for structural destabilization and evolutionary fitness. Byevaluating residue-level conservation alongside language-model log-likelihoods at functionally weighted hotspots (e.g., the furin cleavage site and receptor-binding motif), the score probes whether deep statistical representations of protein sequences can anticipate selection pressures. This approach bypasses the need for explicit training on epidemiological parameters such as transmission rate ( 𝑅0 ) or hospitalization outcomes, relying instead on the model's capacity to infer structural fitness constraints directly from sequence.

### 2.4.1 Aggression Score Formulation

The Aggression Score ( 𝒜 ) quantifies cumulative structural-functional risk as the sum of absolute per-mutation risk contributions over the Trusted mutation set. Each per-mutation contribution combines the zone weight and the signed ESM-2 log-likelihood ratio additively, with the absolute value operator applied to the combined term rather than to its components in isolation:

<!-- image -->

- 𝑴𝑻 (Trusted Mutations): The set of mutations residing outside the ±5 residue exclusion zones.

##### Where:

- 𝝎 𝒛 𝒊 (Zone Weight): A domain-specific multiplier assigned based on the biological significance of the region z in which mutation i occurs (defined in §2.4.2).
- 𝒄₁ , 𝒄₂ (Scaling Constants): Fixed coefficients (c₁ = 20, c₂ = 10 in the current implementation) that set the relative contribution of zone membership versus modelassigned structural deviation to the per-mutation score. As with the zone weights (§2.4.2) and the Prophet alert threshold (§2.5.2), these constants were set heuristically rather than derived through formal statistical optimization; this is discussed further as a limitation in §4.4.
- 𝜻 𝒊 (Signed Structural Magnitude): The signed log-likelihood ratio (LLR) assigned by ESM-2 to the observed substitution at position i, computed by masking the reference residue and comparing model-assigned probabilities for the reference versus observed amino acid. Unlike a purely magnitude-based formulation, ζ ᵢ retains its sign prior to combination with the zone weight; the absolute-value operator is applied only to the combined per-mutation term.

Unlike Telos Prophet (§2.5), which restricts analysis to four positions of established functional significance and reports position-specific forecasts, the Aggression Score aggregates risk contributions across all Trusted mutations without position-specific weighting beyond zone membership; the current implementation does not include a distinct position-sensitivity term.

### 2.4.2 Biological Zone Classification

Telos-S prioritizes mutations based on their location within the spike protein's functional architecture. Table 1 defines the weighting coefficients currently implemented in the analysis pipeline.

| Zone                          | Biological Function                                                   | Weight 𝒘 𝒛 𝒊    |
|-------------------------------|-----------------------------------------------------------------------|-----------------|
| RBM(Receptor Binding Motif)   | Direct ACE2 interface; primary target for neutralizing antibodies.    | 3.0x            |
| RBD (Receptor Binding Domain) | Structural scaffold for ACE2 binding; contains critical epitopes.     | 2.0x            |
| Furin Cleavage Site           | Essential for proteolytic activation and cell-cell fusion (Syncytia). | 1.5x            |
| Other Regions                 | Structural integrity and conformational stability of the S-protein.   | 1.0x (baseline) |

####### Table 1. Biological zone weighting coefficients as implemented in the current pipeline.

Zone weights reflect each region's relevance to immune-evasion-driven structural risk specifically, rather than transmissibility in general. The receptor-binding motif (RBM), which forms the direct interface with both ACE2 and neutralizing antibodies, receives the highest weight. The receptor-binding domain (RBD), a structural scaffold containing additional epitopes (Zahradník et al., 2021), receives an intermediate weight. The furin cleavage site, which governs proteolytic activation and cell-cell fusion efficiency and is therefore mechanistically tied to transmission efficiency rather than to immune escape (Peacock et al., 2021), receives a comparatively lower weight among the three functional zones, while still exceeding the structural baseline. We emphasize that these weights were assigned heuristically on the basis of established structural biology literature, rather than derived through formal statistical calibration against epidemiological outcome data; this is discussed further as a limitation in §4.4.

### 2.5 Evolutionary Forecasting

### 2.5.1 Rationale: From Classification to Trajectory Projection

While standard genomic tools provide a static "genomic autopsy", Telos Prophet (the forecasting module) models protein evolution as a constrained optimization problem within a multi-dimensional fitness landscape. The core hypothesis is that viral lineages navigate a "structural search space" where mutations are filtered by their impact on protein fold stability and functional competence.

Prophet acknowledges a critical biological trade-off: evolution does not optimize for thermodynamic stability in isolation. A virus may tolerate a destabilizing mutation if it facilitates immune evasion or increased ACE2 affinity. Consequently, Prophet reports Structural Transition Probabilities ( 𝑷𝒔𝒕 ) as a signal of structural favorability, identifying the "paths of least resistance" that the virus is structurally equipped to take.

### 2.5.2 Methodology

Prophet performs a localized Deep Mutational Scan (DMS) in silico for every residue within high-priority functional domains (RBM positions 452, 484, 501; Furin cleavage site 681). The process follows a three-step algorithmic sequence:

1. Likelihood Profiling: Prior to inference, a complete Wuhan Coordinate Map is constructed - a direct lookup table mapping each canonical Wuhan-Hu-1 residue position (1-1273) to its corresponding index in the aligned variant sequence, computed in a single O(n) traversal of the aligned sequence by counting non-gap characters sequentially. For each target position p, this map resolves the exact index in the variant sequence regardless of the residue identity at that position, enabling correct localization even in highly mutated variants where the reference amino acid has itself been substituted. The reference residue at p is masked, and ESM-2 is queried once to produce raw output logits over its full tokenizer vocabulary, conditioned on the specific sequence context of the variant.
2. Normalization and Scoring: The masked-position logits are converted directly into a probability distribution via softmax, yielding a structural transition probability for each candidate residue:

<!-- formula-not-decoded -->

Where V denotes the ESM-2 tokenizer vocabulary (33 tokens, comprising the 20 canonical amino acids together with special and ambiguity tokens). Unlike the Aggression Score (§2.4.1), which computes a log-likelihood ratio between two specific model-assigned probabilities (reference versus observed residue), Prophet's transition probabilities are read directly from this single softmax distribution without an intermediate ratio step; the five highest-probability candidates are retained for reporting.

3. Alert Thresholding: A position is flagged with ALERT status if 𝑃𝑠𝑡 &gt;𝜏 , where 𝜏 is a heuristically selected threshold equal to 20% . This threshold reflects two considerations rather than a formal statistical calibration. First, if transition probability mass were spread uniformly across the 19 alternative canonical amino acids (excluding the reference residue), a practical interpretive baseline distinct from the full 33-token softmax denominator described in §2.5.2, since the model assigns negligible mass to special and ambiguity tokens at genuine sequence positions, each alternative would receive approximately 5.3% (1/19); a threshold of 20% represents nearly four times this baseline, requiring the model to indicate a genuine structural preference for a specific substitution rather than incidental tolerance. Second, within the four isolates examined

in this study, furin cleavage site transition probabilities associated with the dominant predicted substitution ranged from 22.4% to 29.7% (§3.3-3.4); a threshold of 20% remains sensitive to this observed range while limiting false-positive inflation in highplasticity zones (e.g., RBM, furin cleavage site), where multiple substitutions can individually exceed background probability without indicating a dominant evolutionary trajectory. We emphasize that this threshold was set heuristically rather than derived through formal statistical optimization (e.g., receiver-operating-characteristic analysis) against a labeled outcome dataset; this is discussed further as a limitation in §4.4.

### 2.5.3 The "Clean-Context" Exclusion Protocol

To limit false-positive alerts arising from low-quality sequencing rather than genuine structural signal, Prophet enforces a conservative exclusion protocol. No forecasts are generated for positions classified as Suspicious or Invalid by the quality-control module (§2.2). Further, if any residue within ±5 positions of a target site in the aligned sequence is classified as Invalid ('X'), the prediction for that position is withheld entirely. This exclusion buffer is distinct from the coordinate-resolution mechanism described in §2.5.2, position localization via the Wuhan Coordinate Map always proceeds independently of local sequence quality and applies only to quality filtering after localization. This protocol ensures that every Prophet alert is backed by a high-fidelity structural context, reducing the likelihood that low-quality sequencing data produces spurious alerts.

### 2.6 Validation Dataset

Isolate selection followed a two-stage rationale. First, three isolates with well-documented epidemiological trajectories and established consensus in the peer-reviewed literature (Delta, Omicron BA.1, and BF.11.3) were selected to establish internal validity: because the clinical and transmission impact of these variants is already characterized, agreement between Aggression Score outputs and known outcomes indicates that the framework captures biologically meaningful signal rather than producing arbitrary numerical output. Only after this internal consistency was established did we extend evaluation to a genuinely novel case.

Second, the 2026 isolate externally designated XFG.5.1.7 was selected specifically because it lacked a dedicated entry in the reference lineage-signature dictionary at the time of analysis. This isolate serves as a direct test of the framework's core motivating premise: that structural risk can be quantified from primary sequence data before formal lineage characterization becomes available. This scenario is not merely hypothetical, SARS-CoV-2 sublineages have repeatedly demonstrated the capacity to circulate at low, near-undetectable prevalence for extended periods before undergoing rapid expansion and renewed public health concern, sometimes months after their sequences were already publicly deposited. A framework that depends on curated lineage dictionaries to flag risk is structurally unable to anticipate this re-emergence pattern until formal classification catches up; a framework operating on primary sequence data alone is not subject to this constraint.

Four GenBank isolates were selected accordingly, spanning distinct evolutionary periods, sequencing quality profiles, and lineage-dictionary coverage status: Delta (B.1.617.2; accession OK091006.1, Japan, 2021), Omicron BA.1 (accession OL672836.1, Belgium, 2021, the first confirmed B.1.1.529 genome detected in Europe; Vanmechelen et al., 2022), BF.11.3 (accession PX916454.1, Canada, collected 2022 / released 2026), and the 2026 isolate externally designated XFG.5.1.7 (accession PZ155177.1, USA). The latter two isolates lack dedicated entries in the reference lineage-signature dictionary, allowing evaluation of Aggression Score performance independent of lineage-dictionary coverage. All isolates were retrieved directly from NCBI GenBank; no proprietary or access-restricted databases were used at any stage.

## 3. Results

### 3.1 Retrospective Consistency Across Evolutionary Checkpoints

Table 1 summarizes Aggression Score ( 𝒜 ) outputs across four genomic isolates spanning distinct evolutionary periods and sequencing quality profiles.

Table 2. Structural risk quantification across four independently verified GenBank isolates.

| Isolate           | Accession   | Origin / Date                      |   𝒜 Score | Q ᵣ    |   Reliable Mutations | Risk Classification Tier   |
|-------------------|-------------|------------------------------------|-----------|--------|----------------------|----------------------------|
| Delta (B.1.617.2) | OK091006.1  | Japan, 2021                        |     210.6 | 63.64% |                    7 | Baseline                   |
| Omicron BA.1      | OL672836.1  | Belgium, 2021 (first EU detection) |   1,074.4 | 100%   |                   33 | Elevated Risk              |
| BF.11.3           | PX916454.1  | Canada, 2022 (released 2026)       |     966.5 | 90.32% |                   27 | Elevated Risk              |
| XFG.5.1.7         | PZ155177.1  | USA, 2026                          |   2,280.5 | 100%   |                   69 | Critical Alteration        |

Delta's lower Q ᵣ reflects localized 'X' ambiguity in the query sequence, correctly triggering the conservative exclusion protocol described in §2.2.

### 3.2 Lineage Identification Fidelity

Delta and Omicron BA.1 both possessing dedicated signatures in the reference dictionary, were correctly classified at 100% confidence, confirming baseline signature-matching accuracy against well-characterized lineages.

### 3.3 Cross-Sequence Predictive Consistency

Independent isolates of Omicron BA.1 (Belgium, 2021) and BF.11.3 (Canada, 2022/2026) both triggered high-confidence Telos Prophet alerts at the furin cleavage site (position 681), predicting a structural transition toward serine (S) with nearly identical probabilities (22.4% and 22.5% respectively), despite substantial genomic and temporal separation between isolates.

### 3.4 Structural Risk Detection Independent of Lineage-Dictionary Coverage

Two isolates lacking dedicated lineage signatures: BF.11.3 (84.6% nearest-match to BA.1) and PZ155177/XFG.5.1.7 (87.5% nearest-match to KP.3.1.1), were nonetheless correctly flagged as elevated structural risk, at Aggression Scores of 966.5 and 2,280.5 respectively. For PZ155177, this analysis was completed on March 21, 2026, five days after the isolate's public release on GenBank (LOCUS date: March 16, 2026), yielding 69 reliable mutations and the highest risk score across the validation set. This recurrence across two independently sourced isolates indicates that Aggression Score quantification does not depend on lineage-dictionary coverage for the specific sublineage under analysis.

## 4. Discussion

### 4.1 Positioning Relative to Existing Structural and Fitness-Prediction Frameworks

This framework occupies a distinct methodological niche relative to two closely related approaches. EVEscape (Thadani et al., 2023) combines a generative evolutionary model with biophysical and structural features to quantify immune-escape potential specifically, and is explicitly designed to operate before surveillance sequencing or experimental antibody data are available. CoVFit (Ito et al., 2025) fine-tunes ESM-2 on genotype-fitness data derived from viral surveillance and immune-evasion assays to predict relative effective reproduction number directly.

The approach evaluated here differs from both in that it applies the base ESM-2 model in a zeroshot configuration without fine-tuning on epidemiological outcome labels to estimate structural destabilization via masked-token log-likelihood ratios, weighted by biologically defined zones. This distinguishes the Aggression Score from CoVFit's supervised fitness estimate and from EVEscape's immune-escape-specific score: it is a general-purpose structural risk proxy that requires no training on prior variant outcome data, at the cost of not directly modeling immune escape or transmissibility as distinct, separable quantities.

### 4.2 Score Calibration and Interpretive Consistency

The relative magnitude of the Aggression Score across validation isolates is broadly consistent with known epidemiological outcomes: Delta ( 𝒜 = 210.6) reflects a period characterized by elevated transmissibility with comparatively moderate immune escape, while Omicron BA.1 ( 𝒜 = 1,074.4) associated with substantial global displacement of prior lineages and reported 3-4× increases in neutralization escape from vaccine-induced antibodies, shows a 5.1× increase in score. This correspondence suggests the Aggression Score may function as a coarse proxy for structural fitness escalation, though we emphasize this is an association observed across four isolates, not a validated predictive relationship; establishing predictive utility would require prospective testing against a larger, epidemiologically annotated cohort.

### 4.3 Lineage-Independent Risk Detection

A recurring pattern across two independently sourced isolates lacking dedicated lineage signatures (BF.11.3 and PZ155177/XFG.5.1.7) is that both were correctly flagged as elevated structural risk despite the absence of a matching entry in the reference signature dictionary. This is consistent with the framework's core design premise: because the Aggression Score is computed directly from primary sequence data rather than from lineage classification, it is not gated by the latency inherent in curating and updating lineage nomenclature and reference dictionaries, a latency that, as illustrated by the PZ155177 case (analyzed five days after GenBank release), can itself constitute a meaningful window during early variant emergence.

### 4.4 Limitations

Several constraints apply to the current implementation. First, the Aggression Score quantifies thermodynamic and conformational destabilization but does not directly model immune-evasion metrics such as antibody-binding affinity; its association with escape phenotypes, as discussed in §4.2, is inferential rather than mechanistic. Second, the current pipeline is specific to the SARSCoV-2 spike protein; generalization to other pathogens of pandemic concern has not been tested. Third, validation in this study is retrospective: all four isolates were analyzed after their epidemiological trajectories were already known (with the partial exception of PZ155177, analyzed shortly after public release but after the isolate's collection). Prospective validation - applying this framework to novel isolates before their clinical or epidemiological significance is established - has not yet been conducted and represents a necessary next step before the Aggression Score can be considered a validated early-warning metric rather than a retrospectively consistent one. Fourth, several numerical constants throughout the pipeline - the zone weights described in §2.4.2, the scaling coefficients c₁ and c₂ in the Aggression Score formulation (§2.4.1), and the Prophet alert threshold τ (§2.5.2) - were assigned heuristically on the basis of established structural biology literature and design judgment, rather than through formal statistical calibration against a labeled epidemiological outcome dataset. While directionally consistent with known biological roles, none of these constants have been optimized or validated quantitatively, and prospective work should treat them as adjustable hyperparameters rather than fixed constants.

### 4.5 Future Directions: From Structural Risk to Epidemiological Translation

The Aggression Score and Prophet outputs described here quantify structural risk at the sequence level but stop short of population-level projection. A downstream module (Telos-SIM) exists as an exploratory extension that maps Aggression Score outputs onto geospatial transmission scenarios; this component has not been validated against observed epidemiological data and is not part of the results reported in this study. We flag it here only to note that translating structural risk signals into calibrated, population-level forecasts validated prospectively against real transmission data is a necessary and distinct undertaking for future work, separate from the structural quantification methodology presented here.

## 5. Conclusion

This study presents a zero-shot structural risk quantification framework built on ESM-2, and evaluates it retrospectively against four SARS-CoV-2 spike protein isolates spanning distinct evolutionary periods, sequencing quality profiles, and lineage-dictionary coverage. Across these isolates, the Aggression Score showed internal consistency with known epidemiological trajectories, and the forecasting module independently converged on structurally equivalent predictions at the furin cleavage site across two genomically and temporally distant isolates (Omicron BA.1 and BF.11.3) a finding consistent with the existence of shared, invariant structural constraints on spike protein evolution at this position.

A central finding of this work is that structural risk quantification via the Aggression Score does not require a matching entry in a curated lineage-signature dictionary: both BF.11.3 and the 2026 isolate externally designated XFG.5.1.7 were correctly flagged as elevated risk despite lacking dedicated signatures. In the case of PZ155177 (XFG.5.1.7), structural analysis was completed five days after the isolate's public release on GenBank, illustrating that primary-sequence-based risk quantification can, in principle, operate within the same narrow window in which lineage classification and public health designation are typically still pending.

These results should be interpreted as retrospective consistency, not prospective predictive validation. All four isolates were analyzed after their broader evolutionary and epidemiological context was already established (PZ155177 being a partial exception, given its recency relative to this analysis). Establishing the Aggression Score as a genuine early-warning signal rather than a metric that is retrospectively coherent requires prospective evaluation on isolates whose epidemiological trajectory is not yet known at the time of analysis, ideally across a larger and more diverse validation cohort than the four isolates examined here.

## Data and Software Availability

All GenBank accessions analyzed in this study (OK091006.1, OL672836.1, PX916454.1, PZ155177.1) are publicly available via NCBI GenBank (https://www.ncbi.nlm.nih.gov/genbank). The complete software implementation, including the Aggression Score and Telos Prophet modules, is released under the MIT License across three public repositories:

Backend (analysis pipeline, Aggression Score and Telos Prophet implementation): https://github.com/Telos-Genomics/telos-s-backend

Frontend (user interface): https://github.com/Telos-Genomics/telos-s-frontend

Deployment orchestration (including the MCP server): https://github.com/TelosGenomics/telos-s-deploy

## References

- Ito, J., Strange, A., Liu, W., Joas, G., Lytras, S., The Genotype to Phenotype Japan (G2P-Japan) Consortium, &amp; Sato, K. (2025). A protein language model for exploring viral fitness landscapes. Nature Communications, 16(1), 4236. https://doi.org/10.1038/s41467-02559422-w
- Lin, Z., Akin, H., Rao, R., Hie, B., Zhu, Z., Lu, W., Smetanin, N., Verkuil, R., Kabeli, O., Shmueli, Y., dos Santos Costa, A., Fazel-Zarandi, M., Sercu, T., Candido, S., &amp; Rives, A. (2023). Evolutionary-scale prediction of atomic-level protein structure with a language model. Science, 379(6637), 1123-1130. https://doi.org/10.1126/science.ade2574
- NCBI Virus Database. National Center for Biotechnology Information. https://www.ncbi.nlm.nih.gov/labs/virus
- Peacock, T.P., Goldhill, D.H., Zhou, J., Baillon, L., Frise, R., Swann, O.C., Kugathasan, R., Penn, R., Brown, J.C., Sanchez-David, R.Y., Braga, L., Kavanagh Williamson, M., Hassard, J.A., Staller, E., Hanley, B., Osborn, M., Giacca, M., Davidson, A.D., Matthews, D.A., &amp; Barclay, W.S. (2021). The furin cleavage site in the SARS-CoV-2 spike protein is required for transmission in ferrets. Nature Microbiology, 6(7), 899-909. https://doi.org/10.1038/s41564-021-00908-w
- Thadani, N.N., Gurev, S., Notin, P., Youssef, N., Rollins, N., Ritter, D., Sander, C., et al. (2023). Learning from prepandemic data to forecast viral escape. Nature, 622(7984), 818-825. https://doi.org/10.1038/s41586-023-06617-0
- Vanmechelen, B., Logist, A.-S., Wawina-Bokalanga, T., Verlinden, J., Martí-Carreras, J., Geenen, C., Slechten, B., Cuypers, L., André, E., Baele, G., &amp; Maes, P. (2022). Identification of the first SARS-CoV-2 lineage B.1.1.529 virus detected in Europe. Microbiology Resource Announcements, 11(2), e01161-21. https://doi.org/10.1128/mra.01161-21
- World Health Organization. (2023, November 21). Initial risk evaluation of BA.2.86 and its sublineages. https://www.who.int/docs/defaultsource/coronaviruse/21112023\_ba.2.86\_ire.pdf
- Zahradník, J., Marciano, S., Shemesh, M., Zoler, E., Harari, D., Chiaravalli, J., Meyer, B., Rudich, Y., Li, C., Marton, I., Dym, O., Elad, N., Lewis, M.G., Andersen, H., Gagne, M., Seder, R.A., Douek, D.C., &amp; Schreiber, G. (2021). SARS-CoV-2 variant prediction and antiviral drug design are enabled by RBD in vitro evolution. Nature Microbiology, 6(9), 1188-1198. https://doi.org/10.1038/s41564-021-00954-4