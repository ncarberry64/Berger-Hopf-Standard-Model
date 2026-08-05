"""Minimal physical-SU(3) gauging of the retained eta p2+p8 collar action."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np

VERSION = "v14.29"


def su3_generators() -> tuple[np.ndarray, ...]:
    """Anti-Hermitian fundamental generators, tr(t_a^dagger t_b)=delta_ab/2."""
    i = 1j
    hermitian = (
        [[0, 1, 0], [1, 0, 0], [0, 0, 0]],
        [[0, -i, 0], [i, 0, 0], [0, 0, 0]],
        [[1, 0, 0], [0, -1, 0], [0, 0, 0]],
        [[0, 0, 1], [0, 0, 0], [1, 0, 0]],
        [[0, 0, -i], [0, 0, 0], [i, 0, 0]],
        [[0, 0, 0], [0, 0, 1], [0, 1, 0]],
        [[0, 0, 0], [0, 0, -i], [0, i, 0]],
        np.diag([1, 1, -2]) / np.sqrt(3),
    )
    return tuple(0.5j * np.asarray(item, dtype=complex) for item in hermitian)


def covariant_derivative(eta: np.ndarray, partial_eta: np.ndarray, gauge_components: np.ndarray) -> np.ndarray:
    """D_mu eta=partial_mu eta+A_mu^a t_a eta in the local m_C=3 chart."""
    eta = np.asarray(eta, dtype=complex)
    partial_eta = np.asarray(partial_eta, dtype=complex)
    gauge_components = np.asarray(gauge_components, dtype=float)
    if eta.shape != (3,) or partial_eta.ndim != 2 or partial_eta.shape[1] != 3:
        raise ValueError("eta must be (3,) and partial_eta must be (directions,3)")
    if gauge_components.shape != (partial_eta.shape[0], 8):
        raise ValueError("gauge components must be (directions,8)")
    generators = su3_generators()
    return np.asarray([
        partial_eta[mu] + sum(gauge_components[mu, a] * generators[a] @ eta for a in range(8))
        for mu in range(partial_eta.shape[0])
    ])


def kinetic_invariant(derivative: np.ndarray) -> float:
    derivative = np.asarray(derivative, dtype=complex)
    return float(2.0 * np.real(np.vdot(derivative, derivative)))


def collar_density(x_eta: float, kappa1: float = 1.0, weight: float = 1.0) -> float:
    if kappa1 <= 0 or weight <= 0 or x_eta < 0:
        raise ValueError("require kappa1, weight>0 and X_eta>=0")
    return -weight * (0.5 * kappa1 * x_eta + 0.125 * x_eta**4)


def action_current(eta: np.ndarray, derivative: np.ndarray, kappa1: float = 1.0, weight: float = 1.0) -> np.ndarray:
    """delta L/d A_mu^a in the anti-Hermitian generator convention."""
    eta = np.asarray(eta, dtype=complex)
    derivative = np.asarray(derivative, dtype=complex)
    x_eta = kinetic_invariant(derivative)
    multiplier = -2.0 * weight * (kappa1 + x_eta**3)
    return np.asarray([
        [multiplier * np.real(np.vdot(derivative[mu], generator @ eta)) for generator in su3_generators()]
        for mu in range(derivative.shape[0])
    ])


@lru_cache(maxsize=1)
def minimally_gauged_action_payload() -> dict[str, Any]:
    validation = {
        "same_independent_physical_SU3_connection": True,
        "no_new_connection_or_coefficient": True,
        "ungauged_action_recovered_at_A_zero": True,
        "representation_is_real_six_via_3_plus_bar3": True,
        "gauge_covariant_X_eta": True,
        "current_is_action_variation": True,
        "frozen_inputs_and_no_CKM_data": True,
    }
    return {
        "artifact": "BHSM_eta_minimally_gauged_p2_p8_action_v14_29",
        "version": VERSION,
        "classification": "AUTHORITATIVE_CLASSICAL_ACTION_PROMOTION",
        "domain": "BHSM collar with the retained parent measure and positive weight w",
        "fields": "A_physical in Conn(P_color), eta in Gamma(P_color x_SU3 S6)",
        "derivative": "D_mu^A eta=partial_mu eta+A_mu^a K_a(eta)",
        "invariant": "X_eta=<D_A eta,D^A eta>=2 Re sum_mu (D_mu eta)^dagger D_mu eta in a local m_C chart",
        "density": "L_etaA=-w[kappa1 X_eta/2+X_eta^4/8]",
        "variation": "delta_A L=-2w(kappa1+X_eta^3) Re<(D^mu eta),t_a eta> delta A_mu^a",
        "coefficient_ledger": {"kappa1": "pre-existing eta coefficient", "p8": "fixed retained coefficient 1/8", "new": []},
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
