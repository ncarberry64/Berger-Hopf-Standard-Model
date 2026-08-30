import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_MINIMUM_CONTRACTION_ADJUDICATION.json"
)


def test_one_shot_replay_localizes_the_minimum_contraction_blocker() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "MINIMUM_INTERVAL_CONTRACTION_BLOCKED_BY_CURRENT_CENTER_Y_Z1_Z2"
    )
    assert payload["summary"]["old_Z2_contains_replay_center"] is False
    assert payload["summary"]["center_displacement_to_old_Z2_radius_lower"] > 1.0e8
    assert payload["summary"]["diagnostic_Y_to_old_Z2_radius_lower"] > 1.0e5
    assert payload["adjudication"]["minimum_interval_contraction_certificate"] == "NOT_AVAILABLE"
    assert payload["adjudication"]["next_Gate7_numerical_campaign_authorized"] is False
    assert payload["claim_boundary"]["actual_root_nonexistence"] == "NOT_CLAIMED"
    assert payload["FULL_BHSM_COMPLETE"] is False
