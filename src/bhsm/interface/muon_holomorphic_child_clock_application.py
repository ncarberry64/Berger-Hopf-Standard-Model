"""Explicit inherited-clock derivative of the original complex child action.

The child raw coordinates stay fixed. Only the three inherited affine
connection germs move. Analytic action-dual placements are not conjugated.
This derivative supplies the canonical exterior tangent, not a pole residue.
"""
from __future__ import annotations
import numpy as np
from .muon_holomorphic_child_action import holomorphic_inherited_child_action, _affine_geometry
from .muon_holomorphic_normal_geometry import holomorphic_geometry_rows, holomorphic_cap_and_weights
from .muon_nonlinear_chronological_n0_action import analytic_constant_maxwell_batch
from .muon_nonlinear_n0_field_action import analytic_intrinsic_n0_jet
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP


def inherited_connection_clock_jet(initial_pair, reference_pair, coordinate_time, rho):
    """Value and exact first derivative along the recorded affine geometry."""
    values = []
    rates = []
    for raw in (np.asarray(initial_pair, complex)[0], *np.asarray(reference_pair, complex)):
        shifted = _affine_geometry(raw, complex(coordinate_time))
        velocity = np.zeros(100, complex)
        velocity[:37] = raw[37:74]
        velocity[98] = raw[99]
        rows = holomorphic_geometry_rows(shifted[:100], rho, connection_only=True)['rows']
        keys = ('connection_lambda', 'lambda_tau', 'lambda_rho')
        values.append(np.array([[row[key].value for key in keys] for row in rows]))
        rates.append(np.array([[row[key].gradient @ velocity for key in keys] for row in rows]))
    return values[0]-values[1]+values[2], rates[0]-rates[1]+rates[2]


def holomorphic_child_explicit_clock_application(raw_child, coordinate_time, initial_pair,
                                                 reference_pair, representation, *,
                                                 nu_squared_action, surface_gamma=None):
    """Compute partial_t L and partial_t grad L at fixed child x/v/y.

    The geometry rows include density, shift, metric, normal and measure
    contacts. The mechanical baseline and cap have no explicit inherited
    clock dependence at fixed child raw fields. Their internal derivatives
    remain in the returned original action and canonical tangent matrix.
    """
    raw = np.asarray(raw_child, complex)
    rep = representation
    action = holomorphic_inherited_child_action(raw, coordinate_time, initial_pair, reference_pair,
        rep, nu_squared_action=nu_squared_action, surface_gamma=surface_gamma)
    ng = rep['gauge_count']
    hs = 100+2*ng
    nr = hs+8
    geo = holomorphic_geometry_rows(raw[:100], rep['rho'])
    cap = holomorphic_cap_and_weights(raw[:100], points=rep['cap_points'])
    eff, eff_t = inherited_connection_clock_jet(initial_pair, reference_pair, coordinate_time, rep['rho'])
    wall_eff, wall_t = inherited_connection_clock_jet(initial_pair, reference_pair, coordinate_time, [WALL])
    gb = np.asarray(rep['gauge_basis'])[:, :, 0].reshape(len(eff), ng, 20)
    gr = np.asarray(rep['gauge_radial_basis'])[:, :, 0].reshape(len(eff), ng, 20)
    A = np.einsum('rjc,j->rc', gb, raw[100:100+ng]).reshape(-1, 5, 4)
    At = np.einsum('rjc,j->rc', gb, raw[100+ng:hs]).reshape(-1, 5, 4)
    Ar = np.einsum('rjc,j->rc', gr, raw[100:100+ng]).reshape(-1, 5, 4)
    A[:, 2:] += M[None]*(eff[:, 0]-1)[:, None, None]
    At[:, 2:] += M[None]*eff[:, 1, None, None]
    Ar[:, 2:] += M[None]*eff[:, 2, None, None]
    connection_rate = np.zeros((len(eff), 3, 5, 4), complex)
    connection_rate[:, :, 2:] = eff_t[:, :, None, None]*M[None, None]
    connection_rate = connection_rate.reshape(len(eff), 60)
    density_keys = ('electric', 'radial', 'angular', 'electric_radial', 'shift')
    densities = np.array([[row[key].value for key in density_keys] for row in geo['rows']])
    local = analytic_constant_maxwell_batch(A, At, Ar, densities)
    maps = np.zeros((len(eff), 60, 2*ng))
    maps[:, :20, :ng] = gb.transpose(0, 2, 1)
    maps[:, 20:40, ng:] = gb.transpose(0, 2, 1)
    maps[:, 40:, :ng] = gr.transpose(0, 2, 1)
    # Exact polarizations: affine in the first four densities, quadratic
    # in shift. These step-one differences have no Taylor truncation.
    dgdc = np.empty((len(eff), 60, 5), complex)
    for k in range(4):
        unit = np.zeros_like(densities)
        unit[:, k] = 1
        unit[:, 4] = densities[:, 4]
        dgdc[:, :, k] = analytic_constant_maxwell_batch(A, At, Ar, unit)['gradient']
    plus, minus = densities.copy(), densities.copy()
    plus[:, 4] += 1
    minus[:, 4] -= 1
    dgdc[:, :, 4] = (analytic_constant_maxwell_batch(A, At, Ar, plus)['gradient']-
        analytic_constant_maxwell_batch(A, At, Ar, minus)['gradient'])/2
    raw_clock = np.zeros(nr, complex)
    value_clock = 0j
    for j, (row, weight) in enumerate(zip(geo['rows'], rep['radial_quadrature'])):
        factor = MAXWELL_TO_CAP*weight
        rate = connection_rate[j]
        value_clock += factor*(local['gradient'][j] @ rate)
        raw_clock[100:hs] += factor*maps[j].T @ local['hessian'][j] @ rate
        density_first = np.array([row[key].gradient for key in density_keys])
        raw_clock[:100] += factor*density_first.T @ dgdc[j].T @ rate
    wall = np.einsum('fcj,j->fc', rep['wall_trace_map'], raw[100:100+ng])
    wall[2:] += M*(wall_eff[0, 0]-1)
    wall_rate = np.zeros(28, complex)
    wall_rate[4:24] = np.vstack((np.zeros((2, 4)), M*wall_t[0, 0])).reshape(20)
    weights = [cap[key] for key in ('wT', 'wS', 'wV')]
    wv = np.array([weight.value for weight in weights])
    scalar_args = dict(lambda_H=rep['scalar_matching']['lambda_H'], nu_squared_action=nu_squared_action)
    scalar = analytic_intrinsic_n0_jet(wall, raw[hs:hs+4], raw[hs+4:], wv, **scalar_args)
    S = np.zeros((28, nr-100))
    S[:4, 2*ng:2*ng+4] = np.eye(4)
    S[4:24, :ng] = rep['wall_trace_map'].reshape(20, ng)
    S[24:, 2*ng+4:] = np.eye(4)
    value_clock += scalar['gradient'] @ wall_rate
    raw_clock[100:] += S.T @ scalar['hessian'] @ wall_rate
    for j, weight in enumerate(weights):
        part = analytic_intrinsic_n0_jet(wall, raw[hs:hs+4], raw[hs+4:], np.eye(3)[j], **scalar_args)
        raw_clock[:100] += weight.gradient*(part['gradient'] @ wall_rate)
    P = action['coordinates']['lift']
    clock = P.T @ raw_clock
    n = action['coordinates']['x_count']
    v = (P.T @ raw)[n:2*n]
    rhs = np.r_[action['gradient'][:n]-action['Lvx'] @ v-clock[n:2*n],
                -action['Lyx'] @ v-clock[2*n:]]
    return dict(action=action, value_clock_first=value_clock, raw_gradient_clock_first=raw_clock,
        gradient_clock_first=clock, effective_connection_clock_first=eff_t,
        effective_wall_connection_clock_first=wall_t, canonical_tangent_rhs=rhs,
        canonical_tangent_operator=action['hessian'][n:, n:],
        explicit_clock_cap_and_child_baseline_first=0j,
        zero_provenance='cap and subtracted child mechanical baseline depend only on held child raw fields',
        analytic_dual_conjugated=False, canonical_compatibility_established=False)
