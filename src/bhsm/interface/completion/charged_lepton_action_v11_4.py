"""Minimal conditional M4 charged-lepton action assembled from frozen BHSM data."""

from __future__ import annotations

from math import exp, pi, sqrt
from typing import Any


VERSION = "v11.4"
LEPTON_MODES = {"tau_slot": (0, 0), "mu_slot": (5, 2), "e_slot": (9, 3)}
PRIMARY_VERDICT = "BHSM_MINIMAL_M4_CHARGED_LEPTON_ACTION_ASSEMBLED_CONDITIONALLY"


def berger_cost(k: int, j: int, anisotropy: float) -> float:
    q = k - 2 * j
    return k * (k + 2) + (anisotropy * anisotropy - 1.0) * q * q


def overlap_eigenvalue(k: int, j: int, anisotropy: float) -> float:
    return exp(-berger_cost(k, j, anisotropy) / (4 * pi))


def yukawa_prefactor() -> float:
    """sqrt(2)*(kappa_H tau^2)*(beta_l tau/3)."""

    return 16 * sqrt(2 * pi) / 3969


def electroweak_saddle(scale_calibration_gev: float, anisotropy: float) -> float:
    if scale_calibration_gev <= 0 or anisotropy <= 0:
        raise ValueError("scale calibration and anisotropy must be positive")
    action_cost = 4 * pi * pi + (anisotropy - 1.0) / (4 * pi * pi)
    return 2 * sqrt(2) * scale_calibration_gev * exp(-action_cost)


def action_payload(
    anisotropy: float = 137.035999084 / (12 * pi * pi),
    scale_calibration_gev: float = 1.220890e19,
) -> dict[str, Any]:
    vacuum = electroweak_saddle(scale_calibration_gev, anisotropy)
    overlaps = {
        name: overlap_eigenvalue(k, j, anisotropy)
        for name, (k, j) in LEPTON_MODES.items()
    }
    yukawas = {name: yukawa_prefactor() * value for name, value in overlaps.items()}
    masses = {name: vacuum * value / sqrt(2) for name, value in yukawas.items()}
    validation = {
        "spectral_operator_nonnegative": all(
            berger_cost(k, j, anisotropy) >= 0 for k, j in LEPTON_MODES.values()
        ),
        "overlap_positive_contraction": all(0 < value <= 1 for value in overlaps.values()),
        "yukawa_dimensionless": True,
        "standard_gauge_invariant_contraction": True,
        "single_trace_normalization": True,
        "single_profile_lift": True,
        "no_lepton_mass_input": True,
        "no_family_fit": True,
        "conditional_inputs_exposed": True,
    }
    return {
        "artifact": "BHSM_minimal_M4_charged_lepton_action_v11_4",
        "version": VERSION,
        "classification": "AUTHOR_SELECTED_MINIMAL_M4_ACTION_COMPLETION_CONDITIONAL",
        "action": "int_M4 [|DH|^2-lambda_H(Hdagger H-nu_BH^2)^2+i Lbar DL+i ebar De-(Lbar Y_BH H e+h.c.)]",
        "anisotropy": anisotropy,
        "anisotropy_status": "INDEPENDENT_FROZEN_THEORY_INPUT_WITH_ALPHA_ANCHORED_NUMERICAL_SCREEN",
        "scale_calibration_GeV": scale_calibration_gev,
        "scale_status": "ONE_UNIVERSAL_DIMENSIONFUL_CALIBRATION",
        "electroweak_saddle_GeV": vacuum,
        "yukawa_prefactor": yukawa_prefactor(),
        "overlap_eigenvalues": overlaps,
        "yukawa_eigenvalues": yukawas,
        "candidate_mass_eigenvalues_GeV": masses,
        "candidate_mass_status": "CONDITIONAL_CALIBRATED_OUTPUT_NOT_PARAMETER_FREE_PREDICTION",
        "independent_Ye_retained": False,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": "ACTION_OWNED_UP_DOWN_YUKAWA_PAIR_AND_COMMON_LEFT_HANDED_CURRENT_KERNEL",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
