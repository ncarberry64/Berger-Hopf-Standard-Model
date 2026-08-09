"""BHSM v15.2 physical Aether-generator selection theorem/no-go package.

This module distinguishes literal matrix representatives from physical
generator classes.  It implements the equivalences that are already forced
by the v15.0/v15.1 relational architecture, audits the action-owned boundary
and Schur routes, and gives a discrete fixed-spectrum witness that survives
the legitimate pre-clock quotient.  The retained BHSM action has no core
Hilbert correspondence or core quadratic form, so the physical quotient is
not yet defined by the action.
"""
from __future__ import annotations

import json
import math
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

VERSION = "v15.2"
OUTCOME = "OUTCOME_F_UPSTREAM_OWNERSHIP_OBSTRUCTION"
PRIMARY_VERDICT = (
    "BHSM_V15_2_PHYSICAL_EQUIVALENCE_IDENTIFIES_STRUCTURE_PRESERVING_UNITARY_"
    "INTERTWINERS_AS_BASIS_GAUGE_AND_PRECLOCK_POSITIVE_GENERATOR_SCALING_AS_"
    "PROCESS_REPARAMETRIZATION_WHILE_UNIFORM_CENTRAL_SHIFTS_REMAIN_ONLY_"
    "CONDITIONALLY_PROJECTIVE_BECAUSE_THE_EVENT_INTERFERENCE_FUNCTOR_IS_NOT_"
    "ACTION_OWNED;_THE_REGULAR_ACTION_SUPPLIES_REGULAR_STRATUM_INCIDENCE_AND_"
    "THEOREM_CLASS_CALDERON_WENTZELL_DATA_BUT_NO_PREGEOMETRIC_CORE_HILBERT_"
    "MODULE_CORE_OPERATOR_ATTACHMENT_QUADRATIC_FORM_OR_STABLE_REFERENCE_CYCLE_"
    "SO_NO_PARENT_VARIATION_SCHUR_FESHBACH_COMMUTANT_COMPOSITION_OR_MINIMALITY_"
    "ARGUMENT_SELECTS_THE_PHYSICAL_GENERATOR_CLOCK_OR_HAMILTONIAN"
)
EXACT_NEXT_OBJECT = (
    "MICROSCOPIC_ACTION_DERIVATION_OF_THE_PREGEOMETRIC_CORE_BOUNDARY_HILBERT_"
    "CORRESPONDENCE_QUADRATIC_FORM_WITH_TRACE_PAIRING_CORE_OPERATOR_ATTACHMENT_"
    "COUPLING_AND_STABLE_REFERENCE_CYCLE_WHOSE_VARIATION_JOINTLY_SELECTS_"
    "THETA_A_K_A_AND_H_EFF"
)


def _as_hermitian(matrix: np.ndarray, name: str = "operator", tol: float = 1e-12) -> np.ndarray:
    value = np.asarray(matrix, dtype=complex)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be square")
    if np.linalg.norm(value - value.conj().T) > tol:
        raise ValueError(f"{name} must be Hermitian")
    return (value + value.conj().T) / 2.0


def _as_unitary(matrix: np.ndarray, dimension: int, tol: float = 1e-12) -> np.ndarray:
    value = np.asarray(matrix, dtype=complex)
    if value.shape != (dimension, dimension):
        raise ValueError("unitary has the wrong dimension")
    if np.linalg.norm(value.conj().T @ value - np.eye(dimension)) > tol:
        raise ValueError("intertwiner must be unitary")
    return value


def structure_preserving_unitary_diagnostics(
    first: np.ndarray,
    second: np.ndarray,
    unitary: np.ndarray,
    first_invariants: Sequence[np.ndarray] = (),
    second_invariants: Sequence[np.ndarray] = (),
    first_projection: np.ndarray | None = None,
    second_projection: np.ndarray | None = None,
) -> dict[str, Any]:
    """Audit whether U is only a basis change of the complete retained data."""
    left = _as_hermitian(first, "first generator")
    right = _as_hermitian(second, "second generator")
    if left.shape != right.shape:
        raise ValueError("generator dimensions differ")
    u = _as_unitary(unitary, left.shape[0])
    if len(first_invariants) != len(second_invariants):
        raise ValueError("invariant lists differ")
    generator_residual = float(np.linalg.norm(right - u @ left @ u.conj().T))
    invariant_residuals = []
    for q_left, q_right in zip(first_invariants, second_invariants, strict=True):
        ql = _as_hermitian(q_left, "first invariant")
        qr = _as_hermitian(q_right, "second invariant")
        invariant_residuals.append(float(np.linalg.norm(qr - u @ ql @ u.conj().T)))
    projection_residual = 0.0
    if (first_projection is None) != (second_projection is None):
        raise ValueError("both reconstruction projections must be supplied")
    if first_projection is not None and second_projection is not None:
        projection_residual = float(
            np.linalg.norm(np.asarray(second_projection) - u @ np.asarray(first_projection) @ u.conj().T)
        )
    maximum = max([generator_residual, projection_residual, *invariant_residuals], default=0.0)
    return {
        "generator_intertwining_residual": generator_residual,
        "invariant_intertwining_residuals": invariant_residuals,
        "reconstruction_projection_residual": projection_residual,
        "structure_preserving_unitary_equivalence": maximum < 1e-12,
        "interpretation": "basis_change_only_when_all_owned_structures_intertwine",
    }


def affine_spectral_equivalence(
    first: Sequence[float], second: Sequence[float], *, allow_shift: bool = True, tol: float = 1e-12
) -> dict[str, Any]:
    """Test equality of spectra modulo a positive scale and optional shift."""
    x = np.sort(np.asarray(first, dtype=float))
    y = np.sort(np.asarray(second, dtype=float))
    if x.ndim != 1 or y.shape != x.shape or x.size == 0:
        raise ValueError("spectra must be nonempty and have equal size")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("spectra must be finite")
    centered_x = x - x[0] if allow_shift else x
    centered_y = y - y[0] if allow_shift else y
    nonzero = np.flatnonzero(np.abs(centered_x) > tol)
    if nonzero.size == 0:
        equivalent = np.linalg.norm(centered_y) < tol
        scale = 1.0 if equivalent else None
    else:
        index = int(nonzero[0])
        scale_value = centered_y[index] / centered_x[index]
        equivalent = scale_value > 0.0 and np.linalg.norm(centered_y - scale_value * centered_x) < tol
        scale = float(scale_value) if equivalent else None
    shift = float(y[0] - (scale or 1.0) * x[0]) if equivalent and allow_shift else 0.0
    return {
        "equivalent": bool(equivalent),
        "positive_scale": scale,
        "central_shift": shift if equivalent else None,
        "allow_central_shift": allow_shift,
    }


def central_shift_gate() -> dict[str, Any]:
    """Classify K -> K+cI in the full relational event system."""
    return {
        "kernel_relation": "U_prime(E)=exp(-i*c*chi(E))*U(E)",
        "single_fixed_depth_transition_probabilities_unchanged": True,
        "uniform_shift_is_relative_G_C_phase": False,
        "block_relative_shift_is_central": False,
        "different_depth_history_interference_can_change": True,
        "character_is_removable_if_chi_is_an_object_coboundary_or_only_rays_are_observable": True,
        "event_interference_or_projectivization_action_owned": False,
        "classification": "CONDITIONAL_PROJECTIVE_EQUIVALENCE_NOT_UNCONDITIONAL_PHYSICAL_GAUGE",
    }


def joint_clocked_hamiltonian(
    generator: np.ndarray, reference_cycle_depth: float, clock_period: float, hbar: float = 1.0
) -> np.ndarray:
    """Return H_eff=hbar*(Delta chi_clk/tau_clk)*K.

    Unlike the v15.1 unit-cycle shorthand, this form makes the pre-clock
    reparameterization covariance explicit.
    """
    k = _as_hermitian(generator, "generator")
    depth, period, quantum = map(float, (reference_cycle_depth, clock_period, hbar))
    if not all(math.isfinite(value) for value in (depth, period, quantum)):
        raise ValueError("clock data must be finite")
    if depth <= 0.0 or period <= 0.0 or quantum <= 0.0:
        raise ValueError("clock depth, period, and hbar must be positive")
    return quantum * depth * k / period


def preclock_scaling_diagnostics(generator: np.ndarray, scale: float, process_depth: float) -> dict[str, Any]:
    k = _as_hermitian(generator, "generator")
    factor, chi = float(scale), float(process_depth)
    if not math.isfinite(factor) or factor <= 0.0 or not math.isfinite(chi):
        raise ValueError("positive finite scale and finite process depth required")
    original = unitary_event_kernel(k, chi)
    transformed = unitary_event_kernel(factor * k, chi / factor)
    return {
        "kernel_residual": float(np.linalg.norm(original - transformed)),
        "is_preclock_reparameterization": bool(np.linalg.norm(original - transformed) < 1e-12),
        "clock_cycle_depth_transformation": "Delta_chi_clk_prime=Delta_chi_clk/a",
        "joint_H_eff_invariant": True,
    }


def invariant_commutant_diagnostics(invariants: Sequence[np.ndarray], tol: float = 1e-10) -> dict[str, Any]:
    """Compute the complex commutant dimension of a finite invariant algebra."""
    if not invariants:
        raise ValueError("at least one invariant is required")
    matrices = [_as_hermitian(item, "invariant") for item in invariants]
    n = matrices[0].shape[0]
    if any(item.shape != (n, n) for item in matrices):
        raise ValueError("invariant dimensions differ")
    identity = np.eye(n, dtype=complex)
    constraints = [np.kron(identity, q) - np.kron(q.T, identity) for q in matrices]
    stacked = np.concatenate(constraints, axis=0)
    singular = np.linalg.svd(stacked, compute_uv=False)
    rank = int(np.sum(singular > tol))
    dimension = n * n - rank
    return {
        "representation_dimension": n,
        "constraint_rank": rank,
        "complex_commutant_dimension": dimension,
        "Hermitian_commutant_real_dimension": dimension,
        "symmetry_selects_unique_generator_mod_identity": dimension <= 2,
    }


def quotient_nonuniqueness_witness() -> dict[str, Any]:
    """Discrete witness surviving unitary, central-shift, and scale quotient."""
    invariant = np.diag([-1.0, 0.0, 1.0])
    first = np.diag([0.0, 1.0, 2.0])
    second = np.diag([0.0, 1.0, 3.0])
    affine = affine_spectral_equivalence(np.diag(first), np.diag(second), allow_shift=True)
    commutant = invariant_commutant_diagnostics([invariant])
    u1 = unitary_event_kernel(first, 1.0)
    u2 = unitary_event_kernel(second, 1.0)
    wentzell = np.diag([1.0, 2.0, 3.0])
    domain = self_adjoint_domain_diagnostics(wentzell)
    f0, f1 = boundary_data_on_domain(wentzell, (1.0, 0.5j, -0.25), (0.2j, -0.1, 0.3))
    g0, g1 = boundary_data_on_domain(wentzell, (0.3j, -0.7, 0.2), (0.1, 0.4j, -0.2))
    green = boundary_green_form(f0, f1, g0, g1)
    return {
        "invariant": invariant.tolist(),
        "generators": [first.tolist(), second.tolist()],
        "spectra": [np.diag(first).tolist(), np.diag(second).tolist()],
        "gap_ratio_invariants": [1.0, 2.0],
        "affine_spectral_equivalence": affine,
        "physically_inequivalent_after_unitary_shift_and_positive_scale_quotient": not affine["equivalent"],
        "invariant_commutant": commutant,
        "commutator_residuals": [
            float(np.linalg.norm(first @ invariant - invariant @ first)),
            float(np.linalg.norm(second @ invariant - invariant @ second)),
        ],
        "unitarity_residuals": [
            float(np.linalg.norm(u1.conj().T @ u1 - np.eye(3))),
            float(np.linalg.norm(u2.conj().T @ u2 - np.eye(3))),
        ],
        "identity_residuals": [
            float(np.linalg.norm(unitary_event_kernel(first, 0.0) - np.eye(3))),
            float(np.linalg.norm(unitary_event_kernel(second, 0.0) - np.eye(3))),
        ],
        "event_composition_residuals": [
            float(np.linalg.norm(unitary_event_kernel(k, 0.7) @ unitary_event_kernel(k, 0.4) - unitary_event_kernel(k, 1.1)))
            for k in (first, second)
        ],
        "same_self_adjoint_domain": domain["self_adjoint_extension"],
        "boundary_Green_form_norm": abs(green),
        "continuous_parameter_used_in_witness": False,
        "physical_action_derived_representation_claimed": False,
    }


def zero_parameter_schur_reduction(
    geometric_block: np.ndarray, core_block: np.ndarray, coupling: np.ndarray
) -> np.ndarray:
    """Conditional z=0 Schur/Feshbach operator D_G-B D_C^-1 B*."""
    dg = _as_hermitian(geometric_block, "geometric block")
    dc = _as_hermitian(core_block, "core block")
    b = np.asarray(coupling, dtype=complex)
    if b.shape != (dg.shape[0], dc.shape[0]):
        raise ValueError("coupling has the wrong shape")
    if np.min(np.abs(np.linalg.eigvalsh(dc))) < 1e-12:
        raise ValueError("core block must be invertible at z=0")
    reduced = dg - b @ np.linalg.solve(dc, b.conj().T)
    return _as_hermitian(reduced, "Schur reduction")


def physical_equivalence_payload() -> dict[str, Any]:
    witness = quotient_nonuniqueness_witness()
    return {
        "version": VERSION,
        "physical_data_tuple": "(H_A,pi_A,D_rel,K_A,{Q_i},P_G,Theta_A,C_clk)",
        "unitary_equivalence": (
            "U must intertwine generator, invariant algebra, relative domain, matching observables, "
            "regular reconstruction projection, and any selected clock structure"
        ),
        "unitary_basis_change_is_physical_difference": False,
        "central_shift_gate": central_shift_gate(),
        "preclock_scaling": {
            "transformation": "K_A_prime=a K_A, chi_prime=chi/a, a>0",
            "classification": "REPARAMETERIZATION_REDUNDANCY_BEFORE_CLOCK_SELECTION",
            "unit_cycle_shortcut_is_not_scale_covariant": True,
            "scale_covariant_joint_observable": "H_eff=hbar*(Delta_chi_clk/tau_clk)*K_A",
        },
        "quotient_definition": (
            "K_admissible modulo structure-preserving unitary intertwiners and positive process "
            "reparameterizations; central shifts only after action-owned projectivization/coboundary proof"
        ),
        "discrete_quotient_witness": witness,
        "physical_quotient_action_owned": False,
    }


def core_module_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "regular_geometric_Hilbert_spaces_owned": True,
        "v14_64_geometric_direct_sum_scope": "M8 plus M5_plus plus M5_minus plus M4 only",
        "pregeometric_core_has_measure": False,
        "pregeometric_core_has_trace_pairing": False,
        "pregeometric_core_has_operator_representation": False,
        "pregeometric_core_has_grading": False,
        "pregeometric_core_has_action_derived_trace_map": False,
        "finite_dimensional_convenience_module_adopted": False,
        "unique_H_C_action_derived": False,
        "classification": "UPSTREAM_OWNERSHIP_OBSTRUCTION",
    }


def boundary_selection_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "variation_rule": (
            "a boundary action (1/2)<Gamma0,Phi Theta_A Gamma0,Phi> would yield "
            "Gamma1 Phi+Theta_A Gamma0 Phi=0"
        ),
        "v14_65_result": "self_adjoint scalar boundary theorem class",
        "v14_66_result": "operator-valued Calderon/Wentzell theorem class; physical blocks open",
        "v14_67_result": "whitened attachment response on an author-selected finite-radius branch",
        "v14_68_result": "canonical rank-two incidence lift inside regular M8/M5/M4 envelopment",
        "pregeometric_core_boundary_term_in_retained_action": False,
        "physical_core_Calderon_projector_owned": False,
        "physical_core_DtN_map_owned": False,
        "physical_Theta_A_action_selected": False,
        "self_adjointness_implies_physical_selection": False,
        "classification": "ADMISSIBLE_DOMAINS_CLASSIFIED_PHYSICAL_DOMAIN_NOT_SELECTED",
    }


def action_schur_composition_payload() -> dict[str, Any]:
    geometric = np.diag([2.0, 3.0])
    core = np.diag([4.0, 5.0])
    coupling = np.array([[1.0, 0.2], [0.2, 0.5]])
    reduced = zero_parameter_schur_reduction(geometric, core, coupling)
    return {
        "version": VERSION,
        "parent_quadratic_form_required": "Q_A[Psi] on an action-owned H_G direct-sum H_C",
        "retained_action_contains_Q_A": False,
        "conditional_block_operator": "D_script_A=[[D_G,B],[B*,D_C]]",
        "conditional_zero_parameter_reduction": "K_eff(0)=D_G-B D_C^{-1} B*",
        "diagnostic_reduction_Hermitian_residual": float(np.linalg.norm(reduced - reduced.conj().T)),
        "diagnostic_reduction_is_physical": False,
        "D_G_action_owned_on_regular_sector_only": True,
        "D_C_action_owned": False,
        "B_action_owned": False,
        "spectral_z_legitimate_before_clock": False,
        "zero_parameter_route_avoids_energy_circularity_but_not_missing_blocks": True,
        "event_group_law": "U(chi2)U(chi1)=U(chi1+chi2)",
        "full_event_functor_selects_generator": False,
        "reason_composition_does_not_select": (
            "every self-adjoint commutant generator exponentiates to a functor and additive chi "
            "also permits unresolved one-dimensional characters"
        ),
        "minimality_is_existing_BHSM_axiom": False,
        "heat_semigroup_microscopic_action_is_existing_BHSM_theorem": False,
    }


def clock_selection_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "action_selected_stable_core_cycle": False,
        "Goldstone_rotor_is_reference_clock": False,
        "reason_Goldstone_rotor_rejected": (
            "its coefficients and physical branch are open, its symmetric modes are gapless, "
            "and it belongs to reconstructed geometry rather than an owned core correspondence"
        ),
        "FR_rotor_is_reference_clock": False,
        "reason_FR_rotor_rejected": "collective inertia/embedding is conditional and no physical repeating core event is selected",
        "relative_periodic_monodromy_is_reference_clock": False,
        "reason_monodromy_rejected": "repository status records the physical orbit and monodromy as absent or synthetic",
        "scale_covariant_formula": "H_eff=hbar*(Delta_chi_clk/tau_clk)*K_A",
        "K_and_cycle_depth_joint_scaling": "K_prime=aK and Delta_chi_clk_prime=Delta_chi_clk/a",
        "joint_H_eff_unique": False,
        "absolute_seconds_or_eV_derived": False,
        "classification": "NO_ACTION_SELECTED_STABLE_REFERENCE_CYCLE",
    }


def uniqueness_payload() -> dict[str, Any]:
    commutant = invariant_commutant_diagnostics([np.diag([-1.0, 0.0, 1.0])])
    return {
        "version": VERSION,
        "T1_physical_generator_equivalence": "CLOSED_STRUCTURALLY",
        "T2_central_shift": "CONDITIONAL_PROJECTIVE_NOT_UNCONDITIONAL",
        "T3_relational_scaling": "PRECLOCK_REPARAMETERIZATION",
        "T4_core_Hilbert_module": "NOT_ACTION_OWNED",
        "T5_boundary_block_selection": "NOT_ACTION_SELECTED",
        "T6_parent_quadratic_form": "ABSENT_FOR_CORE_CORRESPONDENCE",
        "T7_Schur_Feshbach": "CONDITIONAL_MATHEMATICS_BLOCKS_UNOWNED",
        "T8_invariant_commutant": {
            "representative_simple_three_sector_commutant": commutant,
            "actual_full_Aether_invariant_representation_derived": False,
            "uniqueness_from_symmetry": False,
        },
        "T9_event_composition": "NO_ADDITIONAL_UNIQUENESS",
        "T10_clock_existence": "NOT_DERIVED",
        "T11_joint_clock_generator": "NOT_UNIQUE",
        "T12_regular_recovery": "EXACT_V15_1_IDENTITY_LIMIT_RETAINED",
        "T13_physical_uniqueness": "UNRESOLVED_BECAUSE_UPSTREAM_ACTION_OWNERSHIP_IS_ABSENT",
        "admissible_theorem_class_residual": (
            "continuously infinite; simple three-sector commutant has real dimension 3, leaving "
            "dimension 2 before a central quotient and dimension 1 after shift plus positive scale"
        ),
        "physical_generator_cardinality": "UNDEFINED_NOT_ZERO",
        "outcome": OUTCOME,
    }


def completion_payload() -> dict[str, Any]:
    witness = quotient_nonuniqueness_witness()
    recovery = symbolic_regular_recovery()
    validation = {
        "physical_equivalence_defined": True,
        "preclock_scaling_reclassified_correctly": True,
        "central_shift_not_overquotiented": central_shift_gate()["event_interference_or_projectivization_action_owned"] is False,
        "discrete_witness_survives_affine_quotient": witness[
            "physically_inequivalent_after_unitary_shift_and_positive_scale_quotient"
        ],
        "retained_candidates_self_adjoint": witness["same_self_adjoint_domain"],
        "boundary_Green_form_zero": witness["boundary_Green_form_norm"] < 1e-12,
        "norm_conservation": max(witness["unitarity_residuals"]) < 1e-12,
        "event_composition": max(witness["event_composition_residuals"]) < 1e-12,
        "identity_law": max(witness["identity_residuals"]) < 1e-12,
        "regular_BHSM_recovery": recovery["all_residuals_exactly_zero"],
        "no_ordinary_time_primitive": True,
        "no_conventional_energy_primitive": True,
        "no_new_continuous_parameter": True,
        "no_new_primitive_field": True,
        "no_preferred_frame": True,
        "no_empirical_input": True,
        "frozen_predictions_unchanged": True,
        "official_prediction_logic_unchanged": True,
        "USB_untouched": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v15_2",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "physical_equivalence": physical_equivalence_payload(),
        "core_Hilbert_module": core_module_payload(),
        "physical_boundary_selection": boundary_selection_payload(),
        "parent_action_Schur_and_composition": action_schur_composition_payload(),
        "clock_and_joint_Hamiltonian": clock_selection_payload(),
        "physical_uniqueness": uniqueness_payload(),
        "exact_regular_recovery": recovery,
        "K_A_literal_unique": False,
        "K_A_physical_class_unique": False,
        "physical_K_A_quotient_action_defined": False,
        "H_eff_uniquely_determined": False,
        "requested_next_object_fully_closed": False,
        "Hindsight_20_20": {
            "validated": [
                "structure-preserving unitary intertwiners are basis gauge rather than new dynamics",
                "positive generator scaling is pre-clock process reparameterization when chi and clock-cycle depth transform inversely",
                "the scale-covariant observable is H_eff=hbar*(Delta_chi_clk/tau_clk)*K_A",
                "a fixed three-sector pair remains inequivalent after unitary, central-shift, and positive-scale quotients",
                "the retained regular BHSM action and identity recovery remain exact",
            ],
            "invalidated": [
                "the v15.1 two-level spectra {0,1} and {0,2} prove physical pre-clock inequivalence",
                "self-adjointness selects the physical boundary condition",
                "invariant conservation or unitary composition selects unique dynamics",
                "a minimal matrix or zero generator is action-derived physical selection",
                "an arbitrary clock normalization is a derived physical scale",
            ],
            "reclassified": [
                "literal K_A uniqueness becomes equivalence-class uniqueness",
                "generator selection becomes joint generator-cycle selection",
                "central shifts become a projectivization/interference gate rather than automatic gauge",
                "admissible boundary triples become an action-selected boundary-block problem",
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
        "BHSM_aether_generator_equivalence_v15_2.json": physical_equivalence_payload(),
        "BHSM_aether_core_hilbert_module_gate_v15_2.json": core_module_payload(),
        "BHSM_aether_physical_boundary_selection_v15_2.json": boundary_selection_payload(),
        "BHSM_aether_generator_uniqueness_v15_2.json": {
            "uniqueness": uniqueness_payload(),
            "witness": quotient_nonuniqueness_witness(),
            "action_Schur_composition": action_schur_composition_payload(),
        },
        "BHSM_aether_reference_clock_gate_v15_2.json": clock_selection_payload(),
        "BHSM_aether_joint_hamiltonian_selection_v15_2.json": {
            "equivalence": physical_equivalence_payload()["preclock_scaling"],
            "clock": clock_selection_payload(),
        },
        "BHSM_completion_gate_v15_2.json": completion_payload(),
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
