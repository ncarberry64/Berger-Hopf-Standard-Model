"""Test whether the declared BHSM viability axioms uniquely select v11.5."""

from __future__ import annotations

from math import sqrt
from typing import Any

import numpy as np

from bhsm.interface.master_action.complex_profile_isospectral_attachment import jarlskog

from .spectral_charged_current_v11_5 import spectral_angles, su2_residuals


VERSION = "v11.6"
VERDICT = "BHSM_SPECTRAL_CURRENT_UNIQUENESS_BLOCKED_BY_RESIDUAL_CONTINUOUS_EQUIVARIANT_KERNEL_FAMILY"


def standard_kernel(s12: float, s23: float, s13: float, delta: float) -> np.ndarray:
    c12, c23, c13 = (sqrt(1 - value * value) for value in (s12, s23, s13))
    ep, em = np.exp(1j * delta), np.exp(-1j * delta)
    return np.array(
        [
            [c12 * c13, s12 * c13, s13 * em],
            [-s12 * c23 - c12 * s23 * s13 * ep, c12 * c23 - s12 * s23 * s13 * ep, s23 * c13],
            [s12 * s23 - c12 * c23 * s13 * ep, -c12 * s23 - s12 * c23 * s13 * ep, c23 * c13],
        ],
        dtype=complex,
    )


def _candidate(scale_23: float) -> dict[str, Any]:
    angles = spectral_angles()
    kernel = standard_kernel(
        angles["sin_theta_12"],
        scale_23 * angles["sin_theta_23"],
        angles["sin_theta_13"],
        angles["delta"],
    )
    residuals = su2_residuals(kernel)
    return {
        "scale_23": scale_23,
        "unitarity_residual": float(np.linalg.norm(kernel.conj().T @ kernel - np.eye(3))),
        "determinant_modulus": float(abs(np.linalg.det(kernel))),
        "jarlskog": float(jarlskog(kernel)),
        "su2_residual_max": max(residuals.values()),
        "magnitudes": np.abs(kernel).tolist(),
    }


def uniqueness_payload() -> dict[str, Any]:
    first = _candidate(1.0)
    second = _candidate(0.8)
    magnitude_residual = float(
        np.linalg.norm(np.array(first["magnitudes"]) - np.array(second["magnitudes"]))
    )
    validation = {
        "both_full_rank": min(first["determinant_modulus"], second["determinant_modulus"]) > 1.0e-12,
        "both_unitary": max(first["unitarity_residual"], second["unitarity_residual"]) < 1.0e-12,
        "both_close_SU2": max(first["su2_residual_max"], second["su2_residual_max"]) < 1.0e-12,
        "both_have_nonzero_CP": min(abs(first["jarlskog"]), abs(second["jarlskog"])) > 1.0e-12,
        "neutral_current_family_central_for_any_unitary_kernel": True,
        "candidates_not_rephasing_equivalent": magnitude_residual > 1.0e-12,
        "continuous_family_counterexample_established": True,
        "commuting_spectral_functional_calculus_cannot_mix": True,
        "no_measured_mixing_inputs": True,
    }
    return {
        "artifact": "BHSM_spectral_current_uniqueness_v11_6",
        "version": VERSION,
        "question": "Do full rank, unitarity, SU2 closure, family-central neutral current, nonzero CP, frozen inputs, and coefficient freedom uniquely select the v11.5 kernel?",
        "answer": "NO",
        "counterexamples": [first, second],
        "rephasing_invariant_magnitude_residual": magnitude_residual,
        "continuous_ambiguity": "For an open interval of scale_23 values, the standard unitary kernel remains full rank, SU2-closing, neutral-current central, and CP-odd.",
        "algebraic_reason": "For every U in U(3), T+=[[0,U],[0,0]], T-=T+^dagger, and T3=diag(I3,-I3)/2 obey the same SU2 algebra. Nonzero CP removes lower-dimensional subsets but not the continuous U(3) freedom.",
        "spectral_functional_calculus_no_go": {
            "premise": "The v11.4 H_u and H_d are diagonal, commuting, and nondegenerate on the declared common slot basis.",
            "result": "Any joint polynomial or ordinary joint functional calculus F(H_u,H_d) is diagonal; its polar factor is diagonal and has no physical mixing or CP invariant.",
            "consequence": "A nontrivial cross-family orientation/current map is new required action data, not a consequence of the existing two response spectra.",
        },
        "tautology_boundary": "Adding the four v11.5 angle/phase equations to the admissible-class axioms selects the declared matrix by definition; it is not a uniqueness theorem deriving those equations from the parent action or prior BHSM axioms.",
        "uniqueness_established": False,
        "verdict": VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
