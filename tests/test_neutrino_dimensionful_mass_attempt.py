from __future__ import annotations

from dataclasses import replace

from bhsm.interface.neutrino_propagation.curvature_threshold import (
    build_background_coupling,
    build_curvature_threshold,
)
from bhsm.interface.neutrino_propagation.effective_mass import (
    compute_neutrino_propagation_mass,
    load_neutral_scale_law,
)
from bhsm.interface.neutrino_propagation.neutral_kernel import load_neutral_kernel
from bhsm.interface.neutrino_propagation.propagation_state import canonical_channel_states
from bhsm.interface.neutrino_scale import build_neutral_scale_report, derive_neutral_scale_law


def test_dimensionless_only_closure_emits_no_physical_mass() -> None:
    report = build_neutral_scale_report()
    assert report.dimensionful_scale_achieved is False
    assert report.dimensionful_mass_output_produced is False
    assert all(row.effective_mass_eV is None for row in report.dimensionful_mass_attempt)
    assert all(row.effective_mass_GeV is None for row in report.dimensionful_mass_attempt)


def test_effective_mass_accepts_a_unit_source_only_when_explicitly_valid() -> None:
    kernel = load_neutral_kernel()
    scale = replace(
        derive_neutral_scale_law(),
        status_after="ARTIFACT_BACKED_DIMENSIONFUL_SCALE",
        scale_value_eV=2.0,
        scale_value_GeV=2.0e-9,
        unit_available=True,
        unit_source="synthetic unit-source test fixture",
        remaining_missing_object="none",
    )
    result = compute_neutrino_propagation_mass(
        kernel,
        canonical_channel_states()[1],
        build_curvature_threshold(kernel),
        load_neutral_scale_law(),
        build_background_coupling(kernel),
        neutral_scale_result=scale,
    )
    assert result.effective_mass_eV == 2.0 * result.effective_mass_dimensionless
    assert result.effective_mass_GeV == 2.0e-9 * result.effective_mass_dimensionless

