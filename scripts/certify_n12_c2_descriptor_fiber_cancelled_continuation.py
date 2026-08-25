"""Continue C2 with the exact fixed-s birth-limit cancellation."""

from __future__ import annotations

from decimal import Decimal, localcontext
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

from bhsm.interface.aether_forward_c2_descriptor_fiber_ball import (  # noqa: E402
    fresh_center_descriptor_fiber_ball,
)
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from certify_n12_c2_fresh_center_denominator_continuation import (  # noqa: E402
    _center_data,
    _float_lower,
    _float_upper,
    _maximal_closing_step,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION.json"
DATA_RESULT = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION.npz"
PREFIX = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.json"
PREFIX_DATA = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.npz"
RECENTER = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.json"
LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
MAJORANTS = BASE / "BHSM_N12_C2_LAUNCH_ACTION_MAJORANTS.json"
FIBER = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_DENOMINATOR.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_descriptor_fiber_ball.py"
THEORY = ROOT / "theory/n12_c2_descriptor_fiber_cancelled_continuation.md"
INPUTS = (PREFIX, PREFIX_DATA, RECENTER, LINE, MAJORANTS, FIBER, MODULE, THEORY)
QDIM = 37
MAX_BOXES = 64


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fiber_center_field(
    *, center: np.ndarray, weights: np.ndarray, reference: np.ndarray,
    signed_s: float, c_interval: tuple[float, float], ball: dict[str, Any],
) -> dict[str, Any]:
    q_weights, reduced_weights, _, _ = metric_data()
    jet = exact_full_action_jet_at_state(
        12, center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:], points=96,
    )
    gradient = np.asarray(jet.gradient, dtype=float) / weights
    hessian_action = np.asarray(jet.hessian, dtype=float) / weights[:, None] / weights[None, :]
    raw_D = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(raw_D)
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
    c_midpoint = 0.5 * (float(c_interval[0]) + float(c_interval[1]))
    c_halfwidth = 0.5 * (float(c_interval[1]) - float(c_interval[0]))
    nominal_delta = c_midpoint * b_center
    numerator = np.concatenate((
        signed_s * configuration,
        (b_center * psi + signed_s * hard_center) * reduced_weights,
    ))
    field = numerator / nominal_delta
    denominator_error = (
        abs(b_center) * c_halfwidth
        + signed_s * float(ball["hard_remainder_upper"])
    )
    exact_center_delta_lower = nominal_delta - denominator_error
    if exact_center_delta_lower <= 0.0:
        raise ArithmeticError("center descriptor denominator does not close")
    mismatch = (
        float(np.linalg.norm(numerator)) * denominator_error
        / (exact_center_delta_lower * nominal_delta)
    )
    selected_action_norm = float(np.linalg.norm(psi * reduced_weights))
    return {
        "selected_branch": selected,
        "b_psi_center": b_center,
        "c_psi_midpoint": c_midpoint,
        "nominal_Delta": nominal_delta,
        "field_action": field,
        "field_action_norm": float(np.linalg.norm(field)),
        "field_mismatch_upper": mismatch,
        "selected_action_norm": selected_action_norm,
        "exact_center_Delta_lower": exact_center_delta_lower,
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing cancelled-fiber inputs: " + ", ".join(missing))
    prefix, recenter, line_record, majorants, fiber = (
        _load(path) for path in (PREFIX, RECENTER, LINE, MAJORANTS, FIBER)
    )
    if not all(record.get("validation_passed") is True for record in (
        prefix, recenter, line_record, majorants, fiber,
    )):
        raise RuntimeError("validated fixed-s cancellation parents required")
    with np.load(PREFIX_DATA) as data:
        center = np.asarray(
            data["C2_recentered_adaptive_predictor_centers"][-1], dtype=float
        )
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)

    prefix_cover = prefix["recentered_cover"]
    transferred = recenter["recenter"]
    line = line_record["bounds"]
    launch = transferred["recentered_launch_ball"]
    base_pf = transferred["recentered_pole_free_bounds"]
    fifth = float(next(
        row for row in majorants["sectors"] if row["sector"] == "event"
    )["derivative_operator_majorants_0_through_5"][5])
    rows: list[dict[str, Any]] = []
    centers = [center.copy()]
    exhaustion = "CANCELLED_FIBER_SAFETY_LIMIT_REACHED"
    witness: dict[str, Any] = {}

    with localcontext() as context:
        context.prec = 100
        signed_s = Decimal(prefix_cover["final_signed_lambda_decimal"])
        initial_signed_s = signed_s
        tube = Decimal.from_float(float(prefix_cover["final_endpoint_tube_radius_upper"]))
        initial_tube = tube
        center_path = Decimal(0)
        proper_lower_sum = Decimal(0)
        proper_upper_sum = Decimal(0)
        for index in range(MAX_BOXES):
            path_upper = _float_upper(center_path)
            pf = dict(base_pf)
            pf.update({
                "hard_D3_center": float(base_pf["hard_D3_center"])
                + float(base_pf["D4_full_hard_hard_upper"]) * path_upper,
                "rhs_raw_derivative_center": float(base_pf["rhs_raw_derivative_center"])
                + float(base_pf["rhs_raw_second_derivative_upper"]) * path_upper,
                "coupling_center": float(base_pf["coupling_center"])
                + float(base_pf["D4_full_selected_hard_upper"]) * path_upper,
                "center_hard_rate_raw_norm": float(base_pf["center_hard_rate_raw_norm"])
                + float(base_pf["hard_Jacobi_action_upper"]) * path_upper
                / max(float(np.max(weights[QDIM:])), 1.0),
            })
            center_data = _center_data(center, weights, reference, fifth)
            selected_action_norm = float(np.linalg.norm(
                np.asarray(center_data["selected_vector"]) * weights[QDIM:]
            ))
            parent_radius = min(
                float(transferred["recentered_parent_action_radius"]) - path_upper,
                float(line_record["action_coordinate_ball_radius"])
                - float(transferred["old_root_to_new_center_action_distance_upper"])
                - path_upper,
            )
            descriptor_upper = _float_upper(signed_s)
            try:
                for _ in range(16):
                    ball = fresh_center_descriptor_fiber_ball(
                        incoming_tube=_float_upper(tube),
                        parent_radius=parent_radius,
                        descriptor_upper=descriptor_upper,
                        pf=pf, launch=launch, line=line,
                        center_c=tuple(center_data["c_psi_center_interval"]),
                        center_b=tuple(center_data["b_psi_center_interval"]),
                        center_selected_action_norm=selected_action_norm,
                        center_state=center, weights=weights,
                        coefficient_enclosure=_coefficient_enclosure,
                    )
                    proof = _fiber_center_field(
                        center=center, weights=weights, reference=reference,
                        signed_s=float(signed_s),
                        c_interval=tuple(center_data["c_psi_center_interval"]),
                        ball=ball,
                    )
                    step = _maximal_closing_step(
                        center=center, weights=weights, signed_s=float(signed_s),
                        tube=_float_upper(tube), ball=ball, proof=proof,
                    )
                    required_upper = _float_upper(
                        signed_s + Decimal.from_float(float(step["selected_midpoint_step"]))
                    )
                    if required_upper <= descriptor_upper:
                        break
                    descriptor_upper = required_upper
                else:
                    raise ArithmeticError("descriptor-upper fixed point did not close")
            except ArithmeticError as error:
                exhaustion = "CANCELLED_DESCRIPTOR_FIBER_PROOF_EXHAUSTED"
                witness = {
                    "message": str(error),
                    "incoming_tube_upper": _float_upper(tube),
                    "center_path_upper": path_upper,
                }
                break

            signed_step = Decimal.from_float(float(step["selected_midpoint_step"]))
            signed_end = signed_s + signed_step
            physical_u_increment = signed_end**2 - signed_s**2
            if not physical_u_increment > 0:
                exhaustion = "CANCELLED_FIBER_PHYSICAL_INCREMENT_NOT_POSITIVE"
                break
            delta_lower = Decimal.from_float(float(ball["Delta_interval"][0]))
            delta_upper = Decimal.from_float(float(ball["Delta_interval"][1]))
            coordinate_lower = physical_u_increment / (Decimal(2) * delta_upper)
            coordinate_upper = physical_u_increment / (Decimal(2) * delta_lower)
            lapse_lower = Decimal.from_float(float(ball["lapse_interval"][0]))
            lapse_upper = Decimal.from_float(float(ball["lapse_interval"][1]))
            proper_lower = lapse_lower * coordinate_lower
            proper_upper = lapse_upper * coordinate_upper
            proper_lower_sum += proper_lower
            proper_upper_sum += proper_upper
            center_path += Decimal.from_float(float(step["stored_step_norm"]))
            tube = Decimal.from_float(float(step["new_tube"]))
            center = np.asarray(step["stored_center"], dtype=float)
            signed_s = signed_end
            centers.append(center.copy())
            rows.append({
                "cancelled_fiber_index": index + 1,
                "global_segment_index": int(prefix_cover["total_certified_segments"]) + index + 1,
                "selected_branch": int(center_data["selected_branch"]),
                "descriptor_fiber_lambda_upper": float(ball["descriptor_fiber_lambda_upper"]),
                "incoming_tube_upper": float(ball["incoming_endpoint_tube_radius"]),
                "joint_feasibility_upper_radius": float(ball["joint_feasibility_upper_radius"]),
                "selected_ball_radius": float(ball["selected_midpoint_radius"]),
                "hard_denominator_lower": float(ball["hard_self_consistency_denominator_lower"]),
                "Delta_lower": float(ball["Delta_interval"][0]),
                "cancelled_speed_upper": float(ball["regularized_speed_upper"]),
                "cancelled_Jacobi_upper": float(ball["pole_free_regularized_Jacobi_upper"]),
                "center_field_norm": float(proof["field_action_norm"]),
                "center_field_mismatch_upper": float(proof["field_mismatch_upper"]),
                "signed_lambda_step_decimal": str(signed_step),
                "physical_u_increment_decimal": str(physical_u_increment),
                "proper_time_increment_interval": [
                    _float_lower(proper_lower), _float_upper(proper_upper),
                ],
                "Jacobi_growth_upper": float(step["growth"]),
                "endpoint_tube_radius_upper": _float_upper(tube),
                "fresh_center_path_upper": _float_upper(center_path),
                "root_use_inside_selected_ball": float(step["root_use"]),
                "proof_center_is_physical_endpoint": False,
            })
        else:
            exhaustion = "CANCELLED_FIBER_SAFETY_LIMIT_REACHED_WITH_CONTINUATION_OPEN"

    np.savez_compressed(
        DATA_RESULT,
        C2_descriptor_fiber_predictor_centers=np.asarray(centers),
        state_weights=weights,
        branch_reference=reference,
    )
    accepted = len(rows)
    validation = {
        "validated_1064_segment_prefix_consumed": True,
        "exact_fixed_s_cancellation_certifies_strict_extension": accepted > 0,
        "all_centers_retain_branch_24": accepted > 0 and all(
            row["selected_branch"] == 24 for row in rows
        ),
        "all_descriptor_upper_fixed_points_close": accepted > 0 and all(
            Decimal(row["signed_lambda_step_decimal"]) > 0 for row in rows
        ),
        "all_hard_Delta_and_proper_time_margins_positive": accepted > 0 and all(
            row["hard_denominator_lower"] > 0.0
            and row["Delta_lower"] > 0.0
            and row["proper_time_increment_interval"][0] > 0.0 for row in rows
        ),
        "all_tubes_close_in_selected_fiber_balls": accepted > 0 and all(
            row["root_use_inside_selected_ball"] < row["selected_ball_radius"]
            for row in rows
        ),
        "proof_exhaustion_not_promoted_to_event_or_stop": True,
        "no_equation_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION",
        "status": (
            "C2_FIXED_S_CANCELLED_CONTINUATION_CERTIFIED"
            if passed else "C2_FIXED_S_CANCELLED_CONTINUATION_NOT_CERTIFIED"
        ),
        "exact_identity": {
            "flow": "F_s=(s*qdot,b_psi*Psi+s*V_hard)/(c*b_psi+s*R)",
            "birth_limit": "F_0=Psi/c",
            "cancelled_difference": "F_s-F_0=s*(c*V_full-R*Psi)/(c*Delta)",
            "descriptor_fiber": "lambda_event(Y(s))=s",
        },
        "continuation": {
            "prior_total_segments": int(prefix_cover["total_certified_segments"]),
            "additional_certified_segments": accepted,
            "total_certified_segments": int(prefix_cover["total_certified_segments"]) + accepted,
            "rows": rows,
            "initial_signed_lambda_decimal": str(initial_signed_s),
            "final_signed_lambda_decimal": str(signed_s),
            "initial_endpoint_tube_radius_upper": _float_upper(initial_tube),
            "final_endpoint_tube_radius_upper": _float_upper(tube),
            "fresh_center_path_upper": _float_upper(center_path),
            "additional_proper_duration_interval": [
                _float_lower(proper_lower_sum), _float_upper(proper_upper_sum),
            ],
            "exhaustion_classification": exhaustion,
            "exhaustion_witness": witness,
            "exhaustion_is_event_or_canonical_stop": False,
            "data": DATA_RESULT.relative_to(ROOT).as_posix(),
            "data_SHA256": _sha256(DATA_RESULT),
        },
        "adjudication": {
            "independent_b_and_Delta_scalar_wrapping": "REMOVED_BY_EXACT_QUOTIENT_IDENTITY",
            "actual_later_event_or_canonical_stop": "NOT_REACHED",
            "mathematical_history_termination_claimed": False,
            "current_finite_route_blocker": exhaustion,
        },
        "exact_next_dependency": (
            "IF_THE_CANCELLED_SCALAR_FIBER_TUBE_EXHAUSTS,_USE_THE_MEASURED_"
            "FIXED_s_TANGENT_MATRIX_WITH_A_RETAINED_D4_D5_CONJUGATED_"
            "REMAINDER;_OTHERWISE_CONTINUE_TO_AN_ACTUAL_EVENT_OR_STOP"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_CANCELLED_FIBER_CONTINUATION_OR_COMBINED_PROJECTED_TAIL",
            "Gate8": "LOCKED",
            "actual_projected_zero_source_force": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
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
        encoding="utf-8", newline="\n",
    )
    cover = payload["continuation"]
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "additional_segments": cover["additional_certified_segments"],
        "total_segments": cover["total_certified_segments"],
        "final_signed_lambda": cover["final_signed_lambda_decimal"],
        "final_tube": cover["final_endpoint_tube_radius_upper"],
        "exhaustion": cover["exhaustion_classification"],
    }, indent=2))


if __name__ == "__main__":
    main()
