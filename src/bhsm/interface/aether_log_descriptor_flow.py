"""Log-descriptor reparameterization of the exact N12 C2 action flow."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (
    exact_fixed_s_field_action,
)
from bhsm.interface.aether_forward_c2_geometry_incidence import (
    boundary_geometry_action_covectors,
)


STATE_DIMENSION = 98


def exact_log_descriptor_field_action(
    *,
    state: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
    log_descriptor: float,
) -> dict[str, Any]:
    """Return ``dY/dr=s F_s`` for ``r=log(s)`` on the regular chart."""

    r = float(log_descriptor)
    if not math.isfinite(r):
        raise ValueError("finite log descriptor required")
    descriptor = math.exp(r)
    if descriptor <= 0.0 or not math.isfinite(descriptor):
        raise ValueError("representable positive descriptor required")
    fixed = exact_fixed_s_field_action(
        state=state,
        weights=weights,
        reference=reference,
        signed_descriptor=descriptor,
    )
    geometry = boundary_geometry_action_covectors(state=state, weights=weights)
    lapse = math.exp(float(geometry["log_lapse"]))
    delta = float(fixed["Delta"])
    field = descriptor * np.asarray(fixed["field_action"], dtype=float)
    proper_density = lapse * descriptor * descriptor / delta
    return {
        **fixed,
        "signed_descriptor": descriptor,
        "log_descriptor": r,
        "log_descriptor_field_action": field,
        "Dlambda_log_descriptor_field": descriptor * float(fixed["Dlambda_field"]),
        "boundary_lapse": lapse,
        "proper_time_density_d_tau_d_log_s": proper_density,
        "orientation_preserving": proper_density > 0.0,
        "same_action_trajectory": True,
    }


__all__ = ["STATE_DIMENSION", "exact_log_descriptor_field_action"]
