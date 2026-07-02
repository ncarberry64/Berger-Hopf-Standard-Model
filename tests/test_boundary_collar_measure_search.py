from bhsm.interface.boundary_collar_measure.source_search import search_boundary_collar_measure_sources


def test_search_localizes_measure_but_not_average():
    payload = search_boundary_collar_measure_sources()
    assert payload["status"] == "SOURCE_SEARCH_COMPLETE_MEASURE_CONDITIONAL_FRAME_AVERAGE_OPEN"
    assert "unit S3 normalization" in payload["blocking_conditions"]
