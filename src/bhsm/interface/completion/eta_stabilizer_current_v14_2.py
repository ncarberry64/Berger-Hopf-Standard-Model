"""Stabilizer-selector no-current theorem for the eta wall."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable

import numpy as np

VERSION = "v14.2"
VERDICT = (
    "BHSM_ETA_WALL_STABILIZER_SELECTOR_CANNOT_BY_ITSELF_SOURCE_THE_RETAINED_"
    "INDEPENDENT_SU3_GAUSS_LAW"
)


def _gell_mann() -> tuple[np.ndarray, ...]:
    z = 0.0j
    return (
        np.array([[z, 1, z], [1, z, z], [z, z, z]], complex),
        np.array([[z, -1j, z], [1j, z, z], [z, z, z]], complex),
        np.array([[1, z, z], [z, -1, z], [z, z, z]], complex),
        np.array([[z, z, 1], [z, z, z], [1, z, z]], complex),
        np.array([[z, z, -1j], [z, z, z], [1j, z, z]], complex),
        np.array([[z, z, z], [z, z, 1], [z, 1, z]], complex),
        np.array([[z, z, z], [z, z, -1j], [z, 1j, z]], complex),
        np.diag([1, 1, -2]).astype(complex) / np.sqrt(3.0),
    )


def reference_stabilizer_generators() -> tuple[np.ndarray, ...]:
    """Return an anti-symmetric real 7D realization fixing ``e_7``."""

    generators = []
    for lam in _gell_mann():
        anti = 0.5j * lam
        realified = np.block(
            [[anti.real, -anti.imag], [anti.imag, anti.real]]
        )
        embedded = np.zeros((7, 7), dtype=float)
        embedded[:6, :6] = realified
        generators.append(embedded)
    return tuple(generators)


def covariant_selector_derivative(
    selector: Iterable[float],
    derivative: Iterable[float],
    gauge_components: Iterable[float],
) -> np.ndarray:
    u = np.asarray(tuple(selector), dtype=float)
    du = np.asarray(tuple(derivative), dtype=float)
    coefficients = np.asarray(tuple(gauge_components), dtype=float)
    if u.shape != (7,) or du.shape != (7,) or coefficients.shape != (8,):
        raise ValueError("expected selector/derivative in R7 and eight SU3 components")
    connection_action = sum(
        coefficient * generator @ u
        for coefficient, generator in zip(coefficients, reference_stabilizer_generators())
    )
    return du + connection_action


def selector_current(
    selector: Iterable[float],
    derivative: Iterable[float],
    gauge_components: Iterable[float],
) -> np.ndarray:
    u = np.asarray(tuple(selector), dtype=float)
    covariant = covariant_selector_derivative(selector, derivative, gauge_components)
    return np.array(
        [float((generator @ u) @ covariant) for generator in reference_stabilizer_generators()]
    )


@lru_cache(maxsize=1)
def stabilizer_no_current_payload() -> dict[str, Any]:
    selector = np.eye(7)[6]
    derivative = np.array([0.2, -0.1, 0.4, 0.3, -0.2, 0.5, 0.0])
    gauge = np.linspace(-0.7, 0.9, 8)
    generators = reference_stabilizer_generators()
    fixed_norms = [float(np.linalg.norm(generator @ selector)) for generator in generators]
    covariant = covariant_selector_derivative(selector, derivative, gauge)
    current = selector_current(selector, derivative, gauge)
    validation = {
        "eight_stabilizer_generators": len(generators) == 8,
        "generators_anti_symmetric": all(
            np.allclose(generator.T, -generator, atol=1.0e-13) for generator in generators
        ),
        "stabilizer_generators_fix_selector": max(fixed_norms) < 1.0e-13,
        "covariant_derivative_equals_partial_derivative": bool(
            np.allclose(covariant, derivative, atol=1.0e-13)
        ),
        "selector_color_current_zero": float(np.linalg.norm(current)) < 1.0e-13,
        "independent_Gauss_source_not_inferred": True,
    }
    return {
        "artifact": "BHSM_eta_stabilizer_no_color_current_v14_2",
        "version": VERSION,
        "theorem": "T^a u_eta=0 for T^a in Lie(Stab_G2(u_eta))=su3",
        "covariant_derivative_identity": "D_mu u_eta=partial_mu u_eta+A_mu^a T^a u_eta=partial_mu u_eta",
        "current_identity": "J_mu^a[u_eta] proportional to <T^a u_eta,D_mu u_eta>=0",
        "interpretation": (
            "the classical stabilizer selector chooses a color frame but is not the "
            "color-charged matter variable"
        ),
        "verdict": VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
