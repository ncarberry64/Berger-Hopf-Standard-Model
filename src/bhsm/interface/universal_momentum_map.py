"""Action-owned local momentum and Mandelstam invariant map.

The inverse metric/tetrad data must come from the frozen BHSM background.
This module performs only covector contractions and channel bookkeeping; it
does not assume a flat metric or import a collider energy as theory input.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


Array = np.ndarray


@dataclass(frozen=True)
class ActionMomentumMap:
    inverse_metric: Array
    action_version: str
    background_id: str
    chart_id: str
    provenance: tuple[str, ...]
    derived_from_frozen_background: bool

    def __post_init__(self) -> None:
        metric = np.asarray(self.inverse_metric, dtype=float)
        if metric.ndim != 2 or metric.shape[0] != metric.shape[1]:
            raise ValueError("inverse metric must be square")
        if not np.all(np.isfinite(metric)) or not np.allclose(metric, metric.T):
            raise ValueError("inverse metric must be finite and symmetric")
        if abs(np.linalg.det(metric)) <= np.finfo(float).tiny:
            raise ValueError("inverse metric must be nondegenerate")
        if not self.provenance:
            raise ValueError("momentum-map provenance is required")
        object.__setattr__(self, "inverse_metric", metric)

    @property
    def dimension(self) -> int:
        return int(self.inverse_metric.shape[0])

    def require_physical_map(self) -> None:
        if not self.derived_from_frozen_background:
            raise RuntimeError("momentum map is not attached to the frozen BHSM background")

    def invariant(self, covector: Array) -> float:
        momentum = np.asarray(covector, dtype=float)
        if momentum.shape != (self.dimension,):
            raise ValueError("momentum covector has the wrong dimension")
        return float(momentum @ self.inverse_metric @ momentum)


@dataclass(frozen=True)
class MandelstamInvariants:
    s: float
    t: float
    u: float
    momentum_conservation_residual: float
    on_shell_sum_rule_residual: float | None


def mandelstam_invariants(
    momentum_map: ActionMomentumMap,
    incoming: tuple[Array, Array],
    outgoing: tuple[Array, Array],
    *,
    mass_squared: tuple[float, float, float, float] | None = None,
) -> MandelstamInvariants:
    momentum_map.require_physical_map()
    p1, p2 = (np.asarray(value, dtype=float) for value in incoming)
    p3, p4 = (np.asarray(value, dtype=float) for value in outgoing)
    if any(value.shape != (momentum_map.dimension,) for value in (p1, p2, p3, p4)):
        raise ValueError("all external momenta must use the momentum-map chart")
    conservation = float(np.linalg.norm(p1 + p2 - p3 - p4))
    s = momentum_map.invariant(p1 + p2)
    t = momentum_map.invariant(p1 - p3)
    u = momentum_map.invariant(p1 - p4)
    sum_rule = None
    if mass_squared is not None:
        if any(not np.isfinite(value) or value < 0.0 for value in mass_squared):
            raise ValueError("external mass squares must be finite and nonnegative")
        sum_rule = float(abs(s + t + u - sum(mass_squared)))
    return MandelstamInvariants(s, t, u, conservation, sum_rule)


__all__ = ["ActionMomentumMap", "MandelstamInvariants", "mandelstam_invariants"]
