"""Differentiate a cubic action's actual response source independently."""
import itertools
import numpy as np
from flint import arb,arb_mat,ctx
from bhsm.interface.affine_response_residual import response_legs,eigenpair_variation


def test_configuration_derivative_matches_exact_central_difference_of_quadratic_source():
    previous=ctx.prec;ctx.prec=256
    try:
        x=np.array([arb(1),arb(2),arb(3)],dtype=object)
        v=np.array([arb(-2),arb(1),arb(4)],dtype=object)
        R=np.array([[arb(t) for t in row] for row in [[1,-2,3],[2,1,-1],[-1,3,2]]],dtype=object)
        h=np.array([arb(1)/4,-arb(1)/2],dtype=object)
        qw=[2];rw=[3,5];w=[7,11,13];alpha=np.array([arb(2),arb(-1),arb(3)],dtype=object)
        legs=response_legs(x,R,h,qw,rw,w,v[:,None])
        def dot(z):return sum((a*b for a,b in zip(alpha,z)),arb(0))
        def source(z):
            gradient=alpha*dot(z)**2/2
            H=np.outer(alpha,alpha)*dot(z)
            rhs=np.array([3*(2*gradient[0]/7-H[1,0]*2*z[1]/(11*7)),
                          5*(-H[2,0]*2*z[1]/(13*7))],dtype=object)
            return R[:,:2]@(rhs-H[1:,1:]@h)
        actual=(source(x+v)-source(x-v))/2
        for k in range(3):
            g=legs['gradient_left'][:,k];a=legs['configuration_left'][:,k];c=legs['hessian_left'][:,k]
            result=dot(x)*dot(g)*dot(v)-dot(a)*dot(legs['configuration'])*dot(v)
            result-=dot(x)*dot(a)*dot(legs['configuration_derivative'][:,0])
            result-=dot(c)*dot(legs['hard'])*dot(v)
            assert result.overlaps(actual[k])
    finally:ctx.prec=previous


def test_eigenpair_variation_includes_both_border_terms_at_every_corner():
    R=arb_mat([[1,-2,3],[2,1,-1],[-1,3,2]])
    h=[arb(1)/4,-arb(1)/2];b=arb(3)/4;r=[arb(1)/32,arb(1)/64,arb(1)/128]
    bound=eigenpair_variation(np.array(R.entries(),dtype=object).reshape(3,3),h,b,r)
    u=arb_mat(3,1,h+[b])
    for signs in itertools.product((-1,1),repeat=3):
        p0,p1,lam=[a*s for a,s in zip(r,signs)]
        delta=arb_mat([[-lam,0,p0],[0,-lam,p1],[p0,p1,0]])
        actual=R*delta*u
        assert all(limit>=abs(val) for limit,val in zip(bound,actual.entries()))
