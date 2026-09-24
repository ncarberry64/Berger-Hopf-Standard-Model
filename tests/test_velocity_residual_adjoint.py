from flint import arb, arb_mat, ctx
import pytest
from bhsm.interface.velocity_residual_adjoint import directional_covectors


def test_both_coupled_directional_unknowns_cancel_in_velocity_output():
    previous = ctx.prec
    try:
        ctx.prec = 256
        # A saddle matrix with a nonzero null eigenline, as in the retained
        # eigenpair system. Its border makes the complete system invertible.
        K = arb_mat([[0, 0, 1], [0, 2, 0], [1, 0, 0]])
        psi = [arb(1), arb(0)]
        hard = [arb(0), arb(3)]
        border, scale = arb(2), arb(5)
        output = [arb(3), arb(-2)]
        v2, v3, e2, e3 = directional_covectors(K, hard, border, scale, output)
        assert all(v.is_zero() for v in e2.entries()+e3.entries())
        line_rhs = arb_mat([[2], [-3], [1]])
        response_rhs = arb_mat([[4], [1], [-2]])
        expected = sum((v2[i]*line_rhs[i, 0]+v3[i]*response_rhs[i, 0] for i in range(3)), arb(0))
        expected += arb(7)*sum((output[i]*hard[i] for i in range(2)), arb(0))
        for line, response in (([1, 2, 3], [4, 5, 6]), ([-3, 0, 9], [2, -4, 1]), ([0, 0, 0], [0, 0, 0])):
            pu = arb_mat(3, 1, line); hu = arb_mat(3, 1, response)
            G2 = K*pu-line_rhs
            G3 = K*hu-response_rhs + arb_mat(3, 1,
                [border*pu[i, 0] for i in range(2)] + [sum((hard[i]*pu[i, 0] for i in range(2)), arb(0))])
            omega = sum((output[i]*(hu[2, 0]*psi[i]+border*pu[i, 0]+7*hard[i]+scale*hu[i, 0]) for i in range(2)), arb(0))
            corrected = omega-sum((v2[i]*G2[i, 0]+v3[i]*G3[i, 0] for i in range(3)), arb(0))
            assert corrected == expected
        with pytest.raises(ValueError, match='compatible'):
            directional_covectors(K, hard, border, scale, [1])
    finally:
        ctx.prec = previous
