"""Execute and record the five publication audits on an explicit Git index.

This records repository checks, not a physical observable certificate.
All stdout/stderr and exit codes are preserved; existing receipts are not
overwritten. Run after selecting the reviewed scientific files.
"""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = (
    ('status', ['tools/audit_bhsm_status.py']),
    ('claims', ['tools/audit_forbidden_claims.py']),
    ('frozen', ['tools/audit_frozen_prediction_integrity.py']),
    ('precision', ['tools/verify_precision.py']),
    ('public', ['tools/audit_public_readiness.py', '--format', 'json']),
)


def git(*args):
    return subprocess.check_output(['git', '-c', 'gc.auto=0', '-c',
        'maintenance.auto=false', *args], cwd=ROOT).decode().strip()


def materialize(output):
    out = (ROOT/output).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        raise ValueError('new audit output inside the intended checkout required')
    out.mkdir(parents=True)
    head, tree = git('rev-parse', 'HEAD'), git('write-tree')
    env = dict(os.environ, PYTHONPATH='src', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')

    def execute(item):
        label, suffix = item
        argv = [sys.executable, *suffix]
        started = time.monotonic()
        run = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True)
        elapsed = time.monotonic()-started
        streams = {}
        for key, data in (('stdout', run.stdout), ('stderr', run.stderr)):
            path = out/(label+'.'+key+'.txt')
            path.write_bytes(data)
            streams[key] = dict(path=path.relative_to(ROOT).as_posix(),
                bytes=len(data), sha256=sha256(data).hexdigest())
        try:
            result = json.loads(run.stdout)
            semantic_pass = result.get('passed') is True
        except (json.JSONDecodeError, UnicodeDecodeError):
            result = None
            semantic_pass = label == 'precision' and run.stdout.startswith(b'PASS:')
        return dict(label=label, argv=argv, exit_code=run.returncode,
            elapsed_seconds=elapsed, streams=streams, reported_result=result,
            passed=run.returncode == 0 and semantic_pass)

    with ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(pool.map(execute, COMMANDS))
    unchanged = head == git('rev-parse', 'HEAD') and tree == git('write-tree')
    receipt = dict(classification='EXECUTED_FIVE_AUDITS_ON_REVIEWED_PUBLICATION_INDEX',
        working_directory=str(ROOT), head_before_commit=head, checked_index_tree=tree,
        index_and_head_unchanged_during_audits=unchanged,
        environment={k:env[k] for k in ('PYTHONPATH','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')},
        commands=rows, all_passed=unchanged and all(r['passed'] for r in rows),
        frozen_predictions={str(p):sha256((ROOT/p).read_bytes()).hexdigest()
            for p in ('docs/frozen_predictions.md','docs/frozen_predictions.json')},
        scope='repository/status/claims/frozen precision/publication checks on the recorded index; no physical matching, native Pauli or anomaly uncertainty enclosure',
        recorder_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    path = out/'verification.json'
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(all_passed=receipt['all_passed'],
        verification_sha256=sha256(path.read_bytes()).hexdigest(),
        head=head, checked_index_tree=tree,
        audit_exit_codes={r['label']:r['exit_code'] for r in rows})))
    return 0 if receipt['all_passed'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(materialize(args.output))
