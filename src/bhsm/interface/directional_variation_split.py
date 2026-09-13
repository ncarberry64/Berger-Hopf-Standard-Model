"""Enclose a derivative action using a signed center action and a linear tail."""
from flint import arb_mat
from bhsm.interface.direct_physical_hs_jacobian import _matrix


def split_directions(directions):
    v = _matrix(directions)
    center = arb_mat(v.nrows(), v.ncols(), [x.mid() for x in v.entries()])
    return center, v-center


def enclose_split_action(center_action, uniform_derivative, direction_tail):
    """Use DF(z)(v0+delta) = DF(z)v0 + DF(z)delta on one common domain.

    Caller certifies both the center action and the full derivative on that
    domain. No correlation between the tail and z is required for this bound.
    """
    a, d, tail = map(_matrix, (center_action, uniform_derivative, direction_tail))
    if d.ncols() != tail.nrows() or (a.nrows(), a.ncols()) != (d.nrows(), tail.ncols()):
        raise ValueError('compatible action, derivative, and direction-tail shapes required')
    correction = d*tail
    return a+correction, correction
