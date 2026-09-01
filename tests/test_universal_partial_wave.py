import cmath
import math

import numpy as np
import pytest

from bhsm.interface.universal_partial_wave import (
    analyze_partial_wave_unitarity,
    project_coupled_partial_waves,
)


def project(amplitude, maximum_angular_momentum=2):
    return project_coupled_partial_waves(
        amplitude,
        maximum_angular_momentum=maximum_angular_momentum,
        quadrature_order=24,
        action_version="TEST-ACTION",
        background_id="test-background",
        provenance=("unit-test amplitude",),
    )


def test_constant_amplitude_projects_only_to_s_wave() -> None:
    coefficient = 0.17 - 0.03j
    result = project(lambda _cosine: np.asarray([[16.0 * math.pi * coefficient]]))
    assert np.isclose(result.coefficients[0, 0, 0], coefficient)
    assert np.max(np.abs(result.coefficients[1:])) < 1.0e-15


def test_exact_elastic_phase_shift_saturates_complete_unitarity() -> None:
    phase_shift = 0.31
    partial_wave = (cmath.exp(2.0j * phase_shift) - 1.0) / (2.0j)
    result = project(
        lambda _cosine: np.asarray([[16.0 * math.pi * partial_wave]]),
        maximum_angular_momentum=0,
    )
    report = analyze_partial_wave_unitarity(
        result,
        np.asarray([1.0]),
        complete_channel_ledger=True,
    )
    report.require_unitarity()
    assert report.maximum_complete_channel_relative_residual < 1.0e-13


def test_incomplete_subspace_allows_absorption_but_not_excess() -> None:
    partial_wave = (0.8 - 1.0) / (2.0j)
    result = project(
        lambda _cosine: np.asarray([[16.0 * math.pi * partial_wave]]),
        maximum_angular_momentum=0,
    )
    report = analyze_partial_wave_unitarity(
        result,
        np.asarray([1.0]),
        complete_channel_ledger=False,
    )
    report.require_unitarity()
    assert report.rows[0].minimum_absorption_margin_eigenvalue > 0.0
    with pytest.raises(RuntimeError, match="complete coupled-channel"):
        analyze_partial_wave_unitarity(
            result,
            np.asarray([1.0]),
            complete_channel_ledger=True,
        ).require_unitarity()


def test_large_real_tree_partial_wave_is_flagged() -> None:
    result = project(
        lambda _cosine: np.asarray([[16.0 * math.pi * 0.6]]),
        maximum_angular_momentum=0,
    )
    report = analyze_partial_wave_unitarity(
        result,
        np.asarray([1.0]),
        complete_channel_ledger=False,
    )
    assert report.perturbative_real_bound_satisfied is False
    assert report.maximum_unitarity_excess > 0.0
    with pytest.raises(RuntimeError, match="unitarity excess"):
        report.require_unitarity()


def test_projection_rejects_inconsistent_channel_shapes() -> None:
    with pytest.raises(ValueError, match="channel dimension changed"):
        project_coupled_partial_waves(
            lambda cosine: np.eye(1 if cosine < 0.0 else 2),
            maximum_angular_momentum=0,
            quadrature_order=4,
            action_version="TEST-ACTION",
            background_id="test-background",
            provenance=("unit-test",),
        )
