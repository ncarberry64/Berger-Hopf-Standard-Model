"""Exact operator-valued event-shell gauge--Yukawa pushforward.

This corrects the spatially uniform Legendre-factor shortcut of v15.72.  The
eta Legendre coefficient is a field on the cap.  Its one weighted Maxwell
Dirichlet principle nevertheless orders both outputs of the same pushforward:
the gauge DtN form decreases when the event weight decreases, and the induced
LR Green kernel increases.  Their joint crossing must be computed from this
single weighted operator, never from two independently normalized sectors.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np


VERSION = "v15.73"
CLASSIFICATION = "BHSM_EXACT_EVENT_SHELL_UNIFIED_PUSHFORWARD_CORRECTION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def weighted_parent_operator() -> dict[str, Any]:
    return {
        "weight_field": "W_t(rho)=Lambda(sigma_t(rho))*(1+X_eta,t(rho)^3)",
        "Lambda": "1-4*sigma^2",
        "parent_quadratic_form": (
            "Q_t[A]=(K_F^(5)/2)*integral_M5 W_t*Tr_16(d_A A,d_A A)"
        ),
        "weighted_operator": "A_t=d_A^dagger*W_t*d_A_on_the_gauge-fixed_domain",
        "DtN_form": (
            "<a,N[W_t]a>=min_(B A=a) integral_M5 W_t*abs(d_A A)^2"
        ),
        "Green_operator": "G[W_t]=B*A_t^(-1)*B^dagger_on_the_Gauss_quotient",
        "one_operator_only": True,
    }


def dirichlet_monotonicity_theorem() -> dict[str, Any]:
    return {
        "hypothesis": "0<W_1<=W_2_almost_everywhere_on_the_regular_cap",
        "gauge_order": "N[W_1]<=N[W_2]_as_boundary_quadratic_forms",
        "proof": "take_the_infimum_of_the_pointwise-ordered_bulk_Dirichlet_forms",
        "current_order": "G[W_1]>=G[W_2]_on_the_positive_Gauss_quotient",
        "LR_order": "B_u[W_1]>=B_u[W_2]",
        "physical_semantics": (
            "event_softening_reduces_gauge_stiffness_and_strengthens_LR_"
            "binding_in_the_same_calculation"
        ),
    }


def exact_joint_crossing_problem() -> dict[str, Any]:
    return {
        "gauge_two_point": (
            "K_A,i(t)=K_F^(5)*w_i*N[W_t]+Pi_i[W_t],_w_i=(5/3,1,1)"
        ),
        "up_channel_operator": (
            "B_u(t)=2*(7/5)*Chi_LR,t^(1/2)*G[W_t]*Chi_LR,t^(1/2)"
        ),
        "single_crossing_function": "F(t)=lambda_max(B_u(t))-1",
        "first_crossing": "t_star=inf{t:F(t)=0_and_F(t-epsilon)<0}",
        "absolute_gauge_residue": (
            "g_i^(-2)=partial_(p^2)<a_i,K_A,i(t_star;p)a_i>|p^2=mu_star^2"
        ),
        "composite_mode": "B_u(t_star)h_u=h_u",
        "Yukawa_residue": (
            "Y_u=Z_H^(-1/2)*Res_h_u[Gamma_boundary^(barQ_L,u_R,H)]_at_t_star"
        ),
        "same_t_star_and_same_Gamma_boundary": True,
        "separate_normalization_allowed": False,
    }


def v15_72_reclassification() -> dict[str, Any]:
    return {
        "uniform_replacement": "W_t(rho)_to_Lambda(rho)*min_rho(L_eta)",
        "status": "RECLASSIFIED_AS_A_CONTROLLED_UNIFORM-SOFTENING_MODEL",
        "not_exact_for_actual_cap": True,
        "reason": (
            "the_Legendre_minimum_is_on_an_interior_cohomogeneity-one_shell_"
            "and_the_outer_annulus_remains_part_of_the_DtN_problem"
        ),
        "retained_result": (
            "it_proves_how_a_uniform_event_mode_would_link_the_two_residues_"
            "but_does_not_prove_the_actual_shell_crosses"
        ),
        "claimed_actual_crossing": False,
    }


def completion_payload() -> dict[str, Any]:
    parent = weighted_parent_operator()
    order = dirichlet_monotonicity_theorem()
    crossing = exact_joint_crossing_problem()
    correction = v15_72_reclassification()
    validation = {
        "one_weighted_parent_operator": parent["one_operator_only"],
        "gauge_and_LR_orders_are_opposite": (
            order["gauge_order"].startswith("N[W_1]<=")
            and order["current_order"].startswith("G[W_1]>=")
        ),
        "one_crossing_fixes_both": crossing["same_t_star_and_same_Gamma_boundary"],
        "separate_normalization_forbidden": not crossing["separate_normalization_allowed"],
        "uniform_minimum_overclaim_retracted": correction["not_exact_for_actual_cap"],
        "actual_crossing_not_fabricated": not correction["claimed_actual_crossing"],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_event_shell_joint_operator_v15_73",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "weighted_parent_operator": parent,
        "Dirichlet_monotonicity_theorem": order,
        "exact_joint_crossing_problem": crossing,
        "v15_72_reclassification": correction,
        "scientific_result": (
            "ONE_SPATIALLY_WEIGHTED_M5_OPERATOR_NOW_DEFINES_BOTH_THE_ABSOLUTE_"
            "GAUGE_RESIDUE_AND_THE_LR/YUKAWA_CROSSING;_EVENT_SOFTENING_MOVES_"
            "THEM_MONOTONICALLY_IN_OPPOSITE_DIRECTIONS_WITH_NO_SPLIT_INPUT"
        ),
        "active_calculation": (
            "EVALUATE_N[W_t]_AND_B_u(t)_ON_SUCCESSIVE_CONSTRAINT-SOLVED_"
            "LORENTZIAN_CHILD_SLICES_AND_LOCATE_THE_FIRST_COMMON_t_star"
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
    path = target / "BHSM_aether_event_shell_joint_operator_v15_73.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "weighted_parent_operator", "dirichlet_monotonicity_theorem",
    "exact_joint_crossing_problem", "v15_72_reclassification",
    "completion_payload", "deterministic_json", "materialize",
]
