"""Same-action loop, counterterm, and Ward/Slavnov--Taylor assembly.

This module supplies the algebraic renormalization layer of the universal BHSM
physics engine.  It does not invent a regulator, a subtraction scale, or a
counterterm: callers must provide a complete action-owned diagram ledger and
an action-derived scheme.  Laurent poles are combined before the finite
vertex is exposed, so a diagram or seam contribution cannot be silently
zeroed or counted twice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


Array = np.ndarray


@dataclass(frozen=True)
class ActionOwnedRenormalizationScheme:
    scheme_id: str
    action_version: str
    background_id: str
    scale_value: float
    scale_dimension: str
    scale_provenance: tuple[str, ...]
    derived_from_action: bool
    fitted_to_observable: bool = False

    def __post_init__(self) -> None:
        if not self.scheme_id:
            raise ValueError("renormalization scheme needs an identifier")
        if not np.isfinite(self.scale_value) or self.scale_value <= 0.0:
            raise ValueError("renormalization scale must be finite and positive")
        if not self.derived_from_action:
            raise ValueError("BHSM renormalization scale must be action-derived")
        if self.fitted_to_observable:
            raise ValueError("observable-fitted renormalization scales are forbidden")
        if not self.scale_provenance:
            raise ValueError("action-derived scale provenance is required")


@dataclass(frozen=True)
class LaurentCoefficient:
    regulator_power: int
    value: Array

    def __post_init__(self) -> None:
        value = np.asarray(self.value, dtype=complex)
        if value.ndim != 1 or not np.all(np.isfinite(value)):
            raise ValueError("Laurent coefficient must be a finite vector")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True)
class RegulatedDiagram:
    diagram_id: str
    sector: str
    loop_order: int
    contribution_kind: str
    coefficients: tuple[LaurentCoefficient, ...]
    action_version: str
    background_id: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.loop_order < 0:
            raise ValueError("loop order must be nonnegative")
        if self.contribution_kind not in {
            "loop",
            "counterterm",
            "ghost",
            "jacobian",
            "contact",
        }:
            raise ValueError("unknown regulated contribution kind")
        if not self.coefficients:
            raise ValueError("regulated diagram has no Laurent coefficients")
        powers = [coefficient.regulator_power for coefficient in self.coefficients]
        if len(set(powers)) != len(powers):
            raise ValueError("a diagram may contain only one coefficient per power")
        shapes = {coefficient.value.shape for coefficient in self.coefficients}
        if len(shapes) != 1:
            raise ValueError("all Laurent coefficients must share one tensor shape")
        if not self.provenance:
            raise ValueError("diagram provenance is required")


@dataclass(frozen=True)
class LinearWardConstraint:
    constraint_id: str
    linear_map: Array
    expected: Array
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        linear_map = np.asarray(self.linear_map, dtype=complex)
        expected = np.asarray(self.expected, dtype=complex)
        if linear_map.ndim != 2 or expected.shape != (linear_map.shape[0],):
            raise ValueError("Ward constraint dimensions do not agree")
        if not np.all(np.isfinite(linear_map)) or not np.all(np.isfinite(expected)):
            raise ValueError("Ward constraint data must be finite")
        object.__setattr__(self, "linear_map", linear_map)
        object.__setattr__(self, "expected", expected)


@dataclass(frozen=True)
class RenormalizedVertex:
    finite_value: Array
    summed_laurent_coefficients: dict[int, Array]
    maximum_relative_pole_residual: float
    maximum_relative_ward_residual: float
    action_version: str
    background_id: str
    scheme_id: str
    diagram_ids: tuple[str, ...]
    sectors: tuple[str, ...]
    complete_diagram_ledger: bool
    complete_counterterm_ledger: bool
    gate7_closed: bool

    def require_physical_promotion(self, tolerance: float = 1.0e-10) -> None:
        missing: list[str] = []
        if not self.gate7_closed:
            missing.append("Gate7_closed_background")
        if not self.complete_diagram_ledger:
            missing.append("complete_action_owned_diagram_ledger")
        if not self.complete_counterterm_ledger:
            missing.append("complete_action_owned_counterterm_ledger")
        if self.maximum_relative_pole_residual > tolerance:
            missing.append("Laurent_pole_cancellation")
        if self.maximum_relative_ward_residual > tolerance:
            missing.append("Ward_Slavnov_Taylor_closure")
        if missing:
            raise RuntimeError("renormalized vertex promotion blocked by: " + ", ".join(missing))

    def metadata(self) -> dict:
        return {
            "action_version": self.action_version,
            "background_id": self.background_id,
            "renormalization_scheme_id": self.scheme_id,
            "diagram_ids": list(self.diagram_ids),
            "sectors": list(self.sectors),
            "complete_diagram_ledger": self.complete_diagram_ledger,
            "complete_counterterm_ledger": self.complete_counterterm_ledger,
            "external_observable_target_used": False,
            "internal_contributions_zeroed": False,
            "explicit_matrix_inverse_formed": False,
        }


def assemble_renormalized_vertex(
    diagrams: Iterable[RegulatedDiagram],
    scheme: ActionOwnedRenormalizationScheme,
    ward_constraints: Iterable[LinearWardConstraint],
    *,
    complete_diagram_ledger: bool,
    complete_counterterm_ledger: bool,
    gate7_closed: bool,
) -> RenormalizedVertex:
    """Sum a complete regulated ledger and evaluate its closure identities."""

    entries = tuple(diagrams)
    constraints = tuple(ward_constraints)
    if not entries:
        raise ValueError("at least one regulated diagram is required")
    if len({entry.diagram_id for entry in entries}) != len(entries):
        raise ValueError("duplicate diagram id would double-count a contribution")
    for entry in entries:
        if entry.action_version != scheme.action_version:
            raise ValueError("diagram and scheme action versions differ")
        if entry.background_id != scheme.background_id:
            raise ValueError("diagram and scheme backgrounds differ")

    shape = entries[0].coefficients[0].value.shape
    if any(coefficient.value.shape != shape for entry in entries for coefficient in entry.coefficients):
        raise ValueError("all regulated diagrams must share one tensor shape")

    summed: dict[int, Array] = {}
    absolute: dict[int, float] = {}
    for entry in entries:
        for coefficient in entry.coefficients:
            power = coefficient.regulator_power
            summed[power] = summed.get(power, np.zeros(shape, dtype=complex)) + coefficient.value
            absolute[power] = absolute.get(power, 0.0) + float(np.linalg.norm(coefficient.value))
    if 0 not in summed:
        summed[0] = np.zeros(shape, dtype=complex)
        absolute[0] = 0.0

    pole_residuals = [
        float(np.linalg.norm(value) / max(absolute[power], np.finfo(float).tiny))
        for power, value in summed.items()
        if power < 0
    ]
    maximum_pole = max(pole_residuals, default=0.0)

    finite = summed[0]
    ward_residuals: list[float] = []
    for constraint in constraints:
        if constraint.linear_map.shape[1] != finite.size:
            raise ValueError("Ward map and finite vertex dimensions differ")
        residual = constraint.linear_map @ finite - constraint.expected
        scale = max(
            float(np.linalg.norm(constraint.linear_map, ord=2) * np.linalg.norm(finite)),
            float(np.linalg.norm(constraint.expected)),
            np.finfo(float).tiny,
        )
        ward_residuals.append(float(np.linalg.norm(residual) / scale))

    return RenormalizedVertex(
        finite_value=finite,
        summed_laurent_coefficients=summed,
        maximum_relative_pole_residual=maximum_pole,
        maximum_relative_ward_residual=max(ward_residuals, default=float("inf")),
        action_version=scheme.action_version,
        background_id=scheme.background_id,
        scheme_id=scheme.scheme_id,
        diagram_ids=tuple(entry.diagram_id for entry in entries),
        sectors=tuple(sorted({entry.sector for entry in entries})),
        complete_diagram_ledger=bool(complete_diagram_ledger),
        complete_counterterm_ledger=bool(complete_counterterm_ledger),
        gate7_closed=bool(gate7_closed),
    )


__all__ = [
    "ActionOwnedRenormalizationScheme",
    "LaurentCoefficient",
    "LinearWardConstraint",
    "RegulatedDiagram",
    "RenormalizedVertex",
    "assemble_renormalized_vertex",
]
