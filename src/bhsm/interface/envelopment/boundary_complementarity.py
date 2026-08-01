"""Eta-sector conjugation audit and full antimatter fail-closed gate."""

from __future__ import annotations

from typing import Any

import numpy as np

from .relational_axioms import DoctrineStatus


COMPLEMENTARITY_VERDICT = "BHSM_CURRENT_ETA_ACTION_DOES_NOT_ENCODE_ALL_CHARGE_CONJUGATION_DATA"
ETA_SUBRESULT = "BHSM_ETA_SECTOR_PHASE_CONJUGATION_INVOLUTION_DERIVED_CONDITIONALLY"


def eta_conjugation(eta: np.ndarray, covariant_derivative: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Conjugate eta and its derivative, including the conjugate connection."""

    return np.conjugate(eta), np.conjugate(covariant_derivative)


def eta_sector_observables(eta: np.ndarray, covariant_derivative: np.ndarray) -> dict[str, Any]:
    eta_array = np.asarray(eta, dtype=complex)
    derivative = np.asarray(covariant_derivative, dtype=complex)
    if eta_array.ndim != 1 or derivative.ndim != 2 or derivative.shape[1] != eta_array.size:
        raise ValueError("eta must be a vector and D eta must have shape (directions, components)")
    norm = float(np.vdot(eta_array, eta_array).real)
    gram = np.real(derivative.conj() @ derivative.T)
    x_eta = float(np.trace(gram))
    phase_current = np.imag(derivative.conj() @ eta_array)
    return {
        "norm": norm,
        "X_eta": x_eta,
        "stress_kinetic_gram": gram,
        "U1_phase_current": phase_current,
    }


def numerical_involution_audit() -> dict[str, Any]:
    eta = np.array([1 + 2j, -2 + 0.5j, 0.25 - 1j], dtype=complex)
    eta /= np.linalg.norm(eta)
    derivative = np.array(
        [[0.2 + 0.3j, -0.4 + 0.1j, 0.5 - 0.2j], [-0.1j, 0.7 + 0.2j, -0.3 + 0.4j]],
        dtype=complex,
    )
    c_eta, c_derivative = eta_conjugation(eta, derivative)
    cc_eta, cc_derivative = eta_conjugation(c_eta, c_derivative)
    original = eta_sector_observables(eta, derivative)
    conjugate = eta_sector_observables(c_eta, c_derivative)
    return {
        "involution_residual": float(np.linalg.norm(cc_eta - eta) + np.linalg.norm(cc_derivative - derivative)),
        "norm_residual": abs(original["norm"] - conjugate["norm"]),
        "X_eta_residual": abs(original["X_eta"] - conjugate["X_eta"]),
        "stress_residual": float(np.linalg.norm(original["stress_kinetic_gram"] - conjugate["stress_kinetic_gram"])),
        "phase_current_reversal_residual": float(np.linalg.norm(original["U1_phase_current"] + conjugate["U1_phase_current"])),
    }


def full_physical_gate() -> dict[str, Any]:
    return {
        "candidate_map": "C_env:(eta,D_A,A_rep,n)->(eta*,(D_A eta)*,A_conjugate,-or+n as required)",
        "eta_sector_involution": True,
        "eta_norm_X_and_stress_invariant": True,
        "candidate_U1_phase_current_reversed": True,
        "full_action_invariance": None,
        "equal_invariant_mass": None,
        "equal_Floquet_spectrum": None,
        "opposite_additive_gauge_charges": None,
        "conjugate_SM_representations": None,
        "spin_statistics_compatibility": None,
        "controlled_CP_violation": "OPEN_ATTACHMENT_TO_DELTA_BH_PI_OVER_3",
        "interaction_vertices": None,
        "annihilation_or_reconfiguration_channel": None,
        "duplicate_particle_ontology_removed": False,
        "conventional_antiparticle_fields_retained": True,
        "classification": DoctrineStatus.OPEN.value,
    }


def complementarity_payload() -> dict[str, Any]:
    residuals = numerical_involution_audit()
    validation = {
        "eta_involution": residuals["involution_residual"] < 1.0e-14,
        "eta_action_invariants": max(residuals["norm_residual"], residuals["X_eta_residual"]) < 1.0e-14,
        "eta_stress_invariant": residuals["stress_residual"] < 1.0e-14,
        "phase_current_reverses": residuals["phase_current_reversal_residual"] < 1.0e-14,
        "full_equivalence_not_claimed": full_physical_gate()["full_action_invariance"] is None,
        "antiparticle_fields_preserved": full_physical_gate()["conventional_antiparticle_fields_retained"],
    }
    return {
        "artifact": "BHSM_boundary_complementarity_gate_v10_1",
        "author_status": DoctrineStatus.AUTHOR_ONTOLOGY.value,
        "eta_sector_subresult": ETA_SUBRESULT,
        "eta_sector_residuals": residuals,
        "physical_gate": full_physical_gate(),
        "verdict": COMPLEMENTARITY_VERDICT,
        "exact_missing_object": "ETA_BOUNDARY_COMPLEMENTARITY_INVOLUTION_WITH_FULL_GAUGE_REPRESENTATION_DATA",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
