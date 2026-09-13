"""Retain a common longitudinal state parameter in signed action contractions."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls
from bhsm.interface.direct_physical_neighborhood import exact_radius


def contract_affine(at_base,at_full,legs,raw_direction,radius):
    """Enclose S_k(B+u*l)[legs] using the complete S_(k+1)[legs,u].

    The caller must establish |l|<=radius and full-domain containment of every
    B+t*u*l. Legs are held fixed during this coefficient expansion: unknown
    target-state legs may range over their supplied interval boxes. Callbacks
    own the appropriate action state, maps, and factored-integrand context.
    The present retained action supports this expansion through k=4 only.
    """
    if not 2<=len(legs)<=4:raise ValueError('complete next action order required; use orders 2..4')
    direction=_balls(raw_direction);arrays=tuple(_balls(v) for v in legs)
    if (direction.ndim!=1 or not direction.size or any(a.ndim<1 or not all(a.shape)
            or a.shape[0]!=direction.size for a in arrays)):
        raise ValueError('matching finite action legs and raw direction required')
    r=exact_radius(radius)
    extra=direction.reshape((direction.size,)+(1,)*(max(a.ndim for a in arrays)-1))
    base=_balls(at_base(arrays));derivative=_balls(at_full(arrays+(extra,)))
    if base.shape!=derivative.shape or not base.size:raise ValueError('matching complete contraction outputs required')
    result=np.asarray(base+arb(0,r)*derivative,dtype=object)
    if not all(v.is_finite() for v in result.flat):raise ArithmeticError('finite affine action contraction required')
    return result
