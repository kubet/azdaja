import copy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from bench.jev.angle_lab import native as n
from . import replay


class ReplayTests(unittest.TestCase):
    def test_strict_structural_comparison(self):
        replay.equal({'p':.3,'ok':True}, {'p':.3,'ok':True})
        for actual, expected in ((True,1),(1,True),([],{}),(float('nan'),.3),
                                 ({'a':1,'b':2},{'a':1}),([1],[1,2])):
            with self.assertRaises(ValueError): replay.equal(actual, expected)

    def test_retained_public_commands_are_bound_to_exact_inputs_and_reference(self):
        folder = replay.HERE/'results-20260917'
        load = lambda name:n.strict_loads((folder/name).read_bytes())
        public, commands = load('public-workflow.json'), load('public-commands.json')
        ps, ys = load('predictions.json'), load('sample500.json')
        replay.check_workflow(public, commands, ps, ys)
        mutations = [lambda p:p.update(new_provider_calls=1),
                     lambda p:p.update(unobserved_gold_loaded=1),
                     lambda p:p['evaluator'].update(corrected_total=8638.),
                     lambda p:p['events'][8].update(exit=0),
                     lambda p:p['events'][6].update(stdout='{}')]
        for mutate in mutations:
            changed = copy.deepcopy(public); mutate(changed)
            linked_commands = dict(commands, events=changed['events'])
            with self.assertRaises(ValueError):
                replay.check_workflow(changed, linked_commands, ps, ys)
        with self.assertRaises(ValueError):
            replay.check_workflow(public, commands, ps, list(reversed(ys)))

    def test_public_replay_refuses_existing_and_dangling_output_before_work(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as d:
            existing = Path(d)/'keep'; existing.write_bytes(b'unchanged')
            dangling = Path(d)/'link'; dangling.symlink_to(Path(d)/'absent')
            for path in (existing,dangling):
                p = subprocess.run([sys.executable,'-B','-m','bench.jev.audit_sampling.replay',
                    '--results','/not/a/result','--output',str(path)],capture_output=True,text=True)
                self.assertEqual(p.returncode,2)
                self.assertIn('new output file required',p.stderr)
            self.assertEqual(existing.read_bytes(),b'unchanged')
            self.assertTrue(dangling.is_symlink())

    def test_missing_or_altered_artifact_refuses_before_recomputation(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as d:
            folder = Path(d)
            with self.assertRaisesRegex(ValueError,'artifact file'): replay.verify(folder)
            (folder/'result.json').write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError,'retention.result.json'): replay.verify(folder)


if __name__ == '__main__': unittest.main()
