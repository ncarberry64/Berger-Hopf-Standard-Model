import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_CORRECTION_BORDERED_RESPONSE_SECOND_JETS.json"
)


def test_gate7_correction_bordered_response_second_jets_are_scoped():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert len(payload["rows"]) == 48
    assert payload["identity"]["explicit_inverse_formed"] is False
    assert payload["claim_boundary"][
        "center_second_bordered_identity"
    ] == "DERIVED"
    assert payload["claim_boundary"][
        "JAX_D4_as_retained_interval_authority"
    ] == "NOT_CLAIMED"
    assert payload["claim_boundary"][
        "retained_two_free_leg_D4_D5_response_majorants"
    ] == "OPEN"
    assert payload["claim_boundary"][
        "outward_D2f_correction_cone"
    ] == "OPEN_COMPOSITION"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
