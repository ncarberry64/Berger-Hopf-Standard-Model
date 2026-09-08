"""Adjudicate raw skew separately from the stored quadratic-form authority."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'src'))
import certify_n12_gate7_current_green_signed_transverse_tensor_recovery as raw_certificate
from bhsm.interface import symmetric_quadratic_center as representation

recovery = raw_certificate.recovery
RESULT = ROOT / 'artifacts/flagship_integration/BHSM_N12_GATE7_SYMMETRIC_QUADRATIC_REPRESENTATIVES.json'
RAW_SKEW_KEY = 'all_recovered_tensors_are_symmetric_to_binary64_roundoff'
TOLERANCE = 5e-13


def array_hash(value):
    return hashlib.sha256(np.asarray(value, dtype='<f8').tobytes(order='C')).hexdigest().upper()


def validate_raw_scope(payload):
    """Do not waive missing checks or any failure other than the reported skew."""
    expected = {
        'all_370_defined_axis_endpoint_tensors_recovered',
        'all_370_midpoint_tensors_recovered',
        'one_recovery_campaign_fingerprint_retained',
        'all_recovered_total_norms_reproduce_published_norms',
        'all_recovered_output_norms_reproduce_published_norms',
        RAW_SKEW_KEY,
        'all_persisted_transverse_bases_are_orthonormal',
        'all_persisted_transverse_bases_annihilate_their_Green_axes',
        'all_exported_summary_values_finite', '512_bit_Arb_CPU_aggregation_used',
        'no_action_center_mesh_frame_axis_parameter_or_precision_changed',
        'raw_tensor_cache_not_committed_as_release_payload',
        'outward_remainder_and_Gate7_not_claimed', 'FULL_BHSM_COMPLETE',
    }
    checks = payload.get('validation', {})
    if (set(checks) != expected or checks['FULL_BHSM_COMPLETE'] is not False
            or not isinstance(checks[RAW_SKEW_KEY], bool)
            or any(value is not True for key, value in checks.items()
                   if key not in (RAW_SKEW_KEY, 'FULL_BHSM_COMPLETE'))
            or payload.get('validation_passed') is not checks[RAW_SKEW_KEY]):
        raise RuntimeError('raw recovery has an unadjudicated failure or missing check')


def build_payload():
    raw = raw_certificate.build_payload()  # Revalidates all actual shards.
    validate_raw_scope(raw)
    stored = json.loads(raw_certificate.RESULT.read_text(encoding='utf-8'))
    if raw != stored:
        raise RuntimeError('raw aggregate must first be materialized for these exact inputs')
    fingerprint = recovery._fingerprint()
    paths = raw_certificate._paths('endpoint') + raw_certificate._paths('midpoint')
    source_paths = [Path(__file__), Path(representation.__file__), raw_certificate.RESULT,
                    raw_certificate.DATA, Path(raw_certificate.__file__)]
    source_paths.extend(ROOT / relative for relative in raw['inputs'])
    inputs = {p.relative_to(ROOT).as_posix(): raw_certificate._sha(p) for p in source_paths}
    rows = []
    for path in paths:
        before = raw_certificate._sha(path)
        with np.load(path) as source:
            tensor = np.asarray(source['quadratic_tensor'], dtype=float)
            kind, index = str(source['kind'].item()), int(source['index'])
            published_digest = str(source['published_shard_SHA256'].item())
        represented, row = representation.certify_representation(tensor)
        norm = float(np.linalg.norm(tensor))
        skew = float(np.linalg.norm(tensor - tensor.transpose(0, 2, 1)) / max(norm, np.finfo(float).tiny))
        published = recovery._published_path(kind, index)
        if raw_certificate._sha(published) != published_digest:
            raise RuntimeError('published parent changed')
        with np.load(published) as source:
            expected_total = float(source['quadratic_Frobenius_norm'])
            expected_outputs = np.asarray(source['quadratic_output_Frobenius_norms'], dtype=float)
        total_residual = abs(float(np.linalg.norm(represented)) - expected_total) / max(expected_total, np.finfo(float).tiny)
        output_residual = float(np.max(abs(np.linalg.norm(represented, axis=(1, 2)) - expected_outputs)
                                      / np.maximum(expected_outputs, np.finfo(float).tiny)))
        if not (row['projection_rounding_relative_to_maximum_entry_upper'] < TOLERANCE
                and total_residual < TOLERANCE and output_residual < TOLERANCE):
            raise RuntimeError(f'represented quadratic tensor failed unchanged tolerance: {kind} {index}')
        if raw_certificate._sha(path) != before:
            raise RuntimeError('raw tensor changed during verification')
        row.update(kind=kind, index=index, raw_shard_SHA256=before,
                   represented_tensor_binary64_SHA256=array_hash(represented),
                   raw_skew_relative_Frobenius=skew, raw_skew_screen_passed=skew < TOLERANCE,
                   represented_total_norm_relative_residual=total_residual,
                   represented_output_norm_maximum_relative_residual=output_residual)
        rows.append(row)
    if raw_certificate._manifest(paths) != raw['shard_manifest_SHA256']:
        raise RuntimeError('raw manifest changed during representation verification')
    if recovery._fingerprint() != fingerprint or any(
            raw_certificate._sha(ROOT / path) != digest for path, digest in inputs.items()):
        raise RuntimeError('representation certificate inputs changed')
    return {
        'artifact': 'BHSM_N12_GATE7_SYMMETRIC_QUADRATIC_REPRESENTATIVES',
        'status': 'ALL_740_STORED_QUADRATIC_REPRESENTATIVES_VERIFIED',
        'scope': 'SYMMETRIC_POLARIZATION_OF_STORED_QUADRATIC_FORMS_ONLY',
        'campaign_fingerprint': fingerprint,
        'shard_manifest_SHA256': raw['shard_manifest_SHA256'],
        'coverage': {'endpoints': 370, 'midpoints': 370, 'complete': len(rows) == 740},
        'unchanged_tolerance': TOLERANCE,
        'raw_aggregate_validation_passed': raw['validation_passed'],
        'raw_skew_failure_count': sum(not row['raw_skew_screen_passed'] for row in rows),
        'maximum_projection_rounding_Frobenius_upper': max(row['projection_rounding_Frobenius_upper'] for row in rows),
        'maximum_projection_rounding_relative_to_maximum_entry_upper': max(row['projection_rounding_relative_to_maximum_entry_upper'] for row in rows),
        'rows': rows, 'inputs': inputs, 'validation_passed': True,
        'claim_boundary': {'raw_tensors_modified': False, 'raw_skew_failure_preserved': True,
                           'stored_quadratic_form_represented_with_enclosed_rounding': True,
                           'physical_Hessian_error_enclosed': False, 'causal_rounding_enclosed': False,
                           'Gate7_closed': False, 'FULL_BHSM_COMPLETE': False},
    }


def validate_for_consumption(raw, record):
    """Validate the current certificate, not just its success flag."""
    validate_raw_scope(raw)
    if (record.get('validation_passed') is not True
            or record.get('scope') != 'SYMMETRIC_POLARIZATION_OF_STORED_QUADRATIC_FORMS_ONLY'
            or record.get('coverage') != {'endpoints': 370, 'midpoints': 370, 'complete': True}
            or record.get('campaign_fingerprint') != recovery._fingerprint()
            or record.get('shard_manifest_SHA256') != raw.get('shard_manifest_SHA256')
            or record.get('unchanged_tolerance') != TOLERANCE
            or not record.get('inputs')
            or any(raw_certificate._sha(ROOT / path) != digest for path, digest in record['inputs'].items())
            or [(r.get('kind'), r.get('index')) for r in record.get('rows', [])]
               != [('endpoint', i) for i in range(1, 371)] + [('midpoint', i) for i in range(370)]):
        raise RuntimeError('complete current quadratic representation certificate required')


def main():
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in payload.items() if k not in ('rows', 'inputs')}))


if __name__ == '__main__':
    main()
