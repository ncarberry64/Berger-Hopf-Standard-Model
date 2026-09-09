"""Aggregate every noninitial physical endpoint first-derivative error ball."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import json,sys
from pathlib import Path
import numpy as np
from flint import arb,ctx
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_physical_endpoint_first_errors as producer
import certify_n12_gate7_kinematic_causal_arithmetic_envelope as arithmetic
from bhsm.interface import stored_pullback_assembly_error as norms

RESULT=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_PHYSICAL_ENDPOINT_FIRST_ERRORS.json'


def build_payload():
    mid=np.empty((370,99,74));radius=np.empty_like(mid);rows=[];sources={}
    for node in range(1,371):
        _,binding,fingerprint=producer.load_inputs(node)
        path=producer.WORK/f'endpoint_{node:03d}.npz'
        mid[node-1],radius[node-1],record=producer.load_cached(path,node,binding,fingerprint)
        previous=ctx.prec;ctx.prec=512
        try:error=norms._float_upper(norms._norm(mid[node-1])+norms._norm(radius[node-1]))
        finally:ctx.prec=previous
        rows.append(dict(node=node,fingerprint=fingerprint,data_SHA256=record['data_SHA256'],error_frobenius_upper=error))
        for p in (path,path.with_suffix('.json')):sources[p.relative_to(ROOT).as_posix()]=producer.campaign.sha(p)
        for name,digest in binding['sources'].items():
            if name in sources and sources[name]!=digest:raise RuntimeError('conflicting endpoint source binding')
            sources[name]=digest
    for p in (Path(__file__),Path(norms.__file__)):
        sources[p.relative_to(ROOT).as_posix()]=producer.campaign.sha(p)
    arithmetic.prior.coordinate._verified_inputs({'inputs':sources})
    return dict(error_mid=mid,error_radius=radius,nodes=np.arange(1,371)),dict(
        artifact='BHSM_N12_GATE7_PHYSICAL_ENDPOINT_FIRST_ERRORS',
        scope='COMPLETE_PHYSICAL_DF_ERROR_AT_EXACT_NORMALIZED_STORED_ENDPOINT_FRAME_PROJECTORS',
        coverage=dict(noninitial_endpoints=370,required_noninitial_endpoints=370,complete=True),
        inputs=sources,rows=rows,maximum_error_frobenius_upper=max(r['error_frobenius_upper'] for r in rows),
        validation_passed=True,claim_boundary=dict(physical_first_derivative_error_enclosed=True,
            common_projector_derivative_consistency_enclosed=True,initial_endpoint_is_fixed=True,
            physical_frame_error_enclosed=False,physical_Hessian_error_enclosed=False,
            neighborhood_remainder_enclosed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False))


if __name__=='__main__':
    arrays,payload=build_payload();np.savez_compressed(RESULT.with_suffix('.npz'),**arrays)
    payload['data_SHA256']=producer.campaign.cache.file_sha(RESULT.with_suffix('.npz'))
    RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(endpoints=370,maximum_error_frobenius_upper=payload['maximum_error_frobenius_upper'])),flush=True)
