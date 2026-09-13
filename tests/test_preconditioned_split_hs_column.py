from itertools import product
import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface.preconditioned_split_hs_column import local_columns


@pytest.mark.parametrize('side,sign', [('left', 1), ('right', -1)])
def test_both_associations_cover_actual_chain_with_shifted_center(side, sign):
    ctx.prec = 256
    e = arb_mat([[2], [-3]])
    a = arb_mat([[arb(4, 1)], [arb(-2, 2)]])
    w0 = arb_mat([[7], [-5]])  # Exercises the explicit center remainder.
    m = arb_mat([[arb(2, 1), -4], [3, arb(-1, 1)]])
    h = arb(1)/8
    t, l, r = arb_mat([[2, -1], [3, 4]]), arb_mat([[1, 2], [-3, 1]]), arb_mat([[3, 1], [-1, 2]])
    delta = e/2+a*(sign*h/8)-w0
    candidates = local_columns(e, a, w0, m*w0, delta, m, h, t, l, r, 1, side)
    p = r.solve(t)
    for x, y, u, v in product((3, 5), (-4, 0), (1, 3), (-2, 0)):
        ae = arb_mat([[x], [y]])
        me = arb_mat([[u, -4], [3, v]])
        b = me*(e/2+ae*(sign*h/8))
        fixed = p*(l*e+e) if side == 'left' else arb_mat([[0], [1]])-p*e
        exact = fixed+(p*ae)*(h/6)+(p*b)*(2*h/3)
        for candidate in candidates.values():
            assert all(a.contains(b) for a, b in zip(candidate.entries(), exact.entries()))


def test_rejects_uncertain_center():
    with pytest.raises(ValueError):
        local_columns([[1]], [[2]], [[arb(1, 1)]], [[3]], [[4]], [[5]], 1,
                      [[1]], [[1]], [[1]], 0, 'left')
