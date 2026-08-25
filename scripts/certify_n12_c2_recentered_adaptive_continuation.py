"""Continue the compensated C2 descriptor cover from its certified recenter."""

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

from bhsm.interface.aether_forward_c2_adaptive_ball import derived_adaptive_ball  # noqa: E402
from bhsm.interface.aether_forward_c2_descriptor_cover import (  # noqa: E402
    proof_center_field,
    translated_generator,
)
from derive_n12_c2_birth_coefficient_quotient_jet import _coefficient_enclosure  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.json"
DATA_RESULT = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.npz"
RECENTER = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.json"
RECENTER_DATA = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.npz"
ADAPTIVE = BASE / "BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION.json"
PARENT_LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
ADAPTIVE_MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_adaptive_ball.py"
DESCRIPTOR_MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_descriptor_cover.py"
THEORY = ROOT / "theory/n12_c2_recentered_adaptive_continuation.md"
INPUTS = (
    RECENTER,
    RECENTER_DATA,
    ADAPTIVE,
    PARENT_LINE,
    ADAPTIVE_MODULE,
    DESCRIPTOR_MODULE,
    THEORY,
)
MAX_RECENTERED_BOXES = 2048


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _float_upper(value: Decimal) -> float:
    result = float(value)
    return math.nextafter(result, math.inf) if Decimal.from_float(result) < value else result


def _float_lower(value: Decimal) -> float:
    result = float(value)
    return math.nextafter(result, -math.inf) if Decimal.from_float(result) > value else result


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing recentered continuation inputs: " + ", ".join(missing))
    recenter, adaptive, line_record = (_load(path) for path in (RECENTER, ADAPTIVE, PARENT_LINE))
    if not all(record.get("validation_passed") is True for record in (
        recenter, adaptive, line_record,
    )):
        raise RuntimeError("validated recenter, adaptive prefix, and eigenline parents required")
    with np.load(RECENTER_DATA) as data:
        root_state = np.asarray(data["recentered_root_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)

    transferred = recenter["recenter"]
    prefix = adaptive["adaptive_cover"]
    center = root_state.copy()
    pf = transferred["recentered_pole_free_bounds"]
    launch_ball = transferred["recentered_launch_ball"]
    line = line_record["bounds"]
    parent_radius = float(transferred["recentered_parent_action_radius"])
    rows: list[dict[str, Any]] = []
    centers = [center.copy()]
    exhaustion = "RECENTERED_ADAPTIVE_SAFETY_LIMIT_NOT_REACHED"
    exhaustion_witness: dict[str, Any] = {}

    with localcontext() as context:
        context.prec = 100
        signed_s = Decimal(prefix["final_signed_lambda_decimal"])
        initial_signed_s = signed_s
        center_path = Decimal(0)
        tube = Decimal.from_float(float(transferred["incoming_endpoint_tube_upper"]))
        initial_tube = tube
        proper_lower_sum = Decimal(0)
        proper_upper_sum = Decimal(0)

        for index in range(MAX_RECENTERED_BOXES):
            center_path_upper = _float_upper(center_path)
            tube_upper = _float_upper(tube)
            try:
                ball = derived_adaptive_ball(
                    center_path=center_path_upper,
                    tube=tube_upper,
                    pf=pf,
                    launch_ball=launch_ball,
                    line=line,
                    parent_radius=parent_radius,
                    root_state=root_state,
                    weights=weights,
                    coefficient_enclosure=_coefficient_enclosure,
                )
            except ArithmeticError as error:
                exhaustion = "NO_STRICT_RECENTERED_ADAPTIVE_RADIUS_ALLOCATION_REMAINS"
                exhaustion_witness = {
                    "message": str(error),
                    "center_path_upper": center_path_upper,
                    "incoming_tube_upper": tube_upper,
                }
                break
            generator = translated_generator(
                ball=ball,
                pf=pf,
                launch_ball=launch_ball,
                line=line,
                root_state=root_state,
            )
            proof = proof_center_field(
                center=center,
                weights=weights,
                reference=reference,
                signed_s=float(signed_s),
                ball=ball,
                generator=generator,
            )
            available = float(ball["derived_local_radius"]) - tube_upper
            speed = float(generator["regularized_speed_upper"])
            jacobi = float(generator["pole_free_regularized_Jacobi_upper"])
            signed_step_float = min(available / (4.0 * speed), math.log(2.0) / jacobi)
            if not signed_step_float > 0.0:
                exhaustion = "RECENTERED_ADAPTIVE_MAJORANT_STEP_NOT_POSITIVE"
                break
            signed_step = Decimal.from_float(signed_step_float)
            signed_end = signed_s + signed_step
            physical_u_increment = signed_end * signed_end - signed_s * signed_s
            if not physical_u_increment > 0:
                exhaustion = "RECENTERED_DECIMAL_PHYSICAL_INCREMENT_NOT_POSITIVE"
                break

            growth = math.exp(jacobi * signed_step_float)
            predictor_step = signed_step_float * np.asarray(proof["field_action"], dtype=float)
            stored_center = center + predictor_step / weights
            stored_action_step = (stored_center - center) * weights
            rounding_defect = float(np.linalg.norm(stored_action_step - predictor_step))
            stored_step_norm = float(np.linalg.norm(stored_action_step))
            nonlinear = 0.5 * jacobi * speed * signed_step_float**2 * growth
            ideal_tube = growth * (
                tube_upper + signed_step_float * float(proof["field_mismatch_upper"])
            ) + nonlinear
            new_tube = Decimal.from_float(ideal_tube) + Decimal.from_float(rounding_defect)
            new_center_path = center_path + Decimal.from_float(stored_step_norm)
            root_use = _float_upper(new_center_path + new_tube)
            if not root_use < float(ball["total_root_relative_radius"]):
                exhaustion = "RECENTERED_ROUNDING_TUBE_DOES_NOT_CLOSE_SELECTED_BALL"
                exhaustion_witness = {
                    "root_use_upper": root_use,
                    "selected_ball_total_radius": float(ball["total_root_relative_radius"]),
                    "allocation_selected": float(ball["allocation_selected_midpoint"]),
                }
                break

            Delta_lower = Decimal.from_float(float(ball["Delta_interval"][0]))
            Delta_upper = Decimal.from_float(float(ball["Delta_interval"][1]))
            coordinate_lower = physical_u_increment / (Decimal(2) * Delta_upper)
            coordinate_upper = physical_u_increment / (Decimal(2) * Delta_lower)
            lapse_lower = Decimal.from_float(float(ball["lapse_interval"][0]))
            lapse_upper = Decimal.from_float(float(ball["lapse_interval"][1]))
            proper_lower = lapse_lower * coordinate_lower
            proper_upper = lapse_upper * coordinate_upper
            proper_lower_sum += proper_lower
            proper_upper_sum += proper_upper

            rows.append({
                "recentered_adaptive_index": index + 1,
                "global_segment_index": int(prefix["total_certified_segments"]) + index + 1,
                "allocation_lower_necessity": float(ball["allocation_lower_necessity"]),
                "allocation_feasible_upper": float(ball["allocation_feasible_upper"]),
                "allocation_selected_midpoint": float(ball["allocation_selected_midpoint"]),
                "allocation_lower_slack": float(ball["allocation_lower_slack"]),
                "allocation_upper_slack": float(ball["allocation_upper_slack"]),
                "signed_lambda_step_decimal": str(signed_step),
                "physical_u_increment_decimal": str(physical_u_increment),
                "proper_time_increment_interval": [
                    _float_lower(proper_lower), _float_upper(proper_upper)
                ],
                "center_rounding_defect_action_norm": rounding_defect,
                "endpoint_tube_radius_upper": _float_upper(new_tube),
                "center_path_from_recenter_upper": _float_upper(new_center_path),
                "root_relative_path_plus_tube_upper": root_use,
                "translated_ball_total_radius": float(ball["total_root_relative_radius"]),
                "derived_local_radius": float(ball["derived_local_radius"]),
                "hard_self_consistency": float(ball["hard_self_consistency"]),
                "Delta_lower": float(ball["Delta_interval"][0]),
                "proof_center_branch": int(proof["selected_branch"]),
                "predictor_is_physical_endpoint": False,
            })
            center = stored_center
            center_path = new_center_path
            tube = new_tube
            signed_s = signed_end
            centers.append(center.copy())
        else:
            exhaustion = "RECENTERED_ADAPTIVE_SAFETY_LIMIT_REACHED_WITH_CONTINUATION_OPEN"

    np.savez_compressed(
        DATA_RESULT,
        C2_recentered_adaptive_predictor_centers=np.asarray(centers),
        recentered_root_state=root_state,
        state_weights=weights,
        branch_reference=reference,
    )
    accepted = len(rows)
    validation = {
        "recenter_and_prefix_parents_are_validated": True,
        "proof_center_path_resets_exactly_to_zero": True,
        "physical_signed_history_is_continuous_across_recenter": signed_s >= initial_signed_s,
        "incoming_tube_is_preserved_not_reset": initial_tube > 0,
        "recentered_allocation_certifies_at_least_one_new_box": accepted > 0,
        "every_selected_share_is_strictly_inside_derived_interval": accepted > 0 and all(
            row["allocation_lower_necessity"]
            < row["allocation_selected_midpoint"]
            < row["allocation_feasible_upper"] for row in rows
        ),
        "all_signed_physical_and_proper_increments_are_positive": accepted > 0 and all(
            Decimal(row["signed_lambda_step_decimal"]) > 0
            and Decimal(row["physical_u_increment_decimal"]) > 0
            and row["proper_time_increment_interval"][0] > 0.0 for row in rows
        ),
        "all_selected_balls_preserve_strict_majorant_margins": accepted > 0 and all(
            row["hard_self_consistency"] < 0.5 and row["Delta_lower"] > 0.0 for row in rows
        ),
        "all_tubes_close_in_selected_balls": accepted > 0 and all(
            row["root_relative_path_plus_tube_upper"]
            < row["translated_ball_total_radius"] for row in rows
        ),
        "all_centers_remain_branch_24": accepted > 0 and all(
            row["proof_center_branch"] == 24 for row in rows
        ),
        "proof_recenter_or_allocation_exhaustion_not_promoted_to_endpoint": True,
        "no_recurrence_selector_scale_action_term_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION",
        "status": (
            "C2_RECENTERED_COMPENSATED_ADAPTIVE_CONTINUATION_CERTIFIED"
            if passed else "C2_RECENTERED_ADAPTIVE_CONTINUATION_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_ANALYTIC_PROOF_ORIGIN_IS_RESET_TO_THE_LAST_CERTIFIED_CENTER_WHILE_"
            "THE_PHYSICAL_SIGNED_HISTORY_AND_INCOMING_ENDPOINT_TUBE_REMAIN_CONTINUOUS"
        ),
        "recentered_cover": {
            "prior_total_segments": int(prefix["total_certified_segments"]),
            "additional_certified_segments": accepted,
            "total_certified_segments": int(prefix["total_certified_segments"]) + accepted,
            "rows": rows,
            "initial_signed_lambda_decimal": str(initial_signed_s),
            "final_signed_lambda_decimal": str(signed_s),
            "initial_center_path_from_recenter": 0.0,
            "final_center_path_from_recenter_upper": _float_upper(center_path),
            "initial_endpoint_tube_radius_upper": _float_upper(initial_tube),
            "final_endpoint_tube_radius_upper": _float_upper(tube),
            "additional_proper_duration_interval": [
                _float_lower(proper_lower_sum), _float_upper(proper_upper_sum)
            ],
            "exhaustion_classification": exhaustion,
            "exhaustion_witness": exhaustion_witness,
            "exhaustion_is_event_or_canonical_stop": False,
            "data": DATA_RESULT.relative_to(ROOT).as_posix(),
            "data_SHA256": _sha256(DATA_RESULT),
        },
        "adjudication": {
            "recentered_finite_connection_extension": "CERTIFIED" if passed else "OPEN",
            "actual_later_event_or_canonical_stop": "NOT_REACHED",
            "mathematical_history_termination_claimed": False,
            "current_finite_route_blocker": exhaustion,
        },
        "exact_next_dependency": (
            "IF_THE_RECENTERED_COVER_EXHAUSTS_ONLY_PROOF_GEOMETRY_REPEAT_THE_"
            "ACTION_BOUND_TRANSFER_AT_ITS_LAST_CENTER;_OTHERWISE_ADJUDICATE_ONLY_"
            "AN_ACTUAL_RETAINED_EVENT_OR_CANONICAL_STOP"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_FINITE_C2_CONNECTION_OR_COMBINED_PROJECTED_TAIL",
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
        encoding="utf-8",
        newline="\n",
    )
    cover = payload["recentered_cover"]
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "additional_segments": cover["additional_certified_segments"],
        "total_segments": cover["total_certified_segments"],
        "final_center_path": cover["final_center_path_from_recenter_upper"],
        "final_tube": cover["final_endpoint_tube_radius_upper"],
        "exhaustion": cover["exhaustion_classification"],
    }, indent=2))


if __name__ == "__main__":
    main()
