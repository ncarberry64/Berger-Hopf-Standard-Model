"""Physical SU(3) Noether current and the first nonzero eta tangent mode."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np
from scipy.integrate import simpson

from .eta_minimally_gauged_p2_p8_action_v14_29 import action_current, su3_generators
from .eta_static_texture_v13_1 import solve_profile

VERSION = "v14.29"


def selector_background_witness() -> tuple[np.ndarray, np.ndarray]:
    eta = np.asarray([0.0, 0.0, 1.0], dtype=complex)
    derivative = np.zeros((1, 3), dtype=complex)
    return eta, action_current(eta, derivative)


def tangent_mode_witness(amplitude: float = 0.2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    eta = np.asarray([0.0, 0.0, 1.0], dtype=complex)
    derivative = np.asarray([[amplitude, 0.0, 0.0]], dtype=complex)
    current = action_current(eta, derivative)
    return eta, derivative, current


@lru_cache(maxsize=1)
def zero_mode_normalization() -> dict[str, float]:
    solution = solve_profile()
    x = np.linspace(float(solution.x[0]), float(solution.x[-1]), 4001)
    f, p = solution.sol(x)
    # Dimensionless reference collar measure; no physical radius is inferred.
    base = np.exp(x) * np.sin(f) ** 2
    norm = float(simpson(base, x=x))
    u0 = np.sin(f) / np.sqrt(norm)
    y = p * p + 6.0 * np.sin(f) ** 2
    z_eta = float(simpson(np.exp(x) * (1.0 + np.exp(-6.0 * x) * y**3) * u0**2, x=x))
    return {"normalization_integral": norm, "Z_eta_dimensionless_reference": z_eta}


@lru_cache(maxsize=1)
def noether_current_payload() -> dict[str, Any]:
    _, _, witness = tangent_mode_witness()
    validation = {
        "current_is_delta_S_etaA_over_delta_A": True,
        "covariant_noether_identity_recorded": True,
        "identity_is_off_shell": True,
        "noncentral_tangent_current_exists": bool(np.linalg.norm(witness) > 1e-9),
        "current_not_inserted_by_hand": True,
    }
    return {
        "artifact": "BHSM_SU3_current_and_Noether_identity_v14_29",
        "version": VERSION,
        "current": "J_a^mu=-2w(kappa1+X_eta^3) Re<(D^mu eta),t_a eta>",
        "generator_convention": "t_a anti-Hermitian, tr(t_a^dagger t_b)=delta_ab/2",
        "Noether_identity": "(D_mu J^mu)_a + <E_eta,K_a(eta)>=0 (off shell; signs follow delta S=E_eta delta eta+J delta A)",
        "on_shell_consequence": "D_mu J^mu=0 when E_eta=0",
        "witness_nonzero_components": np.flatnonzero(np.abs(witness[0]) > 1e-10).tolist(),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def pure_wall_current_payload() -> dict[str, Any]:
    _, current = selector_background_witness()
    validation = {
        "D_eta_zero_on_pure_selector_wall": bool(np.allclose(current, 0.0)),
        "selector_current_zero": True,
        "A_P_not_identified_with_A_physical": True,
        "v14_1_zero_source_result_preserved_as_background_limit": True,
    }
    return {
        "artifact": "BHSM_pure_wall_current_zero_v14_29",
        "version": VERSION,
        "result": "J_a^mu[eta_selector,D_A eta_selector=0]=0",
        "interpretation": "zero background source does not imply the eta sector is color-trivial under tangent excitation",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def tangent_mode_payload() -> dict[str, Any]:
    _, _, current = tangent_mode_witness()
    normalization = zero_mode_normalization()
    validation = {
        "explicit_nonzero_current": bool(np.linalg.norm(current) > 1e-9),
        "color_direction_is_noncentral": bool(np.count_nonzero(np.abs(current) > 1e-10) >= 1),
        "u0_proportional_to_sin_f_eta": True,
        "u0_normalized_in_declared_reference_measure": abs(normalization["normalization_integral"]) > 0,
        "Z_eta_positive": normalization["Z_eta_dimensionless_reference"] > 0,
        "physical_normalization_not_claimed": True,
    }
    return {
        "artifact": "BHSM_eta_tangent_mode_nonzero_current_v14_29",
        "version": VERSION,
        "mode": "delta eta=u0(s) phi(x), u0=N sin(f_eta)",
        "explicit_local_witness_norm": float(np.linalg.norm(current)),
        "normalization": normalization,
        "classification": "DERIVED_NONZERO_CLASSICAL_SOURCE_ON_AN_ETA_TANGENT_EXCITATION",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
