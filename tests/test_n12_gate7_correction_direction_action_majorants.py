import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_CORRECTION_DIRECTION_ACTION_MAJORANTS.json"
)


def test_correction_direction_action_majorants_are_certified_and_scoped():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert len(payload["rows"]) == 48
    assert payload["ball"]["action_radius"] == 3.6e-6
    assert payload["validation"][
        "expected_committed_majorant_SHA256_verified"
    ] is True
    assert payload["validation"][
        "no_protected_file_edited_or_staged_by_this_certificate"
    ] is True
    assert payload["claim_boundary"]["retained_action_directional_D2_D5"] == (
        "CERTIFIED"
    )
    assert payload["claim_boundary"]["outward_D2f_correction_cone"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
