"""Complete signed mixed action residuals before interval matrix multiplication."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls
from bhsm.interface.affine_response_residual import response_legs
from bhsm.interface.centered_coupled_variation_residual import _inputs


def _mixed(state,psi,eigenvalue,R,centers,axis,transverse):
    data=_inputs(state,psi,eigenvalue,R,centers,transverse['direction'])
    x,p,lam,R,z,v,c,raw_p,raw_z=data;n=p.size;count=z.shape[1]
    u,pu,pv,lu,lv=map(_balls,(axis['direction'],axis['psi'],transverse['psi'],
        axis['eigenvalue'],transverse['eigenvalue']))
    if (u.shape!=(x.size,1) or pu.shape!=(n,1) or pv.shape!=(n,count)
            or lu.shape!=(1,) or lv.shape!=(count,)):
        raise ValueError('complete compatible first variations required')
    return data,u,pu,pv,lu,lv


def _raw(variation,q):
    return np.vstack((np.full((q,variation.shape[1]),arb(0),dtype=object),variation))


def _subtract_center(action,x,p,lam,R,z,c,raw_z,residual,maps):
    n=p.size
    residual-=np.asarray(action(x,[c[:,:,None],raw_z[:,None,:]],maps),dtype=object)
    residual+=lam*(R[:,:n]@z[:n])-(R[:,:n]@p)[:,None]*z[-1][None,:]
    residual-=R[:,-1,None]*(p@z[:n])[None,:]
    if residual.shape!=z.shape or not all(a.is_finite() for a in residual.flat):
        raise ArithmeticError('complete finite mixed residual required')
    return residual


def line_residual(action,state,psi,eigenvalue,preconditioner,centers,axis,transverse,maps):
    """R*(mixed eigenline RHS-K*z0), including differentiated normalization."""
    data,u,pu,pv,lu,lv=_mixed(state,psi,eigenvalue,preconditioner,centers,axis,transverse)
    x,p,lam,R,z,v,c,raw_p,raw_z=data;n=p.size;q=x.size-n;count=z.shape[1]
    raw_pu=_raw(pu,q);raw_pv=_raw(pv,q)
    def contract(*legs):return np.asarray(action(x,list(legs),maps),dtype=object)
    pp=raw_p[:,None,None];uu=u[:,None,:];vv=v[:,None,:];cc=c[:,:,None]
    mixed_slope=contract(pp,pp,uu,vv).reshape(count)
    mixed_slope+=contract(raw_pv[:,None,:],pp,uu).reshape(count)
    mixed_slope+=contract(raw_pu[:,None,:],pp,vv).reshape(count)
    residual=-contract(cc,pp,uu,vv)
    residual-=contract(cc,raw_pv[:,None,:],uu)
    residual-=contract(cc,raw_pu[:,None,:],vv)
    residual+=(R[:,:n]@p)[:,None]*mixed_slope[None,:]
    residual+=lu[0]*(R[:,:n]@pv)+(R[:,:n]@pu)*lv[None,:]
    residual-=R[:,-1,None]*(pu[:,0]@pv)[None,:]
    return _subtract_center(action,x,p,lam,R,z,c,raw_z,residual,maps),mixed_slope


def physical_response_residual(action,state,psi,eigenvalue,hard,border,
        mixed_line,mixed_slopes,preconditioner,centers,q_weights,reduced_weights,
        state_weights,axis,transverse,maps):
    """R*(source_uv-K_uv*y-K_u*y_v-K_v*y_u-K*z0), with all bottom terms."""
    data,u,pu,pv,lu,lv=_mixed(state,psi,eigenvalue,preconditioner,centers,axis,transverse)
    x,p,lam,R,z,v,c,raw_p,raw_z=data;n=p.size;q=x.size-n;count=z.shape[1]
    h,b,hu,hv,bu,bv,px,lx=map(_balls,(hard,[border],axis['hard'],transverse['hard'],
        axis['border'],transverse['border'],mixed_line,mixed_slopes))
    if (h.shape!=(n,) or hu.shape!=(n,1) or hv.shape!=(n,count) or bu.shape!=(1,)
            or bv.shape!=(count,) or px.shape!=(n,count) or lx.shape!=(count,)):
        raise ValueError('complete compatible mixed physical response operands required')
    legs=response_legs(x,R,h,q_weights,reduced_weights,state_weights,v)
    ulegs=response_legs(x,R,h,q_weights,reduced_weights,state_weights,u)
    def contract(*legs):return np.asarray(action(x,list(legs),maps),dtype=object)
    uu=u[:,None,:];vv=v[:,None,:];cc=c[:,:,None]
    aa=legs['configuration_left'][:,:,None]
    residual=contract(legs['gradient_left'][:,:,None],uu,vv)
    residual-=contract(aa,legs['configuration'][:,None,None],uu,vv)
    residual-=contract(aa,legs['configuration_derivative'][:,None,:],uu)
    residual-=contract(aa,ulegs['configuration_derivative'][:,None,:],vv)
    residual-=contract(cc,legs['hard'][:,None,None],uu,vv)
    residual-=contract(cc,_raw(hv,q)[:,None,:],uu)
    residual-=contract(cc,_raw(hu,q)[:,None,:],vv)
    residual+=(R[:,:n]@h)[:,None]*lx[None,:]-b[0]*(R[:,:n]@px)
    residual+=lu[0]*(R[:,:n]@hv)-(R[:,:n]@pu)*bv[None,:]
    residual+=(R[:,:n]@hu)*lv[None,:]-bu[0]*(R[:,:n]@pv)
    residual-=R[:,-1,None]*(h@px+pu[:,0]@hv+hu[:,0]@pv)[None,:]
    return _subtract_center(action,x,p,lam,R,z,c,raw_z,residual,maps)
