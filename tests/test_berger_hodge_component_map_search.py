from bhsm.interface.berger_hodge_component_map.source_search import search_berger_hodge_component_sources

def test_search_localizes_the_open_basis_gate():
    payload = search_berger_hodge_component_sources()
    assert payload["status"] == "SOURCE_SEARCH_COMPLETE_HODGE_MAP_CONDITIONAL_COFRAME_OPEN"
    assert "gauge-action coframe selection" in payload["blocking_conditions"]
