import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from bench.jev.long_task_salvage import replay as r


class SalvageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR'], prefix='salvage-test-')
        self.root = Path(self.temp.name)
        self.used = self.root / 'used'; self.used.mkdir()
    def tearDown(self):
        self.temp.cleanup()

    def make_bundle(self):
        return {'root_prompt': 'root', 'root_reply': '```python\nFINAL(1)\n```',
                'leaves': {r.base.sha(b'evidence'): {'prompt': 'evidence', 'reply': '{"label":"unknown"}',
                            'reply_sha256': r.base.sha(b'{"label":"unknown"}')}}}

    def invoke(self, prompt):
        return subprocess.run([sys.executable, '-B', str(r.HERE / 'provider.py'), str(self.root/'bundle.json'), str(self.used)],
                              input=prompt, capture_output=True)

    def test_public_local_lookup_exact_bytes_and_no_unmatched_fallback(self):
        b = self.make_bundle(); r.base.save(self.root/'bundle.json', b)
        p = self.invoke(b'evidence')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, b'{"label":"unknown"}')
        self.assertEqual(self.invoke(b'evidence').returncode, 2)
        self.assertEqual(self.invoke(b'different evidence').returncode, 2)
        with self.assertRaisesRegex(r.base.Stop, 'consumption_incomplete'):
            r.consumed(b, self.used)
        self.assertEqual(self.invoke(b'root').returncode, 0)
        self.assertEqual(r.consumed(b, self.used)['exact_leaf_replies'], 1)

    def test_changed_response_hash_is_rejected_before_output(self):
        b = self.make_bundle(); b['leaves'][r.base.sha(b'evidence')]['reply'] = 'changed'
        r.base.save(self.root/'bundle.json', b)
        p = self.invoke(b'evidence')
        self.assertEqual(p.returncode, 2)
        self.assertEqual(p.stdout, b'')
        self.assertEqual(list(self.used.iterdir()), [])

    def test_exact_single_expression_replacement(self):
        code = 'x = llm("evidence")\nFINAL(' + r.OLD + ')'
        trace = ('=== root request begin request_id="x" model="m" request_chars=4 ===\nroot\n'
                 '=== root request end request_id="x" ===\n```python\nFINAL(0)\n```\n'
                 '```python\n' + code + '\n```\n=== repair code ===\n' + code +
                 '\n\n=== repair result outcome=failed ===\n')
        root, before, after = r.program_and_root(trace)
        self.assertEqual(root, 'root')
        self.assertEqual(before, code)
        self.assertEqual(after, code.replace(r.OLD, r.NEW))
        with self.assertRaises(r.base.Stop):
            r.program_and_root(trace.replace(r.OLD, 'unrelated()'))

    def test_extra_consumption_record_cannot_pass(self):
        b = self.make_bundle(); r.base.save(self.root/'bundle.json', b)
        self.invoke(b'root'); self.invoke(b'evidence')
        k = r.base.sha(b'extra')
        r.base.save(self.used/(k+'.json'), {'prompt_sha256': k, 'reply_sha256': 'a'*64, 'new_provider_calls':0})
        with self.assertRaisesRegex(r.base.Stop, 'consumption_incomplete'):
            r.consumed(b, self.used)


if __name__ == '__main__':
    unittest.main()
