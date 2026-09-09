from types import SimpleNamespace
import numpy as np
import pytest
from flint import arb, ctx, fmpq
from bhsm.interface import physical_hs_value as hs


def test_weighted_center_preserves_product_lost_by_binary64_rounding():
    previous = ctx.prec
    ctx.prec = 256
    try:
        x, w = 1+2.**-27, 1-2.**-27
        result = hs.weighted_endpoint([x], 3., [w])
        assert result[0] == arb(1)-arb(2)**-54
        assert not result[0].contains(arb(x*w))
        assert result[1] == 3
    finally:
        ctx.prec = previous


def test_midpoint_keeps_endpoint_rate_uncertainty_and_signed_hs_term():
    a, b = [arb(2), arb(4)], [arb(6), arb(8)]
    result = hs.physical_midpoint(a, b, [arb(5, 1), arb(1)], [arb(1), arb(3)], 2)
    assert result[0].contains(arb(fmpq(19, 4)))
    assert result[0].contains(arb(fmpq(21, 4)))
    assert result[1] == arb(fmpq(11, 2))
    with pytest.raises(ValueError):
        hs.physical_midpoint(a, b, [1], [2], 2)
    with pytest.raises(ValueError):
        hs.physical_midpoint(a, b, a, b, -1)


def test_serialized_balls_contain_source_and_reject_negative_radii():
    values = np.array([arb(1, '0.125'), arb('1e-120', '1e-150'), arb(0)], dtype=object)
    mid, rad = hs.rational_balls(values)
    restored = hs.restore_balls(mid, rad)
    assert all(a.contains(b) for a, b in zip(restored, values))
    with pytest.raises(ValueError, match='negative radius'):
        hs.restore_balls(['1'], ['-1/8'])


def test_failed_eigenpair_cannot_escape_and_parent_is_restored():
    def proposal(hessian, midpoint, reference):
        return np.array([arb(1, '1e-5'), arb(0, '1e-5')]), arb(2, '1e-5'), 10., 0.
    cert = SimpleNamespace(_eigenline=proposal, QDIM=0)
    checks = []
    with pytest.raises(ArithmeticError, match='inclusion'):
        with hs.verified_eigenline(cert, checks):
            cert._eigenline(np.diag([1., 3.]), None, [1., 0.])
    assert cert._eigenline is proposal
    assert checks == []


def test_verified_orientation_still_does_not_claim_physical_branch():
    def proposal(hessian, midpoint, reference):
        return np.array([arb(1, '1e-5'), arb(0, '1e-5')]), arb(1, '1e-5'), 10., 0.
    cert = SimpleNamespace(_eigenline=proposal, QDIM=0)
    checks = []
    with hs.verified_eigenline(cert, checks):
        cert._eigenline(np.diag([1., 3.]), None, [1., 0.])
    assert checks[0]['validation_passed']
    assert checks[0]['physical_branch_identification_certified'] is False
    with pytest.raises(ArithmeticError, match='orientation'):
        with hs.verified_eigenline(cert, []):
            cert._eigenline(np.diag([1., 3.]), None, [-1., 0.])


def test_nonfinite_or_nonpositive_operands_are_rejected():
    with pytest.raises(ValueError):
        hs.weighted_endpoint([1.], 0., [0.])
    with pytest.raises(ValueError):
        hs.finite_vector([arb('nan')], 1)


def test_value_wrapper_checks_the_requested_spectral_index():
    def proposal(hessian, midpoint, reference):
        return np.array([arb(1, '1e-5'), arb(0, '1e-5')]), arb(1, '1e-5'), 10., 0.
    cert = SimpleNamespace(_eigenline=proposal, QDIM=0)
    matrix = np.diag([1., 3.])
    checks = []
    with hs.verified_eigenline(cert, checks, expected_index=0):
        cert._eigenline(matrix, matrix, [1., 0.])
    assert checks[0]['selected_zero_based_index_verified'] == 0
    with pytest.raises(ArithmeticError, match='index verification') as failure:
        with hs.verified_eigenline(cert, [], expected_index=1):
            cert._eigenline(matrix, matrix, [1., 0.])
    assert failure.value.eigenpair_inclusion['spectral_index_verification']['validation_passed'] is False
    assert cert._eigenline is proposal
