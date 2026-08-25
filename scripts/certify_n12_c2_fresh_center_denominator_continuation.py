"""Continue C2 from segment 1064 without sufficient half-margin reserves."""

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

from bhsm.interface.aether_forward_c2_denominator_ball import (  # noqa: E402
    fresh_center_denominator_ball,
)
from bhsm.interface.aether_forward_c2_descriptor_cover import (  # noqa: E402
    metric_data,
    proof_center_field,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_FRESH_CENTER_DENOMINATOR_CONTINUATION.json"
DATA_RESULT = BASE / "BHSM_N12_C2_FRESH_CENTER_DENOMINATOR_CONTINUATION.npz"
PREFIX = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.json"
PREFIX_DATA = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.npz"
RECENTER = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.json"
LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
MAJORANTS = BASE / "BHSM_N12_C2_LAUNCH_ACTION_MAJORANTS.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_denominator_ball.py"
THEORY = ROOT / "theory/n12_c2_fresh_center_denominator_continuation.md"
INPUTS = (PREFIX, PREFIX_DATA, RECENTER, LINE, MAJORANTS, MODULE, THEORY)
QDIM = 37
MAX_BOXES = 64
COMPLEX_STEPS = (1.0e-16, 1.0e-18, 1.0e-20, 1.0e-22)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / (1.0 + 1.0e-10), -math.inf)


def _float_upper(value: Decimal) -> float:
    result = float(value)
    return math.nextafter(result, math.inf) if Decimal.from_float(result) < value else result


def _float_lower(value: Decimal) -> float:
    result = float(value)
    return math.nextafter(result, -math.inf) if Decimal.from_float(result) > value else result


def _center_data(
    center: np.ndarray, weights: np.ndarray, reference: np.ndarray,
    fifth_variation_upper: float,
) -> dict[str, Any]:
    jet = exact_full_action_jet_at_state(
        12, center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:], points=96,
    )
    hessian = np.asarray(jet.hessian, dtype=float)
    reduced = hessian[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    complement_values = np.delete(values, selected)
    numeric_gap = float(np.min(np.abs(complement_values - values[selected])))
    mixed = hessian[QDIM:, :QDIM]
    velocity = center[QDIM:2 * QDIM]
    rhs = np.concatenate((
        np.asarray(jet.gradient[:QDIM], dtype=float) - mixed[:QDIM] @ velocity,
        -mixed[QDIM:] @ velocity,
    ))
    b_center = float(psi @ rhs)
    direction = np.concatenate((np.zeros(QDIM), psi))
    cubics: list[float] = []
    for step in COMPLEX_STEPS:
        shifted = center.astype(complex) + 1j * step * direction
        shifted_jet = exact_full_action_jet_at_state(
            12,
            shifted[:QDIM], shifted[QDIM:2 * QDIM], shifted[2 * QDIM:],
            points=96,
        )
        derivative = np.imag(np.asarray(
            shifted_jet.hessian[QDIM:, QDIM:]
        )) / step
        cubics.append(float(psi @ derivative @ psi))
    _, reduced_weights, _, maximum_reduced_weight = metric_data()
    truncation = (
        float(fifth_variation_upper) * maximum_reduced_weight**5
        * max(COMPLEX_STEPS) ** 2 / 6.0
    )
    c_lower = _down(min(cubics) - truncation)
    c_upper = _up(max(cubics) + truncation)
    b_interval = (_down(b_center), _up(b_center))
    return {
        "selected_branch": selected,
        "numeric_selected_eigenvalue": float(values[selected]),
        "numeric_selected_gap": numeric_gap,
        "selected_vector": psi,
        "b_psi_center": b_center,
        "b_psi_center_interval": b_interval,
        "c_psi_complex_step_values": cubics,
        "c_psi_complex_step_truncation_upper": truncation,
        "c_psi_center_interval": (c_lower, c_upper),
        "maximum_reduced_weight": maximum_reduced_weight,
        "weights_match": weights.shape == (98,),
    }


def _maximal_closing_step(
    *, center: np.ndarray, weights: np.ndarray, signed_s: float,
    tube: float, ball: dict[str, Any], proof: dict[str, Any],
) -> dict[str, Any]:
    radius = float(ball["selected_midpoint_radius"])
    field = np.asarray(proof["field_action"], dtype=float)
    field_norm = float(np.linalg.norm(field))
    speed = float(ball["regularized_speed_upper"])
    jacobi = float(ball["pole_free_regularized_Jacobi_upper"])
    mismatch = float(proof["field_mismatch_upper"])
    upper = (radius - tube) / max(field_norm, speed, 1.0e-300)

    def trial(step: float) -> dict[str, Any]:
        exponent = jacobi * step
        if exponent >= 700.0:
            return {"closes": False, "root_use": math.inf}
        growth = math.exp(exponent)
        predictor_action = step * field
        stored_center = center + predictor_action / weights
        stored_action = (stored_center - center) * weights
        rounding = float(np.linalg.norm(stored_action - predictor_action))
        stored_norm = float(np.linalg.norm(stored_action))
        nonlinear = 0.5 * jacobi * speed * step**2 * growth
        new_tube = growth * (tube + step * mismatch) + nonlinear + rounding
        root_use = stored_norm + new_tube
        return {
            "closes": bool(root_use < radius),
            "root_use": root_use,
            "new_tube": new_tube,
            "stored_center": stored_center,
            "stored_step_norm": stored_norm,
            "rounding_defect": rounding,
            "growth": growth,
            "nonlinear_remainder": nonlinear,
        }

    upper_trial = trial(upper)
    if upper_trial["closes"]:
        feasible_upper = upper
    else:
        feasible = 0.0
        infeasible = upper
        for _ in range(100):
            midpoint = 0.5 * (feasible + infeasible)
            if midpoint in (feasible, infeasible):
                break
            if trial(midpoint)["closes"]:
                feasible = midpoint
            else:
                infeasible = midpoint
        feasible_upper = feasible
    selected = 0.5 * feasible_upper
    result = trial(selected)
    if not selected > 0.0 or not result["closes"]:
        raise ArithmeticError("no positive fresh-center descriptor step closes")
    return {
        **result,
        "closing_step_feasible_upper": feasible_upper,
        "selected_midpoint_step": selected,
        "step_selection_has_no_physical_role": True,
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing fresh-center continuation inputs: " + ", ".join(missing))
    prefix, recenter, line_record, majorants = (
        _load(path) for path in (PREFIX, RECENTER, LINE, MAJORANTS)
    )
    if not all(record.get("validation_passed") is True for record in (
        prefix, recenter, line_record, majorants,
    )):
        raise RuntimeError("validated C2 prefix and action parents required")
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
    exhaustion = "FRESH_CENTER_DENOMINATOR_SAFETY_LIMIT_REACHED"
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
            parent_radius = min(
                float(transferred["recentered_parent_action_radius"]) - path_upper,
                float(line_record["action_coordinate_ball_radius"])
                - float(transferred["old_root_to_new_center_action_distance_upper"])
                - path_upper,
            )
            try:
                ball = fresh_center_denominator_ball(
                    incoming_tube=_float_upper(tube),
                    parent_radius=parent_radius,
                    pf=pf,
                    launch=launch,
                    line=line,
                    center_c=tuple(center_data["c_psi_center_interval"]),
                    center_b=tuple(center_data["b_psi_center_interval"]),
                    center_lambda=_float_upper(abs(signed_s)),
                    center_state=center,
                    weights=weights,
                    coefficient_enclosure=_coefficient_enclosure,
                )
                proof = proof_center_field(
                    center=center,
                    weights=weights,
                    reference=reference,
                    signed_s=float(signed_s),
                    ball=ball,
                    generator=ball,
                )
                step = _maximal_closing_step(
                    center=center,
                    weights=weights,
                    signed_s=float(signed_s),
                    tube=_float_upper(tube),
                    ball=ball,
                    proof=proof,
                )
            except ArithmeticError as error:
                exhaustion = "FRESH_CENTER_EXACT_DENOMINATOR_PROOF_EXHAUSTED"
                witness = {
                    "message": str(error),
                    "incoming_tube_upper": _float_upper(tube),
                    "center_path_upper": path_upper,
                }
                break

            signed_step = Decimal.from_float(float(step["selected_midpoint_step"]))
            signed_end = signed_s + signed_step
            physical_u_increment = signed_end * signed_end - signed_s * signed_s
            if not physical_u_increment > 0:
                exhaustion = "FRESH_CENTER_DECIMAL_PHYSICAL_INCREMENT_NOT_POSITIVE"
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
            stored_step = Decimal.from_float(float(step["stored_step_norm"]))
            center_path += stored_step
            tube = Decimal.from_float(float(step["new_tube"]))
            center = np.asarray(step["stored_center"], dtype=float)
            signed_s = signed_end
            centers.append(center.copy())
            rows.append({
                "fresh_center_index": index + 1,
                "global_segment_index": int(prefix_cover["total_certified_segments"]) + index + 1,
                "selected_branch": int(center_data["selected_branch"]),
                "numeric_selected_gap": float(center_data["numeric_selected_gap"]),
                "numeric_selected_eigenvalue_not_used_as_descriptor": float(
                    center_data["numeric_selected_eigenvalue"]
                ),
                "c_psi_center_interval": list(center_data["c_psi_center_interval"]),
                "c_psi_complex_step_spread": max(center_data["c_psi_complex_step_values"])
                - min(center_data["c_psi_complex_step_values"]),
                "b_psi_center_interval": list(center_data["b_psi_center_interval"]),
                "incoming_tube_upper": float(ball["incoming_endpoint_tube_radius"]),
                "joint_feasibility_upper_radius": float(ball["joint_feasibility_upper_radius"]),
                "selected_ball_radius": float(ball["selected_midpoint_radius"]),
                "hard_self_consistency": float(ball["hard_self_consistency"]),
                "hard_denominator_lower": float(ball["hard_self_consistency_denominator_lower"]),
                "b_fixed_point_denominator_lower": float(ball["b_fixed_point_denominator_lower"]),
                "Delta_lower": float(ball["Delta_interval"][0]),
                "signed_lambda_step_decimal": str(signed_step),
                "physical_u_increment_decimal": str(physical_u_increment),
                "proper_time_increment_interval": [
                    _float_lower(proper_lower), _float_upper(proper_upper),
                ],
                "closing_step_feasible_upper": float(step["closing_step_feasible_upper"]),
                "selected_midpoint_step": float(step["selected_midpoint_step"]),
                "Jacobi_growth_upper": float(step["growth"]),
                "endpoint_tube_radius_upper": _float_upper(tube),
                "fresh_center_path_upper": _float_upper(center_path),
                "root_use_inside_selected_ball": float(step["root_use"]),
                "proof_center_is_physical_endpoint": False,
            })
        else:
            exhaustion = "FRESH_CENTER_DENOMINATOR_SAFETY_LIMIT_REACHED_WITH_CONTINUATION_OPEN"

    np.savez_compressed(
        DATA_RESULT,
        C2_fresh_center_predictor_centers=np.asarray(centers),
        state_weights=weights,
        branch_reference=reference,
    )
    accepted = len(rows)
    validation = {
        "validated_1064_segment_prefix_consumed": True,
        "fresh_center_exact_denominator_certifies_a_strict_extension": accepted > 0,
        "all_centers_retain_branch_24": accepted > 0 and all(
            row["selected_branch"] == 24 for row in rows
        ),
        "all_hard_and_b_fixed_point_denominators_are_positive": accepted > 0 and all(
            row["hard_denominator_lower"] > 0.0
            and row["b_fixed_point_denominator_lower"] > 0.0 for row in rows
        ),
        "all_c_b_Delta_lapse_and_radius_rate_margins_are_positive": accepted > 0 and all(
            row["c_psi_center_interval"][0] > 0.0
            and row["b_psi_center_interval"][0] > 0.0
            and row["Delta_lower"] > 0.0
            and row["proper_time_increment_interval"][0] > 0.0 for row in rows
        ),
        "all_selected_balls_strictly_contain_propagated_tubes": accepted > 0 and all(
            row["root_use_inside_selected_ball"] < row["selected_ball_radius"]
            for row in rows
        ),
        "binary64_soft_eigenvalue_not_used_as_signed_descriptor": True,
        "half_hard_and_half_c_proof_reserves_removed_not_physics_changed": True,
        "proof_exhaustion_not_promoted_to_event_or_canonical_stop": True,
        "no_selector_recurrence_scale_action_term_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_FRESH_CENTER_DENOMINATOR_CONTINUATION",
        "status": (
            "C2_FRESH_CENTER_EXACT_DENOMINATOR_EXTENSION_CERTIFIED"
            if passed else "C2_FRESH_CENTER_DENOMINATOR_EXTENSION_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_1064_SEGMENT_EXHAUSTION_WAS_CAUSED_BY_SUFFICIENT_ONE_HALF_"
            "PROOF_RESERVES;_THE_EXACT_POSITIVE_HARD_AND_REGULARIZED_"
            "DENOMINATORS_CERTIFY_A_STRICT_SAME_ACTION_EXTENSION"
        ),
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
        "proof_reserve_adjudication": {
            "old_hard_self_consistency_cap": "1/2_SUFFICIENT_ONLY",
            "new_hard_condition": "1-gap^-1*(D3_center+D4*r)*r>0",
            "old_c_sign_reserve": "ONE_HALF_OF_CERTIFIED_c_SUFFICIENT_ONLY",
            "new_c_condition": "inf_ball(c_psi)>0",
            "joint_radius": "MIDPOINT_BETWEEN_INCOMING_TUBE_AND_DERIVED_FEASIBILITY_SUPREMUM",
            "physical_parameter_added": False,
        },
        "adjudication": {
            "old_1064_box_exhaustion": "REMOVED_AS_PROOF_ONLY_HALF_MARGIN",
            "actual_later_event_or_canonical_stop": "NOT_REACHED",
            "mathematical_history_termination_claimed": False,
            "current_finite_route_blocker": exhaustion,
        },
        "exact_next_dependency": (
            "REPLACE_THE_REMAINING_SCALAR_TUBE_GROWTH_BY_A_MATRIX_LOHNER_OR_"
            "TAYLOR_JACOBI_ENCLOSURE,_OR_CLOSE_THE_ACTUAL_COMBINED_PROJECTED_"
            "MAXIMAL_C2_FORCE_TAIL;_DO_NOT_ADD_MORE_HALF_MARGIN_BOXES"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_SHARP_JACOBI_ENCLOSURE_OR_COMBINED_PROJECTED_TAIL",
            "Gate8": "LOCKED",
            "actual_later_event_or_canonical_stop": "OPEN",
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
    continuation = payload["continuation"]
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "additional_segments": continuation["additional_certified_segments"],
        "total_segments": continuation["total_certified_segments"],
        "final_tube": continuation["final_endpoint_tube_radius_upper"],
        "exhaustion": continuation["exhaustion_classification"],
    }, indent=2))


if __name__ == "__main__":
    main()
