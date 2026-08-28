import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_HARD_INVERSE.json"
)


def test_recentered_cone_bordered_hard_inverse_certificate() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["mesh"]["cells"] == 3009
    assert payload["summary"]["minimum_selected_to_hard_gap_lower"] > 0.0
    assert payload["summary"]["maximum_center_chart_condition_factor_upper"] < 2.0
    assert all(row["bordered_inverse_closed"] for row in payload["rows"])
    assert payload["claim_boundary"][
        "all_3009_recentered_cone_bordered_hard_inverses"
    ] == "CERTIFIED"
    assert payload["claim_boundary"]["recentered_cone_bordered_response"] == (
        "OPEN_UNTIL_RHS_INSERTED"
    )
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
