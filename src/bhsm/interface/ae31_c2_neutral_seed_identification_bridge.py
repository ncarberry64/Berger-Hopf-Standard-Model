"""Identify the historical neutral boundary seed with current-C2 mode slots."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

import numpy as np

from neutral_bridge_pmns_source import neutral_operator
from neutral_minimal_hessian import H_NU, neutral_cost

from bhsm.interface.completion.pair_wake_neutrino_bvp_v14_55 import (
    THREE_SHAPE_CHANNELS,
)
from bhsm.interface.ae31_c2_neutral_semigroup_response_transport import (
    neutral_internal_semigroup_shape,
)
from bhsm.interface.particle_chirality_anomaly_normalization import MODE_LEDGERS


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "AE31_CURRENT_C2_HISTORICAL_NEUTRAL_SEED_IDENTIFICATION_BRIDGE"


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def mode_coordinate_identification() -> dict[str, Any]:
    """Map current ``(k,j)`` modes to the historical ``(q,j)`` coordinates."""

    current_modes = tuple(MODE_LEDGERS["L_L"]["upper"])
    mapped = tuple((k - 2 * j, j) for k, j in current_modes)
    historical = ((0, 0), (3, 0), (1, 1))
    costs = tuple(neutral_cost(q, j) for q, j in mapped)
    return {
        "current_mode_coordinates": "(k,j)",
        "historical_seed_coordinates": "(q,j)_with_q=k-2j",
        "current_neutral_modes": [list(mode) for mode in current_modes],
        "mapped_historical_modes": [list(mode) for mode in mapped],
        "historical_neutral_modes": [list(mode) for mode in historical],
        "slotwise_identification_exact": mapped == historical,
        "historical_H_nu": [list(row) for row in H_NU],
        "historical_mode_costs": list(costs),
        "expected_mode_costs": [0, 9, 5],
        "mode_costs_recovered": costs == (0, 9, 5),
        "new_family_or_particle_ledger_created": False,
    }


def historical_neutral_seed_spectrum() -> dict[str, Any]:
    """Classify the exact historical kernel on the identified three slots."""

    exact = neutral_operator()
    kernel = np.asarray(exact, dtype=float)
    eigenvalues = np.linalg.eigvalsh(kernel)
    return {
        "exact_kernel": [[_fraction_text(value) for value in row] for row in exact],
        "characteristic_polynomial_det_xI_minus_K": (
            "x^3-(14/3)x^2+(175/36)x+5/27"
        ),
        "determinant": "-5/27",
        "leading_2x2_principal_minor": "-1/9",
        "eigenvalues": eigenvalues.tolist(),
        "one_negative_eigenvalue": int(np.count_nonzero(eigenvalues < 0.0)) == 1,
        "positive_semidefinite_stiffness": False,
        "Hermitian_boundary_response_seed": True,
        "common_shift_needed_for_positive_semidefinite": float(-eigenvalues[0]),
        "common_shift_action_derived": False,
        "kernel_may_be_called_physical_mass_squared": False,
    }


def historical_shape_channel_decomposition() -> dict[str, Any]:
    """Resolve ``K_nu`` on the predeclared v14.55 three-channel basis."""

    kernel = np.asarray(neutral_operator(), dtype=float)
    diagonal = np.diag(np.diag(kernel))
    remainder = kernel - diagonal
    channels = [
        np.asarray(row["matrix"], dtype=complex).real
        for row in THREE_SHAPE_CHANNELS
    ]
    coefficients = [float(np.sum(remainder * channel)) for channel in channels]
    reconstruction = diagonal + sum(
        coefficient * channel
        for coefficient, channel in zip(coefficients, channels)
    )
    return {
        "v14_55_channel_labels": [row["label"] for row in THREE_SHAPE_CHANNELS],
        "v14_55_channel_slots": [row["slot"] for row in THREE_SHAPE_CHANNELS],
        "normalized_channel_coefficients": coefficients,
        "exact_coefficients": ["0", "sqrt(2)/3", "sqrt(2)/6"],
        "diagonal_cost_block": diagonal.tolist(),
        "reconstruction_residual": float(np.linalg.norm(reconstruction - kernel)),
        "exact_reconstruction": bool(np.linalg.norm(reconstruction - kernel) < 1.0e-15),
        "direct_0_2_channel_present": False,
        "same_mode_labels_as_coordinate_bridge": [
            row["label"] for row in THREE_SHAPE_CHANNELS
        ] == ["M_(0,0)", "M_(3,0)", "M_(1,1)"],
        "channel_basis_action_selected": False,
        "channel_amplitudes_action_selected": False,
        "interpretation": (
            "THE_HISTORICAL_K_NU_OFF_DIAGONALS_LIVE_EXACTLY_IN_THE_"
            "PREDECLARED_V14_55_NONCOMMUTING_SHAPE_CHANNEL_BASIS"
        ),
    }


def algebraic_mixing_screen() -> dict[str, Any]:
    """Test the seed against the current neutral response and source slot."""

    kernel = np.asarray(neutral_operator(), dtype=float)
    response = np.asarray(
        neutral_internal_semigroup_shape()["semigroup_operator"], dtype=float
    )
    source_projector = np.diag((1.0, 0.0, 0.0))
    response_commutator = kernel @ response - response @ kernel
    source_commutator = kernel @ source_projector - source_projector @ kernel
    return {
        "commutator_norm_with_current_neutral_semigroup_shape": float(
            np.linalg.norm(response_commutator)
        ),
        "commutator_norm_with_canonical_first_slot_source": float(
            np.linalg.norm(source_commutator)
        ),
        "exact_first_slot_source_commutator_norm": "sqrt(2)/3",
        "noncommuting_family_shape_present": bool(
            np.linalg.norm(response_commutator) > 0.0
        ),
        "conditional_canonical_source_conversion_condition_satisfied": bool(
            np.linalg.norm(source_commutator) > 0.0
        ),
        "condition_is_sufficient_for_physical_oscillation": False,
        "why_conditional": (
            "THE_WEAK_FLAVOR_TO_INTERNAL_SLOT_INTERTWINER_AND_LORENTZIAN_"
            "PROPAGATION_OWNER_ARE_NOT_DERIVED"
        ),
    }


def provenance_and_owner_reconciliation() -> dict[str, Any]:
    return {
        "historical_status": "STRONGLY_SUPPORTED_BOUNDARY_SEED_CANDIDATE",
        "same_current_C2_mode_slots_identified": True,
        "eta_nu_action_source_derived": False,
        "beta_nu_action_source_derived": False,
        "kappa_nu_action_source_derived": False,
        "neutral_threshold_operator_derived": False,
        "physical_basis_and_scale_theorem_derived": False,
        "returned_Lorentzian_neutral_self_energy_derived": False,
        "historical_seed_promoted_to_current_action_term": False,
        "result": (
            "IDENTIFICATION_BRIDGE_CLOSED_ALGEBRAICALLY;_VARIATIONAL_AND_"
            "LORENTZIAN_OWNERSHIP_REMAINS_OPEN"
        ),
        "exact_next_owner": (
            "DERIVE_ETA_BETA_KAPPA_OR_THEIR_REPLACEMENT_FROM_THE_RETURNED_"
            "NEUTRAL_ACTION_HESSIAN_ON_THE_IDENTIFIED_CURRENT_C2_SLOTS"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_HISTORICAL_NEUTRAL_SEED_MODE_IDENTIFICATION_DERIVED": True,
        "CURRENT_C2_HISTORICAL_NEUTRAL_SEED_NONCOMMUTATION_DERIVED": True,
        "CURRENT_C2_HISTORICAL_NEUTRAL_SEED_INDEFINITE_NO_GO_DERIVED": True,
        "CURRENT_C2_ACTION_OWNED_NEUTRAL_MIXING_KERNEL_DERIVED": False,
        "CURRENT_C2_PHYSICAL_NEUTRINO_PROPAGATION_OPERATOR_DERIVED": False,
        "CURRENT_C2_PHYSICAL_PMNS_DERIVED": False,
        "CURRENT_C2_PHYSICAL_NEUTRINO_SPLITTINGS_DERIVED": False,
        "arbitrary_positive_shift_inserted": False,
        "measured_neutrino_data_used": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "algebraic_mixing_screen",
    "claim_boundary",
    "historical_neutral_seed_spectrum",
    "historical_shape_channel_decomposition",
    "mode_coordinate_identification",
    "provenance_and_owner_reconciliation",
]
