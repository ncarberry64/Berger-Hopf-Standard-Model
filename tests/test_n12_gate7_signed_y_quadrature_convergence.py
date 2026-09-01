from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_GATE7_SIGNED_Y_QUADRATURE_CONVERGENCE_AUDIT.json"
)


def test_signed_y_quadrature_nonconvergence_is_not_overpromoted() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert payload["status"] == (
        "CURRENT_GAUSS12_RECENTER_NOT_PROMOTABLE;_SIGNED_Y_QUADRATURE_OPEN"
    )
    assert [
        row["right_Gauss_order"] for row in payload["rows"]
    ] == [12, 16, 20]
    assert payload["rows"][2]["candidate_halo_utilization"] > 2.0e5
    assert payload["summary"][
        "stored_to_refined_candidate_halo_utilization"
    ] > 30.0
    assert payload["summary"][
        "Z1_observed_finest_summed_local_order"
    ] > 1.99
    assert payload["claim_boundary"]["Y"] == (
        "OPEN_NONCONVERGED_SIGNED_QUADRATURE"
    )
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
