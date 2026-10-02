# 2026 Medicine candidate list from Codex

This draft, originally prepared independently, contains 32 discovery-centered candidates for the 2026 Nobel Prize in Physiology or Medicine. It is intended for comparison with Claude's independently prepared list and subsequent committee review. The strongest reason to use a broad longlist is coverage: the committee should choose the achievement and its laureates rather than inherit an author's top-three guess.

Research cutoff: 2 October 2026, America/Chicago. Version 1 was drafted without reading Claude's candidate files and is preserved in `revisions/v1/`. Version 2 corrects Habener's eligibility after comparison; no other discoveries or names have been imported from Claude. See [the comparison](comparison_with_claude.md). The nominator stage is omitted as requested. No nomination counts, winning probabilities or committee outcomes are invented.

## Files and committee use

- `candidates.json` is the canonical independent draft, including sources, attribution issues and author assessments.
- `candidates.csv` provides the same 32 entries in a flat table for comparison.
- `committee_longlist.json` contains only the existing member-facing packet fields: `schema_version`, then `ballot_id`, `discovery`, `subfield` and alphabetized `credited_names` per entry.
- `ballot_map.json` maps neutral ballot IDs to the draft's candidate IDs. Give it only to the coordinator.

The draft is alphabetical, not ranked. The committee packet uses a deterministic SHA-256 shuffle with seed `medicine-direct-longlist-c-v2`. Serialize each public payload as compact UTF-8 JSON with sorted keys and unescaped Unicode; hash the seed, a null separator and the serialized payload. Sort by hash, serialized payload, then candidate ID, and assign consecutive B001 through B032. This follows the presentation-blinding approach in the Physics workflow. It does not make this input a simulated nomination sample.

For initial opening rankings, provide only the member's profile and the committee packet. The rationale, reservations, author identity, source registry and crosswalk are research and comparison materials; adding them to opening prompts would change the existing evidence boundary. The packet matches the existing field layout, but the Physics orchestration and validators are category-specific and require 100 nomination records. They cannot be used unchanged for this direct Medicine list.

## Selection and attribution

I included mature discoveries of basic physiology and cell biology alongside major clinical advances and enabling inventions. Award organizations and original papers support the underlying scientific claims; inclusion and reservations are my judgments. Other awards are useful leads, not proof of Nobel candidacy. Coverage is intentionally broader than a final shortlist.

Each credited-name list is a provisional attribution pool. It is neither an actual nomination nor a recommendation to award everyone in the pool. The committee must identify a coherent discovery and select no more than three laureates across the entire prize, including any award split between achievements. GLP-1, optogenetics, PCSK9, CFTR therapy, single-cell methods and condensates need especially careful attribution. Distinct gene discovery and drug-development achievements remain separate where combining them would hide the choice of contribution.

Known deceased pioneers are retained in historical notes rather than eligible name pools: Joel Habener for GLP-1, Zelig Eshhar for CAR-T, Douglas Coleman for leptin, and Dieter Oesterhelt for optogenetics. The already rewarded 2025 peripheral immune-tolerance discovery is not recycled as a new candidate. Recent awards and institutional material were consulted, including the 2026 Lasker awards and 2026 Gairdner material. Historical scientific citations do not establish current life status for every alternative name; this draft is not a complete eligibility registry.

Single-cell RNA sequencing includes Sandberg and Linnarsson, both of whom have existing committee personas in this repository. Spatial transcriptomics also involves Linnarsson as a foundational-paper coauthor. These conflicts are explicit in the JSON. The draft does not resolve recusal or voting rules, and committee simulation must specify how those conflicts are handled. Their names are retained to avoid tailoring scientific attribution to the convenience of the simulation.

## Candidate overview

| Discovery | Names for attribution review |
|---|---|
| A bispecific antibody that substitutes for factor VIII activity in hemophilia A | Kunihiro Hattori; Takehisa Kitazawa; Tomoyuki Igawa |
| Adult stem-cell-derived organoids for studying tissue biology and disease | Hans Clevers; Toshiro Sato |
| BCR-ABL inhibition and molecularly targeted treatment of chronic myeloid leukemia | Brian J. Druker; Charles L. Sawyers; Nicholas B. Lydon |
| Biomolecular condensates and phase separation in cellular organization | Anthony A. Hyman; Clifford P. Brangwynne; Dirk Görlich; Steven L. McKnight |
| CFTR functional rescue and modulator therapies for cystic fibrosis | Fred Van Goor; Jesús Tito González; Michael J. Welsh; Paul A. Negulescu; Sabine Hadida |
| Chaperonin-assisted protein folding | Arthur L. Horwich; F. Ulrich Hartl |
| DNA methylation as a mechanism regulating gene expression | Adrian P. Bird; Howard Cedar; Rudolf Jaenisch |
| Genetically engineered CAR-T cells for treating cancer | Carl H. June; Michel Sadelain |
| GLP-1 physiology and the development of incretin therapies for diabetes and obesity | Daniel J. Drucker; Jens Juul Holst; Lotte Bjerre Knudsen; Svetlana Mojsov |
| HER2-directed antibody therapy for breast cancer | Axel Ullrich; Dennis J. Slamon; H. Michael Shepard |
| Identification of CFTR as the gene responsible for cystic fibrosis | Francis S. Collins; John R. Riordan; Lap-Chee Tsui |
| IL-6 signaling and therapeutic blockade of the IL-6 receptor | Tadamitsu Kishimoto; Toshio Hirano |
| Integrins as receptors mediating cell-matrix and cell-cell adhesion | Erkki Ruoslahti; Richard O. Hynes; Timothy A. Springer |
| Kinetic stabilization of transthyretin and treatment of amyloid disease | Jeffery W. Kelly |
| Leptin and endocrine regulation of appetite and body weight | Jeffrey M. Friedman |
| Long-term potentiation and the synaptic basis of learning and memory | Graham L. Collingridge; Richard G. M. Morris; Timothy V. P. Bliss |
| Mammalian genomic imprinting and parent-of-origin gene expression | Davor Solter; M. Azim Surani |
| Massively parallel DNA sequencing for genome-scale biology and medicine | David Klenerman; Pascal Mayer; Shankar Balasubramanian |
| Notch signaling as a mechanism of cell-fate specification | Gary Struhl; Iva Greenwald; Spyros Artavanis-Tsakonas |
| Optical coherence tomography for noninvasive tissue imaging | David Huang; Eric A. Swanson; James G. Fujimoto |
| Optogenetic control of genetically specified cells with light | Edward S. Boyden; Ernst Bamberg; Georg Nagel; Gero Miesenböck; Karl Deisseroth; Peter Hegemann |
| Orexin signaling in wakefulness and the cause of narcolepsy | Emmanuel Mignot; Masashi Yanagisawa |
| PCSK9 and human genetic validation of a cholesterol-lowering therapeutic target | Catherine Boileau; Helen H. Hobbs; Jonathan C. Cohen; Marianne Abifadel; Nabil G. Seidah |
| Single-cell RNA sequencing for resolving cellular identity and heterogeneity | Aviv Regev; Evan Z. Macosko; Fuchou Tang; Rickard Sandberg; Sten Linnarsson; Stephen R. Quake; Steven A. McCarroll |
| Spatial transcriptomics for mapping gene expression within intact tissue | Joakim Lundeberg; Jonas Frisén; Patrik L. Ståhl; Xiaowei Zhuang |
| The BRCA1 locus and the genetic basis of inherited breast cancer | Mary-Claire King |
| The cGAS-STING pathway linking cytosolic DNA sensing to innate immunity | Glen N. Barber; Hiroki Ishikawa; Jiaxi Wu; Lijun Sun; Zhijian James Chen |
| The unfolded protein response and signaling from the endoplasmic reticulum | Kazutoshi Mori; Peter Walter |
| TNF blockade as a treatment for rheumatoid arthritis and inflammatory disease | Marc Feldmann; Ravinder N. Maini |
| TOR signaling as a regulator of cell growth and nutrient responses | David M. Sabatini; Michael N. Hall; Stuart L. Schreiber |
| VEGF biology and inhibition of pathological angiogenesis | Donald R. Senger; Harold F. Dvorak; Napoleone Ferrara |
| Virus-like particle vaccines that prevent HPV infection and related cancers | Douglas R. Lowy; Ian H. Frazer; John T. Schiller |

## Scientific basis and author assessment

The scientific basis paragraphs below summarize linked sources. Reasons for inclusion, reservations and provisional attribution choices are author judgments, not claims made by those sources.

### A bispecific antibody that substitutes for factor VIII activity in hemophilia A

**Scientific basis:** Emicizumab bridges coagulation factors IX and X to compensate for deficient factor VIII activity. Sources: [Lasker 2026 scientific accounts of orexin and emicizumab](https://laskerfoundation.org/winners/2026-winners/).

**Why include it:** A specific engineering invention with a clear clinical mechanism and substantial treatment benefit.

**Main reservation:** Could be viewed as a powerful disease-specific invention rather than a broad physiological discovery.

**Attribution judgment:** The 2026 Lasker supports this three-person pool; the citation should focus on factor-mimetic bispecific engineering rather than all antibody therapeutics.

### Adult stem-cell-derived organoids for studying tissue biology and disease

**Scientific basis:** Single intestinal stem cells can generate self-organizing organoids, enabling long-term culture of tissue-like structures. Sources: [Sato and colleagues original adult stem-cell organoid paper](https://www.hubrecht.eu/app/uploads/2017/11/nature07935.pdf).

**Why include it:** Changed experimental access to normal and diseased human tissues through a concrete biological discovery and culture method.

**Main reservation:** Clinical impact and physiological completeness vary; adult stem-cell organoids should be distinguished from pluripotent stem-cell organoids.

**Attribution judgment:** This narrow scope supports Clevers and Sato; a broader organoid citation would require additional pioneers and separate attribution research.

### BCR-ABL inhibition and molecularly targeted treatment of chronic myeloid leukemia

**Scientific basis:** Imatinib targets the BCR-ABL kinase driving CML; investigation of resistance enabled subsequent targeted inhibitors. Sources: [Lasker account of targeted CML treatment](https://laskerfoundation.org/winners/molecularly-targeted-treatments-for-chronic-myeloid-leukemia/).

**Why include it:** A durable demonstration that targeting an oncogenic driver can transform cancer treatment.

**Main reservation:** Broader precision-oncology claims overlap with HER2 therapy and depend on many earlier discoveries.

**Attribution judgment:** Keep this kinase-inhibitor achievement separate from trastuzumab; any combined award must still fit the total three-person limit.

### Biomolecular condensates and phase separation in cellular organization

**Scientific basis:** Phase separation and interactions of low-complexity protein domains explain important forms of cellular organization without membrane boundaries. Sources: [Lasker account of low-complexity domains and cell organization](https://laskerfoundation.org/winners/structures-and-functions-of-low-complexity-domains/), [Breakthrough 2023 accounts of condensates and orexin](https://breakthroughprize.org/News/73).

**Why include it:** Introduced a physical mechanism for organizing cellular reactions, with experimental work from complementary approaches.

**Main reservation:** Some proposed functions remain contested or context-dependent; liquid behavior, hydrogels and aggregation should not be equated.

**Attribution judgment:** Hyman-Brangwynne and Gorlich-McKnight support different emphases; select a precise achievement and at most three researchers during deliberation.

### CFTR functional rescue and modulator therapies for cystic fibrosis

**Scientific basis:** Understanding CFTR dysfunction enabled drugs that improve mutant protein folding, trafficking and channel activity. Sources: [Lasker account of CFTR modulator therapy](https://laskerfoundation.org/winners/combined-triple-drug-therapy-for-cystic-fibrosis/), [Gairdner 2025 accounts of CFTR therapy and Notch signaling](https://www.gairdner.org/resource-hub/2025-canada-gairdner-award-winners).

**Why include it:** A mature example of treating a genetic disease by rescuing the defective protein mechanism.

**Main reservation:** The mechanistic, screening and medicinal-chemistry contributions are distributed among more than three scientists.

**Attribution judgment:** The 2025 Lasker names Welsh, Negulescu and Gonzalez; its scientific account also credits Van Goor and Hadida, retained as alternatives.

### Chaperonin-assisted protein folding

**Scientific basis:** Chaperonins provide a protected environment in which proteins can fold, establishing active cellular assistance to protein folding. Sources: [Lasker account of chaperone-assisted protein folding](https://laskerfoundation.org/winners/chaperone-assisted-protein-folding/).

**Why include it:** Changed a basic account of how functional proteins arise in cells; attribution is comparatively compact.

**Main reservation:** Could compete with the unfolded protein response; the committee must distinguish assisted folding from structure prediction.

**Attribution judgment:** This is experimental chaperonin biology, distinct from AlphaFold and computational protein design recognized by Chemistry in 2024.

### DNA methylation as a mechanism regulating gene expression

**Scientific basis:** DNA methylation and its recognition influence gene activity; causal experiments connect methylation changes to disease mechanisms. Sources: [Gairdner account of Bird, Cedar and DNA methylation](https://www.gairdner.org/winner/adrian-peter-bird), [Whitehead account of causal DNA methylation research](https://wi.mit.edu/news/dna-methylation-shown-promote-development-colon-tumors).

**Why include it:** A fundamental account of stable gene regulation beyond DNA sequence, supported by mechanistic experiments.

**Main reservation:** Different discoveries under the broad epigenetics label should not be treated as a single undifferentiated achievement.

**Attribution judgment:** Bird and Cedar anchor methylation and expression; Jaenisch represents causal mammalian experiments. Imprinting remains a separate candidate.

### Genetically engineered CAR-T cells for treating cancer

**Scientific basis:** Engineering T-cell receptors and signaling enabled patient T cells to attack blood cancers, with durable remissions in some patients. Sources: [BBVA account of June and Sadelain CAR-T discoveries](https://www.bbva.com/en/frontiers-of-knowledge-award-goes-to-scientists-who-revolutionized-the-treatment-of-several-types-of-blood-cancer/), [Weizmann institutional memorial for Zelig Eshhar](https://www.weizmann.ac.il/dept/irb/prof-zelig-eshhar).

**Why include it:** A mature clinical transformation built on a distinct engineering advance, with an intelligible two-person configuration.

**Main reservation:** Durability, toxicities and limited solid-tumor success constrain generalization; earlier invention credit must be acknowledged.

**Attribution judgment:** June and Sadelain are the proposed living attribution pool for this scope. Eshhar remains essential historical credit but died in 2025.

### GLP-1 physiology and the development of incretin therapies for diabetes and obesity

**Scientific basis:** Discovery of active GLP-1 and its insulin-stimulating physiology enabled development of durable therapeutic analogues. Sources: [Lasker scientific account of GLP-1 discoveries and therapies](https://laskerfoundation.org/winners/glp-1-based-therapy-for-obesity/).

**Why include it:** Combines a defined physiological discovery with major demonstrated clinical benefit; the scientific and therapeutic narratives both support consideration.

**Main reservation:** Four substantial living attribution claims compete for at most three laureate places; citation scope could determine the outcome.

**Attribution judgment:** Retain Drucker, Holst, Mojsov and Knudsen. Discovery-focused and drug-development-focused configurations differ. Habener is indispensable historical credit but died on 28 December 2025 and is removed from the eligible pool. [Johns Hopkins memorial](https://www.hopkinsmedicine.org/news/articles/2026/04/a-titan-in-endocrinology), [Endocrine Society memorial](https://endocrinenews.endocrine.org/remembering-joel-habener-md/).

### HER2-directed antibody therapy for breast cancer

**Scientific basis:** HER2 biology, antibody engineering and clinical development produced trastuzumab for HER2-positive breast cancer. Sources: [Lasker account of trastuzumab development](https://laskerfoundation.org/winners/herceptin-a-targeted-antibody-therapy-for-breast-cancer/).

**Why include it:** A mature, specific route from molecular disease classification to survival-improving treatment.

**Main reservation:** A combined targeted-cancer-therapy citation would create severe competition for laureate places.

**Attribution judgment:** Keep the HER2 antibody development pool intact and separate from the BCR-ABL kinase-inhibitor pool.

### Identification of CFTR as the gene responsible for cystic fibrosis

**Scientific basis:** Positional cloning and characterization identified CFTR and connected its disruption to cystic fibrosis. Sources: [University of Michigan account of CFTR gene discovery](https://www.uofmhealth.org/news-release/gene-discovery-changed-cystic-fibrosis-care-and-genetic-research-forever), [Riordan and colleagues original CFTR cloning paper](https://doi.org/10.1126/science.2475911).

**Why include it:** A landmark demonstration of finding a disease gene from inheritance and chromosome position.

**Main reservation:** The original gene discovery and later functional rescue therapies offer competing citation scopes.

**Attribution judgment:** Keep gene discovery separate from the Welsh-Negulescu-Gonzalez therapeutic candidate; do not conflate source credit with drug-development credit.

### IL-6 signaling and therapeutic blockade of the IL-6 receptor

**Scientific basis:** Discovery and characterization of IL-6 and its signaling system enabled receptor-blocking treatment such as tocilizumab. Sources: [Japan Prize account of Kishimoto and Hirano IL-6 discoveries](https://www.japanprize.jp/en/prize_past_2011_prize02.html).

**Why include it:** A coherent molecular-to-clinical story with complementary mechanistic contributions and established treatment relevance.

**Main reservation:** A broad cytokine-therapy award risks conflating this discovery with anti-TNF or IL-1 biology.

**Attribution judgment:** The 2011 Japan Prize supports this two-person pool; retain a distinct IL-6 citation.

### Integrins as receptors mediating cell-matrix and cell-cell adhesion

**Scientific basis:** Separate discoveries of extracellular matrix and leukocyte adhesion receptors converged on the integrin family. Sources: [Lasker account of integrin discoveries](https://laskerfoundation.org/winners/integrins-mediators-of-cell-matrix-cell-adhesion/).

**Why include it:** A general organizing principle of tissues and immunity with mature evidence and a coherent three-person configuration.

**Main reservation:** The field is broad; an award needs a sharply defined receptor discovery rather than a general adhesion citation.

**Attribution judgment:** Retain both extracellular matrix and immune adhesion origins when evaluating the common molecular family.

### Kinetic stabilization of transthyretin and treatment of amyloid disease

**Scientific basis:** Stabilizing the transthyretin tetramer with tafamidis reduces its dissociation and aggregation and slows disease progression. Sources: [Gairdner 2026 account of Kelly and tafamidis](https://www.gairdner.org/resource-hub/2026-canada-gairdner-award-winners), [Breakthrough 2022 accounts of sequencing and tafamidis](https://breakthroughprize.org/News/65).

**Why include it:** A precise, experimentally grounded connection between protein mechanism and effective disease-modifying therapy.

**Main reservation:** A narrow disease-focused achievement may compete with broader proteostasis principles; drug-development attribution needs scrutiny.

**Attribution judgment:** Kelly anchors the mechanism-and-therapy discovery; avoid claiming that tafamidis demonstrates a universal treatment for all amyloid diseases.

### Leptin and endocrine regulation of appetite and body weight

**Scientific basis:** Identification of leptin established an endocrine signal linking adipose tissue to feeding behavior and body-weight regulation. Sources: [Lasker account of leptin discovery](https://laskerfoundation.org/winners/leptin-a-hormone-that-regulates-appetite-and-body-weight/), [Jackson Laboratory institutional memorial for Douglas Coleman](https://www.jax.org/news-and-insights/2014/april/douglas-l-coleman-phd-jackson-laboratory-professor-emeritus-1931-2014).

**Why include it:** A fundamental physiological discovery that changed the biological understanding of obesity.

**Main reservation:** The clinical replacement-therapy story is narrower than that for incretin drugs; this is a distinct mechanism, not a GLP-1 variant.

**Attribution judgment:** Friedman is the living pool for this discovery-centered entry; Coleman is indispensable historical credit but died in 2014.

### Long-term potentiation and the synaptic basis of learning and memory

**Scientific basis:** Experiments linked persistent strengthening of hippocampal synapses and its molecular mechanisms to spatial learning and memory. Sources: [Bristol account of the 2016 Brain Prize for LTP and memory](https://www.bristol.ac.uk/news/2016/march/collingridge-brain-prize.html).

**Why include it:** Combines fundamental physiology with causal investigation of a central brain function.

**Main reservation:** A new citation must make clear its distinction from earlier Nobel-recognized work on memory and from place-cell discoveries.

**Attribution judgment:** Use the established 2016 Brain Prize pool while recognizing that LTP and memory are not interchangeable in every experimental context.

### Mammalian genomic imprinting and parent-of-origin gene expression

**Scientific basis:** Independent embryo experiments established functional nonequivalence of maternal and paternal genomes and the basis of genomic imprinting. Sources: [Max Planck account of Solter and Surani genomic imprinting discoveries](https://www.ie-freiburg.mpg.de/solter-gairdner2018).

**Why include it:** An unexpected, fundamental discovery with direct consequences for development and human genetic disorders.

**Main reservation:** Its relation to DNA methylation can invite overbroad merging; the original developmental discovery should remain identifiable.

**Attribution judgment:** Keep the independent Surani and Solter discoveries together, while distinguishing later molecular imprint maintenance mechanisms.

### Massively parallel DNA sequencing for genome-scale biology and medicine

**Scientific basis:** Scalable massively parallel sequencing made DNA sequence analysis broadly usable in biomedical research and medicine. Sources: [Breakthrough 2022 accounts of sequencing and tafamidis](https://breakthroughprize.org/News/65).

**Why include it:** An enabling invention with exceptional effects on genetics, diagnostics and experimental biology.

**Main reservation:** The invention is also a plausible Chemistry achievement; alternative sequencing platforms have separate priority histories.

**Attribution judgment:** This is the specific pool recognized by the 2022 Breakthrough Prize. Do not conflate it with every next-generation or long-read sequencing platform.

### Notch signaling as a mechanism of cell-fate specification

**Scientific basis:** Genetic and molecular discoveries established how Notch signaling controls cell fate, development and tissue patterning. Sources: [Gairdner 2025 accounts of CFTR therapy and Notch signaling](https://www.gairdner.org/resource-hub/2025-canada-gairdner-award-winners).

**Why include it:** A conserved biological mechanism with foundational experimental support and continuing relevance to tissue biology.

**Main reservation:** Cell-fate specification has many historical contributors, and the precise discovery boundary matters.

**Attribution judgment:** These are the three researchers jointly recognized by Gairdner in 2025; this pool is a defensible starting point rather than exhaustive historical credit.

### Optical coherence tomography for noninvasive tissue imaging

**Scientific basis:** Optical coherence tomography produces depth-resolved cross-sectional images of tissue and transformed retinal examination. Sources: [Lasker account of optical coherence tomography](https://laskerfoundation.org/winners/optical-coherence-tomography/).

**Why include it:** A mature invention with extensive direct medical use and a compact attribution configuration.

**Main reservation:** Its optics foundation could also support consideration in Physics; Medicine requires a convincing clinical-invention framing.

**Attribution judgment:** Use the imaging-invention trio; keep OCT distinct from the separate VEGF discovery even though both transformed retinal care.

### Optogenetic control of genetically specified cells with light

**Scientific basis:** Light-sensitive microbial proteins and genetic targeting permit experimental activation or inhibition of specified neuronal populations. Sources: [Lasker account of microbial opsins and optogenetics](https://laskerfoundation.org/winners/light-sensitive-microbial-proteins-optogenetics/), [Official 2013 Brain Prize announcement naming six optogenetics pioneers](https://www.openphilanthropy.org/files/Grants/MIT_Media_Lab_Synthetic_Neurobiology_Group/The_Brain_Prize_Press_Release_on_Award_2013.pdf), [Max Planck institutional memorial for Dieter Oesterhelt](https://www.biochem.mpg.de/dieter-oesterhelt-verstorben).

**Why include it:** Enabled causal experiments on neural circuits at a scale and specificity that changed neuroscience.

**Main reservation:** Several independent enabling contributions make a three-person award difficult; tool impact and biological discovery need to be distinguished.

**Attribution judgment:** Preserve the six living researchers named by the 2013 Brain Prize. Oesterhelt is historical credit only because he died in 2022.

### Orexin signaling in wakefulness and the cause of narcolepsy

**Scientific basis:** Orexin signaling maintains wakefulness, and loss of this system explains narcolepsy; the pathway also supplies drug targets. Sources: [Lasker 2026 scientific accounts of orexin and emicizumab](https://laskerfoundation.org/winners/2026-winners/), [Breakthrough 2023 accounts of condensates and orexin](https://breakthroughprize.org/News/73).

**Why include it:** Connects a basic physiological discovery to a defined human disorder and pharmacology, with clear complementary attribution.

**Main reservation:** Therapeutic maturity differs between receptor antagonism for insomnia and receptor agonism for narcolepsy.

**Attribution judgment:** Treat discovery of the pathway and explanation of disease as complementary work. The 2026 Lasker recognizes these contributions.

### PCSK9 and human genetic validation of a cholesterol-lowering therapeutic target

**Scientific basis:** PCSK9 disease mutations and protective loss-of-function variants established a target for reducing LDL cholesterol and cardiovascular risk. Sources: [Hobbs-Cohen laboratory account of protective PCSK9 variants](https://labs.utsouthwestern.edu/hobbs-cohen-lab/research), [IRCM account of Seidah and PCSK9 biology](https://www.ircm.qc.ca/en/researchers/nabil-g--seidah), [Abifadel and colleagues original PCSK9 disease mutation paper](https://doi.org/10.1038/ng1161).

**Why include it:** A strong example of human genetics directing therapeutic development, with clear physiological consequences.

**Main reservation:** Several discovery and validation teams compete for the three-person limit; distinction from earlier LDL-receptor recognition is necessary.

**Attribution judgment:** Retain protein discovery, disease genetics and protective-variant teams; a Hobbs-Cohen-only framing would prematurely exclude foundational work.

### Single-cell RNA sequencing for resolving cellular identity and heterogeneity

**Scientific basis:** Single-cell transcriptome profiling, sensitive full-length protocols and droplet methods enabled molecular analysis of heterogeneous cell populations. Sources: [Tang and colleagues original single-cell mRNA sequencing paper](https://doi.org/10.1038/nmeth.1315), [Original Smart-Seq paper](https://www.nature.com/articles/nbt.2282), [Original Smart-seq2 paper](https://www.nature.com/articles/nmeth.2639), [Original Drop-seq study and dataset](https://singlecell.broadinstitute.org/single_cell/study/SCP7/drop-seq), [Original single-cell multiplex RNA sequencing paper](https://genome.cshlp.org/content/early/2011/05/04/gr.110882.110.full.pdf).

**Why include it:** Opened a major experimental view of cell identity, with wide use across physiology, development and disease.

**Main reservation:** The first demonstration, improved sensitivity, high throughput and atlas applications represent distinct credit claims; the three-person constraint is severe.

**Attribution judgment:** Preserve methodological alternatives. Inclusion of Sandberg and Linnarsson creates direct conflicts for the existing simulated committee; these require an explicit protocol choice.

### Spatial transcriptomics for mapping gene expression within intact tissue

**Scientific basis:** Spatially resolved sequencing and multiplexed RNA imaging associate molecular cell identity with tissue position. Sources: [Original spatial transcriptomics paper](https://pubmed.ncbi.nlm.nih.gov/27365449/), [Harvard 2026 account of Zhuang and MERFISH cell atlases](https://www.chemistry.harvard.edu/news/2026/05/profile-atlas-maker-microscopic-world).

**Why include it:** Restores anatomical context to molecular cell analysis and enables detailed investigation of tissue organization.

**Main reservation:** Distinct sequencing and imaging inventions have separate priorities, and application maturity varies.

**Attribution judgment:** Zhuang anchors MERFISH; Lundeberg, Frisen and Stahl anchor the spatial sequencing approach. Linnarsson coauthored the original spatial-transcriptomics paper.

### The BRCA1 locus and the genetic basis of inherited breast cancer

**Scientific basis:** Family-based genetic analysis established the BRCA1 locus and a major inherited component of breast cancer susceptibility. Sources: [Lasker account of King and the BRCA1 locus](https://laskerfoundation.org/winners/breast-cancer-genetics-and-human-rights/).

**Why include it:** An identifiable discovery changed disease risk assessment and preventive medicine.

**Main reservation:** Mapping the locus, cloning BRCA1, identifying BRCA2 and exploiting DNA-repair vulnerabilities are different achievements.

**Attribution judgment:** King is the pool for this deliberately narrow citation. A broader BRCA1/BRCA2 citation requires additional names and evidence at the merge stage.

### The cGAS-STING pathway linking cytosolic DNA sensing to innate immunity

**Scientific basis:** STING is an innate immune signaling adaptor; cGAS detects cytosolic DNA and produces the cyclic messenger cGAMP. Sources: [Lasker account of the discovery of cGAS](https://laskerfoundation.org/winners/cgas-enzyme-that-senses-self-and-foreign-dna/), [Ishikawa and Barber original STING paper](https://www.nature.com/articles/nature07317).

**Why include it:** A clearly defined mechanism with consequences for infection, inflammation and antitumor immunity.

**Main reservation:** The clinical translational story is less mature than the mechanistic discovery, and a broad citation complicates credit.

**Attribution judgment:** A cGAS-centered citation could emphasize Chen and the original biochemical discoverers; a pathway citation also brings STING discovery into scope.

### The unfolded protein response and signaling from the endoplasmic reticulum

**Scientific basis:** Identification of ER stress signaling machinery explained how cells sense misfolded proteins and increase their folding capacity. Sources: [Lasker account of the unfolded protein response](https://laskerfoundation.org/winners/unfolded-protein-response/).

**Why include it:** A fundamental, widely reproduced cellular mechanism with an unusually clear two-person attribution.

**Main reservation:** Direct therapeutic benefit is less prominent than its biological importance; related proteostasis discoveries are separate candidates.

**Attribution judgment:** Keep ER stress sensing and signaling separate from chaperonin-assisted folding and from therapeutic stabilization of transthyretin.

### TNF blockade as a treatment for rheumatoid arthritis and inflammatory disease

**Scientific basis:** Experimental work identified TNF as an actionable inflammatory driver and clinical studies established effective TNF blockade. Sources: [Lasker account of anti-TNF therapy](https://laskerfoundation.org/winners/anti-tnf-for-treating-rheumatoid-arthritis/).

**Why include it:** A compelling mechanism-to-treatment story with established benefit and clear complementary laboratory and clinical roles.

**Main reservation:** The previous Medicine prize addressed immune tolerance; thematic succession is a forecasting consideration, not an exclusion rule.

**Attribution judgment:** Retain this cytokine-blockade discovery independently of IL-6 and the already rewarded regulatory T-cell story.

### TOR signaling as a regulator of cell growth and nutrient responses

**Scientific basis:** TOR proteins couple nutrient availability to cell growth; mammalian TOR signaling extends this mechanism to physiological regulation. Sources: [Lasker account of nutrient-sensitive TOR signaling](https://laskerfoundation.org/winners/nutrient-activated-tor-proteins-that-regulate-cell-growth/).

**Why include it:** A central conserved mechanism with effects across metabolism, growth and disease.

**Main reservation:** Discovery of yeast TOR, mammalian mTOR and later pathway mechanisms support different attribution boundaries.

**Attribution judgment:** Hall, Sabatini and Schreiber are an attribution pool, not an endorsed mandatory trio; distinguish original target discovery from later mechanistic work.

### VEGF biology and inhibition of pathological angiogenesis

**Scientific basis:** VEGF and vascular permeability factor proved to be the same signaling molecule; blocking VEGF enabled anti-angiogenic treatment. Sources: [Lasker account of VEGF and anti-VEGF therapy](https://laskerfoundation.org/winners/anti-vegf-therapy-for-wet-macular-degeneration/), [Senger and colleagues original vascular permeability factor paper](https://pubmed.ncbi.nlm.nih.gov/6823562/).

**Why include it:** Connects a defined biological pathway to mature clinical benefit, particularly in retinal disease.

**Main reservation:** Discovery of permeability activity, molecular identification and therapeutic development support different credit allocations.

**Attribution judgment:** Ferrara is central to a therapeutic citation; Dvorak and Senger become important for a broader discovery-of-VEGF/VPF citation.

### Virus-like particle vaccines that prevent HPV infection and related cancers

**Scientific basis:** Noninfectious papillomavirus-like particles can induce protective immunity and form the basis of vaccines preventing HPV infection. Sources: [Lasker account of HPV virus-like particle vaccines](https://laskerfoundation.org/winners/hpv-vaccines-for-cancer-prevention/).

**Why include it:** Links a precise technological advance to cancer prevention and substantial public-health benefit.

**Main reservation:** Particle design, immunogenicity and vaccine development have overlapping priority histories.

**Attribution judgment:** Retain Lowy, Schiller and Frazer for committee attribution review; the Lasker account describes both the NCI work and Frazer contribution.

## Comparison with Claude and interpretation

Compare the two drafts by achievement before comparing laureate configurations. Build their union, consolidate genuine duplicates and preserve differences in scientific scope. For example, the same GLP-1 discovery with different preferred trios is one achievement with attribution alternatives; CFTR gene discovery and CFTR modulator therapy are different achievements. Resolve disputed names against original work, and record additions or removals with their reasons. Agreement between the authors is not a selection threshold.

Freeze the merged list before committee deliberations. Run both committee-model arms on that same list, with independently shuffled candidate order and the same evidence boundaries. This controls input differences when comparing committee behavior, but all resulting outcome shares are conditional on a curated candidate list. They do not measure uncertainty from the skipped nomination process, and simulation agreement alone does not establish calibrated real-world probabilities.

## Eligibility and historical sources

- [Nobel Foundation statutes](https://www.nobelprize.org/about/statutes-of-the-nobel-foundation/) define the prize-sharing and deceased-person constraints.
- [Official 2025 Medicine scientific background](https://www.nobelprize.org/uploads/2025/10/advanced-medicineprize2025.pdf) establishes the already recognized peripheral immune-tolerance discovery.
- [Weizmann memorial](https://www.weizmann.ac.il/dept/irb/prof-zelig-eshhar) records Eshhar's death on 3 July 2025.
- [Jackson Laboratory memorial](https://www.jax.org/news-and-insights/2014/april/douglas-l-coleman-phd-jackson-laboratory-professor-emeritus-1931-2014) records Coleman's death on 16 April 2014.
- [Max Planck memorial](https://www.biochem.mpg.de/dieter-oesterhelt-verstorben) records Oesterhelt's death on 28 November 2022.

- [Johns Hopkins memorial](https://www.hopkinsmedicine.org/news/articles/2026/04/a-titan-in-endocrinology) and [Endocrine Society memorial](https://endocrinenews.endocrine.org/remembering-joel-habener-md/) confirm Habener's death on 28 December 2025.
