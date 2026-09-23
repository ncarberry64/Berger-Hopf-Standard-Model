"""Replace partial LL/LT bounds while retaining the frozen interval-14 debit."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface import history_completion_budget as algebra


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def evaluate(base_path, booked_path, compositions, count, out, lt_increment_prefix=None):
    base = json.loads(base_path.read_bytes())
    booked = json.loads(booked_path.read_bytes())
    if (booked['base_ledger_SHA256'] != sha(base_path)
            or booked['debit_count'] != 1
            or not booked['already_booked_LT_not_charged_again']
            or booked['unknown_remainder_assumed_zero']):
        raise ValueError('Unchanged base and exactly one frozen interval-14 debit required')
    paths = [base_path, booked_path, Path(__file__), Path(algebra.__file__)]
    coefficients = {}
    coverage = list(range(count))
    if not len(base['selected_source_intervals']) <= count <= 370:
        raise ValueError('Nonempty retained-history prefix required')
    for family in ('LL', 'LT'):
        incremental = family == 'LT' and lt_increment_prefix is not None
        prefix = lt_increment_prefix if incremental else f'history_{family}_{count}'
        first = compositions/f'{prefix}_first.json'
        repeat = compositions/f'{prefix}_repeat.json'
        if first.read_bytes() != repeat.read_bytes():
            raise ValueError('Required independent composition repeat differs')
        record = json.loads(first.read_bytes())
        historical = [Path(p) for p in base['source_SHA256']
                      if Path(p).name == f'history_{family}_70_first.json']
        if len(historical) != 1 or sha(historical[0]) != base['source_SHA256'][str(historical[0])]:
            raise ValueError('Bound historical composition receipt required')
        previous = json.loads(historical[0].read_bytes())
        for leaf in ('BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER.npz',
                     'BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz',
                     'direct_causal_quadratic.py'):
            before = [h for p, h in previous['source_SHA256'].items() if Path(p).name == leaf]
            after = [h for p, h in record['source_SHA256'].items() if Path(p).name == leaf]
            if len(before) != 1 or before != after:
                raise ValueError('Frozen maps, axes and transport method must match')
        paths.extend(historical)
        wanted = list(range(len(base['selected_source_intervals']), count)) if incremental else coverage
        if (record['family'] != family or record['certified_source_intervals'] != wanted
                or record['source_lemmas_recomputed']
                or not record['shared_endpoint_coefficients_combined_before_norm']):
            raise ValueError('Complete selected shared-endpoint composition required')
        coefficients[family] = record['result']['frozen_inverse_quadratic_coefficients_upper']
        if incremental:
            old_coefficients = base['operands']['partial_quadratic'][family]
            if (previous['certified_source_intervals'] != base['selected_source_intervals']
                    or previous['result']['frozen_inverse_quadratic_coefficients_upper'] != old_coefficients):
                raise ValueError('Frozen prefix coefficient identity required')
            coefficients[family] = [algebra._number(Fraction(a)+Fraction(b))['upper']
                                    for a, b in zip(old_coefficients, coefficients[family], strict=True)]
        paths.extend((first, repeat))
    old = base['operands']
    payload = algebra.completion_budget(old['Y'], old['Z0'], old['original_radius'],
                                        coefficients['LL'], coefficients['LT'])
    for row, frozen in zip(payload['rows'], booked['rows'], strict=True):
        if row['output'] != frozen['output'] or row['radius']['exact'] != frozen['radius']['exact']:
            raise ValueError('Original output groups and domain must remain unchanged')
        radius = Fraction(row['radius']['exact'])
        value = Fraction(row['known_self_map_part_upper']['exact']) + Fraction(frozen['interval14_value_debit']['exact'])
        derivative = Fraction(row['known_derivative_row_upper']['exact']) + Fraction(frozen['interval14_derivative_debit']['exact'])
        for key, result in {
            'known_self_map_part_upper': value,
            'known_normalized_self_map_part_upper': value/radius,
            'remaining_self_map_allowance': radius-value,
            'remaining_normalized_self_map_allowance': 1-value/radius,
            'known_derivative_row_upper': derivative,
            'remaining_derivative_row_allowance': 1-derivative,
        }.items():
            row[key] = algebra._number(result)
        row['interval14_value_debit'] = frozen['interval14_value_debit']
        row['interval14_derivative_debit'] = frozen['interval14_derivative_debit']
    payload.update(algorithm='INCREMENTAL_PHYSICAL_HISTORY_BUDGET_WITH_FROZEN_ENTRY_V1',
        selected_source_intervals=coverage,
        missing_direct_quadratic_source_intervals=list(range(count, 370)),
        operands=dict(Y=old['Y'], Z0=old['Z0'], original_radius=old['original_radius'], partial_quadratic=coefficients),
        interval14_debit_count=1, old_LL_LT_coefficients_replaced_not_added=True,
        LT_incremental_triangle_bound=bool(lt_increment_prefix),
        LT_boundary_rule=('For the same x in the original domain, norm(A(x)+B(x)) <= norm(A(x))+norm(B(x)). '
                          'No independent parameter copies are introduced. Boundary cancellation is not used.'
                          if lt_increment_prefix else 'Shared endpoint coefficients combined before norms.'),
        interval13_recomputed=False, interval14_recomputed=False,
        unresolved_terms=['TT family beyond the already booked entry contribution',
            f'LL/LT source intervals {count}..369' if count < 370 else 'No missing LL/LT point-source intervals',
            'Uniform nonlinear and derivative remainder on the original domain',
            'Physical branch, frame and quotient identification'],
        source_SHA256={str(p.resolve()): sha(p) for p in paths})
    with out.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(payload, sort_keys=True, indent=2)+'\n')
    print(json.dumps({'selected_intervals': count, 'remaining_self_map_allowances_lower':
        [r['remaining_self_map_allowance']['lower'] for r in payload['rows']]}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for key in ('base', 'booked', 'compositions', 'out'):
        parser.add_argument('--'+key, type=Path, required=True)
    parser.add_argument('--count', type=int, required=True)
    parser.add_argument('--lt-increment-prefix')
    args = parser.parse_args()
    evaluate(args.base, args.booked, args.compositions, args.count, args.out, args.lt_increment_prefix)
