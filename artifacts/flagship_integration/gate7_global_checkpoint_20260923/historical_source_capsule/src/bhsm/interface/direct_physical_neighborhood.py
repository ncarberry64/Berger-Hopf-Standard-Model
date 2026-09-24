"""Outward coordinate boxes for the frozen affine two-radius HS domain.

This constructs a domain. It does not prove uniform field regularity, a
constraint chart, or a contraction on that domain.
"""
import numpy as np
from flint import arb
from bhsm.interface.physical_arb_inputs import preserve_ball
from bhsm.interface.physical_hs_value import finite_vector


def exact_radius(value):
    result = preserve_ball(value)
    if not result.rad().is_zero() or not result >= 0:
        raise ValueError('exact nonnegative radius required')
    return result


def affine_endpoint_box(center, frame, axis, radius_longitudinal,
                        radius_transverse, *, fixed=False):
    """Enclose z + E(e*l+t), |l|<=rL, ||t||2<=rT, with frozen E and e.

    The transverse domain is the full coordinate-space ball, a superset of
    its axis-orthogonal subspace. The stored axis need not have unit norm.
    Interval leaves and cancellation inside E*e are preserved.
    """
    if type(fixed) is not bool:
        raise ValueError('explicit Boolean fixed-endpoint flag required')
    matrix = np.asarray(frame, dtype=object)
    if matrix.ndim != 2 or not all(matrix.shape):
        raise ValueError('nonempty rectangular frame required')
    n, k = matrix.shape
    base = finite_vector([preserve_ball(v) for v in center], n)
    direction = finite_vector([preserve_ball(v) for v in axis], k)
    matrix = np.array([preserve_ball(v) for v in matrix.flat], dtype=object).reshape(n, k)
    r_long, r_trans = exact_radius(radius_longitudinal), exact_radius(radius_transverse)
    radii = []
    for row in matrix:
        longitudinal = abs(sum((a*b for a, b in zip(row, direction, strict=True)), arb(0)))
        # An interval representation of a sum of squares may have a tiny
        # negative lower endpoint after radius rounding. Only its upper
        # endpoint is needed for the supremum norm; take that before sqrt.
        transverse = sum((a**2 for a in row), arb(0)).upper().sqrt()
        radius = arb(0) if fixed else (longitudinal*r_long + transverse*r_trans).upper()
        if not radius.is_finite() or not radius >= 0:
            raise ArithmeticError('finite outward coordinate radius required')
        radii.append(radius)
    boxes = np.array([z + arb(0, r) for z, r in zip(base, radii, strict=True)], dtype=object)
    if not all(v.is_finite() for v in boxes):
        raise ArithmeticError('finite endpoint box required')
    return boxes, np.array(radii, dtype=object)


def unweight_box(weighted, weights):
    """Recover raw state plus the unchanged descriptor using frozen weights."""
    weight = finite_vector([preserve_ball(v) for v in weights], len(weights))
    if not all(v > 0 and v.rad().is_zero() for v in weight):
        raise ValueError('exact positive frozen weights required')
    box = finite_vector([preserve_ball(v) for v in weighted], len(weight)+1)
    result = np.array([z/w for z, w in zip(box[:-1], weight, strict=True)]+[box[-1]], dtype=object)
    if not all(v.is_finite() for v in result):
        raise ArithmeticError('finite raw endpoint box required')
    return result
