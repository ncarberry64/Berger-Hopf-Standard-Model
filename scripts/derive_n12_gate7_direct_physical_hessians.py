"""Restart-safe complete ambient Hessians at paired actual physical HS points."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import multiprocessing
from pathlib import Path
import sys
import time
import numpy as np
from flint import arb, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_direct_physical_jacobians as df
import certify_n12_gate7_ball_physical_hessian_graph as graph
from bhsm.interface import direct_physical_hessian_base as base
from bhsm.interface import physical_arb_inputs as inputs
from bhsm.interface import ball_factored_arb_integrand as factored
from bhsm.interface import factored_arb_integrand as parent_factored
from bhsm.interface import bulk_arb_matrices as bulk

WORK=ROOT/'artifacts/flagship_integration/.direct_physical_hessian_work'
THEORY=ROOT/'theory/n12_gate7_direct_physical_hessian_campaign.md'
ALGORITHM='DIRECT_PHYSICAL_HS_AMBIENT_HESSIAN_ARB256_BALL_FACTORED_UPPER_TRIANGLE_V1'
PRECISION=256
CONTEXT=None


def encoded(record):
    return (json.dumps(record,indent=2,sort_keys=True)+'\n').encode('utf-8')


def write_json(path,record):
    temporary=path.with_suffix('.partial.json')
    temporary.write_bytes(encoded(record));temporary.replace(path)


def merge(files,additional):
    for name,digest in additional.items():
        if name in files and files[name]!=digest:
            raise RuntimeError(f'inconsistent Hessian source: {name}')
        files[name]=digest


def binding():
    point_inputs=df.binding()
    modules=(graph,graph.parent,graph.parent.original,base,inputs,factored,parent_factored,bulk)
    paths=[Path(__file__),THEORY,*[Path(module.__file__) for module in modules],
           Path(graph._batch_scalar.__code__.co_filename),
           Path(base.verified_eigenline.__wrapped__.__code__.co_filename),
           Path(base._real_binary64.__code__.co_filename),
           ROOT/'theory/n12_gate7_ball_physical_hessian_graph.md']
    kernels={df.file_key(path):df.values.sha(path) for path in paths}
    files=dict(point_inputs['files']);merge(files,kernels)
    df.values.verify_binding(dict(files=files))
    return dict(algorithm=ALGORITHM,precision_bits=PRECISION,
        python=sys.version,numpy=np.__version__,python_flint=df.values.flint.__version__,
        value_point_binding=point_inputs,files=files,kernel_files=kernels,
        direction_basis='EXACT_WEIGHTED_AUGMENTED_AMBIENT_IDENTITY',dimension=99)


def validate_point(stage,index):
    if (stage not in ('endpoint','midpoint') or type(index) is not int
            or not 0<=index<(371 if stage=='endpoint' else 370)):
        raise ValueError('valid actual physical endpoint or midpoint required')


def point_directory(stage,index):
    validate_point(stage,index)
    return WORK/f'{stage}_{index:03d}'


def point_context(stage,index,expected):
    global CONTEXT
    validate_point(stage,index)
    fingerprint=hashlib.sha256(encoded(expected)).hexdigest()
    key=(stage,index,fingerprint)
    ctx.prec=PRECISION
    if CONTEXT is not None and CONTEXT['key']==key:
        return CONTEXT
    state,descriptor,weights,reference,value,dependencies=df.point_inputs(
        stage,index,expected['value_point_binding'])
    if graph.cert is not df.values.cert:
        raise RuntimeError('physical Hessian and paired value kernels differ')
    CONTEXT=dict(key=key,state=state,descriptor=descriptor,weights=weights,reference=reference,
                 value=value,dependencies=dependencies,prepared=None)
    return CONTEXT


def prepare(context):
    if context['prepared'] is None:
        with df.sparse.use_optimized_mixed(graph.cert):
            prepared=base.VerifiedHessianBase(graph.cert,context['state'],context['reference'])
        with prepared.use(),df.sparse.use_optimized_mixed(graph.cert):
            value=graph.cert._rate_enclosure(context['state'],context['descriptor'],context['weights'],
                context['reference'],None).value
        if len(value)!=99 or not all(a.overlaps(b) for a,b in zip(value,context['value'],strict=True)):
            raise ArithmeticError('physical Hessian base differs from paired direct value')
        context['prepared']=prepared
    return context['prepared']


def load_row(stage,index,row,expected,dependencies):
    path=point_directory(stage,index)/f'row_{row:03d}.npz'
    raw=path.with_suffix('.json').read_bytes();record=json.loads(raw)
    proof=record.get('eigenpair_verification',{})
    if (raw!=encoded(record) or record.get('algorithm')!=ALGORITHM
            or record.get('scope')!='DIRECT_SELECTED_PHYSICAL_HS_POINT_AMBIENT_HESSIAN_ROW'
            or record.get('binding')!=expected or record.get('dependencies')!=dependencies
            or record.get('stage')!=stage or record.get('index')!=index or record.get('row')!=row
            or record.get('columns')!=list(range(row,99))
            or record.get('data_SHA256')!=df.values.sha(path)
            or record.get('weighted_augmented_identity_directions') is not True
            or record.get('midpoint_uncertainty_retained') is not True
            or record.get('value_overlaps_paired_direct_value') is not True
            or proof.get('validation_passed') is not True
            or proof.get('proposal_center_normalized_before_verification') is not True
            or proof.get('positive_stored_reference_overlap') is not True
            or proof.get('selected_zero_based_index_verified')!=24
            or proof.get('spectral_index_verification',{}).get('validation_passed') is not True):
        raise RuntimeError('direct physical Hessian row binding failed')
    with np.load(path,allow_pickle=False) as arrays:
        if (set(arrays.files)!={'H_mid_q','H_rad_q'}
                or any(arrays[key].shape!=(99,99-row) for key in arrays.files)):
            raise RuntimeError('complete rational upper-triangle row required')
        # Restoration checks finite entries, rational parsing and nonnegative radii.
        values=df.values.hs.restore_balls(arrays['H_mid_q'],arrays['H_rad_q'])
    return values,record


def worker(stage,index,row,expected,recompute=False):
    if type(row) is not int or not 0<=row<99:
        raise ValueError('row in 0..98 required')
    context=point_context(stage,index,expected)
    directory=point_directory(stage,index);path=directory/f'row_{row:03d}.npz'
    df.values.verify_binding(dict(files=expected['kernel_files']))
    previous=None
    if path.exists() or path.with_suffix('.json').exists():
        _,previous=load_row(stage,index,row,expected,context['dependencies'])
        if not recompute:return dict(row=row,reused=True)
    elif recompute:
        raise RuntimeError('independent row recomputation requires prior evidence')
    prepared=prepare(context)
    axis=np.array([arb(int(i==row)) for i in range(99)],dtype=object)
    directions=np.array([[arb(int(i==j)) for j in range(row,99)] for i in range(99)],dtype=object)
    with prepared.use(),df.sparse.use_optimized_mixed(graph.cert),bulk.use_bulk_matrices(graph.cert),\
            factored.use_ball_factored_integrand(graph.cert,context['state']):
        physical=graph.batched_axis_map(context['state'],context['descriptor'],context['weights'],
            context['reference'],axis,directions)
    if physical.shape!=(99,99-row) or not all(v.is_finite() for v in physical.flat):
        raise ArithmeticError('incomplete or nonfinite physical Hessian row')
    ctx.prec=512
    mid,rad=df.values.hs.rational_balls(physical)
    df.values.verify_binding(dict(files=expected['kernel_files']))
    df.values.verify_binding(dict(files=context['dependencies']))
    candidate=directory/f'row_{row:03d}.candidate_{time.time_ns()}.npz'
    np.savez_compressed(candidate,H_mid_q=mid,H_rad_q=rad)
    record=dict(algorithm=ALGORITHM,scope='DIRECT_SELECTED_PHYSICAL_HS_POINT_AMBIENT_HESSIAN_ROW',
        binding=expected,dependencies=context['dependencies'],stage=stage,index=index,row=row,
        columns=list(range(row,99)),data_SHA256=df.values.sha(candidate),
        eigenpair_verification=prepared.eigenpair_verification,value_overlaps_paired_direct_value=True,
        weighted_augmented_identity_directions=True,midpoint_uncertainty_retained=True,
        complete_point_Hessian=False,physical_branch_continuation_certified=False,
        physical_quotient_identified=False,neighborhood_remainder_enclosed=False,
        physical_contraction_proved=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    if previous is not None:
        if record!=previous:
            write_json(candidate.with_suffix('.json'),record)
            raise ArithmeticError('independent physical Hessian row differs; candidates preserved')
        candidate.unlink()
        return dict(row=row,reused=False,independently_reproduced=True)
    candidate.replace(path);write_json(path.with_suffix('.json'),record)
    return dict(row=row,reused=False)


def complete_manifest(stage,index,expected,dependencies):
    directory=point_directory(stage,index)
    for row in range(99):load_row(stage,index,row,expected,dependencies)
    files={df.file_key(directory/f'row_{row:03d}.{ext}'):df.values.sha(directory/f'row_{row:03d}.{ext}')
           for row in range(99) for ext in ('json','npz')}
    return dict(algorithm=ALGORITHM,stage=stage,index=index,binding=expected,dependencies=dependencies,
        rows=list(range(99)),files=files,complete_point_ambient_Hessian=True,
        representation='99_OUTPUTS_AND_FULL_UPPER_INPUT_TRIANGLE;_LOWER_BY_LOCAL_HESSIAN_SYMMETRY',
        neighborhood_remainder_enclosed=False,physical_quotient_identified=False,
        physical_contraction_proved=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def stop_workers(executor):
    if hasattr(executor,'terminate_workers'):
        executor.terminate_workers()
    else:
        for process in (executor._processes or {}).values():process.terminate()
        executor.shutdown(wait=True,cancel_futures=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',choices=['endpoint','midpoint'],required=True)
    parser.add_argument('--index',type=int,required=True)
    parser.add_argument('--workers',type=int,default=6)
    parser.add_argument('--worker-hour-cap',type=float,default=8)
    parser.add_argument('--recompute',action='store_true')
    parser.add_argument('--preflight',action='store_true')
    args=parser.parse_args();validate_point(args.stage,args.index)
    if not 1<=args.workers<=6 or not 0<args.worker_hour_cap<=24 or (args.preflight and args.recompute):
        raise ValueError('bounded worker count and hours required')
    expected=binding();source=point_context(args.stage,args.index,expected)
    if args.preflight:
        print(json.dumps(dict(point_inputs_verified=True,stage=args.stage,index=args.index,
            requested_rows=99,numerical_Hessian_evaluated=False,FULL_BHSM_COMPLETE=False)),flush=True)
        return
    directory=point_directory(args.stage,args.index);directory.mkdir(parents=True,exist_ok=True)
    manifest_path=directory/'manifest.json'
    previous=None
    if manifest_path.exists():
        previous=json.loads(manifest_path.read_text())
        current=complete_manifest(args.stage,args.index,expected,source['dependencies'])
        if previous!=current or manifest_path.read_bytes()!=encoded(current):
            raise RuntimeError('existing complete Hessian manifest changed')
    if args.recompute and previous is None:
        raise RuntimeError('independent full-point recomputation requires a complete prior manifest')
    receipt_path=directory/'reproduction.json'
    if args.recompute and receipt_path.exists():
        # Preserve an earlier successful receipt as history, but do not leave
        # it advertising success while a new independent attempt can fail.
        receipt_path.replace(directory/f'reproduction.before_attempt_{time.time_ns()}.json')
    started=time.monotonic();completed=[];executor=None;failed_row=None
    try:
        # Fresh spawned processes prevent inheriting a previous campaign's base.
        executor=ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn'))
        futures={executor.submit(worker,args.stage,args.index,row,expected,args.recompute):row for row in range(99)}
        for future in as_completed(futures,timeout=args.worker_hour_cap*3600/args.workers):
            failed_row=futures[future];completed.append(future.result());failed_row=None
            write_json(WORK/'active_state.json',dict(stage=args.stage,index=args.index,completed_rows=len(completed),
                requested_rows=99,recomputing=args.recompute,elapsed_seconds=time.monotonic()-started,
                terminal=False,FULL_BHSM_COMPLETE=False))
            if len(completed)%11==0:print(json.dumps(dict(completed_rows=len(completed),requested_rows=99)),flush=True)
        executor.shutdown(wait=True);executor=None
        df.values.verify_binding(expected)
        df.values.verify_binding(dict(files=source['dependencies']))
        manifest=complete_manifest(args.stage,args.index,expected,source['dependencies'])
        if args.recompute:
            if manifest!=previous or not all(v.get('independently_reproduced') is True for v in completed):
                raise ArithmeticError('independent complete Hessian manifest differs')
            write_json(directory/'reproduction.json',dict(byte_identical=True,independent_recomputation=True,
                fresh_spawned_worker_processes=True,rows=list(range(99)),
                manifest_SHA256=df.values.sha(manifest_path),FULL_BHSM_COMPLETE=False))
        else:
            write_json(manifest_path,manifest)
        write_json(WORK/'active_state.json',dict(stage=args.stage,index=args.index,completed_rows=99,
            requested_rows=99,terminal=True,complete_point_ambient_Hessian=True,
            independently_reproduced=args.recompute,FULL_BHSM_COMPLETE=False))
    except BaseException as error:
        if executor is not None:stop_workers(executor)
        failure=dict(stage=args.stage,index=args.index,failed_row=failed_row,completed_rows=len(completed),
            error=repr(error),eigenpair_failure=getattr(error,'eigenpair_inclusion',None),
            terminal=True,FULL_BHSM_COMPLETE=False)
        write_json(WORK/f'failure_{time.time_ns()}.json',failure)
        write_json(WORK/'active_state.json',failure)
        raise


if __name__=='__main__':main()
