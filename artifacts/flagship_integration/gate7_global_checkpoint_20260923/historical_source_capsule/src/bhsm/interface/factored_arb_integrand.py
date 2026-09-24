"""Exact algebraic factorization of the retained local action integrand."""
from contextlib import contextmanager
import hashlib
import inspect
import math
from flint import arb,ctx

PARENT_INTEGRAND_SHA256='F832ADFAF8599FB591E5F5B91A1DA71F4CCE3F356CF3251386785050206C75F8'


def factored_local_algebra(z, radius, axis_a, axis_b, cosine_factor, sine_factor,
                           potential, localization, exponential):
    """Return unweighted bulk/inertia; operations also admit symbolic inputs.

    Constants are supplied explicitly. In particular, the original binary64
    products R*cos, R*sin, 3*cos^2, 3*sin^2 and .5*kappa are not recomputed at
    higher precision or replaced by trigonometric identities.
    """
    log_c,log_a,log_b,cp,ap,bp,lc,la,lb,log_n,npj,beta,beta_prime=z
    inverse_c=exponential(-2*log_c)/(radius*radius)
    inverse_a=exponential(-2*log_a)/(axis_a*axis_a)
    inverse_b=exponential(-2*log_b)/(axis_b*axis_b)
    inverse_n=exponential(-2*log_n)
    hc=lc-beta*cp-beta_prime;ha=la-beta*ap;hb=lb-beta*bp
    adm=-6*inverse_n*(ha**2+hb**2+hc*(ha+hb)+3*ha*hb)
    xeta=inverse_c+cosine_factor*inverse_a+sine_factor*inverse_b-beta**2*inverse_n
    fixed=ap**2+bp**2+3*ap*bp
    volume_prefactor=radius*axis_a**3*axis_b**3
    gravity=(3*axis_a**3*axis_b**3/radius)*exponential(-log_c+3*log_a+3*log_b+log_n)*(npj*(ap+bp)+fixed)
    algebraic=volume_prefactor*exponential(log_c+3*log_a+3*log_b+log_n)*(
        3*inverse_a+3*inverse_b-potential-localization*(xeta/2+xeta**4/8)+adm/2)
    inertia=volume_prefactor*exponential(log_c+3*log_a+3*log_b-log_n)*localization*(1+xeta**3)
    return gravity+algebraic,inertia


@contextmanager
def use_factored_integrand(module,state):
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
    selected=tuple(arb(float(v)) for v in state)
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
                or any(not arb(v)==s for v,s in zip(state_values,selected))):
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
