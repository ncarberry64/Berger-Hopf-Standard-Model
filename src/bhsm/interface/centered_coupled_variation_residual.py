"""Signed action residuals around fixed physical-variation centers."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls
from bhsm.interface.affine_response_residual import response_legs


def _inputs(state,psi,eigenvalue,preconditioner,centers,directions):
    x,p,lam,R,u,v=map(_balls,(state,psi,[eigenvalue],preconditioner,centers,directions))
    n=p.size;q=x.size-n
    if (x.ndim!=1 or p.ndim!=1 or not n or q<=0 or R.shape!=(n+1,n+1)
            or u.ndim!=2 or u.shape[0]!=n+1 or not u.shape[1] or v.shape!=(x.size,u.shape[1])):
        raise ValueError('complete compatible coupled variation operands required')
    if not all(a.rad().is_zero() for a in (*R.flat,*u.flat)):
        raise ValueError('fixed exact preconditioner and variation centers required')
    left=np.full((x.size,n+1),arb(0),dtype=object);left[q:]=R[:,:n].T
    raw_psi=np.concatenate((np.full(q,arb(0)),p))
    raw_center=np.vstack((np.full((q,u.shape[1]),arb(0)),u[:n]))
    return x,p,lam[0],R,u,v,left,raw_psi,raw_center


def line_residual(action,state,psi,eigenvalue,preconditioner,centers,directions,maps):
    """Enclose R*(projected eigenline RHS-K*u0), retaining signed action legs."""
    x,p,lam,R,u,v,c,raw_p,raw_u=_inputs(state,psi,eigenvalue,preconditioner,centers,directions)
    n=p.size;count=u.shape[1]
    slope=np.asarray(action(x,[raw_p[:,None,None],raw_p[:,None,None],v[:,None,:]],maps),dtype=object).reshape(count)
    residual=-np.asarray(action(x,[c[:,:,None],raw_p[:,None,None],v[:,None,:]],maps),dtype=object)
    residual-=np.asarray(action(x,[c[:,:,None],raw_u[:,None,:]],maps),dtype=object)
    Rp=R[:,:n]@p
    residual+=lam*(R[:,:n]@u[:n])+Rp[:,None]*(slope-u[-1])[None,:]
    residual-=R[:,-1,None]*(p@u[:n])[None,:]
    if residual.shape!=(n+1,count) or not all(a.is_finite() for a in residual.flat):
        raise ArithmeticError('complete finite centered selected-line residual required')
    return residual,slope


def physical_response_residual(action,state,psi,eigenvalue,hard,border,line_variation,slopes,
                               preconditioner,centers,q_weights,reduced_weights,state_weights,directions,maps):
    """Enclose R*(dsource-dK*response-K*u0), including both bottom-row terms."""
    x,p,lam,R,u,v,c,raw_p,raw_u=_inputs(state,psi,eigenvalue,preconditioner,centers,directions)
    h,b,dp,slope=map(_balls,(hard,[border],line_variation,slopes))
    n=p.size;count=u.shape[1]
    if h.shape!=(n,) or dp.shape!=(n,count) or slope.shape!=(count,):
        raise ValueError('complete physical response and selected-line variations required')
    legs=response_legs(x,R,h,q_weights,reduced_weights,state_weights,v)
    g=legs['gradient_left'][:,:,None];a=legs['configuration_left'][:,:,None]
    cv=c[:,:,None];vv=v[:,None,:]
    residual=np.asarray(action(x,[g,vv],maps),dtype=object)
    residual-=np.asarray(action(x,[a,legs['configuration'][:,None,None],vv],maps),dtype=object)
    residual-=np.asarray(action(x,[a,legs['configuration_derivative'][:,None,:]],maps),dtype=object)
    residual-=np.asarray(action(x,[cv,legs['hard'][:,None,None],vv],maps),dtype=object)
    residual-=np.asarray(action(x,[cv,raw_u[:,None,:]],maps),dtype=object)
    residual+=(R[:,:n]@h)[:,None]*slope[None,:]-b[0]*(R[:,:n]@dp)
    residual+=lam*(R[:,:n]@u[:n])-(R[:,:n]@p)[:,None]*u[-1][None,:]
    residual-=R[:,-1,None]*((h@dp)+(p@u[:n]))[None,:]
    if residual.shape!=(n+1,count) or not all(a.is_finite() for a in residual.flat):
        raise ArithmeticError('complete finite centered physical-response residual required')
    return residual
