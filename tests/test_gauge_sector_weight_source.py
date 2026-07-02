from bhsm.interface.gauge_coupling_quantum import audit_gauge_sector_weight_source


def test_sector_weights_are_conditional_and_not_trace_promoted():
    result = audit_gauge_sector_weight_source()
    assert result["status"] == "CONDITIONAL_GAUGE_SECTOR_WEIGHT_SOURCE"
    assert result["candidate_weights"] == {"w1": 1, "w2": 2, "w3": 7}
    assert any("do not derive 1,2,7" in item for item in result["evidence_against"])
