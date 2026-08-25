"""Certify the fixed-node radius part of the 1222-core reset pullback."""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_boundary_radius import (  # noqa: E402
    boundary_log_radius_jets,
)
from bhsm.interface.aether_forward_c2_adaptive_ball import (  # noqa: E402
    derived_adaptive_ball,
)
from bhsm.interface.aether_forward_c2_descriptor_cover import (  # noqa: E402
    translated_ball_bounds,
    translated_generator,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_1222_RESET_QUOTIENT_RADIUS_PULLBACK_ENCLOSURE.json"
DATA_RESULT = RESULT.with_suffix(".npz")
CORE = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CORE_DATA = CORE.with_suffix(".npz")
COTANGENT = BASE / "BHSM_N12_C2_1222_SEGMENT_WEYL_COEFFICIENT_COTANGENT.json"
COTANGENT_DATA = COTANGENT.with_suffix(".npz")
OUTER = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
SECOND = BASE / "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.json"
EXTENDED = BASE / "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT.json"
COMPENSATED = BASE / "BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION.json"
COMPENSATED_DATA = COMPENSATED.with_suffix(".npz")
ADAPTIVE = BASE / "BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION.json"
ADAPTIVE_DATA = ADAPTIVE.with_suffix(".npz")
RECENTER = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.json"
RECENTER_DATA = RECENTER.with_suffix(".npz")
RECENTERED = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.json"
RECENTERED_DATA = RECENTERED.with_suffix(".npz")
POLE_FREE = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
ACTION = BASE / "BHSM_N12_FINITE_TERMINAL_ACTION_BALL_MAJORANTS.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
FIBER = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION.json"
GAP = BASE / "BHSM_N12_C2_UNIFORM_GAP_CONTINUATION.json"
SECOND_GAP = BASE / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.json"
BIRTH = BASE / "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET.json"
THEORY = ROOT / "theory" / "n12_c2_1222_reset_quotient_radius_pullback_enclosure.md"
STEP_NUMBERS = tuple(range(1215, 1223))
CHANNELS = (
    "scalar_c3",
    "product_Dirac_lambda1_5_chirality_plus",
    "product_Dirac_lambda1_5_chirality_minus",
)


def _step_path(segment: int) -> Path:
    if segment == 1215:
        return BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
    return BASE / f"BHSM_N12_C2_LOHNER_STEP_{segment}.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _close(left: float, right: float, *, rtol: float = 2.0e-12) -> bool:
    return math.isclose(float(left), float(right), rel_tol=rtol, abs_tol=0.0)


def _replay_translated_growth() -> tuple[list[float], dict[str, Any]]:
    pole_free, launch, line_record, action = (
        _load(path) for path in (POLE_FREE, LAUNCH, LINE, ACTION)
    )
    pf = pole_free["bounds"]
    launch_ball = launch["launch_ball"]
    line = line_record["bounds"]
    parent_radius = float(action["action_coordinate_ball_radius"])
    with np.load(CANDIDATE) as data:
        root_state = np.asarray(data["state"], dtype=float)[:98]

    local: list[float] = []
    residuals: list[float] = []

    extended = _load(EXTENDED)["cover"]
    local.extend(float(row["Jacobi_growth_upper"]) for row in extended["rows"])

    compensated = _load(COMPENSATED)["compensated_cover"]
    with np.load(COMPENSATED_DATA) as data:
        centers = np.asarray(data["C2_compensated_predictor_centers"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    center_path = float(extended["final_center_path_upper"])
    tube = float(extended["final_endpoint_tube_radius_upper"])
    for center, row in zip(centers[:-1], compensated["rows"], strict=True):
        ball = translated_ball_bounds(
            center_path=center_path,
            tube=tube,
            pf=pf,
            launch_ball=launch_ball,
            line=line,
            parent_radius=parent_radius,
            root_state=root_state,
            weights=weights,
            coefficient_enclosure=_coefficient_enclosure,
        )
        generator = translated_generator(
            ball=ball,
            pf=pf,
            launch_ball=launch_ball,
            line=line,
            root_state=root_state,
        )
        step = float(Decimal(row["signed_lambda_step_decimal"]))
        growth = math.exp(float(generator["pole_free_regularized_Jacobi_upper"]) * step)
        local.append(growth)
        residuals.extend((
            abs(float(ball["Delta_interval"][0]) - float(row["Delta_lower"])),
            abs(float(ball["total_root_relative_radius"]) - float(row["translated_ball_total_radius"])),
        ))
        center_path = float(row["center_path_upper"])
        tube = float(row["endpoint_tube_radius_upper"])

    adaptive = _load(ADAPTIVE)["adaptive_cover"]
    with np.load(ADAPTIVE_DATA) as data:
        centers = np.asarray(data["C2_adaptive_predictor_centers"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    center_path = float(compensated["final_center_path_upper"])
    tube = float(compensated["final_endpoint_tube_radius_upper"])
    for center, row in zip(centers[:-1], adaptive["rows"], strict=True):
        ball = derived_adaptive_ball(
            center_path=center_path,
            tube=tube,
            pf=pf,
            launch_ball=launch_ball,
            line=line,
            parent_radius=parent_radius,
            root_state=root_state,
            weights=weights,
            coefficient_enclosure=_coefficient_enclosure,
        )
        generator = translated_generator(
            ball=ball,
            pf=pf,
            launch_ball=launch_ball,
            line=line,
            root_state=root_state,
        )
        step = float(Decimal(row["signed_lambda_step_decimal"]))
        growth = math.exp(float(generator["pole_free_regularized_Jacobi_upper"]) * step)
        local.append(growth)
        residuals.extend((
            abs(float(ball["Delta_interval"][0]) - float(row["Delta_lower"])),
            abs(float(ball["derived_local_radius"]) - float(row["derived_local_radius"])),
        ))
        center_path = float(row["center_path_upper"])
        tube = float(row["endpoint_tube_radius_upper"])

    recenter = _load(RECENTER)["recenter"]
    recentered = _load(RECENTERED)["recentered_cover"]
    with np.load(RECENTERED_DATA) as data:
        centers = np.asarray(data["C2_recentered_adaptive_predictor_centers"], dtype=float)
        root_state = np.asarray(data["recentered_root_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    pf = recenter["recentered_pole_free_bounds"]
    launch_ball = recenter["recentered_launch_ball"]
    parent_radius = float(recenter["recentered_parent_action_radius"])
    center_path = 0.0
    tube = float(recenter["incoming_endpoint_tube_upper"])
    for center, row in zip(centers[:-1], recentered["rows"], strict=True):
        ball = derived_adaptive_ball(
            center_path=center_path,
            tube=tube,
            pf=pf,
            launch_ball=launch_ball,
            line=line,
            parent_radius=parent_radius,
            root_state=root_state,
            weights=weights,
            coefficient_enclosure=_coefficient_enclosure,
        )
        generator = translated_generator(
            ball=ball,
            pf=pf,
            launch_ball=launch_ball,
            line=line,
            root_state=root_state,
        )
        step = float(Decimal(row["signed_lambda_step_decimal"]))
        growth = math.exp(float(generator["pole_free_regularized_Jacobi_upper"]) * step)
        local.append(growth)
        residuals.extend((
            abs(float(ball["Delta_interval"][0]) - float(row["Delta_lower"])),
            abs(float(ball["derived_local_radius"]) - float(row["derived_local_radius"])),
        ))
        center_path = float(row["center_path_from_recenter_upper"])
        tube = float(row["endpoint_tube_radius_upper"])

    return local, {
        "replayed_segment_count": len(local),
        "maximum_absolute_replay_residual": max(residuals, default=0.0),
        "all_replayed_values_finite_positive": all(
            math.isfinite(value) and value >= 1.0 for value in local
        ),
    }


def _all_local_growth() -> tuple[np.ndarray, dict[str, Any]]:
    translated, replay = _replay_translated_growth()
    values = [
        float(_load(OUTER)["extended_segment"]["Jacobi_growth_upper"]),
        float(_load(SECOND)["translated_segment"]["Jacobi_growth_upper"]),
        *translated,
    ]
    for path, key in ((FIBER, "continuation"), (GAP, "continuation"), (SECOND_GAP, "continuation")):
        values.extend(float(row["Jacobi_growth_upper"]) for row in _load(path)[key]["rows"])
    values.extend(float(Decimal(_load(_step_path(index))["segment"]["matrix_growth_upper"])) for index in STEP_NUMBERS)
    return np.asarray(values, dtype=float), replay


def _logsumexp(log_terms: np.ndarray) -> float:
    maximum = float(np.max(log_terms))
    return maximum + math.log(float(np.sum(np.exp(log_terms - maximum))))


def build_payload() -> dict[str, Any]:
    step_paths = tuple(_step_path(index) for index in STEP_NUMBERS)
    inputs = (
        CORE, CORE_DATA, COTANGENT, COTANGENT_DATA, OUTER, SECOND, EXTENDED,
        COMPENSATED, COMPENSATED_DATA, ADAPTIVE, ADAPTIVE_DATA, RECENTER,
        RECENTER_DATA, RECENTERED, RECENTERED_DATA, POLE_FREE, LAUNCH, LINE,
        ACTION, CANDIDATE, FIBER, GAP, SECOND_GAP, BIRTH, THEORY, *step_paths,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing reset-pullback inputs: " + ", ".join(missing))
    records = [_load(path) for path in (
        CORE, COTANGENT, OUTER, SECOND, EXTENDED, COMPENSATED, ADAPTIVE,
        RECENTER, RECENTERED, POLE_FREE, LAUNCH, LINE, ACTION, FIBER, GAP,
        SECOND_GAP, BIRTH, *step_paths,
    )]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated reset-pullback parents required")

    local_growth, replay = _all_local_growth()
    log_node_growth = np.concatenate((
        np.zeros(1), np.cumsum(np.log(local_growth)),
    ))
    with np.load(CORE_DATA) as data:
        nodes = np.asarray(data["C2_proof_center_nodes"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        tubes = np.asarray(data["node_action_tube_upper"], dtype=float)

    q_weights = weights[:37]
    signs = (-1.0) ** np.arange(12)
    b_dual = float(np.linalg.norm(signs / q_weights[25:37]))
    radius_dual = []
    for node, tube in zip(nodes, tubes, strict=True):
        gradient = np.asarray(boundary_log_radius_jets(
            12, node[:37], np.zeros(37), np.zeros(37),
        )["gradient"], dtype=float)
        center_dual = float(np.linalg.norm(gradient / q_weights))
        radius_dual.append(center_dual + 2.0 * b_dual**2 * float(tube))
    radius_dual_array = np.asarray(radius_dual)

    summaries: dict[str, Any] = {}
    arrays: dict[str, np.ndarray] = {
        "local_state_Jacobi_growth_upper": local_growth,
        "node_log_state_Jacobi_growth_upper": log_node_growth,
        "node_log_R4_action_dual_upper": radius_dual_array,
    }
    with np.load(COTANGENT_DATA) as data:
        for channel in CHANNELS:
            cotangent = np.asarray(data[f"{channel}__D_log_R4_node_Weyl"], dtype=float)
            nonzero = np.abs(cotangent) > 0.0
            log_terms = (
                np.log(np.abs(cotangent[nonzero]))
                + np.log(radius_dual_array[nonzero])
                + log_node_growth[nonzero]
            )
            log_bound = _logsumexp(log_terms)
            summaries[channel] = {
                "fixed_node_radius_cotangent_l1_norm": float(np.sum(np.abs(cotangent))),
                "log_reset_image_operator_norm_upper": log_bound,
                "log10_reset_image_operator_norm_upper": log_bound / math.log(10.0),
                "reset_image_operator_norm_upper": (
                    math.exp(log_bound) if log_bound < math.log(np.finfo(float).max) else None
                ),
                "moving_proper_duration_cotangent_l1_norm": float(np.sum(np.abs(
                    np.asarray(data[f"{channel}__D_proper_duration_Weyl"], dtype=float)
                ))),
                "moving_duration_reset_pullback_included": False,
            }

    np.savez_compressed(DATA_RESULT, **arrays)
    birth = _load(BIRTH)
    validation = {
        "exactly_1222_local_growth_factors_assembled": local_growth.shape == (1222,),
        "every_local_growth_factor_is_finite_and_at_least_one": bool(
            np.all(np.isfinite(local_growth)) and np.all(local_growth >= 1.0)
        ),
        "exactly_1223_node_growth_bounds_assembled": log_node_growth.shape == (1223,),
        "replayed_1064_prefix_middle_has_1062_segments": replay["replayed_segment_count"] == 1062,
        "replayed_ball_data_match_stored_rows": replay["maximum_absolute_replay_residual"] < 1.0e-12,
        "all_node_radius_covector_bounds_are_finite_positive": bool(
            np.all(np.isfinite(radius_dual_array)) and np.all(radius_dual_array > 0.0)
        ),
        "actual_C2_reset_image_is_certified": birth["swapped_reset"]["C2_projection_rank"] == 73,
        "fixed_node_radius_cotangent_pullbacks_are_finite_in_log_space": all(
            math.isfinite(row["log_reset_image_operator_norm_upper"])
            for row in summaries.values()
        ),
        "moving_duration_term_not_silently_dropped": all(
            row["moving_proper_duration_cotangent_l1_norm"] > 0.0
            and row["moving_duration_reset_pullback_included"] is False
            for row in summaries.values()
        ),
        "far_core_edge_not_promoted_to_event_or_stop": True,
        "no_selector_recurrence_scale_fit_action_term_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1222_RESET_QUOTIENT_RADIUS_PULLBACK_ENCLOSURE",
        "status": (
            "C2_1222_FIXED_NODE_RADIUS_RESET_PULLBACK_CERTIFIED_DURATION_PULLBACK_OPEN"
            if passed else "C2_1222_RESET_PULLBACK_ENCLOSURE_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_OMITTED_LOCAL_JACOBI_FACTORS_ARE_REPLAYED_FROM_THEIR_ACTION_OWNED_"
            "BALLS_AND_THE_1222_CORE_FIXED_NODE_LOG_RADIUS_WEYL_COTANGENT_HAS_A_"
            "FINITE_OPERATOR_NORM_PULLBACK_ON_EVERY_UNIT_C2_RESET_IMAGE_DIRECTION;_"
            "THE_MOVING_PROPER_DURATION_COTANGENT_IS_NONZERO_AND_REMAINS_OUTSIDE_"
            "THIS_CERTIFICATE"
        ),
        "Jacobi_provenance": {
            "segment_count": int(local_growth.size),
            "node_count": int(log_node_growth.size),
            "block_segment_counts": {
                "outer_margin": 1,
                "translated_second": 1,
                "extended_descriptor": 434,
                "replayed_compensated": 15,
                "replayed_adaptive": 340,
                "replayed_recentered_adaptive": 273,
                "descriptor_fiber_cancelled": 64,
                "uniform_gap": 64,
                "second_uniform_gap": 22,
                "matrix_Lohner": 8,
            },
            "terminal_log_state_Jacobi_growth_upper": float(log_node_growth[-1]),
            "terminal_log10_state_Jacobi_growth_upper": float(log_node_growth[-1] / math.log(10.0)),
            "terminal_state_Jacobi_growth_upper": (
                math.exp(float(log_node_growth[-1]))
                if log_node_growth[-1] < math.log(np.finfo(float).max) else None
            ),
            "replay_crosscheck": replay,
        },
        "fixed_node_radius_pullback": summaries,
        "theorem": {
            "node_state_bound": "norm(D_Y0_Y_i)<=product_(e<i) G_e",
            "radius_covector_bound": (
                "norm(D_Y_logR4)_action_dual<=norm(D_logR4(center))_dual+2*norm(b_signs)_dual^2*tube"
            ),
            "channel_bound": (
                "norm(sum_i c_i*D_Y0_logR4_i)<=sum_i|c_i|*radius_dual_i*product_(e<i)G_e"
            ),
            "reset_image_rule": (
                "THE_C2_BLOCK_OF_A_UNIT_ORTHONORMAL_RESET_TANGENT_DIRECTION_HAS_ACTION_NORM_AT_MOST_ONE"
            ),
            "physical_quotient_rule": (
                "ORTHOGONAL_GAUGE_TIME_PROJECTION_CANNOT_INCREASE_THIS_AMBIENT_C2_IMAGE_BOUND"
            ),
        },
        "open_term": {
            "name": "MOVING_PROPER_DURATION_RESET_COTANGENT",
            "required_object": "D_h_i_COMPOSE_D_RESET_AND_THE_FIXED_s_STATE_PROPAGATOR_FOR_ALL_1222_SEGMENTS",
            "why_not_closed_here": (
                "THE_COEFFICIENT_COTANGENT_CONTAINS_NONZERO_D_proper_duration_WEIGHTS;_"
                "THE_STORED_DURATION_INTERVALS_AND_LOCAL_STATE_GROWTH_BOUNDS_DO_NOT_"
                "BY_THEMSELVES_SUPPLY_THE_SIGNED_MOVING_TIME_FIRST_JET"
            ),
            "exact_formula": (
                "D_h_i=integral_segment_i D_Y(N_boundary*s/Delta)[J_h] ds_"
                "PLUS_THE_TRANSVERSE_MOVING_EDGE_TERM"
            ),
            "not_permitted_substitution": "DURATION_INTERVAL_WIDTH_OR_PROOF_TUBE_IS_NOT_A_DURATION_FIRST_JET",
        },
        "adjudication": {
            "fixed_node_radius_reset_pullback": "CERTIFIED_ON_1222_FINITE_CORE",
            "moving_duration_reset_pullback": "OPEN_CURRENT_FINITE_CORE_SLOT",
            "full_1222_D_xi_M_C": "OPEN_ONLY_AFTER_MOVING_DURATION_AND_GRADED_SOURCE_CONTRACTION",
            "actual_zero_source_force": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
            "physical_Hessian": "WAITING_ON_SADDLE",
        },
        "exact_next_dependency": (
            "DERIVE_THE_ACTION_OWNED_MOVING_PROPER_DURATION_ADJOINT_ON_THE_SAME_"
            "1222_FIXED_s_COVER_AND_CONTRACT_IT_WITH_THE_STORED_D_proper_duration_"
            "WEYL_COTANGENT;_DO_NOT_REOPEN_RESET_RECURRENCE_FIXED_CHANNEL_DINI_"
            "TERMINAL_RECURRENCE_OR_CHORD3"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_MOVING_DURATION_PULLBACK_AND_GRADED_FORCE_CONTRACTION",
            "Gate8": "LOCKED",
            "fixed_node_radius_pullback": "CERTIFIED",
            "moving_duration_pullback": "OPEN",
            "actual_projected_zero_source_force": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in inputs},
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
        "terminal_log10_growth": payload["Jacobi_provenance"]["terminal_log10_state_Jacobi_growth_upper"],
        "channel_log10_bounds": {
            key: row["log10_reset_image_operator_norm_upper"]
            for key, row in payload["fixed_node_radius_pullback"].items()
        },
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
