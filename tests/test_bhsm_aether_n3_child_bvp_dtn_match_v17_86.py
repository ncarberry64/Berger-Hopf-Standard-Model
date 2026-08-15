import math

from bhsm.interface.aether_n3_child_bvp_dtn_match_v17_86 import (
    completion_payload,
)


def test_child_BVP_matches_event_trace_and_reports_DtN_block():
    payload = completion_payload()
    assert payload["validation_passed"] is True
    result = payload["child_bvp_dtn_match"]
    child = result["child_BVP"]
    assert child["maximum_log_trace_residual"] < 2.0e-12
    assert child["minimum_eta_Legendre"] > 0.0
    assert math.isfinite(result["metric_lapse_F_child_norm"])
    assert result["child_static_spatial_BVP_closed"] is False
    assert result["metric_lapse_DtN_flux_promotable"] is False


def test_finite_chart_block_is_not_promoted_as_complete_correspondence():
    result = completion_payload()["child_bvp_dtn_match"]
    assert result["complete_correspondence_evaluated"] is False
    assert result["near_flat_selection_test_eligible"] is False
    assert "ETA_ENDPOINT_REACTION_AND_SIGMA_ADJOINT_FLUX" in result[
        "missing_blocks"
    ]
