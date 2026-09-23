"""A linear response enclosure from an already proved weighted defect bound."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls


def enclose_response(center,preconditioned_residual,weights,defect_row_bounds):
    """Enclose z solving J*z=b from ||I-R*J||_weights < 1.

    The caller must bind the residual R*(b-J*center) and weighted row bounds to
    the same actual family J. A matrix-entry hull need not itself be invertible.
    This function alone proves no action domain or physical rate.
    """
    z,e,r,V=map(_balls,(center,preconditioned_residual,weights,defect_row_bounds))
    if z.ndim!=1 or not z.size or any(a.shape!=z.shape for a in (e,r,V)):
        raise ValueError('matching complete response vectors required')
    if not all(v.rad().is_zero() for v in z) or not all(v>0 and v.rad().is_zero() for v in r):
        raise ValueError('exact center and positive exact norm weights required')
    if not all(v>=0 for v in V):raise ValueError('nonnegative defect row bounds required')
    q=max((v/w).upper() for v,w in zip(V,r,strict=True))
    if not q<1:raise ArithmeticError('strict weighted contraction required')
    residual=max((abs(v).upper()/w).upper() for v,w in zip(e,r,strict=True))
    scale=(residual/(1-q)).upper()
    radius=np.array([(scale*w).upper() for w in r],dtype=object)
    box=np.array([v+arb(0,d) for v,d in zip(z,radius,strict=True)],dtype=object)
    return box,dict(weighted_contraction_upper_rational=str(q.fmpq()),
        weighted_residual_upper_rational=str(residual.fmpq()),
        weighted_error_upper_rational=str(scale.fmpq()),
        action_domain_bound=False,uniform_physical_rate_enclosed=False,FULL_BHSM_COMPLETE=False)
