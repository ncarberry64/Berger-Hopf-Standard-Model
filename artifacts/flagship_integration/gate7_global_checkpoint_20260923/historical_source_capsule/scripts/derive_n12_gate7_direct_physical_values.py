"""Enclose endpoint rates and rates at actual physical HS midpoints.

No Taylor truncation or legacy endpoint-value authority is used. This is
selected-eigenpair, finite-history value evidence, not a physical Y certificate.
"""
import os
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import inspect
import json
from pathlib import Path
import sys
import time
import numpy as np
import flint
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_accepted_replay_center_outward_74d as cert
from bhsm.interface import physical_hs_value as hs

WORK = ROOT/'artifacts/flagship_integration/.direct_physical_value_work'
ALGORITHM = 'DIRECT_PHYSICAL_HS_VALUES_NORMALIZED_PROPOSAL_VERIFIED_EIGENPAIR_AND_INDEX_ARB512_V3'
PRECISION = 512
RATE_SHA256 = '0DC531574372EAA6C69AFAD3B4790A1C7EF52C18E7BA52B6C8FAAA1D442BFC2C'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_json(path, record):
    temporary = path.with_suffix('.partial.json')
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    temporary.replace(path)


def binding():
    if hashlib.sha256(inspect.getsource(cert._rate_enclosure).encode()).hexdigest().upper() != RATE_SHA256:
        raise RuntimeError('frozen physical rate function changed')
    paths = {Path(__file__), Path(cert.__file__), cert.ENDPOINT, cert.ENDPOINT.with_suffix('.npz')}
    # Bind all project source modules actually loaded by the unmodified rate
    # implementation, including transitive definitions of quadrature constants.
    for module in list(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT/'src/bhsm') and path.suffix == '.py':
                paths.add(path)
    return dict(algorithm=ALGORITHM, precision_bits=PRECISION,
        python=sys.version, numpy=np.__version__, python_flint=flint.__version__,
        files={p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)},
        step_convention='EXACT_BINARY64_DIFFERENCE_OF_STORED_ARC_PARAMETERS')


def verify_binding(record):
    for name, digest in record['files'].items():
        if sha(ROOT/name) != digest:
            raise RuntimeError(f'physical value input changed: {name}')


def operands():
    with np.load(cert.ENDPOINT.with_suffix('.npz')) as source:
        x = source['projected_states'].copy()
        w = source['state_weights'].copy()
        s = source['independent_signed_descriptors'].copy()
        ref = source['branch_reference'].copy()
        times = source['collocation_arc_parameters'].copy()
    if (x.shape != (371, 98) or w.shape != (98,) or s.shape != (371,)
            or ref.shape != (61,) or times.shape != (371,)
            or not all(np.isfinite(v).all() for v in (x, w, s, ref, times))
            or np.any(w <= 0) or np.any(np.diff(times) <= 0)):
        raise ValueError('complete finite accepted endpoint operands required')
    return x, w, s, ref, np.diff(times)


def load_cached(stage, index, expected, dependencies):
    path = WORK/f'{stage}_{index:03d}.npz'
    record = json.loads(path.with_suffix('.json').read_text())
    if (record.get('binding') != expected or record.get('dependencies') != dependencies
            or record.get('stage') != stage or record.get('index') != index
            or record.get('data_SHA256') != sha(path)
            or record.get('eigenpair_inclusion', {}).get('validation_passed') is not True
            or record.get('eigenpair_inclusion', {}).get('selected_zero_based_index_verified') != 24
            or record.get('eigenpair_inclusion', {}).get('spectral_index_verification', {}).get('validation_passed') is not True
            or record.get('outward_serialization_contains_source') is not True):
        raise RuntimeError('physical value cache binding failed')
    with np.load(path) as source:
        values = hs.restore_balls(source['value_mid_q'], source['value_rad_q'])
        state = hs.restore_balls(source['weighted_state_mid_q'], source['weighted_state_rad_q'])
    if values.shape != (99,) or state.shape != (99,):
        raise ValueError('incomplete physical value cache')
    return values, record


def worker(stage, index, expected, recompute=False):
    ctx.prec = PRECISION
    if stage not in ('endpoint', 'midpoint') or type(index) is not int or not 0 <= index < (371 if stage == 'endpoint' else 370):
        raise ValueError('invalid physical value point')
    if binding() != expected:
        raise RuntimeError('worker physical value binding changed')
    verify_binding(expected)
    x, w, s, reference, steps = operands()
    dependencies = {}
    if stage == 'endpoint':
        weighted = hs.weighted_endpoint(x[index], s[index], w)
        # Original raw endpoint values are exact binary64 leaves.
        state, descriptor = x[index], arb(float(s[index]))
    else:
        rates = []
        for node in (index, index+1):
            values, _ = load_cached('endpoint', node, expected, {})
            rates.append(values)
            for ext in ('json', 'npz'):
                path = WORK/f'endpoint_{node:03d}.{ext}'
                dependencies[path.relative_to(ROOT).as_posix()] = sha(path)
        weighted = hs.physical_midpoint(hs.weighted_endpoint(x[index], s[index], w),
            hs.weighted_endpoint(x[index+1], s[index+1], w), *rates, float(steps[index]))
        state = np.array([weighted[j]/arb(float(w[j])) for j in range(98)], dtype=object)
        descriptor = weighted[98]
    path = WORK/f'{stage}_{index:03d}.npz'
    previous = None
    if path.exists() or path.with_suffix('.json').exists():
        _, previous = load_cached(stage, index, expected, dependencies)
        if not recompute:
            return dict(stage=stage, index=index, reused=True)
    checks = []
    with hs.verified_eigenline(cert, checks, expected_index=24, normalize_proposal_center=True):
        result = cert._rate_enclosure(state, descriptor, w, reference, None)
    values = hs.finite_vector(result.value, 99)
    if len(checks) != 1:
        raise RuntimeError('exactly one independently verified eigenpair required')
    vm, vr = hs.rational_balls(values)
    sm, sr = hs.rational_balls(weighted)
    verify_binding(expected)
    verify_binding(dict(files=dependencies))
    temporary = path.with_suffix('.partial.npz')
    np.savez_compressed(temporary, value_mid_q=vm, value_rad_q=vr,
        weighted_state_mid_q=sm, weighted_state_rad_q=sr)
    record = dict(scope='FINITE_HISTORY_RATE_VALUES_AT_VERIFIED_SELECTED_EIGENPAIRS',
        stage=stage, index=index, binding=expected, dependencies=dependencies,
        data_SHA256=sha(temporary), eigenpair_inclusion=checks[0],
        outward_serialization_contains_source=True, midpoint_Taylor_truncation_used=False,
        legacy_endpoint_value_cache_used=False, physical_branch_continuation_certified=False,
        physical_Y_recertified=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    if previous is not None:
        if record != previous:
            write_json(WORK/f'{stage}_{index:03d}.repeat_mismatch.json', record)
            raise ArithmeticError('independent physical value reproduction differs; candidate preserved')
        # Retain first evidence; the independent computation must match both
        # data hash and the complete deterministic scientific record.
        temporary.unlink()
        return dict(stage=stage, index=index, reused=False, independently_reproduced=True)
    temporary.replace(path)
    write_json(path.with_suffix('.json'), record)
    load_cached(stage, index, expected, dependencies)
    return dict(stage=stage, index=index, reused=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--all-points', action='store_true')
    parser.add_argument('--midpoints', help='selected intervals; includes their endpoints')
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--worker-hour-cap', type=float, default=3)
    parser.add_argument('--recompute', action='store_true', help='independently repeat existing points and require identical evidence')
    args = parser.parse_args()
    if bool(args.all_points) == bool(args.midpoints):
        raise ValueError('choose all points or explicit midpoints')
    indices = list(range(370)) if args.all_points else [int(v) for v in args.midpoints.split(',')]
    if not indices or len(set(indices)) != len(indices) or any(not 0 <= v < 370 for v in indices):
        raise ValueError('distinct midpoint indices in 0..369 required')
    if not 1 <= args.workers <= 6 or not 0 < args.worker_hour_cap <= 6:
        raise ValueError('bounded workers and worker hours required')
    endpoints = sorted({n for i in indices for n in (i, i+1)})
    WORK.mkdir(parents=True, exist_ok=True)
    expected = binding()
    started = time.monotonic()
    completed = []
    failed_point = None
    if args.recompute and any(not (WORK/f'{stage}_{i:03d}.{ext}').is_file()
            for stage, points in (('endpoint', endpoints), ('midpoint', indices))
            for i in points for ext in ('npz', 'json')):
        raise RuntimeError('independent reproduction requires complete prior selected evidence')
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        try:
            for stage, points in (('endpoint', endpoints), ('midpoint', indices)):
                futures = {executor.submit(worker, stage, i, expected, args.recompute): i for i in points}
                remaining = args.worker_hour_cap*3600/args.workers-(time.monotonic()-started)
                for future in as_completed(futures, timeout=max(0, remaining)):
                    failed_point = dict(stage=stage, index=futures[future])
                    completed.append(future.result())
                    failed_point = None
                    write_json(WORK/'active_state.json', dict(terminal=False, stage=stage,
                        completed=len(completed), requested=len(endpoints)+len(indices),
                        elapsed_seconds=time.monotonic()-started, FULL_BHSM_COMPLETE=False))
                    if len(completed) % 25 == 0:
                        print(json.dumps(dict(stage=stage, completed=len(completed))), flush=True)
        except BaseException as error:
            # Terminate only this executor's owned workers on its own failure.
            for process in (executor._processes or {}).values():
                process.terminate()
            write_json(WORK/f'failure_{time.time_ns()}.json', dict(error=repr(error), completed=completed,
                failed_point=failed_point, eigenpair_inclusion=getattr(error, 'eigenpair_inclusion', None)))
            raise
    verify_binding(expected)
    paths = [WORK/f'{stage}_{i:03d}.{ext}' for stage, points in (('endpoint', endpoints), ('midpoint', indices))
             for i in points for ext in ('npz', 'json')]
    report = dict(scope='SELECTED_DIRECT_PHYSICAL_VALUES', binding=expected,
        endpoints=endpoints, midpoints=indices, files={p.relative_to(ROOT).as_posix(): sha(p) for p in paths},
        all_741_values_covered=len(endpoints) == 371 and len(indices) == 370,
        physical_Y_recertified=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    write_json(WORK/'manifest.json', report)
    if args.recompute:
        if not all(row.get('independently_reproduced') is True for row in completed):
            raise RuntimeError('reproduction requires every selected point to have prior evidence')
        write_json(WORK/'reproduction.json', dict(byte_identical=True, independent_recomputation=True,
            manifest_SHA256=sha(WORK/'manifest.json'), points=len(completed),
            physical_Y_recertified=False, FULL_BHSM_COMPLETE=False))
    write_json(WORK/'active_state.json', dict(terminal=True, completed=len(completed),
        requested=len(completed), manifest_SHA256=sha(WORK/'manifest.json'), FULL_BHSM_COMPLETE=False))
    print(json.dumps(dict(terminal=True, points=len(completed))), flush=True)


if __name__ == '__main__':
    main()
