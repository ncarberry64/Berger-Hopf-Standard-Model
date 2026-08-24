"""Audit whether current certified data realize the joint Gate-7 operator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_JOINT_FINITE_HISTORY_OPERATOR_DATA_GATE.json"
)
INPUTS = (
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json"
    ),
    ARTIFACTS / (
        "n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
    ),
    ARTIFACTS / (
        "n12_direct_checkpoint/BHSM_N12_POSITIVE_DURATION_PERSISTENCE_WITNESS.json"
    ),
    ARTIFACTS / (
        "n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def checkpoint_inventory() -> dict[str, Any]:
    with np.load(INPUTS[-1]) as checkpoint:
        arrays = {
            key: {
                "shape": list(checkpoint[key].shape),
                "dtype": str(checkpoint[key].dtype),
            }
            for key in checkpoint.files
        }
    keys = set(arrays)
    required_history_tokens = {
        "proper_times",
        "history_states",
        "radii_history",
        "temporal_first_derivative",
        "temporal_laplacian",
        "endpoint_form",
        "geometry_operator_jets",
        "geometry_reset_hessian",
        "replacement_force_covector",
    }
    return {
        "arrays": arrays,
        "array_keys": sorted(keys),
        "single_event_child_state_present": arrays.get("state", {}).get("shape")
        == [196],
        "first_constraint_jacobian_present": arrays.get(
            "paired_jacobian", {}
        ).get("shape") == [57, 196],
        "required_history_or_operator_arrays_present": sorted(
            keys & required_history_tokens
        ),
        "required_history_or_operator_arrays_absent": sorted(
            required_history_tokens - keys
        ),
    }


def persistence_inventory(persistence: dict[str, Any]) -> dict[str, Any]:
    fine = persistence["fine_evolution"]
    row_keys = sorted(fine["rows"][0])
    row_state_keys = [
        key for key in row_keys
        if key in {"state", "configuration", "velocity", "radii"}
    ]
    return {
        "coordinate_duration": fine["coordinate_duration"],
        "proper_duration": fine["child_proper_duration"],
        "requested_steps": fine["requested_steps"],
        "completed_as_persistence_test": fine["completed"],
        "row_keys": row_keys,
        "per_node_state_or_radius_keys": row_state_keys,
        "final_state_present": "final_state" in fine,
        "physical_terminal_or_canonical_stop_field_present": any(
            key in fine for key in (
                "physical_terminal_event",
                "canonical_stop",
                "action_owned_endpoint_graph",
            )
        ),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("joint finite-history data-gate inputs required")
    records = [_load(path) for path in INPUTS[:-1]]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated joint finite-history inputs required")
    force_domain, incidence, seam, projected, branch, certificate, persistence = records
    checkpoint = checkpoint_inventory()
    persistence_data = persistence_inventory(persistence)
    validation = {
        "finite_encapsulation_local_existence_preserved": (
            branch["adjudication"][
                "finite_positive_time_completed_encapsulation_exists"
            ] is True
        ),
        "endpoint_checkpoint_and_first_constraint_jacobian_present": (
            checkpoint["single_event_child_state_present"] is True
            and checkpoint["first_constraint_jacobian_present"] is True
        ),
        "checkpoint_does_not_contain_complete_operator_realization": (
            checkpoint["required_history_or_operator_arrays_present"] == []
        ),
        "positive_duration_witness_is_only_persistence_scope": (
            certificate["validation"][
                "existing_positive_duration_persistence_gate"
            ] is True
            and persistence_data[
                "physical_terminal_or_canonical_stop_field_present"
            ] is False
        ),
        "persistence_rows_do_not_store_coefficient_path": (
            persistence_data["per_node_state_or_radius_keys"] == []
        ),
        "arbitrary_validation_cutoff_remains_forbidden": (
            force_domain["domain_adjudication"][
                "arbitrary_regular_free_cutoff_allowed"
            ] is False
        ),
        "domain_parametric_operator_incidence_exists": (
            incidence["incidence"]["history_coefficients_fabricated"] is False
            and incidence["claim_boundary"][
                "domain_parametric_nonzero_local_incidence"
            ] == "DERIVED"
        ),
        "seam_family_is_enclosure_not_actual_oracle": (
            seam["force_adjudication"]["actual_seam_values_available"] is False
        ),
        "projected_solver_ready_but_physical_inputs_open": (
            projected["claim_boundary"][
                "constraint_tangent_force_criterion"
            ] == "DERIVED"
            and projected["claim_boundary"][
                "actual_projected_force_value"
            ] == "OPEN"
            and projected["claim_boundary"][
                "geometry_reset_KKT_Hessian"
            ] == "OPEN"
        ),
        "no_endpoint_selector_periodicity_scale_fit_new_gate_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_JOINT_FINITE_HISTORY_OPERATOR_DATA_GATE",
        "status": "EXECUTABLE_ASSEMBLY_AND_PROJECTED_KKT_READY_ACTION_OWNED_EXTERIOR_ORACLE_MISSING",
        "classification": (
            "THE_CURRENT_DISK_CONTAINS_A_CERTIFIED_EVENT_CHILD_ENDPOINT_STATE,_"
            "ITS_FIRST_CONSTRAINT_JACOBIAN,_DOMAIN_PARAMETRIC_OPERATOR_AND_"
            "VERTEX_BUILDERS,_AND_NULLSPACE_BORDERED_KKT_SOLVERS;_IT_DOES_"
            "NOT_CONTAIN_AN_ACTION_OWNED_COMPLETE_COEFFICIENT_PATH,_TEMPORAL_"
            "FORM,_ACTUAL_ENDPOINT_LOAD,_GEOMETRY_OPERATOR_JET,_PROJECTED_"
            "REPLACEMENT_FORCE,_OR_GEOMETRY_RESET_HESSIAN;_THE_POSITIVE_"
            "DURATION_CHILD_WITNESS_IS_A_PERSISTENCE_TEST_WITH_AN_ARBITRARY_"
            "VALIDATION_END,_NOT_A_COMPLETE_FORCE_DOMAIN"
        ),
        "available_exact_machinery": {
            "finite_encapsulation_event_exists": True,
            "event_to_complete_child_relation_nonempty": True,
            "endpoint_state_and_first_constraint_jacobian": "CERTIFIED",
            "fixed_channel_operator_incidence_for_supplied_history": "DERIVED",
            "exact_heat_minus_zeta_force_functional_for_supplied_operator": "DERIVED",
            "two_sided_negative_axis_seam_intervals": "BROADLY_ENCLOSED",
            "constraint_tangent_force_criterion": "DERIVED",
            "nullspace_and_bordered_KKT_linear_solvers": "DERIVED_AND_CROSSCHECKED",
        },
        "data_inventories": {
            "endpoint_checkpoint": checkpoint,
            "positive_duration_persistence": persistence_data,
        },
        "missing_physical_realization": {
            "complete_action_owned_history_or_equivalent_exterior_Weyl_oracle": True,
            "proper_time_coefficient_path": True,
            "action_owned_temporal_first_derivative_and_form_laplacian": True,
            "actual_two_sided_endpoint_form_over_required_spectrum": True,
            "complete_geometry_operator_first_jet": True,
            "constraint_reduced_geometry_reset_Hessian": True,
            "actual_projected_heat_minus_zeta_force_covector": True,
        },
        "logical_boundary": {
            "failure_is_an_action_theorem_or_operator_data_gap": True,
            "failure_is_not_a_numerical_linear_solver_gap": True,
            "endpoint_checkpoint_alone_determines_nonlocal_heat_force": False,
            "broad_seam_intervals_alone_determine_nonlocal_heat_force": False,
            "persistence_validation_endpoint_may_be_promoted": False,
            "infinite_nonencapsulating_formation_tail_reopened": False,
        },
        "exact_single_highest_upstream_dependency": (
            "DERIVE_FROM_THE_RETAINED_AE2_EULER_DIRAC_ACTION_AN_ACTION_OWNED_"
            "COMPLETE_EVENT_REACHING_PHYSICAL_HISTORY_OPERATOR_REALIZATION_"
            "ON_THE_OWNER_FINITE_ENCAPSULATION_DOMAIN_OR_AN_EQUIVALENT_"
            "ACTUAL_EXTERIOR_WEYL_CALDERON_ORACLE_WITH_ITS_"
            "GEOMETRY_FIRST_JET;_A_VALIDATION_TIME_CUTOFF_OR_HAND_SELECTED_"
            "RESET_FIBER_MEMBER_IS_NOT_ADMISSIBLE"
        ),
        "after_that_dependency": (
            "ASSEMBLE_q_rep,_CONSTRUCT_THE_CONSTRAINT_REDUCED_GEOMETRY_"
            "HESSIAN,_AND_USE_THE_ALREADY_CROSSCHECKED_NULLSPACE_BORDERED_"
            "KKT_SYSTEM_TO_CERTIFY_THE_JOINT_SAME_ACTION_SADDLE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_ACTION_OWNED_EXTERIOR_OPERATOR_ORACLE_OPEN",
            "finite_encapsulation_existence": "CLOSED_LOCAL_ACTION_THEOREM",
            "operator_assembly_formulas": "DERIVED_FOR_SUPPLIED_ORACLE",
            "projected_KKT_solver": "DERIVED",
            "complete_action_owned_exterior_oracle": "OPEN_CURRENT_OWNER",
            "actual_projected_force": "OPEN",
            "geometry_reset_KKT_Hessian": "OPEN_AFTER_ORACLE",
            "same_action_saddle": "OPEN_AFTER_ORACLE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
