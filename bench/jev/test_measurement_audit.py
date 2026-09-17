import copy
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from bench.jev import measurement_audit as a
from bench.jev.measurement_followthrough import evidence as e
from bench.jev.measurement_followthrough.run import HERE


class FinalMeasurementTests(unittest.TestCase):
    def test_actual_full_replay_is_negative_but_consistent(self):
        result=a.verify()
        self.assertEqual(result['status'],'passed')
        self.assertFalse(result['all_quality_bars_passed'])
        self.assertEqual(result['checks']['cumulative_accounting']['typed_calls_started'],12)
        self.assertEqual(result['checks']['flat_unjudged_typed_cases'],25)

    def test_changed_bar_cannot_become_a_rehashed_win(self):
        result=e.load(HERE/'results/combined-replay.json');forged=copy.deepcopy(result)
        forged['lanes']['verifier']['quality_bar_passed']=True
        with self.assertRaisesRegex(ValueError,'retained summary does not replay'):a.verify_summary(result,forged)

    def test_missing_completed_call_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as root:
            copied=Path(root)/'run';copied.mkdir()
            for p in (HERE/'results/native-20260917').iterdir():
                if p.is_file():shutil.copyfile(p,copied/p.name)
            path=copied/'receipt.json';receipt=e.load(path)
            receipt['calls'].pop(0);path.write_bytes(a.n.canonical(receipt))
            with self.assertRaisesRegex(ValueError,'completed call evidence'):e.read_run(copied,e.CONTINUATION_ORDER)

    def test_public_audit_fresh_output_and_refusal_paths(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as root:
            output=Path(root)/'out.json';base=[sys.executable,'-B','-m','bench.jev.measurement_audit','--output']
            first=subprocess.run(base+[str(output)],capture_output=True,text=True,timeout=15)
            self.assertEqual(first.returncode,0,first.stderr)
            before=output.read_bytes()
            again=subprocess.run(base+[str(output)],capture_output=True,text=True,timeout=15)
            self.assertNotEqual(again.returncode,0);self.assertEqual(output.read_bytes(),before)
            link=Path(root)/'link';target=Path(root)/'missing';link.symlink_to(target)
            again=subprocess.run(base+[str(link)],capture_output=True,text=True,timeout=15)
            self.assertNotEqual(again.returncode,0);self.assertFalse(target.exists())


if __name__=='__main__':unittest.main()
