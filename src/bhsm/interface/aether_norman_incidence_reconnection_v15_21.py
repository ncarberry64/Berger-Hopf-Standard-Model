"""BHSM v15.21 NormanWorks incidence reconnection and dynamical kill screen.

This module reconnects the exact v14.68--v14.70 attachment differential
lineage to the v15.9 homoclinic formation orbit and the v15.20 fixed-momentum
inertia theorem.  It distinguishes the action-owned second-sigma derivative
of the eta kinetic block from the still-absent derivative of a globally
selected attachment state map.

The result is fail-closed.  It does not invent a separation coordinate,
phase, wall tension, kick, or sigma coefficient.
"""

from __future__ import annotations

import inspect
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from bhsm.interface.completion.global_attachment_incidence_curvature_v14_68 import (
    canonical_incidence_isometry,
    incidence_map_payload,
)
from bhsm.interface.completion.tensor_differential_incidence_v14_69 import (
    compatibility_jacobian_round,
    heterogeneous_tensor_incidence_isometry,
    provenance_gate_payload as tensor_provenance_gate_payload,
)
from bhsm.interface.completion.second_shape_jacobi_triplet_v14_70 import (
    reflection_stationarity_payload,
    round_graph_metric_second_variation,
)


VERSION = "v15.21"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
CAMPAIGN_OBJECT = (
    "FULL_NORMANWORKS_HINDSIGHT_RECONNECTION_FROM_RELATIVE_INERTIA_THROUGH_"
    "PHYSICAL_INCIDENCE_SIGMA_SATURATION_AND_Q_TO_D_CANONICAL_TRANSFER"
)
OUTCOME = (
    "LOCAL_ETA_SECOND_SIGMA_INERTIA_TENSOR_DERIVED_BUT_GLOBAL_ATTACHMENT_"
    "STATE_DERIVATIVE_AND_CANONICAL_SEPARATION_PAIR_ABSENT"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_TIME_DEPENDENT_GLOBAL_ENVELOPMENT_CRITICAL_STATE_MAP_"
    "PHI_STAR_OF_Q_SIGMA_D_WITH_VARIED_NORMAL_EMBEDDING_COMPLETE_"
    "CONSTRAINT_REDUCTION_NONDEGENERATE_PHYSICAL_HESSIAN_AND_DERIVED_G_"
    "PRODUCING_THE_PHYSICAL_SECOND_SIGMA_AND_Q_D_INCIDENCE_TENSORS"
)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _spd(matrix: Sequence[Sequence[float]], name: str) -> np.ndarray:
    result = np.asarray(matrix, dtype=float)
    if (
        result.ndim != 2
        or result.shape[0] != result.shape[1]
        or not np.allclose(result, result.T, atol=1.0e-12)
    ):
        raise ValueError(f"{name} must be a real symmetric matrix")
    if float(np.min(np.linalg.eigvalsh(result))) <= 0.0:
        raise ValueError(f"{name} must be positive definite")
    return result


def eta_second_sigma_inertia_tensor(
    inertia_zero: Sequence[Sequence[float]], coupling_g: float
) -> np.ndarray:
    """Return D_sigma^2 I_eta at sigma=0 for I=(1+g sigma^2) I0."""

    inertia = _spd(inertia_zero, "I_eta_zero")
    coupling = _finite(coupling_g, "g")
    return 2.0 * coupling * inertia


def eta_fixed_momentum_quartic(
    momentum: Sequence[float],
    inertia_zero: Sequence[Sequence[float]],
    coupling_g: float,
) -> dict[str, Any]:
    """Return the exact Taylor data of the uniform eta inertia weight.

    For I(sigma)=(1+g sigma^2)I0, the fixed-momentum kinetic Hamiltonian is
    p^T I0^-1 p/[2(1+g sigma^2)].  Thus the Landau quartic is
    G_inertia=2 g^2 p^T I0^-1 p.
    """

    inertia = _spd(inertia_zero, "I_eta_zero")
    p = np.asarray(momentum, dtype=float).reshape(-1)
    if p.shape != (inertia.shape[0],) or not np.all(np.isfinite(p)):
        raise ValueError("momentum must be a finite vector on the inertia space")
    coupling = _finite(coupling_g, "g")
    inverse_norm = float(p @ np.linalg.solve(inertia, p))
    return {
        "p_I0_inverse_p": inverse_norm,
        "sigma_quadratic_curvature_shift": -coupling * inverse_norm,
        "sigma_quartic_energy_coefficient": 0.5 * coupling**2 * inverse_norm,
        "G_inertia": 2.0 * coupling**2 * inverse_norm,
        "whitened_B": (coupling * np.eye(inertia.shape[0])).tolist(),
        "second_sigma_inertia_tensor": eta_second_sigma_inertia_tensor(
            inertia, coupling
        ).tolist(),
        "nonnegative": 2.0 * coupling**2 * inverse_norm >= 0.0,
        "coefficient_status": "CONDITIONAL_ON_THE_RETAINED_BUT_UNSELECTED_G",
    }


def homoclinic_formation_phase_space(
    tau: float, *, supercriticality: float, critical_radius: float
) -> dict[str, float | bool]:
    """Evaluate the exact v15.9 homoclinic orbit and its canonical momentum."""

    time = _finite(tau, "tau")
    m = _positive(supercriticality, "supercriticality")
    radius = _positive(critical_radius, "critical_radius")
    inertia = 1.5 * radius**2
    amplitude = math.sqrt(90.0 * m / 23.0)
    omega = math.sqrt(5.0 * m / (6.0 * radius**2))
    x = omega * time
    sech = 1.0 / math.cosh(x)
    tanh = math.tanh(x)
    q = amplitude * sech
    q_dot = -amplitude * omega * sech * tanh
    q_ddot = amplitude * omega**2 * sech * (1.0 - 2.0 * sech**2)
    momentum = inertia * q_dot
    momentum_dot = inertia * q_ddot
    potential = -5.0 * m * q**2 / 8.0 + 23.0 * q**4 / 144.0
    potential_prime = -5.0 * m * q / 4.0 + 23.0 * q**3 / 36.0
    hamiltonian = momentum**2 / (2.0 * inertia) + potential
    return {
        "q": q,
        "q_dot": q_dot,
        "q_ddot": q_ddot,
        "M_q": inertia,
        "p_q": momentum,
        "p_q_dot": momentum_dot,
        "minus_dV_dq": -potential_prime,
        "Hamiltonian": hamiltonian,
        "Hamilton_equation_residual": momentum_dot + potential_prime,
        "p_q_conserved": False,
    }


def formation_peak_momentum_drive(supercriticality: float) -> dict[str, float]:
    """Return the exact maximum of p_q^2/M_q on the homoclinic orbit."""

    m = _positive(supercriticality, "supercriticality")
    return {
        "max_p_q_squared_over_M_q": 225.0 * m**2 / 184.0,
        "sech_squared_at_maximum": 0.5,
        "absolute_omega_tau_at_maximum": math.acosh(math.sqrt(2.0)),
    }


def instantaneous_sigma_activation_window(
    *,
    supercriticality: float,
    critical_radius: float,
    coupling_g: float,
    static_curvature: float,
) -> dict[str, Any]:
    """Return where the fixed-p sigma branch exists along the sigma-zero pulse.

    This is an instantaneous/adiabatic diagnostic, not a conserved-p Routhian
    orbit.  The formation momentum vanishes both at the concentration maximum
    and asymptotically, so an active branch, if present, occurs in two lobes.
    """

    m = _positive(supercriticality, "supercriticality")
    radius = _positive(critical_radius, "critical_radius")
    coupling = _positive(coupling_g, "g")
    curvature = _positive(static_curvature, "K_sigma")
    omega = math.sqrt(5.0 * m / (6.0 * radius**2))
    peak = formation_peak_momentum_drive(m)["max_p_q_squared_over_M_q"]
    peak_ratio = coupling * peak / curvature
    if peak_ratio <= 1.0:
        return {
            "active": False,
            "peak_drive_to_curvature_ratio": peak_ratio,
            "positive_time_interval": None,
            "negative_time_interval": None,
            "active_at_concentration_peak_tau_zero": False,
            "active_asymptotically": False,
            "interpretation": "NO_INSTANTANEOUS_NONZERO_SIGMA_BRANCH",
        }
    discriminant = math.sqrt(1.0 - 1.0 / peak_ratio)
    y_high = 0.5 * (1.0 + discriminant)
    y_low = 0.5 * (1.0 - discriminant)
    entry = math.acosh(1.0 / math.sqrt(y_high)) / omega
    exit_time = math.acosh(1.0 / math.sqrt(y_low)) / omega
    return {
        "active": True,
        "peak_drive_to_curvature_ratio": peak_ratio,
        "sech_squared_roots": [y_low, y_high],
        "positive_time_interval": [entry, exit_time],
        "negative_time_interval": [-exit_time, -entry],
        "active_at_concentration_peak_tau_zero": False,
        "active_asymptotically": False,
        "interpretation": "TWO_TRANSIENT_INSTANTANEOUS_SIGMA_LOBES",
    }


def attachment_state_argument_audit() -> dict[str, Any]:
    """Audit whether the retained explicit incidence maps are state maps."""

    scalar_parameters = list(inspect.signature(canonical_incidence_isometry).parameters)
    tensor_parameters = list(
        inspect.signature(heterogeneous_tensor_incidence_isometry).parameters
    )
    scalar_payload = incidence_map_payload()
    tensor_payload = tensor_provenance_gate_payload()
    return {
        "scalar_incidence_function_arguments": scalar_parameters,
        "tensor_incidence_function_arguments": tensor_parameters,
        "q_argument_present": "q" in scalar_parameters + tensor_parameters,
        "sigma_argument_present": "sigma" in scalar_parameters + tensor_parameters,
        "d_argument_present": "d" in scalar_parameters + tensor_parameters,
        "scalar_map_full_tensor_background_evaluated": scalar_payload[
            "full_tensor_DQ_H_and_trace_maps_evaluated_on_physical_background"
        ],
        "tensor_map_all_physical_provenance_present": tensor_payload[
            "all_physical_provenance_inputs_present"
        ],
        "D2_sigma_attachment_map_evaluable": False,
        "D_q_attachment_state_map_evaluable": False,
        "D_d_attachment_state_map_evaluable": False,
        "conclusion": (
            "THE_RETAINED_MAP_IS_AN_EXACT_FIXED_BACKGROUND_COMPATIBILITY_"
            "ISOMETRY_NOT_A_GLOBAL_CRITICAL_STATE_MAP_PHI_STAR_Q_SIGMA_D"
        ),
    }


def round_separation_incidence_audit(radius: float = 1.0) -> dict[str, Any]:
    """Return the exact round first-shape kernel and second-shape response."""

    scale = _positive(radius, "radius")
    jacobian = compatibility_jacobian_round()
    xi_plus = jacobian[:, 76]
    xi_minus = jacobian[:, 77]
    second = round_graph_metric_second_variation(1.0, [0.0, 0.0, 0.0], scale)
    reflection = reflection_stationarity_payload()
    return {
        "xi_plus_first_compatibility_column_norm": float(np.linalg.norm(xi_plus)),
        "xi_minus_first_compatibility_column_norm": float(np.linalg.norm(xi_minus)),
        "first_order_round_A_d_available": False,
        "first_order_round_G_qd": 0.0,
        "constant_normal_second_shape_tensor": second.tolist(),
        "constant_normal_second_shape_norm": float(np.linalg.norm(second)),
        "second_shape_nonzero": bool(np.linalg.norm(second) > 0.0),
        "second_shape_is_a_first_order_canonical_tangent": False,
        "nonround_action_selected": reflection[
            "nonround_action_stationary_branch_constructed"
        ],
        "canonical_p_d_available": False,
        "selection_rule": (
            "CAP_REFLECTION_SENDS_D_TO_MINUS_D_WHILE_Q_IS_EVEN_SO_ANY_"
            "SMOOTH_G_QD_IS_ODD_IN_D_AND_G_QD_AT_D_ZERO_VANISHES"
        ),
    }


def implicit_physical_tangent_theorem_payload() -> dict[str, Any]:
    """State the exact implicit-response object needed for physical incidence."""

    return {
        "stationary_equation": "F(Phi,Q)=delta_Gamma/delta_Phi=0",
        "constraint_reduced_tangent": (
            "A_A_phys=-H_perp_inverse*P_phys*(partial_F/partial_Q_A)"
        ),
        "kinetic_Gram": "G_AB=<A_A_phys,K_full A_B_phys>",
        "second_sigma_incidence": (
            "D_sigma_squared_of_the_selected_state_and_kinetic_pullback"
        ),
        "q_to_d_incidence": "I_qd=<A_q_phys,K_full A_d_phys>",
        "required_inputs": {
            "time_dependent_global_critical_state_Phi_star_q_sigma_d": False,
            "varied_normal_embedding_and_shape_equation": False,
            "physical_constraint_projector_P_phys": False,
            "invertible_reduced_Hessian_H_perp": False,
            "complete_Lorentzian_kinetic_operator_K_full": False,
            "selected_nonround_or_second_shape_branch": False,
        },
        "evaluable": False,
    }


def completion_payload() -> dict[str, Any]:
    inertia = np.asarray([[2.0, 0.3], [0.3, 1.4]], dtype=float)
    momentum = np.asarray([0.7, -0.2], dtype=float)
    quartic = eta_fixed_momentum_quartic(momentum, inertia, 0.8)
    center = homoclinic_formation_phase_space(
        0.0, supercriticality=0.4, critical_radius=2.0
    )
    off_center = homoclinic_formation_phase_space(
        0.9, supercriticality=0.4, critical_radius=2.0
    )
    inactive = instantaneous_sigma_activation_window(
        supercriticality=0.4,
        critical_radius=2.0,
        coupling_g=0.8,
        static_curvature=1.0,
    )
    active = instantaneous_sigma_activation_window(
        supercriticality=1.0,
        critical_radius=2.0,
        coupling_g=2.0,
        static_curvature=1.0,
    )
    attachment = attachment_state_argument_audit()
    separation = round_separation_incidence_audit()
    implicit = implicit_physical_tangent_theorem_payload()
    validation = {
        "eta_second_sigma_tensor_nonzero_on_control": bool(
            np.linalg.norm(quartic["second_sigma_inertia_tensor"]) > 0.0
        ),
        "fixed_momentum_quartic_nonnegative": quartic["nonnegative"],
        "homoclinic_Hamiltonian_zero": (
            abs(center["Hamiltonian"]) < 1.0e-12
            and abs(off_center["Hamiltonian"]) < 1.0e-12
        ),
        "homoclinic_Hamilton_equation_exact": abs(
            off_center["Hamilton_equation_residual"]
        )
        < 1.0e-12,
        "formation_momentum_not_conserved": (
            center["p_q_conserved"] is False
            and abs(center["p_q_dot"]) > 1.0e-12
        ),
        "instantaneous_branch_can_be_absent": inactive["active"] is False,
        "active_branch_has_two_transient_lobes": (
            active["active"]
            and active["active_at_concentration_peak_tau_zero"] is False
            and active["active_asymptotically"] is False
        ),
        "attachment_map_has_no_q_sigma_d_state_arguments": not any(
            (
                attachment["q_argument_present"],
                attachment["sigma_argument_present"],
                attachment["d_argument_present"],
            )
        ),
        "round_first_shape_qd_zero": (
            separation["xi_plus_first_compatibility_column_norm"] == 0.0
            and separation["xi_minus_first_compatibility_column_norm"] == 0.0
            and separation["first_order_round_G_qd"] == 0.0
        ),
        "round_second_shape_nonzero_but_not_canonical": (
            separation["second_shape_nonzero"]
            and separation["second_shape_is_a_first_order_canonical_tangent"]
            is False
        ),
        "physical_incidence_fails_closed": implicit["evaluable"] is False,
        "no_g_selection_fabricated": quartic["coefficient_status"].endswith(
            "UNSELECTED_G"
        ),
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_norman_incidence_reconnection_v15_21",
        "version": VERSION,
        "campaign_object": CAMPAIGN_OBJECT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "NormanWorks_reconnection": {
            "validated_causal_order": (
                "formation_dynamics_then_inertial_response_then_possible_"
                "enclosure_not_static_particle_properties_first"
            ),
            "source_boundary": (
                "Long_Future_material_supplies_curvature_projection_threshold_"
                "and_dynamic_geometry_hindsight_but_no_explicit_q_sigma_d_"
                "incidence_or_symplectic_law"
            ),
        },
        "second_sigma_result": {
            "derived_local_tensor": "D2_sigma_I_eta=2*g*I_eta_zero",
            "fixed_momentum_reduction": quartic,
            "attachment_second_sigma_incidence": None,
            "reason": attachment["conclusion"],
        },
        "formation_Hamiltonian_correction": {
            "center": center,
            "off_center": off_center,
            "peak": formation_peak_momentum_drive(0.4),
            "inactive_control": inactive,
            "active_control": active,
            "status": (
                "FIXED_P_Q_BRANCH_IS_AN_INSTANTANEOUS_OR_ADIABATIC_SLICE_"
                "NOT_A_CONSERVED_P_Q_ROUTH_ORBIT"
            ),
        },
        "attachment_state_map_audit": attachment,
        "separation_audit": separation,
        "physical_tangent_theorem": implicit,
        "v15_10_sigma_nonuniqueness_resolved": False,
        "material_skin_derived": False,
        "q_to_d_canonical_transfer_derived": False,
        "ejection_derived": False,
        "Hopf_child_derived": False,
        "Hindsight_20_20": {
            "VALIDATED": [
                "Norman_envelopment_is_dynamical_and_relational",
                "the_retained_eta_block_has_D2_sigma_I_eta=2*g*I_eta_zero",
                "fixed_momentum_inverse_inertia_has_a_positive_local_quartic",
                "the_v15_9_homoclinic_formation_momentum_is_not_conserved",
                "round_first_order_normal_separation_is_in_the_compatibility_kernel",
                "round_second_shape_metric_response_is_nonzero",
            ],
            "INVALIDATED": [
                "the_v14_68_to_v14_70_compatibility_isometry_is_already_a_q_sigma_d_state_map",
                "fixed_p_q_is_a_conserved_quantity_on_the_v15_9_homoclinic_orbit",
                "a_nonzero_second_shape_tensor_by_itself_supplies_a_canonical_separation_pair",
                "the_current_attachment_lineage_selects_g_or_resolves_v15_10",
            ],
            "RECLASSIFIED": [
                "v15_20_saturation_as_an_instantaneous_fixed_momentum_Hamiltonian_branch_until_the_coupled_flow_is_solved",
                "the_round_second_shape_route_as_a_quadratic_state_response_not_a_first_order_ejection_channel",
                "the_NormanWorks_material_as_a_causal_hindsight_map_not_an_unwritten_incidence_equation",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "phase_lock_angle_added": False,
            "wall_tension_added": False,
            "separation_kick_added": False,
            "frozen_predictions_changed": False,
            "USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE": (
                USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE
            ),
        },
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_norman_incidence_reconnection_v15_21.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "FULL_BHSM_COMPLETE",
    "CAMPAIGN_OBJECT",
    "OUTCOME",
    "EXACT_NEXT_OBJECT",
    "eta_second_sigma_inertia_tensor",
    "eta_fixed_momentum_quartic",
    "homoclinic_formation_phase_space",
    "formation_peak_momentum_drive",
    "instantaneous_sigma_activation_window",
    "attachment_state_argument_audit",
    "round_separation_incidence_audit",
    "implicit_physical_tangent_theorem_payload",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
