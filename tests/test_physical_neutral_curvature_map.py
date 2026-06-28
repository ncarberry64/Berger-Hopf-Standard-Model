from __future__ import annotations

from bhsm.interface.neutrino_action import derive_or_locate_physical_neutral_curvature_map


def test_dimensionless_response_is_not_promoted_to_physical_curvature() -> None:
    result = derive_or_locate_physical_neutral_curvature_map()
    assert result.status == "CONDITIONAL_PHYSICAL_NEUTRAL_CURVATURE_MAP_CANDIDATE"
    assert result.dimensionless_response_available is True
    assert result.symbolic_physical_map_available is True
    assert result.numeric_per_m2_available is False
    assert result.curvature_per_m2 is None
    assert result.boundary_measure_normalized is False
    assert result.transport_length_available is False
    assert "m^-2" in result.remaining_missing_object

