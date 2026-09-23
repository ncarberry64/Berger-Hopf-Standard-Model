"""Moving-witness identities and action curvature factors."""
from flint import arb, arb_mat, ctx
from bhsm.interface.shared_eigenpair_transport import (
    interpolated_defect, transport_operands, weighted_matrix_norm,
)


def test_joint_interpolation_defect_identity_with_noncommuting_matrices():
    R0, R1 = arb_mat([[1, 2], [0, 1]]), arb_mat([[2, 0], [3, 1]])
    J0, J1 = arb_mat([[2, 1], [1, 1]]), arb_mat([[1, 3], [0, 2]])
    I = arb_mat([[1, 0], [0, 1]])
    result = interpolated_defect(R0, R1, J0, J1, [arb(1), arb(2)])
    for s in (arb(0), arb(1)/4, arb(1)/2, arb(1)):
        direct = I-(R0*(1-s)+R1*s)*(J0*(1-s)+J1*s)
        assembled = result['D0']*(1-s)+result['D1']*s+result['cross']*(s*(1-s))
        assert direct == assembled
        assert weighted_matrix_norm(direct, [arb(1), arb(2)]) <= result['surrogate_defect_upper']


def test_predictor_residual_has_signed_cross_term_and_normalization_curvature():
    H0, H1 = arb_mat([[2, 1], [1, 4]]), arb_mat([[3, 2], [2, 1]])
    p0, p1 = arb_mat([[1], [0]]), arb_mat([[0], [1]])
    l0, l1 = arb(2), arb(1)
    for s in (arb(1)/4, arb(1)/2, arb(3)/4):
        p, l = p0*(1-s)+p1*s, l0*(1-s)+l1*s
        H = H0*(1-s)+H1*s
        cross = (H1-H0)*(p1-p0)-(p1-p0)*(l1-l0)
        assembled = (H0*p0-p0*l0)*(1-s)+(H1*p1-p1*l1)*s-cross*(s*(1-s))
        assert H*p-p*l == assembled
        normalization = ((p.transpose()*p)[0, 0]-1)/2
        expected = -s*(1-s)*((p1-p0).transpose()*(p1-p0))[0, 0]/2
        assert normalization == expected


def test_quartic_hessian_interpolation_error_has_one_eighth_factor():
    # S=x^4/12: H=x^2. On [0,2], max |H(s)-linear H(s)|=1.
    # sup |D4S[.,.,dx,dx]| / 8 = 2*2^2/8 = 1 exactly.
    old = ctx.prec
    ctx.prec = 256
    try:
        ops = transport_operands([arb(0)], [arb(2)], [arb(1), arb(0)],
            [arb(1), arb(0)], arb_mat([[1, 0], [0, 1]]), arb_mat([[1, 0], [0, 1]]),
            [arb(1), arb(1)], 0, [arb(0)], [[arb(0)]], [(0, 1, 'interval')],
            arb(0), curvature=True, variation=True)
        product = ops['domain'].affine(2)
        for leg in ops['legs']:
            product *= leg[0]
        assert product.support()*ops['bound_factor'] >= 1
        assert ops['bound_factor'] == arb(1)/8
        # The point of evaluation is independent of the output interpolation parameter.
        assert ops['line_parameter'] != ops['path_parameter']
    finally:
        ctx.prec = old


def test_midpoint_offset_is_relative_to_the_center_line_not_zeroed():
    ops = transport_operands([arb(0)], [arb(2)], [arb(1), arb(0)],
        [arb(1), arb(0)], arb_mat([[1, 0], [0, 1]]), arb_mat([[1, 0], [0, 1]]),
        [arb(1), arb(1)], 0, [arb(3)/2], [[arb(1)/8]], [(0, 1, 'interval')],
        arb(1)/2, curvature=False, variation=False)
    # Midpoint center 3/2 differs from the straight-line midpoint 1 by 1/2.
    delta = ops['legs'][2][0]
    assert delta.c == arb(1)/2
    assert delta.a.entries()[0] == arb(1)/8
