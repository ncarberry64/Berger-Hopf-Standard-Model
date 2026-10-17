"""Pull actual current N12 physical modes through the child coefficient history.

This consumes the cached action-owned graph Jacobians.  It does not evaluate
another orbit or borrow the historical incoming Q66 frame.  Clock quadrature
includes the moving last arc node and the zero total density jet at first hit.
Boundary Weyl derivatives and the known minus-zeta action component are kept
distinct; no complete six-sector quantum force is asserted.
"""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.linalg import null_space
from scipy.sparse.linalg import expm_multiply

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bhsm.interface.aether_forward_c2_geometry_incidence import boundary_geometry_action_covectors
from bhsm.interface.aether_cancelled_arc_proper_time_pullback import pullback_cancelled_arc_history_to_proper_time
from bhsm.interface.aether_forward_c2_signed_coefficient_adjoint import signed_coefficient_history_adjoint
from bhsm.interface.aether_forward_c2_weyl_riccati import finite_core_weyl_and_coefficient_cotangent
from bhsm.interface.ae4_current_c2_affine72_gauge_calderon_first_jet import affine72_gauge_brst_first_jet
from bhsm.interface.ae4_current_c2_affine72_particle_fiber_calderon import product_dirac_friedrichs_weyl_first_jet
from bhsm.interface.forward_finite_endpoint_heat_force import piecewise_linear_zeta_coefficient_cotangent
from bhsm.interface.finite_core_heat_coefficient_force import finite_core_heat_coefficient_cotangent

DEFAULT_MODES = ROOT / "artifacts/current_runtime/current_physical_mode_response"
DEFAULT_OUT = ROOT / "artifacts/current_runtime/current_child_parent_backreaction"


def _json(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json(item) for item in value]
    return value


def _relative(left, right):
    return float(np.linalg.norm(left-right) / max(np.linalg.norm(left), np.linalg.norm(right), np.finfo(float).tiny))


def _clock_covectors(states, rates, jacobians, weights, lapse, lapse_covectors):
    """Differentiate N*(c.f_q)/(c.c), c=W_q v, on the physical graph."""
    c = states[:, 37:74] * weights[:37]
    square = np.einsum("ni,ni->n", c, c)
    if np.any(square <= 0):
        raise ArithmeticError("configuration-velocity clock chart degenerates")
    alpha = np.einsum("ni,ni->n", c, rates[:, :37]) / square
    derivative = np.einsum("ni,nij->nj", c, jacobians[:, :37]) / square[:, None]
    derivative[:, 37:74] += (
        (rates[:, :37] - 2*alpha[:, None]*c) / square[:, None]
        * (weights[:37]/weights[37:74])[None, :]
    )
    density = np.exp(lapse) * alpha
    covectors = np.exp(lapse)[:, None] * (derivative + alpha[:, None]*lapse_covectors)
    return density, covectors, alpha, square


def coefficient_cotangent_parent_pullback(arrays, node_cotangent, duration_cotangent):
    """Reverse the same 99-variable state/clock graph used by forward jets.

    The clock coordinate is physical proper time, not an extra action mode.
    Segment durations T*du have their complete derivative at terminal T;
    therefore the signed-adjoint API's local duration slot is algebraically
    zero and its nonlocal duration contribution is carried by the terminal
    clock covector.  This drops no duration jet.
    """
    gx, gh = np.asarray(node_cotangent), np.asarray(duration_cotangent)
    r = arrays["radius_action_covectors"].copy()
    rho, beta, u = (arrays[key] for key in ("proper_time_density", "radius_proper_rate", "normalized_proper_times"))
    node_covectors = np.zeros((len(r), 99))
    node_covectors[:, :98] = r
    node_covectors[1:-1, 98] = -beta[1:-1]
    n, f, crossing = (arrays[key] for key in ("terminal_descriptor_action_covector", "terminal_flow_action", "terminal_descriptor_flow_derivative"))
    node_covectors[-1, :98] = r[-1] - float(r[-1] @ f)*n/float(crossing)
    terminal_clock = float(gh @ np.diff(u) + np.sum(gx[1:-1]*beta[1:-1]*u[1:-1]))
    terminal = np.zeros(99)
    terminal[98] = terminal_clock
    adjoint = signed_coefficient_history_adjoint(
        transition_jacobians_action=arrays["state_clock_transition_jacobians"],
        node_log_radius_covectors_action_dual=node_covectors,
        segment_duration_covectors_action_dual=np.zeros((len(r)-1, 99)),
        D_log_radius_functional=gx,
        D_proper_duration_functional=np.zeros(len(r)-1),
        terminal_state_covector_action_dual=terminal,
    )
    forward = gx @ arrays["log_radius_first_jet"] + gh @ arrays["proper_durations_first_jet"]
    initial = np.asarray(adjoint["initial_state_covector_action_dual"])
    reverse = arrays["state_action_first_jet"][0].T @ initial[:98]
    physical = arrays["state_action_first_jet"][0] @ reverse
    return dict(forward=forward, reverse=reverse,
                action_dual=physical, raw_dual=arrays["state_weights"]*physical,
                unrestricted_initial_action_dual=initial[:98],
                adjoint_node_covectors=adjoint["adjoint_node_covectors_action_dual"],
                duality_relative_residual=_relative(forward, reverse),
                duality_absolute_residual=float(np.linalg.norm(forward-reverse)))


def _perturbed_coefficients(arrays, direction, epsilon):
    """Actual cached-J linearized family with moved hit node, nonlinear geometry."""
    U = np.einsum("nij,j->ni", arrays["state_action_first_jet"], direction)
    shifted = arrays["states"] + epsilon*U/arrays["state_weights"]
    flow = arrays["action_rates"] + epsilon*np.einsum("nij,nj->ni", arrays["graph_Jacobian_action"], U)
    arc = arrays["action_lengths"].copy()
    shift = float(arrays["terminal_arc_first_jet"] @ direction)
    arc[-1] += epsilon*shift
    shifted[-1] += epsilon*arrays["terminal_flow_action"]*shift/arrays["state_weights"]
    x, lapse = [], []
    for state in shifted:
        geometry = boundary_geometry_action_covectors(state=state, weights=arrays["state_weights"])
        x.append(geometry["log_R4"]); lapse.append(geometry["log_lapse"])
    x, lapse = np.asarray(x), np.asarray(lapse)
    # Fixed-arc terminal clock differential is checked separately.  The actual
    # moved endpoint has s=0 and hence density=0 with zero total first jet.
    c = shifted[:, 37:74]*arrays["state_weights"][:37]
    rho = np.exp(lapse)*np.einsum("ni,ni->n", c, flow[:, :37])/np.einsum("ni,ni->n", c, c)
    rho[-1] = 0.0
    h_arc = np.diff(arc)
    # The retained birth descriptor is ~1.8e-20.  Generic 73-direction
    # perturbations therefore cross its one-sided domain even at tiny steps.
    # This numerical replay is the signed local extension of the same clock
    # functional, not a claim of a two-sided physical birth family.  Interior
    # densities and all sampled segment integrals must still remain positive.
    if np.any(h_arc <= 0) or np.any(rho[1:-1] <= 0):
        raise ArithmeticError("perturbation leaves the interior sampled clock chart")
    proper = np.r_[0, np.cumsum(.5*h_arc*(rho[:-1]+rho[1:]))]
    if np.any(np.diff(proper) <= 0):
        raise ArithmeticError("perturbed sampled proper clock loses monotonicity")
    duration = proper[-1]
    target = arrays["normalized_proper_times"]*duration
    sampled_arc = np.empty_like(arc)
    sampled_arc[0], sampled_arc[-1] = arc[0], arc[-1]
    for node in range(1, len(arc)-1):
        segment = min(np.searchsorted(proper, target[node], side="right")-1, len(arc)-2)
        delta = target[node]-proper[segment]
        slope = (rho[segment+1]-rho[segment])/h_arc[segment]
        root = np.sqrt(max(0.0, rho[segment]**2+2*slope*delta))
        offset = 2*delta/(rho[segment]+root)
        sampled_arc[node] = arc[segment]+offset
    fixed_u_radius = CubicSpline(arc, x)(sampled_arc)
    return rho, float(duration), fixed_u_radius


def _finite_difference_replay(arrays, zeta_gradient):
    count = arrays["log_radius_first_jet"].shape[1]
    dense = np.cos(np.arange(1, count+1, dtype=float)); dense /= np.linalg.norm(dense)
    probes = [("largest_gain_mode", np.eye(count)[0]), ("smallest_gain_mode", np.eye(count)[-1]),
              ("deterministic_dense", dense), ("current72_birth_slice_direction", arrays["birth_slice_Q72"][:, 0])]
    records = []
    for name, direction in probes:
        da = abs(float(arrays["terminal_arc_first_jet"] @ direction))
        eps = min(1e-5, 1e-3*np.diff(arrays["action_lengths"])[-1]/max(da, 1.0))
        clock_first = abs(arrays["density_first_jet"][1:-1] @ direction)
        clock_nonzero = clock_first > 0
        if np.any(clock_nonzero):
            eps = min(eps, float(np.min(1e-3*arrays["proper_time_density"][1:-1][clock_nonzero]/clock_first[clock_nonzero])))
        expected_T = float(arrays["proper_duration_first_jet"] @ direction)
        expected_x = arrays["log_radius_first_jet"] @ direction
        expected_zeta = float(zeta_gradient @ direction)
        levels = []
        for factor in (1.0, .5, .25):
            step = eps*factor
            positive = _perturbed_coefficients(arrays, direction, step)
            negative = _perturbed_coefficients(arrays, direction, -step)
            fdT = (positive[1]-negative[1])/(2*step)
            fdx = (positive[2]-negative[2])/(2*step)
            hp = positive[1]*np.diff(arrays["normalized_proper_times"])
            hm = negative[1]*np.diff(arrays["normalized_proper_times"])
            zp = piecewise_linear_zeta_coefficient_cotangent(positive[2], hp)["Gamma_SM_zeta"]
            zm = piecewise_linear_zeta_coefficient_cotangent(negative[2], hm)["Gamma_SM_zeta"]
            fdz = (zp-zm)/(2*step)
            levels.append(dict(epsilon=step,
                proper_duration_relative_residual=_relative(np.array([fdT]), np.array([expected_T])),
                proper_duration_absolute_residual=abs(fdT-expected_T),
                fixed_u_radius_relative_residual=_relative(fdx, expected_x),
                fixed_u_radius_absolute_residual=float(np.linalg.norm(fdx-expected_x)),
                zeta_relative_residual=_relative(np.array([fdz]), np.array([expected_zeta])),
                zeta_absolute_residual=abs(fdz-expected_zeta),
                positive_probe_birth_density=float(positive[0][0]),
                negative_probe_birth_density=float(negative[0][0]),
                radius_fd_roundoff_scale=float(np.finfo(float).eps*np.linalg.norm(arrays["log_radius"])/step)))
        records.append(dict(probe=name, terminal_arc_first=float(arrays["terminal_arc_first_jet"]@direction),
                            proper_duration_first=expected_T, zeta_first=expected_zeta, levels=levels))
    return dict(family="SIGNED_BIRTH_CLOCK_EXTENSION_OF_CURRENT_CACHED_ACTION_J_LINEARIZED_STATE_AND_RATE;NONLINEAR_GEOMETRY;MOVING_FIRST_HIT_LAST_NODE",
                two_sided_positive_birth_family=False,
                birth_domain_reason="CURRENT_RHO0_NEAR_ZERO;GENERIC73_DIRECTIONS_HAVE_NONZERO_BIRTH_DESCRIPTOR_JET",
                new_nonlinear_trajectory_solved=False, probes=records)


def run(mode_dir: Path, out: Path):
    started = time.perf_counter()
    modes_report = json.loads((mode_dir/"report.json").read_text(encoding="utf-8"))
    center = Path(modes_report["center"])
    sha = hashlib.sha256(center.read_bytes()).hexdigest().upper()
    if sha != modes_report["center_SHA256"]:
        raise ValueError("mode history and current trajectory differ")
    with np.load(center, allow_pickle=False) as source:
        states, rates, weights = (np.array(source[key]) for key in ("centers", "action_rates", "state_weights"))
        descriptors, descriptor_rates = (np.array(source[key]) for key in ("signed_descriptors", "descriptor_rates"))
    with np.load(mode_dir/"arrays.npz", allow_pickle=False) as source:
        modes = {key: np.array(source[key]) for key in source.files}
    indices = modes["node_indices"]
    if not np.array_equal(indices, np.arange(48)):
        raise ValueError("full current 48-node history required")
    arc, J, U0 = (modes[key] for key in ("action_lengths", "graph_Jacobian_action", "initial_mode_action"))
    U = [U0.copy()]; transitions = []
    for index, width in enumerate(np.diff(arc)):
        propagated = np.c_[np.eye(98), U[-1]]
        for substep in range(4):
            fraction = (substep+.5)/4
            generator = (1-fraction)*J[index]+fraction*J[index+1]
            propagated = expm_multiply(float(width/4)*generator, propagated)
        transitions.append(propagated[:, :98]); U.append(propagated[:, 98:])
    U, transitions = np.asarray(U), np.asarray(transitions)
    geometry = [boundary_geometry_action_covectors(state=state, weights=weights) for state in states]
    x, lapse, r, l = (np.asarray([row[key] for row in geometry]) for key in
        ("log_R4", "log_lapse", "D_log_R4_action_dual", "D_log_lapse_action_dual"))
    rho, density_cov, alpha, square = _clock_covectors(states, rates, J, weights, lapse, l)
    if descriptors[-1] != 0 or rho[-1] != 0:
        raise ValueError("actual canonical stop required")
    n = modes["descriptor_gradient_action"][-1]; f = rates[-1]; crossing = float(n@f)
    if crossing == 0:
        raise ArithmeticError("first hit is not transverse")
    da = -(n@U[-1])/crossing
    hit = U[-1]+f[:, None]*da
    x_first = np.einsum("ni,nij->nj", r, U)
    density_first = np.einsum("ni,nij->nj", density_cov, U)
    pulled = pullback_cancelled_arc_history_to_proper_time(
        arc_nodes=arc, log_radius=x, log_radius_arc_first_jet=x_first,
        proper_time_density=rho, proper_time_density_first_jet=density_first,
        terminal_log_radius_first_jet=r[-1]@hit)
    fixed_T_first = np.asarray(pulled["proper_duration_first_jet"])
    correction = .5*(rho[-2]*da-np.diff(arc)[-1]*density_first[-1])
    T_first = fixed_T_first+correction
    u, T = pulled["normalized_proper_times"], pulled["proper_duration"]
    x_arc_rate = CubicSpline(arc, x)(arc, 1)
    beta = np.zeros_like(rho); beta[1:-1] = x_arc_rate[1:-1]/rho[1:-1]
    normalized_first = np.array(pulled["log_radius_normalized_proper_time_first_jet"])
    normalized_first[1:-1] += beta[1:-1, None]*u[1:-1, None]*correction
    h = T*np.diff(u); h_first = np.diff(u)[:, None]*T_first
    augmented = np.zeros((47, 99, 99)); augmented[:, :98, :98] = transitions
    augmented[:, 98, 98] = 1
    arc_width = np.diff(arc)
    for index in range(47):
        augmented[index, 98, :98] = .5*arc_width[index]*(density_cov[index]+density_cov[index+1]@transitions[index])
    last_hit_cov = -n@transitions[-1]/crossing
    augmented[-1, 98, :98] = .5*arc_width[-1]*density_cov[-2]+.5*rho[-2]*last_hit_cov
    arrays = dict(action_lengths=arc, states=states, action_rates=rates, state_weights=weights,
        graph_Jacobian_action=J, transition_jacobians_action=transitions,
        state_clock_transition_jacobians=augmented,
        state_action_first_jet=U, initial_mode_action=U0,
        terminal_hit_state_action_first_jet=hit, terminal_arc_first_jet=da,
        terminal_descriptor_action_covector=n, terminal_flow_action=f,
        terminal_descriptor_flow_derivative=np.asarray(crossing),
        log_radius=x, log_lapse=lapse, radius_action_covectors=r, lapse_action_covectors=l,
        log_radius_arc_first_jet=x_first, log_radius_first_jet=normalized_first,
        log_radius_arc_rate=x_arc_rate, radius_proper_rate=beta,
        proper_time_density=rho, density_action_covectors=density_cov,
        density_first_jet=density_first, density_hit_endpoint_first_jet=np.zeros(73),
        normalized_proper_times=u, proper_times=np.asarray(pulled["proper_times"]),
        proper_duration=np.asarray(T), proper_durations=h,
        proper_duration_first_jet=T_first, proper_durations_first_jet=h_first,
        fixed_arc_proper_duration_first_jet=fixed_T_first,
        moving_endpoint_duration_first_jet_correction=correction,
        alpha=alpha, configuration_velocity_squared=square)
    birth_descriptor_covector = modes["descriptor_gradient_action"][0]
    birth_normal = birth_descriptor_covector@U0
    birth_normal_norm = float(np.linalg.norm(birth_normal))
    if not birth_normal_norm > 0:
        raise ArithmeticError("current birth descriptor has no physical tangent covector")
    outgoing = birth_normal/birth_normal_norm
    Q72 = null_space(birth_normal[None, :])
    if Q72.shape != (73, 72):
        raise ArithmeticError("current fixed-descriptor birth slice does not have dimension72")
    arrays.update(birth_slice_Q72=Q72,
        birth_descriptor_action_covector=birth_descriptor_covector,
        birth_descriptor_mode_covector=birth_normal,
        birth_outgoing_normal_mode=outgoing,
        birth_outgoing_normal_action=U0@outgoing,
        birth_slice_initial_action=U0@Q72,
        birth_signed_descriptor=np.asarray(descriptors[0]))
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out/"arrays.npz", **arrays)
    print(json.dumps(dict(phase="COEFFICIENT_JETS_READY", arrays=str((out/"arrays.npz").resolve()), nodes=48, parameters=73)), flush=True)

    common = dict(log_radii=x, normalized_proper_times=u, proper_duration=T,
                  log_radius_first_jet=normalized_first, proper_duration_first_jet=T_first,
                  spectral_parameter=-1.0)
    gauge = affine72_gauge_brst_first_jet(**common)
    plus = product_dirac_friedrichs_weyl_first_jet(**common, spatial_dirac_level=0, chirality=1)
    minus = product_dirac_friedrichs_weyl_first_jet(**common, spatial_dirac_level=0, chirality=-1)
    responses = [gauge["coexact"], gauge["BRST_scalar"], plus, minus]
    labels = ["GAUGE_COEXACT_C4", "BRST_SCALAR_C3", "PRODUCT_DIRAC_N0_PLUS", "PRODUCT_DIRAC_N0_MINUS"]
    boundary_duality = []
    for index, label in enumerate(labels):
        weyl = finite_core_weyl_and_coefficient_cotangent(log_radii=x, proper_durations=h,
            channel="scalar" if index<2 else "product_Dirac",
            unit_channel_value=(4.0, 3.0, 1.5, 1.5)[index],
            chirality=1 if index!=3 else -1, spectral_parameter=-1.0, decimal_precision=60)
        replay = coefficient_cotangent_parent_pullback(arrays, weyl["D_log_R4_node_Weyl"], weyl["D_proper_duration_Weyl"])
        boundary_duality.append(dict(channel=label, duality_relative_residual=replay["duality_relative_residual"],
            direct_api_relative_residual=_relative(replay["forward"], np.asarray(responses[index]["D_parameter_Weyl"]))))
    zeta = piecewise_linear_zeta_coefficient_cotangent(x, h)
    feedback = coefficient_cotangent_parent_pullback(arrays, zeta["D_log_R4_Gamma_SM_zeta"], zeta["D_proper_duration_Gamma_SM_zeta"])
    arrays.update(child_boundary_first_jet=np.asarray([row["D_parameter_Weyl"] for row in responses]),
        D_parent_Gamma_SM_zeta=feedback["forward"],
        known_replacement_minus_zeta_parent_covector=-feedback["forward"],
        known_replacement_minus_zeta_parent_action_dual=-feedback["action_dual"],
        known_replacement_minus_zeta_parent_raw_dual=-feedback["raw_dual"],
        zeta_adjoint_node_covectors=feedback["adjoint_node_covectors"],
        zeta_node_coefficient_cotangent=zeta["D_log_R4_Gamma_SM_zeta"],
        zeta_duration_coefficient_cotangent=zeta["D_proper_duration_Gamma_SM_zeta"])
    minus_zeta = -feedback["forward"]
    arrays.update(child_boundary_first_jet_birth72=arrays["child_boundary_first_jet"]@Q72,
        known_replacement_minus_zeta_parent_covector_birth72=Q72.T@minus_zeta,
        known_replacement_minus_zeta_parent_action_dual_birth72=U0@Q72@(Q72.T@minus_zeta),
        known_replacement_minus_zeta_parent_raw_dual_birth72=weights*(U0@Q72@(Q72.T@minus_zeta)),
        known_replacement_minus_zeta_outgoing_normal_component=np.asarray(outgoing@minus_zeta))
    heat_records, heat_scaled, heat_x, heat_h, heat_logs, heat_adjoints = [], [], [], [], [], []
    for index, label in enumerate(labels):
        heat = finite_core_heat_coefficient_cotangent(log_radii=x, proper_durations=h,
            channel="scalar" if index<2 else "product_Dirac",
            unit_channel_value=(4.0, 3.0, 1.5, 1.5)[index], chirality=1 if index!=3 else -1,
            heat_length=1.0)
        scaled = coefficient_cotangent_parent_pullback(arrays,
            heat["scaled_D_log_R4_Gamma_heat"], heat["scaled_D_proper_duration_Gamma_heat"])
        scaled_norm = float(np.linalg.norm(scaled["forward"]))
        parent_log_norm = float(heat["cotangent_common_log_factor"]+np.log(scaled_norm)) if scaled_norm>0 else None
        heat_records.append(dict(channel=label, coefficient_cotangent=heat,
            scaled_parent_covector_norm=scaled_norm, parent_covector_log_norm=parent_log_norm,
            scaled_parent_covector_birth72_norm=float(np.linalg.norm(Q72.T@scaled["forward"])),
            scaled_parent_outgoing_normal_component=float(outgoing@scaled["forward"]),
            scaled_forward_reverse_duality_relative_residual=scaled["duality_relative_residual"],
            graded_sector_weight_or_sum_inserted=False))
        heat_scaled.append(scaled["forward"]); heat_x.append(heat["scaled_D_log_R4_Gamma_heat"])
        heat_h.append(heat["scaled_D_proper_duration_Gamma_heat"])
        heat_logs.append(heat["cotangent_common_log_factor"])
        heat_adjoints.append(scaled["adjoint_node_covectors"])
    arrays.update(child_boundary_channel_names=np.asarray(labels),
        heat_scaled_parent_covectors=np.asarray(heat_scaled),
        heat_scaled_parent_covectors_birth72=np.asarray(heat_scaled)@Q72,
        heat_scaled_parent_action_duals=np.asarray(heat_scaled)@U0.T,
        heat_scaled_parent_raw_duals=(np.asarray(heat_scaled)@U0.T)*weights[None, :],
        heat_scaled_parent_action_duals_birth72=(np.asarray(heat_scaled)@Q72)@(U0@Q72).T,
        heat_cotangent_common_log_factors=np.asarray(heat_logs),
        heat_scaled_node_coefficient_cotangents=np.asarray(heat_x),
        heat_scaled_duration_coefficient_cotangents=np.asarray(heat_h),
        heat_scaled_adjoint_node_covectors=np.asarray(heat_adjoints))
    np.savez_compressed(out/"arrays.npz", **arrays)
    finite_difference = _finite_difference_replay(arrays, feedback["forward"])
    clock_replay = np.exp(lapse)*descriptors/np.asarray([row["cancelled_field_norm"] for row in modes_report["rows"]])
    report = dict(status="CURRENT_N12_CHILD_BOUNDARY_JETS_AND_KNOWN_MINUS_ZETA_PARENT_PULLBACK_EVALUATED",
        center=str(center.resolve()), center_SHA256=sha, mode_response=str(mode_dir.resolve()),
        domain="CURRENT_BRANCH24_FRONTIER_73_PHYSICAL_DIRECTIONS;48_STORED_MACRO_NODES",
        conventions=dict(state_action_first_jet="FIXED_ACTION_ARC_AMBIENT_98_BY_73;CACHED_ACTION_J4_SUBSTEPS",
            log_radius_arc_first_jet="FIXED_ACTION_ARC", density_first_jet="FIXED_ACTION_ARC",
            log_radius_first_jet="FIXED_NORMALIZED_PROPER_TIME_U;MOVING_CANONICAL_FIRST_HIT",
            proper_duration_first_jet="EXACT_DERIVATIVE_OF_SAMPLED_PIECEWISE_LINEAR_CLOCK_WITH_MOVING_LAST_ARC_WIDTH_AND_ZERO_HIT_DENSITY",
            proper_durations_first_jet="FIXED_U_SEGMENTS:DIFF_U_TIMES_D_T_HIT",
            parent_action_dual="ORTHOGONAL_PHYSICAL_TANGENT_REPRESENTATIVE_U0_TIMES_73_COVECTOR",
            replacement_component="MINUS_D_GAMMA_SM_ZETA;HEAT_COMPONENT_NOT_INCLUDED"),
        proper_duration=T, first_hit=dict(descriptor_flow_derivative=crossing,
            stored_descriptor_rate=float(descriptor_rates[-1]),
            rate_relative_discrepancy=abs(crossing-descriptor_rates[-1])/abs(descriptor_rates[-1]),
            terminal_arc_first_norm=float(np.linalg.norm(da)), terminal_arc_first_max_abs=float(np.max(abs(da))),
            first_hit_projector_operator_norm=float(np.linalg.norm(np.eye(98)-np.outer(f,n)/crossing, 2)),
            terminal_hit_descriptor_tangent_residual=float(np.linalg.norm(n@hit)),
            radius_terminal_arc_rate=float(r[-1]@f),
            moving_endpoint_duration_jet_correction_norm=float(np.linalg.norm(correction)),
            moving_endpoint_duration_jet_correction_relative=float(np.linalg.norm(correction)/np.linalg.norm(T_first))),
        clock=dict(configuration_velocity_squared_min=float(square.min()), density_identity_relative_replay=_relative(rho, clock_replay),
            terminal_fixed_arc_density_jet_norm=float(np.linalg.norm(density_first[-1])), terminal_hit_density_jet_norm=0.0),
        cached_flow_replay=dict(
            final_mode_relative_residual=_relative(U[-1], modes["unprojected_ambient_fundamental"]@modes["initial_mode_coefficients"]),
            initial_mode_orthogonality_residual=float(np.linalg.norm(U0.T@U0-np.eye(73), 2)),
            maximum_propagated_constraint_loss=float(max(np.linalg.norm(C@Ui, 2) for C, Ui in zip(modes["normalized_constraint_action"], U))),
            inherited_flow_transport_residual=modes_report["summary"]["maximum_step_flow_transport_residual"]),
        birth_slice=dict(signed_descriptor=float(descriptors[0]), descriptor_mode_covector_norm=birth_normal_norm,
            dimension=72, Q72_orthogonality_residual=float(np.linalg.norm(Q72.T@Q72-np.eye(72), 2)),
            fixed_descriptor_tangency_residual=float(np.linalg.norm(birth_normal@Q72)),
            clock_density_slice_first_norm=float(np.linalg.norm(density_first[0]@Q72)),
            outgoing_descriptor_first=float(birth_normal@outgoing),
            admissible_linearized_cone="BIRTH_DESCRIPTOR_MODE_COVECTOR_DOT_DELTA_PARAMETER_GREATER_OR_EQUAL_ZERO_AT_ZERO_DESCRIPTOR",
            mathematical_condition="At finite anchor require s_birth+b_birth.dot(delta_parameter)>=0 to first order",
            nonlinear_birth_constraint_curvature_evaluated=False),
        boundary_responses=dict(channel_order=labels, gauge=gauge, dirac_plus=plus, dirac_minus=minus,
            boundary_first_jets_are_susceptibilities_not_action_forces=True, forward_reverse_duality=boundary_duality),
        known_zeta_component=dict(Gamma_SM_zeta=zeta["Gamma_SM_zeta"], coefficient=zeta["coefficient"],
            quadrature=zeta["quadrature"], minus_D_Gamma_SM_zeta_parent_norm=float(np.linalg.norm(feedback["forward"])),
            minus_D_Gamma_SM_zeta_parent_max_abs=float(np.max(abs(feedback["forward"]))),
            minus_D_Gamma_SM_zeta_birth72_norm=float(np.linalg.norm(Q72.T@minus_zeta)),
            minus_D_Gamma_SM_zeta_outgoing_normal_component=float(outgoing@minus_zeta),
            common_scale_residual=zeta["common_scale_zeta_force_residual"],
            forward_reverse_duality_relative_residual=feedback["duality_relative_residual"],
            forward_reverse_duality_absolute_residual=feedback["duality_absolute_residual"]),
        individual_finite_core_heat_channels=heat_records,
        finite_difference_replay=finite_difference,
        numerical_scope="CACHED_ACTUAL_ACTION_FIRST_JETS;LINEAR_J_INTERPOLATION;BINARY64_MOVING_CLOCK_AND_CUBIC_SPLINE_RADIUS",
        unsampled_action_curvature_error_bounded=False, historical_Q66_used=False,
        complete_six_sector_heat_force=False, incoming_E1_parent_reset_pullback=False,
        continuous_first_hit_certificate=False, FULL_BHSM_COMPLETE=False,
        elapsed_seconds=time.perf_counter()-started, arrays=str((out/"arrays.npz").resolve()))
    (out/"report.json").write_text(json.dumps(_json(report), indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps(_json(dict(status=report["status"], proper_duration=T, first_hit=report["first_hit"],
        known_zeta_component=report["known_zeta_component"], elapsed_seconds=report["elapsed_seconds"])), indent=2), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode-response", type=Path, default=DEFAULT_MODES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    run(args.mode_response, args.out)
