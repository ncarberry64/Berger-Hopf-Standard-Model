from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_PROJECTOR_INVERSE.json"
)


def test_selected_dop853_cone_projector_inverse() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert payload["summary"][
        "maximum_nonlinear_cone_selected_projector_motion_upper"
    ] < 1.0
    assert payload["claim_boundary"][
        "bordered_hard_inverse_on_candidate_nonlinear_cone"
    ] == "CERTIFIED"
    assert payload["claim_boundary"][
        "candidate_radius_self_map"
    ] == "OPEN_CORRELATED_Y_Z1_Z2"
    assert payload["FULL_BHSM_COMPLETE"] is False
