#### University of Ljubljana Faculty of Computer and Information Science

####### Trnovec Lena

##### Actionable Gene Expression Cell Profiling with Foundation Models

###### MASTER'S THESIS THE 2nd CYCLE MASTER'S STUDY PROGRAMME COMPUTER AND INFORMATION SCIENCE

Supervisor

: Prof. Dr. Blaž Zupan

Co-supervisor

: Prof. Dr. Gad Shaulsky

Ljubljana, 2025

#### Univerza v Ljubljani Fakulteta za računalništvo in informatiko

####### Trnovec Lena

##### Uporaben vektorski opis celice s temeljnimi modeli

###### MAGISTRSKO DELO MAGISTRSKI ŠTUDIJSKI PROGRAM DRUGE STOPNJE RAČUNALNIŠTVO IN INFORMATIKA

#### Mentor : prof. dr. Blaž Zupan Somentor : prof. dr. Gad Shaulsky

Ljubljana, 2025

To delo je ponujeno pod licenco Creative Commons Priznanje avtorstva-Deljenje pod enakimi pogoji 2.5 Slovenija (ali novejšo različico). To pomeni, da se tako besedilo, slike, grafi in druge sestavine dela kot tudi rezultati zaključnega dela lahko prosto distribuirajo, reproducirajo, uporabljajo, priobčujejo javnosti in predelujejo, pod pogojem, da se jasno in vidno navede avtorja in naslov tega dela in da se v primeru spremembe, preoblikovanja ali uporabe tega dela v svojem delu, lahko distribuira predelava le pod licenco, ki je enaka tej. Podrobnosti licence so dostopne na spletni strani creativecommons.si ali na Inštitutu za intelektualno lastnino, Streliška 1, 1000 Ljubljana.

<!-- image -->

Izvorna koda zaključnega dela, njeni rezultati in v ta namen razvita programska oprema je ponujena pod licenco GNU General Public License, različica 3 (ali novejša). To pomeni, da se lahko prosto distribuira in/ali predeluje pod njenimi pogoji. Podrobnosti licence so dostopne na spletni strani http://www.gnu.org/ licenses/ .

## Acknowledgments

This work would not have been possible without the exceptional mentorship of Prof. Dr. Blaž Zupan, whose vision and expertise guided my research approach throughout.

I extend my sincere gratitude to Prof. Dr. Gad Shaulsky from Baylor College of Medicine, whose insights into Dictyostelium discoideum biology and prompt thoughtful feedback significantly enriched this research. I also thank Dr. Mariko Kurasawa, Assistant Professor at Baylor College of Medicine, who conducted the experimental work and provided invaluable help in discussing and interpreting the results.

I am grateful to my colleagues in the bioinformatics laboratory for creating such a supportive and enjoyable working environment.

My heartfelt appreciation goes to my family and friends for their unwavering support, and to my pets for being the perfect study companions throughout this journey. Finally, I am especially grateful to my twin sister Nika, whose constant encouragement and ability to bring joy to even the most stressful moments made all the difference.

Trnovec Lena, 2025

### Contents

## Abstract

## Povzetek

|    | Razširjeni povzetek                     | Razširjeni povzetek                                                     |
|----|-----------------------------------------|-------------------------------------------------------------------------|
|    | I                                       | Kratek pregled sorodnih del . . . . . . . . . . . . . . . . . . . ii    |
|    | II                                      | Predlagana metoda . . . . . . . . . . . . . . . . . . . . . . . . iii   |
|    | III                                     | Eksperimentalna evaluacija . . . . . . . . . . . . . . . . . . . . iv   |
|    | IV                                      | Sklep . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . v |
|  1 | Introduction                            | 1                                                                       |
|  2 | Theoretical Background and Related Work | 5                                                                       |
|    | 2.1                                     | Foundations of Cellular Biology . . . . . . . . . . . . . . . . . 5     |
|    | 2.2                                     | Single-Cell RNA Sequencing . . . . . . . . . . . . . . . . . . . 8      |
|    | 2.3                                     | Machine Learning for Cell Analysis . . . . . . . . . . . . . . . 10     |
|    | 2.4                                     | Foundation Models in scRNA-Seq . . . . . . . . . . . . . . . . 12       |
|    | 2.5                                     | D. discoideum as a Model System . . . . . . . . . . . . . . . . 16      |
|  3 | Methodology                             | 21                                                                      |
|    | 3.1                                     | Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22 |
|    | 3.2                                     | Ortholog Mapping . . . . . . . . . . . . . . . . . . . . . . . . 22     |
|    | 3.3                                     | Embedding the Cells . . . . . . . . . . . . . . . . . . . . . . . 25    |
|    | 3.4                                     | Evaluation Framework . . . . . . . . . . . . . . . . . . . . . . 27     |

####### CONTENTS

|   4 | Results     | Results                                                              |   35 |
|-----|-------------|----------------------------------------------------------------------|------|
|     | 4.1         | UCE and scGPT Lead in Trajectory Alignment . . . . . . . .           |   35 |
|     | 4.2         | UCE Achieves Superior Biological Conservation . . . . . . . .        |   38 |
|     | 4.3         | Discussion . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |   42 |
|   5 | Conclusions | Conclusions                                                          |      |

45

### Abstract

Title: Actionable Gene Expression Cell Profiling with Foundation Models

Modern techniques for analyzing cellular data enable a deeper understanding of diseases and the development of more effective therapies. Recently, foundation models - advanced neural networks trained on vast amounts of data - have been developed, representing an important advancement in the analysis of cellular processes. However, since these models have mostly been trained on human cells, an open question remains: can their knowledge be successfully transferred to evolutionarily distant organisms?

In this master's thesis, we address this very question. As a test case, we chose the social amoeba Dictyostelium discoideum , which diverged from humans more than a billion years ago but has a well-studied biology. We systematically compared different approaches to cellular data analysis, ranging from traditional methods to the latest foundation models, including Geneformer, scGPT, and Universal Cell Embedding (UCE).

Our results show that foundation models can effectively analyze even evolutionarily distant organisms, with UCE emerging as the most successful approach. This model is based on analyzing protein sequences rather than gene names, which allows it to recognize functional similarities regardless of evolutionary distance. UCE successfully identified different cell types, key signaling pathways, and developmental transitions in the amoeba, suggesting the existence of universal principles of cellular functioning. Our study thus paves the way for applying foundation models to the study of a wide range of organisms without the need for additional model training.

####### Keywords

foundation models, cell embeddings, single-cell analysis, transfer learning

### Povzetek

Naslov: Uporaben vektorski opis celice s temeljnimi modeli

Moderne tehnike analize celičnih podatkov omogočajo globlje razumevanje bolezni in razvoj učinkovitejših terapij. V zadnjem času so bili razviti temeljni modeli - napredne nevronske mreže, ki se učijo na ogromnih količinah podatkov - in predstavljajo pomemben napredek pri analizi celičnih procesov. Ker pa so bili ti modeli večinoma učeni na človeških celicah, ostaja odprto vprašanje, ali je njihovo znanje mogoče uspešno prenesti tudi na evolucijsko oddaljene organizme.

V magistrskem delu smo se posvetili prav temu vprašanju. Kot testni primer smo izbrali socialno amebo Dictyostelium discoideum , ki je od človeka evolucijsko oddaljena več kot milijardo let, hkrati pa je biološko dobro raziskana. Sistematično smo primerjali različne pristope k analizi celičnih podatkov: od tradicionalnih metod (PCA) do najnovejših temeljnih modelov, vključno z Geneformer, scGPT in Universal Cell Embedding (UCE).

Rezultati kažejo, da lahko temeljni modeli učinkovito analizirajo tudi evolucijsko oddaljene organizme, pri čemer se je kot najuspešnejši izkazal pristop UCE. Ta temelji na analizi proteinskih sekvenc namesto imen genov, kar mu omogoča prepoznavanje funkcionalnih podobnosti ne glede na evolucijsko razdaljo. UCE je uspešno prepoznal različne tipe celic, ključne signalne poti in razvojne prehode v amebi, kar dokazuje, da obstajajo univerzalna načela celičnega delovanja. Naša raziskava tako odpira pot za uporabo temeljnih modelov pri preučevanju širokega spektra organizmov brez potrebe po dodatnem učenju modelov.

####### Ključne besede

temeljni modeli, vektorski opis celice, analiza celičnih podatkov, prenosno učenje

## Razširjeni povzetek

Sekvenciranje RNK posameznih celic (scRNA-seq) je revolucioniralo naše razumevanje celičnega vedenja, vendar analiza tako kompleksnih podatkov ostaja izziv [1]. Temeljni modeli ( angl. foundation models ) - velike nevronske mreže, ki se učijo na obsežnih zbirkah podatkov - ponujajo nov pristop k analizi celičnih podatkov z možnostjo prepoznavanja splošnih vzorcev celičnega delovanja [2]. Ti modeli so že pokazali odlične rezultate pri obdelavi naravnega jezika in računalniškem vidu, zato so jih raziskovalci začeli prilagajati tudi za biološke podatke [3].

Modeli, kot so Geneformer [4], scGPT [5] in Universal Cell Embedding (UCE) [6], se učijo na podatkih milijonov celic, da bi prepoznali osnovna pravila celičnega delovanja. Vendar pa ostaja vprašanje: ali lahko modeli, izurjeni predvsem na človeških celicah, uspešno analizirajo tudi celice drugih, evolucijsko zelo oddaljenih organizmov? To vprašanje je ključnega pomena, saj bi takšni univerzalni modeli lahko olajšali raziskovanje širokega nabora organizmov brez potrebe po dodatnem učenju.

V magistrski nalogi smo preverili, ali temeljni modeli dejansko delujejo tudi pri organizmih, ki so evolucijsko zelo različni od tistih, na podatkih katerih so bili natrenirani. Za testiranje smo izbrali socialno amebo Dictyostelium discoideum kot idealen preizkusni primer: evolucijsko je od človeka oddaljena več kot milijardo let [7], hkrati pa je njena biologija dobro raziskana, kar omogoča zanesljivo preverjanje rezultatov [8].

### I Kratek pregled sorodnih del

Analiza podatkov o izražanju genov posameznih celic predstavlja izziv zaradi izjemno visoke dimenzionalnosti - tipična celica izraža tisoče genov, posameznih celic pa je tudi več tisoč. To ustvarja kompleksne podatkovne strukture [9]. Tradicionalne metode zmanjševanja dimenzionalnosti, kot je analiza glavnih komponent (PCA), omogočajo učinkovito analizo linearnih vzorcev v podatkih, vendar so omejene pri zajemanju kompleksnejših nelinearnih interakcij, ki so značilne za biološke sisteme [10].

Zato so bile razvite naprednejše metode, ki temeljijo na globokem učenju. Variacijski avtokodirniki (VAE), kot je scVI, vpeljujejo koncept verjetnosti v latentno predstavitev podatkov in lahko prepoznajo tudi nelinearne vzorce ter hkrati odpravijo tehnične artefakte, ki nastanejo med merjenjem [11]. Ti pristopi so uspešni pri analizi bioloških vzorcev, vendar imajo pomembno omejitev: za vsak nov nabor podatkov se morajo znova učiti, zato ne morejo izkoristiti znanja iz prejšnjih analiz.

Temeljni modeli ponujajo novo rešitev tega problema z učenjem na ogromnih količinah podatkov in prenosom pridobljenega znanja na nove naloge [2]. Geneformer stanje celice predstavi kot urejen seznam genov, pri čemer imena genov obravnava kot žetone ( angl. tokens ) in jih razporedi glede na stopnjo njihove aktivnosti. Na naboru 30 milijonov človeških celic se model uči povezav med geni z naključnim prikrivanjem dela genov in napovedovanjem manjkajočih [4]. Model scGPT deluje po podobnem principu [5]. UCE pa gre korak dlje: namesto imen genov kot žetone uporablja aminokislinske sekvence proteinov, ki jih ti geni kodirajo, kar naj bi omogočilo analizo tudi organizmov, ki niso bili vključeni v postopek učenja modela [6].

Kljub obetavnim rezultatom ni jasno, ali ti modeli dejansko delujejo pri vseh organizmih. Geni se med vrstami razlikujejo, evolucijska razdalja lahko ovira prenos znanja, različni organizmi pa imajo tudi edinstvene biološke procese. Neposredna uporaba domenskega znanja pri modeliranju ostaja še neraziskano področje, ki ga naslavlja naša raziskava [12].

### II Predlagana metoda

Da bi odgovorili na vprašanje o medvrstni uporabnosti temeljnih modelov, smo zasnovali sistematičen eksperimentalni pristop. Primerjali smo pet različnih pristopov k analizi celičnih podatkov: tradicionalno metodo PCA, variacijski avtokodirnik scVI ter tri temeljne modele Geneformer, scGPT in UCE. Vse metode smo preizkusili na podatkih amebe Dictyostelium discoideum , pri čemer smo izkoristili dobro poznano biologijo organizma za zanesljivo preverjanje rezultatov.

####### Modelni sistem in podatkovni nabor

Dictyostelium discoideum predstavlja idealen modelni sistem za naš eksperiment [8]. Ta pražival ima edinstveno lastnost: ob pomanjkanju hrane se v 24 urah do 100.000 posameznih celic organizira v večcelično strukturo, v kateri se 80% celic v steblu žrtvuje za preživetje preostalih 20%, ki preživijo kot spore [13]. Organizem je odličen preizkusni sistem zaradi treh glavnih lastnosti: (1) njena biologija je temeljito raziskana in dobro opisana; (2) razvoj poteka predvidljivo in sinhrono; (3) evolucijsko je od človeka oddaljena več kot milijardo let in ima z njim skupnih le približno 30% ortolognih genov [7, 14, 15].

Analizirali smo približno 50.000 celic, izmerjenih v šestih pomembnih časovnih točkah razvoja (0, 4, 8, 12, 16 in 20 ur po začetku stradanja). Pri vsaki celici je bila izmerjena aktivnost 12.883 genov, kar omogoča podrobno sledenje razvojnim procesom na molekularni ravni.

####### Mapiranje ortologov in predstavitve genov

Pri temeljnih modelih Geneformer in scGPT naletimo na izziv kompatibilnosti: ti modeli poznajo le imena človeških genov, ameba pa ima precej drugačne gene in posledično drugačna poimenovanja. Le 10% amebinih genov nosi enako ime kot človeški, zato smo morali poiskati podobne gene med človekom in amebo (t. i. ortologe). Z uporabo baze OrthoDB smo razvili pristop mapiranja ortologov in našli ortologe za 33% genov amebe, kar predstavlja bistveno izboljšanje pokritosti genoma v primerjavi z začetnimi 10% [14].

UCE se problema loti drugače: namesto imen genov uporablja aminokislinska zaporedja proteinov, ki jih ti geni kodirajo. Ta pristop omogoča analizo kateregakoli organizma brez predhodnega iskanja ortologov, saj se opira na funkcionalne podobnosti proteinskih sekvenc [16].

### III Eksperimentalna evaluacija

Uspešnost metod smo ovrednotili na dveh komplementarnih ravneh: (i) ohranjanje razvojne dinamike z difuzijskim psevdočasom (DPT), kjer morajo celice, izmerjene pozneje, v povprečju slediti tistim, izmerjenim zgodaj [17]; (ii) ohranitev znanih bioloških vzorcev razvoja amebe.

Za analizo DPT smo zgradili graf najbližjih sosedov in iz 0-urne časovne točke naključno vzorčili 500 kandidatnih korenov. Psevdočas smo izračunali za vsakega kandidata posebej in končno oceno dobili z uteženim povprečjem, kar zagotavlja robustnost rezultatov. Usklajenost s časom merjenja smo kvantificirali s Spearmanovim rangovnim korelacijskim koeficientom in Linovim koeficientom konkordance ter poročali 95% bootstrap intervale zaupanja.

Za biološko validacijo smo ocenili pet ključnih značilnosti razvoja: (1) razlikovanje tipov celic, (2) aktivnost signalne poti cAMP - molekule, ki omogoča agregacijo celic v večcelične strukture in koordinacijo razvoja, (3) izražanje genov na pomembnih razvojnih prehodih, (4) aktivnost regulonov in (5) genov celičnega cikla [18, 19, 20]. Uspešnost ohranjanja bioloških vzorcev smo povzeli s kombinirano mero avgBIO = (NMI + ARI + ASW label )/3, ki omogoča celovito primerjavo različnih pristopov.

####### Rezultati analize

Rezultati so pokazali jasno hierarhijo uspešnosti: UCE je dosegel najboljše rezultate pri večini nalog. Pri nalogi razlikovanja med tipi celic je UCE dosegel izjemno oceno 0,724, medtem ko so se drugi modeli odrezali bistveno slabše (Geneformer: 0,459; scGPT: 0,445; scVI: 0,438; PCA: 0,349). UCE je pravilno prepoznal kritične trenutke celičnih usodnih odločitev, ko se celice opredelijo za celice stebla ali spor.

UCE je dosegel odlične rezultate tudi pri drugih bioloških nalogah: odlično je prepoznal signalno pot cAMP (ocena 0,820), in delovanje regulonov (ocena 0,399). Pri ohranjanju razvojnih trajektorij je dosegel najboljše ujemanje s časovnim potekom (Linov koeficient konkordance 0,873), sledil pa mu je scGPT (0,857). Tradicionalni pristopi so se odrezali slabše: PCA je dosegel 0,814, Geneformer 0,792, scVI pa le 0,657.

Edina naloga, pri kateri UCE ni dosegel najboljših rezultatov, je bilo prepoznavanje faz celičnega cikla, vendar so se tudi vsi drugi modeli pri tej nalogi odrezali slabo (ocene okrog 0,2). To verjetno ni posledica pomanjkljivosti modelov, temveč dejstva, da je celični cikel v razvoju amebe precej drugačen od tipičnih sistemov.

####### Skladnost rezultatov z biološkim predznanjem

Uspešnost UCE pri medvrstnem prenosu znanja potrjuje, da lahko temeljni modeli uspešno prenašajo znanje tudi na evolucijsko oddaljene organizme. Bistven dejavnik uspeha je uporaba proteinskih sekvenc namesto imen genov - proteini z enako funkcijo ohranijo strukturne podobnosti tudi pri zelo različnih organizmih, kar omogoča prepoznavanje funkcionalnih ekvivalentov brez eksplicitnega mapiranja ortologov [6]. Zanimivo je, da je UCE pri analizi psevdočasa pravilno identificiral kritično razvojno točko okoli 9. ure, ko se celice opredelijo za svojo končno usodo, kar kaže na sposobnost zaznave ključnih bioloških prehodov [8].

### IV Sklep

V magistrskem delu smo predstavili sistematično evalvacijo temeljnih modelov za analizo celic evolucijsko oddaljenih organizmov. Uporaba modela UCE na podatkih amebe Dictyostelium discoideum je pokazala, da lahko temeljni modeli uspešno prenašajo znanje tudi na organizme, ki so evolucijsko oddaljeni več kot milijardo let od tipičnih učnih vrst. To je prvi korak pri razvoju resnično univerzalnih metod za analizo celičnih podatkov, s čimer odpiramo vrata za nadaljnje raziskave na področju računalniške biologije.

Uspešnost pristopa, utemeljenega na beljakovinskih sekvencah, dokazuje obstoj univerzalnih načel celičnega delovanja, ki veljajo kljub velikim evolucijskim razlikam [21, 22]. UCE zajame funkcionalne podobnosti ne glede na to, kako različni so geni posameznih vrst, kar omogoča analizo organizmov brez eksplicitnega mapiranja ortologov ali dodatnega učenja modelov. Naši rezultati odpirajo nova vrata za raziskovanje različnih organizmov z istimi računalniškimi orodji.

To ima pomembne praktične posledice za znanstvenike. Raziskovalci, ki preučujejo manj znane organizme, lahko zdaj uporabijo temeljne modele namesto zapletenih tradicionalnih metod in s tem poenostavijo analizo, pri čemer ohranijo biološki pomen rezultatov. Naše delo hkrati vzpostavlja jasne smernice za ovrednotenje uspešnosti teh modelov na novih organizmih ter prispeva k razvoju evalvacijskih okvirov za prihodnje raziskave.

Pri nadaljnjem delu bi bilo smiselno te pristope preizkusiti tudi na drugih evolucijsko oddaljenih organizmih ter raziskati, kako kombinirati različne tipe bioloških podatkov za še boljše rezultate. Ker temeljni modeli postajajo vse zmogljivejši, je pomembno razumeti njihove možnosti in omejitve pri različnih organizmih [3]. Naše delo zagotavlja metodološki okvir za takšne preizkuse in prispeva k razvoju resnično univerzalnih metod za razumevanje celičnega življenja.

## Chapter 1

## Introduction

Understanding life at the cellular level has been transformed from a distant aspiration to an achievable reality. Over the past decade, revolutionary advances in biotechnology have enabled scientists to peer into individual cells and decode their molecular blueprints with unprecedented precision. Yet, despite generating vast amounts of cellular data, extracting meaningful biological insights remains one of the greatest challenges in modern computational biology [3].

At the heart of this challenge lies a fundamental question: can we generate universal computational representations of cellular states that transcend the divisions between different organisms, tissues, and experimental conditions? Such representations would enable researchers to discover biological patterns and principles that are conserved across the tree of life, potentially accelerating our understanding of fundamental biological processes and disease mechanisms [6, 21].

The recent emergence of foundation models [5, 4, 6] - large neural networks trained on diverse datasets to learn general-purpose representations-offers a promising path toward this goal [2]. In computational biology, these models promise to capture universal patterns of cellular behavior by learning from millions of cells across different species and conditions [2]. However, a critical limitation remains largely unexplored: do these models truly generalize across evolutionary lineages, or are they constrained by the organisms used in their training?

This question is particularly important because most foundation models for cellular analysis have been trained predominantly on human data, reflecting the research community's focus on mammalian model systems [5, 4]. While these models demonstrate impressive performance within their training domain, their ability to generate meaningful representations for evolutionarily distant organisms remains uncertain. This limitation could severely restrict their utility for comparative biology and our understanding of universal cellular principles. Recent zero-shot evaluations have revealed that foundation models like Geneformer and scGPT may face reliability challenges when applied without additional training, particularly in discovery settings where labels are unknown [12].

This thesis addresses this fundamental gap by investigating whether foundation models can transcend their training domains to provide meaningful insights into organisms far removed from their original scope. We evaluate these models on the social amoeba Dictyostelium discoideum , chosen specifically because it represents an ideal test case for cross-species generalization. As shown in Table 1.1, this organism is separated from typical training species by hundreds of millions of years of evolution [7], with only about 30% of its genes orthologous to human genes [14]. This evolutionary relationship is further illustrated in the phylogenetic context (Figure 1.1). Despite this evolutionary distance, D. discoideum possesses well-characterized developmental biology with clear temporal dynamics, measurable cell fate trajectories, and established molecular markers that provide rigorous biological ground truth for evaluation [8].

Our central hypotheses are:

1. Foundation models trained primarily on metazoan species can generate biologically meaningful representations for evolutionarily distant organisms like Dictyostelium discoideum , a protist.

2. These cross-species representations preserve important biological relationships and enable the discovery of patterns not readily apparent when analyzing the data using traditional methods.

Table 1.1: Evolutionary divergence and orthology relationships between human, other species used in training of foundation models, and Dictyostelium discoideum [7, 14]. We explain how the orthologs were determined in Section 3.2.

| Organism                 | Common Name         | Years from Human Divergence   | Genes with Human Orthologs   |
|--------------------------|---------------------|-------------------------------|------------------------------|
| Homo sapiens             | Human               | /                             | /                            |
| Macaca mulatta           | Rhesus monkey       | 26.8 - 30.6 million           | ∼ 83%                        |
| Macaca fascicularis      | Pig-tailed macaque  | 26.8 - 30.6 million           | ∼ 79%                        |
| Microcebus murinus       | Mouse lemur         | 71.4 - 77.5 million           | ∼ 84%                        |
| Mus musculus             | Mouse               | 81.3 - 91.0 million           | ∼ 76%                        |
| Sus scrofa               | Wild boar           | 91.5 - 97.4 million           | ∼ 80%                        |
| Xenopus tropicalis       | Western clawed frog | 348.4 - 355.7 million         | ∼ 75%                        |
| Danio rerio              | Zebrafish           | 423.3 - 440.0 million         | ∼ 69%                        |
| Dictyostelium discoideum | Social amoeba       | 1085.0 - 1671.0 million       | ∼ 33%                        |

Figure 1.1: Evolutionary divergence times between Dictyostelium discoideum and foundation model training species. The social amoeba is separated from commonly used training organisms (shown in bold) by hundreds of millions of years of evolution [7].

<!-- image -->

The significance of this investigation extends beyond technical validation. By probing the limits of foundation model generalization, we seek to understand the fundamental nature of cellular representations and the extent to which biological principles transcend species barriers. Our findings will inform both the development of more robust computational methods and our broader understanding of universal patterns in cellular biology [21, 22].

All computational methods, analysis scripts, and evaluation frameworks developed in this work are freely available on GitHub 1 . The Dictyostelium discoideum single-cell RNA sequencing (scRNA-seq) dataset is publicly accessible through the Gene Expression Omnibus (GEO) database under accession code GSE305468.

This work is structured as follows: Chapter 2 presents the theoretical foundations spanning molecular biology, single-cell technologies, machine learning concepts, and foundation models. Chapter 3 describes our experimental framework for evaluating cross-species generalization. Chapter 4 presents our findings on trajectory preservation and biological conservation. Finally, Chapter 5 discusses the implications and limitations of our work for the broader field of computational biology.

[1 https://github.com/lenatr99/scRNA\_benchmarks](https://github.com/lenatr99/scRNA_benchmarks)

## Theoretical Background and

## Chapter 2 Related Work

This chapter provides the essential theoretical foundation for understanding our investigation into actionable cell profiling using foundation models. Following the approach of building from biological fundamentals to computational methods, we begin in Section 2.1 with the biological foundations of gene expression and cellular systems. Section 2.2 covers single-cell RNA sequencing technology and its unique challenges. In Section 2.3, we introduce the machine learning concepts essential to our work, including representation learning and self-supervised approaches. Section 2.4 examines foundation models for single-cell RNA sequencing analysis. Finally, Section 2.5 presents Dictyostelium discoideum as our model system and explains why it provides an ideal test case for evaluating cross-species generalization.

### 2.1 Foundations of Cellular Biology

Understanding the computational analysis of single-cell data requires a solid foundation in the biological processes that generate the measurements we seek to model. This section introduces the key biological concepts that inform our approach to cell profiling and representation learning.

#### 2.1.1 Cells and Gene Expression

Cells are the fundamental units of life, containing the molecular machinery that enables biological function. At the molecular level, cellular behavior is primarily governed by gene expression-the process by which genetic information encoded in DNA is converted into functional proteins that carry out cellular processes [23].

The central dogma of molecular biology describes the flow of genetic information: DNA is transcribed into messenger RNA (mRNA), which is then translated into proteins. Gene expression is highly regulated, with cells modulating the production of specific proteins in response to internal signals, environmental conditions, and developmental programs. This regulation occurs at multiple levels, including transcriptional control (whether genes are transcribed), post-transcriptional control (mRNA processing and stability), and post-translational control (protein modification and degradation) (Figure 2.1) [23].

Figure 2.1: The central dogma of molecular biology. Genetic information flows from DNA through transcription to mRNA, which is then translated into functional proteins composed of amino acid sequences. This process forms the foundation of gene expression analysis in single-cell RNA sequencing studies, where we measure the number of mRNA molecules captured during sequencing and interpret these counts as mRNA abundance. Importantly, observed mRNA abundance reflects the dynamic balance between mRNA synthesis (transcription) and mRNA degradation, with both processes contributing to the steady-state levels that serve as proxies for cellular state and function.

<!-- image -->

#### 2.1.2 Cellular Heterogeneity and State

Even within apparently uniform cell populations, individual cells can exhibit significant variation in gene expression patterns. This cellular heterogeneity arises from multiple sources: intrinsic noise in gene expression machinery, cell cycle stage differences, microenvironmental variations, and stochastic fluctuations in molecular processes [24]. Recent advances in single-cell technologies have revealed that this variability is not merely technical noise but carries important biological information about cellular states and functions [25, 26].

Understanding cellular heterogeneity is crucial for biological research because it reveals the true diversity of cell states and behaviors that are masked when studying bulk populations. Different cell states can represent distinct functional roles, developmental stages, or responses to perturbations. The ability to profile individual cells has revolutionized our understanding of complex biological systems by revealing rare cell types, developmental trajectories, and the mechanisms of cellular decision-making [27, 28]. However, distinguishing genuine biological heterogeneity from technical artifacts remains a significant challenge in single-cell analysis, requiring sophisticated statistical methods that account for the uncertainty inherent in clustering algorithms [29].

#### 2.1.3 Homeostasis and Cellular Responses

Cells maintain homeostasis through complex regulatory networks that sense environmental conditions and adjust gene expression accordingly. When faced with stress, developmental signals, or other perturbations, cells can undergo dramatic changes in their gene expression programs while maintaining their essential functions [30].

This dynamic nature of cellular systems means that gene expression measurements capture not just the current state of a cell, but also reflect its recent history and current environmental context [31, 32]. Understanding these dynamics is essential for interpreting single-cell data and developing models that can capture meaningful biological relationships across different conditions and organisms.

### 2.2 Single-Cell RNA Sequencing

Single-cell RNA sequencing (scRNA-seq) has emerged as a transformative technology that enables the measurement of gene expression in individual cells, providing unprecedented resolution into cellular heterogeneity and biological processes [1]. The rapid evolution of this technology has enabled analysis of increasingly large and diverse datasets, revealing the full complexity of cellular ecosystems across tissues and organisms [26].

#### 2.2.1 Technical Principles

scRNA-seq protocols typically involve several key steps: single-cell isolation, cell lysis, mRNA capture and reverse transcription, cDNA amplification, library preparation, sequencing, and data analysis (Figure 2.2). A critical feature of modern single-cell protocols is the incorporation of unique molecular barcodes-short DNA sequences that are attached to each cDNA molecule during reverse transcription. These cell-specific barcodes enable computational identification and separation of transcripts originating from individual cells after pooled sequencing, allowing thousands of cells to be processed simultaneously while maintaining single-cell resolution [33]. Each step introduces potential sources of technical variation that must be considered in downstream analysis.

Figure 2.2: Single-cell RNA sequencing methodology. Tissue samples are dissociated into individual cells, mRNA is captured and sequenced, generating gene expression matrices that enable identification of distinct cell types and developmental states at single-cell resolution.

<!-- image -->

The technology faces several platform-specific limitations. Droplet-based methods like 10X Genomics enable high-throughput analysis of thousands of cells but achieve relatively low mRNA capture efficiency (10-20% of molecules), leading to dropout events where genes appear unexpressed despite mRNA being present in the cell. In contrast, plate-based methods such as Smart-seq2 capture a higher fraction of mRNA molecules (30-50%) but are limited to analyzing hundreds rather than thousands of cells [33]. Additional challenges include amplification bias that can distort relative transcript abundances, cell doublets or multiplets that contaminate datasets with artificial cell types, and batch effects arising from different experimental conditions, reagent lots, processing times, or variation between laboratories that introduce systemic biases obscuring true biological variation [9, 18]. The high cost of single-cell experiments also presents significant challenges for experimental design, as substantial sequencing expenses and complex sample preparation requirements lead most studies to rely primarily on internal replication rather than independent biological replicates across separate experiments. Our Dictyostelium discoideum dataset includes independent biological replicates that validate the robustness of patterns observed through internal replication.

#### 2.2.2 Data Characteristics

scRNA-seq data exhibits several distinctive characteristics that influence computational analysis approaches:

- High dimensionality. Typical datasets measure 10,000-30,000 genes per cell, creating extremely high-dimensional feature spaces that pose challenges for visualization and analysis [34, 35].
- Sparsity. Dropout events and the noisy nature of gene expression create datasets with 80-90% zero values, requiring specialized methods for handling sparse data [36].
- Overdispersion. Gene expression exhibits greater variance than expected under simple statistical models, necessitating approaches that can handle this overdispersion [37].

Compositional effects. Since sequencing provides relative rather than absolute measurements, changes in one set of genes can appear to affect the expression of all other genes [38].

These characteristics make scRNA-seq data particularly challenging for computational analysis but also provide rich information about cellular states and behaviors when properly analyzed. Modern computational approaches must address multiple challenges simultaneously: accurate cell type annotation, integration of datasets across different experimental conditions, and inference of cellular communication networks, all while handling the sparsity and noise in scRNA-seq measurements [9, 39].

### 2.3 Machine Learning for Cell Analysis

The analysis of high-dimensional scRNA-seq data relies heavily on machine learning approaches, particularly methods for dimensionality reduction and representation learning. This section introduces the key concepts underlying our computational approach.

#### 2.3.1 Representation Learning

Representation learning seeks to discover meaningful low-dimensional representations of high-dimensional data that preserve important relationships while reducing noise and computational complexity [21]. In the context of scRNA-seq data, effective representations should capture biological relationships such as cell type similarities, developmental trajectories, and responses to perturbations while removing technical artifacts.

Traditional linear methods like Principal Component Analysis (PCA) identify directions of maximum variance in the data. While computationally efficient and interpretable, PCA is limited by its linear nature and may not capture complex non-linear relationships present in biological data [10].

Neural network approaches can learn non-linear representations through multiple layers of transformations [40]. Autoencoders, which learn to compress and reconstruct input data, have proven particularly effective for biological applications [41].

#### 2.3.2 Self-Supervised Learning

Self-supervised learning enables the training of models on large datasets without requiring manually annotated labels [42]. Instead of relying on external supervision, these methods create training signals from the data itself, such as predicting masked portions of the input or learning relationships between different views of the same data.

This approach is particularly valuable for biological data, where obtaining high-quality labels (such as cell type annotations) is often expensive and time-consuming. Self-supervised methods can leverage the vast amounts of unlabeled scRNA-seq data to learn general representations that capture biological structure.

#### 2.3.3 Transfer Learning and Domain Adaptation

Transfer learning allows models trained on one dataset or domain to be applied to new, related tasks with minimal additional training [43]. This approach is particularly relevant for scRNA-seq analysis, where models trained on large reference datasets could potentially be applied to new experimental conditions, cell types, or even species.

However, transfer learning faces challenges when the source and target domains differ significantly. In the context of cross-species applications, differences in gene orthology, evolutionary distance, and unique biological pathways can limit the effectiveness of direct transfer approaches. Zero-shot evaluations have demonstrated that foundation models may be outperformed by simpler methods when applied to domains substantially different from their training data, highlighting the importance of rigorous cross-domain validation [12].

### 2.4 Foundation Models in scRNA-Seq

The challenge of analyzing high-dimensional scRNA-seq data has driven the development of sophisticated dimensionality reduction approaches. Traditional methods like PCA remain valuable for their efficiency and interpretability, but struggle to capture the complex non-linear relationships present in biological systems [10]. This limitation has led to the adoption of deep learning approaches, particularly variational autoencoders, which can model intricate patterns in biological data while providing probabilistic representations [44].

Recent years have witnessed the emergence of foundation models in computational biology, promising to learn universal representations from vast datasets [2]. Foundation models represent a paradigm shift in machine learning, characterized by models trained on broad data using self-supervision at scale that can be adapted to a wide range of downstream tasks. This approach has proven transformative in natural language processing and computer vision [21, 42], leading to their recent adaptation to biological data analysis.

#### 2.4.1 The Foundation Model Paradigm

Foundation models are distinguished by their role as incomplete models that serve as a common basis from which many task-specific models are built via adaptation. They exhibit two defining characteristics: emergence (new capabilities that arise naturally from large-scale training rather than explicit programming) and homogenization (the same models becoming widely adopted across many different applications), with more powerful abilities emerging as the models become larger [2].

In the biological domain, foundation models promise to capture universal patterns of cellular behavior that transcend specific experimental conditions, enabling more robust and generalizable analyses. However, biology presents unique challenges compared to domains like natural language, including greater data heterogeneity, complex batch effects, and the need to handle cross-species variation. Recent advances have demonstrated the potential for foundation models to capture complex developmental trajectories and cellular fate decisions across multiple biological contexts, including applications to disease subtyping and clinical prediction tasks [45].

#### 2.4.2 Embedding Methods for scRNA-Seq Analysis

To evaluate cross-species generalization capabilities, we compare five distinct approaches to single-cell representation learning that span traditional dimensionality reduction, established deep learning methods, and recent foundation models:

- PCA provides a linear dimensionality reduction baseline that identifies directions of maximum variance in the data. While computationally efficient and interpretable, PCA is limited by its linear nature and may not capture complex non-linear relationships present in biological data [10].
- scVI (Single-cell Variational Inference) uses variational autoencoders to learn latent representations of scRNA-seq data while explicitly modeling technical sources of variation such as batch effects and library size differences [11]. While effective for batch correction and data integration, scVI requires retraining for each new dataset and does not capture crossdataset relationships.
- Geneformer treats cells as sequences of gene tokens ranked by expression level and uses transformer architectures to learn gene regulatory relationships [4]. The model captures important aspects of gene regulation and cell type relationships but was trained on human scRNA-seq data (29.9 million transcriptomes), raising questions about its applicability to evolutionarily distant organisms.
- scGPT applies transformer architectures to single-cell multi-omics data, treating genes as tokens in a sequence and learning contextual relationships between co-expressed genes [5]. While powerful, the model requires substantial computational resources and its generalization to novel organisms remains largely unexplored.
- UCE (Universal Cell Embedding) stands as the most comprehensive approach

to achieving universal cellular representations through protein-based gene representations that theoretically enable cross-species analysis without explicit orthology mapping [6]. Yet despite its promise of universality, UCE's performance on organisms evolutionarily distant from its training data remains largely uncharted territory.

Table 2.1 summarizes the key characteristics that distinguish these approaches for cross-species analysis.

Table 2.1: Comparison of embedding methods for cross-species scRNA-seq analysis

| Method                                                                              | PCA                       | scVI                                        | Geneformer                                        | scGPT                                           | UCE                                                                                                                                       |
|-------------------------------------------------------------------------------------|---------------------------|---------------------------------------------|---------------------------------------------------|-------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Architecture Gene Representation Retraining Required Training Size Training Species | Linear Gene expression No | Variational Autoencoder Gene expression Yes | Transformer Gene tokens No 29.9M cells H. sapiens | Transformer Gene tokens No 33M cells H. sapiens | Transformer Protein embeddings No 36M cells H. sapiens M. musculus M. murinus D. rerio S. scrofa M. mulatta M. fascicularis X. tropicalis |

#### 2.4.3 Universal Cell Embedding

The UCE model [6] represents the most ambitious attempt to overcome these limitations through protein-based gene representations that eliminate the need for explicit orthology mapping. However, its actual performance on evolutionarily distant organisms remains unexplored, creating a critical knowledge gap that this thesis directly addresses.

####### Model Architecture and Training

UCEemploys a novel 'bag of RNA' approach that abstracts cells as expressionweighted samples of their constituent genes. The model architecture consists of a 33-layer transformer with over 650 million parameters. During preprocessing, UCE samples 1024 genes (with replacement) from each cell, weighted by their log-normalized expression levels. Each gene is represented using protein embeddings generated by ESM2 [16], a large protein language model trained for atomic-level structure prediction that converts amino acid sequences into structural representations. Genes are organized by chromosomal location and separated by special chromosome tokens before being fed into the transformer [6].

UCE is trained using a self-supervised masked gene prediction objective. During training, 20% of the expressed genes are randomly masked, and the model learns to predict whether these masked genes (along with randomly selected unexpressed genes) were originally expressed in the cell. This binary classification task uses cross-entropy loss and enables the model to learn meaningful cellular representations without requiring any cell type annotations [6].

The model's training strategy leverages a massive, diverse dataset comprising over 36 million cells from multiple species, tissues, and experimental conditions. This extensive training enables UCE to learn universal patterns of gene expression that potentially transcend species boundaries.

####### Cross-Species Capabilities

UCE achieves cross-species universality through its protein-based gene representation approach, which does not require orthology mapping between species. Instead of relying on gene-to-gene correspondence, UCE represents each gene by the protein it encodes using ESM2 protein embeddings [16]. This approach allows UCE to meaningfully represent any protein-coding gene from any species based solely on its amino acid sequence, regardless of whether that species was included in the training data or whether clear orthologs exist in other species [6]. This protein-centric approach assumes that functionally similar proteins will have similar sequence-derived embeddings, enabling the model to identify biological patterns that span across species without explicit evolutionary mapping.

####### Promises and Limitations

The universal nature of UCE embeddings offers several theoretical advantages: direct comparison of cells from different experiments without additional processing; discovery of biological patterns that may not emerge in smaller studies; and enabling of comparative studies across species and conditions [6].

However, UCE's universal claims remain to be fully validated, particularly for organisms that differ substantially from those in the training dataset. While the protein-based approach eliminates the need for orthology mapping, limitations may still arise when applied to organisms with highly divergent protein sequences or unique gene families not well-represented in the ESM2 protein structure prediction model training data [16]. A fundamental constraint of UCE's protein-centric design is its exclusive focus on protein-coding genes, which excludes non-coding RNAs such as long non-coding RNAs, microRNAs, and other regulatory transcripts that play crucial roles in cellular regulation and development [46]. This limitation potentially reduces the model's analytical power by omitting important regulatory elements that could provide additional insights into cellular states and transitions. Additionally, the model's performance may degrade for organisms with substantially different gene expression patterns or regulatory mechanisms compared to the predominantly metazoan training data. Understanding these limitations is crucial for determining the true scope of UCE's applicability and forms a central motivation for our investigation.

### 2.5 D. discoideum as a Model System

Dictyostelium discoideum , commonly known as the social amoeba, represents an ideal model system for testing the cross-species generalization capabilities of foundation models. This section explains the unique properties of this organism that make it particularly suitable for our investigation.

#### 2.5.1 Biological System Overview

Dictyostelium discoideum is a soil-dwelling amoeba that undergoes a remarkable developmental transformation when nutrients become scarce. Up to 100,000 individual amoebae abandon their solitary lifestyle and coordinate to form a multicellular fruiting body over approximately 24 hours (Figure 2.3) [8, 13].

Figure 2.3: Developmental lifecycle of Dictyostelium discoideum . Upon starvation, individual amoebae aggregate through cAMP chemotaxis. They form mounds in which initial cell fate decisions occur and the cells differentiate into prespore (orange) and prestalk (blue). The aggregates develop into a motile slug in which the prestalk cells occupy mainly the anterior region and prespore cells occupy mainly the posterior region. Upon culmination, the structures develop into fruiting bodies in which the prestalk cells differentiate into stalk cells that eventually die and the prespore cells differentiate into viable spores.

<!-- image -->

The developmental program consists of distinct, well-characterized stages [47]. During aggregation, starving cells respond to cyclic adenosine monophosphate (cAMP) signals and converge into aggregates through chemotaxis. Early in development, cells make initial prespore and prestalk fate decisions, and these differentiated cells subsequently assume appropriate positions during three-dimensional mound formation. The mound elongates into a motile slug where the prestalk/prespore proportions (20%/80%) become clearly established as the slug migrates toward favorable environmental conditions for fruiting body formation. Finally, during culmination, prestalk cells undergo terminal differentiation into stalk cells that form the supporting stalk, while prespore cells undergo terminal differentiation into hardy spores capable of surviving adverse conditions [8, 48].

#### 2.5.2 Advantages of D. discoideum as a Model System

This developmental system provides several unique advantages for evaluating foundation models:

- Well-characterized biology. The developmental timeline, cell fate decisions, and molecular mechanisms are thoroughly understood, providing clear biological ground truth for evaluation. Key regulatory genes, signaling pathways, and cell type markers have been extensively characterized [8, 13].
- Temporal dynamics. The 24-hour developmental program creates measurable trajectories that test whether embeddings capture biological progression and maintain temporal relationships [47].
- Developmental synchronicity. Unlike most multicellular systems where individual organisms develop at different rates, Dictyostelium discoideum populations exhibit remarkable synchronicity-all multicellular structures reach the same developmental stage simultaneously. This unique property provides unusually high levels of internal replication and eliminates confounding effects from developmental asynchrony that complicate analysis in other systems [15].
- Clear cell type distinctions. The binary prestalk/prespore differentiation provides a straightforward classification task with well-defined molecular markers [48].
- Evolutionary distance. As a protist belonging to the Amoebozoa supergroup, Dictyostelium discoideum is evolutionarily distant from the metazoan species (primarily human) typically used to train foundation models. This evolutionary distance provides a stringent test of true universality versus overfitting to particular taxonomic groups [7].

#### 2.5.3 scRNA-Seq Studies of Development

Recent scRNA-seq studies are beginning to resolve the complexity of Dictyostelium discoideum development, revealing previously unrecognized in- termediate states, cell-to-cell heterogeneity within established cell types, and dynamic, signaling-linked changes in gene expression that accompany development.[49].

These high-resolution datasets provide an ideal testing ground for foundation models because they combine well-understood biology with the technical challenges typical of scRNA-seq data. The combination of clear biological expectations and comprehensive molecular characterization allows for rigorous evaluation of whether foundation model embeddings capture true biological relationships in an organism very different from those used in training.

#### 2.5.4 Cross-Species Evaluation Challenges

Applying foundation models to Dictyostelium discoideum presents several specific challenges that test different aspects of model robustness:

- Protein sequence divergence. While UCE's protein-based approach eliminates the need for orthology mapping, Dictyostelium discoideum proteins may have diverged significantly from those represented in the ESM2 protein language model training data [16], potentially affecting the quality of protein embeddings for some genes.
- Unique biological processes. Social development and the specific mechanisms of Dictyostelium discoideum cell differentiation involve pathways not present in the training organisms.
- Expression pattern differences. The relative expression levels and co-expression patterns may differ significantly from those in animal systems.

These challenges make Dictyostelium discoideum an excellent test case for evaluating the true universality of foundation models and identifying the limits of cross-species applicability.

## Chapter 3

## Methodology

This chapter presents a comprehensive experimental framework for evaluating the cross-species applicability of foundation models in scRNA-seq analysis. We assess whether foundation models, trained primarily on metazoan species, can generate biologically meaningful representations for the evolutionarily distant social amoeba Dictyostelium discoideum .

Our methodology addresses three fundamental questions: Can foundation models trained primarily on human data capture meaningful biological relationships in an organism separated by vast evolutionary timescales? How do protein-based gene representations compare to traditional ortholog-mapping approaches? What evaluation frameworks can reliably assess the biological validity of embeddings across different species?

We develop a multi-faceted evaluation protocol that compares five embedding methods-PCA, scVI, Geneformer, scGPT, and UCE-using established biological ground truth from Dictyostelium discoideum development. Our evaluation strategy combines biological conservation metrics and trajectory preservation analyses to provide a assessment of foundation model generalization to non-metazoan organisms.

### 3.1 Data

Our primary dataset consists of scRNA-seq measurements from Dictyostelium discoideum development. The experimental design focuses on the wild-type AX4 strain, with cells collected at six critical time points during the developmental program: 0, 4, 8, 12, 16, and 20 hours post-starvation. The resulting expression matrix structure is shown in Table 3.1.

Table 3.1: scRNA-seq expression matrix structure.

| Cell barcode       | Time   | Gene ID Gene Symbol   | DDB_G0267698 DDB_G0267698   | DDB_G0269682 atxn2   | DDB_G0269688 sdad1   | n . . . . . .   | genes = 12 , 883 DDB_G0294048 nad4   |
|--------------------|--------|-----------------------|-----------------------------|----------------------|----------------------|-----------------|--------------------------------------|
| AAACCCAAGACATACA-1 | 00hr   |                       | 0                           | 11                   | 2                    | . . .           | 32                                   |
| AAACCCAAGATCCCGC-1 | 00hr   |                       | 1                           | 1                    | 0                    | . . .           | 1                                    |
| AAACGAAAGAATAACC-1 | 00hr   |                       | 2                           | 3                    | 0                    | . . .           | 8                                    |
| AAACGAAAGAATCGTA-1 | 00hr   |                       | 0                           | 4                    | 2                    | . . .           | 3                                    |
| AAACGAACAAGACGGT-1 | 00hr   |                       | 0                           | 2                    | 5                    | . . .           | 13                                   |
| . . .              | . . .  |                       | . . .                       | . . .                | . . .                |                 | . . .                                |
| TTTGTTGTCTTGTGCC-1 | 20hr   |                       | 0                           | 1                    | 0                    | . . .           | 0                                    |

n cells = 48 , 983

The dataset measures the mRNA abundance levels of 12,883 genes across approximately 10,000 individual cells per time point, yielding roughly 50,000 total cell profiles. Each measurement represents the mRNA content captured from a single cell - the raw counts reflect the number of sequencing reads mapping to each gene (Figure 3.1).

The data are stored in AnnData format (.h5ad files), the standard structure for scRNA-seq analysis in Python [52]. Each AnnData object contains: (1) an expression matrix with cells as rows and genes as columns, (2) cell metadata including strain, time point, and inferred cell types, and (3) gene annotations with functional classifications. This structure enables efficient analysis while preserving the experimental context essential for developmental studies.

### 3.2 Ortholog Mapping

Foundation models like Geneformer and scGPT were trained on human gene identifiers, creating an immediate compatibility problem when applied to Dictyostelium discoideum data. Direct application results in severe genome undercoverage-fewer than 10% of genes are recognized due to species-specific naming conventions. This limitation necessitates ortholog mapping to translate between gene identifiers across species.

Figure 3.1: Example single-cell gene expression measurements during Dictyostelium discoideum development. mRNA abundance for three key developmental genes measured from an individual cell across the six time points in our dataset: acaA encodes an enzyme that produces cAMP signals for cell aggregation [50], cprD encodes a cysteine proteinase abundant in vegetative cells that decreases during development [51], pkaC responds to cAMP signals for cell fate control and csaA encodes a cell-cell adhesion protein [50].

<!-- image -->

Orthologs are genes in different species that evolved from a common ancestral gene and typically retain the same function [22]. We developed a systematic ortholog identification pipeline using OrthoDB v12 [14], querying the API for orthologous gene pairs between human and the social amoeba.

OrthoDB returns many-to-many relationships that require systematic filtering to establish reliable one-to-one mappings. We implemented a hierarchical confidence scoring system with four strategies:

1. Naturally unique orthologs (confidence = 1.0): Cases where OrthoDB identifies exactly one ortholog per species
2. Reciprocal best hits (confidence = 0.95): Mutual highest-scoring orthologs between species pairs

3. Most specific human orthologs with confidence calculated as:

<!-- formula-not-decoded -->

where n orthologs is the number of organism genes orthologous to the human gene

4. Fallback selection (confidence = 0.5): Random selection from remaining candidates

Table 3.2: Some orthologous genes between Dictyostelium discoideum and humans.

| Dictyostelium Gene   | Human Ortholog   | Function             |
|----------------------|------------------|----------------------|
| DDB_G0293414         | BRCA2            | DNA repair           |
| DDB_G0281569         | ATR              | DNA damage signaling |
| DDB_G0275809         | MSH2             | DNA mismatch repair  |
| DDB_G0278741         | PARP1            | DNA repair signaling |
| DDB_G0287607         | PCNA             | DNA replication      |
| DDB_G0272775         | CDC23            | Cell cycle control   |
| DDB_G0267460         | CYBA             | Oxidative defense    |

We retained only relationships with confidence above 0.7, yielding 4,188 high-confidence orthologous pairs from 13,847 initial candidates. This increases effective genome coverage for foundation model evaluation from 10% to 33%, a substantial improvement, yet still incomplete. The coverage limitation underscores the fundamental advantage of UCE's protein-based approach, which achieves universal gene representation without requiring ortholog mapping.

Table 3.2 presents representative orthologs between Dictyostelium discoideum and humans, illustrating conservation of essential cellular processes across vast evolutionary distances.

These conserved orthologs demonstrate that fundamental cellular mechanisms persist across species, reflecting the essential nature of processes such as DNA repair, cell cycle regulation, and protein quality control.

### 3.3 Embedding the Cells

To evaluate cross-species capabilities, we selected five embedding methods that represent distinct approaches to single-cell representation learning. Our selection includes traditional dimensionality reduction (PCA), established deep learning method (scVI), and recent foundation models (Geneformer, scGPT, UCE). This diverse set enables us to assess whether foundation models offer advantages over conventional approaches when applied to evolutionarily distant organisms.

The critical distinction between these methods lies in their retraining requirements, which fundamentally determines their practical utility for crossspecies analysis. Methods requiring retraining (like scVI) impose several severe limitations: they demand resource-intensive data labeling and model training for each new dataset, resulting in time-consuming and inefficient workflows that produce sub-optimal analyses based on small, limited datasets. More fundamentally, retraining destroys the universality of representations: when model weights are updated during fine-tuning, the underlying structure changes, making it impossible to compare embeddings across different datasets or experiments. This limitation prevents the cross-dataset discoveries that are essential for understanding universal biological principles.

Table 3.3: Implementation details and configurations for embedding methods

| Method               | PCA           | scVI        | Geneformer           | scGPT                | UCE                 |
|----------------------|---------------|-------------|----------------------|----------------------|---------------------|
| Input preprocessing  | Raw counts    | Raw counts  | Rank normalization   | Expression binning   | Weighted resampling |
| Architecture Details | 50 components | 2-layer VAE | 12-layer transformer | 12-layer transformer | 4-layer transformer |
| Output Dimension     | 50            | 30          | 512                  | 512                  | 1280                |
| Genome Coverage      | 100%          | 100%        | 32.6%                | 33.0%                | 97.4%               |
| Ortholog Mapping     | No            | No          | Yes                  | Yes                  | No                  |

We implemented all embedding methods in Python following established protocols. Foundation models were selected based on their recommended configurations for zero-shot cell embedding tasks. While all methods use raw count data as input, each applies method-specific preprocessing steps according to their architectural requirements: PCA and scVI directly process raw counts, Geneformer applies rank normalization, scGPT performs gene binning, and UCE uses log normalization (Table 3.3).

- PCA was computed using deafult scanpy settings [52] with 50 principal components.
- scVI required retraining on our dataset using the scvi-tools package with 2 layers, 30 latent dimensions, and negative binomial gene likelihood. Raw count data were provided directly to scVI, as the model's probabilistic framework explicitly models technical variation including library size and batch effects (time points) through learned parameters [53]. The model trained for 163 epochs until convergence.
- Geneformer used the pre-trained gf-12L-95M-i4096 model (12 layers, ∼ 95 million parameters) with ortholog-mapped gene identifiers. Gene expression values were rank-normalized within each cell, ordering genes by their expression levels normalized by their corpus-wide expression patterns. This rank-based tokenization strategy prioritizes genes that distinguish cell states while reducing sensitivity to absolute expression levels.
- scGPT used the pre-trained scGPT\_CP model with ortholog-mapped gene identifiers. Expression values were binned into discrete tokens using a cell-specific binning strategy that divides expression levels into consecutive intervals, converting continuous values into categorical expression levels (e.g., low, medium, high). This approach enables the transformer to process gene expression as discrete tokens similar to words in natural language processing, while ensuring consistent semantic meaning across different sequencing batches.
- UCE was applied using the 4-layer foundation model rather than the deeper 33-layer variant. Genes were represented with ESM2 protein embeddings instead of gene identifiers, enabling cross-species use without orthology mapping. For each cell, UCE builds the input by drawing 1,024 times from the set of expressed (non-zero) genes with replacement, using log-transformed counts as weights so higher-count genes are more likely

to be selected. The 33-layer model produced artificial separations in our data, likely due to overfitting to patterns that do not generalize to Dictyostelium discoideum .

All embeddings were computed on the full dataset and stored for comparative evaluation across all metrics.

### 3.4 Evaluation Framework

To determine whether the embeddings capture meaningful biological relationships in Dictyostelium discoideum , we need evaluation metrics. Our central question is whether the embeddings preserve the developmental biology we understand from decades of research while being robust to technical variation in the scRNA-seq data.

#### 3.4.1 Trajectory Preservation

To evaluate whether embeddings preserve temporal relationships in Dictyostelium discoideum development, we implemented diffusion pseudotime (DPT) analysis [17]. DPT measures transitions between cells using diffusionlike random walks on a weighted nearest-neighbor graph, computing distances based on transition probabilities in diffusion map space. By ordering cells according to their probabilities of differentiating toward different fates, DPT reconstructs developmental trajectories and enables us to measure how well different embedding methods preserve the actual developmental sequence.

To address the uncertainty in root cell selection for trajectory inference, we implemented a robust multi-root approach. We sampled 500 candidate root cells from the 0-hour timepoint using uniform random sampling. For each embedding method, we constructed k-nearest neighbor graphs and computed DPT pseudotime using each candidate root separately. The diffusion map computation was performed once per embedding, then DPT was computed efficiently for each root candidate. All pseudotime values were scaled to the 20-hour developmental span.

The final pseudotime estimate for each embedding was computed as a weighted average across all candidate roots, providing a more robust measure than single-root approaches. This methodology reduces the impact of suboptimal root selection while maintaining computational efficiency.

To assess temporal alignment quality visually, we divided the resulting pseudotime values into six equally spaced bins and calculated the mean experimental time within each bin. These temporal alignment relationships were visualized as one-dimensional plots positioned below UMAP projections in our results, enabling direct evaluation of whether computational cell ordering corresponds to chronological progression. Well-preserved trajectories exhibit monotonic increases in experimental time across sequential pseudotime bins, providing an intuitive assessment of trajectory fidelity.

To quantify trajectory preservation, we evaluated the correlation between inferred pseudotime and actual developmental time using two complementary metrics with 95% bootstrap confidence intervals. The confidence intervals account for uncertainty from both cell sampling and root selection by implementing stratified bootstrap resampling across developmental time points while simultaneously sampling subsets of candidate roots (50 roots per bootstrap replicate from the full candidate set). This dual-sampling approach provides robust uncertainty estimates that capture both biological and methodological variability.

- Spearman Rank Correlation quantifies the monotonic relationship between computed pseudotime and actual sampling time, measuring whether embeddings preserve the ordering of developmental stages without requiring precise timing alignment [54]. The score ranges from -1 to 1 and is scaled to 0-1 by the transformation ( s +1) / 2 where s is the Spearman rank correlation coefficient.
- Lin's Concordance Correlation Coefficient (CCC) evaluates both precision and accuracy by combining correlation strength with agreement between pseudotime and sampling time scales. This metric provides a stringent assessment of trajectory preservation by penalizing both poor correlation

and systematic timing deviations [55].

#### 3.4.2 Biological Benchmarks and Scoring

We evaluate embedding quality using the single-cell Integration Benchmark (scIB) framework [18], which has become the standard for comparing integration methods.

For Dictyostelium discoideum , we focus on five key biological relationships that embeddings should preserve, ranked based on how well they should be preserved:

- Cell types. The fundamental prestalk/prespore distinction that defines cellular fate during development. We evaluate whether embeddings cluster cells according to their developmental destiny rather than technical artifacts [8, 48].
- cAMP signaling. Cyclic adenosine monophosphate (cAMP) serves as the primary signaling molecule coordinating development, acting as both an extracellular chemoattractant and intracellular second messenger. cAMP-induced genes are critical for aggregation, cell fate specification, and developmental timing. Embeddings should reflect the activity of cAMP-responsive pathways throughout development [50].
- Milestone gene expression. These genes exhibit sharp expression changes at specific developmental transitions and represent the temporal progression through aggregation, mound formation, slug migration, and culmination, with distinct subsets being downregulated or upregulated at each stage boundary [19]. Embeddings should capture clear separation between cells with high versus low expression of these milestone genes, reflecting the developmental transitions they mark.
- Regulon activity. Groups of genes that remain coordinately regulated despite genetic and temporal perturbations [19]. These include ribosome biogenesis genes (active during growth and early stages of development), cell death and morphogenesis genes (active mid-development), and terminal differentiation genes (active late in development).

Cell cycle. The cell cycle regulates cell growth and division through four phases (G1, S, G2, M) [23]. During Dictyostelium discoideum development, cells undergo compressed cell cycle dynamics with extremely short S and M phases, remaining predominantly in G2 phase [56]. This creates expression patterns where traditional cell cycle markers show minimal variation, making computational distinction between cell cycle states challenging despite cell cycle genes being among the most evolutionarily conserved across eukaryotes.

The specific gene sets and their sizes for each biological benchmark are detailed in Table 3.4.

To evaluate these relationships, we implemented a gene signature-based cell classification approach. For each gene set, we calculate signature scores by averaging normalized expression levels across constituent genes. We then apply Otsu's thresholding method to distinguish cells with high versus low signature scores.

Otsu's method automatically finds the optimal threshold t ∗ that maximizes the between-class variance while minimizing within-class variance [20]. Given signature scores, the method maximizes the between-class variance criterion:

<!-- formula-not-decoded -->

where ω 0 ( t ) and ω 1 ( t ) are the proportions of cells below and above threshold t , respectively, and µ 0 ( t ) and µ 1 ( t ) are their corresponding mean signature scores. This criterion effectively separates the signature score distribution into two groups by finding the threshold that maximizes the separation between their means while accounting for class proportions.

This objective and adaptive approach provides biologically meaningful categories without requiring manual threshold selection, ensuring consistent classification across different gene sets and embedding methods. The approach transforms the continuous gene expression space into discrete biological categories that can be compared across different embedding methods.

Having established these biologically meaningful cell classifications, we can now evaluate how well different embedding methods preserve these relationships using the scIB framework's quantitative metrics.

Table 3.4: Gene sets used for biological benchmark evaluation. Milestones represent genes differentially expressed during D. discoideum developmental transitions (↑ = upregulated, ↓ = downregulated) [19].

| Biological benchmark   | Gene set                             |   # of genes | Examples of genes          |
|------------------------|--------------------------------------|--------------|----------------------------|
| Cell type              | prespore                             |           36 | pspA, cotA                 |
|                        | prestalk                             |           47 | ecmA, ampA                 |
| Milestones             | no aggregation → rippling ↓          |          294 | cupA, uduA2                |
|                        | loose aggregate → tight aggregate ↓  |           11 | pks26, rliD                |
|                        | tight aggregate → tipped aggregate ↓ |           20 | rasY, prtA                 |
|                        | Mexican hat → culmination ↓          |            9 | DDB_G0293676, DDB_G0268158 |
|                        | no aggregation → rippling ↑          |          247 | pks26, tgrO2               |
|                        | rippling → loose aggregate ↑         |           71 | mybAA, cmbC                |
|                        | loose aggregate → tight aggregate ↑  |          260 | kif2, aslM                 |
|                        | tight aggregate → tipped aggregate ↑ |           35 | tps2, cyp519C1             |
|                        | tipped aggregate → slug ↑            |           12 | osbB, DDB_G0281015         |
|                        | slug → Mexican hat ↑                 |          209 | sahA, stcA                 |
|                        | Mexican hat → culmination ↑          |           45 | aslA-1, sigL-1             |
| Regulon clusters       | C1                                   |           30 | bms1l, bxdc1               |
|                        | C2                                   |           66 | acly, atp5D                |
|                        | C3                                   |           68 | abcA1, abcA9               |
|                        | C4                                   |           55 | DD7-1, abnB                |
|                        | C5                                   |           41 | dpp3-1, lap                |
|                        | C6                                   |           74 | 5NT, acaA                  |
|                        | C7                                   |           40 | ak1, detA                  |
|                        | C8                                   |           23 | arrD, colA                 |
|                        | C9                                   |           20 | sigN1, sigN11              |
|                        | C10                                  |           36 | ase1A, aurK                |
|                        | C11                                  |           77 | D7, aarA                   |
|                        | C12                                  |           57 | abcG7, carB                |
|                        | C13                                  |           64 | 2C, cyp516A1               |
|                        | C14                                  |           19 | ecmF, zplC-1               |
|                        | C15                                  |           91 | abcG5, abcG6               |
|                        | C16                                  |           74 | 7E, adamts                 |
|                        | C17                                  |           61 | ecmB, fmoB                 |
|                        | C18                                  |           46 | cotE, cyp516B1             |
|                        | C19                                  |           58 | aco, cfr ps1               |
|                        | C20                                  |           54 | abcG18, aslA-1             |
| cAMP-induced genes     | cAMP-induced genes                   |           59 | cbpA, cotB                 |
| cell cycle             | S phase                              |           12 | plk, aurK                  |
|                        | M phase                              |           12 | pcnA, cdc45                |

To quantify biological conservation across embedding methods, we use the avgBIO composite metric, which measures the overall preservation of biological relationships [5]. This summary score averages three complementary clustering metrics to provide a comprehensive assessment of how well embeddings maintain biologically meaningful cell type distinctions while avoiding overreliance on any single measure. The avgBIO score ranges from 0 to 1, where higher values indicate better preservation of biological structure:

<!-- formula-not-decoded -->

This composite approach balances different aspects of clustering quality, ensuring robust evaluation across diverse biological contexts. Each component metric captures distinct properties of biological conservation, and their combination provides a unified framework for comparing embedding performance. The three constituent metrics are:

Normalized Mutual Information (NMI) quantifies the agreement between computationally discovered clusters and known biological cell type labels [57]. NMI measures how much information the clustering structure shares with the true biological classification, normalized by the entropy of both partitions. Values range from 0 (no agreement) to 1 (perfect agreement), where higher values indicate that the embedding successfully preserves biologically meaningful cell type distinctions:

<!-- formula-not-decoded -->

where I ( X,Y ) is the mutual information between cluster assignments X and true labels Y , and H ( X ) and H ( Y ) are their respective entropies. The normalization ensures that NMI accounts for differences in cluster number and size distribution, making it robust for comparing embeddings with varying cluster structures.

Adjusted Rand Index (ARI) measures clustering agreement while correcting for chance, making it robust for imbalanced datasets [58]. The Rand Index counts the fraction of cell pairs that are either both in the same cluster and same true class, or both in different clusters and different true classes. ARI provides the chance-corrected version that ranges from 0 to 1, with 1 indicating perfect agreement:

<!-- formula-not-decoded -->

where Index is the observed Rand Index from the clustering, Expected Index is the Rand Index expected by random chance, and Maximum Index is the highest possible Rand Index given the cluster and class sizes. This normalization ensures that ARI captures actual clustering performance beyond what would be expected from random assignments.

Average Silhouette Width (ASW) for cell types evaluates how well different cell types are separated while maintaining within-type cohesion [59]. For each cell, the silhouette width measures the quality of its cluster assignment by comparing intra-cluster distances to inter-cluster distances:

<!-- formula-not-decoded -->

where a ( i ) is the average distance from cell i to other cells within the same cluster and b ( i ) is the average distance to cells in the nearest neighboring cluster. Silhouette widths range from -1 to +1, with higher values indicating better cluster assignment. The score is scaled to the range 0-1 for evaluation, where values closer to 1 indicate that cells are well-matched to their assigned clusters and poorly matched to neighboring clusters.

## Chapter 4

## Results

We comprehensively evaluated the cross-species generalization capabilities of foundation models by comparing five embedding approaches on Dictyostelium discoideum development. Our analysis compared traditional methods (PCA, scVI) against foundation models (scGPT, Geneformer, UCE) using two complementary evaluation frameworks: trajectory preservation analysis and biological conservation benchmarks.

### 4.1 UCE and scGPT Lead in Trajectory Alignment

We evaluated how well different embedding methods preserve the temporal progression of Dictyostelium discoideum development using diffusion pseudotime analysis. Each embedding method was assessed on its ability to maintain the correct ordering of developmental stages and align computational pseudotime with experimental sampling times.

Figure 4.1: Trajectory preservation across embedding methods during Dictyostelium discoideum development. (a) Each panel shows results for one embedding method. Upper images display UMAP projections where each dot represents a single cell positioned according to the first two UMAP dimensions (x and y axes), with dot color representing experimental sampling time; lower graphs show temporal alignment plots mapping computational pseudotime bins (x-axis) to experimental time distributions (y-axis). (b) Quantitative evaluation of trajectory preservation performance. Upper bars show Spearman rank correlation coefficients; lower bars display Lin's concordance correlation coefficients. The confidence intervals are computed via 1000 bootstrap iterations.

<!-- image -->

Visual analysis of UMAP projections reveals distinct patterns across embedding methods (Figure 4.1a). PCA embeddings demonstrate the clearest temporal clustering, with cells forming distinct islands for each sampling time and exhibiting only slight overlap between the 16 and 20 hour time points. In contrast, the foundation models reveal an intriguing biological pattern that transcends simple temporal progression. scVI displays the most pronounced bifurcation, where the 12, 16, and 20 hour samples each split into two distinct clusters, with these paired clusters elegantly separated by the 8 hour sample. UCE shows a similar but more subtle splitting pattern, particularly evident in the later time points where cells segregate into distinct subgroups. scGPT and Geneformer exhibit this bifurcation to a lesser degree. This consistent emergence of dual clusters across multiple foundation models hints at an underlying biological structure-the discovery of distinct cellular identities that become apparent only when examined through the lens of cell type classification in the following analysis.

The temporal alignment plots provide a quantitative assessment of the pseudotime preservation quality. scGPT achieves the best alignment between pseudotime and sampling time among all methods tested, with only slight deviations from the experimental timeline. PCA demonstrates good overall temporal alignment, though the 8 and 12 hour stages are compressed leftward on the timeline. UCE displays intermediate performance with early time points (0, 4, 8, 12, 16 hours) shifted leftward, tight clustering of 12 and 16 hour stages, and 20 hour cells dominating the timeline's right portion. Geneformer performs the worst in terms of alignment, with the 12, 16 and 20 hour time points mixed and compressed toward the right. scVI exhibits the most problematic time point distribution, with 4 and 8 hour stages spreading extensively rightward while the 12, 16, and 20 hour stages cluster together at the timeline's end.

Quantitative trajectory metrics confirm these observations (Figure 4.1b). Spearman rank correlation coefficients demonstrate strong monotonic relationships for all methods, with values around 0.9 and confidence intervals confirming that their differences are not statistically significant. These values indicate that all embedding methods successfully preserve the overall temporal ordering. Lin's concordance correlation coefficients provide a more stringent evaluation of both correlation strength and timing accuracy: UCE leads with 0.873, scGPT follows with 0.857, PCA achieves 0.814, Geneformer reaches 0.792, and scVI scores 0.657. The lower concordance scores relative to rank correlations reveal timing deviations, with scVI showing the largest discrepancy between preserved ordering and actual temporal alignment, as also demonstrated in the temporal alignment plots.

### 4.2 UCE Achieves Superior Biological Conservation

We assessed how well embedding methods maintain key biological patterns in Dictyostelium discoideum using the scIB framework across five distinct biological features. UCE consistently outperforms other methods on most biological benchmarks, achieving the highest avgBIO scores for four out of five evaluated features.

Cell type classification reveals the most pronounced performance differences across embedding methods and resolves the clustering patterns observed in trajectory analysis. The dual clusters that emerged in later developmental time points across multiple foundation models now reveal their biological significance: they correspond precisely to prespore and prestalk cell fate decisions. UCE achieves exceptional performance in distinguishing these cell fates with an avgBIO score of 0.724, substantially outperforming all other methods (Figure 4.2). Geneformer ranks second with 0.459, followed by scGPT at 0.445, scVI at 0.438, and PCA at 0.349.

cAMP signaling pathway preservation shows strong UCE performance as well. UCE achieves the highest avgBIO score of 0.820, again demonstrating superior clustering of cells based on cAMP-responsive gene expression patterns (Figure 4.2). Another method that performs relatively well is scGPT with the avgBIO score of 0.582. The remaining methods cluster closer to- gether: Geneformer achieves 0.449, scVI attains 0.462, and PCA scores 0.392. Visual inspection reveals UCE and scGPT create two well-defined clusters representing high and low activity of cAMP induced genes.

Figure 4.2: Cell type classification performance and cAMP-induced gene expression analysis. (a) UMAP projections where each dot represents a single cell colored by cell type assignments based on expression signatures. (b) AvgBIO scores measuring clustering agreement with cell types. (c) UMAP projections where each dot represents a single cell colored by expression signatures of cAMP-induced genes. (d) AvgBIO scores measuring clustering agreement with cAMP-induced gene expression signatures.

<!-- image -->

Figure 4.3: Preservation of milestone gene expression and regulon activity. (a) UMAP embeddings where each dot represents a single cell colored by milestone gene expression signatures. (b) AvgBIO score quantifying clustering agreement with milestone gene signatures. (c) UMAP embeddings where each dot represents a single cell colored by regulon activity signatures. (d) AvgBIO score quantifying clustering agreement with regulon activity signatures.

<!-- image -->

Figure 4.4: Cell cycle state preservation across embedding methods. (a) UMAP projections where each dot represents a single cell colored by cell cycle phase signatures. (b) AvgBIO scores measuring clustering agreement with cell cycle signatures.

<!-- image -->

Milestone gene expression analysis demonstrates UCE's continued advantage, though with reduced performance margins. UCE leads with an avgBIO score of 0.320, scGPT follows with 0.342 while other methods perform more similarly: scVI achieves 0.315, Geneformer reaches 0.308, and PCA scores 0.278 (Figure 4.3). The smaller performance differences suggest that milestone gene patterns are more challenging to capture, as these genes are transiently upregulated and downregulated during developmental transitions rather than defining stable cell type identities.

Regulon activity preservation follows the established pattern with UCE

achieving the highest avgBIO score of 0.399 and scGPT following with 0.342. Performance differences remain modest among other methods: scVI reaches 0.315, Geneformer achieves 0.308, and PCA scores 0.278 (Figure 4.3). These results indicate UCE better captures the coordinated expression patterns of gene regulatory networks by a small margin.

Cell cycle classification presents the only exception to UCE's dominance. All methods perform poorly, with avgBIO scores around 0.2. This finding suggests that cell cycle classification is inherently challenging for all embedding methods, likely due to the compressed cell cycle dynamics in Dictyostelium discoideum development.

### 4.3 Discussion

Our findings demonstrate that foundation models can indeed capture meaningful biological relationships across vast evolutionary distances, challenging the assumption that such models are fundamentally constrained by their training distribution. The superior performance of UCE across four out of five biological benchmarks in Dictyostelium discoideum suggests that certain aspects of cellular organization represent universal principles that persist despite profound evolutionary divergence.

This universality appears most pronounced in fundamental cellular processes. UCE's exceptional performance in distinguishing prespore and prestalk cell fates indicates that the molecular signatures underlying cell type specification follow conserved patterns that foundation models can recognize. Similarly, the strong preservation of cAMP signaling pathways suggests that core signaling mechanisms maintain sufficient molecular similarity across species to enable cross-species recognition by protein-based representations.

The protein-centric approach underlying UCE's design proves particularly insightful in this context. By representing genes through their encoded protein sequences rather than relying on explicit orthology mapping, UCE captures functional relationships that transcend species-specific gene nomenclature and evolutionary history. This approach effectively leverages the fact that protein function is more conserved than sequence identity, enabling the model to recognize functionally equivalent proteins even when their evolutionary relationships are unclear.

Remarkably, our trajectory analysis reveals that UCE captures the most critical period of developmental decision-making through its pseudotime compression patterns (Figure 4.5). The compressed scale around 9 hours aligns precisely with the known fate-choice leap, when canonical prespore and prestalk markers fire together in rapid succession. This observation suggests that UCE successfully identifies and emphasizes the period of most intense molecular change, when cells commit to their final fates through coordinated transcriptional programs.

Figure 4.5: Comparison of sampling time and pseudotime in UCE embeddings. (a) UMAP projections colored by sampling time and (b) pseudotime. Bottom graph shows the temporal alignment plot mapping computational pseudotime bins to experimental time distributions.

<!-- image -->

Despite UCE's overall strong performance, our results reveal specific domains where foundation model universality encounters biological constraints. The universal poor performance across all embedding methods in cell cycle classification likely reflects the compressed cell cycle dynamics in Dictyostelium discoideum development rather than limitations in cross-species generalization per se, demonstrating that even highly conserved processes may not be computationally tractable when their underlying temporal dynamics differ substantially from typical systems.

## Chapter 5

## Conclusions

Foundation models in computational biology promise to capture universal cellular patterns that transcend experimental contexts. However, their universality claims have remained largely theoretical, with most validation occurring within domains similar to their training data. Current research focuses primarily on performance within familiar biological contexts, while the critical challenge of cross-species generalization remains largely unexplored despite being essential for comparative biology and universal principle discovery.

Our work fills this gap by providing an evaluation of foundation model generalization across evolutionary boundaries. Through a comprehensive evaluation framework that systematically compares five embedding approaches using biological conservation metrics and trajectory preservation analysis, we provide an assessment of different gene representation strategies for crossspecies analysis. By testing foundation models on Dictyostelium discoideum , an organism separated from typical training species by hundreds of millions of years of evolution, we demonstrate that foundation models can transcend their training limitations to capture meaningful biological relationships in evolutionarily distant organisms. Our work establishes biological benchmarks for non-metazoan development and demonstrates that UCE achieves superior biological conservation across most benchmarks while preserving developmental trajectories, establishing that protein-based gene representations can effectively bridge species boundaries without requiring orthology mapping or retraining.

The practical implications extend beyond technical validation. Foundation models offer researchers working with non-model organisms a compelling alternative to traditional dimensionality reduction approaches, potentially eliminating the need for extensive batch correction and dataset-specific preprocessing while maintaining biological interpretability. By preserving biological meaning while reducing computational bottlenecks, these models democratize access to sophisticated analytical approaches across diverse biological systems.

This work establishes systematic computational evaluation frameworks for assessing cross-species generalization and contributes evaluation tools for assessing future models, providing essential guidance for researchers seeking to apply foundation models beyond their original training domains. Beyond immediate applications, our findings open avenues for extending these approaches to other evolutionarily distant organisms and demonstrate the feasibility of applying foundation models to comparative biology studies that were previously challenging. As foundation models become increasingly sophisticated, understanding their capabilities and limitations across diverse biological contexts becomes essential for responsible application in computational biology research.

### Bibliography

- [1] Fuchou Tang, Catalin Barbacioru, Yangzhou Wang, Ellen Nordman, et al. mRNA-Seq whole-transcriptome analysis of a single cell. Nature Methods , 6(5):377-382, 2009.
- [2] Rishi Bommasani, Drew A Hudson, Ehsan Adeli, Russ Altman, et al. On the opportunities and risks of foundation models. arXiv preprint arXiv:2108.07258 , 2021.
- [3] Xu Chang, Yunxi Zheng, and Kai Xu. Single-cell RNA sequencing: Technological progress and biomedical application in cancer research. Molecular Biotechnology , 66(7):1497-1519, July 2024.
- [4] Christina V. Theodoris, Ling Xiao, Anant Chopra, Mark D. Chaffin, et al. Transfer learning enables predictions in network biology. Nature , 618:616-624, 2023.
- [5] Haotian Cui, Chloe Wang, Hassaan Maan, Kuan Pang, et al. scGPT: toward building a foundation model for single-cell multi-omics using generative ai. Nature Methods , 21:1470-1480, 2024.
- [6] Yanay Rosen, Yusuf Roohani, Ayush Agrawal, Leon Samotorcan, et al. Universal cell embeddings: A foundation model for cell biology. bioRxiv , 2024.
- [7] Sudhir Kumar, Michael Suleski, Jack M Craig, Adrienne E Kasprowicz, et al. TimeTree 5: An expanded resource for species divergence times. Molecular Biology and Evolution , 39(8):msac174, August 2022.

- [8] Richard H. Kessin. Dictyostelium: Evolution, Cell Biology, and the Development of Multicellularity . Cambridge University Press, Cambridge, 2001.
- [9] Malte D Luecken and Fabian J Theis. Current best practices in single-cell RNA-seq analysis: a tutorial. Molecular Systems Biology , 15(6):e8746, 2019.
- [10] Ian T Jolliffe and Jorge Cadima. Principal component analysis. Philosophical Transactions of the Royal Society A , 374(2065):20150202, 2016.
- [11] Romain Lopez, Jeffrey Regier, Michael B. Cole, Michael I. Jordan, et al. Deep generative modeling for single-cell transcriptomics. Nature Methods , 15:1053-1058, 2018.
- [12] Kasia Z. Kedzierska, Lorin Crawford, Ava P. Amini, and Alex X. Lu. Zero-shot evaluation reveals limitations of single-cell foundation models. Genome Biology , 26(1):101, April 2025.
- [13] Jeffrey G Williams. Dictyostelium finds new roles to model. Genetics , 185(3):717-726, July 2010.
- [14] Fredrik Tegenfeldt, Dmitry Kuznetsov, Mosè Manni, Matthew Berkeley, et al. OrthoDB and BUSCO update: annotation of orthologs with wider sampling of genomes. Nucleic Acids Research , 53(D1):D516-D522, January 2025.
- [15] Rafael David Rosengarten, Balaji Santhanam, Danny Fuller, Mariko Katoh-Kurasawa, William F Loomis, Blaz Zupan, and Gad Shaulsky. Leaps and lulls in the developmental transcriptome of Dictyostelium discoideum. BMC Genomics , 16(1):294, December 2015.
- [16] Zeming Lin, Halil Akin, Roshan Rao, Brian Hie, et al. Evolutionaryscale prediction of atomic-level protein structure with a language model. Science , 379(6637):1123-1130, 2023.

- [17] Laleh Haghverdi, Maren Büttner, F Alexander Wolf, Florian Buettner, et al. Diffusion pseudotime robustly reconstructs lineage branching. Nature Methods , 13(10):845-848, 2016.
- [18] Malte D Luecken, Maren Büttner, Kridsadakorn Chaichoompu, Anna Danese, et al. Benchmarking atlas-level data integration in single-cell genomics. Nature Methods , 19(1):41-50, 2022.
- [19] Mariko Katoh-Kurasawa, Karin Hrovatin, Shigenori Hirose, Amanda Webb, et al. Transcriptional milestones in Dictyostelium development. Genome Research , 31(8):1498-1511, 2021.
- [20] Nobuyuki Otsu. A threshold selection method from gray-level histograms. IEEE transactions on systems, man, and cybernetics , 9(1):62-66, 1979.
- [21] Yoshua Bengio, Aaron Courville, and Pascal Vincent. Representation learning: a review and new perspectives. IEEE Transactions on Pattern Analysis and Machine Intelligence , 35(8):1798-1828, 2013.
- [22] Eugene V Koonin. Orthologs, paralogs, and evolutionary genomics. Annual Review of Genetics , 39:309-338, 2005.
- [23] Bruce Alberts, Alexander Johnson, Julian Lewis, David Morgan, et al. Molecular Biology of the Cell . Garland Science, New York, 6th edition, 2015.
- [24] Michael B Elowitz, Arnold J Levine, Eric D Siggia, and Peter S Swain. Stochastic gene expression in a single cell. Science , 297(5584):1183-1186, 2002.
- [25] Hannah Dueck, James Eberwine, and Junhyong Kim. Variation is function: Are single cell differences functionally important? Testing the hypothesis that single cell variation is required for aggregate function. BioEssays , 38(2):172-180, February 2016.

- [26] Giulia Carangelo, Luca Muccillo, et al. From multitude to singularity: An up-to-date overview of scRNA-seq data generation and analysis. Frontiers in Genetics , 13:994069, 2022.
- [27] Huidong Chen, Luca Albergante, Jonathan Y. Hsu, Caleb A. Lareau, et al. Single-cell trajectories reconstruction, exploration and mapping of omics data with STREAM. Nature Communications , 10(1):1903, April 2019.
- [28] Daniel E Wagner, Caleb Weinreb, Zach M Collins, James A Briggs, et al. Single-cell mapping of gene expression landscapes and lineage in the zebrafish embryo. Science , 360(6392):981-987, 2018.
- [29] Isaac N Grabski and Rafael A Irizarry. Significance analysis for clustering with single-cell RNA-sequencing data. Nature Methods , 20(8):1196-1202, 2023.
- [30] Hiroaki Kitano. Biological robustness. Nature Reviews Genetics , 5(11):826-837, 2004.
- [31] Wanze Chen, Orane Guillaume-Gentil, Pernille Yde Rainer, Christoph G. Gäbelein, et al. Live-seq enables temporal transcriptomic recording of single cells. Nature , 608(7924):733-740, August 2022.
- [32] Gioele La Manno, Ruslan Soldatov, Amit Zeisel, Emelie Braun, et al. RNA velocity of single cells. Nature , 560(7719):494-498, August 2018.
- [33] Valentine Svensson, Roser Vento-Tormo, and Sarah A Teichmann. Exponential scaling of single-cell RNA-seq in the past decade. Nature Protocols , 13(4):599-604, 2018.
- [34] He Jiangping, Lin Lihui, Chen Jiekai, et al. Practical bioinformatics pipelines for single-cell RNA-seq data analysis. Biophysics Reports , 8(3):158-169, 2022.

- [35] Lukas Heumos, Anna C. Schaar, Christopher Lance, Anastasia Litinetskaya, et al. Best practices for single-cell analysis across modalities. Nature Reviews Genetics , 24(8):550-572, August 2023.
- [36] Ruochen Jiang, Tianyi Sun, Dongyuan Song, and Jingyi Jessica Li. Statistics or biology: the zero-inflation controversy about scRNA-seq data. Genome Biology , 23(1):31, January 2022.
- [37] Christoph Hafemeister and Rahul Satija. Normalization and variance stabilization of single-cell RNA-seq data using regularized negative binomial regression. Genome Biology , 20(1):296, December 2019.
- [38] Gregory B Gloor, Jean M Macklaim, Vera Pawlowsky-Glahn, and Juan J Egozcue. Microbiome datasets are compositional: and this is not optional. Frontiers in Microbiology , 8:2224, 2017.
- [39] Mengjie Cheng, Zhenyi Jiang, et al. A review of single-cell RNA-Seq annotation, integration, and cell-cell communication. Cells , 12(14):1907, 2023.
- [40] Kevin Gurney. An Introduction to Neural Networks . CRC Press, 1 edition, October 2018.
- [41] Pascal Vincent, Hugo Larochelle, Isabelle Lajoie, Yoshua Bengio, et al. Stacked denoising autoencoders: Learning useful representations in a deep network with a local denoising criterion. Journal of Machine Learning Research , 11:3371-3408, 2010.
- [42] Xiao Liu, Fanjin Zhang, Zhenyu Hou, Li Mian, et al. Self-supervised learning: Generative or contrastive. IEEE Transactions on Knowledge and Data Engineering , 35(1):857-876, 2021.
- [43] Sinno Jialin Pan and Qiang Yang. A survey on transfer learning. IEEE Transactions on Knowledge and Data Engineering , 22(10):1345-1359, 2010.

- [44] Diederik P. Kingma and Max Welling. Auto-Encoding Variational Bayes, December 2022. arXiv:1312.6114 [stat].
- [45] Philipp Weiler, Marius Lange, Michal Klein, Dana Pe'er, et al. CellRank 2: unified fate mapping in multiview single-cell data. Nature Methods , 21(7):1196-1205, July 2024.
- [46] Rafael D. Rosengarten, Balaji Santhanam, Janez Kokosar, and Gad Shaulsky. The long non-coding RNA transcriptome of Dictyostelium discoideum development. G3: Genes|Genomes|Genetics , 7(2):387-398, 2017.
- [47] Lucija Strmecki, Dana M Greene, and Catherine J Pears. Developmental decisions in Dictyostelium discoideum. Developmental Biology , 284(1):2536, 2005.
- [48] Toshinari Maruo, Haruyo Sakamoto, Negin Iranfar, Danny Fuller, et al. Control of cell type proportioning in Dictyostelium discoideum by differentiation-inducing factor as determined by in situ hybridization. Eukaryotic Cell , 3(5):1241-1248, October 2004.
- [49] Vanja Antolović, Thorsten Lenn, Anaïs Miermont, and Jonathan R Chubb. Generation of single-cell transcript variability by repression. Current Biology , 27(12):1811-1817, 2017.
- [50] Paul Kriebel and Carole Parent. Adenylyl cyclase expression and regulation during the differentiation of Dictyostelium discoideum. IUBMB life , 56(9):541-546, 2004.
- [51] Glaucia M. Souza, John Hirai, Darshini P. Mehta, and Hudson H. Freeze. Identification of two novel Dictyostelium discoideum cysteine proteinases that carry N-Acetylglucosamine-1-P modification. Journal of Biological Chemistry , 270(48):28938-28945, December 1995.

- [52] F Alexander Wolf, Philipp Angerer, and Fabian J Theis. Scanpy: largescale single-cell gene expression data analysis. Genome Biology , 19(1):15, 2018.
- [53] Adam Gayoso, Romain Lopez, Galen Xing, Pierre Boyeau, et al. A python library for probabilistic analysis of single-cell omics data. Nature Biotechnology , Feb 2022.
- [54] Charles Spearman. The proof and measurement of association between two things. American Journal of Psychology , 15(1):72-101, 1904.
- [55] Lawrence I-Kuei Lin. A concordance correlation coefficient to evaluate reproducibility. Biometrics , 45(1):255-268, 1989.
- [56] Gerald Weeks and Cornelis J. Weijer. The Dictyostelium cell cycle and its relationship to differentiation. FEMS Microbiology Letters , 124(2):123130, December 1994.
- [57] Alexander Strehl and Joydeep Ghosh. Cluster ensembles - a knowledge reuse framework for combining multiple partitions. Journal of Machine Learning Research , 3:583-617, 2002.
- [58] Lawrence Hubert and Phipps Arabie. Comparing partitions. Journal of Classification , 2:193-218, 1985.
- [59] Peter J. Rousseeuw. Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. Journal of Computational and Applied Mathematics , 20:53-65, 1987.