"""Current-C2 incidence and selection rule for an ell=2 capture response."""

from __future__ import annotations

from math import pi, sqrt
from typing import Any

from bhsm.interface.ae31_c2_coexact_su2l_charged_current import (
    weak_charged_representation_ledger,
)
from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import (
    action_composition_contract,
)
from bhsm.interface.completion.differential_shear_softening_v14_83 import (
    completion_payload as shear_payload,
)
from bhsm.interface.completion.stationary_full_preimage_transport_no_go_v14_85 import (
    completion_payload as stationary_shear_payload,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "AE31_CURRENT_C2_R2_ELECTRON_CAPTURE_SELECTION_RULE"


def normalized_s3_rank2_witness() -> dict[str, Any]:
    """Exact rank-zero/rank-two multiplication witness on the unit S3."""

    volume = 2.0 * pi**2
    y0 = 1.0 / sqrt(volume)
    # For a uniform point on S3 subset R4,
    # E[(x1^2-x2^2)^2]=1/6 and E[x1^2-x2^2]=0.
    raw_rank2_norm_squared = volume / 6.0
    normalization = 1.0 / sqrt(raw_rank2_norm_squared)
    diagonal = 0.0
    rank0_to_rank2 = y0
    return {
        "rank0_harmonic": "Y0=1/sqrt(2*pi^2)",
        "rank2_harmonic": "Y2=(sqrt(3)/pi)*(x1^2-x2^2)",
        "S3_volume": volume,
        "rank2_normalization": normalization,
        "rank2_mean": 0.0,
        "rank2_norm_squared": 1.0,
        "diagonal_Gaunt_000_to_2": diagonal,
        "off_diagonal_Gaunt_0_2_2": rank0_to_rank2,
        "lowest_isotropic_mode_first_order_diagonal_shift": 0.0,
        "rank0_to_rank2_mixing_allowed": rank0_to_rank2 > 0.0,
    }


def recovered_r2_provenance() -> dict[str, Any]:
    """Separate the exact shear theorem from a physical capture coordinate."""

    shear = shear_payload()
    stationary = stationary_shear_payload()
    return {
        "historical_exact_operator": shear["reduced_theorem"]["linearized_stiffness"],
        "historical_scalarized_notation": "r2_eff=r2_0-chi2*D_shear",
        "notation_status": (
            "A_SCALAR_EIGENCHANNEL_SUMMARY_OF_H_EFF_NOT_AN_INDEPENDENT_"
            "ELECTRON_ORBITAL_OR_CURRENT_C2_ACTION_FIELD"
        ),
        "conditional_equal_inertia_chi2": shear["reduced_theorem"][
            "equal_inertia_ell2"
        ],
        "current_stationary_branch_Delta_A": stationary["v14_84_evaluation"][
            "Delta_A_on_present_branch"
        ],
        "current_stationary_branch_shear_operator": stationary[
            "v14_84_evaluation"
        ]["normalized_shear_operator"],
        "positive_semidefinite_sign_theorem_reusable": stationary[
            "v14_84_evaluation"
        ]["positive_semidefinite_sign_theorem_preserved"],
        "nonzero_physical_r2_transport_derived": False,
        "r2_is_a_capturable_electron_state_derived": False,
    }


def electron_metric_incidence_contract() -> dict[str, Any]:
    """Attach ell=2 geometry to the covariant lepton action, conditionally."""

    action = action_composition_contract()
    return {
        "lepton_action_owner": action["action_version"],
        "metric_variation_identity": (
            "delta_h S_e=(1/2)*integral_sqrt(-g)*h_mu_nu*T_e^(mu_nu)"
        ),
        "conditional_ell2_attachment": "h_mu_nu=r2*h_mu_nu^(ell2)",
        "mixed_incidence": (
            "partial^2 S_e/(partial r2 partial Psi_e)=variation_of_D_e_"
            "along_h^(ell2)"
        ),
        "new_electron_shear_coefficient_required": False,
        "historical_full_preimage_H2_to_current_M4_metric_intertwiner_derived": False,
        "therefore_current_C2_numeric_mixed_block_derived": False,
        "round_lowest_multiplet_trace_selection_rule": (
            "Tr_lowest(P*delta_D[h_ell2]*P)=0_FOR_AN_ISOTROPIC_ROUND_"
            "MULTIPLET_TRACE_BY_SO4_HARMONIC_ORTHOGONALITY"
        ),
        "full_lowest_spinor_matrix_evaluated": False,
        "allowed_first_order_role": (
            "ELL0_TO_ELL2_MIXING_OR_INTERNAL_MULTIPLET_SPLITTING_NOT_AN_"
            "ISOTROPIC_ELL0_DIAGONAL_BINDING_TERM"
        ),
    }


def capture_vertex_and_hessian_gate() -> dict[str, Any]:
    """Locate the exact missing blocks of p+e -> n+nu_e."""

    current = weak_charged_representation_ledger()
    return {
        "attached_leptonic_current": "bar(nu_eL)*gamma^mu*e_L",
        "attached_quark_current": "sum_color(bar(u_L)*gamma^mu*d_L)",
        "current_family_action": current["family_action"],
        "capture_amplitude_factorization": (
            "A_EC=<nu_e|J_lep^mu|e_env>*<n|J_had_mu|p>"
        ),
        "electron_environment_operator": (
            "D_e_env=D_e+M_EM+M_residual_hadronic+delta_D[h_ell2]"
        ),
        "capture_hessian_required_blocks": [
            "electron_environment_Dirac_block",
            "proton_neutron_returned_composite_block",
            "hadronic_weak_current_matrix_element",
            "outgoing_neutrino_boundary_trace_block",
        ],
        "leptonic_weak_representation_attached": True,
        "quark_weak_representation_attached": True,
        "physical_proton_neutron_states_derived": False,
        "physical_hadronic_weak_matrix_element_derived": False,
        "complete_electron_environment_operator_derived": False,
        "capture_Hessian_derived": False,
        "stationary_capturable_electron_mode_derived": False,
    }


def scientific_decision() -> dict[str, Any]:
    return {
        "r2_enters_in_principle": (
            "YES_AS_AN_ACTION_METRIC_VARIATION_AFTER_THE_H2_TO_M4_"
            "INTERTWINER_IS_DERIVED"
        ),
        "r2_produces_isotropic_lowest_stationary_electron_mode_at_first_order": False,
        "reason": (
            "AN_ELL2_TRACEFREE_PERTURBATION_HAS_ZERO_ISOTROPIC_MULTIPLET_"
            "TRACE_ON_THE_ROUND_LOWEST_CHANNEL;_THE_UNEVALUATED_FULL_SPINOR_"
            "BLOCK_MAY_MIX_OR_SPLIT_MODES_BUT_CANNOT_SUPPLY_A_COMMON_"
            "ISOTROPIC_BINDING_SHIFT"
        ),
        "r2_may_dress_a_capture_state": True,
        "r2_may_be_renamed_the_capture_orbital": False,
        "exact_next_object": (
            "DRIVEN_CURRENT_C2_NUCLEAR_COMPOSITE_BACKGROUND_WITH_ACTION_OWNED_"
            "H2_TO_M4_METRIC_TRACE_COMPLETE_EM_RESPONSE_AND_PROTON_NEUTRON_"
            "WEAK_MATRIX_ELEMENT"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_R2_PROVENANCE_RECONSTRUCTED": True,
        "CURRENT_C2_ELL2_ISOTROPIC_LOWEST_TRACE_SELECTION_RULE_DERIVED": True,
        "CURRENT_C2_ELL0_TO_ELL2_MIXING_CHANNEL_DERIVED": True,
        "CURRENT_C2_FULL_LOWEST_SPINOR_ELL2_BLOCK_DERIVED": False,
        "CURRENT_C2_R2_TO_M4_METRIC_INTERTWINER_DERIVED": False,
        "CURRENT_C2_ELECTRON_NUCLEAR_CAPTURE_HESSIAN_DERIVED": False,
        "CURRENT_C2_STATIONARY_CAPTURABLE_ELECTRON_MODE_DERIVED": False,
        "CURRENT_C2_PHYSICAL_ELECTRON_CAPTURE_AMPLITUDE_DERIVED": False,
        "CURRENT_C2_OUTGOING_NEUTRINO_BOUNDARY_MODE_DERIVED": False,
        "measured_capture_or_neutrino_data_used": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "capture_vertex_and_hessian_gate",
    "claim_boundary",
    "electron_metric_incidence_contract",
    "normalized_s3_rank2_witness",
    "recovered_r2_provenance",
    "scientific_decision",
]
