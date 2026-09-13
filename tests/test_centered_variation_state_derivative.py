"""Independent centered differences are exact for these quadratic residuals."""
from itertools import product
import numpy as np
from flint import arb,ctx
from bhsm.interface.centered_coupled_variation_residual import line_residual,physical_response_residual
from bhsm.interface.centered_variation_state_derivative import line_state_derivative,response_state_derivative


def test_complete_affine_state_derivatives_match_polynomial_centered_differences():
    previous=ctx.prec;ctx.prec=256
    try:
        q,n=1,2;size=q+n
        a=np.array([arb(2),arb(-1),arb(3)]);b=np.array([arb(1),arb(2),arb(-1)])
        def action(x,legs,maps):
            rank=len(legs);result=None
            for indices in product(range(size),repeat=rank):
                if rank==2:
                    i,j=indices;t=arb(int(i==j))+(a@x)*a[i]*a[j]+(b@x)**2*b[i]*b[j]/2
                elif rank==3:
                    i,j,k=indices;t=a[i]*a[j]*a[k]+(b@x)*b[i]*b[j]*b[k]
                else:
                    i,j,k,l=indices;t=b[i]*b[j]*b[k]*b[l]
                for leg,i in zip(legs,indices):t=t*leg[i]
                result=t if result is None else result+t
            return result
        x=np.array([arb(1)/4,arb(1)/8,-arb(1)/2]);p=np.array([arb(1),arb(0)]);lam=arb(2)
        R=np.array([[arb(int(i==j))+arb((i+1)*(j+1))/16 for j in range(3)] for i in range(3)])
        u=np.array([[arb(i+1)/8,arb(2*i+1)/16] for i in range(3)])
        v=np.array([[arb(i+1),arb(1-i)] for i in range(3)])
        d=np.array([[arb(2-i),arb(i-1)] for i in range(3)])
        qw=np.array([arb(2)]);rw=np.array([arb(3),arb(4)]);w=np.array([arb(2),arb(3),arb(5)])
        h=np.array([arb(1)/8,-arb(1)/4]);border=arb(3)
        dp=np.array([[arb(0),arb(0)],[arb(1)/16,-arb(1)/8]])
        line=line_state_derivative(action,x,p,lam,R,u,v,d,None)
        response=response_state_derivative(action,x,p,lam,h,R,u,qw,rw,w,v,d,None)
        step=arb(1)/1024
        for col in range(d.shape[1]):
            sides=[]
            for sign in (-1,1):
                xx=x+sign*step*d[:,col]
                lin,slopes=line_residual(action,xx,p,lam,R,u,v,None)
                res=physical_response_residual(action,xx,p,lam,h,border,dp,slopes,R,u,qw,rw,w,v,None)
                sides.append((lin,res))
            for actual,which in ((line,0),(response,1)):
                expected=(sides[1][which]-sides[0][which])/(2*step)
                assert all(abs(a-b)<arb('1e-60') for a,b in zip(actual[:,:,col].flat,expected.flat))
    finally:ctx.prec=previous
