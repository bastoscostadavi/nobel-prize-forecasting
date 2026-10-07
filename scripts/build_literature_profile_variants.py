"""Build five factual editorial versions for each of six Literature members.

Original profiles remain untouched. Facts, quotations and source links are
held constant across versions after removal of Persona and inferred tastes.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COMMITTEE = ROOT / 'agent-data/literature/committee'
MEMBERS = ('olsson-anders', 'mattson-ellen', 'sward-anne', 'sem-sandberg-steve', 'palm-anna-karin', 'carlberg-ingrid')
SECTION_KEYS = ('Biography', 'Research / intellectual footprint', 'Public statements and values', 'Connections', 'Uncertainty')
REMOVALS = {
    'olsson-anders': {
        '- His lean toward difficult, language-centred modernist work is inferred from his scholarship and speeches. Ceremony speeches are presented on behalf of the Academy, so they do not purely reflect his personal taste.':
        '- Ceremony speeches are presented on behalf of the Academy and do not establish personal voting preferences.',
    },
    'mattson-ellen': {
        '- Her tastes are inferred from her fiction, her interview and two ceremony speeches, which are given on behalf of the Academy.':
        '- Ceremony speeches are given on behalf of the Academy and do not establish personal voting preferences.',
    },
    'sward-anne': {
        '- **Style (inferred from Academy and critical descriptions):** intense, sensory prose that moves between harshness and beauty; attention to the body, desire and taboo.': '',
        '- Her tastes are inferred from interviews and her fiction. She has not given a Nobel ceremony speech that I could find.':
        '- No Nobel ceremony speech by her was identified in the source research.',
    },
    'sem-sandberg-steve': {
        '- His tastes are inferred mostly from his own fiction and essays and from a single set of 2025 Nobel remarks. His DN criticism was not surveyed.':
        '- His DN criticism was not surveyed. The 2025 Nobel remarks do not establish personal voting preferences.',
    },
    'palm-anna-karin': {
        '- Most of her personal literary taste is inferred from her fiction and her Lagerlöf work. Her one Nobel interview was given on behalf of the committee.':
        '- Her Nobel interview was given on behalf of the committee and does not establish personal voting preferences.',
    },
    'carlberg-ingrid': {
        '- Her literary tastes in fiction and poetry are largely undocumented. The persona extrapolates from her non-fiction and her public role (inference).':
        '- Her literary tastes in fiction and poetry are largely undocumented.',
    },
}
LAYOUTS = {1: (0,1,2,3,4), 2: (0,2,1,4,3), 3: (1,0,3,2,4), 4: (0,3,2,1,4), 5: (1,2,0,4,3)}
HEADINGS = {
    1: ('Biography', 'Literary and intellectual work', 'Attributed public statements', 'Connections', 'Uncertainty'),
    2: ('Career background', 'Publications and literary practice', 'Statements on record', 'Professional ties', 'Source limitations'),
    3: ('Biographical record', 'Writing and scholarly record', 'Documented statements', 'Institutional connections', 'Unresolved details'),
    4: ('Education and appointments', 'Subjects and forms in public work', 'Attributed statements', 'Affiliations and relationships', 'Evidence caveats'),
    5: ('Career and committee service', 'Literary and critical record', 'Public statements and attribution', 'Documented connections', 'Uncertainties in the record'),
}
NOTE = ('Neutral factual record of committee service, biography, literary work, attributed statements and evidence limitations. '
        'No inferred temperament, prize preference or likely vote is assigned. Official prize interviews and ceremony speeches '
        'may express a collective position rather than a personal view. Original source verification dates and caveats are retained.')

def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()

def factual_tokens(text):
    return Counter(re.sub(r'(?m)^- ', '', text).split())

def quote_inventory(text):
    return Counter(re.findall(r'"([^"\n]*)"', text))

def parse_source(member, raw):
    blocks = re.split(r'^## (.+)\n', raw, flags=re.M)
    sections = dict(zip(blocks[1::2], blocks[2::2]))
    if set(sections) != set(SECTION_KEYS) | {'Persona'}:
        raise ValueError(f'Unexpected sections: {member}')
    factual = {key: sections[key].strip() for key in SECTION_KEYS}
    for old, new in REMOVALS[member].items():
        matched = [key for key, body in factual.items() if old in body]
        if len(matched) != 1:
            raise ValueError(f'Expected one removal: {member}: {old}')
        factual[matched[0]] = factual[matched[0]].replace(old,new).strip()
    return blocks[0].strip(), factual

def reorder_blocks(body, version, index):
    # Move complete paragraphs/bullets, never clauses inside a statement.
    if index == 1 and version in (3,4,5):
        blocks = re.split(r'(?m)(?=^- )',body)
        if blocks[0].strip():
            raise ValueError('Literary-work section requires explicit handling')
        blocks = [b.strip() for b in blocks if b.strip()]
        if version == 5: blocks = blocks[1:] + blocks[:1]
        else: blocks.reverse()
        return '\n\n'.join(blocks)
    return body

def render(member,header,factual,version):
    bodies=[reorder_blocks(factual[key],version,i) for i,key in enumerate(SECTION_KEYS)]
    if factual_tokens('\n'.join(bodies)) != factual_tokens('\n'.join(factual.values())):
        raise ValueError(f'Facts changed: {member} v{version}')
    first, rest=header.split('\n',1)
    text=first+'\n\n'+NOTE+'\n'+rest+'\n\n'+'\n\n'.join(
        f'## {HEADINGS[version][i]}\n\n{bodies[i]}' for i in LAYOUTS[version])+'\n'
    retained=header+'\n'+'\n'.join(factual.values())
    if quote_inventory(text) != quote_inventory(retained):
        raise ValueError(f'Quotes changed: {member}')
    if Counter(re.findall(r'https?://\S+',text)) != Counter(re.findall(r'https?://\S+',retained)):
        raise ValueError(f'Links changed: {member}')
    if re.search(r'(?im)^## Persona$|\bYou are\b|\bpersona\b|\btastes are inferred\b',text):
        raise ValueError(f'Inferred preferences remain: {member}')
    return text

def main():
    outputs={}; originals={}
    manifest={'schema_version':1,'profile_versions':5,'members':{},'committee_members':list(MEMBERS),
              'policy':'Identical retained facts, quotes, links and caveats in all five versions; editorial headings and block order vary. No fabricated tastes or votes.',
              'coopted_member':'carlberg-ingrid','coopted_voting_status':'Undocumented; simulation voting assumption must be stated separately.'}
    for member in MEMBERS:
        source=COMMITTEE/member/'profile.md'; raw=source.read_text(); originals[source]=raw
        header,factual=parse_source(member,raw)
        record={'source_path':str(source.relative_to(ROOT)),'source_sha256':sha256(raw),'versions':{}}
        manifest['members'][member]=record
        for version in range(1,6):
            target=source.with_name(f'profile_terra_v{version}.md'); text=render(member,header,factual,version)
            if target.exists() and target.read_text()!=text: raise ValueError(f'Refusing to replace different profile: {target}')
            outputs[target]=text; record['versions'][str(version)]={'path':str(target.relative_to(ROOT)),'sha256':sha256(text)}
    for target,text in outputs.items(): target.write_text(text)
    (COMMITTEE/'terra_profile_variants.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    for source,raw in originals.items():
        if source.read_text()!=raw: raise ValueError(f'Original changed: {source}')
    print('Created/verified 30 Literature profiles: six members × five fact-equivalent versions.')

if __name__=='__main__': main()
