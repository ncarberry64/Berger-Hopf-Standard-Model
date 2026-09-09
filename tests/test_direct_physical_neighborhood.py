from fractions import Fraction
from itertools import product
import numpy as np
import pytest
from flint import arb, ctx, fmpq
from bhsm.interface import direct_physical_neighborhood as domain
from bhsm.interface import physical_hs_value as hs


@pytest.fixture(autouse=True)
def precision():
    previous = ctx.prec
    ctx.prec = 256
    yield
    ctx.prec = previous


def test_nonunit_axis_and_row_norm_extremizers_are_enclosed():
    frame, axis = [[3, 4], [0, -2]], [2, -1]
    boxes, radii = domain.affine_endpoint_box([7, 9], frame, axis, 2, 5)
    assert radii[0] == 29 and radii[1] == 14
    # Independently attain the coordinate extrema using E's row directions.
    for sign in (-1, 1):
        assert boxes[0].contains(arb(7 + sign*29))
        assert boxes[1].contains(arb(9 + sign*14))
    assert not boxes[0].contains(arb(37))


def test_rational_disk_samples_with_signed_frame_and_axis():
    frame = [[3, 4], [-5, 12], [1, -1]]
    axis = [2, -3]
    center = [1, 2, 3]
    boxes, _ = domain.affine_endpoint_box(center, frame, axis, 2, 5)
    disk = [(Fraction(3), Fraction(4)), (Fraction(4), Fraction(3)),
            (Fraction(0), Fraction(5)), (Fraction(1, 2), Fraction(1, 3))]
    for longitudinal, transverse, sx, sy in product((-2, 0, 2), disk, (-1, 1), (-1, 1)):
        t = (sx*transverse[0], sy*transverse[1])
        for row, z, box in zip(frame, center, boxes, strict=True):
            value = Fraction(z)+sum(Fraction(a)*(e*longitudinal+b) for a, e, b in zip(row, axis, t))
            assert box.contains(arb(fmpq(value.numerator, value.denominator)))


def test_interval_frame_and_axis_leaves_are_not_narrowed():
    boxes, _ = domain.affine_endpoint_box([arb(10, 1)], [[arb(2, 1), arb(-1, 1)]],
                                        [arb(1, 1), arb(0, 1)], 1, 1)
    for z, a, b, e, f, l, t in product((9, 11), (1, 3), (-2, 0), (0, 2), (-1, 1), (-1, 1), (-1, 1)):
        # t lies along the first coordinate; norm is one.
        assert boxes[0].contains(arb(z+(a*e+b*f)*l+a*t))


def test_fixed_initial_endpoint_keeps_center_uncertainty_only():
    center = [arb(1, '0.125'), arb(2)]
    boxes, radii = domain.affine_endpoint_box(center, np.eye(2, dtype=int), [2, 0], 3, 4, fixed=True)
    assert all(r.is_zero() for r in radii)
    assert all(a.contains(b) and a.mid() == b.mid() for a, b in zip(boxes, center))
    assert boxes[1] == 2


def test_signed_longitudinal_contraction_precedes_absolute_value():
    _, radii = domain.affine_endpoint_box([0], [[1, -1]], [7, 7], 100, 0)
    assert radii[0].is_zero()


def test_raw_weighting_and_serialization_preserve_entire_box():
    box, _ = domain.affine_endpoint_box([arb(1, '0.1'), arb(3)], [[3], [2]], [2], 1, 1)
    raw = domain.unweight_box(box, [2])
    assert (raw[0]*2).contains(box[0])
    assert raw[1].contains(box[1])
    m, r = hs.rational_balls(raw)
    assert all(a.contains(b) for a, b in zip(hs.restore_balls(m, r), raw))


def test_nonlinear_endpoint_rates_are_needed_for_actual_midpoint_tube():
    left, _ = domain.affine_endpoint_box([2], [[1]], [1], 1, 0)
    right, _ = domain.affine_endpoint_box([4], [[1]], [1], 1, 0)
    uniform = hs.physical_midpoint(left, right, [left[0]**2], [right[0]**2], 1)
    center_only = hs.physical_midpoint(left, right, [4], [16], 1)
    for a, b in product((1, 2, 3), (3, 4, 5)):
        value = arb(fmpq(a+b, 2)+fmpq(a*a-b*b, 8))
        assert uniform[0].contains(value)
    # a=1,b=5 gives zero; using only the center rates loses this value.
    assert not center_only[0].contains(arb(0))


@pytest.mark.parametrize('bad', [-1, arb(1, '0.1'), float('inf'), True])
def test_invalid_radius_rejected(bad):
    with pytest.raises((ValueError, TypeError)):
        domain.affine_endpoint_box([0], [[1]], [1], bad, 1)


@pytest.mark.parametrize('weights', [[0], [-1], [arb(2, '0.1')], [float('nan')]])
def test_invalid_frozen_weights_rejected(weights):
    with pytest.raises((ValueError, TypeError)):
        domain.unweight_box([1, 2], weights)


def test_bad_dimensions_and_nonfinite_frame_rejected():
    for frame, axis in (([[1, 2]], [1]), ([], []), ([[float('nan')]], [1])):
        with pytest.raises((ValueError, TypeError)):
            domain.affine_endpoint_box([0], frame, axis, 1, 1)
