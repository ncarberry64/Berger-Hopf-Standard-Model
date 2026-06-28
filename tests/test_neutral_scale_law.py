from __future__ import annotations

from math import pi

import pytest

from bhsm.interface.neutrino_scale import derive_neutral_scale_law


def test_neutral_scale_law_preserves_dimensionless_tau_without_units() -> None:
    result = derive_neutral_scale_law()
    assert result.scale_value_dimensionless == pytest.approx(1.0 / (4.0 * pi**1.5))
    assert result.status_before == "DIMENSIONLESS_ONLY_CLOSURE"
    assert result.status_after == "OPEN_MISSING_NEUTRAL_SCALE"
    assert result.unit_available is False
    assert result.scale_value_eV is None
    assert result.scale_value_GeV is None


def test_neutral_scale_law_uses_no_forbidden_inputs() -> None:
    result = derive_neutral_scale_law()
    assert result.empirical_derivation_inputs_used is False
    assert result.reference_values_used_as_theorem_inputs is False
    assert result.electron_neutrino_limit_used_as_derivation_input is False
    assert result.w_mass_used_as_theorem_input is False

