"""Mixed second derivatives after canceling the verified common border scale."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls

KEYS=('configuration','psi','hard','border','descriptor','cpsi','remainder')


def _jet(values,q,n,count):
    if not isinstance(values,dict) or set(values)!=set(KEYS):raise ValueError('all seven variation fields required')
    result={key:_balls(values[key]) for key in KEYS}
    shapes={'configuration':(q,count),'psi':(n,count),'hard':(n,count)}
    if any(value.shape!=shapes.get(key,(count,)) for key,value in result.items()):
        raise ValueError('complete compatible variation columns required')
    return result


def normalized_mixed(configuration,weights,psi,hard,border,descriptor,cpsi,remainder,
                     axis,transverse,mixed,*,coupled_identities_and_variations=False):
    """Require p.p=1, p.h=0 and both first/mixed differentiated identities."""
    if coupled_identities_and_variations is not True:
        raise ValueError('verified coupled identities through mixed second order required')
    c,w,p,h,svals=map(_balls,(configuration,weights,psi,hard,[border,descriptor,cpsi,remainder]))
    if (c.ndim!=1 or not c.size or p.ndim!=1 or not p.size or h.shape!=p.shape
            or w.shape!=p.shape or not all(v>=1 for v in w)):
        raise ValueError('complete compatible coupled physical value operands required')
    candidate=np.asarray(transverse.get('psi') if isinstance(transverse,dict) else None)
    if candidate.ndim!=2 or candidate.shape[1]<1:raise ValueError('nonempty transverse variation matrix required')
    count=candidate.shape[1];u=_jet(axis,c.size,p.size,1);v=_jet(transverse,c.size,p.size,count);uv=_jet(mixed,c.size,p.size,count)
    b,s,cp,rem=svals
    if b>0:sign=1
    elif b<0:sign=-1
    else:raise ArithmeticError('verified nonzero border sign required')
    t=s/b;a=p+t*h;nu=w*w-1
    size=sum((z*z for z in h),arb(0))+sum((z*z for z in c),arb(0))
    Q=arb(1)+sum((wi*ai*ai for wi,ai in zip(nu,a)),arb(0))+t*t*size
    N=Q.sqrt()
    if not N>0:raise ArithmeticError('positive coupled field norm required')
    U=np.concatenate((t*c,w*a,np.array([cp+t*rem],dtype=object)))
    result=np.empty((U.size,count),dtype=object)
    for k in range(count):
        du={key:value[:,0] if value.ndim==2 else value[0] for key,value in u.items()}
        dv={key:value[:,k] if value.ndim==2 else value[k] for key,value in v.items()}
        dx={key:value[:,k] if value.ndim==2 else value[k] for key,value in uv.items()}
        tu=(du['descriptor']-t*du['border'])/b;tv=(dv['descriptor']-t*dv['border'])/b
        tx=(dx['descriptor']-t*dx['border']-tu*dv['border']-tv*du['border'])/b
        au=du['psi']+tu*h+t*du['hard'];av=dv['psi']+tv*h+t*dv['hard']
        ax=dx['psi']+tx*h+tu*dv['hard']+tv*du['hard']+t*dx['hard']
        Su=2*(h@du['hard']+c@du['configuration']);Sv=2*(h@dv['hard']+c@dv['configuration'])
        Sx=2*(du['hard']@dv['hard']+h@dx['hard']+du['configuration']@dv['configuration']+c@dx['configuration'])
        qu=sum((nu[i]*a[i]*au[i] for i in range(p.size)),arb(0))+t*tu*size+t*t*Su/2
        qv=sum((nu[i]*a[i]*av[i] for i in range(p.size)),arb(0))+t*tv*size+t*t*Sv/2
        qx=sum((nu[i]*(au[i]*av[i]+a[i]*ax[i]) for i in range(p.size)),arb(0))
        qx+=(tu*tv+t*tx)*size+t*tu*Sv+t*tv*Su+t*t*Sx/2
        Uu=np.concatenate((tu*c+t*du['configuration'],w*au,
            np.array([du['cpsi']+tu*rem+t*du['remainder']],dtype=object)))
        Uv=np.concatenate((tv*c+t*dv['configuration'],w*av,
            np.array([dv['cpsi']+tv*rem+t*dv['remainder']],dtype=object)))
        Ux=np.concatenate((tx*c+tu*dv['configuration']+tv*du['configuration']+t*dx['configuration'],w*ax,
            np.array([dx['cpsi']+tx*rem+tu*dv['remainder']+tv*du['remainder']+t*dx['remainder']],dtype=object)))
        result[:,k]=sign*(Ux-(Uu*qv+Uv*qu+U*qx)/Q+3*U*qu*qv/(Q*Q))/N
    if not all(v.is_finite() for v in result.flat):raise ArithmeticError('finite coupled mixed physical derivatives required')
    return result,dict(border_sign=sign,coupled_identities_through_mixed_second_order_required=True,
        common_border_scale_canceled_before_second_differentiation=True,
        action_domain_bound=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
