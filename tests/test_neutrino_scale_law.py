from __future__ import annotations

import pytest
from math import pi

from bhsm.interface.neutrino_propagation.effective_mass import load_neutral_scale_law


def test_scale_law_uses_dimensionless_tau_and_reports_missing_units() -> None:
    scale = load_neutral_scale_law()
    assert scale.dimensionless_scale == pytest.approx(1.0 / (4.0 * pi**1.5))
    assert scale.status == "OPEN_MISSING_NEUTRAL_SCALE"
    assert scale.effective_mass_eV_per_unit is None
    assert scale.effective_mass_GeV_per_unit is None
    assert "dimensionful neutral scale" in scale.missing_object
