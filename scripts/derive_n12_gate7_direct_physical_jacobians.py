"""Direct ambient DF enclosures at independently reproduced physical HS points."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
import sys
import time
import numpy as np
from flint import arb,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_direct_physical_values as values
from bhsm.interface import sparse_arb_mixed_jets as sparse
WORK=ROOT/'artifacts/flagship_integration/.direct_physical_jacobian_work'
ALGORITHM='DIRECT_PHYSICAL_HS_POINT_AMBIENT_DF_ARB256_NORMALIZED_INDEX24_V1'
PRECISION=256


def file_key(path):
    return path.relative_to(ROOT).as_posix()


def binding():
    manifest_path=values.WORK/'manifest.json'
    receipt_path=values.WORK/'reproduction.json'
    manifest=json.loads(manifest_path.read_text())
    receipt=json.loads(receipt_path.read_text())
    if (manifest.get('endpoints')!=list(range(371)) or manifest.get('midpoints')!=list(range(370))
            or manifest.get('all_741_values_covered') is not True
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or receipt.get('points')!=741 or receipt.get('manifest_SHA256')!=values.sha(manifest_path)):
        raise RuntimeError('complete independently reproduced physical values required')
    required={file_key(values.WORK/f'{stage}_{i:03d}.{ext}')
              for stage,count in (('endpoint',371),('midpoint',370))
              for i in range(count) for ext in ('json','npz')}
    if set(manifest['files'])!=required:
        raise RuntimeError('exact full physical value inventory required')
    values.verify_binding(dict(files=manifest['files']))
    sources=dict(manifest['binding']['files'])
    for path in (Path(__file__),Path(values.__file__),Path(sparse.__file__),manifest_path,receipt_path):
        name,digest=file_key(path),values.sha(path)
        if name in sources and sources[name]!=digest:
            raise RuntimeError('physical value and derivative sources disagree')
        sources[name]=digest
    values.verify_binding(dict(files=sources))
    return dict(algorithm=ALGORITHM,precision_bits=PRECISION,
                python=sys.version,numpy=np.__version__,python_flint=values.flint.__version__,
                value_binding=manifest['binding'],files=sources)


def point_inputs(stage,index,expected):
    if stage not in ('endpoint','midpoint') or type(index) is not int or not 0<=index<(371 if stage=='endpoint' else 370):
        raise ValueError('valid physical derivative point required')
    values.verify_binding(expected)
    x,w,s,reference,_=values.operands()
    dependencies={}
    if stage=='midpoint':
        dependencies={file_key(values.WORK/f'endpoint_{n:03d}.{ext}'):values.sha(values.WORK/f'endpoint_{n:03d}.{ext}')
                      for n in (index,index+1) for ext in ('json','npz')}
    ctx.prec=512
    reference_value,_=values.load_cached(stage,index,expected['value_binding'],dependencies)
    path=values.WORK/f'{stage}_{index:03d}.npz'
    with np.load(path) as data:
        weighted=values.hs.restore_balls(data['weighted_state_mid_q'],data['weighted_state_rad_q'])
    for source in (path,path.with_suffix('.json')):
        dependencies[file_key(source)]=values.sha(source)
    # Each consumed point must also match the full independently reproduced
    # manifest, not merely be a locally self-consistent replacement record.
    manifest=json.loads((values.WORK/'manifest.json').read_text())
    if any(manifest['files'].get(k)!=v for k,v in dependencies.items()):
        raise RuntimeError('physical derivative point differs from paired value manifest')
    ctx.prec=PRECISION
    if stage=='endpoint':
        state,descriptor=x[index],arb(float(s[index]))
    else:
        state=np.array([weighted[j]/arb(float(w[j])) for j in range(98)],dtype=object)
        descriptor=weighted[98]
    return state,descriptor,w,reference,reference_value,dependencies


def load_cached(stage,index,expected,dependencies):
    path=WORK/f'{stage}_{index:03d}.npz'
    record=json.loads(path.with_suffix('.json').read_text())
    proof=record.get('eigenpair_verification',{})
    if (record.get('binding')!=expected or record.get('dependencies')!=dependencies
            or record.get('stage')!=stage or record.get('index')!=index
            or record.get('data_SHA256')!=values.sha(path)
            or proof.get('validation_passed') is not True or proof.get('selected_zero_based_index_verified')!=24
            or proof.get('spectral_index_verification',{}).get('validation_passed') is not True
            or record.get('value_overlaps_paired_direct_value') is not True):
        raise RuntimeError('direct physical derivative cache binding failed')
    with np.load(path) as data:
        df=values.hs.restore_balls(data['DF_mid_q'],data['DF_rad_q'])
    if df.shape!=(99,99):raise RuntimeError('complete ambient 99 by 99 DF required')
    return df,record


def worker(stage,index,expected,recompute=False):
    state,descriptor,weights,reference,reference_value,dependencies=point_inputs(stage,index,expected)
    path=WORK/f'{stage}_{index:03d}.npz'
    previous=None
    if path.exists() or path.with_suffix('.json').exists():
        _,previous=load_cached(stage,index,expected,dependencies)
        if not recompute:return dict(stage=stage,index=index,reused=True)
    directions=np.array([arb(int(i==j)) for i in range(99) for j in range(99)],dtype=object).reshape(99,99)
    checks=[]
    with sparse.use_optimized_mixed(values.cert),values.hs.verified_eigenline(
            values.cert,checks,expected_index=24,normalize_proposal_center=True):
        result=values.cert._rate_enclosure(state,descriptor,weights,reference,directions)
    matrix=np.asarray(result.derivative,dtype=object)
    rate=values.hs.finite_vector(result.value,99)
    if matrix.shape!=(99,99) or not all(v.is_finite() for v in matrix.flat):
        raise ArithmeticError('complete finite physical DF required')
    if len(checks)!=1:raise RuntimeError('one independently verified eigenpair required')
    overlap=all(a.overlaps(b) for a,b in zip(rate,reference_value,strict=True))
    arrays={}
    ctx.prec=512
    raw_state=values.hs.finite_vector(np.r_[state,[descriptor]],99)
    for name,array in (('DF',matrix),('value',rate),('evaluation_raw_state',raw_state)):
        arrays[name+'_mid_q'],arrays[name+'_rad_q']=values.hs.rational_balls(np.asarray(array,dtype=object))
    values.verify_binding(expected);values.verify_binding(dict(files=dependencies))
    candidate=path.with_suffix('.partial.npz')
    np.savez_compressed(candidate,**arrays)
    record=dict(scope='DIRECT_SELECTED_PHYSICAL_HS_POINT_AMBIENT_DF',stage=stage,index=index,
        binding=expected,dependencies=dependencies,data_SHA256=values.sha(candidate),
        eigenpair_verification=checks[0],value_overlaps_paired_direct_value=overlap,
        weighted_augmented_identity_directions=True,midpoint_uncertainty_retained=True,
        physical_branch_continuation_certified=False,physical_quotient_certified=False,
        physical_Z1_recertified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    if not overlap or (previous is not None and record!=previous):
        values.write_json(WORK/f'{stage}_{index:03d}.candidate_failure.json',record)
        raise ArithmeticError('derivative value overlap or independent reproduction failed; candidate preserved')
    if previous is not None:
        candidate.unlink()
        return dict(stage=stage,index=index,reused=False,independently_reproduced=True)
    candidate.replace(path);values.write_json(path.with_suffix('.json'),record)
    load_cached(stage,index,expected,dependencies)
    return dict(stage=stage,index=index,reused=False)


def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all-points',action='store_true');group.add_argument('--midpoints')
    parser.add_argument('--workers',type=int,default=6)
    parser.add_argument('--worker-hour-cap',type=float,default=1)
    parser.add_argument('--recompute',action='store_true')
    args=parser.parse_args()
    indices=list(range(370)) if args.all_points else [int(v) for v in args.midpoints.split(',')]
    if not indices or len(set(indices))!=len(indices) or any(not 0<=i<370 for i in indices):
        raise ValueError('distinct midpoint indices in 0..369 required')
    if not 1<=args.workers<=6 or not 0<args.worker_hour_cap<=24:
        raise ValueError('bounded workers and worker hours required')
    stages=[('endpoint',sorted({j for i in indices for j in (i,i+1)})),('midpoint',indices)]
    WORK.mkdir(parents=True,exist_ok=True);expected=binding()
    if args.recompute and any(not (WORK/f'{stage}_{i:03d}.{ext}').is_file()
            for stage,points in stages for i in points for ext in ('json','npz')):
        raise RuntimeError('independent reproduction requires complete prior selected evidence')
    completed=[];failed_point=None;started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        try:
            for stage,points in stages:
                futures={executor.submit(worker,stage,i,expected,args.recompute):i for i in points}
                remaining=args.worker_hour_cap*3600/args.workers-(time.monotonic()-started)
                for future in as_completed(futures,timeout=max(0,remaining)):
                    failed_point=dict(stage=stage,index=futures[future]);completed.append(future.result());failed_point=None
                    values.write_json(WORK/'active_state.json',dict(terminal=False,stage=stage,completed=len(completed),
                        requested=sum(len(p) for _,p in stages),elapsed_seconds=time.monotonic()-started,FULL_BHSM_COMPLETE=False))
                    if len(completed)%10==0:print(json.dumps(dict(completed=len(completed),stage=stage)),flush=True)
        except BaseException as error:
            # Python 3.14 provides an executor-owned shutdown; retain a
            # compatibility path for supported earlier Python versions.
            if hasattr(executor,'terminate_workers'):executor.terminate_workers()
            else:
                for process in (executor._processes or {}).values():process.terminate()
            values.write_json(WORK/f'failure_{time.time_ns()}.json',dict(error=repr(error),completed=completed,
                failed_point=failed_point,eigenpair_inclusion=getattr(error,'eigenpair_inclusion',None)))
            raise
    if binding()!=expected:raise RuntimeError('derivative campaign dependencies changed')
    paths=[WORK/f'{stage}_{i:03d}.{ext}' for stage,points in stages for i in points for ext in ('json','npz')]
    report=dict(scope='SELECTED_DIRECT_PHYSICAL_HS_AMBIENT_JACOBIANS',binding=expected,
        endpoints=stages[0][1],midpoints=indices,files={file_key(p):values.sha(p) for p in paths},
        all_741_DF_covered=len(stages[0][1])==371 and len(indices)==370,
        physical_Z1_recertified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    values.write_json(WORK/'manifest.json',report)
    if args.recompute:
        if not all(row.get('independently_reproduced') is True for row in completed):raise RuntimeError('independent point computation required')
        values.write_json(WORK/'reproduction.json',dict(byte_identical=True,independent_recomputation=True,
            manifest_SHA256=values.sha(WORK/'manifest.json'),points=len(completed),FULL_BHSM_COMPLETE=False))
    values.write_json(WORK/'active_state.json',dict(terminal=True,completed=len(completed),FULL_BHSM_COMPLETE=False))
    print(json.dumps(dict(terminal=True,points=len(completed))),flush=True)


if __name__=='__main__':main()
