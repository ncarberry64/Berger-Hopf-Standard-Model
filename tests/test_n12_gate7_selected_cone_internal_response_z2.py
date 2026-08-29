from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2.json"
)


def test_selected_cone_internal_response_and_causal_z2() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["status"] == (
        "SELECTED_CONE_INTERNAL_RESPONSE_AND_CAUSAL_TAYLOR_Z2_CERTIFIED"
    )
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert len(payload["rows"]) == 48
    assert payload["summary"]["selected_cone_radius_utilization"] < 1.0
    assert payload["summary"]["maximum_local_proof_tube_utilization"] < 1.0
    assert payload["summary"][
        "maximum_signed_quadratic_center_correction_2_norm"
    ] < 1.0e-24
    assert payload["claim_boundary"]["physical_transverse_Z2_input"] == (
        "CERTIFIED_BY_SIGNED_THIRD_ORDER_TAYLOR_VOLTERRA_CAUSAL_ENCLOSURE"
    )
    assert payload["claim_boundary"]["propagator_Z1_and_signed_Y"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
