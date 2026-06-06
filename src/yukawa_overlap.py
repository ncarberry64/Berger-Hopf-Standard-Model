"""Yukawa hierarchy screens from the universal overlap rule."""

from __future__ import annotations

from math import exp

from berger_spectrum import berger_lambda, ledger_modes
from constants import BERGER_A_DEFAULT, EMPIRICAL_MASS_RATIOS, S_OVERLAP
from screening import ScreenResult, relative_error


def mass_ratio(k: int, j: int, a: float = BERGER_A_DEFAULT, s: float = S_OVERLAP) -> float:
    """Return m_i / m_3 = exp[-S lambda_{k,j}]."""

    return exp(-s * berger_lambda(k, j, a=a))


def hierarchy_screen(
    a: float = BERGER_A_DEFAULT,
    empirical: dict[str, dict[str, float]] | None = None,
) -> ScreenResult:
    """Evaluate supplied mode-ledger mass-ratio screens."""

    empirical_values = empirical or EMPIRICAL_MASS_RATIOS
    outputs: dict[str, float] = {}
    references: dict[str, float] = {}
    errors: dict[str, float | None] = {}
    for sector, ranks in ledger_modes().items():
        for rank, mode in ranks.items():
            key = f"{sector}.{rank}"
            outputs[key] = mass_ratio(mode.k, mode.j, a=a)
            if rank in empirical_values.get(sector, {}):
                references[key] = empirical_values[sector][rank]
                errors[key] = relative_error(outputs[key], references[key])
            else:
                errors[key] = None

    return ScreenResult(
        name="berger_yukawa_hierarchy_screen",
        assumptions=(
            f"Berger squash parameter a = {a}.",
            f"Universal overlap S = {S_OVERLAP}.",
            "Mode ledger is supplied rather than independently derived.",
            "Heavy generation in each charged sector is assigned to (0,0).",
        ),
        outputs=outputs,
        empirical=references,
        relative_error=errors,
        status="screened",
    )

