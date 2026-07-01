from bhsm.interface.ckm_boundary_measure_normalization import search_boundary_measure_normalization_sources

def test_search_separates_symbolic_measure_from_same_term_normalization():
    p = search_boundary_measure_normalization_sources()
    assert p["status"] == "CONDITIONAL_BOUNDARY_MEASURE_SOURCE"
    assert "CKM-term measure attachment" in p["missing_sources"]
    assert p["empirical_inputs_used"] is False
