"""Propagate stored addition/projection error through the 370 local maps.

Requires all scalar corrections, but not the supplemental contractions.
This supplies one local error operand; physical and causal enclosures remain
separate obligations.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
from flint import arb, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'src'))
import certify_n12_gate7_current_green_signed_transverse_causal_center as causal
import certify_n12_gate7_current_green_scalar_covector_correction as corrected
from bhsm.interface import current_green_stored_tensor_error as transport

RESULT=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_STORED_ROUNDING_LOCAL_TRANSPORT.json'

def _array_hash(value):
    return hashlib.sha256(np.asarray(value,dtype='<f8').tobytes(order='C')).hexdigest().upper()

def build_payload():
    certificate=json.loads(corrected.RESULT.read_text())
    corrected.validate_for_consumption(certificate)
    records={(r['kind'],r['index']):r for r in certificate['rows']}
    sources={Path(__file__),Path(transport.__file__),Path(causal.__file__),
        Path(corrected.__file__),Path(corrected.correction.__file__),corrected.RESULT,
        Path(transport._squared_norm.__code__.co_filename),
        Path(causal.supplemental.__file__),Path(causal.center.__file__),
        Path(causal.cert.__file__),Path(causal.component.__file__),
        ROOT/'src/bhsm/interface/current_green_supplemental_midpoint.py',
        causal.JACOBIAN.with_suffix('.npz'),causal.ENDPOINT.with_suffix('.npz'),
        causal.PRECONDITIONER.with_suffix('.npz'),causal.AMBIENT.with_suffix('.npz')}
    sources.update(p.with_suffix('.npz') for p in
                   (causal.center.REPLAY,causal.center.PARTITION,causal.center.SCALAR))
    sources.update(corrected.correction.recovery._path(kind,index) for kind,index in corrected.KEYS)
    sources.update(causal.MIXED_WORK/f'endpoint_{i:03d}.npz' for i in range(1,371))
    inputs={p.relative_to(ROOT).as_posix():causal._sha(p) for p in sources}
    geometry=causal.supplemental._load_geometry()
    axes=causal.component._load_axes()
    with np.load(causal.JACOBIAN.with_suffix('.npz')) as source:
        endpoint_tangents=source['endpoint_physical_tangent_action'].copy()
        midpoint_tangents=source['midpoint_physical_tangent_action'].copy()
    with np.load(causal.ENDPOINT.with_suffix('.npz')) as source:
        times=source['collocation_arc_parameters'].copy()
    with np.load(causal.PRECONDITIONER.with_suffix('.npz')) as source:
        right_blocks=source['reduced_right_Newton_blocks'].copy()
    with np.load(causal.AMBIENT.with_suffix('.npz')) as source:
        ambient=source['ambient_DF_mid'].copy()
    rows=[]
    previous=ctx.prec;ctx.prec=512
    try:
        for index in range(370):
            h=float(times[index+1]-times[index])
            midpoint=causal._kinematic_midpoint_map(index,h,axes,endpoint_tangents,midpoint_tangents)
            completion,_=causal.supplemental._completion(index,geometry)
            midpoint_coordinates=np.linalg.solve(completion.full_basis,midpoint.augmented)[:73]
            test=causal.cert._frame(endpoint_tangents[index+1],causal.cert.TEST_DESCRIPTOR_SCALE).T
            inverse_test=-np.linalg.solve(right_blocks[index],test)
            incidence=inverse_test@ambient[index]
            left_output=h*inverse_test/6+h*h*incidence/12
            right_output=h*inverse_test/6-h*h*incidence/12
            midpoint_output=2*h*inverse_test/3
            components=[]
            for kind,node,left,right in [
                    ('endpoint',index,left_output,None),
                    ('endpoint',index+1,right_output,None),
                    ('midpoint',index,midpoint_output,midpoint_coordinates)]:
                if kind=='endpoint' and node==0:continue
                if right is None:
                    with np.load(corrected.correction.recovery._path(kind,node)) as source:
                        right=source['transverse_basis'].T.copy()
                record=records[kind,node]
                result=transport.bound_stored_tensor_error(left,right,
                    record['projection_rounding_Frobenius_upper'],
                    record['scalar_addition_rounding_Frobenius_upper'])
                result['local_error_bounds_require_external_verification']=False
                result.update(kind=kind,index=node,input_map_SHA256=_array_hash(right),
                              output_map_SHA256=_array_hash(left))
                components.append(result)
            total=sum(arb(row['mapped_total_error_frobenius_upper']) for row in components)
            rows.append(dict(interval=index,components=components,
                local_pair_tensor_error_frobenius_upper=transport._float_upper(total),
                # Each endpoint input has norm <=r, hence its concatenation
                # has squared norm <=2r^2. This is only a local bound.
                local_block_sup_quadratic_error_coefficient_upper=transport._float_upper(2*total)))
    finally:ctx.prec=previous
    if any(causal._sha(ROOT/p)!=digest for p,digest in inputs.items()):
        raise RuntimeError('Stored rounding transport inputs changed')
    corrected.validate_for_consumption(certificate)
    return dict(artifact='BHSM_N12_GATE7_STORED_ROUNDING_LOCAL_TRANSPORT',
        scope='LOCAL_STORED_ROUNDING_THROUGH_EXACT_STORED_MAPS_ONLY',
        coverage=dict(intervals=370,complete=True),rows=rows,inputs=inputs,
        maximum_local_pair_tensor_error_frobenius_upper=max(r['local_pair_tensor_error_frobenius_upper'] for r in rows),
        validation_passed=True,claim_boundary=dict(stored_addition_and_projection_errors_transported_locally=True,
            adjoint_evaluation_error_enclosed=False,physical_Hessian_error_enclosed=False,
            map_construction_rounding_enclosed=False,coordinate_solve_error_enclosed=False,
            pullback_assembly_rounding_enclosed=False,causal_accumulation_enclosed=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False))

def main():
    payload=build_payload()
    RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k not in ('rows','inputs')}))

if __name__=='__main__':main()
