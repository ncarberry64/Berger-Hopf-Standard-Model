import numpy as np
import pytest

from bhsm.interface.universal_dressed_pole import solve_dressed_pole


def solve(symbol, derivative, initial, mode, *, complete=True, gate7=True):
    return solve_dressed_pole(
        symbol,
        derivative,
        initial,
        mode,
        action_version="TEST-ACTION",
        background_id="test-background",
        provenance=("unit-test self energy",),
        complete_self_energy_ledger=complete,
        gate7_closed=gate7,
    )


def test_scalar_complex_pole_returns_mass_width_and_residue() -> None:
    pole = 9.0 - 0.6j
    result = solve(
        lambda z: np.asarray([[z - pole]]),
        lambda _z: np.asarray([[1.0]]),
        8.0,
        np.asarray([1.0]),
    )
    result.require_physical_promotion()
    assert abs(result.spectral_parameter - pole) < 1.0e-14
    assert abs(result.pole_mass - 3.0) < 1.0e-14
    assert abs(result.pole_width - 0.2) < 1.0e-14
    assert abs(result.residue[0, 0] - 1.0) < 1.0e-14


def test_bordered_solver_tracks_selected_matrix_pole_without_determinant() -> None:
    first = 4.0 - 0.1j
    second = 7.0 - 0.4j
    result = solve(
        lambda z: np.diag([z - first, 2.0 * (z - second)]),
        lambda _z: np.diag([1.0, 2.0]),
        3.5,
        np.asarray([1.0, 0.0]),
    )
    assert abs(result.spectral_parameter - first) < 1.0e-14
    assert np.linalg.norm(result.right_mode - np.asarray([1.0, 0.0])) < 1.0e-14
    assert result.simple is True
    assert result.relative_symbol_residual < 1.0e-14


def test_upper_half_plane_pole_is_not_a_causal_decay_width() -> None:
    result = solve(
        lambda z: np.asarray([[z - (4.0 + 0.2j)]]),
        lambda _z: np.asarray([[1.0]]),
        4.0,
        np.asarray([1.0]),
    )
    assert result.causal_width is False
    with pytest.raises(RuntimeError, match="nonnegative_pole_width"):
        result.require_physical_promotion()


def test_incomplete_self_energy_or_open_gate_blocks_promotion() -> None:
    result = solve_dressed_pole(
        lambda z: np.asarray([[z - 1.0]]),
        lambda _z: np.asarray([[1.0]]),
        0.8,
        np.asarray([1.0]),
        action_version="TEST-ACTION",
        background_id="test-background",
        provenance=("unit-test",),
        complete_self_energy_ledger=False,
        gate7_closed=False,
    )
    with pytest.raises(RuntimeError, match="Gate7_closed_background"):
        result.require_physical_promotion()
