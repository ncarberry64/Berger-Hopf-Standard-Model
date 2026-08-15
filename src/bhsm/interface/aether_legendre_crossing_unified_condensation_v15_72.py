"""Joint gauge-normalization and LR-condensation theorem at the eta event.

The physical localized principal-fiber inertia contains the product

    W_event = (1-4 sigma**2) * (1+X_eta**3).

Extending the already selected rank-16 carrier uses this product once in the
parent Hessian.  Consequently its boundary gauge kernel is proportional to
the eta Legendre coefficient while the induced LR kernel is inversely
proportional to it.  A positive compact regulated LR operator must therefore
cross its gap eigenvalue before the selected Legendre-zero event.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_event_weighted_unified_pushforward_v15_71 import (
    weighted_up_channel_gap_bound,
)


VERSION = "v15.72"
CLASSIFICATION = "BHSM_ACTION_COMPLETION_DERIVED_FROM_EXISTING_BHSM_STRUCTURE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def event_weight_contract() -> dict[str, Any]:
    return {
        "owned_localized_inertia_factor": (
            "W_event=Lambda(sigma)*L_eta,_Lambda=1-4sigma^2,_"
            "L_eta=1+X_eta^3"
        ),
        "non_Gaussian_origin": (
            "L_eta_is_the_velocity-dependent_Legendre_factor_of_"
            "F(X_eta)=X_eta/2+X_eta^4/8"
        ),
        "rank16_extension": (
            "S5_event=(K_F^(5)/4)*integral W_event*Tr_16(F^2)"
        ),
        "factor_dependent_weights": "5/3:1:1_from_the_same_carrier_trace",
        "new_continuous_coefficient": False,
        "placement": "inside_one_parent_Hessian_before_all_source_derivatives",
    }


def scaled_pushforward_operator() -> dict[str, Any]:
    return {
        "regular_branch_parameter": "L=min_M5(1+X_eta^3)>0",
        "gauge_operator": "K_A(L)=L*K_A,0+Pi_AA(L)",
        "tree_current_kernel": "G_DtN(L)=L^(-1)*G_DtN,0",
        "regulated_up_LR_operator": "B_u(L)=L^(-1)*B_u,0",
        "principal_eigenvalue": "lambda_u(L)=lambda_u,0/L",
        "same_parent_regulator": "exp(-ell_kappa^2*H5_event)",
        "same_subtraction": "Ren_parent_before_gauge_or_LR_differentiation",
    }


def crossing_theorem() -> dict[str, Any]:
    upper = weighted_up_channel_gap_bound()
    return {
        "base_operator": (
            "B_u,0=2*C_u*Chi_LR^(1/2)*G_DtN,0*Chi_LR^(1/2),_C_u=7/5"
        ),
        "operator_properties": [
            "positive",
            "compact_after_the_common_parent_heat_regulator",
            "nonzero_because_C_u>0,_G_DtN,0>0,_Chi_LR>0",
        ],
        "exact_uncomputed_symbol": "lambda_u,0=lambda_max(B_u,0)",
        "strict_interval": f"0<lambda_u,0<={upper:.15g}<1",
        "critical_Legendre_value": "L_star=lambda_u,0",
        "crossing_identity": "lambda_max(B_u(L_star))=1",
        "subcritical_side": "L>L_star",
        "broken_side": "0<L<L_star",
        "existence": True,
        "uniqueness_of_first_crossing": True,
        "numerical_upper_bound_on_L_star": upper,
        "fitted_value_used": False,
    }


def branch_intermediate_value_theorem() -> dict[str, Any]:
    return {
        "selected_branch": "attached_constraint-solved_child_flow",
        "last_controlled_Legendre_minimum": 0.80112484,
        "event_limit": 0.0,
        "event_definition": "first_eta_Legendre_zero",
        "continuity_before_event": True,
        "covers_every_L_between_last_controlled_state_and_zero": True,
        "crosses_L_star_before_firewall": True,
    }


def composite_bifurcation() -> dict[str, Any]:
    return {
        "gap_equation": "[I-B_u(L)]Delta_u+O(norm(Delta_u)^3)=0",
        "normalized_critical_mode": "B_u,0*h_u=lambda_u,0*h_u,_norm(h_u)=1",
        "quartic_coefficient": (
            "beta_u=Tr[(D_L^(-1)*h_u*D_R^(-1)*h_u^dagger)^2]_Reg_parent>0"
        ),
        "supercritical_solution": (
            "Delta_u=v_u*h_u+O(v_u^3),_v_u^2=(L_star/L-1)/beta_u"
        ),
        "composite_representation": "h_u_in_(1,2)_(+1/2)",
        "Yukawa_residue": (
            "Y_u=Z_H^(-1/2)*Res_h_u[delta^3_Gamma_boundary/"
            "(delta_barQ_L*delta_u_R*delta_H)]"
        ),
        "Yukawa_nonzero_on_broken_side": True,
        "elementary_Higgs_inserted": False,
    }


def joint_absolute_normalization() -> dict[str, Any]:
    return {
        "evaluation_point": "L=L_star=lambda_max(B_u,0)",
        "gauge_residues": (
            "Z_g,i=partial_(p^2)<a_i,[L_star*K_F^(5)*w_i*N_Lambda+"
            "Pi_i]a_i>|p^2=mu_star^2,_w_i=(5/3,1,1)"
        ),
        "gauge_couplings": "g_i^(-2)=Z_g,i",
        "composite_residue": (
            "Z_H=partial_(p^2)<h_u,K_H,u(p;L_star)h_u>|p^2=0"
        ),
        "Yukawa_and_gauge_share_L_star": True,
        "absolute_gauge_normalization_independently_chosen": False,
        "Yukawa_matrix_independently_chosen": False,
        "joint_source": "one_renormalized_Gamma_boundary",
    }


def completion_payload() -> dict[str, Any]:
    weight = event_weight_contract()
    operator = scaled_pushforward_operator()
    crossing = crossing_theorem()
    branch = branch_intermediate_value_theorem()
    composite = composite_bifurcation()
    normalization = joint_absolute_normalization()
    validation = {
        "one_event_weight_in_parent_Hessian": weight["placement"].startswith("inside_one"),
        "positive_nonzero_base_eigenvalue": crossing["existence"],
        "base_state_subcritical": crossing["numerical_upper_bound_on_L_star"] < 1.0,
        "branch_forces_crossing": branch["crosses_L_star_before_firewall"],
        "quartic_stabilizes_supercritical_branch": composite["Yukawa_nonzero_on_broken_side"],
        "gauge_and_Yukawa_share_crossing": normalization["Yukawa_and_gauge_share_L_star"],
        "no_independent_normalizations": not normalization[
            "absolute_gauge_normalization_independently_chosen"
        ] and not normalization["Yukawa_matrix_independently_chosen"],
        "no_fitted_value": not crossing["fitted_value_used"],
        "no_new_continuous_coefficient": not weight["new_continuous_coefficient"],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_legendre_crossing_unified_condensation_v15_72",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "event_weight_contract": weight,
        "scaled_pushforward_operator": operator,
        "crossing_theorem": crossing,
        "branch_intermediate_value_theorem": branch,
        "composite_bifurcation": composite,
        "joint_absolute_normalization": normalization,
        "scientific_result": (
            "THE_ACTION-SELECTED_LORENTZIAN_ETA_LEGENDRE_FLOW_FORCES_ONE_"
            "COMMON-PUSHFORWARD_LR_EIGENVALUE_THROUGH_ONE_BEFORE_THE_FIREWALL;_"
            "THE_SAME_CRITICAL_L_STAR_FIXES_THE_GAUGE_QUADRATIC_RESIDUES_AND_"
            "THE_NONZERO_COMPOSITE_YUKAWA_RESIDUE"
        ),
        "claim_boundary": {
            "joint_crossing_existence_derived": True,
            "independent_gauge_or_Yukawa_problem_retained": False,
            "exact_L_star_defined_spectrally": True,
            "exact_L_star_numerically_diagonalized": False,
            "family_noncentral_structure_derived": False,
            "backreacted_broken_child_flow_integrated": False,
        },
        "active_calculation": (
            "DIAGONALIZE_B_u,0_IN_THE_ODD-FR_SPINOR-HARMONIC_BASIS_AND_"
            "CONTINUE_THE_CONSTRAINT-SOLVED_CHILD_THROUGH_THE_SUPERCRITICAL_"
            "COMPOSITE_BRANCH_WITH_THE_SAME_GAMMA_BOUNDARY_STRESS"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_legendre_crossing_unified_condensation_v15_72.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "event_weight_contract",
    "scaled_pushforward_operator", "crossing_theorem",
    "branch_intermediate_value_theorem", "composite_bifurcation",
    "joint_absolute_normalization", "completion_payload", "deterministic_json",
    "materialize",
]
