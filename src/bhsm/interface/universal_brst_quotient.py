"""Constraint/gauge quotient and Faddeev--Popov operator construction.

The quotient frame is the Euclidean orthogonal complement of the supplied
linearized constraints and infinitesimal gauge orbit.  The ghost operator is
the gauge-condition derivative along that orbit.  This is matrix algebra on
action-owned inputs; it neither invents a gauge condition nor assumes ghost
cancellation from a boolean flag.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import linalg


Array = np.ndarray


@dataclass(frozen=True)
class BRSTPhysicalQuotient:
    physical_frame: Array
    ghost_operator: Array
    quotient_constant: Array
    quotient_linear: Array
    gauge_null_relative_residual: float
    constraint_frame_relative_residual: float
    gauge_frame_relative_residual: float
    ghost_minimum_singular_value: float
    action_version: str
    background_id: str
    gauge_condition_id: str
    provenance: tuple[str, ...]

    @property
    def physical_dimension(self) -> int:
        return int(self.physical_frame.shape[1])

    def require_regular_brst_quotient(self, tolerance: float = 1.0e-10) -> None:
        missing: list[str] = []
        if self.constraint_frame_relative_residual > tolerance:
            missing.append("constraint_tangent_quotient")
        if self.gauge_frame_relative_residual > tolerance:
            missing.append("gauge_orbit_quotient")
        if self.gauge_null_relative_residual > tolerance:
            missing.append("quadratic_gauge_null_identity")
        if self.ghost_minimum_singular_value <= tolerance:
            missing.append("regular_Faddeev_Popov_operator")
        if missing:
            raise RuntimeError("BRST quotient blocked by: " + ", ".join(missing))

    def metadata(self) -> dict:
        return {
            "action_version": self.action_version,
            "background_id": self.background_id,
            "gauge_condition_id": self.gauge_condition_id,
            "ambient_dimension": self.physical_frame.shape[0],
            "physical_dimension": self.physical_dimension,
            "ghost_dimension": self.ghost_operator.shape[0],
            "explicit_kinetic_inverse_formed": False,
            "gauge_condition_selected_from_observable": False,
            "provenance": list(self.provenance),
        }


def build_brst_physical_quotient(
    constant_symbol: Array,
    linear_symbol: Array,
    tangent_constraints: Array,
    gauge_generators: Array,
    gauge_condition_derivative: Array,
    *,
    action_version: str,
    background_id: str,
    gauge_condition_id: str,
    provenance: tuple[str, ...],
    nullspace_tolerance: float | None = None,
) -> BRSTPhysicalQuotient:
    constant = np.asarray(constant_symbol, dtype=complex)
    linear = np.asarray(linear_symbol, dtype=complex)
    constraints = np.asarray(tangent_constraints, dtype=complex)
    generators = np.asarray(gauge_generators, dtype=complex)
    gauge_condition = np.asarray(gauge_condition_derivative, dtype=complex)
    if constant.ndim != 2 or constant.shape[0] != constant.shape[1]:
        raise ValueError("constant quadratic symbol must be square")
    ambient = constant.shape[0]
    if linear.shape != constant.shape:
        raise ValueError("quadratic symbols must have the same shape")
    if constraints.ndim != 2 or constraints.shape[1] != ambient:
        raise ValueError("constraint rows have the wrong ambient dimension")
    if generators.ndim != 2 or generators.shape[0] != ambient:
        raise ValueError("gauge-generator columns have the wrong ambient dimension")
    gauge_dimension = generators.shape[1]
    if gauge_condition.shape != (gauge_dimension, ambient):
        raise ValueError("gauge-condition derivative must map ambient states to gauge slots")
    if not provenance:
        raise ValueError("BRST quotient provenance is required")

    annihilator = np.vstack((constraints, generators.conj().T))
    frame = linalg.null_space(annihilator, rcond=nullspace_tolerance)
    ghost = gauge_condition @ generators
    quotient_constant = frame.conj().T @ constant @ frame
    quotient_linear = frame.conj().T @ linear @ frame

    tiny = np.finfo(float).tiny
    constraint_residual = float(
        np.linalg.norm(constraints @ frame)
        / max(np.linalg.norm(constraints, ord=2) * np.linalg.norm(frame, ord=2), tiny)
    ) if constraints.shape[0] else 0.0
    gauge_frame_residual = float(
        np.linalg.norm(generators.conj().T @ frame)
        / max(np.linalg.norm(generators, ord=2) * np.linalg.norm(frame, ord=2), tiny)
    ) if gauge_dimension else 0.0
    gauge_null_numerator = np.hypot(
        np.linalg.norm(constant @ generators),
        np.linalg.norm(linear @ generators),
    )
    gauge_null_denominator = max(
        np.hypot(np.linalg.norm(constant, ord=2), np.linalg.norm(linear, ord=2))
        * np.linalg.norm(generators, ord=2),
        tiny,
    )
    ghost_singular = linalg.svdvals(ghost)
    minimum_ghost = float(np.min(ghost_singular, initial=np.inf))
    return BRSTPhysicalQuotient(
        physical_frame=frame,
        ghost_operator=ghost,
        quotient_constant=quotient_constant,
        quotient_linear=quotient_linear,
        gauge_null_relative_residual=float(gauge_null_numerator / gauge_null_denominator),
        constraint_frame_relative_residual=constraint_residual,
        gauge_frame_relative_residual=gauge_frame_residual,
        ghost_minimum_singular_value=minimum_ghost,
        action_version=action_version,
        background_id=background_id,
        gauge_condition_id=gauge_condition_id,
        provenance=provenance,
    )


__all__ = ["BRSTPhysicalQuotient", "build_brst_physical_quotient"]
