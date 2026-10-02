# Consolidated 2026 Medicine candidate longlist

This is the common list for Nobel-agent review: **53 discovery entries**, combining the Codex draft (32) and Claude’s draft (40). There are 19 shared discoveries, 13 unique to Codex and 21 unique to Claude. All 72 input entries are accounted for exactly once; both drafts’ credited names, including Claude’s `other_names`, survive after name normalization. The attribution review adds documented contributors where a broad discovery description otherwise omitted a major role.

Research cutoff: **2 October 2026**, America/Chicago. Version: **merged v1**. The nominator stage was omitted at the user’s request. These are forecasting inputs, not known actual Nobel nominations. The list is alphabetical, without a preferred ranking or laureate trio.

## Files to use

- [committee_longlist.json](committee_longlist.json): the shuffled opening packet to give the Nobel agents. It contains only ballot IDs, discovery, subfield and alphabetical provisional credit pools.
- [AGENT_HANDOFF.md](AGENT_HANDOFF.md): instructions for interpreting and assessing the packet.
- [candidates.json](candidates.json): the canonical researched list with scientific scope, assessments, attribution notes, provenance and sources.
- [attribution_review.md](attribution_review.md): the review decisions and evidence for every discovery.
- [ballot_map.json](ballot_map.json): coordinator-only crosswalk from neutral B IDs to canonical M IDs.
- [coordinator_manifest.json](coordinator_manifest.json): input hashes, coverage checks, eligibility notes and committee-persona flags.
- [export_packet.py](export_packet.py): validates provenance and regenerates the packet, map and manifest from the canonical JSON.

For initial independent rankings, give each agent its Medicine committee profile, the handoff instructions, the packet and any relevant conflict declaration. Author identities, source-list membership and author assessments belong in the coordinator materials; introducing the researched dossier later should be done at the same stage for every agent.

The packet uses the opening-field layout already established in the repository. The existing Physics runners and nomination validators remain category-specific; this packet has not been wired into or validated as a complete Medicine simulation run.

## Attribution decisions

We preserved complementary roles: King’s BRCA1 mapping and Skolnick’s cloning consortium; the separate orexin and hypocretin discovery programs; Bliss/Lømo discovery, Collingridge mechanism and Morris memory work; CAR-T contributions from Rosenberg alongside June and Sadelain; and the experimental cGAS/STING and mammalian TOR contributors.

The review also restores Adams for BCL-2, Thein and Bauer for fetal-hemoglobin regulation/translation, Goate for APP mutations, Hedrick and Yanagi for T-cell receptor cloning, Montague for computational reward work, Iliff for glymphatic experiments and Varmus for joint Wnt1 identification. These are provisional scientific attribution choices, not selected laureates. Varmus’s prior Nobel and potential citation overlap are explicitly flagged.

Known deceased pioneers are retained as historical contributors outside the recipient pools. Habener’s exclusion carries forward the independently verified correction in Codex v2; Chambon’s 2026 death and DeLong’s 2024 death are also documented. Current institutional evidence replaces Claude’s unsupported “assumed living” fallback for Cohen and Sankaran. This is a targeted eligibility review; shortlisted recipients still need a current life-status check.

DNA methylation, MECP2/Rett and imprinting remain separate; so do CFTR gene identification and CFTR rescue therapies, and single-cell and spatial transcriptomics. Broad or disputed entries retain scope reservations in the dossier. The tau/alpha-synuclein entry contains separable protein discoveries and will need a precise citation if shortlisted. Glymphatic physiology remains available for assessment with both contrary mouse-clearance evidence and supportive 2026 human evidence recorded.

## Committee-persona issues

Single-cell RNA sequencing credits Rickard Sandberg and Sten Linnarsson, both existing committee personas. Linnarsson also coauthored the foundational spatial-transcriptomics paper. These flags require an explicit simulation recusal/declaration policy. Sandberg’s related-methods expertise in the spatial entry is informational, not a proven conflict. Scientific credit is retained independently of simulation convenience.

## Consolidated list

Each name pool may contain more than three people. Agents must choose a coherent achievement and **at most three recipients across the entire prize**, including any split award. Pools are starting points for attribution review, not exhaustive priority judgments.

| ID | Discovery | Provisional credit pool |
|---|---|---|
| M001 | A bispecific antibody that substitutes for factor VIII activity in hemophilia A | Kunihiro Hattori; Takehisa Kitazawa; Tomoyuki Igawa |
| M002 | Adult stem-cell-derived organoids for studying tissue biology and disease | Hans Clevers; Toshiro Sato |
| M003 | AMP-activated protein kinase as a sensor and regulator of cellular energy balance | D. Grahame Hardie |
| M004 | Antisense correction of SMN2 splicing to treat spinal muscular atrophy | Adrian R. Krainer; C. Frank Bennett |
| M005 | APP mutations and the amyloid-cascade model of Alzheimer’s disease | Alison M. Goate; John Hardy |
| M006 | BCL-2-mediated cell survival, apoptosis control, and the basis of targeted cancer therapy | Andreas Strasser; David L. Vaux; Jerry M. Adams; Suzanne Cory |
| M007 | BCL11A regulation of fetal hemoglobin and its therapeutic reactivation in hemoglobin disorders | Daniel E. Bauer; Stuart H. Orkin; Swee Lay Thein; Vijay G. Sankaran |
| M008 | BCR-ABL inhibition and molecularly targeted treatment of chronic myeloid leukemia | Brian J. Druker; Charles L. Sawyers; Nicholas B. Lydon |
| M009 | Biomolecular condensates and phase separation in cellular organization | Anthony A. Hyman; Clifford P. Brangwynne; Dirk Görlich; Steven L. McKnight |
| M010 | Causal roles of gut microbial communities in host metabolism and childhood growth | Jeffrey I. Gordon |
| M011 | CFTR functional rescue and modulator therapies for cystic fibrosis | Fred Van Goor; Jesús Tito González; Michael J. Welsh; Paul A. Negulescu; Sabine Hadida |
| M012 | Chaperonin-assisted protein folding | Arthur L. Horwich; F. Ulrich Hartl |
| M013 | Discovery, mapping, and cloning of BRCA1-linked inherited breast and ovarian cancer susceptibility | Mark H. Skolnick; Mary-Claire King |
| M014 | Distinct B- and T-lymphocyte lineages and their roles in adaptive immunity | Jacques F. A. P. Miller; Max D. Cooper |
| M015 | DNA methylation as a mechanism regulating gene expression | Adrian P. Bird; Howard Cedar; Rudolf Jaenisch |
| M016 | Fetal cell-free DNA in maternal blood and noninvasive prenatal screening | Y. M. Dennis Lo |
| M017 | Genetically engineered CAR-T cells for treating cancer | Carl H. June; Michel Sadelain; Steven A. Rosenberg |
| M018 | GLP-1 physiology and the development of incretin therapies for diabetes and obesity | Daniel J. Drucker; Jens Juul Holst; Lotte Bjerre Knudsen; Svetlana Mojsov |
| M019 | HER2-directed antibody therapy for breast cancer | Axel Ullrich; Dennis J. Slamon; H. Michael Shepard |
| M020 | High-frequency deep brain stimulation for Parkinson’s disease | Alim-Louis Benabid |
| M021 | Identification of CFTR as the gene responsible for cystic fibrosis | Francis S. Collins; John R. Riordan; Lap-Chee Tsui |
| M022 | IL-6 signaling and therapeutic blockade of the IL-6 receptor | Tadamitsu Kishimoto; Toshio Hirano |
| M023 | Integrins as receptors mediating cell-matrix and cell-cell adhesion | Erkki Ruoslahti; Richard O. Hynes; Timothy A. Springer |
| M024 | Kinetic stabilization of transthyretin and treatment of amyloid disease | Jeffery W. Kelly |
| M025 | Leptin and endocrine regulation of appetite and body weight | Jeffrey M. Friedman |
| M026 | Long-term potentiation and the synaptic basis of learning and memory | Graham L. Collingridge; Richard G. M. Morris; Terje Lømo; Timothy V. P. Bliss |
| M027 | Mammalian genomic imprinting and parent-of-origin gene expression | Davor Solter; M. Azim Surani |
| M028 | Massively parallel DNA sequencing for genome-scale biology and medicine | David Klenerman; Pascal Mayer; Shankar Balasubramanian |
| M029 | MECP2 biology, the molecular cause of Rett syndrome, and reversibility in mouse models | Adrian P. Bird; Huda Y. Zoghbi |
| M030 | Mitochondrial DNA inheritance and mutations as causes of human disease | Douglas C. Wallace |
| M031 | Modern multichannel cochlear implants and speech-processing strategies | Blake S. Wilson; Graeme M. Clark; Ingeborg Hochmair |
| M032 | Molecular identification and cloning of the T-cell antigen receptor | Mark M. Davis; Stephen M. Hedrick; Tak W. Mak; Yoshihiro Yanagi |
| M033 | Molecular mechanisms of bacterial quorum sensing and coordinated behavior | Bonnie L. Bassler; E. Peter Greenberg |
| M034 | Neural and computational mechanisms linking reward prediction errors to learning | P. Read Montague; Peter Dayan; Ray Dolan; Wolfram Schultz |
| M035 | Notch signaling as a mechanism of cell-fate specification | Gary Struhl; Iva Greenwald; Spyros Artavanis-Tsakonas |
| M036 | Optical coherence tomography for noninvasive tissue imaging | David Huang; Eric A. Swanson; James G. Fujimoto |
| M037 | Optogenetic control of genetically specified cells with light | Edward S. Boyden; Ernst Bamberg; Georg Nagel; Gero Miesenböck; Karl Deisseroth; Peter Hegemann |
| M038 | Orexin/hypocretin discovery and its role in wakefulness and narcolepsy | Emmanuel Mignot; Luis de Lecea; Masashi Yanagisawa; Takeshi Sakurai; Thomas S. Kilduff |
| M039 | PCSK9 and human genetic validation of a cholesterol-lowering therapeutic target | Catherine Boileau; Helen H. Hobbs; Jonathan C. Cohen; Marianne Abifadel; Nabil G. Seidah |
| M040 | Perivascular cerebrospinal-fluid exchange and the proposed glymphatic clearance mechanism | Jeffrey J. Iliff; Maiken Nedergaard |
| M041 | Sarcomere gene mutations as causes of inherited hypertrophic cardiomyopathy | Christine E. Seidman; Jonathan G. Seidman |
| M042 | Single-cell RNA sequencing for resolving cellular identity and heterogeneity | Aviv Regev; Evan Z. Macosko; Fuchou Tang; Rickard Sandberg; Sten Linnarsson; Stephen R. Quake; Steven A. McCarroll |
| M043 | Spatial transcriptomics for mapping gene expression within intact tissue | Joakim Lundeberg; Jonas Frisén; Patrik L. Ståhl; Xiaowei Zhuang |
| M044 | Tau and alpha-synuclein as molecular components of pathological neurodegenerative filaments | Maria Grazia Spillantini; Michel Goedert |
| M045 | TGF-beta receptor-to-SMAD signaling and its control of cell fate | Joan Massagué |
| M046 | The cGAS-STING pathway linking cytosolic DNA sensing to innate immunity | Glen N. Barber; Hiroki Ishikawa; Jiaxi Wu; Lijun Sun; Zhijian James Chen |
| M047 | The nuclear hormone receptor superfamily and ligand-dependent gene regulation | Ronald M. Evans |
| M048 | The unfolded protein response and signaling from the endoplasmic reticulum | Kazutoshi Mori; Peter Walter |
| M049 | TNF blockade as a treatment for rheumatoid arthritis and inflammatory disease | Marc Feldmann; Ravinder N. Maini |
| M050 | TOR signaling as a regulator of cell growth and nutrient responses | David M. Sabatini; Michael N. Hall; Stuart L. Schreiber |
| M051 | VEGF biology and inhibition of pathological angiogenesis | Donald R. Senger; Harold F. Dvorak; Napoleone Ferrara |
| M052 | Virus-like particle vaccines that prevent HPV infection and related cancers | Douglas R. Lowy; Ian H. Frazer; John T. Schiller |
| M053 | Wnt genes and signaling in cell fate, development, and tissue renewal | Harold E. Varmus; Roel Nusse |

## Rebuild and check

Run `python3 agent-data/medicine/candidates/merged/export_packet.py` from the repository. The script checks input hashes, one-to-one coverage, name retention, source references and packet/crosswalk consistency. The deterministic order uses SHA-256 of `medicine-consolidated-longlist-v1`, a null separator and compact public-payload JSON with sorted keys and unescaped Unicode. Sorting by digest, serialized payload and candidate ID gives consecutive B001–B053.

The source drafts remain in [Codex c](../c/README.md) and [Claude](../claude-opus-5-5/candidates.json). This merged directory is the common input going forward.
