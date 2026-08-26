import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_NODE1214_SIGNED_DURATION_DENSITY_COVECTOR.json"
)


def test_node1214_signed_duration_density_covector() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == "C2_NODE1214_SIGNED_DURATION_DENSITY_COVECTOR_BALL_CERTIFIED"
    assert payload["tube"]["Delta_interval"][0] > 0.0
    assert payload["tube"]["proper_duration_density_interval"][0] > 0.0
    assert payload["covector"]["zero_exclusion_margin_lower"] > 0.0
    assert payload["covector"]["independent_norm_lower"] > 0.0
    assert payload["adjudication"]["transposed_exact_segment_map_action"] == "OPEN_CURRENT_OWNER"
    assert payload["adjudication"]["Gate7"] == "OPEN"
    assert payload["adjudication"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
