from flint import arb,ctx
from bhsm.interface.shared_expression_graph import ExpressionDomain
from bhsm.interface.shared_mixed_rate_graph import normalized_graph
from bhsm.interface.physical_ball_rate_jet import product,normalize_augmented


def test_common_border_recurrence_matches_complete_quotient_with_moving_frame():
    old=ctx.prec;ctx.prec=256
    try:
        keys=('value','u','v','uv')
        # Exact two-plane rotation jets, embedded in the 61-dimensional frame.
        # psi.psi=1 and psi.h=0 hold through both mixed derivatives.
        psi={k:[arb(x) for x in row]+[arb(0)]*59 for k,row in zip(keys,((1,0),(0,2),(0,3),(-6,0)))}
        h={k:[arb(x) for x in row]+[arb(0)]*59 for k,row in zip(keys,((0,4),(-8,0),(-12,0),(0,-24)))}
        scalar=lambda row:dict(zip(keys,map(arb,row)))
        b=scalar((5,2,-1,3));s=scalar((2,-1,4,2))
        C=scalar((3,1,-2,4));J=scalar((-2,3,1,-1))
        c={k:[arb(x)]+[arb(0)]*36 for k,x in zip(keys,(2,3,-1,0))}
        rw=[arb(2),arb(3)]+[arb(1)]*59
        U={k:[] for k in keys}
        scalar_row=lambda vec,i:{k:vec[k][i] for k in keys}
        for i in range(37):
            z=product(s,scalar_row(c,i))
            for k in keys:U[k].append(z[k])
        for i in range(61):
            bp,sh=product(b,scalar_row(psi,i)),product(s,scalar_row(h,i))
            for k in keys:U[k].append(rw[i]*(bp[k]+sh[k]))
        bc,sj=product(b,C),product(s,J)
        for k in keys:U[k].append(bc[k]+sj[k])
        lower=sum((x*x for x in U['value'][:98]),arb(0)).sqrt().lower()
        reference=normalize_augmented(U,lower)
        d=ExpressionDomain([(0,1,'interval')],['unused'])
        def wrap(z):return {k:[d.affine(x) for x in v] if isinstance(v,list) else d.affine(v) for k,v in z.items()}
        result=normalized_graph(wrap(psi),wrap(h),wrap(b),wrap(s),wrap(c),rw,wrap(C),wrap(J),arb(5),{})
        for key in keys:
            for x,y in zip(result[key],reference[key]):
                assert (x.enclosure()-y).contains(0)
                assert x.enclosure().rad()<arb('1e-60')
    finally:ctx.prec=old
