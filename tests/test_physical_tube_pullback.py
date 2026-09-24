"""Exact incidence and moving numerical inverse checks; no physical reruns."""
from flint import arb,ctx
import pytest
import numpy as np
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.shared_hs_physical_pullback import (
    dense_incidence,composed_rate_second,signed_hs_second)
from bhsm.interface.shared_moving_chart_solve import solve
from bhsm.interface.hermite_tube_directions import displacement_directions


def test_dense_jet_midpoint_includes_second_incidence_and_descriptor():
    ctx.prec=256
    zero=[arb(0)]*99
    def jet(value,u,v,uv):
        return {k:zero[:98]+[arb(x)] for k,x in zip(('value','u','v','uv'),(value,u,v,uv))}
    left,right=jet(2,1,1,0),jet(3,2,3,0)
    f,g=jet(4,4,4,2),jet(9,12,18,12)
    h=arb(1)/4
    m=dense_incidence(arb(1)/2,h,left,right,f,g)
    assert m['value'][-1] == arb(5)/2-5*h/8
    assert m['uv'][-1] == -10*h/8
    midpoint_second=composed_rate_second([arb(7)]*99,[arb(11)]*99)
    full=signed_hs_second(h,[arb(2)]*99,midpoint_second,[arb(12)]*99)
    assert (12*full[-1]+43).contains(0)
    omitted=signed_hs_second(h,[arb(2)]*99,[arb(7)]*99,[arb(12)]*99)
    assert full[-1] != omitted[-1]


@pytest.mark.parametrize('tau',(0,1))
def test_dense_jets_return_original_endpoint_at_both_ends(tau):
    a={k:[arb(i)] for i,k in enumerate(('value','u','v','uv'),1)}
    b={k:[arb(i+5)] for i,k in enumerate(('value','u','v','uv'),1)}
    got=dense_incidence(arb(tau),arb(2),a,b,b,a)
    assert got == (a if tau==0 else b)


def test_moving_preconditioner_is_residual_corrected_not_differentiated():
    ctx.prec=256
    d=TaylorDomain([(0,1,'interval')],1)
    rhs=[d.affine(1,[arb(1)])]
    R=[[d.affine(arb(1)/2,[arb(1)/10])]]
    answer,proof=solve(rhs,lambda x:[2*x[0]],R,[arb(1)],arb(1)/5)
    # True solution of 2x=1+theta. A changing numerical R does not change it.
    for theta in (-1,0,1):
        v=answer[0]
        enclosed=v.c+v.a[0,0]*theta+arb(0,v.r)
        assert enclosed.contains(arb(1+theta)/2)
    assert proof['weighted_correction_upper']>0


def test_moving_solve_rejects_unproved_inverse_and_foreign_parameters():
    d=TaylorDomain([(0,1,'interval')],1)
    other=TaylorDomain([(0,1,'interval')],1)
    for R,q in [([[d.affine(1)]],arb(1)),([[other.affine(1)]],arb(0))]:
        with pytest.raises(ValueError):solve([d.affine(1)],lambda x:x,R,[arb(1)],q)


def test_incomplete_incidence_output_rejected():
    with pytest.raises(ValueError):composed_rate_second([arb(1)],[arb(1),arb(2)])
    with pytest.raises(ValueError):signed_hs_second(arb(1),[arb(1)],[],[arb(1)])


def test_cubic_bend_directions_reconstruct_exact_polynomial():
    ctx.prec=256
    def point(x):
        return dict(x=np.array([arb(x)]+[arb(0)]*97,dtype=object),
                    scaled=[[arb(0)]*75 for _ in range(98)])
    left,right,mid=point(0),point(10),point(arb(9)/2)
    rates=[[arb(x)]+[arb(0)]*97 for x in (2,4)]
    directions=displacement_directions(left,right,rates,arb(2),(left,mid,0),arb(0),arb(1)/2)
    for u in (-1,0,1):
        tau=(arb(1)+u)/4
        got=directions[0,0]+u*directions[0,1]+(2*u*u-1)*directions[0,2]+u**3*directions[0,3]
        expected=-5*tau+14*tau**2-8*tau**3
        assert (got-expected).is_zero()
    assert all(v.is_zero() for v in directions[:,4:].flat)


def test_cubic_tube_rejects_cell_outside_local_half():
    point=dict(x=[arb(0)]*98,scaled=[[arb(0)]*75 for _ in range(98)])
    with pytest.raises(ValueError):
        displacement_directions(point,point,[[arb(0)]*98]*2,arb(1),
                                (point,point,0),arb(0),arb(1))
