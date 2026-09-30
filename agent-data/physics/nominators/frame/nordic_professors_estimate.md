# Nordic physics professors (nominator category 4): rough estimate

Status: **deprioritized** on 2026-09-30. The coordinator decided the 100-nominator sample will be drawn only from OpenAlex publication data (see `international_pool.csv`). This file keeps what had already been collected. It is not a finished count.

## Statutory wording (nobelprize.org/nomination/physics, fetched 2026-09-30)
Category 4 is "Tenured professors in the Physical sciences at the universities and institutes of technology of Sweden, Denmark, Finland, Iceland and Norway, and Karolinska Institutet, Stockholm". The wording says "physical sciences", not "physics", so astronomy and possibly neighbouring fields may be included. It is also unclear whether "tenured professors" covers tenured associate professors (DK *lektor*, NO *førsteamanuensis*, FI *university lecturer*). The estimate below counts full professors only.

## Measured directly (staff pages fetched with curl on 2026-09-30)
| Department | Full professors listed | Also listed |
|---|---:|---|
| Niels Bohr Institute, Univ. of Copenhagen (nbi.ku.dk/english/staff) | ~48 | ~40 associate professors, ~30 assistant professors, emeriti |
| Dept. of Physics, Univ. of Oslo (mn.uio.no/fysikk/english/people/aca) | 36 | 21 associate professors, 7 "Professor II" (adjunct) |
| Dept. of Physics, NTNU (ntnu.edu/physics/employees) | 34 | 16 associate professors |

The staff pages for Uppsala, Lund, KTH, Chalmers, Stockholm, Gothenburg, Aarhus, DTU, Helsinki, Aalto and Iceland are rendered by JavaScript or sit behind a Cloudflare challenge, so curl could not count them. They were not counted.

## Order-of-magnitude estimate (full professors in physics and astronomy)
The measured large departments have 35 to 50 full professors each. Other departments were given size classes by judgement, not by measurement:

| Country | Assumed departments (full professors) | Estimate |
|---|---|---:|
| Sweden | Uppsala ~55, Lund ~50, KTH ~45, Chalmers ~45, Stockholm (incl. astronomy, Nordita) ~40, Linköping ~30, Gothenburg ~15, Umeå ~12, others (Luleå, Karlstad, Örebro, Linnaeus, Mid Sweden, Malmö, KI medical physics) ~25 | ~300-350 |
| Denmark | NBI 48 (measured), DTU Physics + Electro/Fotonik ~35, Aarhus ~30, SDU ~10, Aalborg + Roskilde ~10 | ~130 |
| Norway | Oslo 36 (measured), NTNU 34 (measured), Bergen ~20, Tromsø ~10, others ~10 | ~110 |
| Finland | Helsinki (incl. atmospheric physics) ~40, Aalto ~35, Jyväskylä ~20, Turku ~12, Oulu ~10, Tampere ~10, others ~5 | ~130 |
| Iceland | University of Iceland ~8 | ~8 |
| **Total** | | **~700-750 (plausible range 500-1,000)** |

If tenured associate professors in DK, NO and FI count, the total roughly doubles to ~1,200-1,500.

Implication: with about 3,000 invitations per year, statutory category 4 could make up roughly a quarter of all physics nominators. The OpenAlex-based pool puts the Nordic countries at only ~3% (their share of publication output), so a sample drawn purely from publication shares under-weights Nordic nominators compared with the statutory frame.

## Example Nordic professors (41), systematically taken from the three measured staff lists
Subfields are my classification (project categories).

| Name | Institution | Subfield |
|---|---|---|
| Brian Møller Andersen | Niels Bohr Institute, Copenhagen | condensed matter |
| Emil Bjerrum-Bohr | Niels Bohr Institute, Copenhagen | particle/nuclear |
| Vitor Cardoso | Niels Bohr Institute, Copenhagen | astro/cosmology (gravitation) |
| Poul Henrik Damgaard | Niels Bohr Institute, Copenhagen | particle/nuclear |
| Karsten Flensberg | Niels Bohr Institute, Copenhagen | condensed matter |
| Jens Hjorth | Niels Bohr Institute, Copenhagen | astro/cosmology |
| Charles M. Marcus | Niels Bohr Institute, Copenhagen | condensed matter / quantum information |
| Klaus Mølmer | Niels Bohr Institute, Copenhagen | AMO/quantum optics |
| Jesper Nygård | Niels Bohr Institute, Copenhagen | condensed matter |
| Niels Obers | Niels Bohr Institute, Copenhagen | particle/nuclear (string theory) |
| Eugene Polzik | Niels Bohr Institute, Copenhagen | AMO/quantum optics |
| Albert Schliesser | Niels Bohr Institute, Copenhagen | AMO/quantum optics (optomechanics) |
| Irene Tamborra | Niels Bohr Institute, Copenhagen | astro/cosmology (astroparticle) |
| Kim Sneppen | Niels Bohr Institute, Copenhagen | statistical/complex systems |
| Dorthe Dahl-Jensen | Niels Bohr Institute, Copenhagen | other (ice/climate physics) |
| Erik Adli | University of Oslo | particle/nuclear (accelerators) |
| Torsten Bringmann | University of Oslo | particle/nuclear (astroparticle theory) |
| Anders Malthe-Sørenssen | University of Oslo | statistical/complex systems |
| Knut Jørgen Måløy | University of Oslo | statistical/complex systems |
| Sunniva Siem | University of Oslo | particle/nuclear |
| Ann-Cecilie Larsen | University of Oslo | particle/nuclear |
| Heidi Sandaker | University of Oslo | particle/nuclear |
| Steinar Stapnes | University of Oslo | particle/nuclear |
| Andrej Kuznetsov | University of Oslo | condensed matter |
| Olav Fredrik Syljuåsen | University of Oslo | condensed matter |
| Justin William Wells | University of Oslo | condensed matter |
| Johannes Skaar | University of Oslo | optics/photonics |
| Jøran Idar Moen | University of Oslo | other (space physics) |
| Arne Brataas | NTNU | condensed matter |
| Asle Sudbø | NTNU | condensed matter |
| Jacob Wüsthoff Linder | NTNU | condensed matter |
| Mathias Kläui | NTNU | condensed matter |
| Chiara Ciccarelli | NTNU | condensed matter |
| Jeroen Danon | NTNU | condensed matter / quantum information |
| Randi Holmestad | NTNU | condensed matter (electron microscopy) |
| Jens Oluf Andersen | NTNU | particle/nuclear (theory) |
| Michael Kachelriess | NTNU | astro/cosmology (astroparticle) |
| Alex Hansen | NTNU | statistical/complex systems |
| Sauro Succi | NTNU | statistical/complex systems |
| Erika Eiser | NTNU | statistical/complex systems (soft matter) |
| Irina T. Sorokina | NTNU | optics/photonics |

Gaps: there are no Swedish, Finnish or Icelandic names here, because those pages could not be scraped. For Swedish senior physicists, see the Swedish members in `kva_physics.csv`.
