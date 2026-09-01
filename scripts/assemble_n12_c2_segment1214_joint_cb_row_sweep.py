"""Assemble the signed non-scale ``D2(cb)`` sweep on segment 1214."""

from __future__ import annotations

import json
import math
from pathlib import Path

import assemble_n12_c2_complete_cb_row_sweep as base


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "flagship_integration"
RESULT = ARTIFACTS / "BHSM_N12_C2_SEGMENT1214_JOINT_NON_SCALE_CB_OPERATOR.json"
DATA_RESULT = RESULT.with_suffix(".npz")


def main() -> None:
    base.ROWS = ARTIFACTS / ".n12_c2_segment1214_joint_cb_rows"
    base.REFERENCE_ROW = (
        ARTIFACTS
        / "BHSM_N12_C2_SEGMENT1214_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE.json"
    )
    base.THEORY = ROOT / "theory" / "n12_c2_segment1214_joint_domain_extension.md"
    base.RESULT = RESULT
    base.DATA_RESULT = DATA_RESULT
    base.RADIUS = 5.5212888273161885e-11
    base.main()

    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_C2_SEGMENT1214_JOINT_NON_SCALE_CB_OPERATOR"
    payload["status"] = "C2_SEGMENT1214_JOINT_NON_SCALE_CB_OPERATOR_CERTIFIED"
    payload["classification"] = (
        "OUTWARD_ROUNDED_SIGNED_ONE_AXIS_ROW_SWEEP_ON_THE_FULL_"
        "SEGMENT1214_JOINT_NON_SCALE_DOMAIN"
    )
    payload["domain"] = {
        "segment": [1214, 1215],
        "joint_action_radius": base.RADIUS,
        "endpoint_local_radius": 5.5104723095444935e-11,
        "strict_extension": base.RADIUS > 5.5104723095444935e-11,
    }
    payload["adjudication"].update({
        "segment1214_joint_non_scale_cb_operator": "CERTIFIED",
        "complete_non_scale_D2Delta_operator": "OPEN_PENDING_SEGMENT_sR",
    })
    payload["exact_next_dependency"] = (
        "ADD_THE_REISSUED_SEGMENT1214_JOINT_sR_OPERATOR_AND_TEST_THE_"
        "COMPLETE_JOINT_DOMAIN_DDELTA_TRANSPORT"
    )
    wrapper = Path(__file__).resolve()
    payload["inputs"][wrapper.relative_to(ROOT).as_posix()] = base.sha256(wrapper)
    payload["transport_budget_before_sR"]["cb_remaining_budget"] = math.nextafter(
        payload["transport_budget_before_sR"]["pre_sR_operator_ceiling"]
        - payload["operator"]["non_scale_cb_Frobenius_upper"],
        -math.inf,
    )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "joint_action_radius": base.RADIUS,
        "non_scale_cb_Frobenius_upper": payload["operator"][
            "non_scale_cb_Frobenius_upper"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
