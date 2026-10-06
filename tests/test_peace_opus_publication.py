"""Check Opus publication auditing without making any model requests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import summarize_peace_oneshot_claude as publication


class OpusPublicationTests(unittest.TestCase):
    def runtime(self, *, model='claude-opus-5-5', tool=False, changed=False):
        value = {'achievement': 'Civilian relief', 'laureates': ["Sudan's Emergency Response Rooms"],
                 'rationale': 'Protecting civilians'}
        record = dict(value)
        if changed:
            value['laureates'] = ['Another organization']
        events = [
            {'type': 'system', 'subtype': 'init', 'model': model, 'session_id': 'independent-session', 'tools': [], 'mcp_servers': []},
            {'type': 'assistant', 'message': {'model': model, 'content': [{'type': 'text', 'text': json.dumps(value)}]}},
            {'type': 'result', 'subtype': 'success', 'is_error': False, 'result': json.dumps(value), 'modelUsage': {model: {}}},
        ]
        if tool:
            events.append({'type': 'other', 'nested': {'type': 'tool_result', 'content': 'external'}})
        return record, '\n'.join(json.dumps(e) for e in events)

    def test_audit_accepts_exact_runtime_answer_and_model(self):
        record, raw = self.runtime()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'runtime.jsonl'; path.write_text(raw)
            session, models = publication.audit(path, record)
        self.assertEqual(session, 'independent-session')
        self.assertEqual(models, {'claude-opus-5-5'})

    def test_changed_answers_model_drift_and_nested_tools_are_rejected(self):
        for options in ({'changed': True}, {'model': 'claude-sonnet-5-5'}, {'tool': True}):
            record, raw = self.runtime(**options)
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'runtime.jsonl'; path.write_text(raw)
                with self.assertRaises((ValueError, RuntimeError)):
                    publication.audit(path, record)


if __name__ == '__main__':
    unittest.main()
