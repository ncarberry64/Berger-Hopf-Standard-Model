from bhsm.interface.weak_gauge_action_source import search_weak_gauge_action_sources


def test_search_keeps_action_value_open():
    result = search_weak_gauge_action_sources()
    assert result["g2_action_evidence"] == []
    assert result["alpha2_action_evidence"] == []
    assert "overall k unfixed" in result["evidence_against_action_derivation"]
