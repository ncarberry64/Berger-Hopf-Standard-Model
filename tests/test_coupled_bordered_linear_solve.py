"""The coupled inverse bound must contain entire RHS families, not just centers."""
import numpy as np
import pytest
from flint import arb,arb_mat,ctx
from bhsm.interface.coupled_bordered_linear_solve import enclose_columns


def test_weighted_family_contains_solutions_for_two_distinct_rhs_columns():
    previous=ctx.prec;ctx.prec=256
    try:
        R=np.array([[arb(1),arb(0)],[arb(0),arb(1)]])
        r=np.array([arb(1),arb(2)])
        # J=[[1,t],[t,1]], |t|<=1/8, hence weighted row sums 1/4 and 1/8.
        V=np.array([arb(1)/4,arb(1)/8])
        b=np.array([[arb(2,arb(1)/16),arb(-3)],[arb(1),arb(4,arb(1)/32)]])
        box,residual,proofs=enclose_columns(R,b,r,V)
        assert box.shape==b.shape and len(proofs)==2
        for t in (arb(-1)/8,arb(0),arb(1)/8):
            K=arb_mat([[arb(1),-t],[t,arb(-1)]])
            for column in range(2):
                exact=K.inv()*arb_mat(2,1,[v.mid() for v in b[:,column]])
                assert all(box[i,column].contains(exact[i,0]) for i in range(2))
        assert residual[0,0].contains(b[0,0])
    finally:ctx.prec=previous


def test_noncontracting_family_cannot_return_an_inverse_bound():
    R=np.array([[arb(1)]]);b=np.array([[arb(2)]])
    with pytest.raises(ArithmeticError,match='strict weighted contraction'):
        enclose_columns(R,b,[arb(1)],[arb(1)])


def test_uncertain_preconditioner_is_rejected():
    with pytest.raises(ValueError,match='exact preconditioner'):
        enclose_columns([[arb(1,arb(1)/8)]],[[arb(1)]],[arb(1)],[arb(0)])
