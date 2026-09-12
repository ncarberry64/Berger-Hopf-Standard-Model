"""Exact linear families exercise the weighted Neumann response estimate."""
import numpy as np
import pytest
from flint import arb,arb_mat,ctx
from bhsm.interface.weighted_response_enclosure import enclose_response


def test_normalized_eigenpair_jacobian_response_over_parameter_interval():
    previous=ctx.prec;ctx.prec=256
    try:
        # H=diag(1+x,3), p=(1,0), lambda=1+x, |x|<=1/4.
        R=arb_mat([[0,0,1],[0,arb(1)/2,0],[-1,0,0]])
        J=arb_mat([[0,0,-1],[0,arb(2,'0.25'),0],[1,0,0]])
        rhs=arb_mat([[2],[4],[3]])
        center=arb_mat([[3],[2],[-2]])
        error=R*(rhs-J*center)
        box,report=enclose_response(center.entries(),error.entries(),[2,4,1],[0,arb(1)/2,0])
        for x in (arb(-1)/4,arb(0),arb(1)/4):
            actual=[arb(3),4/(2-x),arb(-2)]
            assert all(a.contains(b) for a,b in zip(box,actual))
        assert not report['action_domain_bound'] and not report['uniform_physical_rate_enclosed']
    finally:ctx.prec=previous


def test_contraction_boundary_and_uncertain_center_fail_closed():
    with pytest.raises(ArithmeticError,match='strict'):
        enclose_response([0,0],[1,1],[1,1],[0,1])
    with pytest.raises(ValueError,match='exact center'):
        enclose_response([arb(0,'.1'),0],[1,1],[1,1],[0,0])
