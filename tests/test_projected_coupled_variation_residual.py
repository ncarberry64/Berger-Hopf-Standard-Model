"""Check projection algebra and retention of an uncertain common coefficient."""
import numpy as np
from flint import arb,ctx
from bhsm.interface.projected_coupled_variation_residual import line_residual
from bhsm.interface.centered_coupled_variation_residual import line_residual as original


def test_uncertain_rank_one_action_cancels_before_interval_evaluation():
    previous=ctx.prec;ctx.prec=256
    try:
        coefficient=arb(2,arb(1)/4)
        def action(state,legs,maps):
            result=coefficient
            for leg in legs:result=result*leg[1]
            return result
        R=np.array([[arb(2),arb(1),arb(0)],[arb(1),arb(3),arb(1)],[arb(1),arb(-1),arb(2)]])
        args=(action,[arb(0)]*3,[arb(1),arb(0)],arb(1),R,
              np.full((3,1),arb(0)),[[arb(0)],[arb(1)],[arb(0)]],None)
        projected,_=line_residual(*args);separate,_=original(*args)
        assert all(v.is_zero() for v in projected.flat)
        assert any(v.rad()>0 for v in separate.flat)
    finally:ctx.prec=previous


def test_nonzero_center_and_general_vector_match_original_exact_algebra():
    previous=ctx.prec;ctx.prec=256
    try:
        a=np.array([arb(2),arb(-1),arb(3)])
        def action(state,legs,maps):
            result=arb(1)
            for leg in legs:result=result*np.tensordot(a,leg,axes=(0,0))
            return result
        R=np.array([[arb(int(i==j))+arb((i+1)*(j+1))/16 for j in range(3)] for i in range(3)])
        centers=np.array([[arb(i+1)/16,arb(2*i+1)/8] for i in range(3)])
        directions=np.array([[arb(i+1),arb(2-i)] for i in range(3)])
        args=(action,[arb(1)/8]*3,[arb(3)/4,arb(1)/2],arb(2),R,centers,directions,None)
        actual,slopes=line_residual(*args);expected,old_slopes=original(*args)
        assert all(abs(a-b)<arb('1e-60') for a,b in zip(actual.flat,expected.flat))
        assert all(abs(a-b)<arb('1e-60') for a,b in zip(slopes,old_slopes))
    finally:ctx.prec=previous
