"""Factored retained integrand at interval-valued physical HS states."""
from contextlib import contextmanager
import hashlib
import inspect
import math
from flint import arb, ctx
from bhsm.interface.factored_arb_integrand import (
    PARENT_INTEGRAND_SHA256, factored_local_algebra,
)
from bhsm.interface.physical_arb_inputs import preserve_ball, same_ball_vector


@contextmanager
def use_ball_factored_integrand(module,state):
    """Use one fixed-state cached local geometry; restore the parent on exit.

    Quadrature, maps, local affine values, boundary and global inertia reciprocal
    remain owned by the unchanged parent. This context is process-local and
    must be included explicitly in a consumer's source fingerprint.
    """
    original=module._integrand
    digest=hashlib.sha256(inspect.getsource(original).encode()).hexdigest().upper()
    if digest!=PARENT_INTEGRAND_SHA256:
        raise RuntimeError('parent integrand changed; explicit reconciliation required')
    precision=ctx.prec
    selected=tuple(preserve_ball(v) for v in state)
    cached=[original(selected,node,0) for node in range(module.POINTS)]
    constants=[]
    for node in range(module.POINTS):
        coordinate=float(module._BASIS[0][node])
        sigma=-0.5+2.0*coordinate/math.pi-math.sin(4.0*coordinate)/(2.0*math.pi)
        kappa0=15.0*5.0**(1.0/3.0)/4.0
        # Preserve exactly the floating constants in the original expression.
        constants.append(tuple(arb(float(v)) for v in (
            module.RADIUS0,module.RADIUS0*math.cos(coordinate),module.RADIUS0*math.sin(coordinate),
            3*math.cos(coordinate)**2,3*math.sin(coordinate)**2,0.5*kappa0,1.0-4.0*sigma**2)))

    def factored(state_values,node,directions,leg_values=None):
        if (ctx.prec!=precision or len(state_values)!=len(selected)
                or not same_ball_vector(state_values,selected)):
            raise RuntimeError('cached local geometry state or precision mismatch')
        base=cached[node]
        variables=module._local_variables(base.values,directions,leg_values)
        bulk,inertia=factored_local_algebra(variables,*constants[node],lambda x:x.exp())
        weight=float(module._BASIS[1][node])
        return module.LocalTerm(base.maps,base.values,weight*bulk,weight*inertia)

    module._integrand=factored
    try:
        yield
    finally:
        module._integrand=original
