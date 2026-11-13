"""Freeze actual common fixed-Y canonical current and source-jet applications."""
from pathlib import Path
from hashlib import sha256
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
STEM = 'muon_common_y_current_response'
FOLDER = ROOT/'artifacts'/(STEM+'_20261011')


def identity(name):
    b = (ROOT/name).read_bytes()
    return dict(path=name, bytes=len(b), sha256=sha256(b).hexdigest())


def main():
    files, pairs, commands = set(), {}, []
    pins = 0
    for n in (2, 3):
        result = json.loads((FOLDER/f'run_{n}'/'result.json').read_bytes())
        for p, h in result['input_hashes'].items():
            if identity(p)['sha256'] != h:
                raise ValueError('consumed canonical coefficient changed: '+p)
            pins += 1
    names = sorted((*result['array_archives'], 'result.json'))
    for name in names:
        rows = [identity((FOLDER/f'run_{n}'/name).relative_to(ROOT).as_posix()) for n in (2, 3)]
        if len({(r['bytes'], r['sha256']) for r in rows}) != 1:
            raise ValueError('actual common fixed-Y replay differs: '+name)
        pairs[name] = rows
        files.update(r['path'] for r in rows)
    for n, code in ((1, 1), (2, 0), (3, 0)):
        logs = {}
        for channel in ('stdout', 'stderr'):
            p = f'artifacts/{STEM}_run_{n}.{channel}.txt'
            logs[channel] = dict(**identity(p), text=(ROOT/p).read_text())
            files.add(p)
        commands.append(dict(argv=[sys.executable, f'scripts/evaluate_{STEM}.py', '--output', f'artifacts/{STEM}_20261011/run_{n}'],
            cwd=str(ROOT), environment_overrides=dict(PYTHONPATH='src', OPENBLAS_NUM_THREADS='1'), exit_code=code, logs=logs,
            scope='historical first attempt failed while aggregating unequal rectangular residual shapes; no result was exported; fixed by summing individual squared Frobenius norms' if n == 1 else 'final unchanged producer'))
    logs = {}
    for channel in ('stdout', 'stderr'):
        p = f'artifacts/{STEM}_tests_4.{channel}.txt'
        files.add(p)
        logs[channel] = dict(**identity(p), text=(ROOT/p).read_text())
    commands.append(dict(argv=[sys.executable, '-m', 'pytest', '--noconftest', '-q', f'tests/test_{STEM}.py'],
        cwd=str(ROOT), environment_overrides=dict(PYTHONPATH='src', OPENBLAS_NUM_THREADS='1'), exit_code=0, tests_passed=3, logs=logs))
    files.update((f'src/bhsm/interface/{STEM}.py', f'tests/test_{STEM}.py', f'scripts/evaluate_{STEM}.py',
        Path(__file__).relative_to(ROOT).as_posix()))
    verification = dict(classification='VERIFIED_COMMON_FIXED_Y_CURRENT_AND_BOTH_CANONICAL_MAGNETIC_DIRECTIONS',
        commands=commands, independent_byte_replays=pairs, verified_input_hash_count=pins, actual_records=result['records'],
        review='Owner independently checked spin-major C6 tensor n1, canonical angular sign, both midpoint trace halves, literal left/current map, rectangular forward/reverse signs, source/target Y insertions, and fixed-geometry charge-map zero scope.',
        DERIVED='Common action A0+yA1 coefficient recurrence including all odd powers and rectangular -A_target^-1 deltaA A_source^-1; exact stored inverse-defect and coefficient residual certificate, paired current contraction and Neumann tail.',
        EVALUATED='Actual incoming/child canonical charge-current and both magnetic source directions at16/32/64 cells on the unchanged coefficient domain; physical fixed middle/light Y values applied after common coefficient solves.',
        CONTROL_ONLY='Separate initial-zero/free-final inverse component per arm. The Y0 coefficient does not select an H-zero background or physical state; independent synthetic tests are derivative/certificate checks.',
        UNEVALUATED='Joined physical current trace, entry and temporal continuum bounds, magnetic-Y tail, completed quantum loop/native relative heat/domain, graph-resolved overlap and normalized Pauli remainder/final observable uncertainty.',
        OWNER_DEFINITION_GAP='none established', physical_a_mu=None, physical_g_mu=None, complete_observable=False,
        error_scope=result['error_scope'])
    p = FOLDER/'verification.json'
    p.write_text(json.dumps(verification, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    files.add(p.relative_to(ROOT).as_posix())
    manifest = dict(classification='FROZEN_REPLAYED_COMMON_FIXED_Y_CANONICAL_CURRENT', byte_identical_replay=True,
        files=[identity(p) for p in sorted(files)], complete_observable=False)
    q = FOLDER/'publication_manifest.json'
    q.write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(files=len(files), verification=identity(p.relative_to(ROOT).as_posix()),
        publication_manifest=identity(q.relative_to(ROOT).as_posix())), sort_keys=True))


if __name__ == '__main__':
    main()
