"""Hypercharge derivation under the admitted Standard Model chiral pattern."""

from __future__ import annotations

from fractions import Fraction

from constants import HIGGS_HYPERCHARGE
from screening import ScreenResult


def derive_hypercharges(higgs_y: Fraction = HIGGS_HYPERCHARGE) -> dict[str, Fraction]:
    """Derive one-generation left-Weyl hypercharges.

    Inputs admitted by the framework:
    - Standard Model chiral representation pattern.
    - Higgs-selected U(1) with hypercharge ``higgs_y``.
    - Yukawa invariance.
    - SU(2)^2 U(1) and mixed gravitational anomaly cancellation.

    Field names use left-handed Weyl notation: ``u_c``, ``d_c``, and ``e_c``
    are charge-conjugate singlets.
    """

    y_q = higgs_y / 3
    y_l = -3 * y_q
    y_u_c = -y_q - higgs_y
    y_d_c = -y_q + higgs_y
    y_e_c = higgs_y - y_l
    return {
        "Q": y_q,
        "u_c": y_u_c,
        "d_c": y_d_c,
        "L": y_l,
        "e_c": y_e_c,
        "H": higgs_y,
    }


def hypercharge_screen(higgs_y: Fraction = HIGGS_HYPERCHARGE) -> ScreenResult:
    """Return an auditable hypercharge derivation record."""

    charges = derive_hypercharges(higgs_y)
    return ScreenResult(
        name="hypercharge_derivation",
        assumptions=(
            "SM chiral representation pattern is admitted.",
            "Higgs-selected U(1) has Y_H = 1/2 by normalization.",
            "Yukawa terms QHu_c, QH*d_c, LH*e_c are U(1)-invariant.",
            "SU(2)^2 U(1) and mixed gravitational anomalies vanish.",
        ),
        outputs={name: str(value) for name, value in charges.items()},
        empirical={},
        relative_error={},
        status="conditional",
    )


def yukawa_invariance_residuals(charges: dict[str, Fraction]) -> dict[str, Fraction]:
    """Residuals for the three one-generation charged Yukawa invariants."""

    return {
        "up": charges["Q"] + charges["H"] + charges["u_c"],
        "down": charges["Q"] - charges["H"] + charges["d_c"],
        "charged_lepton": charges["L"] - charges["H"] + charges["e_c"],
    }

