from __future__ import annotations

import numpy as np
import pytest

from bhsm.interface.current_green_supplemental_midpoint import (
    AmbientCompletion,
    complete_ambient_basis,
    reconstruct_mapped_midpoint_hessian,
    reconstruct_midpoint_hessian,
    solve_midpoint_coordinates,
)


def test_completion_retains_exact_tensor_directions_and_spans_ambient_map() -> None:
    rng = np.random.default_rng(2099)
    frame = rng.normal(size=(8, 5))
    axis = rng.normal(size=5)
    axis /= np.linalg.norm(axis)
    # Construct the coordinate complement without asking a rank heuristic to
    # choose its dimension.
    seed = np.eye(5)[:, int(np.argmin(abs(axis)))]
    seed -= axis * (axis @ seed)
    vectors = [seed / np.linalg.norm(seed)]
    for column in np.eye(5).T:
        candidate = column - axis * (axis @ column)
        for vector in vectors:
            candidate -= vector * (vector @ candidate)
        if np.linalg.norm(candidate) > 1.0e-10 and len(vectors) < 4:
            vectors.append(candidate / np.linalg.norm(candidate))
    transverse = np.column_stack(vectors)
    completion = complete_ambient_basis(frame, axis, transverse)
    assert completion.retained_directions.shape == (8, 4)
    assert completion.complement_directions.shape == (8, 4)
    assert np.allclose(completion.retained_directions, frame @ transverse)
    assert np.linalg.matrix_rank(completion.full_basis) == 8
    assert completion.coordinate_basis_residual < 5.0e-13
    assert completion.normal_frame_residual < 5.0e-13

    ambient_map = rng.normal(size=(8, 11))
    coordinates = solve_midpoint_coordinates(completion, ambient_map)
    reconstructed = (
        completion.retained_directions @ coordinates.retained
        + completion.complement_directions @ coordinates.complement
    )
    assert np.allclose(reconstructed, ambient_map, rtol=2.0e-14, atol=2.0e-14)
    assert coordinates.relative_reconstruction_residual_2 < 5.0e-14


def test_block_reconstruction_equals_direct_full_hessian_pullback() -> None:
    rng = np.random.default_rng(2111)
    outputs, retained, complement, columns = 3, 4, 2, 7
    hessian = rng.normal(size=(outputs, retained + complement, retained + complement))
    hessian = 0.5 * (hessian + hessian.transpose(0, 2, 1))
    a = rng.normal(size=(retained, columns))
    d = rng.normal(size=(complement, columns))
    coordinates = type("Coordinates", (), {"retained": a, "complement": d})()
    actual = reconstruct_midpoint_hessian(
        hessian[:, :retained, :retained],
        hessian[:, retained:, :retained],
        hessian[:, retained:, retained:],
        coordinates,
    )
    transform = np.vstack((a, d))
    expected = np.einsum("oab,ai,bj->oij", hessian, transform, transform)
    assert np.allclose(actual, expected, rtol=2.0e-14, atol=2.0e-14)


def test_mapped_reconstruction_applies_all_signed_terms_before_output_map() -> None:
    rng = np.random.default_rng(2123)
    frame = rng.normal(size=(7, 4))
    axis = rng.normal(size=4)
    axis /= np.linalg.norm(axis)
    q, _ = np.linalg.qr(np.column_stack((axis, np.eye(4))))
    transverse = q[:, 1:]
    completion = complete_ambient_basis(frame, axis, transverse)
    ambient_map = rng.normal(size=(7, 9))
    output_map = rng.normal(size=(3, 5))
    full_hessian = rng.normal(size=(5, 7, 7))
    full_hessian = 0.5 * (
        full_hessian + full_hessian.transpose(0, 2, 1)
    )
    basis = completion.full_basis
    basis_hessian = np.einsum(
        "oab,ai,bj->oij", full_hessian, basis, basis, optimize=True,
    )
    actual, coordinates = reconstruct_mapped_midpoint_hessian(
        output_map,
        basis_hessian[:, :3, :3],
        basis_hessian[:, 3:, :3],
        basis_hessian[:, 3:, 3:],
        completion,
        ambient_map,
    )
    expected = np.einsum(
        "co,oab,ai,bj->cij",
        output_map, full_hessian, ambient_map, ambient_map,
        optimize=True,
    )
    assert np.allclose(actual, expected, rtol=5.0e-14, atol=5.0e-14)
    assert coordinates.relative_reconstruction_residual_2 < 5.0e-14


def test_completion_and_reconstruction_fail_closed_on_invalid_inputs() -> None:
    frame = np.eye(4, 3)
    axis = np.array([1.0, 0.0, 0.0])
    basis = np.eye(3)[:, 1:]
    with pytest.raises(ValueError, match="finite"):
        complete_ambient_basis(frame * np.nan, axis, basis)
    with pytest.raises(ValueError, match="coordinate basis"):
        complete_ambient_basis(frame, axis, basis + 0.1)

    singular = AmbientCompletion(
        retained_directions=np.eye(4)[:, :2],
        complement_directions=np.eye(4)[:, 2:],
        full_basis=np.diag([1.0, 1.0, 1.0, 0.0]),
        frame_qr_diagonal=np.ones(3),
        coordinate_basis_residual=0.0,
        normal_frame_residual=0.0,
        full_basis_condition_2=float("inf"),
    )
    with pytest.raises(np.linalg.LinAlgError):
        solve_midpoint_coordinates(singular, np.eye(4))
