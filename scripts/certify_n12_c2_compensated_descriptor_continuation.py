"""Continue the C2 cover with a compensated descriptor and center enclosure."""

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

from bhsm.interface.aether_forward_c2_descriptor_cover import (  # noqa: E402
    proof_center_field,
    translated_ball_bounds,
    translated_generator,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION.json"
DATA_RESULT = BASE / "BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION.npz"
EXTENDED = BASE / "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT.json"
EXTENDED_DATA = BASE / "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT.npz"
POLE_FREE = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
PARENT_LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
PARENT_ACTION = BASE / "BHSM_N12_FINITE_TERMINAL_ACTION_BALL_MAJORANTS.json"
MARGINS = BASE / "BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_descriptor_cover.py"
THEORY = ROOT / "theory/n12_c2_compensated_descriptor_continuation.md"
INPUTS = (
    EXTENDED,
    EXTENDED_DATA,
    POLE_FREE,
    LAUNCH,
    PARENT_LINE,
    PARENT_ACTION,
    MARGINS,
    CANDIDATE,
    MODULE,
    THEORY,
)
MAX_COMPENSATED_BOXES = 256


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _float_upper(value: Decimal) -> float:
    result = float(value)
    if Decimal.from_float(result) < value:
        result = math.nextafter(result, math.inf)
    return result


def _float_lower(value: Decimal) -> float:
    result = float(value)
    if Decimal.from_float(result) > value:
        result = math.nextafter(result, -math.inf)
    return result


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing compensated continuation inputs: " + ", ".join(missing))
    extended, pole_free, launch, line_record, action, margins = (
        _load(path) for path in (
            EXTENDED, POLE_FREE, LAUNCH, PARENT_LINE, PARENT_ACTION, MARGINS,
        )
    )
    if not all(record.get("validation_passed") is True for record in (
        extended, pole_free, launch, line_record, action, margins,
    )):
        raise RuntimeError("validated compensated continuation parents required")

    with np.load(EXTENDED_DATA) as data:
        prior_centers = np.asarray(data["C2_predictor_centers"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    with np.load(CANDIDATE) as data:
        root_state = np.asarray(data["state"], dtype=float)[:98]

    center = prior_centers[-1].copy()
    pf = pole_free["bounds"]
    launch_ball = launch["launch_ball"]
    line = line_record["bounds"]
    parent_radius = float(action["action_coordinate_ball_radius"])
    prior_cover = extended["cover"]

    rows: list[dict[str, Any]] = []
    new_centers = [center.copy()]
    exhaustion = "COMPENSATED_SAFETY_LIMIT_NOT_REACHED"
    with localcontext() as context:
        context.prec = 80
        signed_s = Decimal(str(prior_cover["final_signed_lambda"]))
        center_path = Decimal(str(prior_cover["final_center_path_upper"]))
        tube = Decimal(str(prior_cover["final_endpoint_tube_radius_upper"]))
        proper_duration_lower = Decimal(0)
        proper_duration_upper = Decimal(0)

        for index in range(MAX_COMPENSATED_BOXES):
            center_path_upper = _float_upper(center_path)
            tube_upper = _float_upper(tube)
            ball = translated_ball_bounds(
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
            if not (
                float(ball["derived_local_radius"]) > tube_upper
                and float(ball["hard_self_consistency"]) < 0.5
                and float(ball["Delta_interval"][0]) > 0.0
                and float(ball["lapse_interval"][0]) > 0.0
                and float(ball["D_tau_log_R4_interval"][0]) > 0.0
            ):
                exhaustion = "CURRENT_MAJORANTS_DO_NOT_CERTIFY_A_NEXT_COMPENSATED_BALL"
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
                exhaustion = "CURRENT_COMPENSATED_MAJORANT_STEP_NOT_POSITIVE"
                break
            signed_step = Decimal.from_float(signed_step_float)
            signed_end = signed_s + signed_step
            physical_u_increment = signed_end * signed_end - signed_s * signed_s
            if physical_u_increment <= 0:
                exhaustion = "DECIMAL_DESCRIPTOR_INCREMENT_NOT_POSITIVE"
                break

            growth = math.exp(jacobi * signed_step_float)
            predictor_step = signed_step_float * np.asarray(proof["field_action"], dtype=float)
            intended_center = center + predictor_step / weights
            stored_action_step = (intended_center - center) * weights
            center_rounding_defect = float(np.linalg.norm(stored_action_step - predictor_step))
            stored_action_step_norm = float(np.linalg.norm(stored_action_step))
            nonlinear = 0.5 * jacobi * speed * signed_step_float**2 * growth
            ideal_tube_float = growth * (
                tube_upper + signed_step_float * float(proof["field_mismatch_upper"])
            ) + nonlinear
            new_tube = (
                Decimal.from_float(ideal_tube_float)
                + Decimal.from_float(center_rounding_defect)
            )
            new_center_path = center_path + Decimal.from_float(stored_action_step_norm)
            root_use_upper = _float_upper(new_center_path + new_tube)
            if not root_use_upper < float(ball["total_root_relative_radius"]):
                exhaustion = "COMPENSATED_ROUNDING_TUBE_DOES_NOT_CLOSE_NEXT_BALL"
                break

            Delta_lower = Decimal.from_float(float(ball["Delta_interval"][0]))
            Delta_upper = Decimal.from_float(float(ball["Delta_interval"][1]))
            coordinate_lower = physical_u_increment / (Decimal(2) * Delta_upper)
            coordinate_upper = physical_u_increment / (Decimal(2) * Delta_lower)
            lapse_lower = Decimal.from_float(float(ball["lapse_interval"][0]))
            lapse_upper = Decimal.from_float(float(ball["lapse_interval"][1]))
            proper_lower = lapse_lower * coordinate_lower
            proper_upper = lapse_upper * coordinate_upper
            proper_duration_lower += proper_lower
            proper_duration_upper += proper_upper

            rows.append({
                "compensated_index_after_436_segment_prefix": index + 1,
                "signed_lambda_start_decimal": str(signed_s),
                "signed_lambda_step_decimal": str(signed_step),
                "signed_lambda_end_decimal": str(signed_end),
                "physical_u_increment_decimal": str(physical_u_increment),
                "proper_time_increment_interval": [
                    _float_lower(proper_lower), _float_upper(proper_upper)
                ],
                "center_rounding_defect_action_norm": center_rounding_defect,
                "stored_center_action_step_norm": stored_action_step_norm,
                "ideal_tube_before_rounding_defect": ideal_tube_float,
                "endpoint_tube_radius_upper": _float_upper(new_tube),
                "center_path_upper": _float_upper(new_center_path),
                "root_relative_path_plus_tube_upper": root_use_upper,
                "translated_ball_total_radius": float(ball["total_root_relative_radius"]),
                "translated_ball_local_radius": float(ball["derived_local_radius"]),
                "Delta_lower": float(ball["Delta_interval"][0]),
                "hard_self_consistency": float(ball["hard_self_consistency"]),
                "proof_center_branch": int(proof["selected_branch"]),
                "predictor_is_physical_endpoint": False,
            })
            center = intended_center
            center_path = new_center_path
            tube = new_tube
            signed_s = signed_end
            new_centers.append(center.copy())
        else:
            exhaustion = "COMPENSATED_SAFETY_LIMIT_REACHED_WITH_CONTINUATION_STILL_OPEN"

    np.savez_compressed(
        DATA_RESULT,
        C2_compensated_predictor_centers=np.asarray(new_centers),
        state_weights=weights,
        branch_reference=reference,
    )
    accepted = len(rows)
    validation = {
        "extended_binary64_parent_is_validated": True,
        "at_least_one_compensated_box_is_certified": accepted > 0,
        "all_decimal_signed_and_physical_u_increments_are_positive": accepted > 0 and all(
            Decimal(row["signed_lambda_step_decimal"]) > 0
            and Decimal(row["physical_u_increment_decimal"]) > 0
            for row in rows
        ),
        "all_proper_time_lower_bounds_are_positive": accepted > 0 and all(
            row["proper_time_increment_interval"][0] > 0.0 for row in rows
        ),
        "all_rounding_defects_are_added_to_tubes": accepted > 0 and all(
            row["endpoint_tube_radius_upper"]
            >= row["ideal_tube_before_rounding_defect"]
            + row["center_rounding_defect_action_norm"]
            for row in rows
        ),
        "all_compensated_tubes_close": accepted > 0 and all(
            row["root_relative_path_plus_tube_upper"]
            < row["translated_ball_total_radius"] for row in rows
        ),
        "all_selected_centers_remain_branch_24": accepted > 0 and all(
            row["proof_center_branch"] == 24 for row in rows
        ),
        "arithmetic_or_majorant_exhaustion_not_promoted_to_endpoint": True,
        "no_recurrence_selector_scale_action_term_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION",
        "status": (
            "C2_COMPENSATED_DESCRIPTOR_CONTINUATION_CERTIFIED_TO_NEXT_MAJORANT_EXHAUSTION"
            if passed else "C2_COMPENSATED_DESCRIPTOR_CONTINUATION_NOT_CERTIFIED"
        ),
        "classification": (
            "DECIMAL_DESCRIPTOR_AND_TUBE_ACCUMULATION_WITH_EXPLICIT_CENTER_"
            "ROUNDING_DEFECT_ENCLOSURE_CONTINUES_THE_SAME_C2_HISTORY_BEYOND_"
            "THE_BINARY64_SIGNED_ACCUMULATOR_LIMIT_WITHOUT_CHANGING_THE_ACTION"
        ),
        "compensated_cover": {
            "prior_total_segments": extended["cover"]["certified_total_segment_count"],
            "additional_certified_segments": accepted,
            "total_certified_segments": extended["cover"]["certified_total_segment_count"] + accepted,
            "rows": rows,
            "final_signed_lambda_decimal": str(signed_s),
            "additional_proper_duration_interval": [
                _float_lower(proper_duration_lower),
                _float_upper(proper_duration_upper),
            ],
            "final_center_path_upper": _float_upper(center_path),
            "final_endpoint_tube_radius_upper": _float_upper(tube),
            "exhaustion_classification": exhaustion,
            "exhaustion_is_event_or_canonical_stop": False,
            "data": DATA_RESULT.relative_to(ROOT).as_posix(),
            "data_SHA256": _sha256(DATA_RESULT),
        },
        "method": {
            "decimal_precision": 80,
            "signed_descriptor_and_physical_u": "DECIMAL_EXACT_FROM_BINARY64_STEP_BOUNDS",
            "center_storage": "BINARY64_WITH_ACTION_NORM_ROUNDING_DEFECT_ADDED_TO_TUBE",
            "center_path_and_tube_accumulators": "DECIMAL_WITH_OUTWARD_BINARY64_EXPORT",
            "action_jet_and_majorants": "UNCHANGED_RETAINED_N12_OBJECTS",
        },
        "adjudication": {
            "binary64_signed_accumulator_blocker": "REMOVED",
            "actual_later_event_or_canonical_stop": "NOT_REACHED",
            "current_finite_route_blocker": exhaustion,
            "mathematical_history_termination_claimed": False,
        },
        "exact_next_dependency": (
            "SHARPEN_OR_RECENTER_THE_CURRENT_TRANSLATED_BALL_AND_JACOBI_"
            "MAJORANTS_AT_THE_COMPENSATED_EXHAUSTION,_OR_CLOSE_THE_DIRECT_"
            "COMBINED_PROJECTED_FORCE_TAIL;_DO_NOT_PROMOTE_PROOF_TUBE_"
            "EXHAUSTION_TO_A_PHYSICAL_STOP"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_RECENTERED_C2_CONTINUATION_OR_COMBINED_PROJECTED_TAIL",
            "Gate8": "LOCKED",
            "compensated_C2_continuation": "CERTIFIED" if passed else "OPEN",
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
    cover = payload["compensated_cover"]
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "additional_segments": cover["additional_certified_segments"],
        "total_segments": cover["total_certified_segments"],
        "exhaustion": cover["exhaustion_classification"],
    }, indent=2))


if __name__ == "__main__":
    main()
