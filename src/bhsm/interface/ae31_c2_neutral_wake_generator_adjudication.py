"""Adjudicate the historical neutral seed as stiffness or wake generator."""

from __future__ import annotations

from typing import Any

import numpy as np

from neutral_bridge_pmns_source import neutral_operator


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "AE31_CURRENT_C2_NEUTRAL_WAKE_GENERATOR_ADJUDICATION"


def positive_stiffness_zero_reference_theorem() -> dict[str, Any]:
    """Apply the PSD zero-diagonal lemma to the historical neutral seed."""

    kernel = np.asarray(neutral_operator(), dtype=float)
    beta = float(kernel[0, 1])
    leading_minor = float(np.linalg.det(kernel[:2, :2]))
    return {
        "lemma": "H_positive_semidefinite_AND_H00=0_IMPLIES_H0j=0_FOR_ALL_j",
        "proof": "0<=det([[H00,H01],[H10,H11]])=-abs(H01)^2",
        "historical_H00": float(kernel[0, 0]),
        "historical_beta": beta,
        "leading_principal_minor": leading_minor,
        "exact_leading_principal_minor": "-beta^2=-1/9",
        "historical_seed_is_positive_stiffness": False,
        "same_obstruction_for_any_nonzero_beta_with_zero_reference_cost": True,
        "positive_mass_squared_interpretation_requires": (
            "BETA_ZERO_OR_AN_ACTION_DERIVED_POSITIVE_REFERENCE_DIAGONAL_"
            "SATISFYING_ALL_SCHUR_COMPLEMENT_BOUNDS"
        ),
    }


def traceless_wake_generator() -> dict[str, Any]:
    """Remove only the dynamically irrelevant common phase from ``K_nu``."""

    kernel = np.asarray(neutral_operator(), dtype=float)
    common = float(np.trace(kernel) / 3.0)
    generator = kernel - common * np.eye(3)
    eigenvalues = np.linalg.eigvalsh(generator)
    gaps = np.diff(eigenvalues)
    return {
        "common_trace_shift": common,
        "exact_common_trace_shift": "14/9",
        "traceless_generator": generator.tolist(),
        "trace_residual": float(abs(np.trace(generator))),
        "Hermitian": bool(np.allclose(generator, generator.T)),
        "eigenvalues": eigenvalues.tolist(),
        "two_nonzero_eigenvalue_gaps": bool(np.all(np.abs(gaps) > 0.0)),
        "ordered_eigenvalue_gaps": gaps.tolist(),
        "common_shift_changes_gaps": False,
        "negative_eigenvalue_obstructs_first_order_unitary_evolution": False,
        "classification": "ALGEBRAICALLY_ADMISSIBLE_FIRST_ORDER_WAKE_GENERATOR_SHAPE",
    }


def unitary_wake_evolution(proper_time: float) -> dict[str, Any]:
    """Construct ``exp(-i tau H)`` spectrally for the traceless seed."""

    time = float(proper_time)
    if not np.isfinite(time):
        raise ValueError("finite proper_time required")
    generator = np.asarray(traceless_wake_generator()["traceless_generator"])
    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    evolution = eigenvectors @ np.diag(np.exp(-1.0j * time * eigenvalues)) @ eigenvectors.T
    residual = np.linalg.norm(evolution.conj().T @ evolution - np.eye(3))
    return {
        "proper_time": time,
        "unitarity_residual": float(residual),
        "unitary": bool(residual < 2.0e-14),
        "norm_preserving": True,
        "formula": "U(tau)=exp(-i*tau*(K_nu-tr(K_nu)I3/3))",
        "physical_time_unit_derived": False,
        "physical_monodromy_derived": False,
    }


def historical_first_order_owner_alignment() -> dict[str, Any]:
    return {
        "v14_56_action_term": "i*z_dagger*D_tau*z-z_dagger*H_wake*z",
        "v14_56_equation": "i*D_tau*z=H_wake*z",
        "v14_57_owner_formula": (
            "H_wake=traceless_Hermitian_part(P(N_child-N_parent-J_interface)P"
            "+sum_A partial_A_zeta_rel_prime_0*G_A)"
        ),
        "K_nu_has_correct_Hermitian_three_channel_type": True,
        "K_nu_equals_action_evaluated_H_wake_on_current_C2": False,
        "why_not": (
            "THE_CURRENT_C2_PHYSICAL_DTN_INTERFACE_AND_RELATIVE_ZETA_SHAPE_"
            "DERIVATIVES_HAVE_NOT_BEEN_EVALUATED_ON_THE_IDENTIFIED_NEUTRAL_MODES"
        ),
        "v14_57_diagnostic_fixture_may_be_substituted": False,
        "historical_candidate_coefficients_may_be_substituted": False,
        "exact_next_calculation": (
            "EVALUATE_THE_V14_57_TRACELESS_HERMITIAN_WAKE_FORMULA_WITH_THE_"
            "CURRENT_C2_PHYSICAL_DTN_INTERFACE_AND_RELATIVE_ZETA_SHAPE_JETS"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_ZERO_REFERENCE_POSITIVE_STIFFNESS_MIXING_NO_GO_DERIVED": True,
        "CURRENT_C2_HISTORICAL_KNU_TRACELESS_UNITARY_GENERATOR_SHAPE_DERIVED": True,
        "CURRENT_C2_HISTORICAL_KNU_ALGEBRAICALLY_ELIGIBLE_AS_HWAKE": True,
        "CURRENT_C2_ACTION_EVALUATED_PHYSICAL_HWAKE_DERIVED": False,
        "CURRENT_C2_PHYSICAL_NEUTRINO_MONODROMY_DERIVED": False,
        "CURRENT_C2_PHYSICAL_NEUTRINO_MASS_SPLITTINGS_DERIVED": False,
        "arbitrary_positive_shift_inserted": False,
        "historical_diagnostic_fixture_substituted": False,
        "measured_neutrino_data_used": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "historical_first_order_owner_alignment",
    "positive_stiffness_zero_reference_theorem",
    "traceless_wake_generator",
    "unitary_wake_evolution",
]
