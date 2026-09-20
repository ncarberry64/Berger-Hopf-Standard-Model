"""Analytic dependency and residual checks; no physical closure assertions."""
import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface.shared_parameter_residual import (
    PolynomialMatrix as Poly, affine_dot_polynomial, quadratic_support,
    coupled_first_variation_residual, solve_projected_residual,
    lifted_rate_residual, hs_right_column_residual)


def poly(terms, rows=1, cols=1):
    return Poly({key: arb_mat(rows, cols, [arb(v) for v in values])
                 for key, values in terms.items()}, rows, cols, 1)


def test_shared_dependency_survives_two_implicit_solves():
    # e1=theta, e2=e1/4+3theta/4. The true output e1-e2 is identically
    # zero, whereas separate boxes for the two solutions allow +/-2.
    r = poly({(0,): [1, '0.75']}, 2, 1)
    E = poly({(): [0, 0, '0.25', 0]}, 2, 2)
    bounds, proof = solve_projected_residual(r, E, arb_mat([[1, -1]]), [arb(1)]*2)
    assert bounds[0].is_zero()
    assert all(v.is_zero() for v in proof['projected_tail_operator'].entries())
    assert not proof['shared_parameter_polynomial'].terms


def test_common_parameter_survives_variable_inverse_and_tail():
    # e=theta/(1-theta/4), |theta|<=1; maximum absolute value is 4/3.
    r = poly({(0,): [1]})
    E = poly({(0,): ['0.25']})
    bounds, proof = solve_projected_residual(r, E, arb_mat([[1]]), [arb(1)], steps=2)
    assert bounds[0] >= arb(4)/3 and bounds[0] < arb('1.333334')
    assert set(proof['shared_parameter_polynomial'].terms) == {(0,), (0, 0)}


def test_uncertain_coefficients_do_not_cancel_as_if_exact():
    r = Poly({(0,): arb_mat(2, 1, [arb(1, '0.1'), arb(1, '0.1')])}, 2, 1, 1)
    E = Poly({}, 2, 2, 1)
    bounds, _ = solve_projected_residual(r, E, arb_mat([[1, -1]]), [arb(1)]*2)
    assert bounds[0] >= arb('0.2')


def test_polynomial_quadratic_combines_same_monomials_before_support():
    # x=(theta,theta), y=(theta,-theta); dot(x,y)=0 at the same input.
    x = arb_mat([[0, 1], [0, 1]])
    y = arb_mat([[0, 1], [0, -1]])
    assert quadratic_support(affine_dot_polynomial(x, y), [(0, 1, 'interval')]).is_zero()
    # theta0^2+theta1^2 <= 1 on a unit Euclidean ball. This nonoptimal
    # support implementation may overbound, but must contain the true range.
    C = arb_mat([[0, 0, 0], [0, 1, 0], [0, 0, 1]])
    assert quadratic_support(C, [(0, 2, 'euclidean')]) >= 1


def test_exact_normalization_residual_is_not_assumed_zero():
    p = arb_mat([[1, 0], [0, 1]])
    g = affine_dot_polynomial(p, p)/2
    g[0, 0] -= arb('0.5')
    result = quadratic_support(g, [(0, 1, 'interval')])
    assert result == arb('0.5')  # discarded quadratic would incorrectly be zero
    with pytest.raises(ValueError, match='cover'):
        quadratic_support(g, [])


def test_actual_coupled_residual_equations_and_bottom_row_dependency():
    # H=diag(0,2), psi=(1,0), lambda=0, hard=(0,theta), border=1.
    # source=(1,2theta). Along theta: H_u=0, psi_u=0, hard_u=(0,1).
    # All eight unchanged residual blocks must vanish, including the lower
    # response variation row; perturbing it must be detected.
    zero = poly({})
    psi = poly({(): [1, 0]}, 2)
    hard = poly({(0,): [0, 1]}, 2)
    psi_u = poly({}, 2)
    hu = poly({(): [0, 1]}, 2)
    args = [poly({(): [0, 0, 0, 2]}, 2, 2), poly({}, 2, 2),
            poly({(): [1, 0], (0,): [0, 2]}, 2), poly({(): [0, 2]}, 2),
            psi, zero, hard, poly({(): [1]}), psi_u, zero, hu, zero]
    residual = coupled_first_variation_residual(*args)
    assert all(not value.terms for value in residual.values())
    args[-2] = poly({(): [1, 1]}, 2)
    residual = coupled_first_variation_residual(*args)
    assert residual['axis_response_normalization'].terms[()][0, 0] == 1


def test_no_stacked_contraction_is_inferred_from_invertible_blocks():
    # Each diagonal block is exactly inverted, but an unweighted off-diagonal
    # coupling of 2 is not a contraction in the supplied norm.
    with pytest.raises(ArithmeticError, match='stacked'):
        solve_projected_residual(poly({(): [1, 1]}, 2),
            poly({(): [0, 0, 2, 0]}, 2, 2), arb_mat([[1, 1]]), [arb(1)]*2)


def test_lifted_norm_keeps_derivative_of_the_same_denominator():
    result = lifted_rate_residual(poly({(): [2]}), poly({(): [4]}),
        poly({(): [3]}), poly({(): [5]}), poly({(): [2]}), poly({(): [4]}),
        poly({(): [1, '1.5']}, 2), poly({(): [0, '-0.5']}, 2))
    assert all(not value.terms for value in result.values())
    # Dropping norm_u loses the common normalization derivative.
    result = lifted_rate_residual(poly({(): [2]}), poly({(): [4]}),
        poly({(): [3]}), poly({(): [5]}), poly({(): [2]}), poly({}),
        poly({(): [1, '1.5']}, 2), poly({(): [0, '-0.5']}, 2))
    assert result['rate_u'].terms[()][0, 0] == -4


def test_hs_chain_keeps_endpoint_dependency_in_midpoint_and_column():
    # h=2, L=theta, R=2theta, F_L=L, F_R=R gives M=5theta/4.
    # A=3theta and w=1/2-3theta/4. With B=w the theta terms in D cancel.
    result = hs_right_column_residual(poly({(0,): [1]}), poly({(0,): [2]}),
        poly({(0,): ['1.25']}), poly({(0,): [1]}), poly({(0,): [2]}),
        poly({(0,): [3]}), poly({(): ['0.5'], (0,): ['-0.75']}),
        poly({(): ['0.5'], (0,): ['-0.75']}), poly({(): [1]}), arb(2),
        arb_mat([[1]]), arb_mat([[1]]), arb_mat([[1]]))
    assert not result['midpoint_relation'].terms
    assert not result['chain_direction'].terms
    column = result['projected_right_column']
    assert column.terms[()][0, 0].contains(arb(2)/3)
    assert all(v[0, 0].contains(0) for k, v in column.terms.items() if k)


def test_normalization_alone_leaves_arbitrarily_large_tangent_response():
    # At theta=0, psi=(1,0), hard=0, psi_u=0, hard_u=(0,K).
    # Every normalization row vanishes for arbitrary K. With b=s=1,
    # N=psi+hard and N_u=hard_u, the normalized derivative still has size K.
    # This is an information-sufficiency example, not a BHSM physical state.
    for K in (2, 1000):
        psi = arb_mat([[1, 0], [0, 0]])
        zero = arb_mat(2, 2)
        hu = arb_mat([[0, 0], [K, 0]])
        assert shared_dot_zero(psi, zero)
        assert shared_dot_zero(psi, hu)
        result = lifted_rate_residual(poly({(): [1, 0]}, 2), poly({(): [0, K]}, 2),
            poly({}), poly({}), poly({(): [1]}), poly({}),
            poly({(): [1, 0, 0]}, 3), poly({(): [0, K, 0]}, 3))
        assert all(not value.terms for value in result.values())


def shared_dot_zero(left, right):
    return all(v.is_zero() for v in affine_dot_polynomial(left, right).entries())


@pytest.fixture(autouse=True)
def precision():
    previous = ctx.prec
    ctx.prec = 128
    yield
    ctx.prec = previous
