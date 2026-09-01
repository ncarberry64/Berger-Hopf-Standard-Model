"""Certify the signed duration-density covector on the segment joint tube."""

from __future__ import annotations

import json
from pathlib import Path

import certify_n12_c2_node1214_signed_duration_density_covector as base


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "flagship_integration"
RESULT = ARTIFACTS / "BHSM_N12_C2_SEGMENT1214_JOINT_DURATION_DENSITY_COVECTOR.json"


def main() -> None:
    base.DDELTA = (
        ARTIFACTS / "BHSM_N12_C2_SEGMENT1214_JOINT_NON_SCALE_DDELTA_OPERATOR.json"
    )
    base.DDELTA_DATA = base.DDELTA.with_suffix(".npz")
    base.THEORY = ROOT / "theory" / "n12_c2_segment1214_joint_domain_extension.md"
    base.RESULT = RESULT
    base.DATA_RESULT = RESULT.with_suffix(".npz")
    base.EXPECTED_RADIUS = 5.5212888273161885e-11
    base.main()

    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_C2_SEGMENT1214_JOINT_DURATION_DENSITY_COVECTOR"
    payload["status"] = (
        "C2_SEGMENT1214_JOINT_DURATION_DENSITY_COVECTOR_BALL_CERTIFIED"
    )
    payload["classification"] = (
        "EXACT_BHSM_INCIDENCE_WITH_DDELTA_MEAN_VALUE_ENCLOSURE_ON_THE_"
        "FULL_SEGMENT1214_JOINT_NON_SCALE_DOMAIN"
    )
    payload["tube"]["segment"] = [1214, 1215]
    payload["adjudication"].update({
        "segment1214_joint_DDelta_covector": "CERTIFIED",
        "segment1214_joint_duration_density_covector": "CERTIFIED",
        "transposed_exact_segment_map_action": "OPEN_CURRENT_OWNER",
    })
    payload["exact_next_dependency"] = (
        "APPLY_THIS_JOINT_DOMAIN_SIGNED_SOURCE_BALL_THROUGH_THE_TRANSPOSED_"
        "EXACT_SEGMENT1214_VARIATIONAL_ACTION_AND_INTEGRATE"
    )
    wrapper = Path(__file__).resolve()
    payload["inputs"][wrapper.relative_to(ROOT).as_posix()] = base._sha256(wrapper)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "zero_exclusion_margin_lower": payload["covector"][
            "zero_exclusion_margin_lower"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
