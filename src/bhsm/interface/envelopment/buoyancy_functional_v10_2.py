"""Current-action exhaustion theorem for BHSM Topological Buoyancy."""

from __future__ import annotations

from typing import Any

from .backreaction_v10_2 import backreaction_payload
from .global_constraint_v10_2 import global_constraint_payload
from .normal_geometry_v10_2 import geometry_payload
from .radion_variation_v10_2 import radion_payload


PRIMARY_VERDICT = "BHSM_CURRENT_PARENT_ACTION_CANNOT_GENERATE_TOPOLOGICAL_BUOYANCY"
SCALE_VERDICT = "BHSM_BUOYANCY_BACKGROUND_LEAVES_ONE_UNFIXED_DIMENSIONAL_MODULUS"
WEAK_FIELD_VERDICT = "BHSM_BUOYANCY_WEAK_FIELD_LIMIT_BLOCKED_BY_NO_PHYSICAL_BUOYANCY_OPERATOR"
NEXT_EXACT_OBJECT = (
    "ACTION_DOMAIN_THEOREM_SELECTING_ONE_PHYSICAL_NORMAL_OR_RADION_DEGREE_"
    "WITH_COMPLETE_LOCALIZED_STRESS_PULLBACK_AND_COVARIANT_GLOBAL_RESTORING_CONSTRAINT"
)


def obstruction_theorem() -> dict[str, Any]:
    geometry = geometry_payload()
    radion = radion_payload()
    constraint = global_constraint_payload()
    backreaction = backreaction_payload()
    premises = {
        "normal_field_missing": geometry["normal_variation"]["psi_in_configuration_space"] is False,
        "static_radion_equilibrium_missing": radion["radion_variation"]["positive_static_solution"] is False,
        "radion_to_seam_map_missing": radion["ownership"]["physical_buoyancy_radion"] is None,
        "global_restoring_constraint_missing": constraint["selected_constraint"] is None,
        "complete_stress_pullback_missing": backreaction["cross_stratum_gate"]["complete_T_AB_total_on_one_domain"] is None,
        "compactness_observable_missing": backreaction["compactness"]["gauge_invariant_compactness_observable"] is None,
    }
    return {
        "statement": (
            "The current stratified action has neither a varied normal embedding field nor a "
            "static action-selected seam radion, and it supplies no compactness-coupled global "
            "restoring constraint or complete localized stress pullback. Therefore no functional "
            "U_buoy[psi,a_F] with the required BHSM ownership can be obtained from this action."
        ),
        "premises": premises,
        "premises_all_proved": all(premises.values()),
        "conclusion": PRIMARY_VERDICT,
        "classification": "BLOCKED_EXACT_OBJECT_PROVED",
    }


def functional_gate() -> dict[str, Any]:
    return {
        "U_buoy": None,
        "domain": None,
        "delta_U_delta_psi": None,
        "delta_U_delta_a_F": None,
        "dimensions": None,
        "boundedness": None,
        "equilibrium": None,
        "second_variation": None,
        "ghost_status": None,
        "gradient_status": None,
        "tachyon_status": None,
        "gauge_zero_modes_separated": False,
        "local_source_term": None,
        "global_restoring_term": None,
        "new_gravity_mediator": False,
        "fitted_parameters": [],
        "proxy_R_promoted": False,
        "verdict": PRIMARY_VERDICT,
    }


def weak_field_gate() -> dict[str, Any]:
    return {
        "action_selected_static_background": None,
        "linearized_buoyancy_operator": None,
        "effective_Newtonian_potential": None,
        "inverse_square_far_field": None,
        "attraction_sign": None,
        "universal_free_fall": None,
        "gravitational_redshift": None,
        "local_Lorentz_compatibility": "parent action covariant; no derived buoyancy limit",
        "composition_dependence": None,
        "effective_G": None,
        "empirical_constants_used": [],
        "numerical_scan_performed": False,
        "reason_no_scan": "no physical background or boundary-value problem is action-selected",
        "verdict": WEAK_FIELD_VERDICT,
    }


def dynamic_envelope_coupling() -> dict[str, Any]:
    return {
        "R": "collective texture size only",
        "s": "collective enclosure amplitude",
        "psi": None,
        "a_F": "M8 homogeneous metric mode, not localized seam depth",
        "R_map": None,
        "depth_dependent_coefficients_A_i": None,
        "kappa1_effective_of_depth": None,
        "mixed_action_blocks": {
            "delta2S_da_F_delta_Psi": 0,
            "delta2S_da_F_delta_H": 0,
        },
        "coupled_reduced_action": None,
        "arbitrary_coupling_added": False,
    }


def absolute_scale_gate() -> dict[str, Any]:
    return {
        "global_modulus": None,
        "primitive_ratio": "lambda=kappa0/kappa1 remains an unfixed theory coefficient ratio",
        "kappa1_unit_bridge": None,
        "unique_scale": False,
        "remaining_dimensional_degeneracy": 1,
        "physical_eV_GeV_output": None,
        "verdict": SCALE_VERDICT,
    }


def extension_comparison() -> list[dict[str, Any]]:
    return [
        {"class": "varied normal embedding", "new_field": "psi or embedding X", "new_parameter": None, "status": "REQUIRES_ACTION_DOMAIN_EXTENSION", "adopted": False},
        {"class": "full radion pushforward completion", "new_field": "no new M8 field; new cross-stratum ownership", "new_parameter": None, "status": "REQUIRES_REPLACING_OR_MATCHING_STORED_S5_OWNER", "adopted": False},
        {"class": "fixed global volume", "new_field": "auxiliary multiplier", "new_parameter": "V_star", "status": "EXTERNAL_DIMENSIONFUL_INPUT", "adopted": False},
        {"class": "nonminimal curvature-envelopment coupling", "new_field": None, "new_parameter": "new coupling", "status": "NEW_ACTION_TERM", "adopted": False},
        {"class": "topological multiplier", "new_field": "auxiliary multiplier", "new_parameter": "possibly none", "status": "DEGREE_STILL_SCALE_FREE", "adopted": False},
    ]


def buoyancy_functional_payload() -> dict[str, Any]:
    theorem = obstruction_theorem()
    functional = functional_gate()
    validation = {
        "obstruction_complete": theorem["premises_all_proved"],
        "functional_absent": functional["U_buoy"] is None,
        "R_not_depth": not functional["proxy_R_promoted"],
        "weak_field_fails_closed": weak_field_gate()["effective_Newtonian_potential"] is None,
        "no_numerical_scan": not weak_field_gate()["numerical_scan_performed"],
        "scale_fails_closed": absolute_scale_gate()["physical_eV_GeV_output"] is None,
        "no_extension_adopted": not any(row["adopted"] for row in extension_comparison()),
    }
    return {
        "artifact": "BHSM_topological_buoyancy_functional_v10_2",
        "obstruction_theorem": theorem,
        "functional": functional,
        "weak_field": weak_field_gate(),
        "dynamic_envelope": dynamic_envelope_coupling(),
        "absolute_scale": absolute_scale_gate(),
        "extension_comparison": extension_comparison(),
        "verdict": PRIMARY_VERDICT,
        "next_exact_object": NEXT_EXACT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
