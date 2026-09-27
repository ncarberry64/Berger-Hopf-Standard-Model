"""Canonical complete-child outputs, with explicit event/child orientation.

Arguments are actual owned values (one column) or their derivatives in common
parameter columns. This assembly does not supply a missing history functional.
Source: v21.35 _child_rows_at_order, with its constraint rows kept in F_joint.
"""
from flint import arb_mat


def native_seven_residual(*, child_trace, event_trace, child_momentum,
                         event_momentum, child_conormal, child_momentum_rate,
                         child_force, event_conormal):
    """Boundary balance, distinct from either side's material reaction."""
    traces = (child_trace, event_trace)
    pairs = (child_momentum, event_momentum, child_conormal,
             child_momentum_rate, child_force, event_conormal)
    if any(x.nrows() != 3 for x in traces) or any(x.nrows() != 2 for x in pairs):
        raise ValueError('three trace and two canonical/flux rows required')
    if len({x.ncols() for x in traces + pairs}) != 1:
        raise ValueError('all outputs must use the same parameter columns')
    trace = child_trace - event_trace
    momentum = child_momentum - event_momentum
    flux = child_conormal + child_momentum_rate - child_force + event_conormal
    return arb_mat(trace.tolist() + momentum.tolist() + flux.tolist())


def event_boundary_outputs(*, event_trace, event_momentum, event_conormal):
    """Unsigned event G7=[Tqe; Pe; Gamma_e], as in the frozen native packet."""
    if (event_trace.nrows(), event_momentum.nrows(), event_conormal.nrows()) != (3, 2, 2):
        raise ValueError('three trace, two momentum and two conormal outputs required')
    if len({x.ncols() for x in (event_trace, event_momentum, event_conormal)}) != 1:
        raise ValueError('common parameter columns required')
    return arb_mat(event_trace.tolist() + event_momentum.tolist() + event_conormal.tolist())


def required_event_boundary_outputs(*, child_trace, child_momentum,
                                    child_conormal, child_momentum_rate, child_force):
    """Child-required event G7; equality to the event arm is the seven balances."""
    if any(x.nrows() != 2 for x in (child_conormal, child_momentum_rate, child_force)):
        raise ValueError('two flux channels required')
    return event_boundary_outputs(event_trace=child_trace, event_momentum=child_momentum,
        event_conormal=child_force-child_momentum_rate-child_conormal)


def native_row_indices(order):
    """Select native rows from [trace3, constraints(2N+1), momentum2, flux2]."""
    if not isinstance(order, int) or order < 2:
        raise ValueError('integer Galerkin order >= 2 required')
    start = 3 + 2 * order + 1
    return (0, 1, 2, start, start + 1, start + 2, start + 3)
