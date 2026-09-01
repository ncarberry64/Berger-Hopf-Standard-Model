"""SU(3) singlet enclosure-to-exterior polarizability bridge.

The closed-child Gauss constraint and historical Wilson singlets exclude a
linear exterior color charge.  This module derives the first nonvanishing
finite-size numerator: a singlet can respond through an internal colored
excitation and return to the singlet sector.  The returned hadron Hamiltonian
and its excitation resolvent remain open.
"""

from __future__ import annotations

from itertools import permutations
from typing import Any, Iterable, Sequence

import numpy as np

from bhsm.interface.completion.eta_minimally_gauged_p2_p8_action_v14_29 import (
    su3_generators,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "AE31_CURRENT_C2_COLOR_SINGLET_RESIDUAL_RESPONSE_BRIDGE"


def hermitian_su3_generators() -> tuple[np.ndarray, ...]:
    """Return T_a=-i t_a with Tr(T_a T_b)=delta_ab/2."""

    return tuple(-1.0j * generator for generator in su3_generators())


def meson_singlet_state() -> np.ndarray:
    state = np.zeros(9, dtype=complex)
    for index in range(3):
        state[3 * index + index] = 1.0 / np.sqrt(3.0)
    return state


def baryon_singlet_state() -> np.ndarray:
    state = np.zeros(27, dtype=complex)
    for permutation in permutations(range(3)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(3)
            for j in range(i + 1, 3)
        )
        flat = (3 * permutation[0] + permutation[1]) * 3 + permutation[2]
        state[flat] = (-1.0) ** inversions / np.sqrt(6.0)
    return state


def _finite_weights(values: Iterable[float], length: int) -> np.ndarray:
    weights = np.asarray(tuple(values), dtype=float)
    if weights.shape != (length,) or not np.all(np.isfinite(weights)):
        raise ValueError(f"expected {length} finite probe weights")
    return weights


def meson_probe_operators(weights: Iterable[float]) -> tuple[np.ndarray, ...]:
    """Constituent-resolved q/anti-q exterior color probes."""

    f_q, f_qbar = _finite_weights(weights, 2)
    identity = np.eye(3)
    return tuple(
        f_q * np.kron(generator, identity)
        - f_qbar * np.kron(identity, generator.conj())
        for generator in hermitian_su3_generators()
    )


def baryon_probe_operators(weights: Iterable[float]) -> tuple[np.ndarray, ...]:
    """Constituent-resolved three-quark exterior color probes."""

    f_1, f_2, f_3 = _finite_weights(weights, 3)
    identity = np.eye(3)
    return tuple(
        f_1 * np.kron(np.kron(generator, identity), identity)
        + f_2 * np.kron(np.kron(identity, generator), identity)
        + f_3 * np.kron(np.kron(identity, identity), generator)
        for generator in hermitian_su3_generators()
    )


def singlet_transition_response(
    state: Sequence[complex], probes: Sequence[np.ndarray]
) -> dict[str, Any]:
    """Return direct singlet charge and singlet-to-colored numerator."""

    singlet = np.asarray(state, dtype=complex)
    if singlet.ndim != 1 or not np.isclose(np.vdot(singlet, singlet), 1.0):
        raise ValueError("state must be a normalized vector")
    projector = np.outer(singlet, singlet.conj())
    complement = np.eye(singlet.size) - projector
    direct = [projector @ probe @ projector for probe in probes]
    transitions = [complement @ probe @ projector for probe in probes]
    numerator = float(
        sum(np.linalg.norm(transition, ord="fro") ** 2 for transition in transitions)
    )
    return {
        "direct_singlet_linear_response_norm": float(
            max(np.linalg.norm(item, ord=2) for item in direct)
        ),
        "singlet_to_colored_transition_numerator": numerator,
        "linear_color_charge_zero": all(
            np.linalg.norm(item, ord=2) < 1.0e-12 for item in direct
        ),
        "transition_channel_nonzero": numerator > 1.0e-12,
    }


def meson_response(weights: Iterable[float]) -> dict[str, Any]:
    f_q, f_qbar = _finite_weights(weights, 2)
    response = singlet_transition_response(
        meson_singlet_state(), meson_probe_operators((f_q, f_qbar))
    )
    exact = (4.0 / 3.0) * (f_q - f_qbar) ** 2
    return {
        **response,
        "exact_formula": "N_M=C_F*(f_q-f_qbar)^2,_C_F=4/3",
        "exact_value": exact,
        "formula_residual": abs(
            response["singlet_to_colored_transition_numerator"] - exact
        ),
        "uniform_long_wavelength_probe_annihilates_singlet": bool(
            np.isclose(f_q, f_qbar)
            and response["singlet_to_colored_transition_numerator"] < 1.0e-12
        ),
    }


def baryon_response(weights: Iterable[float]) -> dict[str, Any]:
    probe_weights = _finite_weights(weights, 3)
    response = singlet_transition_response(
        baryon_singlet_state(), baryon_probe_operators(probe_weights)
    )
    mean = float(np.mean(probe_weights))
    exact = float(2.0 * np.sum((probe_weights - mean) ** 2))
    return {
        **response,
        "exact_formula": "N_B=2*sum_i(f_i-f_bar)^2",
        "exact_value": exact,
        "formula_residual": abs(
            response["singlet_to_colored_transition_numerator"] - exact
        ),
        "uniform_long_wavelength_probe_annihilates_singlet": bool(
            np.allclose(probe_weights, mean)
            and response["singlet_to_colored_transition_numerator"] < 1.0e-12
        ),
    }


def schur_polarizability(
    state: Sequence[complex],
    probes: Sequence[np.ndarray],
    colored_resolvent: np.ndarray,
) -> dict[str, Any]:
    """Evaluate -P V Q R_Q Q V P for an explicitly supplied R_Q >= 0."""

    singlet = np.asarray(state, dtype=complex)
    projector = np.outer(singlet, singlet.conj())
    complement = np.eye(singlet.size) - projector
    resolvent = np.asarray(colored_resolvent, dtype=complex)
    if resolvent.shape != projector.shape:
        raise ValueError("colored_resolvent has the wrong dimension")
    if not np.allclose(resolvent, resolvent.conj().T, atol=1.0e-12):
        raise ValueError("colored_resolvent must be Hermitian")
    if np.min(np.linalg.eigvalsh(resolvent)) < -1.0e-12:
        raise ValueError("colored_resolvent must be positive semidefinite")
    if not np.allclose(projector @ resolvent, 0.0, atol=1.0e-12):
        raise ValueError("colored_resolvent must be supported on Q=I-P")
    effective = np.zeros_like(projector)
    for probe in probes:
        effective -= projector @ probe @ complement @ resolvent @ complement @ probe @ projector
    eigenvalues = np.linalg.eigvalsh(effective)
    return {
        "operator": effective,
        "largest_eigenvalue": float(np.max(eigenvalues)),
        "negative_semidefinite": float(np.max(eigenvalues)) <= 1.0e-12,
        "nonzero": bool(np.linalg.norm(effective, ord=2) > 1.0e-12),
        "formula": "H_eff^(2)=-sum_a P1*V_a*Q*R_Q*Q*V_a*P1",
    }


def enclosure_response_contract() -> dict[str, Any]:
    return {
        "reused_upstream_assets": [
            "V14_17_WILSON_DRESSED_MESON_AND_BARYON_SINGLET_FUNCTIONALS",
            "V15_58_CLOSED_S3_GLOBAL_COLOR_GAUSS_SINGLET_CONDITION",
            "CURRENT_C2_RANK16_QUARK_COLOR_REPRESENTATIONS",
            "CURRENT_C2_PARENT_SU3_GAUGE_COEFFICIENT_RAY",
        ],
        "linear_exterior_map": "P1*V_color*P1=0",
        "first_admissible_residual_map": (
            "P1*V_color*Q_colored*(Q(H_hadron-E1)Q)^(-1)*Q_colored*V_color*P1"
        ),
        "physical_interpretation": (
            "NO_FREE_COLOR_LEAKAGE;_A_FINITE_COMPOSITE_CAN_HAVE_A_"
            "COLOR_SINGLET_POLARIZABILITY_THROUGH_INTERNAL_COLORED_STATES"
        ),
        "uniform_probe_result": "ZERO_BY_GLOBAL_GAUSS_SINGLET_CLOSURE",
        "finite_size_probe_result": "NONZERO_NUMERATOR_WHEN_CONSTITUENT_WEIGHTS_DIFFER",
        "wilson_source_is_action_term": False,
        "returned_hadron_resolvent_derived": False,
        "interhadron_residual_potential_derived": False,
        "area_law_or_mass_gap_derived": False,
        "hadron_mass_spectrum_derived": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_COLOR_SINGLET_LINEAR_EXTERIOR_CHARGE_ZERO_DERIVED": True,
        "CURRENT_C2_MESON_FINITE_SIZE_COLOR_TRANSITION_NUMERATOR_DERIVED": True,
        "CURRENT_C2_BARYON_FINITE_SIZE_COLOR_TRANSITION_NUMERATOR_DERIVED": True,
        "CURRENT_C2_COLOR_SINGLET_SCHUR_POLARIZABILITY_SIGN_DERIVED": True,
        "CURRENT_C2_RETURNED_HADRON_COLORED_RESOLVENT_DERIVED": False,
        "CURRENT_C2_NONZERO_PHYSICAL_RESIDUAL_NUCLEAR_FORCE_DERIVED": False,
        "CURRENT_C2_GLOBAL_ASYMPTOTIC_CONFINEMENT_THEOREM_DERIVED": False,
        "CURRENT_C2_HADRON_MASS_DERIVED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "baryon_probe_operators",
    "baryon_response",
    "baryon_singlet_state",
    "claim_boundary",
    "enclosure_response_contract",
    "hermitian_su3_generators",
    "meson_probe_operators",
    "meson_response",
    "meson_singlet_state",
    "schur_polarizability",
    "singlet_transition_response",
]
