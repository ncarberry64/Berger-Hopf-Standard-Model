"""Compose physical center Hessian errors with the complete incidence envelope.

The default requires all 370 midpoint and 370 noninitial endpoint certificates.
An explicit selection computes an isolated additive contribution, never a full
physical bound or a self-map witness with missing errors silently set to zero.
"""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
import argparse
import json
import sys
from pathlib import Path
import numpy as np
from flint import arb, ctx
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_physical_incidence_causal_envelope as incidence
import certify_n12_gate7_physical_endpoint_full_output_pullbacks as endpoint
from bhsm.interface import physical_hessian_causal_error as composition

prior = incidence.prior
campaign = incidence.incidence.campaign
RESULT = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_PHYSICAL_HESSIAN_CAUSAL_ENVELOPE.json'
SELECTED = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_SELECTED_PHYSICAL_HESSIAN_CAUSAL_COMPONENT.json'
THEORY = ROOT/'theory/n12_gate7_physical_hessian_causal_envelope.md'


def bind_file(inputs, path):
    incidence.first.merge_sources(inputs, {path.relative_to(ROOT).as_posix(): campaign.sha(path)})


def read_point(stem, inputs, source_key):
    record = json.loads(stem.with_suffix('.json').read_text())
    if campaign.sha(stem.with_suffix('.npz')) != record['data_SHA256']:
        raise RuntimeError('physical Hessian point data changed')
    with np.load(stem.with_suffix('.npz')) as source:
        arrays = {name: source[name].copy() for name in source.files}
    incidence.first.merge_sources(inputs, record[source_key])
    for suffix in ('.json', '.npz'):
        bind_file(inputs, stem.with_suffix(suffix))
    return record, arrays


def validate_midpoint(record, index):
    if (record.get('interval') != index
            or record.get('scope') != 'SELECTED_PHYSICAL_HESSIAN_AND_ENDPOINT_DF_ERRORS_AT_STORED_FRAMES_WITH_FROZEN_OUTPUT_MAP'
            or any(record.get(key) is not True for key in (
                'physical_Hessian_at_this_midpoint_enclosed',
                'physical_first_derivative_error_enclosed_at_stored_frames',
                'common_projector_derivative_consistency_enclosed'))):
        raise RuntimeError('complete physical midpoint Hessian/DF certificate required')
    point = record['physical_point_certificate']
    if (point.get('interval') != index or point.get('all_rows_present') is not True
            or point.get('direction_pairs') != 4950 or point.get('input_dimension') != 99):
        raise RuntimeError('all 99 physical midpoint Hessian rows required')
    value = record['local_pair_uniform_quadratic_coefficient_upper']
    if value != record['physical_error_pullback']['local_pair_uniform_quadratic_coefficient_upper']:
        raise RuntimeError('midpoint coefficient differs from its pullback certificate')
    return value


def validate_endpoint(record, node):
    if (record.get('node') != node
            or record.get('scope') != 'SELECTED_PHYSICAL_ENDPOINT_HESSIAN_ERROR_WITH_PHYSICAL_MIDPOINT_DF_AND_FROZEN_OUTPUT_CONSTRUCTION'
            or record.get('rows') != 74 or record.get('direction_pairs') != 2775
            or any(record.get(key) is not True for key in (
                'physical_Hessian_at_this_endpoint_enclosed',
                'exact_normalized_projector_direction_errors_included',
                'physical_midpoint_DF_incidence_error_enclosed',
                'combined_output_bound_replaces_stored_construction_bound'))):
        raise RuntimeError('complete physical endpoint Hessian/DF incidence certificate required')
    result = {}
    for row in record['components']:
        key = row['interval'], row['output_label']
        value = row['single_endpoint_quadratic_coefficient_upper']
        if key in result or value != row['physical_error_pullback']['total_error_pullback_frobenius_upper']:
            raise RuntimeError('duplicate or inconsistent endpoint incident coefficient')
        result[key] = value
    if set(result) != {(i, label) for i, label, _ in endpoint.old.incident_slots(node)}:
        raise RuntimeError('complete endpoint incident slots required')
    return result


def load_midpoint(index, inputs, output):
    candidates = [ROOT/f'artifacts/flagship_integration/.physical_first_{b}_hessian_pullback_work/midpoint_{index:03d}'
                  for b in ('original', 'factored')]
    stem = next((p for p in candidates if p.with_suffix('.json').exists()), candidates[0])
    record, arrays = read_point(stem, inputs, 'source_SHA256')
    value = validate_midpoint(record, index)
    operands = record['physical_point_certificate']['operand_binary64_SHA256']
    for key in ('basis', 'coordinates', 'output', 'error_mid', 'error_radius'):
        if campaign.array_sha(arrays[key]) != operands[key]:
            raise RuntimeError('midpoint Hessian pullback operands changed')
    coordinate = incidence.first.coordinates.RESULT/f'midpoint_{index:03d}.json'
    if campaign.sha(coordinate) != record['physical_coordinate_point_SHA256']:
        raise RuntimeError('physical midpoint coordinates changed')
    # The midpoint output does not depend on DF; its construction certificate
    # must nevertheless be the same one used by the full incidence envelope.
    matches = [r for r in output['rows'][index]['components'] if r['kind'] == 'midpoint' and r['index'] == index]
    if len(matches) != 1 or prior.maps._array_hash(arrays['output']) != matches[0]['output_map_SHA256']:
        raise RuntimeError('midpoint output map differs from the causal envelope')
    return value, dict(interval=index, certificate=stem.relative_to(ROOT).as_posix()+'.json',
                       coefficient_upper=value)


def load_endpoint(node, inputs, base):
    stem = endpoint.RESULT/f'endpoint_{node:03d}'
    record, arrays = read_point(stem, inputs, 'inputs')
    values = validate_endpoint(record, node)
    if {k: campaign.array_sha(v) for k, v in arrays.items()} != record['operand_binary64_SHA256']:
        raise RuntimeError('endpoint Hessian pullback operands changed')
    for row in record['components']:
        if row['physical_incidence_point_SHA256'] != base['rows'][row['interval']]['physical_incidence_point_SHA256']:
            raise RuntimeError('endpoint physical incidence differs from the causal envelope')
    return values, dict(node=node, certificate=stem.relative_to(ROOT).as_posix()+'.json',
                        incident_coefficients=[dict(interval=i, output_label=label, coefficient_upper=v)
                                               for (i, label), v in sorted(values.items())])


def build_payload(midpoints, nodes, *, selected_only=False):
    base = json.loads(incidence.RESULT.read_text())
    if (base.get('artifact') != 'BHSM_N12_GATE7_PHYSICAL_INCIDENCE_CAUSAL_ENVELOPE'
            or base.get('validation_passed') is not True
            or base.get('coverage') != dict(intervals=370, nodes=371, noninitial_endpoints=370, complete=True)
            or [r['interval'] for r in base.get('rows', [])] != list(range(370))):
        raise RuntimeError('complete physical incidence causal envelope required')
    inputs = dict(base['inputs'])
    output = json.loads(prior.output.RESULT.read_text())
    if inputs.get(prior.output.RESULT.relative_to(ROOT).as_posix()) != campaign.sha(prior.output.RESULT):
        raise RuntimeError('stored output certificate differs from the incidence envelope')
    mids, ends, midpoint_records, endpoint_records = {}, {}, [], []
    for index in midpoints:
        if index in mids:
            raise ValueError('duplicate midpoint selection')
        mids[index], record = load_midpoint(index, inputs, output)
        midpoint_records.append(record)
    for node in nodes:
        if node in ends:
            raise ValueError('duplicate endpoint selection')
        ends[node], record = load_endpoint(node, inputs, base)
        endpoint_records.append(record)
    assembled = composition.assemble_local_bounds(mids, ends, selected_only=selected_only)
    with np.load(prior.center.DATA) as source:
        maps = source['causal_maps_center'].copy()
    if maps.shape != (370, 74, 74) or prior.maps._array_hash(maps) != base['causal_maps_SHA256']:
        raise RuntimeError('complete matching causal maps required')
    for path in (Path(__file__), THEORY, Path(composition.__file__), Path(incidence.k.causal.__file__),
                 incidence.RESULT, prior.center.DATA, prior.RESULT):
        bind_file(inputs, path)
    prior.coordinate._verified_inputs({'inputs': inputs})
    transport = incidence.k.causal.transport_local_errors(maps, np.array(assembled['local_coefficients_upper']))
    foundation = json.loads(prior.RESULT.read_text())
    if (foundation.get('artifact') != 'BHSM_N12_GATE7_STORED_CAUSAL_ARITHMETIC_ENVELOPE'
            or foundation.get('scope') != 'VERIFIED_STORED_PULLBACK_AND_CAUSAL_COMPOSITION_ARITHMETIC_ONLY'
            or foundation.get('validation_passed') is not True
            or foundation.get('coverage') != dict(intervals=370, nodes=371, complete=True)
            or foundation['causal_maps_SHA256'] != base['causal_maps_SHA256']
            or foundation['axes_SHA256'] != base['axes_SHA256']):
        raise RuntimeError('stored foundation maps or axes differ')
    incidence.first.merge_sources(inputs, prior.coordinate._verified_inputs(foundation))
    # Perturb this new source once. Never apply map_gain to an already lifted
    # total. The full branch below recomposes all raw source errors together.
    previous = ctx.prec
    ctx.prec = 512
    try:
        source = arb(transport['maximum_node_error_norm_upper'])
        gain = arb(foundation['frozen_map_perturbation_gain_upper'])
        if not gain >= 0 or not gain < 1:
            raise RuntimeError('frozen map perturbation gain must lie in [0,1)')
        projections = foundation['fixed_axis_projection_norms_upper']
        additional = [incidence.k.resolved._float_upper(arb(p)*source/(1-gain)) for p in projections]
    finally:
        ctx.prec = previous
    payload = dict(artifact=('BHSM_N12_GATE7_SELECTED_PHYSICAL_HESSIAN_CAUSAL_COMPONENT' if selected_only
                            else 'BHSM_N12_GATE7_PHYSICAL_HESSIAN_CAUSAL_ENVELOPE'),
        scope=assembled['scope'], coverage=assembled['coverage'], inputs=inputs,
        causal_maps_SHA256=base['causal_maps_SHA256'], axes_SHA256=base['axes_SHA256'],
        midpoint_records=midpoint_records, endpoint_records=endpoint_records,
        local_coefficients_upper=assembled['local_coefficients_upper'], transport=transport,
        selected_or_complete_component_frozen_quadratic_coefficients_upper=additional,
        missing_errors_assumed_zero=False, validation_passed=True,
        claim_boundary=dict(complete_center_transverse_Hessian_error_at_stored_frames_enclosed=(not selected_only),
            physical_frame_error_enclosed=False, Y_Z1_central_mixed_coefficients_not_recertified_here=True,
            neighborhood_remainder_enclosed=False, physical_contraction_proved=False,
            Gate7_closed=False, FULL_BHSM_COMPLETE=False))
    if not selected_only:
        errors = dict(base['source_error_coefficients'])
        errors['physical_center_Hessian'] = transport['maximum_node_error_norm_upper']
        combined = prior.envelope.combine_stored_causal_errors(foundation['reconstructed_response_coefficients'],
            list(errors.values()), foundation['frozen_map_perturbation_gain_upper'], projections)
        combined.update(all_input_bounds_require_external_verification=False,
                        complete_center_transverse_Hessian_error_at_stored_frames_enclosed=True)
        coefficients = json.loads(prior.center.RESULT.read_text())['coefficients']
        with np.load(prior.center.ENDPOINT.with_suffix('.npz')) as data:
            ceiling = float(data['independent_signed_descriptors'][-1]/prior.center.cert.TRIAL_DESCRIPTOR_SCALE)
        payload.update(source_error_coefficients=errors, arithmetic_and_center_Hessian_envelope=combined,
            stored_polynomial_adjudication=prior.radii.continuous_two_radius_screen(coefficients['Y'], coefficients['Z1'],
                coefficients['central_quadratic'], coefficients['mixed_quadratic'],
                combined['frozen_map_transverse_quadratic_coefficients_upper'], ceiling))
    prior.coordinate._verified_inputs({'inputs': inputs})
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selected-only', action='store_true')
    parser.add_argument('--midpoints')
    parser.add_argument('--nodes')
    args = parser.parse_args()
    if not args.selected_only and (args.midpoints is not None or args.nodes is not None):
        parser.error('explicit subsets require --selected-only')
    if args.selected_only:
        midpoints = campaign.parse_intervals(args.midpoints) if args.midpoints else []
        nodes = endpoint.old.producer.first.parse_nodes(args.nodes) if args.nodes else []
        if not midpoints and not nodes:
            parser.error('a nonempty explicit selection is required')
    else:
        midpoints, nodes = list(range(370)), list(range(1, 371))
    payload = build_payload(midpoints, nodes, selected_only=args.selected_only)
    path = SELECTED if args.selected_only else RESULT
    path.write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(scope=payload['scope'], complete=payload['coverage']['complete'],
        component_coefficients=payload['selected_or_complete_component_frozen_quadratic_coefficients_upper'])), flush=True)


if __name__ == '__main__':
    main()
