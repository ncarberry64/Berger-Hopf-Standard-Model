"""Bind the universal expansion engine to the retained N12 local action.

The JAX evaluator and the authoritative analytic two-jet implement the same
96-point retained local action.  This adapter checks their value, gradient,
and Hessian at the requested background before it exposes matrix-free third
and fourth derivatives.  It is a local-kernel adapter; history gluing,
Fourier/momentum assembly, and seam terms remain explicit downstream inputs.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from bhsm.interface.aether_jax_full_local_action import (
    MDIM,
    POINTS,
    QDIM,
    STATE_DIMENSION,
    action_value,
    numpy_value_gradient_hessian,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.universal_physical_action_expansion import (
    JaxDirectionalActionOracle,
    PhysicalActionExpansion,
    PhysicalBackground,
)


Array = np.ndarray


@dataclass(frozen=True)
class RetainedActionEquivalenceAudit:
    value_absolute_error: float
    gradient_relative_error: float
    hessian_relative_error: float
    points: int
    validation_tolerance: float
    validation_passed: bool

    def metadata(self) -> dict:
        return {
            "retained_action": "BHSM_N12_FULL_LOCAL_ACTION",
            "quadrature_points": self.points,
            "value_absolute_error": self.value_absolute_error,
            "gradient_relative_error": self.gradient_relative_error,
            "hessian_relative_error": self.hessian_relative_error,
            "validation_tolerance": self.validation_tolerance,
            "validation_passed": self.validation_passed,
            "orders_cross_checked_against_analytic_jet": [0, 1, 2],
            "orders_3_4_backend": "NESTED_JAX_JVP_OF_SAME_RETAINED_EXPRESSION",
            "history_and_seam_terms_included": False,
        }


def _relative_error(first: Array, second: Array) -> float:
    numerator = float(np.linalg.norm(np.asarray(first) - np.asarray(second)))
    denominator = max(
        float(np.linalg.norm(np.asarray(first))),
        float(np.linalg.norm(np.asarray(second))),
        np.finfo(float).tiny,
    )
    return numerator / denominator


def audit_retained_n12_action_equivalence(
    state: Array,
    *,
    tolerance: float = 2.0e-12,
) -> RetainedActionEquivalenceAudit:
    state = np.asarray(state, dtype=float)
    if state.shape != (STATE_DIMENSION,):
        raise ValueError(f"retained N12 state must have shape ({STATE_DIMENSION},)")
    jax_value, jax_gradient, jax_hessian = numpy_value_gradient_hessian(state)
    exact = exact_full_action_jet_at_state(
        12,
        state[:QDIM],
        state[QDIM:2 * QDIM],
        state[2 * QDIM:2 * QDIM + MDIM],
        points=POINTS,
    )
    value_error = abs(jax_value - float(exact.value))
    gradient_error = _relative_error(jax_gradient, exact.gradient)
    hessian_error = _relative_error(jax_hessian, exact.hessian)
    passed = bool(
        value_error <= tolerance
        and gradient_error <= tolerance
        and hessian_error <= tolerance
    )
    return RetainedActionEquivalenceAudit(
        value_absolute_error=value_error,
        gradient_relative_error=gradient_error,
        hessian_relative_error=hessian_error,
        points=POINTS,
        validation_tolerance=tolerance,
        validation_passed=passed,
    )


def retained_n12_local_action_expansion(
    state: Array,
    physical_frame: Array,
    *,
    background_id: str,
    gate7_closed: bool,
    provenance: tuple[str, ...],
    validation_tolerance: float = 2.0e-12,
) -> tuple[PhysicalActionExpansion, RetainedActionEquivalenceAudit]:
    """Return a validated local action expansion on a supplied quotient frame."""

    audit = audit_retained_n12_action_equivalence(
        state,
        tolerance=validation_tolerance,
    )
    if not audit.validation_passed:
        raise RuntimeError("retained analytic and JAX local-action jets disagree")
    background = PhysicalBackground(
        state=np.asarray(state, dtype=float),
        physical_frame=np.asarray(physical_frame, dtype=float),
        action_version="BHSM-AE-2.0.0",
        background_id=background_id,
        gate7_closed=gate7_closed,
        provenance=provenance + (
            "aether_jax_full_local_action:96-point retained expression",
            "aether_n3_exact_full_local_action_jet_v17_60:analytic S0-S2 cross-check",
        ),
    )
    return PhysicalActionExpansion(JaxDirectionalActionOracle(action_value), background), audit


__all__ = [
    "RetainedActionEquivalenceAudit",
    "audit_retained_n12_action_equivalence",
    "retained_n12_local_action_expansion",
]
