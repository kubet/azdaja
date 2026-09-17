"""Explicit one-shot local-setup continuation; no completed judgment is rerun."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from bench.jev.angle_lab import campaign as original
from bench.jev.angle_lab import native as n
from bench.jev.angle_lab.gate import prepare_grade as gate

HERE = Path(__file__).parent
ROOT = HERE.resolve().parents[2]


def predecessor(path):
    receipt = n.strict_loads((path / 'receipt.json').read_text())
    body = n.strict_loads((path / 'calibration-observation.json').read_text())
    request = n.strict_loads((path / 'calibration-request.json').read_text())
    fit = n.strict_loads((path / 'calibration-result.json').read_text())
    trace = n.usage_summary(path / 'model-trace.jsonl')
    if not (receipt['status'] == 'stopped' and receipt['stop_reason'] == 'public_cli_exec'
            and receipt['typed_calls_started'] == receipt['confirmed_typed_requests'] == 1
            and receipt['logical_llm_calls'] == 1 and receipt['typed_questions'] == 20
            and receipt['known_typed_input_tokens'] == 3261
            and receipt['known_typed_output_tokens'] == 404
            and receipt['typed_unknown_usage'] == receipt['typed_unknown_output_usage'] == 0
            and trace['entered_turns'] == 0 and trace['setup_attempts'] == 1
            and trace['logical_request_ids'] == 1 and trace['succeeded_events'] == 0):
        raise n.Stop('predecessor_not_declared_setup_failure')
    observed = body['observation']
    if (n.canonical(request) != n.canonical(n.inspect_pack(gate.calibration()))
            or observed['model'] != n.MODEL
            or observed['_azdaja']['request_sha256'] != n.sha(n.canonical(request))
            or body['stats']['provider_requests'] != 1
            or observed['usage'] != {'input_tokens': 3261, 'output_tokens': 404}
            or fit != gate.fit_threshold(original.probabilities(observed))):
        raise n.Stop('predecessor_binding_or_threshold')
    return receipt, observed


def inventory(prior, binary):
    manifest_path = original.HERE / 'FROZEN.json'
    old = n.strict_loads(manifest_path.read_text())
    if old['files'] != original.inputs() or old['binary_sha256'] != n.sha(binary.read_bytes()):
        raise n.Stop('original_freeze_changed')
    predecessor(prior)
    files = {str(ROOT / name): digest for name, digest in old['files'].items()}
    files[str(manifest_path.resolve())] = n.sha(manifest_path.read_bytes())
    for p in sorted(HERE.glob('*')):
        if p.suffix in ('.md', '.py'):
            files[str(p.resolve())] = n.sha(p.read_bytes())
    for p in sorted(prior.glob('*')):
        if p.is_file():
            files[str(p.resolve())] = n.sha(p.read_bytes())
    files[str(binary.resolve())] = n.sha(binary.read_bytes())
    return files


class Continuation(n.Campaign):
    def __init__(self, binary, output, frozen, prior, attached_root, origin_start):
        self.prior, self.carried = predecessor(prior)
        self.origin_start = origin_start
        self.calibration_reused = False
        super().__init__(binary, output, frozen, authorized=True, attached_root=attached_root)
        self.receipt['predecessor_receipt_sha256'] = n.sha((prior / 'receipt.json').read_bytes())
        self.receipt['continuation_reason'] = 'isolated_local_bridge_after_zero_entered_turn_setup_failure'
        self.checkpoint()

    def left(self):
        remaining = min(super().left(), n.MAX_SECONDS - (time.time() - self.origin_start))
        if remaining <= 0:
            raise n.Stop('original_campaign_deadline')
        return remaining

    def checkpoint(self):
        keys = ('typed_calls_started', 'confirmed_typed_requests', 'typed_questions',
                'known_typed_input_tokens', 'known_typed_output_tokens', 'typed_unknown_usage',
                'typed_unknown_output_usage', 'logical_llm_calls')
        self.receipt['cumulative_including_stopped_predecessor'] = {
            key: self.prior[key] + self.receipt[key] for key in keys}
        self.receipt['wall_seconds_since_original_start'] = time.time() - self.origin_start
        super().checkpoint()

    def configure(self, enabled):
        remaining = n.MAX_INPUT - self.prior['known_typed_input_tokens'] - self.receipt['known_typed_input_tokens']
        if enabled and remaining <= 0:
            raise n.Stop('cumulative_input_budget')
        super().configure(enabled)
        path = self.work / 'config.toml'
        text = path.read_text()
        old = n.MAX_INPUT - self.receipt['known_typed_input_tokens']
        text = text.replace(f'max_input_tokens_per_cell={max(1, old)}\n',
                            f'max_input_tokens_per_cell={max(1, remaining)}\n')
        path.write_text(text)
        path.chmod(0o600)

    @n.terminal
    def typed(self, name, pack):
        if name == 'calibration':
            if self.calibration_reused or n.canonical(n.inspect_pack(pack)) != n.canonical(n.inspect_pack(gate.calibration())):
                raise n.Stop('invalid_calibration_reuse')
            self.load('carried_calibration', self.carried)
            retained = n.strict_loads(self.cell('carried-calibration-reentry',
                'observations["calibration"] = json.loads(carried_calibration)\nFINAL(observations["calibration"])\n'))
            if retained != self.carried:
                raise n.Stop('carried_reentry_changed')
            self.calibration_reused = True
            self.receipt['carried_calibration_sha256'] = n.sha(n.canonical(retained))
            self.checkpoint()
            return retained
        if self.prior['typed_calls_started'] + self.receipt['typed_calls_started'] >= n.MAX_REQUESTS:
            raise n.Stop('cumulative_typed_attempt_budget')
        return super().typed(name, pack)

    @n.terminal
    def generate(self, name, pack, instruction=None):
        if self.prior['logical_llm_calls'] + self.receipt['logical_llm_calls'] >= n.MAX_GENERATIVE:
            raise n.Stop('cumulative_generative_budget')
        return super().generate(name, pack, instruction)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prior', type=Path, required=True)
    ap.add_argument('--azdaja', type=Path, required=True)
    ap.add_argument('--manifest', type=Path, default=HERE / 'FROZEN.json')
    ap.add_argument('--seal', action='store_true')
    ap.add_argument('--live', action='store_true')
    ap.add_argument('--acknowledge-provider-calls', action='store_true')
    ap.add_argument('--credential-state-root', type=Path)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    if args.seal == args.live:
        ap.error('choose exactly one of --seal or --live')
    files = inventory(args.prior, args.azdaja)
    if args.seal:
        prior = n.strict_loads((args.prior / 'receipt.json').read_text())
        manifest = {'schema': 'azdaja.angle_setup_continuation.v1', 'files': files,
                    'source_commit': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                    'origin_start_unix': (args.prior / 'receipt.json').stat().st_mtime - prior['elapsed_seconds'],
                    'no_completed_request_repeated': True}
        with args.manifest.open('xb') as stream:
            stream.write(n.canonical(manifest) + b'\n')
        print(json.dumps({'status':'sealed','files':len(files),'provider_calls':0}))
        return 0
    if not args.acknowledge_provider_calls or not args.output or not args.credential_state_root:
        ap.error('live needs acknowledgement, new output and private credential state')
    manifest = n.strict_loads(args.manifest.read_text())
    if manifest['files'] != files:
        raise n.Stop('continuation_freeze_changed')
    files[str(args.manifest.resolve())] = n.sha(args.manifest.read_bytes())
    with args.manifest.with_suffix('.started').open('xb') as stream:
        stream.write(n.canonical({'manifest_sha256':n.sha(args.manifest.read_bytes()),'automatic_retry':False})+b'\n')
    c = Continuation(args.azdaja, args.output, files, args.prior, args.credential_state_root,
                     manifest['origin_start_unix'])
    try:
        original.run(c)
    except BaseException as error:
        reason = str(error) if isinstance(error,n.Stop) else type(error).__name__
        c.finish('stopped',reason)
        print(json.dumps({'status':'stopped','reason':reason}))
        return 2
    c.finish('completed')
    print(json.dumps({'status':c.receipt['status'],
                     'cumulative':c.receipt['cumulative_including_stopped_predecessor']}))
    return 0 if c.receipt['status']=='completed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
