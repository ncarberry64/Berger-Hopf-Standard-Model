from flint import arb, arb_mat, ctx
from bhsm.interface.coupled_action_output_adjoint import FirstJet, linearize, adjoint_proposal


def test_full_adjoint_recovers_upstream_line_and_response_coupling():
    old = ctx.prec
    ctx.prec = 128
    try:
        # p=(1,0), h=0, b=s=1, Hu=0. The second normalized velocity
        # derivative is pu_y+hu_y. Its two equations are 2pu_y and
        # 2hu_y+pu_y, hence adjoint weights 1/4 and 1/2 respectively.
        H, Hu = arb_mat([[0, 0], [0, 2]]), arb_mat(2, 2)
        zero, unit = [arb(0)]*2, [arb(1)]*2
        centers = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
        descriptors = lambda *args: [FirstJet(arb(0), arb_mat(1, 12)) for _ in range(4)]
        J, gradient, value = linearize(H, Hu, [arb(0)], [arb(0)],
                                       unit, 1, 0, [arb(0), arb(0), arb(1), arb(0)], centers, descriptors)
        beta, defect = adjoint_proposal(J, gradient)
        assert value.is_zero()
        assert beta[0, 7] == arb('0.25')
        assert beta[0, 10] == arb('0.5')
        assert all(x.is_zero() for x in defect.entries())
        assert gradient[0, 7] == 1 and gradient[0, 10] == 1
    finally:
        ctx.prec = old
