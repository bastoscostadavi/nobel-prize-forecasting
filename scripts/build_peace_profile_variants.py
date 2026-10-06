"""Build five neutral editorial versions for the five Peace voting members.

The source profiles remain untouched. Every version retains the same factual
record, quotations, source links and caveats after uniform removal of Persona
instructions and unsupported deductions about temperament or voting preferences.
Variants reorder existing factual blocks and change headings and presentation;
they never add facts or fabricate member-specific views.
"""

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COMMITTEE = ROOT / "agent-data/peace/committee"
MEMBERS = (
    "frydnes-jorgen-watne",
    "toje-asle",
    "clemet-kristin",
    "enger-anne",
    "larsen-gry",
)
SPLIT_ANCHORS = {
    "clemet-kristin": "She has led Civita since 2006.",
    "enger-anne": "After leaving politics she was Secretary General",
    "frydnes-jorgen-watne": "He became Secretary General of Norsk PEN in 2023.",
    "larsen-gry": "She was Secretary General of CARE Norway",
    "toje-asle": "He served as Research Director at the Norwegian Nobel Institute",
}
REPLACEMENTS = {
    "enger-anne": {
        " The persona is inferred from her political career and SNL's characterisation.": "",
    },
    "frydnes-jorgen-watne": {
        "The persona's emphasis on courage and democracy is inferred from his speeches, which are official committee texts and may reflect collective drafting rather than only his personal view.":
        "His speeches are official committee texts and may reflect collective drafting rather than only his personal view; they do not establish personal voting preferences.",
    },
    "larsen-gry": {
        " The persona is inferred from her career.": "",
    },
    "toje-asle": {
        "The persona's weighting of realism versus normative commitments is an inference from his writings.":
        "His writings do not establish how he would weigh realism against normative commitments in a committee vote.",
    },
    "clemet-kristin": {
        "**Pro-European and transatlantic:**": "**European recognition and commentary:**",
    },
}
SECTION_KEYS = (
    "Biography", "Research / intellectual footprint", "Public statements and values",
    "Connections", "Uncertainty",
)
LAYOUTS = {
    1: (0, 1, 2, 3, 4),
    2: (0, 1, 2, 4, 3),
    3: (1, 0, 3, 2, 4),
    4: (0, 3, 2, 1, 4),
    5: (1, 2, 0, 4, 3),
}
HEADINGS = {
    1: ("Biography", "Research / intellectual footprint", "Attributed public statements", "Connections", "Uncertainty"),
    2: ("Career and public service", "Published work and public activity", "Statements on record", "Institutional and professional ties", "Source limitations"),
    3: ("Biographical record", "Research and public-policy record", "Documented public statements", "Professional connections", "Unresolved details"),
    4: ("Education and appointments", "Subjects addressed in public work", "Attributed statements", "Affiliations and relationships", "Evidence caveats"),
    5: ("Career background", "Intellectual and public record", "Public statements and their attribution", "Documented connections", "Uncertainties in the record"),
}
NOTE = (
    "Neutral factual record of committee service, biography, public work, attributed "
    "statements and evidence limitations. No inferred temperament, prize preference "
    "or likely vote is assigned. Official committee releases and presentation "
    "speeches may express a collective position rather than a personal view."
)


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def parse_source(member, raw):
    blocks = re.split(r"^## (.+)\n", raw, flags=re.M)
    sections = dict(zip(blocks[1::2], blocks[2::2]))
    if set(sections) != set(SECTION_KEYS) | {"Persona"}:
        raise ValueError(f"Unexpected source sections for {member}: {set(sections)}")
    header = blocks[0].strip()
    factual = {key: sections[key].strip() for key in SECTION_KEYS}
    for old, new in REPLACEMENTS.get(member, {}).items():
        matches = [key for key, body in factual.items() if old in body]
        if len(matches) != 1:
            raise ValueError(f"Expected one occurrence of removal for {member}: {old}")
        key = matches[0]
        factual[key] = factual[key].replace(old, new)
    if "**Role:** Secretary" in header or "non-voting" in header:
        raise ValueError(f"Non-voting member cannot receive simulation profiles: {member}")
    return header, factual


def factual_tokens(text):
    # Removing bullet markers permits equivalent bullet/paragraph presentation.
    return Counter(re.sub(r"(?m)^- ", "", text).split())


def quote_inventory(text):
    return Counter(re.findall(r'"([^"\n]*)"', text))


def render(member, header, factual, version):
    bodies = [factual[key] for key in SECTION_KEYS]
    if version > 1:
        biography = bodies[0]
        anchor = SPLIT_ANCHORS[member]
        if biography.count(anchor) != 1:
            raise ValueError(f"Biography anchor changed for {member}")
        position = biography.index(anchor)
        early, later = biography[:position].strip(), biography[position:].strip()
        bodies[0] = "\n\n".join((later, early) if version in (3, 5) else (early, later))
    if version in (3, 4):
        research = bodies[1].splitlines()
        if any(line and not line.startswith("- ") for line in research):
            raise ValueError(f"Research paragraphs need explicit handling for {member}")
        bodies[1] = "\n\n".join(line[2:] for line in reversed(research) if line)
    if version == 5:
        bodies[3] = "\n".join(reversed(bodies[3].splitlines()))
    if factual_tokens("\n".join(bodies)) != factual_tokens("\n".join(factual.values())):
        raise ValueError(f"Editorial variant changed retained facts: {member} v{version}")
    # Preserve the entire source header, including links and dated verification.
    first_line, rest = header.split("\n", 1)
    text = first_line + "\n\n" + NOTE + "\n" + rest + "\n\n"
    text += "\n\n".join(
        f"## {HEADINGS[version][index]}\n\n{bodies[index]}"
        for index in LAYOUTS[version]
    ) + "\n"
    retained = header + "\n" + "\n".join(factual.values())
    if quote_inventory(text) != quote_inventory(retained):
        raise ValueError(f"Quotation inventory changed: {member} v{version}")
    source_links = Counter(re.findall(r"https?://\S+", retained))
    if Counter(re.findall(r"https?://\S+", text)) != source_links:
        raise ValueError(f"Source-link inventory changed: {member} v{version}")
    if re.search(r"(?im)^## Persona$|\bYou are\b|\bpersona\b", text):
        raise ValueError(f"Persona content remains: {member} v{version}")
    return text


def main():
    manifest = {
        "schema_version": 1,
        "profile_versions": 5,
        "voting_members": list(MEMBERS),
        "excluded_non_voting_secretary": "harpviken-kristian-berg",
        "policy": "Neutral factual conditioning in all five versions; editorial order, headings and presentation vary while retained facts, quotation and link inventories remain identical. No new research or inferred preferences.",
        "members": {},
    }
    outputs = {}
    originals = {}
    for member in MEMBERS:
        source = COMMITTEE / member / "profile.md"
        raw = source.read_text()
        originals[source] = raw
        header, factual = parse_source(member, raw)
        record = {"source_path": str(source.relative_to(ROOT)), "source_sha256": sha256(raw), "versions": {}}
        manifest["members"][member] = record
        for version in range(1, 6):
            target = source.with_name(f"profile_terra_v{version}.md")
            text = render(member, header, factual, version)
            if target.exists() and target.read_text() != text:
                raise SystemExit(f"Refusing to overwrite a different existing profile: {target}")
            outputs[target] = text
            record["versions"][str(version)] = {"path": str(target.relative_to(ROOT)), "sha256": sha256(text)}
    # Validate all files before writing any version.
    for target, text in outputs.items():
        target.write_text(text)
    (COMMITTEE / "terra_profile_variants.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    for source, raw in originals.items():
        if source.read_text() != raw:
            raise ValueError(f"Original source was changed during generation: {source}")
    print("Created/verified 25 neutral Peace profiles: five voting members × five versions; original profiles unchanged. Fact-token, quotation and source-link inventories verified for every variant.")


if __name__ == "__main__":
    main()
