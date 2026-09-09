"""Combine selected physical Hessians, physical endpoint DF, and output errors."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_joint_physical_midpoint_error as previous
import certify_n12_gate7_physical_first_causal_envelope as causal


def build_point(index,output):
    arrays,old=previous.build_point(index,output)
    stem=causal.coordinates.RESULT/f'midpoint_{index:03d}'
    record=json.loads(stem.with_suffix('.json').read_text())
    if causal.coordinates.endpoint.campaign.cache.file_sha(stem.with_suffix('.npz'))!=record['data_SHA256']:
        raise RuntimeError('physical first-derivative coordinate data changed')
    with np.load(stem.with_suffix('.npz')) as source:coordinate={k:source[k].copy() for k in source.files}
    causal.validate_coordinate_point(record,index,coordinate,dict(basis=arrays['basis'],
        approximate_coordinates=arrays['coordinates'],output=arrays['output']))
    delta=record['coordinate_error']['combined_coordinate_error']['combined_operator_norm_upper']
    correction,bound=previous.joint.pullback_with_frozen_output(arrays['output'],arrays['error_mid'],
        arrays['error_radius'],arrays['coordinates'],delta,old['output_map_error_upper'])
    arrays['correction_center']=correction
    sources=dict(old['source_SHA256']);causal.merge_sources(sources,record['source_SHA256'])
    for path in (Path(__file__),Path(causal.__file__),causal.THEORY,stem.with_suffix('.json'),stem.with_suffix('.npz')):
        causal.merge_sources(sources,{path.relative_to(ROOT).as_posix():previous.physical.campaign.sha(path)})
    causal.prior.coordinate._verified_inputs({'inputs':sources})
    return arrays,dict(interval=index,
        scope='SELECTED_PHYSICAL_HESSIAN_AND_ENDPOINT_DF_ERRORS_AT_STORED_FRAMES_WITH_FROZEN_OUTPUT_MAP',
        physical_point_certificate=old['physical_point_certificate'],source_SHA256=sources,
        physical_coordinate_point_SHA256=previous.physical.campaign.sha(stem.with_suffix('.json')),
        physical_endpoint_certificates=record['physical_endpoint_certificates'],
        combined_coordinate_error_upper=delta,output_map_error_upper=old['output_map_error_upper'],
        physical_error_pullback=bound,local_pair_uniform_quadratic_coefficient_upper=bound['local_pair_uniform_quadratic_coefficient_upper'],
        physical_Hessian_at_this_midpoint_enclosed=True,physical_first_derivative_error_enclosed_at_stored_frames=True,
        common_projector_derivative_consistency_enclosed=True,all_midpoints_covered=False,
        physical_frame_error_enclosed=False,endpoint_hessians_covered=False,neighborhood_remainder_enclosed=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--midpoints',required=True)
    parser.add_argument('--backend',choices=['original','factored'],default='original');args=parser.parse_args()
    if args.backend=='factored':
        import derive_n12_gate7_factored_physical_hessian_errors as backend
        backend.install_backend()
    envelope=json.loads(previous.arithmetic.RESULT.read_text())
    if envelope.get('validation_passed') is not True or envelope.get('coverage')!=dict(intervals=370,nodes=371,complete=True):
        raise RuntimeError('complete kinematic arithmetic envelope required')
    causal.prior.coordinate._verified_inputs(envelope)
    output=json.loads(causal.prior.output.RESULT.read_text())
    directory=ROOT/f'artifacts/flagship_integration/.physical_first_{args.backend}_hessian_pullback_work'
    directory.mkdir(parents=True,exist_ok=True)
    for index in previous.physical.campaign.parse_intervals(args.midpoints):
        arrays,payload=build_point(index,output);stem=directory/f'midpoint_{index:03d}'
        np.savez_compressed(stem.with_suffix('.npz'),**arrays)
        payload['data_SHA256']=previous.physical.campaign.cache.file_sha(stem.with_suffix('.npz'))
        causal.prior.coordinate._verified_inputs({'inputs':payload['source_SHA256']})
        stem.with_suffix('.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(interval=index,backend=args.backend,local_pair_error=payload['local_pair_uniform_quadratic_coefficient_upper'])),flush=True)


if __name__=='__main__':main()
