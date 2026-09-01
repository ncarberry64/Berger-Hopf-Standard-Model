import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.json"
)


def test_bordered_hard_response_matrix_is_center_certified():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["bordered_center"]["selected_branch"] == 24
    assert payload["bordered_center"]["minimum_bordered_singular_value"] > 0.0
    assert abs(payload["bordered_center"]["selected_line_orthogonality_residual"]) < 1.0e-8
    assert payload["variational_matrix"]["fixed_descriptor_hard_response_operator_norm"] > 0.0
    assert "SECOND_VARIATION_REMAINDER_OPEN" in payload["status"]
    assert payload["hindsight"]["obstruction_physical"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
