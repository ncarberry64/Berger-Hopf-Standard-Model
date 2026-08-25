from __future__ import annotations

import numpy as np
import pytest

from bhsm.interface.parametric_finite_stratum_exterior_oracle import (
    schur_weyl_directional_jet,
)


def _fixture() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    base = np.asarray(
        [
            [4.0, 0.2, -0.4, 0.1],
            [0.2, 3.5, 0.3, -0.2],
            [-0.4, 0.3, 5.0, 0.6],
            [0.1, -0.2, 0.6, 4.5],
        ]
    )
    first = np.asarray(
        [
            [0.2, -0.1, 0.05, 0.02],
            [-0.1, 0.3, -0.04, 0.07],
            [0.05, -0.04, -0.2, 0.06],
            [0.02, 0.07, 0.06, 0.1],
        ]
    )
    second = np.asarray(
        [
            [0.05, 0.02, -0.01, 0.03],
            [0.02, -0.04, 0.02, -0.01],
            [-0.01, 0.02, 0.06, -0.02],
            [0.03, -0.01, -0.02, 0.08],
        ]
    )
    return base, first, second


def test_value_and_two_jets_match_centered_differences() -> None:
    base, first, second = _fixture()
    result = schur_weyl_directional_jet(
        base, first, second, (0, 1), z=-1.0
    )
    step = 2.0e-4

    def value(parameter: float) -> np.ndarray:
        matrix = base + parameter * first + 0.5 * parameter**2 * second
        return schur_weyl_directional_jet(
            matrix,
            first + parameter * second,
            second,
            (0, 1),
            z=-1.0,
        )["value"]

    plus = value(step)
    minus = value(-step)
    center = value(0.0)
    finite_first = (plus - minus) / (2.0 * step)
    finite_second = (plus - 2.0 * center + minus) / step**2
    assert np.linalg.norm(result["first"] - finite_first) < 1.0e-9
    assert np.linalg.norm(result["second"] - finite_second) < 2.0e-7
    assert result["explicit_matrix_inverse_formed"] is False


def test_block_unitary_covariance() -> None:
    base, first, second = _fixture()
    angle_b, angle_i = 0.31, -0.27
    ub = np.asarray(
        [[np.cos(angle_b), -np.sin(angle_b)], [np.sin(angle_b), np.cos(angle_b)]]
    )
    ui = np.asarray(
        [[np.cos(angle_i), -np.sin(angle_i)], [np.sin(angle_i), np.cos(angle_i)]]
    )
    unitary = np.block(
        [[ub, np.zeros((2, 2))], [np.zeros((2, 2)), ui]]
    )
    original = schur_weyl_directional_jet(
        base, first, second, (0, 1), z=-1.0
    )
    transformed = schur_weyl_directional_jet(
        unitary.T @ base @ unitary,
        unitary.T @ first @ unitary,
        unitary.T @ second @ unitary,
        (0, 1),
        z=-1.0,
    )
    for key in ("value", "first", "second"):
        assert np.linalg.norm(transformed[key] - ub.T @ original[key] @ ub) < 1.0e-12


def test_noncoercive_interior_and_nonhermitian_inputs_fail_closed() -> None:
    base, first, second = _fixture()
    bad = base.copy()
    bad[2:, 2:] = -2.0 * np.eye(2)
    with pytest.raises(np.linalg.LinAlgError, match="not certified coercive"):
        schur_weyl_directional_jet(bad, first, second, (0, 1), z=-1.0)
    nonhermitian = first.copy()
    nonhermitian[0, 1] += 0.2
    with pytest.raises(ValueError, match="Hermitian"):
        schur_weyl_directional_jet(
            base, nonhermitian, second, (0, 1), z=-1.0
        )
