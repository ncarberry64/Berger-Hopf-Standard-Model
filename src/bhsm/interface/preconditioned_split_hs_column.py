"""Keep fixed output projection and shared endpoint uncertainty inside the HS tail."""
from flint import arb, arb_mat
from bhsm.interface.direct_physical_hs_jacobian import _matrix
from bhsm.interface.directed_physical_hs_column import _step


def local_columns(trial, endpoint_action, center_direction, center_action,
                  direction_tail, midpoint_df, step, test, frozen_left,
                  frozen_right, column, side):
    """Equivalent local columns from caller-certified center and uniform DF.

    The caller certifies center_action = DF_M(center_direction) and the endpoint
    action on matching physical domains. The combined expression uses exact
    derivative linearity and includes the center-rounding remainder explicitly.
    It does not establish physical frame derivatives or quotient identification.
    """
    e, a, w0, b0, delta, m, t, l, r = map(_matrix, (trial, endpoint_action,
        center_direction, center_action, direction_tail, midpoint_df, test,
        frozen_left, frozen_right))
    n, k = e.nrows(), r.nrows()
    if (side not in ('left', 'right') or type(column) is not int or not 0 <= column < k
            or any((x.nrows(), x.ncols()) != (n, 1) for x in (e, a, w0, b0, delta))
            or any((x.nrows(), x.ncols()) != (n, n) for x in (m, l))
            or (t.nrows(), t.ncols()) != (k, n) or r.ncols() != k
            or any(not v.rad().is_zero() for v in w0.entries())):
        raise ValueError('compatible fixed-frame columns and exact direction center required')
    h = _step(step)
    sign = 1 if side == 'left' else -1
    p = r.solve(t)
    q = p*m
    fixed = p*(l*e+e) if side == 'left' else arb_mat(k, 1, [arb(i == column) for i in range(k)])-p*e
    preconditioned = fixed+(p*a)*(h/6)+(p*b0+q*delta)*(2*h/3)
    a0 = arb_mat(n, 1, [x.mid() for x in a.entries()])
    da = a-a0
    rounding = e/2+a0*(sign*h/8)-w0
    coefficient = p*(h/6)+q*(sign*h*h/12)
    combined = fixed+(p*a0)*(h/6)+(p*b0)*(2*h/3)+coefficient*da+(q*rounding)*(2*h/3)
    return dict(preconditioned_tail=preconditioned, combined_endpoint_tail=combined)
