"""Curvature/topographic screening scaffold for BHSM scalar modes."""

from __future__ import annotations

from dataclasses import dataclass


CURVATURE_SCREENING_DERIVED = "CURVATURE_SCREENING_DERIVED"


@dataclass(frozen=True)
class CurvatureScreeningCondition:
    """One sufficient curvature/topographic screening condition."""

    id: str
    coupling_operator: str
    curvature_source: str
    flat_limit_suppresses: bool
    observable_fifth_force_survives: bool
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def curvature_screening_conditions() -> tuple[CurvatureScreeningCondition, ...]:
    """Return action-level curvature/topographic screening conditions."""

    return (
        CurvatureScreeningCondition(
            id="CS1",
            coupling_operator="L_int ~ phi R_topo",
            curvature_source="R_topo = K[rho_Phi] or equivalent topographic curvature scalar",
            flat_limit_suppresses=True,
            observable_fifth_force_survives=False,
            status=CURVATURE_SCREENING_DERIVED,
            assumptions=(
                "The mode couples to topographic curvature/gradient sources rather than direct matter density.",
                "The local flat/low-curvature limit is the relevant fifth-force comparison limit.",
            ),
            limitations=(
                "The full action must prove that direct matter density couplings are absent.",
                "Curvature positivity/profile assumptions remain tied to the broader H_T/scalar scaffold.",
            ),
        ),
        CurvatureScreeningCondition(
            id="CS2",
            coupling_operator="local flat limit: R_topo -> 0",
            curvature_source="topographic gradients vanish in the local flat comparison patch",
            flat_limit_suppresses=True,
            observable_fifth_force_survives=False,
            status=CURVATURE_SCREENING_DERIVED,
            assumptions=(
                "No boundary defect produces a nonzero local topographic source.",
            ),
            limitations=(
                "This is a sufficient screening criterion, not a proof of global scalar decoupling.",
            ),
        ),
    )


def curvature_screening_factor(curvature: float, reference_scale: float) -> float:
    """Return a bounded curvature-screening proxy in [0, 1)."""

    if curvature < 0.0:
        raise ValueError("curvature must be nonnegative")
    if reference_scale <= 0.0:
        raise ValueError("reference_scale must be positive")
    return float(curvature / (curvature + reference_scale))

