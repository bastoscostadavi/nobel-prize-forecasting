import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_literature_profile_variants as profiles
import launch_literature_cohort as launcher
SPEC=importlib.util.spec_from_file_location('literature_merge_test',ROOT/'agent-data/literature/candidates/merge/consolidate.py')
merger=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(merger)

class LiteraturePreparationTests(unittest.TestCase):
    def test_profile_variants_preserve_facts_quotes_links_and_originals(self):
        manifest=json.loads((profiles.COMMITTEE/'terra_profile_variants.json').read_text())
        self.assertEqual(len(manifest['members']),6)
        for member in profiles.MEMBERS:
            source=profiles.COMMITTEE/member/'profile.md';raw=source.read_text()
            self.assertEqual(profiles.sha256(raw),manifest['members'][member]['source_sha256'])
            header,factual=profiles.parse_source(member,raw)
            texts=[]
            for version in range(1,6):
                text=profiles.render(member,header,factual,version);texts.append(text)
                target=profiles.COMMITTEE/member/f'profile_terra_v{version}.md'
                self.assertEqual(text,target.read_text())
                self.assertEqual(profiles.sha256(text),manifest['members'][member]['versions'][str(version)]['sha256'])
            self.assertEqual(len(set(texts)),5)

    def test_merge_requires_actual_second_draft_and_complete_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a=root/'codex.json';b=root/'claude.json';review=root/'review.json'
            rows=[{'candidate_id':f'C{i}','name':f'Writer {i}','achievement':f'Contribution {i}',
                   'field':'fiction; language X'} for i in range(8)]
            a.write_text(json.dumps({'category':'literature','candidates':rows}))
            with mock.patch.object(merger,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'Missing claude draft'):merger.merge(a,b,review)
                b.write_text(json.dumps({'category':'literature','candidates':copy.deepcopy(rows)}))
                with self.assertRaisesRegex(ValueError,'Review required'):merger.merge(a,b,review)
                decisions={merger.writer_key(r['name']):{'action':'keep','reason':'Reviewed synthetic literary case','achievement':r['achievement']} for r in rows}
                review.write_text(json.dumps({'writers':decisions}))
                result=merger.merge(a,b,review)
                self.assertEqual(result['candidate_count'],8)
                self.assertEqual(result['merge_summary']['shared_writers'],8)
                self.assertEqual(len(result['source_crosswalk']),16)
                self.assertTrue(all(len(c['credited_names'])==1 for c in result['candidates']))
                decisions.pop('writer-7');review.write_text(json.dumps({'writers':decisions}))
                with self.assertRaisesRegex(ValueError,'Incomplete source accounting'):merger.merge(a,b,review)

    def test_queue_waits_for_both_peace_cohorts_and_rejects_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);directory=root/'results/peace';directory.mkdir(parents=True)
            def write(arm,status,totals):
                (directory/f'{arm}_committee_progress.json').write_text(json.dumps({'status':status,'totals':totals}))
            with mock.patch.object(launcher,'ROOT',root):
                write('terra','complete',{'complete':25});write('claude','running',{'complete':20,'running':1,'pending':4})
                self.assertEqual(len(launcher.peace_ready()),1)
                write('claude','failed',{'complete':20})
                with self.assertRaisesRegex(ValueError,'Peace dispatcher failed'):launcher.peace_ready()
                write('claude','complete',{'complete':25})
                self.assertEqual(launcher.peace_ready(),[])

    def test_explicit_independent_list_is_frozen_without_claiming_consolidation(self):
        source=ROOT/'agent-data/literature/candidates/codex/candidates.json'
        snapshot=launcher.frozen_inputs('openai',source)
        self.assertEqual(len(snapshot),37)
        self.assertIn(str(source.relative_to(ROOT)),snapshot)
        self.assertNotIn('agent-data/literature/candidates/candidates.json',snapshot)
        self.assertEqual(json.loads(source.read_text())['candidate_count'],50)

    def test_missing_common_list_cannot_queue_or_launch(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(launcher,'SOURCE',Path(tmp)/'missing.json'):
            with self.assertRaisesRegex(ValueError,'Literature list is missing'):launcher.frozen_inputs('openai')

if __name__=='__main__':unittest.main()
