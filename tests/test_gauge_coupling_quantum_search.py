from bhsm.interface.gauge_coupling_quantum import search_gauge_coupling_quantum_sources


def test_search_finds_registry_but_no_action_attachment():
    result = search_gauge_coupling_quantum_sources()
    assert result["status"] == "ARTIFACT_BACKED_GAUGE_COUPLING_REGISTRY_PATTERN"
    assert result["action_attachment_evidence"] == []
    assert result["g2_action_evidence"] == []
