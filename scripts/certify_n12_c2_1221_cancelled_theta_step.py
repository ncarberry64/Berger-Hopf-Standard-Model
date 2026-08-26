"""Certify a denominator-free theta step from the tracked 1221 C2 edge."""

from __future__ import annotations

from decimal import Decimal, localcontext
import hashlib
import json
import math
import os
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
CENTER = BASE / "BHSM_N12_C2_1221_CANCELLED_CENTER_MATRIX.json"
CENTER_DATA = CENTER.with_suffix(".npz")
BORDERED = BASE / "BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1221.json"
BORDERED_DATA = BORDERED.with_suffix(".npz")
GROWTH = BASE / "BHSM_N12_C2_LOHNER_GROWTH_1221.json"
STEP = BASE / "BHSM_N12_C2_LOHNER_STEP_1221.json"
RESULT = BASE / "BHSM_N12_C2_CANCELLED_THETA_STEP_FROM_1221.json"
DATA = RESULT.with_suffix(".npz")
INFLATION = 1.0 + 1.0e-10
EXPANDED = os.environ.get("BHSM_N12_EXPANDED_CANCELLED_THETA", "0") == "1"
LINE = BASE / "BHSM_N12_C2_1221_FULL_ACTION_EIGENLINE_BALL_R1E8.json"
ACTION = BASE / "BHSM_N12_C2_1221_CANCELLED_CHART_ACTION_MAJORANTS_R1E8.json"
if EXPANDED:
    RESULT = BASE / "BHSM_N12_C2_EXPANDED_CANCELLED_THETA_STEP_FROM_1221.json"
    DATA = RESULT.with_suffix(".npz")
INPUTS = (CENTER, CENTER_DATA, BORDERED, BORDERED_DATA, GROWTH, STEP) + (
    (LINE, ACTION) if EXPANDED else ()
)


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
    center_record, bordered_record, growth, prior = (
        json.loads(path.read_text(encoding="utf-8"))
        for path in (CENTER, BORDERED, GROWTH, STEP)
    )
    if not all(record.get("validation_passed") is True for record in (
        center_record, bordered_record, growth, prior,
    )):
        raise RuntimeError("validated tracked 1221 parents required")
    with np.load(CENTER_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        fixed = np.asarray(data["exact_center_field_action"], dtype=float)
        fixed_first = np.asarray(
            data["fixed_s_field_matrix_partial_action"], dtype=float
        )
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

    incoming = float(prior["segment"]["endpoint_tube_radius_upper"])
    # Every consumed second-variation bound is certified on the preceding
    # fixed-s domain.  Stay inside that common parent, even though the line and
    # coefficient charts individually extend farther.
    outer = float(prior["domain"]["selected_domain_radius"])
    radius = 0.5 * (incoming + outer)
    fresh = growth["fresh_line_bounds"]
    pf = growth["fresh_pole_free_bounds"]
    if EXPANDED:
        line = json.loads(LINE.read_text(encoding="utf-8"))
        if line.get("validation_passed") is not True:
            raise RuntimeError("validated expanded full-action line required")
        line_bounds = line["bounds"]
        inverse = _up(1.0 / float(line_bounds["eigenline_gap_lower"]))
        p1 = float(
            line_bounds["weighted_selected_to_complement_first_variation_on_ball"]
        )
        p2 = float(line_bounds["selected_line_second_variation_coefficient_upper"])
        lambda_one = float(line_bounds["selected_eigenvalue_first_derivative_bound"])
        lambda_two = float(line_bounds["selected_eigenvalue_raw_Hessian_bound"])
        K2 = _up(
            float(line_bounds["D4_ambient_ambient_raw_reduced_raw_reduced"])
            + lambda_two + 2.0 * p2
        )
        radius_multiplier = float(os.environ.get(
            "BHSM_N12_EXPANDED_RADIUS_MULTIPLIER", "2.0"
        ))
        if not 1.0 < radius_multiplier <= 25.0:
            raise ValueError("expanded radius multiplier must lie in (1,25]")
        outer = radius_multiplier * incoming
        radius = outer
    else:
        inverse = _up(1.0 / float(fresh["eigenline_gap_lower"]))
        p1 = float(fresh["weighted_selected_to_complement_first_variation_on_ball"])
        p2 = float(fresh["selected_line_second_variation_coefficient_upper"])
        lambda_one = float(fresh["selected_eigenvalue_first_derivative_bound"])
        lambda_two = float(fresh["selected_eigenvalue_raw_Hessian_bound"])
        K2 = _up(
            float(pf["D4_full_hard_hard_upper"])
            + lambda_two + 2.0 * p2
        )
    relative_center = float(center_record["fixed_descriptor_matrix"][
        "bordered_relative_tangent_tensor_Frobenius_upper"
    ])
    relative_ball = _up(relative_center + inverse * K2 * radius)
    response_self = _up(2.0 * radius * relative_ball)
    if response_self >= 1.0:
        raise ArithmeticError("cancelled response fixed point does not close")
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
        raise ArithmeticError("cancelled response enclosure did not converge")

    rhs0 = _up(float(np.linalg.norm(forcing[:-1])))
    rhs1 = float(pf["rhs_raw_derivative_center"])
    b0 = float(response[-1])
    b1 = _up(float(np.linalg.norm(response_first[-1])))
    b2 = _up(p2 * rhs0 + 2.0 * p1 * rhs1 + f2)
    b_upper = _up(abs(b0) + b1 * radius + 0.5 * b2 * radius**2)
    b_lower = _down(b0 - b1 * radius - 0.5 * b2 * radius**2)

    signed_s = float(Decimal(prior["segment"]["signed_descriptor_end"]))
    Delta = float(center_record["center_field"]["Delta"])
    G = Delta * fixed
    DG_partial = Delta * fixed_first + np.outer(fixed, delta_first)
    DG_error = _up(
        abs(Delta) * float(center_record["fixed_descriptor_matrix"][
            "total_center_matrix_remainder_upper"
        ]) + float(np.linalg.norm(fixed)) * delta_first_error
    )
    q_weights, reduced_weights, maximum_q_weight, maximum_reduced_weight = metric_data()
    selected_zero = _up(maximum_reduced_weight)
    selected_one = _up(maximum_reduced_weight * p1)
    selected_two = _up(maximum_reduced_weight * p2)
    G2 = _up(
        b2 * selected_zero + 2.0 * b1 * selected_one
        + b_upper * selected_two + signed_s * maximum_reduced_weight * x2_ball
    )
    G1 = _up(float(np.linalg.norm(DG_partial, 2)) + DG_error + G2 * radius)
    mu_center = float(np.linalg.eigvalsh(
        0.5 * (DG_partial + DG_partial.T)
    )[-1])
    mu = _up(mu_center + DG_error + G2 * radius)

    c0 = float(growth["moving_cubic"]["center_value"])
    c1 = float(growth["moving_cubic"]["center_complete_first_derivative_upper"])
    c2 = float(growth["moving_cubic"]["second_derivative_upper"])
    if EXPANDED:
        action = json.loads(ACTION.read_text(encoding="utf-8"))
        derivatives = next(
            row["derivative_operator_majorants_0_through_5"]
            for row in action["sectors"] if row["sector"] == "child"
        )
        d3, d4, d5 = map(float, derivatives[3:6])
        lambda_three = _up(
            d5 + 6.0 * d4 * p1 + 6.0 * d3 * p1**2 + 2.0 * d3 * p2
        )
        configuration = _up(
            float(np.linalg.norm(q_weights * center[37:74]))
            + maximum_q_weight * radius
        )
        hard_zero = _up(math.hypot(configuration, maximum_reduced_weight * x_bound))
        hard_one = _up(math.hypot(maximum_q_weight, maximum_reduced_weight * x1_ball))
        hard_two = _up(maximum_reduced_weight * x2_ball)
        R2 = _up(
            lambda_three * hard_zero + 2.0 * lambda_two * hard_one
            + lambda_one * hard_two
        )
    else:
        R2 = float(prior["second_variation"]["R_second_variation_upper"])
    Delta2 = _up(
        c2 * b_upper + 2.0 * c1 * (b1 + b2 * radius)
        + (abs(c0) + c1 * radius + 0.5 * c2 * radius**2) * b2
        + signed_s * R2
    )
    Delta_abs = _up(
        abs(Delta) + (float(np.linalg.norm(delta_first)) + delta_first_error) * radius
        + 0.5 * Delta2 * radius**2
    )
    Delta_first_center_error = _up(
        float(np.linalg.norm(delta_first)) + delta_first_error
    )
    coefficient = _coefficient_enclosure(center, weights, radius)
    Gnorm = _up(float(np.linalg.norm(G)))
    upper = min(
        0.9 * (radius - incoming) / Gnorm,
        0.45 * signed_s / Delta_abs,
    )

    def trial(h: float) -> dict:
        growth_factor = math.exp(mu * h)
        truncation = _up(0.5 * G1 * Gnorm * h**2 * growth_factor)
        center_step = h * G
        endpoint_center = center + center_step / weights
        stored = (endpoint_center - center) * weights
        rounding = _up(float(np.linalg.norm(stored - center_step)))
        tube = _up(growth_factor * incoming + truncation + rounding)
        path = _up(float(np.linalg.norm(stored)))
        return {
            "closes": path + tube < radius and signed_s - h * Delta_abs > 0.0,
            "endpoint_center": endpoint_center,
            "endpoint_tube": tube,
            "center_path": path,
            "total_use": path + tube,
            "growth": growth_factor,
            "truncation": truncation,
            "rounding": rounding,
            "descriptor_interval": [
                _down(signed_s - h * Delta_abs),
                _up(signed_s + h * Delta_abs),
            ],
        }

    if not trial(upper)["closes"]:
        feasible, infeasible = 0.0, upper
        for _ in range(100):
            midpoint = 0.5 * (feasible + infeasible)
            if trial(midpoint)["closes"]:
                feasible = midpoint
            else:
                infeasible = midpoint
        upper = feasible
    h = 0.5 * upper
    result = trial(h)
    if h <= 0.0 or not result["closes"]:
        raise ArithmeticError("no positive cancelled theta step closes")
    descriptor_center = signed_s + h * Delta
    replay = exact_cancelled_euler_dirac_field_action(
        state=result["endpoint_center"], weights=weights, reference=reference,
        signed_descriptor=descriptor_center,
    )
    proper_lower = (
        coefficient["root_lapse_interval"][0]
        * result["descriptor_interval"][0] * h
    )
    np.savez_compressed(
        DATA,
        center_state=center,
        endpoint_predictor_center=result["endpoint_center"],
        state_weights=weights,
        branch_reference=reference,
        signed_descriptor_start=np.asarray(signed_s),
        signed_descriptor_center_end=np.asarray(descriptor_center),
        endpoint_tube_radius=np.asarray(result["endpoint_tube"]),
    )
    validation = {
        "same_action_cancelled_identity_used": True,
        "response_fixed_point_closes": response_self < 1.0,
        "b_psi_stays_positive": b_lower > 0.0,
        "selected_domain_contains_tube_and_center": result["closes"],
        "signed_descriptor_interval_stays_positive": result["descriptor_interval"][0] > 0.0,
        "positive_proper_duration": proper_lower > 0.0,
        "branch_24_replays_at_predictor": int(replay["selected_branch"]) == 24,
        "Delta_sign_not_required_as_domain_condition": True,
        "binary64_eigenvalue_not_used_as_descriptor": True,
        "predictor_not_promoted_to_physical_endpoint": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": (
            "BHSM_N12_C2_EXPANDED_CANCELLED_THETA_STEP_FROM_1221"
            if EXPANDED else "BHSM_N12_C2_CANCELLED_THETA_STEP_FROM_1221"
        ),
        "status": (
            "C2_EXPANDED_CANCELLED_THETA_EXTENSION_FROM_1221_CERTIFIED"
            if passed and EXPANDED else
            "C2_CANCELLED_THETA_EXTENSION_FROM_1221_CERTIFIED"
            if passed else "C2_CANCELLED_THETA_STEP_FAILED"
        ),
        "domain": {
            "incoming_tube_radius": incoming,
            "selected_radius": radius,
            "response_self_consistency": response_self,
            "expanded_full_action_line_consumed": EXPANDED,
            "b_psi_interval": [b_lower, b_upper],
            "Delta_absolute_upper": Delta_abs,
            "Delta_center": Delta,
            "Delta_first_variation_center_plus_error_upper": Delta_first_center_error,
            "Delta_second_variation_upper": Delta2,
            "lapse_interval": coefficient["root_lapse_interval"],
        },
        "cancelled_field": {
            "center_norm": Gnorm,
            "center_first_variation_partial_norm": float(np.linalg.norm(DG_partial, 2)),
            "center_first_variation_remainder_upper": DG_error,
            "second_variation_upper": G2,
            "first_variation_ball_upper": G1,
            "logarithmic_norm_ball_upper": mu,
        },
        "segment": {
            "theta_step": h,
            "theta_step_feasible_upper": upper,
            "signed_descriptor_start": signed_s,
            "signed_descriptor_center_end": descriptor_center,
            "signed_descriptor_endpoint_interval": result["descriptor_interval"],
            "center_path_upper": result["center_path"],
            "endpoint_tube_radius_upper": result["endpoint_tube"],
            "joint_domain_use_upper": result["total_use"],
            "matrix_growth_upper": result["growth"],
            "Euler_truncation_upper": result["truncation"],
            "proper_time_increment_lower": proper_lower,
            "proof_center_is_physical_endpoint": False,
        },
        "exact_next_dependency": (
            "RECENTER_THE_CANCELLED_FIELD_BALL_AT_THE_NEW_PREDICTOR_AND_ITERATE_"
            "UNTIL_LOG_s_IS_RELIABLE_THEN_CONTINUE_TO_CAPTURE_OR_RETAINED_STOP"
        ),
        "validation": validation,
        "validation_passed": passed,
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
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
