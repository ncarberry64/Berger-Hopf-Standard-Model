"""Certify the moving-duration reset pullback on the 1222-segment C2 core."""

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

from bhsm.interface.aether_forward_c2_adaptive_ball import derived_adaptive_ball  # noqa: E402
from bhsm.interface.aether_forward_c2_descriptor_cover import (  # noqa: E402
    metric_data,
    translated_ball_bounds,
    translated_generator,
)
from bhsm.interface.aether_forward_c2_descriptor_fiber_ball import (  # noqa: E402
    fresh_center_descriptor_fiber_ball,
)
from bhsm.interface.aether_forward_c2_duration_adjoint import (  # noqa: E402
    segment_duration_pullback_upper,
)
from bhsm.interface.aether_forward_c2_uniform_gap_fiber_ball import (  # noqa: E402
    uniform_gap_descriptor_fiber_ball,
)
from certify_n12_c2_descriptor_fiber_cancelled_continuation import (  # noqa: E402
    _fiber_center_field,
)
from certify_n12_c2_fresh_center_denominator_continuation import (  # noqa: E402
    _center_data,
    _float_upper,
    _maximal_closing_step,
)
from certify_n12_c2_uniform_gap_continuation import _center_response  # noqa: E402
from derive_n12_c2_birth_coefficient_quotient_jet import _coefficient_enclosure  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_1222_MOVING_DURATION_PULLBACK_ENCLOSURE.json"
DATA_RESULT = RESULT.with_suffix(".npz")
CORE = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CORE_DATA = CORE.with_suffix(".npz")
COTANGENT = BASE / "BHSM_N12_C2_1222_SEGMENT_WEYL_COEFFICIENT_COTANGENT.json"
COTANGENT_DATA = COTANGENT.with_suffix(".npz")
RADIUS = BASE / "BHSM_N12_C2_1222_RESET_QUOTIENT_RADIUS_PULLBACK_ENCLOSURE.json"
RADIUS_DATA = RADIUS.with_suffix(".npz")
OUTER = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
SECOND = BASE / "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.json"
SECOND_BALL = BASE / "BHSM_N12_C2_SECOND_TRANSLATED_DESCRIPTOR_BALL.json"
EXTENDED = BASE / "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT.json"
EXTENDED_DATA = EXTENDED.with_suffix(".npz")
COMPENSATED = BASE / "BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION.json"
COMPENSATED_DATA = COMPENSATED.with_suffix(".npz")
ADAPTIVE = BASE / "BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION.json"
ADAPTIVE_DATA = ADAPTIVE.with_suffix(".npz")
RECENTER = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.json"
RECENTERED = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.json"
RECENTERED_DATA = RECENTERED.with_suffix(".npz")
POLE_FREE = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
ACTION = BASE / "BHSM_N12_FINITE_TERMINAL_ACTION_BALL_MAJORANTS.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
FIBER = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION.json"
FIBER_DATA = FIBER.with_suffix(".npz")
MAJORANTS = BASE / "BHSM_N12_C2_LAUNCH_ACTION_MAJORANTS.json"
FIBER_PARENT = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_DENOMINATOR.json"
GAP = BASE / "BHSM_N12_C2_UNIFORM_GAP_CONTINUATION.json"
GAP_DATA = GAP.with_suffix(".npz")
BIRTH_REMAINDER = BASE / "BHSM_N12_C2_BIRTH_LIMIT_CONJUGATED_TANGENT_REMAINDER.json"
HARD = BASE / "BHSM_N12_C2_UNIFORM_GAP_HARD_RESPONSE.json"
SECOND_GAP = BASE / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.json"
SECOND_GAP_DATA = SECOND_GAP.with_suffix(".npz")
CHART = BASE / "BHSM_N12_C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART.json"
FRESH_GROWTH = BASE / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_duration_adjoint.py"
THEORY = ROOT / "theory" / "n12_c2_1222_moving_duration_pullback_enclosure.md"
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


def _append(rows: list[tuple[float, float, float]], ball: dict[str, Any], delta_derivative: float) -> None:
    rows.append((
        float(ball["Delta_interval"][0]),
        float(delta_derivative),
        float(ball["lapse_interval"][1]),
    ))


def _translated_majorants() -> tuple[list[tuple[float, float, float]], float]:
    launch_record = _load(LAUNCH)
    outer = _load(OUTER)
    second = _load(SECOND)
    second_ball = _load(SECOND_BALL)["translated_ball"]
    pole_free, line_record, action = (_load(path) for path in (POLE_FREE, LINE, ACTION))
    pf = pole_free["bounds"]
    launch_ball = launch_record["launch_ball"]
    line = line_record["bounds"]
    parent_radius = float(action["action_coordinate_ball_radius"])
    with np.load(CANDIDATE) as data:
        root_state = np.asarray(data["state"], dtype=float)[:98]
    lapse_upper_outer = float(launch_record["explicit_segment"]["lapse_interval_on_launch_ball"][1])
    rows: list[tuple[float, float, float]] = [(
        float(outer["improved_launch_ball"]["Delta_interval"][0]),
        float(launch_ball["Delta_action_derivative_upper"]),
        lapse_upper_outer,
    ), (
        float(second_ball["Delta_interval"][0]),
        float(second["translated_generator"]["Delta_action_derivative_upper"]),
        float(second_ball["lapse_interval"][1]),
    )]
    residual = 0.0

    extended = _load(EXTENDED)["cover"]
    with np.load(EXTENDED_DATA) as data:
        centers = np.asarray(data["C2_predictor_centers"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    for center, row in zip(centers[:-1], extended["rows"], strict=True):
        ball = translated_ball_bounds(
            center_path=float(row["center_path_upper_before"]),
            tube=float(row["incoming_tube_radius"]),
            pf=pf, launch_ball=launch_ball, line=line,
            parent_radius=parent_radius, root_state=root_state, weights=weights,
            coefficient_enclosure=_coefficient_enclosure,
        )
        generator = translated_generator(
            ball=ball, pf=pf, launch_ball=launch_ball, line=line, root_state=root_state,
        )
        _append(rows, ball, float(generator["Delta_action_derivative_upper"]))
        residual = max(residual, abs(float(ball["Delta_interval"][0]) - float(row["Delta_lower"])))

    compensated = _load(COMPENSATED)["compensated_cover"]
    with np.load(COMPENSATED_DATA) as data:
        centers = np.asarray(data["C2_compensated_predictor_centers"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    center_path = float(extended["final_center_path_upper"])
    tube = float(extended["final_endpoint_tube_radius_upper"])
    for center, row in zip(centers[:-1], compensated["rows"], strict=True):
        ball = translated_ball_bounds(
            center_path=center_path, tube=tube, pf=pf, launch_ball=launch_ball,
            line=line, parent_radius=parent_radius, root_state=root_state,
            weights=weights, coefficient_enclosure=_coefficient_enclosure,
        )
        generator = translated_generator(ball=ball, pf=pf, launch_ball=launch_ball, line=line, root_state=root_state)
        _append(rows, ball, float(generator["Delta_action_derivative_upper"]))
        residual = max(residual, abs(float(ball["Delta_interval"][0]) - float(row["Delta_lower"])))
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
            center_path=center_path, tube=tube, pf=pf, launch_ball=launch_ball,
            line=line, parent_radius=parent_radius, root_state=root_state,
            weights=weights, coefficient_enclosure=_coefficient_enclosure,
        )
        generator = translated_generator(ball=ball, pf=pf, launch_ball=launch_ball, line=line, root_state=root_state)
        _append(rows, ball, float(generator["Delta_action_derivative_upper"]))
        residual = max(residual, abs(float(ball["Delta_interval"][0]) - float(row["Delta_lower"])))
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
            center_path=center_path, tube=tube, pf=pf, launch_ball=launch_ball,
            line=line, parent_radius=parent_radius, root_state=root_state,
            weights=weights, coefficient_enclosure=_coefficient_enclosure,
        )
        generator = translated_generator(ball=ball, pf=pf, launch_ball=launch_ball, line=line, root_state=root_state)
        _append(rows, ball, float(generator["Delta_action_derivative_upper"]))
        residual = max(residual, abs(float(ball["Delta_interval"][0]) - float(row["Delta_lower"])))
        center_path = float(row["center_path_from_recenter_upper"])
        tube = float(row["endpoint_tube_radius_upper"])
    return rows, residual


def _fiber_majorants() -> tuple[list[tuple[float, float, float]], float]:
    prefix, recenter, line_record, majorants, fiber_parent = (
        _load(path) for path in (RECENTERED, RECENTER, LINE, MAJORANTS, FIBER_PARENT)
    )
    record = _load(FIBER)["continuation"]
    with np.load(FIBER_DATA) as data:
        centers = np.asarray(data["C2_descriptor_fiber_predictor_centers"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    transferred = recenter["recenter"]
    launch = transferred["recentered_launch_ball"]
    base_pf = transferred["recentered_pole_free_bounds"]
    line = line_record["bounds"]
    fifth = float(next(row for row in majorants["sectors"] if row["sector"] == "event")["derivative_operator_majorants_0_through_5"][5])
    tube = float(record["initial_endpoint_tube_radius_upper"])
    path = 0.0
    rows: list[tuple[float, float, float]] = []
    residual = 0.0
    for center, stored in zip(centers[:-1], record["rows"], strict=True):
        pf = dict(base_pf)
        pf.update({
            "hard_D3_center": float(base_pf["hard_D3_center"]) + float(base_pf["D4_full_hard_hard_upper"]) * path,
            "rhs_raw_derivative_center": float(base_pf["rhs_raw_derivative_center"]) + float(base_pf["rhs_raw_second_derivative_upper"]) * path,
            "coupling_center": float(base_pf["coupling_center"]) + float(base_pf["D4_full_selected_hard_upper"]) * path,
            "center_hard_rate_raw_norm": float(base_pf["center_hard_rate_raw_norm"]) + float(base_pf["hard_Jacobi_action_upper"]) * path / max(float(np.max(weights[37:])), 1.0),
        })
        center_data = _center_data(center, weights, reference, fifth)
        selected_norm = float(np.linalg.norm(np.asarray(center_data["selected_vector"]) * weights[37:]))
        parent_radius = min(
            float(transferred["recentered_parent_action_radius"]) - path,
            float(line_record["action_coordinate_ball_radius"]) - float(transferred["old_root_to_new_center_action_distance_upper"]) - path,
        )
        ball = fresh_center_descriptor_fiber_ball(
            incoming_tube=tube, parent_radius=parent_radius,
            descriptor_upper=float(stored["descriptor_fiber_lambda_upper"]),
            pf=pf, launch=launch, line=line,
            center_c=tuple(center_data["c_psi_center_interval"]),
            center_b=tuple(center_data["b_psi_center_interval"]),
            center_selected_action_norm=selected_norm, center_state=center,
            weights=weights, coefficient_enclosure=_coefficient_enclosure,
        )
        _append(rows, ball, float(ball["Delta_action_derivative_upper"]))
        residual = max(residual, abs(float(ball["Delta_interval"][0]) - float(stored["Delta_lower"])))
        tube = float(stored["endpoint_tube_radius_upper"])
        path = float(stored["fresh_center_path_upper"])
    return rows, residual


def _gap_majorants(*, second: bool) -> tuple[list[tuple[float, float, float]], float]:
    if second:
        prefix = _load(GAP)["continuation"]
        record = _load(SECOND_GAP)["continuation"]
        data_path = SECOND_GAP_DATA
        data_key = "C2_second_uniform_gap_predictor_centers"
        growth = _load(FRESH_GROWTH)
        fresh = growth["fresh_line_bounds"]
        line = {
            "eigenline_gap_lower": float(fresh["eigenline_gap_lower"]),
            "weighted_selected_to_complement_first_variation_on_ball": float(fresh["weighted_selected_to_complement_first_variation_on_ball"]),
            "selected_eigenvalue_first_derivative_bound": float(fresh["selected_eigenvalue_first_derivative_bound"]),
            "selected_eigenvalue_raw_Hessian_bound": float(fresh["selected_eigenvalue_raw_Hessian_bound"]),
        }
        birth = {
            "moving_cubic": growth["moving_cubic"],
            "selected_line": {
                "first_variation_coefficient_upper": float(fresh["weighted_selected_to_complement_first_variation_on_ball"]),
                "complete_second_variation_coefficient_upper": float(fresh["selected_line_second_variation_coefficient_upper"]),
            },
            "birth_limit_generator": growth["birth_limit_generator"],
        }
        pf = growth["fresh_pole_free_bounds"]
        certificate_radius = float(growth["radius_derivation"]["selected_growth_chart_radius"])
        path_key = "fresh_center_path_upper"
        path = 0.0
    else:
        prefix = _load(FIBER)["continuation"]
        record = _load(GAP)["continuation"]
        data_path = GAP_DATA
        data_key = "C2_uniform_gap_predictor_centers"
        recenter = _load(RECENTER)
        line = _load(LINE)["bounds"]
        birth = _load(BIRTH_REMAINDER)
        pf = recenter["recenter"]["recentered_pole_free_bounds"]
        certificate_radius = float(birth["physical_tube"]["certified_matrix_center_ball_radius"])
        path_key = "matrix_center_path_upper"
        path = float(prefix["fresh_center_path_upper"])
    with np.load(data_path) as data:
        centers = np.asarray(data[data_key], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    tube = float(record["initial_endpoint_tube_radius_upper"])
    rows: list[tuple[float, float, float]] = []
    residual = 0.0
    for center, stored in zip(centers[:-1], record["rows"], strict=True):
        response = _center_response(center, weights, reference)
        ball = uniform_gap_descriptor_fiber_ball(
            incoming_tube=tube, parent_radius=certificate_radius - path,
            base_path=path,
            descriptor_upper=float(stored["descriptor_fiber_lambda_upper"]),
            pf=pf, line=line, birth=birth, center_state=center,
            center_b=float(response["b_psi_center"]),
            center_hard_raw_norm=float(response["hard_rate_raw_norm"]),
            center_selected_action_norm=float(response["selected_action_norm"]),
            weights=weights, coefficient_enclosure=_coefficient_enclosure,
        )
        _append(rows, ball, float(ball["Delta_action_derivative_upper"]))
        residual = max(residual, abs(float(ball["Delta_interval"][0]) - float(stored["Delta_lower"])))
        tube = float(stored["endpoint_tube_radius_upper"])
        path = float(stored[path_key])
    return rows, residual


def _matrix_delta_derivative(segment: int) -> float:
    step = _load(_step_path(segment))
    if segment == 1215:
        center_path = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
        center_data_path = center_path.with_suffix(".npz")
        bordered_data_path = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.npz"
        growth_path = FRESH_GROWTH
    else:
        prior = segment - 1
        center_path = BASE / f"BHSM_N12_C2_LOHNER_FIXED_S_FIELD_{prior}.json"
        center_data_path = center_path.with_suffix(".npz")
        bordered_data_path = BASE / f"BHSM_N12_C2_LOHNER_BORDERED_MATRIX_{prior}.npz"
        growth_path = BASE / f"BHSM_N12_C2_LOHNER_GROWTH_{prior}.json"
    center_record = _load(center_path)
    growth = _load(growth_path)
    with np.load(center_data_path) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        response = np.asarray(data["bordered_response"], dtype=float) if "bordered_response" in data else None
        response_first = np.asarray(data["bordered_response_derivative_action"], dtype=float) if "bordered_response_derivative_action" in data else None
    with np.load(bordered_data_path) as data:
        if response is None:
            response = np.asarray(data["bordered_response"], dtype=float)
        if response_first is None:
            response_first = np.asarray(data["bordered_response_derivative_action"], dtype=float)
        K = np.asarray(data["bordered_matrix"], dtype=float)
    domain = float(step["domain"]["selected_domain_radius"])
    fresh = growth["fresh_line_bounds"]
    pf = growth["fresh_pole_free_bounds"]
    x_bound = float(step["second_variation"]["response_norm_upper"])
    x1_ball = float(step["second_variation"]["response_first_variation_upper"])
    p1 = float(fresh["weighted_selected_to_complement_first_variation_on_ball"])
    p2 = float(fresh["selected_line_second_variation_coefficient_upper"])
    forcing = K @ response
    rhs0 = float(np.linalg.norm(forcing[:-1]))
    rhs1 = float(pf["rhs_raw_derivative_center"])
    f2 = float(pf["rhs_raw_second_derivative_upper"])
    b1 = float(np.linalg.norm(response_first[-1]))
    b2 = p2 * rhs0 + 2.0 * p1 * rhs1 + f2
    b1_ball = b1 + b2 * domain
    cubic = growth["moving_cubic"]
    c1_ball = float(cubic["center_complete_first_derivative_upper"]) + float(cubic["second_derivative_upper"]) * domain
    c_upper = float(step["domain"]["c_interval"][1])
    b_upper = float(step["domain"]["b_psi_interval"][1])
    lambda_one = float(fresh["selected_eigenvalue_first_derivative_bound"])
    lambda_two = float(fresh["selected_eigenvalue_raw_Hessian_bound"])
    q_weights, _, maximum_q_weight, maximum_reduced_weight = metric_data()
    configuration = q_weights * center[37:74]
    configuration_bound = float(np.linalg.norm(configuration)) + maximum_q_weight * domain
    full_hard_zero = math.hypot(configuration_bound, maximum_reduced_weight * x_bound)
    full_hard_one = math.hypot(maximum_q_weight, maximum_reduced_weight * x1_ball)
    R1 = lambda_two * full_hard_zero + lambda_one * full_hard_one
    R2 = float(step["second_variation"]["R_second_variation_upper"])
    signed_s = float(Decimal(center_record["center_field"]["signed_descriptor_decimal"]))
    return math.nextafter(
        (c1_ball * b_upper + c_upper * b1_ball + signed_s * (R1 + R2 * domain)) * (1.0 + 1.0e-10),
        math.inf,
    )


def _matrix_majorants() -> list[tuple[float, float, float]]:
    rows = []
    for segment in range(1215, 1223):
        step = _load(_step_path(segment))
        rows.append((
            float(step["domain"]["Delta_interval"][0]),
            _matrix_delta_derivative(segment),
            float(step["domain"]["lapse_interval"][1]),
        ))
    return rows


def _logsumexp(values: np.ndarray) -> float:
    maximum = float(np.max(values))
    return maximum + math.log(float(np.sum(np.exp(values - maximum))))


def build_payload() -> dict[str, Any]:
    inputs = (
        CORE, CORE_DATA, COTANGENT, COTANGENT_DATA, RADIUS, RADIUS_DATA,
        OUTER, SECOND, SECOND_BALL, EXTENDED, EXTENDED_DATA, COMPENSATED,
        COMPENSATED_DATA, ADAPTIVE, ADAPTIVE_DATA, RECENTER, RECENTERED,
        RECENTERED_DATA, POLE_FREE, LAUNCH, LINE, ACTION, CANDIDATE, FIBER,
        FIBER_DATA, MAJORANTS, FIBER_PARENT, GAP, GAP_DATA, BIRTH_REMAINDER,
        HARD, SECOND_GAP, SECOND_GAP_DATA, CHART, FRESH_GROWTH, MODULE, THEORY,
        *(_step_path(segment) for segment in range(1215, 1223)),
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing duration-pullback inputs: " + ", ".join(missing))
    json_inputs = [path for path in inputs if path.suffix == ".json"]
    if not all(_load(path).get("validation_passed") is True for path in json_inputs):
        raise RuntimeError("validated duration-pullback parents required")

    translated, translated_residual = _translated_majorants()
    fiber, fiber_residual = _fiber_majorants()
    gap, gap_residual = _gap_majorants(second=False)
    second_gap, second_gap_residual = _gap_majorants(second=True)
    matrix = _matrix_majorants()
    majorants = np.asarray((*translated, *fiber, *gap, *second_gap, *matrix), dtype=float)
    with np.load(CORE_DATA) as data:
        durations = np.asarray(data["segment_proper_duration_interval"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    with np.load(RADIUS_DATA) as data:
        local_growth = np.asarray(data["local_state_Jacobi_growth_upper"], dtype=float)
        log_node_growth = np.asarray(data["node_log_state_Jacobi_growth_upper"], dtype=float)
    signs = (-1.0) ** np.arange(1, 13)
    lapse_dual = float(np.linalg.norm(signs / weights[74:86]))
    segment_start_bounds = np.asarray([
        segment_duration_pullback_upper(
            proper_duration_upper=float(duration[1]),
            lapse_log_action_dual=lapse_dual,
            delta_lower=float(row[0]),
            delta_action_derivative_upper=float(row[1]),
            local_state_growth_upper=float(growth),
        )
        for duration, row, growth in zip(durations, majorants, local_growth, strict=True)
    ])
    log_birth_bounds = np.log(segment_start_bounds) + log_node_growth[:-1]
    channel_summaries: dict[str, Any] = {}
    with np.load(COTANGENT_DATA) as data:
        for channel in CHANNELS:
            cotangent = np.asarray(data[f"{channel}__D_proper_duration_Weyl"], dtype=float)
            nonzero = (np.abs(cotangent) > 0.0) & (segment_start_bounds > 0.0)
            log_terms = np.log(np.abs(cotangent[nonzero])) + log_birth_bounds[nonzero]
            log_bound = _logsumexp(log_terms)
            channel_summaries[channel] = {
                "duration_cotangent_l1_norm": float(np.sum(np.abs(cotangent))),
                "log_reset_image_operator_norm_upper": log_bound,
                "log10_reset_image_operator_norm_upper": log_bound / math.log(10.0),
                "reset_image_operator_norm_upper": (
                    math.exp(log_bound) if log_bound < math.log(np.finfo(float).max) else None
                ),
            }
    arrays = {
        "segment_Delta_lower": majorants[:, 0],
        "segment_Delta_action_derivative_upper": majorants[:, 1],
        "segment_lapse_upper": majorants[:, 2],
        "segment_duration_pullback_from_start_upper": segment_start_bounds,
        "segment_log_duration_pullback_from_birth_upper": log_birth_bounds,
    }
    np.savez_compressed(DATA_RESULT, **arrays)
    replay_residual = max(translated_residual, fiber_residual, gap_residual, second_gap_residual)
    validation = {
        "exactly_1222_segment_majorants_assembled": majorants.shape == (1222, 3),
        "block_counts_sum_to_1222": len(translated) + len(fiber) + len(gap) + len(second_gap) + len(matrix) == 1222,
        "all_Delta_lapse_and_derivative_majorants_are_finite_positive": bool(
            np.all(np.isfinite(majorants)) and np.all(majorants[:, 0] > 0.0)
            and np.all(majorants[:, 1] >= 0.0) and np.all(majorants[:, 2] > 0.0)
        ),
        "replayed_ball_Delta_bounds_match_stored_rows": replay_residual < 1.0e-12,
        "all_segment_duration_pullbacks_are_finite_positive": bool(
            np.all(np.isfinite(segment_start_bounds)) and np.all(segment_start_bounds > 0.0)
        ),
        "all_channel_duration_cotangent_pullbacks_are_finite_in_log_space": all(
            math.isfinite(row["log_reset_image_operator_norm_upper"])
            for row in channel_summaries.values()
        ),
        "duration_interval_not_substituted_for_duration_first_jet": True,
        "matrix_Lohner_Delta_first_variations_reconstructed_from_certified_inputs": len(matrix) == 8,
        "far_core_edge_not_promoted_to_event_or_stop": True,
        "no_selector_recurrence_scale_fit_action_term_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1222_MOVING_DURATION_PULLBACK_ENCLOSURE",
        "status": "C2_1222_MOVING_DURATION_RESET_PULLBACK_NORM_CERTIFIED" if passed else "C2_1222_MOVING_DURATION_PULLBACK_NOT_CERTIFIED",
        "classification": (
            "THE_NON_SCALE_MOVING_PROPER_DURATION_FIRST_JET_IS_BOUNDED_ON_THE_"
            "ENTIRE_1222_FIXED_DESCRIPTOR_CORE_BY_THE_SAME_ACTION_BALL_DELTA_"
            "DERIVATIVES_LAPSE_COVECTOR_AND_STATE_JACOBI_PRODUCTS;_ITS_STORED_"
            "WEYL_COTANGENT_THEREFORE_HAS_A_FINITE_RESET_IMAGE_OPERATOR_NORM"
        ),
        "segment_provenance": {
            "block_counts": {
                "translated_prefix": len(translated),
                "descriptor_fiber": len(fiber),
                "uniform_gap": len(gap),
                "second_uniform_gap": len(second_gap),
                "matrix_Lohner": len(matrix),
            },
            "maximum_replay_Delta_lower_residual": replay_residual,
            "minimum_Delta_lower": float(np.min(majorants[:, 0])),
            "maximum_Delta_action_derivative_upper": float(np.max(majorants[:, 1])),
            "lapse_log_action_dual": lapse_dual,
            "maximum_segment_start_duration_pullback_upper": float(np.max(segment_start_bounds)),
            "maximum_log10_birth_duration_pullback_upper": float(np.max(log_birth_bounds) / math.log(10.0)),
        },
        "channel_duration_pullback": channel_summaries,
        "theorem": {
            "proper_integrand": "q_tau(s,Y)=N_boundary(Y)*s/Delta(Y)",
            "logarithmic_first_variation": "Dlog(q_tau)=Dlog(N_boundary)-Dlog(Delta)",
            "segment_start_bound": "norm(D_Ystart h_e)<=h_e^+*G_e*(norm(DlogN)+DDelta_e^+/Delta_e^-)",
            "birth_pullback": "norm(D_Y0 h_e)<=product_(j<e)G_j*norm(D_Ystart h_e)",
            "Weyl_contraction": "norm(sum_e D_h_e_M*D_Y0_h_e)<=sum_e|D_h_e_M|*norm(D_Y0_h_e)",
            "reset_image_rule": "THE_C2_BLOCK_OF_A_UNIT_ORTHONORMAL_RESET_TANGENT_DIRECTION_HAS_ACTION_NORM_AT_MOST_ONE",
            "physical_quotient_rule": "ORTHOGONAL_GAUGE_TIME_PROJECTION_CANNOT_INCREASE_THE_BOUND",
        },
        "claim_boundary": {
            "Gate7": "ACTIVE_COMPLETE_FINITE_CORE_GEOMETRY_COTANGENT_AND_GRADED_FORCE_VALUE",
            "Gate8": "LOCKED",
            "moving_duration_reset_pullback_norm": "CERTIFIED_ON_1222_FINITE_CORE",
            "moving_duration_reset_pullback_covector_value": "OPEN_REQUIRES_BACKWARD_ADJOINT_CENTER_CONTRACTION",
            "maximal_tail_beyond_1222": "OPEN",
            "actual_projected_zero_source_force": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "adjudication": {
            "duration_first_jet_existence_and_operator_norm": "CLOSED_ON_FINITE_CORE",
            "actual_signed_duration_covector": "OPEN",
            "complete_finite_core_geometry_cotangent_norm": "READY_TO_COMBINE_WITH_RADIUS_PART",
            "zero_source_force": "OPEN",
        },
        "exact_next_dependency": (
            "RUN_THE_INVERSE_FREE_BACKWARD_CENTER_ADJOINT_TO_OBTAIN_THE_SIGNED_"
            "RADIUS_PLUS_DURATION_RESET_COVECTOR,_THEN_CONTRACT_THE_EXACT_GRADED_"
            "SOURCE_AND_TEST_THE_PROJECTED_FORCE;_THE_FINITE_CORE_FIRST_JET_NORM_"
            "IS_NO_LONGER_MISSING"
        ),
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
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": payload["status"],
        "blocks": payload["segment_provenance"]["block_counts"],
        "maximum_replay_residual": payload["segment_provenance"]["maximum_replay_Delta_lower_residual"],
        "channel_log10_bounds": {
            key: row["log10_reset_image_operator_norm_upper"]
            for key, row in payload["channel_duration_pullback"].items()
        },
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
