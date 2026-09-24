"""Analytic checks of complete normalization and bordered physical-rate jets."""
from flint import arb,ctx
from bhsm.interface.physical_ball_rate_jet import normalize_augmented,complete_rate


def test_descriptor_is_divided_by_physical_norm_but_excluded_from_it():
    ctx.prec=256
    U={k:[arb(0)]*99 for k in ('value','u','v','uv')}
    U['value'][0:2]=[arb(3),arb(4)];U['value'][98]=arb(7)
    U['u'][0]=arb(1);U['v'][1]=arb(1)
    U['u'][98]=arb(2);U['v'][98]=arb(3);U['uv'][98]=arb(5)
    result=normalize_augmented(U,arb(5))
    for i,target in ((0,8),(1,69),(98,2952)):
        assert (3125*result['uv'][i]-target).contains(0)


def test_complete_graph_matches_quadratic_action_analytic_rate():
    ctx.prec=256
    state=[arb(0)]*98;state[0]=arb(2);state[37]=arb(1)
    diagonal=[arb(1)]*37+[arb(i+2) for i in range(61)]
    class Quadratic:
        def gradient(self,legs):
            if len(legs)>=2:return [arb(0)]*98
            return [a*b for a,b in zip(diagonal,legs[0] if legs else state)]
        def __call__(self,legs):
            assert len(legs)>=3
            return arb(0)
    def solve(rhs):
        # K for psi=e0, lambda=2, H=diag(2,3,...,62).
        return [rhs[-1]]+[rhs[i]/i for i in range(1,61)]+[rhs[0]]
    psi=[arb(1)]+[arb(0)]*60
    direction=[arb(1)]+[arb(0)]*97
    descriptor=dict(value=arb(1),u=arb(0),v=arb(0),uv=arb(0))
    result=complete_rate(Quadratic(),solve,state,psi,direction,direction,descriptor,
                         [arb(1)]*37,[arb(1)]*61,[arb(1)]*98,arb(5).sqrt().lower())
    uv=result['rate']['uv']
    # f=(1,b)/sqrt(1+b^2), b=2; its exact second derivative is
    # (7,-6)/(25 sqrt(5)). Both implicit responses and normalization enter.
    assert (25*arb(5).sqrt()*uv[0]-7).contains(0)
    assert (25*arb(5).sqrt()*uv[37]+6).contains(0)
    assert uv[-1].is_zero()
