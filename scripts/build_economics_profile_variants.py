"""Build one neutral baseline plus four factual Economics profile variants.

Preserve the source profiles. Rotate factual sections, change headings and
reorder bullet blocks without adding preferences or changing factual content.
Persona instructions and speculation about personal voting are removed
uniformly before the five versions are constructed.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COMMITTEE = ROOT / 'agent-data/economics/committee'
KEYS = ('Biography', 'Research / intellectual footprint', 'Public statements and values', 'Connections', 'Uncertainty')
LAYOUTS = {1: (0, 1, 2, 3, 4), 2: (1, 0, 3, 2, 4), 3: (0, 3, 2, 1, 4),
           4: (2, 1, 0, 4, 3), 5: (1, 2, 3, 0, 4)}
HEADINGS = {
    1: ('Biography', 'Research record', 'Attributed public statements', 'Connections', 'Uncertainty'),
    2: ('Education and career', 'Published research', 'Statements on record', 'Professional relationships', 'Source limitations'),
    3: ('Career background', 'Research contributions', 'Documented statements', 'Affiliations and collaborators', 'Evidence caveats'),
    4: ('Biographical record', 'Research and methods', 'Public statements and attribution', 'Institutional and research ties', 'Unresolved details'),
    5: ('Career and appointments', 'Intellectual work', 'Attributed statements', 'Documented connections', 'Limitations of the record'),
}
NOTE = 'Factual profile for the simulated committee. Attributed statements and institutional speeches do not establish personal voting preferences. All eleven listed participants vote in this experiment by modeling assumption; actual voting rights are not inferred from their titles.'

def tokens(text):
    return Counter(re.sub(r'(?m)^- ', '', text).split())

def blocks(body):
    if body.startswith('- '):
        return re.split(r'\n(?=- )', body)
    return body.split('\n\n')

def parse(raw):
    split = re.split(r'^## (.+)\n', raw, flags=re.M)
    sections = dict(zip(split[1::2], split[2::2]))
    if set(sections) != set(KEYS) | {'Persona'}:
        raise ValueError('Unexpected section inventory')
    removals = [sections['Persona'].strip()]
    factual = {}
    for key in KEYS:
        retained = []
        for block in blocks(sections[key].strip()):
            if re.search(r'\bPersona\b|presumably co-opted', block, re.I):
                removals.append(block)
            else:
                retained.append(block)
        factual[key] = '\n'.join(retained) if sections[key].strip().startswith('- ') else '\n\n'.join(retained)
    # Preserve institutional-speech limitations after removing the inferred
    # persona explanations that originally contained them.
    factual['Uncertainty'] += '\n- Presentation speeches delivered for the Academy may reflect collective drafting and do not establish the speaker\'s private prize preferences.'
    return split[0].strip(), factual, removals

def render(header, factual, version):
    body = {}
    for index, key in enumerate(KEYS):
        items = blocks(factual[key])
        if version in (2, 5) and key in ('Research / intellectual footprint', 'Connections'):
            items = list(reversed(items))
        if version in (3, 4) and len(items) > 1:
            items = items[1:] + items[:1]
        body[index] = ('\n' if factual[key].startswith('- ') else '\n\n').join(items)
    if tokens('\n'.join(body.values())) != tokens('\n'.join(factual.values())):
        raise ValueError('Retained facts changed')
    first, rest = header.split('\n', 1)
    text = first+'\n\n'+NOTE+'\n'+rest+'\n\n'
    text += '\n\n'.join(f'## {HEADINGS[version][i]}\n\n{body[i]}' for i in LAYOUTS[version])+'\n'
    baseline = header+'\n'+'\n'.join(factual.values())
    for pattern in (r'https?://\S+', r'"([^"\n]*)"'):
        if Counter(re.findall(pattern, text)) != Counter(re.findall(pattern, baseline)):
            raise ValueError('Source link or quotation inventory changed')
    if re.search(r'(?im)^## Persona$|\bYou are\b|\bpersona\b', text):
        raise ValueError('Persona instructions remain')
    return text

def main():
    sources = sorted(COMMITTEE.glob('*/profile.md'))
    assert len(sources) == 11
    manifest = {'schema_version': 1, 'profile_versions': 5,
                'policy': 'One factual baseline and four editorial variants. Uniformly omit Persona instructions and speculative private preferences; identical retained facts, links and quotation inventories in all five versions.',
                'voting_assumption': 'All eleven listed participants vote, including the secretary and co-opted participants; majority six.', 'members': {}}
    outputs = {}
    originals = {}
    for source in sources:
        raw = source.read_text(); originals[source] = raw
        header, factual, removed = parse(raw)
        record = {'source_path': str(source.relative_to(ROOT)), 'source_sha256': hashlib.sha256(raw.encode()).hexdigest(),
                  'uniformly_omitted_blocks': removed, 'versions': {}}
        manifest['members'][source.parent.name] = record
        for version in range(1, 6):
            target = source.with_name(f'profile_terra_v{version}.md')
            text = render(header, factual, version)
            if target.exists() and target.read_text() != text:
                raise ValueError(f'Refusing to replace existing different profile: {target}')
            outputs[target] = text
            record['versions'][str(version)] = {'path': str(target.relative_to(ROOT)), 'sha256': hashlib.sha256(text.encode()).hexdigest()}
    for path, text in outputs.items(): path.write_text(text)
    (COMMITTEE/'terra_profile_variants.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    assert all(p.read_text() == text for p, text in originals.items())
    print('Verified 55 factual profiles: 11 participants × 5 versions. Original profiles preserved.')

if __name__ == '__main__': main()
