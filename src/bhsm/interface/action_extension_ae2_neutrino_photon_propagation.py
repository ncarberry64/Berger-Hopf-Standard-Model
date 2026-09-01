"""Provenance-safe photon/neutrino propagation audit for BHSM-AE-2.0.0.

The routines in this module do not add an action term.  They distinguish an
operator actually owned by AE2 from historical boundary seeds, conditional
effective propagation ansatzes, and frozen comparison outputs.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np


ACTION_VERSION = "BHSM-AE-2.0.0"
FULL_BHSM_COMPLETE = False

PROVENANCE_CLASSES = (
    "ACTION_DERIVED",
    "GEOMETRY_DERIVED",
    "OWNER_ONTOLOGY",
    "BOUNDARY_SEED",
    "FROZEN_OUTPUT",
    "CONDITIONAL",
    "HISTORICAL",
    "SUPERSEDED",
    "NOT_DERIVED",
)


def _hermitian(matrix: Sequence[Sequence[complex]], name: str) -> np.ndarray:
    value = np.asarray(matrix, dtype=complex)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be square")
    if not np.all(np.isfinite(value)) or not np.allclose(value, value.conj().T):
        raise ValueError(f"{name} must be finite Hermitian")
    return value


def electroweak_null_channel(
    g_2: float, g_1: float, orientation_stiffness: float
) -> dict[str, Any]:
    """Return the exact algebraic Q_em null-direction diagnostic.

    This is a representation/Higgs-block statement.  It deliberately does
    not promote the vector to a physical transverse photon channel.
    """

    g2 = float(g_2)
    g1 = float(g_1)
    stiffness = float(orientation_stiffness)
    if not all(math.isfinite(v) for v in (g2, g1, stiffness)):
        raise ValueError("finite electroweak inputs required")
    if g2 <= 0.0 or g1 <= 0.0 or stiffness < 0.0:
        raise ValueError("positive couplings and nonnegative stiffness required")
    factor = stiffness / 4.0
    matrix = factor * np.asarray(
        [
            [g2 * g2, 0.0, 0.0, 0.0],
            [0.0, g2 * g2, 0.0, 0.0],
            [0.0, 0.0, g2 * g2, -g2 * g1],
            [0.0, 0.0, -g2 * g1, g1 * g1],
        ]
    )
    null = np.asarray([0.0, 0.0, g1, g2])
    return {
        "basis": ["W1", "W2", "W3", "B"],
        "matrix": matrix.tolist(),
        "Q_em_null_vector": [0.0, 0.0, "g1", "g2"],
        "Q_em_null_residual": float(np.linalg.norm(matrix @ null)),
        "rank": int(np.linalg.matrix_rank(matrix, tol=1.0e-12)),
        "nullity": int(4 - np.linalg.matrix_rank(matrix, tol=1.0e-12)),
        "representation_null_direction_derived": True,
        "physical_transverse_domain_traced": False,
        "physical_photon_null_channel_derived": False,
    }


def neutral_seed_spectrum(
    kernel: Sequence[Sequence[complex]],
) -> dict[str, Any]:
    """Audit the historical K_nu boundary seed without promoting it."""

    value = _hermitian(kernel, "neutral boundary seed")
    eigenvalues = np.linalg.eigvalsh(value)
    return {
        "eigenvalues": [float(x) for x in eigenvalues],
        "positive_semidefinite": bool(np.min(eigenvalues) >= -1.0e-12),
        "positive_definite": bool(np.min(eigenvalues) > 1.0e-12),
        "linear_positive_stiffness_matrix": bool(
            np.min(eigenvalues) >= -1.0e-12
        ),
        "raw_seed_may_be_used_as_physical_mass_matrix": False,
    }


def oscillation_phase_scaling_gate(
    stiffness_eigenvalues: Sequence[float] | None,
    *,
    translation_energy_generator_owned: bool,
    physical_momentum_map_owned: bool,
) -> dict[str, Any]:
    """Type-check the physical L/E phase law before calling it oscillation."""

    values = None
    nontrivial_splittings = False
    if stiffness_eigenvalues is not None:
        values = np.asarray(stiffness_eigenvalues, dtype=float)
        if values.ndim != 1 or values.size != 3 or not np.all(np.isfinite(values)):
            raise ValueError("three finite stiffness eigenvalues required")
        nontrivial_splittings = bool(np.ptp(values) > 1.0e-12)
    owned = bool(
        values is not None
        and nontrivial_splittings
        and translation_energy_generator_owned
        and physical_momentum_map_owned
    )
    return {
        "stiffness_eigenvalues": None if values is None else values.tolist(),
        "nontrivial_splittings": nontrivial_splittings,
        "translation_energy_generator_owned": bool(
            translation_energy_generator_owned
        ),
        "physical_momentum_map_owned": bool(physical_momentum_map_owned),
        "formal_high_energy_law": (
            "Delta_Theta_ij=hbar*c*Delta_mu_ij^2*L/(2E)+O(E^-2)"
        ),
        "formal_dispersion": (
            "E^2=p^2*c^2+(hbar*c*mu)^2_ONLY_AFTER_THE_GENERATORS_ARE_OWNED"
        ),
        "physical_one_over_E_phase_derived": owned,
        "status": "DERIVED" if owned else "OPEN",
    }


def dimensionless_splitting_ratio(
    stiffness_eigenvalues: Sequence[float] | None,
) -> dict[str, Any]:
    """Return r_nu only for a nondegenerate ordered three-level operator."""

    if stiffness_eigenvalues is None:
        return {
            "ratio": None,
            "formula": "(mu_2^2-mu_1^2)/(mu_3^2-mu_1^2)",
            "status": "OPEN",
            "reason": "ACTION_OWNED_STIFFNESS_EIGENVALUES_ABSENT",
        }
    values = np.sort(np.asarray(stiffness_eigenvalues, dtype=float))
    if values.shape != (3,) or not np.all(np.isfinite(values)):
        raise ValueError("three finite stiffness eigenvalues required")
    denominator = values[2] - values[0]
    if abs(denominator) <= 1.0e-12:
        return {
            "ratio": None,
            "formula": "(mu_2^2-mu_1^2)/(mu_3^2-mu_1^2)",
            "status": "OPEN",
            "reason": "THREEFOLD_DEGENERACY_MAKES_RATIO_UNDEFINED",
        }
    return {
        "ratio": float((values[1] - values[0]) / denominator),
        "formula": "(mu_2^2-mu_1^2)/(mu_3^2-mu_1^2)",
        "status": "DERIVED",
        "reason": None,
    }


def propagation_family_adjudication() -> dict[str, Any]:
    """State the strongest exact common-family result on current disk."""

    return {
        "status": "PARTIAL",
        "shared_geometry": [
            "same_positive_lapse_forward_history_x(tau)=log_R4(tau)",
            "same_AE2_reset_glued_bundle_domain_at_the_event_child_seam",
            "fixed_round_spatial_eigenbasis_with_representation_dependent_blocks",
        ],
        "photon_or_gauge_exact_family": (
            "scalar/deRham_transfer:_-d_tau^2+c_rho*exp(-2x)"
        ),
        "fermion_exact_family": (
            "product_Dirac:_A_lambda^*A_lambda,_A_lambda=d_tau+"
            "chirality*lambda*exp(-x)"
        ),
        "schematic_universal_operator": (
            "P_rho=-D_tau^2+exp(-x)D_rho+exp(-2x)L_rho+C_rho"
        ),
        "schematic_universal_operator_status": "NOT_RECOVERED_AS_ONE_EXACT_OPERATOR",
        "why": (
            "THE_FACTORIZED_DIRAC_FORM_MUST_NOT_BE_EXPANDED_USING_AN_"
            "INDEPENDENT_s_prime_COEFFICIENT,_AND_THE_TRANSVERSE_GAUGE_"
            "CHANNEL_HAS_A_DISTINCT_DE_RHAM_AND_WENTZELL_DOMAIN"
        ),
        "identical_representations_assumed": False,
    }


def final_adjudication() -> dict[str, Any]:
    """Return the sprint's exact public status fields."""

    return {
        "PHOTON MECHANICAL STATUS": (
            "Q_EM_REPRESENTATION_NULL_DIRECTION_DERIVED_CONDITIONALLY;_"
            "PHYSICAL_TRANSVERSE_PROPAGATION_CHANNEL_OPEN"
        ),
        "NEUTRINO MECHANICAL STATUS": (
            "NEUTRAL_KINETIC_SUBCARRIER_SHARED_WITH_AE2;_ACTION_OWNED_"
            "THREE_SLOT_PROPAGATION_STIFFNESS_AND_MASS_RESPONSE_OPEN"
        ),
        "COMMON GEOMETRIC PROPAGATION FAMILY": "PARTIAL",
        "PHYSICAL PHOTON NULL CHANNEL": "OPEN",
        "ACTION-OWNED NEUTRAL THREE-SLOT PROPAGATION OPERATOR": "OPEN",
        "POSITIVE PROPAGATION-STIFFNESS MATRIX": "OPEN",
        "PMNS BASIS-MISMATCH DERIVATION": "OPEN",
        "1/E OSCILLATION PHASE LAW": "OPEN",
        "DIMENSIONLESS DELTA-M-SQUARED RATIO": "OPEN",
        "ABSOLUTE NEUTRINO MASS SCALE": "OPEN",
        "PI/3 CP HOLONOMY ATTACHMENT": "FLAVOR-SEED-ONLY",
        "GATE-7 RECONVERGENCE": "PARTIAL_SHARED_GEOMETRY",
        "FROZEN PREDICTIONS CHANGED": False,
        "FULL_BHSM_COMPLETE": False,
        "highest_upstream_new_dependency": (
            "ACTION_DERIVED_NEUTRAL_THREE_SLOT_INVARIANT_SUBBUNDLE_"
            "PROJECTOR_COMMUTING_WITH_D_AE2,_D_AE2_SQUARED,_THE_RESET_"
            "LIFT_U_R,_AND_THE_GAUGE_BRST_ACTION"
        ),
    }


__all__ = [
    "ACTION_VERSION",
    "FULL_BHSM_COMPLETE",
    "PROVENANCE_CLASSES",
    "electroweak_null_channel",
    "neutral_seed_spectrum",
    "oscillation_phase_scaling_gate",
    "dimensionless_splitting_ratio",
    "propagation_family_adjudication",
    "final_adjudication",
]
