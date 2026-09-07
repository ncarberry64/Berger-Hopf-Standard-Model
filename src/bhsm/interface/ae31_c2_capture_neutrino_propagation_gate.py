"""Capture-source to propagation-dependent neutrino operator gate."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from bhsm.interface.ae31_c2_coexact_su2l_charged_current import (
    weak_charged_representation_ledger,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "AE31_CURRENT_C2_CAPTURE_NEUTRINO_PROPAGATION_GATE"


def electron_capture_family_source() -> dict[str, Any]:
    """Return the electron-flavor source selected by the charged current."""

    state = np.asarray((1.0, 0.0, 0.0), dtype=complex)
    current = weak_charged_representation_ledger()
    return {
        "family_basis": ["nu_e", "nu_mu", "nu_tau"],
        "source_vector": state.real.tolist(),
        "source_projector": np.outer(state, state.conj()).real.tolist(),
        "charged_current_family_action": current["family_action"],
        "production_statement": "CAPTURE_SELECTS_AN_INITIAL_NU_E_WEAK_SOURCE",
        "fixed_mass_eigenstate_selected_at_production": False,
        "propagation_operator_selected_at_production": False,
    }


def family_central_propagation(
    initial_state: Iterable[complex], scalar_phase: float
) -> dict[str, Any]:
    """Prove that a family-central environment changes only common phase."""

    initial = np.asarray(tuple(initial_state), dtype=complex)
    if initial.shape != (3,) or not np.isclose(np.vdot(initial, initial), 1.0):
        raise ValueError("initial_state must be a normalized C3 vector")
    phase = float(scalar_phase)
    if not np.isfinite(phase):
        raise ValueError("scalar_phase must be finite")
    evolution = np.exp(-1.0j * phase) * np.eye(3)
    final = evolution @ initial
    initial_probabilities = np.abs(initial) ** 2
    final_probabilities = np.abs(final) ** 2
    return {
        "evolution": evolution,
        "initial_probabilities": initial_probabilities.tolist(),
        "final_probabilities": final_probabilities.tolist(),
        "probability_change_norm": float(
            np.linalg.norm(final_probabilities - initial_probabilities)
        ),
        "flavor_change": False,
        "theorem": "K_nu(x)=kappa(x)*I3_IMPLIES_U=exp(-i*Phi)*I3",
    }


def common_shift_invariance(
    family_operator: Iterable[Iterable[complex]], common_shift: float
) -> dict[str, Any]:
    """Show that curvature/common environment shifts no oscillation gap."""

    operator = np.asarray(tuple(tuple(row) for row in family_operator), dtype=complex)
    if operator.shape != (3, 3) or not np.allclose(
        operator, operator.conj().T, atol=1.0e-12
    ):
        raise ValueError("family_operator must be a Hermitian 3x3 matrix")
    shift = float(common_shift)
    if not np.isfinite(shift):
        raise ValueError("common_shift must be finite")
    eigenvalues = np.linalg.eigvalsh(operator)
    shifted = np.linalg.eigvalsh(operator + shift * np.eye(3))
    gaps = np.asarray(
        (eigenvalues[1] - eigenvalues[0], eigenvalues[2] - eigenvalues[1])
    )
    shifted_gaps = np.asarray((shifted[1] - shifted[0], shifted[2] - shifted[1]))
    return {
        "eigenvalues": eigenvalues.tolist(),
        "shifted_eigenvalues": shifted.tolist(),
        "independent_adjacent_gaps": gaps.tolist(),
        "shifted_adjacent_gaps": shifted_gaps.tolist(),
        "gap_invariance_residual": float(np.linalg.norm(shifted_gaps - gaps)),
        "common_environment_generates_splittings": False,
    }


def squared_neutral_operator_contract() -> dict[str, Any]:
    """Separate a local D^2 response from a physical mass observable."""

    return {
        "schematic_operator": (
            "D_nu_eff=slash_nabla+Sigma_curvature+Sigma_weak+Sigma_environment"
        ),
        "Lichnerowicz_scalar_term": "D_slash^2=-nabla^2+R/4+gauge_curvature",
        "R_over_4_family_action": "(R/4)*I3",
        "curvature_alone_generates_family_splittings": False,
        "local_D_squared_eigenvalue_is_automatically_a_mass_squared": False,
        "reason": (
            "THE_SPECTRUM_ALSO_CONTAINS_MOMENTUM_CURVATURE_GAUGE_POTENTIAL_"
            "AND_BOUNDARY_DATA"
        ),
        "admissible_masslike_readout": (
            "SUBTRACTED_ZERO_MOMENTUM_POLE_OR_PARENT_RELATIVE_CYCLE_"
            "QUASI_ENERGY_OF_THE_PROPAGATING_MODE"
        ),
        "environment_dependent_mass_support_possible_in_principle": True,
        "environment_dependent_mass_support_action_derived": False,
    }


def family_noncentrality_theorem() -> dict[str, Any]:
    return {
        "current_capture_source_family_kernel": "I3",
        "scalar_curvature_family_kernel": "I3",
        "family_central_weak_environment_changes_common_phase_only": True,
        "necessary_for_oscillation": (
            "K_nu_family(x)_NOT_PROPORTIONAL_TO_I3_WITH_AT_LEAST_TWO_"
            "NONZERO_EIGENVALUE_DIFFERENCES_AFTER_TRANSPORT"
        ),
        "additional_conversion_condition": (
            "[K_nu_family(x),P_nu_e]_NOT_IDENTICALLY_ZERO_OR_EQUIVALENT_"
            "NONTRIVIAL_PATH_ORDERED_MONODROMY"
        ),
        "family_noncentrality_alone_sufficient_for_flavor_conversion": False,
        "common_shift_cancels_from_all_oscillation_phases": True,
        "position_dependent_eigenvectors_require_path_ordering": True,
        "unitary_transport_condition": "K_nu_family(x)=K_nu_family(x)^dagger",
        "current_C2_family_noncentral_neutral_operator_derived": False,
    }


def capture_boundary_to_propagation_contract() -> dict[str, Any]:
    return {
        "chain": [
            "electron_nuclear_capture_Hessian",
            "outgoing_nu_e_boundary_source_trace",
            "retarded_or_positive_frequency_neutral_Calderon_map",
            "transported_family_neutral_operator_K_nu(x)",
            "subtracted_pole_or_cycle_quasi_energy_readout",
        ],
        "boundary_equation": (
            "gamma_Sigma(nu)=G_nu_retarded*J_capture[p,e_to_n,nu_e]"
        ),
        "capture_Hessian_derived": False,
        "outgoing_nu_e_boundary_trace_derived": False,
        "physical_neutral_outer_Green_operator_derived": False,
        "family_noncentral_K_nu_x_derived": False,
        "two_nonzero_propagation_splittings_derived": False,
        "PMNS_detector_map_derived": False,
    }


def historical_neutrino_reconciliation() -> dict[str, Any]:
    return {
        "v14_55_reusable_ontology": [
            "PROPAGATION_PHASE_MAY_DEPEND_ON_ENVIRONMENT",
            "INSTANTANEOUS_WAKE_RESPONSE_IS_NOT_A_PRIMITIVE_STATIC_MASS",
            "PARENT_RELATIVE_CYCLE_QUASI_ENERGY_IS_THE_CANDIDATE_MASS_READOUT",
        ],
        "v14_55_status": "FORMALIZED_HYPOTHESIS_NOT_ACTION_DERIVED",
        "current_owner": (
            "RETURNED_RECONSTRUCTED_SPACETIME_NEUTRAL_SELF_ENERGY_AND_"
            "PROPAGATION_MONODROMY"
        ),
        "capture_event_role": (
            "SETS_THE_INITIAL_WEAK_SOURCE_AND_BOUNDARY_GEOMETRY_NOT_A_"
            "MEASURED_OR_FIXED_NEUTRINO_MASS"
        ),
        "detector_flavor_response_identified_with_mass_eigenbasis": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_CAPTURE_INITIAL_NUE_FAMILY_SOURCE_DERIVED": True,
        "CURRENT_C2_FAMILY_CENTRAL_PROPAGATION_NO_OSCILLATION_THEOREM_DERIVED": True,
        "CURRENT_C2_COMMON_ENVIRONMENT_SHIFT_GAP_INVARIANCE_DERIVED": True,
        "CURRENT_C2_CURVATURE_ALONE_NEUTRINO_SPLITTING_NO_GO_DERIVED": True,
        "CURRENT_C2_CAPTURE_OUTGOING_NEUTRINO_BOUNDARY_MODE_DERIVED": False,
        "CURRENT_C2_FAMILY_NONCENTRAL_NEUTRAL_OPERATOR_DERIVED": False,
        "CURRENT_C2_NONTRIVIAL_NEUTRAL_FLAVOR_MONODROMY_DERIVED": False,
        "CURRENT_C2_NEUTRINO_MASS_SUPPORT_PROPAGATION_DEPENDENCE_DERIVED": False,
        "CURRENT_C2_TWO_NEUTRINO_SPLITTINGS_DERIVED": False,
        "CURRENT_C2_PMNS_DERIVED": False,
        "measured_neutrino_data_used": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "capture_boundary_to_propagation_contract",
    "claim_boundary",
    "common_shift_invariance",
    "electron_capture_family_source",
    "family_central_propagation",
    "family_noncentrality_theorem",
    "historical_neutrino_reconciliation",
    "squared_neutral_operator_contract",
]
