"""Retained E1+ geometry and candidate material-wall area variations.

The evaluated coefficients belong to the existing minimal area action.
They do not select a formation eigenmode, sum membrane actions across
strata, or establish a full stationary classical/KKT base.  The M8 wall
and its M5 quotient have different unweighted area measures; the moving
fiber measure is required when transporting the former action downward.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path

import numpy as np

from .aether_diagonal_sp1_m4_attachment_v15_50 import diagonal_quotient_geometry
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from .covariant_bubble_interface_mechanics import ACTION_VERSION, interface_stiffness


ROOT = Path(__file__).resolve().parents[3]
RESET_RECEIPT = 'artifacts/muon_birth_transfer_value_20261008/retained_reset/run_1/result.json'
STATE_SOURCE = 'artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz'


def _vector(value, length, name):
    array = np.asarray(value, dtype=float)
    if array.shape != (length,) or not np.all(np.isfinite(array)):
        raise ValueError(f'{name} must be a finite vector of length {length}')
    return array


def wall_geometry_snapshot(q, velocity, lapse_shift, *, order=12):
    """Evaluate exact endpoint basis formulas at the fixed chi=pi/4 wall.

    u and lapse use k=1..N, whereas w,v and shift use j=0..N-1.
    Endpoint parity zeros are analytic zeros, not sin(pi) rounding tests.
    Time derivatives are the supplied retained coordinate velocities.
    """
    if type(order) is not int or order < 1:
        raise ValueError('positive integer order required')
    q = _vector(q, 1 + 3*order, 'q')
    velocity = _vector(velocity, 1 + 3*order, 'velocity')
    lapse_shift = _vector(lapse_shift, 2*order, 'lapse_shift')
    k = np.arange(1, order + 1, dtype=float)
    j = np.arange(order, dtype=float)
    signs_k, signs_j = (-1.0)**k, (-1.0)**j
    u_coeff, w_coeff, v_coeff = np.split(q[1:], 3)
    u_rate, w_rate, v_rate = np.split(velocity[1:], 3)
    n_coeff, b_coeff = np.split(lapse_shift, 2)
    u, w, v = (float(x @ signs) for x, signs in
               ((u_coeff, signs_k), (w_coeff, signs_j), (v_coeff, signs_j)))
    # d2[sin(2chi)^2 cos(4jchi)] at chi=pi/4.
    window_second = -(8.0 + 16.0*j*j)*signs_j
    u_second = float(u_coeff @ (-(4.0*k)**2*signs_k))
    w_second = float(w_coeff @ window_second)
    v_second = float(v_coeff @ window_second)
    n_second = float(n_coeff @ (-(4.0*k)**2*signs_k))
    beta_first = float(-4.0*b_coeff @ signs_j)
    log_n = float(n_coeff @ signs_k)
    radius = RADIUS0*math.exp(float(q[0]))
    C = radius*math.exp(u + w)
    A = radius*math.exp(u + v)/math.sqrt(2.0)
    B = radius*math.exp(u - v)/math.sqrt(2.0)
    N = math.exp(log_n)
    quotient = diagonal_quotient_geometry(A, B)
    log_c_rate = float(velocity[0] + u_rate @ signs_k + w_rate @ signs_j)
    log_a_rate = float(velocity[0] + u_rate @ signs_k + v_rate @ signs_j)
    log_b_rate = float(velocity[0] + u_rate @ signs_k - v_rate @ signs_j)
    Hc = (log_c_rate - beta_first)/N
    lam = quotient['lambda']
    # log R4 and log L_F derivatives from the actual square completion.
    r_first = 2.0*lam - 1.0
    r_second = u_second + (1.0 - 2.0*lam)*v_second - 2.0 - 8.0*lam*(1.0 - lam)
    fiber_first = 1.0 - 2.0*lam
    fiber_second = u_second + (2.0*lam - 1.0)*v_second - 2.0 + 8.0*lam*(1.0 - lam)
    result = dict(
        chi_star=math.pi/4, C=C, A=A, B=B, N=N,
        R4=quotient['M4_spatial_radius'], fiber_radius=quotient['fiber_radius'],
        lambda_geom=lam, endpoint_profiles=dict(u=u, w=w, v=v, log_N=log_n),
        endpoint_basis=dict(u_lapse_indices=[1, order], w_v_shift_indices=[0, order-1]),
        chi_first_log=dict(C=0.0, A=-1.0, B=1.0, N=0.0, R4=r_first, fiber=fiber_first),
        chi_second_log=dict(C=u_second+w_second, A=u_second+v_second-2.0,
                            B=u_second-v_second-2.0, N=n_second,
                            R4=r_second, fiber=fiber_second),
        shift=dict(beta=0.0, beta_chi=beta_first),
        coordinate_time_log_rates=dict(C=log_c_rate, A=log_a_rate, B=log_b_rate),
        Hc=Hc,
        unit_wall_normal='n=C_star^(-1) partial_chi at beta_star=0',
        unit_normal_trace_per_amplitude=[0.0, -1.0/C, 1.0/C],
        fixed_eta_wall_levelset_derivative_per_amplitude=4.0/(math.pi*C),
        fixed_chart_state_levelset_derivative=0.0,
    )
    scalars = [C, A, B, N, Hc, r_second, fiber_second]
    if not all(math.isfinite(x) for x in scalars) or min(C, A, B, N) <= 0:
        raise ValueError('finite positive reconstructed metric required')
    return result


def candidate_surface_normal_form(geometry, *, stratum):
    """Return the area-action quadratic form, keeping its time/contact terms.

    The normal amplitude a is unselected.  For chi(t,y;s)=pi/4+s*a/C_star,
    S''/gamma = integral d_tau dmu_spatial [(D_tau a-Hc*a)^2
    - |grad a|^2 - V_graph*a^2].  The finite local V_graph includes K^2
    at a nonminimal wall.  It is not the full restoring Jacobi operator
    obtained after time integration by parts or bulk elimination.
    """
    if stratum not in ('M8', 'M5'):
        raise ValueError('only the supplied M8 wall or its M5 quotient is available')
    C, A, B, N = (float(geometry[name]) for name in ('C', 'A', 'B', 'N'))
    if not all(math.isfinite(x) and x > 0 for x in (C, A, B, N)):
        raise ValueError('finite positive metric required')
    second = geometry['chi_second_log']
    if stratum == 'M8':
        spatial_density = A**3*B**3
        log_first = 0.0
        log_second = second['N'] + 3.0*second['A'] + 3.0*second['B']
        gradient = dict(unit_S3_A=1.0/A**2, unit_S3_B=1.0/B**2)
        worldvolume_dimension = 7
    else:
        r = float(geometry['R4'])
        spatial_density = r**3
        log_first = 3.0*geometry['chi_first_log']['R4']
        log_second = second['N'] + 3.0*second['R4']
        gradient = dict(unit_S3_quotient=1.0/r**2)
        worldvolume_dimension = 4
    density = N*spatial_density
    K = log_first/C
    V = (log_second + log_first**2)/C**2
    return dict(
        owner_action_version=ACTION_VERSION, stratum=stratum,
        surface_action='-gamma integral_W dmu_h',
        gamma_formula=f'alpha_FSC*ell_s^(-{worldvolume_dimension})',
        worldvolume_dimension=worldvolume_dimension,
        coordinate_time_area_density_per_unit_angular_measure=density,
        proper_time_spatial_density_per_unit_angular_measure=spatial_density,
        mean_curvature=K,
        first_action_density_per_gamma_per_normal_amplitude=-density*K,
        second_action_embedding_path_contact_per_gamma_per_chi_second=-density*log_first,
        nonlinear_path_rule='Add -gamma*rho*(partial_chi log rho)*chi_wall,ss to S_ss if the owned level-set path has nonzero second embedding derivative',
        second_normal_form=dict(
            measure='d_tau times the stratum spatial metric measure',
            per_gamma='(D_tau a-Hc*a)^2-grad_squared-V_graph*a^2',
            normal_time_connection=float(geometry['Hc']),
            gradient_coefficients=gradient, V_graph=V,
            mean_curvature_squared=K*K,
            normal_area_measure_log_contact=log_second/C**2,
            weak_action_hessian='(D_tau-Hc)^dagger(D_tau-Hc)+Delta_spatial-V_graph in the displayed proper-time/spatial pairing',
            time_integration_by_parts_requires='D_tau Hc and D_tau log(spatial_density), or use the displayed factorized weak form',
        ),
        surface_inertia_density_per_gamma=spatial_density,
        normal_amplitude_selected=False, gamma_value=None,
        full_inertia_normalization=None, full_bulk_impedance=None,
        full_classical_stationary_base=False,
        error_scope='Evaluated binary64 geometry coefficients of the exact candidate area-variation law; no rounding, continuum or physical-mode enclosure',
    )


def supplied_surface_stiffness(alpha_fsc, scale_length, *, stratum):
    """Existing owner's stiffness law with explicitly supplied inputs only."""
    if stratum not in ('M8', 'M5'):
        raise ValueError('M8 or M5 required')
    return interface_stiffness(alpha_fsc, scale_length, 7 if stratum == 'M8' else 4)


def evaluate_retained_candidate_geometry(repository: Path | str = ROOT):
    """Consume the immutable E1+ receipt and original state; run no old producer."""
    repository = Path(repository)
    receipt_path = repository/RESET_RECEIPT
    receipt = json.loads(receipt_path.read_text(encoding='utf8'))
    state_path = repository/STATE_SOURCE
    identity = next(row for row in receipt['input_identities'] if row['path'] == STATE_SOURCE)
    if sha256(state_path.read_bytes()).hexdigest() != identity['sha256']:
        raise ValueError('retained state hash disagrees with reset receipt')
    if (receipt['state_binding']['outgoing_C2']['selected_branch'] != 24
            or receipt['state_binding']['outgoing_C2']['source_indices_zero_based'] != [0, 98]
            or receipt['state_binding']['one_common_event'] is not True):
        raise ValueError('E1+ outgoing C2 state binding required')
    values = receipt['retained_state_values']['Phi_mu_plus_geometry']
    state = np.array([float.fromhex(x) for x in values['binary64_hex']])
    with np.load(state_path, allow_pickle=False) as data:
        original = np.asarray(data['state'][:98])
    if state.shape != (98,) or not np.array_equal(state.view(np.uint64), original.view(np.uint64)):
        raise ValueError('receipt geometry is not the original bit-exact E1+ state')
    geometry = wall_geometry_snapshot(state[:37], state[37:74], state[74:], order=12)
    groups = receipt['residual_groups']
    return deepcopy(dict(
        classification='EVALUATED_RETAINED_E1_PLUS_CANDIDATE_WALL_GEOMETRY_AND_AREA_ACTION',
        source=dict(receipt_path=RESET_RECEIPT, receipt_sha256=sha256(receipt_path.read_bytes()).hexdigest(),
                    state_path=STATE_SOURCE, state_sha256=identity['sha256'],
                    branch=24, event='COMMON_P_TO_MU_BIRTH_E1',
                    state_slice_zero_based=[0, 98]),
        geometry=geometry,
        separate_surface_contributions={name:candidate_surface_normal_form(geometry, stratum=name)
                                        for name in ('M8', 'M5')},
        moving_fiber_pullback=dict(
            equation='N*A^3*B^3=(N*R4^3)*L_F^3 in compatible unit angular measures',
            log_fiber_cubic_first=3.0*geometry['chi_first_log']['fiber'],
            log_fiber_cubic_second=3.0*geometry['chi_second_log']['fiber'],
            unweighted_M5_membrane_is_M8_membrane=False,
            sum_across_strata_performed=False),
        retained_geometric_base_residual=dict(
            multiplier_constraints=groups['child_multiplier_constraints'],
            canonical_energy_constraint=groups['child_canonical_energy_constraint'],
            scope='Existing retained reduced-action multiplier and canonical-energy rows only',
            full_classical_L_eta=None, full_classical_stationarity_established=False),
        pairing_domain=dict(
            pairing='Proper-time stratum spatial metric measure for the real normal amplitude',
            spatial_domains=dict(M8='S3_A times S3_B', M5='diagonal Sp1 quotient S3_R4'),
            temporal_domain='Inherited regular material wall; weak-form temporal endpoint terms retained by the caller',
            normal='Spacelike material-wall normal at E1+, not the temporal E1 Cauchy normal',
            intrinsic_M4_interface_embedding=None,
            actual_active_strata=None, complete_normal_section=None),
        physical_source=dict(psi_mu_plus=None, xi_psi=None, b_psi=None,
                             full_inertia_normalization=None, full_KKT_base=None),
        execution=dict(old_action_producer_calls=0, numerical_roots_or_histories=0),
    ))
