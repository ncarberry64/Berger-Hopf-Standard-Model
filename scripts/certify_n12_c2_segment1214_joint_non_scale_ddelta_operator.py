"""Certify complete non-scale ``D2Delta`` on the segment-1214 joint tube."""

from __future__ import annotations

import json
from pathlib import Path

import certify_n12_c2_complete_non_scale_ddelta_operator as base


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "flagship_integration"
RESULT = ARTIFACTS / "BHSM_N12_C2_SEGMENT1214_JOINT_NON_SCALE_DDELTA_OPERATOR.json"


def main() -> None:
    base.CB = ARTIFACTS / "BHSM_N12_C2_SEGMENT1214_JOINT_NON_SCALE_CB_OPERATOR.json"
    base.CB_DATA = base.CB.with_suffix(".npz")
    base.SUPPRESSED = (
        ARTIFACTS / "BHSM_N12_C2_SEGMENT1214_JOINT_COMPLETE_SUPPRESSED_R_OPERATOR.json"
    )
    base.THEORY = ROOT / "theory" / "n12_c2_segment1214_joint_domain_extension.md"
    base.RESULT = RESULT
    base.DATA_RESULT = RESULT.with_suffix(".npz")
    base.RADIUS = 5.5212888273161885e-11
    base.main()

    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_C2_SEGMENT1214_JOINT_NON_SCALE_DDELTA_OPERATOR"
    payload["status"] = (
        "C2_SEGMENT1214_JOINT_NON_SCALE_DDELTA_COVECTOR_TRANSPORT_CERTIFIED"
    )
    payload["classification"] = (
        "OUTWARD_ROUNDED_COMPLETE_INTRINSIC_QUOTIENT_OPERATOR_ON_THE_"
        "FULL_SEGMENT1214_JOINT_DOMAIN"
    )
    payload["transport"]["segment"] = [1214, 1215]
    payload["adjudication"].update({
        "segment1214_joint_non_scale_cb_operator": "CERTIFIED",
        "segment1214_joint_non_scale_sR_operator": "CERTIFIED",
        "segment1214_joint_non_scale_D2Delta_operator": "CERTIFIED",
        "transposed_exact_segment_map_action": "OPEN_CURRENT_OWNER",
    })
    payload["exact_next_dependency"] = (
        "DERIVE_THE_SIGNED_DURATION_DENSITY_COVECTOR_ON_THIS_SAME_JOINT_"
        "DOMAIN_THEN_APPLY_THE_TRANSPOSED_EXACT_SEGMENT_VARIATIONAL_ACTION"
    )
    wrapper = Path(__file__).resolve()
    payload["inputs"][wrapper.relative_to(ROOT).as_posix()] = base._sha256(wrapper)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "complete_operator_upper": payload["decomposition"][
            "complete_non_scale_D2Delta_operator_2_norm_upper"
        ],
        "zero_exclusion_margin_lower": payload["transport"][
            "transported_covector_zero_exclusion_margin_lower"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
