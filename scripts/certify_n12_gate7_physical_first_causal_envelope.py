"""Replace stored midpoint-coordinate errors with physical endpoint DF errors."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import json,sys
from pathlib import Path
import numpy as np
from flint import arb,ctx
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_kinematic_causal_arithmetic_envelope as kinematic
import certify_n12_gate7_physical_first_midpoint_coordinates as coordinates
import certify_n12_gate7_physical_endpoint_first_errors as endpoints

prior=kinematic.prior
RESULT=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_PHYSICAL_FIRST_CAUSAL_ENVELOPE.json'
THEORY=ROOT/'theory/n12_gate7_physical_first_causal_envelope.md'


def coordinate_pullback_from_block_bounds(blocks,approximate_norms,error_norms):
    """Local-pair coefficient from certified output-mapped UU, CU, CC bounds."""
    b,a,e=[kinematic.resolved._real_binary64(v,n) for v,n in
           ((blocks,'tensor blocks'),(approximate_norms,'coordinate norms'),(error_norms,'coordinate errors'))]
    if b.shape!=(3,) or a.shape!=(2,) or e.shape!=(2,) or any(np.any(v<0) for v in (b,a,e)):
        raise ValueError('three tensor bounds and two nonnegative coordinate/error bounds required')
    previous=ctx.prec;ctx.prec=512
    try:
        uu,cu,cc=[arb(float(v)) for v in b];au,ac=[arb(float(v)) for v in a];eu,ec=[arb(float(v)) for v in e]
        total=uu*(2*au*eu+eu*eu)+2*cu*(au*ec+ac*eu+eu*ec)+cc*(2*ac*ec+ec*ec)
        return kinematic.resolved._float_upper(2*total)
    finally:ctx.prec=previous


def validate_coordinate_point(record,index,arrays,base):
    expected_nodes=[n for n in (index,index+1) if n!=0]
    if (record.get('interval')!=index
            or record.get('scope')!='PHYSICAL_FIRST_DERIVATIVE_AND_STORED_CONSTRUCTION_COORDINATE_ERROR'
            or record.get('physical_first_derivative_error_enclosed') is not True
            or record.get('common_projector_derivative_consistency_enclosed') is not True
            or [r['node'] for r in record.get('physical_endpoint_certificates',[])]!=expected_nodes
            or record.get('coordinate_error',{}).get('scope')!=record['scope']):
        raise RuntimeError('complete matching physical first-derivative coordinate certificate required')
    if {k:coordinates.endpoint.campaign.array_sha(v) for k,v in arrays.items()}!=record['operand_binary64_SHA256']:
        raise RuntimeError('physical coordinate data or hash changed')
    for name,key in (('basis','basis'),('coordinates','approximate_coordinates'),('output','output')):
        if not np.array_equal(arrays[name],base[key]):
            raise RuntimeError('physical and stored coordinate operands differ')


def merge_sources(target,source):
    for name,digest in source.items():
        if name in target and target[name]!=digest:raise RuntimeError('conflicting physical first-derivative source')
        target[name]=digest


def build_payload():
    old=prior.build_payload()
    stored=json.loads(kinematic.RESULT.read_text())
    if (stored.get('artifact')!='BHSM_N12_GATE7_KINEMATIC_CAUSAL_ARITHMETIC_ENVELOPE'
            or stored.get('scope')!='STORED_CAUSAL_ARITHMETIC_WITH_NORMALIZED_MIDPOINT_CONSTRUCTION_ONLY'
            or stored.get('validation_passed') is not True
            or stored.get('coverage')!=dict(intervals=370,nodes=371,complete=True)
            or stored.get('causal_maps_SHA256')!=old['causal_maps_SHA256']
            or [r['interval'] for r in stored.get('rows',[])]!=list(range(370))):
        raise RuntimeError('complete same-map stored kinematic envelope required')
    inputs=dict(old['inputs']);merge_sources(inputs,prior.coordinate._verified_inputs(stored))
    endpoint_record=json.loads(endpoints.RESULT.read_text())
    if (endpoint_record.get('artifact')!='BHSM_N12_GATE7_PHYSICAL_ENDPOINT_FIRST_ERRORS'
            or endpoint_record.get('scope')!='COMPLETE_PHYSICAL_DF_ERROR_AT_EXACT_NORMALIZED_STORED_ENDPOINT_FRAME_PROJECTORS'
            or endpoint_record.get('validation_passed') is not True
            or endpoint_record.get('coverage')!=dict(noninitial_endpoints=370,required_noninitial_endpoints=370,complete=True)
            or [r['node'] for r in endpoint_record.get('rows',[])]!=list(range(1,371))
            or coordinates.endpoint.campaign.cache.file_sha(endpoints.RESULT.with_suffix('.npz'))!=endpoint_record['data_SHA256']):
        raise RuntimeError('complete physical endpoint DF aggregate required')
    merge_sources(inputs,prior.coordinate._verified_inputs(endpoint_record))
    for path in (Path(__file__),THEORY,kinematic.RESULT,endpoints.RESULT,endpoints.RESULT.with_suffix('.npz')):
        merge_sources(inputs,{path.relative_to(ROOT).as_posix():prior.center._sha(path)})
    endpoint_rows={r['node']:r for r in endpoint_record['rows']}
    coordinate_rows=prior.output._coordinate_rows(json.loads(prior.coordinate.RESULT.read_text()))
    output=json.loads(prior.output.RESULT.read_text())
    correction_path=prior.coordinate.old.scalar_correction_certificate.RESULT
    corrections=json.loads(correction_path.read_text())
    prior.coordinate.old.scalar_correction_certificate.validate_for_consumption(corrections)
    correction_rows={(r['kind'],r['index']):r for r in corrections['rows']}
    rows=[];previous=ctx.prec;ctx.prec=512
    try:
        for index,coordinate_row in enumerate(coordinate_rows):
            stem=coordinates.RESULT/f'midpoint_{index:03d}'
            record=json.loads(stem.with_suffix('.json').read_text())
            if coordinates.endpoint.campaign.cache.file_sha(stem.with_suffix('.npz'))!=record['data_SHA256']:
                raise RuntimeError('physical midpoint-coordinate data changed')
            base_stem=kinematic.construction.RESULT/f'midpoint_{index:03d}'
            base_record=json.loads(base_stem.with_suffix('.json').read_text())
            kinematic.validate_point(base_record,index)
            if prior.center._sha(base_stem.with_suffix('.json'))!=stored['rows'][index]['kinematic_point_SHA256']:
                raise RuntimeError('base kinematic point differs from its complete envelope')
            if coordinates.endpoint.campaign.cache.file_sha(base_stem.with_suffix('.npz'))!=base_record['data_SHA256']:
                raise RuntimeError('base kinematic data changed')
            with np.load(stem.with_suffix('.npz')) as source:arrays={k:source[k].copy() for k in source.files}
            with np.load(base_stem.with_suffix('.npz')) as source:base={k:source[k].copy() for k in source.files}
            validate_coordinate_point(record,index,arrays,base)
            for row in record['physical_endpoint_certificates']:
                if any(row[k]!=endpoint_rows[row['node']][k] for k in ('fingerprint','data_SHA256')):
                    raise RuntimeError('coordinate and complete endpoint certificates differ')
            merge_sources(inputs,record['source_SHA256'])
            for p in (stem.with_suffix('.json'),stem.with_suffix('.npz')):
                merge_sources(inputs,{p.relative_to(ROOT).as_posix():prior.center._sha(p)})
            x,l=arrays['coordinates'],arrays['output']
            bounds=record['coordinate_error']['combined_coordinate_error']
            eu,ec=bounds['retained_operator_norm_upper'],bounds['complement_operator_norm_upper']
            au,ac=kinematic.assembly._operator(x[:73]),kinematic.assembly._operator(x[73:])
            local_coordinate=coordinate_pullback_from_block_bounds(
                base_record['combined_stored_tensor_pullback']['mapped_tensor_block_norms_upper'],
                [kinematic.resolved._float_upper(au),kinematic.resolved._float_upper(ac)],[eu,ec])
            correction=correction_rows['midpoint',index]
            storage_cross=kinematic.resolved.bound_storage_coordinate_cross_error(
                kinematic.resolved._float_upper(au),eu,kinematic.resolved._float_upper(kinematic.assembly._operator(l)),
                kinematic.resolved._float_upper(kinematic.assembly._norm(l[:,-1])),
                correction['projection_rounding_Frobenius_upper'],correction['scalar_addition_rounding_Frobenius_upper'])
            row=output['rows'][index]
            if row['interval']!=index:raise RuntimeError('output certificate ordering differs')
            midpoint=[r for r in row['components'] if r['kind']=='midpoint']
            if len(midpoint)!=1 or midpoint[0]['index']!=index or midpoint[0]['output_map_SHA256']!=prior.maps._array_hash(l):
                raise RuntimeError('same unique certified midpoint output required')
            map_error=row['output_map_error_bounds']['maps']['midpoint']
            midpoint_output=kinematic.output_error.bound_output_error_pullback(
                map_error['operator_error_upper'],map_error['scalar_column_error_upper'],
                kinematic.resolved._float_upper(au+arb(eu)),kinematic.resolved._float_upper(ac+arb(ec)),
                coordinate_row['tensor_block_frobenius_upper'],correction['projection_rounding_Frobenius_upper'],
                correction['scalar_addition_rounding_Frobenius_upper'])
            endpoint_output=sum((arb(r['mapped_output_error_frobenius_upper']) for r in row['components'] if r['kind']=='endpoint'),arb(0))
            local=arb(local_coordinate)+2*(arb(storage_cross)+arb(midpoint_output)+endpoint_output)
            rows.append(dict(interval=index,physical_coordinate_point_SHA256=prior.center._sha(stem.with_suffix('.json')),
                combined_coordinate_error=bounds,combined_stored_tensor_local_coefficient_upper=local_coordinate,
                coordinate_storage_cross_local_coefficient_upper=kinematic.resolved._float_upper(2*arb(storage_cross)),
                output_coordinate_storage_cross_local_coefficient_upper=kinematic.resolved._float_upper(2*(arb(midpoint_output)+endpoint_output)),
                combined_local_coefficient_upper=kinematic.resolved._float_upper(local)))
            if (index+1)%50==0:print(json.dumps(dict(physical_first_composition_intervals=index+1)),flush=True)
        with np.load(prior.center.DATA) as source:maps=source['causal_maps_center'].copy()
        if prior.maps._array_hash(maps)!=old['causal_maps_SHA256']:raise RuntimeError('causal maps differ')
        transport=kinematic.causal.transport_local_errors(maps,np.array([r['combined_local_coefficient_upper'] for r in rows]))
        errors=dict(assembly=old['stored_source_error_coefficients']['assembly'],storage=old['stored_source_error_coefficients']['storage'],
                    physical_first_coordinate_storage_and_output_cross=transport['maximum_node_error_norm_upper'])
        combined=prior.envelope.combine_stored_causal_errors(old['reconstructed_response_coefficients'],list(errors.values()),
            old['frozen_map_perturbation_gain_upper'],old['fixed_axis_projection_norms_upper'])
        combined.update(all_input_bounds_require_external_verification=False,kinematic_midpoint_construction_rounding_enclosed=True,
                        first_derivative_physical_error_enclosed_at_stored_frames=True)
        coefficients=json.loads(prior.center.RESULT.read_text())['coefficients']
        with np.load(prior.center.ENDPOINT.with_suffix('.npz')) as source:
            ceiling=float(source['independent_signed_descriptors'][-1]/prior.center.cert.TRIAL_DESCRIPTOR_SCALE)
        screen=prior.radii.continuous_two_radius_screen(coefficients['Y'],coefficients['Z1'],coefficients['central_quadratic'],
            coefficients['mixed_quadratic'],combined['frozen_map_transverse_quadratic_coefficients_upper'],ceiling)
    finally:ctx.prec=previous
    prior.coordinate._verified_inputs({'inputs':inputs})
    return dict(artifact='BHSM_N12_GATE7_PHYSICAL_FIRST_CAUSAL_ENVELOPE',
        scope='CAUSAL_ARITHMETIC_AND_PHYSICAL_ENDPOINT_DF_AT_EXACT_STORED_FRAMES',
        coverage=dict(intervals=370,nodes=371,noninitial_endpoints=370,complete=True),inputs=inputs,rows=rows,
        causal_maps_SHA256=old['causal_maps_SHA256'],axes_SHA256=old['axes_SHA256'],
        replaced_prior_terms=['kinematic_coordinate_storage_and_output_cross'],source_error_coefficients=errors,
        transport=transport,arithmetic_envelope=combined,stored_polynomial_adjudication=screen,validation_passed=True,
        claim_boundary=dict(physical_first_derivative_error_enclosed_at_stored_frames=True,
            common_projector_derivative_consistency_enclosed=True,coordinate_storage_output_cross_terms_included=True,
            physical_Hessian_error_enclosed=False,physical_frame_error_enclosed=False,
            Y_Z1_central_mixed_coefficients_not_recertified_here=True,neighborhood_remainder_enclosed=False,
            physical_contraction_proved=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False))


if __name__=='__main__':
    payload=build_payload();RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(coefficients=payload['arithmetic_envelope']['frozen_map_transverse_quadratic_coefficients_upper'],
                         status=payload['stored_polynomial_adjudication']['status'])),flush=True)
