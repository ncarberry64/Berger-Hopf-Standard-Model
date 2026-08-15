from bhsm.interface.aether_n3_second_complete_child_chart_reconstruction_v18_28 import completion_payload


def test_v18_28_second_complete_child_chart_reconstruction() -> None:
    payload = completion_payload()
    result = payload["second_complete_child_chart_reconstruction"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["chart"]["full_chart_rank"] == 14
    assert result["physical_row_count"] == 14
    assert result["additional_global_KKT_rows"] == 0
    assert result["nonzero_motion_retained"]
