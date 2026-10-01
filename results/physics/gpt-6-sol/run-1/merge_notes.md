# Physics run-1 consolidation notes

All 100 nominations were consolidated using only this run's source JSON records and the merge prompt. Counts refer to people explicitly listed in each record's `nominees` array; names mentioned as historical context or collaborators in motivation prose are not additional nominees. Names are ordered by nomination frequency, then first appearance in lexicographic source-file order (and source-array order within a file).

## Ambiguous merge decisions

- **AdS/CFT and the holographic principle:** `thorlacius-larus.json` credits Maldacena, Susskind and 't Hooft, whereas `kim-seok.json` and `randall-lisa.json` credit Maldacena, Polyakov and Witten. The first record explicitly nominates the principle's realization in the same 1997 gauge/gravity duality and emphasizes the same black-hole and strong-coupling consequences. These were merged; the alternative credited names are retained in `other_names`.
- **Squeezing:** `adhikari-rana.json` emphasizes gravitational-wave interferometry and Mavalvala, while `nussenzveig-paulo.json` and `walmsley-ian.json` emphasize Kimble's generation of squeezed light. All nominate squeezed light as a resource for surpassing quantum measurement noise, with the same Caves-to-detector development. They were merged; frequency places Kimble in the first three and preserves Mavalvala in `other_names`.
- **Cirac-Zoller theory and trapped-ion processors:** `bloch-immanuel.json` and `lukin-mikhail.json` share the 1995 ion-gate blueprint and optical-lattice simulation proposals. They were merged despite Blatt appearing only in the latter. The experimentally focused optical-lattice nominations (`demarco-brian.json`, `kohl-michael.json`) remain a separate candidate, as do the Rydberg-array nomination and optical atom-photon network nomination: their defining experimental platforms and appropriate credited people differ.
- **Optical-lattice simulation:** The two nominations concern Hubbard-model simulation, Mott transitions and quantum gas microscopes, despite one crediting Zoller and the other Esslinger. They were merged; the frequency/tie rule retains Zoller in the first three and Esslinger in `other_names`.
- **Kilonovae:** The two records nominate the same prediction/identification of radioactive merger transients and r-process production, although one adds Tanvir's early observation and the other Tanaka's opacity calculations. They were merged and preserve both names.
- **BAO:** The prediction-inclusive `verde-licia.json` and observation/survey-focused `frenk-carlos.json` concern the same acoustic feature and cosmic standard ruler. They were merged, preserving both Sunyaev and Colless; Colless wins their one-nomination tie by first appearance.
- **IceCube:** The four records share the high-energy astrophysical-neutrino discovery and telescope realization. Spiering's inclusion in `resconi-elisa.json` does not create a separate achievement and is preserved.
- **Photonic crystals:** The band-gap concepts and Noda's later device realizations were merged as one discovery/development. Photonic crystal fibres (`tong-limin.json`) remain separate because they nominate a specific fibre architecture and guidance technology, with different inventors.
- **Circuit QED:** The two nominations concern the same 2004 strong-coupling framework, though one names Wallraff and the other Girvin. They were merged and preserve both names; Wallraff precedes Girvin by the source-order tie rule.

## Ambiguous split decisions

- **Exoplanet transit methods versus atmospheric spectroscopy:** `queloz-didier.json` combines radii, Kepler occurrence-rate measurements and spectroscopy; `van-dishoeck-ewine.json` specifically nominates molecular atmospheric detection and retrieval. They remain separate because merging would collapse the Borucki/Kepler demographics contribution into the Tinetti/molecular-spectroscopy contribution. Their common Charbonneau/Seager work is acknowledged by the sources and retained in both groups.
- **Topological quantum matter:** The five topological-insulator/quantum-spin-Hall nominations were merged, but quantum anomalous Hall transport (`xie-xincheng.json`) and topological superconductivity/Majorana theory (`tanaka-yukio.json`) remain separate discoveries with different defining mechanisms and credited people.
- **Clock platforms:** Neutral-atom optical lattice clocks were merged across two records. The thorium-229 nuclear clock remains separate because its nuclear transition and enabling spectroscopy are a distinct achievement despite shared credit to Ye.
- **Related quantum-information devices:** Defect-spin control, semiconductor electron-spin qubits, circuit QED, optical cavity interfaces, optomechanics and quantum error correction remain separate contributions. Shared quantum-network or error-correction applications do not make their discoveries identical.
- **Cosmology:** Inflation and primordial quantum fluctuations were merged across their two records despite Linde/Starobinsky credit differences. WMAP's precision observational mapping and BAO's acoustic standard ruler remain separate nominated achievements.

## Name normalization and source quality

- `Artur Ekert` (`zeilinger-anton.json`) was normalized to `Artur K. Ekert`, matching the other three QKD sources; all four describe E91 and the same Oxford/Singapore affiliation.
- `Viatcheslav Mukhanov` (`challinor-anthony.json`) was normalized to `Viatcheslav F. Mukhanov` (`peiris-hiranya.json`); both sources describe the same Mukhanov-Chibisov fluctuation contribution. This changes the inflation name counts.
- `J. Ignacio Cirac` (`laurat-julien.json`) was normalized to `Juan Ignacio Cirac`, matching the expanded name in the other atomic quantum-information sources. This does not alter a within-group frequency.
- `Alexander Polyakov` in the two AdS/CFT records was normalized to `Alexander M. Polyakov`, the fuller spelling in `parisi-giorgio.json`. The distinct conformal-field-theory achievement remains separate; normalization does not alter the AdS/CFT within-group frequencies.
- No malformed source record was found. All one-off nominations are retained.
