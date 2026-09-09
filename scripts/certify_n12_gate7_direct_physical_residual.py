"""Compose all independently reproduced direct HS values into residual bounds."""
import os
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import derive_n12_gate7_direct_physical_values as values
import certify_n12_gate7_stored_causal_arithmetic_envelope as foundation
from bhsm.interface import direct_physical_residual as residual

center = foundation.center
RESULT = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_DIRECT_PHYSICAL_VALUE_RESIDUAL_ENVELOPE.json'
THEORY = ROOT/'theory/n12_gate7_direct_physical_residual.md'


def merge(inputs, additional):
    for name, digest in additional.items():
        if name in inputs and inputs[name] != digest:
            raise RuntimeError(f'inconsistent residual source: {name}')
        inputs[name] = digest


def merge_verified_raw_sources(inputs, raw_inputs, additional):
    """Keep raw-byte attestations alongside the legacy text-normalized map.

    Verify raw bytes before deriving a normalized digest. Neither convention
    substitutes for the other, and a conflicting earlier binding is retained.
    """
    values.verify_binding(dict(files=additional))
    new_raw, new_normalized = dict(raw_inputs), dict(inputs)
    merge(new_raw, additional)
    merge(new_normalized, {name: center._sha(ROOT/name) for name in additional})
    inputs.update(new_normalized)
    raw_inputs.update(new_raw)


def load_foundation():
    record = json.loads(foundation.RESULT.read_text())
    if (record.get('artifact') != 'BHSM_N12_GATE7_STORED_CAUSAL_ARITHMETIC_ENVELOPE'
            or record.get('validation_passed') is not True
            or record.get('coverage') != dict(intervals=370, nodes=371, complete=True)):
        raise RuntimeError('complete verified frozen arithmetic foundation required')
    inputs = dict(foundation.coordinate._verified_inputs(record))
    required = [center.ENDPOINT.with_suffix('.npz'), center.PRECONDITIONER.with_suffix('.npz'),
                center.JACOBIAN.with_suffix('.npz'), center.DATA]
    if any(p.relative_to(ROOT).as_posix() not in inputs for p in required):
        raise RuntimeError('foundation lacks exact residual operand bindings')
    with np.load(center.DATA) as source:
        maps = source['causal_maps_center'].copy()
    axes = center.component._load_axes()
    if (maps.shape != (370, 74, 74) or axes.shape != (371, 74)
            or foundation.maps._array_hash(maps) != record['causal_maps_SHA256']
            or foundation.maps._array_hash(axes) != record['axes_SHA256']):
        raise RuntimeError('residual maps or axes differ from foundation')
    return record, inputs, maps, axes


def load_all_values():
    manifest_path = values.WORK/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    receipt = json.loads((values.WORK/'reproduction.json').read_text())
    if (manifest.get('endpoints') != list(range(371)) or manifest.get('midpoints') != list(range(370))
            or manifest.get('all_741_values_covered') is not True
            or receipt.get('byte_identical') is not True
            or receipt.get('independent_recomputation') is not True
            or receipt.get('points') != 741 or receipt.get('manifest_SHA256') != values.sha(manifest_path)):
        raise RuntimeError('all 741 independently reproduced direct values required')
    expected = {(values.WORK/f'{stage}_{i:03d}.{ext}').relative_to(ROOT).as_posix()
                for stage, count in (('endpoint', 371), ('midpoint', 370))
                for i in range(count) for ext in ('json', 'npz')}
    if set(manifest['files']) != expected:
        raise RuntimeError('complete exact direct value file inventory required')
    inputs = dict(manifest['binding']['files'])
    merge(inputs, manifest['files'])
    values.verify_binding(dict(files=inputs))
    endpoints = [values.load_cached('endpoint', i, manifest['binding'], {})[0] for i in range(371)]
    midpoints = []
    for i in range(370):
        dependencies = {(values.WORK/f'endpoint_{node:03d}.{ext}').relative_to(ROOT).as_posix():
                        values.sha(values.WORK/f'endpoint_{node:03d}.{ext}')
                        for node in (i, i+1) for ext in ('json', 'npz')}
        midpoints.append(values.load_cached('midpoint', i, manifest['binding'], dependencies)[0])
    for path in (manifest_path, values.WORK/'reproduction.json'):
        merge(inputs, {path.relative_to(ROOT).as_posix(): values.sha(path)})
    return endpoints, midpoints, inputs


def build_payload():
    previous = ctx.prec
    ctx.prec = 512
    try:
        base, inputs, maps, axes = load_foundation()
        endpoints, midpoints, value_inputs = load_all_values()
        raw_inputs = {}
        merge_verified_raw_sources(inputs, raw_inputs, value_inputs)
        if values.cert.ENDPOINT != center.ENDPOINT:
            raise RuntimeError('physical value and residual endpoint sources differ')
        x, w, s, _, steps = values.operands()
        states = [values.hs.weighted_endpoint(x[i], s[i], w) for i in range(371)]
        with np.load(center.JACOBIAN.with_suffix('.npz')) as source:
            tangents = source['endpoint_physical_tangent_action'].copy()
        with np.load(center.PRECONDITIONER.with_suffix('.npz')) as source:
            right = source['reduced_right_Newton_blocks'].copy()
        if tangents.shape != (371, 98, 73) or right.shape != (370, 74, 74):
            raise RuntimeError('complete endpoint test frames and right blocks required')
        sources = []
        for i in range(370):
            test = center.cert._frame(tangents[i+1], center.cert.TEST_DESCRIPTOR_SCALE).T
            sources.append(residual.local_residual_source(right[i], test, states[i], states[i+1],
                endpoints[i], midpoints[i], endpoints[i+1], float(steps[i])))
        response = residual.bound_causal_residual(maps, sources, axes, base['frozen_map_perturbation_gain_upper'])
        if response['fixed_axis_projection_norms_upper'] != base['fixed_axis_projection_norms_upper']:
            raise RuntimeError('residual projection norms differ from foundation')
        for path in (Path(__file__), THEORY, Path(residual.__file__), Path(values.__file__),
                     foundation.RESULT, Path(foundation.maps.__file__),
                     Path(residual.transport_local_errors.__code__.co_filename),
                     Path(residual.combine_stored_causal_errors.__code__.co_filename)):
            merge_verified_raw_sources(inputs, raw_inputs, {path.relative_to(ROOT).as_posix(): values.sha(path)})
        foundation.coordinate._verified_inputs(dict(inputs=inputs))
        values.verify_binding(dict(files=raw_inputs))
        return dict(artifact='BHSM_N12_GATE7_DIRECT_PHYSICAL_VALUE_RESIDUAL_ENVELOPE',
            scope=response['scope'], coverage=dict(intervals=370, endpoints=371, direct_values=741, complete=True),
            inputs=inputs, input_hash_convention='SHA256_CRLF_TO_LF_FOR_JSON_MD_PY',
            raw_input_SHA256=raw_inputs, raw_input_hash_convention='SHA256_EXACT_FILE_BYTES',
            causal_maps_SHA256=base['causal_maps_SHA256'], axes_SHA256=base['axes_SHA256'],
            response=response, validation_passed=True,
            claim_boundary=dict(selected_branch_finite_history_residual_enclosed=True,
                endpoint_product_rounding_enclosed=True, actual_HS_midpoint_rates_used=True,
                floating_gap_assumed=False, midpoint_Taylor_truncation_used=False,
                physical_branch_continuation_certified=False, physical_quotient_identified=False,
                physical_Y_recertified=False, physical_contraction_proved=False,
                Gate7_closed=False, FULL_BHSM_COMPLETE=False))
    finally:
        ctx.prec = previous


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight-foundation', action='store_true')
    args = parser.parse_args()
    if args.preflight_foundation:
        load_foundation()
        print(json.dumps(dict(frozen_foundation_ready=True, direct_values_not_checked=True)), flush=True)
        return
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(selected_branch_residual_bounds=payload['response']['frozen_inverse_residual_bounds_upper'],
        physical_Y_recertified=False, FULL_BHSM_COMPLETE=False)), flush=True)


if __name__ == '__main__':
    main()
