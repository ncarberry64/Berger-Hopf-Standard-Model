"""Record focused action checks and the consumed stored-response replay."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / 'run_1'
if OUT.exists():
    raise FileExistsError('preserve executed checks')
OUT.mkdir()
ENV = dict(os.environ, PYTHONPATH='src;scripts', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
TESTS = (
    'tests/test_muon_mixed_changing_birth_action.py',
    'tests/test_muon_full_canonical_terminal_return.py',
    'tests/test_muon_fixed_parent_finite_shooting.py',
    'tests/test_muon_fixed_parent_fiber_admission.py',
    'tests/test_muon_stored_fiber_canonical_tangent.py',
    'tests/test_muon_retracted_child_birth.py',
    'tests/test_muon_exact_stored_phase_reset_value.py',
    'tests/test_muon_full_d5_localized_lepton_trace.py',
)


def execute(label, suffix):
    argv = [sys.executable, *suffix]
    start_utc = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    run = subprocess.run(argv, cwd=ROOT, env=ENV, capture_output=True)
    streams = {}
    for key, data in (('stdout', run.stdout), ('stderr', run.stderr)):
        p = OUT / (label + '.' + key + '.txt')
        p.write_bytes(data)
        streams[key] = dict(path=p.relative_to(ROOT).as_posix(), bytes=len(data), sha256=sha256(data).hexdigest())
    return dict(argv=argv, start_utc=start_utc, end_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=time.monotonic()-start, exit_code=run.returncode, streams=streams)


commands = [execute('focused_tests', ['-m', 'pytest', '-q', *TESTS]),
    execute('complete_finite_work_replay', ['scripts/evaluate_muon_corrected_finite_fiber_work.py',
        '--output', 'artifacts/muon_corrected_finite_fiber_work_20261012/run_3'])]
members = ('complete_finite_action_work.npz', 'result.json')
replay = {}
for name in members:
    hashes = {str(i):sha256((ROOT/'artifacts/muon_corrected_finite_fiber_work_20261012'/f'run_{i}'/name).read_bytes()).hexdigest()
        for i in (1, 2, 3)}
    replay[name] = dict(hashes=hashes, byte_identical=len(set(hashes.values())) == 1)
pins = {name:sha256((ROOT/name).read_bytes()).hexdigest() for name in TESTS}
pins['scripts/evaluate_muon_corrected_finite_fiber_work.py'] = sha256((ROOT/'scripts/evaluate_muon_corrected_finite_fiber_work.py').read_bytes()).hexdigest()
record = dict(classification='EXECUTED_FOCUSED_ACTION_CHECKS_AND_CONSUMED_RESPONSE_REPLAY',
    working_directory=str(ROOT), environment={k:ENV[k] for k in ('PYTHONPATH','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')},
    commands=commands, replay=replay, checked_source_hashes=pins,
    all_passed=all(c['exit_code'] == 0 for c in commands) and all(r['byte_identical'] for r in replay.values()),
    error_scope='Stored matrix/endpoint-cotangent arithmetic and action/constraint/dual implementation checks. These do not admit the nonlinear birth candidate, select a retarded exterior or formation section, or enclose a physical pole, native Pauli contribution or anomaly uncertainty.')
p = OUT/'verification.json'
p.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
print(json.dumps(dict(all_passed=record['all_passed'], verification_sha256=sha256(p.read_bytes()).hexdigest())))
raise SystemExit(0 if record['all_passed'] else 1)
