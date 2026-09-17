"""Explicit remaining-work amendment. Default and offline modes make no calls."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

from bench.jev.angle_lab import native as n
from bench.jev.measurement_v2 import run as original
from . import evidence as e

HERE = Path(__file__).resolve().parent


def remaining_rows():
    by_name = {r['name']: r for r in original.packs()}
    return [by_name[name] for name in e.CONTINUATION_NAMES]


def inventory(binary):
    files = original.inventory(binary)
    files[str((e.ORIGINAL/'FROZEN.json').resolve())] = n.sha((e.ORIGINAL/'FROZEN.json').read_bytes())
    files[str((e.ORIGINAL/'FROZEN.started').resolve())] = n.sha((e.ORIGINAL/'FROZEN.started').read_bytes())
    candidates = [p for p in e.PREDECESSOR.iterdir() if p.is_file()]
    candidates += [p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.md')]
    for p in candidates:
        files[str(p.resolve())] = n.sha(p.read_bytes())
    return dict(sorted(files.items()))


class Continuation(original.Measurement):
    def __init__(self, *args, previous, **kwargs):
        self.previous = previous
        super().__init__(*args, **kwargs)

    def left(self):
        left = super().left() - self.previous['receipt']['elapsed_seconds']
        if left <= 0:
            raise n.Stop('cumulative_campaign_deadline')
        return left

    def configure(self, enabled):
        # Reuse the frozen native configuration with the actual remaining token
        # budget, not a fresh allowance. Restore this run's receipt counters.
        prior = self.previous['totals']['known_typed_input_tokens']
        self.receipt['known_typed_input_tokens'] += prior
        try:
            if self.previous['totals']['typed_unknown_usage']:
                raise n.Stop('predecessor_unknown_input_usage')
            super().configure(enabled)
        finally:
            self.receipt['known_typed_input_tokens'] -= prior

    def checkpoint(self):
        self.receipt['experiment_schema'] = 'azdaja.jev_measurement_continuation.v1'
        self.receipt['official_rah_submission'] = False
        self.receipt['automatic_approval_authorized'] = False
        self.receipt['original_study_status'] = 'stopped'
        self.receipt['predecessor_receipt_sha256'] = n.sha((e.PREDECESSOR/'receipt.json').read_bytes())
        self.receipt['carried_totals'] = self.previous['totals']
        self.receipt['cumulative_totals'] = {
            key: value + self.receipt[key] for key, value in self.previous['totals'].items()}
        self.receipt['no_previously_attempted_pair_repeated'] = True
        # Original checkpoint deliberately owns atomic persistence and elapsed.
        n.Campaign.checkpoint(self)

    @n.terminal
    def typed(self, name, pack):
        if self.previous['totals']['typed_calls_started'] + self.receipt['typed_calls_started'] >= 12:
            raise n.Stop('cumulative_typed_cap')
        if self.previous['totals']['known_typed_input_tokens'] + self.receipt['known_typed_input_tokens'] >= n.MAX_INPUT:
            raise n.Stop('cumulative_input_cap')
        return super().typed(name, pack)

    @n.terminal
    def generate(self, name, pack):
        if self.previous['totals']['logical_llm_calls'] + self.receipt['logical_llm_calls'] >= 12:
            raise n.Stop('cumulative_generative_cap')
        entered = self.previous['trace']['entered_turns'] + n.usage_summary(self.output/'model-trace.jsonl')['entered_turns']
        if entered + 2 > 24:
            raise n.Stop('cumulative_entered_turn_reservation')
        return super().generate(name, pack)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--seal', action='store_true')
    mode.add_argument('--offline', action='store_true')
    mode.add_argument('--live', action='store_true')
    ap.add_argument('--azdaja', type=Path)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--manifest', type=Path, default=HERE/'FROZEN.json')
    ap.add_argument('--credential-state-root', type=Path)
    ap.add_argument('--acknowledge-provider-calls', action='store_true')
    args = ap.parse_args()
    if not (args.live or args.offline or args.seal):
        print(json.dumps({'status':'offline_plan','provider_calls':0,'original_study_status':'stopped',
                          'remaining_packs':e.CONTINUATION_NAMES,'retries':0}))
        return 0
    if not args.azdaja:
        ap.error('--azdaja required')
    previous = e.predecessor()
    files = inventory(args.azdaja)
    if args.seal:
        frozen = {'schema':'azdaja.measurement_continuation_freeze.v1','files':files,
                  'sealed_at':datetime.now(timezone.utc).isoformat(),
                  'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  'predecessor_receipt_sha256':n.sha((e.PREDECESSOR/'receipt.json').read_bytes()),
                  'remaining_order':e.CONTINUATION_ORDER,'carried_totals':previous['totals'],
                  'original_study_status':'stopped','provider_calls':0}
        with args.manifest.open('xb') as stream:
            stream.write(n.canonical(frozen)+b'\n')
        print(json.dumps({'status':'sealed','files':len(files),'provider_calls':0}))
        return 0
    if not args.output or os.path.lexists(args.output):
        ap.error('new --output required')
    if args.live:
        if not args.acknowledge_provider_calls or not args.credential_state_root:
            ap.error('live requires acknowledgement and private credential state')
        frozen = e.load(args.manifest)
        e.check(frozen['files'] == files, 'continuation freeze changed')
        files[str(args.manifest.resolve())] = n.sha(args.manifest.read_bytes())
        with args.manifest.with_suffix('.started').open('xb') as stream:
            stream.write(n.canonical({'manifest_sha256':files[str(args.manifest.resolve())], 'retries':0})+b'\n')
    campaign = Continuation(args.azdaja, args.output, files, previous=previous, authorized=True,
                            attached_root=args.credential_state_root if args.live else None)
    for key in ('AZDAJA_JCODE_API_SOCKET','JCODE_API_SOCKET','JCODE_SOCKET','JCODE_RUNTIME_DIR'):
        campaign.env.pop(key,None)
    try:
        original.exercise(campaign, remaining_rows(), args.live)
    except BaseException as error:
        campaign.finish('stopped',str(error) if isinstance(error,n.Stop) else type(error).__name__)
        print(json.dumps({'status':'stopped','reason':campaign.receipt['stop_reason'],
                          'cumulative_totals':campaign.receipt['cumulative_totals']}))
        return 2
    campaign.finish('completed' if args.live else 'offline_public_workflow_passed')
    print(json.dumps({'status':campaign.receipt['status'],'original_study_status':'stopped',
                      'cumulative_totals':campaign.receipt['cumulative_totals']}))
    return 0 if campaign.receipt['status'] != 'stopped' and campaign.receipt.get('cleanup_exit') == 0 else 2


if __name__ == '__main__':
    raise SystemExit(main())
