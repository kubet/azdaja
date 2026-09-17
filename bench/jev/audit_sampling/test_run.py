"""Offline public-path and independently derived sampling checks."""
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from . import run
from .estimator import estimate


class SamplingRunTests(unittest.TestCase):
    def test_fixed_sampler_is_uniform_without_replacement_not_gold_ranked(self):
        seed=int.from_bytes(hashlib.sha256(b'audit-sampling-v1|100|0').digest(),'big')
        expected=random.Random(seed).sample(range(1000),100)
        self.assertEqual(run.selected_indices(100,0,1000),expected)
        self.assertEqual(len(set(expected)),100)
        self.assertNotEqual(run.selected_indices(100,1,1000),expected)

    def test_oracle_size_satisfies_variance_and_is_minimal(self):
        for N in (10,100,17469):
            for v in (0,.01,.25,1):
                for target in (1,50,100):
                    k=run.required_labels(N,v,target)
                    self.assertLessEqual(N*N*(1-k/N)*v/k,target*target+1e-8)
                    if k>1:self.assertGreater(N*N*(1-(k-1)/N)*v/(k-1),target*target-1e-8)

    def test_fast_simulation_agrees_with_independent_public_estimator(self):
        rows=[{'id':str(i),'p_ham':p,'gold_ham':y} for i,(p,y) in enumerate(
            ((.1,False),(.9,True),(.8,False),(.3,True),(.2,False),(.7,True)))]
        with patch.object(run,'SIZES',(2,3)),patch.object(run,'REPLICATES',4):
            population,summaries,replicates=run.simulate(rows,time.monotonic()+10)
        for row in replicates:
            indices=run.selected_indices(row['size'],row['replicate'],len(rows))
            reference=estimate([{'id':r['id'],'p':r['p_ham']} for r in rows],
                [{'id':rows[i]['id'],'label':rows[i]['gold_ham']} for i in indices])
            self.assertAlmostEqual(row['arms']['raw_p']['estimate'],reference['corrected_total'])
            self.assertAlmostEqual(row['arms']['raw_p']['standard_error'],reference['estimated_standard_error'])
            self.assertAlmostEqual(row['arms']['uniform_only']['estimate'],reference['uniform_total'])
        self.assertEqual(len(replicates),8)
        self.assertFalse(summaries['2']['raw_p']['interval_is_finite_sample_guarantee'])

    def test_deadline_does_not_return_partial_win(self):
        rows=[{'id':str(i),'p_ham':.3,'gold_ham':bool(i%2)} for i in range(100)]
        with self.assertRaisesRegex(ValueError,'deadline'):
            run.simulate(rows,time.monotonic()-1)

    def test_public_cli_refuses_existing_and_dangling_outputs(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as d:
            existing=Path(d)/'exists';existing.mkdir()
            dangling=Path(d)/'dangling';dangling.symlink_to(Path(d)/'missing')
            for path in (existing,dangling):
                p=subprocess.run([sys.executable,'-B','-m','bench.jev.audit_sampling.run',
                    '--output',str(path),'--azdaja','/does/not/exist'],capture_output=True,text=True)
                self.assertEqual(p.returncode,2)
                self.assertIn('new output directory required',p.stderr)
            self.assertTrue(dangling.is_symlink())

    def test_actual_retained_binary_public_lifecycle_and_invalid_reentry(self):
        binary=Path(os.environ['AZDAJA_BINARY'])
        ps=[{'id':'a','p':.9},{'id':'b','p':.2},{'id':'c','p':.8}]
        ys=[{'id':'c','label':False},{'id':'a','label':True}]
        receipt=run.public_workflow(binary,ps,ys,Path(os.environ['JCODE_SCRATCH_DIR']))
        self.assertEqual(receipt['status'],'passed')
        self.assertEqual(receipt['new_provider_calls'],0)
        self.assertTrue(receipt['trace_empty'])
        self.assertTrue(receipt['changed_id_rejected'])
        self.assertEqual(receipt['unobserved_gold_loaded'],0)
        self.assertEqual(receipt['cleanup_exit'],0)


if __name__=='__main__':unittest.main()
