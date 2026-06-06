"""Shared result type for numerical and algebraic screens."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


VALID_STATUSES = {"derived", "conditional", "screened", "open"}


@dataclass(frozen=True)
class ScreenResult:
    """Auditable record for a computation in the framework."""

    name: str
    assumptions: tuple[str, ...]
    outputs: Mapping[str, Any]
    empirical: Mapping[str, Any]
    relative_error: Mapping[str, float | None]
    status: str

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(f"invalid screen status: {self.status!r}")


def relative_error(value: float, reference: float) -> float:
    """Return absolute relative error against a nonzero reference."""

    if reference == 0:
        raise ValueError("reference value must be nonzero")
    return abs((value - reference) / reference)

