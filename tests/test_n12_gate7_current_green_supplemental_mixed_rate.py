from __future__ import annotations

from itertools import permutations
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/derive_n12_gate7_current_green_supplemental_mixed_rate.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("supplemental_mixed_rate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _symmetric_tensor(rng: np.random.Generator, order: int, scale: float) -> np.ndarray:
    value = rng.normal(scale=scale, size=(3,) * order)
    variants = [value.transpose(ordering) for ordering in permutations(range(order))]
    return sum(variants) / len(variants)


def test_rectangular_mixed_rate_matches_independent_polynomial_difference(monkeypatch) -> None:
    module = _module()
    rng = np.random.default_rng(2141)
    linear = rng.normal(scale=0.1, size=3)
    quadratic = np.diag([1.0, 2.0, 4.0])
    cubic = _symmetric_tensor(rng, 3, 0.08)
    quartic = _symmetric_tensor(rng, 4, 0.025)
    quintic = _symmetric_tensor(rng, 5, 0.006)
    action_weights = np.array([1.3, 0.8, 1.1])

    def derivatives(state: np.ndarray) -> tuple[np.ndarray, ...]:
        x = np.asarray(state, dtype=float)
        gradient = (
            linear + quadratic @ x
            + 0.5 * np.einsum("ijk,j,k->i", cubic, x, x)
            + np.einsum("ijkl,j,k,l->i", quartic, x, x, x) / 6.0
            + np.einsum("ijklm,j,k,l,m->i", quintic, x, x, x, x) / 24.0
        )
        hessian = (
            quadratic + np.einsum("ijk,k->ij", cubic, x)
            + 0.5 * np.einsum("ijkl,k,l->ij", quartic, x, x)
            + np.einsum("ijklm,k,l,m->ij", quintic, x, x, x) / 6.0
        )
        third = (
            cubic + np.einsum("ijkl,l->ijk", quartic, x)
            + 0.5 * np.einsum("ijklm,l,m->ijk", quintic, x, x)
        )
        fourth = quartic + np.einsum("ijklm,m->ijkl", quintic, x)
        return gradient, hessian, third, fourth, quintic

    def signed(state: np.ndarray, *legs: np.ndarray) -> np.ndarray:
        tensor = derivatives(state)[len(legs) - 1]
        matrix_legs = [np.asarray(leg).ndim == 2 for leg in legs]
        dimensions = [np.asarray(leg).shape[1] for leg in legs if np.asarray(leg).ndim == 2]
        result = np.empty(dimensions or (), dtype=float)
        for output_index in np.ndindex(*dimensions) if dimensions else [()]:
            directions = []
            cursor = 0
            for leg, is_matrix in zip(legs, matrix_legs, strict=True):
                array = np.asarray(leg, dtype=float)
                if is_matrix:
                    directions.append(
                        array[:, output_index[cursor]] / action_weights
                    )
                    cursor += 1
                else:
                    directions.append(array / action_weights)
            value = tensor
            for direction in directions:
                value = np.tensordot(value, direction, axes=(0, 0))
            result[output_index] = float(value)
        return result

    q_weights = np.array([1.2])
    reduced_weights = np.array([0.8, 1.1])
    monkeypatch.setattr(module.center, "QDIM", 1)
    monkeypatch.setattr(module.center, "REDUCED", 2)
    monkeypatch.setattr(module.center, "STATE", 3)
    monkeypatch.setattr(module.center, "OUTPUTS", 4)
    monkeypatch.setattr(module.center, "SELECTED", 0)
    monkeypatch.setattr(
        module.center, "metric_data",
        lambda: (q_weights, reduced_weights, None, None),
    )
    monkeypatch.setattr(module.center, "_exact_jet", lambda state: derivatives(state)[:2])
    monkeypatch.setattr(module.center, "_signed", signed)

    weights = action_weights
    reference = np.array([1.0, 0.0])

    def direct_rate(augmented: np.ndarray) -> np.ndarray:
        state = augmented[:3]
        descriptor = float(augmented[3])
        gradient, hessian = derivatives(state)[:2]
        reduced_hessian = hessian[1:, 1:]
        values, vectors = np.linalg.eigh(reduced_hessian)
        psi = vectors[:, 0]
        if psi @ reference < 0.0:
            psi = -psi
        configuration = q_weights * state[1:2]
        gradient_action = gradient / weights
        hessian_action = hessian / weights[:, None] / weights[None, :]
        forcing = reduced_weights * (
            np.array([q_weights[0] * gradient_action[0], 0.0])
            - hessian_action[1:, :1] @ configuration
        )
        bordered = np.block([
            [reduced_hessian - values[0] * np.eye(2), psi[:, None]],
            [psi[None, :], np.zeros((1, 1))],
        ])
        response = np.linalg.solve(bordered, np.r_[forcing, 0.0])
        hard, bpsi = response[:-1], response[-1]
        numerator = np.r_[
            descriptor * configuration,
            reduced_weights * (bpsi * psi + descriptor * hard),
        ]
        norm = np.linalg.norm(numerator)
        field = numerator / norm
        reduced_lift = np.zeros((3, 2))
        reduced_lift[1:] = reduced_weights[:, None] * np.eye(2)
        p_action = reduced_lift @ psi
        hard_action = np.r_[configuration, reduced_weights * hard]
        cpsi, remainder = signed(
            state, p_action, p_action, np.column_stack((p_action, hard_action)),
        )
        return np.r_[field, (cpsi * bpsi + descriptor * remainder) / norm]

    center = np.array([0.3, -0.2, 0.15, 0.7])
    left = np.array([0.11, -0.07, 0.05, -0.09])
    right = np.array([
        [0.03, -0.08],
        [0.06, 0.02],
        [-0.04, 0.09],
        [0.10, -0.05],
    ])
    actual, diagnostics = module.mixed_rate_map(
        center[:3], center[3], weights, reference, left, right,
    )

    def difference(step: float) -> np.ndarray:
        columns = []
        for column in right.T:
            raw_left = np.r_[left[:3] / weights, left[3]]
            raw_column = np.r_[column[:3] / weights, column[3]]
            columns.append((
                direct_rate(center + step * raw_left + step * raw_column)
                - direct_rate(center + step * raw_left - step * raw_column)
                - direct_rate(center - step * raw_left + step * raw_column)
                + direct_rate(center - step * raw_left - step * raw_column)
            ) / (4.0 * step**2))
        return np.column_stack(columns)

    coarse = difference(2.0e-3)
    fine = difference(1.0e-3)
    expected = (4.0 * fine - coarse) / 3.0
    np.testing.assert_allclose(actual, expected, rtol=2.0e-6, atol=2.0e-8)
    assert diagnostics.base_response_residual_2_norm < 1.0e-13
    assert diagnostics.left_first_response_relative_residual < 1.0e-13
    assert diagnostics.right_first_response_relative_residual < 1.0e-13
    assert diagnostics.mixed_response_relative_residual < 1.0e-13
    assert diagnostics.mixed_eigenline_normalization_residual < 1.0e-13


def test_rectangular_mixed_rate_rejects_incompatible_shapes(monkeypatch) -> None:
    module = _module()
    monkeypatch.setattr(module.center, "STATE", 3)
    monkeypatch.setattr(module.center, "OUTPUTS", 4)
    with pytest.raises(ValueError, match="incompatible shapes"):
        module.mixed_rate_map(
            np.zeros(3), 0.0, np.ones(3), np.ones(2),
            np.zeros(4), np.zeros((3, 1)),
        )
