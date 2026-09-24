import pytest
from flint import arb,arb_mat,ctx
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor
from bhsm.interface.common_input_error_pullback import pullback_constant_errors


def test_common_input_corrections_are_pulled_back_before_the_euclidean_norm():
    original_precision=ctx.prec
    try:
        ctx.prec=256
        domain=TaylorDomain([(0,1,'interval')],1)
        model=InputLinearTaylor(domain,arb_mat([[0,0,1,1]]),arb_mat([[0,0,3,-3]]),arb(1)/4,
                               [(0,2,'euclidean'),(2,4,'box')])
        result=pullback_constant_errors(model,[(2,arb_mat([[1,0],[0,1]]))],2)
        assert result.constant_bound()>=arb(2).sqrt() and result.constant_bound()<2
        assert model.constant_bound()==2
        assert result.a==model.a and result.r==model.r
        for x,y in ((1,0),(0,1),(arb(3)/8,arb(7)/8)):
            for theta in (-1,1):
                v=arb_mat([[x],[y],[x],[y]])
                before=model.at_input(v);after=result.at_input(v)
                assert before.c+before.a[0,0]*theta==after.c+after.a[0,0]*theta
        with pytest.raises(ValueError,match='disjoint'):
            pullback_constant_errors(model,[(2,arb_mat([[1,0],[0,1]])),(2,arb_mat([[1,0],[0,1]]))],2)
    finally:
        ctx.prec=original_precision
