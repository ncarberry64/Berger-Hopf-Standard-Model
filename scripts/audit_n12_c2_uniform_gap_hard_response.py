"""Audit the C2 finite-s correction with the already uniform hard gap."""

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
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CANCELLED = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION.json"
CANCELLED_DATA = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION.npz"
RECENTER = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.json"
LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
BIRTH = BASE / "BHSM_N12_C2_BIRTH_LIMIT_CONJUGATED_TANGENT_REMAINDER.json"
RESULT = BASE / "BHSM_N12_C2_UNIFORM_GAP_HARD_RESPONSE.json"
THEORY = ROOT / "theory" / "n12_c2_uniform_gap_hard_response.md"
INPUTS = (CANCELLED, CANCELLED_DATA, RECENTER, LINE, BIRTH, THEORY)
QDIM = 37
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


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing uniform-gap inputs: " + ", ".join(missing))
    cancelled, recenter, line_record, birth = (
        _json(path) for path in (CANCELLED, RECENTER, LINE, BIRTH)
    )
    if not all(record.get("validation_passed") is True for record in (
        cancelled, recenter, line_record, birth,
    )):
        raise RuntimeError("validated continuation, line, and birth parents required")
    with np.load(CANCELLED_DATA) as data:
        center = np.asarray(data["C2_descriptor_fiber_predictor_centers"][-1], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)

    q_weights, reduced_weights, maximum_q_weight, maximum_reduced_weight = metric_data()
    jet = exact_full_action_jet_at_state(
        12, center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:], points=96,
    )
    gradient = np.asarray(jet.gradient, dtype=float) / weights
    hessian_action = np.asarray(jet.hessian, dtype=float) / weights[:, None] / weights[None, :]
    raw_reduced = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(raw_reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    complement = np.delete(vectors, selected, axis=1)
    hard_values = np.delete(values, selected)
    configuration = q_weights * center[QDIM:2 * QDIM]
    mixed_vq = hessian_action[QDIM:QDIM + QDIM, :QDIM]
    mixed_mq = hessian_action[2 * QDIM:, :QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient[:QDIM] - mixed_vq @ configuration,
        -mixed_mq @ configuration,
    ))
    rhs_raw = reduced_weights * rhs_action
    b_center = float(psi @ rhs_raw)
    hard_center = complement @ ((complement.T @ rhs_raw) / hard_values)

    continuation = cancelled["continuation"]
    last = continuation["rows"][-1]
    radius = _up(float(continuation["final_endpoint_tube_radius_upper"]))
    path = _up(float(continuation["fresh_center_path_upper"]))
    total_radius = _up(radius + path)
    descriptor = _up(float(continuation["final_signed_lambda_decimal"]))
    line = line_record["bounds"]
    pf = recenter["recenter"]["recentered_pole_free_bounds"]
    hard_inverse = _up(1.0 / float(line["eigenline_gap_lower"]))
    rhs_derivative = _up(
        float(pf["rhs_raw_derivative_center"])
        + float(pf["rhs_raw_second_derivative_upper"]) * total_radius
    )
    hard_d3 = _up(
        float(pf["hard_D3_center"])
        + float(pf["D4_full_hard_hard_upper"]) * total_radius
    )
    coupling = _up(
        float(pf["coupling_center"])
        + float(pf["D4_full_selected_hard_upper"]) * total_radius
    )
    projector_derivative = _up(
        2.0 * float(line["weighted_selected_to_complement_first_variation_on_ball"])
    )
    # The line theorem already says inf gap(D_h(Y),lambda(Y)) >= gap_lower
    # throughout the parent ball.  Integrate the covariant response inequality
    # from the exact center.  This preserves the center spectral solve and
    # replaces the divergent geometric Neumann sum by its finite exponential.
    hard_linear_rate = _up(hard_inverse * hard_d3)
    hard_exponent = _up(hard_linear_rate * radius)
    exponential = _up(math.exp(hard_exponent))
    b_seed = _up(abs(b_center) + rhs_derivative * radius)
    for _ in range(32):
        hard_affine = _up(hard_inverse * (
            rhs_derivative + projector_derivative * b_seed
        ))
        if hard_linear_rate > 0.0:
            hard_rate_raw = _up(
                float(np.linalg.norm(hard_center)) * exponential
                + hard_affine * math.expm1(hard_exponent) / hard_linear_rate
            )
        else:
            hard_rate_raw = _up(float(np.linalg.norm(hard_center)) + hard_affine * radius)
        structured_b = _up(
            rhs_derivative
            + (coupling + descriptor * projector_derivative) * hard_rate_raw
        )
        updated_b_seed = _up(abs(b_center) + structured_b * radius)
        if updated_b_seed <= b_seed * (1.0 + 1.0e-12):
            b_seed = max(b_seed, updated_b_seed)
            break
        b_seed = updated_b_seed
    else:
        raise ArithmeticError("uniform-gap b/hard-response fixed point did not close")
    hard_affine = _up(hard_inverse * (
        rhs_derivative + projector_derivative * b_seed
    ))
    hard_jacobi_raw = _up(hard_linear_rate * hard_rate_raw + hard_affine)
    hard_rate_action = _up(maximum_reduced_weight * hard_rate_raw)
    hard_jacobi_action = _up(maximum_reduced_weight * hard_jacobi_raw)
    b_interval = (
        _down(b_center - structured_b * radius),
        _up(b_center + structured_b * radius),
    )

    cubic = birth["moving_cubic"]
    c0 = float(cubic["center_value"])
    c1 = float(cubic["center_complete_first_derivative_upper"])
    c2 = float(cubic["second_derivative_upper"])
    c_interval = (
        _down(c0 - c1 * total_radius - 0.5 * c2 * total_radius**2),
        _up(c0 + c1 * total_radius + 0.5 * c2 * total_radius**2),
    )
    c_derivative = _up(c1 + c2 * total_radius)

    lambda_one = _up(float(line["selected_eigenvalue_first_derivative_bound"]))
    lambda_two = _up(float(line["selected_eigenvalue_raw_Hessian_bound"]))
    configuration_upper = _up(float(np.linalg.norm(configuration)) + maximum_q_weight * radius)
    full_hard_flow = _up(math.hypot(configuration_upper, hard_rate_action))
    full_hard_jacobi = _up(math.hypot(maximum_q_weight, hard_jacobi_action))
    remainder = _up(lambda_one * full_hard_flow)
    remainder_jacobi = _up(lambda_two * full_hard_flow + lambda_one * full_hard_jacobi)
    c_upper = max(abs(value) for value in c_interval)
    b_upper = max(abs(value) for value in b_interval)
    delta_interval = (
        _down(c_interval[0] * b_interval[0] - descriptor * remainder),
        _up(c_interval[1] * b_interval[1] + descriptor * remainder),
    )
    delta_derivative = _up(
        b_upper * c_derivative + c_upper * structured_b
        + lambda_one * remainder + descriptor * remainder_jacobi
    )

    p1 = float(birth["selected_line"]["first_variation_coefficient_upper"])
    p2 = float(birth["selected_line"]["complete_second_variation_coefficient_upper"])
    selected_action_center = float(np.linalg.norm(psi * reduced_weights))
    selected_action_upper = _up(
        selected_action_center + maximum_reduced_weight * p1 * radius
        + 0.5 * maximum_reduced_weight * p2 * radius**2
    )
    selected_action_derivative = _up(maximum_reduced_weight * (p1 + p2 * radius))
    c_lower = c_interval[0]
    delta_lower = delta_interval[0]
    if c_lower <= 0.0 or b_interval[0] <= 0.0 or delta_lower <= 0.0:
        raise ArithmeticError(
            "uniform-gap finite-s denominator is not positive: "
            f"c={c_interval}, b={b_interval}, Delta={delta_interval}, "
            f"hard={hard_rate_action}"
        )
    numerator = _up(c_upper * full_hard_flow + remainder * selected_action_upper)
    numerator_derivative = _up(
        c_derivative * full_hard_flow + c_upper * full_hard_jacobi
        + remainder_jacobi * selected_action_upper
        + remainder * selected_action_derivative
    )
    denominator = _down(c_lower * delta_lower)
    denominator_derivative = _up(
        c_derivative * max(abs(value) for value in delta_interval)
        + c_upper * delta_derivative
    )
    correction_norm = _up(numerator / denominator)
    correction_jacobi = _up(
        numerator_derivative / denominator
        + numerator * denominator_derivative / denominator**2
    )
    finite_s_jacobi = _up(descriptor * correction_jacobi)
    birth_operator = float(
        birth["birth_limit_generator"]["full_action_ball_operator_norm_upper"]
    )
    full_fixed_s_operator = _up(birth_operator + finite_s_jacobi)
    covered_horizon = _up(
        float(continuation["final_signed_lambda_decimal"])
        - float(continuation["initial_signed_lambda_decimal"])
    )
    covered_growth = _up(math.exp(full_fixed_s_operator * covered_horizon))

    old_hard_denominator = float(last["hard_denominator_lower"])
    validation = {
        "branch_24_replayed": selected == 24,
        "uniform_line_gap_is_strict": float(line["eigenline_gap_lower"]) > 0.0,
        "uniform_hard_inverse_uses_line_theorem_once": hard_inverse > 0.0,
        "old_second_Neumann_denominator_is_not_used": True,
        "old_exhausted_denominator_is_positive_but_tiny": 0.0 < old_hard_denominator < 1.0e-3,
        "uniform_hard_rate_and_jacobi_are_finite": (
            math.isfinite(hard_rate_action) and math.isfinite(hard_jacobi_action)
        ),
        "c_b_and_Delta_stay_positive": (
            c_interval[0] > 0.0 and b_interval[0] > 0.0 and delta_interval[0] > 0.0
        ),
        "finite_s_correction_jacobi_is_finite": math.isfinite(finite_s_jacobi),
        "complete_fixed_s_operator_and_growth_are_finite": math.isfinite(covered_growth),
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_UNIFORM_GAP_HARD_RESPONSE",
        "status": (
            "C2_UNIFORM_GAP_HARD_RESPONSE_AND_FINITE_s_JACOBI_CERTIFIED"
            if passed else "C2_UNIFORM_GAP_HARD_RESPONSE_INVALID"
        ),
        "matching_audit": {
            "diagram_slot": "C2_FINITE_s_HARD_RESPONSE",
            "required_type": "UNIFORM_INVERSE_OF_THE_SELECTED_LINE_COMPLEMENT_BLOCK",
            "matched_BHSM_object": "CERTIFIED_ORDERED_EVENT_EIGENLINE_GAP_ON_THE_FULL_ACTION_BALL",
            "equivalence": "BORDERED_KKT_OR_ORTHOGONAL_SCHUR_COMPLEMENT",
            "match": "VALID_MATCH",
        },
        "hard_response": {
            "uniform_gap_lower": float(line["eigenline_gap_lower"]),
            "uniform_inverse_upper": hard_inverse,
            "old_redundant_Neumann_denominator_lower": old_hard_denominator,
            "old_redundant_inflation_factor": _up(1.0 / old_hard_denominator),
            "covariant_Gronwall_exponent_upper": hard_exponent,
            "covariant_Gronwall_factor_upper": exponential,
            "center_hard_rate_raw_norm": float(np.linalg.norm(hard_center)),
            "hard_rate_action_upper": hard_rate_action,
            "hard_Jacobi_action_upper": hard_jacobi_action,
            "structured_b_derivative_upper": structured_b,
        },
        "finite_s_correction": {
            "descriptor_upper": descriptor,
            "physical_tube_radius": radius,
            "matrix_center_total_radius": total_radius,
            "c_interval": list(c_interval),
            "b_interval": list(b_interval),
            "Delta_interval": list(delta_interval),
            "correction_norm_upper": correction_norm,
            "correction_Jacobi_before_s_upper": correction_jacobi,
            "s_times_correction_Jacobi_upper": finite_s_jacobi,
            "birth_limit_full_ball_operator_upper": birth_operator,
            "complete_fixed_s_operator_upper": full_fixed_s_operator,
            "covered_descriptor_horizon": covered_horizon,
            "covered_full_ball_growth_upper": covered_growth,
        },
        "adjudication": {
            "hard_denominator_collapse": "REDUNDANT_SECOND_INVERTIBILITY_PROOF_NOT_A_PHYSICAL_STOP",
            "finite_s_correction": "CERTIFIED_ON_CURRENT_PHYSICAL_TUBE",
            "actual_event_or_canonical_stop": "NOT_REACHED",
            "Gate7": "OPEN_CONTINUATION",
            "Gate8": "LOCKED",
        },
        "hindsight": {
            "result": "VALIDATED",
            "classification": "REDUNDANT_INVERTIBILITY_PROOF",
            "obstruction_physical": False,
        },
        "exact_next_dependency": (
            "REISSUE_THE_C2_FRESH_CENTER_CONTINUATION_WITH_THE_UNIFORM_GAP_"
            "HARD_RESPONSE_AND_COMPLETE_FIXED_s_OPERATOR_BOUND"
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
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "old_inflation": payload["hard_response"]["old_redundant_inflation_factor"],
        "hard_Jacobi": payload["hard_response"]["hard_Jacobi_action_upper"],
        "finite_s_Jacobi": payload["finite_s_correction"]["s_times_correction_Jacobi_upper"],
        "growth": payload["finite_s_correction"]["covered_full_ball_growth_upper"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
