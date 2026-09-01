from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_SPECTRUM.json"
)


def test_selected_dop853_candidate_nonlinear_cone_spectrum() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert payload["mesh"]["cells"] == payload["mesh"][
        "full_selected_DOP853_cover_cells"
    ]
    assert payload["summary"]["minimum_nonlinear_cone_boundary_gap_lower"] > 0.0
    assert payload["claim_boundary"][
        "selected_line_on_candidate_nonlinear_DOP853_cone"
    ] == "CERTIFIED_SIMPLE"
    assert payload["claim_boundary"][
        "candidate_radius_self_map"
    ] == "OPEN_CORRELATED_Y_Z1_Z2"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
