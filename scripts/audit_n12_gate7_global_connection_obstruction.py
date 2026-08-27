"""Localize the finite Gate-7 reset-to-capture globalization obstruction.

This audit consumes the closed local continuation machinery.  It does not
extend the trajectory.  Its purpose is to decide whether the existing
certificates already define a finite monotonicity, cone, degree, or finite
cover proof from the reset-generated family to the stable capture tube (or
to a retained canonical stop).
"""

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

from bhsm.interface.aether_asymptotic_terminal_chart import (  # noqa: E402
    compactified_terminal_chart,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_GLOBAL_CONNECTION_OBSTRUCTION.json"
COVER = BASE / "BHSM_N12_C2_EXPANDED_CANCELLED_THETA_COVER_FROM_1221.json"
COVER_DATA = COVER.with_suffix(".npz")
RECENTER = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_RECENTER.json"
SHEARED = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_SHEARED_STEP.json"
SHEARED_DATA = SHEARED.with_suffix(".npz")
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
PARAMETRIC = BASE / "BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
TERMINAL = BASE / "BHSM_N12_ASYMPTOTIC_TERMINAL_CHART_PROJECTION.json"
CAPTURE = BASE / "BHSM_N12_GATE7_QUANTITATIVE_STABLE_CAPTURE_TUBE.json"
CONNECTION = BASE / "BHSM_N12_C2_FINITE_CONNECTION_RESIDUAL.json"
DICHOTOMY = (
    ROOT
    / "artifacts"
    / "intrinsic_state_selection"
    / "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
)
TERMINAL_MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_asymptotic_terminal_chart.py"
THEORY = ROOT / "theory" / "n12_gate7_global_connection_obstruction.md"
INPUTS = (
    COVER,
    COVER_DATA,
    RECENTER,
    SHEARED,
    SHEARED_DATA,
    LAUNCH,
    PARAMETRIC,
    TERMINAL,
    CAPTURE,
    CONNECTION,
    DICHOTOMY,
    TERMINAL_MODULE,
    THEORY,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _terminal_trends() -> dict[str, Any]:
    with np.load(COVER_DATA) as data:
        centers = np.asarray(data["predictor_centers"], dtype=float)
    with np.load(SHEARED_DATA) as data:
        sheared_endpoint = np.asarray(data["endpoint_predictor_center"], dtype=float)
    centers = np.vstack((centers, sheared_endpoint))
    projected = [compactified_terminal_chart(center) for center in centers]
    log_r4 = np.asarray([item["log_R4"] for item in projected], dtype=float)
    product_norm = np.asarray([item["product_norm"] for item in projected], dtype=float)
    center_norm = np.asarray(
        [np.linalg.norm(item["center_coordinates"]) for item in projected],
        dtype=float,
    )
    normal_norm = np.asarray(
        [np.linalg.norm(item["velocity_normals"]) for item in projected],
        dtype=float,
    )
    multiplier_norm = np.asarray(
        [np.linalg.norm(item["multipliers"]) for item in projected],
        dtype=float,
    )
    terminal = _load(TERMINAL)
    tube_log_epsilon = float(
        terminal["capture_origin_witness"]["tube_log_epsilon"]
    )
    endpoint_log_epsilon = float(projected[-1]["log_epsilon"])
    return {
        "stored_center_count_including_sheared_endpoint": int(centers.shape[0]),
        "initial_log_R4": float(log_r4[0]),
        "endpoint_log_R4": float(log_r4[-1]),
        "binary64_log_R4_spread": float(np.ptp(log_r4)),
        "initial_terminal_product_norm": float(product_norm[0]),
        "endpoint_terminal_product_norm": float(product_norm[-1]),
        "terminal_product_norm_decrease": float(product_norm[0] - product_norm[-1]),
        "terminal_product_norm_relative_decrease": float(
            (product_norm[0] - product_norm[-1]) / product_norm[0]
        ),
        "endpoint_center_coordinate_norm": float(center_norm[-1]),
        "endpoint_velocity_normal_norm": float(normal_norm[-1]),
        "endpoint_multiplier_norm": float(multiplier_norm[-1]),
        "endpoint_log_epsilon": endpoint_log_epsilon,
        "capture_tube_log_epsilon_upper": tube_log_epsilon,
        "remaining_log_epsilon_gap": endpoint_log_epsilon - tube_log_epsilon,
        "interpretation": (
            "THE_STORED_BINARY64_CENTERS_SHOW_NO_RESOLVED_RADIUS_MOTION_AND_ONLY_"
            "A_TINY_TERMINAL_PRODUCT_NORM_CHANGE;_THIS_IS_A_DIAGNOSTIC_TREND,_NOT_"
            "AN_INTERVAL_MONOTONICITY_THEOREM"
        ),
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing globalization inputs: " + ", ".join(missing))
    cover, recenter, sheared, launch, parametric, terminal, capture, connection, dichotomy = (
        _load(path)
        for path in (
            COVER,
            RECENTER,
            SHEARED,
            LAUNCH,
            PARAMETRIC,
            TERMINAL,
            CAPTURE,
            CONNECTION,
            DICHOTOMY,
        )
    )
    parents = (
        cover,
        recenter,
        sheared,
        launch,
        parametric,
        terminal,
        capture,
        connection,
        dichotomy,
    )
    if not all(parent.get("validation_passed") is True for parent in parents):
        raise RuntimeError("validated globalization parents required")

    rows = cover["cover"]["rows"]
    theta_steps = np.asarray([row["theta_step"] for row in rows], dtype=float)
    tube_radii = np.asarray(
        [row["endpoint_tube_radius_upper"] for row in rows], dtype=float
    )
    descriptor_centers = np.asarray(
        [cover["cover"]["initial_signed_descriptor"]]
        + [row["signed_descriptor_center_end"] for row in rows],
        dtype=float,
    )
    delta_centers = np.asarray([row["center_Delta"] for row in rows], dtype=float)
    step_ratios = theta_steps[1:] / theta_steps[:-1]
    terminal_trends = _terminal_trends()
    sheared_step = sheared["segment"]
    endpoint = recenter["endpoint"]

    trend_audit = {
        "cover_segment_count": len(rows),
        "cover_theta_total": float(cover["cover"]["theta_total"]),
        "sheared_theta_step": float(sheared_step["theta_step"]),
        "combined_certified_theta_advance": float(
            cover["cover"]["theta_total"] + sheared_step["theta_step"]
        ),
        "theta_step_first": float(theta_steps[0]),
        "theta_step_last": float(theta_steps[-1]),
        "theta_step_last_over_first": float(theta_steps[-1] / theta_steps[0]),
        "theta_step_ratio_min": float(np.min(step_ratios)),
        "theta_step_ratio_max": float(np.max(step_ratios)),
        "theta_step_ratio_median": float(np.median(step_ratios)),
        "cover_tube_radius_initial": float(tube_radii[0]),
        "cover_tube_radius_final": float(tube_radii[-1]),
        "cover_tube_growth_factor": float(tube_radii[-1] / tube_radii[0]),
        "cover_descriptor_center_initial": float(descriptor_centers[0]),
        "cover_descriptor_center_final": float(descriptor_centers[-1]),
        "cover_descriptor_center_growth_factor": float(
            descriptor_centers[-1] / descriptor_centers[0]
        ),
        "cover_descriptor_interval_final_lower": float(
            cover["cover"]["final_signed_descriptor_interval"][0]
        ),
        "recentered_descriptor_interval_lower": float(
            endpoint["signed_descriptor_interval"][0]
        ),
        "sheared_descriptor_interval_lower": float(
            sheared_step["signed_descriptor_interval_end"][0]
        ),
        "Delta_center_min": float(np.min(delta_centers)),
        "Delta_center_max": float(np.max(delta_centers)),
        "recentered_Delta_interval": list(sheared["domain"]["Delta_interval"]),
        "cover_exhaustion": cover["cover"]["exhaustion"],
        "cover_joint_domain_use_final": float(
            cover["cover"]["final_joint_domain_use_upper"]
        ),
        "cover_expanded_ball_radius": float(cover["cover"]["expanded_ball_radius"]),
        "sheared_joint_domain_use": float(sheared_step["joint_domain_use_upper"]),
        "sheared_selected_fresh_radius": float(sheared["domain"]["selected_fresh_radius"]),
        "terminal_projection": terminal_trends,
    }

    globalization_audit = {
        "MONOTONICITY": {
            "signed_descriptor": (
                "CERTIFIED_INCREASING_ON_THE_REALIZED_FINITE_COVER_AND_FIRST_"
                "SHEARED_BLOCK_BUT_NOT_A_CAPTURE_DISTANCE_AND_NO_GLOBAL_Delta_"
                "SIGN_REGION_CONNECTS_IT_TO_THE_TERMINAL_TUBE"
            ),
            "Delta": (
                "STRICTLY_POSITIVE_ON_THE_CURRENT_LOCAL_BLOCKS_ONLY;_Delta_ZERO_"
                "IS_NOT_A_CANONICAL_STOP_AND_NO_CONNECTED_GLOBAL_SIGN_THEOREM_EXISTS"
            ),
            "log_R4_H4": (
                "POSITIVE_H4_AND_EPSILON_DECAY_ARE_CERTIFIED_INSIDE_THE_CAPTURE_"
                "TUBE_ONLY;_NO_PRECAPTURE_LOWER_BOUND_FOR_D_LOG_R4_IS_AVAILABLE"
            ),
            "capture_distance": (
                "NO_INTERVAL_SIGN_FOR_THE_DERIVATIVE_OF_THE_74_COMPONENT_PRODUCT_"
                "DISTANCE_OR_ANY_ACTION_OWNED_EQUIVALENT_IS_CERTIFIED"
            ),
            "verdict": "NO_EXISTING_MONOTONE_QUANTITY_FORCES_GLOBAL_TUBE_ENTRY",
        },
        "CONE_GRAPH_TRANSFORM": {
            "endpoint_center_tangent_operator_norm": sheared["graph_variation"][
                "center_tangent_operator_norm"
            ],
            "endpoint_center_tangent_numerical_abscissa": sheared[
                "graph_variation"
            ]["center_tangent_numerical_abscissa"],
            "endpoint_interval_logarithmic_norm_upper": sheared[
                "graph_variation"
            ]["logarithmic_norm_ball_upper"],
            "local_graph_status": "ONE_SHEARED_INVARIANT_GRAPH_BLOCK_CERTIFIED",
            "asymptotic_cone_status": "STRICTLY_INWARD_ONLY_INSIDE_CAPTURE_TUBE",
            "missing_join": (
                "NO_SINGLE_CONE_FIELD_OR_UNIFORM_GRAPH_TRANSFORM_INEQUALITY_IS_"
                "CERTIFIED_ON_A_CONNECTED_REGION_OVERLAPPING_BOTH_BLOCKS"
            ),
            "verdict": "NO_GLOBAL_CONE_CONNECTION_DERIVED",
        },
        "DEGREE_COVERING": {
            "reset_launch_dimension": launch["dimension_theorem"][
                "C2_launch_manifold"
            ],
            "reset_seed_dimension": launch["dimension_theorem"][
                "swapped_C2_seed_image"
            ],
            "terminal_descriptor_dimension": terminal["map"]["descriptor_dimension"],
            "terminal_log_epsilon_is_additional": True,
            "compact_reset_parameter_box": "NOT_CERTIFIED",
            "propagated_reset_to_terminal_map": "NOT_CERTIFIED",
            "square_transverse_degree_map": "NOT_DEFINED",
            "boundary_exclusion_or_covering_faces": "NOT_CERTIFIED",
            "degree_value": "UNDEFINED_NOT_ZERO",
            "verdict": (
                "DIMENSION_COUNTS_AND_TERMINAL_JETS_ALONE_DO_NOT_DEFINE_A_"
                "BROUWER_DEGREE_OR_COVERING_RELATION"
            ),
        },
        "COMPACT_FINITE_SUBCOVER": {
            "current_cover_is_finite": True,
            "current_cover_termination": cover["cover"]["exhaustion"],
            "uniform_future_step_lower_bound": "NOT_CERTIFIED",
            "compact_full_reset_family_domain": "NOT_CERTIFIED",
            "finite_number_of_future_recenters": "NOT_BOUNDED",
            "verdict": "NO_FINITE_GLOBAL_SUBCOVER_THEOREM_DERIVED",
        },
        "EVENT_ALTERNATIVE": {
            "current_later_event_or_stop": sheared["adjudication"][
                "actual_later_event_or_canonical_stop"
            ],
            "Delta_zero_is_stop": False,
            "retained_stop_partition_exists": connection["validation"][
                "maximal_stop_list_is_existing_only"
            ],
            "first_hit_map_on_reset_family": "NOT_CERTIFIED",
            "verdict": "NO_FIRST_RETAINED_STOP_DERIVED",
        },
    }

    exact_missing_connector = {
        "route_A_global_inequality": (
            "A_CONNECTED_PRECAPTURE_INVARIANT_REGION_WITH_UNIFORM_EXISTING_DOMAIN_"
            "MARGINS_AND_AN_ACTION_OWNED_FUNCTIONAL_FORCING_FINITE_TUBE_ENTRY"
        ),
        "route_B_finite_set_map": (
            "A_COMPACT_NONEMPTY_RESET_QUOTIENT_PARAMETER_DOMAIN_K,_A_VALIDATED_"
            "FLOW_OR_FIRST_HIT_MAP_FROM_K_TO_THE_TERMINAL_CHART,_AND_EITHER_"
            "STRICT_TUBE_INCLUSION_OR_A_SQUARE_TRANSVERSE_MAP_WITH_BOUNDARY_"
            "EXCLUSION_AND_NONZERO_DEGREE"
        ),
        "route_C_stop": (
            "A_UNIFORM_FIRST_HIT_CERTIFICATE_FOR_ONE_ALREADY_RETAINED_CANONICAL_"
            "STOP_WITH_TRANSVERSALITY_AND_ALL_PRIOR_DOMAIN_MARGINS"
        ),
        "not_missing": [
            "another local proof radius",
            "another proof-center recenter",
            "another selected-line refinement",
            "a new selector or terminal recurrence law",
        ],
    }

    validation = {
        "all_parent_artifacts_validate": True,
        "sixteen_segment_cover_consumed": len(rows) == 16,
        "first_sheared_recenter_consumed": sheared["validation"][
            "sheared_matrix_Lohner_step_closes"
        ],
        "reset_launch_is_73_dimensional": launch["dimension_theorem"][
            "C2_launch_manifold"
        ]
        == 73,
        "terminal_descriptor_has_74_components": terminal["map"][
            "descriptor_dimension"
        ]
        == 74,
        "terminal_projection_is_executable": terminal["claim_boundary"][
            "terminal_capture_projection"
        ]
        == "DERIVED_WITH_FIRST_AND_MIXED_SECOND_JETS",
        "stable_capture_tube_is_certified": capture["claim_boundary"][
            "quantitative_capture_tube"
        ]
        == "CERTIFIED",
        "reset_entry_remains_open": capture["claim_boundary"][
            "AE2_reset_image_enters_capture_tube"
        ]
        == "OPEN_CURRENT_OWNER",
        "parametric_family_is_local_only": parametric["claim_boundary"][
            "numeric_parametric_or_interval_history_oracle"
        ]
        == "OPEN",
        "finite_connection_solution_is_open": connection["claim_boundary"][
            "actual_finite_connection_solution"
        ]
        == "OPEN",
        "cover_exhausted_by_fixed_step_budget_not_physical_stop": cover["cover"][
            "exhaustion"
        ]
        == "MAXIMUM_COVER_STEPS_REACHED_WITH_DOMAIN_OPEN",
        "current_cover_does_not_reach_capture_log_scale": terminal_trends[
            "remaining_log_epsilon_gap"
        ]
        > 1000.0,
        "current_terminal_product_norm_is_nonzero": terminal_trends[
            "endpoint_terminal_product_norm"
        ]
        > 1.0,
        "no_stop_reached": sheared["adjudication"][
            "actual_later_event_or_canonical_stop"
        ]
        == "NOT_REACHED",
        "maximal_flow_dichotomy_preserved": dichotomy["domain"]["new_gate"] is False,
        "connection_not_disproved": True,
        "no_selector_recurrence_chord_fit_scale_action_or_time_direction_added": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_GLOBAL_CONNECTION_OBSTRUCTION",
        "status": (
            "EXACT_GLOBAL_CONNECTION_OBSTRUCTION_LOCALIZED"
            if passed
            else "GLOBAL_CONNECTION_AUDIT_INVALID"
        ),
        "classification": (
            "THE_CLOSED_LOCAL_COVER,_SHEARED_RECENTER,_73_DIMENSIONAL_RESET_"
            "LAUNCH,_EXECUTABLE_TERMINAL_PROJECTION,_AND_STABLE_TUBE_DO_NOT_YET_"
            "COMPOSE_TO_A_FINITE_GLOBAL_CONNECTION_THEOREM;_THE_EXACT_MISSING_"
            "OBJECT_IS_A_COMPACT_BOUNDARY_CONTROLLED_PROPAGATED_RESET_SET_MAP_OR_"
            "AN_EQUIVALENT_GLOBAL_INVARIANT_REGION,_NOT_ANOTHER_LOCAL_RADIUS"
        ),
        "current_certified_sheared_endpoint": {
            "selected_branch": endpoint["selected_branch"],
            "incoming_endpoint_tube_radius_upper": endpoint[
                "incoming_endpoint_tube_radius_upper"
            ],
            "fresh_chart_radius": endpoint["fresh_chart_radius"],
            "fresh_growth_radius": endpoint["fresh_growth_radius"],
            "center_Delta": endpoint["center_Delta"],
            "center_cancelled_field_action_norm": endpoint[
                "center_cancelled_field_action_norm"
            ],
            "sheared_Delta_interval": list(sheared["domain"]["Delta_interval"]),
            "sheared_descriptor_interval_end": list(
                sheared_step["signed_descriptor_interval_end"]
            ),
            "sheared_endpoint_tube_radius_upper": sheared_step[
                "endpoint_tube_radius_upper"
            ],
            "positive_proper_time": sheared["validation"]["positive_proper_duration"],
        },
        "trend_audit": trend_audit,
        "globalization_audit": globalization_audit,
        "exact_missing_connector": exact_missing_connector,
        "adjudication": {
            "RESET_TO_CAPTURE_GLOBAL_CONNECTION_DERIVED": False,
            "RESET_TO_FIRST_RETAINED_STOP_DERIVED": False,
            "EXACT_GLOBAL_CONNECTION_OBSTRUCTION_LOCALIZED": passed,
            "another_local_block_authorized_as_default_next_step": False,
            "connection_mathematically_impossible": False,
            "Gate7": "OPEN_ON_EXACT_GLOBAL_CONNECTOR",
            "downstream_rank72_force_KKT_Hessian": "WAITING_ON_CONNECTION_OR_STOP",
        },
        "hindsight": {
            "VALIDATED": (
                "THE_LOCAL_RESET_FAMILY,_FINITE_COVER,_SHEARED_RECENTER,_TERMINAL_"
                "PROJECTION,_AND_CAPTURE_TUBE_ARE_REAL_AND_COMPATIBLE_LOCAL_OBJECTS"
            ),
            "INVALIDATED": (
                "REPEATED_LOCAL_RADIUS_OR_RECENTER_IMPROVEMENT_BY_ITSELF_MATERIALLY_"
                "ADVANCES_THE_GLOBAL_CAPTURE_PROOF"
            ),
            "OPEN": "ONE_FINITE_GLOBAL_RESET_SET_CONNECTION_OR_FIRST_RETAINED_STOP",
            "GLOBALIZATION_CHECK": (
                "YES_THE_NEXT_THEOREM_MUST_SUPPLY_THE_COMPACT_PROPAGATED_SET_MAP_"
                "WITH_BOUNDARY_CONTROL_OR_AN_EQUIVALENT_INVARIANT_REGION"
            ),
            "BHSM_NATIVE_CHECK": (
                "THE_CONNECTION_OR_STOP_IS_ACTION_OBSERVABLE_REQUIRED;_THE_CHOICE_"
                "OF_MONOTONICITY_CONE_DEGREE_OR_MULTIPLE_SHOOTING_IS_PROOF_METHOD"
            ),
        },
        "claim_boundary": {
            "Gate7": "OPEN_EXACT_GLOBAL_CONNECTION_CONNECTOR_LOCALIZED",
            "Gate8": "LOCKED",
            "reset_to_capture": "NOT_CERTIFIED",
            "first_retained_stop": "NOT_CERTIFIED",
            "global_connection_impossibility": "NOT_CLAIMED",
            "actual_projected_zero_source_force": "OPEN_AFTER_CONNECTION_OR_STOP",
            "same_action_KKT_root": "WAITING_ON_FORCE",
            "physical_constrained_Hessian": "WAITING_ON_KKT_ROOT",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "DERIVE_ONE_FINITE_BHSM_NATIVE_GLOBAL_CONNECTOR:_EITHER_A_CONNECTED_"
            "INVARIANT_REGION_FORCING_CAPTURE,_A_COMPACT_RESET_QUOTIENT_FLOW_OR_"
            "FIRST_HIT_MAP_WITH_STRICT_TUBE_INCLUSION_OR_NONZERO_DEGREE_AND_"
            "BOUNDARY_EXCLUSION,_OR_THE_TRANSVERSE_FIRST_HIT_OF_AN_EXISTING_"
            "CANONICAL_STOP;_DO_NOT_CONTINUE_UNBOUNDED_LOCAL_RECENTERING"
        ),
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
    print(
        json.dumps(
            {
                "status": payload["status"],
                "remaining_log_epsilon_gap": payload["trend_audit"][
                    "terminal_projection"
                ]["remaining_log_epsilon_gap"],
                "next": payload["exact_next_dependency"],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
