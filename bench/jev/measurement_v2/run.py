"""One-shot native measurement. Import and default command never call providers."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from bench.jev.angle_lab import native as n

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BINARY_SHA = '13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32'


def packs():
    rows = n.strict_loads((HERE / 'fixtures/packs.json').read_bytes())
    if not isinstance(rows, list) or not 1 <= len(rows) <= 12:
        raise n.Stop('pack_count')
    names, ids = set(), set()
    counts = {'flat': 0, 'verifier': 0}
    for row in rows:
        if set(row) != {'name', 'lane', 'pack'} or row['lane'] not in counts:
            raise n.Stop('pack_manifest_shape')
        if row['name'] in names or not n.IDENTIFIER.fullmatch(row['name']):
            raise n.Stop('pack_name')
        names.add(row['name'])
        request = n.inspect_pack(row['pack'])
        if ids.intersection(request['questions']):
            raise n.Stop('duplicate_question')
        ids.update(request['questions'])
        counts[row['lane']] += len(request['questions'])
        kind = 'choice' if row['lane'] == 'flat' else 'noul'
        if any(q['type'] != kind for q in request['questions'].values()):
            raise n.Stop('question_kind')
    if counts != {'flat': 100, 'verifier': 200}:
        raise n.Stop('panel_counts')
    return rows


def inventory(binary):
    if n.sha(binary.read_bytes()) != BINARY_SHA:
        raise n.Stop('binary_identity')
    files = [p for p in HERE.rglob('*') if p.is_file() and p.suffix in ('.py', '.json', '.md')
             and 'results' not in p.relative_to(HERE).parts and p.name != 'FROZEN.json']
    files += [ROOT / 'bench/jev/angle_lab/native.py',
              ROOT / 'bench/jev/span_selection/kernel.py', ROOT / 'bench/jev/span_selection/run.py']
    files.append(binary)
    return {str(p.resolve()): n.sha(p.read_bytes()) for p in sorted(set(files))}


class Measurement(n.Campaign):
    @n.terminal
    def typed(self, name, pack):
        if self.receipt['typed_calls_started'] >= 12:
            raise n.Stop('preregistered_typed_cap')
        return super().typed(name, pack)

    def checkpoint(self):
        self.receipt['experiment_schema'] = 'azdaja.jev_measurement_v2.v1'
        self.receipt['official_rah_submission'] = False
        self.receipt['automatic_approval_authorized'] = False
        super().checkpoint()


def exercise(campaign, rows, live):
    campaign.receipt['benchmark_rows'] = []
    campaign.start()
    for ordinal, row in enumerate(rows):
        pack = row['pack']
        if not live:
            campaign.load('check_payload', pack)
            observed = n.strict_loads(campaign.cell(row['name'] + '-preflight',
                'p = json.loads(check_payload)\nFINAL({"sha256":sha256(check_payload),"ids":list(p["questions"].keys()),"attempts":judge_stats()["attempts"]})\n'))
            if observed != {'sha256': n.sha(n.canonical(pack)), 'ids': sorted(pack['questions']), 'attempts': 0}:
                raise n.Stop('native_pack_custody')
            continue
        arms = ('typed', 'generative') if ordinal % 2 == 0 else ('generative', 'typed')
        for arm in arms:
            name = row['name'] + '-' + arm
            entry = {'schema_version': 1, 'fixture': row['name'], 'lane': row['lane'],
                     'arm': arm, 'status': 'attempted', 'question_ids': sorted(pack['questions']),
                     'input_sha256': n.sha(n.canonical(pack)), 'binary_sha256': BINARY_SHA,
                     'model': n.MODEL if arm == 'typed' else n.GENERATOR,
                     'automatic_approval_authorized': False, 'official_rah_submission': False}
            campaign.receipt['benchmark_rows'].append(entry)
            campaign.checkpoint()
            start = time.monotonic()
            try:
                result = campaign.typed(name, pack) if arm == 'typed' else campaign.generate(name, pack)
                entry.update(status='completed', response_sha256=n.sha(n.canonical(result)),
                             whole_operation_seconds=time.monotonic()-start,
                             native_call=campaign.receipt['calls'][-1])
            except BaseException:
                entry.update(status='stopped', whole_operation_seconds=time.monotonic()-start)
                campaign.checkpoint()
                raise
            campaign.checkpoint()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--azdaja', type=Path)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--seal', action='store_true')
    mode.add_argument('--offline', action='store_true')
    mode.add_argument('--live', action='store_true')
    ap.add_argument('--acknowledge-provider-calls', action='store_true')
    ap.add_argument('--credential-state-root', type=Path)
    ap.add_argument('--manifest', type=Path, default=HERE/'FROZEN.json')
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    if not (args.seal or args.offline or args.live):
        print(json.dumps({'status':'offline_plan','provider_calls':0,'panels':{'flat':100,'verifier':200}}))
        return 0
    if not args.azdaja:
        ap.error('--azdaja required')
    rows = packs()
    files = inventory(args.azdaja)
    if args.seal:
        receipt = {'schema':'azdaja.jev_measurement_freeze.v1', 'files':files,
                   'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                   'binary_sha256':BINARY_SHA,'provider_calls':0,'pack_count':len(rows)}
        with args.manifest.open('xb') as stream:
            stream.write(n.canonical(receipt)+b'\n')
        print(json.dumps({'status':'sealed','files':len(files),'provider_calls':0}))
        return 0
    if not args.output or os.path.lexists(args.output):
        ap.error('new --output required')
    if args.live:
        if not args.acknowledge_provider_calls or not args.credential_state_root:
            ap.error('live needs explicit acknowledgement and private credential state')
        frozen = n.strict_loads(args.manifest.read_bytes())
        if frozen['files'] != files:
            raise n.Stop('freeze_changed')
        files[str(args.manifest.resolve())] = n.sha(args.manifest.read_bytes())
        with args.manifest.with_suffix('.started').open('xb') as stream:
            stream.write(n.canonical({'manifest_sha256':files[str(args.manifest.resolve())], 'automatic_retry':False})+b'\n')
    campaign = Measurement(args.azdaja, args.output, files, authorized=True,
                           attached_root=args.credential_state_root if args.live else None)
    # Never inherit another experiment's shared socket or model/runtime routing.
    for key in ('AZDAJA_JCODE_API_SOCKET', 'JCODE_API_SOCKET', 'JCODE_SOCKET', 'JCODE_RUNTIME_DIR'):
        campaign.env.pop(key, None)
    try:
        exercise(campaign, rows, args.live)
    except BaseException as error:
        campaign.finish('stopped', str(error) if isinstance(error,n.Stop) else type(error).__name__)
        print(json.dumps({'status':'stopped','reason':campaign.receipt['stop_reason']}))
        return 2
    campaign.finish('completed' if args.live else 'offline_public_workflow_passed')
    if campaign.receipt['status'] == 'stopped' or campaign.receipt.get('cleanup_exit') != 0:
        return 2
    print(json.dumps({'status':campaign.receipt['status'], 'typed_calls_started':campaign.receipt['typed_calls_started'],
                      'logical_llm_calls':campaign.receipt['logical_llm_calls']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
