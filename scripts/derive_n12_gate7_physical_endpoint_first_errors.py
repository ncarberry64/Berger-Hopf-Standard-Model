"""Bound physical endpoint DF errors at exactly normalized stored projectors."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse,hashlib,inspect,json,sys,time
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_physical_midpoint_hessian_errors as campaign
from bhsm.interface import factored_arb_integrand as factored
from bhsm.interface import independent_arb_contraction_axes as axes_backend
from bhsm.interface import sparse_arb_mixed_jets as sparse
from bhsm.interface import prescribed_arb_action_jet as prescribed

c=campaign.center;cert=c.cert
WORK=ROOT/'artifacts/flagship_integration/.physical_endpoint_first_error_work'
ALGORITHM='PHYSICAL_ENDPOINT_DF_NORMALIZED_PROJECTOR_ARB256_V1'
RATE_SHA256='0DC531574372EAA6C69AFAD3B4790A1C7EF52C18E7BA52B6C8FAAA1D442BFC2C'
PRECISION=256
COMMON=None
ORIGINAL_JETS=cert._arb_action_jets
ORIGINAL_EIGEN=cert._eigenline


def common():
    global COMMON
    if COMMON is None:
        if hashlib.sha256(inspect.getsource(cert._rate_enclosure).encode()).hexdigest().upper()!=RATE_SHA256:
            raise RuntimeError('physical rate graph changed')
        paths=[Path(__file__),Path(campaign.__file__),Path(c.__file__),Path(cert.__file__),
               Path(factored.__file__),Path(axes_backend.__file__),Path(sparse.__file__),Path(prescribed.__file__),
               Path(cert.metric_data.__code__.co_filename),Path(cert.standard_model_casimir_coefficient.__code__.co_filename)]
        COMMON=dict(inputs=c.center._load_inputs(),axes=c.component._load_axes(),
            sources={p.relative_to(ROOT).as_posix():campaign.sha(p) for p in paths},
            provenance=campaign.graph.original._provenance())
    return COMMON


def load_inputs(node):
    if type(node) is not int or not 1<=node<=370:raise ValueError('endpoint node outside 1..370')
    ctx.prec=PRECISION;loaded=common();inputs=loaded['inputs']
    path=c.MIXED_WORK/f'endpoint_{node:03d}.npz'
    with np.load(path) as source:stored=source['first_mid'][:,1:].copy()
    values=dict(state=inputs['endpoint'][0][node],descriptor=float(inputs['endpoint'][1][node]),
        weights=inputs['weights'],reference=inputs['reference'],axis=loaded['axes'][node],
        frame=cert._frame(inputs['endpoint'][2][node],cert.TRIAL_DESCRIPTOR_SCALE),stored_first=stored)
    if stored.shape!=(99,74) or not all(np.all(np.isfinite(v)) for v in values.values()):
        raise ValueError('complete finite endpoint operands required')
    binding=dict(algorithm=ALGORITHM,node=node,precision_bits=PRECISION,rate_function_SHA256=RATE_SHA256,
        arrays={name:campaign.array_sha(value) for name,value in values.items()},sources=loaded['sources'],
        stored_first_source={path.relative_to(ROOT).as_posix():campaign.cache.file_sha(path)},
        original_provenance=loaded['provenance'])
    fingerprint=hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest().upper()
    return values,binding,fingerprint


def validate_arrays(mid,radius):
    if (np.asarray(mid).dtype!=np.dtype('float64') or np.asarray(radius).dtype!=np.dtype('float64')
            or np.shape(mid)!=(99,74) or np.shape(radius)!=(99,74)
            or not np.all(np.isfinite(mid)) or not np.all(np.isfinite(radius)) or np.any(radius<0)):
        raise ValueError('complete finite binary64 endpoint error arrays required')


def load_cached(path,node,binding,fingerprint):
    record=json.loads(path.with_suffix('.json').read_text())
    if (record.get('node')!=node or record.get('binding')!=binding or record.get('fingerprint')!=fingerprint
            or record.get('data_SHA256')!=campaign.cache.file_sha(path)
            or record.get('outward_export_contains_Arb_source') is not True):
        raise RuntimeError('endpoint error cache binding changed')
    with np.load(path) as source:
        if (int(source['node'])!=node or str(source['fingerprint'].item())!=fingerprint
                or int(source['precision_bits'])!=PRECISION):raise RuntimeError('endpoint internal binding differs')
        mid=source['error_mid'].copy();radius=source['error_radius'].copy()
    validate_arrays(mid,radius)
    return mid,radius,record


def worker(node,expected):
    values,binding,fingerprint=load_inputs(node)
    if fingerprint!=expected:raise RuntimeError('endpoint inputs changed')
    for name,digest in binding['sources'].items():
        if campaign.sha(ROOT/name)!=digest:raise RuntimeError('endpoint source changed')
    target=WORK/f'endpoint_{node:03d}.npz'
    if target.exists():
        load_cached(target,node,binding,fingerprint)
        return dict(node=node,reused=True)
    if target.with_suffix('.json').exists():raise RuntimeError('incomplete existing endpoint evidence')
    started=time.perf_counter();a=[arb(float(v)) for v in values['axis']]
    squared=sum((v*v for v in a),arb(0))
    if not squared>0:raise ValueError('nonzero normalized projector axis required')
    projector=arb_mat([[int(i==j)-a[i]*a[j]/squared for j in range(74)] for i in range(74)])
    directions=cert._array(cert._mat(values['frame'])*projector)
    with sparse.use_optimized_mixed(cert):jets=ORIGINAL_JETS(values['state'])
    eigen=ORIGINAL_EIGEN(jets.hessian_arb,jets.hessian_mid,values['reference'])
    def cached_jets(state):
        if not np.array_equal(state,values['state']):raise RuntimeError('cached endpoint state changed')
        return jets
    def cached_eigen(hessian,midpoint,reference):
        if hessian is not jets.hessian_arb or midpoint is not jets.hessian_mid or not np.array_equal(reference,values['reference']):
            raise RuntimeError('cached endpoint eigenline changed')
        return eigen
    cert._arb_action_jets=cached_jets;cert._eigenline=cached_eigen
    try:
        with factored.use_factored_integrand(cert,values['state']),axes_backend.use_independent_contraction_axes(cert),sparse.use_optimized_mixed(cert):
            result=cert._rate_enclosure(values['state'],values['descriptor'],values['weights'],values['reference'],directions)
    finally:cert._arb_action_jets=ORIGINAL_JETS;cert._eigenline=ORIGINAL_EIGEN
    physical=np.asarray(result.derivative,dtype=object)
    if physical.shape!=(99,74) or not all(v.is_finite() for v in physical.flat):
        raise ArithmeticError('incomplete physical endpoint derivative')
    error=np.array([v-arb(float(m)) for v,m in zip(physical.flat,values['stored_first'].flat)],dtype=object).reshape(99,74)
    mid,radius=cert._export(error);validate_arrays(mid,radius)
    if not all(arb(float(m),float(r)).contains(v) for m,r,v in zip(mid.flat,radius.flat,error.flat)):
        raise ArithmeticError('endpoint error export lost containment')
    for name,digest in binding['sources'].items():
        if campaign.sha(ROOT/name)!=digest:raise RuntimeError('endpoint source changed during evaluation')
    temporary=target.with_suffix('.partial.npz')
    np.savez_compressed(temporary,error_mid=mid,error_radius=radius,node=np.asarray(node),
                       fingerprint=np.asarray(fingerprint),precision_bits=np.asarray(PRECISION))
    record=dict(node=node,binding=binding,fingerprint=fingerprint,data_SHA256=campaign.cache.file_sha(temporary),
        scope='PHYSICAL_DF_ERROR_AT_EXACT_NORMALIZED_STORED_ENDPOINT_FRAME_PROJECTOR',
        outward_export_contains_Arb_source=True,physical_frame_error_enclosed=False,
        all_endpoints_covered=False,neighborhood_remainder_enclosed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    temporary.replace(target);metadata=target.with_suffix('.json');temporary=target.with_suffix('.partial.json')
    temporary.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n');temporary.replace(metadata)
    load_cached(target,node,binding,fingerprint)
    return dict(node=node,reused=False,seconds=time.perf_counter()-started)


def parse_nodes(value):
    nodes=[int(v) for v in value.split(',')]
    if not nodes or len(set(nodes))!=len(nodes) or any(not 1<=v<=370 for v in nodes):
        raise ValueError('distinct endpoint nodes 1..370 required')
    return nodes


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--nodes');group.add_argument('--all-endpoints',action='store_true')
    parser.add_argument('--workers',type=int,default=6);parser.add_argument('--worker-hour-cap',type=float,default=3)
    args=parser.parse_args()
    if not 1<=args.workers<=6 or not 0<args.worker_hour_cap<=6:raise ValueError('bounded workers and cap required')
    nodes=list(range(1,371)) if args.all_endpoints else parse_nodes(args.nodes)
    WORK.mkdir(parents=True,exist_ok=True);bindings={node:load_inputs(node)[2] for node in nodes}
    started=time.monotonic();completed=[];executor=ProcessPoolExecutor(max_workers=args.workers)
    state_path=WORK/'active_state.json'
    try:
        futures=[executor.submit(worker,node,bindings[node]) for node in nodes]
        for future in as_completed(futures,timeout=3600*args.worker_hour_cap/args.workers):
            completed.append(future.result())
            state=dict(scope='SELECTED_PHYSICAL_ENDPOINT_FIRST_DERIVATIVE_ERRORS',terminal=False,
                requested_nodes=nodes,completed_nodes=sorted(r['node'] for r in completed),
                completed=len(completed),requested=len(nodes),elapsed_seconds=time.monotonic()-started,
                Gate7_closed=False,FULL_BHSM_COMPLETE=False)
            state_path.write_text(json.dumps(state,indent=2,sort_keys=True)+'\n')
            if len(completed)%25==0 or len(completed)==len(nodes):
                print(json.dumps(dict(completed=len(completed),requested=len(nodes),elapsed_seconds=state['elapsed_seconds'])),flush=True)
    except BaseException as exc:
        for process in (executor._processes or {}).values():process.terminate()
        executor.shutdown(wait=True,cancel_futures=True)
        (WORK/f'failure_{time.time_ns()}.json').write_text(json.dumps(dict(error=repr(exc),completed=len(completed)),indent=2)+'\n')
        raise
    else:executor.shutdown(wait=True)
    for node in nodes:
        _,binding,fingerprint=load_inputs(node);load_cached(WORK/f'endpoint_{node:03d}.npz',node,binding,fingerprint)
    state['terminal']=True;state['selected_nodes_complete']=True
    state_path.write_text(json.dumps(state,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(selected_nodes_complete=True,nodes=len(nodes))),flush=True)


if __name__=='__main__':main()
