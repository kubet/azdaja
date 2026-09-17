#!/usr/bin/env python3
"""One sealed native model-authored long-task pair. Default is provider-free."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from bench.jev.long_task import grade as scoring

ARMS = ('generative', 'optional_typed')
MODEL, TYPED_MODEL = 'gpt-5.6-sol', 'jev-1.13.0'
SECONDS, MAX_INPUT, MAX_OUTPUT, MAX_LOGICAL = 2100, 6_000_000, 500_000, 160
OUTPUT_LIMIT, TRACE_LIMIT = 2_097_152, 16_777_216
CONSTRAINTS = {
    'generative': 'ARM CONSTRAINT: use ordinary generative llm/llm_batch or deterministic code. judge_many is forbidden in this control and has no attached credential. judge_stats is allowed only for accounting, never evidence.',
    'optional_typed': 'ARM CONSTRAINT: you may optionally use judge_many as well as ordinary generative llm/llm_batch and deterministic code. Choose the useful combination yourself. Typed use is not mandatory. No particular threshold or decomposition is prescribed.',
}
SECRET_SHAPE = re.compile(rb'(?:apikey_[A-Za-z0-9]+_[A-Za-z0-9]+|sk-(?:proj-)?[A-Za-z0-9_-]{24,})')


class Stop(RuntimeError):
    pass


def check(value, reason):
    if not value:
        raise Stop(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n').encode()


def loads(raw):
    return json.loads(raw, object_pairs_hook=scoring.unique_object,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def save(path, value):
    raw = canonical(value)
    check(not SECRET_SHAPE.search(raw), 'credential_shaped_output_refused')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def checkpoint(path, value):
    raw = canonical(value)
    check(not SECRET_SHAPE.search(raw), 'credential_shaped_checkpoint_refused')
    temp = path.with_name(path.name + '.new')
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def environment(private, output):
    env = dict(os.environ)
    for name in list(env):
        if re.search(r'API.?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|AUTHORIZATION|SOCKET|_SOCK$', name, re.I) or name.startswith(('AZDAJA_', 'JCODE_', 'RLM_')):
            env.pop(name)
    env.update(HOME=str(private / 'home'), JCODE_HOME=str(private / 'jcode'),
               JCODE_RUNTIME_DIR=str(private / 'runtime'), AZDAJA_HOME=str(private / 'state'),
               AZDAJA_CONFIG=str(private / 'config.toml'),
               AZDAJA_MODEL_TRACE=str(output / 'model-trace.jsonl'),
               AZDAJA_SOLO_TRACE=str(output / 'solo-trace.txt'))
    return env


def config(provider='jcode-api'):
    return ('sub_llm_cmd=' + json.dumps(provider) + '\n'
            f'default_model="{MODEL}"\njcode_provider="openai"\njcode_reasoning="medium"\n'
            'sub_timeout=120\ncell_timeout=1800\noutput_cap=262144\nmax_calls_per_cell=150\n'
            '[judge]\nenabled=true\n'
            f'model="{TYPED_MODEL}"\nexpected_model="{TYPED_MODEL}"\n'
            'key_env="TYPESAFE_API_KEY"\ntimeout_secs=30\nmax_requests_per_cell=160\n'
            'max_questions_per_cell=4096\nmax_request_bytes=90000\nmax_response_bytes=262144\n'
            'max_input_tokens_per_cell=4000000\n')


def task(arm):
    check(arm in ARMS, 'unknown_arm')
    return (HERE / 'task.txt').read_text() + '\n' + CONSTRAINTS[arm]


def inventory(binary):
    binary = Path(binary).resolve(strict=True)
    required = ['PLAN.md', 'ATTRIBUTION.md', 'task.txt', 'schema.json', 'run.py', 'test_run.py',
                'prepare.py', 'test_prepare.py', 'grade.py', 'test_grade.py',
                'native_acceptance.py', 'test_native_acceptance.py',
                'fixtures/corpus.json', 'fixtures/questions.json', 'fixtures/gold.json',
                'fixtures/source-manifest.json']
    paths = [HERE / name for name in required]
    paths += [ROOT / name for name in ['Cargo.lock', 'Cargo.toml', 'build.rs']]
    paths += sorted((ROOT / 'src').rglob('*.rs'))
    check(all(p.is_file() and not p.is_symlink() for p in paths), 'source_inventory_missing')
    return {'files': {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in paths},
            'binary': {'path': str(binary), 'sha256': sha(binary.read_bytes())},
            'jcode': {'path': str(Path(shutil.which('jcode')).resolve()),
                      'sha256': sha(Path(shutil.which('jcode')).resolve().read_bytes())}}


def check_seal(binary):
    path = HERE / 'FROZEN.json'
    seal = loads(path.read_bytes())
    check(seal['inventory'] == inventory(binary), 'frozen_inventory_changed')
    check(seal['arms'] == list(ARMS) and seal['seconds_per_arm'] == SECONDS, 'frozen_policy_changed')
    return sha(path.read_bytes())


def trace_summary(path, partial=False):
    raw = path.read_bytes() if path.exists() else b''
    check(len(raw) <= TRACE_LIMIT, 'model_trace_limit')
    if partial and raw and not raw.endswith(b'\n'):
        raw = raw[:raw.rfind(b'\n') + 1]
    events = [loads(line) for line in raw.splitlines() if line.strip()]
    by_id = {}
    for event in events:
        check(type(event) is dict and event.get('event') == 'model_attempt', 'trace_event')
        rid = event.get('request_id')
        check(type(rid) is str and rid, 'trace_id')
        check(type(event.get('attempt')) is int and 1 <= event['attempt'] <= 8, 'trace_attempt')
        entered = event.get('entered_turn')
        check(entered is None or type(entered) is int and 1 <= entered <= 4, 'trace_entered')
        check(event.get('outcome') in ('succeeded', 'failed'), 'trace_outcome')
        if event['outcome'] == 'succeeded':
            check(entered is not None and event.get('model') == MODEL and event.get('provider') == 'OpenAI', 'model_identity')
        by_id.setdefault(rid, []).append(event)
    for group in by_id.values():
        check(len(group) <= 8 and sum(e.get('entered_turn') is None for e in group) <= 4, 'trace_attempt_budget')
        ordinals = [e['attempt'] for e in group]
        check(len(ordinals) == len(set(ordinals)), 'duplicate_physical_attempt')
    usage = {}
    for field in ('input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'reasoning_tokens'):
        known = [e[field] for e in events if e.get(field) is not None]
        check(all(type(x) is int and x >= 0 for x in known), 'invalid_usage')
        usage[field] = {'known_total': sum(known),
                        'unknown_entered_events': sum(e.get('entered_turn') is not None and e.get(field) is None for e in events)}
    return {'events': len(events), 'logical_requests': len(by_id),
            'entered_turns': sum(e.get('entered_turn') is not None for e in events),
            'setup_attempts': sum(e.get('entered_turn') is None for e in events),
            'succeeded_events': sum(e['outcome'] == 'succeeded' for e in events),
            'failed_events': sum(e['outcome'] == 'failed' for e in events), 'usage': usage}


def usage_ok(summary):
    check(summary['logical_requests'] <= MAX_LOGICAL, 'logical_request_budget')
    for field, cap in [('input_tokens', MAX_INPUT), ('output_tokens', MAX_OUTPUT)]:
        check(summary['usage'][field]['unknown_entered_events'] == 0, 'unknown_entered_usage')
        check(summary['usage'][field]['known_total'] <= cap, 'known_usage_cap')


def runtime_summary(path):
    raw = path.read_bytes()
    check(len(raw) <= TRACE_LIMIT and not SECRET_SHAPE.search(raw), 'solo_trace_limit_or_credential')
    match = re.search(rb'\n=== solo runtime trace begin request_id=("[^"\n]+") ===\n([^\n]+)\n=== solo runtime trace end request_id=\1 ===\n\Z', raw)
    check(match is not None, 'trusted_runtime_footer_missing')
    value = loads(match[2])
    check(value['event'] == 'solo_runtime' and value['request_id'] == loads(match[1]), 'runtime_identity')
    cells = value.get('judge_cells')
    check(type(cells) is list and cells, 'typed_snapshot_missing')
    fields = ('attempts', 'successful_requests', 'failed_attempts', 'questions', 'cache_hits',
              'known_input_tokens', 'known_output_tokens', 'unknown_input_usage_requests',
              'unknown_output_usage_requests', 'total_wall_ns')
    totals = dict.fromkeys(fields, 0)
    for cell in cells:
        check(type(cell) is dict, 'typed_snapshot_unknown')
        for field in fields:
            check(type(cell.get(field)) is int and cell[field] >= 0, 'typed_stats_domain')
            totals[field] += cell[field]
        check(type(cell.get('provider_requests')) is int and
              cell['attempts'] == cell['successful_requests'] + cell['failed_attempts'] == cell['provider_requests'], 'typed_stats_consistency')
        check(cell['unknown_input_usage_requests'] <= cell['attempts'] and cell['unknown_output_usage_requests'] <= cell['attempts'], 'typed_unknown_consistency')
    check(totals['attempts'] <= 160 and totals['questions'] <= 4096, 'typed_campaign_cap')
    value['typed_totals'] = totals
    return value


def opaque_copy(source, destination, max_bytes=131072):
    """Read only the explicit private credential source, never print its contents."""
    fd = os.open(source, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        meta = os.fstat(stream.fileno())
        check(stat.S_ISREG(meta.st_mode) and meta.st_uid == os.getuid() and not meta.st_mode & 0o077 and 0 < meta.st_size <= max_bytes, 'private_credential_file_policy')
        raw = stream.read(max_bytes + 1)
    check(len(raw) <= max_bytes, 'credential_size')
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return sha(raw)


def stop_bridge(state):
    base = state / 'jcode-api'
    pidfile, runtimefile = base / 'bridge.pid', base / 'runtime-dir'
    if not pidfile.exists() or not runtimefile.exists():
        return False
    pid, directory = int(pidfile.read_text()), Path(runtimefile.read_text().strip())
    probe = subprocess.run(['ps', '-p', str(pid), '-o', 'args='], capture_output=True, text=True, timeout=5)
    if probe.returncode:
        return False
    args = shlex.split(probe.stdout)
    check(len(args) > 2 and Path(args[0]).name == 'jcode' and args[1] == 'api-bridge'
          and '--api-socket' in args and args[args.index('--api-socket') + 1] == str(directory / 'api.sock'), 'owned_bridge_identity')
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return False
    for _ in range(20):
        probe = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='], capture_output=True, text=True, timeout=5)
        if probe.returncode or probe.stdout.strip().startswith('Z'):
            return True
        time.sleep(.1)
    # Revalidate before escalation so PID reuse can never target another process.
    current = subprocess.run(['ps', '-p', str(pid), '-o', 'args='], capture_output=True, text=True, timeout=5)
    if current.returncode:
        return True
    check(shlex.split(current.stdout) == args, 'owned_bridge_identity_changed')
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return True
    for _ in range(20):
        probe = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='], capture_output=True, text=True, timeout=5)
        if probe.returncode or probe.stdout.strip().startswith('Z'):
            return True
        time.sleep(.1)
    raise Stop('owned_bridge_still_running')


def terminate(process):
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        return process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return process.wait(timeout=8)


def run_arm(binary, arm, destination, private, *, auth, attached, offline_provider=None):
    setup_started = time.monotonic()
    destination.mkdir(mode=0o700)
    private.mkdir(mode=0o700)
    for sub in ('home', 'jcode', 'runtime', 'state', 'source'):
        (private / sub).mkdir(mode=0o700)
    credential_paths = []
    auth_hash = None
    cfg = config(offline_provider or 'jcode-api')
    (private / 'config.toml').write_text(cfg)
    os.chmod(private / 'config.toml', 0o600)
    shutil.copyfile(HERE / 'fixtures/corpus.json', private / 'source/corpus.json')
    shutil.copyfile(HERE / 'schema.json', private / 'source/schema.json')
    question = task(arm)
    save(destination / 'admission.json', {'arm': arm, 'input_sha256': sha((private / 'source/corpus.json').read_bytes()),
         'task_sha256': sha(question.encode()), 'task': question, 'config': cfg,
         'binary_sha256': sha(binary.read_bytes()), 'offline_stub': offline_provider is not None})
    save(destination / 'started.json', {'started_unix': time.time(), 'arm': arm})
    env = environment(private, destination)
    command = [str(binary), 'solo', question, '-f', str(private / 'source/corpus.json'),
               '--schema', str(private / 'source/schema.json'), '--model', MODEL, '--sub-model', MODEL]
    started = time.monotonic()
    receipt = {'schema': 'azdaja.long_task.arm.v1', 'arm': arm, 'status': 'running',
               'stop_reason': None, 'offline_stub': offline_provider is not None,
               'setup_seconds': started - setup_started,
               'billing_known': False, 'typed_accounting_known': False,
               'generative_accounting_scope': 'Retained completed model_attempt events. In-flight requests on hard interruption may be unobserved; recorded usage is then a lower bound, not zero.'}
    process = None
    checkpoint(destination / 'receipt.json', receipt)
    try:
        if offline_provider is None:
            auth_dest = private / 'jcode/openai-auth.json'
            credential_paths.append(auth_dest)
            auth_hash = opaque_copy(auth, auth_dest)
            if arm == 'optional_typed':
                directory = private / 'state/credentials'
                directory.mkdir(mode=0o700)
                key_dest = directory / (sha(b'TYPESAFE_API_KEY') + '.key')
                credential_paths.append(key_dest)
                opaque_copy(attached, key_dest, 8192)
        with (destination / 'stdout.txt').open('xb') as stdout, (destination / 'stderr.txt').open('xb') as stderr:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                       env=env, cwd=private / 'source', start_new_session=True)
            next_progress = 0
            while process.poll() is None:
                elapsed = time.monotonic() - started
                check(elapsed <= SECONDS, 'absolute_arm_deadline')
                check(all(not p.exists() or p.stat().st_size <= limit for p, limit in [
                    (destination / 'stdout.txt', OUTPUT_LIMIT), (destination / 'stderr.txt', OUTPUT_LIMIT),
                    (destination / 'solo-trace.txt', TRACE_LIMIT), (destination / 'model-trace.jsonl', TRACE_LIMIT)]), 'output_limit')
                if offline_provider is None:
                    observed = trace_summary(destination / 'model-trace.jsonl', partial=True)
                    usage_ok(observed)
                    receipt['generative'] = observed
                if elapsed >= next_progress:
                    receipt['elapsed_seconds'] = elapsed
                    checkpoint(destination / 'receipt.json', receipt)
                    print('JCODE_PROGRESS ' + json.dumps({'message': 'long_task ' + arm, 'seconds': round(elapsed),
                          'logical_requests': receipt.get('generative', {}).get('logical_requests', 0)}), flush=True)
                    next_progress = elapsed + 20
                time.sleep(0.5)
            receipt['exit'] = process.wait()
        if offline_provider is None:
            receipt['generative'] = trace_summary(destination / 'model-trace.jsonl')
            usage_ok(receipt['generative'])
        runtime = runtime_summary(destination / 'solo-trace.txt')
        receipt.update(runtime=runtime, typed_accounting_known=True)
        totals = runtime['typed_totals']
        check(totals['known_input_tokens'] <= 4_000_000 and totals['failed_attempts'] == 0
              and totals['unknown_input_usage_requests'] == totals['unknown_output_usage_requests'] == 0,
              'typed_budget_failure_or_unknown_usage')
        if arm == 'generative':
            check(totals['attempts'] == 0 and totals['total_wall_ns'] == 0, 'control_typed_evaluation')
        check(receipt['exit'] == 0 and runtime['outcome'] == 'succeeded', 'native_solo_failed')
        raw = (destination / 'stdout.txt').read_bytes()
        check(len(raw) <= OUTPUT_LIMIT and not SECRET_SHAPE.search(raw), 'final_output_policy')
        prediction = loads(raw)
        save(destination / 'prediction.json', prediction)
        receipt['status'] = 'completed_outputs_pending_scoring'
    except BaseException as error:
        receipt['status'] = 'stopped'
        receipt['stop_reason'] = str(error) if isinstance(error, Stop) else type(error).__name__
        receipt['interrupted'] = isinstance(error, (KeyboardInterrupt, SystemExit))
        if process is not None:
            receipt['exit'] = terminate(process)
    finally:
        try:
            receipt['owned_bridge_stop_requested'] = stop_bridge(private / 'state')
        except (OSError, ValueError, Stop, subprocess.SubprocessError) as error:
            receipt['cleanup_error'] = type(error).__name__
            receipt['status'] = 'stopped'
        try:
            for path in credential_paths:
                path.unlink(missing_ok=True)
            # These entire roots were created by this arm. Include possible
            # private auth refresh/temporary files, not only the original copy.
            shutil.rmtree(private / 'jcode')
            if (private / 'state/credentials').exists():
                shutil.rmtree(private / 'state/credentials')
            receipt['private_credentials_removed'] = all(not p.exists() for p in credential_paths)
            if auth_hash is not None:
                receipt['original_auth_unchanged'] = sha(auth.read_bytes()) == auth_hash
        except OSError as error:
            receipt.update(status='stopped', private_credentials_removed=False,
                           credential_cleanup_error=type(error).__name__)
        receipt['elapsed_seconds'] = time.monotonic() - started
        receipt['workflow_seconds'] = receipt['setup_seconds'] + receipt['elapsed_seconds']
        if receipt['elapsed_seconds'] > SECONDS and receipt['status'].startswith('completed'):
            receipt.update(status='stopped', stop_reason='completion_deadline')
        if offline_provider is None:
            try:
                receipt['generative'] = trace_summary(destination / 'model-trace.jsonl')
            except (OSError, ValueError, Stop) as error:
                receipt['generative_accounting_error'] = type(error).__name__
        if not receipt['typed_accounting_known']:
            try:
                receipt['runtime'] = runtime_summary(destination / 'solo-trace.txt')
                receipt['typed_accounting_known'] = True
            except (OSError, ValueError, Stop):
                pass
        receipt['retained_files'] = {p.name: sha(p.read_bytes()) for p in destination.iterdir() if p.is_file() and p.name != 'receipt.json'}
        checkpoint(destination / 'receipt.json', receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seal', action='store_true')
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--acknowledge-provider-calls', action='store_true')
    parser.add_argument('--binary', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--auth-file', type=Path)
    parser.add_argument('--attached-file', type=Path)
    args = parser.parse_args(argv)
    if not args.live and not args.seal:
        print(json.dumps({'status': 'offline_plan', 'arms': ARMS, 'provider_calls': 0}))
        return 0
    check(args.binary is not None, 'binary_required')
    binary = args.binary.resolve(strict=True)
    if args.seal:
        check(not args.live, 'conflicting_modes')
        save(HERE / 'FROZEN.json', {'schema': 'azdaja.long_task.freeze.v1', 'inventory': inventory(binary),
             'arms': list(ARMS), 'seconds_per_arm': SECONDS, 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()})
        print(json.dumps({'status': 'sealed', 'provider_calls': 0}))
        return 0
    check(args.acknowledge_provider_calls and args.output and args.auth_file and args.attached_file, 'explicit_live_arguments')
    check(args.output.is_absolute() and args.output.parent.is_dir(), 'absolute_existing_output_parent_required')
    check(not os.path.lexists(args.output), 'output_exists')
    frozen_sha = check_seal(binary)
    scratch = Path(os.environ['JCODE_SCRATCH_DIR']).resolve(strict=True)
    check(scratch != ROOT and ROOT not in scratch.parents, 'private_scratch_inside_repository')
    save(HERE / 'FROZEN.started', {'frozen_sha256': frozen_sha, 'started_unix': time.time()})
    args.output.mkdir(mode=0o700)
    private_root = Path(tempfile.mkdtemp(prefix='jev-long-private-', dir=str(scratch)))
    save(args.output / 'campaign.json', {'schema': 'azdaja.long_task.campaign.v1', 'frozen_sha256': frozen_sha,
         'binary_sha256': sha(binary.read_bytes()), 'arms': list(ARMS), 'private_runtime_outside_repository': not private_root.is_relative_to(ROOT) if hasattr(private_root, 'is_relative_to') else str(ROOT) not in str(private_root)})
    def interrupted(signum, frame):
        raise KeyboardInterrupt('campaign interrupted')
    signal.signal(signal.SIGTERM, interrupted)
    receipts = {}
    for arm in ARMS:
        check_seal(binary)
        receipts[arm] = run_arm(binary, arm, args.output / arm, private_root / arm,
                               auth=args.auth_file, attached=args.attached_file)
        print(json.dumps({'arm': arm, 'status': receipts[arm]['status'], 'seconds': receipts[arm]['elapsed_seconds']}), flush=True)
        if receipts[arm].get('interrupted') or receipts[arm].get('cleanup_error') or receipts[arm].get('credential_cleanup_error'):
            break
    save(args.output / 'terminal.json', {'status': 'pair_terminal', 'arms': {a: r['status'] for a, r in receipts.items()},
         'all_completed': len(receipts) == len(ARMS) and all(r['status'].startswith('completed') for r in receipts.values()), 'new_campaigns_authorized': False})
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, Stop) as error:
        print(json.dumps({'status': 'refused', 'reason': str(error) if isinstance(error, Stop) else type(error).__name__, 'no_implicit_retry': True}))
        raise SystemExit(2)
