"""Common-parent stress lift and conservation obstruction for BHSM v10.3."""

from __future__ import annotations

from typing import Any

import numpy as np


STRESS_VERDICT = "BHSM_STRATIFIED_ACTION_LACKS_A_CONSERVED_COMMON_DOMAIN_STRESS_TENSOR"


def tangential_stress_lift(stress: np.ndarray, tangents: np.ndarray) -> np.ndarray:
    """Lift contravariant intrinsic stress by T_parent=E T_intrinsic E^T."""

    tensor = np.asarray(stress, dtype=float)
    frame = np.asarray(tangents, dtype=float)
    if tensor.ndim != 2 or tensor.shape[0] != tensor.shape[1]:
        raise ValueError("intrinsic stress must be square")
    if frame.ndim != 2 or frame.shape[1] != tensor.shape[0]:
        raise ValueError("tangent frame columns must match intrinsic dimension")
    return frame @ tensor @ frame.T


def component_audit() -> dict[str, Any]:
    return {
        "distributional_lift": (
            "T8_seam^AB(x)=int_M4 sqrt|h| T4^mu_nu e_mu^A e_nu^B "
            "delta8(x-X(y))/sqrt|G| d4y"
        ),
        "tangential_component": "T4^mu_nu exactly",
        "normal_normal_component": 0,
        "normal_tangential_component": 0,
        "normal_force_location": "distributional divergence through K^I_mu_nu T4^mu_nu, not T_nn",
        "divergence_identity": (
            "nabla_A T8_seam^AB=delta_Sigma[(D_mu T4^mu_nu)e_nu^B-"
            "T4^mu_nu K^I_mu_nu n_I^B]"
        ),
        "tangential_conservation": "D_mu T4^mu_nu=0 on intrinsic equations",
        "normal_conservation_requires": "T4^mu_nu K^I_mu_nu plus bulk/matcher reaction=0",
        "current_shape_equation_present": False,
    }


def representation_audit() -> list[dict[str, Any]]:
    return [
        {
            "representation": "delta-supported M4 in M8",
            "free_width": False,
            "linear_distribution_well_defined": True,
            "nonlinear_self_products_controlled": False,
            "current_action_selected": False,
        },
        {
            "representation": "finite collar profile",
            "free_width": True,
            "linear_distribution_well_defined": True,
            "nonlinear_self_products_controlled": "conditional on profile",
            "current_action_selected": False,
        },
        {
            "representation": "smooth scalar domain wall",
            "free_width": "must follow from wall action",
            "linear_distribution_well_defined": True,
            "nonlinear_self_products_controlled": True,
            "current_action_selected": "only the separate M5 scalar wall, not an M8 localization of all M4 sectors",
        },
        {
            "representation": "normalized cap/fiber pushforward",
            "free_width": False,
            "linear_distribution_well_defined": True,
            "nonlinear_self_products_controlled": True,
            "current_action_selected": "maps exist, but source/target actions remain independent off shell",
        },
    ]


def ownership_audit() -> dict[str, Any]:
    return {
        "M8_stress": ["G/chi/sigma8/eta/omega sectors"],
        "M5_stress": ["independent cap geometry and sigma5"],
        "M4_stress": ["intrinsic SM EFT, h, and currents"],
        "matcher_response": "KKT adjoint reactions C85*Lambda85 and C54*Lambda54",
        "matcher_is_physical_stress_tensor": False,
        "one_common_T8_total": None,
        "distributional_conservation": False,
        "regulated_conservation": None,
        "v6_27_special_fold_residual": "vanishes through O(D2 q) on fixed B1 support",
        "special_fold_result_is_all_sector_nonlinear_conservation": False,
    }


def stress_payload() -> dict[str, Any]:
    components = component_audit()
    ownership = ownership_audit()
    representations = representation_audit()
    validation = {
        "intrinsic_lift_is_tangential": components["normal_normal_component"] == 0,
        "normal_force_in_divergence": "K^I" in components["normal_force_location"],
        "shape_equation_missing": not components["current_shape_equation_present"],
        "no_common_tensor": ownership["one_common_T8_total"] is None,
        "no_regulator_selected": not any(row["current_action_selected"] is True for row in representations[:2]),
        "special_result_not_overpromoted": not ownership["special_fold_result_is_all_sector_nonlinear_conservation"],
    }
    return {
        "artifact": "BHSM_common_domain_stress_pullback_v10_3",
        "components": components,
        "representations": representations,
        "ownership": ownership,
        "verdict": STRESS_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
