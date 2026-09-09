"""Enclose every frozen causal map and its complete-chain perturbation gain."""
import json
import hashlib
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_current_green_signed_transverse_causal_center as center
from bhsm.interface import frozen_causal_map_error as construction

RESULT = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_FROZEN_CAUSAL_MAP_CONSTRUCTION.json'
THEORY = ROOT/'theory/n12_gate7_frozen_causal_map_construction.md'


def _array_hash(value):
    return hashlib.sha256(np.asarray(value,dtype='<f8').tobytes(order='C')).hexdigest().upper()


def _verify_bindings(inputs):
    if not inputs:
        raise RuntimeError('Nonempty certificate input bindings required')
    for name, digest in inputs.items():
        path = (ROOT/name).resolve()
        if not path.is_relative_to(ROOT.resolve()) or center._sha(path) != digest:
            raise RuntimeError(f'Changed frozen-map certificate input: {name}')


def _verify_center(record):
    if (record.get('artifact') != 'BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER'
            or record.get('status') != 'SIGNED_TRANSVERSE_CAUSAL_CENTER_COMPOSED'
            or record.get('validation_passed') is not True
            or record.get('data_SHA256') != center._sha(center.DATA)):
        raise RuntimeError('Complete unchanged signed causal center required')
    inputs = record.get('inputs', {})
    required = (center.JACOBIAN.with_suffix('.npz'), center.PRECONDITIONER.with_suffix('.npz'),
                Path(center.component.__file__), Path(center.cert.__file__))
    if any(p.relative_to(ROOT).as_posix() not in inputs for p in required):
        raise RuntimeError('Center lacks frozen-map operand bindings')
    _verify_bindings(inputs)
    return inputs


def build_payload():
    record = json.loads(center.RESULT.read_text())
    inputs = dict(_verify_center(record))
    sources = (Path(__file__).resolve(), THEORY, center.RESULT, center.DATA,
               Path(construction.__file__), Path(construction.causal.__file__),
               Path(construction._exact_matrix.__code__.co_filename),
               Path(construction._real_binary64.__code__.co_filename))
    for path in sources:
        name, digest = path.relative_to(ROOT).as_posix(), center._sha(path)
        if name in inputs and inputs[name] != digest:
            raise RuntimeError('Inconsistent frozen-map source binding')
        inputs[name] = digest
    with np.load(center.JACOBIAN.with_suffix('.npz')) as source:
        tangents = source['endpoint_physical_tangent_action'].copy()
    with np.load(center.PRECONDITIONER.with_suffix('.npz')) as source:
        left = source['left_Newton_blocks'].copy()
        right = source['reduced_right_Newton_blocks'].copy()
    maps = center.component._causal_maps(tangents, left, right)
    with np.load(center.DATA) as source:
        if maps.shape != (370,74,74) or not np.array_equal(maps, source['causal_maps_center']):
            raise RuntimeError('Frozen maps differ from the complete signed center')
    rows = []
    for i in range(370):
        operands = dict(right=right[i], left=left[i], approximate=maps[i],
            test=center.cert._frame(tangents[i+1], center.cert.TEST_DESCRIPTOR_SCALE).T,
            trial=center.cert._frame(tangents[i], center.cert.TRIAL_DESCRIPTOR_SCALE))
        row = construction.bound_frozen_map_error(**operands)
        row.update(interval=i, operand_binary64_SHA256={name:_array_hash(value)
                                                       for name,value in operands.items()})
        rows.append(row)
        if (i+1)%50 == 0:
            print(json.dumps(dict(certified_frozen_maps=i+1)), flush=True)
    perturbation = construction.transport_map_perturbations(
        maps, np.asarray([r['map_operator_error_upper'] for r in rows]))
    _verify_bindings(inputs)
    return dict(
        artifact='BHSM_N12_GATE7_FROZEN_CAUSAL_MAP_CONSTRUCTION',
        scope='EXACT_STORED_OPERANDS_AND_FROZEN_INVERSE_CAUSAL_MAP_CONSTRUCTION_ONLY',
        coverage=dict(intervals=370,nodes=371,complete=True), inputs=inputs, rows=rows,
        causal_maps_SHA256=_array_hash(maps), perturbation=perturbation,
        maximum_map_operator_error_upper=max(r['map_operator_error_upper'] for r in rows),
        validation_passed=True,
        claim_boundary=dict(frozen_causal_map_construction_error_enclosed=True,
            preconditioner_redefined=False, physical_operand_errors_enclosed=False,
            source_and_stored_response_bounds_require_external_verification=True,
            physical_Hessian_error_enclosed=False, output_map_construction_rounding_enclosed=False,
            pullback_assembly_rounding_enclosed=False, center_covariance_rounding_enclosed=False,
            neighborhood_remainder_enclosed=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False))


def main():
    payload = build_payload()
    RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(maximum_map_operator_error_upper=payload['maximum_map_operator_error_upper'],
        perturbation_gain_upper=payload['perturbation']['perturbation_gain_upper'],
        status=payload['perturbation']['status'], validation_passed=payload['validation_passed'])), flush=True)


if __name__ == '__main__':
    main()
