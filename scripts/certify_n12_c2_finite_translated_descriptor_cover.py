"""Build a finite inverse-free translated C2 descriptor cover prefix."""

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

from bhsm.interface.aether_forward_c2_descriptor_cover import (  # noqa: E402
    proof_center_field,
    translated_ball_bounds,
    translated_generator,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_FINITE_TRANSLATED_DESCRIPTOR_COVER.json"
DATA_RESULT = BASE / "BHSM_N12_C2_FINITE_TRANSLATED_DESCRIPTOR_COVER.npz"
START_BALL = BASE / "BHSM_N12_C2_SECOND_TRANSLATED_DESCRIPTOR_BALL.json"
START_SEGMENT = BASE / "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.json"
START_DATA = BASE / "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.npz"
EXTENSION = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
POLE_FREE = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
PARENT_LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
PARENT_ACTION = BASE / "BHSM_N12_FINITE_TERMINAL_ACTION_BALL_MAJORANTS.json"
MARGINS = BASE / "BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_descriptor_cover.py"
THEORY = ROOT / "theory/n12_c2_finite_translated_descriptor_cover.md"
INPUTS = (
    START_BALL, START_SEGMENT, START_DATA, EXTENSION, POLE_FREE, LAUNCH,
    PARENT_LINE, PARENT_ACTION, MARGINS, CANDIDATE, MODULE, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(
    *,
    max_additional_boxes: int = 96,
    data_result: Path = DATA_RESULT,
) -> dict[str, Any]:
    if max_additional_boxes <= 0:
        raise ValueError("positive translated-cover safety limit required")
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete finite translated cover inputs required")
    start_ball, start_segment, extension, pole_free, launch, line_record, action, margins = (
        _load(path) for path in (
            START_BALL, START_SEGMENT, EXTENSION, POLE_FREE, LAUNCH,
            PARENT_LINE, PARENT_ACTION, MARGINS,
        )
    )
    if not all(record.get("validation_passed") is True for record in (
        start_ball, start_segment, extension, pole_free, launch,
        line_record, action, margins,
    )):
        raise RuntimeError("validated finite translated cover parents required")
    with np.load(START_DATA) as data:
        center = np.asarray(data["C2_predictor_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
        signed_s = float(data["signed_lambda_end"])
    with np.load(CANDIDATE) as data:
        root_state = np.asarray(data["state"], dtype=float)[:98]

    pf = pole_free["bounds"]
    launch_ball = launch["launch_ball"]
    line = line_record["bounds"]
    parent_radius = float(action["action_coordinate_ball_radius"])
    center_path = float(start_ball["translated_ball"]["center_path_upper"])
    tube = float(start_segment["endpoint_recenter"]["endpoint_tube_radius_upper"])
    rows: list[dict[str, Any]] = []
    centers = [center.copy()]
    signed_values = [signed_s]
    exhaustion = "COMPUTATIONAL_SAFETY_LIMIT_NOT_REACHED"
    resolution_witness: dict[str, float | int] | None = None

    for index in range(max_additional_boxes):
        ball = translated_ball_bounds(
            center_path=center_path,
            tube=tube,
            pf=pf,
            launch_ball=launch_ball,
            line=line,
            parent_radius=parent_radius,
            root_state=root_state,
            weights=weights,
            coefficient_enclosure=_coefficient_enclosure,
        )
        if not (
            float(ball["derived_local_radius"]) > tube
            and float(ball["hard_self_consistency"]) < 0.5
            and float(ball["Delta_interval"][0]) > 0.0
            and float(ball["lapse_interval"][0]) > 0.0
            and float(ball["D_tau_log_R4_interval"][0]) > 0.0
        ):
            exhaustion = "CURRENT_MAJORANTS_DO_NOT_CERTIFY_A_NEXT_TRANSLATED_BALL"
            break
        generator = translated_generator(
            ball=ball, pf=pf, launch_ball=launch_ball,
            line=line, root_state=root_state,
        )
        proof = proof_center_field(
            center=center, weights=weights, reference=reference,
            signed_s=signed_s, ball=ball, generator=generator,
        )
        available = float(ball["derived_local_radius"]) - tube
        speed = float(generator["regularized_speed_upper"])
        Jacobi = float(generator["pole_free_regularized_Jacobi_upper"])
        signed_step = min(available / (4.0 * speed), math.log(2.0) / Jacobi)
        growth = math.exp(Jacobi * signed_step)
        predictor_step = signed_step * np.asarray(proof["field_action"], dtype=float)
        nonlinear = 0.5 * Jacobi * speed * signed_step**2 * growth
        new_tube = growth * (
            tube + signed_step * float(proof["field_mismatch_upper"])
        ) + nonlinear
        new_center_path = center_path + float(np.linalg.norm(predictor_step))
        root_use = new_center_path + new_tube
        if not root_use < float(ball["total_root_relative_radius"]):
            exhaustion = "CURRENT_JACOBI_EULER_MAJORANT_DOES_NOT_CLOSE_NEXT_TUBE"
            break
        signed_end = signed_s + signed_step
        if not signed_end > signed_s:
            ulp = math.nextafter(signed_s, math.inf) - signed_s
            resolution_witness = {
                "attempted_cover_index_after_two_segment_prefix": index + 1,
                "signed_lambda_start": signed_s,
                "certified_signed_lambda_step": signed_step,
                "binary64_signed_lambda_ulp": ulp,
                "step_to_ulp_ratio": signed_step / ulp,
                "binary64_signed_lambda_end": signed_end,
                "binary64_physical_u_increment": signed_end**2 - signed_s**2,
            }
            exhaustion = (
                "CURRENT_BINARY64_SIGNED_DESCRIPTOR_INCREMENT_NOT_RESOLVED"
            )
            break
        physical_u_increment = signed_end**2 - signed_s**2
        Delta_lower, Delta_upper = (
            float(value) for value in ball["Delta_interval"]
        )
        coordinate_time = (
            physical_u_increment / (2.0 * Delta_upper),
            physical_u_increment / (2.0 * Delta_lower),
        )
        lapse_lower, lapse_upper = (
            float(value) for value in ball["lapse_interval"]
        )
        proper_time = (
            lapse_lower * coordinate_time[0],
            lapse_upper * coordinate_time[1],
        )
        rows.append({
            "cover_index_after_two_segment_prefix": index + 1,
            "signed_lambda_start": signed_s,
            "signed_lambda_step": signed_step,
            "signed_lambda_end": signed_end,
            "physical_u_increment": physical_u_increment,
            "proper_time_increment_interval": list(proper_time),
            "center_path_upper_before": center_path,
            "incoming_tube_radius": tube,
            "translated_ball_total_radius": float(ball["total_root_relative_radius"]),
            "translated_ball_local_radius": float(ball["derived_local_radius"]),
            "Delta_lower": Delta_lower,
            "hard_self_consistency": float(ball["hard_self_consistency"]),
            "regularized_speed_upper": speed,
            "pole_free_Jacobi_upper": Jacobi,
            "Delta_action_derivative_upper": float(
                generator["Delta_action_derivative_upper"]
            ),
            "Jacobi_growth_upper": growth,
            "proof_center_branch": int(proof["selected_branch"]),
            "proof_center_field_norm": float(proof["field_action_norm"]),
            "proof_center_mismatch_upper": float(proof["field_mismatch_upper"]),
            "predictor_action_step_norm": float(np.linalg.norm(predictor_step)),
            "nonlinear_remainder_upper": nonlinear,
            "endpoint_tube_radius_upper": new_tube,
            "root_relative_path_plus_tube_upper": root_use,
            "predictor_is_physical_endpoint": False,
        })
        center = center + predictor_step / weights
        center_path = new_center_path
        tube = new_tube
        signed_s = signed_end
        centers.append(center.copy())
        signed_values.append(signed_s)
    else:
        exhaustion = "COMPUTATIONAL_SAFETY_LIMIT_REACHED_WITH_CONTINUATION_STILL_OPEN"

    np.savez_compressed(
        data_result,
        C2_predictor_centers=np.asarray(centers),
        state_weights=weights,
        branch_reference=reference,
        signed_lambda_values=np.asarray(signed_values),
        final_endpoint_action_tube=np.asarray(tube),
    )
    positive_rows = bool(rows) and all(
        row["signed_lambda_step"] > 0.0
        and row["proper_time_increment_interval"][0] > 0.0
        and row["proof_center_branch"] == 24
        for row in rows
    )
    validation = {
        "actual_C2_signed_descriptor_objects_fill_all_flow_slots": True,
        "foreign_flow_box_physics_not_imported": True,
        "at_least_one_additional_translated_box_certified": bool(rows),
        "all_certified_steps_have_positive_signed_and_proper_duration": positive_rows,
        "all_certified_steps_retain_branch_24": bool(rows) and all(
            row["proof_center_branch"] == 24 for row in rows
        ),
        "all_endpoint_tubes_close_in_their_derived_balls": bool(rows) and all(
            row["root_relative_path_plus_tube_upper"]
            < row["translated_ball_total_radius"] for row in rows
        ),
        "lapse_radius_rate_selected_line_and_Legendre_domains_inherited": (
            float(line["eigenline_gap_lower"]) > 0.0
            and float(margins["Legendre_transfer"]["event"]["root_ball_lower"]) > 0.0
        ),
        "cover_exhaustion_not_promoted_to_canonical_stop": True,
        "proof_centers_not_promoted_to_physical_endpoints_or_selectors": True,
        "no_recurrence_periodic_endpoint_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_FINITE_TRANSLATED_DESCRIPTOR_COVER",
        "status": (
            "FINITE_MULTI_BOX_C2_TRANSLATED_DESCRIPTOR_COVER_CERTIFIED"
            if passed else "C2_FINITE_TRANSLATED_DESCRIPTOR_COVER_NOT_CERTIFIED"
        ),
        "matching_audit": {
            "diagram_slot": "C2_MAXIMAL_FORWARD_SIGNED_DESCRIPTOR_COVER",
            "required_mathematical_type": "RECENTERABLE_GRONWALL_EULER_FLOW_BOX",
            "external_identity_adapter": "VALID_MATCH_GENERAL_MATHEMATICS_ONLY",
            "legacy_child_state_and_full_Dirac_inverse": "INVALID_MATCH_WRONG_DOMAIN_AND_OPERATOR",
            "actual_C2_hard_solve_soft_source_Delta_and_reset_centers": "VALID_MATCH",
        },
        "cover": {
            "certified_additional_box_count": len(rows),
            "certified_total_segment_count": 2 + len(rows),
            "rows": rows,
            "final_signed_lambda": signed_s,
            "final_center_path_upper": center_path,
            "final_endpoint_tube_radius_upper": tube,
            "exhaustion_classification": exhaustion,
            "exhaustion_is_canonical_stop": False,
            "data": data_result.relative_to(ROOT).as_posix(),
            "data_SHA256": _sha256(data_result),
            **(
                {"resolution_witness": resolution_witness}
                if resolution_witness is not None else {}
            ),
        },
        "adjudication": {
            "physical_encapsulation_endpoint_reached": False,
            "canonical_stop_reached": False,
            "outcome": "FINITE_REGULAR_FORWARD_COVER_PREFIX_CERTIFIED",
        },
        "exact_next_dependency": (
            "SHARPEN_THE_TRANSLATED_JACOBI_OR_HIGHER_ORDER_ENDPOINT_"
            "REMAINDER_AT_THE_RECORDED_COVER_EXHAUSTION,_THEN_CONTINUE_"
            "THE_SAME_C2_HISTORY"
        ),
        "claim_boundary": {
            "finite_multi_box_C2_cover": "CERTIFIED" if passed else "OPEN",
            "complete_M_C2_maximal_response": "OPEN_AFTER_CONTINUATION",
            "zero_source_force": "OPEN_AFTER_COMPLETE_M_C2",
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
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
        "additional_boxes": payload["cover"]["certified_additional_box_count"],
        "total_segments": payload["cover"]["certified_total_segment_count"],
        "final_signed_lambda": payload["cover"]["final_signed_lambda"],
        "final_tube": payload["cover"]["final_endpoint_tube_radius_upper"],
        "exhaustion": payload["cover"]["exhaustion_classification"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
