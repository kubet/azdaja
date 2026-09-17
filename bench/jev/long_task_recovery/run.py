#!/usr/bin/env python3
"""One explicitly sealed transport-only follow-through, never an implicit retry."""
import argparse
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from bench.jev.long_task import run as base

PREVIOUS = base.HERE / 'results/initial-20260917'
PREVIOUS_RETENTION_SHA = '0b9b01f7f3b25455141219b856a20077191918491833dbbe9294c00b81c993e5'
ORIGINAL_SECONDS = 2100


def predecessor():
    raw = (PREVIOUS / 'RETENTION.json').read_bytes()
    base.check(base.sha(raw) == PREVIOUS_RETENTION_SHA, 'predecessor_retention_changed')
    retained = base.loads(raw)['files']
    actual = {str(p.relative_to(PREVIOUS)): base.sha(p.read_bytes())
              for p in PREVIOUS.rglob('*') if p.is_file() and p.name != 'RETENTION.json'}
    base.check(actual == retained, 'predecessor_artifacts_changed')
    spent = {}
    for arm in base.ARMS:
        folder = PREVIOUS / arm
        receipt = base.loads((folder / 'receipt.json').read_bytes())
        trace = [base.loads(line) for line in (folder / 'model-trace.jsonl').read_bytes().splitlines()]
        base.check(receipt['status'] == 'stopped' and receipt['stop_reason'] == 'unknown_entered_usage', 'predecessor_status')
        base.check(len(trace) == 1 and trace[0]['depth'] == 0 and trace[0]['outcome'] == 'failed'
                   and trace[0]['error_category'] == 'timeout' and trace[0]['latency_ms'] == 60009,
                   'predecessor_root_timeout')
        base.check(not (folder / 'stdout.txt').read_bytes()
                   and b'=== root response' not in (folder / 'solo-trace.txt').read_bytes(), 'predecessor_has_output')
        seconds = receipt['workflow_seconds']
        base.check(type(seconds) in (int, float) and math.isfinite(seconds) and 0 < seconds < ORIGINAL_SECONDS,
                   'predecessor_timing')
        base.check(receipt['original_auth_unchanged'] and receipt['private_credentials_removed'], 'predecessor_cleanup')
        spent[arm] = seconds
    return spent


def inventory(binary):
    value = base.inventory(binary)
    for path in [HERE / 'AMENDMENT.md', HERE / 'run.py', HERE / 'test_run.py',
                 base.HERE / 'FROZEN.json', base.HERE / 'FROZEN.started', PREVIOUS / 'RETENTION.json']:
        base.check(path.is_file() and not path.is_symlink(), 'recovery_inventory_missing')
        value['files'][str(path.relative_to(ROOT))] = base.sha(path.read_bytes())
    value['predecessor_workflow_seconds'] = predecessor()
    value['remaining_seconds'] = {a: math.floor(ORIGINAL_SECONDS - s)
                                  for a, s in value['predecessor_workflow_seconds'].items()}
    return value


def check_seal(binary):
    raw = (HERE / 'FROZEN.json').read_bytes()
    seal = base.loads(raw)
    base.check(seal['inventory'] == inventory(binary) and seal['arms'] == list(base.ARMS), 'recovery_seal_changed')
    return base.sha(raw)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seal', action='store_true')
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--acknowledge-provider-calls', action='store_true')
    for name in ('binary', 'output', 'auth-file', 'attached-file'):
        parser.add_argument('--' + name, type=Path)
    args = parser.parse_args(argv)
    if not args.live and not args.seal:
        print(base.canonical({'status': 'offline_plan', 'provider_calls': 0, 'new_pair_limit': 1}).decode().strip())
        return 0
    base.check(args.binary is not None, 'binary_required')
    binary = args.binary.resolve(strict=True)
    if args.seal:
        base.check(not args.live, 'conflicting_modes')
        base.save(HERE / 'FROZEN.json', {'schema': 'azdaja.long_task.recovery_freeze.v1',
                  'inventory': inventory(binary), 'arms': list(base.ARMS),
                  'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()})
        print('{"status":"sealed","provider_calls":0}')
        return 0
    base.check(args.acknowledge_provider_calls and args.output and args.auth_file and args.attached_file,
               'explicit_live_arguments')
    base.check(args.output.is_absolute() and args.output.parent.is_dir() and not os.path.lexists(args.output), 'new_absolute_output')
    scratch = Path(os.environ['JCODE_SCRATCH_DIR']).resolve(strict=True)
    base.check(scratch != ROOT and ROOT not in scratch.parents, 'private_scratch_inside_repository')
    frozen = check_seal(binary)
    prior = predecessor()
    base.save(HERE / 'FROZEN.started', {'frozen_sha256': frozen, 'started_unix': time.time()})
    args.output.mkdir(mode=0o700)
    private = Path(tempfile.mkdtemp(prefix='jev-long-recovery-private-', dir=str(scratch)))
    base.save(args.output / 'campaign.json', {'schema': 'azdaja.long_task.recovery_campaign.v1',
              'frozen_sha256': frozen, 'binary_sha256': base.sha(binary.read_bytes()),
              'predecessor_retention_sha256': PREVIOUS_RETENTION_SHA,
              'prior_entered_requests_unknown_usage': 2, 'cumulative_usage_is_lower_bound': True,
              'private_runtime_outside_repository': True})
    def interrupt(signum, frame):
        raise KeyboardInterrupt('campaign interrupted')
    signal.signal(signal.SIGTERM, interrupt)
    receipts = {}
    for arm in base.ARMS:
        check_seal(binary)
        old_limit = base.SECONDS
        try:
            base.SECONDS = math.floor(ORIGINAL_SECONDS - prior[arm])
            receipts[arm] = base.run_arm(binary, arm, args.output / arm, private / arm,
                                         auth=args.auth_file, attached=args.attached_file)
        finally:
            base.SECONDS = old_limit
        receipt = receipts[arm]
        receipt['predecessor_workflow_seconds'] = prior[arm]
        receipt['cumulative_workflow_seconds'] = prior[arm] + receipt['workflow_seconds']
        receipt['prior_entered_requests_unknown_usage'] = 1
        receipt['cumulative_usage_is_lower_bound'] = True
        if receipt['status'].startswith('completed') and receipt['cumulative_workflow_seconds'] > ORIGINAL_SECONDS:
            receipt.update(status='stopped', stop_reason='cumulative_workflow_deadline')
        base.checkpoint(args.output / arm / 'receipt.json', receipt)
        print(base.canonical({'arm': arm, 'status': receipt['status'], 'seconds': receipt['workflow_seconds']}).decode().strip(), flush=True)
        if receipt.get('interrupted') or receipt.get('cleanup_error') or receipt.get('credential_cleanup_error'):
            break
    base.save(args.output / 'terminal.json', {'status': 'pair_terminal',
              'arms': {a: r['status'] for a, r in receipts.items()},
              'all_completed': len(receipts) == 2 and all(r['status'].startswith('completed') for r in receipts.values()),
              'cumulative_workflow_seconds': {a: prior[a] + r['workflow_seconds'] for a, r in receipts.items()},
              'further_campaigns_authorized': False, 'cumulative_usage_is_lower_bound': True})
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, base.Stop) as error:
        print(base.canonical({'status': 'refused', 'reason': str(error) if isinstance(error, base.Stop) else type(error).__name__,
                              'no_implicit_retry': True}).decode().strip())
        raise SystemExit(2)
