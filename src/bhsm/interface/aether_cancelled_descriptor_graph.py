"""Coupled signed-descriptor graph for the cancelled C2 action field."""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (
    exact_cancelled_euler_dirac_field_action,
)


STATE_DIMENSION = 98


def exact_cancelled_descriptor_graph_field_action(
    *, state: np.ndarray, weights: np.ndarray, reference: np.ndarray,
    signed_descriptor: float,
) -> dict[str, Any]:
    """Return the extended field ``(G_theta, Delta)`` on ``s=lambda(Y)``.

    The defining incidence is exact:

    ``d/dtheta (s-lambda(Y)) = Delta-Dlambda[G_theta] = 0``.

    Thus the descriptor is a graph coordinate, not an independent source of
    interval uncertainty.  The binary64 eigenvalue remains diagnostic only.
    """

    field = exact_cancelled_euler_dirac_field_action(
        state=state,
        weights=weights,
        reference=reference,
        signed_descriptor=signed_descriptor,
    )
    delta = float(field["Delta"])
    extended = np.concatenate((
        np.asarray(field["cancelled_field_action"], dtype=float),
        np.asarray([delta]),
    ))
    return {
        **field,
        "extended_graph_field_action": extended,
        "signed_descriptor_rate": delta,
        "Dlambda_cancelled_field": delta,
        "descriptor_graph_defect_rate": 0.0,
        "descriptor_is_independent_interval_coordinate": False,
        "binary64_eigenvalue_used_as_descriptor": False,
    }


__all__ = ["exact_cancelled_descriptor_graph_field_action"]

