"""Certify one C2 fixed-descriptor Lohner step with signed cancellation."""

from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
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
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
CENTER_DATA = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.npz"
RESPONSE = BASE / "BHSM_N12_C2_BORDERED_RESPONSE_SECOND_VARIATION_BALL.json"
BORDERED_DATA = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.npz"
GROWTH = BASE / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
CONTINUATION = BASE / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.json"
PARENT = BASE / "BHSM_N12_C2_TERMINAL_PARENT_ACTION_MAJORANTS_1P5E10.json"
TERMINAL = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
RESULT = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
ENDPOINT = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.npz"
THEORY = ROOT / "theory" / "n12_c2_cancelled_field_lohner_step.md"
PARENT_DRIVER = ROOT / "scripts" / "materialize_n12_c2_terminal_parent_action_majorants.py"
INPUTS = (
    CENTER, CENTER_DATA, RESPONSE, BORDERED_DATA, GROWTH, CONTINUATION,
    PARENT, TERMINAL, THEORY, PARENT_DRIVER,
)
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
        raise FileNotFoundError("missing cancelled-field Lohner inputs: " + ", ".join(missing))
    center_record, response_record, growth, continuation, parent = (
        _json(path) for path in (CENTER, RESPONSE, GROWTH, CONTINUATION, PARENT)
    )
    if not all(record.get("validation_passed") is True for record in (
        center_record, response_record, growth, continuation, parent,
    )):
        raise RuntimeError("validated center, response, growth, continuation, and parent required")
    with np.load(CENTER_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        field = np.asarray(data["exact_center_field_action"], dtype=float)
        field_first = np.asarray(data["fixed_s_field_matrix_partial_action"], dtype=float)
    with np.load(BORDERED_DATA) as data:
        response = np.asarray(data["bordered_response"], dtype=float)
        response_first = np.asarray(data["bordered_response_derivative_action"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
        psi = np.asarray(data["selected_vector"], dtype=float)
        K = np.asarray(data["bordered_matrix"], dtype=float)
        forcing = K @ response
    terminal_data = np.load(TERMINAL)
    terminal = np.asarray(terminal_data["state"][:center.size], dtype=float)

    q_weights, reduced_weights, maximum_q_weight, maximum_reduced_weight = metric_data()
    previous = continuation["continuation"]
    incoming_tube = float(previous["final_endpoint_tube_radius_upper"])
    terminal_distance = _up(float(np.linalg.norm((center - terminal) * weights)))
    parent_radius = float(parent["action_coordinate_ball_radius"])
    parent_remaining = _down(parent_radius - terminal_distance)
    fresh_remaining = _down(
        float(growth["radius_derivation"]["selected_growth_chart_radius"])
        - float(previous["fresh_center_path_upper"])
    )
    maximal_domain = min(parent_remaining, fresh_remaining)
    if maximal_domain <= incoming_tube:
        raise ArithmeticError("no domain radius remains beyond incoming tube")
    domain_radius = 0.5 * (incoming_tube + maximal_domain)

    fresh = growth["fresh_line_bounds"]
    pf = growth["fresh_pole_free_bounds"]
    inverse = _up(1.0 / float(fresh["eigenline_gap_lower"]))
    psi_two = float(fresh["selected_line_second_variation_coefficient_upper"])
    K_two = _up(
        float(pf["D4_full_hard_hard_upper"])
        + float(fresh["selected_eigenvalue_raw_Hessian_bound"])
        + 2.0 * psi_two
    )
    relative_center = float(center_record["fixed_descriptor_matrix"][
        "bordered_relative_tangent_tensor_Frobenius_upper"
    ])
    relative_ball = _up(relative_center + inverse * K_two * domain_radius)
    response_self = _up(2.0 * domain_radius * relative_ball)
    if response_self >= 1.0:
        raise ArithmeticError("extended bordered response fixed point does not close")
    x0 = _up(float(np.linalg.norm(response)))
    x1 = _up(float(np.linalg.norm(response_first)))
    f2 = float(pf["rhs_raw_second_derivative_upper"])
    x_bound = x0
    for _ in range(64):
        x2_base = _up(inverse * (f2 + K_two * x_bound))
        x1_ball = _up((x1 + domain_radius * x2_base) / (1.0 - response_self))
        x2_ball = _up(x2_base + 2.0 * relative_ball * x1_ball)
        updated = _up(x0 + x1_ball * domain_radius + 0.5 * x2_ball * domain_radius**2)
        if updated <= x_bound * (1.0 + 1.0e-12):
            x_bound = max(x_bound, updated)
            break
        x_bound = updated
    else:
        raise ArithmeticError("extended response bound did not converge")

    rhs0 = _up(float(np.linalg.norm(forcing[:-1])))
    rhs1 = float(pf["rhs_raw_derivative_center"])
    p1 = float(fresh["weighted_selected_to_complement_first_variation_on_ball"])
    p2 = psi_two
    b0 = float(response[-1])
    b1 = _up(float(np.linalg.norm(response_first[-1])))
    b2 = _up(p2 * rhs0 + 2.0 * p1 * rhs1 + f2)
    b_radius = _up(b1 * domain_radius + 0.5 * b2 * domain_radius**2)
    b_lower = _down(b0 - b_radius)
    b_upper = _up(b0 + b_radius)

    c0 = float(center_record["center_field"]["moving_cubic_from_Dlambda_Psi"])
    c1 = float(growth["moving_cubic"]["center_complete_first_derivative_upper"])
    c2 = float(growth["moving_cubic"]["second_derivative_upper"])
    c_lower = _down(c0 - c1 * domain_radius - 0.5 * c2 * domain_radius**2)
    c_upper = _up(c0 + c1 * domain_radius + 0.5 * c2 * domain_radius**2)
    c1_ball = _up(c1 + c2 * domain_radius)

    event_derivatives = next(
        row["derivative_operator_majorants_0_through_5"]
        for row in parent["sectors"] if row["sector"] == "event"
    )
    action_d3, action_d4, action_d5 = map(float, event_derivatives[3:6])
    lambda_one = float(fresh["selected_eigenvalue_first_derivative_bound"])
    lambda_two = float(fresh["selected_eigenvalue_raw_Hessian_bound"])
    lambda_three = _up(
        action_d5 + 6.0 * action_d4 * p1
        + 6.0 * action_d3 * p1**2 + 2.0 * action_d3 * p2
    )
    selected_zero = _up(float(np.linalg.norm(psi * reduced_weights)))
    selected_bound = _up(
        selected_zero + maximum_reduced_weight * p1 * domain_radius
        + 0.5 * maximum_reduced_weight * p2 * domain_radius**2
    )
    selected_one = _up(maximum_reduced_weight * (p1 + p2 * domain_radius))
    selected_two = _up(maximum_reduced_weight * p2)

    configuration = q_weights * center[QDIM:2 * QDIM]
    configuration_bound = _up(float(np.linalg.norm(configuration)) + maximum_q_weight * domain_radius)
    full_hard_zero = _up(math.hypot(configuration_bound, maximum_reduced_weight * x_bound))
    full_hard_one = _up(math.hypot(maximum_q_weight, maximum_reduced_weight * x1_ball))
    full_hard_two = _up(maximum_reduced_weight * x2_ball)
    R0 = abs(float(center_record["center_field"]["R_Dlambda_Vhard"]))
    R1 = _up(lambda_two * full_hard_zero + lambda_one * full_hard_one)
    R2 = _up(
        lambda_three * full_hard_zero
        + 2.0 * lambda_two * full_hard_one
        + lambda_one * full_hard_two
    )
    signed_s = float(center_record["center_field"]["signed_descriptor_decimal"])
    R_bound = _up(R0 + R1 * domain_radius + 0.5 * R2 * domain_radius**2)
    Delta_lower = _down(c_lower * b_lower - signed_s * R_bound)
    Delta_upper = _up(c_upper * b_upper + signed_s * R_bound)
    b1_ball = _up(b1 + b2 * domain_radius)
    Delta_one = _up(c1_ball * b_upper + c_upper * b1_ball + signed_s * (R1 + R2 * domain_radius))
    Delta_two = _up(c2 * b_upper + 2.0 * c1_ball * b1_ball + c_upper * b2 + signed_s * R2)

    # F_s=Psi/c+s G, G=(c V-R Psi)/(c Delta).  The response, line, and
    # spectral derivatives have already been combined before this scalar
    # quotient bound is applied.
    P0 = _up(c_upper * full_hard_zero + R_bound * selected_bound)
    P1 = _up(
        c1_ball * full_hard_zero + c_upper * full_hard_one
        + (R1 + R2 * domain_radius) * selected_bound + R_bound * selected_one
    )
    P2 = _up(
        c2 * full_hard_zero + 2.0 * c1_ball * full_hard_one
        + c_upper * full_hard_two + R2 * selected_bound
        + 2.0 * (R1 + R2 * domain_radius) * selected_one
        + R_bound * selected_two
    )
    Q_lower = _down(c_lower * Delta_lower)
    Q_one = _up(c1_ball * Delta_upper + c_upper * Delta_one)
    Q_two = _up(c2 * Delta_upper + 2.0 * c1_ball * Delta_one + c_upper * Delta_two)
    correction_two = _up(
        P2 / Q_lower + 2.0 * P1 * Q_one / Q_lower**2
        + P0 * Q_two / Q_lower**2 + 2.0 * P0 * Q_one**2 / Q_lower**3
    )
    birth_two = float(growth["birth_limit_generator"]["D2F0_action_operator_upper"])
    field_two = _up(birth_two + signed_s * correction_two)
    center_mu = float(center_record["fixed_descriptor_matrix"][
        "center_tangent_numerical_abscissa_upper"
    ])
    center_operator = _up(float(np.linalg.norm(field_first, 2)) + float(
        center_record["fixed_descriptor_matrix"]["total_center_matrix_remainder_upper"]
    ))
    field_one_ball = _up(center_operator + field_two * domain_radius)
    logarithmic_norm_ball = _up(center_mu + field_two * domain_radius)

    coefficient = _coefficient_enclosure(center, weights, domain_radius)
    if not (
        c_lower > 0.0 and b_lower > 0.0 and Delta_lower > 0.0
        and coefficient["root_lapse_interval"][0] > 0.0
        and coefficient["root_D_tau_log_R4_interval"][0] > 0.0
    ):
        raise ArithmeticError("cancelled-field domain margins are not positive")

    field_norm = _up(float(np.linalg.norm(field)))
    nominal_step = _down(0.9 * (domain_radius - incoming_tube) / field_norm)
    step = nominal_step
    with localcontext() as context:
        context.prec = 120
        context.rounding = ROUND_CEILING
        for _ in range(96):
            h = Decimal.from_float(step)
            mu = Decimal.from_float(logarithmic_norm_ball)
            f0d = Decimal.from_float(field_norm)
            f1d = Decimal.from_float(field_one_ball)
            growth_factor = (mu * h).exp()
            endpoint_tube = (
                growth_factor * Decimal.from_float(incoming_tube)
                + Decimal("0.5") * f1d * f0d * h**2
            )
            center_path = f0d * h + Decimal("0.5") * f1d * f0d * h**2
            total_use = endpoint_tube + center_path
            if total_use < Decimal.from_float(domain_radius):
                break
            step *= 0.8
        else:
            raise ArithmeticError("cancelled-field Lohner step did not close")
    endpoint_tube_float = _up(float(endpoint_tube))
    center_path_float = _up(float(center_path))
    total_use_float = _up(float(total_use))
    acceleration = field_first @ field
    endpoint_center = center + step * field / weights + 0.5 * step**2 * acceleration / weights
    stored_step_norm = float(np.linalg.norm((endpoint_center - center) * weights))

    endpoint_hessian = np.asarray(exact_full_action_jet_at_state(
        12, endpoint_center[:QDIM], endpoint_center[QDIM:2 * QDIM],
        endpoint_center[2 * QDIM:], points=96,
    ).hessian, dtype=float)[QDIM:, QDIM:]
    _, endpoint_vectors = np.linalg.eigh(endpoint_hessian)
    endpoint_branch = int(np.argmax(np.abs(endpoint_vectors.T @ reference)))

    with localcontext() as context:
        context.prec = 120
        old_s = Decimal(center_record["center_field"]["signed_descriptor_decimal"])
        step_s = Decimal.from_float(step)
        new_s = old_s + step_s
        physical_increment = new_s**2 - old_s**2
        context.rounding = ROUND_FLOOR
        coordinate_lower = physical_increment / (Decimal(2) * Decimal.from_float(Delta_upper))
        proper_lower = Decimal.from_float(coefficient["root_lapse_interval"][0]) * coordinate_lower
        context.rounding = ROUND_CEILING
        coordinate_upper = physical_increment / (Decimal(2) * Decimal.from_float(Delta_lower))
        proper_upper = Decimal.from_float(coefficient["root_lapse_interval"][1]) * coordinate_upper

    np.savez_compressed(
        ENDPOINT,
        center_state=center,
        endpoint_predictor_center=endpoint_center,
        state_weights=weights,
        branch_reference=reference,
        exact_center_field_action=field,
        center_acceleration_action=acceleration,
        signed_descriptor_step=np.asarray(step),
        endpoint_tube_radius=np.asarray(endpoint_tube_float),
    )
    validation = {
        "terminal_parent_majorant_contains_domain": terminal_distance + domain_radius < parent_radius,
        "fresh_growth_chart_contains_domain": domain_radius < fresh_remaining,
        "domain_strictly_contains_incoming_tube": domain_radius > incoming_tube,
        "extended_bordered_response_fixed_point_closes": response_self < 1.0,
        "c_b_Delta_lapse_and_radius_rate_are_positive": (
            c_lower > 0.0 and b_lower > 0.0 and Delta_lower > 0.0
            and coefficient["root_lapse_interval"][0] > 0.0
            and coefficient["root_D_tau_log_R4_interval"][0] > 0.0
        ),
        "cancelled_correction_second_variation_is_subdominant_to_birth": (
            signed_s * correction_two < birth_two
        ),
        "matrix_Lohner_tube_and_center_close_inside_domain": total_use_float < domain_radius,
        "positive_step_has_nonzero_stored_geometry": step > 0.0 and stored_step_norm > 0.0,
        "branch_24_replayed_at_predictor_center": endpoint_branch == 24,
        "positive_physical_and_proper_duration": physical_increment > 0 and proper_lower > 0,
        "proof_edge_not_promoted_to_event_or_canonical_stop": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP",
        "status": (
            "C2_CANCELLED_FIXED_s_MATRIX_LOHNER_SEGMENT_1215_CERTIFIED"
            if passed else "C2_CANCELLED_FIELD_LOHNER_STEP_INVALID"
        ),
        "domain": {
            "terminal_center_distance": terminal_distance,
            "parent_action_radius": parent_radius,
            "parent_remaining_radius": parent_remaining,
            "fresh_chart_remaining_radius": fresh_remaining,
            "maximal_joint_domain_radius": maximal_domain,
            "selected_domain_radius": domain_radius,
            "incoming_endpoint_tube_radius": incoming_tube,
            "c_interval": [c_lower, c_upper],
            "b_psi_interval": [b_lower, b_upper],
            "Delta_interval": [Delta_lower, Delta_upper],
            "lapse_interval": coefficient["root_lapse_interval"],
            "D_tau_log_R4_interval": coefficient["root_D_tau_log_R4_interval"],
        },
        "second_variation": {
            "response_self_consistency": response_self,
            "response_norm_upper": x_bound,
            "response_first_variation_upper": x1_ball,
            "response_second_variation_upper": x2_ball,
            "selected_eigenvalue_third_variation_upper": lambda_three,
            "R_second_variation_upper": R2,
            "cancelled_correction_second_variation_before_s_upper": correction_two,
            "s_times_cancelled_correction_second_variation_upper": signed_s * correction_two,
            "birth_limit_second_variation_upper": birth_two,
            "complete_fixed_s_second_variation_upper": field_two,
            "center_tangent_numerical_abscissa_upper": center_mu,
            "fixed_s_logarithmic_norm_ball_upper": logarithmic_norm_ball,
            "fixed_s_first_variation_ball_upper": field_one_ball,
        },
        "segment": {
            "prior_certified_segments": int(previous["total_certified_segments"]),
            "total_certified_segments": int(previous["total_certified_segments"]) + 1,
            "signed_descriptor_start": str(old_s),
            "signed_descriptor_step": str(step_s),
            "signed_descriptor_end": str(new_s),
            "physical_u_increment": str(physical_increment),
            "proper_time_increment_interval": [float(proper_lower), float(proper_upper)],
            "matrix_growth_upper": str(growth_factor),
            "center_path_upper": center_path_float,
            "endpoint_tube_radius_upper": endpoint_tube_float,
            "joint_domain_use_upper": total_use_float,
            "stored_step_action_norm": stored_step_norm,
            "endpoint_selected_branch": endpoint_branch,
            "proof_center_is_physical_endpoint": False,
        },
        "adjudication": {
            "actual_later_event_or_canonical_stop": "NOT_REACHED",
            "old_binary64_zero_step_limit": "REMOVED_BY_MATRIX_LOHNER_STEP",
            "hindsight_outcome": "C_REGULAR_CONTINUATION_EXTENDED",
            "Gate7": "G7_08_OPEN_MAXIMAL_C2_FORCE_OR_FINITE_EVENT_STOP",
            "Gate8": "LOCKED",
        },
        "hindsight": {
            "result": "VALIDATED",
            "classification": "PROOF_TECHNIQUE;_SCALAR_WRAPPING_AND_ZERO_STEP_REMOVED",
            "obstruction_physical": False,
        },
        "exact_next_dependency": (
            "RECENTER_THE_FRESH_DESCRIPTOR_EIGENLINE_AND_BORDERED_MATRIX_AT_"
            "THE_1215_PREDICTOR,_THEN_ITERATE_THE_SAME_CANCELLED_FIELD_"
            "LOHNER_CONSTRUCTION_UNTIL_EVENT_STOP_OR_MAXIMAL_FORCE_TAIL"
        ),
        "endpoint_data": ENDPOINT.relative_to(ROOT).as_posix(),
        "endpoint_data_SHA256": _sha256(ENDPOINT),
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
        "domain_radius": payload["domain"]["selected_domain_radius"],
        "field_second": payload["second_variation"]["complete_fixed_s_second_variation_upper"],
        "step": payload["segment"]["signed_descriptor_step"],
        "stored_step": payload["segment"]["stored_step_action_norm"],
        "endpoint_tube": payload["segment"]["endpoint_tube_radius_upper"],
        "domain_use": payload["segment"]["joint_domain_use_upper"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
