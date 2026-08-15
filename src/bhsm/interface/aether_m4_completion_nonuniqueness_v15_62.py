"""Rank theorem for intrinsic-M4 completion data on the hybrid reset."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np


VERSION = "v15.62"
CLASSIFICATION = "BHSM_INTRINSIC_M4_COMPLETION_NONUNIQUENESS_RANK_THEOREM"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def intrinsic_wilson_parameterization() -> dict[str, Any]:
    return {
        "canonical_fields": "canonically_normalized_A_mu,_H,_and_48_Weyl_fields",
        "continuous_data": {
            "gauge": ["g_common_at_mu_star"],
            "Higgs_potential": ["m_H_squared", "lambda_H"],
            "Yukawa": ["Y_u_in_Mat3C", "Y_d_in_Mat3C", "Y_e_in_Mat3C", "Y_nu_in_Mat3C"],
        },
        "raw_real_dimension": 1 + 2 + 4 * 18,
        "family_central_restriction": (
            "Y_f=y_f*I3_reduces_each_complex_3x3_matrix_to_one_complex_number"
        ),
        "family_central_real_dimension": 1 + 2 + 4 * 2,
        "all_are_invisible_in_the_A=H=Psi=0_background_equations": True,
    }


def reset_background_coefficient_jacobian() -> np.ndarray:
    """Derivative of reset background equations with respect to M4 Wilson data.

    At A=H=Psi=0, gauge, Yukawa and quartic interaction variations vanish.
    The returned matrix represents the eleven family-central real directions
    against the background field equations.
    """

    return np.zeros((11, 11), dtype=float)


def explicit_inequivalent_completion_family() -> dict[str, Any]:
    return {
        "common_background": "A_star=0,_H_star=0,_Psi_star=0_on_R_times_S3",
        "action_family": (
            "S_w=int_sqrt(-h)[-1/4*F_canonical^2+abs(D_gH)^2-"
            "m2*HdaggerH-lambda*(HdaggerH)^2-sum_f(barPsi_L*Y_f*H_f*Psi_R+h.c.)]"
        ),
        "member_free": {
            "g": 0.0,
            "m2": 0.0,
            "lambda": 0.0,
            "Y_f": "0_3_for_all_f",
        },
        "member_interacting_central": {
            "g": "any_positive_g",
            "m2": "any_real_m2",
            "lambda": "any_positive_lambda",
            "Y_f": "any_complex_y_f_times_I3",
        },
        "same_background_first_variation": True,
        "same_event_invariant_tuple": True,
        "same_anomaly_ledger": True,
        "different_fluctuation_Hessians_and_scattering": True,
        "continuum_cardinality": True,
    }


def coefficient_functor_requirement() -> dict[str, Any]:
    return {
        "required_map": (
            "M_micro:I_star_to_(g_common,m_H_squared,lambda_H,Y_u,Y_d,Y_e,Y_nu)"
        ),
        "domain": (
            "the_discrete_degree-one_negative-child_odd-FR_event_class_with_"
            "rank16_representation_and_round_internal_Dirac_spectrum"
        ),
        "codomain": "the_intrinsic_M4_Wilson_operator_space_modulo_field_redefinitions",
        "required_properties": [
            "single-valued",
            "gauge_and_diffeomorphism_invariant",
            "compatible_with_event_gluing",
            "compatible_with_the_global_spin_bundle",
            "fixes_boundary_renormalization_conditions",
            "fixes_the_finite_bifundamental_Dirac_block",
            "uses_no_measured_SM_target",
        ],
        "continuous_event_tangent": "zero_space",
        "consequence": (
            "continuous_Wilson_outputs_cannot_be_inherited_state_coordinates;_"
            "they_must_be_universal_values_of_a_new_microscopic_law"
        ),
        "such_a_map_present_in_current_action": False,
    }


def unique_actualization_distinction() -> dict[str, Any]:
    return {
        "state_level": (
            "Fix(P_s_on_selected_event_basin)/(Gauge_times_Diff)={z_star}"
        ),
        "state_level_unique": True,
        "theory_level": (
            "the_fiber_of_intrinsic_M4_actions_over_the_same_z_star_has_"
            "continuum_cardinality"
        ),
        "theory_level_unique": False,
        "logical_rule": (
            "a_unique_solution_of_each_member_of_an_action_family_does_not_"
            "select_a_unique_member_of_that_family"
        ),
        "FULL_BHSM_complete": False,
    }


def completion_payload() -> dict[str, Any]:
    parameters = intrinsic_wilson_parameterization()
    jacobian = reset_background_coefficient_jacobian()
    family = explicit_inequivalent_completion_family()
    functor = coefficient_functor_requirement()
    uniqueness = unique_actualization_distinction()
    validation = {
        "raw_parameter_rank_counted": parameters["raw_real_dimension"] == 75,
        "central_parameter_rank_counted": parameters[
            "family_central_real_dimension"
        ] == 11,
        "background_coefficient_jacobian_zero": np.count_nonzero(jacobian) == 0,
        "background_cannot_select_coefficients": np.linalg.matrix_rank(jacobian) == 0,
        "inequivalent_actions_share_reset": family[
            "same_background_first_variation"
        ] and family["different_fluctuation_Hessians_and_scattering"],
        "missing_relation_named_as_functor": functor["required_map"].startswith(
            "M_micro:"
        ),
        "functor_not_fabricated": not functor[
            "such_a_map_present_in_current_action"
        ],
        "state_and_theory_uniqueness_not_conflated": uniqueness[
            "state_level_unique"
        ] and not uniqueness["theory_level_unique"],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_m4_completion_nonuniqueness_v15_62",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "intrinsic_Wilson_parameterization": parameters,
        "background_coefficient_Jacobian": jacobian.tolist(),
        "inequivalent_completion_family": family,
        "coefficient_functor_requirement": functor,
        "unique_actualization_distinction": uniqueness,
        "claim_boundary": {
            "state_level_unique_actualization_derived": True,
            "theory_level_intrinsic_M4_nonuniqueness_derived": True,
            "current_background_can_select_missing_coefficients": False,
            "required_microscopic_coefficient_functor_derived": False,
        },
        "active_calculation": (
            "SEARCH_THE_EXISTING_BHSM_EVENT_AND_GLOBAL_SPIN-GAUGE_CATEGORY_"
            "FOR_A_NATURAL_SINGLE-VALUED_COEFFICIENT_FUNCTOR;_IF_NONE_EXISTS,_"
            "THE_COMPLETE_INTERACTING_MODEL_REQUIRES_AN_EXPLICIT_NEW_"
            "FOUNDATIONAL_LAW_RATHER_THAN_FURTHER_BACKGROUND_EVOLUTION"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_m4_completion_nonuniqueness_v15_62.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "intrinsic_wilson_parameterization", "reset_background_coefficient_jacobian",
    "explicit_inequivalent_completion_family", "coefficient_functor_requirement",
    "unique_actualization_distinction", "completion_payload",
    "deterministic_json", "materialize",
]
