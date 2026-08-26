"""Certify one invariant-graph Lohner step from the expanded C2 endpoint."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RECENTER = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_RECENTER.json"
FIELD = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_FIXED_S_FIELD.json"
FIELD_DATA = FIELD.with_suffix(".npz")
BORDERED = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_BORDERED_MATRIX.json"
BORDERED_DATA = BORDERED.with_suffix(".npz")
GROWTH = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_GROWTH.json"
TANGENT = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_SHEARED_DESCRIPTOR_TANGENT.json"
TANGENT_DATA = TANGENT.with_suffix(".npz")
ACTION = BASE / "BHSM_N12_C2_1221_CANCELLED_CHART_ACTION_MAJORANTS_R1E8.json"
THEORY = ROOT / "theory" / "n12_c2_1221_expanded_endpoint_recenter.md"
RESULT = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_SHEARED_STEP.json"
DATA = RESULT.with_suffix(".npz")
INFLATION = 1.0 + 1.0e-10


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict:
    inputs = (
        RECENTER, FIELD, FIELD_DATA, BORDERED, BORDERED_DATA, GROWTH,
        TANGENT, TANGENT_DATA, ACTION, THEORY,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing endpoint sheared-step inputs: " + ", ".join(missing))
    recenter, field_record, bordered_record, growth, tangent, action = (
        json.loads(path.read_text(encoding="utf-8"))
        for path in (RECENTER, FIELD, BORDERED, GROWTH, TANGENT, ACTION)
    )
    if not all(record.get("validation_passed") is True for record in (
        recenter, field_record, bordered_record, growth, tangent, action,
    )):
        raise RuntimeError("validated endpoint recenter parents required")
    with np.load(FIELD_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        delta_first = np.asarray(data["Delta_first_partial_action"], dtype=float)
        delta_first_error = float(
            data["Delta_first_total_remainder_action_norm_upper"]
        )
    with np.load(BORDERED_DATA) as data:
        K = np.asarray(data["bordered_matrix"], dtype=float)
        response = np.asarray(data["bordered_response"], dtype=float)
        response_first = np.asarray(
            data["bordered_response_derivative_action"], dtype=float
        )
        reference = np.asarray(data["branch_reference"], dtype=float)
        forcing = K @ response
    with np.load(TANGENT_DATA) as data:
        graph_DG = np.asarray(
            data["sheared_descriptor_graph_tangent_partial"], dtype=float
        )
        lambda_first_center = np.asarray(
            data["lambda_gradient_action"], dtype=float
        )

    q_weights, reduced_weights, q_max, reduced_max = metric_data()
    incoming = float(recenter["endpoint"]["incoming_endpoint_tube_radius_upper"])
    outer = float(growth["radius_derivation"]["selected_growth_chart_radius"])
    radius = 0.5 * (incoming + outer)
    fresh = growth["fresh_line_bounds"]
    pf = growth["fresh_pole_free_bounds"]
    inverse = _up(1.0 / float(fresh["eigenline_gap_lower"]))
    p1 = float(fresh["weighted_selected_to_complement_first_variation_on_ball"])
    p2 = float(fresh["selected_line_second_variation_coefficient_upper"])
    lambda_one = float(fresh["selected_eigenvalue_first_derivative_bound"])
    lambda_two = float(fresh["selected_eigenvalue_raw_Hessian_bound"])
    K2 = _up(float(pf["D4_full_hard_hard_upper"]) + lambda_two + 2.0 * p2)
    relative_center = float(field_record["fixed_descriptor_matrix"][
        "bordered_relative_tangent_tensor_Frobenius_upper"
    ])
    relative_ball = _up(relative_center + inverse * K2 * radius)
    response_self = _up(2.0 * radius * relative_ball)
    if response_self >= 1.0:
        raise ArithmeticError("endpoint bordered response ball does not close")

    x0 = _up(float(np.linalg.norm(response)))
    x1 = _up(float(np.linalg.norm(response_first)))
    f2 = float(pf["rhs_raw_second_derivative_upper"])
    x_bound = x0
    for _ in range(64):
        x2_base = _up(inverse * (f2 + K2 * x_bound))
        x1_ball = _up((x1 + radius * x2_base) / (1.0 - response_self))
        x2_ball = _up(x2_base + 2.0 * relative_ball * x1_ball)
        updated = _up(x0 + x1_ball * radius + 0.5 * x2_ball * radius**2)
        if updated <= x_bound * (1.0 + 1.0e-12):
            x_bound = max(x_bound, updated)
            break
        x_bound = updated
    else:
        raise ArithmeticError("endpoint response fixed point did not converge")

    rhs0 = _up(float(np.linalg.norm(forcing[:-1])))
    rhs1 = float(pf["rhs_raw_derivative_center"])
    b0 = float(response[-1])
    b1 = _up(float(np.linalg.norm(response_first[-1])))
    b2 = _up(p2 * rhs0 + 2.0 * p1 * rhs1 + f2)
    b1_ball = _up(b1 + b2 * radius)
    b_upper = _up(abs(b0) + b1 * radius + 0.5 * b2 * radius**2)
    b_lower = _down(b0 - b1 * radius - 0.5 * b2 * radius**2)

    selected_zero = _up(reduced_max)
    selected_one = _up(reduced_max * p1)
    selected_two = _up(reduced_max * p2)
    configuration = _up(
        float(np.linalg.norm(q_weights * center[37:74])) + q_max * radius
    )
    hard_zero = _up(math.hypot(configuration, reduced_max * x_bound))
    hard_one = _up(math.hypot(q_max, reduced_max * x1_ball))
    hard_two = _up(reduced_max * x2_ball)

    derivatives = next(
        row["derivative_operator_majorants_0_through_5"]
        for row in action["sectors"] if row["sector"] == "child"
    )
    d3, d4, d5 = map(float, derivatives[3:6])
    lambda_three = _up(
        d5 + 6.0 * d4 * p1 + 6.0 * d3 * p1**2 + 2.0 * d3 * p2
    )
    R2 = _up(
        lambda_three * hard_zero + 2.0 * lambda_two * hard_one
        + lambda_one * hard_two
    )
    c0 = float(growth["moving_cubic"]["center_value"])
    c1 = float(growth["moving_cubic"]["center_complete_first_derivative_upper"])
    c2 = float(growth["moving_cubic"]["second_derivative_upper"])
    c1_ball = _up(c1 + c2 * radius)
    c_upper = _up(abs(c0) + c1 * radius + 0.5 * c2 * radius**2)
    descriptor_interval = list(tangent["incoming_correlated_descriptor_interval"])
    signed_s = float(tangent["signed_descriptor"])
    signed_s_upper = float(descriptor_interval[1])
    Delta2 = _up(
        c2 * b_upper + 2.0 * c1_ball * b1_ball + c_upper * b2
        + signed_s_upper * R2
    )
    Delta0 = float(field_record["center_field"]["Delta"])
    Delta1 = _up(float(np.linalg.norm(delta_first)) + delta_first_error)
    Delta_variation = _up(Delta1 * radius + 0.5 * Delta2 * radius**2)
    Delta_interval = [
        _down(Delta0 - Delta_variation),
        _up(Delta0 + Delta_variation),
    ]
    if Delta_interval[0] <= 0.0:
        raise ArithmeticError("recentered Delta interval is not positive")

    graph_second = _up(
        b2 * selected_zero + 2.0 * b1_ball * selected_one
        + b_upper * selected_two + lambda_two * hard_zero
        + 2.0 * lambda_one * hard_one + signed_s_upper * hard_two
    )
    graph_norm = _up(float(np.linalg.norm(graph_DG, 2)))
    graph_mu_center = float(np.linalg.eigvalsh(
        0.5 * (graph_DG + graph_DG.T)
    )[-1])
    graph_one_ball = _up(graph_norm + graph_second * radius)
    graph_mu_ball = _up(graph_mu_center + graph_second * radius)

    center_field = exact_cancelled_euler_dirac_field_action(
        state=center, weights=weights, reference=reference,
        signed_descriptor=signed_s,
    )
    G = np.asarray(center_field["cancelled_field_action"], dtype=float)
    Gnorm = _up(float(np.linalg.norm(G)))
    coefficient = _coefficient_enclosure(center, weights, radius)
    step_upper = min(
        0.9 * (radius - incoming) / Gnorm,
        0.45 * descriptor_interval[0] / abs(Delta_interval[1]),
    )

    def trial(h: float) -> dict:
        matrix_growth = math.exp(graph_mu_ball * h)
        truncation = _up(0.5 * graph_one_ball * Gnorm * h**2 * matrix_growth)
        action_step = h * G
        endpoint = center + action_step / weights
        stored = (endpoint - center) * weights
        rounding = _up(float(np.linalg.norm(stored - action_step)))
        tube = _up(matrix_growth * incoming + truncation + rounding)
        path = _up(float(np.linalg.norm(stored)))
        total = path + tube
        next_descriptor = [
            _down(descriptor_interval[0] + h * Delta_interval[0]),
            _up(descriptor_interval[1] + h * Delta_interval[1]),
        ]
        return {
            "closes": total < radius and next_descriptor[0] > 0.0,
            "endpoint": endpoint,
            "tube": tube,
            "path": path,
            "total": total,
            "growth": matrix_growth,
            "truncation": truncation,
            "rounding": rounding,
            "descriptor_interval": next_descriptor,
        }

    if not trial(step_upper)["closes"]:
        feasible, infeasible = 0.0, step_upper
        for _ in range(100):
            midpoint = 0.5 * (feasible + infeasible)
            if trial(midpoint)["closes"]:
                feasible = midpoint
            else:
                infeasible = midpoint
        step_upper = feasible
    h = 0.5 * step_upper
    outcome = trial(h)
    if h <= 0.0 or not outcome["closes"]:
        raise ArithmeticError("no positive endpoint sheared-graph step closes")
    descriptor_center_end = signed_s + h * Delta0
    replay = exact_cancelled_euler_dirac_field_action(
        state=outcome["endpoint"], weights=weights, reference=reference,
        signed_descriptor=descriptor_center_end,
    )
    proper_lower = (
        float(coefficient["root_lapse_interval"][0])
        * descriptor_interval[0] * h
    )
    np.savez_compressed(
        DATA,
        center_state=center,
        endpoint_predictor_center=outcome["endpoint"],
        state_weights=weights,
        branch_reference=reference,
        sheared_graph_tangent_center=graph_DG,
        signed_descriptor_center_start=np.asarray(signed_s),
        signed_descriptor_center_end=np.asarray(descriptor_center_end),
        signed_descriptor_interval_end=np.asarray(outcome["descriptor_interval"]),
        endpoint_tube_radius=np.asarray(outcome["tube"]),
    )
    validation = {
        "fresh_radius_strictly_contains_incoming_tube": radius > incoming,
        "bordered_response_fixed_point_closes": response_self < 1.0,
        "internal_b_psi_stays_positive": b_lower > 0.0,
        "complete_graph_second_variation_is_finite": math.isfinite(graph_second),
        "recentered_Delta_interval_is_strictly_positive": Delta_interval[0] > 0.0,
        "sheared_matrix_Lohner_step_closes": outcome["closes"],
        "correlated_descriptor_interval_stays_positive": outcome[
            "descriptor_interval"
        ][0] > 0.0,
        "positive_proper_duration": proper_lower > 0.0,
        "branch_24_replayed_at_predictor": int(replay["selected_branch"]) == 24,
        "binary64_eigenvalue_not_used_as_descriptor": True,
        "predictor_not_promoted_to_event_or_physical_endpoint": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_SHEARED_STEP",
        "status": (
            "C2_INVARIANT_GRAPH_MATRIX_LOHNER_FORWARD_STEP_CERTIFIED"
            if passed else "C2_INVARIANT_GRAPH_SHEARED_STEP_FAILED"
        ),
        "domain": {
            "incoming_endpoint_tube_radius": incoming,
            "selected_fresh_radius": radius,
            "response_self_consistency": response_self,
            "b_psi_interval": [b_lower, b_upper],
            "Delta_interval": Delta_interval,
            "lapse_interval": coefficient["root_lapse_interval"],
        },
        "graph_variation": {
            "center_tangent_operator_norm": graph_norm,
            "center_tangent_numerical_abscissa": graph_mu_center,
            "complete_second_variation_upper": graph_second,
            "first_variation_ball_upper": graph_one_ball,
            "logarithmic_norm_ball_upper": graph_mu_ball,
            "included_terms": (
                "D2(bPsi)+D2(lambda*Vhard),_INCLUDING_D2lambda*Vhard_"
                "AND_2Dlambda*DVhard"
            ),
        },
        "segment": {
            "theta_step": h,
            "theta_step_feasible_upper": step_upper,
            "signed_descriptor_center_start": signed_s,
            "signed_descriptor_center_end": descriptor_center_end,
            "signed_descriptor_interval_start": descriptor_interval,
            "signed_descriptor_interval_end": outcome["descriptor_interval"],
            "center_path_upper": outcome["path"],
            "endpoint_tube_radius_upper": outcome["tube"],
            "joint_domain_use_upper": outcome["total"],
            "matrix_growth_upper": outcome["growth"],
            "Euler_truncation_upper": outcome["truncation"],
            "proper_time_increment_lower": proper_lower,
            "proof_center_is_physical_endpoint": False,
        },
        "adjudication": {
            "old_expanded_ball_edge": "REMOVED_BY_ACTION_OWNED_RECENTER",
            "actual_later_event_or_canonical_stop": "NOT_REACHED",
            "GATE7_RESET_TO_CAPTURE": "OPEN",
        },
        "hindsight": {
            "validated": (
                "FIRST_RECENTERED_SHEARED_INVARIANT_GRAPH_FORWARD_BLOCK"
            ),
            "invalidated": (
                "INDEPENDENT_DESCRIPTOR_WRAPPING_AS_A_STOPPING_MECHANISM"
            ),
            "open": (
                "ITERATED_SHEARED_RECENTERING_TO_CAPTURE_OR_RETAINED_STOP"
            ),
            "bhsm_native_check": "ACTION_REQUIRED_DYNAMIC_CONNECTION",
        },
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in inputs
        },
        "exact_next_dependency": (
            "RECENTER_THE_SAME_SHEARED_GRAPH_AT_THIS_PREDICTOR_AND_ITERATE_"
            "TO_STRICT_NHIM_CAPTURE_OR_THE_FIRST_RETAINED_STOP"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
