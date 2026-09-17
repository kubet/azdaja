"""Actual public commands after experiment cleanup. No provider calls permitted."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SCRATCH = Path(os.environ['JCODE_SCRATCH_DIR'])
BINARY = SCRATCH/'jev-ingest-native-e75d836-azdaja'
EXPECTED_BINARY = '13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    assert sha(BINARY.read_bytes()) == EXPECTED_BINARY
    retained = json.loads((OUT/'RETENTION.json').read_text())
    for item in retained['files']:
        assert sha((ROOT/item['path']).read_bytes()) == item['sha256']
    checks = []
    with tempfile.TemporaryDirectory(prefix='jev-post-cleanup-',dir=SCRATCH) as folder:
        work = Path(folder)
        env = dict(os.environ)
        for key in list(env):
            if any(s in key.upper() for s in ('API_KEY','APIKEY','TOKEN','SECRET','PASSWORD','CREDENTIAL','AUTHORIZATION')):
                env.pop(key)
        env.update(PYTHONDONTWRITEBYTECODE='1', AZDAJA_HOME=str(work/'state'),
                   JCODE_HOME=str(work/'empty-jcode'), AZDAJA_CONFIG=str(work/'config.toml'),
                   AZDAJA_MODEL_TRACE=str(work/'no-model-trace.jsonl'))
        (work/'config.toml').write_text('sub_llm_cmd="/usr/bin/false"\n[judge]\nenabled=false\n')

        def command(name, argv, code=None, expected=0):
            started=time.monotonic()
            p=subprocess.run(argv,input=code,cwd=ROOT,env=env,capture_output=True,text=True,timeout=30)
            assert p.returncode==expected,(name,p.returncode,p.stderr[:300])
            checks.append({'name':name,'exit':p.returncode,'seconds':time.monotonic()-started,
                           'stdout_sha256':sha(p.stdout.encode()),'stderr_sha256':sha(p.stderr.encode())})
            return p

        commands=[('row645', ['bench.jev.row645_labels.audit'], ROOT/'bench/jev/row645_labels/result.json'),
                  ('combined', ['bench.jev.measurement_followthrough.report','--continuation',str(OUT/'native-20260917')], OUT/'combined-replay.json'),
                  ('final-audit', ['bench.jev.measurement_audit'], OUT/'final-acceptance.json')]
        for name,args,reference in commands:
            destination=work/(name+'.json')
            argv=[sys.executable,'-B','-m',*args,'--output',str(destination)]
            command(name+'-public-cli',argv)
            assert json.loads(destination.read_bytes()) == json.loads(reference.read_bytes())
            before=destination.read_bytes()
            p=command(name+'-existing-output-refused',argv,expected=1)
            assert 'FileExistsError' in p.stderr and destination.read_bytes()==before
            link=work/(name+'-dangling');target=work/(name+'-absent');link.symlink_to(target)
            argv[-1]=str(link)
            p=command(name+'-dangling-output-refused',argv,expected=1)
            assert 'FileExistsError' in p.stderr and not target.exists()

        # The real public admission command must hit the consumed seal before
        # constructing any campaign, resolving a credential or starting a cell.
        # Both private credential/provider profiles are absent as a second guard.
        for module,base in [('bench.jev.measurement_v2.run',ROOT/'bench/jev/measurement_v2'),
                            ('bench.jev.measurement_followthrough.run',OUT.parent)]:
            marker=base/'FROZEN.started';before=marker.read_bytes()
            destination=work/(base.name+'-forbidden-run')
            p=command(base.name+'-consumed-seal-refused',
                      [sys.executable,'-B','-m',module,'--live','--acknowledge-provider-calls',
                       '--azdaja',str(BINARY),'--credential-state-root',str(work/'absent-credentials'),
                       '--output',str(destination)], expected=1)
            assert 'FileExistsError' in p.stderr and 'FROZEN.started' in p.stderr
            assert not destination.exists() and marker.read_bytes()==before
        assert not (work/'state').exists() and not (work/'empty-jcode').exists()

        # Exercise the real persistent evaluator on all300 retained outcomes,
        # with exact raw inputs and an independently written reduction.
        caps=json.loads(command('native-static-caps',[str(BINARY),'doctor','--caps']).stdout)
        assert 'judge_many' in json.dumps(caps)
        ledger=json.loads((OUT/'combined-replay.json').read_text())['ledger']
        raw=json.dumps(ledger,ensure_ascii=False,separators=(',',':')).encode()
        payload=work/'ledger.json';payload.write_bytes(raw)
        sid=command('native-start',[str(BINARY),'start']).stdout.strip()
        try:
            command('native-load-retained-ledger',[str(BINARY),'load',sid,str(payload),'retained_ledger'])
            program='''rows = json.loads(retained_ledger)
reduced = {}
for lane in ["flat", "verifier"]:
    reduced[lane] = {}
    for arm in ["typed", "generative"]:
        total = 0
        observed = 0
        correct = 0
        false_support = 0
        false_flags = 0
        for row in rows:
            if row["lane"] == lane:
                total += 1
                if row[arm] is not None:
                    observed += 1
                    if row[arm] == row["expected"]:
                        correct += 1
                    if lane == "verifier" and row[arm] == "yes" and row["expected"] == "no":
                        false_support += 1
                    if lane == "verifier" and row[arm] == "no" and row["expected"] == "yes":
                        false_flags += 1
        reduced[lane][arm] = {"total":total,"observed":observed,"correct":correct,"false_support":false_support,"false_flags":false_flags}
FINAL({"sha256":sha256(retained_ledger),"reduced":reduced,"judge_attempts":judge_stats()["attempts"]})
'''
            command('native-independent-reduction-exec',[str(BINARY),'exec',sid],program)
            result=json.loads(command('native-independent-reduction-final',[str(BINARY),'final',sid]).stdout)
            assert result['sha256']==sha(raw) and result['judge_attempts']==0
            expected={'flat':{'typed':{'total':100,'observed':75,'correct':67,'false_support':0,'false_flags':0},'generative':{'total':100,'observed':100,'correct':89,'false_support':0,'false_flags':0}},
                      'verifier':{'typed':{'total':200,'observed':200,'correct':179,'false_support':15,'false_flags':6},'generative':{'total':200,'observed':200,'correct':180,'false_support':14,'false_flags':6}}}
            assert result['reduced']==expected
            command('native-persistent-reentry-exec',[str(BINARY),'exec',sid],'FINAL(reduced)\n')
            again=json.loads(command('native-persistent-reentry-final',[str(BINARY),'final',sid]).stdout)
            assert again==expected
        finally:
            command('native-kill',[str(BINARY),'kill',sid])
        assert not (work/'no-model-trace.jsonl').exists()
        assert not (work/'empty-jcode').exists()
    for item in retained['files']:
        assert sha((ROOT/item['path']).read_bytes()) == item['sha256']
    receipt={'schema_version':1,'schema':'azdaja.measurement_post_cleanup_public_acceptance.v1',
             'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'status':'passed','commands':checks,'new_provider_calls':0,'judge_attempts':0,
             'model_trace_created':False,'retained_artifacts_unchanged':len(retained['files']),
             'native_reduction':expected,'all_semantic_quality_bars_passed':False,
             'flat100_completed_judgments_achieved':False,
             'limits':['This validates public delivery and retained accounting, not new semantic evidence.',
                       'The completed-judgment flat100target remains blocked by the original rejected response.']}
    output=OUT/'post-cleanup-public-acceptance.json'
    with output.open('xb') as f:f.write(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()+b'\n')
    print(json.dumps({'status':'passed','public_commands':len(checks),'new_provider_calls':0,
                      'native_reduction_matched':True,'retained_artifacts_unchanged':len(retained['files'])}))


if __name__=='__main__':main()
