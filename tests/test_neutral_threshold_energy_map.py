from __future__ import annotations

from bhsm.interface.neutrino_scale import build_threshold_energy_map


def test_threshold_energy_map_reports_exact_missing_objects() -> None:
    result = build_threshold_energy_map()
    assert result.status == "OPEN_MISSING_THRESHOLD_TO_ENERGY_MAP"
    assert result.neutral_scale_eV is None
    assert result.neutral_scale_GeV is None
    assert result.unit_anchor_available is False
    assert result.transport_normalization_available is False
    assert "threshold-to-energy map" in result.missing_object

