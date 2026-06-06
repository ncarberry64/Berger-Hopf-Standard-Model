"""Electroweak-scale gauge coupling matching screens."""

from __future__ import annotations

from math import pi

from constants import (
    ALPHA3_MZ_EMPIRICAL,
    ALPHA_EM_INV_EW_EMPIRICAL,
    SIN2_THETA_W_EMPIRICAL,
)
from screening import ScreenResult, relative_error


def coupling_screens() -> dict[str, float]:
    """Return the supplied coupling-screen values."""

    alpha_1 = 1.0 / (6.0 * pi**2)
    alpha_2 = 2.0 / (6.0 * pi**2)
    alpha_3 = 7.0 / (6.0 * pi**2)
    return {
        "alpha_1": alpha_1,
        "alpha_2": alpha_2,
        "alpha_3": alpha_3,
        "sin2_theta_w": 3.0 / 13.0,
        "alpha_em_inv_mew": 13.0 * pi**2,
    }


def gauge_coupling_screen() -> ScreenResult:
    """Return an auditable coupling matching record."""

    outputs = coupling_screens()
    empirical = {
        "alpha_3": ALPHA3_MZ_EMPIRICAL,
        "sin2_theta_w": SIN2_THETA_W_EMPIRICAL,
        "alpha_em_inv_mew": ALPHA_EM_INV_EW_EMPIRICAL,
    }
    errors = {
        key: relative_error(outputs[key], reference)
        for key, reference in empirical.items()
    }
    return ScreenResult(
        name="gauge_coupling_matching_screen",
        assumptions=(
            "Coupling relations are interpreted as electroweak-scale matching screens.",
            "alpha_3 uses the supplied approximate factor 7/(6 pi^2).",
        ),
        outputs=outputs,
        empirical=empirical,
        relative_error=errors,
        status="screened",
    )

