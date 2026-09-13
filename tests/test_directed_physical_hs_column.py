import numpy as np
import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface.directed_physical_hs_column import chain_direction, local_column
from bhsm.interface.direct_physical_hs_defect import local_defect_blocks


def test_noncommuting_chain_and_both_defect_signs():
    ctx.prec = 256
    a, m, b = [arb_mat(v) for v in ([[2, 3], [-1, 4]], [[3, -2], [5, 7]], [[1, 6], [-3, 2]])]
    el, er = arb_mat([[1, 2], [3, -1]]), arb_mat([[2, -1], [1, 4]])
    t, l, r = arb_mat([[2, 3], [1, -2]]), arb_mat([[4, -3], [2, 5]]), arb_mat([[3, 1], [2, 4]])
    h = arb(1)/8
    expected = local_defect_blocks(a, m, b, h, el, er, t, l, r, precision=256)
    for side, e, df, name in (('left', el, a, 'DL'), ('right', er, b, 'DR')):
        for j in range(2):
            v = arb_mat(2, 1, [e[i, j] for i in range(2)])
            av = df*v
            w = chain_direction(v, av, h, side)
            for result in local_column(v, av, m*w, h, t, l, r, j, side).values():
                assert all(result[i, 0].overlaps(expected[name][i, j]) for i in range(2))


def test_interval_chain_contains_endpoints_and_keeps_uncertainty():
    trial = arb_mat([[2], [-4]])
    action = arb_mat([[arb(3, 1)], [arb(-2, 2)]])
    for side, sign in (('left', 1), ('right', -1)):
        result = chain_direction(trial, action, arb(1)/2, side)
        for i, (mid, radius) in enumerate(((3, 1), (-2, 2))):
            for value in (mid-radius, mid+radius):
                assert result[i, 0].contains(trial[i, 0]/2+sign*arb(value)/16)
            assert not result[i, 0].rad().is_zero()


@pytest.mark.parametrize('step', [0, -1, arb(1, '0.01')])
def test_rejects_nonpositive_or_uncertain_step(step):
    with pytest.raises(ValueError):
        chain_direction([[1]], [[2]], step, 'left')


def test_rejects_wrong_direction_shape():
    with pytest.raises(ValueError):
        chain_direction(np.eye(2), np.eye(2), 1, 'left')
