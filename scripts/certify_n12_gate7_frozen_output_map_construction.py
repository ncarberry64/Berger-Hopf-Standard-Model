"""Transport complete frozen output-map arithmetic, including storage cross terms."""
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_resolved_coordinate_causal_transport as coordinate
import certify_n12_gate7_frozen_causal_map_construction as maps_certificate
from bhsm.interface import frozen_output_map_error as output
from bhsm.interface import current_green_causal_error as causal_error
from bhsm.interface.current_green_midpoint_coordinate_error import _squared_norm, _float_upper
from bhsm.interface.resolved_midpoint_coordinate_error import _exact_matrix, _operator_norm_upper

center = coordinate.center
RESULT = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_FROZEN_OUTPUT_MAP_CONSTRUCTION.json'
THEORY = ROOT/'theory/n12_gate7_frozen_output_map_construction.md'


def _coordinate_rows(record):
    if (record.get('artifact') != 'BHSM_N12_GATE7_RESOLVED_COORDINATE_CAUSAL_TRANSPORT'
            or record.get('validation_passed') is not True
            or record.get('scope') != 'RESOLVED_COORDINATE_AND_STORAGE_CROSS_ERROR_THROUGH_EXACT_STORED_TENSOR_AND_CAUSAL_MAPS_ONLY'
            or record.get('coverage') != dict(intervals=370,nodes=371,complete=True)):
        raise RuntimeError('Complete resolved-coordinate certificate required')
    rows = record.get('rows',[])
    if len(rows) != 370 or [r.get('interval') for r in rows] != list(range(370)):
        raise RuntimeError('All 370 ordered coordinate rows required')
    return rows


def _match_output(component, value):
    if component.get('output_map_SHA256') != maps_certificate._array_hash(value):
        raise RuntimeError('Output map differs from the verified stored-rounding pullback')


def build_payload():
    coordinate_record = json.loads(coordinate.RESULT.read_text())
    prior_rows = _coordinate_rows(coordinate_record)
    local_record = json.loads(coordinate.storage.local.RESULT.read_text())
    coordinate.storage._local_bounds(local_record)
    correction_record = json.loads(coordinate.old.scalar_correction_certificate.RESULT.read_text())
    coordinate.old.scalar_correction_certificate.validate_for_consumption(correction_record)
    corrections = {(r['kind'],r['index']):r for r in correction_record['rows']}
    map_record = json.loads(maps_certificate.RESULT.read_text())
    if (map_record.get('artifact') != 'BHSM_N12_GATE7_FROZEN_CAUSAL_MAP_CONSTRUCTION'
            or map_record.get('validation_passed') is not True
            or map_record.get('scope') != 'EXACT_STORED_OPERANDS_AND_FROZEN_INVERSE_CAUSAL_MAP_CONSTRUCTION_ONLY'
            or map_record.get('coverage') != dict(intervals=370,nodes=371,complete=True)):
        raise RuntimeError('Complete frozen causal-map certificate required')
    inputs = {}
    for record in (coordinate_record,local_record,map_record):
        for name,digest in coordinate._verified_inputs(record).items():
            if name in inputs and inputs[name] != digest:
                raise RuntimeError('Conflicting input binding')
            inputs[name] = digest
    sources = (Path(__file__).resolve(),THEORY,coordinate.RESULT,maps_certificate.RESULT,
        coordinate.storage.local.RESULT,coordinate.old.scalar_correction_certificate.RESULT,
        Path(output.__file__),Path(causal_error.__file__),Path(coordinate.__file__),
        Path(maps_certificate.__file__),Path(_exact_matrix.__code__.co_filename),
        Path(_squared_norm.__code__.co_filename))
    for path in sources:
        name,digest = path.relative_to(ROOT).as_posix(),center._sha(path)
        if name in inputs and inputs[name] != digest:
            raise RuntimeError('Conflicting source binding')
        inputs[name] = digest
    with np.load(center.JACOBIAN.with_suffix('.npz')) as source:
        tangents = source['endpoint_physical_tangent_action'].copy()
    with np.load(center.PRECONDITIONER.with_suffix('.npz')) as source:
        right = source['reduced_right_Newton_blocks'].copy()
        left = source['left_Newton_blocks'].copy()
    with np.load(center.ENDPOINT.with_suffix('.npz')) as source:
        times = source['collocation_arc_parameters'].copy()
    with np.load(center.AMBIENT.with_suffix('.npz')) as source:
        ambient = source['ambient_DF_mid'].copy()
    maps = center.component._causal_maps(tangents,left,right)
    if (maps.shape != (370,74,74)
            or maps_certificate._array_hash(maps) != map_record.get('causal_maps_SHA256')
            or maps_certificate._array_hash(maps) != coordinate_record.get('causal_maps_SHA256')):
        raise RuntimeError('Causal maps differ between complete certificates')
    rows, endpoint_norms = [],{}
    previous = ctx.prec
    ctx.prec = 512
    try:
        for i,prior in enumerate(prior_rows):
            h = float(times[i+1]-times[i])
            test = center.cert._frame(tangents[i+1],center.cert.TEST_DESCRIPTOR_SCALE).T
            b = -np.linalg.solve(right[i],test)
            incidence = b@ambient[i]
            stored = np.asarray([h*b/6+h*h*incidence/12,h*b/6-h*h*incidence/12,2*h*b/3])
            map_bounds = output.bound_output_map_errors(right[i],test,ambient[i],h,stored)
            components = []
            for slot,(kind,node,label) in enumerate((('endpoint',i,'left'),
                    ('endpoint',i+1,'right'),('midpoint',i,'midpoint'))):
                if kind == 'endpoint' and node == 0:
                    continue
                stored_components = [r for r in local_record['rows'][i]['components']
                                     if r['kind'] == kind and r['index'] == node]
                if len(stored_components) != 1:
                    raise RuntimeError('Unique stored-rounding component required')
                component = stored_components[0]
                _match_output(component,stored[slot])
                correction = corrections[kind,node]
                if kind == 'midpoint':
                    if (maps_certificate._array_hash(stored[slot]) != prior['output_map_SHA256']
                            or prior['operand_binary64_SHA256']['retained_retained'] != correction['represented_tensor_binary64_SHA256']):
                        raise RuntimeError('Midpoint output differs from resolved-coordinate proof')
                    u = _float_upper(arb(prior['approximate_retained_coordinates_operator_norm_upper'])
                                     +arb(prior['retained_coordinate_error_operator_norm_upper']))
                    c = _float_upper(arb(prior['approximate_complement_coordinates_operator_norm_upper'])
                                     +arb(prior['complement_coordinate_error_operator_norm_upper']))
                    q = prior['tensor_block_frobenius_upper']
                else:
                    if node not in endpoint_norms:
                        tensor,basis = center._tensor(kind,node)
                        input_map = basis.T
                        if (maps_certificate._array_hash(tensor) != correction['represented_tensor_binary64_SHA256']
                                or maps_certificate._array_hash(input_map) != component['input_map_SHA256']):
                            raise RuntimeError('Endpoint tensor or input map differs from its certificate')
                        norm = _operator_norm_upper(_exact_matrix(input_map),_squared_norm(input_map).sqrt().upper())
                        endpoint_norms[node] = (maps_certificate._array_hash(input_map),
                                               _float_upper(norm),_float_upper(_squared_norm(tensor).sqrt().upper()))
                    input_hash,u,tensor_norm = endpoint_norms[node]
                    if input_hash != component['input_map_SHA256']:
                        raise RuntimeError('Adjacent endpoint input maps differ')
                    c,q = 0.0,[tensor_norm,0.0,0.0]
                bound = map_bounds['maps'][label]
                error = output.bound_output_error_pullback(bound['operator_error_upper'],
                    bound['scalar_column_error_upper'],u,c,q,
                    correction['projection_rounding_Frobenius_upper'],
                    correction['scalar_addition_rounding_Frobenius_upper'])
                components.append(dict(kind=kind,index=node,output_label=label,
                    output_map_SHA256=component['output_map_SHA256'],
                    exact_retained_coordinate_norm_upper=u,exact_complement_coordinate_norm_upper=c,
                    tensor_block_frobenius_upper=q,mapped_output_error_frobenius_upper=error))
            local = _float_upper(2*sum(arb(r['mapped_output_error_frobenius_upper']) for r in components))
            rows.append(dict(interval=i,output_map_error_bounds=map_bounds,components=components,
                             local_uniform_quadratic_coefficient_upper=local))
            if (i+1)%50 == 0:
                print(json.dumps(dict(certified_output_intervals=i+1)),flush=True)
        transport = causal_error.transport_local_errors(maps,
            np.asarray([r['local_uniform_quadratic_coefficient_upper'] for r in rows]))
        coefficient = transport['maximum_node_error_norm_upper']
        multiplier = map_record['perturbation']['source_error_multiplier_upper']
        frozen_coefficient = _float_upper(arb(coefficient)*arb(multiplier)) if multiplier is not None else None
    finally:
        ctx.prec = previous
    coordinate._verified_inputs({'inputs':inputs})
    return dict(artifact='BHSM_N12_GATE7_FROZEN_OUTPUT_MAP_CONSTRUCTION',
        scope='FROZEN_OUTPUT_MAP_CONSTRUCTION_WITH_COORDINATE_AND_STORAGE_CROSS_ERRORS_ONLY',
        coverage=dict(intervals=370,nodes=371,complete=True),inputs=inputs,rows=rows,
        causal_maps_SHA256=maps_certificate._array_hash(maps),transport=transport,
        maximum_stored_causal_output_error_coefficient_upper=coefficient,
        maximum_frozen_causal_output_error_coefficient_upper=frozen_coefficient,
        validation_passed=True,claim_boundary=dict(output_map_construction_arithmetic_enclosed=True,
            output_coordinate_storage_cross_errors_included=True,physical_operand_errors_enclosed=False,
            physical_Hessian_error_enclosed=False,kinematic_midpoint_construction_rounding_enclosed=False,
            pullback_assembly_rounding_enclosed=False,center_covariance_rounding_enclosed=False,
            neighborhood_remainder_enclosed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False))


def main():
    payload = build_payload()
    RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:payload[k] for k in ('maximum_stored_causal_output_error_coefficient_upper',
        'maximum_frozen_causal_output_error_coefficient_upper','validation_passed')}),flush=True)


if __name__ == '__main__':
    main()
