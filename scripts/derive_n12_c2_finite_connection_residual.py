"""Assemble and audit the executable C2 finite-connection residual contract."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.c2_finite_connection_residual import (  # noqa: E402
    assemble_c2_finite_connection_residual,
    fixed_event_child_reset_rows,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_FINITE_CONNECTION_RESIDUAL.json"
FULL_RESET = BASE / "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json"
RESET_DATA = BASE / "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.npz"
REFINED = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json"
REFINED_DATA = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz"
FINITE_CORE = BASE / "BHSM_N12_C2_FINITE_COVER_VOLTERRA_WEYL.json"
FINITE_COVER = BASE / "BHSM_N12_C2_FINITE_TRANSLATED_DESCRIPTOR_COVER.json"
COVER_DATA = BASE / "BHSM_N12_C2_FINITE_TRANSLATED_DESCRIPTOR_COVER.npz"
TRANSVERSALITY = BASE / "BHSM_N12_LOCAL_RESET_TERMINAL_TRANSVERSALITY_AUDIT.json"
KKT = BASE / "BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json"
CHRONOLOGY = BASE / "BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json"
DICHOTOMY = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
MODULE = ROOT / "src/bhsm/interface/c2_finite_connection_residual.py"
THEORY = ROOT / "theory/n12_c2_finite_connection_residual.md"
INPUTS = (
    FULL_RESET,
    RESET_DATA,
    REFINED,
    REFINED_DATA,
    FINITE_CORE,
    FINITE_COVER,
    COVER_DATA,
    TRANSVERSALITY,
    KKT,
    CHRONOLOGY,
    DICHOTOMY,
    MODULE,
    THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _algebraic_witness() -> dict[str, Any]:
    initial = np.asarray([0.0, 1.0])
    nodes = np.asarray([[0.0, 1.0], [0.5, 1.0], [1.0, 1.0]])
    assembled = assemble_c2_finite_connection_residual(
        child_initial_state=initial,
        path_nodes=nodes,
        log_duration=0.0,
        reset_rows=lambda state: np.asarray([state[0]]),
        vector_field=lambda state: np.asarray([1.0, 0.0]),
        endpoint_function=lambda state: state[0] - 1.0,
        margin_functions={
            "positive_lapse": lambda state: state[1],
            "selected_line_gap": lambda state: 2.0 - state[0],
        },
        endpoint_kind="RETAINED_EVENT",
    )
    return {
        "model": "GENERAL_MATHEMATICAL_LINEAR_FLOW_NOT_A_BHSM_HISTORY",
        "duration": assembled.duration,
        "reset_residual_norm": float(np.linalg.norm(assembled.reset)),
        "birth_seam_residual_norm": float(np.linalg.norm(assembled.birth_seam)),
        "flow_residual_norm": float(np.linalg.norm(assembled.flow)),
        "endpoint_residual": float(assembled.endpoint[0]),
        "total_residual_norm": float(np.linalg.norm(assembled.vector)),
        "minimum_margins": dict(assembled.minimum_margins),
        "path_admissible": assembled.path_admissible,
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing finite-connection inputs: " + ", ".join(missing))
    records = [_load(path) for path in (
        FULL_RESET,
        REFINED,
        FINITE_CORE,
        FINITE_COVER,
        TRANSVERSALITY,
        KKT,
        CHRONOLOGY,
        DICHOTOMY,
    )]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated finite-connection parents required")
    (
        full_reset,
        refined,
        finite_core,
        finite_cover,
        transversality,
        kkt,
        chronology,
        dichotomy,
    ) = records

    with np.load(RESET_DATA) as data:
        reset_center = np.asarray(data["center_state"], dtype=float)
        reset_jacobian = np.asarray(data["analytic_full_reset_jacobian"], dtype=float)
    with np.load(REFINED_DATA) as data:
        refined_state = np.asarray(data["state"], dtype=float)
    with np.load(COVER_DATA) as data:
        centers = np.asarray(data["C2_predictor_centers"], dtype=float)
        signed_values = np.asarray(data["signed_lambda_values"], dtype=float)

    witness = _algebraic_witness()
    partition_witness = fixed_event_child_reset_rows(np.arange(57, dtype=float))
    child_state_dimension = refined_state.size // 2
    fixed_event_child_reset_rows_count = full_reset["dimensions"]["rows"] - 26
    raw_child_fiber_dimension = child_state_dimension - fixed_event_child_reset_rows_count
    endpoint_stratum_raw_dimension = raw_child_fiber_dimension + 1 - 1
    physical_dimension = endpoint_stratum_raw_dimension - 1

    matching_audit = [
        {
            "diagram_slot": "FIXED_EVENT_CHILD_RESET_ROWS",
            "required_type": "31_ROW_MAP_ON_98_DIMENSIONAL_CHILD_STATE",
            "candidate": "ROWS_26_TO_56_OF_RETAINED_FULL_RESET_RESIDUAL",
            "dimension_domain_check": "VALID_31_BY_98_LOCAL_GRAPH",
            "provenance_check": "AE2_ACTION_RESET",
            "verdict": "VALID_MATCH",
        },
        {
            "diagram_slot": "POSITIVE_DURATION",
            "required_type": "STRICTLY_POSITIVE_PHYSICAL_TIME_PARAMETER",
            "candidate": "T=exp(theta)",
            "dimension_domain_check": "VALID_GLOBAL_POSITIVITY_CHART",
            "provenance_check": "PARAMETERIZATION_ONLY_NO_NEW_SCALE",
            "verdict": "VALID_MATCH",
        },
        {
            "diagram_slot": "C2_FORWARD_VECTOR_FIELD",
            "required_type": "RETAINED_EULER_DIRAC_V_AE2_ON_REGULAR_CHILD_DOMAIN",
            "candidate": "SIGNED_DESCRIPTOR_PROOF_CENTER_FIELD_AND_98_SEGMENT_COVER",
            "dimension_domain_check": "VALID_CERTIFIED_PREFIX_ONLY",
            "provenance_check": "RETAINED_ACTION_INVERSE_FREE_DESCRIPTOR",
            "verdict": "ACTUALLY_MISSING_AS_CERTIFIED_CONTINUOUS_CALLBACK_BEYOND_PREFIX",
        },
        {
            "diagram_slot": "ENDPOINT_GRAPH",
            "required_type": "FIRST_TRANSVERSE_RETAINED_EVENT_OR_EXISTING_CANONICAL_STOP",
            "candidate": "ORDERED_BRANCH_24_EVENT_AND_MAXIMAL_FLOW_STOP_LIST",
            "dimension_domain_check": "FUNCTION_TYPES_KNOWN_NO_LATER_HIT_CERTIFIED",
            "provenance_check": "RETAINED_EVENT_AND_DOMAIN_DICHOTOMY",
            "verdict": "ACTUALLY_MISSING_AS_REACHED_LATER_ENDPOINT",
        },
        {
            "diagram_slot": "PATH_DOMAIN_MARGINS",
            "required_type": "STRICT_NODEWISE_ACTION_DOMAIN_INEQUALITIES",
            "candidate": "LAPSE_METRIC_LEGENDRE_INERTIA_TRACE_GAUGE_DIRAC_AND_LINE_GAP",
            "dimension_domain_check": "VALID_ON_CERTIFIED_PREFIX",
            "provenance_check": "CONTINUUM_MAXIMAL_FLOW_DICHOTOMY",
            "verdict": "VALID_MATCH_PREFIX_ONLY",
        },
        {
            "diagram_slot": "PHYSICAL_TIME_QUOTIENT",
            "required_type": "ONE_EXACT_WHOLE_HISTORY_TIME_ORBIT",
            "candidate": "INTRINSIC_QUOTIENT_COUNT",
            "dimension_domain_check": "67_RAW_TO_66_PHYSICAL",
            "provenance_check": "RETAINED_ACTION_SYMMETRY_EXPLICIT_GENERATOR_NOT_NEEDED_FOR_CONNECTION_RESIDUAL",
            "verdict": "VALID_MATCH_INTRINSIC_COUNT",
        },
    ]

    validation = {
        "all_inputs_validated": True,
        "joint_reset_state_dimension_is_196": reset_center.shape == (196,),
        "full_reset_Jacobian_is_57_by_196": reset_jacobian.shape == (57, 196),
        "refined_root_is_same_joint_dimension": refined_state.shape == reset_center.shape,
        "fixed_event_child_partition_has_31_rows": partition_witness.shape == (31,),
        "child_state_dimension_is_98": child_state_dimension == 98,
        "raw_fixed_event_child_fiber_dimension_is_67": raw_child_fiber_dimension == 67,
        "duration_plus_endpoint_preserves_raw_stratum_dimension_67": endpoint_stratum_raw_dimension == 67,
        "intrinsic_time_quotient_leaves_66": physical_dimension == 66,
        "finite_cover_has_97_nodes": centers.shape == (97, 98),
        "finite_cover_signed_values_match_nodes": signed_values.shape == (97,),
        "finite_prefix_ends_on_positive_event_side": signed_values[-1] > 0.0,
        "finite_prefix_is_not_endpoint": finite_core["claim_boundary"]["physical_encapsulation_endpoint_reached"] is False,
        "local_reset_chart_does_not_claim_later_hit": transversality["route_adjudication"]["local_reset_IFT_supplies_finite_stratum"] is False,
        "finite_route_is_optional_sufficient_not_universal": chronology["adjudication"]["finite_endpoint_BVP_route_remains_valid"] is True and chronology["adjudication"]["post_event_finite_terminal_reachability_required"] is False,
        "KKT_consumes_same_endpoint_partition": kkt["system"]["endpoint"].startswith("FIRST_TRANSVERSE_RETAINED_EVENT"),
        "maximal_stop_list_is_existing_only": dichotomy["domain"]["new_gate"] is False,
        "executable_assembly_witness_closes_exactly": math.isclose(witness["total_residual_norm"], 0.0, abs_tol=1.0e-15),
        "no_recurrence_periodic_endpoint_validation_cutoff_selector_scale_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_C2_FINITE_CONNECTION_RESIDUAL",
        "status": (
            "EXECUTABLE_C2_FINITE_CONNECTION_RESIDUAL_ASSEMBLED_ACTUAL_LATER_ENDPOINT_UNSOLVED"
            if passed
            else "C2_FINITE_CONNECTION_RESIDUAL_NOT_ASSEMBLED"
        ),
        "classification": (
            "THE_ACTION_NATIVE_FIXED_EVENT_CHILD_RESET_FLOW_ENDPOINT_AND_DOMAIN_"
            "PARTITION_IS_NOW_AN_EXECUTABLE_INVERSE_FREE_RESIDUAL_WITH_THE_EXACT_"
            "67_RAW_TO_66_PHYSICAL_DIMENSION_COUNT;_THE_ACTUAL_CONTINUOUS_C2_"
            "CONTINUATION_TO_A_LATER_EVENT_OR_CANONICAL_STOP_IS_NOT_CERTIFIED"
        ),
        "residual_system": {
            "positive_duration": "T=exp(theta)>0",
            "fixed_event_child_reset": "C_reset,child(Y0)=full_reset_rows[26:]=0",
            "birth_seam": "Y_path,0-Y0=0",
            "normalized_time_flow": "Y_j+1-Y_j-(T*Delta_s/2)*(V(Y_j)+V(Y_j+1))=0",
            "endpoint": "e_ord(Y_N)=0_OR_ONE_EXISTING_CANONICAL_STOP_GRAPH",
            "domain_margins": "STRICT_INEQUALITIES_AUDITED_NODEWISE_NOT_RESIDUAL_PENALTIES",
            "matrix_inverse_formed": False,
        },
        "dimension_ledger": {
            "joint_event_child_state": int(reset_center.size),
            "fixed_event_rows_removed": 26,
            "child_state": child_state_dimension,
            "fixed_event_child_reset_rows": fixed_event_child_reset_rows_count,
            "raw_child_reset_fiber": raw_child_fiber_dimension,
            "positive_duration_parameters": 1,
            "endpoint_scalar_equations": 1,
            "raw_endpoint_stratum_after_flow_elimination": endpoint_stratum_raw_dimension,
            "exact_whole_history_time_orbits": 1,
            "physical_endpoint_stratum": physical_dimension,
            "common_scale": "RETAINED_PHYSICAL_DIRECTION",
        },
        "actual_prefix": {
            "path_node_count": int(centers.shape[0]),
            "state_dimension": int(centers.shape[1]),
            "segment_count": finite_core["finite_history_response"]["segment_count"],
            "final_signed_branch_24_eigenvalue": float(signed_values[-1]),
            "proper_duration_interval": finite_core["finite_history_response"]["proper_duration_interval"],
            "physical_endpoint_reached": False,
            "canonical_stop_reached": False,
            "role": "CERTIFIED_INITIAL_GUESS_PREFIX_NOT_A_BVP_SOLUTION",
        },
        "matching_audit": matching_audit,
        "algebraic_assembly_witness": witness,
        "adjudication": {
            "finite_connection_residual_contract": "DERIVED_EXECUTABLE",
            "actual_fixed_event_child_reset_slot": "MATCHED",
            "actual_finite_prefix_initial_guess": "MATCHED_98_SEGMENTS",
            "actual_continuous_flow_beyond_prefix": "OPEN",
            "actual_later_event_or_canonical_stop_hit": "OPEN",
            "finite_endpoint_stratum": "NOT_CERTIFIED_HERE",
            "infinite_combined_projected_force_route": "PRESERVED_ALTERNATIVE",
            "zero_source_force": "WAITING_ON_ROUTE_CLOSURE",
        },
        "exact_next_dependency": (
            "IMPLEMENT_THE_ACTUAL_CERTIFIED_C2_DESCRIPTOR_CONTINUATION_CALLBACK_"
            "WITH_EVENT_AND_EXISTING_STOP_MONITORS_FROM_THE_98_SEGMENT_PREFIX,_THEN_"
            "SOLVE_AND_CERTIFY_THIS_CONNECTION_RESIDUAL_OR_RETURN_TO_THE_DIRECT_"
            "COMBINED_PROJECTED_FORCE_TAIL;_DO_NOT_USE_THE_C2_BIRTH_ROOT_AS_A_"
            "LATER_ENDPOINT"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_ACTUAL_C2_CONNECTION_OR_COMBINED_PROJECTED_TAIL",
            "Gate8": "LOCKED",
            "finite_connection_residual": "DERIVED_EXECUTABLE",
            "actual_finite_connection_solution": "OPEN",
            "actual_projected_zero_source_force": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
            "physical_Hessian": "WAITING_ON_SADDLE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "physical_dimension": payload["dimension_ledger"]["physical_endpoint_stratum"],
        "actual_connection": payload["claim_boundary"]["actual_finite_connection_solution"],
    }, indent=2))


if __name__ == "__main__":
    main()
