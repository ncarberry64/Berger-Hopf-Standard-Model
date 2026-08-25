import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_C2_UNIFORM_GAP_CONTINUATION.json"
)


def _payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_uniform_gap_continuation_strictly_extends_prefix():
    payload = _payload()
    continuation = payload["continuation"]
    assert payload["validation_passed"] is True
    assert continuation["prior_total_segments"] == 1128
    assert continuation["additional_certified_segments"] > 0
    assert continuation["total_certified_segments"] > 1128
    assert all(row["selected_branch"] == 24 for row in continuation["rows"])
    assert all(row["uniform_hard_gap_lower"] > 0.0 for row in continuation["rows"])


def test_uniform_gap_continuation_preserves_claim_boundary():
    payload = _payload()
    assert payload["adjudication"]["redundant_hard_denominator"] == "REMOVED"
    assert payload["adjudication"]["actual_later_event_or_canonical_stop"] == "NOT_REACHED"
    assert payload["adjudication"]["Gate7"] == "OPEN_CONTINUATION"
    assert payload["adjudication"]["Gate8"] == "LOCKED"
    assert payload["hindsight"]["outcome"] == "C_REGULAR_CONTINUATION_REMAINS_OPEN"
    assert payload["hindsight"]["obstruction_physical"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
