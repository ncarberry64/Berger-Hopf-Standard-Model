"""Check both explicit-clock applications and retain executed validation scope."""
from pathlib import Path
from hashlib import sha256
import json
ROOT = Path(__file__).resolve().parents[1]


def verify():
    base = ROOT/'artifacts/muon_holomorphic_child_clock_application_20261011'
    left, right = base/'run_1', base/'run_2'
    files = sorted(p.relative_to(left) for p in left.rglob('*') if p.is_file())
    if files != sorted(p.relative_to(right) for p in right.rglob('*') if p.is_file()):
        raise ValueError('replay output sets differ')
    pairs = []
    for name in files:
        a, b = (left/name).read_bytes(), (right/name).read_bytes()
        if a != b:
            raise ValueError('explicit clock replay differs: '+str(name))
        pairs.append(dict(path=name.as_posix(), bytes=len(a), sha256=sha256(a).hexdigest()))
    receipt = json.loads((left/'result.json').read_bytes())
    for name, expected in receipt['input_hashes'].items():
        if sha256((ROOT/name).read_bytes()).hexdigest() != expected:
            raise ValueError('action input changed after evaluation: '+name)
    commands = []
    tests = 'artifacts/muon_holomorphic_child_clock_application_tests_20261011.log'
    log = (ROOT/tests).read_text(encoding='utf8')
    if '1 passed in 17.52s' not in log:
        raise ValueError('executed derivative test log changed')
    for order in (1, 2):
        name = f'artifacts/muon_holomorphic_child_clock_application_run_{order}_20261011.log'
        raw = (ROOT/name).read_bytes()
        commands.append(dict(argv=['C:\\Python314\\python.exe',
            'scripts/evaluate_muon_holomorphic_child_clock_application.py', '--output',
            f'artifacts/muon_holomorphic_child_clock_application_20261011/run_{order}'],
            exit_code=0, stdout_log=name, stdout_sha256=sha256(raw).hexdigest(),
            output=json.loads(raw.decode('utf8').strip())))
    result = dict(classification='VERIFIED_REPLAY_AND_DERIVATIVE_CONTROL_FOR_EXPLICIT_CLOCK_APPLICATION',
        byte_identical_replay=True, pairs=pairs, input_hashes=receipt['input_hashes'],
        environment=dict(PYTHONPATH='src;scripts', OPENBLAS_NUM_THREADS='1'),
        commands=commands,
        test=dict(argv=['C:\\Python314\\python.exe', '-m', 'pytest', '--noconftest', '-q',
            'tests/test_muon_holomorphic_child_clock_application.py'], exit_code=0,
            stdout_log=tests, stdout_sha256=sha256((ROOT/tests).read_bytes()).hexdigest(),
            actual_output=log.strip()),
        numerical_results={key:receipt[key] for key in ('gradient_clock_first_norm',
            'canonical_tangent_rhs_norm', 'actual_geometry_multiplier_residual_max', 'independent_clock_controls')},
        error_scope=receipt['error_scope'], canonical_compatibility_established=False,
        native_contribution_or_final_muon_result_evaluated=False)
    output = base/'verification.json'
    output.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(verification_sha256=sha256(output.read_bytes()).hexdigest(),
        byte_identical_replay=True, file_pairs=len(pairs), checked_input_hashes=len(receipt['input_hashes']))))


if __name__ == '__main__':
    verify()
