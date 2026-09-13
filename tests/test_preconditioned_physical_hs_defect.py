"""Compare reassociated enclosures with the original physical HS operator."""
from itertools import product
import numpy as np
import pytest
from flint import arb,ctx
from bhsm.interface.direct_physical_hs_defect import local_defect_blocks as original
from bhsm.interface.preconditioned_physical_hs_defect import local_defect_blocks


def test_reassociated_intervals_contain_original_point_operators():
    previous=ctx.prec;ctx.prec=256
    try:
        a=np.array([[arb(1),arb(2),arb(0)],[arb(-1),arb(3),arb(1)],[arb(2),arb(0),arb(1)]])
        m=a.T.copy();b=a.copy()
        a[0,1]=arb(2,arb(1)/32);m[1,2]=arb(1,arb(1)/64);b[2,0]=arb(2,arb(1)/128)
        e0=[[1,0],[1,1],[0,1]];e1=[[1,1],[0,1],[1,0]];t=[[1,2,1],[2,1,-1]]
        l=[[1,0,1],[0,2,0],[1,0,3]];r=[[2,1],[1,2]];h=arb(1)/8
        args=(h,e0,e1,t,l,r)
        boxes={method:local_defect_blocks(a,m,b,*args,association=method,precision=256)
               for method in ('solve_first','preconditioned_chain','combined_endpoint_coefficient')}
        for signs in product((-1,1),repeat=3):
            aa=a.copy();mm=m.copy();bb=b.copy()
            aa[0,1]=arb(2)+signs[0]*arb(1)/32
            mm[1,2]=arb(1)+signs[1]*arb(1)/64
            bb[2,0]=arb(2)+signs[2]*arb(1)/128
            exact=original(aa,mm,bb,*args,precision=512)
            for blocks in boxes.values():
                for key in ('C','DL','DR'):
                    assert all(x.contains(y) for x,y in zip(blocks[key].entries(),exact[key].entries()))
        fixed=local_defect_blocks(a,m,b,*args,initial_endpoint_fixed=True)
        assert all(x.is_zero() for x in fixed['DL'].entries())
    finally:ctx.prec=previous


def test_unknown_product_association_is_rejected():
    with pytest.raises(ValueError,match='association'):
        local_defect_blocks(None,None,None,None,None,None,None,None,None,association='approximate')
