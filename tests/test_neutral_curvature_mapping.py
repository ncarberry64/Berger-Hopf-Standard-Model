from __future__ import annotations

from bhsm.interface.neutrino_scale import derive_or_locate_neutral_curvature_mapping


def test_neutral_mapping_distinguishes_response_from_physical_curvature() -> None:
    result = derive_or_locate_neutral_curvature_mapping()
    assert result.dimensionless_curvature_response_available is True
    assert result.physical_curvature_units_available is False
    assert result.curvature_value_per_m2 is None
    assert result.status == "OPEN_MISSING_NEUTRAL_CURVATURE_MAPPING"
    assert "m^-2" in result.remaining_missing_object

