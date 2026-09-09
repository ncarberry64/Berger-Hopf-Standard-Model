"""Combine same-operand stored tensor, assembly, covariance, and map certificates."""
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_signed_covariance_causal_recomposition as covariance
import certify_n12_gate7_resolved_coordinate_causal_transport as coordinate
import certify_n12_gate7_frozen_output_map_construction as output
import certify_n12_gate7_frozen_causal_map_construction as maps
import certify_n12_gate7_stored_pullback_assembly as assembly
from bhsm.interface import stored_causal_arithmetic_envelope as envelope
from bhsm.interface import nonnegative_two_radius_screen as radii

center=coordinate.center
RESULT=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_STORED_CAUSAL_ARITHMETIC_ENVELOPE.json'
THEORY=ROOT/'theory/n12_gate7_stored_causal_arithmetic_envelope.md'


SOURCES=(
    (covariance.RESULT,'BHSM_N12_GATE7_SIGNED_COVARIANCE_CAUSAL_RECOMPOSITION',
     'RECONSTRUCTED_LOCAL_TENSOR_RESPONSE_THROUGH_EXACT_STORED_CAUSAL_MAPS_AND_AXES'),
    (assembly.RESULT,'BHSM_N12_GATE7_STORED_PULLBACK_ASSEMBLY',
     'RECONSTRUCTED_LOCAL_TENSOR_ASSEMBLY_THROUGH_EXACT_STORED_CAUSAL_MAPS_ONLY'),
    (coordinate.RESULT,'BHSM_N12_GATE7_RESOLVED_COORDINATE_CAUSAL_TRANSPORT',
     'RESOLVED_COORDINATE_AND_STORAGE_CROSS_ERROR_THROUGH_EXACT_STORED_TENSOR_AND_CAUSAL_MAPS_ONLY'),
    (coordinate.storage.RESULT,'BHSM_N12_GATE7_STORED_ROUNDING_CAUSAL_TRANSPORT',
     'STORED_ADDITION_AND_PROJECTION_ERROR_THROUGH_EXACT_STORED_CAUSAL_MAPS_ONLY'),
    (output.RESULT,'BHSM_N12_GATE7_FROZEN_OUTPUT_MAP_CONSTRUCTION',
     'FROZEN_OUTPUT_MAP_CONSTRUCTION_WITH_COORDINATE_AND_STORAGE_CROSS_ERRORS_ONLY'),
    (maps.RESULT,'BHSM_N12_GATE7_FROZEN_CAUSAL_MAP_CONSTRUCTION',
     'EXACT_STORED_OPERANDS_AND_FROZEN_INVERSE_CAUSAL_MAP_CONSTRUCTION_ONLY'),
)


def _verify_record(record,artifact,scope,map_hash):
    if (record.get('artifact')!=artifact or record.get('scope')!=scope
            or record.get('validation_passed') is not True
            or record.get('coverage')!=dict(intervals=370,nodes=371,complete=True)
            or record.get('causal_maps_SHA256')!=map_hash):
        raise RuntimeError(f'Complete same-map certificate required: {artifact}')
    return coordinate._verified_inputs(record)


def build_payload():
    with np.load(center.DATA) as d:causal_maps=d['causal_maps_center'].copy()
    if causal_maps.shape!=(370,74,74):raise RuntimeError('Complete center maps required')
    map_hash=maps._array_hash(causal_maps)
    inputs,records={},{}
    for path,artifact,scope in SOURCES:
        record=json.loads(path.read_text())
        records[artifact]=record
        for name,digest in _verify_record(record,artifact,scope,map_hash).items():
            if name in inputs and inputs[name]!=digest:
                raise RuntimeError(f'Inconsistent arithmetic input binding: {name}')
            inputs[name]=digest
    record_center=json.loads(center.RESULT.read_text())
    maps._verify_center(record_center)
    for path in (Path(__file__).resolve(),THEORY,Path(envelope.__file__),Path(radii.__file__),
                 center.RESULT,center.DATA,*(p for p,_,_ in SOURCES),Path(maps.__file__),
                 Path(coordinate.__file__),Path(envelope._real_binary64.__code__.co_filename)):
        name,digest=path.relative_to(ROOT).as_posix(),center._sha(path)
        if name in inputs and inputs[name]!=digest:
            raise RuntimeError('Inconsistent arithmetic source binding')
        inputs[name]=digest
    c=records[SOURCES[0][1]]
    axes=center.component._load_axes()
    if maps._array_hash(axes)!=c['axes_SHA256']:
        raise RuntimeError('Axes differ from the covariance recomposition')
    source_errors={
        'assembly':records[SOURCES[1][1]]['maximum_causal_assembly_error_coefficient_upper'],
        'coordinate_and_storage_cross':records[SOURCES[2][1]]['maximum_causal_coordinate_and_storage_cross_coefficient_upper'],
        'storage':records[SOURCES[3][1]]['maximum_node_block_sup_quadratic_error_coefficient_upper'],
        # Use the stored-map value here. The combined perturbation formula
        # applies the frozen-map source multiplier once to the entire sum.
        'output_and_coordinate_storage_cross':records[SOURCES[4][1]]['maximum_stored_causal_output_error_coefficient_upper'],
    }
    map_gain=records[SOURCES[5][1]]['perturbation']['perturbation_gain_upper']
    projection_norms=envelope.fixed_axis_projection_norms(axes)
    combined=envelope.combine_stored_causal_errors(c['coefficients'],list(source_errors.values()),map_gain,projection_norms)
    combined['all_input_bounds_require_external_verification']=False
    coefficients=record_center['coefficients']
    with np.load(center.ENDPOINT.with_suffix('.npz')) as d:
        ceiling=float(d['independent_signed_descriptors'][-1]/center.cert.TRIAL_DESCRIPTOR_SCALE)
    screen=radii.continuous_two_radius_screen(coefficients['Y'],coefficients['Z1'],
        coefficients['central_quadratic'],coefficients['mixed_quadratic'],
        combined['frozen_map_transverse_quadratic_coefficients_upper'],ceiling)
    coordinate._verified_inputs({'inputs':inputs})
    return dict(artifact='BHSM_N12_GATE7_STORED_CAUSAL_ARITHMETIC_ENVELOPE',
        scope='VERIFIED_STORED_PULLBACK_AND_CAUSAL_COMPOSITION_ARITHMETIC_ONLY',
        coverage=dict(intervals=370,nodes=371,complete=True),inputs=inputs,
        causal_maps_SHA256=map_hash,axes_SHA256=maps._array_hash(axes),
        reconstructed_response_coefficients=c['coefficients'],stored_source_error_coefficients=source_errors,
        frozen_map_perturbation_gain_upper=map_gain,fixed_axis_projection_norms_upper=projection_norms,
        arithmetic_envelope=combined,stored_polynomial_adjudication=screen,
        validation_passed=True,claim_boundary=dict(stored_tensor_pullback_and_causal_composition_arithmetic_enclosed=True,
            coordinate_storage_output_map_cross_errors_included=True,
            covariance_formation_reconciliation_and_propagation_enclosed=True,
            physical_Hessian_error_enclosed=False,physical_direction_construction_rounding_enclosed=False,
            kinematic_midpoint_construction_rounding_enclosed=False,
            physical_ambient_derivative_error_enclosed=False,
            Y_Z1_central_mixed_coefficients_not_recertified_here=True,
            neighborhood_remainder_enclosed=False,physical_contraction_proved=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False))


def main():
    payload=build_payload()
    RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(coefficients=payload['arithmetic_envelope']['frozen_map_transverse_quadratic_coefficients_upper'],
        stored_polynomial_status=payload['stored_polynomial_adjudication']['status'],
        validation_passed=payload['validation_passed'])),flush=True)


if __name__=='__main__':main()
