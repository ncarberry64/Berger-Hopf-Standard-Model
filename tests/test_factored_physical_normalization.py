"""Check the exact field identity and cancellation of uncertain common scale."""
import itertools
import numpy as np
import pytest
from flint import arb,ctx
from bhsm.interface.factored_physical_normalization import normalized_value


def test_common_scale_uncertainty_cancels_when_descriptor_is_zero():
    previous=ctx.prec;ctx.prec=256
    try:
        result,proof=normalized_value([2],[1,1],[arb(3)/5,arb(4)/5],[1,2],arb(1,'.2'),0,arb(1)/10,3)
        assert result[1].contains(arb(3)/5) and result[2].contains(arb(4)/5)
        assert max(float(v.rad()) for v in result)<1e-60
        assert proof['border_sign']==1
    finally:ctx.prec=previous


def test_both_border_signs_match_the_original_formula_at_box_corners():
    previous=ctx.prec;ctx.prec=256
    try:
        for sign in (-1,1):
            b=sign*arb(2,'.25');s=arb(1,'.125')
            result,_=normalized_value([1],[1,2],[arb(3)/5,arb(4)/5],[arb(1)/2,-arb(1)/4],b,s,arb(1)/8,arb(1)/16)
            for db,ds in itertools.product((-1,1),repeat=2):
                bp=sign*(arb(2)+db*arb(1)/8);sp=arb(1)+ds*arb(1)/16
                G=np.array([sp,bp*arb(3)/5+sp/2,2*(bp*arb(4)/5-sp/4)],dtype=object)
                norm=sum((v**2 for v in G),arb(0)).sqrt()
                exact=np.concatenate((G/norm,np.array([(bp/8+sp/16)/norm])))
                assert all(a.contains(v) for a,v in zip(result,exact))
    finally:ctx.prec=previous


def test_zero_crossing_border_and_zero_norm_fail_closed():
    with pytest.raises(ArithmeticError,match='border sign'):
        normalized_value([1],[1],[1],[1],arb(0,1),1,1,1)
    with pytest.raises(ArithmeticError,match='positive factored'):
        normalized_value([0],[1],[0],[0],1,0,0,0)
