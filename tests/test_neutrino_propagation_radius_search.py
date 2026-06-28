from __future__ import annotations

from bhsm.interface.neutrino_scale import derive_or_locate_neutrino_propagation_radius


def test_propagation_radius_search_fails_closed_without_physical_radius() -> None:
    result = derive_or_locate_neutrino_propagation_radius()
    assert result.status == "OPEN_MISSING_PROPAGATION_LOCALIZATION_RADIUS"
    assert result.value_m is None
    assert result.source_file is None
    assert result.empirical_radius_rejected is True
    assert result.candidates_checked

