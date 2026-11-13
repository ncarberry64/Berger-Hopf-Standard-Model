"""One consumed column of the retained seven-port implicit machinery.

These helpers operate on supplied, common-frame weak-form covectors. They
produce no physical displacement, owner Euler derivative, or domain map.
In particular a seven-row output derivative g_n is never treated as F_b.
The real Arb pairing is the algebraic dual pairing of supplied form entries;
the physical geometric pairing must already be in those entries.
"""
from flint import arb, arb_mat

from .geometric_material_port import geometric_trace_jet, required_material_jet


def seven_port_forcing_direction(*, trace_map, state_direction, trace_shape,
                                 momentum, force, conormal, momentum_mixed,
                                 momentum_rate_direction):
    """Assemble one [trace(3), momentum(2), dynamic flux(2)] column.

    All moving-seam terms are explicit operands. A proved zero is supplied
    as an explicit zero column; absence is never interpreted as zero.
    This reuses the existing 3/4 split without introducing an action seed
    for a trace or an eighth port coordinate.
    """
    if state_direction is None or state_direction.ncols() != 1:
        raise ValueError('one supplied state/displacement direction required')
    trace = geometric_trace_jet(trace_map, state_direction, trace_shape)
    material = required_material_jet(momentum, force, conormal,
                                     momentum_mixed, momentum_rate_direction)
    if material.ncols() != 1:
        raise ValueError('one supplied material direction required')
    return arb_mat(trace.tolist() + material.tolist())


def solve_bulk_forcing_column(F_n, f_column):
    """Solve F_n delta=-f for one column, retaining every supplied KKT row.

    The replay is in the supplied residual-row coordinates. Its enclosure is
    not an owned norm or a continuum bound unless that row/norm map is
    established separately. No inverse, symmetry or regularizer is used.
    """
    if F_n is None or f_column is None:
        raise ValueError('the residual action and consumed forcing are required')
    n = F_n.nrows()
    if n == 0 or F_n.ncols() != n or (f_column.nrows(), f_column.ncols()) != (n, 1):
        raise ValueError('square residual action and exactly one forcing column required')
    response = -F_n.solve(f_column)
    return dict(response=response, replay=F_n * response + f_column)


def real_stationary_impedance_column(H, f_column, Q_XX_column):
    """Conditional real stationary weak-action Schur contraction.

    H/f must be the SAME Hermitian stationary action blocks with their dual
    pairings and constraints, not arbitrary residual-row transformations.
    KKT multipliers remain in H; positivity is on the allowed physical
    tangent. Q_XX is the contracted full quadratic form, with no 1/2.
    This function does not establish the action/positivity identification
    and must not be applied to a causal nonsymmetric residual as impedance.
    """
    solved = solve_bulk_forcing_column(H, f_column)
    response = solved['response']
    qxx = arb(Q_XX_column)
    schur = qxx + (f_column.transpose() * response)[0, 0]
    direct = (qxx + (response.transpose() * H * response)[0, 0]
              + 2 * (response.transpose() * f_column)[0, 0])
    return dict(**solved, schur=schur, direct=direct, difference=direct - schur)
