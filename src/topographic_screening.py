"""Topographic screening conditions for scalar decoupling scaffolds."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ScreeningCondition:
    """One sufficient screening condition for a scalar/topographic mode."""

    id: str
    name: str
    statement: str
    suppresses_direct_on_shell_scalar: bool
    status: str
    limitations: tuple[str, ...]


def derivative_coupling_suppression(momentum: float, scale: float) -> float:
    """Return a simple derivative-coupling suppression proxy."""

    if momentum < 0 or scale <= 0:
        raise ValueError("momentum must be nonnegative and scale positive")
    return float((momentum / scale) ** 2)


def curvature_filter_strength(curvature: float, cutoff: float) -> float:
    """Return a bounded curvature-filter proxy in [0,1)."""

    if curvature < 0 or cutoff <= 0:
        raise ValueError("curvature must be nonnegative and cutoff positive")
    return float(curvature / (curvature + cutoff))


def topographic_screening_conditions() -> tuple[ScreeningCondition, ...]:
    """Return sufficient topographic screening conditions."""

    return (
        ScreeningCondition(
            id="S1",
            name="mass_gap_condition",
            statement="Orthogonal scalar/topographic modes above 4*pi^2*v are heavy lifted states.",
            suppresses_direct_on_shell_scalar=True,
            status="SUFFICIENT_CONDITION_SCAFFOLD",
            limitations=("Requires full scalar spectrum to prove globally.",),
        ),
        ScreeningCondition(
            id="S2",
            name="derivative_filter",
            statement="Derivative-coupled light modes are conditionally screened at low momentum.",
            suppresses_direct_on_shell_scalar=True,
            status="CONDITIONAL_SCREENING_SCAFFOLD",
            limitations=("Requires action-level derivative coupling derivation.",),
        ),
        ScreeningCondition(
            id="S3",
            name="curvature_filter",
            statement="Curvature-filtered modes couple only through filtered topographic channels.",
            suppresses_direct_on_shell_scalar=True,
            status="CONDITIONAL_SCREENING_SCAFFOLD",
            limitations=("Requires curvature/profile operator proof.",),
        ),
        ScreeningCondition(
            id="S4",
            name="screened_topographic_channel",
            statement="Screened topographic modes are not new on-shell light particles in the scaffold ontology.",
            suppresses_direct_on_shell_scalar=True,
            status="CONDITIONAL_SCREENING_SCAFFOLD",
            limitations=("Screening is scaffold-audited, not fully action-proven.",),
        ),
    )


def topographic_screening_report() -> dict[str, Any]:
    """Return JSON-ready screening report."""

    return {
        "conditions": [asdict(row) for row in topographic_screening_conditions()],
        "example_derivative_suppression": derivative_coupling_suppression(1.0, 1000.0),
        "example_curvature_filter": curvature_filter_strength(1.0, 1000.0),
        "theorem_complete": False,
        "limitations": (
            "Screening conditions are sufficient scaffolds.",
            "A direct unscreened light scalar remains forbidden/open risk.",
        ),
    }
