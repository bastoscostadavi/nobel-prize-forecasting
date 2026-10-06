"""Build the consolidated 2026 Peace candidate list from the Claude and Codex drafts.

Every input entry must be either merged into a retained candidate or listed in
TRIM with a reason; the script refuses to write otherwise.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "claude-opus-5-5" / "candidates.json"
CODEX = ROOT / "codex" / "candidates.json"

PUB = "public_nomination_2026"
PRIO = "prio_director_list_2026"
ODDS = "bookmaker_leader_sept_2026"
AUTHOR = "author_addition"

# (field, achievement, credited pool, claude ids, codex keys, evidence, flags)
CANDIDATES = [
    # Humanitarian relief and protection of civilians
    ("Humanitarian relief in armed conflict",
     "Volunteer-led emergency relief through communal kitchens, clinics and evacuations in Sudan's civil war",
     ["Sudan's Emergency Response Rooms"],
     ["p01"], ["sudan-emergency-response-rooms"], [PUB, PRIO, ODDS], []),
    ("Humanitarian relief in armed conflict",
     "Protecting, rescuing and returning children affected by the war in Ukraine",
     ["Mykola Kuleba", "Save Ukraine", "Save the Children"],
     ["p02"], ["mykola-kuleba", "save-ukraine", "save-the-children"], [PUB, PRIO], []),
    ("Humanitarian relief in armed conflict",
     "Independent medical care for civilians in war zones and defence of medical neutrality",
     ["Médecins Sans Frontières"],
     ["p03"], ["msf"], [ODDS],
     ["Previous laureate (1999).",
      "Committee proximity: chair Frydnes worked for MSF 2004-2011 and later sat on the MSF Norway board."]),
    ("Humanitarian relief in armed conflict",
     "Upholding international humanitarian law and protecting civilians, detainees and the missing",
     ["International Committee of the Red Cross", "International Federation of Red Cross and Red Crescent Societies"],
     ["p04"], ["icrc"], [AUTHOR], ["ICRC is a three-time laureate (1917, 1944, 1963); IFRC shared 1963."]),
    ("Humanitarian relief in armed conflict",
     "Sustaining education, health care and relief for Palestine refugees under existential political pressure",
     ["UNRWA", "Philippe Lazzarini"],
     ["p05"], ["unrwa", "philippe-lazzarini"], [PUB], ["Politically contested; Israel banned its operations in 2024-25."]),
    ("Humanitarian relief in armed conflict",
     "Feeding civilians at scale in war and disaster zones, including Gaza, Ukraine and Sudan",
     ["World Central Kitchen", "José Andrés"],
     ["p06"], ["world-central-kitchen", "jose-andres"], [AUTHOR], []),
    ("Protection of the displaced",
     "Protection and assistance for a record number of forcibly displaced people and defence of humanitarian access",
     ["UNHCR", "Norwegian Refugee Council", "Jan Egeland"],
     ["p07", "p08"], ["unhcr", "norwegian-refugee-council", "jan-egeland"], [AUTHOR],
     ["UNHCR is a two-time laureate (1954, 1981).", "NRC is Norwegian; the committee has never honoured a Norwegian organisation."]),
    ("Humanitarian relief in armed conflict",
     "Civilian search and rescue under bombardment in Syria",
     ["Syria Civil Defence (White Helmets)", "Raed Al Saleh"],
     ["p09"], ["syria-civil-defence"], [AUTHOR],
     ["Raed Al Saleh became a minister in Syria's transitional government in 2025."]),
    ("Humanitarian relief in armed conflict",
     "Rescuing migrants and refugees at sea in the central Mediterranean",
     ["SOS Méditerranée", "Sea-Watch", "Open Arms", "Óscar Camps"],
     ["p10"], ["sos-mediterranee"], [AUTHOR], []),
    ("Humanitarian relief in armed conflict",
     "Keeping hospitals running and treating patients under siege in Gaza",
     ["Hussam Abu Safiya", "Sara Al-Saqqa"],
     ["p12"], ["hussam-abu-safiya", "sara-al-saqqa"], [PUB],
     ["Abu Safiya has been detained by Israel since Dec 2024."]),
    ("Disarmament and protection of civilians",
     "Demining and clearing explosive remnants of war to protect civilians",
     ["HALO Trust", "Mines Advisory Group", "Norwegian People's Aid"],
     ["p13"], ["halo-trust", "mines-advisory-group"], [AUTHOR],
     ["ICBL already received the prize (1997).", "Norwegian People's Aid is Norwegian."]),
    # Press freedom
    ("Press freedom",
     "Defending journalists as killings of reporters reach record levels",
     ["Committee to Protect Journalists", "Reporters Without Borders"],
     ["p16", "p17"], ["committee-to-protect-journalists", "reporters-without-borders"], [PRIO], []),
    ("Press freedom",
     "Reporting from Gaza at extreme personal risk in the deadliest conflict for journalists on record",
     ["Palestinian Journalists Syndicate", "Wael Al-Dahdouh", "Motaz Azaiza", "Bisan Owda"],
     ["p18"], [], [AUTHOR], []),
    ("Press freedom",
     "Independent journalism under authoritarian rule in Georgia and Belarus",
     ["Mzia Amaglobeli", "Andrzej Poczobut"],
     ["p21"], ["mzia-amaglobeli", "andrzej-poczobut"], [AUTHOR], ["Joint Sakharov Prize 2025; both imprisoned."]),
    ("Press freedom",
     "Defending press freedom and democracy in Hong Kong",
     ["Jimmy Lai", "Chow Hang-tung", "Nathan Law"],
     ["p53"], ["jimmy-lai", "nathan-law"], [AUTHOR], ["Lai sentenced in Feb 2026."]),
    ("Accountability and international law",
     "Open-source and spatial investigation of war crimes and disinformation",
     ["Bellingcat", "Eliot Higgins", "Forensic Architecture"],
     ["p20"], ["forensic-architecture"], [AUTHOR], []),
    # International law and accountability
    ("Accountability and international law",
     "Peace through international law: adjudicating disputes between states and prosecuting atrocity crimes",
     ["International Court of Justice", "International Criminal Court"],
     ["p22"], ["international-court-of-justice", "international-criminal-court"], [PUB, PRIO],
     ["ICC under US sanctions; prosecutor Karim Khan on leave amid a misconduct inquiry."]),
    ("Accountability and international law",
     "Defending judicial independence as a check on executive power",
     ["International Association of Judges"],
     ["p23"], ["international-association-of-judges"], [PUB], []),
    ("Accountability and international law",
     "Upholding international law and documenting violations in the occupied Palestinian territory",
     ["Francesca Albanese"],
     ["p24"], ["francesca-albanese"], [PUB], ["Under US sanctions since July 2025; highly polarising."]),
    ("Accountability and international law",
     "Israeli and Palestinian documentation of abuses under occupation and in the Gaza war",
     ["B'Tselem", "Al-Haq", "Breaking the Silence", "Physicians for Human Rights-Israel"],
     ["p66"], ["btselem", "al-haq"], [AUTHOR], []),
    ("Accountability and international law",
     "Global investigation and advocacy against human rights abuses",
     ["Human Rights Watch", "Amnesty International"],
     ["p28"], ["human-rights-watch", "amnesty-international"], [AUTHOR], ["Amnesty is a previous laureate (1977)."]),
    ("Accountability and international law",
     "Documenting the disappeared of the Assad era and collecting evidence for prosecutions",
     ["Syrian Center for Media and Freedom of Expression", "Mazen Darwish", "Caesar Families Association",
      "Syrian Network for Human Rights", "Commission for International Justice and Accountability"],
     ["p25", "p26"], [], [AUTHOR], []),
    # Nuclear safety
    ("Nuclear safety and non-proliferation",
     "Nuclear safety and safeguards in wartime, including at Zaporizhzhia, and verification in Iran",
     ["International Atomic Energy Agency", "Rafael Grossi"],
     ["p31"], ["iaea"], [AUTHOR], ["IAEA and ElBaradei are 2005 laureates."]),
    # Climate and Indigenous rights
    ("Climate and environmental peace",
     "Climate justice advocacy for Africa and the global South",
     ["Vanessa Nakate"],
     ["p34"], [], [ODDS], []),
    ("Climate and environmental peace",
     "Youth climate mobilisation and non-violent solidarity activism",
     ["Greta Thunberg"],
     ["p35"], ["greta-thunberg"], [PUB], []),
    ("Climate and environmental peace",
     "A lifetime making the planetary crisis visible to a global public",
     ["David Attenborough"],
     ["p36"], [], [ODDS], ["Turned 100 in May 2026."]),
    ("Climate and environmental peace",
     "Securing the ICJ advisory opinion on states' legal obligations on climate change",
     ["Pacific Islands Students Fighting Climate Change", "Ralph Regenvanu", "Julian Aguon", "Vishal Prasad"],
     ["p37"], ["pacific-islands-students-fighting-climate-change", "julian-aguon"], [AUTHOR], []),
    ("Climate and environmental peace",
     "Indigenous land defence in the Amazon as climate protection",
     ["Davi Kopenawa Yanomami", "Hutukara Yanomami Association", "Articulação dos Povos Indígenas do Brasil (APIB)",
      "Raoni Metuktire"],
     ["p40"], ["davi-kopenawa", "hutukara-yanomami-association"], [AUTHOR], []),
    # Democracy and human rights
    ("Democracy and human rights",
     "Continuing the Russian democratic opposition after Alexei Navalny's death",
     ["Yulia Navalnaya"],
     ["p42"], ["yulia-navalnaya"], [ODDS], []),
    ("Democracy and human rights",
     "Defending Russia's political prisoners and refugees",
     ["OVD-Info", "Svetlana Gannushkina", "Vladimir Kara-Murza", "Ilya Yashin"],
     ["p43"], ["vladimir-kara-murza", "ilya-yashin"], [AUTHOR], ["Memorial already honoured in 2022."]),
    ("Democracy and human rights",
     "Non-violent resistance to dictatorship in Belarus",
     ["Sviatlana Tsikhanouskaya", "Maria Kalesnikava"],
     ["p44"], ["sviatlana-tsikhanouskaya", "maria-kolesnikova"], [AUTHOR],
     ["Bialiatski/Viasna honoured 2022. Kalesnikava released in 2026 (Codex draft)."]),
    ("Democracy and human rights",
     "Defending Moldova's democracy against hybrid interference",
     ["Maia Sandu"],
     ["p48"], ["maia-sandu"], [PUB], []),
    ("Democracy and human rights",
     "Student-led non-violent movement for accountability and the rule of law in Serbia",
     ["Serbian student protest movement"],
     ["p49"], [], [AUTHOR], ["An unstructured movement; recipient hard to define."]),
    ("Democracy and human rights",
     "Non-violent legal and civic defence of democracy against Georgia's authoritarian turn",
     ["Georgian Young Lawyers' Association", "Georgian pro-European civic movement"],
     ["p50"], ["georgian-young-lawyers-association"], [AUTHOR], []),
    ("Democracy and human rights",
     "Exposing the mass internment of Uyghurs",
     ["Ilham Tohti", "Rahile Dawut", "World Uyghur Congress"],
     ["p54"], ["ilham-tohti"], [AUTHOR], ["Tohti and Dawut imprisoned with life sentences."]),
    ("Democracy and human rights",
     "Non-violent resistance to Myanmar's military junta",
     ["Myanmar Civil Disobedience Movement", "National Unity Consultative Council", "Kyaw Moe Tun",
      "Justice for Myanmar"],
     ["p55"], ["myanmar-nucc", "kyaw-moe-tun", "justice-for-myanmar"], [AUTHOR],
     ["Aung San Suu Kyi is a 1991 laureate."]),
    ("Women, peace and security",
     "Women's resistance and education under Taliban rule",
     ["Mahbouba Seraj", "Fawzia Koofi", "Sima Samar"],
     ["p57"], ["mahbouba-seraj", "fawzia-koofi", "sima-samar"], [AUTHOR], []),
    ("Women, peace and security",
     "'Woman, Life, Freedom': women's non-violent resistance in Iran",
     ["Nasrin Sotoudeh"],
     ["p58"], ["nasrin-sotoudeh"], [AUTHOR], ["Narges Mohammadi is a 2023 laureate; a repeat theme."]),
    ("Democracy and human rights",
     "Non-violent mobilisation against enforced disappearances in Balochistan",
     ["Mahrang Baloch"],
     [], ["mahrang-baloch"], [AUTHOR], []),
    # Israeli-Palestinian peacebuilding
    ("Mediation and reconciliation",
     "Joint Jewish-Arab non-violent movements for peace and equality",
     ["Standing Together", "Combatants for Peace", "Parents Circle-Families Forum"],
     ["p65"], ["combatants-for-peace", "parents-circle-families-forum"], [AUTHOR], []),
    ("Women, peace and security",
     "Israeli and Palestinian women organising together for a negotiated peace",
     ["Women Wage Peace", "Women of the Sun", "Yael Admi", "Reem Al-Hajajreh"],
     [], ["women-wage-peace", "women-of-the-sun", "yael-admi", "reem-al-hajajreh"], [AUTHOR], []),
    # Diplomacy, mediation and multilateral cooperation
    ("Diplomacy and mediation",
     "Brokering the 2025 Gaza ceasefire and hostage releases",
     ["Donald Trump", "Steve Witkoff", "Jared Kushner", "Mohammed bin Abdulrahman Al Thani", "Hassan Rashad",
      "Ibrahim Kalın"],
     ["p70", "p71"], ["donald-trump"], [PUB, ODDS],
     ["Committee hostility to Trump is well documented; passed over in 2025."]),
    ("Diplomacy and mediation",
     "Non-governmental and faith-based mediation of armed conflicts",
     ["Centre for Humanitarian Dialogue", "Community of Sant'Egidio"],
     ["p75", "p76"], ["centre-for-humanitarian-dialogue", "community-of-santegidio"], [AUTHOR], []),
    ("Women, peace and security",
     "Community peacebuilding, demilitarisation and survivor support in Somalia",
     ["Elman Peace", "Ilwad Elman", "Fartuun Adan"],
     [], ["elman-peace", "ilwad-elman", "fartuun-adan"], [AUTHOR], []),
    ("Multilateral cooperation",
     "Preserving the rules-based multilateral trading system against trade wars",
     ["World Trade Organization", "Ngozi Okonjo-Iweala"],
     ["p83"], ["world-trade-organization"], [PUB, PRIO], []),
    ("Multilateral cooperation",
     "Twenty-five years of cooperation between geopolitical rivals in orbit",
     ["International Space Station partnership"],
     ["p84"], ["international-space-station-partnership"], [PRIO], ["Recipient hard to define."]),
    ("Multilateral cooperation",
     "Global health cooperation amid the collapse of aid funding",
     ["World Health Organization", "Tedros Adhanom Ghebreyesus"],
     ["p87"], ["world-health-organization"], [AUTHOR], ["US withdrawal took effect in Jan 2026."]),
]

UNLIKELY = "most unlikely outcome (long shot, or a recipient the committee is very unlikely to choose)"
WEAK = "weaker or narrower than a retained entry in the same area"
PRIOR = "substantial overlap with a recent laureate"

TRIM = {
    # Claude draft
    "p11": WEAK, "p14": WEAK, "p15": PRIOR, "p19": WEAK, "p27": WEAK, "p29": WEAK, "p30": PRIOR,
    "p32": UNLIKELY, "p33": UNLIKELY, "p38": WEAK, "p39": UNLIKELY, "p41": UNLIKELY, "p45": UNLIKELY,
    "p46": UNLIKELY, "p47": PRIOR, "p51": WEAK, "p52": UNLIKELY, "p56": WEAK, "p59": WEAK, "p60": WEAK,
    "p61": UNLIKELY, "p62": WEAK, "p63": UNLIKELY, "p64": UNLIKELY, "p67": WEAK, "p68": WEAK, "p69": WEAK,
    "p72": UNLIKELY, "p73": UNLIKELY, "p74": UNLIKELY, "p77": UNLIKELY, "p78": UNLIKELY, "p79": UNLIKELY,
    "p80": UNLIKELY, "p81": UNLIKELY, "p82": UNLIKELY, "p85": UNLIKELY, "p86": WEAK, "p88": WEAK,
    "p89": WEAK, "p90": WEAK, "p91": UNLIKELY, "p92": UNLIKELY, "p93": UNLIKELY, "p94": WEAK,
    # Codex draft (main pool)
    "aaja-chemnitz": UNLIKELY, "lisa-murkowski": UNLIKELY, "alokiir-malual": UNLIKELY,
    "aminatou-haidar": WEAK, "anabela-lemos": WEAK, "justica-ambiental": WEAK, "audrey-tang": WEAK,
    "concordis-international": UNLIKELY, "council-of-europe": WEAK, "gubad-ibadoghlu": WEAK,
    "guo-jianmei": WEAK, "human-rights-data-analysis-group": WEAK,
    "international-commission-on-missing-persons": WEAK, "international-crisis-group": UNLIKELY,
    "issa-amro": WEAK, "youth-against-settlements": WEAK, "jalila-haider": WEAK, "joan-carling": WEAK,
    "john-coale": UNLIKELY, "juan-carlos-jintiach": WEAK, "mark-carney": UNLIKELY, "marthe-wandou": WEAK,
    "mother-nature-cambodia": WEAK, "nonviolent-peaceforce": WEAK, "osce-odihr": WEAK, "carter-center": WEAK,
    "palestine-childrens-relief-fund": WEAK, "peace-direct": WEAK, "phyllis-omido": WEAK,
    "pope-leo-xiv": UNLIKELY, "ctbto-preparatory-commission": WEAK, "rural-womens-assembly": WEAK,
    "search-for-common-ground": WEAK, "stop-killer-robots": WEAK, "svalbard-global-seed-vault": UNLIKELY,
    "timnit-gebru": UNLIKELY, "unesco": WEAK, "victoria-tauli-corpuz": WEAK, "visaka-dharmadasa": WEAK,
    "volodymyr-zelenskyy": UNLIKELY, "wilpf": WEAK, "yad-vashem": UNLIKELY,
    # Codex repeat-award supplement
    "ican-nuclear": PRIOR, "unicef": WEAK, "world-food-programme": PRIOR,
}

# Excluded before the merge for committee proximity (Claude draft method note).
PROXIMITY_EXCLUSIONS = [
    {"name": "CARE International", "reason": "Gry Larsen was Secretary General of CARE Norway (2015-2020)."},
    {"name": "PEN International / Norwegian PEN", "reason": "Chair Frydnes is Secretary General of PEN Norway."},
]


def main() -> None:
    claude = json.loads(CLAUDE.read_text())
    codex = json.loads(CODEX.read_text())
    claude_ids = {c["candidate_id"]: c for c in claude["candidates"]}
    codex_keys = {c["candidate_key"]: c for c in codex["candidates"] + codex["repeat_award_supplement"]}

    used_claude = [i for c in CANDIDATES for i in c[3]]
    used_codex = [k for c in CANDIDATES for k in c[4]]
    for ids, pool, label in ((used_claude, claude_ids, "Claude"), (used_codex, codex_keys, "Codex")):
        unknown = sorted(set(ids) - set(pool))
        if unknown:
            raise SystemExit(f"unknown {label} ids: {unknown}")
        dup = sorted({i for i in ids if ids.count(i) > 1} | (set(ids) & set(TRIM)))
        if dup:
            raise SystemExit(f"{label} ids used twice or both kept and trimmed: {dup}")
        missing = sorted(set(pool) - set(ids) - set(TRIM))
        if missing:
            raise SystemExit(f"{label} ids neither kept nor trimmed: {missing}")
    if len(CANDIDATES) > 50:
        raise SystemExit("more than 50 candidates")

    ordered = sorted(CANDIDATES, key=lambda c: (c[0], c[1]))
    entries = []
    for n, (field, achievement, names, cids, ckeys, evidence, flags) in enumerate(ordered, 1):
        entries.append({
            "candidate_id": f"PE{n:02d}",
            "achievement": achievement,
            "field": field,
            "credited_names": names,
            "evidence": evidence,
            "flags": flags,
            "sources": {"claude": cids, "codex": ckeys},
        })

    trimmed = []
    for key, reason in TRIM.items():
        if key in claude_ids:
            c = claude_ids[key]
            trimmed.append({"source": "claude", "id": key, "name": "; ".join(c["nominees"]),
                            "achievement": c["achievement"], "reason": reason})
        else:
            c = codex_keys[key]
            trimmed.append({"source": "codex", "id": key, "name": c["name"], "reason": reason})

    out = {
        "schema_version": 1,
        "category": "peace",
        "prize_year": 2026,
        "list_id": "peace-2026",
        "version": 1,
        "prepared_by": "Claude (claude-opus-5-5) consolidation of the Claude and Codex drafts",
        "research_cutoff": "2026-10-03",
        "nominator_stage": {"status": "omitted", "simulated_nominations": False},
        "inputs": [
            {"list_id": "claude-opus-5-5", "path": str(CLAUDE.relative_to(ROOT.parents[2])),
             "candidate_count": len(claude["candidates"])},
            {"list_id": codex["list_id"], "path": str(CODEX.relative_to(ROOT.parents[2])),
             "candidate_count": len(codex["candidates"]),
             "repeat_award_supplement_count": len(codex["repeat_award_supplement"])},
        ],
        "candidate_count": len(entries),
        "candidate_order": "alphabetical_by_field_then_achievement_not_rank",
        "award_rule": "credited_names is a pool and may exceed three; an award names at most three laureates "
                      "(individuals and/or organisations).",
        "evidence_definitions": {
            PUB: "publicly reported 2026 nomination (sealed list; submission timing not verified)",
            PRIO: "on the PRIO Director's 2026 list",
            ODDS: "among the bookmaker leaders in late September 2026",
            AUTHOR: "added by one or both drafting models on documented work",
        },
        "candidates": entries,
        "trimmed_entries": trimmed,
        "proximity_exclusions": PROXIMITY_EXCLUSIONS,
    }
    (ROOT / "candidates.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    with open(ROOT / "candidates.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["candidate_id", "achievement", "field", "credited_names"])
        for e in entries:
            w.writerow([e["candidate_id"], e["achievement"], e["field"], "; ".join(e["credited_names"])])
    print(f"{len(entries)} candidates, {len(trimmed)} trimmed input entries")


if __name__ == "__main__":
    main()
