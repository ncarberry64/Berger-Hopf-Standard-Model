"""Certify the next cancellation-preserving C2 Lohner segment, number 1216."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_c2_bordered_response_second_variation_ball as response  # noqa: E402
import certify_n12_c2_cancelled_field_lohner_step as step  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
PRIOR_SEGMENT = int(os.environ.get("BHSM_N12_C2_LOHNER_SEGMENT", "1215"))
NEXT_SEGMENT = PRIOR_SEGMENT + 1
PRIOR = BASE / (
    "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json" if PRIOR_SEGMENT == 1215
    else f"BHSM_N12_C2_LOHNER_STEP_{PRIOR_SEGMENT}.json"
)
CENTER = BASE / f"BHSM_N12_C2_LOHNER_FIXED_S_FIELD_{PRIOR_SEGMENT}.json"
CENTER_DATA = BASE / f"BHSM_N12_C2_LOHNER_FIXED_S_FIELD_{PRIOR_SEGMENT}.npz"
BORDERED = BASE / f"BHSM_N12_C2_LOHNER_BORDERED_MATRIX_{PRIOR_SEGMENT}.json"
BORDERED_DATA = BASE / f"BHSM_N12_C2_LOHNER_BORDERED_MATRIX_{PRIOR_SEGMENT}.npz"
GROWTH = BASE / f"BHSM_N12_C2_LOHNER_GROWTH_{PRIOR_SEGMENT}.json"
CONTINUATION = BASE / f"BHSM_N12_C2_LOHNER_STEP_{NEXT_SEGMENT}_INPUT.json"
RESPONSE_RESULT = BASE / f"BHSM_N12_C2_LOHNER_RESPONSE_BALL_{PRIOR_SEGMENT}.json"
RESULT = BASE / f"BHSM_N12_C2_LOHNER_STEP_{NEXT_SEGMENT}.json"
ENDPOINT = BASE / f"BHSM_N12_C2_LOHNER_STEP_{NEXT_SEGMENT}.npz"
PARENT = BASE / os.environ.get(
    "BHSM_N12_C2_PARENT_RESULT",
    "BHSM_N12_C2_TERMINAL_PARENT_ACTION_MAJORANTS_1P5E10.json",
)
TERMINAL = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
PARENT_DRIVER = ROOT / "scripts" / "materialize_n12_c2_terminal_parent_action_majorants.py"
THEORY = ROOT / "theory" / "n12_c2_lohner_step_1216.md"


def main() -> None:
    inputs = (PRIOR, CENTER, CENTER_DATA, BORDERED, BORDERED_DATA, GROWTH, THEORY)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing 1216 Lohner inputs: " + ", ".join(missing))
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    center_record = json.loads(CENTER.read_text(encoding="utf-8"))
    if not prior["validation_passed"] or not center_record["validation_passed"]:
        raise RuntimeError("validated segment 1215 and recentered field required")
    CONTINUATION.write_text(json.dumps({
        "artifact": f"BHSM_N12_C2_LOHNER_STEP_{NEXT_SEGMENT}_INPUT",
        "continuation": {
            "total_certified_segments": prior["segment"]["total_certified_segments"],
            "final_endpoint_tube_radius_upper": prior["segment"]["endpoint_tube_radius_upper"],
            "final_signed_lambda_decimal": prior["segment"]["signed_descriptor_end"],
            "fresh_center_path_upper": 0.0,
        },
        "validation_passed": True,
        "FULL_BHSM_COMPLETE": False,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")

    response.CENTER = CENTER
    response.CENTER_DATA = CENTER_DATA
    response.BORDERED = BORDERED
    response.BORDERED_DATA = BORDERED_DATA
    response.GROWTH = GROWTH
    response.RESULT = RESPONSE_RESULT
    response.THEORY = THEORY
    response.INPUTS = (CENTER, CENTER_DATA, BORDERED, BORDERED_DATA, GROWTH, THEORY)
    response_payload = response.build_payload()
    response_payload["artifact"] = f"BHSM_N12_C2_LOHNER_RESPONSE_BALL_{PRIOR_SEGMENT}"
    response_payload["status"] = (
        f"C2_LOHNER_{PRIOR_SEGMENT}_BORDERED_RESPONSE_SECOND_VARIATION_BALL_CERTIFIED"
        if response_payload["validation_passed"] else f"C2_LOHNER_RESPONSE_BALL_{PRIOR_SEGMENT}_INVALID"
    )
    response_payload["exact_next_dependency"] = (
        "TAKE_CANCELLED_FIXED_s_MATRIX_LOHNER_SEGMENT_1216"
    )
    RESPONSE_RESULT.write_text(
        json.dumps(response_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )

    step.CENTER = CENTER
    step.CENTER_DATA = CENTER_DATA
    step.RESPONSE = RESPONSE_RESULT
    step.BORDERED_DATA = BORDERED_DATA
    step.GROWTH = GROWTH
    step.CONTINUATION = CONTINUATION
    step.PARENT = PARENT
    step.TERMINAL = TERMINAL
    step.RESULT = RESULT
    step.ENDPOINT = ENDPOINT
    step.THEORY = THEORY
    step.PARENT_DRIVER = PARENT_DRIVER
    step.INPUTS = (
        CENTER, CENTER_DATA, RESPONSE_RESULT, BORDERED_DATA, GROWTH,
        CONTINUATION, PARENT, TERMINAL, THEORY, PARENT_DRIVER,
    )
    payload = step.build_payload()
    payload["artifact"] = f"BHSM_N12_C2_LOHNER_STEP_{NEXT_SEGMENT}"
    payload["status"] = (
        f"C2_CANCELLED_FIXED_s_MATRIX_LOHNER_SEGMENT_{NEXT_SEGMENT}_CERTIFIED"
        if payload["validation_passed"] else f"C2_LOHNER_STEP_{NEXT_SEGMENT}_INVALID"
    )
    payload["exact_next_dependency"] = (
        "RECENTER_BRANCH_24_AND_THE_BORDERED_FIXED_s_MATRIX_AT_THE_1216_"
        "PREDICTOR,_THEN_REPEAT_THE_SAME_LOHNER_CONSTRUCTION"
    )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "response_status": response_payload["status"],
        "step_status": payload["status"],
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
