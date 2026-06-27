from __future__ import annotations

import pytest

from bhsm.interface import pdg_interface
from bhsm.interface.validation import ExperimentalValue, ValidationComparison


def test_central_value_comparison() -> None:
    reference = ExperimentalValue("x", "central_value", "test", value_gev=10.0, uncertainty_gev=0.5)
    result = ValidationComparison.compare(11.0, reference)
    assert result.delta_gev == 1.0
    assert result.absolute_delta_gev == 1.0
    assert result.relative_delta == pytest.approx(0.1)
    assert result.sigma_delta == 2.0


def test_upper_limit_and_range_comparisons() -> None:
    upper = ExperimentalValue("nu", "upper_limit", "test", upper_gev=2.0)
    upper_result = ValidationComparison.compare(1.5, upper)
    assert upper_result.below_upper_limit is True
    assert upper_result.upper_limit_margin_gev == pytest.approx(0.5)

    interval = ExperimentalValue("y", "range", "test", lower_gev=1.0, upper_gev=2.0)
    range_result = ValidationComparison.compare(3.0, interval)
    assert range_result.inside_range is False
    assert range_result.distance_to_range == 1.0


def test_offline_fallback_reference_kinds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pdg_interface, "is_pdg_available", lambda: False)
    w = pdg_interface.load_reference_with_fallback("W_boson")
    neutrino = pdg_interface.load_reference_with_fallback("electron_neutrino")
    assert w.reference_kind == "central_value"
    assert w.source_label and w.source_url
    assert neutrino.reference_kind == "upper_limit"
    assert neutrino.value_gev is None
    assert neutrino.upper_gev == pytest.approx(0.45e-9)
    assert neutrino.metadata["not_a_measured_central_mass"] is True
    assert neutrino.metadata["pdg_query_status"] == "PACKAGE_UNAVAILABLE"
