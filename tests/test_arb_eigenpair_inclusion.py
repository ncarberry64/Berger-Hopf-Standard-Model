import numpy as np
import pytest
from flint import arb, ctx, fmpq
from bhsm.interface.arb_eigenpair_inclusion import verify_eigenpair_box


def proposal():
    return np.array([arb(1, '1e-5'), arb(0, '1e-5')], dtype=object), arb(1, '1e-5')


def test_uncertain_symmetric_matrix_has_a_unique_enclosed_normalized_eigenpair():
    h = np.array([[arb(1, '1e-8'), arb(0, '1e-8')],
                  [arb(0, '1e-8'), arb(3, '1e-8')]], dtype=object)
    p, lam = proposal()
    result = verify_eigenpair_box(h, p, lam)
    assert result['normalized_eigenpair_enclosed']
    assert result['weighted_contraction_upper'] < .001
    assert result['maximum_image_radius_ratio_upper'] < .01
    assert result['floating_spectral_gap_assumed'] is False
    assert result['physical_branch_identification_certified'] is False


def test_wrong_proposed_eigenvalue_fails_inclusion_despite_small_derivative():
    p, lam = proposal()
    result = verify_eigenpair_box(np.diag([2., 3.]), p, lam)
    assert result['contraction']
    assert not result['strict_self_inclusion']
    assert not result['validation_passed']


def test_boundary_eigenvalue_does_not_pass_strict_inclusion():
    delta = 2.**-20
    p = np.array([arb(1, delta), arb(0, delta)], dtype=object)
    result = verify_eigenpair_box(np.diag([1+delta, 3.]), p, arb(1, delta))
    assert not result['validation_passed']


def test_multiple_eigenvalue_rejects_singular_center_jacobian():
    p, lam = proposal()
    with pytest.raises(ArithmeticError, match='singular|nonfinite'):
        verify_eigenpair_box(np.eye(2), p, lam)


def test_precision_restored_and_zero_radius_rejected():
    before = ctx.prec
    p, lam = proposal()
    verify_eigenpair_box(np.diag([1., 3.]), p, lam, precision=256)
    assert ctx.prec == before
    with pytest.raises(ValueError, match='positive proposed radii'):
        verify_eigenpair_box(np.eye(2), p, arb(1))
    assert ctx.prec == before


def test_nonfinite_and_shape_errors_fail_closed():
    p, lam = proposal()
    with pytest.raises(ValueError, match='finite'):
        verify_eigenpair_box(np.diag([float('nan'), 3.]), p, lam)
    with pytest.raises(ValueError, match='matching vector'):
        verify_eigenpair_box(np.eye(3), p, lam)


def test_saved_target_radius_is_not_silently_enlarged_on_reconstruction():
    p, lam = proposal()
    exact = [v.rad().fmpq() for v in [*p, lam]]
    reconstructed = [arb(arb(v.mid().fmpq()), arb(r)) for v, r in zip([*p, lam], exact)]
    result = verify_eigenpair_box(np.diag([1., 3.]), reconstructed[:2], reconstructed[2],
                                 exact_radii=exact)
    assert result['validation_passed']
    assert list(map(fmpq, result['target_radii_rational'])) == exact
    with pytest.raises(ValueError, match='target radii'):
        verify_eigenpair_box(np.diag([1., 3.]), p, lam, exact_radii=[1., 1., 1.])
