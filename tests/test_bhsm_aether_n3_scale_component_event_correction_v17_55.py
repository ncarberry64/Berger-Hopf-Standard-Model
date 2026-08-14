from bhsm.interface.aether_n3_scale_component_event_correction_v17_55 import (
    PRIORITY_PROFILES,
    completion_payload,
)


def test_profiles_bounded():
    assert len(PRIORITY_PROFILES) == 8
    assert all(len(profile) == 2 and min(profile) > 0 for profile in PRIORITY_PROFILES)


def test_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["status"] == "RECLASSIFIED"
