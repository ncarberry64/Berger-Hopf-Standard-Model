"""Shared-parameter, arbitrary contracted jets of the retained action.

This encloses action derivatives, not implicit physical solutions. In particular
a fixed-leg fifth derivative is not a bound for the complete physical Hessian.
"""
import math
import numpy as np
from flint import arb
from bhsm.interface.factored_arb_integrand import factored_local_algebra
from bhsm.interface.shared_action_taylor import Taylor, scalar_taylor_action


def contract(module, state, legs, progress=None):
    """Enclose D^m S(x(theta))[v1(theta),...,vm(theta)], 1 <= m <= 6.

    All Taylor operands use ONE domain. Legs are evaluated pointwise: this
    routine does not differentiate a varying leg with respect to theta.
    Local polynomial factors are differentiated algebraically; exponentials,
    the global inertia inverse and the boundary square root retain remainders.
    """
    if len(state) != module.STATE or not 1 <= len(legs) <= 6:
        raise ValueError('complete action state and one through six legs required')
    if not all(isinstance(v, Taylor) for v in state):
        raise ValueError('shared Taylor state required')
    domain = state[0].domain
    if any(v.domain is not domain for v in state):
        raise ValueError('one common parameter domain required')
    if any(len(v) != module.STATE for v in legs):
        raise ValueError('complete raw action legs required')
    if any(isinstance(v, Taylor) and v.domain is not domain for leg in legs for v in leg):
        raise ValueError('legs must retain the state parameter identities')
    # Local maps and offsets depend on quadrature only, not on a physical solve.
    geometry = [module._integrand([arb(0)]*module.STATE, j, 0)
                for j in range(module.POINTS)]
    m = len(legs)
    with scalar_taylor_action(module):
        bulk = module.Mixed.constant(0, m)
        inertia = module.Mixed.constant(0, m)
        for j, base in enumerate(geometry):
            values = [sum((state[k]*a for k, a in mapping), domain.affine(c))
                      for mapping, c in zip(base.maps, base.values, strict=True)]
            local_legs = [np.asarray([sum((leg[k]*a for k, a in mapping), arb(0))
                         for mapping in base.maps], dtype=object) for leg in legs]
            variables = module._local_variables(values, m, local_legs)
            x = float(module._BASIS[0][j])
            sigma = -0.5+2*x/math.pi-math.sin(4*x)/(2*math.pi)
            constants = [module.RADIUS0, module.RADIUS0*math.cos(x),
                         module.RADIUS0*math.sin(x), 3*math.cos(x)**2,
                         3*math.sin(x)**2, 0.5*(15*5**(1/3)/4), 1-4*sigma**2]
            b, i = factored_local_algebra(variables, *map(arb, constants), lambda v: v.exp())
            weight = float(module._BASIS[1][j])
            bulk += weight*b
            inertia += weight*i
            if progress and (j+1) % 16 == 0:
                progress(j+1, module.POINTS)
        i0 = inertia.d[0]
        if not isinstance(i0, Taylor) or not i0.enclosure() > 0:
            raise ArithmeticError('positive global inertia not enclosed')
        action = bulk-(0.25/(2.0*module.HOPF_ORBIT_VOLUME**2))/inertia
        _, boundary = module._boundary(np.asarray(state, dtype=object), m,
                                       [np.asarray(v, dtype=object) for v in legs])
        value = (action+boundary).d[-1]
    if not isinstance(value, Taylor):
        value = domain.affine(value)
    return value, i0.enclosure().lower()
