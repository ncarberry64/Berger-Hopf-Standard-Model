"""Freeze the replayed true-birth chronological heat application."""
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
STEM = 'muon_joined_chronological_heat_mean'
FOLDER = ROOT / 'artifacts' / (STEM + '_20261011')


def identity(name):
    data = (ROOT / name).read_bytes()
    return dict(path=name, bytes=len(data), sha256=sha256(data).hexdigest())


def main():
    files = set()
    pairs = {}
    commands = []
    pins = 0
    for name in ('application.npz', 'result.json'):
        rows = [identity((FOLDER / f'run_{n}' / name).relative_to(ROOT).as_posix()) for n in (1, 2)]
        if len({(r['bytes'], r['sha256']) for r in rows}) != 1:
            raise ValueError('independent joined application differs: ' + name)
        pairs[name] = rows
        files.update(r['path'] for r in rows)
    for n in (1, 2):
        result = json.loads((FOLDER / f'run_{n}' / 'result.json').read_bytes())
        for p, h in result['input_hashes'].items():
            if identity(p)['sha256'] != h:
                raise ValueError('consumed joined action changed: ' + p)
            pins += 1
        logs = {}
        for channel in ('stdout', 'stderr'):
            p = f'artifacts/{STEM}_run_{n}.{channel}.txt'
            files.add(p)
            logs[channel] = dict(**identity(p), text=(ROOT / p).read_text())
        commands.append(dict(argv=[sys.executable, f'scripts/evaluate_{STEM}.py', '--output', f'artifacts/{STEM}_20261011/run_{n}'],
            cwd=str(ROOT), environment_overrides=dict(PYTHONPATH='src', OPENBLAS_NUM_THREADS='1'), exit_code=0, logs=logs))
    logs = {}
    for channel in ('stdout', 'stderr'):
        p = f'artifacts/{STEM}_tests.{channel}.txt'
        files.add(p)
        logs[channel] = dict(**identity(p), text=(ROOT / p).read_text())
    commands.append(dict(argv=[sys.executable, '-m', 'pytest', '--noconftest', '-q', f'tests/test_{STEM}.py'],
        cwd=str(ROOT), environment_overrides=dict(PYTHONPATH='src', OPENBLAS_NUM_THREADS='1'), exit_code=0, tests_passed=1, logs=logs))
    files.update((f'src/bhsm/interface/{STEM}.py', f'tests/test_{STEM}.py', f'scripts/evaluate_{STEM}.py',
        Path(__file__).relative_to(ROOT).as_posix()))
    record = dict(classification='VERIFIED_JOINED_TRUE_BIRTH_CHRONOLOGICAL_HEAT_MEAN', commands=commands,
        independent_byte_replays=pairs, verified_input_hash_count=pins, actual_records=result['records'],
        review='Owner independently checked incoming endpoint reversal, unchanged Gauss/frame reactions, initial midpoint half-contact, and distinct inherited parent action forcing and heat target. No zero-far or Lorentz/positive-heat identity is promoted.',
        DERIVED='Original signed canonical initial-value rows; chronological reversal with actual computed far canonical mean; full midpoint D3 load and explicit initial-x target; inherited affine parent action and native parameter contacts once.',
        EVALUATED='Both original and chronological constrained primal responses, two named chronological adjoints, explicit endpoint and inherited-parent native contacts on the same changing C6/temporal8 heat target.',
        CONTROL_ONLY='Conditional retained coefficient cell and c=1e-11 spectral probe. Initial-row derivative check uses an independent constrained quadratic action.',
        UNEVALUATED='Physical exterior/relative completion, full starting-loop and temporal complements, graph-resolved overlap subtraction, normalized soft Pauli remainder, final a_mu/g_mu and total uncertainty.',
        OWNER_DEFINITION_GAP='none established', statistics_factor_applied=False,
        physical_a_mu=None, physical_g_mu=None, complete_observable=False, error_scope=result['error_scope'])
    p = FOLDER / 'verification.json'
    p.write_text(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf8', newline='\n')
    files.add(p.relative_to(ROOT).as_posix())
    manifest = dict(classification='FROZEN_REPLAYED_JOINED_CHRONOLOGICAL_HEAT_MEAN', byte_identical_replay=True,
        files=[identity(p) for p in sorted(files)], complete_observable=False)
    q = FOLDER / 'publication_manifest.json'
    q.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(publication_manifest=identity(q.relative_to(ROOT).as_posix()),
        verification=identity(p.relative_to(ROOT).as_posix()), files=len(files)), sort_keys=True))


if __name__ == '__main__':
    main()
