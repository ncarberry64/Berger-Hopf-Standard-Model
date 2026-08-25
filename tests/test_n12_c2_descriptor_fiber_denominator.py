import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_C2_DESCRIPTOR_FIBER_DENOMINATOR.json"
)


def test_descriptor_fiber_denominator_is_certified() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replay = payload["segment_1128_replay"]
    assert payload["validation_passed"] is True
    assert replay["isotropic_normal_overestimate_factor"] > 1.0e5
    assert replay["fiber_restricted_Delta_lower"] > 1.0e-15
    assert replay["fiber_over_isotropic_Delta_improvement"] > 1.0e5
    assert replay["hard_denominator_lower"] > 0.0


def test_fiber_theorem_does_not_promote_a_stop() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["adjudication"]["actual_later_event_or_canonical_stop"] == "NOT_REACHED"
    assert payload["adjudication"]["mathematical_history_termination_claimed"] is False
    assert payload["claim_boundary"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
