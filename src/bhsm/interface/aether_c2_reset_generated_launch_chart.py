"""Linear-algebra construction of the reset-generated C2 launch chart.

The retained reset relation has a full-row-rank Jacobian ``J`` on the
event/child product.  After the certified double-event incidence is read in
the forward swapped orientation, the old event half is the new C2 seed.  Its
projection has one fewer tangent direction than a regular constrained child
because the ordered-event equation is still imposed at the seed.  The exact
fixed-descriptor vector field supplies the missing transverse direction.

This module constructs bases and projectors only.  It neither selects a reset
member nor inverts an Euler--Dirac kinetic block.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def _numerical_rank(values: np.ndarray, threshold: float) -> int:
    return int(np.count_nonzero(np.asarray(values, dtype=float) > threshold))


def reset_generated_launch_decomposition(
    *,
    reset_jacobian: np.ndarray,
    outgoing_field_action: np.ndarray,
    state_dimension: int,
    reset_rank: int,
    rank_threshold: float = 1.0e-8,
) -> dict[str, Any]:
    """Return the reset tangent, C2 seed image, lift kernel, and launch basis.

    Coordinates are action-normalized.  ``outgoing_field_action`` is the
    exact fixed-``s`` field at the event seed.  The returned launch basis is
    the orthonormal seed-image basis augmented by the normalized component of
    the outgoing field transverse to that image.
    """

    jacobian = np.asarray(reset_jacobian, dtype=float)
    field = np.asarray(outgoing_field_action, dtype=float)
    if jacobian.ndim != 2:
        raise ValueError("reset Jacobian must be a matrix")
    if jacobian.shape[1] != 2 * state_dimension:
        raise ValueError("reset Jacobian has the wrong product dimension")
    if field.shape != (state_dimension,):
        raise ValueError("outgoing field has the wrong state dimension")
    if not (
        np.all(np.isfinite(jacobian))
        and np.all(np.isfinite(field))
        and np.isfinite(rank_threshold)
        and rank_threshold > 0.0
    ):
        raise ValueError("finite inputs and a positive rank threshold required")

    _, reset_singular_values, reset_vh = np.linalg.svd(
        jacobian, full_matrices=True
    )
    observed_reset_rank = _numerical_rank(reset_singular_values, rank_threshold)
    if observed_reset_rank != reset_rank:
        raise ValueError("reset Jacobian does not have the declared rank")
    reset_tangent = reset_vh[reset_rank:].T

    # In the forward swapped incidence, the original event half becomes the
    # outgoing C2 seed.  Its image remains on the ordered-event hypersurface.
    event_projection = reset_tangent[:state_dimension]
    event_u, event_singular_values, event_vh = np.linalg.svd(
        event_projection, full_matrices=True
    )
    event_rank = _numerical_rank(event_singular_values, rank_threshold)
    event_image = event_u[:, :event_rank]
    event_kernel_coordinates = event_vh[event_rank:].T
    event_lift_kernel = reset_tangent @ event_kernel_coordinates

    field_norm = float(np.linalg.norm(field))
    if not field_norm > 0.0:
        raise ValueError("nonzero outgoing field required")
    field_unit = field / field_norm
    transverse = field_unit - event_image @ (event_image.T @ field_unit)
    # The physical transverse component is small relative to the full field.
    # Reproject once to remove cancellation-level roundoff before normalizing.
    transverse -= event_image @ (event_image.T @ transverse)
    transverse_norm = float(np.linalg.norm(transverse))
    if not transverse_norm > rank_threshold:
        raise ValueError("outgoing field is not transverse to the event image")
    transverse_unit = transverse / transverse_norm
    launch_basis = np.column_stack((event_image, transverse_unit))

    return {
        "reset_singular_values": reset_singular_values,
        "reset_tangent_basis": reset_tangent,
        "event_projection_singular_values": event_singular_values,
        "event_image_basis": event_image,
        "event_lift_kernel_basis": event_lift_kernel,
        "outgoing_field_action": field,
        "outgoing_transverse_unit": transverse_unit,
        "launch_basis": launch_basis,
        "reset_rank": observed_reset_rank,
        "reset_tangent_dimension": int(reset_tangent.shape[1]),
        "event_projection_rank": event_rank,
        "event_lift_kernel_dimension": int(event_lift_kernel.shape[1]),
        "launch_dimension": int(launch_basis.shape[1]),
        "reset_tangent_residual_norm": float(
            np.linalg.norm(jacobian @ reset_tangent, ord=2)
        ),
        "event_lift_projection_residual_norm": float(
            np.linalg.norm(event_lift_kernel[:state_dimension], ord=2)
        ),
        "event_lift_reset_residual_norm": float(
            np.linalg.norm(jacobian @ event_lift_kernel, ord=2)
        ),
        "outgoing_transverse_component_norm": transverse_norm,
        "launch_orthonormality_residual_norm": float(
            np.linalg.norm(
                launch_basis.T @ launch_basis
                - np.eye(launch_basis.shape[1]),
                ord=2,
            )
        ),
        "explicit_matrix_inverse_formed": False,
    }


__all__ = ["reset_generated_launch_decomposition"]
