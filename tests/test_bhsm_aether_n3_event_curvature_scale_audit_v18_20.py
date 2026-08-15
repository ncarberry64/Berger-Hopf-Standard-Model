from bhsm.interface.aether_n3_event_curvature_scale_audit_v18_20 import completion_payload


def test_v18_20_measures_event_curvature_without_reusing_bad_hessian() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["event_curvature_scale_audit"]
    assert result["event_support_dimension"] == 37
    assert result["uniform_raw_step_hessian_v18_19"] == "INVALIDATED"
    assert not result["physical_event_changed"]
