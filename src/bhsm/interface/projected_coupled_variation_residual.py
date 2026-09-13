"""Combine the selected-line projection inside the signed action leg."""
import numpy as np
from bhsm.interface.centered_coupled_variation_residual import _inputs


def line_residual(action,state,psi,eigenvalue,preconditioner,centers,directions,maps):
    """Same centered line residual, with R*(I-p*p^T) contracted before bounds.

    The algebra is valid without replacing any uncertain input by its midpoint.
    The physical meaning of the selected-line RHS remains the caller's proof.
    """
    x,p,lam,R,u,v,c,raw_p,raw_u=_inputs(state,psi,eigenvalue,preconditioner,centers,directions)
    n=p.size;count=u.shape[1];rp=R[:,:n]@p
    projected=c-raw_p[:,None]*rp[None,:]
    slopes=np.asarray(action(x,[raw_p[:,None,None],raw_p[:,None,None],v[:,None,:]],maps),dtype=object).reshape(count)
    residual=-np.asarray(action(x,[projected[:,:,None],raw_p[:,None,None],v[:,None,:]],maps),dtype=object)
    residual-=np.asarray(action(x,[c[:,:,None],raw_u[:,None,:]],maps),dtype=object)
    residual+=lam*(R[:,:n]@u[:n])-rp[:,None]*u[-1][None,:]
    residual-=R[:,-1,None]*(p@u[:n])[None,:]
    if residual.shape!=(n+1,count) or not all(a.is_finite() for a in residual.flat):
        raise ArithmeticError('complete finite projected selected-line residual required')
    return residual,slopes
