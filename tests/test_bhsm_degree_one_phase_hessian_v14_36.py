from __future__ import annotations

import numpy as np

from bhsm.interface.completion.degree_one_phase_hessian_completion_gate_v14_36 import (
    all_payloads,
    materialization_hashes,
)
from bhsm.interface.completion.degree_one_phase_hessian_v14_36 import (
    BOXES,
    FLAVOR_CHANNELS,
    berger_channel_eigenvalue,
    bifurcation_gate_payload,
    completion_payload,
    finite_box_phase_eigenvalues,
    path_b_density_derivatives,
    phase_second_variation_density,
    positivity_theorem_payload,
    round_smash_spectrum_payload,
)


def test_path_b_density_derivatives_have_required_signs() -> None:
    fp, fpp = path_b_density_derivatives(np.asarray([0.0, 0.5, 2.0]))
    assert np.all(fp > 0.0)
    assert np.all(fpp >= 0.0)
    assert phase_second_variation_density(0.5, 0.25, -0.1) > 0.0


def test_requested_channel_costs_are_positive_and_ordered() -> None:
    values = [berger_channel_eigenvalue(*channel) for channel in FLAVOR_CHANNELS]
    assert all(value > 0.0 for value in values)
    assert values == sorted(values)


def test_finite_box_requested_channels_have_no_negative_mode() -> None:
    for channel in FLAVOR_CHANNELS:
        values = finite_box_phase_eigenvalues(*channel, points=140, count=2)
        assert np.min(values) > 0.0


def test_lowest_box_modes_approach_zero_from_above() -> None:
    channel = (4, 4)
    lowest = [
        finite_box_phase_eigenvalues(*channel, points=140, x_min=left, x_max=right, count=1)[0]
        for left, right in BOXES
    ]
    assert lowest[0] > lowest[1] > lowest[2] > 0.0


def test_scientific_payloads_validate() -> None:
    for payload in (
        positivity_theorem_payload(),
        round_smash_spectrum_payload(),
        bifurcation_gate_payload(),
        completion_payload(),
    ):
        assert payload["validation_passed"]
    assert completion_payload()["phase_Hessian_gate"] == "PASSED_NONNEGATIVE_NO_BIFURCATION"
    assert completion_payload()["BHSM_complete"] is False


def test_deterministic_materialization(tmp_path) -> None:
    first = materialization_hashes(tmp_path / "one")
    second = materialization_hashes(tmp_path / "two")
    assert first == second
    assert len(first) == len(all_payloads()) == 4
