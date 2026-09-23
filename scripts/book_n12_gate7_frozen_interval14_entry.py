"""Book the reproduced rank-one entry once in the retained-history ledger.

This consumes frozen lemmas; it performs no interval-13/14 recomputation.
All ledger sums/differences use exact rational arithmetic.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def evaluate(work, out):
    receipt_path = work/'interval14_entry_reproduction_manual_exact_repair_v1.json'
    receipt = json.loads(receipt_path.read_bytes())
    comparison = receipt['entry_assembly_comparison']
    expected = '76CDA67FA8751B4B7C1753D3CA43C47F9031F1C14C24D32C8D9061FCD87FF3A9'
    first, repeat = Path(comparison['first']), Path(comparison['repeat'])
    if (not comparison['byte_identical'] or not receipt['midpoint_scalar_reproduced']
            or not receipt['shared_tail_repair_validated']
            or sha(first) != expected or sha(repeat) != expected
            or first.read_bytes() != repeat.read_bytes()):
        raise ValueError('Frozen independently reproduced entry required')
    entry = json.loads(first.read_bytes())
    if not entry['strict_entry_target_pass'] or not entry['strict_transport_allocation_pass']:
        raise ValueError('Both strict frozen tests must pass')
    base_path = work/'history_budget_first.json'
    base = json.loads(base_path.read_bytes())
    if base['unknown_remainder_assumed_zero']:
        raise ValueError('Unknown contributions must remain unknown')
    report = lambda x: dict(exact=str(x), approximate=float(x))
    rows = []
    costs = ['frozen_longitudinal_transport_including_TT_linear_upper',
             'frozen_transverse_transport_including_TT_linear_upper']
    for i, (old, cost_key) in enumerate(zip(base['rows'], costs, strict=True)):
        cost = Fraction(entry[cost_key]['exact'])
        derivative = Fraction(entry['weighted_derivative_row_contributions_upper'][i]['exact'])
        radius = Fraction(old['radius']['exact'])
        known = Fraction(old['known_self_map_part_upper']['exact'])+cost
        known_derivative = Fraction(old['known_derivative_row_upper']['exact'])+derivative
        rows.append(dict(output=old['output'], radius=report(radius),
            interval14_value_debit=report(cost), interval14_derivative_debit=report(derivative),
            known_self_map_part_upper=report(known), remaining_self_map_allowance=report(radius-known),
            known_derivative_row_upper=report(known_derivative), remaining_derivative_allowance=report(1-known_derivative),
            full_history_inequality_status='NOT_CERTIFIED_MISSING_PATHS'))
    payload = dict(algorithm='FROZEN_INTERVAL14_ENTRY_ADDITIVE_HISTORY_LEDGER_V1',
        entry_id='interval14:right:73<-14:TT-linear-plus-unaccounted-entry-remainder',
        base_ledger_SHA256=sha(base_path), entry_assembly_SHA256=expected,
        reproduction_receipt_SHA256=sha(receipt_path),
        debit_count=1, duplicate_booking_rule='Replace this snapshot; never add it again to itself.',
        already_booked_LT_not_charged_again=True, rows=rows,
        original_radius_preserved=True, full_history_inequalities_certified=False,
        interval13_recomputed=False, interval14_recomputed=False, unknown_remainder_assumed_zero=False,
        unresolved_terms=base['remaining_terms'], missing_direct_quadratic_source_intervals=base['missing_direct_quadratic_source_intervals'],
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    with out.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(payload,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'entry_booked_once':True,'remaining_self_map_allowances':[r['remaining_self_map_allowance']['approximate'] for r in rows],
        'known_derivative_rows':[r['known_derivative_row_upper']['approximate'] for r in rows]}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    evaluate(args.work.resolve(),args.out.resolve())
