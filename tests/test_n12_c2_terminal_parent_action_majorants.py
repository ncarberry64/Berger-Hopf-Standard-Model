import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_TERMINAL_PARENT_ACTION_MAJORANTS_1P5E10.json"


def test_terminal_parent_action_majorants() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["action_coordinate_ball_radius"] == 1.5e-10
    assert all(row["value_enclosed"] for row in payload["sectors"])
    event = next(row for row in payload["sectors"] if row["sector"] == "event")
    assert event["derivative_operator_majorants_0_through_5"][5] > 0.0
