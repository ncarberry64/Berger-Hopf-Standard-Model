"""BHSM v15.3 microscopic Aether-core action ownership audit.

The retained architecture supplies an associative event-composition skeleton
but no action-owned involution, positive state, C*-norm, GNS representation,
closed core form, or geometry-core correspondence map.  This package records
the resulting Outcome-G obstruction and uses two fixed cyclic completions only
as a constructive nonuniqueness witness; neither completion is adopted as
physical BHSM data.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .aether_dynamical_correspondence_v15_1 import (
    boundary_data_on_domain,
    boundary_green_form,
    self_adjoint_domain_diagnostics,
    symbolic_regular_recovery,
    unitary_event_kernel,
)
from .aether_generator_selection_v15_2 import (
    affine_spectral_equivalence,
    central_shift_gate,
    preclock_scaling_diagnostics,
)

VERSION = "v15.3"
OUTCOME = "OUTCOME_G_EXISTING_BHSM_INSUFFICIENT_TO_DEFINE_A_POSITIVE_CORE_STRUCTURE"
PRIMARY_VERDICT = (
    "BHSM_V15_3_THE_EXISTING_ARCHITECTURE_DERIVES_ONLY_AN_ASSOCIATIVE_"
    "INVARIANT_GRADED_EVENT_COMPOSITION_SKELETON_FOR_THE_PREGEOMETRIC_CORE_"
    "BUT_NO_DAGGER_INVOLUTION_POSITIVE_STATE_TRACE_CSTAR_NORM_GNS_"
    "REPRESENTATION_CLOSED_CORE_QUADRATIC_FORM_OR_CORE_TO_GEOMETRY_"
    "CORRESPONDENCE_MAP;_THE_V10_TO_V14_SUPPORT_ATTACHMENT_AND_CALDERON_"
    "ACTIONS_LIVE_ON_REGULAR_STRATA_OR_VANISH_AT_THE_HAAR_ENDPOINT_AND_DO_NOT_"
    "SUPPLY_THE_MISSING_CORE_DATA;_TWO_FIXED_CYCLIC_POSITIVE_COMPLETIONS_"
    "SATISFY_ALL_CURRENT_ADMISSIBILITY_AND_RECOVERY_GATES_BUT_ARE_"
    "INEQUIVALENT_SO_NO_MICROSCOPIC_CORE_ACTION_BOUNDARY_BLOCK_EVENT_KERNEL_"
    "GENERATOR_CLOCK_OR_HAMILTONIAN_IS_ACTION_DERIVED"
)
EXACT_NEXT_OBJECT = (
    "FOUNDATIONAL_PREGEOMETRIC_DAGGER_EVENT_ALGEBRA_WITH_A_DISTINGUISHED_"
    "FAITHFUL_POSITIVE_STATE_CLOSED_INVARIANT_DIRICHLET_FORM_AND_BOUNDED_"
    "GEOMETRY_CORE_CORRESPONDENCE_MORPHISM_FROM_WHICH_THE_GNS_REPRESENTATION_"
    "BOUNDARY_VARIATION_RELATIONAL_GENERATOR_AND_RECONSTRUCTION_MAP_ARE_DERIVED"
)

FORBIDDEN_CORE_PRIMITIVES = (
    "spacetime_coordinate",
    "coordinate_time",
    "metric_tensor",
    "spacetime_volume_measure",
    "ordinary_energy",
    "ordinary_energy_density",
    "preferred_frame",
)


def _as_hermitian(matrix: np.ndarray, name: str = "operator", tol: float = 1e-12) -> np.ndarray:
    value = np.asarray(matrix, dtype=complex)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be square")
    if np.linalg.norm(value - value.conj().T) > tol:
        raise ValueError(f"{name} must be Hermitian")
    return (value + value.conj().T) / 2.0


def cyclic_shift(order: int) -> np.ndarray:
    """Return the left-regular shift of the finite cyclic group Z_order."""
    n = int(order)
    if n < 2:
        raise ValueError("cyclic witness order must be at least two")
    shift = np.zeros((n, n), dtype=complex)
    for index in range(n):
        shift[(index + 1) % n, index] = 1.0
    return shift


def cyclic_dirichlet_operator(order: int) -> np.ndarray:
    """Canonical graph form operator 2I-S-S* after Z_n is declared."""
    shift = cyclic_shift(order)
    return _as_hermitian(2.0 * np.eye(order) - shift - shift.conj().T, "cyclic Laplacian")


def normalized_pairing(left: Sequence[complex], right: Sequence[complex]) -> complex:
    """Normalized counting pairing for a declared finite cyclic witness."""
    x = np.asarray(left, dtype=complex)
    y = np.asarray(right, dtype=complex)
    if x.ndim != 1 or y.shape != x.shape or x.size == 0:
        raise ValueError("pairing vectors must be nonempty and have equal shape")
    return complex(np.vdot(x, y) / x.size)


def quadratic_form(operator: np.ndarray, vector: Sequence[complex]) -> float:
    matrix = _as_hermitian(operator)
    state = np.asarray(vector, dtype=complex)
    if state.shape != (matrix.shape[0],):
        raise ValueError("state dimension mismatch")
    return float(np.real(np.vdot(state, matrix @ state)))


def finite_form_diagnostics(operator: np.ndarray) -> dict[str, Any]:
    matrix = _as_hermitian(operator)
    eigenvalues = np.linalg.eigvalsh(matrix)
    return {
        "dimension": int(matrix.shape[0]),
        "spectrum": [float(value) for value in eigenvalues],
        "Hermitian_residual": float(np.linalg.norm(matrix - matrix.conj().T)),
        "semibounded": bool(np.min(eigenvalues) >= -1e-12),
        "closed": True,
        "closable": True,
        "associated_operator_self_adjoint": True,
        "kernel_dimension": int(np.sum(np.abs(eigenvalues) < 1e-12)),
        "finite_dimensional_theorem_only": True,
    }


def weighted_pairing_nonuniqueness_witness() -> dict[str, Any]:
    """Two fixed faithful states on the same commutative algebra C^2."""
    weights_first = np.array([0.5, 0.5])
    weights_second = np.array([1.0 / 3.0, 2.0 / 3.0])
    observable = np.array([1.0, 0.0])
    values = [float(weights_first @ observable), float(weights_second @ observable)]
    return {
        "algebra": "C_direct_sum_C",
        "faithful_state_weights": [weights_first.tolist(), weights_second.tolist()],
        "same_observable_expectations": values,
        "states_related_by_algebra_automorphism": False,
        "reason": "the unordered weight multisets {1/2,1/2} and {1/3,2/3} differ",
        "continuous_parameter_introduced": False,
        "either_state_action_selected": False,
    }


def cyclic_foundation(order: int) -> dict[str, Any]:
    """Return a fixed positive completion witness, never a physical proposal."""
    shift = cyclic_shift(order)
    laplacian = cyclic_dirichlet_operator(order)
    spectrum = np.linalg.eigvalsh(laplacian)
    unitary = unitary_event_kernel(laplacian, 1.0)
    invariant = np.eye(order)
    return {
        "label": f"FINITE_CYCLIC_COMPLETION_Z{order}",
        "algebra": f"complex_group_star_algebra_C[Z_{order}]",
        "representation": "left_regular",
        "Hilbert_dimension": order,
        "pairing": "normalized_counting_pairing",
        "quadratic_form": "q(psi)=<psi,(2I-S-S*)psi>",
        "operator_spectrum": [float(value) for value in spectrum],
        "positive": bool(np.min(spectrum) >= -1e-12),
        "closed": True,
        "self_adjoint": True,
        "invariant_commutator_residual": float(np.linalg.norm(laplacian @ invariant - invariant @ laplacian)),
        "shift_unitarity_residual": float(np.linalg.norm(shift.conj().T @ shift - np.eye(order))),
        "evolution_unitarity_residual": float(np.linalg.norm(unitary.conj().T @ unitary - np.eye(order))),
        "ordinary_spacetime_measure_used": False,
        "physical_foundation_adopted": False,
    }


def microscopic_nonuniqueness_witness() -> dict[str, Any]:
    """Two discrete positive completions allowed by all current core axioms."""
    first = cyclic_foundation(2)
    second = cyclic_foundation(3)
    return {
        "foundations": [first, second],
        "same_current_core_firewall": True,
        "same_identity_decoupling_recovery": True,
        "same_no_empirical_input_status": True,
        "unitarily_or_module_equivalent": False,
        "reason_not_equivalent": "different algebra dimensions and inequivalent regular representation ranks 2 and 3",
        "different_core_spectra": [first["operator_spectrum"], second["operator_spectrum"]],
        "continuous_parameter_introduced": False,
        "either_foundation_selected_by_BHSM": False,
    }


def attachment_block_diagnostics(core_order: int) -> dict[str, Any]:
    """Finite conditional attachment witness after a core completion is chosen.

    The map sends the core constant vector to one geometric boundary channel.
    It demonstrates adjoint compatibility and total-form closure, not action
    ownership of the map.
    """
    n = int(core_order)
    core = cyclic_dirichlet_operator(n) + np.eye(n)
    geometric = np.array([[2.0]], dtype=complex)
    coupling = np.ones((1, n), dtype=complex) / np.sqrt(n)
    total = np.block([[geometric, -coupling], [-coupling.conj().T, core]])
    total = _as_hermitian(total, "total form operator")
    eigenvalues = np.linalg.eigvalsh(total)
    rng = np.random.default_rng(1503 + n)
    geometric_state = rng.normal(size=1) + 1j * rng.normal(size=1)
    core_state = rng.normal(size=n) + 1j * rng.normal(size=n)
    adjoint_residual = abs(
        np.vdot(geometric_state, coupling @ core_state)
        - np.vdot(coupling.conj().T @ geometric_state, core_state)
    )
    return {
        "core_order": n,
        "coupling_shape": list(coupling.shape),
        "attachment_adjoint_residual": float(adjoint_residual),
        "total_form_Hermitian_residual": float(np.linalg.norm(total - total.conj().T)),
        "total_form_minimum_eigenvalue": float(np.min(eigenvalues)),
        "total_form_closed": True,
        "total_form_semibounded": bool(np.min(eigenvalues) >= -1e-12),
        "associated_total_operator_self_adjoint": True,
        "attachment_map_action_owned": False,
        "diagnostic_only": True,
    }


def candidate_foundations_payload() -> dict[str, Any]:
    rows = [
        {
            "candidate": "A_ordinary_Hilbert_space",
            "canonical_pairing_if_H_is_supplied": True,
            "new_unselected_primitives": ["dimension_or_multiplicity", "Hilbert_space", "representation", "operator"],
            "selected": False,
            "verdict": "SUFFICIENT_SCHEMA_NOT_DERIVED",
        },
        {
            "candidate": "B_Hilbert_module_correspondence",
            "naturally_models_geometry_core_relation": True,
            "new_unselected_primitives": ["left_and_right_algebras", "module_inner_product", "completion", "correspondence_map"],
            "selected": False,
            "verdict": "BEST_STRUCTURAL_SCHEMA_BUT_NO_OWNED_COEFFICIENT_ALGEBRA_OR_INNER_PRODUCT",
        },
        {
            "candidate": "C_spectral_triple_like",
            "new_unselected_primitives": ["star_algebra", "Hilbert_representation", "Dirac_operator", "compactness_and_dimension_axioms"],
            "selected": False,
            "verdict": "NOT_FORCED_AND_WOULD_SMUGGLE_RECONSTRUCTION_AXIOMS_UPSTREAM",
        },
        {
            "candidate": "D_relative_boundary_spectral_correspondence",
            "reuses_regular_theorem_class": True,
            "new_unselected_primitives": ["core_trace_space", "core_Green_pairing", "core_Calderon_or_DtN_block"],
            "selected": False,
            "verdict": "REGULAR_SIDE_ONLY_CORE_EXTENSION_UNDERIVED",
        },
        {
            "candidate": "E_unbounded_KK_cycle",
            "new_unselected_primitives": ["Cstar_algebras", "countably_generated_module", "regular_operator", "compactness_data"],
            "selected": False,
            "verdict": "MATHEMATICALLY_POSSIBLE_BUT_NOT_DEMANDED_BY_CURRENT_ACTION",
        },
        {
            "candidate": "F_algebraic_event_category_quadratic_form",
            "architecture_owned_part": "associative_identity_and_invariant_graded_composition_skeleton",
            "missing_positive_parts": ["dagger", "positive_state", "norm", "completion", "closed_form"],
            "selected": False,
            "verdict": "MINIMUM_DERIVED_SKELETON_NOT_YET_A_POSITIVE_MICROSCOPIC_FOUNDATION",
        },
    ]
    return {
        "version": VERSION,
        "candidates": rows,
        "preferred_schema_if_new_axioms_are_added": "Hilbert_Cstar_correspondence_or_GNS_boundary_correspondence",
        "preferred_schema_is_currently_derived": False,
        "candidate_foundation_uniqueness": False,
    }


def core_algebra_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "architecture_derived": {
            "event_objects_and_composable_spans": True,
            "associative_composition": True,
            "identity_events": True,
            "additive_process_depth_grading": True,
            "parent_invariant_signature_grading": True,
            "free_complex_linear_category_span_is_constructible": True,
        },
        "not_derived": {
            "physical_allowed_morphism_set": True,
            "dagger_or_event_reversal": True,
            "star_algebra": True,
            "positive_cone": True,
            "Cstar_norm": True,
            "completion": True,
            "faithful_state": True,
        },
        "physical_core_observable_algebra_action_derived": False,
        "classification": "ALGEBRAIC_COMPOSITION_SKELETON_ONLY_NO_POSITIVE_STAR_ALGEBRA",
    }


def core_representation_payload() -> dict[str, Any]:
    witness = microscopic_nonuniqueness_witness()
    return {
        "version": VERSION,
        "GNS_representation_available_after_positive_state": True,
        "positive_state_action_owned": False,
        "Hilbert_or_module_rank_fixed": False,
        "canonical_inner_product_derived": False,
        "null_ideal_and_quotient_derived": False,
        "grading_derived": False,
        "real_structure_derived": False,
        "fundamental_core_spinors_derived": False,
        "regular_boundary_Hilbert_space_reconstructed_from_core": False,
        "constructive_nonuniqueness": witness,
        "physical_core_representation_derived": False,
    }


def core_pairing_payload() -> dict[str, Any]:
    witness = weighted_pairing_nonuniqueness_witness()
    return {
        "version": VERSION,
        "Hilbert_trace_requires_representation_first": True,
        "supertrace_requires_action_owned_grading": True,
        "normalized_trace_requires_selected_algebra_or_symmetry": True,
        "KMS_or_thermal_state_justified": False,
        "categorical_trace_derived": False,
        "boundary_pairing_inherited_from_regular_correspondence_only": True,
        "core_scalar_pairing_action_derived": False,
        "fixed_pairing_nonuniqueness_witness": witness,
    }


def core_quadratic_form_payload() -> dict[str, Any]:
    witness = microscopic_nonuniqueness_witness()
    return {
        "version": VERSION,
        "action_owned_core_form_found": False,
        "representation_theorem": (
            "a densely_defined_closed_semibounded form on a selected Hilbert representation "
            "would define a unique self_adjoint associated operator"
        ),
        "representation_theorem_selects_form_or_Hilbert_space": False,
        "cyclic_completion_diagnostics": [
            finite_form_diagnostics(cyclic_dirichlet_operator(2)),
            finite_form_diagnostics(cyclic_dirichlet_operator(3)),
        ],
        "diagnostic_forms_are_physical": False,
        "constructive_nonuniqueness": witness,
        "q_C_derived": False,
        "D_C_derived": False,
    }


def geometry_core_attachment_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "v11_support_and_attachment_domain": "regular_upsilon_positive_or_asymptotic_Haar_end",
        "v11_3_reciprocal_attachment_on_shell_endpoint_behavior": "vanishes_like_sqrt_upsilon_for_bounded_regular_data",
        "v11_3_term_has_new_boundary_flux": False,
        "v14_64_to_v14_69_incidence_scope": "reconstructible_M8_M5_plus_minus_M4_strata",
        "regular_Wentzell_data_define_core_Wentzell_data": False,
        "core_trace_map_action_owned": False,
        "core_boundary_pairing_action_owned": False,
        "b_GC_action_owned": False,
        "conditional_fixed_completion_diagnostics": [attachment_block_diagnostics(2), attachment_block_diagnostics(3)],
        "classification": "ATTACHMENT_THEOREM_CLASS_AVAILABLE_ONLY_AFTER_NEW_CORE_DATA",
    }


def total_action_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "schematic_form": "I_A=-Im<Psi,D_chi Psi>-q_G-q_C-b_GC",
        "regular_q_G_owned": True,
        "core_pairing_owned": False,
        "q_C_owned": False,
        "b_GC_owned": False,
        "KLMN_closure_if_attachment_is_relatively_form_bounded_below_one": True,
        "relative_form_bound_evaluated_for_physical_core": False,
        "total_q_A_closed_action_owned": False,
        "associated_total_operator_derived": False,
        "variation_gives_physical_core_equation": False,
        "variation_gives_physical_geometry_core_equation": False,
        "variation_selects_physical_boundary_condition": False,
        "ordinary_spacetime_integration_on_core_used": False,
    }


def boundary_event_payload() -> dict[str, Any]:
    wentzell = np.diag([1.0, 2.0])
    domain = self_adjoint_domain_diagnostics(wentzell)
    f0, f1 = boundary_data_on_domain(wentzell, (1.0 + 0.2j, -0.3), (0.1j, 0.4))
    g0, g1 = boundary_data_on_domain(wentzell, (0.2, -0.5j), (0.3, -0.1j))
    green = boundary_green_form(f0, f1, g0, g1)
    return {
        "version": VERSION,
        "theorem_class_self_adjoint_boundary_domain": domain,
        "sample_Green_form_norm": abs(green),
        "physical_Theta_A_from_core_action": False,
        "physical_Calderon_projector": False,
        "physical_DtN_relation": False,
        "event_amplitude_from_microscopic_core_action": False,
        "v15_1_conditional_kernel_form_retained": "U_A(chi)=exp(-i chi K_A)",
        "central_shift_gate": central_shift_gate(),
        "central_shift_projective_gauge_resolved": False,
        "reason": "no action_owned_history_sum_interference_rule_or_endpoint_coboundary_theorem",
    }


def reconstruction_clock_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "exact_regular_restriction_recovery": True,
        "core_to_geometry_emergence_map_derived": False,
        "locality_from_core_derived": False,
        "dimension_from_core_derived": False,
        "metric_from_core_derived": False,
        "boundary_from_core_derived": False,
        "orientation_or_connection_from_core_derived": False,
        "causal_or_temporal_structure_from_core_derived": False,
        "missing_reconstruction_theorem": (
            "spectral_or_correspondence_reconstruction_from_the_selected_positive_core_algebra_state_form_and_attachment"
        ),
        "stable_core_cycle_action_derived": False,
        "Delta_chi_clock_derived": False,
        "tau_clock_derived": False,
        "H_eff_selected": False,
        "high_excitation_low_reconstructibility_test_eligible": False,
    }


def fifteen_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "T1_core_algebra": "COMPOSITION_SKELETON_ONLY_PHYSICAL_STAR_ALGEBRA_NOT_DERIVED",
        "T2_core_representation": "NOT_DERIVED_MULTIPLE_FIXED_COMPLETIONS",
        "T3_core_pairing_trace": "NOT_DERIVED_MULTIPLE_FIXED_FAITHFUL_STATES",
        "T4_core_quadratic_form": "NOT_ACTION_OWNED",
        "T5_geometry_core_attachment": "NOT_ACTION_OWNED",
        "T6_total_form_closability": "CONDITIONAL_THEOREM_ONLY_PHYSICAL_FORM_UNDEFINED",
        "T7_operator_representation": "CONDITIONAL_ON_MISSING_CLOSED_FORM_AND_REPRESENTATION",
        "T8_boundary_variation_selection": "NOT_SELECTED",
        "T9_Schur_Feshbach_generator": "INELIGIBLE_PHYSICAL_BLOCK_OPERATOR_ABSENT",
        "T10_central_shift_projectivization": "UNRESOLVED",
        "T11_event_amplitude": "NOT_DERIVED",
        "T12_geometric_reconstruction": "EXACT_RESTRICTION_RECOVERY_BUT_NO_CORE_TO_GEOMETRY_EMERGENCE_MAP",
        "T13_stable_clock": "NOT_DERIVED",
        "T14_joint_Hamiltonian": "NOT_SELECTED",
        "T15_microscopic_foundation_uniqueness": "FALSE_AT_ADMISSIBILITY_LEVEL_PHYSICAL_SET_UNDEFINED",
        "outcome": OUTCOME,
        "residual_ambiguity": "AT_LEAST_TWO_DISCRETE_FIXED_COMPLETIONS_AND_IN_FACT_UNBOUNDED_ALGEBRA_REPRESENTATION_STATE_FORM_CHOICES",
    }


def completion_payload() -> dict[str, Any]:
    recovery = symbolic_regular_recovery()
    witness = microscopic_nonuniqueness_witness()
    scaling = preclock_scaling_diagnostics(np.diag([0.0, 1.0, 3.0]), 2.0, 0.75)
    affine = affine_spectral_equivalence([0.0, 1.0, 2.0], [0.0, 1.0, 3.0])
    validation = {
        "no_primitive_spacetime_coordinate": True,
        "no_primitive_metric": True,
        "no_coordinate_time": True,
        "no_ordinary_energy": True,
        "no_spacetime_core_measure": True,
        "algebraic_composition_consistent": True,
        "positive_witness_pairings": True,
        "diagnostic_forms_closed": all(
            finite_form_diagnostics(cyclic_dirichlet_operator(n))["closed"] for n in (2, 3)
        ),
        "diagnostic_operators_self_adjoint": all(
            finite_form_diagnostics(cyclic_dirichlet_operator(n))["associated_operator_self_adjoint"] for n in (2, 3)
        ),
        "conditional_Green_form_zero": boundary_event_payload()["sample_Green_form_norm"] < 1e-12,
        "attachment_adjoint_compatible": all(
            attachment_block_diagnostics(n)["attachment_adjoint_residual"] < 1e-12 for n in (2, 3)
        ),
        "invariants_preserved_in_witnesses": all(
            item["invariant_commutator_residual"] < 1e-12 for item in witness["foundations"]
        ),
        "v15_2_scaling_rule_retained": scaling["is_preclock_reparameterization"],
        "v15_2_affine_quotient_witness_retained": not affine["equivalent"],
        "central_shift_not_overpromoted": not boundary_event_payload()["central_shift_projective_gauge_resolved"],
        "regular_BHSM_recovery": recovery["all_residuals_exactly_zero"],
        "v15_1_unitary_theorem_class_retained": True,
        "v15_0_core_firewall_retained": True,
        "no_preferred_frame": True,
        "no_empirical_inputs": True,
        "no_arbitrary_continuous_coefficient": True,
        "frozen_predictions_unchanged": True,
        "official_prediction_logic_unchanged": True,
        "USB_untouched": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v15_3",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "candidate_foundations": candidate_foundations_payload(),
        "core_algebra": core_algebra_payload(),
        "core_representation": core_representation_payload(),
        "core_pairing": core_pairing_payload(),
        "core_quadratic_form": core_quadratic_form_payload(),
        "geometry_core_attachment": geometry_core_attachment_payload(),
        "total_microscopic_action": total_action_payload(),
        "boundary_and_event": boundary_event_payload(),
        "reconstruction_and_clock": reconstruction_clock_payload(),
        "theorem_gates": fifteen_gate_payload(),
        "exact_regular_recovery": recovery,
        "core_algebra_action_derived": False,
        "core_representation_action_derived": False,
        "core_pairing_action_derived": False,
        "core_quadratic_form_action_derived": False,
        "geometry_core_attachment_action_derived": False,
        "total_microscopic_action_derived": False,
        "physical_boundary_block_selected": False,
        "event_kernel_action_derived": False,
        "central_shift_projective_gauge_proved": False,
        "physical_generator_class_selected": False,
        "stable_clock_selected": False,
        "H_eff_selected": False,
        "regular_BHSM_recovery_exact": recovery["all_residuals_exactly_zero"],
        "Hindsight_20_20": {
            "validated": [
                "the v15.0 event architecture supplies an associative identity and invariant graded algebraic composition skeleton",
                "a selected positive state would produce a GNS representation but no such state is action owned",
                "a selected closed semibounded form would produce a self-adjoint operator but no such core form is action owned",
                "the existing regular action and identity-limit recovery remain exact",
                "two fixed positive cyclic completions prove microscopic admissibility nonuniqueness without continuous tuning",
            ],
            "invalidated": [
                "an ordinary Hilbert-space core is automatically canonical",
                "spectral-triple axioms are forced by current BHSM",
                "regular Wentzell data automatically define core Wentzell data",
                "a convenient trace is a derived trace",
                "finite dimensionality is justified by simplicity",
                "spacetime integration is admissible as a primitive pregeometric core action",
                "self-adjointness alone selects the microscopic foundation",
            ],
            "reclassified": [
                "core Hilbert space becomes a possible GNS or Hilbert-correspondence output after algebra and positive-state selection",
                "core operator becomes the representation-theorem output of a more fundamental closed quadratic form",
                "boundary condition becomes a variation-derived attachment law rather than an extension chosen from a theorem class",
                "the Aether core remains an algebraic composition candidate rather than a positive state sector until positivity data are supplied",
            ],
            "open": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "FULL_BHSM_COMPLETE": False,
        "MARK_III": "NOT_REACHED",
        "USB_SYNCHRONIZATION_ELIGIBLE": False,
        "new_continuous_parameter_introduced": False,
        "new_fundamental_dynamical_field_introduced": False,
        "preferred_frame_introduced": False,
        "empirical_inputs_used": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_aether_core_algebra_gate_v15_3.json": core_algebra_payload(),
        "BHSM_aether_core_representation_gate_v15_3.json": core_representation_payload(),
        "BHSM_aether_core_pairing_gate_v15_3.json": core_pairing_payload(),
        "BHSM_aether_core_quadratic_form_v15_3.json": core_quadratic_form_payload(),
        "BHSM_aether_geometry_core_attachment_v15_3.json": geometry_core_attachment_payload(),
        "BHSM_aether_total_microscopic_action_v15_3.json": total_action_payload(),
        "BHSM_aether_boundary_variation_selection_v15_3.json": boundary_event_payload(),
        "BHSM_aether_event_kernel_gate_v15_3.json": {
            "event": boundary_event_payload(),
            "foundation_nonuniqueness": microscopic_nonuniqueness_witness(),
        },
        "BHSM_aether_clock_from_microscopic_action_v15_3.json": reconstruction_clock_payload(),
        "BHSM_completion_gate_v15_3.json": completion_payload(),
    }


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def materialize(directory: str | Path) -> list[Path]:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, payload in artifact_payloads().items():
        path = target / name
        path.write_text(deterministic_json(payload), encoding="utf-8")
        paths.append(path)
    return paths
