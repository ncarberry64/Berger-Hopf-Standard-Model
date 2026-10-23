"""Literal common cap/Maxwell/Higgs action on general endpoint fields.

This is the same normalized action used by the retained mean descriptor,
now applied to an explicit incoming or child coefficient vector.  A zero
independent gauge starting field does not delete its Euler/Gauss rows.
The finite radial/angle representation and parameter scope remain explicit.
"""
from __future__ import annotations

import numpy as np

from .muon_moving_geometric_action import moving_cap_action_jet
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import (
    FIELD_ORDER, background_subtracted_maxwell_action_jet,
    full_maxwell_weak_geometric_jets, full_maxwell_gauge_hessian_matrix,
)
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet
from .muon_parent_retarded_hypercharge import WALL, regular_radial_basis
from .muon_parent_mean_causal_action import mean_coordinate_lift, VOLUME, MAXWELL_TO_CAP


def _vector(value, size, name):
    if value is None or not np.isrealobj(value):
        raise ValueError(f'explicit real {name} required')
    result = np.asarray(value, float)
    if result.shape != (size,) or not np.isfinite(result).all():
        raise ValueError(f'finite {name} of length{size} required')
    return result


def pointwise_full_field_action(raw_coefficients, representation, *,
                               nu_squared_action, surface_gamma=None):
    """Evaluate the common action and all its raw228 first/second derivatives.

    Raw order is q37/v37/m24/n/ndot, a60/adot60, H4/Hdot4.  The radial
    basis, wall trace, scalar normalization and cap Maxwell subtraction
    are inherited without choosing a covariance, initial gauge state,
    physical scale, normal mode or worldvolume interval.
    """
    raw = _vector(raw_coefficients, 228, 'common raw field coefficients')
    rep = representation
    if len(rep['gauge_labels']) != 60:
        raise ValueError('the retained all5 mean gauge representation is required')
    nu2 = float(nu_squared_action)
    if not np.isfinite(nu2) or nu2 < 0:
        raise ValueError('explicit nonnegative action-unit nu_squared required')
    if surface_gamma is not None:
        surface_gamma = float(surface_gamma)
        if not np.isfinite(surface_gamma) or surface_gamma <= 0:
            raise ValueError('an assigned surface coefficient must be positive')
    q, v, m = raw[:37], raw[37:74], raw[74:98]
    s, sr = raw[98:100]
    a, at = raw[100:160], raw[160:220]
    H, Ht = raw[220:224], raw[224:228]
    cap = moving_cap_action_jet(12, q, v, m, points=rep['cap_points'],
                              source_value=s, source_rate=sr)
    geo = geometric_connection_coefficient_jets(12, q, v, m, rep['rho'],
                                               source_value=s, source_rate=sr)
    gb, gr = rep['gauge_basis'], rep['gauge_radial_basis']
    count = len(gb)
    tv = np.zeros((count, 120, 1, 5, 4))
    tt, tr = tv.copy(), tv.copy()
    ta = np.zeros((count, 120, 1, 3, 5, 4))
    tv[:, :60] = gb
    tr[:, :60] = gr
    tt[:, 60:] = gb
    fields = dict(gauge=np.einsum('rj... ,j->r...', gb, a),
                  gauge_tau=np.einsum('rj... ,j->r...', gb, at),
                  gauge_rho=np.einsum('rj... ,j->r...', gr, a),
                  gauge_angular=np.zeros((count, 1, 3, 5, 4)))
    tests = dict(tests=tv, tests_tau=tt, tests_rho=tr, tests_angular=ta)
    delta = background_subtracted_maxwell_action_jet(
        geo, rep['radial_quadrature'], np.ones(1), **fields)
    weak = full_maxwell_weak_geometric_jets(
        geo, rep['radial_quadrature'], np.ones(1), **fields, **tests)
    gauge = full_maxwell_gauge_hessian_matrix(
        geo, rep['radial_quadrature'], np.ones(1), **fields, **tests)
    gradient = np.zeros(228)
    hessian = np.zeros((228, 228))
    value = cap['total'].value + MAXWELL_TO_CAP*delta['value']
    gradient[:100] = cap['total'].gradient + MAXWELL_TO_CAP*delta['gradient']
    hessian[:100, :100] = cap['total'].hessian + MAXWELL_TO_CAP*delta['hessian']
    gradient[100:220] = MAXWELL_TO_CAP*weak['weak']['values']
    hessian[100:220, 100:220] = MAXWELL_TO_CAP*gauge['matrix']
    cross = MAXWELL_TO_CAP*weak['weak']['geometric_jacobian']
    hessian[100:220, :100] = cross
    hessian[:100, 100:220] = cross.T
    metric = intrinsic_m4_weight_jet(12, q, v, m, source_value=s, source_rate=sr)
    wall_basis, _ = regular_radial_basis(np.array([WALL]), rep['radial_order'])
    trace = np.zeros((1, 5, 4, 60))
    for j, label in enumerate(rep['gauge_labels']):
        trace[0, FIELD_ORDER.index(label['field']), label['internal'], j] = wall_basis[0, label['radial']]
    scalar_value = np.zeros((1, 4, 8))
    scalar_derivative = np.zeros((1, 4, 4, 8))
    scalar_value[0, :, :4] = np.eye(4)
    scalar_derivative[0, 0, :, 4:] = np.eye(4)
    scalar = material_intrinsic_higgs_gauge_action_jet(
        metric, scalar_coefficients=np.r_[H, Ht], scalar_value_map=scalar_value,
        scalar_derivative_map=scalar_derivative, gauge_coefficients=a,
        gauge_trace_map=trace, angular_quadrature=np.ones(1),
        lambda_H=rep['scalar_matching']['lambda_H'], nu_squared_action=nu2)['action']
    lift_scalar = np.zeros((168, 228))
    lift_scalar[:100, :100] = np.eye(100)
    lift_scalar[100:108, 220:228] = np.eye(8)
    lift_scalar[108:168, 100:160] = np.eye(60)
    value += scalar.value/VOLUME**2
    gradient += lift_scalar.T@scalar.gradient/VOLUME**2
    hessian += lift_scalar.T@scalar.hessian@lift_scalar/VOLUME**2
    if surface_gamma is not None:
        surface = cap['surface_per_gamma']
        value += surface_gamma*surface.value
        gradient[:100] += surface_gamma*surface.gradient
        hessian[:100, :100] += surface_gamma*surface.hessian
    coordinates = mean_coordinate_lift(rep['gauge_labels'])
    P = coordinates['lift']
    G, HH = P.T@gradient, P.T@hessian@P
    return dict(value=float(value), raw_gradient=gradient, raw_hessian=hessian,
        gradient=G, hessian=HH, coordinates=coordinates,
        Lxx=HH[:90, :90], Lxv=HH[:90, 90:180], Lxy=HH[:90, 180:],
        Lvx=HH[90:180, :90], Lvv=HH[90:180, 90:180], Lvy=HH[90:180, 180:],
        Lyx=HH[180:, :90], Lyv=HH[180:, 90:180], Lyy=HH[180:, 180:],
        constraint_rows=G[180:], canonical_rows=G[90:180],
        raw_geometry_first_variation=gradient[:100],
        raw_gauge_value_cotangent=gradient[100:160],
        raw_gauge_rate_cotangent=gradient[160:220],
        raw_H_value_cotangent=gradient[220:224], raw_H_rate_cotangent=gradient[224:228],
        surface_value_per_gamma=float(cap['surface_per_gamma'].value),
        surface_gradient_per_gamma=cap['surface_per_gamma'].gradient,
        surface_hessian_per_gamma=cap['surface_per_gamma'].hessian,
        nu_squared_action=nu2, surface_gamma=surface_gamma,
        action_normalization=dict(cap=1., independent_Maxwell=MAXWELL_TO_CAP,
                                  intrinsic_Higgs=1/VOLUME**2),
        zero_independent_gauge_Euler_inferred=False,
        multiplier_and_At_Gauss_rows_retained=True,
        field_and_embedding_advection_count=1,
        radial_basis_is_representation_not_physical_boundary_choice=True,
        full_stationary_birth_or_native_Pauli_established=False)


def pointwise_wall_gauge_conormal(raw_coefficients, representation):
    """Evaluate the radial momentum ON the material wall, not its integral.

    The covector is oriented toward increasing rho (wall plus).  It is
    the same Maxwell action's natural face term, with its geometry100
    derivative.  The intrinsic M4 scalar has a separate temporal dual.
    No zero conormal boundary condition is imposed.
    """
    raw = _vector(raw_coefficients, 228, 'common raw field coefficients')
    rep = representation
    basis, derivative = regular_radial_basis(np.array([WALL]), rep['radial_order'])
    value_map = np.zeros((1, 60, 1, 5, 4))
    radial_map = np.zeros_like(value_map)
    for j, label in enumerate(rep['gauge_labels']):
        f, k = FIELD_ORDER.index(label['field']), label['internal']
        value_map[0, j, 0, f, k] = basis[0, label['radial']]
        radial_map[0, j, 0, f, k] = derivative[0, label['radial']]
    a, at = raw[100:160], raw[160:220]
    fields = dict(gauge=np.einsum('rj...,j->r...', value_map, a),
                  gauge_tau=np.einsum('rj...,j->r...', value_map, at),
                  gauge_rho=np.einsum('rj...,j->r...', radial_map, a),
                  gauge_angular=np.zeros((1, 1, 3, 5, 4)))
    geo = geometric_connection_coefficient_jets(12, raw[:37], raw[37:74], raw[74:98],
        np.array([WALL]), source_value=raw[98], source_rate=raw[99])
    weak = full_maxwell_weak_geometric_jets(geo, np.ones(1), np.ones(1),
        **fields, tests=value_map, tests_tau=np.zeros_like(value_map),
        tests_rho=radial_map, tests_angular=np.zeros((1, 60, 1, 3, 5, 4)))
    momentum = weak['radial_momentum_test']
    return dict(radial_action_covector=MAXWELL_TO_CAP*momentum['values'],
        geometry_derivative=MAXWELL_TO_CAP*momentum['geometric_jacobian'],
        orientation='increasing rho; material wall plus, not temporal Cauchy normal',
        face_location=WALL, radial_quadrature_reused_as_face=False,
        imposed_zero_flux=False, natural_wall_term_is_physical_ensemble=False)


def coefficient_time_euler_application(action, master_rate):
    """Apply actual Euler rows at supplied same-vector rates/accelerations.

    eta=(x,v,y), etadot=(v,acceleration,ydot).  The residual is
    L_x-d_t L_v, L_y; no zero acceleration or multiplier-rate assumption
    is inserted.  Boundary traces still require their paired action rows.
    """
    rate = _vector(master_rate, 216, 'master coefficient-time tangent')
    G, H = action['gradient'], action['hessian']
    canonical_rate = H[90:180]@rate
    residual = np.r_[G[:90]-canonical_rate, G[180:]]
    return dict(residual=residual, dynamic_euler=residual[:90],
                algebraic_constraint=residual[90:], canonical_rate=canonical_rate,
                physical_clock_conversion_inserted=False,
                acceleration_or_multiplier_rate_silently_zero=False)
