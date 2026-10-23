"""Freeze completed independent action applications without rerunning producers."""
from pathlib import Path
from hashlib import sha256
import json

ROOT = Path(__file__).resolve().parents[3]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


PACKAGES = (
    ('muon_wick_temporal_action', (2, 3), (2, 3),
     'VERIFIED_LITERAL_FULL488_TEMPORAL_WICK_ACTION_REPLAY',
     '3 passed in 0.90s',
     ['run_1 failed on the original static-array time indexing before output; the corrected producer completed runs 2 and 3'],
     'binary64 literal continued action/Gauss/canonical comparisons; no positive-real heat, exterior contour, continuum, or physical Pauli identification'),
    ('muon_corrected_birth_mean', (1, 2), (1, 2),
     'VERIFIED_CORRECTED_MOVING226_BIRTH_MEAN_REPLAY',
     '2 passed in 1.73s',
     ['first algebraic test tolerance 3e-16 was below its observed 1.22e-15 summed Gauss rounding; final tolerance 3e-15'],
     'Arb certificate applies to exact stored 226-row arrays; upstream action/Dg step-halving, representation, domain, and physical Pauli errors are excluded'),
    ('muon_corrected_birth_canonical_mean', (2, 3), (1, 2, 3),
     'VERIFIED_CORRECTED_BIRTH_CANONICAL_MEAN_AND_PARENT_FORCING_REPLAY',
     '2 passed', [],
     'binary64 same-action canonical Hessian/source applications; upstream mean/Dg, continuum, and physical chronological state errors excluded'),
    ('muon_wick_canonical_inverse', (1, 2), (1, 2),
     'VERIFIED_CONTINUED_SAME_DOMAIN_FULL488_CANONICAL_INVERSE_REPLAY',
     '2 passed in 2.21s', [],
     'binary64 continued canonical inverse and transpose adjoint on inherited finite action domain; refinement diagnostics are not certified continuum or physical Pauli errors'),
)


def freeze(name, pair_runs, retained_runs, classification, test_stdout, earlier, error_scope):
    base = ROOT/'artifacts'/f'{name}_20261011'
    files = [ROOT/f'src/bhsm/interface/{name}.py', ROOT/f'tests/test_{name}.py',
             ROOT/f'scripts/evaluate_{name}.py', Path(__file__).resolve()]
    pairs = []
    for filename in ('application.npz', 'result.json'):
        a, b = [base/f'run_{i}'/filename for i in pair_runs]
        if a.read_bytes() != b.read_bytes():
            raise RuntimeError(f'independent replay differs: {name} {filename}')
        pairs.append(dict(paths=[p.relative_to(ROOT).as_posix() for p in (a, b)],
                          sha256=digest(a), byte_identical=True))
    dependencies = {}
    commands = []
    for number in retained_runs:
        output = base/f'run_{number}'
        files += sorted(output.iterdir())
        metadata = json.loads((output/'result.json').read_bytes())
        for relative, expected in metadata['input_hashes'].items():
            if digest(ROOT/relative) != expected:
                raise RuntimeError('consumed input changed: '+relative)
            if relative in dependencies and dependencies[relative] != expected:
                raise RuntimeError('inconsistent consumed input: '+relative)
            dependencies[relative] = expected
        command_path = base/'execution_logs'/f'run_{number}.command.json'
        if command_path.exists():
            command = json.loads(command_path.read_bytes())
            if command['exit_code'] != 0:
                raise RuntimeError('producer did not finish: '+str(command_path))
            commands.append(dict(path=command_path.relative_to(ROOT).as_posix(), **command))
            files.append(command_path)
            for label in ('stdout', 'stderr'):
                files.append(base/'execution_logs'/f'run_{number}.{label}.txt')
        else:
            commands.append(dict(run=number, exit_code=0, output_preserved=True,
                stdout=None, capture_limitation='Initial direct CLI output was truncated by the tool; independent runs 2 and 3 have complete captured commands/stdout/stderr.'))
    # Only successful application logs are consumed; failed pre-output logs remain preserved.
    files += sorted((base/'execution_logs').glob('*.py'))
    verification = dict(classification=classification, pairs=pairs,
        commands=commands, source_dependencies_verified=True,
        tests=dict(command=f'PYTHONPATH=src C:/Python314/python.exe -m pytest --noconftest tests/test_{name}.py -q',
                   exit_code=0, stdout=test_stdout),
        earlier_fixture_or_loader_corrections=earlier,
        physical_native_heat_or_Pauli_completed=False, error_scope=error_scope)
    verify = base/'verification.json'
    verify.write_text(json.dumps(verification, indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
    files.append(verify)
    entries = {}
    for path in files:
        if not path.is_file():
            raise RuntimeError('unexpected output directory: '+str(path))
        data = path.read_bytes()
        if len(data) > 10*1024**2:
            raise RuntimeError('publication cap exceeded: '+str(path))
        if path.suffix in ('.py', '.json', '.txt') and b'\r\n' in data:
            raise RuntimeError('non-LF consumed text: '+str(path))
        entries[path.relative_to(ROOT).as_posix()] = dict(bytes=len(data), sha256=sha256(data).hexdigest())
    manifest = base/'publication_manifest.json'
    manifest.write_text(json.dumps(dict(classification=classification, files=entries,
        dependencies=dependencies, pairs=pairs, physical_native_heat_or_Pauli_completed=False),
        indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
    return dict(package=name, files=len(entries), dependencies=len(dependencies),
                manifest_sha256=digest(manifest), archive_sha256=pairs[0]['sha256'])


if __name__ == '__main__':
    for package in PACKAGES:
        print(json.dumps(freeze(*package), sort_keys=True))
