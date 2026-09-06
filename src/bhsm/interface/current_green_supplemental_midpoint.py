"""Lossless basis completion for the Gate-7 midpoint Hessian supplement.

The retained midpoint tensor acts on 73 ambient directions ``U``.  Endpoint
transverse Hermite--Simpson variations need not remain in their span.  This
module completes those exact stored directions to a 99-dimensional ambient
basis and reconstructs the full midpoint pullback from the retained ``UU``
block plus only the new ``CU`` and ``CC`` blocks.

These routines are center linear algebra.  They deliberately make no outward
interval, action-domain, or Gate-7 claim.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AmbientCompletion:
    """Deterministic ambient completion and its explicit diagnostics."""

    retained_directions: np.ndarray
    complement_directions: np.ndarray
    full_basis: np.ndarray
    frame_qr_diagonal: np.ndarray
    coordinate_basis_residual: float
    normal_frame_residual: float
    full_basis_condition_2: float


@dataclass(frozen=True)
class MidpointCoordinates:
    """Coordinates of one ambient midpoint map in the completed basis."""

    retained: np.ndarray
    complement: np.ndarray
    reconstruction_residual_2: float
    relative_reconstruction_residual_2: float


def complete_ambient_basis(
    frame: np.ndarray,
    axis: np.ndarray,
    stored_transverse_basis: np.ndarray,
    *,
    coordinate_tolerance: float = 5.0e-13,
) -> AmbientCompletion:
    """Complete the exact stored tensor directions without rank truncation.

    ``frame`` has shape ``(m,n)``, ``axis`` has length ``n``, and the stored
    basis has shape ``(n,n-1)``.  The first complement direction is the
    action-frame image of the current-Green axis.  The remaining ``m-n``
    directions are the complete-QR normal columns of the same frame.

    The dimensions are fixed by the proof domain; no singular value threshold
    is used to discard a direction.  A zero QR pivot or a failed coordinate
    identity stops the construction.
    """

    frame = np.asarray(frame, dtype=float)
    axis = np.asarray(axis, dtype=float)
    basis = np.asarray(stored_transverse_basis, dtype=float)
    if frame.ndim != 2:
        raise ValueError("frame must be a matrix")
    ambient, coordinates = frame.shape
    if ambient < coordinates or axis.shape != (coordinates,):
        raise ValueError("frame and axis dimensions are incompatible")
    if basis.shape != (coordinates, coordinates - 1):
        raise ValueError("stored transverse basis has the wrong shape")
    if not (
        np.all(np.isfinite(frame))
        and np.all(np.isfinite(axis))
        and np.all(np.isfinite(basis))
    ):
        raise ValueError("basis inputs must be finite")

    coordinate_basis = np.column_stack((basis, axis))
    coordinate_gram = coordinate_basis.T @ coordinate_basis
    coordinate_residual = float(np.linalg.norm(
        coordinate_gram - np.eye(coordinates), ord=2,
    ))
    if coordinate_residual >= coordinate_tolerance:
        raise ValueError(
            "stored transverse basis and axis do not form the retained "
            f"coordinate basis: residual={coordinate_residual:.17g}"
        )

    q, r = np.linalg.qr(frame, mode="complete")
    diagonal = np.abs(np.diag(r[:coordinates, :coordinates]))
    if diagonal.shape != (coordinates,) or np.any(diagonal == 0.0):
        raise ValueError("midpoint action frame lost an expected QR pivot")
    normals = q[:, coordinates:]
    normal_residual = float(np.linalg.norm(frame.T @ normals, ord=2))

    retained = frame @ basis
    central = frame @ axis
    complement = np.column_stack((central, normals))
    full = np.column_stack((retained, complement))
    if full.shape != (ambient, ambient):
        raise ValueError("ambient completion did not produce a square basis")
    condition = float(np.linalg.cond(full, p=2))
    if not np.isfinite(condition):
        raise ValueError("completed midpoint basis is singular")
    return AmbientCompletion(
        retained_directions=retained,
        complement_directions=complement,
        full_basis=full,
        frame_qr_diagonal=diagonal,
        coordinate_basis_residual=coordinate_residual,
        normal_frame_residual=normal_residual,
        full_basis_condition_2=condition,
    )


def solve_midpoint_coordinates(
    completion: AmbientCompletion,
    ambient_map: np.ndarray,
) -> MidpointCoordinates:
    """Solve ``M = U A + C D`` and retain its reconstruction residual."""

    ambient_map = np.asarray(ambient_map, dtype=float)
    basis = np.asarray(completion.full_basis, dtype=float)
    if ambient_map.ndim != 2 or ambient_map.shape[0] != basis.shape[0]:
        raise ValueError("ambient midpoint map has an incompatible shape")
    if not np.all(np.isfinite(ambient_map)):
        raise ValueError("ambient midpoint map must be finite")
    coefficients = np.linalg.solve(basis, ambient_map)
    retained_dimension = completion.retained_directions.shape[1]
    reconstructed = basis @ coefficients
    residual = float(np.linalg.norm(reconstructed - ambient_map, ord=2))
    scale = max(float(np.linalg.norm(ambient_map, ord=2)), np.finfo(float).tiny)
    return MidpointCoordinates(
        retained=coefficients[:retained_dimension],
        complement=coefficients[retained_dimension:],
        reconstruction_residual_2=residual,
        relative_reconstruction_residual_2=residual / scale,
    )


def reconstruct_midpoint_hessian(
    retained_retained: np.ndarray,
    complement_retained: np.ndarray,
    complement_complement: np.ndarray,
    coordinates: MidpointCoordinates,
) -> np.ndarray:
    """Reconstruct ``H[M,M]`` from ``UU``, ``CU``, and ``CC`` blocks.

    The first array has shape ``(o,u,u)``, the second ``(o,c,u)``, and the
    third ``(o,c,c)``.  The returned tensor has shape ``(o,k,k)`` for a
    midpoint map with ``k`` endpoint-pair columns.  Both signed cross legs are
    included before any norm is taken.
    """

    q_uu = np.asarray(retained_retained, dtype=float)
    q_cu = np.asarray(complement_retained, dtype=float)
    q_cc = np.asarray(complement_complement, dtype=float)
    a = np.asarray(coordinates.retained, dtype=float)
    d = np.asarray(coordinates.complement, dtype=float)
    if q_uu.ndim != 3 or q_uu.shape[1] != q_uu.shape[2]:
        raise ValueError("retained Hessian block must be square per output")
    outputs, retained, _ = q_uu.shape
    complement = q_cc.shape[1] if q_cc.ndim == 3 else -1
    if (
        q_cu.shape != (outputs, complement, retained)
        or q_cc.shape != (outputs, complement, complement)
        or a.ndim != 2
        or d.ndim != 2
        or a.shape[0] != retained
        or d.shape[0] != complement
        or a.shape[1] != d.shape[1]
    ):
        raise ValueError("supplemental Hessian blocks have incompatible shapes")
    if not all(np.all(np.isfinite(value)) for value in (q_uu, q_cu, q_cc, a, d)):
        raise ValueError("supplemental Hessian inputs must be finite")

    uu = np.einsum("oui,uk,il->okl", q_uu, a, a, optimize=True)
    cu = np.einsum("ocu,ck,ul->okl", q_cu, d, a, optimize=True)
    uc = np.einsum("ocu,uk,cl->okl", q_cu, a, d, optimize=True)
    cc = np.einsum("ocd,ck,dl->okl", q_cc, d, d, optimize=True)
    result = uu + cu + uc + cc
    return 0.5 * (result + result.transpose(0, 2, 1))

