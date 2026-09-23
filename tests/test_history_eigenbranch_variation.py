import numpy as np
from flint import arb, ctx
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.history_eigenbranch_variation import hermite_history, row_certificate


def test_history_matches_exact_endpoints_and_actual_hs_midpoint():
    previous=ctx.prec;ctx.prec=256
    try:
        d=TaylorDomain([(0,1,'interval')],1);a=d.affine
        left=[a(2,[arb(1)])];right=[a(3,[arb(-1)])]
        f=[a(5)];g=[a(7)]
        for t,target in [(0,left),(1,right),('0.5',[(left[0]+right[0])/2+arb('0.25')*(f[0]-g[0])/8])]:
            got=hermite_history(left,right,f,g,arb('0.25'),a(t))[0]
            assert (got-target[0]).support().is_zero()
    finally:ctx.prec=previous


def test_row_certificate_includes_normalization_curvature_and_large_H_failure():
    previous=ctx.prec;ctx.prec=256
    try:
        R=np.array([[arb(int(i==j)) for j in range(62)] for i in range(62)],dtype=object)
        D=np.full((62,62),arb(0),dtype=object)
        w=[(arb(2)**-20)]*62;Y=[arb('1e-20')]*62
        ref=[arb(1)]+[arb(0)]*60;center=ref+[arb(0)]
        small=[arb('1e-10')]*62
        good=row_certificate(Y,D,R,w,small,small,ref,center)
        assert good['validation_passed']
        assert good['rows'][-1]['eigenpair_and_normalization_border_upper']>0
        large=[arb('0.000002')]+[arb(0)]*61
        bad=row_certificate(Y,D,R,w,small,large,ref,center)
        assert not bad['validation_passed'] and bad['contraction_margin_lower']<0
    finally:ctx.prec=previous
