"""Restart-safe physical Hessian error rows at explicitly selected midpoints."""
from __future__ import annotations
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
from flint import arb,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_current_green_signed_transverse_causal_center as center
import certify_n12_gate7_batched_mixed_physical_graph as graph
from bhsm.interface.sparse_arb_mixed_jets import use_optimized_mixed
from bhsm.interface import physical_hessian_row_cache as cache

WORK=ROOT/'artifacts/flagship_integration/.physical_midpoint_hessian_error_work'
PRECISION=256
ALGORITHM='PHYSICAL_MIDPOINT_HESSIAN_ERROR_ARB256_UPPER_TRIANGLE_V1'
LEGACY_FINGERPRINT='58AC4BF8DA3BD91104CE79123D21CCB2283A1F454840DFD750050042C24B007F'
LEGACY_REPORT_SHA='71EDD3D23971690CEBE0E251CBC3463682E008E31DBF9F7403BEED079CEB8B5F'
ORIGINAL_JETS=graph.cert._arb_action_jets
ORIGINAL_EIGEN=graph.cert._eigenline
CONTEXT=None


def sha(path):
    path=Path(path);data=path.read_bytes()
    if path.suffix in ('.py','.md','.json'):data=data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest().upper()


def array_sha(value):
    value=np.asarray(value,dtype=np.float64)
    return hashlib.sha256(str(value.shape).encode()+value.tobytes(order='C')).hexdigest().upper()


def load_inputs(interval):
    if type(interval) is not int or not 0<=interval<370:raise ValueError('midpoint outside 0..369')
    ctx.prec=PRECISION
    inputs=center.center._load_inputs()
    completion,_=center.supplemental._completion(interval,{'inputs':inputs})
    uu,_=center._tensor('midpoint',interval)
    with np.load(center.supplemental._aggregate_path(interval)) as d:
        cu=d['complement_retained'].copy();cc=d['complement_complement'].copy()
    tensor=np.empty((99,99,99))
    tensor[:,:73,:73]=uu;tensor[:,73:,:73]=cu
    tensor[:,:73,73:]=cu.transpose(0,2,1);tensor[:,73:,73:]=cc
    if not np.all(np.isfinite(tensor)) or not np.array_equal(tensor,tensor.transpose(0,2,1)):
        raise RuntimeError('finite symmetric stored quadratic representative required')
    values=dict(state=inputs['midpoint'][0][interval],descriptor=float(inputs['midpoint'][1][interval]),
                weights=inputs['weights'],reference=inputs['reference'],basis=completion.full_basis,tensor=tensor)
    sources=[Path(__file__),Path(graph.__file__),Path(graph.original.__file__),Path(graph.cert.__file__),
             Path(use_optimized_mixed.__wrapped__.__code__.co_filename),Path(graph._batch_scalar.__code__.co_filename),
             Path(cache.__file__)]
    binding=dict(algorithm=ALGORITHM,interval=interval,precision_bits=PRECISION,
        arrays={k:array_sha(v) for k,v in values.items()},
        sources={p.relative_to(ROOT).as_posix():sha(p) for p in sources},
        original_kernel_sha256=graph.original._kernel_sha(),original_provenance=graph.original._provenance())
    fingerprint=hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest().upper()
    return values,binding,fingerprint


def point_directory(interval):return WORK/f'midpoint_{interval:03d}'


def verify_legacy_binding(legacy,current,producer_path,cache_path):
    if (legacy['arrays']!=current['arrays'] or legacy['precision_bits']!=current['precision_bits']
            or legacy['original_kernel_sha256']!=current['original_kernel_sha256']
            or legacy['original_provenance']!=current['original_provenance']):
        raise ValueError('legacy point has different mathematical inputs or physical kernel')
    for name,digest in current['sources'].items():
        if name not in (producer_path,cache_path) and legacy['sources'].get(name)!=digest:
            raise ValueError('legacy computational source differs')


def adopt_first_midpoint():
    """Copy reviewed pilot balls with their original hashes; leave the pilot intact."""
    report_path=ROOT/'tmp/bhsm_first_physical_midpoint_error_pullback_20260909.json'
    if cache.file_sha(report_path)!=LEGACY_REPORT_SHA:raise ValueError('legacy aggregate changed')
    legacy=json.loads(report_path.read_text())
    if legacy['physical_row_fingerprint']!=LEGACY_FINGERPRINT or not legacy['all_rows_present']:
        raise ValueError('legacy full-point coverage missing')
    _,binding,fingerprint=load_inputs(0)
    verify_legacy_binding(legacy['source_binding'],binding,Path(__file__).relative_to(ROOT).as_posix(),
                           Path(cache.__file__).relative_to(ROOT).as_posix())
    for name,digest in legacy['source_binding']['sources'].items():
        if sha(ROOT/name)!=digest:raise ValueError('legacy source evidence changed')
    old_directory=ROOT/'tmp/bhsm_first_physical_midpoint_error_20260909'
    destination=point_directory(0);destination.mkdir(parents=True,exist_ok=True)
    binding_path=destination/'binding.json'
    if binding_path.exists() and json.loads(binding_path.read_text())!=binding:
        raise ValueError('existing canonical point binding differs')
    binding_path.write_text(json.dumps(binding,indent=2,sort_keys=True)+'\n')
    for row in range(99):
        path=old_directory/f'row_{row:03d}.npz';target=destination/path.name
        if cache.file_sha(path)!=legacy['row_data_SHA256'][path.name]:raise ValueError('legacy row changed')
        with np.load(path) as d:
            if int(d['row'])!=row or int(d['precision_bits'])!=PRECISION or str(d['fingerprint'].item())!=LEGACY_FINGERPRINT:
                raise ValueError('legacy row binding differs')
            mid=d['error_mid'].copy();radius=d['error_radius'].copy()
        if target.exists():
            existing_mid,existing_radius,_=cache.load_row(target,row,fingerprint)
            if not np.array_equal(existing_mid,mid) or not np.array_equal(existing_radius,radius):
                raise ValueError('adopted data differs from original pilot')
        else:
            cache.save_row(target,mid,radius,row,fingerprint,
                dict(kind='verified_legacy_adoption',fingerprint=LEGACY_FINGERPRINT,
                     data_SHA256=legacy['row_data_SHA256'][path.name],aggregate_SHA256=LEGACY_REPORT_SHA))
    cache.assemble_rows(destination,fingerprint)
    return dict(interval=0,adopted_rows=99,fingerprint=fingerprint,physical_kernel_rerun=False)


def prepare_worker(interval,expected):
    global CONTEXT
    if CONTEXT is not None and CONTEXT[0]==interval:return CONTEXT[1:]
    values,binding,fingerprint=load_inputs(interval)
    if fingerprint!=expected:raise RuntimeError('worker input binding changed')
    cert=graph.cert
    with use_optimized_mixed(cert):jets=ORIGINAL_JETS(values['state'])
    eigen=ORIGINAL_EIGEN(jets.hessian_arb,jets.hessian_mid,values['reference'])
    def cached_jets(state):
        if not np.array_equal(state,values['state']):raise RuntimeError('cached state mismatch')
        return jets
    def cached_eigen(hessian,midpoint,reference):
        if hessian is not jets.hessian_arb or midpoint is not jets.hessian_mid or not np.array_equal(reference,values['reference']):
            raise RuntimeError('cached eigenline inputs differ')
        return eigen
    cert._arb_action_jets=cached_jets;cert._eigenline=cached_eigen
    CONTEXT=(interval,values,binding,fingerprint)
    return values,binding,fingerprint


def worker(interval,row,expected):
    values,binding,fingerprint=prepare_worker(interval,expected)
    if fingerprint!=expected:raise RuntimeError('cached point fingerprint differs')
    for name,digest in binding['sources'].items():
        if sha(ROOT/name)!=digest:raise RuntimeError('campaign source changed during execution')
    target=point_directory(interval)/f'row_{row:03d}.npz'
    if target.exists():
        cache.load_row(target,row,fingerprint)
        return dict(interval=interval,row=row,reused=True)
    started=time.perf_counter()
    with use_optimized_mixed(graph.cert):
        physical=graph.batched_axis_map(values['state'],values['descriptor'],values['weights'],values['reference'],
                                       values['basis'][:,row],values['basis'][:,row:])
    if physical.shape!=(99,99-row) or not all(v.is_finite() for v in physical.flat):
        raise ArithmeticError('physical Hessian row is incomplete or nonfinite')
    error=np.empty(physical.shape,dtype=object)
    for i,j in np.ndindex(error.shape):error[i,j]=physical[i,j]-arb(float(values['tensor'][i,row,row+j]))
    mid,radius=graph.cert._export(error)
    if not all(arb(float(m),float(r)).contains(e) for m,r,e in zip(mid.flat,radius.flat,error.flat)):
        raise ArithmeticError('outward error export does not contain its Arb source')
    cache.save_row(target,mid,radius,row,fingerprint,dict(kind='computed_arb_error',outward_export_verified=True))
    cache.load_row(target,row,fingerprint)
    return dict(interval=interval,row=row,reused=False,seconds=time.perf_counter()-started)


def parse_intervals(text):
    result=[int(v) for v in text.split(',')]
    if not result or len(set(result))!=len(result) or any(not 0<=v<370 for v in result):
        raise ValueError('explicit distinct midpoint indices 0..369 required')
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--midpoints')
    p.add_argument('--workers',type=int,default=6);p.add_argument('--worker-hour-cap',type=float,default=12)
    p.add_argument('--adopt-first-midpoint',action='store_true');args=p.parse_args()
    if not 1<=args.workers<=6 or not 0<args.worker_hour_cap<=12:raise ValueError('bounded workers and cap required')
    if args.adopt_first_midpoint:print(json.dumps(adopt_first_midpoint()),flush=True)
    if args.midpoints is None:
        if args.adopt_first_midpoint:return
        p.error('explicit --midpoints required')
    intervals=parse_intervals(args.midpoints);bindings={}
    for interval in intervals:
        _,binding,fingerprint=load_inputs(interval);bindings[interval]=fingerprint
        directory=point_directory(interval);directory.mkdir(parents=True,exist_ok=True)
        path=directory/'binding.json'
        if path.exists() and json.loads(path.read_text())!=binding:raise RuntimeError('existing point binding differs')
        path.write_text(json.dumps(binding,indent=2,sort_keys=True)+'\n')
    started=time.monotonic();records=[];state_path=WORK/'active_state.json'
    executor=ProcessPoolExecutor(max_workers=args.workers)
    try:
        futures=[executor.submit(worker,interval,row,bindings[interval]) for interval in intervals for row in range(99)]
        for future in as_completed(futures,timeout=3600*args.worker_hour_cap/args.workers):
            record=future.result();records.append(record)
            state=dict(scope='SELECTED_MIDPOINT_PHYSICAL_HESSIAN_ERRORS_ONLY',terminal=False,
                selected_midpoints=intervals,completed_rows=len(records),requested_rows=len(futures),
                completed_by_midpoint={str(i):sum(r['interval']==i for r in records) for i in intervals},
                elapsed_seconds=time.monotonic()-started,FULL_BHSM_COMPLETE=False)
            state_path.write_text(json.dumps(state,indent=2,sort_keys=True)+'\n')
            if len(records)%33==0 or len(records)==len(futures):print(json.dumps(state),flush=True)
    except BaseException as exc:
        for process in (executor._processes or {}).values():process.terminate()
        executor.shutdown(wait=True,cancel_futures=True)
        failure=dict(error=repr(exc),completed_rows=len(records),elapsed_seconds=time.monotonic()-started)
        (WORK/f'failure_{time.time_ns()}.json').write_text(json.dumps(failure,indent=2)+'\n')
        raise
    else:executor.shutdown(wait=True)
    for interval in intervals:cache.assemble_rows(point_directory(interval),bindings[interval])
    state['terminal']=True;state['complete_selected_points']=True
    state_path.write_text(json.dumps(state,indent=2,sort_keys=True)+'\n')
    print(json.dumps(state),flush=True)


if __name__=='__main__':main()
