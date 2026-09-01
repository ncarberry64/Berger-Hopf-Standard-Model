import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.json"
)


def test_second_uniform_gap_continuation_extends_fresh_chart():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    continuation = payload["continuation"]
    assert payload["validation_passed"] is True
    assert continuation["prior_total_segments"] == 1192
    assert continuation["additional_certified_segments"] > 0
    assert continuation["total_certified_segments"] > 1192
    assert all(row["selected_branch"] == 24 for row in continuation["rows"])
    assert all(row["uniform_hard_gap_lower"] > 0.0 for row in continuation["rows"])
    assert continuation["exhaustion_classification"] == "BINARY64_PREDICTOR_CENTER_REPRESENTATION_LIMIT"
    assert payload["hindsight"]["classification"].endswith("NUMERICAL_CONDITIONING")
    assert payload["hindsight"]["obstruction_physical"] is False
    assert payload["adjudication"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
