"""Exact fixed-zero-independent-gauge restriction of the assigned action.

The cap already contains the mechanical connection. Therefore the extra
Maxwell geometry action is S(Abar(q)+a)-S(Abar(q)); at fixed a=0 its value
and all geometry derivatives vanish identically. This reduction says
nothing about gauge Euler, gauge Hessian or geometry/gauge mixed rows.
They must still be obtained from the full Maxwell action.
"""
from __future__ import annotations

import numpy as np

from .muon_moving_geometric_action import moving_cap_action_jet
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet


def _require_zero_independent_gauge(fields, wall_gauge):
    """Check every independent one-form component and its retained jets."""
    for key in ('gauge', 'gauge_tau', 'gauge_rho', 'gauge_angular'):
        a = np.asarray(fields[key])
        if not np.isfinite(a).all() or np.any(a != 0):
            raise ValueError('the exact fixed-a=0 restriction requires zero '+key)
    wall = np.asarray(wall_gauge, float)
    if wall.shape != (5, 4) or not np.isfinite(wall).all() or np.any(wall != 0):
        raise ValueError('the same zero independent wall one-form trace is required')


def zero_gauge_geometry_action(q, qdot, m, *, rho, radial_quadrature, fields,
        H_real, H_rate, wall_gauge, lambda_H, nu_squared_action=None,
        surface_gamma=None, normal=0., normal_rate=0., cap_points=48):
    """Apply cap plus material Higgs at the exact fixed-a=0 restriction.

    The arguments retain the existing assigned-action interface. Radial
    quadrature describes the cancelled independent sector and is checked,
    not used to redefine the cap or intrinsic action measure. Higgs fields
    and rates remain solver coordinates, including their nonzero spatial
    mechanical covariant derivative. No physical field or mode is chosen.
    """
    _require_zero_independent_gauge(fields, wall_gauge)
    rho = np.asarray(rho, float); radial_quadrature = np.asarray(radial_quadrature, float)
    if rho.ndim != 1 or radial_quadrature.shape != rho.shape or not np.isfinite(rho).all() or not np.isfinite(radial_quadrature).all():
        raise ValueError('finite retained radial quadrature required')
    H = np.asarray(H_real, float); rate = np.asarray(H_rate, float)
    if H.shape != (4,) or rate.shape != (4,) or not np.isfinite(H).all() or not np.isfinite(rate).all():
        raise ValueError('finite realified Higgs doublet and coordinate-time rate required')
    cap = moving_cap_action_jet(12, q, qdot, m, points=cap_points,
        source_value=normal, source_rate=normal_rate)
    weights = intrinsic_m4_weight_jet(12, q, qdot, m,
        source_value=normal, source_rate=normal_rate)
    # Exact restriction of the owned material Higgs polynomial, not a
    # substitute background. j_i=-i sigma_i, sum j_i^dagger j_i=3 I2.
    # At_ref=0 and H has no ordinary angular derivative in this finite
    # component, but DiH=(lambda-1)j_i H remains nonzero.
    nu = 0.
    if nu_squared_action is not None:
        if not np.isfinite(nu_squared_action) or nu_squared_action < 0:
            raise ValueError('an explicit nonnegative action-unit nu squared is required')
        nu = float(nu_squared_action)
    wt = weights['wT']; K = 3*weights['wS']*(weights['mechanical_connection_lambda']-1)**2
    V = float(lambda_H)*weights['wV']; gap = float(H@H)-nu
    normalization = 1/(2*np.pi**2)
    h = normalization*(wt*float(rate@rate)-K*float(H@H)-V*gap**2)
    scalar_gradient = normalization*np.r_[-2*K.value*H-4*V.value*gap*H, 2*wt.value*rate]
    scalar_hessian = np.zeros((8, 8))
    scalar_hessian[:4, :4] = normalization*(-2*K.value*np.eye(4)-4*V.value*(gap*np.eye(4)+2*np.outer(H,H)))
    scalar_hessian[4:, 4:] = 2*normalization*wt.value*np.eye(4)
    geometry_scalar = normalization*np.column_stack((
        -2*K.gradient[:,None]*H-4*V.gradient[:,None]*gap*H,
        2*wt.gradient[:,None]*rate))
    sectors = dict(
        cap=dict(value=cap['total'].value, gradient=cap['total'].gradient, hessian=cap['total'].hessian),
        independent_Maxwell=dict(value=0., gradient=np.zeros(100), hessian=np.zeros((100, 100))),
        Higgs_assigned=dict(value=h.value, gradient=h.gradient[:100], hessian=h.hessian[:100, :100]))
    if surface_gamma is not None:
        if not np.isfinite(surface_gamma):
            raise ValueError('finite explicitly assigned area coefficient required')
        a = cap['surface_per_gamma']
        sectors['surface_assigned'] = dict(value=surface_gamma*a.value,
            gradient=surface_gamma*a.gradient, hessian=surface_gamma*a.hessian)
    value = sum(s['value'] for s in sectors.values())
    gradient = sum((s['gradient'] for s in sectors.values()), np.zeros(100))
    hessian = sum((s['hessian'] for s in sectors.values()), np.zeros((100, 100)))
    return dict(value=float(value), gradient=gradient, hessian=hessian,
        multiplier_constraints=gradient[74:98], constraint_jacobian=hessian[74:98], sectors=sectors,
        surface_gradient_per_gamma=cap['surface_per_gamma'].gradient,
        surface_hessian_per_gamma=cap['surface_per_gamma'].hessian,
        cap_energy=float(np.asarray(qdot)@cap['total'].gradient[37:74]+normal_rate*cap['total'].gradient[99]-cap['total'].value),
        scalar_real_canonical_dual=scalar_gradient[4:],
        scalar_coefficient_gradient=scalar_gradient,
        scalar_coefficient_hessian=scalar_hessian,
        geometry_scalar_hessian=geometry_scalar,
        independent_Maxwell_geometry_restriction='S(Abar+a)-S(Abar) at fixed a=0: exact zero',
        gauge_Euler_or_Hessian_zero_claim=False,
        physical_Pauli_contraction=False, stationary_E1_claim=False)
