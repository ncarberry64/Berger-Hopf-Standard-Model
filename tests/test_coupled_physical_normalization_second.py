"""Compare with Taylor coefficients of the original, uncanceled physical field."""
import numpy as np
import pytest
from flint import arb,arb_series,ctx
from bhsm.interface.coupled_physical_normalization_second import normalized_mixed


@pytest.mark.parametrize('sign',[-1,1])
def test_original_field_series_matches_coupled_second_derivative(sign):
    previous=ctx.prec;cap=ctx.cap;ctx.prec=512;ctx.cap=3
    try:
        x=arb(1)/8;y=-arb(1)/16;theta=x+y
        p=np.array([theta.cos(),theta.sin()]);normal=np.array([-p[1],p[0]])
        amplitude=1+x*y;h=amplitude*normal;c=np.array([1+x,2+y]);w=np.array([arb(2),arb(3)])
        b=sign*(2+x+y+x*y);s=x+2*y+x*y;cp=1+x*x+y*y+x*y;rem=1+3*x-2*y+x*y
        def jet(dc,dp,dh,db,ds,dcp,dr):
            return dict(configuration=np.array(dc,dtype=object)[:,None],psi=np.array(dp,dtype=object)[:,None],hard=np.array(dh,dtype=object)[:,None],
                border=np.array([db]),descriptor=np.array([ds]),cpsi=np.array([dcp]),remainder=np.array([dr]))
        u=jet([arb(1),arb(0)],normal,y*normal-amplitude*p,sign*(1+y),1+y,2*x+y,3+y)
        v=jet([arb(0),arb(1)],normal,x*normal-amplitude*p,sign*(1+x),2+x,2*y+x,-2+x)
        uv=jet([arb(0),arb(0)],-p,(1-amplitude)*normal-(x+y)*p,arb(sign),arb(1),arb(1),arb(1))
        actual,_=normalized_mixed(c,w,p,h,b,s,cp,rem,u,v,uv,coupled_identities_and_variations=True)
        def coefficient(dx,dy):
            xx=arb_series([x,dx],3);yy=arb_series([y,dy],3);angle=xx+yy
            pp=[angle.cos(),angle.sin()];qq=1+xx*yy;hh=[-qq*pp[1],qq*pp[0]]
            cc=[1+xx,2+yy];bb=sign*(2+xx+yy+xx*yy);ss=xx+2*yy+xx*yy
            ccp=1+xx*xx+yy*yy+xx*yy;rr=1+3*xx-2*yy+xx*yy
            G=[ss*ci for ci in cc]+[w[i]*(bb*pp[i]+ss*hh[i]) for i in range(2)]
            norm=sum((z*z for z in G),arb_series([0],3)).sqrt()
            return [(z/norm)[2] for z in G+[(ccp*bb+ss*rr)]]
        both=coefficient(1,1);one=coefficient(1,0);other=coefficient(0,1)
        expected=[a-b-c for a,b,c in zip(both,one,other)]
        assert all(abs(a-b)<arb('1e-100') for a,b in zip(actual[:,0],expected))
    finally:ctx.prec=previous;ctx.cap=cap


def test_coupled_second_order_identities_are_required():
    with pytest.raises(ValueError,match='identities through mixed second order'):
        normalized_mixed(*([None]*11))
