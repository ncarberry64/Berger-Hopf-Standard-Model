"""Check cancellation and a smooth normalized/orthogonal coupled family."""
import numpy as np
import pytest
from flint import arb,ctx
from bhsm.interface.coupled_physical_normalization import normalized_value
from bhsm.interface.coupled_physical_normalization_derivative import normalized_derivative


def test_common_border_scale_variation_cancels_exactly():
    result,_=normalized_derivative([arb(1)],[arb(1)],[arb(1)],[arb(0)],arb(2),arb(1),arb(3),arb(4),
        [[arb(0)]],[[arb(0)]],[[arb(0)]],[arb(1)],[arb(1)/2],[arb(0)],[arb(0)],
        coupled_identities_and_variations=True)
    assert all(v.is_zero() for v in result.flat)


def test_derivative_matches_smooth_coupled_family_and_unit_norm():
    previous=ctx.prec;ctx.prec=256
    try:
        theta=arb(1)/4
        def operands(x):
            p=np.array([x.cos(),x.sin()]);h=np.array([-x.sin(),x.cos()])*2
            return [arb(1)+x],[arb(1),arb(2)],p,h,arb(2)+x,arb(3)/10+x/5,arb(3)+x,2*x
        args=operands(theta)
        dp=np.array([[-theta.sin()],[theta.cos()]])
        dh=np.array([[-2*theta.cos()],[-2*theta.sin()]])
        result,_=normalized_derivative(*args,[[arb(1)]],dp,dh,[arb(1)],[arb(1)/5],[arb(1)],[arb(2)],
            coupled_identities_and_variations=True)
        def value(x):return normalized_value(*operands(x),normalized_eigenpair=True,bordered_orthogonality=True)[0]
        epsilon=arb(2)**-30
        finite_difference=(value(theta+epsilon)-value(theta-epsilon))/(2*epsilon)
        assert all(abs(a-b)<arb('1e-15') for a,b in zip(result[:,0],finite_difference))
        unit_tangent=sum((a*b for a,b in zip(value(theta)[:-1],result[:-1,0])),arb(0))
        assert unit_tangent.contains(0)
    finally:ctx.prec=previous


def test_component_boxes_do_not_establish_the_required_identities():
    with pytest.raises(ValueError,match='verified coupled identities'):
        normalized_derivative([1],[1],[1],[0],2,1,3,4,[[0]],[[0]],[[0]],[1],[0],[0],[0])
