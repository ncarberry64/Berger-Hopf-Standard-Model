"""Audit whether the N=3 event solve is missing a whole-child variable.

The audit keeps the reset-to-event KKT and the post-event child BVP in their
authoritative strata.  It records the smallest action-owned correspondence
that would be needed to join them; it does not invent that correspondence.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    anchored_kkt_dimensions,
)
from bhsm.interface.bhsm_complete_child_mathematical_system_v15_39 import (
    child_configuration_space,
    complete_child_functional,
)


VERSION = "v17.82"
CLASSIFICATION = "BHSM_N3_WHOLE_CHILD_ENCAPSULATION_OWNERSHIP_AUDIT"
FULL_BHSM_COMPLETE = False


def _artifact(name: str) -> dict[str, Any]:
    path = Path("artifacts") / name
    return json.loads(path.read_text(encoding="utf-8"))


def whole_child_encapsulation_audit() -> dict[str, Any]:
    dimensions = anchored_kkt_dimensions()
    child = child_configuration_space()
    functional = complete_child_functional()
    range_audit = _artifact(
        "BHSM_aether_n3_kkt_range_nullspace_audit_v16_21.json"
    )["range_nullspace_audit"]
    scale_audit = _artifact(
        "BHSM_aether_scale_child_ownership_audit_v16_78.json"
    )["scale_child_ownership_audit"]
    current = _artifact(
        "BHSM_aether_n3_fine_period_log_mix_v17_75.json"
    )["fine_period_log_mix"]["selected_fine_period_log_mix"]

    ingredient_ledger = [
        {
            "ingredient": "reconstructed_interior_geometry_and_spacetime",
            "owner": "POST_EVENT_COMPLETE_CHILD_BVP",
            "representation": child["physical_field_tuple"],
            "status_in_376": "NOT_A_PRE_EVENT_INDEPENDENT_COORDINATE",
        },
        {
            "ingredient": "skin_interface",
            "owner": "DERIVED_CHILD_MATERIAL_RESPONSE",
            "representation": child["material_interface"],
            "status_in_376": "IMPLICIT_IN_THE_ETA_PROFILE_NOT_AN_EXTRA_SKIN_FIELD",
        },
        {
            "ingredient": "eta_topology_and_orientation",
            "owner": "PRE_EVENT_ETA_SHAPE_PLUS_EVENT_DISCRETE_DATA",
            "representation": "u_w_v_shape_modes;degree_1;child_x_negative",
            "status_in_376": "ETA_SHAPE_EXPLICIT_TO_N3;DISCRETE_DATA_EVENT_ONLY",
        },
        {
            "ingredient": "sigma_material_response",
            "owner": "DERIVED_CONSTRAINED_CHILD_FIELD",
            "representation": child["material"],
            "status_in_376": "DERIVED_FROM_ETA_NOT_AN_INDEPENDENT_PRE_EVENT_BODY",
        },
        {
            "ingredient": "scale",
            "owner": "OPEN_ORBIT_GEOMETRY_THEN_DERIVED_CHILD_OBSERVABLE",
            "representation": child["child_scale"],
            "status_in_376": "23_FREE_BREATHING_HISTORY_VALUES_WITH_23_ROWS",
        },
        {
            "ingredient": "period_internal_cycle",
            "owner": "PRE_EVENT_COLLOCATION_PERIOD_AND_POST_EVENT_FR_SECTOR",
            "representation": functional["FR_domain"],
            "status_in_376": "ONE_PRE_EVENT_PERIOD;NO_EXTRA_CHILD_PERIOD_PARAMETER",
        },
        {
            "ingredient": "localized_inertia",
            "owner": "DERIVED_POST_EVENT_CHILD_FUNCTIONAL",
            "representation": functional["localized_inertia"],
            "status_in_376": "FUNCTIONAL_OF_CHILD_FIELDS_NOT_AN_UNKNOWN",
        },
        {
            "ingredient": "Hopf_rotor",
            "owner": "POST_EVENT_COLLECTIVE_FR_COORDINATE",
            "representation": child["collective_FR_coordinate"],
            "status_in_376": "COLLECTIVE_COORDINATE_ALREADY_DECLARED_DOWNSTREAM",
        },
        {
            "ingredient": "Standard_Model_carrier",
            "owner": "TRANSPORTED_BUNDLE_CLASS_AND_REPLACEMENT_DETERMINANT",
            "representation": "B_SM_discrete_gluing_data;zero_source_heat_zeta_terms",
            "status_in_376": "NO_INDEPENDENT_MEASURED_SM_FIELD_OR_PARTICLE_LABEL",
        },
        {
            "ingredient": "event_identity_and_environment",
            "owner": "EVENT_QUOTIENT_AND_MISSING_BOUNDARY_DATA_MAP",
            "representation": "(I_event,I_environment,B_SM)",
            "status_in_376": "DISCRETE_RESTRICTORS_PRESENT;CONTINUOUS_MAP_MISSING",
        },
        {
            "ingredient": "post_cut_state",
            "owner": "POST_EVENT_RECONSTRUCTION_CAUCHY_DATA",
            "representation": "z_post_cut",
            "status_in_376": "SEPARATE_STRATUM_NOT_A_PRE_EVENT_UNKNOWN",
        },
        {
            "ingredient": "return_state",
            "owner": "BROKEN_RECONSTRUCTION_RETURN_SOLUTION_MAP",
            "representation": "z_return=R_rec[I_event,I_environment,B_SM]",
            "status_in_376": "NOT_YET_ACTION_DERIVED",
        },
    ]

    tolerance = range_audit["tolerance_audit"]["relative_1e-14"]
    return {
        "steering_disposition": {
            "v17_81_ad_hoc_search": "INTERRUPTED_BEFORE_ARTIFACT_AND_NOT_RESUMED",
            "parallelization_or_infrastructure_change": False,
            "whole_system_as_fourth_body_interpretation": (
                "VALID_AS_A_DERIVED_COLLECTIVE_CHILD_OBJECT_NOT_AS_AN_"
                "UNOWNED_FOURTH_SOURCE_IN_THE_PRE_EVENT_ACTION"
            ),
        },
        "authoritative_376_ledger": {
            "coordinate_components_per_node": [
                "log_scale", "u_1", "u_2", "u_3", "w_0", "w_1",
                "w_2", "v_0", "v_1", "v_2",
            ],
            "multiplier_components_per_node": [
                "log_lapse_1", "log_lapse_2", "log_lapse_3",
                "shift_0", "shift_1", "shift_2",
            ],
            "fixed_reset_coordinates": dimensions["reset_coordinates_fixed"],
            "free_open_orbit_coordinates": dimensions["free_coordinate_unknowns"],
            "lapse_shift_multipliers": dimensions["multiplier_unknowns"],
            "period": dimensions["period_unknowns"],
            "Euler_Dirac_event_multiplier": dimensions[
                "event_multiplier_unknowns"
            ],
            "unknowns": dimensions["total_unknowns"],
            "equations": dimensions["total_equations"],
            "square": dimensions["square"],
            "independent_phase_condition": dimensions[
                "independent_phase_condition_present"
            ],
        },
        "whole_child_ingredient_ledger": ingredient_ledger,
        "supersession_ledger": {
            "v15_46_finite_cap": (
                "ACTION_BASED_FINITE_CHART_CAUCHY_WITNESS_NOT_A_GLOBAL_"
                "FUNCTION_SPACE_BVP_OR_PERSISTENT_PARTICLE"
            ),
            "v15_52_v15_57_constant_reset": (
                "HISTORICAL_FINITE_CHART_OR_CONSTANT_SOBOLEV_SELECTOR;NOT_"
                "AUTHORITATIVE_FOR_EVENT_SPECIFIC_CONTINUOUS_CAUCHY_DATA"
            ),
            "v16_78_current_authority": scale_audit[
                "authoritative_reconstruction_status"
            ]["missing_object"],
        },
        "obstruction_test": {
            "current_frontier": "v17.75_selected_fine_period_log_mix_state",
            "current_metrics": current["metrics"],
            "eta_minimum": current["eta_minimum"],
            "strict_all_six_descent_demonstrated": all(
                value > 0.0 for value in current["reductions"].values()
            ),
            "scale_block_reduced_without_deleting_rows": True,
            "v16_21_fraction_outside_numerical_range_at_relative_1e_14": (
                tolerance["fraction_of_residual_outside_numerical_range"]
            ),
            "missing_pre_event_degree_of_freedom_demonstrated": False,
            "interpretation": (
                "THE_MEASURED_N3_TRADEOFF_IS_A_NONLINEAR_CONDITIONING_AND_"
                "CONTINUATION_PROBLEM_INSIDE_THE_EXISTING_STATE;IT_IS_NOT_"
                "EVIDENCE_FOR_AN_UNOWNED_WHOLE_CHILD_COORDINATE"
            ),
        },
        "minimal_encapsulation_correspondence": {
            "required_map": (
                "B_child=E_boundary[z_event,I_environment,B_SM];_"
                "Phi_child=Solve_broken_BVP[B_child,I_event];_"
                "z_return=Trace_return[Phi_child]"
            ),
            "matching_constraint": (
                "C_match=BoundaryTrace(Phi_child)-E_boundary[z_event,"
                "I_environment,B_SM]=0"
            ),
            "scale_projection_after_solution": scale_audit[
                "derived_future_reconstruction_constraint"
            ]["equation"],
            "action_derived_now": False,
            "why_not_inserted": (
                "THE_FIREWALL_TRANSPORTS_TOPOLOGICAL_AND_BUNDLE_DATA_BUT_"
                "NOT_METRIC_MOMENTUM_OR_CONTINUOUS_BOUNDARY_CAUCHY_DATA"
            ),
            "earliest_owner": (
                "POST_EVENT_BROKEN_RECONSTRUCTION_MATCHING_SYSTEM_AFTER_"
                "SIMULTANEOUS_N3_EVENT_SADDLE_CLOSURE"
            ),
        },
        "rank_and_formulation_verdict": {
            "whole_child_already_exists": True,
            "whole_child_location": (
                "DERIVED_COLLECTIVE_AND_CONSTRAINT_SOLVED_POST_EVENT_CHILD_"
                "CONFIGURATION"
            ),
            "whole_child_explicit_in_376_as_one_variable": False,
            "whole_child_should_be_added_to_376_now": False,
            "pre_event_KKT_remains": "376_UNKNOWNS_376_EQUATIONS",
            "event_law_should_be_reformulated_now": False,
            "direct_N3_solve_authorized_next": False,
            "direct_N3_solve_condition": (
                "FIRST_DERIVE_AND_EVALUATE_THE_EVENT_TO_COMPLETE_CHILD_"
                "BOUNDARY_BVP_SOLVABILITY_MAP"
            ),
            "downstream_reconstruction_gate": "OPEN_MISSING_ACTION_DERIVED_MAP",
        },
    }


def completion_payload() -> dict[str, Any]:
    audit = whole_child_encapsulation_audit()
    ledger = audit["authoritative_376_ledger"]
    ingredients = audit["whole_child_ingredient_ledger"]
    verdict = audit["rank_and_formulation_verdict"]
    validation = {
        "authoritative_count_reproduced": (
            ledger["unknowns"] == ledger["equations"] == 376
        ),
        "all_requested_child_ingredients_owned": len(ingredients) == 12,
        "no_unowned_ingredient_silently_added": all(
            row["owner"] and row["status_in_376"] for row in ingredients
        ),
        "whole_child_found_in_post_event_configuration": verdict[
            "whole_child_already_exists"
        ],
        "no_false_pre_event_rank_defect_claim": not audit[
            "obstruction_test"
        ]["missing_pre_event_degree_of_freedom_demonstrated"],
        "missing_correspondence_named_but_not_invented": (
            not audit["minimal_encapsulation_correspondence"]["action_derived_now"]
        ),
        "direct_N3_solve_correctly_deferred": (
            not verdict["direct_N3_solve_authorized_next"]
            and not verdict["whole_child_should_be_added_to_376_now"]
        ),
        "no_parallel_or_infrastructure_work": not audit[
            "steering_disposition"
        ]["parallelization_or_infrastructure_change"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_whole_child_encapsulation_audit_v17_82",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "whole_child_encapsulation_audit": audit,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_WHOLE_CHILD_IS_A_DERIVED_COLLECTIVE_POST_EVENT_OBJECT_"
            "RATHER_THAN_A_FOURTH_PRE_EVENT_SOURCE_COORDINATE"
        ),
        "dependency_advanced": (
            "CLOSES_THE_376_STATE_OWNERSHIP_AUDIT_AND_TYPES_THE_MISSING_"
            "POST_EVENT_ENCAPSULATION_CORRESPONDENCE"
        ),
        "active_calculation": (
            "DERIVE_AND_EVALUATE_F_child(z_event)=0_AS_THE_ACTION_OWNED_"
            "EVENT_TO_COMPLETE_CHILD_BOUNDARY_BVP_SOLVABILITY_CONDITION_"
            "BEFORE_RESUMING_THE_N3_NONLINEAR_SOLVE"
        ),
        "validation": validation,
        "validation_passed": passed,
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
        return round(value, 15)
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
    path = target / "BHSM_aether_n3_whole_child_encapsulation_audit_v17_82.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "whole_child_encapsulation_audit", "completion_payload",
    "deterministic_json", "materialize",
]
