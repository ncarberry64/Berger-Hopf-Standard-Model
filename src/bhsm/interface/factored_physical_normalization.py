"""Cancel a verified nonzero common response scale before field normalization."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls


def normalized_value(configuration,reduced_weights,psi,hard,border,descriptor,cpsi,remainder):
    """Evaluate the retained normalized field after factoring its border scale.

    G=b*[s/b*configuration, redW*(psi+s/b*hard)] and
    delta=b*(cpsi+s/b*remainder). Its normalization cancels |b|, retaining sign(b).
    Caller owns the complete action/eigenpair/response input enclosures.
    """
    configuration,w,psi,hard,scalars=map(_balls,(configuration,reduced_weights,psi,hard,
        [border,descriptor,cpsi,remainder]))
    if (configuration.ndim!=1 or not configuration.size or psi.ndim!=1 or not psi.size
            or w.shape!=psi.shape or hard.shape!=psi.shape or not all(v>0 for v in w)):
        raise ValueError('complete physical field operands and positive weights required')
    b,s,c,r=scalars
    if b>0:sign=1
    elif b<0:sign=-1
    else:raise ArithmeticError('verified nonzero border sign required for factorization')
    ratio=s/b
    G=np.concatenate((ratio*configuration,w*(psi+ratio*hard)))
    norm=sum((v**2 for v in G),arb(0)).sqrt()
    if not norm>0:raise ArithmeticError('positive factored field norm required')
    result=np.concatenate((sign*G/norm,np.array([sign*(c+ratio*r)/norm],dtype=object)))
    if not all(v.is_finite() for v in result):raise ArithmeticError('finite normalized field required')
    return result,dict(border_sign=int(sign),factored_norm_lower_rational=str(norm.lower().fmpq()),
        original_norm_lower_rational=str((abs(b)*norm).lower().fmpq()),
        action_domain_bound=False,FULL_BHSM_COMPLETE=False)
