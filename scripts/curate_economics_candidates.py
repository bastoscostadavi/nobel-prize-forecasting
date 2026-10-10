"""Build the frozen, contribution-centred 50-entry Economics simulation pool.

Keep the Claude input untouched. Record every source entry as retained, merged,
or omitted. Codex's earlier research was not saved as a contemporaneous file;
the research supplement records the independently researched additions actually
used here, rather than inventing an original file or nomination count.
"""
import hashlib
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'agent-data/economics/candidates'
SOURCE = DIRECTORY / 'claude-opus-5-5/candidates.json'
SELECTED = [125, 60, 144, 13, 1, 24, 50, 102, 97, 156, 21, 127,
            30, 148, 66, 117, 25, 26, 2, 40, 103, 63, 3, 34, 98,
            72, 91, 94, 17, 100, 119, 9, 14, 52, 74, 22, 83, 48,
            112, 67, 77, 7, 89, 78, 68, 6, 49, 152, 136]
# Only genuinely overlapping contributions are collapsed. Some authors remain
# in several distinct entries: credit overlap is not contribution equivalence.
MERGED = {23: 125, 29: 125, 59: 7, 75: 3, 101: 13, 131: 148,
          142: 117, 138: 13, 121: 144, 32: 144, 107: 100,
          115: 50, 41: 22, 132: 9, 70: 79}
# e070 and e079 are both excluded: preserve their relationship in the audit,
# rather than implying they were incorporated into the active 50-entry pool.
MERGED.pop(70)

CLARIVATE = 'https://clarivate.com/citation-laureates/economics/'
SUPPLEMENT = {
    'schema_version': 1, 'category': 'economics', 'author': 'Codex',
    'compiled_on': '2026-10-07',
    'provenance': 'Research supplement to the earlier independent research in this conversation. The earlier broad draft was not saved to disk. This file records the additions and refinements used in the consolidation, not a reconstructed original draft.',
    'contributions': [
        {'key': 'digital-markets', 'contribution': 'Economic analysis of information technology, digital markets and network industries',
         'credited_names': ['Susan Athey', 'Hal R. Varian', 'Carl Shapiro', 'Michael L. Katz', 'Joseph Farrell'],
         'sources': [CLARIVATE], 'note': 'Athey and Varian are jointly named by Clarivate in 2026. Other names reflect the related information-goods and network-industry programme in the Claude input.'},
        {'key': 'evolutionary-economics', 'contribution': 'Evolutionary economics, organizational routines and economic dynamism',
         'credited_names': ['Sidney G. Winter'], 'historical_names': ['Richard R. Nelson (deceased 2025)'],
         'sources': [CLARIVATE, 'https://www.economic-evolution.net/index.php/weblog/newsarticle/333/'],
         'note': 'Distinct routines and evolutionary framework. Adjacent to the innovation-driven growth prize of 2025; Nelson cannot be included as a prospective laureate.'},
        {'key': 'weak-identification', 'contribution': 'Weak instruments and identification-robust inference',
         'credited_names': ['James H. Stock', 'Douglas Staiger', 'Donald W. K. Andrews', 'Motohiro Yogo', 'Marcelo J. Moreira'],
         'sources': ['https://www.nber.org/papers/t0151']},
        {'key': 'collateral-amplification', 'contribution': 'Collateral constraints, credit cycles and the financial accelerator',
         'credited_names': ['Nobuhiro Kiyotaki', 'John Moore', 'Mark Gertler', 'Simon Gilchrist'],
         'sources': ['https://www.nber.org/papers/w5083', 'https://www.nber.org/papers/w6455']},
        {'key': 'hank', 'contribution': 'Heterogeneous-agent New Keynesian models and monetary transmission',
         'credited_names': ['Greg Kaplan', 'Benjamin Moll', 'Giovanni L. Violante'],
         'sources': ['https://www.nber.org/papers/w21897'],
         'note': 'Corrects Gianluca Violante to Giovanni L. Violante. This is not the Krusell–Smith incomplete-markets entry.'},
        {'key': 'present-bias', 'contribution': 'Present bias, self-control and reference-dependent preferences',
         'credited_names': ['David Laibson', 'Matthew Rabin', 'George Loewenstein', "Ted O'Donoghue", 'Botond Koszegi'],
         'sources': ['https://scholar.harvard.edu/laibson/publications', 'https://eml.berkeley.edu/~rabin/'],
         'note': 'Corrects David I. Laibson to David Laibson. The three-person cap applies to final awards, not the alternative credit pool.'},
        {'key': 'digital-productivity', 'contribution': 'Information technology, digitization and the measurement of productivity',
         'credited_names': ['Erik Brynjolfsson', 'Lorin M. Hitt', 'Avi Goldfarb', 'Catherine E. Tucker'],
         'sources': ['https://www.aeaweb.org/articles?id=10.1257/jep.14.4.23'],
         'note': 'Productivity and digitization are kept separate from competition and pricing in information markets.'},
    ],
    'eligibility_sources': [
        'https://www.bu.edu/econ/?p=34458',
        'https://news.stanford.edu/stories/2026/03/obituary-john-roberts',
        'https://news.cornell.edu/stories/2026/05/erik-thorbecke-economist-global-impact-dies-97',
        'https://www.nobelprize.org/prizes/lists/all-prizes-in-economic-sciences/all/?gallery_style=page',
    ],
}

OVERRIDES = {
    60: {'discovery': SUPPLEMENT['contributions'][0]['contribution'],
         'credited_names': SUPPLEMENT['contributions'][0]['credited_names'], 'sources': [CLARIVATE]},
    144: {'discovery': 'Nominal rigidities, the New Keynesian framework and the modern theory of monetary policy',
          'credited_names': ['Michael Woodford', 'Jordi Gali', 'John B. Taylor', 'Guillermo A. Calvo', 'Mark Gertler', 'Lawrence J. Christiano', 'Martin Eichenbaum', 'Frank Smets'],
          'sources': [CLARIVATE], 'credit_note': 'Alternative credit configurations span nominal-rigidity models, the monetary-policy synthesis and quantitative implementations; a simulation must choose a coherent subset of at most three.'},
    13: {'discovery': SUPPLEMENT['contributions'][3]['contribution'],
         'credited_names': SUPPLEMENT['contributions'][3]['credited_names'], 'sources': SUPPLEMENT['contributions'][3]['sources']},
    125: {'discovery': 'Structural estimation of demand, competition and dynamic industry models',
          'credited_names': ['Steven T. Berry', 'James A. Levinsohn', 'Ariel Pakes', 'Timothy F. Bresnahan', 'Peter C. Reiss', 'C. Lanier Benkard', 'Jonathan Levin'],
          'sources': ['https://www.its.caltech.edu/~mshum/gradio/papers/BerryLevinsohnPakes1995.pdf'],
          'credit_note': 'BLP and related structural industrial organization are consolidated to prevent near-duplicate candidacies; choose recipients for the specific citation, not the whole pool.'},
    7: {'discovery': 'Bayesian persuasion and information design',
        'credited_names': ['Emir Kamenica', 'Matthew Gentzkow', 'Dirk Bergemann', 'Stephen Morris']},
    3: {'discovery': 'Agglomeration, cities, housing and the spatial distribution of economic activity',
        'credited_names': ['Edward L. Glaeser', 'Gilles Duranton', 'Diego Puga', 'Enrico Moretti', 'Joseph Gyourko']},
    50: {'discovery': 'Robust inference and semiparametric estimation in econometrics',
         'credited_names': ['Whitney K. Newey', 'Kenneth D. West', 'Donald W. K. Andrews', 'James L. Powell', 'Oliver B. Linton'],
         'sources': ['https://www.nber.org/papers/t0055', 'https://www.nber.org/papers/t0144']},
    156: {'credited_names': SUPPLEMENT['contributions'][2]['credited_names'], 'sources': SUPPLEMENT['contributions'][2]['sources']},
    100: {'discovery': SUPPLEMENT['contributions'][5]['contribution'],
          'credited_names': SUPPLEMENT['contributions'][5]['credited_names'], 'sources': SUPPLEMENT['contributions'][5]['sources']},
    22: {'discovery': 'Dynamic factor models, macroeconomic forecasting and forecast evaluation',
         'credited_names': ['James H. Stock', 'Mark W. Watson', 'Lucrezia Reichlin', 'Francis X. Diebold', 'Roberto S. Mariano', 'Kenneth D. West']},
    9: {'discovery': 'Experimental markets, behavioural game theory and strategic reasoning',
        'credited_names': ['Colin F. Camerer', 'Vincent P. Crawford', 'Charles A. Holt', 'Charles R. Plott', 'John H. Kagel']},
    117: {'discovery': 'Technology, trade shocks, tasks and changes in labour demand and wage inequality',
          'credited_names': ['David H. Autor', 'Lawrence F. Katz', 'David Dorn', 'Gordon H. Hanson'],
          'sources': ['https://www.nber.org/papers/w18054']},
    148: {'discovery': 'Long-run inequality, top incomes, wealth distribution and offshore wealth',
          'sources': ['https://www.nber.org/papers/w22945']},
    30: {'credited_names': ['Emmanuel Saez', 'Raj Chetty', 'Joel Slemrod', 'Stefanie Stantcheva'],
         'sources': ['https://www.nber.org/papers/w15012', 'https://www.nber.org/papers/w14399']},
    66: {'credited_names': ['Raj Chetty', 'Nathaniel Hendren', 'John N. Friedman', 'Lawrence F. Katz'],
         'sources': ['https://www.nber.org/papers/w21156']},
    26: {'credited_names': ['Eric A. Hanushek', 'Caroline M. Hoxby', 'Thomas J. Kane', 'Ludger Woessmann']},
    49: {'credited_names': SUPPLEMENT['contributions'][4]['credited_names'], 'sources': SUPPLEMENT['contributions'][4]['sources'],
         'conflict_flags': ['Giovanni Violante is a documented co-author of committee secretary Per Krusell. HANK builds on the heterogeneous-agent literature; the committee-centred Krusell–Smith entry is excluded.']},
    63: {'discovery': 'Trade policy, special-interest politics and political-economy models of protection',
         'credit_note': 'Narrowed to political economy of trade; innovation-driven growth was honoured in 2025.',
         'sources': ['https://www.nber.org/papers/w4149']},
    72: {'credited_names': ['Andrei Shleifer', 'Rafael La Porta', 'Florencio Lopez-de-Silanes', 'Robert W. Vishny'],
         'overlap_review': 'Adjacent to the 2024 institutions prize; the distinct legal-origins/financial-development programme must justify a separate citation.'},
    136: {'discovery': SUPPLEMENT['contributions'][6]['contribution'],
          'credited_names': SUPPLEMENT['contributions'][6]['credited_names'], 'sources': SUPPLEMENT['contributions'][6]['sources']},
    77: {'sources': ['https://www.nber.org/papers/w23564'],
         'overlap_review': 'Adjacent to the 2021 causal-inference prize; distinguish machine-learning methods and heterogeneous effects from already honoured identification results.'},
    83: {'sources': ['https://www.nber.org/papers/w13290', 'https://www.nber.org/papers/w13018'],
         'conflict_flags': ['Peter Klenow is a documented co-author of committee member Timo Boppart.']},
    152: {'sources': ['https://www.nber.org/papers/w21633']},
}

def normalized(name):
    return ''.join(c for c in unicodedata.normalize('NFKD', name).casefold() if c.isalnum())

def main():
    original = SOURCE.read_bytes()
    data = json.loads(original)
    entries = {int(c['candidate_id'][1:]): c for c in data['candidates']}
    assert len(SELECTED) == len(set(SELECTED)) == 49
    assert set(MERGED).isdisjoint(SELECTED) and set(MERGED.values()) <= set(SELECTED)
    candidates = []
    for number in SELECTED:
        source = entries[number]
        linked = [number, *sorted(k for k, v in MERGED.items() if v == number)]
        c = {'discovery': source['contribution'], 'subfield': source['subfield'],
             'credited_names': source['nominees'], 'historical_and_additional_names': source['other_names'],
             'overlap_review': source['overlap_review'], 'conflict_flags': [],
             'source_claude_ids': [entries[n]['candidate_id'] for n in linked],
             'sources': [], 'credit_note': 'The credited pool is provisional. Only one to three people may receive an award; additional names in the original draft remain available in the provenance record.'}
        c.update(OVERRIDES.get(number, {}))
        candidates.append(c)
    winter = SUPPLEMENT['contributions'][1]
    candidates.append({'discovery': winter['contribution'], 'subfield': 'Evolutionary and organisational economics',
                       'credited_names': winter['credited_names'], 'historical_and_additional_names': winter['historical_names'],
                       'overlap_review': 'Adjacent to the 2025 innovation-driven growth prize; organizational routines and evolutionary theory require a distinct citation.',
                       'conflict_flags': [], 'source_claude_ids': [], 'sources': winter['sources'],
                       'credit_note': winter['note'], 'source_codex_key': winter['key']})
    candidates.sort(key=lambda c: c['discovery'].casefold())
    for index, c in enumerate(candidates, 1):
        c['candidate_id'] = f'E{index:03d}'
    committee = {normalized(p.read_text().splitlines()[0][2:]) for p in (ROOT/'agent-data/economics/committee').glob('*/profile.md')}
    dead = {normalized(n) for n in ['Jonathan Eaton', 'John Roberts', 'D. John Roberts', 'Patrick Bajari', 'Richard R. Nelson', 'Erik Thorbecke', 'David Schmeidler', 'Halbert White']}
    for c in candidates:
        assert c['credited_names'] and len(c['credited_names']) == len(set(c['credited_names']))
        assert not {normalized(n) for n in c['credited_names']} & (committee | dead)
        assert not any('(Nobel' in n or '(deceased' in n for n in c['credited_names'])
    assert len(candidates) == 50
    used = {sid: c['candidate_id'] for c in candidates for sid in c['source_claude_ids']}
    exclusions = []
    strong = {15, 19, 55, 70, 79, 85, 108, 132, 154, 155}
    for number, c in entries.items():
        if c['candidate_id'] in used:
            status = 'retained' if number in SELECTED else 'merged'
            reason = 'Included in the contribution-centred simulation pool.' if status == 'retained' else 'Consolidated with a related contribution to avoid overlapping candidacies.'
        else:
            status = 'omitted'
            reason = 'Outside the 50-entry cap after balancing field coverage, foundational contribution, maturity and attribution. Omission is an editorial scope decision, not a probability or ineligibility finding.'
            if number in (55, 155): reason = 'Committee-centred foundational credit (Per Krusell or Per Stromberg); omitted rather than removing a central contributor from the prospective award.'
            elif number in strong: reason = 'Strong overlap with an earlier prize; deprioritized under the 50-entry cap. Distinct later advances may still be deserving.'
            elif number in (47, 137, 153): reason = 'Growth and innovation are adjacent to the 2018 and 2025 prizes; omitted under the coverage cap.'
        exclusions.append({'source_candidate_id': c['candidate_id'], 'contribution': c['contribution'],
                           'status': status, 'canonical_candidate_id': used.get(c['candidate_id']), 'reason': reason})
    supplement_path = DIRECTORY/'codex/research_supplement.json'
    supplement_path.parent.mkdir(parents=True, exist_ok=True)
    supplement_text = json.dumps(SUPPLEMENT, ensure_ascii=False, indent=2)+'\n'
    supplement_path.write_text(supplement_text)
    result = {'schema_version': 1, 'category': 'economics', 'year': 2026, 'list_id': 'economics-2026-consolidated-50-v1',
              'candidate_count': 50, 'candidate_order': 'alphabetical_by_contribution_not_rank', 'compiled_on': '2026-10-07',
              'method': 'Editorial consolidation of the 156-entry Claude draft and independent Codex research. Fifty contribution-centred candidates, not fifty individuals. Alternative credited pools can exceed three; any final award has at most three unique living laureates. Historical contributors and earlier laureates are not ballot credit choices. Current committee members and committee-centred achievements are excluded. The list is a broad forecasting pool, not a ranking or official nomination record.',
              'inputs': {'claude': {'path': str(SOURCE.relative_to(ROOT)), 'sha256': hashlib.sha256(original).hexdigest(), 'candidate_count': 156},
                         'codex': {'path': str(supplement_path.relative_to(ROOT)), 'sha256': hashlib.sha256(supplement_text.encode()).hexdigest(), 'source_type': 'independent research supplement; original broad conversation draft was not saved'}},
              'eligibility_note': 'The Claude draft reports living-status checks on 2026-10-03, with unmatched people assumed living. Primary obituaries and 2026 Clarivate coverage were checked for relevant additions/corrections. This is not a comprehensive primary-source certification of every recipient. See research_supplement.json and source eligibility notes.',
              'candidates': candidates}
    (DIRECTORY/'candidates.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    audit = {'schema_version': 1, 'input_sha256': hashlib.sha256(original).hexdigest(),
             'output_candidate_count': 50, 'source_decisions': exclusions,
             'codex_additions': [{'canonical_candidate_id': c['candidate_id'], 'contribution': c['discovery']} for c in candidates if not c['source_claude_ids']],
             'credit_corrections': ['Gianluca Violante corrected to Giovanni L. Violante.', 'David I. Laibson corrected to David Laibson.', 'John Roberts, Jonathan Eaton and Richard Nelson are historical contributors, not eligible credit choices.']}
    (DIRECTORY/'consolidation_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2)+'\n')
    lines = ['# Economics candidates for 2026', '', 'The simulation pool contains **50 contributions**, ordered alphabetically. Names are alternative credit pools, not a proposed joint award: each simulated prize may name at most three people in total.', '',
             'The 156-entry Claude draft is preserved. The merged pool incorporates Codex research, groups related contributions, removes committee-centred entries and deprioritizes strong overlap with previous prizes. Every Claude entry has a retained, merged or omitted decision in `consolidation_audit.json`. The earlier Codex broad draft was not saved to disk; the research supplement records the additions used here.', '',
             'The candidate research began on 3 October and was updated for consolidation on 7 October 2026. Source metadata and overlap caveats are retained in `candidates.json`; the blinded ballots contain only contribution, subfield and prospective credited names. Historical names and earlier laureates do not enter the credit pool.', '',
             '| ID | Contribution | Prospective credit pool |', '|---|---|---|']
    lines += [f"| {c['candidate_id']} | {c['discovery']} | {'; '.join(c['credited_names'])} |" for c in candidates]
    lines += ['', 'The 2026 Clarivate Economics selections add the Athey–Varian information-technology pairing and Sidney Winter, and reinforce the monetary-policy entry. [Clarivate](https://clarivate.com/citation-laureates/economics/). Prior-prize overlap is assessed against the [Nobel Economics prize record](https://www.nobelprize.org/prizes/lists/all-prizes-in-economic-sciences/all/?gallery_style=page).', '']
    (DIRECTORY/'README.md').write_text('\n'.join(lines))
    assert SOURCE.read_bytes() == original
    print('Saved 50 candidates and a disposition for all 156 Claude entries; source untouched.')

if __name__ == '__main__':
    main()
