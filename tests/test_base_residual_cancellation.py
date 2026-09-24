import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor
from bhsm.interface.base_residual_cancellation import (
    BaseResidualBlock, weighted_tail_at_input, weighted_tail_on_physical_input)


@pytest.fixture(autouse=True)
def precision():
    previous = ctx.prec
    ctx.prec = 256
    yield
    ctx.prec = previous


def test_mixed_base_input_term_is_cancelled_with_its_nonlinear_residual_tail():
    domain = TaylorDomain([(0, 2, 'box')], 2)
    # On the graph z=x^2, G=z-x^2=0. The discarded quadratic has radius 1.
    residual = domain.affine(0, [0, 1], 1)
    original = InputLinearTaylor(domain, arb_mat([[0, 0]]),
        arb_mat([[0, 0], [0, 2]]), 0, [(0, 1, 'euclidean'), (1, 2, 'box')])
    polynomial, weighted = BaseResidualBlock([residual], [1]).cancel(original)
    assert polynomial.support().is_zero()
    direction = arb_mat([[1], [arb(3)/8]])
    added = weighted_tail_at_input(weighted, direction)
    assert added == arb(3)/4
    assert weighted_tail_on_physical_input(weighted, [(1, arb_mat([[arb(3)/8]]))], 1) == added
    # The graph attains this value at x=z=u=1: omitting the tail is invalid.
    assert 2 * arb(3)/8 == added


def test_cancellation_preserves_shared_physical_state_coefficient():
    domain = TaylorDomain([(0, 2, 'box')], 2)
    residual = domain.affine(0, [-arb(1)/16, 1])
    original = InputLinearTaylor(domain, arb_mat([[0]]), arb_mat([[0], [2]]))
    polynomial, weighted = BaseResidualBlock([residual], [1]).cancel(original)
    assert polynomial.a == arb_mat([[arb(1)/8], [0]])
    assert all(v.is_zero() for v in weighted.entries())
    assert polynomial.support() == arb(1)/8


def test_uncertain_jacobian_is_retained_after_point_covector_selection():
    domain = TaylorDomain([(0, 1, 'box')], 1)
    coefficient = arb(1, arb(1)/64)
    residual = domain.affine(0, [coefficient], arb(1)/128)
    original = InputLinearTaylor(domain, arb_mat([[0]]), arb_mat([[1]]))
    polynomial, weighted = BaseResidualBlock([residual], [0]).cancel(original)
    assert polynomial.a[0, 0].contains(arb(1)/64)
    assert polynomial.a[0, 0].contains(-arb(1)/64)
    assert weighted_tail_at_input(weighted, arb_mat([[1]])) >= arb(1)/128


def test_incomplete_physical_input_mapping_is_rejected():
    with pytest.raises(ValueError, match='every auxiliary'):
        weighted_tail_on_physical_input(arb_mat([[1, 2, 3]]), [(1, arb_mat([[1]]))], 1)


def test_cancel_before_interval_transport_preserves_its_shared_residual_factor():
    domain = TaylorDomain([(0, 2, 'box')], 2)
    residual = domain.affine(0, [-1, 1])
    block = BaseResidualBlock([residual], [1])
    value = InputLinearTaylor(domain, arb_mat([[0]]), arb_mat([[-1], [1]]))
    transport = arb(2, arb(1)/8)
    polynomial, weighted = block.cancel(value)
    before = polynomial * transport
    after, _ = block.cancel(value * transport)
    # Both are valid on z=x; only the first keeps M*(z-x)=M*0 intact.
    assert before.support().is_zero()
    assert all(v.is_zero() for v in weighted.entries())
    assert after.support() >= arb(1)/4
