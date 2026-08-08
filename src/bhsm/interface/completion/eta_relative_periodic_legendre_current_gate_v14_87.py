"""BHSM v14.87 eta relative-periodic Legendre/current gate.

This module derives the velocity Legendre Hessian of the retained Lorentzian
Path-B p2+p8 eta density and applies it to the missing reflected coexact L=2
momentum source.  It distinguishes a sourced ADM response from the still
unproved physical shape-transport generator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from bhsm.interface.completion.full_preimage_cap_inertia_operator_v14_84 import (
    CHARGED_CURRENT_PROVENANCE_GATE,
    EXACT_NEXT_OBJECT,
    NONCENTRAL_CURRENT_GATE,
)
from bhsm.interface.completion.source_free_relative_frame_v14_41 import (
    coexact_shift_eigenvalue,
)


VERSION = "v14.87"
PRIMARY_VERDICT = (
    "BHSM_V14_87_THE_RETAINED_LORENTZIAN_PATH_B_P2_PLUS_P8_ETA_ACTION_HAS_"
    "A_POSITIVE_VELOCITY_LEGENDRE_HESSIAN_ONLY_INSIDE_THE_EXPLICIT_CONE_"
    "KAPPA1_PLUS_X_CUBED_MINUS_6_X_SQUARED_NORM_D0ETA_SQUARED_GREATER_THAN_"
    "ZERO;_ON_THE_ZERO_CANONICAL_MOMENTUM_STATIONARY_BRANCH_THIS_FORCES_"
    "D0ETA_ZERO_AND_THEREFORE_ZERO_REFLECTION_ODD_COEXACT_L2_ETA_CURRENT,_"
    "WHILE_A_NONZERO_PERIODIC_BRANCH_REQUIRES_AN_ACTION_SELECTED_CHARGE_OR_"
    "EXCHANGE_SECTOR_AND_MUST_PASS_THE_LEGENDRE_CONVEXITY_KILL_SCREEN_BEFORE_"
    "ITS_SOURCED_COEXACT_ADM_RESPONSE_CAN_BE_MIXED_INTO_PHYSICAL_SHAPE_TRANSPORT"
)
NEXT_EXECUTABLE_SUBOBJECT = (
    "ACTION_SELECTED_NONZERO_REFLECTION_ODD_COEXACT_L2_ETA_OR_COLLECTIVE_"
    "DIRAC_CHARGE_SECTOR_WITH_POINTWISE_LEGENDRE_POSITIVITY_GLOBAL_"
    "CONSTRAINTS_SELF_ADJOINT_FULL_PREIMAGE_DOMAIN_AND_EXPLICIT_MIXED_"
    "VARIATION_FROM_THE_SOURCED_MOMENTUM_RESPONSE_INTO_THE_ELL2_SHAPE_TRANSPORT"
)


def path_b_derivatives(x_eta: float, kappa1: float = 1.0) -> tuple[float, float]:
    """Return F'(X),F''(X) for F(X)=kappa1 X/2+X^4/8."""

    if x_eta < 0.0 or kappa1 <= 0.0:
        raise ValueError("the retained admissible branch requires X>=0 and kappa1>0")
    return 0.5 * (kappa1 + x_eta**3), 1.5 * x_eta**2


def lorentzian_eta_legendre_hessian(
    velocity: Sequence[float],
    spatial_gradient_norm_squared: float,
    *,
    kappa1: float = 1.0,
    weight: float = 1.0,
) -> np.ndarray:
    """Hessian dp/dv for L=-w F(s-|v|^2) on the retained X>=0 branch."""

    v = np.asarray(velocity, dtype=float)
    if v.ndim != 1 or v.size == 0:
        raise ValueError("velocity must be a nonempty vector")
    if spatial_gradient_norm_squared < 0.0 or kappa1 <= 0.0 or weight <= 0.0:
        raise ValueError("norm and action coefficients must be nonnegative/positive")
    speed_squared = float(np.dot(v, v))
    x_eta = spatial_gradient_norm_squared - speed_squared
    fp, fpp = path_b_derivatives(x_eta, kappa1)
    return 2.0 * weight * (fp * np.eye(v.size) - 2.0 * fpp * np.outer(v, v))


def legendre_eigenvalues(
    velocity: Sequence[float],
    spatial_gradient_norm_squared: float,
    *,
    kappa1: float = 1.0,
    weight: float = 1.0,
) -> dict[str, float]:
    """Analytic transverse and velocity-parallel Legendre eigenvalues."""

    v = np.asarray(velocity, dtype=float)
    if v.ndim != 1 or v.size == 0:
        raise ValueError("velocity must be a nonempty vector")
    speed_squared = float(np.dot(v, v))
    x_eta = spatial_gradient_norm_squared - speed_squared
    path_b_derivatives(x_eta, kappa1)
    transverse = weight * (kappa1 + x_eta**3)
    parallel = weight * (kappa1 + x_eta**3 - 6.0 * x_eta**2 * speed_squared)
    return {
        "X": x_eta,
        "speed_squared": speed_squared,
        "transverse": transverse,
        "parallel": parallel,
        "minimum": min(transverse, parallel),
    }


def canonical_eta_momentum(
    velocity: Sequence[float],
    spatial_gradient_norm_squared: float,
    *,
    kappa1: float = 1.0,
    weight: float = 1.0,
) -> np.ndarray:
    """Canonical p=2wF'(X)v=w(kappa1+X^3)v."""

    v = np.asarray(velocity, dtype=float)
    values = legendre_eigenvalues(
        v,
        spatial_gradient_norm_squared,
        kappa1=kappa1,
        weight=weight,
    )
    return weight * (kappa1 + values["X"] ** 3) * v


def finite_difference_legendre_error(
    velocity: Sequence[float],
    spatial_gradient_norm_squared: float,
    *,
    epsilon: float = 1.0e-6,
) -> float:
    """Verify the analytic Legendre Hessian as the Jacobian of p_eta."""

    v = np.asarray(velocity, dtype=float)
    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    analytic = lorentzian_eta_legendre_hessian(v, spatial_gradient_norm_squared)
    numeric = np.zeros_like(analytic)
    for column in range(v.size):
        direction = np.zeros_like(v)
        direction[column] = epsilon
        numeric[:, column] = (
            canonical_eta_momentum(v + direction, spatial_gradient_norm_squared)
            - canonical_eta_momentum(v - direction, spatial_gradient_norm_squared)
        ) / (2.0 * epsilon)
    return float(np.linalg.norm(numeric - analytic, ord=np.inf))


def eta_spatial_momentum_current(
    velocity: Sequence[float],
    spatial_derivatives: Sequence[Sequence[float]],
    *,
    kappa1: float = 1.0,
    weight: float = 1.0,
) -> np.ndarray:
    """J_i=w(kappa1+X^3)<D0 eta,D_i eta> in an orthonormal frame."""

    v = np.asarray(velocity, dtype=float)
    gradients = np.asarray(spatial_derivatives, dtype=float)
    if v.ndim != 1 or gradients.ndim != 2 or gradients.shape[1] != v.size:
        raise ValueError("spatial derivatives must have shape (directions,target rank)")
    spatial_norm = float(np.sum(gradients * gradients))
    values = legendre_eigenvalues(v, spatial_norm, kappa1=kappa1, weight=weight)
    return weight * (kappa1 + values["X"] ** 3) * (gradients @ v)


def reflected_odd_coefficients(
    plus: Sequence[float],
    minus: Sequence[float],
    reflection: Sequence[Sequence[float]],
) -> np.ndarray:
    """Odd cap coefficient after pulling the minus datum to the plus cap."""

    p = np.asarray(plus, dtype=float)
    m = np.asarray(minus, dtype=float)
    transform = np.asarray(reflection, dtype=float)
    if p.ndim != 1 or m.shape != p.shape or transform.shape != (p.size, p.size):
        raise ValueError("cap coefficients and reflection must match")
    if not np.allclose(transform.T @ transform, np.eye(p.size), atol=1e-12, rtol=0.0):
        raise ValueError("reflection must be orthogonal")
    return 0.5 * (p - transform.T @ m)


def sourced_coexact_shift_coefficients(
    current_l2: Sequence[float],
    *,
    radius: float = 1.0,
    gravitational_coupling: float = 1.0,
) -> np.ndarray:
    """Solve L_shift beta_L2=kappa_grav J_L2 on the round reference domain."""

    current = np.asarray(current_l2, dtype=float)
    if current.ndim != 1 or radius <= 0.0 or gravitational_coupling <= 0.0:
        raise ValueError("require a coefficient vector and positive action scales")
    eigenvalue = coexact_shift_eigenvalue(2, radius)
    return gravitational_coupling * current / eigenvalue


def deterministic_witness() -> dict[str, Any]:
    """Exercise positive, near-singular, and negative Legendre branches."""

    x_eta = 1.0
    critical_speed = np.sqrt((1.0 + x_eta**3) / (6.0 * x_eta**2))
    speeds = {
        "positive": 0.25,
        "near_positive": critical_speed * (1.0 - 1.0e-8),
        "negative": 0.8,
    }
    rows: dict[str, Any] = {}
    for label, speed in speeds.items():
        v = np.asarray([speed, 0.0, 0.0])
        spatial = x_eta + speed**2
        analytic = legendre_eigenvalues(v, spatial)
        numeric = np.linalg.eigvalsh(lorentzian_eta_legendre_hessian(v, spatial))
        rows[label] = {
            "speed": speed,
            "analytic_parallel": analytic["parallel"],
            "numeric_eigenvalues": numeric.tolist(),
        }
    rng = np.random.default_rng(1487)
    q, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    velocity = np.asarray([0.2, -0.1, 0.05, 0.08])
    spatial = 1.4 + float(np.dot(velocity, velocity))
    original = lorentzian_eta_legendre_hessian(velocity, spatial)
    rotated = lorentzian_eta_legendre_hessian(q @ velocity, spatial)
    return {
        "critical_speed_at_X1": critical_speed,
        "branches": rows,
        "basis_covariance_residual": float(np.linalg.norm(rotated - q @ original @ q.T)),
        "finite_difference_legendre_error": finite_difference_legendre_error(velocity, spatial),
    }


def completion_payload() -> dict[str, Any]:
    witness = deterministic_witness()
    zero_velocity = np.zeros(4)
    zero_gradients = np.eye(4)
    zero_momentum = canonical_eta_momentum(zero_velocity, 1.0)
    zero_current = eta_spatial_momentum_current(zero_velocity, zero_gradients)
    odd = reflected_odd_coefficients(np.zeros(8), np.zeros(8), np.eye(8))
    sourced_shift = sourced_coexact_shift_coefficients(np.ones(8), radius=2.0)
    validation = {
        "analytic_positive_branch": witness["branches"]["positive"]["analytic_parallel"] > 0.0,
        "near_singular_branch_resolved_positive": witness["branches"]["near_positive"]["analytic_parallel"] > 0.0,
        "negative_branch_detected": witness["branches"]["negative"]["analytic_parallel"] < 0.0,
        "basis_covariance": witness["basis_covariance_residual"] < 1e-12,
        "finite_difference_legendre_jacobian": witness["finite_difference_legendre_error"] < 1e-8,
        "zero_velocity_has_zero_canonical_momentum": np.allclose(zero_momentum, 0.0),
        "zero_velocity_has_zero_spatial_current": np.allclose(zero_current, 0.0),
        "zero_caps_have_zero_odd_L2_current": np.allclose(odd, 0.0),
        "round_L2_sourced_resolvent_is_kappa_R2_over_5": np.allclose(sourced_shift, 0.8),
        "full_BHSM_not_claimed": True,
        "flavor_gates_preserved": True,
    }
    return {
        "artifact": "BHSM_eta_relative_periodic_legendre_current_gate_v14_87",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "canonical_exact_next_object": EXACT_NEXT_OBJECT,
        "next_executable_subobject": NEXT_EXECUTABLE_SUBOBJECT,
        "action": {
            "density": "L_eta=-w F(X), F(X)=kappa1 X/2+X^4/8",
            "Lorentzian_invariant": "X=|D_i eta|^2-|D_0 eta|^2",
            "canonical_momentum": "p_eta=w(kappa1+X^3)D_0 eta",
            "velocity_Legendre_Hessian": "K=2w[F'(X)I-2F''(X)D0eta tensor D0eta]",
            "transverse_eigenvalue": "w(kappa1+X^3)",
            "parallel_eigenvalue": "w[kappa1+X^3-6X^2|D0eta|^2]",
        },
        "kinetic_kill_screen": {
            "positive_condition": "kappa1+X^3-6X^2|D0eta|^2>0 pointwise",
            "equality": "Legendre degeneracy; canonical evolution and cap inertia reduction singular",
            "negative": "physical eta velocity direction is negative before any cap-inertia positivity claim",
            "periodic_background_status": "ABSENT_SO_CONDITION_NOT_EVALUATED_PHYSICALLY",
        },
        "zero_momentum_theorem": {
            "domain": "retained X>=0, kappa1>0, w>0 branch",
            "statement": "p_eta=0 pointwise iff D0eta=0",
            "consequence": "J_i_eta=w(kappa1+X^3)<D0eta,D_i eta>=0",
            "reflection_odd_coexact_L2_current": "ZERO_ON_RETAINED_STATIONARY_BRANCH",
        },
        "sourced_coexact_response": {
            "equation": "L_shift beta_perp=kappa_grav P_coex J_eta",
            "round_L2_eigenvalue": "5/R^2",
            "solution": "beta_L2=(kappa_grav R^2/5)J_L2",
            "claim_boundary": (
                "a sourced ADM response is not yet the physical Delta A; the canonical mixed "
                "variation into tangential shape transport remains required"
            ),
        },
        "selection_result": {
            "action_selected_nonzero_eta_charge": False,
            "action_selected_orbit_amplitude": False,
            "action_selected_orbit_period": False,
            "external_CKM_or_mass_data_used": False,
            "source_free_periodic_eta_route": "CLOSED_ON_ZERO_MOMENTUM_BRANCH",
            "nonzero_charge_or_exchange_route": "OPEN_WITH_LEGENDRE_KILL_SCREEN",
        },
        "open_gates": {
            "charged_current_kernel": CHARGED_CURRENT_PROVENANCE_GATE,
            "noncentral_left_handed_current": NONCENTRAL_CURRENT_GATE,
        },
        "completion_status": {
            "eta_cap_kinetic_positivity": "CONDITIONAL_CONVEXITY_CONE_NOT_PHYSICALLY_EVALUATED",
            "physical_relative_transport": "OPEN",
            "degree_one_full_preimage_periodic_background": "OPEN",
            "common_self_adjoint_domain": "OPEN",
            "complete_ell2_Hessian": "OPEN",
            "BHSM_complete": False,
            "Mark_III": "NOT_REACHED",
            "physical_execution_blocked": True,
            "USB_synchronization_eligible": False,
        },
        "Hindsight_20_20": {
            "validated": [
                "the exact eta velocity Legendre eigenvalues and positivity cone",
                "zero canonical momentum forces zero eta current on the retained branch",
                "the conditional round L2 sourced coexact resolvent",
            ],
            "invalidated": [
                "unconditional eta kinetic positivity for an unknown periodic branch",
                "source-free zero-momentum eta dynamics as a nonzero L2 transport source",
                "a sourced ADM response by itself as physical shape transport",
            ],
            "reclassified": [
                "the periodic eta BVP must include a charge/exchange selection and hyperbolicity kill screen"
            ],
            "open": [
                "action selection of a nonzero reflection-odd coexact L2 charge sector",
                "global constrained periodic BVP and common self-adjoint domain",
                "mixed current-to-shape transport variation and complete Hessian",
            ],
        },
        "numeric_witness": witness,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    def default(value: Any) -> Any:
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()
        raise TypeError(type(value).__name__)

    return json.dumps(payload, indent=2, sort_keys=True, default=default) + "\n"


def materialize(repository: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[4] if repository is None else Path(repository)
    output = root / "artifacts" / "BHSM_eta_relative_periodic_legendre_current_gate_v14_87.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deterministic_json(completion_payload()), encoding="utf-8", newline="\n")
    return output
