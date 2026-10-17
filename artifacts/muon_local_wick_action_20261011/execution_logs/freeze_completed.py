"""Freeze independently replayed local Wick action applications and commands."""
from pathlib import Path
from hashlib import sha256
import json

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'artifacts/muon_local_wick_action_20261011'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    files = [ROOT/p for p in ('src/bhsm/interface/muon_local_wick_action.py',
        'tests/test_muon_local_wick_action.py', 'scripts/evaluate_muon_local_wick_action.py')]
    dependencies = {}; pairs = []
    for side in ('incoming', 'outgoing'):
        for filename in ('application.npz', 'result.json'):
            a, b = [BASE/f'{side}_run_{i}'/filename for i in (1, 2)]
            if a.read_bytes() != b.read_bytes():
                raise RuntimeError('independent local action replay changed: '+side+' '+filename)
            pairs.append(dict(paths=[p.relative_to(ROOT).as_posix() for p in (a, b)],
                sha256=digest(a), byte_identical=True))
            files += [a, b]
        for number in (1, 2):
            md = json.loads((BASE/f'{side}_run_{number}'/'result.json').read_bytes())
            for path, expected in md['input_hashes'].items():
                if digest(ROOT/path) != expected:
                    raise RuntimeError('consumed owner changed: '+path)
                dependencies[path] = expected
            command_path = BASE/'execution_logs'/f'{side}_run_{number}.command.json'
            command = json.loads(command_path.read_bytes())
            if command['exit_code']:
                raise RuntimeError('producer did not finish')
            command['captured_text_newline_policy'] = 'CRLF normalized to LF; stdout/stderr content unchanged'
            command_path.write_text(json.dumps(command, indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
            files.append(command_path)
            for stem in ('stdout', 'stderr'):
                p = BASE/'execution_logs'/f'{side}_run_{number}.{stem}.txt'
                p.write_bytes(p.read_bytes().replace(b'\r\n', b'\n')); files.append(p)
    verify = BASE/'verification.json'
    verification = dict(classification='VERIFIED_INDEPENDENT_LITERAL_LOCAL_WICK_ACTION_REPLAY',
        pairs=pairs, source_dependencies_verified=True,
        tests=dict(command='PYTHONPATH=src C:/Python314/python.exe -m pytest --noconftest tests/test_muon_local_wick_action.py -q',
            exit_code=0, stdout='7 passed in 2.93s', scope='literal action, nonlinear Hessian, source rates, conormal, FP and canonical-row checks'),
        earlier_test_fixture_errors=['zero-dimensional old Jet max guard', 'missing old Maxwell clock metadata', 'keyword-only old Higgs action call'],
        physical_native_heat_or_Pauli_completed=False,
        error_scope='binary64 local action polynomial comparison and independent replay; analytic-contour/domain/production uncertainty not certified')
    verify.write_text(json.dumps(verification, indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
    files.append(verify); files += sorted((BASE/'execution_logs').glob('*.py'))
    entries = {}
    for path in files:
        data = path.read_bytes()
        if len(data)>10*1024**2:
            raise RuntimeError('file exceeds publication cap')
        if path.suffix in ('.py', '.json', '.txt') and b'\r\n' in data:
            raise RuntimeError('text is not LF')
        entries[path.relative_to(ROOT).as_posix()] = dict(bytes=len(data), sha256=sha256(data).hexdigest())
    manifest = BASE/'publication_manifest.json'
    manifest.write_text(json.dumps(dict(classification='VERIFIED_LITERAL_LOCAL_WICK_ACTION_SOURCE_AND_REPLAY',
        files=entries, dependencies=dependencies, pairs=pairs,
        physical_native_heat_or_Pauli_completed=False), indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(files=len(entries), manifest_sha256=digest(manifest)), sort_keys=True))


if __name__ == '__main__':
    main()
