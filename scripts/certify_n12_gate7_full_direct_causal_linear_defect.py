"""Compose all paired physical-point local defects through the frozen inverse."""
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
import derive_n12_gate7_full_direct_physical_jacobians as backend
import certify_n12_gate7_direct_physical_local_defects as local
from bhsm.interface import centered_causal_linear_defect as linear

WORK = ROOT/'artifacts/flagship_integration/.full_direct_physical_local_defect_work'
RESULT = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_FULL_DIRECT_CAUSAL_LINEAR_DEFECT.json'
THEORY = ROOT/'theory/n12_gate7_centered_causal_linear_defect.md'
LOCAL_WRAPPER = ROOT/'scripts/certify_n12_gate7_full_direct_physical_local_defects.py'
ALGORITHM = 'FULL_DIRECT_FIXED_FRAME_CAUSAL_LINEAR_DEFECT_ARB512_SIGNED_CENTERS_V1'


def verify_manifest(manifest, receipt, path):
    indices = list(range(370))
    expected = {local.df.file_key(WORK/f'interval_{i:03d}.{ext}')
                for i in indices for ext in ('json', 'npz')}
    if (manifest.get('algorithm') != local.ALGORITHM
            or manifest.get('intervals') != indices
            or manifest.get('all_intervals_assembled') is not True
            or set(manifest.get('files', {})) != expected
            or receipt.get('intervals') != indices
            or receipt.get('byte_identical') is not True
            or receipt.get('independent_recomputation') is not True
            or receipt.get('manifest_SHA256') != local.df.values.sha(path)):
        raise RuntimeError('all 370 independently reproduced local defects required')
    local.df.values.verify_binding(dict(files=manifest['files']))


def verify_record(record, index, source, path):
    if (record.get('algorithm') != local.ALGORITHM
            or record.get('scope') != 'FIXED_FRAME_DIRECT_PHYSICAL_HS_LOCAL_NEWTON_DEFECT'
            or record.get('interval') != index or record.get('precision_bits') != 512
            or record.get('initial_endpoint_fixed') is not (index == 0)
            or record.get('actual_physical_HS_midpoint_DF_used') is not True
            or record.get('validation_passed') is not True
            or record.get('inputs') != source['inputs']
            or record.get('raw_input_SHA256') != source['raw_inputs']
            or record.get('causal_maps_SHA256') != source['causal_maps_SHA256']
            or record.get('axes_SHA256') != source['axes_SHA256']
            or record.get('input_hash_convention') != 'SHA256_CRLF_TO_LF_FOR_JSON_MD_PY'
            or record.get('raw_input_hash_convention') != 'SHA256_EXACT_FILE_BYTES'
            or record.get('data_SHA256') != local.df.values.sha(path)):
        raise RuntimeError(f'local interval {index} differs from the verified common operands')


def load_inputs():
    backend.install_backend()
    manifest_path = WORK/'manifest.json'
    receipt_path = WORK/'reproduction.json'
    manifest = json.loads(manifest_path.read_text())
    receipt = json.loads(receipt_path.read_text())
    verify_manifest(manifest, receipt, manifest_path)
    # This verifies the full DF reproduction, current physics source binding,
    # frozen foundation, endpoint identity and complete frame/inverse shapes.
    source = local.load_inputs(list(range(370)))
    merge = local.residual.merge_verified_raw_sources
    merge(source['inputs'], source['raw_inputs'],
          {local.df.file_key(LOCAL_WRAPPER): local.df.values.sha(LOCAL_WRAPPER)})
    left, right = [], []
    for i in range(370):
        path = WORK/f'interval_{i:03d}.npz'
        record = json.loads(path.with_suffix('.json').read_text())
        verify_record(record, i, source, path)
        with np.load(path, allow_pickle=False) as arrays:
            expected = {name+suffix for name in ('C', 'DL', 'DR') for suffix in ('_mid_q', '_rad_q')}
            if set(arrays.files) != expected or any(arrays[key].shape != (74, 74) for key in expected):
                raise RuntimeError('complete rational local block inventory required')
            blocks = [local.df.values.hs.restore_balls(arrays[name+'_mid_q'], arrays[name+'_rad_q'])
                      for name in ('DL', 'DR')]
            if i == 0 and any(not value.is_zero() for value in blocks[0].flat):
                raise RuntimeError('fixed initial local input block must be zero')
            left.append(blocks[0]); right.append(blocks[1])
    base = json.loads(local.residual.foundation.RESULT.read_text())
    with np.load(local.residual.center.DATA) as arrays:
        maps = arrays['causal_maps_center'].copy()
    axes = local.residual.center.component._load_axes()
    array_hash = local.residual.foundation.maps._array_hash
    if (array_hash(maps) != source['causal_maps_SHA256']
            or array_hash(axes) != source['axes_SHA256']):
        raise RuntimeError('linear response maps or axes differ from local certificates')
    additional = dict(manifest['files'])
    # Capture every new computation source BEFORE evaluation; recheck on exit.
    for path in (manifest_path, receipt_path, Path(__file__), THEORY, Path(linear.__file__),
                 Path(linear.transport_local_errors.__code__.co_filename),
                 Path(linear.combine_stored_causal_errors.__code__.co_filename),
                 Path(linear._float_upper.__code__.co_filename),
                 Path(linear._matrix.__code__.co_filename), Path(local.df.values.hs.__file__)):
        local.residual.merge(additional, {local.df.file_key(path): local.df.values.sha(path)})
    merge(source['inputs'], source['raw_inputs'], additional)
    return base, source, maps, axes, left, right


def build_payload(progress=None):
    previous = ctx.prec
    ctx.prec = 512
    try:
        base, source, maps, axes, left, right = load_inputs()
        response = linear.bound_causal_linear_defect(maps, left, right, axes,
            base['frozen_map_perturbation_gain_upper'], progress=progress)
        if response['fixed_axis_projection_norms_upper'] != base['fixed_axis_projection_norms_upper']:
            raise RuntimeError('linear projection norms differ from the frozen foundation')
        local.residual.foundation.coordinate._verified_inputs(dict(inputs=source['inputs']))
        local.df.values.verify_binding(dict(files=source['raw_inputs']))
        return dict(artifact='BHSM_N12_GATE7_FULL_DIRECT_CAUSAL_LINEAR_DEFECT', algorithm=ALGORITHM,
            scope='SELECTED_BRANCH_FIXED_FRAME_FINITE_HISTORY_LINEAR_DEFECT',
            coverage=dict(intervals=370, nodes=371, direct_DF_points=741, complete=True),
            inputs=source['inputs'], raw_input_SHA256=source['raw_inputs'],
            input_hash_convention='SHA256_CRLF_TO_LF_FOR_JSON_MD_PY',
            raw_input_hash_convention='SHA256_EXACT_FILE_BYTES',
            causal_maps_SHA256=source['causal_maps_SHA256'], axes_SHA256=source['axes_SHA256'],
            response=response, validation_passed=True,
            claim_boundary=dict(selected_branch_fixed_frame_finite_history_linear_defect_enclosed=True,
                actual_physical_HS_midpoint_DF_used=True, frozen_inverse_unchanged=True,
                midpoint_Taylor_truncation_used=False, physical_branch_continuation_certified=False,
                physical_quotient_identified=False, state_dependent_frame_derivatives_enclosed=False,
                neighborhood_remainder_enclosed=False, physical_Z1_recertified=False,
                physical_contraction_proved=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False))
    finally:
        ctx.prec = previous


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--recompute', action='store_true')
    args = parser.parse_args()
    if args.recompute and not RESULT.exists():
        raise RuntimeError('independent repeat requires a prior complete result')
    if RESULT.exists() and not args.recompute:
        raise RuntimeError('result exists; use --recompute to preserve prior evidence')
    def progress(node, count):
        if node == 1 or node % 10 == 0 or node == count:
            print(json.dumps(dict(causal_rows=node, intervals=count, FULL_BHSM_COMPLETE=False)), flush=True)
    payload = build_payload(progress)
    data = (json.dumps(payload, indent=2, sort_keys=True)+'\n').encode('utf-8')
    candidate = RESULT.with_suffix('.repeat_candidate.json' if args.recompute else '.partial.json')
    candidate.write_bytes(data)
    if args.recompute:
        if RESULT.read_bytes() != data:
            raise ArithmeticError('independent full linear response differs; both results preserved')
        candidate.unlink()
        local.df.values.write_json(RESULT.with_suffix('.reproduction.json'), dict(
            byte_identical=True, independent_recomputation=True,
            result_SHA256=local.df.values.sha(RESULT), FULL_BHSM_COMPLETE=False))
    else:
        candidate.replace(RESULT)
    print(json.dumps(dict(bounds=payload['response']['frozen_inverse_linear_defect_bounds_upper'],
        reproduced=args.recompute, physical_Z1_recertified=False, FULL_BHSM_COMPLETE=False)), flush=True)


if __name__ == '__main__':
    main()
