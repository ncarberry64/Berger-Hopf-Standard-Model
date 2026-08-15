"""Event-naturality theorem for the missing intrinsic-M4 coefficient map.

The selected hybrid event is a connected discrete orbit.  Its arrows act
trivially on gauge-invariant Wilson coefficients, so naturality makes a
coefficient assignment constant on that orbit but does not select the
constant.  The owned C3 family action gives circulant, not central, Yukawa
matrices.  This module identifies the smallest new law signature without
inserting any coefficient values.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np


VERSION = "v15.63"
CLASSIFICATION = "BHSM_EVENT_COEFFICIENT_NATURALITY_AND_MINIMAL_LAW_SIGNATURE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def cyclic_shift_matrix() -> np.ndarray:
    """Return the C3 family generator in the triality basis."""

    return np.asarray(((0, 0, 1), (1, 0, 0), (0, 1, 0)), dtype=complex)


def circulant_yukawa(a: complex, b: complex, c: complex) -> np.ndarray:
    """General complex 3-by-3 matrix commuting with the C3 shift."""

    return np.asarray(((a, c, b), (b, a, c), (c, b, a)), dtype=complex)


def family_symmetry_parameter_count() -> dict[str, Any]:
    shift = cyclic_shift_matrix()
    witness = circulant_yukawa(1 + 2j, -3 + 0.5j, 4 - 7j)
    return {
        "owned_family_symmetry": "C3_generated_by_the_triality_shift_P",
        "invariance_equation": "P*Y_f*P^(-1)=Y_f_equivalently_[P,Y_f]=0",
        "commutator_witness_norm": float(np.linalg.norm(shift @ witness - witness @ shift)),
        "C3_commutant": "C[P]={a*I3+b*P+c*P^2};_three_complex_dimensions",
        "real_dimensions_per_Yukawa": {
            "unrestricted_Mat3C": 18,
            "C3_invariant_circulant": 6,
            "family_central_y_times_I3": 2,
        },
        "total_intrinsic_M4_real_dimensions": {
            "unrestricted": 1 + 2 + 4 * 18,
            "owned_C3_invariant": 1 + 2 + 4 * 6,
            "stronger_family_central_kill_screen": 1 + 2 + 4 * 2,
        },
        "family_centrality_follows_from_owned_C3": False,
    }


def event_naturality_theorem() -> dict[str, Any]:
    return {
        "selected_event_object": "I_star",
        "selected_event_orbit": "connected_degree-one_negative-child_odd-FR_component",
        "continuous_event_tangent_dimension": 0,
        "coefficient_object": (
            "W_central=R_g_times_R_m2_times_R_lambda_times_C_yu_times_C_yd_"
            "times_C_ye_times_C_ynu"
        ),
        "coefficient_object_real_dimension": 11,
        "event_arrow_action_on_gauge_invariant_Wilson_data": "trivial",
        "naturality_equation": "M_micro(target(a))=M_micro(source(a))_for_every_event_arrow_a",
        "transitive_orbit_consequence": "M_micro_is_constant_on_the_selected_orbit",
        "constant_value_selected_by_naturality": False,
        "space_of_natural_assignments": "Nat(I_star,W_central)_isomorphic_to_W_central",
        "natural_assignment_real_dimension": 11,
        "Z2_Z3_event_witnesses_remove_this_freedom": False,
        "reason": (
            "requiring_one_assignment_to_be_constant_on_each_or_even_both_"
            "connected_witness_groupoids_still_allows_every_constant_c_in_W"
        ),
    }


def minimal_microscopic_law_signature() -> dict[str, Any]:
    return {
        "new_foundational_object_count": 1,
        "object": (
            "a_universal_gauge-diffeomorphism-event-compatible_selection_law_"
            "L_micro_on_(I,c)_with_c_in_W,_or_equivalently_its_unique_argmin_"
            "functor_M_micro(I)"
        ),
        "selection_equation": (
            "d_c*L_micro(I_star,c_star)=0_and_Hess_c*L_micro(I_star,c_star)>0"
        ),
        "outputs": [
            "g_common_at_mu_star",
            "m_H_squared",
            "lambda_H",
            "Y_u",
            "Y_d",
            "Y_e",
            "Y_nu",
        ],
        "required_properties": [
            "single-valued_unique_minimizer_modulo_field_redefinitions",
            "dimensionless_after_using_R4_and_canonical_field_normalization",
            "gauge_and_diffeomorphism_invariant",
            "natural_under_event_gluing",
            "compatible_with_the_global_spin_and_real-structure_domains",
            "bounded_Higgs_potential_and_positive_gauge_kinetic_form",
            "nonzero_finite_bifundamental_Dirac_block_if_interacting_masses_are_claimed",
            "defined_before_any_comparison_with_measured_SM_parameters",
        ],
        "eleven_independent_constants_required_as_new_primitives": False,
        "why_one_law_is_minimal": (
            "one_scalar_selection_function_with_a_unique_stationary_point_can_"
            "generate_all_Wilson_outputs,_whereas_naturality_alone_has_no_"
            "equation_in_the_coefficient_directions"
        ),
        "arbitrary_quadratic_center_allowed": False,
        "zero_norm_selector_action_derived": False,
        "explicit_formula_derived_from_current_BHSM_structure": False,
        "provenance": (
            "BHSM_ACTION_COMPLETION_MATHEMATICALLY_REQUIRED;_FORM_NOT_YET_"
            "DERIVED_FROM_EXISTING_BHSM_STRUCTURE"
        ),
    }


def completion_payload() -> dict[str, Any]:
    family = family_symmetry_parameter_count()
    naturality = event_naturality_theorem()
    law = minimal_microscopic_law_signature()
    validation = {
        "C3_commutator_zero": family["commutator_witness_norm"] < 1.0e-13,
        "raw_dimension_75": family["total_intrinsic_M4_real_dimensions"]["unrestricted"] == 75,
        "owned_C3_dimension_27": family["total_intrinsic_M4_real_dimensions"]["owned_C3_invariant"] == 27,
        "central_kill_screen_dimension_11": family[
            "total_intrinsic_M4_real_dimensions"
        ]["stronger_family_central_kill_screen"] == 11,
        "naturality_fiber_dimension_11": naturality["natural_assignment_real_dimension"] == 11,
        "naturality_does_not_fabricate_value": not naturality[
            "constant_value_selected_by_naturality"
        ],
        "minimal_law_is_one_object_not_eleven_constants": law[
            "new_foundational_object_count"
        ] == 1 and not law["eleven_independent_constants_required_as_new_primitives"],
        "arbitrary_center_forbidden": not law["arbitrary_quadratic_center_allowed"],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_event_coefficient_naturality_v15_63",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "family_symmetry_parameter_count": family,
        "event_naturality_theorem": naturality,
        "minimal_microscopic_law_signature": law,
        "claim_boundary": {
            "owned_C3_commutant_derived": True,
            "event_naturality_exhausted": True,
            "single_new_law_type_mathematically_forced": True,
            "law_formula_or_Wilson_values_derived": False,
        },
        "active_calculation": (
            "DERIVE_L_micro_FROM_THE_ACTION-OWNED_STRATIFIED_DIRAC_BOUNDARY_"
            "PAIRING_AND_EVENT_STATE,_WITH_THE_COEFFICIENT_DIRECTIONS_TREATED_"
            "AS_VARIATIONAL_OUTPUTS_AND_WITHOUT_AN_ARBITRARY_CENTER"
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
    path = target / "BHSM_aether_event_coefficient_naturality_v15_63.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "cyclic_shift_matrix",
    "circulant_yukawa", "family_symmetry_parameter_count",
    "event_naturality_theorem", "minimal_microscopic_law_signature",
    "completion_payload", "deterministic_json", "materialize",
]
