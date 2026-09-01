import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_RETAINED_CORRECTION_BORDERED_RESPONSE_FIRST_JETS.json"
)


def test_retained_correction_bordered_response_first_jets_are_scoped():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert len(payload["rows"]) == 48
    assert payload["identity"]["border_dimension"] == 62
    assert payload["identity"]["explicit_inverse_formed"] is False
    assert payload["validation"][
        "no_mismatched_graph_reconnaissance_used_as_proof_input"
    ] is True
    assert payload["claim_boundary"][
        "retained_center_bordered_response_first_jet"
    ] == "DERIVED"
    assert payload["claim_boundary"][
        "outward_bordered_response_first_jet_tube"
    ] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
