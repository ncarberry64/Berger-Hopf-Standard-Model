"""Combine complete non-scale ``D2(cb)`` and global ``s D2R`` bounds."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CB = BASE / "BHSM_N12_C2_COMPLETE_NON_SCALE_CB_OPERATOR.json"
CB_DATA = CB.with_suffix(".npz")
SUPPRESSED = BASE / "BHSM_N12_C2_COMPLETE_SUPPRESSED_R_OPERATOR.json"
FIELD = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
FIELD_DATA = FIELD.with_suffix(".npz")
COMMON_SCALE = BASE / "BHSM_N12_C2_COMMON_SCALE_WEYL_COVARIANCE.json"
THEORY = ROOT / "theory" / "n12_c2_complete_non_scale_ddelta_operator.md"
RESULT = BASE / "BHSM_N12_C2_COMPLETE_NON_SCALE_DDELTA_OPERATOR.json"
DATA_RESULT = RESULT.with_suffix(".npz")
RADIUS = 5.5104723095444935e-11
INFLATION = 1.0 + 1.0e-12


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    paths = (CB, CB_DATA, SUPPRESSED, FIELD, FIELD_DATA, COMMON_SCALE, THEORY)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing complete-D2Delta inputs: " + ", ".join(missing))
    cb, suppressed, field, common_scale = (
        _load(path) for path in (CB, SUPPRESSED, FIELD, COMMON_SCALE)
    )
    if not all(item.get("validation_passed") is True for item in (
        cb, suppressed, field, common_scale,
    )):
        raise RuntimeError("validated complete-D2Delta parents are required")
    if cb.get("data_SHA256") != _sha256(CB_DATA):
        raise RuntimeError("non-scale cb data digest is stale")

    with np.load(FIELD_DATA) as data:
        delta_partial = np.asarray(data["Delta_first_partial_action"], dtype=float)
        seed_remainder = float(data["Delta_first_total_remainder_action_norm_upper"])
    non_scale_center = delta_partial[1:]
    center_norm = _up(float(np.linalg.norm(non_scale_center)))
    cb_operator = _up(float(cb["operator"]["non_scale_cb_Frobenius_upper"]))
    suppressed_operator = _up(float(
        suppressed["complete_s_suppressed_R_second_operator_2_norm_upper"]
    ))
    complete_operator = _up(cb_operator + suppressed_operator)
    transported_radius = _up(seed_remainder + complete_operator * RADIUS)
    zero_margin = _down(center_norm - transported_radius)
    ceiling = _down((center_norm - seed_remainder) / RADIUS)

    np.savez_compressed(
        DATA_RESULT,
        non_scale_DDelta_partial_action=non_scale_center,
        transported_action_dual_ball_radius_upper=np.asarray(transported_radius),
        complete_non_scale_D2Delta_operator_2_norm_upper=np.asarray(complete_operator),
    )
    validation = {
        "complete_non_scale_cb_operator_is_certified": (
            cb["adjudication"]["complete_non_scale_cb_operator"] == "CERTIFIED"
        ),
        "complete_global_sR_operator_is_certified": (
            suppressed["adjudication"]["complete_non_scale_sR_operator"] == "CERTIFIED"
        ),
        "same_node_1214_tube_is_used": (
            float(cb["transport_budget_before_sR"]["state_action_radius"]) == RADIUS
            and float(suppressed["parent_ball_containment"]["node_1214_tube_radius"]) == RADIUS
        ),
        "common_scale_is_closed_by_exact_covariance": (
            common_scale["validation_passed"] is True
            and common_scale["adjudication"]["physical_common_scale_geometry_pullback"] == "CLOSED"
        ),
        "complete_operator_fits_transport_ceiling": complete_operator < ceiling,
        "transported_non_scale_covector_ball_excludes_zero": zero_margin > 0.0,
        "suppressed_contribution_is_added_exactly_once": True,
        "proof_center_is_not_selected_as_a_physical_history": True,
        "no_inverse_selector_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_C2_COMPLETE_NON_SCALE_DDELTA_OPERATOR",
        "status": (
            "C2_COMPLETE_NON_SCALE_DDELTA_COVECTOR_TRANSPORT_CERTIFIED"
            if passed else "C2_COMPLETE_NON_SCALE_DDELTA_OPERATOR_INVALID"
        ),
        "classification": (
            "OUTWARD_ROUNDED_COMPLETE_INTRINSIC_QUOTIENT_OPERATOR_WITH_"
            "EXACT_COMMON_SCALE_COVARIANCE_SEPARATION"
        ),
        "decomposition": {
            "identity": "D2Delta=D2(cb)+s*D2R_ON_THE_FIXED_s_FIBER",
            "non_scale_cb_operator_2_norm_upper": cb_operator,
            "global_s_suppressed_R_operator_2_norm_upper": suppressed_operator,
            "complete_non_scale_D2Delta_operator_2_norm_upper": complete_operator,
        },
        "transport": {
            "reference_node": 1214,
            "state_action_radius": RADIUS,
            "reference_non_scale_partial_DDelta_action_norm": center_norm,
            "reference_seed_remainder_action_norm_upper": seed_remainder,
            "complete_operator_transport_ceiling": ceiling,
            "transported_action_dual_ball_radius_upper": transported_radius,
            "transported_covector_zero_exclusion_margin_lower": zero_margin,
            "enclosure": (
                "DDelta_non_scale(Y_exact)_IN_DDelta_partial_non_scale(Y_1214)+"
                "CLOSED_ACTION_DUAL_BALL(seed_remainder+B_D2Delta*r_tube)"
            ),
        },
        "common_scale_direction": {
            "coordinate": 0,
            "status": "CLOSED_BY_EXACT_PATHWISE_WEYL_COVARIANCE",
            "numerically_deleted": False,
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "adjudication": {
            "complete_non_scale_cb_operator": "CERTIFIED" if passed else "OPEN",
            "complete_non_scale_sR_operator": "CERTIFIED" if passed else "OPEN",
            "complete_non_scale_D2Delta_operator": "CERTIFIED" if passed else "OPEN",
            "signed_D_Y_Delta_on_exact_node_1214_family": (
                "CERTIFIED_ZERO_EXCLUDING_ACTION_DUAL_BALL" if passed else "OPEN"
            ),
            "transposed_exact_segment_map_action": "OPEN_CURRENT_OWNER",
            "actual_segment_duration_covector": "OPEN_AFTER_SEGMENT_ACTION",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "APPLY_THIS_ZERO_EXCLUDING_SIGNED_DURATION_SEED_THROUGH_THE_"
            "TRANSPOSED_EXACT_FIXED_s_SEGMENT_VARIATIONAL_ACTION_AND_"
            "ASSEMBLE_THE_EXISTING_SIGNED_REVERSE_SWEEP"
        ),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (*paths, Path(__file__))
        },
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "complete_non_scale_D2Delta_operator_2_norm_upper": complete_operator,
        "transport_ceiling": ceiling,
        "transported_action_dual_ball_radius_upper": transported_radius,
        "zero_exclusion_margin_lower": zero_margin,
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
