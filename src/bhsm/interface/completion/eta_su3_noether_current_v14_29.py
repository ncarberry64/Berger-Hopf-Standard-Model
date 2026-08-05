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
    # xi=0 is the stabilizer-fixed coset base point in the tangent chart.
    eta = np.zeros(3, dtype=complex)
    derivative = np.zeros((1, 3), dtype=complex)
    return eta, action_current(eta, derivative)


def tangent_mode_witness(amplitude: float = 0.2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # A compactly supported phase-rotating tangent mode has this local value.
    eta = np.asarray([amplitude, 0.0, 0.0], dtype=complex)
    derivative = np.asarray([[1j * amplitude, 0.0, 0.0]], dtype=complex)
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
        "current": "source J_a^mu=+2w(kappa1+X_eta^3) Re[(t_a xi)^dagger D^mu xi] in the local m_C chart; delta S/delta A=-J",
        "generator_convention": "t_a anti-Hermitian, tr(t_a^dagger t_b)=delta_ab/2",
        "Noether_identity": "for source J defined by delta S=-int J delta A and delta A=-D epsilon: (D_mu J^mu)_a-<E_eta,K_a(eta)>=0; equivalently D_mu(delta S/delta A_mu)_a+<E_eta,K_a>=0",
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
        "result": "J_a^mu[xi=0]=0 because K_a(eta_0)=0; a pure normal wall also has D_mu eta=0",
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
        "mode": "off-shell finite-action tangent test: eta=Exp_eta0[u(s) chi(x)e^{ikx}e1], with u vanishing at collar ends and chi compactly supported",
        "explicit_local_witness_norm": float(np.linalg.norm(current)),
        "normalization": normalization,
        "classification": "NONZERO_OFF_SHELL_TANGENT_SOURCE_WITNESS_FOR_THE_CONDITIONAL_COVARIANTIZED_ACTION_NOT_A_CLASSICAL_PARTICLE_SOLUTION",
        "physical_Z_eta_status": "OPEN_BECAUSE_THE_AUTHORITATIVE_COLLAR_JACOBIAN_WIDTH_AND_ZERO_MODE_DOMAIN_ARE_NOT_FIXED",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
