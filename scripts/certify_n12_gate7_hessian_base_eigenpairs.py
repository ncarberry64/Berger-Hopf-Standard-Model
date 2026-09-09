"""Verify the unchanged common eigenpair preparation for complete Hessian points."""
import os
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
import numpy as np
import flint
from flint import ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from bhsm.interface import physical_hs_value as hs
from bhsm.interface import arb_eigenpair_inclusion as inclusion
from bhsm.interface import arb_symmetric_inertia as inertia

ALGORITHM = 'COMPLETE_HESSIAN_POINT_COMMON_BASE_EIGENPAIR_AND_INDEX_ARB256_V1'
WORK = ROOT/'artifacts/flagship_integration/.hessian_base_eigenpair_work'
ACTIVE_BACKEND = None
CAMPAIGN = None


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def install(name):
    global ACTIVE_BACKEND, CAMPAIGN
    if ACTIVE_BACKEND is not None:
        if ACTIVE_BACKEND != name:
            raise RuntimeError('one Hessian backend per process required')
        return CAMPAIGN
    modules = dict(original='derive_n12_gate7_physical_midpoint_hessian_errors',
        factored='derive_n12_gate7_factored_physical_hessian_errors',
        bulk='derive_n12_gate7_bulk_physical_hessian_errors')
    module = importlib.import_module(modules[name])
    if name == 'original':
        campaign = module
    else:
        module.install_backend()
        campaign = module.campaign
    ACTIVE_BACKEND, CAMPAIGN = name, campaign
    return campaign


def proof_sources():
    paths = [Path(__file__), Path(hs.__file__), Path(inclusion.__file__), Path(inertia.__file__)]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}


def write_json(path, record):
    temporary = path.with_suffix('.partial.json')
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    temporary.replace(path)


def verify_sources(campaign, binding, sources):
    for group in ('sources', 'original_provenance'):
        for name, digest in binding[group].items():
            if campaign.sha(ROOT/name) != digest:
                raise RuntimeError(f'Hessian computation source changed: {name}')
    if proof_sources() != sources:
        raise RuntimeError('common-base proof source changed')


def worker(backend, index, expected, sources, recompute=False):
    campaign = install(backend)
    values, binding, fingerprint = campaign.load_inputs(index)
    if fingerprint != expected:
        raise RuntimeError('Hessian common-base input fingerprint changed')
    directory = campaign.point_directory(index)
    if json.loads((directory/'binding.json').read_text()) != binding:
        raise RuntimeError('Hessian row cache has a different common-base binding')
    verify_sources(campaign, binding, sources)
    # This validates every existing row and its exact fingerprint. It does
    # not call any physical Hessian worker or regenerate a Hessian row.
    _, _, rows = campaign.cache.assemble_rows(directory, fingerprint)
    if len(rows) != 99:
        raise RuntimeError('all 99 Hessian rows required')
    paths = [directory/'binding.json']+[directory/f'row_{i:03d}.{ext}'
             for i in range(99) for ext in ('json', 'npz')]
    raw_files = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    point = WORK/backend/f'midpoint_{index:03d}.npz'
    previous = None
    if point.exists() or point.with_suffix('.json').exists():
        previous = json.loads(point.with_suffix('.json').read_text())
        if (previous.get('algorithm') != ALGORITHM or previous.get('backend') != backend
                or previous.get('interval') != index or previous.get('fingerprint') != fingerprint or previous.get('binding') != binding
                or previous.get('raw_cache_files') != raw_files or previous.get('proof_sources') != sources
                or previous.get('data_SHA256') != sha(point)
                or previous.get('eigenpair_verification', {}).get('selected_zero_based_index_verified') != 24
                or previous.get('eigenpair_verification', {}).get('spectral_index_verification', {}).get('validation_passed') is not True
                or previous.get('eigenpair_verification', {}).get('validation_passed') is not True):
            raise RuntimeError('common-base eigenpair cache binding failed')
        if not recompute:
            return dict(backend=backend, index=index, reused=True)
    # Each backend deliberately prepares its original base jets and eigenline
    # before installing factored or bulk contraction scopes. Reconstruct only
    # that common phase at the original precision, then verify its exact balls.
    # Ensure --recompute also means a fresh preparation when this API is used
    # twice in the same process; the CLI additionally uses a fresh worker pool.
    campaign.CONTEXT = None
    campaign.prepare_worker(index, fingerprint)
    cert = campaign.graph.cert
    jets = cert._arb_action_jets(values['state'])
    ctx.prec = 512
    checks = []
    with hs.verified_eigenline(cert, checks, expected_index=24):
        psi, eigenvalue, _, _ = cert._eigenline(jets.hessian_arb, jets.hessian_mid, values['reference'])
    if len(checks) != 1:
        raise RuntimeError('one verified common-base eigenpair required')
    arrays = {}
    for name, value in (('hessian', jets.hessian_arb[cert.QDIM:, cert.QDIM:]),
                        ('psi', psi), ('eigenvalue', np.asarray([eigenvalue], dtype=object))):
        arrays[name+'_mid_q'], arrays[name+'_rad_q'] = hs.rational_balls(value)
    verify_sources(campaign, binding, sources)
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in paths} != raw_files:
        raise RuntimeError('Hessian row cache changed during base verification')
    point.parent.mkdir(parents=True, exist_ok=True)
    temporary = point.with_suffix('.partial.npz')
    np.savez_compressed(temporary, **arrays)
    record = dict(algorithm=ALGORITHM, scope='VERIFIED_COMMON_BASE_FOR_COMPLETE_SOURCE_BOUND_HESSIAN_POINT',
        backend=backend, interval=index, fingerprint=fingerprint, binding=binding, raw_cache_files=raw_files,
        proof_sources=sources, base_precision_bits=campaign.PRECISION, verification_precision_bits=512,
        runtime=dict(python=sys.version, numpy=np.__version__, python_flint=flint.__version__),
        data_SHA256=sha(temporary), eigenpair_verification=checks[0], complete_Hessian_rows=99,
        physical_Hessian_rows_recomputed=False, physical_branch_continuation_certified=False,
        all_physical_Hessian_points_certified=False, physical_contraction_proved=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    if previous is not None:
        if record != previous:
            write_json(point.with_suffix('.repeat_mismatch.json'), record)
            raise ArithmeticError('common-base eigenpair reproduction differs; candidate preserved')
        temporary.unlink()
        return dict(backend=backend, index=index, independently_reproduced=True)
    temporary.replace(point)
    write_json(point.with_suffix('.json'), record)
    return dict(backend=backend, index=index, reused=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=('original', 'factored', 'bulk'), required=True)
    parser.add_argument('--midpoints', required=True)
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--worker-hour-cap', type=float, default=1)
    parser.add_argument('--recompute', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or not 0 < args.worker_hour_cap <= 2:
        raise ValueError('bounded workers and worker hours required')
    campaign = install(args.backend)
    indices = campaign.parse_intervals(args.midpoints)
    sources = proof_sources()
    expected = {i: campaign.load_inputs(i)[2] for i in indices}
    directory = WORK/args.backend
    directory.mkdir(parents=True, exist_ok=True)
    if args.recompute and any(not (directory/f'midpoint_{i:03d}.{ext}').exists()
            for i in indices for ext in ('npz', 'json')):
        raise RuntimeError('complete prior evidence required for independent reproduction')
    completed, failed = [], None
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        try:
            futures = {executor.submit(worker, args.backend, i, expected[i], sources, args.recompute): i for i in indices}
            for future in as_completed(futures, timeout=args.worker_hour_cap*3600/args.workers):
                failed = futures[future]
                completed.append(future.result())
                failed = None
                print(json.dumps(dict(backend=args.backend, completed=len(completed), requested=len(indices))), flush=True)
        except BaseException as error:
            for process in (executor._processes or {}).values():
                process.terminate()
            write_json(directory/f'failure_{time.time_ns()}.json', dict(error=repr(error), interval=failed,
                eigenpair_inclusion=getattr(error, 'eigenpair_inclusion', None), completed=completed))
            raise
    paths = [directory/f'midpoint_{i:03d}.{ext}' for i in indices for ext in ('npz', 'json')]
    record = dict(backend=args.backend, midpoints=indices, points=len(indices),
        files={p.relative_to(ROOT).as_posix(): sha(p) for p in paths},
        independently_reproduced=bool(args.recompute and all(r.get('independently_reproduced') for r in completed)),
        all_physical_Hessian_points_certified=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    write_json(directory/('reproduction.json' if args.recompute else 'manifest.json'), record)


if __name__ == '__main__':
    main()
