"""Bind physical midpoint errors to the completed stored kinematic construction."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_selected_physical_hessian_pullbacks as physical
import certify_n12_gate7_stored_midpoint_kinematic_construction as construction
import certify_n12_gate7_kinematic_causal_arithmetic_envelope as arithmetic
from bhsm.interface import physical_hessian_frozen_pullback as joint


def build_point(index,output_record):
    arrays,physical_record=physical.aggregate_point(index)
    stem=construction.RESULT/f'midpoint_{index:03d}'
    record=json.loads(stem.with_suffix('.json').read_text());arithmetic.validate_point(record,index)
    if physical.campaign.cache.file_sha(stem.with_suffix('.npz'))!=record['data_SHA256']:
        raise RuntimeError('kinematic data changed')
    with np.load(stem.with_suffix('.npz')) as source:
        for left,right in (('basis','basis'),('coordinates','approximate_coordinates'),
                           ('target','stored_target'),('output','output')):
            if not np.array_equal(arrays[left],source[right]):
                raise RuntimeError('physical and kinematic point operands differ')
    if physical_record['physical_source_binding']['arrays']!=record['physical_operand_source_binding']['arrays']:
        raise RuntimeError('physical and kinematic state, tensor or basis differs')
    row=output_record['rows'][index]
    if row['interval']!=index:raise RuntimeError('output certificate ordering differs')
    components=[r for r in row['components'] if r['kind']=='midpoint' and r['index']==index]
    if (len(components)!=1 or components[0]['output_map_SHA256']!=
            arithmetic.prior.maps._array_hash(arrays['output'])):
        raise RuntimeError('physical output map differs from its arithmetic certificate')
    delta=record['construction']['combined_construction_and_solve_error']['combined_operator_norm_upper']
    output_delta=row['output_map_error_bounds']['maps']['midpoint']['operator_error_upper']
    correction,bound=joint.pullback_with_frozen_output(arrays['output'],arrays['error_mid'],
        arrays['error_radius'],arrays['coordinates'],delta,output_delta)
    arrays['correction_center']=correction
    paths=[Path(__file__),Path(joint.__file__),Path(joint.physical.__file__),Path(joint.arithmetic.__file__),
           stem.with_suffix('.json'),stem.with_suffix('.npz'),arithmetic.RESULT,arithmetic.prior.output.RESULT]
    return arrays,dict(interval=index,
        scope='SELECTED_PHYSICAL_HESSIAN_ERROR_WITH_NORMALIZED_STORED_KINEMATICS_AND_FROZEN_OUTPUT_MAP',
        physical_point_certificate=physical_record,kinematic_point_SHA256=physical.campaign.sha(stem.with_suffix('.json')),
        source_SHA256={p.relative_to(ROOT).as_posix():physical.campaign.sha(p) for p in paths},
        combined_coordinate_error_upper=delta,output_map_error_upper=output_delta,physical_error_pullback=bound,
        local_pair_uniform_quadratic_coefficient_upper=bound['local_pair_uniform_quadratic_coefficient_upper'],
        physical_Hessian_at_this_midpoint_enclosed=True,all_midpoints_covered=False,
        first_derivative_physical_error_enclosed=False,common_projector_derivative_consistency_enclosed=False,
        physical_frame_error_enclosed=False,endpoint_hessians_covered=False,
        neighborhood_remainder_enclosed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--midpoints',required=True)
    parser.add_argument('--backend',choices=['original','factored'],default='original');args=parser.parse_args()
    if args.backend=='factored':
        import derive_n12_gate7_factored_physical_hessian_errors as backend
        backend.install_backend()
    envelope=json.loads(arithmetic.RESULT.read_text())
    if (envelope.get('validation_passed') is not True or
            envelope.get('coverage')!=dict(intervals=370,nodes=371,complete=True)):
        raise RuntimeError('complete kinematic arithmetic envelope required')
    arithmetic.prior.coordinate._verified_inputs(envelope)
    output_record=json.loads(arithmetic.prior.output.RESULT.read_text())
    directory=ROOT/f'artifacts/flagship_integration/.joint_{args.backend}_physical_midpoint_error_work'
    directory.mkdir(parents=True,exist_ok=True)
    for index in physical.campaign.parse_intervals(args.midpoints):
        arrays,payload=build_point(index,output_record);stem=directory/f'midpoint_{index:03d}'
        np.savez_compressed(stem.with_suffix('.npz'),**arrays)
        payload['data_SHA256']=physical.campaign.cache.file_sha(stem.with_suffix('.npz'))
        arithmetic.prior.coordinate._verified_inputs({'inputs':payload['source_SHA256']})
        stem.with_suffix('.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(interval=index,backend=args.backend,
            local_pair_error=payload['local_pair_uniform_quadratic_coefficient_upper'])),flush=True)


if __name__=='__main__':main()
