"""Outward arithmetic for a supplied physical-Hessian error ball."""
import math
import numpy as np
from flint import arb, ctx
from bhsm.interface import stored_pullback_assembly_error as assembly


def pullback_hessian_error(output, error_mid, error_radius, coordinates,
                           coordinate_error_upper=0.0):
    """Enclose sym(L E[X*,X*]) about a computed signed correction tensor.

    E is supplied as an entrywise midpoint/radius ball and
    ||X*-coordinates||_2 <= coordinate_error_upper is a caller-owned bound.
    The caller must bind those inputs to the actual physical certificate.
    Output-map construction and physical direction errors are not enclosed
    here. The arithmetic target uses the exact stored output matrix L.
    """
    l, q, r, x = [assembly._real_binary64(value, name) for value, name in (
        (output, 'output'), (error_mid, 'error midpoint'),
        (error_radius, 'error radius'), (coordinates, 'coordinates'))]
    if (q.ndim != 3 or q.shape != r.shape or q.shape[1] != q.shape[2]
            or l.ndim != 2 or x.ndim != 2 or min(q.shape) == 0
            or l.shape[1] != q.shape[0] or x.shape[0] != q.shape[1]
            or min(l.shape) == 0 or min(x.shape) == 0 or np.any(r < 0)):
        raise ValueError('matching nonempty Hessian ball and pullback dimensions required')
    delta = float(coordinate_error_upper)
    if not math.isfinite(delta) or delta < 0:
        raise ValueError('finite nonnegative coordinate error bound required')
    center, center_rounding = assembly.assemble_pullback_with_error(
        l, q, x, symmetrize=True)
    radius_center, radius_rounding = assembly.assemble_pullback_with_error(
        np.abs(l), r, np.abs(x), symmetrize=True)
    center_rounding = center_rounding['assembly_error_frobenius_upper']
    radius_rounding = radius_rounding['assembly_error_frobenius_upper']
    previous = ctx.prec; ctx.prec = assembly.PRECISION
    try:
        radius_norm = (assembly._norm(radius_center) + arb(radius_rounding)).upper()
        # A crude norm is used only for the tiny coordinate perturbation term;
        # the principal error center and radius retain output-channel scaling.
        weighted_source = (assembly._operator(l) * (
            assembly._norm(q) + assembly._norm(r))).upper()
        coordinate_error = (weighted_source * (
            2 * assembly._operator(x) * arb(delta) + arb(delta)**2)).upper()
        enclosing_error = (arb(center_rounding) + radius_norm + coordinate_error).upper()
        total = (assembly._norm(center) + enclosing_error).upper()
        report = dict(
            scope='STORED_OUTPUT_MAP_QUADRATIC_PULLBACK_OF_SUPPLIED_HESSIAN_ERROR_BALL',
            midpoint_assembly_error_frobenius_upper=float(center_rounding),
            propagated_entrywise_radius_frobenius_upper=assembly._float_upper(radius_norm),
            coordinate_perturbation_frobenius_upper=assembly._float_upper(coordinate_error),
            correction_center_frobenius_upper=assembly._float_upper(assembly._norm(center)),
            correction_enclosure_frobenius_radius_upper=assembly._float_upper(enclosing_error),
            total_error_pullback_frobenius_upper=assembly._float_upper(total),
            input_hessian_error_ball_requires_certificate=True,
            coordinate_error_bound_requires_certificate=delta != 0,
            physical_direction_errors_enclosed=False,
            output_map_construction_error_enclosed=False,
            all_node_physical_hessian_enclosed=False,
            neighborhood_remainder_enclosed=False, Gate7_closed=False,
            FULL_BHSM_COMPLETE=False)
    finally: ctx.prec = previous
    return center, report
