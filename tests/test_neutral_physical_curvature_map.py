from __future__ import annotations

from bhsm.interface.neutrino_scale import search_neutral_physical_curvature_map


def test_curvature_search_keeps_dimensionless_response_separate_from_m2() -> None:
    result = search_neutral_physical_curvature_map()
    assert result.status == "CONDITIONAL_PHYSICAL_CURVATURE_MAP_CANDIDATE"
    assert result.dimensionless_response_available is True
    assert result.symbolic_candidate_found is True
    assert result.numeric_per_m2_found is False
    assert result.physical_unit_normalization_available is False
    rows = {row.candidate_key: row for row in result.candidates}
    assert rows["neutral_dimensionless_threshold_response"].status == "DIMENSIONLESS_CURVATURE_RESPONSE"
    assert rows["neutral_dimensionless_threshold_response"].numeric_per_m2_available is False
    assert rows["empirical_curvature_scale"].status == "FORBIDDEN_EMPIRICAL_CURVATURE_SCALE"

