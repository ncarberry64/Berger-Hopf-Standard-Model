from __future__ import annotations

from bhsm.interface.neutrino_propagation.curvature_threshold import build_background_coupling, build_curvature_threshold
from bhsm.interface.neutrino_propagation.effective_mass import compute_neutrino_propagation_mass, load_neutral_scale_law
from bhsm.interface.neutrino_propagation.neutral_kernel import load_neutral_kernel
from bhsm.interface.neutrino_propagation.propagation_state import canonical_channel_states, normalized_state


def _inputs():
    kernel = load_neutral_kernel()
    return kernel, build_curvature_threshold(kernel), load_neutral_scale_law(), build_background_coupling(kernel)


def test_zero_propagation_gives_zero_bhsm_mass_contribution() -> None:
    kernel, threshold, scale, background = _inputs()
    state = normalized_state("stopped", (0.0, 1.0, 0.0), 0.0)
    result = compute_neutrino_propagation_mass(kernel, state, threshold, scale, background)
    assert result.effective_mass_dimensionless == 0.0
    assert result.effective_mass_eV is None
    assert result.effective_mass_GeV is None


def test_nonzero_propagation_responses_are_nonnegative() -> None:
    kernel, threshold, scale, background = _inputs()
    results = [
        compute_neutrino_propagation_mass(kernel, state, threshold, scale, background)
        for state in canonical_channel_states()
    ]
    assert all(row.effective_mass_dimensionless >= 0.0 for row in results)
    assert any(row.effective_mass_dimensionless > 0.0 for row in results)
    assert all(row.status == "OPEN_MISSING_NEUTRAL_SCALE" for row in results)
