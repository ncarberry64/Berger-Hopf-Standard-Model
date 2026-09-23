import pytest
from flint import arb,ctx
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.shared_positive_norm_jet import normalize


def test_normalized_mixed_uses_same_norm_equation():
    old=ctx.prec;ctx.prec=256
    try:
        d=TaylorDomain([(0,1,'interval')],1);a=d.affine
        got=normalize([a(1),a(0)],[a(0),a(1)],[a(0),a(1)],[a(0),a(0)],arb(1))
        assert got['norm_uv'].enclosure().contains(1)
        assert got['physical_mixed'][0].enclosure().contains(-1)
        assert got['physical_mixed'][1].enclosure().contains(0)
    finally:ctx.prec=old


def test_norm_requires_inherited_positive_lower():
    d=TaylorDomain([(0,1,'interval')],1);a=d.affine
    with pytest.raises(ArithmeticError,match='positive inherited'):
        normalize([a(1)],[a(0)],[a(0)],[a(0)],arb(0))
