"""Signed zeta value/first jet of the owned linear coefficient elements.

The coefficient is explicit: a binary64 action constant and exact 59/30
are different realizations. No new history is selected here. Piecewise
coefficient-model error must be supplied separately for a physical proof.
"""
from flint import arb, arb_mat
from bhsm.interface.heat_zeta_mixed_boundary_launch import exponential_moment


def zeta_first(x, h, dx, dh, *, coefficient):
    """Stream integral -c sum h int_0^1 exp(-linear x) and its first jet.

    Retains coefficient and duration terms with their signs until the sum.
    No operator matrix, spectrum or history-state array is allocated.
    """
    count, directions = len(h), dx.ncols()
    if len(x) != count+1 or dx.nrows() != count+1 or (dh.nrows(), dh.ncols()) != (count, directions):
        raise ValueError('aligned coefficient and duration first jets required')
    c = arb(coefficient)
    if not c.is_finite():
        raise ValueError('explicit finite owned zeta coefficient required')
    value = arb(0)
    coefficient_first, duration_first = arb_mat(1, directions), arb_mat(1, directions)
    for i in range(count):
        left, right, duration = arb(x[i]), arb(x[i+1]), arb(h[i])
        if not duration > 0:
            raise ValueError('strictly positive proper duration required')
        delta = right-left
        m0, m1 = exponential_moment(delta, 0), exponential_moment(delta, 1)
        e = (-left).exp()
        value -= c*duration*e*m0
        for j in range(directions):
            coefficient_first[0, j] += c*duration*e*((m0-m1)*dx[i, j]+m1*dx[i+1, j])
            duration_first[0, j] -= c*e*m0*dh[i, j]
    return dict(value=value, first=coefficient_first+duration_first,
                coefficient_first=coefficient_first, duration_first=duration_first)
