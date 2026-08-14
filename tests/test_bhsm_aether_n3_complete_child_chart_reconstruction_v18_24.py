from bhsm.interface.aether_n3_complete_child_chart_reconstruction_v18_24 import completion_payload


def test_v18_24_recomputes_the_complete_child_chart() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["complete_child_chart_reconstruction"]
    assert result["chart"]["full_chart_rank"] == 14
    assert result["physical_row_count"] == 14
    assert result["additional_global_KKT_rows"] == 0
    assert result["nonzero_motion_retained"]
