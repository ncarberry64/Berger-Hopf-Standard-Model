"""Gate 29B one-loop RG matching scaffold.

This module treats the supplied geometric couplings as electroweak-scale
matching conditions. Two-loop and threshold matching are explicit placeholders,
not completed calculations.
"""

from __future__ import annotations

from math import exp, log, pi
from typing import Mapping

SM_B_ONE_LOOP = {"alpha1": 41 / 10, "alpha2": -19 / 6, "alpha3": -7}

# Empirical electroweak reference inputs.
MZ = 91.1876
ALPHA_EM_INV_MZ_EMPIRICAL = 127.95
SIN2_THETA_W_MZ_EMPIRICAL = 0.23122
ALPHA3_MZ_EMPIRICAL = 0.1179
ELECTROWEAK_WINDOW_GEV = (50.0, 150.0)


def default_reference_values() -> dict[str, float]:
    """Return approximate empirical GUT-normalized couplings at MZ."""

    alpha_em = 1.0 / ALPHA_EM_INV_MZ_EMPIRICAL
    cos2_theta_w = 1.0 - SIN2_THETA_W_MZ_EMPIRICAL
    return {
        "alpha1": (5.0 / 3.0) * alpha_em / cos2_theta_w,
        "alpha2": alpha_em / SIN2_THETA_W_MZ_EMPIRICAL,
        "alpha3": ALPHA3_MZ_EMPIRICAL,
    }


def geometric_matching_values() -> dict[str, float]:
    """Return supplied geometric matching values."""

    return {
        "alpha1": 1.0 / (6.0 * pi**2),
        "alpha2": 1.0 / (3.0 * pi**2),
        "alpha3": 7.0 / (6.0 * pi**2),
    }


def run_alpha_inverse_one_loop(alpha_inv_mu0: float, b: float, mu0: float, mu: float) -> float:
    """Run alpha^{-1} from mu0 to mu at one loop."""

    if alpha_inv_mu0 <= 0:
        raise ValueError("alpha_inv_mu0 must be positive")
    if mu0 <= 0 or mu <= 0:
        raise ValueError("scales must be positive")
    return float(alpha_inv_mu0 - (b / (2.0 * pi)) * log(mu / mu0))


def run_couplings_one_loop(
    alpha_values: Mapping[str, float],
    mu0: float,
    mu: float,
) -> dict[str, float]:
    """Run all supplied SM couplings at one loop."""

    output: dict[str, float] = {}
    for name, alpha in alpha_values.items():
        if name not in SM_B_ONE_LOOP:
            raise ValueError(f"unknown coupling: {name}")
        if alpha <= 0:
            raise ValueError("alpha values must be positive")
        alpha_inv = run_alpha_inverse_one_loop(1.0 / alpha, SM_B_ONE_LOOP[name], mu0, mu)
        output[name] = 1.0 / alpha_inv
    return output


def solve_matching_scale_one_loop(
    target_alpha: float,
    geom_alpha: float,
    b: float,
    reference_mu: float,
) -> float:
    """Solve mu_star where one-loop running target_alpha reaches geom_alpha."""

    if target_alpha <= 0 or geom_alpha <= 0:
        raise ValueError("couplings must be positive")
    if reference_mu <= 0:
        raise ValueError("reference_mu must be positive")
    if b == 0:
        raise ValueError("one-loop coefficient b must be nonzero")
    target_inv = 1.0 / target_alpha
    geom_inv = 1.0 / geom_alpha
    log_ratio = (target_inv - geom_inv) * (2.0 * pi / b)
    return float(reference_mu * exp(log_ratio))


def matching_report(
    reference_values: Mapping[str, float] | None = None,
    reference_mu: float = MZ,
) -> dict[str, object]:
    """Return one-loop geometric matching-scale report."""

    refs = dict(default_reference_values() if reference_values is None else reference_values)
    geom = geometric_matching_values()
    low, high = ELECTROWEAK_WINDOW_GEV
    rows: dict[str, dict[str, float | bool]] = {}
    for name in ("alpha1", "alpha2", "alpha3"):
        scale = solve_matching_scale_one_loop(
            target_alpha=refs[name],
            geom_alpha=geom[name],
            b=SM_B_ONE_LOOP[name],
            reference_mu=reference_mu,
        )
        rows[name] = {
            "reference_alpha": refs[name],
            "geometric_alpha": geom[name],
            "matching_scale_gev": scale,
            "in_electroweak_window": bool(low <= scale <= high),
        }
    return {
        "status": "ONE_LOOP_SCAFFOLD",
        "reference_mu_gev": reference_mu,
        "electroweak_window_gev": ELECTROWEAK_WINDOW_GEV,
        "rows": rows,
        "limitations": (
            "Full two-/three-loop threshold matching remains OPEN; this is a one-loop scaffold."
        ),
    }


def threshold_placeholder(*args: object, **kwargs: object) -> dict[str, object]:
    """Explicit placeholder for future threshold corrections."""

    return {
        "status": "PLACEHOLDER_OPEN",
        "complete": False,
        "inputs": {"args": args, "kwargs": kwargs},
        "limitation": "Threshold matching is not implemented.",
    }


def two_loop_placeholder(*args: object, **kwargs: object) -> dict[str, object]:
    """Explicit placeholder for future two-loop running."""

    return {
        "status": "PLACEHOLDER_OPEN",
        "complete": False,
        "inputs": {"args": args, "kwargs": kwargs},
        "limitation": "Two-loop RG matching is not implemented.",
    }
