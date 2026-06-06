"""PMNS helpers for effective neutrino-sector extensions."""

from __future__ import annotations

import numpy as np

from ckm import is_unitary
from constants import ALPHA_INV_LOW_ENERGY


def pmns_from_left_bases(charged_lepton_left: np.ndarray, neutrino_left: np.ndarray) -> np.ndarray:
    """Return U_PMNS = U_eL^dagger U_nuL for an effective neutrino extension."""

    return np.asarray(charged_lepton_left).conj().T @ np.asarray(neutrino_left)


def pmns_is_unitary(matrix: np.ndarray, atol: float = 1e-10) -> bool:
    """Return True if an effective PMNS matrix is unitary to tolerance."""

    return is_unitary(matrix, atol=atol)


def pmns_effective_angles(alpha: float | None = None) -> dict[str, float]:
    """Return supplied PMNS effective-extension screen outputs.

    This is not a minimal-SM prediction. The implemented rules are:
    - sin^2(theta_13) = 3 alpha
    - sin^2(theta_12) = 1/3 - 3 alpha
    - sin^2(theta_23) = 1/2 + 6 alpha
    - Delta m^2_21 / Delta m^2_31 = 4 alpha
    """

    resolved_alpha = 1.0 / ALPHA_INV_LOW_ENERGY if alpha is None else float(alpha)
    if resolved_alpha <= 0:
        raise ValueError("alpha must be positive")
    return {
        "sin2_theta_13": 3.0 * resolved_alpha,
        "sin2_theta_12": (1.0 / 3.0) - 3.0 * resolved_alpha,
        "sin2_theta_23": 0.5 + 6.0 * resolved_alpha,
        "delta_m2_21_over_delta_m2_31": 4.0 * resolved_alpha,
    }


def pmns_effective_screen(alpha: float | None = None) -> dict[str, object]:
    """Return PMNS effective-extension screen record."""

    return {
        "angles": pmns_effective_angles(alpha),
        "status": "EFFECTIVE_EXTENSION_SCREEN",
        "alpha": 1.0 / ALPHA_INV_LOW_ENERGY if alpha is None else float(alpha),
        "limitation": (
            "PMNS rows use an effective neutrino-sector extension; neutrino "
            "masses are not part of the minimal Standard Model ledger."
        ),
    }
