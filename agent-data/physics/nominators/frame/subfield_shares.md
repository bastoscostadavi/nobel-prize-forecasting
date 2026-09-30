# Physics research by subfield and region, 2016-2025 (OpenAlex)

Queried on 2026-09-30 from https://api.openalex.org (no API key; `mailto` parameter set). The scripts are in `frame/scripts/`. All counts are **works** (papers), not people.

## Filters
- **Common filter for every query:** `publication_year:2016-2025,type:article|review,is_retracted:false`. Preprints, datasets, errata and paratext are left out, so an arXiv preprint merged into its journal record is counted once.
- **"Strict" physics:** `primary_topic.field.id:31`, where field 31 is OpenAlex's "Physics and Astronomy". This field has 8 subfields and 104 topics. Each work has exactly one primary topic, so the categories do not overlap.
- **"Extended" physics** adds 18 topics that OpenAlex files outside field 31 but that are physics by content: quantum information and computing (filed under Computer Science); graphene, 2D materials, iron-based superconductors, multiferroics and similar (Materials Science); metamaterials, plasmonics, photonic devices, lasers and THz (Engineering and Materials); and accelerators and FELs. The filter is `primary_topic.id:<those ids>`. **The extended set is the headline definition**, because under the strict definition quantum information is 0% and condensed matter is badly under-counted: OpenAlex files most solid-state work under Materials Science.
- **Highly cited:** the same filters plus `cited_by_count:>200`.
- **Project categories:** each topic was mapped by hand to one of 8 categories (see the appendix). OpenAlex's own subfield labels are also reported (Table 1).
- **Countries:** `group_by=authorships.institutions.country_code` counts a work once for each country that has at least one author on it (full counting). **Regions** (Tables 5-6) sum these country counts and normalize to 100%, so they are shares of author-country mentions. **Continents** come from `group_by=authorships.institutions.continent`.

## Headline (extended set, all works 2016-2025, N = 1,636,742)
Condensed matter 22.7%, astro/cosmology 22.9%, particle/nuclear 12.0%, optics/photonics 12.2%, "other" 13.2%, statistical/complex 7.1%, AMO 6.6%, quantum information 3.3%.

Among works cited more than 200 times, condensed matter (30%), quantum information (6%) and optics/photonics (14%) gain share. Particle/nuclear (7%) and "other" (7%) lose share.

By country, China (19.7% of works) and the USA (19.1%) are level on raw output. Among highly cited works the USA is far ahead: it has an author on 52% of them, against 26% for China.

### Table 1. OpenAlex native subfields, strict field 31 only

| OpenAlex subfield | works 2016-25 | share | works cited>200 | share |
|---|---:|---:|---:|---:|
| Astronomy and Astrophysics | 374,301 | 28.5% | 2,565 | 32.5% |
| Atomic and Molecular Physics, and Optics | 370,506 | 28.2% | 2,693 | 34.1% |
| Nuclear and High Energy Physics | 206,309 | 15.7% | 1,103 | 14.0% |
| Statistical and Nonlinear Physics | 149,290 | 11.4% | 682 | 8.6% |
| Condensed Matter Physics | 107,700 | 8.2% | 549 | 7.0% |
| Radiation | 78,228 | 6.0% | 165 | 2.1% |
| Instrumentation | 19,566 | 1.5% | 84 | 1.1% |
| Acoustics and Ultrasonics | 6,459 | 0.5% | 49 | 0.6% |
| **Total** | **1,312,359** | | **7,890** | |

### Table 2. Project categories (topic-level mapping)

| Category | strict: all | strict: cited>200 | **extended: all** | extended: cited>200 |
|---|---:|---:|---:|---:|
| condensed matter | 16.7% | 19.9% | **22.7%** | 30.2% |
| particle/nuclear | 14.3% | 10.5% | **12.0%** | 7.3% |
| astro/cosmology | 28.6% | 35.8% | **22.9%** | 24.5% |
| AMO/quantum optics | 8.2% | 9.1% | **6.6%** | 6.2% |
| quantum information | 0.0% | 0.0% | **3.3%** | 5.9% |
| optics/photonics | 7.0% | 6.8% | **12.2%** | 13.6% |
| statistical/complex systems | 8.8% | 8.2% | **7.1%** | 5.6% |
| other | 16.5% | 9.7% | **13.2%** | 6.6% |
| N works | 1,312,359 | 7,890 | 1,636,742 | 11,507 |

### Table 3. Countries: share of works with at least one author in the country (extended set; full counting, so columns sum to more than 100%)

| Country | all works | cited>200 |
|---|---:|---:|
| CN | 19.7% | 25.9% |
| US | 19.1% | 52.3% |
| DE | 9.1% | 23.3% |
| GB | 6.8% | 20.0% |
| JP | 6.4% | 11.4% |
| RU | 5.8% | 5.6% |
| FR | 5.7% | 14.1% |
| IN | 5.1% | 4.0% |
| IT | 5.0% | 11.2% |
| ES | 3.7% | 10.6% |
| CH | 2.7% | 10.7% |
| CA | 2.7% | 9.1% |
| KR | 2.6% | 5.1% |
| AU | 2.2% | 8.4% |
| NL | 2.1% | 8.5% |
| BR | 2.0% | 3.3% |
| PL | 2.0% | 3.9% |
| IR | 1.6% | 0.8% |
| SE | 1.6% | 4.4% |
| TW | 1.3% | 3.3% |
| (no country known) | 0.0% | 0.0% |

### Table 4. Continents: share of works with at least one author on the continent (extended set)

| Continent | all works | cited>200 |
|---|---:|---:|
| Europe | 34.1% | 53.3% |
| Asia | 39.3% | 44.1% |
| North America | 21.4% | 55.0% |
| South America | 3.8% | 6.4% |
| Oceania | 2.5% | 8.9% |
| Africa | 2.5% | 3.4% |

### Table 5. Regions: share of author-country mentions (normalized to 100%; basis for pool stratification)

| Region | all works | cited>200 |
|---|---:|---:|
| USA | 14.1% | 17.5% |
| Canada | 2.0% | 3.0% |
| Europe (non-Nordic) | 34.6% | 42.4% |
| Nordic | 2.9% | 4.2% |
| China | 14.5% | 8.6% |
| Japan | 4.7% | 3.8% |
| Other East Asia (KR,TW,SG,HK) | 4.0% | 5.2% |
| India | 3.8% | 1.3% |
| Russia | 4.3% | 1.9% |
| Middle East/Turkey/Iran/Pakistan | 5.4% | 2.7% |
| Latin America | 4.2% | 3.8% |
| Oceania | 1.8% | 3.1% |
| Rest of world | 3.8% | 2.5% |

### Table 6. Region mix within each category (all works 2016-2025, normalized author-country mentions)

| Category | USA | Canada | Europe (non-Nordic) | Nordic | China | Japan | Other East Asia (KR,TW,SG,HK) | India | Russia | Middle East/Turkey/Iran/Pakistan | Latin America | Oceania | Rest of world |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| condensed matter | 13 | 1 | 28 | 2 | 19 | 7 | 6 | 5 | 5 | 5 | 3 | 1 | 4 |
| particle/nuclear | 11 | 2 | 43 | 3 | 8 | 4 | 3 | 4 | 4 | 6 | 6 | 1 | 5 |
| astro/cosmology | 18 | 3 | 42 | 4 | 6 | 4 | 3 | 3 | 3 | 3 | 6 | 3 | 3 |
| AMO/quantum optics | 14 | 2 | 35 | 3 | 17 | 4 | 3 | 3 | 5 | 5 | 3 | 2 | 3 |
| quantum information | 14 | 3 | 30 | 2 | 21 | 4 | 5 | 4 | 2 | 6 | 3 | 2 | 2 |
| optics/photonics | 10 | 2 | 21 | 2 | 32 | 4 | 6 | 3 | 5 | 7 | 2 | 2 | 4 |
| statistical/complex systems | 12 | 1 | 25 | 2 | 22 | 3 | 3 | 4 | 4 | 13 | 4 | 2 | 5 |
| other | 18 | 2 | 34 | 3 | 13 | 5 | 3 | 4 | 5 | 5 | 3 | 2 | 3 |

Same, restricted to works cited>200:

| Category | USA | Canada | Europe (non-Nordic) | Nordic | China | Japan | Other East Asia (KR,TW,SG,HK) | India | Russia | Middle East/Turkey/Iran/Pakistan | Latin America | Oceania | Rest of world |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| condensed matter | 23 | 1 | 30 | 2 | 18 | 7 | 10 | 1 | 1 | 3 | 1 | 2 | 1 |
| particle/nuclear | 9 | 3 | 48 | 5 | 4 | 3 | 4 | 1 | 3 | 5 | 7 | 2 | 7 |
| astro/cosmology | 14 | 4 | 50 | 6 | 3 | 3 | 3 | 2 | 2 | 2 | 5 | 4 | 3 |
| AMO/quantum optics | 23 | 3 | 45 | 4 | 8 | 5 | 4 | 1 | 2 | 3 | 1 | 2 | 0 |
| quantum information | 26 | 7 | 41 | 2 | 10 | 4 | 2 | 0 | 1 | 1 | 0 | 4 | 1 |
| optics/photonics | 21 | 3 | 26 | 2 | 21 | 2 | 10 | 1 | 3 | 3 | 1 | 6 | 1 |
| statistical/complex systems | 29 | 2 | 35 | 2 | 14 | 2 | 3 | 2 | 1 | 4 | 2 | 2 | 2 |
| other | 23 | 2 | 49 | 5 | 8 | 2 | 4 | 1 | 1 | 2 | 1 | 2 | 1 |

## Caveats
- **Topic classification is noisy.** OpenAlex assigns topics automatically. Some field-31 topics are mislabelled, for example "Superconducting and THz Device Technology" under Astronomy and "Magnetic properties of thin films" under AMO. The hand mapping corrects for this at topic level, but misclassified individual works remain.
- **"Other"** covers climate and atmosphere-adjacent topics, radiation and medical physics, plasma and fusion, NMR, and some generic or junk topics (e.g. "Scientific Research and Discoveries", "Advanced Mathematical Theories and Applications"). It is kept so that the shares add up, but for sampling nominators it is the least meaningful category.
- **The extended set is a judgement call**, with 18 topics added. Other physics-adjacent topics were left out on purpose because they are dominated by engineering or chemistry: fluid dynamics and turbulence, general semiconductor devices, perovskite solar cells, plasma diagnostics (822k works, very noisy), and "Particle accelerators and beam dynamics" (1.26M works, evidently mis-clustered).
- **Full counting inflates regions with large collaborations.** A LHC or LIGO paper counts once for each of dozens of countries, which boosts Europe in particle/astro and among highly cited works. Fractional counting is not available through the group_by API.
- **Output is not the same as the nominator population.** Chinese, Indian, Iranian and Russian output shares are much higher than their shares of highly cited work, and probably higher than their shares of the Academy's invitation lists (unknown).
- The group_by for highly cited works uses current citation counts, so papers from 2023-2025 are under-represented.

## Appendix: topic to category mapping
- **condensed matter**: field-31 topics: T10022 Semiconductor Quantum Structures and Devices; T10037 Physics of Superconductivity and Magnetism; T10049 Magnetic properties of thin films; T10099 GaN-based semiconductor devices and materials; T10382 Quantum and electron transport phenomena; T10591 Theoretical and Computational Physics; T10657 Topological Materials and Phenomena; T10681 Rare-earth and actinide compounds; T10923 Force Microscopy Techniques and Applications; T11682 Advanced Condensed Matter Physics; T11803 Superconducting and THz Device Technology; T11804 Quantum many-body systems; T11853 Semiconductor materials and interfaces; T11965 Quantum, superfluid, helium dynamics; T12491 Superconductivity in MgB2 and Alloys; T12762 Crystallography and Radiation Phenomena; T13531 Surface and Thin Film Phenomena. **Extended additions:** T10083 Graphene research and applications; T10275 2D Materials and Applications; T11766 Iron-based superconductors research; T10607 Magnetic and transport properties of perovskites and related materials; T10886 Multiferroics and related materials; T12200 Heusler alloys; T11758 Organic and Molecular Conductors Research; T11808 Superconducting Materials and Applications
- **particle/nuclear**: field-31 topics: T10025 Black Holes and Theoretical Physics; T10048 Particle physics theoretical and experimental studies; T10093 Nuclear physics research studies; T10224 Quantum Chromodynamics and Particle Interactions; T10527 High-Energy Particle Collisions Research; T10921 Neutrino Physics Research; T11044 Particle Detector Development and Performance; T11216 Radiation Detection and Scintillator Technologies; T11415 Noncommutative and Quantum Gravity Theories; T11683 Quantum and Classical Electrodynamics; T11949 Nuclear Physics and Applications; T12220 Quantum Electrodynamics and Casimir Effect; T13414 Radioactive Decay and Measurement Techniques; T13458 Astronomical and nuclear sciences. **Extended additions:** T10559 Particle Accelerators and Free-Electron Lasers
- **astro/cosmology**: field-31 topics: T10026 Galaxies: Formation, Evolution, Phenomena; T10039 Stellar, planetary, and galactic studies; T10095 Cosmology and Gravitation Theories; T10159 Ionosphere and magnetosphere dynamics; T10251 Solar and Space Plasma Dynamics; T10325 Astro and Planetary Science; T10406 Planetary Science and Exploration; T10463 Pulsars and Gravitational Waves Research; T10477 Astrophysics and Star Formation Studies; T10744 Astrophysical Phenomena and Observations; T10818 Astrophysics and Cosmic Phenomena; T11090 Dark Matter and Cosmic Phenomena; T11323 Gamma-ray bursts and supernovae; T11960 Relativity and Gravitational Theory; T12450 Radio Astronomy Observations and Technology; T12788 Space Science and Extraterrestrial Life; T12836 History and Developments in Astronomy; T12917 Astronomy and Astrophysical Research; T13175 Historical Astronomy and Related Studies
- **AMO/quantum optics**: field-31 topics: T10425 Cold Atom Physics and Bose-Einstein Condensates; T10523 Atomic and Molecular Physics; T10566 Laser-Matter Interactions and Applications; T10622 Quantum Mechanics and Applications; T11262 Quantum Mechanics and Non-Hermitian Physics; T11414 Quantum optics and atomic interactions; T11449 Mechanical and Optical Resonators; T11993 Atomic and Subatomic Physics Research; T12004 Advanced Frequency and Time Standards; T12612 Strong Light-Matter Interactions
- **quantum information**: field-31 topics: (none). **Extended additions:** T10020 Quantum Information and Cryptography; T10682 Quantum Computing Algorithms and Architecture
- **optics/photonics**: field-31 topics: T10490 Orbital Angular Momentum in Optics; T10666 Photonic Crystals and Applications; T10739 Electromagnetic Scattering and Analysis; T10988 Advanced Fiber Laser Technologies; T11050 Photorefractive and Nonlinear Optics; T11484 Adaptive optics and wavefront sensing; T11575 Nonlinear Photonic Systems; T11897 Digital Holography and Microscopy; T11996 Random lasers and scattering media; T12153 Advanced Optical Sensing Technologies; T13493 Optical and Acousto-Optic Technologies; T14363 Optical properties and cooling technologies in crystalline materials. **Extended additions:** T10245 Metamaterials and Metasurfaces Applications; T10295 Plasmonic and Surface Plasmon Research; T10299 Photonic and Optical Devices; T11429 Semiconductor Lasers and Optical Devices; T11127 Solid State Laser Technologies; T10752 Terahertz technology and applications; T12466 Near-Field Optical Microscopy
- **statistical/complex systems**: field-31 topics: T10064 Complex Network Analysis Techniques; T10244 Chaos control and synchronization; T10248 Nonlinear Waves and Solitons; T11206 Model Reduction and Neural Networks; T11261 Quantum chaos and dynamical systems; T11513 stochastic dynamics and bifurcation; T11520 Advanced Thermodynamics and Statistical Mechanics; T12261 Statistical Mechanics and Entropy; T12592 Opinion Dynamics and Social Influence; T14299 Complex Systems and Dynamics
- **other**: field-31 topics: T10002 Advanced Chemical Physics Studies; T10346 Magnetic confinement fusion research; T10358 Advanced Radiotherapy Techniques; T10384 Laser-Plasma Interactions and Diagnostics; T10787 Lightning and Electromagnetic Phenomena; T11175 Gyrotron and Vacuum Electronics Research; T11177 Spectroscopy and Quantum Chemical Studies; T11183 Advanced X-ray Imaging Techniques; T11445 Origins and Evolution of Life; T11486 Micro and Nano Robotics; T11603 Dust and Plasma Wave Phenomena; T11666 Color Science and Applications; T11733 X-ray Spectroscopy and Fluorescence Analysis; T12077 Vacuum and Plasma Arcs; T12250 Experimental and Theoretical Physics Studies; T12516 Advanced Mathematical Theories and Applications; T12603 NMR spectroscopy and applications; T12717 Space exploration and regulation; T13080 Advanced Differential Geometry Research; T13126 Scientific Research and Discoveries; T13769 Fusion and Plasma Physics Studies; T14311 Electrical and Electromagnetic Research