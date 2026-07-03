from bhsm.interface.berger_hodge_component_map.gauge_trace_hodge_expansion import audit_gauge_trace_hodge_expansion

def test_trace_expansion_is_conditional_not_a_coupling_derivation():
    payload = audit_gauge_trace_hodge_expansion()
    assert payload["status"] == "CONDITIONAL_GAUGE_TRACE_HODGE_COMPONENT_EXPANSION"
    assert "does not attach coupling normalization" in payload["claim_boundary"]
