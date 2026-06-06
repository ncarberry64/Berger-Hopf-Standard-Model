"""Electroweak scale candidate and Hopf lift calculations."""

from __future__ import annotations

from math import exp, pi, sqrt

from constants import ALPHA_INV_LOW_ENERGY, PLANCK_ENERGY_GEV, V_HIGGS_EMPIRICAL_GEV
from screening import ScreenResult, relative_error


def epsilon_alpha(alpha_inv: float = ALPHA_INV_LOW_ENERGY) -> float:
    """Return epsilon_alpha = alpha^{-1}/(12 pi^2) - 1."""

    return alpha_inv / (12.0 * pi**2) - 1.0


def electroweak_scale_candidate(
    planck_energy_gev: float = PLANCK_ENERGY_GEV,
    alpha_inv: float = ALPHA_INV_LOW_ENERGY,
) -> float:
    """Return v = 2 sqrt(2) E_P exp[-4 pi^2 - epsilon_alpha/(4 pi^2)]."""

    eps = epsilon_alpha(alpha_inv)
    exponent = -4.0 * pi**2 - eps / (4.0 * pi**2)
    return 2.0 * sqrt(2.0) * planck_energy_gev * exp(exponent)


def hopf_lift_mass(v_gev: float) -> float:
    """Return M_lift = 4 pi^2 v in GeV."""

    return 4.0 * pi**2 * v_gev


def higgs_scale_screen() -> ScreenResult:
    """Return an auditable electroweak-scale record."""

    eps = epsilon_alpha()
    v = electroweak_scale_candidate()
    lift = hopf_lift_mass(v)
    outputs = {
        "epsilon_alpha": eps,
        "v_gev": v,
        "m_lift_gev": lift,
    }
    empirical = {"v_gev": V_HIGGS_EMPIRICAL_GEV}
    return ScreenResult(
        name="electroweak_scale_candidate",
        assumptions=(
            f"E_P = {PLANCK_ENERGY_GEV} GeV.",
            f"alpha^-1 = {ALPHA_INV_LOW_ENERGY}.",
            "Formula is treated as a numerical scale screen.",
        ),
        outputs=outputs,
        empirical=empirical,
        relative_error={"v_gev": relative_error(v, V_HIGGS_EMPIRICAL_GEV)},
        status="screened",
    )

