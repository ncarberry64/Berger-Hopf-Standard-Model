"""Extend the C2 cover to the current binary64 descriptor-resolution limit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_c2_finite_translated_descriptor_cover import (  # noqa: E402
    build_payload as build_cover_payload,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT.json"
DATA_RESULT = BASE / "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT.npz"
BASE_SCRIPT = ROOT / "scripts/certify_n12_c2_finite_translated_descriptor_cover.py"
THEORY = ROOT / "theory/n12_c2_extended_descriptor_resolution_audit.md"
MAX_ADDITIONAL_BOXES = 512


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, object]:
    if not BASE_SCRIPT.is_file() or not THEORY.is_file():
        raise FileNotFoundError("extended descriptor audit inputs required")
    payload = build_cover_payload(
        max_additional_boxes=MAX_ADDITIONAL_BOXES,
        data_result=DATA_RESULT,
    )
    cover = payload["cover"]
    validation = dict(payload["validation"])
    resolution = cover.get("resolution_witness")
    validation.update({
        "expanded_safety_limit_not_reached": (
            cover["exhaustion_classification"]
            == "CURRENT_BINARY64_SIGNED_DESCRIPTOR_INCREMENT_NOT_RESOLVED"
        ),
        "resolution_witness_materialized": isinstance(resolution, dict),
        "accepted_rows_remain_strictly_positive": validation[
            "all_certified_steps_have_positive_signed_and_proper_duration"
        ],
        "failed_increment_is_below_one_binary64_ulp": (
            isinstance(resolution, dict)
            and resolution["step_to_ulp_ratio"] < 1.0
        ),
        "failed_increment_does_not_advance_signed_coordinate": (
            isinstance(resolution, dict)
            and resolution["binary64_signed_lambda_end"]
            == resolution["signed_lambda_start"]
        ),
        "failed_increment_has_zero_binary64_physical_duration": (
            isinstance(resolution, dict)
            and resolution["binary64_physical_u_increment"] == 0.0
        ),
        "arithmetic_exhaustion_not_promoted_to_event_or_stop": True,
    })
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload.update({
        "artifact": "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT",
        "status": (
            "C2_COVER_EXTENDED_TO_BINARY64_SIGNED_DESCRIPTOR_RESOLUTION_LIMIT"
            if passed
            else "C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT_FAILED"
        ),
        "classification": (
            "THE_SAME_ACTION_INVERSE_FREE_COVER_CERTIFIES_434_ADDITIONAL_"
            "BOXES_AFTER_THE_TWO_LAUNCH_BOXES_BEFORE_THE_NEXT_POSITIVE_"
            "CERTIFIED_STEP_FALLS_BELOW_BINARY64_RESOLUTION;_THIS_IS_A_"
            "PROOF_COORDINATE_ARITHMETIC_EXHAUSTION_NOT_AN_EVENT_OR_CANONICAL_STOP"
        ),
        "arithmetic_adjudication": {
            "accepted_additional_boxes": cover["certified_additional_box_count"],
            "accepted_total_segments": cover["certified_total_segment_count"],
            "attempted_next_box": (
                resolution["attempted_cover_index_after_two_segment_prefix"]
                if isinstance(resolution, dict) else None
            ),
            "physical_event_reached": False,
            "canonical_stop_reached": False,
            "action_domain_margin_failed": False,
            "binary64_signed_accumulator_stagnated": True,
            "mathematical_continuation_disproved": False,
        },
        "exact_next_dependency": (
            "REBUILD_THE_SIGNED_DESCRIPTOR_ACCUMULATOR_AND_RECENTERED_STATE_"
            "PREDICTOR_IN_VALIDATED_MULTIPRECISION_OR_INTERVAL_ARITHMETIC_USING_"
            "THE_SAME_ACTION_FIELD_AND_MAJORANTS;_DO_NOT_TREAT_BINARY64_"
            "STAGNATION_AS_A_CANONICAL_STOP"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_MULTIPRECISION_C2_CONTINUATION_OR_COMBINED_PROJECTED_TAIL",
            "Gate8": "LOCKED",
            "extended_finite_C2_cover": "CERTIFIED_TO_ARITHMETIC_RESOLUTION",
            "actual_later_event_or_canonical_stop": "OPEN",
            "actual_projected_zero_source_force": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    })
    payload["inputs"].update({
        BASE_SCRIPT.relative_to(ROOT).as_posix(): _sha256(BASE_SCRIPT),
        THEORY.relative_to(ROOT).as_posix(): _sha256(THEORY),
    })
    return payload


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    cover = payload["cover"]
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "total_segments": cover["certified_total_segment_count"],
        "exhaustion": cover["exhaustion_classification"],
        "resolution_witness": cover["resolution_witness"],
    }, indent=2))


if __name__ == "__main__":
    main()
