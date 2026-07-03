from bhsm.interface.berger_frame_weighting.source_search import search_berger_frame_weighting_sources

def test_search_finds_no_action_selected_average():
    payload = search_berger_frame_weighting_sources()
    assert payload["status"] == "SOURCE_SEARCH_COMPLETE_FRAME_WEIGHTING_OPEN"
    assert "average normalization" in payload["blocking_conditions"]
