from bhsm.interface.aether_n3_event_predictor_log_corrector_v17_52 import (
    CORRECTOR_PROFILES,
    PREDICTOR_EVENT_ROOT_FRACTION,
    completion_payload,
    event_predictor,
)


def test_predictor_is_bounded_and_improves_event():
    result = event_predictor()
    assert 0 < PREDICTOR_EVENT_ROOT_FRACTION < 1
    assert result["predictor_metrics"]["event"] < result["base_metrics"]["event"]


def test_corrector_profiles_are_positive_four_owner_profiles():
    assert len(CORRECTOR_PROFILES) == 8
    assert all(len(profile) == 4 and min(profile) > 0 for profile in CORRECTOR_PROFILES)


def test_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["status"] == "RECLASSIFIED"
    assert payload["event_predictor_log_corrector"]["base_strict_candidate_count"] == 0
