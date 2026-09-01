"""Exact kinematic projection to the N12 compactified physical chart.

The output ordering is the retained 74-component weight-seven quotient:
25 center coordinates, 25 velocity normals, and 24 multipliers.  The twelve
local time/lapse-chain coordinates are omitted exactly as in the bordered
descriptor.  ``log_epsilon`` is primary so the Gate-7 capture scale does not
underflow binary floating point.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0
from bhsm.interface.interval_weight_seven_graph_first_variation import (
    squared_product_weights,
)
from bhsm.interface.weight_seven_transverse_descriptor import (
    physical_coordinate_indices,
)


ORDER = 12
QDIM = 3 * ORDER + 1
MDIM = 2 * ORDER
STATE_DIMENSION = 2 * QDIM + MDIM
PHYSICAL = 2 * ORDER + 1
DESCRIPTOR = 2 * PHYSICAL + MDIM


@dataclass(frozen=True)
class RadiusDifferential:
    """First three derivatives of ``x=log R4`` at one state."""

    value: float
    gradient: np.ndarray
    hessian: np.ndarray
    boundary_shape: float

    def third(self, left: np.ndarray, right: np.ndarray, third: np.ndarray) -> float:
        """Contract the only nonzero third derivative with three directions."""

        h = _checked(left, QDIM, "left coordinate direction")
        k = _checked(right, QDIM, "right coordinate direction")
        ell = _checked(third, QDIM, "third coordinate direction")
        signs = (-1.0) ** np.arange(ORDER)
        section = slice(1 + 2 * ORDER, 1 + 3 * ORDER)
        tangent = math.tanh(2.0 * self.boundary_shape)
        sech_squared = 1.0 - tangent * tangent
        coefficient = 8.0 * sech_squared * tangent
        return float(
            coefficient
            * (signs @ h[section])
            * (signs @ k[section])
            * (signs @ ell[section])
        )


def _checked(value: np.ndarray, size: int, name: str) -> np.ndarray:
    vector = np.asarray(value, dtype=float)
    if vector.shape != (size,) or not np.all(np.isfinite(vector)):
        raise ValueError(f"finite {name} vector of length {size} required")
    return vector


def _split(state: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    y = _checked(state, STATE_DIMENSION, "N12 state")
    return y[:QDIM], y[QDIM : 2 * QDIM], y[2 * QDIM :]


def radius_differential(coordinates: np.ndarray) -> RadiusDifferential:
    """Return the exact value, gradient, and Hessian of ``log R4``."""

    q = _checked(coordinates, QDIM, "coordinate")
    signs_u = (-1.0) ** np.arange(1, ORDER + 1)
    signs_b = (-1.0) ** np.arange(ORDER)
    u_section = slice(1, 1 + ORDER)
    b_section = slice(1 + 2 * ORDER, 1 + 3 * ORDER)
    boundary_u = float(signs_u @ q[u_section])
    boundary_b = float(signs_b @ q[b_section])
    absolute = abs(2.0 * boundary_b)
    log_cosh = absolute + math.log1p(math.exp(-2.0 * absolute)) - math.log(2.0)
    tangent = math.tanh(2.0 * boundary_b)
    gradient = np.zeros(QDIM)
    gradient[0] = 1.0
    gradient[u_section] = signs_u
    gradient[b_section] = -tangent * signs_b
    hessian = np.zeros((QDIM, QDIM))
    hessian[b_section, b_section] = (
        -2.0 * (1.0 - tangent * tangent) * np.outer(signs_b, signs_b)
    )
    return RadiusDifferential(
        value=(
            math.log(RADIUS0 / 2.0)
            + float(q[0])
            + boundary_u
            - 0.5 * log_cosh
        ),
        gradient=gradient,
        hessian=hessian,
        boundary_shape=boundary_b,
    )


def compactified_terminal_chart(state: np.ndarray) -> dict[str, object]:
    """Project one regular N12 state to ``(log epsilon,a,eta,m)``.

    The common-scale center coordinate is recentered by the represented round
    expanding scale,

    ``q0_tilde=q0-log(2 R4/RADIUS0)``.

    Its velocity normal is the derivative of this same quantity in the
    retained coordinate time.  Proper-time positivity is monitored
    separately by the action domain and no lapse value is fitted here.
    """

    q, velocity, multipliers = _split(state)
    radius = radius_differential(q)
    physical = physical_coordinate_indices(ORDER)
    center = q[physical].copy()
    center[0] = q[0] - radius.value + math.log(RADIUS0 / 2.0)
    normal = velocity[physical].copy()
    normal[0] = velocity[0] - float(radius.gradient @ velocity)
    descriptor = np.concatenate((center, normal, multipliers))
    weights_squared = np.asarray(squared_product_weights(), dtype=float)
    if descriptor.shape != (DESCRIPTOR,) or weights_squared.shape != (DESCRIPTOR,):
        raise RuntimeError("inconsistent retained descriptor ordering")
    return {
        "log_R4": radius.value,
        "log_epsilon": -2.0 * radius.value,
        "epsilon_underflows_binary64": -2.0 * radius.value < math.log(np.finfo(float).tiny),
        "center_coordinates": center,
        "velocity_normals": normal,
        "multipliers": multipliers.copy(),
        "descriptor": descriptor,
        "product_norm": float(np.sqrt(weights_squared @ (descriptor * descriptor))),
        "physical_coordinate_indices": physical.copy(),
        "common_scale_recentered_not_quotiented": True,
    }


def compactified_terminal_chart_jets(
    state: np.ndarray,
    left_direction: np.ndarray,
    right_direction: np.ndarray,
    mixed_state_direction: np.ndarray | None = None,
) -> dict[str, object]:
    """Return first and mixed-second jets of the compactified chart.

    ``mixed_state_direction`` is the mixed second derivative of an upstream
    state family.  Setting it to zero returns the ordinary bilinear Hessian
    contraction.  Epsilon derivatives are normalized by epsilon, avoiding
    underflow at the certified capture scale.
    """

    y = _checked(state, STATE_DIMENSION, "N12 state")
    left = _checked(left_direction, STATE_DIMENSION, "left state direction")
    right = _checked(right_direction, STATE_DIMENSION, "right state direction")
    mixed = (
        np.zeros(STATE_DIMENSION)
        if mixed_state_direction is None
        else _checked(mixed_state_direction, STATE_DIMENSION, "mixed state direction")
    )
    q, velocity, _ = _split(y)
    hq, hv, hm = _split(left)
    kq, kv, km = _split(right)
    ellq, ellv, ellm = _split(mixed)
    radius = radius_differential(q)
    physical = physical_coordinate_indices(ORDER)

    dx_h = float(radius.gradient @ hq)
    dx_k = float(radius.gradient @ kq)
    d2x = float(hq @ radius.hessian @ kq + radius.gradient @ ellq)

    center_first_left = hq[physical].copy()
    center_first_right = kq[physical].copy()
    center_mixed = ellq[physical].copy()
    center_first_left[0] = hq[0] - dx_h
    center_first_right[0] = kq[0] - dx_k
    center_mixed[0] = ellq[0] - d2x

    normal_first_left = hv[physical].copy()
    normal_first_right = kv[physical].copy()
    normal_mixed = ellv[physical].copy()
    normal_first_left[0] = (
        hv[0] - float(hq @ radius.hessian @ velocity) - float(radius.gradient @ hv)
    )
    normal_first_right[0] = (
        kv[0] - float(kq @ radius.hessian @ velocity) - float(radius.gradient @ kv)
    )
    normal_mixed[0] = (
        ellv[0]
        - radius.third(hq, kq, velocity)
        - float(hq @ radius.hessian @ kv)
        - float(kq @ radius.hessian @ hv)
        - float(ellq @ radius.hessian @ velocity)
        - float(radius.gradient @ ellv)
    )

    descriptor_first_left = np.concatenate((center_first_left, normal_first_left, hm))
    descriptor_first_right = np.concatenate((center_first_right, normal_first_right, km))
    descriptor_mixed = np.concatenate((center_mixed, normal_mixed, ellm))
    return {
        "D_log_epsilon_left": -2.0 * dx_h,
        "D_log_epsilon_right": -2.0 * dx_k,
        "D2_log_epsilon_mixed": -2.0 * d2x,
        "D_epsilon_over_epsilon_left": -2.0 * dx_h,
        "D_epsilon_over_epsilon_right": -2.0 * dx_k,
        "D2_epsilon_over_epsilon_mixed": 4.0 * dx_h * dx_k - 2.0 * d2x,
        "D_descriptor_left": descriptor_first_left,
        "D_descriptor_right": descriptor_first_right,
        "D2_descriptor_mixed": descriptor_mixed,
        "mixed_state_direction_consumed": mixed_state_direction is not None,
    }


__all__ = [
    "DESCRIPTOR",
    "MDIM",
    "ORDER",
    "PHYSICAL",
    "QDIM",
    "STATE_DIMENSION",
    "compactified_terminal_chart",
    "compactified_terminal_chart_jets",
    "radius_differential",
]
