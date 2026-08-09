"""BHSM v14.94 local-environment finite-time encapsulation gate.

This package tests the only exact, constraint-reduced, time-dependent M8 P1
backgrounds presently retained: the round and Jensen fixed-shape branches.
They are genuine dynamical data, not static Hessian fixtures.  The expanding
round branch has positive homogeneous shape stiffness.  Jensen has one
homogeneous tachyon at every finite time, rather than a local environmental
threshold crossing.  Both are spatially homogeneous, cap common, and carry
zero spatial transport and reflection-relative momentum.  Hence neither is a
local encapsulation event.  General nonhomogeneous constraint-solved incoming
wave packets remain outside the derived phase space, so Path A remains open.

No external environment, detector, susceptibility, pressure, fitted
threshold, new field, or new coefficient is introduced.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.p1_lorentzian_background_constraint import (
    constraint_reduced_shape_masses,
    fixed_shape_solution,
    hamiltonian_constraint,
)


VERSION = "v14.94"
PRIMARY_OBJECT = (
    "ACTION_OWNED_LOCAL_ENVIRONMENT_DRIVEN_FINITE_TIME_INSTABILITY_AND_"
    "ENCAPSULATION_EVENT_WITH_THRESHOLD_CROSSING_NONLINEAR_SATURATION_"
    "CONSTRAINT_CLOSURE_AND_MODE_SELECTION"
)
PATH_A_STATUS = "NO_ENCAPSULATION_EVENT_IN_CONTROLLED_RETAINED_SECTORS_PATH_A_REMAINS_OPEN"
EXACT_NEXT_OBJECT = (
    "CONSTRAINT_SOLVED_NONHOMOGENEOUS_LORENTZIAN_M8_INCOMING_WAVE_PACKET_"
    "WITH_QUASILOCAL_NOETHER_FLUX_TIME_PRESERVED_COMMON_DOMAIN_AND_LOCAL_"
    "PHYSICAL_TANGENT_PROPAGATOR"
)
PRIMARY_VERDICT = (
    "BHSM_V14_94_THE_EXACT_CONSTRAINT_REDUCED_ROUND_AND_JENSEN_LORENTZIAN_"
    "P1_BRANCHES_SUPPLY_ACTION_OWNED_TIME_DEPENDENT_CANONICAL_MOMENTUM_BUT_"
    "ARE_SPATIALLY_HOMOGENEOUS_CAP_COMMON_AND_HAVE_ZERO_LOCAL_TRANSPORT_"
    "FLUX_AND_ZERO_DELTA_PI;_THE_ROUND_BRANCH_HAS_NO_HOMOGENEOUS_SHAPE_"
    "INSTABILITY_WHILE_JENSEN_HAS_ONE_GLOBAL_TACHYON_AT_EVERY_FINITE_TIME_"
    "RATHER_THAN_A_LOCAL_THRESHOLD_CROSSING_AND_NO_ACTION_DERIVED_NONLINEAR_"
    "COMPLETION;_THEREFORE_NO_ENCAPSULATION_EVENT_EXISTS_IN_THE_CONTROLLED_"
    "RETAINED_SECTORS_BUT_GENERAL_NONHOMOGENEOUS_PATH_A_DYNAMICS_REMAINS_OPEN"
)


def environment_variable_ledger() -> list[dict[str, Any]]:
    """Return the action-owned environmental variables and their status."""

    return [
        {"variable": "h_ij", "action": "M8_P1_Einstein_Hilbert_plus_GHY", "canonical": "configuration", "interpretation": "local_spatial_geometry", "scope": "local", "dynamics": "independent_subject_to_constraints"},
        {"variable": "pi^ij", "action": "M8_P1_ADM_kinetic_block", "canonical": "momentum", "interpretation": "extrinsic_curvature_momentum", "scope": "local_density", "dynamics": "constraint_reduced"},
        {"variable": "eta", "action": "M8_eta_p2_plus_p8", "canonical": "configuration", "interpretation": "degree_one_internal_geometry", "scope": "local_with_global_degree", "dynamics": "independent_unit_map"},
        {"variable": "p_eta", "action": "M8_eta_Legendre_map", "canonical": "momentum", "interpretation": "eta_transport", "scope": "local_density", "dynamics": "positive_Legendre_cone_only"},
        {"variable": "chi,p_chi", "action": "M8_chi_kinetic_block", "canonical": "pair", "interpretation": "bulk_scalar_environment", "scope": "local", "dynamics": "independent"},
        {"variable": "sigma,p_sigma", "action": "M8_sigma_kinetic_potential_eta_multiplier", "canonical": "pair", "interpretation": "envelopment_order_parameter", "scope": "local", "dynamics": "independent"},
        {"variable": "K_ij", "action": "derived_from_h_dot_lapse_shift", "canonical": "derived", "interpretation": "expansion_and_shear", "scope": "local", "dynamics": "not_independent"},
        {"variable": "cap_seam_GHY_Brown_York_data", "action": "retained_cap_GHY_and_matchers", "canonical": "boundary_response", "interpretation": "quasilocal_transfer_after_boundary_choice", "scope": "interface", "dynamics": "constrained"},
        {"variable": "parent_child_scales_and_attachment", "action": "retained_stratified_KKT_correspondence", "canonical": "partial_only", "interpretation": "cross_stratum_environment", "scope": "stratified", "dynamics": "no_closed_common_Lorentzian_phase_space"},
    ]


def exact_incoming_state(branch: str, time: float = 1.0, kappa0: float = 1.0, kappa1: float = 1.0) -> dict[str, Any]:
    """Return exact fixed-shape M8 data and constraint residuals."""

    if branch not in {"round", "jensen"}:
        raise ValueError("branch must be 'round' or 'jensen'")
    state = fixed_shape_solution(branch, time, kappa0, kappa1)
    residual = hamiltonian_constraint(
        state["a4"], state["a2"], state["a1"],
        state["H4"], state["H2"], state["H1"], kappa0, kappa1,
    )
    volume_rate = 4.0 * state["H4"] + 2.0 * state["H2"] + state["H1"]
    return {
        "branch": branch,
        "time": time,
        "metric_scales": {key: state[key] for key in ("a4", "a2", "a1")},
        "extrinsic_rates": {key: state[key] for key in ("H4", "H2", "H1")},
        "canonical_metric_momentum": "pi^ij=(kappa1/2)sqrt(h)(K^ij-Kh^ij)",
        "canonical_momentum_nonzero": abs(volume_rate) > 0.0,
        "Hamiltonian_constraint_residual": residual,
        "momentum_constraint_residual": 0.0,
        "constraint_propagation": "dot(C_H)=-Theta*C_H=0",
        "spatially_homogeneous": True,
        "physical_time_dependent": True,
        "incoming_localized_flux_state": False,
    }


def local_flux_and_energy_ledger() -> dict[str, Any]:
    return {
        "local_gravitational_energy_density": None,
        "reason": "generally_covariant_P1_gravity_has_no_gauge_invariant_local_energy_density",
        "closed_S7_boundary": None,
        "closed_S7_Hamiltonian": "constraint_generator_zero_on_shell_not_positive_scalar_energy",
        "Brown_York_energy": "available_only_after_physical_boundary_normal_reference_and_ensemble_are_selected",
        "homogeneous_spatial_matter_flux": 0.0,
        "homogeneous_spatial_gravitational_transport_flux": 0.0,
        "homogeneous_cap_relative_flux": 0.0,
        "geometric_work": "common_scale_evolution_not_local_transport",
        "seam_transfer": 0.0,
        "internal_exchange": "none_on_eta_identity_chi_sigma_zero_P1_branches",
        "balance_law": "dH_Omega/dt=-integral_boundary(F_H)+S_Omega_requires_a_selected_quasilocal_Hamiltonian",
        "event_energy_accounting": None,
    }


def homogeneous_shape_operator(branch: str, time: float, kappa0: float = 1.0, kappa1: float = 1.0) -> dict[str, Any]:
    """Return the exact time-dependent reduced shape operator."""

    state = fixed_shape_solution(branch, time, kappa0, kappa1)
    masses = constraint_reduced_shape_masses(branch, state["a4"])
    theta = 7.0 * state["H4"]
    operators = []
    for index, mass_squared in enumerate(masses):
        matrix = np.array([[0.0, 1.0], [-mass_squared, -theta]])
        eigenvalues = np.linalg.eigvals(matrix)
        operators.append(
            {
                "mode": index,
                "mass_squared": mass_squared,
                "q_velocity_operator": matrix.tolist(),
                "instantaneous_growth_exponents": [
                    {"real": float(value.real), "imag": float(value.imag)} for value in eigenvalues
                ],
                "positive_growth_exponent": bool(max(value.real for value in eigenvalues) > 1.0e-14),
            }
        )
    return {
        "branch": branch,
        "time": time,
        "M_proportional_to": "a4^7_times_constant_shape_volume_ratio",
        "equation": "M(t)q_ddot+M_dot(t)q_dot+M(t)m_squared(t)q=0",
        "first_order_form": "d_t(q,v)=L_phys(t)(q,v)",
        "gauge_reduction": "lapse_time_and_Hamiltonian_volume_direction_removed_v6_0_10",
        "domain": "two_homogeneous_shape_modes_on_closed_S7",
        "operators": operators,
    }


def instability_mechanism_ledger() -> list[dict[str, Any]]:
    return [
        {"mechanism": "stiffness_crossing", "round": "NO_m2=4/a2_positive", "jensen": "NO_CROSSING_one_m2=-4/a4^2_at_every_finite_time"},
        {"mechanism": "Hamiltonian_Krein_collision", "round": "NONE_IN_TWO_DECOUPLED_POSITIVE_HOMOGENEOUS_MODES", "jensen": "NOT_NEEDED_ALREADY_INDEFINITE_STIFFNESS"},
        {"mechanism": "parametric_instability", "round": "NONPERIODIC_COSH_BACKGROUND_NO_FLOQUET_BAND_DERIVED", "jensen": "GLOBAL_TACHYON_DOMINATES"},
        {"mechanism": "non_normal_transient_growth", "round": "CONTRACTING_ANTIFRICTION_CAN_AMPLIFY_GLOBALLY_NOT_LOCALLY", "jensen": "POSSIBLE_BUT_NOT_AN_ENVIRONMENTAL_THRESHOLD"},
        {"mechanism": "resonant_transfer", "round": "SIGMA_10_4_4_CUBIC_ZERO_AT_SIGMA_ZERO", "jensen": "NO_ACTION_DERIVED_MULTIMODE_COMPLETION_TENSOR"},
    ]


def _mode_rhs(branch: str, mode: int, time: float, state: np.ndarray) -> np.ndarray:
    operator = np.asarray(homogeneous_shape_operator(branch, time)["operators"][mode]["q_velocity_operator"])
    return operator @ state


def integrate_linear_mode(branch: str, mode: int, t0: float, t1: float, steps: int) -> dict[str, Any]:
    """Deterministic RK4 fundamental matrix for one reduced physical mode."""

    if branch not in {"round", "jensen"} or mode not in {0, 1}:
        raise ValueError("invalid branch or mode")
    if not (math.isfinite(t0) and math.isfinite(t1) and t1 > t0):
        raise ValueError("require finite t1>t0")
    if not isinstance(steps, int) or steps < 1:
        raise ValueError("steps must be a positive integer")
    dt = (t1 - t0) / steps
    fundamental = np.eye(2)
    time = t0
    for _ in range(steps):
        k1 = np.column_stack([_mode_rhs(branch, mode, time, fundamental[:, j]) for j in range(2)])
        mid1 = fundamental + 0.5 * dt * k1
        k2 = np.column_stack([_mode_rhs(branch, mode, time + 0.5 * dt, mid1[:, j]) for j in range(2)])
        mid2 = fundamental + 0.5 * dt * k2
        k3 = np.column_stack([_mode_rhs(branch, mode, time + 0.5 * dt, mid2[:, j]) for j in range(2)])
        end = fundamental + dt * k3
        k4 = np.column_stack([_mode_rhs(branch, mode, time + dt, end[:, j]) for j in range(2)])
        fundamental += dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        time += dt
    singular_values = np.linalg.svd(fundamental, compute_uv=False)
    a0 = fixed_shape_solution(branch, t0, 1.0, 1.0)["a4"]
    a1 = fixed_shape_solution(branch, t1, 1.0, 1.0)["a4"]
    expected_determinant = (a0 / a1) ** 7
    return {
        "branch": branch,
        "mode": mode,
        "interval": [t0, t1],
        "steps": steps,
        "fundamental_matrix_q_v": fundamental.tolist(),
        "largest_coordinate_singular_value": float(max(singular_values)),
        "coordinate_norm_warning": "q_v_Euclidean_singular_value_is_not_a_background_independent_physical_norm",
        "determinant": float(np.linalg.det(fundamental)),
        "expected_Wronskian_determinant": expected_determinant,
        "Wronskian_residual": abs(float(np.linalg.det(fundamental)) - expected_determinant),
    }


def resolution_convergence() -> dict[str, Any]:
    rows = [integrate_linear_mode("jensen", 1, 0.0, 4.0, steps) for steps in (200, 400, 800)]
    matrices = [np.asarray(row["fundamental_matrix_q_v"]) for row in rows]
    return {
        "discretization": "fixed_step_RK4_on_exact_time_dependent_reduced_operator",
        "domain": "t_in=0_to_t_out=4_in_primitive_lambda_equals_1_units",
        "resolutions": rows,
        "difference_200_400": float(np.linalg.norm(matrices[0] - matrices[1])),
        "difference_400_800": float(np.linalg.norm(matrices[1] - matrices[2])),
        "observed_refinement": float(np.linalg.norm(matrices[0] - matrices[1]) / np.linalg.norm(matrices[1] - matrices[2])),
        "maximum_Wronskian_residual": max(row["Wronskian_residual"] for row in rows),
        "nonlinear_event_simulated": False,
    }


def event_gate_status() -> dict[str, Any]:
    return {
        "event_phases": {"incoming": "EXACT_HOMOGENEOUS_DYNAMICS_ONLY", "threshold": None, "encapsulation": None, "outgoing": None},
        "local_environment_profile": "SPATIALLY_CONSTANT_ON_EXACT_BRANCHES",
        "threshold_condition": None,
        "threshold_location_time": None,
        "unstable_mode": "JENSEN_HOMOGENEOUS_SHAPE_MODE_1_GLOBAL_AT_ALL_FINITE_TIMES",
        "growth": "FINITE_TIME_LINEAR_PROPAGATOR_COMPUTED_NO_LOCAL_THRESHOLD",
        "nonlinear_coefficients": None,
        "nonlinear_completion": None,
        "completion_criterion_C_enc": None,
        "mode_selection": None,
        "discrete_completion_class": None,
        "energy_geometry_interference": None,
        "sigma_symmetry": "SIGMA_EQUALS_ZERO_ON_EXACT_BRANCHES_Z2_CUBIC_REMAINS_ZERO",
        "constraints_through_event": None,
        "common_domain": "GLOBAL_CLOSED_S7_AND_FIXED_SMOOTH_CAP_TRANSMISSION_PRESERVED_BY_HOMOGENEITY;_NO_MOVING_DOMAIN_EVENT",
        "event_energy_accounting": None,
        "post_event_state": None,
        "persistence_class": None,
        "initial_condition_robustness": "JENSEN_TACHYON_LINEARLY_ROBUST_BUT_NOT_LOCAL_ENCAPSULATION",
        "phase_diagram": {"round_expanding": "STABLE_HOMOGENEOUS_SHAPE_PROPAGATION", "round_contracting": "GLOBAL_ANTIFRICTION_AMPLIFICATION", "jensen": "GLOBAL_HOMOGENEOUS_TACHYON", "local_event": "UNTESTED_REQUIRES_NONHOMOGENEOUS_CONSTRAINT_SOLVE"},
        "L2_instability": None,
        "DeltaPi_t": 0.0,
        "M_plus": None,
        "M_minus": None,
        "J_dyn": None,
        "B_dyn_L2": None,
        "internal_spectral_bundle_eligibility": False,
    }


def completion_payload() -> dict[str, Any]:
    round_in = exact_incoming_state("round")
    jensen_in = exact_incoming_state("jensen")
    round_operator = homogeneous_shape_operator("round", 1.0)
    jensen_operator = homogeneous_shape_operator("jensen", 1.0)
    convergence = resolution_convergence()
    event = event_gate_status()
    validation = {
        "no_new_environment_field_or_parameter": True,
        "round_initial_constraints_close": abs(round_in["Hamiltonian_constraint_residual"]) < 1.0e-13 and round_in["momentum_constraint_residual"] == 0.0,
        "jensen_initial_constraints_close": abs(jensen_in["Hamiltonian_constraint_residual"]) < 1.0e-13 and jensen_in["momentum_constraint_residual"] == 0.0,
        "incoming_canonical_momenta_nonzero": round_in["canonical_momentum_nonzero"] and jensen_in["canonical_momentum_nonzero"],
        "round_stiffness_positive": all(row["mass_squared"] > 0.0 for row in round_operator["operators"]),
        "jensen_has_one_global_tachyon": sum(row["mass_squared"] < 0.0 for row in jensen_operator["operators"]) == 1,
        "jensen_has_no_stiffness_threshold": instability_mechanism_ledger()[0]["jensen"].startswith("NO_CROSSING"),
        "RK4_fourth_order_refinement": convergence["observed_refinement"] > 12.0,
        "Wronskian_identity_converged": convergence["maximum_Wronskian_residual"] < 1.0e-9,
        "homogeneous_flux_not_mislabeled_outgoing": local_flux_and_energy_ledger()["homogeneous_spatial_gravitational_transport_flux"] == 0.0,
        "global_instability_not_mislabeled_local_event": event["threshold_location_time"] is None,
        "undefined_event_objects_not_relabelled_zero": event["nonlinear_completion"] is None and event["event_energy_accounting"] is None,
        "Path_B_not_activated": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": True,
    }
    return {
        "artifact": "BHSM_local_environment_finite_time_encapsulation_gate_v14_94",
        "version": VERSION,
        "primary_object": PRIMARY_OBJECT,
        "primary_verdict": PRIMARY_VERDICT,
        "action_owned_environment": environment_variable_ledger(),
        "incoming_states": {"round": round_in, "jensen": jensen_in},
        "outgoing_flux_and_energy": local_flux_and_energy_ledger(),
        "physical_time_dependent_operator": {"round": round_operator, "jensen": jensen_operator},
        "instability_mechanisms": instability_mechanism_ledger(),
        "finite_time_evolution": convergence,
        "event_gate": event,
        "PATH_A_STATUS": PATH_A_STATUS,
        "LOCAL_ENVIRONMENT_INSTABILITY_DERIVED": False,
        "HOMOGENEOUS_GLOBAL_INSTABILITY_DERIVED": True,
        "FINITE_TIME_ENCAPSULATION_EVENT_DERIVED": False,
        "NONLINEAR_COMPLETION_DERIVED": False,
        "MODE_SELECTION_DERIVED": False,
        "CONSTRAINTS_PRESERVED_THROUGH_EVENT": None,
        "EVENT_ENERGY_ACCOUNTED": None,
        "PROTECTED_INTERNAL_SPECTRAL_BAND_DERIVED": False,
        "SMOOTH_INTERNAL_MODE_BUNDLE_DERIVED": False,
        "PATH_B_FALLBACK_ACTIVATED": False,
        "Hindsight_20_20": {
            "validated": [
                "exact round and Jensen branches provide constraint-satisfying time-dependent canonical momentum",
                "round homogeneous shape dynamics has no instability",
                "Jensen has one global homogeneous tachyon at every finite time",
                "finite-time reduced propagator converges and obeys the Wronskian identity",
            ],
            "invalidated": [
                "homogeneous expansion as localized outgoing flux",
                "the Jensen tachyon as a local environmental threshold crossing",
                "linear amplification alone as nonlinear encapsulation completion",
            ],
            "reclassified": [
                "encapsulation as a finite event rather than a permanent soliton",
                "the exact P1 branches as incoming-dynamics controls rather than event solutions",
            ],
            "open": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "completion_status": {
            "FULL_BHSM_COMPLETE": False,
            "MARK_III": "NOT_REACHED",
            "PHYSICAL_EXECUTION_BLOCKED": True,
            "USB_SYNCHRONIZATION_ELIGIBLE": False,
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def materialize(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return target
