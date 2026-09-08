"""Carry all local stored-rounding coefficients through the frozen causal chain."""
from pathlib import Path
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(ROOT/'src'))

import certify_n12_gate7_stored_rounding_local_transport as local
from bhsm.interface import current_green_causal_error as transport

RESULT = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_STORED_ROUNDING_CAUSAL_TRANSPORT.json'
THEORY = ROOT/'theory/n12_gate7_stored_rounding_causal_transport.md'


def _local_bounds(payload):
    """Accept only the complete local producer and its current bound inputs."""
    if (payload.get('validation_passed') is not True
            or payload.get('artifact') != 'BHSM_N12_GATE7_STORED_ROUNDING_LOCAL_TRANSPORT'
            or payload.get('scope') != 'LOCAL_STORED_ROUNDING_THROUGH_EXACT_STORED_MAPS_ONLY'
            or payload.get('coverage') != dict(intervals=370, complete=True)):
        raise RuntimeError('Complete stored-rounding local certificate required')
    rows = payload.get('rows', [])
    if len(rows) != 370 or [r.get('interval') for r in rows] != list(range(370)):
        raise RuntimeError('All 370 ordered local bounds required')
    inputs = payload.get('inputs', {})
    required = [Path(local.__file__), Path(local.transport.__file__), local.corrected.RESULT,
                local.causal.JACOBIAN.with_suffix('.npz'),
                local.causal.PRECONDITIONER.with_suffix('.npz')]
    if any(p.relative_to(ROOT).as_posix() not in inputs for p in required):
        raise RuntimeError('Local certificate lacks its required input bindings')
    for name, digest in inputs.items():
        path = (ROOT/name).resolve()
        if not path.is_relative_to(ROOT.resolve()) or local.causal._sha(path) != digest:
            raise RuntimeError(f'Stale local transport input: {name}')
    certificate = json.loads(local.corrected.RESULT.read_text())
    local.corrected.validate_for_consumption(certificate)
    return np.asarray([r['local_block_sup_quadratic_error_coefficient_upper'] for r in rows], dtype=float)


def build_payload():
    sources = [Path(__file__), THEORY, Path(transport.__file__),
               Path(transport._real_binary64.__code__.co_filename),
               local.RESULT, Path(local.__file__), Path(local.causal.component.__file__),
               Path(local.causal.cert.__file__),
               local.causal.JACOBIAN.with_suffix('.npz'),
               local.causal.PRECONDITIONER.with_suffix('.npz')]
    inputs = {p.relative_to(ROOT).as_posix(): local.causal._sha(p) for p in sources}
    bounds = _local_bounds(json.loads(local.RESULT.read_text()))
    with np.load(local.causal.JACOBIAN.with_suffix('.npz')) as data:
        tangents = data['endpoint_physical_tangent_action'].copy()
    with np.load(local.causal.PRECONDITIONER.with_suffix('.npz')) as data:
        left = data['left_Newton_blocks'].copy()
        right = data['reduced_right_Newton_blocks'].copy()
    maps = local.causal.component._causal_maps(tangents, left, right)
    result = transport.transport_local_errors(maps, bounds)
    if any(local.causal._sha(ROOT/name) != digest for name, digest in inputs.items()):
        raise RuntimeError('Causal rounding transport inputs changed during execution')
    _local_bounds(json.loads(local.RESULT.read_text()))
    return dict(
        artifact='BHSM_N12_GATE7_STORED_ROUNDING_CAUSAL_TRANSPORT',
        scope='STORED_ADDITION_AND_PROJECTION_ERROR_THROUGH_EXACT_STORED_CAUSAL_MAPS_ONLY',
        inputs=inputs, causal_maps_SHA256=local._array_hash(maps),
        coverage=dict(intervals=370, nodes=371, complete=True),
        transport=result,
        local_error_bounds_require_external_verification=False,
        node_block_sup_quadratic_error_coefficient_upper=result['node_error_norm_upper'],
        maximum_node_block_sup_quadratic_error_coefficient_upper=result['maximum_node_error_norm_upper'],
        validation_passed=True,
        claim_boundary=dict(stored_addition_and_projection_errors_transported_causally=True,
            physical_Hessian_error_enclosed=False, adjoint_evaluation_error_enclosed=False,
            map_construction_rounding_enclosed=False, coordinate_solve_error_enclosed=False,
            pullback_assembly_rounding_enclosed=False, center_covariance_rounding_enclosed=False,
            neighborhood_remainder_enclosed=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False),
    )


def main():
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({k: payload[k] for k in ('artifact', 'coverage', 'validation_passed',
        'maximum_node_block_sup_quadratic_error_coefficient_upper')}))


if __name__ == '__main__':
    main()
