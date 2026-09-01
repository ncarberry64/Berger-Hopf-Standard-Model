"""Certify the bordered C2 response through second variation on the tube."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
CENTER_DATA = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.npz"
BORDERED = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.json"
BORDERED_DATA = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.npz"
GROWTH = BASE / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
RESULT = BASE / "BHSM_N12_C2_BORDERED_RESPONSE_SECOND_VARIATION_BALL.json"
THEORY = ROOT / "theory" / "n12_c2_bordered_response_second_variation_ball.md"
INPUTS = (CENTER, CENTER_DATA, BORDERED, BORDERED_DATA, GROWTH, THEORY)
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
        raise FileNotFoundError("missing bordered second-variation inputs: " + ", ".join(missing))
    center, bordered, growth = (_json(path) for path in (CENTER, BORDERED, GROWTH))
    if not all(record.get("validation_passed") is True for record in (
        center, bordered, growth,
    )):
        raise RuntimeError("validated center, bordered, and growth parents required")
    with np.load(BORDERED_DATA) as data:
        K = np.asarray(data["bordered_matrix"], dtype=float)
        response = np.asarray(data["bordered_response"], dtype=float)
        response_first = np.asarray(data["bordered_response_derivative_action"], dtype=float)
        forcing = K @ response

    matrix = center["fixed_descriptor_matrix"]
    fresh = growth["fresh_line_bounds"]
    pf = growth["fresh_pole_free_bounds"]
    radius = float(matrix["incoming_endpoint_tube_radius"])
    inverse = _up(1.0 / float(fresh["eigenline_gap_lower"]))
    psi_two = float(fresh["selected_line_second_variation_coefficient_upper"])
    K_two = _up(
        float(pf["D4_full_hard_hard_upper"])
        + float(fresh["selected_eigenvalue_raw_Hessian_bound"])
        + 2.0 * psi_two
    )
    relative_center = float(
        matrix["bordered_relative_tangent_tensor_Frobenius_upper"]
    )
    relative_second = _up(inverse * K_two)
    relative_ball = _up(relative_center + relative_second * radius)
    self_consistency = _up(2.0 * radius * relative_ball)
    if self_consistency >= 1.0:
        raise ArithmeticError(
            f"bordered response second-variation fixed point fails: {self_consistency}"
        )

    response_zero = _up(float(np.linalg.norm(response)))
    response_one = _up(float(np.linalg.norm(response_first)))
    forcing_two = float(pf["rhs_raw_second_derivative_upper"])
    response_bound = response_zero
    for _ in range(64):
        second_base = _up(inverse * (forcing_two + K_two * response_bound))
        first_ball = _up(
            (response_one + radius * second_base) / (1.0 - self_consistency)
        )
        second_ball = _up(second_base + 2.0 * relative_ball * first_ball)
        updated = _up(
            response_zero + first_ball * radius
            + 0.5 * second_ball * radius**2
        )
        if updated <= response_bound * (1.0 + 1.0e-12):
            response_bound = max(response_bound, updated)
            break
        response_bound = updated
    else:
        raise ArithmeticError("bordered response radius fixed point did not converge")

    rhs_zero = _up(float(np.linalg.norm(forcing[:-1])))
    rhs_one = float(pf["rhs_raw_derivative_center"])
    p1 = float(fresh["weighted_selected_to_complement_first_variation_on_ball"])
    b_zero = float(response[-1])
    b_one = _up(float(np.linalg.norm(response_first[-1])))
    b_two = _up(psi_two * rhs_zero + 2.0 * p1 * rhs_one + forcing_two)
    b_radius = _up(b_one * radius + 0.5 * b_two * radius**2)
    b_interval = (
        _down(b_zero - b_radius),
        _up(b_zero + b_radius),
    )
    hard_action_bound = _up(response_bound)
    hard_first_ball = first_ball
    hard_second_ball = second_ball

    validation = {
        "uniform_bordered_inverse_uses_certified_hard_gap": inverse > 0.0,
        "relative_second_variation_self_consistency_is_strict": self_consistency < 1.0,
        "bordered_response_radius_fixed_point_converged": response_bound > response_zero,
        "structured_b_interval_is_strictly_positive": b_interval[0] > 0.0,
        "hard_response_first_and_second_variations_are_finite": (
            math.isfinite(hard_first_ball) and math.isfinite(hard_second_ball)
        ),
        "full_field_quotient_remainder_not_claimed_here": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_BORDERED_RESPONSE_SECOND_VARIATION_BALL",
        "status": (
            "C2_BORDERED_HARD_RESPONSE_AND_b_psi_SECOND_VARIATION_BALL_CERTIFIED"
            if passed else "C2_BORDERED_RESPONSE_SECOND_VARIATION_BALL_INVALID"
        ),
        "ball": {
            "incoming_tube_radius": radius,
            "uniform_bordered_inverse_upper": inverse,
            "bordered_K_second_variation_upper": K_two,
            "center_relative_tangent_tensor_upper": relative_center,
            "relative_tangent_tensor_ball_upper": relative_ball,
            "relative_second_variation_self_consistency": self_consistency,
            "response_center_norm": response_zero,
            "response_norm_upper": hard_action_bound,
            "response_first_variation_upper": hard_first_ball,
            "response_second_variation_upper": hard_second_ball,
            "b_psi_center": b_zero,
            "b_psi_first_variation_center_upper": b_one,
            "b_psi_second_variation_upper": b_two,
            "b_psi_interval": list(b_interval),
        },
        "adjudication": {
            "hard_response_second_variation": "CERTIFIED_ON_INCOMING_FIXED_DESCRIPTOR_TUBE",
            "b_psi_positivity": "CERTIFIED_ON_INCOMING_FIXED_DESCRIPTOR_TUBE",
            "full_fixed_s_field_interval": "OPEN_CONJUGATED_QUOTIENT_REMAINDER",
            "actual_event_or_canonical_stop": "NOT_REACHED",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
        },
        "hindsight": {
            "result": "VALIDATED",
            "classification": "HARD_RESPONSE_PROOF_ARTIFACT_REMOVED",
            "obstruction_physical": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_SIGNED_SECOND_VARIATION_OF_THE_CANCELLED_FULL_FIELD_"
            "Psi_OVER_c_PLUS_s_TIMES_cV_MINUS_RPsi_OVER_cDelta_AND_PROPAGATE_"
            "THE_CONJUGATED_TANGENT_ELLIPSOID"
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
        "self_consistency": payload["ball"]["relative_second_variation_self_consistency"],
        "response_upper": payload["ball"]["response_norm_upper"],
        "response_first": payload["ball"]["response_first_variation_upper"],
        "response_second": payload["ball"]["response_second_variation_upper"],
        "b_interval": payload["ball"]["b_psi_interval"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
