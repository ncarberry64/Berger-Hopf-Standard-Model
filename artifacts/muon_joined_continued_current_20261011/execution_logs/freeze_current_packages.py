"""Verify independent continued-current applications and freeze their receipts."""
from pathlib import Path
from hashlib import sha256
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[3]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def freeze(name, test_result, error_scope):
    base = ROOT/'artifacts'/f'{name}_20261011'
    source = ROOT/f'src/bhsm/interface/{name}.py'
    files = [source, ROOT/f'tests/test_{name}.py',
             ROOT/f'scripts/evaluate_{name}.py', Path(__file__).resolve()]
    dependencies = {}
    pairs = []
    commands = []
    a, b = base/'run_1', base/'run_2'
    if sorted(p.name for p in a.iterdir()) != sorted(p.name for p in b.iterdir()):
        raise RuntimeError('independent output inventory differs: '+name)
    for original in sorted(a.iterdir()):
        repeated = b/original.name
        if original.read_bytes() != repeated.read_bytes():
            raise RuntimeError('independent output bytes differ: '+str(original))
        pairs.append(dict(paths=[p.relative_to(ROOT).as_posix() for p in (original, repeated)],
                          sha256=digest(original), byte_identical=True))
    for number in (1, 2):
        run = base/f'run_{number}'
        files += sorted(run.iterdir())
        metadata = json.loads((run/'result.json').read_bytes())
        for relative, expected in metadata['input_hashes'].items():
            if digest(ROOT/relative) != expected:
                raise RuntimeError('consumed source/input changed: '+relative)
            if relative in dependencies and dependencies[relative] != expected:
                raise RuntimeError('inconsistent source/input: '+relative)
            dependencies[relative] = expected
        command_path = base/'execution_logs'/f'run_{number}.command.json'
        command = json.loads(command_path.read_bytes())
        if command['exit_code'] != 0:
            raise RuntimeError('producer failed: '+str(command_path))
        commands.append(dict(path=command_path.relative_to(ROOT).as_posix(), **command))
        files.append(command_path)
        for label in ('stdout', 'stderr'):
            files.append(base/'execution_logs'/f'run_{number}.{label}.txt')
    files += sorted((base/'execution_logs').glob('*.py'))
    verify = base/'verification.json'
    verify.write_text(json.dumps(dict(classification='VERIFIED_CONTINUED_CURRENT_ACTION_REPLAY',
        pairs=pairs, commands=commands, tests=test_result,
        source_dependencies_verified=True, error_scope=error_scope,
        real_Euclidean_sectorial_heat_contour_proved=False,
        finite_cutoff_relative_completion_identified=False,
        physical_Pauli_completed=False), indent=2, sort_keys=True)+'\n',
        encoding='utf8', newline='\n')
    files.append(verify)
    entries = {}
    for path in files:
        data = path.read_bytes()
        if len(data) > 10*1024**2:
            raise RuntimeError('publication cap exceeded: '+str(path))
        if path.suffix in ('.py', '.json', '.txt') and b'\r\n' in data:
            raise RuntimeError('non-LF text: '+str(path))
        entries[path.relative_to(ROOT).as_posix()] = dict(bytes=len(data), sha256=sha256(data).hexdigest())
    manifest = base/'publication_manifest.json'
    manifest.write_text(json.dumps(dict(classification='VERIFIED_CONTINUED_CURRENT_ACTION_REPLAY',
        files=entries, dependencies=dependencies, pairs=pairs,
        physical_native_heat_or_Pauli_completed=False), indent=2, sort_keys=True)+'\n',
        encoding='utf8', newline='\n')
    return dict(package=name, source_sha256=digest(source), manifest_sha256=digest(manifest),
                result_sha256=digest(a/'result.json'), files=len(entries), dependencies=len(dependencies))


if __name__ == '__main__':
    argv = ['C:/Python314/python.exe', '-m', 'pytest', '--noconftest',
            'tests/test_muon_continued_current_factor.py',
            'tests/test_muon_joined_continued_current.py', '-q']
    environment = dict(PYTHONPATH='src', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    process = subprocess.run(argv, cwd=ROOT, env={**os.environ, **environment}, capture_output=True, text=True)
    test_result = dict(argv=argv, cwd=str(ROOT), environment=environment,
                       exit_code=process.returncode, stdout=process.stdout, stderr=process.stderr)
    if process.returncode:
        raise RuntimeError(json.dumps(test_result))
    print(json.dumps(test_result, sort_keys=True))
    print(json.dumps(freeze('muon_continued_current_factor', test_result,
        'binary64 same-domain inverse, analytic transpose current dual, and quadrature refinement; no certified continuum, sectorial real-contour heat, physical external-shell, finite-cutoff, or Pauli error'), sort_keys=True))
    print(json.dumps(freeze('muon_joined_continued_current', test_result,
        'binary64 finite canonical common-frame joined inverse and action-derived free-face Poisson/Schur return; neither numerical far face is identified with E0/infinity and no full exterior/native or Pauli reduction is claimed'), sort_keys=True))
