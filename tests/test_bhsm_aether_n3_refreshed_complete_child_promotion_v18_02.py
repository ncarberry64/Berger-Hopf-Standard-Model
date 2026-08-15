from bhsm.interface.aether_n3_refreshed_complete_child_promotion_v18_02 import (
    completion_payload,
    v18_02_selected_raw_vector,
)


def test_refreshed_complete_child_promotion_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["refreshed_complete_child_promotion"]
    child = result["event_to_complete_child"]
    persistence = result["persistence"]
    assert child["maximum_trace_residual"] < 1.0e-9
    assert child["maximum_seven_constraint_residual"] < 1.0e-9
    assert child["attachment_momentum_residual_norm"] < 1.0e-7
    assert child["resolved_dynamic_flux_envelope"] < 2.0e-5
    assert persistence["duration"] > 0.0
    assert persistence["nonzero_relative_evolution_retained"]
    assert child["additional_global_KKT_rows"] == 0
    assert v18_02_selected_raw_vector().shape == (376,)
