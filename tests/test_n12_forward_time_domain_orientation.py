import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FORWARD_TIME_DOMAIN_ORIENTATION_AUDIT.json"
)


def test_single_forward_time_domain_is_recovered_without_new_selector():
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    assert data["validation_passed"] is True
    assert data["admissible_clock_domain"]["number_of_physical_time_orientations"] == 1
    assert data["admissible_clock_domain"]["new_condition_added"] is False
    reflected = data["formal_reflection_reclassification"]
    assert reflected["second_physical_temporal_orientation"] is False
    assert reflected["requires_action_selection_of_time_orientation"] is False
    assert reflected["independently_satisfies_same_forward_domain_at_certified_N12_root"] is True
    assert reflected["is_gauge_or_quotiented"] is False
    assert data["singular_boundary_label"]["physical_time_orientation_selector"] is False
    assert data["intrinsic_state_consequence"][
        "artificial_two_temporal_sector_ambiguity_removed"
    ] is True
    assert data["FULL_BHSM_COMPLETE"] is False
