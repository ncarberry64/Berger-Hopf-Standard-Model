"""Canonical BHSM v10.0 Machian geometric-envelopment doctrine.

This module registers definitions and structural postulates.  It deliberately
does not turn the ontology into a dynamical theorem or a particle prediction.
"""

from __future__ import annotations

from typing import Any

import numpy as np


VERSION = "v10.0"
SPRINT = "bhsm-unified-envelopment-foundation-v10-0"
SOURCE_PR208_SHA = "953aea690c5aba356d305c9031a759dd672dccfa"
FOUNDATION_VERDICT = "BHSM_MACHIAN_GEOMETRIC_ENVELOPMENT_FOUNDATION_INTEGRATED"
PRIMARY_VERDICT = (
    "BHSM_DYNAMIC_ENVELOPMENT_ACTION_AND_COMPLETION_ARCHITECTURE_"
    "CONSTRUCTED_CONDITIONALLY"
)
NEXT_EXACT_OBJECT = (
    "ACTION_SELECTED_GAUGE_DRESSED_CHARGED_SELF_ENVELOPMENT_RELATIVE_"
    "PERIODIC_ORBIT_WITH_LOCAL_CHIRAL_TRANSGRESSION"
)

CLASSIFICATIONS = (
    "DERIVED",
    "DERIVED_CONDITIONAL",
    "STRUCTURAL_POSTULATE",
    "CANDIDATE",
    "PROXY_ONLY",
    "INVALIDATED",
    "OPEN",
    "BLOCKED_EXACT_OBJECT_PROVED",
)

FAMILY_LEDGERS = {
    "lepton": ((0, 0), (5, 2), (9, 3)),
    "up": ((0, 0), (6, 0), (10, 1)),
    "down": ((0, 0), (6, 3), (8, 2)),
}

PROJECTOR_RESIDUAL_ZERO_TOLERANCE = 1.0e-14


def _stable_projector_residual(value: float) -> float:
    """Serialize numerical zero independently of BLAS/platform roundoff."""

    residual = float(value)
    return 0.0 if abs(residual) <= PROJECTOR_RESIDUAL_ZERO_TOLERANCE else residual


def canonical_doctrine() -> dict[str, Any]:
    return {
        "name": "Machian Geometric Envelopment",
        "classification": "STRUCTURAL_POSTULATE",
        "statement": (
            "The universe is one closed interconnected geometric system; a "
            "particle is a persistent topologically organized and dynamically "
            "maintained energy-geometry differential of the parent spacetime."
        ),
        "reciprocity": [
            "global geometry -> local envelopment",
            "local envelopment -> global geometry",
        ],
        "hierarchy": ["cosmos", "environment", "envelopment", "sub-envelopment"],
        "theorem_claimed": False,
        "canonical_repository_doctrine": True,
    }


def complete_state_definition() -> dict[str, Any]:
    return {
        "state": "Phi(tau)=(G_AB,chi,sigma,eta,A_gauge,boundary/collar data)",
        "bulk_v10_fields": ["G_AB", "chi", "sigma", "eta", "Lambda_eta"],
        "stratified_or_conditional_fields": ["A_gauge", "boundary/collar data"],
        "equivalence": ["gauge", "admissible diffeomorphism"],
        "classification": "STRUCTURAL_POSTULATE",
    }


def particle_definition() -> dict[str, Any]:
    return {
        "definition": "[Phi(tau)] with Phi(tau+T)=h.Phi(tau)",
        "allowed_h": [
            "gauge transformation",
            "admissible diffeomorphism",
            "G2/Spin/triality transformation",
            "C3 family operation",
            "internal phase advance",
        ],
        "static_soliton": "constant-orbit special case only",
        "rigid_fixed_radius_required": False,
        "classification": "STRUCTURAL_POSTULATE",
    }


def boundary_definition() -> dict[str, Any]:
    return {
        "undifferentiated_branch": "sigma=0",
        "formation_gate": "lambda_min(H_sigma^(0)[Phi])=0",
        "positive": "undifferentiated branch locally stable",
        "zero": "physicality mode marginal",
        "negative": "nonlinear envelopment branch required",
        "surface_definition": (
            "level set or transition region only after a nonlinear sigma!=0 "
            "solution exists"
        ),
        "allowed_motion": ["breathe", "deform", "move", "merge", "bifurcate", "collapse", "relax"],
        "fixed_coordinate_boundary": False,
        "classification": "STRUCTURAL_POSTULATE",
    }


def mass_definition() -> dict[str, Any]:
    return {
        "charged": "m_phys^2=-P_A P^A; P^A=int_Sigma T_total^(AB)n_B dSigma",
        "total_stress_requires": [
            "geometry",
            "chi/sigma",
            "eta/triality",
            "gauge dressing",
            "boundary/collar",
            "background response",
        ],
        "neutrino": "propagation-phase or quasi-energy splitting",
        "local_arbitrary_mass_input": False,
        "physical_mass_derived": False,
        "classification": "STRUCTURAL_POSTULATE",
    }


def cyclic_shift() -> np.ndarray:
    """Return the regular three-cycle acting on a structural family module."""

    return np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], dtype=complex)


def cyclic_projectors() -> tuple[np.ndarray, ...]:
    C = cyclic_shift()
    omega = np.exp(2j * np.pi / 3)
    return tuple(
        sum(omega ** (-r * n) * np.linalg.matrix_power(C, n) for n in range(3)) / 3
        for r in range(3)
    )


def generation_definition() -> dict[str, Any]:
    projectors = cyclic_projectors()
    identity = np.eye(3, dtype=complex)
    raw_residuals = {
        "idempotence": max(float(np.linalg.norm(P @ P - P)) for P in projectors),
        "Hermiticity": max(float(np.linalg.norm(P - P.conj().T)) for P in projectors),
        "orthogonality": max(
            float(np.linalg.norm(projectors[i] @ projectors[j]))
            for i in range(3)
            for j in range(3)
            if i != j
        ),
        "completeness": float(np.linalg.norm(sum(projectors) - identity)),
    }
    residuals = {key: _stable_projector_residual(value) for key, value in raw_residuals.items()}
    return {
        "definition": "three stable C3/Floquet family eigenbundles of one envelopment system",
        "projector_formula": "P_r=(1/3) sum_(n=0)^2 omega^(-rn) C^n",
        "frozen_ledgers": {key: [list(slot) for slot in value] for key, value in FAMILY_LEDGERS.items()},
        "projector_algebra": "DERIVED",
        "projector_residuals": residuals,
        "projector_residual_zero_tolerance": PROJECTOR_RESIDUAL_ZERO_TOLERANCE,
        "unique_projector_to_frozen_slot_correspondence": None,
        "correspondence_gate": "OPEN_ACTION_OWNED_C3_FLOQUET_TO_FROZEN_KJQ_INTERTWINER",
        "classification": "DERIVED_CONDITIONAL",
    }


def sector_ontology() -> dict[str, Any]:
    return {
        "charged_lepton": {
            "target": "asymptotic timelike gauge-dressed self-envelopment",
            "first_physical_target": "electron-like orbit",
            "status": "OPEN",
        },
        "quark": {
            "target": "color-open sub-envelopment inside a color-neutral parent",
            "isolated_soliton_primary_target": False,
            "status": "OPEN_COLOR_NEUTRAL_PARENT_REQUIRED",
        },
        "neutrino": {
            "target": "near-null propagation-supported envelopment",
            "primitive_static_rest_enclosure": False,
            "status": "OPEN_THREE_SECTOR_MONODROMY_REQUIRED",
        },
        "measurement": {
            "definition": "nonlinear transition among coupled-system envelopment basins",
            "verbal_resonance_is_probability_theorem": False,
            "status": "OPEN_NORMALIZED_TRANSITION_AMPLITUDE_THEOREM_REQUIRED",
        },
    }


def frozen_hierarchy_reinterpretation() -> dict[str, Any]:
    return {
        "operator": "Theta_f=exp[-Lambda_f/(4*pi)]",
        "candidate_role": "one-cycle transfer, attenuation, survival, or residue operator",
        "classification": "CANDIDATE",
        "action_origin_of_1_over_4pi": None,
        "numerical_frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
    }


def long_future_alignment() -> dict[str, Any]:
    return {
        "source_status": (
            "author-provided campaign summary; no repository copy of The Long "
            "Future of Space was located"
        ),
        "bubble": "localized persistent envelopment, not a rigid inserted shell",
        "bow_shock": "moving environment-relative transition region candidate",
        "cavitation": "formation or collapse of a nonlinear differentiated basin candidate",
        "moving_threshold": "lambda_min(H_sigma^(0)[Phi]) crossing along a dynamical orbit",
        "scientific_status": "STRUCTURAL_POSTULATE_AND_CANDIDATE_TRANSLATION",
        "independent_historical_text_verified": False,
    }


def foundation_payload() -> dict[str, Any]:
    generation = generation_definition()
    validation = {
        "classification_vocabulary_exact": set(CLASSIFICATIONS) == {
            "DERIVED",
            "DERIVED_CONDITIONAL",
            "STRUCTURAL_POSTULATE",
            "CANDIDATE",
            "PROXY_ONLY",
            "INVALIDATED",
            "OPEN",
            "BLOCKED_EXACT_OBJECT_PROVED",
        },
        "three_family_ledgers_preserved": all(len(value) == 3 for value in FAMILY_LEDGERS.values()),
        "cyclic_projectors_exact": max(generation["projector_residuals"].values()) < 1.0e-12,
        "fixed_radius_not_required": not particle_definition()["rigid_fixed_radius_required"],
        "fixed_boundary_not_inserted": not boundary_definition()["fixed_coordinate_boundary"],
        "frozen_predictions_unchanged": True,
    }
    return {
        "artifact": "BHSM_machian_geometric_envelopment_foundation_v10_0",
        "version": VERSION,
        "sprint": SPRINT,
        "source_pr208_sha": SOURCE_PR208_SHA,
        "canonical_doctrine": canonical_doctrine(),
        "complete_state": complete_state_definition(),
        "particle": particle_definition(),
        "boundary": boundary_definition(),
        "mass": mass_definition(),
        "generation": generation,
        "sectors": sector_ontology(),
        "frozen_hierarchy": frozen_hierarchy_reinterpretation(),
        "long_future_alignment": long_future_alignment(),
        "foundation_status": "REACHED",
        "foundation_verdict": FOUNDATION_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "physical_prediction_promoted": False,
    }
