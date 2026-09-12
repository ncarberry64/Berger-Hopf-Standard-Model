"""Differentiate the same coupled normalization before interval evaluation."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls


def normalized_derivative(configuration,weights,psi,hard,border,descriptor,cpsi,remainder,
                          dconfiguration,dpsi,dhard,dborder,ddescriptor,dcpsi,dremainder,
                          *,coupled_identities_and_variations=False):
    """Require psi^T psi=1, psi^T hard=0 and their differentiated identities.

    All variations must describe the same actual coupled family. Component
    boxes cannot establish these identities. No change of physical formula is
    made: the nonzero common border scale cancels before differentiation.
    """
    if coupled_identities_and_variations is not True:
        raise ValueError('verified coupled identities and their variations required')
    c,w,p,h,scalars,dc,dp,dh,db,ds,dcp,dr=map(_balls,(
        configuration,weights,psi,hard,[border,descriptor,cpsi,remainder],
        dconfiguration,dpsi,dhard,dborder,ddescriptor,dcpsi,dremainder))
    if (c.ndim!=1 or not c.size or p.ndim!=1 or not p.size or h.shape!=p.shape or w.shape!=p.shape
            or not all(v>=1 for v in w) or dp.ndim!=2 or dp.shape[0]!=p.size or not dp.shape[1]
            or dh.shape!=dp.shape or dc.shape!=(c.size,dp.shape[1])
            or any(a.shape!=(dp.shape[1],) for a in (db,ds,dcp,dr))):
        raise ValueError('complete compatible coupled normalization variations required')
    b,s,cp,r=scalars
    if b>0:sign=1
    elif b<0:sign=-1
    else:raise ArithmeticError('verified nonzero border sign required')
    t=s/b;dt=(ds-t*db)/b
    combined=p+t*h
    dcombined=dp+h[:,None]*dt[None,:]+t*dh
    size=sum((v**2 for v in h),arb(0))+sum((v**2 for v in c),arb(0))
    norm_squared=arb(1)+sum(((wi**2-1)*vi**2 for wi,vi in zip(w,combined)),arb(0))+t**2*size
    norm=norm_squared.sqrt()
    if not norm>0:raise ArithmeticError('positive coupled field norm required')
    half_dnorm_squared=np.array([
        sum(((w[i]**2-1)*combined[i]*dcombined[i,k] for i in range(p.size)),arb(0))
        +t*dt[k]*size+t**2*(sum((h[i]*dh[i,k] for i in range(p.size)),arb(0))
                           +sum((c[i]*dc[i,k] for i in range(c.size)),arb(0)))
        for k in range(dp.shape[1])],dtype=object)
    numerator=np.concatenate((t*c,w*combined,np.array([cp+t*r],dtype=object)))
    dnumerator=np.vstack((c[:,None]*dt[None,:]+t*dc,w[:,None]*dcombined,dcp+dt*r+t*dr))
    result=sign*(dnumerator-numerator[:,None]*half_dnorm_squared[None,:]/norm_squared)/norm
    if not all(v.is_finite() for v in result.flat):raise ArithmeticError('finite coupled first derivatives required')
    return result,dict(border_sign=sign,coupled_identities_and_variations_required=True,
        common_border_scale_canceled_before_differentiation=True,
        action_domain_bound=False,FULL_BHSM_COMPLETE=False)
