"""CKM mixing helpers for left-handed internal-basis misalignment."""

from __future__ import annotations

from math import cos, sin, sqrt
from typing import Mapping

import numpy as np


def ckm_from_left_bases(up_left: np.ndarray, down_left: np.ndarray) -> np.ndarray:
    """Return V_CKM = U_uL^dagger U_dL."""

    return np.asarray(up_left).conj().T @ np.asarray(down_left)


def is_unitary(matrix: np.ndarray, atol: float = 1e-10) -> bool:
    """Return True if matrix is unitary to tolerance."""

    m = np.asarray(matrix)
    return bool(np.allclose(m.conj().T @ m, np.eye(m.shape[0]), atol=atol))


def ckm_angles_from_bhsm_ratios(
    ratios: Mapping[str, Mapping[str, float]],
) -> dict[str, float]:
    """Return BHSM CKM screen angles from internal overlap mass ratios.

    Implemented supplied screen rules:
    - sin(theta_12) ~= sqrt(d/s)
    - sin(theta_23) ~= 2(s/b)
    - sin(theta_13) ~= sqrt(u/t)
    """

    down = ratios["down_quarks"]
    up = ratios["up_quarks"]
    s_over_b = float(down["middle"])
    d_over_b = float(down["light"])
    u_over_t = float(up["light"])
    if s_over_b <= 0 or d_over_b < 0 or u_over_t < 0:
        raise ValueError("mass ratios must be nonnegative and s/b must be positive")
    return {
        "sin_theta_12": sqrt(d_over_b / s_over_b),
        "sin_theta_23": 2.0 * s_over_b,
        "sin_theta_13": sqrt(u_over_t),
    }


def ckm_matrix_magnitudes(
    theta12: float,
    theta23: float,
    theta13: float,
    delta: float | None = None,
) -> np.ndarray:
    """Return CKM matrix magnitudes from three screen angles.

    ``delta`` is optional. If absent, the current implementation uses a real
    CP-conserving placeholder for matrix magnitudes and does not claim a CP
    phase prediction.
    """

    for value in (theta12, theta23, theta13):
        if value < 0 or value >= 1:
            raise ValueError("sine angles must lie in [0, 1)")
    s12, s23, s13 = theta12, theta23, theta13
    c12 = sqrt(1.0 - s12**2)
    c23 = sqrt(1.0 - s23**2)
    c13 = sqrt(1.0 - s13**2)
    phase = 0.0 if delta is None else delta
    exp_minus = complex(cos(phase), -sin(phase))
    exp_plus = complex(cos(phase), sin(phase))
    matrix = np.array(
        [
            [c12 * c13, s12 * c13, s13 * exp_minus],
            [
                -s12 * c23 - c12 * s23 * s13 * exp_plus,
                c12 * c23 - s12 * s23 * s13 * exp_plus,
                s23 * c13,
            ],
            [
                s12 * s23 - c12 * c23 * s13 * exp_plus,
                -c12 * s23 - s12 * c23 * s13 * exp_plus,
                c23 * c13,
            ],
        ],
        dtype=complex,
    )
    return np.abs(matrix)


def ckm_prediction_rows(ratios: Mapping[str, Mapping[str, float]]) -> dict[str, object]:
    """Return CKM screen outputs from BHSM ratios."""

    angles = ckm_angles_from_bhsm_ratios(ratios)
    magnitudes = ckm_matrix_magnitudes(
        angles["sin_theta_12"],
        angles["sin_theta_23"],
        angles["sin_theta_13"],
        delta=None,
    )
    return {
        "angles": angles,
        "matrix_magnitudes": magnitudes,
        "status": "BHSM_INTERNAL_RULE_SCREEN",
        "cp_phase_status": "PLACEHOLDER",
        "limitation": (
            "CKM angles use supplied BHSM mass-ratio screen rules; CP phase is "
            "not predicted by the current implementation."
        ),
    }
