import math
from flint import arb,ctx
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.shared_complete_rate_jet import trilinear_jet,coupled_rate


def test_all_moving_trilinear_assignments_against_exact_polynomial():
    old=ctx.prec;ctx.prec=256
    try:
        d=TaylorDomain([(0,1,'interval')],1);a=d.affine;x=arb('0.5')
        def evaluate(legs):
            order=len(legs);v=a(x**(5-order)/math.factorial(5-order))
            for leg in legs:v*=leg[0]
            return v
        p=dict(value=[a('1.5')],u=[a(2)],v=[a(3)],uv=[a(0)])
        q=dict(value=[a('0.5')],u=[a(-2)],v=[a(-3)],uv=[a(0)])
        result=trilinear_jet(evaluate,[p,p,q],[a(2)],[a(3)],a('0.140625'))
        assert result['u'].enclosure().contains(arb('0.9375'))
        assert result['v'].enclosure().contains(arb('1.40625'))
        assert result['uv'].enclosure().contains(arb('-1.5'))
    finally:ctx.prec=old


def test_common_border_derivatives_cancel_exactly():
    old=ctx.prec;ctx.prec=256
    try:
        d=TaylorDomain([(0,1,'interval')],1);a=d.affine
        scalar=lambda v,u=0,uv=0:dict(value=a(v),u=a(u),v=a(u),uv=a(uv))
        vector=lambda v:dict(value=[a(v)],u=[a(0)],v=[a(0)],uv=[a(0)])
        # h=s=c=0, psi=1. The normalized field is (0,1,C), independent
        # of arbitrarily large b first/mixed derivatives.
        got=coupled_rate(vector(1),vector(0),scalar(2,10**8,10**12),scalar(0),vector(0),
                         [arb(1)],scalar(3),scalar(4),arb(1))
        assert all(v.support().is_zero() for v in got['mixed'])
        assert got['common_border_canceled']
    finally:ctx.prec=old
