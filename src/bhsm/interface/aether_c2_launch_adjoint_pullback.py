"""Cotangent pullback through the reset-generated C2 launch chart."""

from __future__ import annotations

from typing import Any

import numpy as np


def c2_launch_adjoint_pullback(
    *,
    reset_tangent_basis: np.ndarray,
    event_image_basis: np.ndarray,
    outgoing_field_action: np.ndarray,
    state_covector_action_dual: np.ndarray,
    direct_seam_covector_action_dual: np.ndarray,
    state_dimension: int,
    rank_threshold: float = 1.0e-8,
) -> dict[str, Any]:
    """Split a full reset-tangent force into seam and outgoing C2 pieces.

    The first half of the reset product is the outgoing C2 seed after the
    certified forward swap.  All arrays use the stored action-normalized
    coordinates, so Euclidean transpose is the corresponding dual pullback.
    """

    tangent = np.asarray(reset_tangent_basis, dtype=float)
    image_basis = np.asarray(event_image_basis, dtype=float)
    field = np.asarray(outgoing_field_action, dtype=float)
    state_covector = np.asarray(state_covector_action_dual, dtype=float)
    direct_covector = np.asarray(direct_seam_covector_action_dual, dtype=float)
    product_dimension, tangent_dimension = tangent.shape
    if product_dimension != 2 * state_dimension:
        raise ValueError("reset tangent has the wrong product dimension")
    if image_basis.shape[0] != state_dimension:
        raise ValueError("event image has the wrong state dimension")
    if field.shape != (state_dimension,) or state_covector.shape != (
        state_dimension,
    ):
        raise ValueError("field and state covector must use the C2 state space")
    if direct_covector.shape != (product_dimension,):
        raise ValueError("direct seam covector must use the reset product space")
    if not all(
        np.all(np.isfinite(value))
        for value in (tangent, image_basis, field, state_covector, direct_covector)
    ):
        raise ValueError("finite launch-adjoint inputs required")
    if not np.isfinite(rank_threshold) or rank_threshold <= 0.0:
        raise ValueError("positive finite rank threshold required")

    seed_map = tangent[:state_dimension]
    _, seed_singular_values, seed_vh = np.linalg.svd(
        seed_map, full_matrices=True
    )
    seed_rank = int(np.count_nonzero(seed_singular_values > rank_threshold))
    if image_basis.shape[1] != seed_rank:
        raise ValueError("event image basis does not have the seed-map rank")
    seed_kernel_coordinates = seed_vh[seed_rank:].T
    fixed_seed_lift = tangent @ seed_kernel_coordinates

    image_projection_residual = float(
        np.linalg.norm(
            seed_map - image_basis @ (image_basis.T @ seed_map), ord=2
        )
    )
    field_image_coordinates = image_basis.T @ field
    field_transverse = field - image_basis @ field_image_coordinates
    # Remove cancellation-level roundoff in the nearly tangent subtraction.
    field_transverse -= image_basis @ (image_basis.T @ field_transverse)
    transverse_scale = float(np.linalg.norm(field_transverse))
    if not transverse_scale > rank_threshold:
        raise ValueError("outgoing field is not transverse to the event image")
    transverse_unit = field_transverse / transverse_scale
    orthonormal_launch_basis = np.column_stack((image_basis, transverse_unit))

    natural_launch_map = np.column_stack((image_basis, field))
    natural_to_orthonormal = np.zeros((seed_rank + 1, seed_rank + 1))
    natural_to_orthonormal[:seed_rank, :seed_rank] = np.eye(seed_rank)
    natural_to_orthonormal[:seed_rank, -1] = field_image_coordinates
    natural_to_orthonormal[-1, -1] = transverse_scale

    downstream_reset_pullback = seed_map.T @ state_covector
    direct_reset_pullback = tangent.T @ direct_covector
    total_reset_pullback = direct_reset_pullback + downstream_reset_pullback
    natural_launch_pullback = natural_launch_map.T @ state_covector
    orthonormal_launch_pullback = orthonormal_launch_basis.T @ state_covector
    transformed_orthonormal_pullback = (
        natural_to_orthonormal.T @ orthonormal_launch_pullback
    )
    natural_pullback_residual = float(
        np.linalg.norm(natural_launch_pullback - transformed_orthonormal_pullback)
    )
    natural_pullback_scale = max(
        1.0,
        float(np.linalg.norm(natural_launch_pullback)),
        float(np.linalg.norm(transformed_orthonormal_pullback)),
    )

    return {
        "seed_map": seed_map,
        "seed_singular_values": seed_singular_values,
        "seed_kernel_coordinates": seed_kernel_coordinates,
        "fixed_seed_lift": fixed_seed_lift,
        "orthonormal_launch_basis": orthonormal_launch_basis,
        "natural_launch_map": natural_launch_map,
        "natural_to_orthonormal": natural_to_orthonormal,
        "downstream_reset_pullback": downstream_reset_pullback,
        "direct_reset_pullback": direct_reset_pullback,
        "total_reset_pullback": total_reset_pullback,
        "natural_launch_pullback": natural_launch_pullback,
        "orthonormal_launch_pullback": orthonormal_launch_pullback,
        "seed_rank": seed_rank,
        "seed_kernel_dimension": int(seed_kernel_coordinates.shape[1]),
        "launch_dimension": int(natural_launch_map.shape[1]),
        "transverse_scale": transverse_scale,
        "image_projection_residual_norm": image_projection_residual,
        "downstream_kernel_annihilation_residual_norm": float(
            np.linalg.norm(
                seed_kernel_coordinates.T @ downstream_reset_pullback
            )
        ),
        "kernel_split_residual_norm": float(
            np.linalg.norm(
                seed_kernel_coordinates.T @ total_reset_pullback
                - fixed_seed_lift.T @ direct_covector
            )
        ),
        "natural_orthonormal_pullback_residual_norm": float(
            natural_pullback_residual
        ),
        "natural_orthonormal_pullback_relative_residual": float(
            natural_pullback_residual / natural_pullback_scale
        ),
        "explicit_matrix_inverse_formed": False,
        "tangent_dimension": tangent_dimension,
    }


__all__ = ["c2_launch_adjoint_pullback"]
