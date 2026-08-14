from bhsm.interface.aether_n3_direct_constrained_trust_newton_v17_83 import (
    completion_payload,
)


def test_direct_constrained_trust_newton_is_classified():
    payload = completion_payload()
    assert payload["validation_passed"] is True
    result = payload["direct_constrained_trust_newton"]
    assert result["owner_weighting_or_tangent_mixture"] is False
    selected = result["selected_direct_trust_newton_state"]
    if selected is not None:
        assert selected["complete_reduced"] is True
        assert selected["absolute_event_reduced"] is True
        assert selected["eta_minimum"] > 1.0e-5
