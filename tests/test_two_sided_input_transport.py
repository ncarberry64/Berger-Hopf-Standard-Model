from flint import arb, arb_mat, ctx
import pytest
from bhsm.interface.two_sided_input_transport import transport_coefficients
from bhsm.interface.directed_physical_hs_column import chain_direction, local_column


@pytest.mark.parametrize('side', ['left', 'right'])
@pytest.mark.parametrize('longitudinal', [False, True])
def test_regrouped_full_block_matches_original_independent_column_chain(side, longitudinal):
    old = ctx.prec
    ctx.prec = 256
    try:
        E = arb_mat([[1, 2], [3, 1], [-1, 2]])
        A = arb_mat([[3, -1], [2, 4], [0, 3]])
        M = arb_mat([[1, 2, 0], [0, 1, -2], [-1, 0, 3]])
        A0 = arb_mat([[2, 1], [-3, 1], [1, -2]])
        U = arb_mat([[1, -1], [2, -2], [3, -3]])
        test = arb_mat([[1, 2, -1], [2, -3, 1]])
        right = arb_mat([[2, 0], [0, 4]])
        left = arb_mat([[2, 1, 0], [0, 3, -1], [1, 0, 1]])
        Q = arb_mat([[1, 1]]) if longitudinal else arb_mat([[1, -1], [-1, 1]])/2
        h = arb(3)/8
        QP = Q*right.solve(test)
        fixed, coefficient = transport_coefficients(QP, Q, E, M, h, A0, U,
            side=side, frozen_left=left if side == 'left' else None)
        grouped = fixed+QP*M*U*(2*h/3)+coefficient*(A-A0)
        for j in range(2):
            e = arb_mat(3, 1, [E[i, j] for i in range(3)])
            a = arb_mat(3, 1, [A[i, j] for i in range(3)])
            b = M*chain_direction(e, a, h, side)
            original = Q*local_column(e, a, b, h, test, left, right, j, side)['combined']
            assert original == arb_mat(Q.nrows(), 1, [grouped[i, j] for i in range(Q.nrows())])
    finally:
        ctx.prec = old


def test_left_block_cannot_drop_frozen_left_jacobian():
    unit = arb_mat([[1]])
    with pytest.raises(ValueError, match='frozen left'):
        transport_coefficients(unit, unit, unit, unit, 1, unit, unit, side='left')
