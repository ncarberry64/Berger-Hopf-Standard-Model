from bhsm.interface.aether_n3_event_projected_calderon_flux_v17_92 import (
    completion_payload,
)


def test_event_projected_calderon_flux_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["event_projected_calderon_flux"]
    assert len(result["constraint_preserving_event_attachment_flux"]) == 2
    assert result["event_attachment_flux_norm"] > 0.0
    ledger = result["complete_outer_flux_ledger"]
    assert ledger["reconstructed_child_metric_eta_scalar_projection"] == "OPEN"
    assert ledger["sum_not_set_to_zero_by_reflection"]
    assert not payload["direct_N3_solve_authorized_next"]
