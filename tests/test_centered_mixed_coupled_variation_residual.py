"""Compare signed contractions with complete, independently assembled systems."""
import numpy as np
import pytest
from flint import arb,ctx
from bhsm.interface import centered_mixed_coupled_variation_residual as signed


def operands():
    q,n=2,3;size=q+n
    def values(shape,offset):
        return np.array([arb(i+offset)/16 for i in range(np.prod(shape))],dtype=object).reshape(shape)
    x=values((size,),1);p=values((n,),2);h=values((n,),3);lam=arb(2);b=arb(3)/4
    R=values((n+1,n+1),1)+np.eye(n+1,dtype=int);z=values((n+1,2),2)
    u=dict(direction=values((size,1),1),psi=values((n,1),2),hard=values((n,1),3),
        border=values((1,),4),eigenvalue=values((1,),5))
    v=dict(direction=values((size,2),2),psi=values((n,2),3),hard=values((n,2),4),
        border=values((2,),5),eigenvalue=values((2,),6))
    px=values((n,2),7)
    qw=np.array([arb(2),arb(3)]);rw=np.array([arb(4),arb(5),arb(6)])
    w=np.concatenate((qw,rw))
    return x,p,h,lam,b,R,z,u,v,px,qw,rw,w


def action_family(coefficient):
    modes=[np.array([arb(1),arb(-2),arb(3),arb(-1),arb(2)]),
           np.array([arb(-2),arb(1),arb(1),arb(2),arb(-3)])]
    def action(x,legs,maps):
        result=arb(0)
        for a in modes:
            term=coefficient*(a@x).exp()
            for leg in legs:term=term*np.tensordot(a,leg,axes=(0,0))
            result=result+term
        return result
    def matrix(x,directions=()):
        result=np.full((5,5),arb(0),dtype=object)
        for a in modes:
            term=coefficient*(a@x).exp()
            for d in directions:term*=a@d
            result+=np.outer(a,a)*term
        return result
    def gradient_mixed(x,u,v):
        return sum((a*(coefficient*(a@x).exp()*(a@u)*(a@v)) for a in modes),
            np.full(5,arb(0),dtype=object))
    return action,matrix,gradient_mixed


def explicit_systems(coefficient,args):
    x,p,h,lam,b,R,z,u,v,px,qw,rw,w=args;q=2;n=3
    _,matrix,gradient_mixed=action_family(coefficient)
    H=matrix(x);I=np.eye(n,dtype=int)
    K=np.full((n+1,n+1),arb(0),dtype=object)
    K[:n,:n]=H[q:,q:]-lam*I;K[:n,n]=p;K[n,:n]=p
    left=[];right=[];slopes=[]
    du=u['direction'][:,0];pu=u['psi'][:,0];hu=u['hard'][:,0]
    Hu=matrix(x,[du]);config=qw*x[q:q+q];config_u=qw*du[q:q+q]
    for k in range(2):
        dv=v['direction'][:,k];pv=v['psi'][:,k];hv=v['hard'][:,k]
        Hv=matrix(x,[dv]);Hx=matrix(x,[du,dv]);guv=gradient_mixed(x,du,dv)
        lx=p@Hx[q:,q:]@p+pv@Hu[q:,q:]@p+pu@Hv[q:,q:]@p
        slopes.append(lx)
        rhs=np.empty(n+1,dtype=object)
        rhs[:n]=-Hx[q:,q:]@p-Hu[q:,q:]@pv-Hv[q:,q:]@pu+lx*p
        rhs[:n]+=u['eigenvalue'][0]*pv+v['eigenvalue'][k]*pu
        rhs[n]=-pu@pv;left.append(R@(rhs-K@z[:,k]))
        config_v=qw*dv[q:q+q];source=np.empty(n,dtype=object)
        for i in range(n):
            value=qw[i]*guv[i]/w[i] if i<q else arb(0)
            for j in range(q):
                value-=(Hx[q+i,j]*config[j]+Hu[q+i,j]*config_v[j]+Hv[q+i,j]*config_u[j])/(w[q+i]*w[j])
            source[i]=rw[i]*value
        rhs[:n]=source-(Hx[q:,q:]-lx*I)@h-b*px[:,k]
        rhs[:n]-=(Hu[q:,q:]-u['eigenvalue'][0]*I)@hv+v['border'][k]*pu
        rhs[:n]-=(Hv[q:,q:]-v['eigenvalue'][k]*I)@hu+u['border'][0]*pv
        rhs[n]=-(h@px[:,k]+pu@hv+pv@hu)
        right.append(R@(rhs-K@z[:,k]))
    return np.column_stack(left),np.column_stack(right),np.array(slopes)


@pytest.mark.parametrize('uncertain',[False,True])
def test_complete_dense_system_matches_signed_mixed_residuals(uncertain):
    previous=ctx.prec;ctx.prec=512
    try:
        args=operands();x,p,h,lam,b,R,z,u,v,px,qw,rw,w=args
        coefficient=arb(1,arb(1)/16) if uncertain else arb(1)
        action,_,_=action_family(coefficient)
        line,lx=signed.line_residual(action,x,p,lam,R,z,u,v,None)
        response=signed.physical_response_residual(action,x,p,lam,h,b,px,lx,R,z,qw,rw,w,u,v,None)
        for c in ([arb(15)/16,arb(17)/16] if uncertain else [arb(1)]):
            old_line,old_response,old_lx=explicit_systems(c,args)
            for actual,expected in ((line,old_line),(response,old_response),(lx,old_lx)):
                if uncertain:assert all(a.contains(e) for a,e in zip(actual.flat,expected.flat))
                else:assert all(abs(a-e)<arb('1e-100') for a,e in zip(actual.flat,expected.flat))
    finally:ctx.prec=previous
