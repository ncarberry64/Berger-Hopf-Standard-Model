"""Complete state derivatives of centered physical variation residuals.

Eigenpair and response operands are held fixed while differentiating the state.
They may range over their proved boxes throughout a mean-value integration.
"""
import numpy as np
from flint import arb
from bhsm.interface.centered_coupled_variation_residual import _inputs
from bhsm.interface.affine_eigenpair_contraction import _balls
from bhsm.interface.affine_response_residual import response_legs


def _domain(state,directions):
    d=_balls(directions)
    if d.ndim!=2 or d.shape[0]!=state.size or not d.shape[1]:
        raise ValueError('complete nonempty affine state directions required')
    return d


def line_state_derivative(action,state,psi,eigenvalue,preconditioner,centers,directions,domain_directions,maps):
    """D_x of R*(b_line-K*u0), shape (bordered rows, input columns, domain columns)."""
    x,p,lam,R,u,v,c,raw_p,raw_u=_inputs(state,psi,eigenvalue,preconditioner,centers,directions)
    d=_domain(x,domain_directions);n=p.size;count=u.shape[1]
    out=np.empty((n+1,count,d.shape[1]),dtype=object)
    pp=raw_p[:,None,None,None];vv=v[:,None,:,None];dd=d[:,None,None,:]
    dslope=np.asarray(action(x,[pp,pp,vv,dd],maps),dtype=object).reshape(1,count,d.shape[1])
    rp=R[:,:n]@p
    for start in range(0,n+1,4):
        stop=min(start+4,n+1);cc=c[:,start:stop,None,None]
        tile=-np.asarray(action(x,[cc,pp,vv,dd],maps),dtype=object)
        tile-=np.asarray(action(x,[cc,raw_u[:,None,:,None],dd],maps),dtype=object)
        tile+=rp[start:stop,None,None]*dslope
        out[start:stop]=tile
    if not all(v.is_finite() for v in out.flat):raise ArithmeticError('finite line state derivative required')
    return out


def response_state_derivative(action,state,psi,eigenvalue,hard,preconditioner,centers,
                              q_weights,reduced_weights,state_weights,directions,domain_directions,maps):
    """D_x of the complete response residual with p,lambda,h,b,dp held fixed."""
    x,p,lam,R,u,v,c,raw_p,raw_u=_inputs(state,psi,eigenvalue,preconditioner,centers,directions)
    d=_domain(x,domain_directions);h=_balls(hard);n=p.size;count=u.shape[1]
    if h.shape!=(n,):raise ValueError('complete hard response required')
    legs=response_legs(x,R,h,q_weights,reduced_weights,state_weights,v)
    domain_legs=response_legs(x,R,h,q_weights,reduced_weights,state_weights,d)
    out=np.empty((n+1,count,d.shape[1]),dtype=object)
    pp=raw_p[:,None,None,None];vv=v[:,None,:,None];dd=d[:,None,None,:]
    config=legs['configuration'][:,None,None,None]
    cv=legs['configuration_derivative'][:,None,:,None]
    cd=domain_legs['configuration_derivative'][:,None,None,:]
    hh=legs['hard'][:,None,None,None]
    dslope=np.asarray(action(x,[pp,pp,vv,dd],maps),dtype=object).reshape(1,count,d.shape[1])
    rh=R[:,:n]@h
    for start in range(0,n+1,4):
        stop=min(start+4,n+1);cc=c[:,start:stop,None,None]
        g=legs['gradient_left'][:,start:stop,None,None]
        a=legs['configuration_left'][:,start:stop,None,None]
        tile=np.asarray(action(x,[g,vv,dd],maps),dtype=object)
        tile-=np.asarray(action(x,[a,config,vv,dd],maps),dtype=object)
        tile-=np.asarray(action(x,[a,cd,vv],maps),dtype=object)
        tile-=np.asarray(action(x,[a,cv,dd],maps),dtype=object)
        tile-=np.asarray(action(x,[cc,hh,vv,dd],maps),dtype=object)
        tile-=np.asarray(action(x,[cc,raw_u[:,None,:,None],dd],maps),dtype=object)
        tile+=rh[start:stop,None,None]*dslope
        out[start:stop]=tile
    if not all(v.is_finite() for v in out.flat):raise ArithmeticError('finite response state derivative required')
    return out
