import math

import numpy as np
import pytest

from bhsm.interface.universal_spectral_density import (
    source_contracted_spectral_density,
)


def density(symbol, frame=np.eye(1), *, complete=True, gate7=True):
    return source_contracted_spectral_density(
        symbol,
        (0.0, 1.0, 2.0),
        frame,
        action_version="TEST-ACTION",
        background_id="test-background",
        provenance=("unit-test retarded symbol",),
        complete_self_energy_ledger=complete,
        gate7_closed=gate7,
    )


def test_scalar_retarded_pole_gives_positive_lorentzian_density() -> None:
    mass_squared = 1.0
    epsilon = 0.2
    result = density(
        lambda spectral: np.asarray([[spectral - mass_squared + 1.0j * epsilon]])
    )
    expected = np.asarray([
        epsilon / (math.pi * ((spectral - mass_squared) ** 2 + epsilon**2))
        for spectral in result.spectral_points
    ])
    assert np.allclose(result.density_matrices[:, 0, 0].real, expected)
    assert result.minimum_density_eigenvalue > 0.0
    assert result.maximum_linear_solve_relative_residual < 1.0e-14
    result.require_physical_promotion()


def test_rectangular_source_frame_contracts_only_selected_directions() -> None:
    frame = np.asarray([[1.0], [0.0]])
    result = density(
        lambda spectral: np.diag([
            spectral - 1.0 + 0.1j,
            spectral - 4.0 + 0.3j,
        ]),
        frame,
    )
    expected_at_one = 1.0 / (math.pi * 0.1)
    assert result.density_matrices.shape == (3, 1, 1)
    assert np.isclose(result.density_matrices[1, 0, 0].real, expected_at_one)


def test_advanced_sign_fails_spectral_positivity() -> None:
    result = density(lambda spectral: np.asarray([[spectral - 1.0 - 0.2j]]))
    assert result.positive_semidefinite is False
    with pytest.raises(RuntimeError, match="positive_spectral_measure"):
        result.require_physical_promotion()


def test_open_gate_and_incomplete_ledger_block_promotion() -> None:
    result = density(
        lambda spectral: np.asarray([[spectral - 1.0 + 0.2j]]),
        complete=False,
        gate7=False,
    )
    with pytest.raises(RuntimeError, match="Gate7_closed_background"):
        result.require_physical_promotion()


def test_spectral_mesh_must_be_strictly_increasing() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        source_contracted_spectral_density(
            lambda spectral: np.asarray([[spectral + 1.0j]]),
            (0.0, 0.0),
            np.eye(1),
            action_version="TEST-ACTION",
            background_id="test-background",
            provenance=("unit-test",),
            complete_self_energy_ledger=True,
            gate7_closed=True,
        )
