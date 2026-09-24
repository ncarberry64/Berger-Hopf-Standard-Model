"""Consume frozen global lemmas and new partial compositions, without replay."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface import history_completion_budget as algebra


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def evaluate(evidence_root, compositions, out):
    base = evidence_root/'artifacts/flagship_integration'
    paths = {key: base/f'BHSM_N12_GATE7_{name}.json' for key, name in (
        ('residual', 'DIRECT_PHYSICAL_VALUE_RESIDUAL_ENVELOPE'),
        ('linear', 'FULL_DIRECT_CAUSAL_LINEAR_DEFECT'),
        ('radius', 'PHYSICAL_INCIDENCE_CAUSAL_ENVELOPE'))}
    records = {key: json.loads(path.read_bytes()) for key, path in paths.items()}
    residual, linear, radius = (records[k] for k in ('residual', 'linear', 'radius'))
    for key in ('causal_maps_SHA256', 'axes_SHA256'):
        if len({record[key] for record in records.values()}) != 1:
            raise ValueError('Identical original maps and projections required')
    if not all(record['validation_passed'] for record in records.values()):
        raise ValueError('Retained certified lemmas required')
    if not all(records[k]['coverage']['complete'] for k in ('residual', 'linear')):
        raise ValueError('Complete global point-data coverage required')
    coefficients = {}
    coverage = {}
    for family in ('LL', 'LT'):
        first = compositions/f'history_{family}_70_first.json'
        repeat = compositions/f'history_{family}_70_repeat.json'
        if first.read_bytes() != repeat.read_bytes():
            raise ValueError('Independent new composition must reproduce exactly')
        record = json.loads(first.read_bytes())
        if (record['family'] != family or record['source_lemmas_recomputed']
                or record['local_interval_13_certificate_reopened']
                or not record['shared_endpoint_coefficients_combined_before_norm']):
            raise ValueError('Signed shared-endpoint composition required')
        coefficients[family] = record['result']['frozen_inverse_quadratic_coefficients_upper']
        coverage[family] = record['certified_source_intervals']
        paths[f'{family}_first'] = first
        paths[f'{family}_repeat'] = repeat
    if coverage['LL'] != coverage['LT']:
        raise ValueError('Matching selected source coverage required')
    y = residual['response']['frozen_inverse_residual_bounds_upper']
    z = linear['response']['frozen_inverse_linear_defect_bounds_upper']
    r = radius['stored_polynomial_adjudication']['witness']['radius']
    payload = algebra.completion_budget(y, z, r, coefficients['LL'], coefficients['LT'])
    payload.update(
        algorithm='FULL_HISTORY_MISSING_REMAINDER_EXACT_BUDGET_V1',
        operands=dict(Y=y, Z0=z, original_radius=r, partial_quadratic=coefficients),
        selected_source_intervals=coverage['LL'],
        missing_direct_quadratic_source_intervals=sorted(set(range(370))-set(coverage['LL'])),
        remaining_terms=[
            'TT quadratic sources on all intervals (available 0..69 not yet composed)',
            'LL and LT sources on intervals 70..369',
            'uniform nonlinear remainder and derivative remainder on the original full-history domain',
            'physical branch, frame and quotient identification obligations'],
        local_interval_13_status='CLOSED_AND_FROZEN_USER_ACCEPTED_LEMMA',
        local_interval_13_recomputed=False,
        new_action_evaluations=0,
        verdict='OPEN — SPECIFIC REMAINING OBSTRUCTION',
        certification_FAIL_means='The complete required bound is unavailable; no physical inequality violation is proved.')
    paths['producer'] = Path(__file__)
    paths['algebra'] = Path(algebra.__file__)
    payload['source_SHA256'] = {str(path.resolve()): sha(path) for path in paths.values()}
    with out.open('xb') as stream:
        stream.write((json.dumps(payload, indent=2, sort_keys=True)+'\n').encode())
    print(json.dumps(payload['rows'], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--compositions', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    evaluate(args.evidence_root.resolve(), args.compositions.resolve(), args.out)
