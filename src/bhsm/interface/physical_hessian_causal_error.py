"""Assemble certified midpoint and endpoint Hessian error coefficients."""
import math
from flint import arb, ctx
from bhsm.interface.current_green_midpoint_coordinate_error import _float_upper


def assemble_local_bounds(midpoints, endpoints, *, intervals=370, selected_only=False):
    """Join incident errors in the common squared block-sup input radius.

    Midpoint values already include the factor two for a two-endpoint input.
    Endpoint values are single-node coefficients, and are not doubled again.
    In selected mode the returned vector describes only the explicitly selected
    additive component. Its zeros say nothing about uncomputed physical errors.
    """
    if type(intervals) is not int or intervals < 1:
        raise ValueError('positive interval count required')
    if any(type(i) is not int or not 0 <= i < intervals for i in midpoints):
        raise ValueError('invalid midpoint index')
    if any(type(n) is not int or not 1 <= n <= intervals for n in endpoints):
        raise ValueError('invalid noninitial endpoint index')
    for node, components in endpoints.items():
        expected = {(node-1, 'right')}
        if node < intervals:
            expected.add((node, 'left'))
        if set(components) != expected:
            raise ValueError('every selected endpoint must include both incident slots')
    values = [*midpoints.values(), *(v for c in endpoints.values() for v in c.values())]
    if any(isinstance(v, bool) or not math.isfinite(v) or v < 0 for v in values):
        raise ValueError('finite nonnegative error coefficients required')
    missing_midpoints = sorted(set(range(intervals)) - midpoints.keys())
    missing_endpoints = sorted(set(range(1, intervals+1)) - endpoints.keys())
    complete = not missing_midpoints and not missing_endpoints
    if not complete and not selected_only:
        raise RuntimeError('complete physical Hessian coverage required; missing errors are unknown')
    previous = ctx.prec
    ctx.prec = 512
    try:
        rows = []
        for index in range(intervals):
            terms = []
            if index in midpoints:
                terms.append(midpoints[index])
            for node, label in ((index, 'left'), (index+1, 'right')):
                if node in endpoints:
                    terms.append(endpoints[node][index, label])
            rows.append(_float_upper(sum((arb(float(v)) for v in terms), arb(0))))
    finally:
        ctx.prec = previous
    return dict(local_coefficients_upper=rows,
                coverage=dict(midpoints=sorted(midpoints), endpoints=sorted(endpoints),
                              missing_midpoints=missing_midpoints,
                              missing_endpoints=missing_endpoints, complete=complete),
                scope=('SELECTED_ADDITIVE_HESSIAN_ERROR_COMPONENT_ONLY' if selected_only
                       else 'COMPLETE_CENTER_HESSIAN_ERROR_COMPONENT_AT_STORED_FRAMES'),
                missing_errors_assumed_zero=False)
