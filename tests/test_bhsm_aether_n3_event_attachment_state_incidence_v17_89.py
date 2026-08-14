from bhsm.interface.aether_n3_event_attachment_state_incidence_v17_89 import (
    completion_payload,
)


def test_event_attachment_state_incidence_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["event_attachment_state_incidence"]
    assert result["state_jacobian_rank"] == 2
    assert result["four_stratum_state_jacobian_rank"] == 2
    assert result["matcher_residual"] < 1.0e-14
    assert result["differential_matcher_residual"] < 1.0e-14
    assert not result["conditional_representative_only"]["physical_event_block"]
    assert not payload["direct_N3_solve_authorized_next"]
