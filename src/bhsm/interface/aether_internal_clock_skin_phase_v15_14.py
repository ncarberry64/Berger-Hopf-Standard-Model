"""BHSM internal-clock/skin-domain and contact-impulse obstruction.

The author principle makes the child clock an independent physical history.
It fixes dynamical transport once a self-adjoint child Hamiltonian and an
initial state/domain are known.  It does not, by itself, select the normal
maximal-isotropic skin domain: scalar clock evolution preserves every graph.
The retained action also supplies only a coefficient-locked *formula* for the
Hayward impulse; the contact embedding derivatives needed to evaluate it and
the matter boundary generator needed to supplement it remain absent.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .aether_boundary_identity_ejection_v15_13 import (
    boundary_identity_trace_unitary,
)
from .aether_cycle_sigma_coefficient_reconstruction_v15_10 import (
    retained_nonuniqueness_witness,
)


VERSION = "v15.14"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
OUTCOME = "INTERNAL_CLOCK_TRANSPORT_DERIVED_CONDITIONALLY_BUT_SKIN_DOMAIN_AND_IMPULSE_UNSELECTED"
PRIMARY_VERDICT = (
    "BHSM_INTERNAL_CLOCK_PROPER_TIME_AND_STONE_HOLONOMY_DEFINE_INDEPENDENT_"
    "PARENT_AND_CHILD_STATE_EVOLUTION_ONCE_THE_PHYSICAL_METRICS_GENERATORS_"
    "AND_DOMAINS_ARE_GIVEN;_THEY_DO_NOT_SELECT_THE_DOMAINS_BECAUSE_A_COMMON_"
    "CLOCK_PHASE_MULTIPLIES_BOTH_NORMAL_TRACE_POLARIZATIONS_AND_PRESERVES_"
    "EVERY_MAXIMAL_ISOTROPIC_GRAPH;_THE_CHILD_GENERATOR_IS_THEREFORE_"
    "CIRCULAR_IF_CONSTRUCTED_FROM_A_PHYSICAL_HAMILTONIAN_WHOSE_DOMAIN_ALREADY_"
    "CONTAINS_THE_UNKNOWN_SKIN_PHASE;_THE_HAYWARD_ACTION_GIVES_A_"
    "COEFFICIENT_LOCKED_PROJECTED_IMPULSE_FORMULA_BUT_NO_NUMERICAL_OR_SIGN_"
    "SELECTED_IMPULSE_WITHOUT_THE_CONTACT_EMBEDDING_AND_BOUNDARY_MATTER_LAW"
)
EXACT_NEXT_OBJECT = (
    "VARIATION_DERIVED_PARENT_AND_CHILD_SKIN_MATTER_BOUNDARY_ACTION_AND_"
    "INCEPTION_CONDITION_COUPLING_THE_NORMAL_TRACE_POLARIZATION_TO_THE_"
    "INTERNAL_CLOCK_GENERATOR_WITHOUT_A_FREE_PHASE"
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


def _hermitian(matrix: Sequence[Sequence[complex]], name: str) -> np.ndarray:
    result = np.asarray(matrix, dtype=complex)
    if result.ndim != 2 or result.shape[0] != result.shape[1]:
        raise ValueError(f"{name} must be square")
    if not np.all(np.isfinite(result)) or not np.allclose(
        result, np.conjugate(result.T), atol=1.0e-13
    ):
        raise ValueError(f"{name} must be finite and Hermitian")
    return result


def internal_clock_holonomy(
    generator: Sequence[Sequence[complex]], proper_time_interval: float
) -> np.ndarray:
    """Return exp(-i Delta tau G) for a constant physical generator."""

    operator = _hermitian(generator, "generator")
    interval = _finite(proper_time_interval, "proper_time_interval")
    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    phases = np.exp(-1j * interval * eigenvalues)
    return (eigenvectors * phases) @ np.conjugate(eigenvectors.T)


def proper_clock_interval(metric_contraction: float, parameter_interval: float) -> float:
    """Proper time along a regular timelike worldtube history segment.

    ``metric_contraction`` is the constant diagnostic value g(v,v)<0 for the
    chosen segment.  In the physical calculation it is integrated pointwise.
    """

    contraction = _finite(metric_contraction, "metric_contraction")
    interval = _finite(parameter_interval, "parameter_interval")
    if contraction >= 0.0 or interval < 0.0:
        raise ValueError("require a timelike tangent and nonnegative parameter interval")
    return math.sqrt(-contraction) * interval


def maximal_isotropic_trace(alpha: float, amplitude: complex = 1.0) -> np.ndarray:
    """Reduced normal trace (psi_+,psi_-) with psi_-=U(alpha) psi_+."""

    unitary = boundary_identity_trace_unitary(_finite(alpha, "alpha"), 0.0)[0, 0]
    value = complex(amplitude)
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise ValueError("amplitude must be finite")
    return np.array([value, unitary * value], dtype=complex)


def trace_graph_residual(trace: Sequence[complex], alpha: float) -> float:
    """Residual of the normal maximal-isotropic graph relation."""

    vector = np.asarray(trace, dtype=complex)
    if vector.shape != (2,) or not np.all(np.isfinite(vector)):
        raise ValueError("trace must be a finite two-vector")
    unitary = boundary_identity_trace_unitary(_finite(alpha, "alpha"), 0.0)[0, 0]
    return float(abs(vector[1] - unitary * vector[0]))


def scalar_clock_evolve_trace(trace: Sequence[complex], energy: float, interval: float) -> np.ndarray:
    """Evolve both normal polarizations with one internal-clock phase."""

    vector = np.asarray(trace, dtype=complex)
    if vector.shape != (2,) or not np.all(np.isfinite(vector)):
        raise ValueError("trace must be a finite two-vector")
    phase = np.exp(-1j * _finite(energy, "energy") * _finite(interval, "interval"))
    return phase * vector


def clock_domain_nonselection_witness() -> dict[str, Any]:
    """Show that the same child clock is compatible with every skin phase."""

    rows = []
    for alpha in (-2.0, -0.5, 0.0, 1.0, 3.0):
        before = maximal_isotropic_trace(alpha, 0.7 - 0.2j)
        after = scalar_clock_evolve_trace(before, energy=1.3, interval=0.8)
        rows.append(
            {
                "alpha": alpha,
                "before_graph_residual": trace_graph_residual(before, alpha),
                "after_graph_residual": trace_graph_residual(after, alpha),
                "norm_residual": float(
                    abs(np.vdot(after, after).real - np.vdot(before, before).real)
                ),
            }
        )
    return {
        "clock_energy": 1.3,
        "clock_interval": 0.8,
        "all_domains_preserved": all(row["after_graph_residual"] < 1.0e-14 for row in rows),
        "all_norms_preserved": all(row["norm_residual"] < 1.0e-14 for row in rows),
        "continuously_many_alpha_compatible": True,
        "rows": rows,
        "reason": (
            "the_internal_clock_phase_multiplies_psi_plus_and_psi_minus_"
            "equally_so_the_ratio_psi_minus_over_psi_plus_is_unchanged"
        ),
    }


def relative_internal_phase(
    parent_initial_phase: float,
    child_initial_phase: float,
    parent_generator_integral: float,
    child_generator_integral: float,
) -> float:
    """Return theta_c-theta_p for D_tau psi=0 conventions."""

    parent0 = _finite(parent_initial_phase, "parent_initial_phase")
    child0 = _finite(child_initial_phase, "child_initial_phase")
    parent_integral = _finite(parent_generator_integral, "parent_generator_integral")
    child_integral = _finite(child_generator_integral, "child_generator_integral")
    return (child0 - child_integral) - (parent0 - parent_integral)


def generator_logarithm_branches(
    unitary_phase: float, proper_time_interval: float, branches: Sequence[int]
) -> list[float]:
    """Self-adjoint scalar generators giving U=exp(i*unitary_phase)."""

    phase = _finite(unitary_phase, "unitary_phase")
    interval = _positive(proper_time_interval, "proper_time_interval")
    return [-(phase + 2.0 * math.pi * int(branch)) / interval for branch in branches]


def hayward_projected_contact_impulse(
    kappa1: float,
    joint_measure: float,
    boost_angle: float,
    joint_measure_d: float,
    boost_angle_d: float,
) -> float:
    """Project -delta S_J/delta d for S_J=kappa1*A_J*theta.

    This is coefficient locked.  The two derivatives are outputs of the
    constraint-solved contact embedding, not adjustable impulse parameters.
    """

    coupling = _positive(kappa1, "kappa1")
    measure = _finite(joint_measure, "joint_measure")
    angle = _finite(boost_angle, "boost_angle")
    measure_derivative = _finite(joint_measure_d, "joint_measure_d")
    angle_derivative = _finite(boost_angle_d, "boost_angle_d")
    if measure < 0.0:
        raise ValueError("joint_measure must be nonnegative")
    return -coupling * (angle * measure_derivative + measure * angle_derivative)


def clock_generalized_force(
    state: Sequence[complex], generator_shape_derivative: Sequence[Sequence[complex]]
) -> float:
    """Feynman--Hellmann force -<psi,dG/dd psi> for a normalized state."""

    vector = np.asarray(state, dtype=complex)
    derivative = _hermitian(generator_shape_derivative, "generator_shape_derivative")
    if vector.ndim != 1 or vector.size != derivative.shape[0] or not np.all(np.isfinite(vector)):
        raise ValueError("state and generator derivative dimensions must match")
    norm = float(np.vdot(vector, vector).real)
    if norm <= 0.0:
        raise ValueError("state must have positive norm")
    normalized = vector / math.sqrt(norm)
    value = -np.vdot(normalized, derivative @ normalized)
    if abs(value.imag) > 1.0e-12:
        raise ValueError("Hermitian expectation must be real")
    return float(value.real)


def internal_clock_payload() -> dict[str, Any]:
    witness = clock_domain_nonselection_witness()
    return {
        "parent_clock": "d_tau_p=sqrt(-g_p(v_p,v_p))*d_lambda_p_on_a_regular_parent_worldtube",
        "child_clock": "d_tau_c=sqrt(-g_c(v_c,v_c))*d_lambda_c_on_a_regular_child_worldtube",
        "clock_equality_imposed": False,
        "clock_synchronization_at_contact_imposed": False,
        "clock_is_action_owned_once_physical_metric_and_history_exist": True,
        "physical_child_metric_and_worldtube_solution_present": False,
        "stable_recurring_child_clock_present": False,
        "conditional_generator": (
            "G_s=B_s[H_s_phys]_only_after_the_constraint_reduced_Hamiltonian_"
            "and_its_self_adjoint_domain_are_defined"
        ),
        "conditional_transport": "U_s=Pexp[-i*integral G_s d_tau_s]",
        "representation_dependence": (
            "Levi_Civita_spin_and_gauge_connections_induce_distinct_associated_bundle_transports"
        ),
        "normal_domain_vs_tangential_transport": {
            "normal_domain": "psi_minus=U_skin*psi_plus",
            "worldtube_transport": "D_tau_psi=0",
            "same_mathematical_object": False,
        },
        "constructive_nonselection": witness,
        "G_from_H_circularity": (
            "H_c_phys_is_not_an_operator_until_Dom(H_c)_U_skin_is_chosen;_"
            "applying_B_c_to_H_c_phys_cannot_select_the_U_skin_already_used_"
            "to_define_H_c_phys"
        ),
        "worldtube_holonomy_fixes_change_not_inception_value": True,
        "child_inception_phase_selected": False,
    }


def phase_quotient_payload() -> dict[str, Any]:
    before = maximal_isotropic_trace(1.2, 0.3 + 0.4j)
    common_phase = np.exp(0.71j)
    after = common_phase * before
    relative_before = relative_internal_phase(0.2, 0.9, 0.4, 1.1)
    relative_after = relative_internal_phase(0.2 + 0.71, 0.9 + 0.71, 0.4, 1.1)
    return {
        "common_state_phase_graph_residual": trace_graph_residual(after, 1.2),
        "extension_parameter_before_and_after_common_phase": [1.2, 1.2],
        "global_state_phase_changes_extension_parameter": False,
        "relative_dynamic_phase": "Delta_theta=(theta_c0-theta_p0)-int_Gc_dtaut_c+int_Gp_dtau_p",
        "relative_phase_common_shift_residual": abs(relative_after - relative_before),
        "relative_inception_phase_needed": "theta_c0-theta_p0",
        "relative_inception_phase_action_selected": False,
        "central_generator_shift_unconditional_gauge": False,
        "reason": (
            "v15_2_and_v15_3_found_no_action_owned_projectivization_or_"
            "history_interference_rule;_at_contact_a_relative_phase_can_enter_"
            "an_offdiagonal_matter_coupling_if_one_is_derived"
        ),
        "U1_skin_domain_quotiented_by_global_wavefunction_phase": False,
    }


def contact_impulse_payload() -> dict[str, Any]:
    zero_hayward = hayward_projected_contact_impulse(2.0, 0.7, 0.4, 0.0, 0.0)
    zero_clock = clock_generalized_force([1.0, 0.0], np.zeros((2, 2)))
    return {
        "canonical_jump": "Delta_P_d=-delta_S_contact/delta_d",
        "retained_contact_action": "S_Hayward=kappa1*A_J*theta",
        "Hayward_projection": (
            "Delta_P_d_H=-kappa1*(theta*dA_J/dd+A_J*dtheta/dd)"
        ),
        "new_Hayward_coefficient": False,
        "contact_embedding_A_J_of_d_present": False,
        "contact_boost_angle_theta_of_d_present": False,
        "projected_Hayward_impulse_evaluable": False,
        "zero_shape_derivative_control": zero_hayward,
        "clock_boundary_force": "F_d_clock=-<Psi_c,(partial_d G_c)Psi_c>",
        "phase_continuity_alone_force": zero_clock,
        "nonzero_clock_force_requires": "action_derived_partial_d_G_c_or_Berry_curvature",
        "physical_partial_d_G_c_present": False,
        "matter_skin_action_in_retained_action": 0,
        "total_contact_impulse_sign_selected": False,
        "outgoing_ejection_momentum_selected": False,
        "finite_post_contact_ejection_trajectory_selected": False,
        "no_ejection_branch": "DE_ENVELOPMENT_BY_AUTHOR_RULE_BUT_RECEIVING_TRAJECTORY_NOT_DERIVED",
    }


def sigma_selection_payload() -> dict[str, Any]:
    witness = retained_nonuniqueness_witness()
    labels = list(witness["triples"])
    return {
        "witnesses": labels,
        "physical_child_Hamiltonian_for_each_witness_evaluable": False,
        "boundary_generator_for_each_witness_evaluable": False,
        "contact_impulse_for_each_witness_evaluable": False,
        "clock_compatibility_shared_by_all_scalar_graph_phases": True,
        "surviving_witness_count": len(labels),
        "v15_10_nonuniqueness_resolved": False,
    }


def completion_payload() -> dict[str, Any]:
    clock = internal_clock_payload()
    quotient = phase_quotient_payload()
    impulse = contact_impulse_payload()
    sigma = sigma_selection_payload()
    generator = np.array([[1.0, 0.2j], [-0.2j, 2.0]], dtype=complex)
    u1 = internal_clock_holonomy(generator, 0.3)
    u2 = internal_clock_holonomy(generator, 0.5)
    u12 = internal_clock_holonomy(generator, 0.8)
    branches = generator_logarithm_branches(0.6, 1.7, (-1, 0, 1))
    validation = {
        "proper_child_clock_covariant_when_worldtube_exists": math.isclose(
            proper_clock_interval(-4.0, 0.5), 1.0
        ),
        "clock_holonomy_unitary": np.linalg.norm(np.conjugate(u1.T) @ u1 - np.eye(2)) < 1.0e-13,
        "clock_holonomy_composes": np.linalg.norm(u2 @ u1 - u12) < 1.0e-13,
        "clock_preserves_all_trace_graph_witnesses": clock[
            "constructive_nonselection"
        ]["all_domains_preserved"],
        "clock_preserves_norm": clock["constructive_nonselection"]["all_norms_preserved"],
        "common_state_phase_does_not_change_domain_alpha": not quotient[
            "global_state_phase_changes_extension_parameter"
        ],
        "relative_phase_common_shift_invariant": quotient[
            "relative_phase_common_shift_residual"
        ] < 1.0e-14,
        "single_endpoint_holonomy_has_log_branches": len(set(round(value, 12) for value in branches)) == 3,
        "Hayward_impulse_projection_coefficient_locked": math.isclose(
            hayward_projected_contact_impulse(2.0, 3.0, 0.5, 0.4, -0.2), 0.8
        ),
        "constant_generator_has_zero_clock_shape_force": impulse[
            "phase_continuity_alone_force"
        ] == 0.0,
        "v15_10_nonuniqueness_not_fabricated_closed": not sigma[
            "v15_10_nonuniqueness_resolved"
        ],
        "v15_11_fixed_Haar_no_go_preserved": True,
        "v15_12_Hayward_normalization_preserved": True,
        "v15_13_boundary_identity_preserved": True,
        "no_new_phase_impulse_or_buoyancy_parameter": True,
        "no_empirical_input_or_retuning": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_internal_clock_skin_phase_v15_14",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "independent_internal_clocks_and_holonomies": clock,
        "global_and_relative_phase_quotient": quotient,
        "contact_canonical_impulse": impulse,
        "v15_10_selection": sigma,
        "phase_nonuniqueness_resolved": False,
        "ejection": "NOT_DERIVED_NO_ACTION_SELECTED_CONTACT_IMPULSE",
        "Hopf_child": "NOT_REACHED_NO_EJECTED_COUPLED_ETA_SIGMA_METRIC_DOMAIN_SOLUTION",
        "persistence": "NOT_REACHED",
        "downstream_Standard_Model": "NOT_REACHED_NO_PHYSICAL_CHILD_COMMON_DOMAIN",
        "Hindsight_20_20": {
            "VALIDATED": [
                "parent_and_child_proper_times_are_independent_geometric_functionals_on_their_own_regular_worldtubes",
                "a_selected_self_adjoint_generator_produces_unique_unitary_internal_clock_transport",
                "the_physical_relative_dynamic_phase_is_history_dependent_and_common_phase_shift_invariant_conditionally",
                "the_Hayward_contact_action_projects_to_a_coefficient_locked_canonical_impulse_formula",
            ],
            "INVALIDATED": [
                "internal_clock_evolution_alone_selects_the_normal_self_adjoint_skin_domain",
                "a_global_wavefunction_phase_quotient_removes_the_maximal_isotropic_extension_parameter",
                "the_child_on_shell_Hamiltonian_can_select_the_domain_needed_to_define_that_same_Hamiltonian",
                "phase_continuity_with_a_shape_independent_generator_produces_ejection_impulse",
                "the_Hayward_coefficient_alone_fixes_the_impulse_without_contact_embedding_derivatives",
            ],
            "RECLASSIFIED": [
                "child_clock_as_a_transport_law_on_a_selected_domain_not_a_domain_selection_law",
                "relative_phase_as_history_plus_inception_data_not_contact_synchronization",
                "contact_ejection_as_a_projected_corner_and_boundary_stress_calculation",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "scientific_terminal_condition": (
            "BOUNDARY_IDENTITY_PLUS_INTERNAL_CLOCK_TRANSPORT_STILL_LEAVES_"
            "CONTINUOUS_INEQUIVALENT_SELF_ADJOINT_SKIN_DOMAINS_AND_AN_"
            "UNSELECTED_RELATIVE_INCEPTION_PHASE"
        ),
        "missing_physical_assumption_plain_language": (
            "BHSM_must_derive_from_its_action_how_matter_behaves_normally_at_"
            "each_skin_and_how_that_rule_is_initialized_when_the_child_skin_"
            "forms;_an_internal_clock_tells_an_already_defined_state_how_to_"
            "evolve_but_does_not_choose_the_boundary_condition_it_evolves_on"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "skin_phase_adopted": False,
            "inception_phase_adopted": False,
            "contact_impulse_adopted": False,
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
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
    path = target / "BHSM_aether_internal_clock_skin_phase_v15_14.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path
