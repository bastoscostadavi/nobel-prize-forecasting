# Five neutral Peace committee profile versions

Each of the five voting members has `profile_terra_v1.md` through `profile_terra_v5.md`. All five versions use the same factual record from the original `profile.md`: biographies, publications and public work, attributed statements, professional connections, sources and factual uncertainties. The prescriptive Persona section and unsupported deductions about temperament or voting preferences are removed uniformly, including in v1. Original profiles remain unchanged.

The four additional versions change section headings, section order, biography paragraph order and the presentation or order of the public-work and connections sections. Existing factual wording and direct quotations are preserved. These are editorial sensitivity variants, with no invented personalities, new factual research or differing opinions. Statements in official committee speeches and releases retain the caveat that they may express a collective position rather than a member's personal view.

`scripts/build_peace_profile_variants.py` reproduces and verifies the 25 files. It checks identical retained factual-token, quotation and source-link inventories, excludes Persona instructions, refuses to overwrite a differing existing variant, and records source and output SHA-256 hashes in `terra_profile_variants.json`.

The voting members are chair Jørgen Watne Frydnes, vice chair Asle Toje, Kristin Clemet, Anne Enger and Gry Larsen. Kristian Berg Harpviken is the non-voting secretary; his original profile is preserved and he does not receive a voting profile version.

The requested design is 25 committee simulations per model: five runs with each of the five profile versions. Every voting member and every stage within a simulation should use its assigned version. Profile-version groups have equal weight. Simulated selection frequencies describe these runs and are not calibrated Nobel Prize probabilities.
