from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/certify_n12_gate7_current_green_signed_transverse_causal_center.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("signed_causal_center", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_signed_output_and_input_maps_are_composed_before_norms() -> None:
    module = _module()
    rng = np.random.default_rng(1729)
    tensor = rng.normal(size=(5, 4, 4))
    tensor = 0.5 * (tensor + tensor.transpose(0, 2, 1))
    output_map = rng.normal(size=(3, 5))
    input_map = rng.normal(size=(4, 6))
    transformed = module._transformed(output_map, tensor, input_map)
    expected = np.empty((3, 6, 6))
    for left in range(6):
        for right in range(6):
            expected[:, left, right] = output_map @ np.einsum(
                "oab,a,b->o", tensor, input_map[:, left], input_map[:, right],
            )
    assert np.allclose(transformed, expected, rtol=2.0e-14, atol=2.0e-14)


def test_local_pair_covariances_retain_left_cross_right_evaluations() -> None:
    module = _module()
    rng = np.random.default_rng(1733)
    local = rng.normal(size=(module.COORDINATES, 2 * module.COORDINATES,
                             2 * module.COORDINATES))
    local = 0.5 * (local + local.transpose(0, 2, 1))
    covariances = module._covariance_blocks(local)
    left = local[:, :module.COORDINATES, :module.COORDINATES]
    cross = 2.0 * local[:, :module.COORDINATES, module.COORDINATES:]
    right = local[:, module.COORDINATES:, module.COORDINATES:]
    for covariance, block in zip(
        covariances, (left, cross, right), strict=True,
    ):
        flat = block.reshape((module.COORDINATES, -1))
        assert np.allclose(covariance, flat @ flat.T, rtol=2.0e-14, atol=2.0e-10)


def test_adjacent_diagonal_sources_are_combined_before_the_causal_norm() -> None:
    module = _module()
    rng = np.random.default_rng(1741)
    vectors = rng.normal(size=(2, 3, module.COORDINATES))
    local_covariances = np.einsum(
        "ipa,ipb->ipab", vectors, vectors, optimize=True,
    )
    adjacent = np.zeros((2, module.COORDINATES, module.COORDINATES))
    adjacent[1] = np.outer(vectors[0, 2], vectors[1, 0])
    maps = np.stack((
        np.eye(module.COORDINATES),
        np.eye(module.COORDINATES) + 1.0e-3 * rng.normal(
            size=(module.COORDINATES, module.COORDINATES)
        ),
    ))
    axes = rng.normal(size=(3, module.COORDINATES))
    axes /= np.linalg.norm(axes, axis=1)[:, None]
    longitudinal, transverse = module._causal_bounds(
        local_covariances, adjacent, maps, axes,
    )

    diagonal_node1_at_node2 = maps[1] @ vectors[0, 2] + vectors[1, 0]
    expected = [
        diagonal_node1_at_node2,
        vectors[1, 2],
        maps[1] @ vectors[0, 1],
        vectors[1, 1],
    ]
    axis = axes[2]
    expected_l = sum(abs(float(axis @ value)) for value in expected)
    expected_t = sum(float(np.linalg.norm(value - axis * (axis @ value)))
                     for value in expected)
    assert np.isclose(longitudinal[2], expected_l, rtol=2.0e-14)
    assert np.isclose(transverse[2], expected_t, rtol=2.0e-14)
