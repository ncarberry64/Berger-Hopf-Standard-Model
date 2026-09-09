"""Physical endpoint Hessian errors in the 74 exact normalized projector columns."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse,hashlib,json,sys,time
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import numpy as np
from flint import arb,arb_mat,ctx
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_physical_endpoint_first_errors as first
from bhsm.interface import arb_direction_physical_graph as directions_adapter

campaign=first.campaign;graph=campaign.graph;cert=graph.cert;cache=campaign.cache
WORK=ROOT/'artifacts/flagship_integration/.physical_endpoint_hessian_error_work'
ALGORITHM='PHYSICAL_ENDPOINT_HESSIAN_NORMALIZED_PROJECTOR_ARB256_V1'
PRECISION=256;DIMENSION=74
ORIGINAL_JETS=cert._arb_action_jets;ORIGINAL_EIGEN=cert._eigenline
CONTEXT=None;EVALUATE=directions_adapter.build_ball_direction_graph(graph)


def load_inputs(node):
    values,original_binding,_=first.load_inputs(node)
    tensor,basis=campaign.center._tensor('endpoint',node)
    if tensor.shape!=(99,73,73) or basis.shape!=(74,73) or not np.all(np.isfinite(tensor)) or not np.all(np.isfinite(basis)):
        raise ValueError('complete finite stored endpoint tensor and basis required')
    if not np.array_equal(tensor,tensor.transpose(0,2,1)):raise ValueError('symmetric endpoint quadratic representative required')
    values=dict(values,tensor=tensor,transverse_basis=basis)
    sources=dict(original_binding['sources'])
    for path in (Path(__file__),Path(directions_adapter.__file__),Path(graph.__file__),Path(graph.original.__file__),
                 Path(cache.__file__),Path(campaign.center.__file__),Path(campaign.center.scalar_correction_certificate.__file__)):
        sources[path.relative_to(ROOT).as_posix()]=campaign.sha(path)
    binding=dict(algorithm=ALGORITHM,node=node,precision_bits=PRECISION,
        arrays={k:campaign.array_sha(v) for k,v in values.items()},sources=sources,
        first_derivative_operand_binding=original_binding,original_kernel_sha256=graph.original._kernel_sha(),
        original_provenance=graph.original._provenance(),parent_batched_graph_SHA256=directions_adapter.PARENT_FUNCTION_SHA256)
    fingerprint=hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest().upper()
    return values,binding,fingerprint


def exact_projector_directions(frame,axis):
    a=[arb(float(v)) for v in axis];squared=sum((v*v for v in a),arb(0))
    if not squared>0:raise ValueError('nonzero endpoint axis required')
    projector=arb_mat([[int(i==j)-a[i]*a[j]/squared for j in range(len(a))] for i in range(len(a))])
    return cert._array(cert._mat(frame)*projector)


def stored_projected_row(tensors,basis,row):
    """Enclose Q[V.T,V.T] using the exact supplied stored basis and tensor."""
    v=np.asarray(basis,dtype=float)
    if v.ndim!=2 or not 0<=row<v.shape[0] or not np.all(np.isfinite(v)):
        raise ValueError('finite projected basis and valid row required')
    left=arb_mat([[arb(float(x)) for x in v[row]]])
    right=arb_mat([[arb(float(x)) for x in column] for column in v[row:].T])
    if any(q.nrows()!=v.shape[1] or q.ncols()!=v.shape[1] for q in tensors):
        raise ValueError('tensor and projected basis dimensions differ')
    result=np.empty((len(tensors),v.shape[0]-row),dtype=object)
    for output,q in enumerate(tensors):
        product=left*q*right
        for j in range(result.shape[1]):result[output,j]=product[0,j]
    return result


def prepare_worker(node,expected):
    global CONTEXT
    if CONTEXT is not None and CONTEXT['node']==node:
        if CONTEXT['fingerprint']!=expected:raise RuntimeError('cached endpoint fingerprint differs')
        return CONTEXT
    values,binding,fingerprint=load_inputs(node)
    if fingerprint!=expected:raise RuntimeError('endpoint Hessian inputs changed')
    with first.sparse.use_optimized_mixed(cert):jets=ORIGINAL_JETS(values['state'])
    eigen=ORIGINAL_EIGEN(jets.hessian_arb,jets.hessian_mid,values['reference'])
    def cached_jets(state):
        if not np.array_equal(state,values['state']):raise RuntimeError('cached endpoint Hessian state changed')
        return jets
    def cached_eigen(hessian,midpoint,reference):
        if hessian is not jets.hessian_arb or midpoint is not jets.hessian_mid or not np.array_equal(reference,values['reference']):
            raise RuntimeError('cached endpoint Hessian eigenline changed')
        return eigen
    cert._arb_action_jets=cached_jets;cert._eigenline=cached_eigen
    CONTEXT=dict(node=node,values=values,binding=binding,fingerprint=fingerprint,
        directions=exact_projector_directions(values['frame'],values['axis']),
        tensors=[cert._mat(q) for q in values['tensor']])
    return CONTEXT


def point_directory(node):return WORK/f'endpoint_{node:03d}'


def worker(node,row,expected):
    if type(row) is not int or not 0<=row<DIMENSION:raise ValueError('endpoint Hessian row outside 0..73')
    context=prepare_worker(node,expected);v=context['values'];binding=context['binding']
    for name,digest in binding['sources'].items():
        if campaign.sha(ROOT/name)!=digest:raise RuntimeError('endpoint Hessian source changed')
    path=point_directory(node)/f'row_{row:03d}.npz'
    if path.exists():
        cache.load_row(path,row,expected,dimension=DIMENSION)
        return dict(node=node,row=row,reused=True)
    started=time.perf_counter();directions=context['directions']
    with first.factored.use_factored_integrand(cert,v['state']),first.sparse.use_optimized_mixed(cert):
        physical=EVALUATE(v['state'],v['descriptor'],v['weights'],v['reference'],directions[:,row],directions[:,row:])
    target=stored_projected_row(context['tensors'],v['transverse_basis'],row)
    if physical.shape!=(99,DIMENSION-row) or not all(x.is_finite() for x in physical.flat):
        raise ArithmeticError('endpoint physical Hessian row incomplete or nonfinite')
    error=physical-target;mid,radius=cert._export(error)
    if not all(arb(float(m),float(r)).contains(value) for m,r,value in zip(mid.flat,radius.flat,error.flat)):
        raise ArithmeticError('endpoint Hessian outward export lost containment')
    for name,digest in binding['sources'].items():
        if campaign.sha(ROOT/name)!=digest:raise RuntimeError('endpoint Hessian source changed during computation')
    cache.save_row(path,mid,radius,row,expected,
        dict(kind='physical_endpoint_projector_Hessian_minus_exact_stored_projected_tensor',outward_export_verified=True),dimension=DIMENSION)
    cache.load_row(path,row,expected,dimension=DIMENSION)
    return dict(node=node,row=row,reused=False,seconds=time.perf_counter()-started)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--nodes',required=True)
    parser.add_argument('--workers',type=int,default=6);parser.add_argument('--worker-hour-cap',type=float,default=3);args=parser.parse_args()
    if not 1<=args.workers<=6 or not 0<args.worker_hour_cap<=12:raise ValueError('bounded workers and time cap required')
    nodes=first.parse_nodes(args.nodes);bindings={}
    for node in nodes:
        _,binding,fingerprint=load_inputs(node);bindings[node]=fingerprint
        directory=point_directory(node);directory.mkdir(parents=True,exist_ok=True);path=directory/'binding.json'
        if path.exists() and json.loads(path.read_text())!=binding:raise RuntimeError('existing endpoint Hessian binding differs')
        path.write_text(json.dumps(binding,indent=2,sort_keys=True)+'\n')
    started=time.monotonic();records=[];executor=ProcessPoolExecutor(max_workers=args.workers)
    try:
        futures=[executor.submit(worker,node,row,bindings[node]) for node in nodes for row in range(DIMENSION)]
        for future in as_completed(futures,timeout=3600*args.worker_hour_cap/args.workers):
            records.append(future.result())
            state=dict(scope='SELECTED_ENDPOINT_PHYSICAL_HESSIAN_ERRORS_AT_EXACT_STORED_FRAME_PROJECTORS',terminal=False,
                selected_nodes=nodes,completed_rows=len(records),requested_rows=len(futures),
                completed_by_endpoint={str(n):sum(r['node']==n for r in records) for n in nodes},
                elapsed_seconds=time.monotonic()-started,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
            (WORK/'active_state.json').write_text(json.dumps(state,indent=2,sort_keys=True)+'\n')
            if len(records)%37==0 or len(records)==len(futures):print(json.dumps(state),flush=True)
    except BaseException as exc:
        for process in (executor._processes or {}).values():process.terminate()
        executor.shutdown(wait=True,cancel_futures=True)
        (WORK/f'failure_{time.time_ns()}.json').write_text(json.dumps(dict(error=repr(exc),completed_rows=len(records)),indent=2)+'\n')
        raise
    else:executor.shutdown(wait=True)
    for node in nodes:cache.assemble_rows(point_directory(node),bindings[node],dimension=DIMENSION)
    state['terminal']=True;state['selected_nodes_complete']=True
    (WORK/'active_state.json').write_text(json.dumps(state,indent=2,sort_keys=True)+'\n')
    print(json.dumps(state),flush=True)


if __name__=='__main__':main()
