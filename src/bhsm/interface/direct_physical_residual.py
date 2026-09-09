"""Enclose direct HS residuals through the unchanged frozen causal inverse."""
import numpy as np
from flint import arb, arb_mat, ctx
from bhsm.interface.physical_hs_value import finite_vector
from bhsm.interface.current_green_midpoint_coordinate_error import _float_upper, _real_binary64
from bhsm.interface.current_green_causal_error import transport_local_errors
from bhsm.interface.stored_causal_arithmetic_envelope import (
    fixed_axis_projection_norms, combine_stored_causal_errors,
)


def norm_upper(values):
    entries = list(values)
    if not entries or not all(v.is_finite() for v in entries):
        raise ArithmeticError('complete finite entries required for norm')
    return sum((abs(v).upper()**2 for v in entries), arb(0)).sqrt().upper()


def local_residual_source(right, test, left_state, right_state, left_rate, middle_rate, right_rate, step):
    """Return -R^-1 T [z1-z0-h(f0+4fm+f1)/6], retaining every input radius."""
    r, t = _real_binary64(right, 'right block'), _real_binary64(test, 'test frame')
    if r.ndim != 2 or r.shape[0] == 0 or r.shape[0] != r.shape[1] or t.ndim != 2 or t.shape[0] != r.shape[0]:
        raise ValueError('square right block and matching test frame required')
    count = t.shape[1]
    z0, z1, f0, fm, f1 = [finite_vector(v, count) for v in (left_state, right_state, left_rate, middle_rate, right_rate)]
    h = arb(step)
    if not h.is_finite() or not h.rad().is_zero() or not h > 0:
        raise ValueError('positive exact stored step required')
    residual = z1-z0-h*(f0+4*fm+f1)/6
    rhs = arb_mat(t.tolist())*arb_mat(count, 1, residual.tolist())
    source = -arb_mat(r.tolist()).inv()*rhs
    if not all(v.is_finite() for v in source.entries()):
        raise ArithmeticError('nonfinite local residual solve')
    return np.array(source.entries(), dtype=object)


def bound_causal_residual(maps, sources, axes, map_gain):
    """Signed centers plus separate source radii; apply map perturbation once.

    Caller owns physical branch identification and verification that map_gain
    bounds the frozen map construction for these exact stored maps and axes.
    """
    p, a = _real_binary64(maps, 'maps'), _real_binary64(axes, 'axes')
    if (p.ndim != 3 or p.shape[0] == 0 or p.shape[1] == 0 or p.shape[1] != p.shape[2]
            or a.shape != (p.shape[0]+1, p.shape[1]) or len(sources) != len(p)):
        raise ValueError('complete square causal maps, axes and sources required')
    previous = ctx.prec
    ctx.prec = 512
    try:
        dimension = p.shape[1]
        z = arb_mat(dimension, 1)
        rows, radii = [], []
        for i, values in enumerate(sources):
            source = finite_vector(values, dimension)
            radii.append(_float_upper(norm_upper(v.rad() for v in source)))
            center = arb_mat(dimension, 1, [v.mid() for v in source])
            z = arb_mat(p[i].tolist())*z+center
            axis = arb_mat(1, dimension, a[i+1].tolist())
            longitudinal = (axis*z)[0, 0]
            transverse = z-axis.transpose()*(axis*z)
            rows.append(dict(node=i+1, longitudinal_upper=_float_upper(abs(longitudinal)),
                transverse_upper=_float_upper(norm_upper(transverse.entries()))))
        coefficients = [max(row[key] for row in rows) for key in ('longitudinal_upper', 'transverse_upper')]
        transport = transport_local_errors(p, np.asarray(radii))
        projection = fixed_axis_projection_norms(a)
        combined = combine_stored_causal_errors(coefficients,
            [transport['maximum_node_error_norm_upper']], map_gain, projection)
        return dict(scope='DIRECT_RESIDUAL_THROUGH_VERIFIED_FROZEN_MAPS_CONDITIONAL_ON_SELECTED_BRANCH',
            signed_center_rows=rows, signed_center_projection_bounds_upper=coefficients,
            local_source_radii_upper=radii, source_uncertainty_transport=transport,
            fixed_axis_projection_norms_upper=projection,
            frozen_inverse_residual_bounds_upper=combined['frozen_map_transverse_quadratic_coefficients_upper'],
            map_source_error=combined['frozen_map_response_error_coefficient_upper'],
            map_source_cross_errors_included=True, midpoint_Taylor_truncation_used=False,
            physical_branch_identification_certified=False, physical_Y_recertified=False,
            Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    finally:
        ctx.prec = previous
