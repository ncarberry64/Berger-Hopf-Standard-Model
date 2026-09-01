import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_C2_UNIFORM_GAP_HARD_RESPONSE.json"
)


def _payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_uniform_gap_hard_response_certified():
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["matching_audit"]["match"] == "VALID_MATCH"
    assert payload["hard_response"]["uniform_gap_lower"] > 0.0
    assert payload["hard_response"]["old_redundant_inflation_factor"] > 1000.0
    assert payload["finite_s_correction"]["Delta_interval"][0] > 0.0
    assert payload["finite_s_correction"]["covered_full_ball_growth_upper"] >= 1.0


def test_proof_exhaustion_is_not_promoted_to_physical_stop():
    payload = _payload()
    assert payload["adjudication"]["hard_denominator_collapse"].startswith("REDUNDANT")
    assert payload["adjudication"]["actual_event_or_canonical_stop"] == "NOT_REACHED"
    assert payload["adjudication"]["Gate7"] == "OPEN_CONTINUATION"
    assert payload["adjudication"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
