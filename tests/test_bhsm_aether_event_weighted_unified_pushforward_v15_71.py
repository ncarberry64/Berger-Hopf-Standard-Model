from bhsm.interface.aether_event_weighted_unified_pushforward_v15_71 import (
    completion_payload,
    electric_dtn,
    localization_weight,
    transverse_dtn,
    weighted_up_channel_gap_bound,
)


def test_event_weight_endpoints() -> None:
    assert localization_weight(0.0) == 0.0
    assert abs(localization_weight(3.141592653589793 / 2.0) - 1.0) < 1e-14


def test_weighted_dtn_is_positive() -> None:
    assert transverse_dtn(2) > 0.0
    assert electric_dtn(1) > 0.0


def test_minimal_weight_does_not_fake_gap() -> None:
    assert 0.0 < weighted_up_channel_gap_bound() < 1.0


def test_payload_validates() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert not payload["unified_localization_contract"]["supercritical"]
