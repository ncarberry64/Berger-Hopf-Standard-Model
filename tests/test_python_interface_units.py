from __future__ import annotations

import pytest

from bhsm.interface.constants import JOULE_PER_GEV, KG_PER_GEV_C2
from bhsm.interface.units import GeometricUnitMapper


def test_energy_and_mass_conversions_round_trip() -> None:
    mapper = GeometricUnitMapper()
    assert mapper.mass_gev_to_ev(2.5) == pytest.approx(2.5e9)
    assert mapper.mass_ev_to_gev(2.5e9) == pytest.approx(2.5)
    assert mapper.mass_gev_to_kg(1.0) == pytest.approx(KG_PER_GEV_C2)
    assert mapper.mass_kg_to_gev(KG_PER_GEV_C2) == pytest.approx(1.0)
    assert mapper.energy_gev_to_joule(1.0) == pytest.approx(JOULE_PER_GEV)
    assert mapper.energy_joule_to_gev(JOULE_PER_GEV) == pytest.approx(1.0)


def test_anchor_calibration_is_explicit() -> None:
    mapper = GeometricUnitMapper.from_anchor(2.0, 80.0, "W_boson", "test source")
    assert mapper.scale_gev_per_tension == 40.0
    assert mapper.tension_to_mass_gev(2.0) == 80.0
    assert mapper.anchor_particle == "W_boson"
    assert mapper.calibration_mode == "EMPIRICAL_CALIBRATION_ANCHOR"
    assert mapper.to_dict()["anchor_is_independent_prediction"] is False


def test_zero_tension_anchor_is_rejected() -> None:
    with pytest.raises(ValueError, match="anchor_tension"):
        GeometricUnitMapper.from_anchor(0.0, 80.0, "W_boson", "test source")
