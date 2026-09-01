"""Joint same-action renormalization-group transport.

All running parameters travel in one vector under one beta-function oracle.
This prevents a gauge, Yukawa, or HS sector from receiving an independent
finite shift.  Preserved action identities may be supplied as residual
functions and are checked along the entire integrated trajectory.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np
from scipy import integrate


Array = np.ndarray


@dataclass(frozen=True)
class ActionBetaFunction:
    parameter_ids: tuple[str, ...]
    evaluate: Callable[[float, Array], Array]
    action_version: str
    scheme_id: str
    provenance: tuple[str, ...]
    derived_from_same_action_ledger: bool
    fitted_to_observable: bool = False

    def __post_init__(self) -> None:
        if not self.parameter_ids or len(set(self.parameter_ids)) != len(self.parameter_ids):
            raise ValueError("RG parameter ids must be nonempty and unique")
        if not self.derived_from_same_action_ledger:
            raise ValueError("beta function must come from the same-action loop ledger")
        if self.fitted_to_observable:
            raise ValueError("observable-fitted beta functions are forbidden")
        if not self.scheme_id or not self.provenance:
            raise ValueError("RG scheme and provenance are required")


@dataclass(frozen=True)
class RGInvariant:
    invariant_id: str
    residual: Callable[[Array], Array]
    provenance: tuple[str, ...]


@dataclass(frozen=True)
class RGTrajectory:
    log_scale: Array
    values: Array
    parameter_ids: tuple[str, ...]
    maximum_invariant_residual: float
    action_version: str
    scheme_id: str
    successful: bool

    def endpoint(self) -> dict[str, float]:
        return {
            name: float(self.values[index, -1])
            for index, name in enumerate(self.parameter_ids)
        }

    def require_promotable(self, tolerance: float = 1.0e-9) -> None:
        if not self.successful:
            raise RuntimeError("RG integration did not complete")
        if self.maximum_invariant_residual > tolerance:
            raise RuntimeError("RG flow violates an action-owned Ward/invariant identity")


def integrate_joint_rg_flow(
    beta: ActionBetaFunction,
    initial_values: Array,
    initial_scale: float,
    final_scale: float,
    invariants: Iterable[RGInvariant] = (),
    *,
    sample_count: int = 65,
    relative_tolerance: float = 1.0e-10,
    absolute_tolerance: float = 1.0e-12,
) -> RGTrajectory:
    initial = np.asarray(initial_values, dtype=float)
    if initial.shape != (len(beta.parameter_ids),) or not np.all(np.isfinite(initial)):
        raise ValueError("initial RG vector has the wrong shape or nonfinite values")
    if min(initial_scale, final_scale) <= 0.0 or not np.isfinite(initial_scale + final_scale):
        raise ValueError("RG scales must be finite and positive")
    if sample_count < 2:
        raise ValueError("RG trajectory needs at least two samples")
    t0, t1 = np.log(initial_scale), np.log(final_scale)
    samples = np.linspace(t0, t1, sample_count)

    def rhs(log_scale: float, values: Array) -> Array:
        result = np.asarray(beta.evaluate(float(log_scale), np.asarray(values)), dtype=float)
        if result.shape != initial.shape or not np.all(np.isfinite(result)):
            raise ArithmeticError("beta function returned invalid data")
        return result

    solution = integrate.solve_ivp(
        rhs,
        (t0, t1),
        initial,
        t_eval=samples,
        rtol=relative_tolerance,
        atol=absolute_tolerance,
        method="DOP853",
    )
    invariant_rows = tuple(invariants)
    maximum_residual = 0.0
    for invariant in invariant_rows:
        for column in solution.y.T:
            residual = np.asarray(invariant.residual(column), dtype=float)
            if not np.all(np.isfinite(residual)):
                maximum_residual = float("inf")
                break
            maximum_residual = max(maximum_residual, float(np.linalg.norm(residual)))
    return RGTrajectory(
        log_scale=solution.t,
        values=solution.y,
        parameter_ids=beta.parameter_ids,
        maximum_invariant_residual=maximum_residual,
        action_version=beta.action_version,
        scheme_id=beta.scheme_id,
        successful=bool(solution.success),
    )


__all__ = [
    "ActionBetaFunction",
    "RGInvariant",
    "RGTrajectory",
    "integrate_joint_rg_flow",
]
