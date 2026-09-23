"""Signed raw action legs for the retained bordered-response source."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls


def response_legs(state,preconditioner,hard_center,q_weights,reduced_weights,state_weights,directions):
    """Construct the four complete action contractions in D_x[R*(b-H*h0)]."""
    x,R,h,qw,rw,w,v=map(_balls,(state,preconditioner,hard_center,q_weights,reduced_weights,state_weights,directions))
    q,n=qw.size,rw.size
    if (qw.ndim!=1 or rw.ndim!=1 or not 0<q<=n or x.shape!=(q+n,) or w.shape!=x.shape
            or h.shape!=(n,) or R.shape!=(n+1,n+1) or v.ndim!=2 or v.shape[0]!=q+n):
        raise ValueError('complete compatible physical response operands required')
    if not all(a>0 for values in (qw,rw,w) for a in values):
        raise ValueError('positive metric weights required')
    g=np.full((q+n,n+1),arb(0),dtype=object)
    a=g.copy();c=g.copy();d=np.full(q+n,arb(0),dtype=object)
    dh=np.full_like(v,arb(0));hard=np.concatenate((np.full(q,arb(0),dtype=object),h))
    for j in range(n):
        for k in range(n+1):
            a[q+j,k]=R[k,j]*rw[j]/w[q+j]
            c[q+j,k]=R[k,j]
            if j<q:g[j,k]=R[k,j]*rw[j]*qw[j]/w[j]
    for j in range(q):
        d[j]=qw[j]*x[q+j]/w[j]
        dh[j]=qw[j]*v[q+j]/w[j]
    return dict(gradient_left=g,configuration_left=a,hessian_left=c,
        configuration=d,configuration_derivative=dh,hard=hard)


def eigenpair_variation(preconditioner,hard_center,border_center,radii):
    """Bound p/lambda uncertainty in R*((b,0)-K*(h0,b0))."""
    R,h,b,r=map(_balls,(preconditioner,hard_center,[border_center],radii))
    n=h.size
    if h.ndim!=1 or not n or r.shape!=(n+1,) or R.shape!=(n+1,n+1):
        raise ValueError('matching eigenpair and response operands required')
    if not all(v>=0 for v in r):raise ValueError('nonnegative eigenpair radii required')
    return np.array([(r[-1]*abs(sum((R[k,j]*h[j] for j in range(n)),arb(0))).upper()
        +sum((abs(b[0]*R[k,j]+R[k,n]*h[j]).upper()*r[j] for j in range(n)),arb(0))).upper()
        for k in range(n+1)],dtype=object)
