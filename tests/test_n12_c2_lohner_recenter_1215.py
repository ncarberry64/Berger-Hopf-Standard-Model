import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_LOHNER_RECENTER_1215.json"


def test_lohner_recenter_1215() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    radius = payload["radius_derivation"]
    assert payload["validation_passed"] is True
    assert payload["center"]["selected_branch"] == 24
    assert radius["selected_fresh_chart_radius"] > radius["incoming_endpoint_tube_upper"]
    assert radius["selected_chart_bounds"]["eigenline_gap_lower"] > 0.0
    assert payload["chart_semantics"]["proof_chart_boundary_is_physical_stop"] is False
    assert payload["FLAGSHIP_READY"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
