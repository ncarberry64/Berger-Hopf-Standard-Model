"""Include complete physical midpoint DF incidence in the existing causal bound."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import json,sys
from pathlib import Path
import numpy as np
from flint import arb,ctx
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_physical_first_causal_envelope as first
import certify_n12_gate7_physical_midpoint_incidence_errors as incidence

prior=first.prior;k=first.kinematic
RESULT=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_PHYSICAL_INCIDENCE_CAUSAL_ENVELOPE.json'
THEORY=ROOT/'theory/n12_gate7_physical_incidence_causal_envelope.md'


def validate_incidence(record,index,arrays):
    if (record.get('interval')!=index or record.get('scope')!='PHYSICAL_MIDPOINT_DF_AND_FROZEN_ENDPOINT_OUTPUT_CONSTRUCTION_ERROR'
            or record.get('physical_midpoint_DF_incidence_error_enclosed') is not True
            or record.get('combined_endpoint_output_bounds_replace_stored_construction_bounds') is not True
            or set(record.get('output_map_error_bounds',{}))!={'left','right'}):
        raise RuntimeError('matching complete physical incidence/output certificate required')
    if {name:incidence.campaign.array_sha(value) for name,value in arrays.items()}!=record['operand_binary64_SHA256']:
        raise RuntimeError('physical incidence operands changed')


def load_incidence(index):
    stem=incidence.RESULT/f'midpoint_{index:03d}';record=json.loads(stem.with_suffix('.json').read_text())
    if incidence.campaign.cache.file_sha(stem.with_suffix('.npz'))!=record['data_SHA256']:
        raise RuntimeError('physical incidence data changed')
    with np.load(stem.with_suffix('.npz')) as source:arrays={name:source[name].copy() for name in source.files}
    validate_incidence(record,index,arrays)
    sources=dict(record['source_SHA256'])
    for path in (stem.with_suffix('.json'),stem.with_suffix('.npz')):
        first.merge_sources(sources,{path.relative_to(ROOT).as_posix():incidence.campaign.sha(path)})
    return record,arrays,sources


def build_payload():
    base=prior.build_payload();old=json.loads(first.RESULT.read_text())
    if (old.get('artifact')!='BHSM_N12_GATE7_PHYSICAL_FIRST_CAUSAL_ENVELOPE'
            or old.get('scope')!='CAUSAL_ARITHMETIC_AND_PHYSICAL_ENDPOINT_DF_AT_EXACT_STORED_FRAMES'
            or old.get('validation_passed') is not True
            or old.get('coverage')!=dict(intervals=370,nodes=371,noninitial_endpoints=370,complete=True)
            or old.get('causal_maps_SHA256')!=base['causal_maps_SHA256']
            or [r['interval'] for r in old.get('rows',[])]!=list(range(370))):
        raise RuntimeError('complete same-map physical endpoint first-derivative envelope required')
    inputs=dict(base['inputs']);first.merge_sources(inputs,prior.coordinate._verified_inputs(old))
    for path in (Path(__file__),THEORY,first.RESULT,Path(incidence.__file__)):
        first.merge_sources(inputs,{path.relative_to(ROOT).as_posix():incidence.campaign.sha(path)})
    output=json.loads(prior.output.RESULT.read_text())
    coordinate_rows=prior.output._coordinate_rows(json.loads(prior.coordinate.RESULT.read_text()))
    correction_record=json.loads(prior.coordinate.old.scalar_correction_certificate.RESULT.read_text())
    prior.coordinate.old.scalar_correction_certificate.validate_for_consumption(correction_record)
    corrections={(r['kind'],r['index']):r for r in correction_record['rows']}
    rows=[];previous=ctx.prec;ctx.prec=512
    try:
        for index,oldrow in enumerate(old['rows']):
            record,arrays,sources=load_incidence(index);first.merge_sources(inputs,sources)
            physical_stem=first.coordinates.RESULT/f'midpoint_{index:03d}'
            if incidence.campaign.sha(physical_stem.with_suffix('.json'))!=oldrow['physical_coordinate_point_SHA256']:
                raise RuntimeError('physical midpoint coordinates differ from complete envelope')
            with np.load(physical_stem.with_suffix('.npz')) as source:x=source['coordinates'].copy()
            errors=oldrow['combined_coordinate_error'];eu,ec=errors['retained_operator_norm_upper'],errors['complement_operator_norm_upper']
            au,ac=k.assembly._operator(x[:73]),k.assembly._operator(x[73:])
            original=output['rows'][index];correction=corrections['midpoint',index]
            midpoint_error=original['output_map_error_bounds']['maps']['midpoint']
            midpoint=k.output_error.bound_output_error_pullback(
                midpoint_error['operator_error_upper'],midpoint_error['scalar_column_error_upper'],
                k.resolved._float_upper(au+arb(eu)),k.resolved._float_upper(ac+arb(ec)),
                coordinate_rows[index]['tensor_block_frobenius_upper'],correction['projection_rounding_Frobenius_upper'],
                correction['scalar_addition_rounding_Frobenius_upper'])
            components=[]
            for slot,label in enumerate(('left','right')):
                node=index+slot
                if node==0:continue
                candidates=[r for r in original['components'] if r['kind']=='endpoint' and r['index']==node]
                if len(candidates)!=1 or candidates[0]['output_map_SHA256']!=prior.maps._array_hash(arrays['stored_output_maps'][slot]):
                    raise RuntimeError('physical incidence and stored endpoint output operands differ')
                c=candidates[0];bound=record['output_map_error_bounds'][label];correction=corrections['endpoint',node]
                error=k.output_error.bound_output_error_pullback(bound['operator_error_upper'],bound['scalar_column_error_upper'],
                    c['exact_retained_coordinate_norm_upper'],c['exact_complement_coordinate_norm_upper'],c['tensor_block_frobenius_upper'],
                    correction['projection_rounding_Frobenius_upper'],correction['scalar_addition_rounding_Frobenius_upper'])
                components.append(dict(node=node,output_label=label,physical_output_error_frobenius_upper=error))
            output_cross=2*(arb(midpoint)+sum((arb(r['physical_output_error_frobenius_upper']) for r in components),arb(0)))
            local=arb(oldrow['combined_stored_tensor_local_coefficient_upper'])+arb(oldrow['coordinate_storage_cross_local_coefficient_upper'])+output_cross
            rows.append(dict(interval=index,physical_incidence_point_SHA256=incidence.campaign.sha(incidence.RESULT/f'midpoint_{index:03d}.json'),
                combined_stored_tensor_local_coefficient_upper=oldrow['combined_stored_tensor_local_coefficient_upper'],
                coordinate_storage_cross_local_coefficient_upper=oldrow['coordinate_storage_cross_local_coefficient_upper'],
                physical_endpoint_output_components=components,
                physical_output_coordinate_storage_cross_local_coefficient_upper=k.resolved._float_upper(output_cross),
                combined_local_coefficient_upper=k.resolved._float_upper(local)))
            if (index+1)%50==0:print(json.dumps(dict(physical_incidence_composition_intervals=index+1)),flush=True)
        with np.load(prior.center.DATA) as source:maps=source['causal_maps_center'].copy()
        if prior.maps._array_hash(maps)!=base['causal_maps_SHA256']:raise RuntimeError('causal maps changed')
        transport=k.causal.transport_local_errors(maps,np.array([r['combined_local_coefficient_upper'] for r in rows]))
        source_errors=dict(assembly=base['stored_source_error_coefficients']['assembly'],storage=base['stored_source_error_coefficients']['storage'],
            physical_first_incidence_coordinate_storage_and_output_cross=transport['maximum_node_error_norm_upper'])
        combined=prior.envelope.combine_stored_causal_errors(base['reconstructed_response_coefficients'],list(source_errors.values()),
            base['frozen_map_perturbation_gain_upper'],base['fixed_axis_projection_norms_upper'])
        combined.update(all_input_bounds_require_external_verification=False,kinematic_midpoint_construction_rounding_enclosed=True,
            first_derivative_physical_error_enclosed_at_stored_frames=True,physical_midpoint_DF_incidence_error_enclosed=True)
        coefficients=json.loads(prior.center.RESULT.read_text())['coefficients']
        with np.load(prior.center.ENDPOINT.with_suffix('.npz')) as source:ceiling=float(source['independent_signed_descriptors'][-1]/prior.center.cert.TRIAL_DESCRIPTOR_SCALE)
        screen=prior.radii.continuous_two_radius_screen(coefficients['Y'],coefficients['Z1'],coefficients['central_quadratic'],
            coefficients['mixed_quadratic'],combined['frozen_map_transverse_quadratic_coefficients_upper'],ceiling)
    finally:ctx.prec=previous
    prior.coordinate._verified_inputs({'inputs':inputs})
    return dict(artifact='BHSM_N12_GATE7_PHYSICAL_INCIDENCE_CAUSAL_ENVELOPE',
        scope='CAUSAL_ARITHMETIC_WITH_PHYSICAL_ENDPOINT_DF_AND_MIDPOINT_DF_INCIDENCE_AT_STORED_FRAMES',
        coverage=dict(intervals=370,nodes=371,noninitial_endpoints=370,complete=True),inputs=inputs,rows=rows,
        causal_maps_SHA256=base['causal_maps_SHA256'],axes_SHA256=base['axes_SHA256'],
        replaced_prior_terms=['physical_first_coordinate_storage_and_output_cross'],source_error_coefficients=source_errors,
        transport=transport,arithmetic_envelope=combined,stored_polynomial_adjudication=screen,validation_passed=True,
        claim_boundary=dict(physical_endpoint_DF_coordinate_errors_enclosed=True,physical_midpoint_DF_incidence_error_enclosed=True,
            combined_output_bounds_replace_previous_endpoint_output_bounds=True,physical_Hessian_error_enclosed=False,
            physical_frame_error_enclosed=False,Y_Z1_central_mixed_coefficients_not_recertified_here=True,
            neighborhood_remainder_enclosed=False,physical_contraction_proved=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False))


if __name__=='__main__':
    payload=build_payload();RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(coefficients=payload['arithmetic_envelope']['frozen_map_transverse_quadratic_coefficients_upper'],
        status=payload['stored_polynomial_adjudication']['status'])),flush=True)
