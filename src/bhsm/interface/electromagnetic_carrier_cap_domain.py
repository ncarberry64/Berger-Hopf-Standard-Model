"""Leading regular-cap coexact Maxwell radial tests, not a global domain.

The density proof and application are separate. This helper changes no old
radial basis, inherited source profile, Gauss coordinate or physical field.
Normalization is for the dimensionless leading kinetic weight x**4 dx.
"""
from __future__ import annotations

import numpy as np
from scipy.special import eval_jacobi, gammaln


def _positive_real(value, name):
    a = np.asarray(value)
    if a.shape != () or (np.iscomplexobj(a) and a.imag != 0):
        raise ValueError(name + ' must be a positive real scalar')
    x = float(a.real)
    if not np.isfinite(x) or x <= 0:
        raise ValueError(name + ' must be positive and finite')
    return x


def coexact_indicial_data(curl_squared):
    """Data for -(rho**4 a')'+lambda*rho**2 a=0, lambda>0.

    This is the leading fixed-time transverse spatial equation. Generic
    finite-form vectors need not have the homogeneous solution asymptotic.
    Longitudinal/Gauss rows and the coupled retarded domain are not selected.
    """
    lam = _positive_real(curl_squared, 'curl_squared')
    root = np.sqrt(9 + 4*lam)
    alpha = 2*lam/(3 + root)  # avoids cancellation for small positive lambda
    return dict(curl_squared=lam, alpha=alpha, negative_alpha=(-3-root)/2,
                weighted_L2_power=4, inverse_square_potential=lam+2,
                finite_energy_power_condition='a~rho**s: s>-3/2 for lambda>0',
                leading_spatial_limit_point=True,
                full_moving_strong_domain_or_native_operator_identified=False)


def coexact_radial_jacobi(rho, order, *, curl_squared, wall):
    """Normalized x**alpha(1-x) Jacobi interiors plus x**alpha wall lift.

    The interior family uses P_j**(2,4+2alpha)(2x-1). It is orthonormal
    under integral_0^1 x**4 B_i B_j dx. The independent final wall lift
    is not normalized or assigned a boundary value by this function.
    """
    if type(order) is not int or order < 1:
        raise ValueError('positive integer order required')
    length = _positive_real(wall, 'wall')
    rr = np.asarray(rho)
    if np.iscomplexobj(rr) and np.any(rr.imag != 0):
        raise ValueError('real regular-cap radial points required')
    rr = np.asarray(rr.real, dtype=float)
    if rr.ndim != 1 or not len(rr) or not np.isfinite(rr).all() or np.any(rr <= 0) or np.any(rr > length):
        raise ValueError('nonempty radial points in 0<rho<=wall required')
    alpha = coexact_indicial_data(curl_squared)['alpha']
    x = rr/length
    regular = x**alpha
    derivative = alpha*x**(alpha-1)/length
    values, firsts = [], []
    ja, jb = 2., 4+2*alpha
    for j in range(order):
        lognorm = (gammaln(j+ja+1)+gammaln(j+jb+1)-gammaln(j+1)
                   -gammaln(j+ja+jb+1)-np.log(2*j+ja+jb+1))
        scale = np.exp(-lognorm/2)
        p = scale*eval_jacobi(j, ja, jb, 2*x-1)
        dp = (scale*(j+ja+jb+1)/length*eval_jacobi(j-1, ja+1, jb+1, 2*x-1)
              if j else np.zeros_like(x))
        values.append(regular*(1-x)*p)
        firsts.append((derivative*(1-x)-regular/length)*p+regular*(1-x)*dp)
    values.append(regular)
    firsts.append(derivative)
    return np.column_stack(values), np.column_stack(firsts)
