"""Exact remaining budgets, never a substitute for missing physical bounds."""
from fractions import Fraction
import math


def _nonnegative(value):
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError('Finite nonnegative certified operands required')
    return Fraction.from_float(value)


def _number(value):
    approximation = float(value)
    lower = approximation
    upper = approximation
    if Fraction.from_float(lower) > value:
        lower = math.nextafter(lower, -math.inf)
    if Fraction.from_float(upper) < value:
        upper = math.nextafter(upper, math.inf)
    return dict(exact=str(value), lower=lower, upper=upper)


def completion_budget(y, z, radius, partial_ll, partial_lt):
    """Separate known homogeneous terms from two genuinely unknown remainders.

    R is the remainder of the full frozen Newton map after its constant,
    center-linear and selected LL/LT quadratic terms. E is its derivative
    remainder. R and E include all omitted source families and neighborhoods;
    neither is assumed zero. The derivative of the known homogeneous
    quadratic majorant contributes twice its value in the radius norm.

    Inputs are certified nonnegative binary64 upper bounds. The returned
    rational allowances refer to the selected branch and fixed frames only;
    they do not establish the remaining physical domain identifications.
    """
    if (any(len(v) != 2 for v in (y, z, radius, partial_ll, partial_lt))
            or any(len(row) != 2 for row in z)):
        raise ValueError('Two output groups and two original radii required')
    y, r, c, m = [[_nonnegative(v) for v in a]
                  for a in (y, radius, partial_ll, partial_lt)]
    z = [[_nonnegative(v) for v in row] for row in z]
    if not all(r):
        raise ValueError('Original radii must be positive')
    rows = []
    for i in range(2):
        linear = sum(z[i][j]*r[j] for j in range(2))
        quadratic = c[i]*r[0]**2 + 2*m[i]*r[0]*r[1]
        base = y[i] + linear + quadratic
        derivative = (linear + 2*quadratic)/r[i]
        rows.append(dict(
            output=('longitudinal', 'transverse')[i],
            radius=_number(r[i]), known_self_map_part_upper=_number(base),
            known_normalized_self_map_part_upper=_number(base/r[i]),
            remaining_self_map_allowance=_number(r[i]-base),
            remaining_normalized_self_map_allowance=_number(1-base/r[i]),
            known_derivative_row_upper=_number(derivative),
            remaining_derivative_row_allowance=_number(1-derivative),
            known_partial_quadratic_upper=_number(quadratic)))
    return dict(
        scope='EXACT_BUDGET_CONDITIONAL_ON_MISSING_FULL_HISTORY_REMAINDERS',
        rows=rows,
        inequalities=[
            dict(name='longitudinal_self_map',
                 lhs='known_self_map_part_L + R_L', rhs=_number(r[0]),
                 certified_full_lhs_upper=None, rigorous_margin=None,
                 certification_status='FAIL', mathematical_status='UNDECIDED'),
            dict(name='transverse_self_map',
                 lhs='known_self_map_part_T + R_T', rhs=_number(r[1]),
                 certified_full_lhs_upper=None, rigorous_margin=None,
                 certification_status='FAIL', mathematical_status='UNDECIDED'),
            dict(name='contraction',
                 lhs='max(known_derivative_row_L + E_L, known_derivative_row_T + E_T)',
                 rhs=_number(Fraction(1)),
                 certified_full_lhs_upper=None, rigorous_margin=None,
                 certification_status='FAIL', mathematical_status='UNDECIDED')],
        unknown_remainder_assumed_zero=False,
        physical_inequality_violation_proved=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)
