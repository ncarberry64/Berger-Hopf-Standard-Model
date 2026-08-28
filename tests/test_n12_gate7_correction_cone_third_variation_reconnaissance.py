import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_CORRECTION_CONE_THIRD_VARIATION_RECONNAISSANCE.json"
)


def test_correction_cone_third_variation_remains_reconnaissance():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["structural_validation_passed"] is True
    assert payload["validation_passed"] is False
    assert len(payload["rows"]) == 48
    assert payload["validation"][
        "two_correction_legs_contracted_before_operator_norm"
    ] is True
    assert payload["validation"]["no_finite_difference_subtraction_used"] is True
    assert payload["claim_boundary"]["retained_action_D5_remainder"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
