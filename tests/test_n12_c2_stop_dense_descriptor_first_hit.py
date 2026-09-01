import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_STOP_DENSE_DESCRIPTOR_FIRST_HIT.json"
)


def test_dense_center_has_one_descending_first_hit() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    validation = payload["validation"]
    assert payload["validation_passed"] is True
    assert validation[
        "all_complete_preterminal_polynomials_strictly_positive"
    ] is True
    assert validation[
        "terminal_polynomial_strictly_positive_before_root_bracket"
    ] is True
    assert validation["terminal_polynomial_derivative_strictly_negative"] is True
    assert validation[
        "terminal_zero_bracket_has_positive_left_and_negative_right"
    ] is True
    assert payload["summary"]["terminal_derivative_Bernstein_upper"] < 0.0


def test_dense_center_certificate_preserves_claim_boundary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    boundary = payload["claim_boundary"]
    assert boundary["stored_center_first_hit"] is True
    assert boundary["exact_history_first_hit"].startswith("OPEN_")
    assert boundary["Gate7"] == "ACTIVE"
    assert boundary["FULL_BHSM_COMPLETE"] is False
