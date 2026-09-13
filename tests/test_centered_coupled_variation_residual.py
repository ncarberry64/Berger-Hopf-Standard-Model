"""Compare signed action residuals against direct exact polynomial matrices."""
from itertools import product
import numpy as np
import pytest
from flint import arb,ctx
from bhsm.interface.centered_coupled_variation_residual import line_residual,physical_response_residual


def test_signed_residuals_equal_direct_bordered_matrix_residuals():
    previous=ctx.prec;ctx.prec=256
    try:
        q,n=2,3;size=q+n
        x=np.array([arb(i+1)/7 for i in range(size)])
        a=np.array([arb(v) for v in (1,-2,1,0,3)])
        b=np.array([arb(v) for v in (2,1,-1,1,0)])
        H=np.array([[arb(int(i==j)*(i+1))+(a@x)*a[i]*a[j]+(b@x)**2*b[i]*b[j]/2
                     for j in range(size)] for i in range(size)])
        T=np.array([[[a[i]*a[j]*a[k]+(b@x)*b[i]*b[j]*b[k] for k in range(size)]
                     for j in range(size)] for i in range(size)])
        def action(state,legs,maps):
            tensor=H if len(legs)==2 else T
            result=None
            for indices in product(range(size),repeat=len(legs)):
                term=tensor[indices]
                for leg,index in zip(legs,indices):term=term*leg[index]
                result=term if result is None else result+term
            return result
        p=np.array([arb(1),arb(0),arb(0)]);lam=arb(2)
        R=np.array([[(arb(int(i==j))+arb((i+1)*(j+2))/31).mid() for j in range(n+1)] for i in range(n+1)])
        u=np.array([[arb((i+1)*(j+1))/16 for j in range(2)] for i in range(n+1)])
        v=np.array([[arb(value) for value in row] for row in ((1,0),(0,2),(1,-1),(2,1),(-1,3))])
        K=np.full((n+1,n+1),arb(0));K[:n,:n]=H[q:,q:]-lam*np.eye(n,dtype=int)
        K[:n,n]=p;K[n,:n]=p
        dH=np.array([[[sum((T[q+i,q+j,k]*v[k,col] for k in range(size)),arb(0))
                       for j in range(n)] for i in range(n)] for col in range(2)])
        slopes=np.array([p@matrix@p for matrix in dH])
        rhs=np.vstack((np.column_stack([-matrix@p+slopes[col]*p for col,matrix in enumerate(dH)]),np.full((1,2),arb(0))))
        expected=R@(rhs-K@u)
        actual,computed_slopes=line_residual(action,x,p,lam,R,u,v,None)
        assert all(abs(a-b)<arb('1e-60') for a,b in zip(actual.flat,expected.flat))
        assert all(abs(a-b)<arb('1e-60') for a,b in zip(slopes,computed_slopes))

        qw=np.array([arb(2),arb(3)]);rw=np.array([arb(3),arb(4),arb(5)])
        w=np.array([arb(i+1) for i in range(size)])
        hard=np.array([arb(0),-arb(1)/7,arb(2)/7]);border=arb(3)
        dp=np.array([[arb(0),arb(0)],[arb(1)/5,arb(2)/5],[-arb(1)/4,arb(1)/8]])
        configuration=qw*x[q:q+q];dc=qw[:,None]*v[q:q+q]
        drhs=np.empty((n,2),dtype=object)
        for i,col in product(range(n),range(2)):
            value=qw[i]*(H@v)[i,col]/w[i] if i<q else arb(0)
            for j in range(q):
                value-=H[q+i,j]*dc[j,col]/(w[q+i]*w[j])
                value-=sum((T[q+i,j,k]*v[k,col] for k in range(size)),arb(0))*configuration[j]/(w[q+i]*w[j])
            drhs[i,col]=rw[i]*value
        rhs=np.vstack((np.column_stack([drhs[:,col]-(matrix-slopes[col]*np.eye(n,dtype=int))@hard-border*dp[:,col]
                                        for col,matrix in enumerate(dH)]),-(hard@dp)[None,:]))
        expected=R@(rhs-K@u)
        actual=physical_response_residual(action,x,p,lam,hard,border,dp,slopes,R,u,qw,rw,w,v,None)
        assert all(abs(a-b)<arb('1e-60') for a,b in zip(actual.flat,expected.flat))
    finally:ctx.prec=previous


def test_uncertain_variation_centers_are_rejected():
    with pytest.raises(ValueError,match='fixed exact'):
        line_residual(None,[arb(0),arb(0)],[arb(1)],arb(1),[[arb(1),arb(0)],[arb(0),arb(1)]],
            [[arb(0,arb(1)/8)],[arb(0)]],[[arb(1)],[arb(0)]],None)
