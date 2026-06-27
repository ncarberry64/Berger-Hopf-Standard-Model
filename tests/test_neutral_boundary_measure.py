from __future__ import annotations

from bhsm.interface.neutrino_scale import analyze_neutral_boundary_measure


def test_symbolic_boundary_measure_is_not_a_physical_unit_anchor() -> None:
    result = analyze_neutral_boundary_measure()
    assert result.measure_symbol == "dmu_boundary dt"
    assert result.couples_to_neutral_kernel is True
    assert result.physical_normalization_available is False
    assert result.background_energy_density_available is False
    assert result.status == "OPEN_MISSING_BOUNDARY_MEASURE"

