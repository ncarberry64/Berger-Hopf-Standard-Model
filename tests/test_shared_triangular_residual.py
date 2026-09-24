import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface.shared_parameter_residual import PolynomialMatrix as Poly
from bhsm.interface.shared_triangular_residual import transport


def scalar(terms):
    return Poly({key: arb_mat([[arb(v)]]) for key, v in terms.items()}, 1, 1, 1)


def test_large_feedforward_coupling_preserves_exact_shared_cancellation():
    # x=t, y=2x-2t=0: raw stack infinity norm 2 must not preclude this proof.
    bounds, proof = transport([scalar({(0,): 1}), scalar({(0,): -2})],
                             {(1, 0): scalar({(): 2})}, arb_mat([[0, 1]]), [[arb(1)]]*2)
    assert bounds[0].is_zero()
    assert proof['blocks'][1]['upstream_operator_bounds'][0] == 2


def test_diagonal_tail_and_upstream_amplification_are_both_retained():
    old = ctx.prec
    ctx.prec = 128
    try:
        # x=1+t*x/4, y=3x. At t=1, y=4, so dropping either tail is unsound.
        bounds, proof = transport([scalar({(): 1}), scalar({})],
            {(0, 0): scalar({(0,): '0.25'}), (1, 0): scalar({(): 3})},
            arb_mat([[0, 1]]), [[arb(1)]]*2, steps=2)
        assert bounds[0] >= 4 and bounds[0] < arb('4.000001')
        assert proof['projected_tail'][0] > 0
    finally:
        ctx.prec = old


def test_cycle_and_noncontracting_diagonal_are_rejected():
    with pytest.raises(ValueError, match='acyclic'):
        transport([scalar({}), scalar({})], {(0, 1): scalar({(): 1})},
                  arb_mat([[1, 1]]), [[arb(1)]]*2)
    with pytest.raises(ArithmeticError, match='diagonal'):
        transport([scalar({(): 1})], {(0, 0): scalar({(): 1})}, arb_mat([[1]]), [[arb(1)]])
