"""Attach complete physical endpoint DF errors to midpoint coordinate bounds."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_physical_endpoint_first_errors as endpoint
import certify_n12_gate7_stored_midpoint_kinematic_construction as construction
import certify_n12_gate7_kinematic_causal_arithmetic_envelope as arithmetic
from bhsm.interface import physical_first_midpoint_coordinate_error as combine

RESULT=ROOT/'artifacts/flagship_integration/.physical_first_midpoint_coordinate_error_work'


def build_point(index):
    stem=construction.RESULT/f'midpoint_{index:03d}'
    record=json.loads(stem.with_suffix('.json').read_text());arithmetic.validate_point(record,index)
    if endpoint.campaign.cache.file_sha(stem.with_suffix('.npz'))!=record['data_SHA256']:
        raise RuntimeError('stored kinematic point changed')
    with np.load(stem.with_suffix('.npz')) as source:base={name:source[name].copy() for name in source.files}
    d=np.zeros((2,99,74));radius=np.zeros_like(d);records=[]
    paths=[Path(__file__),Path(combine.__file__),Path(combine.kinematic.__file__),
           Path(combine.kinematic.resolved.__file__),stem.with_suffix('.json'),stem.with_suffix('.npz'),arithmetic.RESULT]
    sources={p.relative_to(ROOT).as_posix():endpoint.campaign.sha(p) for p in paths}
    for side,node in enumerate((index,index+1)):
        if node==0:
            if np.any(base['frames'][side]!=0) or np.any(base['first_derivatives'][side]!=0):
                raise RuntimeError('initial endpoint must be fixed')
            continue
        values,binding,fingerprint=endpoint.load_inputs(node)
        path=endpoint.WORK/f'endpoint_{node:03d}.npz'
        d[side],radius[side],source_record=endpoint.load_cached(path,node,binding,fingerprint)
        for name,key in (('frame','frames'),('axis','axes'),('stored_first','first_derivatives')):
            if not np.array_equal(values[name],base[key][side]):
                raise RuntimeError('endpoint physical DF and midpoint kinematic operands differ')
        records.append(dict(node=node,fingerprint=fingerprint,data_SHA256=source_record['data_SHA256']))
        for p in (path,path.with_suffix('.json')):sources[p.relative_to(ROOT).as_posix()]=endpoint.campaign.sha(p)
        sources.update(binding['sources'])
    arrays,bound=combine.combine_coordinate_errors(base['basis'],base['combined_coordinate_error_mid'],
        base['combined_coordinate_error_radius'],d,radius,float(base['step']),73)
    arrays.update(basis=base['basis'],coordinates=base['approximate_coordinates'],output=base['output'],
                  endpoint_first_error_mid=d,endpoint_first_error_radius=radius)
    payload=dict(interval=index,scope=bound['scope'],coordinate_error=bound,
        physical_endpoint_certificates=records,source_SHA256=sources,
        operand_binary64_SHA256={k:endpoint.campaign.array_sha(v) for k,v in arrays.items()},
        physical_first_derivative_error_enclosed=True,common_projector_derivative_consistency_enclosed=True,
        all_midpoints_covered=False,physical_frame_error_enclosed=False,
        physical_Hessian_error_enclosed=False,neighborhood_remainder_enclosed=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    arithmetic.prior.coordinate._verified_inputs({'inputs':sources})
    return arrays,payload


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--midpoints');group.add_argument('--all-midpoints',action='store_true');args=parser.parse_args()
    envelope=json.loads(arithmetic.RESULT.read_text())
    if (envelope.get('validation_passed') is not True or
            envelope.get('coverage')!=dict(intervals=370,nodes=371,complete=True)):
        raise RuntimeError('complete stored kinematic envelope required')
    arithmetic.prior.coordinate._verified_inputs(envelope)
    indices=list(range(370)) if args.all_midpoints else endpoint.campaign.parse_intervals(args.midpoints)
    RESULT.mkdir(parents=True,exist_ok=True)
    for index in indices:
        arrays,payload=build_point(index);stem=RESULT/f'midpoint_{index:03d}'
        np.savez_compressed(stem.with_suffix('.npz'),**arrays)
        payload['data_SHA256']=endpoint.campaign.cache.file_sha(stem.with_suffix('.npz'))
        stem.with_suffix('.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
        if not args.all_midpoints or (index+1)%50==0 or index==369:
            print(json.dumps(dict(interval=index,coordinate_error=payload['coordinate_error']['combined_coordinate_error'])),flush=True)


if __name__=='__main__':main()
