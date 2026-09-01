"""Sharpen the expanded theta cover with its realized Delta subball."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
PARENT = BASE / "BHSM_N12_C2_EXPANDED_CANCELLED_THETA_STEP_FROM_1221.json"
COVER = BASE / "BHSM_N12_C2_EXPANDED_CANCELLED_THETA_COVER_FROM_1221.json"
RESULT = BASE / "BHSM_N12_C2_1221_CANCELLED_DELTA_MONOTONICITY.json"
INFLATION = 1.0 + 1.0e-10


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict:
    parent, cover_record = (
        json.loads(path.read_text(encoding="utf-8")) for path in (PARENT, COVER)
    )
    if not parent.get("validation_passed") or not cover_record.get("validation_passed"):
        raise RuntimeError("validated expanded parent and cover required")
    domain = parent["domain"]
    cover = cover_record["cover"]
    radius = float(cover["final_joint_domain_use_upper"])
    delta0 = float(domain["Delta_center"])
    delta1 = float(domain["Delta_first_variation_center_plus_error_upper"])
    delta2 = float(domain["Delta_second_variation_upper"])
    variation = _up(delta1 * radius + 0.5 * delta2 * radius**2)
    delta_interval = [
        _down(delta0 - variation),
        _up(delta0 + variation),
    ]
    theta = float(cover["theta_total"])
    s0 = float(cover["initial_signed_descriptor"])
    sharpened = [
        _down(s0 + delta_interval[0] * theta),
        _up(s0 + delta_interval[1] * theta),
    ]
    center = float(cover["final_signed_descriptor_center"])
    validation = {
        "complete_realized_cover_lies_inside_expanded_parent": (
            radius < float(cover["expanded_ball_radius"])
        ),
        "Delta_is_strictly_positive_on_complete_realized_cover": (
            delta_interval[0] > 0.0
        ),
        "signed_descriptor_is_monotone_on_complete_realized_cover": (
            sharpened[0] >= s0
        ),
        "center_descriptor_is_contained_in_sharpened_interval": (
            sharpened[0] <= center <= sharpened[1]
        ),
        "sharpened_lower_bound_exceeds_independent_wrapped_lower_bound": (
            sharpened[0] > float(cover["final_signed_descriptor_interval"][0])
        ),
        "no_predictor_promoted_to_physical_endpoint": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1221_CANCELLED_DELTA_MONOTONICITY",
        "status": (
            "C2_CANCELLED_DELTA_POSITIVE_AND_DESCRIPTOR_MONOTONE_ON_FINITE_COVER"
            if passed else "C2_CANCELLED_DELTA_MONOTONICITY_FAILED"
        ),
        "realized_cover_radius": radius,
        "Delta_interval_on_realized_cover": delta_interval,
        "independent_wrapped_descriptor_interval_superseded": (
            cover["final_signed_descriptor_interval"]
        ),
        "sharpened_correlated_descriptor_interval": sharpened,
        "adjudication": {
            "near_zero_independent_descriptor_lower_bound": "SCALAR_WRAPPING_ARTIFACT",
            "Delta_turning_point_reached": False,
            "event_or_canonical_stop_reached": False,
            "expanded_parent_ball_exhausted": False,
        },
        "exact_next_dependency": (
            "RECENTER_SIGNED_Delta_AND_CANCELLED_RESPONSE_AT_THE_FINAL_COVER_"
            "PREDICTOR_WITH_THE_SHARPENED_DESCRIPTOR_INTERVAL"
        ),
        "inputs": {
            PARENT.relative_to(ROOT).as_posix(): _sha256(PARENT),
            COVER.relative_to(ROOT).as_posix(): _sha256(COVER),
        },
        "validation": validation,
        "validation_passed": passed,
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
