"""Canonical BHSM flavor matrix and CKM CP screen.

The functions here use the canonical model geometry already stored on
``BHSMModel``. They do not tune the Berger anisotropy or insert empirical CKM
values into the calculation.
"""

from __future__ import annotations

from math import isfinite, sin, sqrt
from typing import TYPE_CHECKING

import numpy as np

from ckm import ckm_angles_from_bhsm_ratios, ckm_matrix_magnitudes
from constants import S_OVERLAP
from mode_selection import hopf_charge

if TYPE_CHECKING:
    from bhsm_model import BHSMModel


LIGHT_UP_MODE = (10, 1)
LIGHT_DOWN_MODE = (8, 2)


def canonical_mass_ratios(model: "BHSMModel") -> dict[str, dict[str, float]]:
    """Return charged-sector mass ratios from the model's canonical geometry."""

    return {
        sector: dict(yukawa.ratios)
        for sector, yukawa in model.yukawa_sectors.items()
    }


def canonical_ckm_angles(model: "BHSMModel") -> dict[str, float]:
    """Return CKM angle screens from canonical BHSM mass ratios."""

    return ckm_angles_from_bhsm_ratios(canonical_mass_ratios(model))


def canonical_ckm_delta(model: "BHSMModel") -> dict[str, float | int | str]:
    """Return the Hopf-phase CKM CP screen.

    The internal-rule option is delta = Delta q * sqrt(S), where Delta q is
    computed from the light up/down Hopf charges. The model argument is kept so
    the report can record the active geometry without changing the rule.
    """

    q_u = hopf_charge(*LIGHT_UP_MODE)
    q_d = hopf_charge(*LIGHT_DOWN_MODE)
    delta_q = q_u - q_d
    delta = float(delta_q * sqrt(S_OVERLAP))
    if not isfinite(delta):
        raise ValueError("computed CKM delta is not finite")
    return {
        "delta": delta,
        "delta_q": delta_q,
        "q_u": q_u,
        "q_d": q_d,
        "S": S_OVERLAP,
        "geometry": model.geometry_config.name,
        "status": "HOPF_PHASE_CP_SCREEN",
        "formula": "delta_CKM = (q_u - q_d) * sqrt(S)",
    }


def canonical_ckm_matrix(model: "BHSMModel") -> np.ndarray:
    """Return canonical CKM matrix magnitudes including the Hopf-phase CP screen."""

    angles = canonical_ckm_angles(model)
    delta = float(canonical_ckm_delta(model)["delta"])
    return ckm_matrix_magnitudes(
        angles["sin_theta_12"],
        angles["sin_theta_23"],
        angles["sin_theta_13"],
        delta=delta,
    )


def jarlskog_invariant(theta12: float, theta23: float, theta13: float, delta: float) -> float:
    """Return the CKM Jarlskog invariant from sine angles and CP phase."""

    for value in (theta12, theta23, theta13):
        if value < 0 or value >= 1:
            raise ValueError("sine angles must lie in [0, 1)")
    c12 = sqrt(1.0 - theta12**2)
    c23 = sqrt(1.0 - theta23**2)
    c13 = sqrt(1.0 - theta13**2)
    return float(c12 * c23 * c13**2 * theta12 * theta23 * theta13 * sin(delta))


def canonical_flavor_report(model: "BHSMModel") -> dict[str, object]:
    """Return canonical flavor-matrix outputs for the active BHSM model."""

    ratios = canonical_mass_ratios(model)
    angles = canonical_ckm_angles(model)
    delta = canonical_ckm_delta(model)
    matrix = canonical_ckm_matrix(model)
    jarlskog = jarlskog_invariant(
        angles["sin_theta_12"],
        angles["sin_theta_23"],
        angles["sin_theta_13"],
        float(delta["delta"]),
    )
    return {
        "geometry": {
            "name": model.geometry_config.name,
            "a": model.geometry_config.a,
            "status": model.geometry_config.status,
        },
        "mass_ratios": ratios,
        "angles": angles,
        "delta": delta,
        "jarlskog": jarlskog,
        "matrix_magnitudes": matrix,
        "status": "BHSM_CANONICAL_FLAVOR_SCREEN",
        "cp_phase_status": "HOPF_PHASE_CP_SCREEN",
        "limitation": (
            "Canonical flavor matrix uses internal-rule mass ratios and Hopf "
            "phase CP screen; full action derivation of Omega_f remains open."
        ),
    }
