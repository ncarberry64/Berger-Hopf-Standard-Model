"""Covariant assembly of the two-sided AE2 Calderon seam response."""

from __future__ import annotations

import numpy as np


def _square(value: np.ndarray, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if (
        matrix.ndim != 2
        or matrix.shape[0] != matrix.shape[1]
        or not np.all(np.isfinite(matrix))
    ):
        raise ValueError(f"{name} must be a finite square matrix")
    return matrix


def _unitary(value: np.ndarray, tolerance: float = 1.0e-11) -> np.ndarray:
    matrix = _square(value, "reset lift")
    if np.linalg.norm(matrix.conj().T @ matrix - np.eye(matrix.shape[0]), ord=2) > tolerance:
        raise ValueError("reset lift must be unitary")
    return matrix


def covariant_effective_event_load(
    child_calderon: np.ndarray,
    wentzell: np.ndarray,
    reset_lift: np.ndarray,
) -> np.ndarray:
    """Return ``U_R^* M_child U_R + W_phys`` in the event frame."""

    child = _square(child_calderon, "child Calderon response")
    boundary = _square(wentzell, "Wentzell response")
    lift = _unitary(reset_lift)
    if child.shape != boundary.shape or child.shape != lift.shape:
        raise ValueError("seam matrices must have one square shape")
    return lift.conj().T @ child @ lift + boundary


def covariant_effective_event_load_jet(
    child_covariant_jet: np.ndarray,
    wentzell_covariant_jet: np.ndarray,
    reset_lift: np.ndarray,
) -> np.ndarray:
    """Return the covariant jet of the effective event load.

    The AE2 reset lift is a transition map of one global bundle.  With the
    compatible parameter-space connection ``nabla U_R=0``.  Ordinary frame
    derivatives of ``U_R`` are therefore absorbed into the covariant child
    response jet rather than treated as an independent physical source.
    """

    child = _square(child_covariant_jet, "child covariant jet")
    boundary = _square(wentzell_covariant_jet, "Wentzell covariant jet")
    lift = _unitary(reset_lift)
    if child.shape != boundary.shape or child.shape != lift.shape:
        raise ValueError("seam jet matrices must have one square shape")
    return lift.conj().T @ child @ lift + boundary


def covariant_seam_response(
    event_calderon: np.ndarray,
    child_calderon: np.ndarray,
    wentzell: np.ndarray,
    reset_lift: np.ndarray,
) -> np.ndarray:
    """Return ``M_event + U_R^* M_child U_R + W_phys``."""

    event = _square(event_calderon, "event Calderon response")
    load = covariant_effective_event_load(child_calderon, wentzell, reset_lift)
    if event.shape != load.shape:
        raise ValueError("event response must match the effective load")
    return event + load


def transition_covariant_derivative(
    reset_lift: np.ndarray,
    ordinary_derivative: np.ndarray,
    event_connection: np.ndarray,
    child_connection: np.ndarray,
) -> np.ndarray:
    """Return ``dU+A_child U-U A_event`` for a bundle transition map."""

    lift = _unitary(reset_lift)
    derivative = _square(ordinary_derivative, "ordinary reset-lift derivative")
    event = _square(event_connection, "event connection")
    child = _square(child_connection, "child connection")
    if not (lift.shape == derivative.shape == event.shape == child.shape):
        raise ValueError("transition data must have one square shape")
    return derivative + child @ lift - lift @ event


__all__ = [
    "covariant_effective_event_load",
    "covariant_effective_event_load_jet",
    "covariant_seam_response",
    "transition_covariant_derivative",
]
