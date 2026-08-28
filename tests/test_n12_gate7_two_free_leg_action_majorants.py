import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_TWO_FREE_LEG_ACTION_MAJORANTS.json"
)


def test_gate7_two_free_leg_action_majorants_are_scoped():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert len(payload["rows"]) == 48
    assert payload["tensor_slot_map"]["d[15]"] == (
        "D4L[free_1,free_2,correction,correction]"
    )
    assert payload["validation"][
        "two_distinct_identity_subspace_legs_used"
    ] is True
    assert payload["claim_boundary"][
        "retained_two_free_leg_action_D2_D5_ball"
    ] == "CERTIFIED"
    assert payload["claim_boundary"][
        "branchwise_selected_line_composition"
    ] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
