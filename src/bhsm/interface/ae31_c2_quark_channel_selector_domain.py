"""Domain and state requirements for the current-C2 quark-channel selector."""

from __future__ import annotations

from math import isfinite
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_fixed_history_state_nonuniqueness import (
    pure_self_dual_covariance,
)
from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION


CLASSIFICATION = "AE31_CURRENT_C2_QUARK_CHANNEL_SELECTOR_DOMAIN_THEOREM"


def classical_selector_domain() -> dict[str, Any]:
    """Classify intrinsic and reduced-auxiliary Hessians without conflation."""

    return {
        "action_version": ACTION_VERSION,
        "intrinsic_quark_channel_coordinates": ["H_u", "H_d"],
        "intrinsic_H_u_H_d_are_active_AE31_fields": False,
        "intrinsic_reason": (
            "AE3_1_ADDS_ONE_CHARGED_LEPTON_INTRINSIC_H_FIELD_BUT_NO_"
            "QUARK_LR_HIGGS_TRILINEARS_OR_INDEPENDENT_H_u_H_d_COORDINATES"
        ),
        "intrinsic_quark_channel_Hessian_status": "UNDEFINED_ON_ACTIVE_FIELD_SPACE",
        "intrinsic_undefined_may_be_relabelled_zero": False,
        "reduced_auxiliary_probe_coordinates": ["HS_up", "HS_down"],
        "evaluated_fermion_background": "c_star=0",
        "reduced_product_Dirac_pure_HS_curvature": [[0.0, 0.0], [0.0, 0.0]],
        "reduced_probe_rank": 0,
        "reduced_probe_is_complete_dynamical_HS_Hessian": False,
        "reduced_zero_block_selects_physical_direction": False,
        "physical_zero_quark_Hessian_promoted": False,
    }


def hadamard_susceptibility_witness(theta: float) -> dict[str, Any]:
    """Exhibit state dependence of a finite two-channel loop susceptibility.

    The proxy ``Tr[P V_f (I-P) V_g]`` is the finite-dimensional particle-hole
    part of a quadratic response.  It is not promoted as the BHSM Hessian; it
    is a counterexample to deriving state independence from action/domain and
    Hadamard class alone.
    """

    angle = float(theta)
    if not isfinite(angle):
        raise ValueError("finite covariance angle required")
    covariance = pure_self_dual_covariance(angle)
    projection = np.asarray(covariance["covariance_theta"], dtype=complex)
    complement = np.eye(4, dtype=complex) - projection
    charge = np.asarray(covariance["charge_grading_matrix"], dtype=complex)
    vertices = (
        np.diag((1.0, 0.0, -1.0, 0.0)).astype(complex),
        np.diag((0.0, 1.0, 0.0, -1.0)).astype(complex),
    )
    response = np.asarray(
        [
            [np.trace(projection @ left @ complement @ right).real for right in vertices]
            for left in vertices
        ],
        dtype=float,
    )
    return {
        "theta": angle,
        "proxy_formula": "chi_fg(P)=Tr[P*V_f*(I-P)*V_g]",
        "vertex_charge_commutator_norms": [
            float(np.linalg.norm(vertex @ charge - charge @ vertex))
            for vertex in vertices
        ],
        "susceptibility_matrix": response.tolist(),
        "susceptibility_rank": int(np.linalg.matrix_rank(response, tol=1.0e-12)),
        "susceptibility_trace": float(np.trace(response)),
        "same_action_Dirac_domain_and_Hadamard_class": True,
        "finite_rank_smoothing_covariance_change": angle != 0.0,
        "proxy_is_physical_BHSM_quark_Hessian": False,
        "purpose": "STATE_INDEPENDENCE_COUNTEREXAMPLE_ONLY",
    }


def selector_state_dependence_theorem() -> dict[str, Any]:
    reference = hadamard_susceptibility_witness(0.0)
    rotated = hadamard_susceptibility_witness(np.pi / 6.0)
    first = np.asarray(reference["susceptibility_matrix"])
    second = np.asarray(rotated["susceptibility_matrix"])
    return {
        "reference": reference,
        "finite_rank_rotated": rotated,
        "response_difference_frobenius_norm": float(np.linalg.norm(second - first)),
        "response_changes_within_same_Hadamard_class": bool(
            np.linalg.norm(second - first) > 1.0e-12
        ),
        "action_and_domain_alone_fix_finite_channel_response": False,
        "Hadamard_singularity_condition_alone_fixes_finite_channel_response": False,
        "actual_BHSM_selector_state_independence_proved": False,
        "logical_consequence": (
            "A_CURRENT_C2_QUANTUM_CHANNEL_HESSIAN_REQUIRES_AN_ACTION_SELECTED_"
            "COVARIANCE_OR_A_DIRECT_PROOF_THAT_ITS_SELECTED_COMBINATION_IS_"
            "INDEPENDENT_OF_THE_SMOOTH_BISOLUTION_PART"
        ),
    }


def quantum_selector_contract() -> dict[str, Any]:
    return {
        "candidate_effective_functional": "Gamma_1loop[C,H]=-Tr_log(D_C[H])",
        "second_variation_identity": (
            "D_g_D_f_Gamma=Tr[G_C*V_g*G_C*V_f]-Tr[G_C*Q_fg]"
        ),
        "G_C": "STATE_DEPENDENT_CURRENT_C2_FEYNMAN_INVERSE",
        "V_f": "ACTION_OWNED_FIRST_HS_OR_INTRINSIC_HIGGS_VERTEX",
        "Q_fg": "ACTION_OWNED_TWO_CHANNEL_CONTACT_VERTEX",
        "current_AE31_V_up_V_down_intrinsic_vertices_present": False,
        "current_C2_complete_dynamical_HS_kernel_present": False,
        "current_C2_action_selected_Feynman_inverse_present": False,
        "historical_periodic_superdeterminant_may_replace_current_domain": False,
        "formula_currently_evaluable_as_physical_selector": False,
    }


def exact_dependency_order() -> dict[str, Any]:
    return {
        "steps": [
            {
                "order": 1,
                "object": "CURRENT_C2_ACTION_OWNED_QUARK_HIGGS_OR_HS_VERTICES_V_u_V_d_Q_fg",
                "present": False,
            },
            {
                "order": 2,
                "object": "CURRENT_C2_COMPLETE_DYNAMICAL_TWO_CHANNEL_KERNEL_ON_AE3_1_DOMAIN",
                "present": False,
            },
            {
                "order": 3,
                "object": "ACTION_SELECTED_FEYNMAN_COVARIANCE_OR_PROVED_STATE_INDEPENDENCE",
                "present": False,
            },
            {
                "order": 4,
                "object": "FULL_RENORMALIZED_2X2_CHANNEL_HESSIAN_AND_UNIQUE_EIGENDIRECTION",
                "present": False,
            },
        ],
        "first_missing_object": (
            "CURRENT_C2_ACTION_OWNED_QUARK_HIGGS_OR_HS_VERTICES_V_u_V_d_Q_fg"
        ),
        "state_selection_can_be_skipped_before_quantum_evaluation": False,
        "physical_channel_diagonalization_ready": False,
        "quark_mass_fit_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_AE31_INTRINSIC_QUARK_CHANNEL_HESSIAN_DOMAIN_CLASSIFIED": True,
        "CURRENT_AE31_INTRINSIC_QUARK_CHANNEL_HESSIAN_DEFINED": False,
        "CURRENT_C2_REDUCED_ZERO_HS_CURVATURE_IS_PHYSICAL_SELECTOR": False,
        "CURRENT_C2_QUANTUM_SELECTOR_STATE_DEPENDENCE_COUNTEREXAMPLE_DERIVED": True,
        "CURRENT_C2_ACTION_SELECTED_FERMION_COVARIANCE_DERIVED": False,
        "CURRENT_C2_QUARK_CHANNEL_DIRECTION_SELECTED": False,
        "CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_ACTION_OWNED": False,
        "CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED": False,
        "CKM_MATRIX_DERIVED": False,
        "MEASURED_QUARK_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "classical_selector_domain",
    "exact_dependency_order",
    "hadamard_susceptibility_witness",
    "quantum_selector_contract",
    "selector_state_dependence_theorem",
]
