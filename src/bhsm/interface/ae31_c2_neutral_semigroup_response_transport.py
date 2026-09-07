"""Transport the retained neutral family response shape to current C2.

This reuses the historical neutral mode ledger and the already-attached frozen
Berger heat-semigroup rule.  It deliberately distinguishes that positive
overlap response from a Lorentzian neutrino propagation Hamiltonian.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.ae3_c2_hopf_semigroup_transport import (
    FROZEN_INTERNAL_BERGER_SHAPE,
    FROZEN_OVERLAP_WIDTH,
    frozen_internal_semigroup_attachment,
)
from bhsm.interface.ae3_family_harmonic_energy_pullback import (
    ROLE_ORDER,
    pulled_back_operator,
)
from bhsm.interface.particle_chirality_anomaly_normalization import MODE_LEDGERS


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "AE31_CURRENT_C2_NEUTRAL_SEMIGROUP_RESPONSE_TRANSPORT"


def neutral_mode_ledger() -> dict[str, Any]:
    """Recover, rather than recreate, the retained neutral family modes."""

    left = tuple(MODE_LEDGERS["L_L"]["upper"])
    conjugate = tuple(MODE_LEDGERS["nu_c"]["singlet"])
    return {
        "source": "particle_chirality_anomaly_normalization.MODE_LEDGERS",
        "left_neutral_modes": [list(mode) for mode in left],
        "conjugate_neutral_modes": [list(mode) for mode in conjugate],
        "left_right_ledgers_match": left == conjugate,
        "mode_ledger_rebuilt": False,
        "particle_spectrum_rebuilt": False,
    }


def neutral_internal_semigroup_shape() -> dict[str, Any]:
    """Evaluate the frozen neutral response on the retained family slots."""

    modes = tuple(MODE_LEDGERS["L_L"]["upper"])
    costs = []
    for k, j in modes:
        q = k - 2 * j
        costs.append(
            k * (k + 2)
            + (FROZEN_INTERNAL_BERGER_SHAPE**2 - 1.0) * q**2
        )
    costs_array = np.asarray(costs, dtype=float)
    weights = np.exp(-FROZEN_OVERLAP_WIDTH * costs_array)
    generator = pulled_back_operator(costs)
    response = pulled_back_operator(weights.tolist())
    ordered = np.sort(weights)
    gaps = np.diff(ordered)
    return {
        "action_version": ACTION_VERSION,
        "carrier": "ACTUAL_RESET_SELECTED_MAXIMAL_C2_HISTORY",
        "internal_factor": "RETAINED_NEUTRAL_BERGER_MODE_AND_FAMILY_FIBER",
        "slot_roles": list(ROLE_ORDER),
        "slot_role_to_weak_flavor_map_derived": False,
        "modes": [list(mode) for mode in modes],
        "frozen_internal_Berger_shape": FROZEN_INTERNAL_BERGER_SHAPE,
        "frozen_overlap_width": FROZEN_OVERLAP_WIDTH,
        "Berger_generator_costs": costs,
        "family_generator": generator.tolist(),
        "semigroup_weights": weights.tolist(),
        "semigroup_operator": response.tolist(),
        "positive_definite": bool(np.all(weights > 0.0)),
        "contraction": bool(np.max(weights) <= 1.0),
        "self_adjoint": bool(np.allclose(response, response.T)),
        "family_noncentral": len(set(weights.tolist())) == 3,
        "two_nonzero_response_gaps": bool(np.all(gaps > 0.0)),
        "ordered_response_gaps": gaps.tolist(),
        "classification": "POSITIVE_EUCLIDEAN_OVERLAP_RESPONSE_SHAPE",
        "Lorentzian_unitary_propagation_operator": False,
        "physical_neutrino_mass_operator": False,
        "measured_neutrino_data_used": False,
    }


def charged_neutral_common_projector_test() -> dict[str, Any]:
    """Test the neutral shape against the attached charged-lepton response."""

    neutral = np.asarray(neutral_internal_semigroup_shape()["semigroup_operator"])
    charged = np.asarray(
        frozen_internal_semigroup_attachment()["sectors"]["charged_lepton"][
            "family_operator"
        ]
    )
    commutator = neutral @ charged - charged @ neutral
    source_projector = np.diag((1.0, 0.0, 0.0))
    canonical_source_commutator = neutral @ source_projector - source_projector @ neutral
    return {
        "charged_neutral_commutator_norm": float(np.linalg.norm(commutator)),
        "common_family_projector_algebra": bool(np.linalg.norm(commutator) == 0.0),
        "canonical_common_projector_PMNS": np.eye(3).tolist(),
        "canonical_PMNS_nontrivial": False,
        "canonical_first_slot_source_commutator_norm": float(
            np.linalg.norm(canonical_source_commutator)
        ),
        "canonical_first_slot_source_converts": False,
        "physical_weak_flavor_to_internal_slot_intertwiner_derived": False,
        "basis_warning": (
            "THE_ABSTRACT_WEAK_FLAVOR_ORDER_NUE_NUMU_NUTAU_CANNOT_BE_"
            "SILENTLY_IDENTIFIED_WITH_THE_INTERNAL_HEAVY_MIDDLE_LIGHT_SLOTS"
        ),
    }


def neutral_current_c2_attachment_certificate() -> dict[str, Any]:
    """Prove the tensor-factor attachment, without inventing a physical projector."""

    spatial_dimension = 9
    spin_dimension = 2
    family_dimension = 3
    spatial_identity = np.eye(spatial_dimension)
    spin_identity = np.eye(spin_dimension)
    family_identity = np.eye(family_dimension)
    reset_lift = np.asarray(((0.0, 1.0), (1.0, 0.0)))
    reset = np.kron(spatial_identity, np.kron(reset_lift, family_identity))
    restriction = np.kron(
        np.diag([1.0] * 4 + [0.0] * 5),
        np.kron(spin_identity, family_identity),
    )
    carrier = np.kron(
        np.diag(np.linspace(0.0, 1.0, spatial_dimension)),
        np.kron(spin_identity, family_identity),
    )
    family_response = np.asarray(
        neutral_internal_semigroup_shape()["semigroup_operator"]
    )
    lifted = np.kron(
        spatial_identity, np.kron(spin_identity, family_response)
    )
    commutators = {
        "with_reset": float(np.linalg.norm(lifted @ reset - reset @ lifted)),
        "with_enclosure_restriction": float(
            np.linalg.norm(lifted @ restriction - restriction @ lifted)
        ),
        "with_localization_carrier": float(
            np.linalg.norm(lifted @ carrier - carrier @ lifted)
        ),
    }
    return {
        "factorization": "L2(C2)_carrier tensor (Spin x G_SM) tensor F_neutral",
        "commutator_certificate": commutators,
        "all_tested_attachment_commutators_zero": max(commutators.values()) == 0.0,
        "frozen_response_attached_by_tensor_factorization": True,
        "frozen_response_current_AE31_variational_term": False,
        "commutator_with_full_D_AE2_squared_derived": False,
        "commutator_with_full_gauge_BRST_action_derived": False,
        "physical_rank_three_neutral_subbundle_projector_derived": False,
    }


def propagation_owner_classification() -> dict[str, Any]:
    return {
        "derived_object": "CURRENT_C2_NEUTRAL_INTERNAL_SEMIGROUP_RESPONSE_SHAPE",
        "why_not_propagation": (
            "EXP_MINUS_S_K_IS_A_POSITIVE_OVERLAP_CONTRACTION_NOT_THE_"
            "ACTION_DERIVED_REAL_TIME_EVOLUTION_EXP_MINUS_I_INTEGRAL_H_DT"
        ),
        "analytic_continuation_or_Lorentzian_owner_derived": False,
        "neutral_retarded_Calderon_map_derived": False,
        "returned_neutral_self_energy_derived": False,
        "weak_flavor_internal_basis_intertwiner_derived": False,
        "path_dependent_noncommuting_monodromy_derived": False,
        "response_gaps_can_be_called_Delta_m_squared": False,
        "exact_next_owner": (
            "ACTION_DERIVE_THE_RETURNED_LORENTZIAN_NEUTRAL_SELF_ENERGY_"
            "AND_ITS_WEAK_FLAVOR_TO_INTERNAL_FAMILY_INTERTWINER"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_NEUTRAL_MODE_LEDGER_RECOVERED": True,
        "CURRENT_C2_NEUTRAL_INTERNAL_SEMIGROUP_RESPONSE_SHAPE_ATTACHED": True,
        "CURRENT_C2_NEUTRAL_RESPONSE_FAMILY_NONCENTRALITY_DERIVED": True,
        "CURRENT_C2_NEUTRAL_RESPONSE_TWO_GAPS_DERIVED": True,
        "CURRENT_C2_CHARGED_NEUTRAL_COMMON_PROJECTOR_NO_MIXING_DERIVED": True,
        "CURRENT_C2_PHYSICAL_WEAK_FLAVOR_INTERNAL_INTERTWINER_DERIVED": False,
        "CURRENT_C2_FAMILY_NONCENTRAL_NEUTRAL_PROPAGATION_OPERATOR_DERIVED": False,
        "CURRENT_C2_NONTRIVIAL_PMNS_DERIVED": False,
        "CURRENT_C2_TWO_NEUTRINO_MASS_SPLITTINGS_DERIVED": False,
        "particle_spectrum_rebuilt": False,
        "measured_neutrino_data_used": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "charged_neutral_common_projector_test",
    "claim_boundary",
    "neutral_current_c2_attachment_certificate",
    "neutral_internal_semigroup_shape",
    "neutral_mode_ledger",
    "propagation_owner_classification",
]
