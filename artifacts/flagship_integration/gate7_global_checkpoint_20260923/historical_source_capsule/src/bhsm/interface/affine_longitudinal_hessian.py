"""Mean-value Hessian enclosures retaining one signed affine direction.

The enclosed domain is a correlated tube, not its larger coordinate hull.
This module does not provide action derivatives or certify a physical field.
"""
import numpy as np
from flint import arb
from bhsm.interface.physical_arb_inputs import preserve_ball
from bhsm.interface.physical_hs_value import finite_vector
from bhsm.interface.direct_physical_neighborhood import exact_radius, unweight_box


def endpoint_tube(center, frame, axis, radius_longitudinal, radius_transverse,
                  weights, *, fixed=False):
    """Split z+E(e*l+t) into a transverse box and a common scalar direction.

    ||t||2<=rT is enclosed coordinatewise, while l is kept common to every
    component of E*e. Frame/axis interval uncertainty is retained outwardly.
    The descriptor is not unweighted. No unit-axis assumption is made.
    """
    if type(fixed) is not bool:
        raise ValueError('explicit Boolean fixed-endpoint flag required')
    matrix = np.asarray(frame, dtype=object)
    if matrix.ndim != 2 or not all(matrix.shape) or matrix.shape[0] != len(weights)+1:
        raise ValueError('complete augmented rectangular frame required')
    n, k = matrix.shape
    matrix = np.array([preserve_ball(v) for v in matrix.flat], dtype=object).reshape(n, k)
    z = finite_vector([preserve_ball(v) for v in center], n)
    e = finite_vector([preserve_ball(v) for v in axis], k)
    if not all(v.is_finite() for v in matrix.flat):
        raise ValueError('finite frame required')
    rL, rT = exact_radius(radius_longitudinal), exact_radius(radius_transverse)
    if fixed:
        rL, rT = arb(0), arb(0)
    direction = np.array([sum((a*b for a, b in zip(row, e, strict=True)), arb(0))
                          for row in matrix], dtype=object)
    transverse = np.array([(sum((v**2 for v in row), arb(0)).upper().sqrt()*rT).upper()
                           for row in matrix], dtype=object)
    base = np.array([v+arb(0, r) for v, r in zip(z, transverse, strict=True)], dtype=object)
    raw_base = unweight_box(base, weights)
    raw_direction = unweight_box(direction, weights)
    raw_hull = np.array([v+u*arb(0, rL) for v, u in zip(raw_base, raw_direction, strict=True)], dtype=object)
    if not all(v.is_finite() for v in raw_hull):
        raise ArithmeticError('finite full segment hull required')
    return dict(raw_transverse_box=raw_base, raw_longitudinal_direction=raw_direction,
                raw_segment_hull=raw_hull, radius_longitudinal=rL,
                radius_transverse=rT, fixed=fixed)


def enclose_hessian(base_hessian, directional_third, radius_longitudinal):
    """H(B+u*l) subset H(B)+[-rL,rL]*D3S(X)[.,.,u].

    Caller must establish that X contains B+s*u*l for all 0<=s<=1 and that
    directional_third encloses the complete signed action contraction on X.
    Its entries must not be formed by summing absolute input-leg terms first.
    """
    base, third = [np.asarray(v, dtype=object) for v in (base_hessian, directional_third)]
    if base.ndim != 2 or not base.shape[0] or base.shape[0] != base.shape[1] or third.shape != base.shape:
        raise ValueError('matching nonempty square Hessian and third contraction required')
    base = np.array([preserve_ball(v) for v in base.flat], dtype=object).reshape(base.shape)
    third = np.array([preserve_ball(v) for v in third.flat], dtype=object).reshape(third.shape)
    if not all(v.is_finite() for a in (base, third) for v in a.flat):
        raise ValueError('finite Hessian operands required')
    segment = arb(0, exact_radius(radius_longitudinal))
    result = base+segment*third
    if not all(v.is_finite() for v in result.flat):
        raise ArithmeticError('finite mean-value Hessian enclosure required')
    return result
