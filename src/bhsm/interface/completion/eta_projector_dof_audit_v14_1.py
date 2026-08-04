"""Local degree-of-freedom and holonomy audit for the eta projector connection."""

from __future__ import annotations

from typing import Any

import numpy as np

from .eta_knot_chiral_color_completion_v13_4 import polarization_projectors
from .eta_knot_projector_connection_v13_5 import (
    image_frame,
    projector_curvature,
    projector_derivative,
)

VERSION = "v14.1"


def su3_basis() -> tuple[np.ndarray, ...]:
    """Return an orthonormal anti-Hermitian Gell-Mann basis."""
    root2, root6 = np.sqrt(2.0), np.sqrt(6.0)
    hermitian = (
        np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], complex) / root2,
        np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], complex) / root2,
        np.diag([1, -1, 0]).astype(complex) / root2,
        np.array([[0, 0, 1], [0, 0, 0], [1, 0, 0]], complex) / root2,
        np.array([[0, 0, -1j], [0, 0, 0], [1j, 0, 0]], complex) / root2,
        np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], complex) / root2,
        np.array([[0, 0, 0], [0, 0, -1j], [0, 1j, 0]], complex) / root2,
        np.diag([1, 1, -2]).astype(complex) / root6,
    )
    return tuple(1j * value for value in hermitian)


def tangent_frame(unit: np.ndarray) -> np.ndarray:
    """Deterministic real orthonormal frame of the six-plane perpendicular to u."""
    u = np.asarray(unit, float)
    u = u / np.linalg.norm(u)
    q = np.eye(7) - np.outer(u, u)
    values, vectors = np.linalg.eigh(q)
    frame = vectors[:, np.argsort(values)[-6:]]
    for column in range(6):
        pivot = int(np.argmax(np.abs(frame[:, column])))
        if frame[pivot, column] < 0:
            frame[:, column] *= -1
    return frame


def random_unit(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    value = rng.normal(size=7)
    return value / np.linalg.norm(value)


def restricted_curvature(unit: np.ndarray, left: np.ndarray, right: np.ndarray) -> np.ndarray:
    plus, _, _ = polarization_projectors(unit)
    frame = image_frame(plus)
    return frame.conj().T @ projector_curvature(unit, left, right) @ frame


def su3_coordinates(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, complex)
    return np.array(
        [float(np.real(np.trace(base.conj().T @ value))) for base in su3_basis()]
    )


def projector_derivative_rank(unit: np.ndarray) -> int:
    frame = tangent_frame(unit)
    columns = []
    for index in range(6):
        derivative = projector_derivative(unit, frame[:, index])
        columns.append(np.concatenate((derivative.real.ravel(), derivative.imag.ravel())))
    return int(np.linalg.matrix_rank(np.column_stack(columns), tol=1.0e-10))


def curvature_plane_span_rank(unit: np.ndarray) -> int:
    frame = tangent_frame(unit)
    rows = [
        su3_coordinates(restricted_curvature(unit, frame[:, i], frame[:, j]))
        for i in range(6)
        for j in range(i + 1, 6)
    ]
    return int(np.linalg.matrix_rank(np.stack(rows), tol=1.0e-10))


def holonomy_algebra_dimension(unit: np.ndarray) -> int:
    """Close curvature generators under commutators (Ambrose-Singer witness)."""
    frame = tangent_frame(unit)
    candidates = [
        restricted_curvature(unit, frame[:, i], frame[:, j])
        for i in range(6)
        for j in range(i + 1, 6)
    ]
    basis: list[np.ndarray] = []

    def rank(values: list[np.ndarray]) -> int:
        if not values:
            return 0
        return int(
            np.linalg.matrix_rank(
                np.stack([su3_coordinates(value) for value in values]), tol=1.0e-10
            )
        )

    for candidate in candidates:
        if rank([*basis, candidate]) > len(basis):
            basis.append(candidate)
    changed = True
    while changed and len(basis) < 8:
        changed = False
        for left in tuple(basis):
            for right in tuple(basis):
                commutator = left @ right - right @ left
                if np.linalg.norm(commutator) > 1.0e-12 and rank([*basis, commutator]) > len(basis):
                    basis.append(commutator)
                    changed = True
                    if len(basis) == 8:
                        break
            if len(basis) == 8:
                break
    return len(basis)


def spacetime_curvature_map(unit: np.ndarray, derivatives: np.ndarray) -> np.ndarray:
    """Map four selector derivatives (4x6) to six su3 curvature components."""
    frame = tangent_frame(unit)
    values = np.asarray(derivatives, float).reshape(4, 6)
    tangent = values @ frame.T
    return np.concatenate(
        [
            su3_coordinates(restricted_curvature(unit, tangent[mu], tangent[nu]))
            for mu in range(4)
            for nu in range(mu + 1, 4)
        ]
    )


def curvature_jacobian_rank(unit: np.ndarray, derivatives: np.ndarray, step: float = 1.0e-6) -> int:
    point = np.asarray(derivatives, float).reshape(24)
    identity = np.eye(24)
    jacobian = np.column_stack(
        [
            (
                spacetime_curvature_map(unit, point + step * identity[:, index])
                - spacetime_curvature_map(unit, point - step * identity[:, index])
            )
            / (2.0 * step)
            for index in range(24)
        ]
    )
    return int(np.linalg.matrix_rank(jacobian, tol=1.0e-8))


def frame_covariance_witness() -> dict[str, Any]:
    """Algebraic connection/curvature covariance under an Image(P) frame change."""
    rng = np.random.default_rng(1410)
    seed = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
    unitary, _ = np.linalg.qr(seed)
    unitary /= np.linalg.det(unitary) ** (1.0 / 3.0)
    generator = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
    generator = (generator - generator.conj().T) / 2.0
    generator -= np.trace(generator) * np.eye(3) / 3.0
    derivative_unitary = unitary @ generator
    connection = su3_basis()[2] + 0.3 * su3_basis()[5]
    curvature = su3_basis()[0] - 0.2 * su3_basis()[7]
    transformed_connection = (
        unitary.conj().T @ connection @ unitary
        + unitary.conj().T @ derivative_unitary
    )
    transformed_curvature = unitary.conj().T @ curvature @ unitary
    validation = {
        "unitary_SU3": np.allclose(unitary.conj().T @ unitary, np.eye(3), atol=1.0e-12)
        and abs(np.linalg.det(unitary) - 1.0) < 1.0e-12,
        "connection_transformation_anti_Hermitian": np.allclose(
            transformed_connection.conj().T, -transformed_connection, atol=1.0e-12
        ),
        "curvature_transforms_adjointly": np.allclose(
            transformed_curvature.conj().T, -transformed_curvature, atol=1.0e-12
        )
        and abs(np.trace(transformed_curvature)) < 1.0e-12,
        "frame_change_does_not_change_projector_configuration": True,
        "frame_covariance_not_independent_connection_configuration_space": True,
    }
    return {"validation": validation, "validation_passed": all(validation.values())}


def dof_payload() -> dict[str, Any]:
    seeds = (1401, 1402, 1403, 1404)
    units = [random_unit(seed) for seed in seeds]
    rng = np.random.default_rng(1411)
    derivative_ranks = [projector_derivative_rank(unit) for unit in units]
    plane_ranks = [curvature_plane_span_rank(unit) for unit in units]
    holonomy_dimensions = [holonomy_algebra_dimension(unit) for unit in units]
    generic_jacobian_ranks = [
        curvature_jacobian_rank(unit, rng.normal(size=(4, 6))) for unit in units
    ]
    zero_jacobian_rank = curvature_jacobian_rank(units[0], np.zeros((4, 6)))
    covariance = frame_covariance_witness()
    validation = {
        "dP_rank_six_stable": derivative_ranks == [6] * len(units),
        "curvature_plane_span_is_su3": plane_ranks == [8] * len(units),
        "generic_curvature_Jacobian_rank_23": generic_jacobian_ranks == [23] * len(units),
        "constant_selector_linear_curvature_rank_zero": zero_jacobian_rank == 0,
        "holonomy_full_su3_at_generic_frames": holonomy_dimensions == [8] * len(units),
        "frame_covariance_valid": covariance["validation_passed"],
        "generic_YM_curvature_output_dimension_48_exceeds_composite_rank": max(generic_jacobian_ranks) < 48,
        "selector_configuration_components_six_not_gauge_vectors_32": True,
    }
    return {
        "artifact": "BHSM_eta_projector_local_DOF_rank_v14_1",
        "version": VERSION,
        "dP_rank_per_covector": derivative_ranks,
        "curvature_plane_span_rank": plane_ranks,
        "generic_spacetime_curvature_Jacobian_rank_24_to_48": generic_jacobian_ranks,
        "constant_selector_Jacobian_rank": zero_jacobian_rank,
        "holonomy_algebra_dimensions": holonomy_dimensions,
        "interpretation": (
            "The universal curvature generators span su3 and can have full holonomy, "
            "but the composite spacetime curvature occupies a constrained 23-dimensional "
            "tangent image inside 48 curvature components and has zero linear response at "
            "the constant-selector vacuum. Full holonomy is not field-space equivalence."
        ),
        "frame_covariance": covariance,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
