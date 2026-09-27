"""Material derivatives of supplied canonical lifts, without inventing ports.

A right inverse of a boundary-output Jacobian is a coordinate lift. It is
not, by itself, an identity expressing that output as an action variation.
"""
from flint import arb_mat


def differentiated_lift(K, lift, dK, dtarget):
    """Differentiate K L = E with the actual moving target supplied explicitly.

    Return one matrix per material direction. No inverse or second operator
    tensor is formed, and absent material input is never treated as zero.
    """
    n, m = lift.nrows(), lift.ncols()
    if (K.nrows(), K.ncols()) != (n, n):
        raise ValueError('canonical KKT/lift dimensions disagree')
    if dK is None or dtarget is None or len(dK) != len(dtarget):
        raise ValueError('owned KKT and target material derivatives required')
    results = []
    for dk, de in zip(dK, dtarget):
        if (dk.nrows(), dk.ncols()) != (n, n) or (de.nrows(), de.ncols()) != (n, m):
            raise ValueError('material derivative dimensions disagree')
        results.append(K.solve(de - dk * lift))
    return results


def moving_action_contraction(lift, gradient, gradient_jets, lift_jets):
    """D(L^T g)[P] = L^T Dg[P] + DL[P]^T g, with the ordinary PLUS sign.

    This evaluates contractions for explicitly supplied owned directions;
    it does not identify these with the seven native boundary outputs.
    """
    n, m = lift.nrows(), lift.ncols()
    if gradient.ncols() != 1 or gradient.nrows() != n or gradient_jets.nrows() != n:
        raise ValueError('gradient and lift dimensions disagree')
    if lift_jets is None or len(lift_jets) != gradient_jets.ncols():
        raise ValueError('one owned material lift derivative per direction required')
    direct = lift.transpose() * gradient_jets
    moving = arb_mat(m, gradient_jets.ncols())
    for j, dl in enumerate(lift_jets):
        if (dl.nrows(), dl.ncols()) != (n, m):
            raise ValueError('material lift dimensions disagree')
        column = dl.transpose() * gradient
        for a in range(m):
            moving[a, j] = column[a, 0]
    return dict(fixed_seed=direct, moving_seed=moving, total=direct + moving)
