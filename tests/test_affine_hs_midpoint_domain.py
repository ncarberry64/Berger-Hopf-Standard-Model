"""Check actual midpoint inclusion without dropping affine or rate uncertainty."""
import itertools
import numpy as np
import pytest
from flint import arb,ctx
from bhsm.interface.affine_hs_midpoint_domain import midpoint_domain,group_row_bounds
from bhsm.interface.physical_hs_value import physical_midpoint
from bhsm.interface.direct_physical_neighborhood import unweight_box


def test_midpoint_hull_contains_joint_endpoint_tubes_and_uniform_field_remainders():
    previous=ctx.prec;ctx.prec=256
    try:
        a=np.array([arb(1),arb(2),arb(3)]);b=np.array([arb(2),arb(-1),arb(4)])
        EL=np.array([[1,-2],[3,1],[2,0]]);ER=np.array([[-1,2],[1,2],[0,3]])
        eL=[2,-1];eR=[-1,3];w=[2,4];h=arb(1)/8
        fL=np.array([arb(1,'.25'),arb(-2,'.125'),arb(3,'.5')])
        fR=np.array([arb(-1,'.125'),arb(2,'.25'),arb(1,'.5')])
        domain=midpoint_domain(a,b,EL,ER,eL,eR,fL,fR,h,w,[.25,.5],[.125,.25])
        for sL,sR,fSign in itertools.product((-1,1),repeat=3):
            tL=np.array([arb(3)/40,arb(1)/10])*sL
            tR=np.array([arb(0),arb(1)/4])*sR
            left=a+EL@(np.array(eL)*arb(sL)/4+tL)
            right=b+ER@(np.array(eR)*arb(sR)/2+tR)
            ratesL=np.array([v.mid()+fSign*v.rad()/2 for v in fL])
            ratesR=np.array([v.mid()-fSign*v.rad()/2 for v in fR])
            actual=unweight_box(physical_midpoint(left,right,ratesL,ratesR,h),w)
            assert all(v.contains(z) for v,z in zip(domain['raw_segment_hull'],actual))
        assert domain['raw_directions'].shape==(3,9)
        assert domain['raw_directions'][2,0]==2  # Descriptor stays unweighted; axis is not normalized.
    finally:ctx.prec=previous


def test_group_norms_do_not_cancel_independent_longitudinal_inputs():
    groups=[dict(start=0,stop=1,norm='interval',radius=1),
            dict(start=1,stop=2,norm='interval',radius=1),
            dict(start=2,stop=4,norm='euclidean',radius=2)]
    assert group_row_bounds([[1,-1,3,4]],groups)[0]>=12
    with pytest.raises(ValueError,match='all directions'):
        group_row_bounds([[1,-1,3,4,5]],groups)
    with pytest.raises(ValueError,match='disjoint'):
        group_row_bounds([[1,-1,3,4]],[groups[0],groups[0]])
