"""Transport resolved U/C coordinate errors through the same stored center."""
import json
from pathlib import Path
import sys

import numpy as np
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'scripts'))

import certify_n12_gate7_current_green_midpoint_coordinate_pullback as old
import certify_n12_gate7_stored_rounding_causal_transport as storage
from bhsm.interface import resolved_midpoint_coordinate_error as resolved
from bhsm.interface import current_green_causal_error as causal_error
from bhsm.interface import current_green_stored_tensor_error as tensor_error
from bhsm.interface import nonnegative_two_radius_screen as radii

center = old.causal
RESULT = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_RESOLVED_COORDINATE_CAUSAL_TRANSPORT.json'
THEORY = ROOT/'theory/n12_gate7_resolved_coordinate_causal_transport.md'


def _verified_inputs(record):
    inputs = record.get('inputs', {})
    if not inputs:
        raise RuntimeError('Certificate has no input bindings')
    for name, digest in inputs.items():
        path = (ROOT/name).resolve()
        if not path.is_relative_to(ROOT.resolve()) or center._sha(path) != digest:
            raise RuntimeError(f'Certificate input changed: {name}')
    return inputs


def _coordinate_rows(record):
    if (record.get('artifact') != 'BHSM_N12_GATE7_MIDPOINT_COORDINATE_PULLBACK'
            or record.get('validation_passed') is not True
            or record.get('scope') != 'COORDINATE_ERROR_THROUGH_EXACT_STORED_BINARY64_TENSOR_ONLY'
            or record.get('coverage') != dict(verified_midpoints=370, required_midpoints=370, complete=True)):
        raise RuntimeError('Complete existing coordinate certificate required')
    rows = record.get('rows', [])
    if len(rows) != 370 or [r.get('interval') for r in rows] != list(range(370)):
        raise RuntimeError('All 370 ordered coordinate records required')
    return rows


def _verify_operands(row, operands):
    hashes = {name: old.coordinate._array_hash(value) for name, value in operands.items()}
    if hashes != row.get('operand_binary64_SHA256'):
        raise RuntimeError(f"Previously certified coordinate operands changed: {row.get('interval')}")
    return hashes


def build_payload():
    record = json.loads(old.RESULT.read_text())
    old_rows = _coordinate_rows(record)
    center_record = json.loads(center.RESULT.read_text())
    storage_record = json.loads(storage.RESULT.read_text())
    storage_local = json.loads(storage.local.RESULT.read_text())
    storage._local_bounds(storage_local)
    corrected_record = json.loads(old.scalar_correction_certificate.RESULT.read_text())
    corrected_rows = {(r['kind'], r['index']): r for r in corrected_record['rows']}
    if (center_record.get('validation_passed') is not True
            or center_record.get('status') != 'SIGNED_TRANSVERSE_CAUSAL_CENTER_COMPOSED'
            or center_record.get('data_SHA256') != center._sha(center.DATA)):
        raise RuntimeError('Complete unchanged signed center required')
    if (storage_record.get('artifact') != 'BHSM_N12_GATE7_STORED_ROUNDING_CAUSAL_TRANSPORT'
            or storage_record.get('validation_passed') is not True
            or storage_record.get('coverage') != dict(intervals=370, nodes=371, complete=True)):
        raise RuntimeError('Complete stored-rounding causal certificate required')
    sources = (old.RESULT, center.RESULT, center.DATA, storage.RESULT,
               storage.local.RESULT, old.scalar_correction_certificate.RESULT, THEORY,
               Path(__file__).resolve(), Path(resolved.__file__).resolve(),
               Path(causal_error.__file__).resolve(), Path(tensor_error.__file__).resolve(),
               Path(radii.__file__).resolve())
    inputs = {p.relative_to(ROOT).as_posix(): center._sha(p) for p in sources}
    for prior in (record, center_record, storage_record, storage_local):
        for name, digest in _verified_inputs(prior).items():
            if name in inputs and inputs[name] != digest:
                raise RuntimeError(f'Inconsistent input binding: {name}')
            inputs[name] = digest
    geometry = old.supplement._load_geometry()
    original = geometry['inputs']
    midpoint_tangents = original['midpoint'][2]
    with np.load(center.ENDPOINT.with_suffix('.npz')) as source:
        times = source['collocation_arc_parameters'].copy()
        ceiling = float(source['independent_signed_descriptors'][-1] / center.cert.TRIAL_DESCRIPTOR_SCALE)
    with np.load(center.JACOBIAN.with_suffix('.npz')) as source:
        map_tangents = source['endpoint_physical_tangent_action'].copy()
        map_midpoint_tangents = source['midpoint_physical_tangent_action'].copy()
    if not np.array_equal(map_midpoint_tangents, midpoint_tangents):
        raise RuntimeError('Coordinate basis frame differs from the completed center')
    axes = center.component._load_axes()
    with np.load(center.PRECONDITIONER.with_suffix('.npz')) as source:
        right = source['reduced_right_Newton_blocks'].copy()
        left = source['left_Newton_blocks'].copy()
    rows = []
    previous = ctx.prec
    ctx.prec = resolved.PRECISION
    try:
        for index, prior in enumerate(old_rows):
            completion, _ = old.supplement._completion(index, geometry)
            corrected, _ = old.scalar_correction_certificate.correction.corrected_tensor('midpoint', index)
            uu = old.quadratic_representatives.representation.symmetric_center(corrected)
            with np.load(old.supplement._aggregate_path(index)) as source:
                cu = source['complement_retained'].copy()
                cc = source['complement_complement'].copy()
            h = float(times[index+1]-times[index])
            target = center._kinematic_midpoint_map(index, h, axes, map_tangents, map_midpoint_tangents).augmented
            approximate = np.linalg.solve(completion.full_basis, target)
            operands = dict(basis=completion.full_basis, target=target,
                            approximate_coordinates=approximate, retained_retained=uu,
                            complement_retained=cu, complement_complement=cc)
            # The old certificate used raw partition axes. The complete center
            # first normalizes those axes, then its kinematic map normalizes
            # them again; this can change the last bits. Verify the old operands
            # exactly, and independently certify the actual center operands.
            prior_target = center._kinematic_midpoint_map(index, h,
                original['endpoint'][3], original['endpoint'][2], midpoint_tangents).augmented
            prior_operands = dict(operands, target=prior_target,
                approximate_coordinates=np.linalg.solve(completion.full_basis, prior_target))
            prior_hashes = _verify_operands(prior, prior_operands)
            hashes = {name: old.coordinate._array_hash(value) for name, value in operands.items()}
            row = resolved.bound_resolved_coordinate_pullback_error(**operands)
            test = center.cert._frame(map_tangents[index+1], center.cert.TEST_DESCRIPTOR_SCALE).T
            output = 2.0*h*(-np.linalg.solve(right[index], test))/3.0
            norm = tensor_error._matrix_norm_upper(output)
            stored_midpoint = [part for part in storage_local['rows'][index]['components']
                               if part['kind'] == 'midpoint' and part['index'] == index]
            if (len(stored_midpoint) != 1
                    or stored_midpoint[0]['input_map_SHA256'] != old.coordinate._array_hash(approximate[:73])
                    or stored_midpoint[0]['output_map_SHA256'] != old.coordinate._array_hash(output)):
                raise RuntimeError('Stored-rounding maps differ from the actual center pullback')
            scalar_norm = tensor_error._squared_norm(output[:, -1]).sqrt().upper()
            correction = corrected_rows['midpoint', index]
            cross = resolved.bound_storage_coordinate_cross_error(
                row['approximate_retained_coordinates_operator_norm_upper'],
                row['retained_coordinate_error_operator_norm_upper'],
                tensor_error._float_upper(norm), tensor_error._float_upper(scalar_norm),
                correction['projection_rounding_Frobenius_upper'],
                correction['scalar_addition_rounding_Frobenius_upper'])
            # The coordinate pullback already has the concatenated 148 input
            # coordinates. Its squared Euclidean input norm is <=2*r_T^2.
            local_coordinate = 2*norm*arb(row['pullback_coordinate_error_frobenius_upper'])
            local_cross = 2*arb(cross)
            local = local_coordinate + local_cross
            row.update(interval=index, operand_binary64_SHA256=hashes,
                       prior_operand_binary64_SHA256=prior_hashes,
                       center_target_matches_prior_target=bool(np.array_equal(target, prior_target)),
                       historical_coarse_bound_on_raw_axis_target=prior['pullback_coordinate_error_frobenius_upper'],
                       output_map_SHA256=old.coordinate._array_hash(output),
                       output_operator_norm_upper=tensor_error._float_upper(norm),
                       local_coordinate_coefficient_upper=tensor_error._float_upper(local_coordinate),
                       local_storage_coordinate_cross_coefficient_upper=tensor_error._float_upper(local_cross),
                       local_uniform_quadratic_coefficient_upper=tensor_error._float_upper(local))
            rows.append(row)
            if (index+1) % 50 == 0:
                print(json.dumps({'resolved_coordinate_intervals': index+1}), flush=True)
        maps = center.component._causal_maps(map_tangents, left, right)
        with np.load(center.DATA) as source:
            if not np.array_equal(maps, source['causal_maps_center']):
                raise RuntimeError('Causal maps differ from the completed signed center')
        transported = causal_error.transport_local_errors(
            maps, np.asarray([r['local_uniform_quadratic_coefficient_upper'] for r in rows]))
        error_upper = transported['maximum_node_error_norm_upper']
        storage_upper = storage_record['maximum_node_block_sup_quadratic_error_coefficient_upper']
        coeff = center_record['coefficients']
        augmented = [tensor_error._float_upper(arb(v)+arb(error_upper)+arb(storage_upper))
                     for v in coeff['signed_transverse_quadratic_center']]
        screen = radii.continuous_two_radius_screen(coeff['Y'], coeff['Z1'],
            coeff['central_quadratic'], coeff['mixed_quadratic'], augmented, ceiling)
    finally:
        ctx.prec = previous
    _verified_inputs({'inputs': inputs})
    return dict(
        artifact='BHSM_N12_GATE7_RESOLVED_COORDINATE_CAUSAL_TRANSPORT',
        scope='RESOLVED_COORDINATE_AND_STORAGE_CROSS_ERROR_THROUGH_EXACT_STORED_TENSOR_AND_CAUSAL_MAPS_ONLY',
        coverage=dict(intervals=370, nodes=371, complete=True), inputs=inputs, rows=rows,
        causal_maps_SHA256=old.coordinate._array_hash(maps), transport=transported,
        maximum_pullback_coordinate_error_frobenius_upper=max(r['pullback_coordinate_error_frobenius_upper'] for r in rows),
        maximum_causal_coordinate_and_storage_cross_coefficient_upper=error_upper,
        maximum_causal_storage_coefficient_upper=storage_upper,
        center_target_differs_from_prior_target_count=sum(not r['center_target_matches_prior_target'] for r in rows),
        stored_polynomial_with_coordinate_and_storage_error=dict(
            augmented_transverse_coefficients=augmented, adjudication=screen,
            other_physical_and_arithmetic_errors_still_omitted=True),
        validation_passed=True,
        claim_boundary=dict(coordinate_errors_transported_through_exact_stored_causal_maps=True,
            coordinate_storage_cross_error_included=True,
            physical_direction_construction_rounding_enclosed=False, physical_Hessian_error_enclosed=False,
            output_and_causal_map_construction_rounding_enclosed=False,
            pullback_assembly_rounding_enclosed=False, center_covariance_rounding_enclosed=False,
            neighborhood_remainder_enclosed=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False))


def main():
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
    print(json.dumps({
        'maximum_causal_coordinate_and_storage_cross_coefficient_upper': payload['maximum_causal_coordinate_and_storage_cross_coefficient_upper'],
        'augmented_screen_status': payload['stored_polynomial_with_coordinate_and_storage_error']['adjudication']['status'],
        'validation_passed': payload['validation_passed']}), flush=True)


if __name__ == '__main__':
    main()
