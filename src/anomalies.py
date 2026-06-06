"""Gauge and mixed anomaly audits for one Standard Model generation."""

from __future__ import annotations

from fractions import Fraction

from hypercharge import derive_hypercharges
from screening import ScreenResult


def anomaly_residuals(charges: dict[str, Fraction] | None = None) -> dict[str, Fraction]:
    """Return anomaly residuals in left-Weyl hypercharge convention."""

    y = charges or derive_hypercharges()
    q, u, d, l, e = y["Q"], y["u_c"], y["d_c"], y["L"], y["e_c"]
    return {
        "SU3_SU3_U1": 2 * q + u + d,
        "SU2_SU2_U1": 3 * q + l,
        "gravity_gravity_U1": 6 * q + 3 * u + 3 * d + 2 * l + e,
        "U1_U1_U1": 6 * q**3 + 3 * u**3 + 3 * d**3 + 2 * l**3 + e**3,
    }


def anomalies_cancel(charges: dict[str, Fraction] | None = None) -> bool:
    """Return True when all implemented anomaly residuals vanish exactly."""

    return all(value == 0 for value in anomaly_residuals(charges).values())


def anomaly_screen(charges: dict[str, Fraction] | None = None) -> ScreenResult:
    """Return an auditable anomaly-cancellation record."""

    residuals = anomaly_residuals(charges)
    return ScreenResult(
        name="one_generation_anomaly_cancellation",
        assumptions=(
            "One SM generation in left-Weyl notation.",
            "Color and weak multiplicities are included.",
            "No right-handed neutrino is included in the minimal ledger.",
        ),
        outputs={name: str(value) for name, value in residuals.items()},
        empirical={},
        relative_error={},
        status="derived",
    )

