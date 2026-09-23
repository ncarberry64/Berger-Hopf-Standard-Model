"""Normalize using identities proved by the coupled eigenpair/response systems."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls


def normalized_value(configuration,reduced_weights,psi,hard,border,descriptor,cpsi,remainder,
                     *,normalized_eigenpair=False,bordered_orthogonality=False):
    """Require psi^T psi=1 and psi^T hard=0 for the same actual coupled solution.

    With t=s/b, the scaled norm squared is exactly
    1+sum((w^2-1)*(psi+t*hard)^2)+t^2*(||hard||^2+||configuration||^2).
    Component boxes alone do not establish either required identity.
    """
    if normalized_eigenpair is not True or bordered_orthogonality is not True:
        raise ValueError('verified coupled normalization and orthogonality required')
    configuration,w,psi,hard,scalars=map(_balls,(configuration,reduced_weights,psi,hard,
        [border,descriptor,cpsi,remainder]))
    if (configuration.ndim!=1 or not configuration.size or psi.ndim!=1 or not psi.size
            or w.shape!=psi.shape or hard.shape!=psi.shape or not all(v>=1 for v in w)):
        raise ValueError('complete physical field operands and Sobolev weights at least one required')
    b,s,c,r=scalars
    if b>0:sign=1
    elif b<0:sign=-1
    else:raise ArithmeticError('verified nonzero border sign required')
    t=s/b;combined=psi+t*hard
    norm_squared=arb(1)+sum(((wi**2-1)*vi**2 for wi,vi in zip(w,combined)),arb(0))
    norm_squared+=t**2*(sum((v**2 for v in hard),arb(0))+sum((v**2 for v in configuration),arb(0)))
    norm=norm_squared.sqrt()
    if not norm>0:raise ArithmeticError('positive coupled field norm required')
    G=np.concatenate((t*configuration,w*combined))
    value=np.concatenate((sign*G/norm,np.array([sign*(c+t*r)/norm],dtype=object)))
    if not all(v.is_finite() for v in value):raise ArithmeticError('finite normalized field required')
    return value,dict(border_sign=sign,coupled_identities_required=True,
        factored_norm_lower_rational=str(norm.lower().fmpq()),
        original_norm_lower_rational=str((abs(b)*norm).lower().fmpq()),
        action_domain_bound=False,FULL_BHSM_COMPLETE=False)
