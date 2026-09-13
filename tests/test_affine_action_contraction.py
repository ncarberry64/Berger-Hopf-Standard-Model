"""Independent polynomial families test state correlation and batched coverage."""
import itertools
import math
import numpy as np
from flint import arb,ctx
from bhsm.interface.affine_action_contraction import contract_affine


def polynomial(a,x,legs):
    k=len(legs);result=(a@x)**(5-k)/math.factorial(5-k)
    for leg in legs:result=result*np.tensordot(a,leg,axes=(0,0))
    return result


def test_common_state_parameter_cancels_where_raw_coordinate_box_does_not():
    previous=ctx.prec;ctx.prec=256
    try:
        a=np.array([arb(1),arb(-1)]);base=np.array([arb(0),arb(0)])
        radius=arb(1)/8;full=np.array([arb(0,radius),arb(0,radius)])
        direction=np.array([arb(1),arb(1)]);legs=[np.array([arb(1),arb(0)])]*4;calls=[]
        def at_base(v):calls.append(('base',len(v)));return polynomial(a,base,v)
        def at_full(v):calls.append(('full',len(v)));return polynomial(a,full,v)
        result=contract_affine(at_base,at_full,legs,direction,radius)
        assert result.item().is_zero()
        assert polynomial(a,full,legs).rad()>0
        assert calls==[('base',4),('full',5)]
    finally:ctx.prec=previous


def test_nonconstant_batched_contraction_contains_correlated_family_samples():
    previous=ctx.prec;ctx.prec=256
    try:
        a=np.array([arb(1),arb(2)]);r=arb(1)/32;noise=arb(1)/64
        base=np.array([arb(1,noise),arb(-1,noise)]);direction=np.array([arb(1),arb(2)])
        full=base+direction*arb(0,r)
        legs=[np.array([[[arb(1)],[arb(2)]],[[arb(2)],[arb(-1)]]]),
              np.array([[[arb(1),arb(2),arb(3)]],[[arb(2),arb(1),arb(-1)]]])]
        result=contract_affine(lambda v:polynomial(a,base,v),lambda v:polynomial(a,full,v),legs,direction,r)
        assert result.shape==(2,3)
        for signs in itertools.product([-1,1],repeat=2):
            center=np.array([arb(1)+signs[0]*noise,arb(-1)+signs[1]*noise])
            for t in [-r,arb(0),r]:
                exact=polynomial(a,center+direction*t,legs)
                assert all(v.contains(e) for v,e in zip(result.flat,exact.flat))
    finally:ctx.prec=previous
