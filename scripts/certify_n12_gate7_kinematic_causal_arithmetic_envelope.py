"""Replace coarse coordinate bounds with complete normalized midpoint bounds."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_stored_causal_arithmetic_envelope as prior
import certify_n12_gate7_stored_midpoint_kinematic_construction as construction
from bhsm.interface import current_green_causal_error as causal
from bhsm.interface import frozen_output_map_error as output_error
from bhsm.interface import resolved_midpoint_coordinate_error as resolved
from bhsm.interface import stored_pullback_assembly_error as assembly

RESULT=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_KINEMATIC_CAUSAL_ARITHMETIC_ENVELOPE.json'
THEORY=ROOT/'theory/n12_gate7_kinematic_causal_arithmetic_envelope.md'


def validate_point(record,index):
    if (record.get('interval')!=index
            or record.get('scope')!='NORMALIZED_MIDPOINT_CONSTRUCTION_AND_SOLVE_FROM_EXACT_STORED_OPERANDS'
            or record.get('exact_stored_first_derivatives_only') is not True
            or record.get('construction',{}).get('combined_bound_replaces_stored_target_coordinate_solve_bound') is not True
            or record.get('combined_stored_tensor_pullback',{}).get('scope')!=
                'STORED_OUTPUT_TENSOR_PULLBACK_OF_CERTIFIED_COORDINATE_ERRORS'):
        raise RuntimeError('matching stored midpoint construction certificate required')


def build_payload():
    # Reuse all existing certificate/operand checks; preserve the prior artifact.
    old=prior.build_payload()
    inputs=dict(old['inputs'])
    coordinate=json.loads(prior.coordinate.RESULT.read_text())
    coordinate_rows=prior.output._coordinate_rows(coordinate)
    output=json.loads(prior.output.RESULT.read_text())
    if len(output['rows'])!=370 or [r['interval'] for r in output['rows']]!=list(range(370)):
        raise RuntimeError('complete ordered output-map certificate required')
    correction_path=prior.coordinate.old.scalar_correction_certificate.RESULT
    corrections=json.loads(correction_path.read_text())
    prior.coordinate.old.scalar_correction_certificate.validate_for_consumption(corrections)
    correction_rows={(r['kind'],r['index']):r for r in corrections['rows']}
    paths=[Path(__file__),THEORY,Path(construction.__file__),Path(causal.__file__),
           Path(output_error.__file__),Path(resolved.__file__),Path(assembly.__file__),correction_path]
    for path in paths:inputs[path.relative_to(ROOT).as_posix()]=prior.center._sha(path)
    rows=[];previous=ctx.prec;ctx.prec=512
    try:
        for index,coordinate_row in enumerate(coordinate_rows):
            stem=construction.RESULT/f'midpoint_{index:03d}'
            record=json.loads(stem.with_suffix('.json').read_text())
            validate_point(record,index)
            if construction.campaign.cache.file_sha(stem.with_suffix('.npz'))!=record['data_SHA256']:
                raise RuntimeError('kinematic point data changed')
            for path in (stem.with_suffix('.json'),stem.with_suffix('.npz')):
                inputs[path.relative_to(ROOT).as_posix()]=prior.center._sha(path)
            for group in ('source_SHA256','derivative_source_SHA256'):
                for name,digest in record[group].items():
                    if name in inputs and inputs[name]!=digest:raise RuntimeError('inconsistent construction source')
                    inputs[name]=digest
            prior.coordinate._verified_inputs({'inputs':record['source_SHA256']})
            prior.coordinate._verified_inputs({'inputs':record['derivative_source_SHA256']})
            with np.load(stem.with_suffix('.npz')) as source:
                arrays={name:source[name].copy() for name in source.files}
            hashes={name:construction.campaign.array_sha(arrays[name])
                    for name in record['operand_binary64_SHA256']}
            if hashes!=record['operand_binary64_SHA256']:raise RuntimeError('kinematic operand hash changed')
            values,binding,_=construction.campaign.load_inputs(index)
            if binding!=record['physical_operand_source_binding']:raise RuntimeError('kinematic physical operands changed')
            for name,digest in binding['sources'].items():
                if name in inputs and inputs[name]!=digest:raise RuntimeError('inconsistent physical source')
                inputs[name]=digest
            q=values['tensor'];x=arrays['approximate_coordinates'];l=arrays['output']
            if (construction.campaign.array_sha(arrays['basis'])!=binding['arrays']['basis']
                    or construction.campaign.array_sha(q)!=record['stored_tensor_SHA256']):
                raise RuntimeError('construction basis or stored tensor differs')
            expected=dict(basis=values['basis'],target=arrays['stored_target'],
                approximate_coordinates=x,retained_retained=q[:,:73,:73],
                complement_retained=q[:,73:,:73],complement_complement=q[:,73:,73:])
            if {k:construction.campaign.array_sha(v) for k,v in expected.items()}!=coordinate_row['operand_binary64_SHA256']:
                raise RuntimeError('kinematic and original coordinate operands differ')
            if (construction.campaign.array_sha(l)!=record['output_map_SHA256']
                    or record['output_map_SHA256']!=coordinate_row['output_map_SHA256']):
                raise RuntimeError('kinematic and original output maps differ')
            # load_inputs selects physical Arb256; restore this composition's precision.
            ctx.prec=512
            bound=record['construction']['combined_construction_and_solve_error']
            eu=bound['retained_operator_norm_upper'];ec=bound['complement_operator_norm_upper']
            au=assembly._operator(x[:73]);ac=assembly._operator(x[73:])
            correction=correction_rows['midpoint',index]
            storage_cross=resolved.bound_storage_coordinate_cross_error(
                resolved._float_upper(au),eu,resolved._float_upper(assembly._operator(l)),
                resolved._float_upper(assembly._norm(l[:,-1])),
                correction['projection_rounding_Frobenius_upper'],
                correction['scalar_addition_rounding_Frobenius_upper'])
            endpoint_components=[r for r in output['rows'][index]['components'] if r['kind']=='endpoint']
            midpoint_components=[r for r in output['rows'][index]['components'] if r['kind']=='midpoint']
            if len(midpoint_components)!=1 or midpoint_components[0]['index']!=index:
                raise RuntimeError('unique midpoint output component required')
            map_error=output['rows'][index]['output_map_error_bounds']['maps']['midpoint']
            midpoint_output=output_error.bound_output_error_pullback(
                map_error['operator_error_upper'],map_error['scalar_column_error_upper'],
                resolved._float_upper(au+arb(eu)),resolved._float_upper(ac+arb(ec)),
                coordinate_row['tensor_block_frobenius_upper'],
                correction['projection_rounding_Frobenius_upper'],
                correction['scalar_addition_rounding_Frobenius_upper'])
            endpoints=sum((arb(r['mapped_output_error_frobenius_upper']) for r in endpoint_components),arb(0))
            local_construction=arb(record['combined_stored_tensor_pullback']['local_pair_uniform_quadratic_coefficient_upper'])
            local=local_construction+2*(arb(storage_cross)+arb(midpoint_output)+endpoints)
            rows.append(dict(interval=index,kinematic_point_SHA256=prior.center._sha(stem.with_suffix('.json')),
                combined_stored_tensor_local_coefficient_upper=float(local_construction),
                coordinate_storage_cross_local_coefficient_upper=resolved._float_upper(2*arb(storage_cross)),
                output_coordinate_storage_cross_local_coefficient_upper=resolved._float_upper(2*(arb(midpoint_output)+endpoints)),
                combined_local_coefficient_upper=resolved._float_upper(local)))
            if (index+1)%50==0:print(json.dumps(dict(kinematic_composition_intervals=index+1)),flush=True)
        with np.load(prior.center.DATA) as source:maps=source['causal_maps_center'].copy()
        if construction.campaign.array_sha(maps)!=old['causal_maps_SHA256']:raise RuntimeError('causal maps differ')
        transport=causal.transport_local_errors(maps,np.array([r['combined_local_coefficient_upper'] for r in rows]))
        errors=dict(assembly=old['stored_source_error_coefficients']['assembly'],
            storage=old['stored_source_error_coefficients']['storage'],
            kinematic_coordinate_storage_and_output_cross=transport['maximum_node_error_norm_upper'])
        combined=prior.envelope.combine_stored_causal_errors(old['reconstructed_response_coefficients'],
            list(errors.values()),old['frozen_map_perturbation_gain_upper'],old['fixed_axis_projection_norms_upper'])
        combined['all_input_bounds_require_external_verification']=False
        combined['kinematic_midpoint_construction_rounding_enclosed']=True
        coefficients=json.loads(prior.center.RESULT.read_text())['coefficients']
        with np.load(prior.center.ENDPOINT.with_suffix('.npz')) as source:
            ceiling=float(source['independent_signed_descriptors'][-1]/prior.center.cert.TRIAL_DESCRIPTOR_SCALE)
        screen=prior.radii.continuous_two_radius_screen(coefficients['Y'],coefficients['Z1'],
            coefficients['central_quadratic'],coefficients['mixed_quadratic'],
            combined['frozen_map_transverse_quadratic_coefficients_upper'],ceiling)
    finally:ctx.prec=previous
    prior.coordinate._verified_inputs({'inputs':inputs})
    return dict(artifact='BHSM_N12_GATE7_KINEMATIC_CAUSAL_ARITHMETIC_ENVELOPE',
        scope='STORED_CAUSAL_ARITHMETIC_WITH_NORMALIZED_MIDPOINT_CONSTRUCTION_ONLY',
        coverage=dict(intervals=370,nodes=371,complete=True),inputs=inputs,rows=rows,
        causal_maps_SHA256=old['causal_maps_SHA256'],axes_SHA256=old['axes_SHA256'],
        replaced_prior_terms=['coordinate_and_storage_cross','output_and_coordinate_storage_cross'],
        stored_source_error_coefficients=errors,transport=transport,arithmetic_envelope=combined,
        stored_polynomial_adjudication=screen,validation_passed=True,
        claim_boundary=dict(kinematic_midpoint_construction_rounding_enclosed=True,
            coordinate_storage_output_cross_terms_included=True,physical_Hessian_error_enclosed=False,
            first_derivative_physical_error_enclosed=False,common_projector_derivative_consistency_enclosed=False,
            physical_frame_error_enclosed=False,Y_Z1_central_mixed_coefficients_not_recertified_here=True,
            neighborhood_remainder_enclosed=False,physical_contraction_proved=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False))


if __name__=='__main__':
    payload=build_payload();RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(coefficients=payload['arithmetic_envelope']['frozen_map_transverse_quadratic_coefficients_upper'],
                         status=payload['stored_polynomial_adjudication']['status'])),flush=True)
