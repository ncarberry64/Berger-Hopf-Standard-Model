"""Exact current-radius criteria for a shared-parameter global remainder.

On the unit ball of the maximum two-radius history norm, let G be the
normalized physical remainder after the ledger's booked functions. If
G(0)=DG(0)=0 and sup ||D2 G_i|| <= kappa_i on every radial segment, then
||G_i|| <= kappa_i/2 and ||DG_i|| <= kappa_i. These are sufficient bounds,
not values inferred from point Hessians or selected local diagnostics.
"""
from fractions import Fraction
from bhsm.interface.history_completion_budget import _number


PROOF_FLAGS = (
    'same_action_and_center', 'same_original_domain',
    'booked_functions_excluded_exactly_once', 'zero_value_and_derivative_at_center',
    'complete_HS_midpoint_relation', 'all_direction_pairs',
    'common_parameters_preserved_through_output', 'uniform_second_derivative_enclosed',
    'required_independent_reproduction_passed',
)


def evaluate(ledger, ledger_sha256, uniform=None):
    rows = ledger['rows']
    if [row['output'] for row in rows] != ['longitudinal', 'transverse']:
        raise ValueError('Two ordered output groups required')
    if ledger.get('interval14_debit_count') != 1:
        raise ValueError('The frozen interval-14 debit must appear exactly once')
    radius = [Fraction(row['radius']['exact']) for row in rows]
    known = [Fraction(row['known_self_map_part_upper']['exact']) for row in rows]
    derivative = [Fraction(row['known_derivative_row_upper']['exact']) for row in rows]
    if any(r <= 0 for r in radius):
        raise ValueError('Positive original radii required')
    for row, r, value, d in zip(rows, radius, known, derivative, strict=True):
        if (Fraction(row['remaining_self_map_allowance']['exact']) != r-value or
                Fraction(row['remaining_derivative_row_allowance']['exact']) != 1-d):
            raise ValueError('Ledger allowance identity differs')
    targets = [min(2*(r-v)/r, 1-d)
               for r, v, d in zip(radius, known, derivative, strict=True)]
    result = dict(
        algorithm='CURRENT_RADIUS_GLOBAL_PHYSICAL_REMAINDER_CHECKPOINT_V1',
        ledger_SHA256=ledger_sha256,
        radius_exact=[str(r) for r in radius],
        norm='MAXIMUM_OF_TWO_RADIUS_NORMALIZED_HISTORY_GROUP_NORMS',
        uniform_kappa_strict_targets=[_number(k) for k in targets],
        target_is_a_proved_bound=False,
        implication=dict(value_remainder='R_i <= r_i*kappa_i/2',
                         normalized_derivative_remainder='E_i <= kappa_i'),
        global_physical_contraction_certified=False,
        physical_inequality_violation_proved=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False,
    )
    kappa = None
    if uniform is not None:
        if (uniform.get('method') != 'GLOBAL_SHARED_PARAMETER_REMAINDER_HESSIAN' or
                uniform.get('ledger_SHA256') != ledger_sha256 or
                uniform.get('radius_exact') != result['radius_exact'] or
                uniform.get('history_intervals') != list(range(370)) or
                any(uniform.get(key) is not True for key in PROOF_FLAGS) or
                not uniform.get('proof_artifact_SHA256')):
            raise ValueError('Complete same-ledger physical uniform proof required')
        raw = uniform.get('kappa_upper_exact', [])
        if len(raw) != 2 or any(not isinstance(v, str) for v in raw):
            raise ValueError('Two exact rational outward bounds required')
        kappa = [Fraction(v) for v in raw]
        if any(k < 0 for k in kappa):
            raise ValueError('Nonnegative remainder bounds required')
    result['missing_object'] = (
        'A full-history shared-parameter physical remainder Hessian certificate '
        'on the current domain, with exact booked-function/center identities and '
        'the physical HS midpoint and output attachment.' if kappa is None else None)
    result['classification'] = 'INCOMPLETE_REMAINDER_INFORMATION'
    inequalities = []
    for i, name in enumerate(('longitudinal_self_map', 'transverse_self_map')):
        lhs = None if kappa is None else known[i]+radius[i]*kappa[i]/2
        margin = None if lhs is None else radius[i]-lhs
        inequalities.append(dict(name=name, known_part_upper=_number(known[i]),
            certified_full_lhs_upper=None if lhs is None else _number(lhs),
            required_rhs=_number(radius[i]),
            rigorous_margin=None if margin is None else _number(margin),
            status='PASS' if margin is not None and margin > 0 else 'FAIL_TO_CERTIFY'))
    lhs = None if kappa is None else max(d+k for d, k in zip(derivative, kappa))
    margin = None if lhs is None else 1-lhs
    inequalities.append(dict(name='contraction', known_rows_upper=[_number(d) for d in derivative],
        certified_full_lhs_upper=None if lhs is None else _number(lhs),
        required_rhs=_number(Fraction(1)), rigorous_margin=None if margin is None else _number(margin),
        status='PASS' if margin is not None and margin > 0 else 'FAIL_TO_CERTIFY'))
    result['inequalities'] = inequalities
    if kappa is not None:
        result['kappa_upper'] = [_number(k) for k in kappa]
        passed = all(row['status'] == 'PASS' for row in inequalities)
        result['global_physical_contraction_certified'] = passed
        result['classification'] = 'PHYSICAL_CONTRACTION_CERTIFIED' if passed else 'INSUFFICIENT_ENCLOSURE'
    return result
