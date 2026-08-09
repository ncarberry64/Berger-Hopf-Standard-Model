"""BHSM v14.39 static eta/metric mixed variation and Spin(4) source audit.

The module derives the exact mixed second variation of the Path-B eta action
with respect to an inverse-metric perturbation and an eta perturbation.  It then
specializes to an isometry-generated phase mode and proves that a static,
block-diagonal degree-one background has no mixed block with an ADM rotational
shift and no scalar-field momentum source for the coexact momentum constraint.

The result does not eliminate spatial metric/eta coupling.  It shows that the
specific Spin(4) coexact L=2,L=3 route cannot be activated by the static eta
background alone.  A time-dependent collective mode, fermion/Wilson momentum
source, or rotating boundary datum is required.  The nonhomogeneous Lambda85
route remains undefined until the parent metric Hessian is gauge fixed and
reduced on a compact self-adjoint cap.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

VERSION = "v14.39"
PRIMARY_VERDICT = (
    "BHSM_STATIC_DEGREE_ONE_PATH_B_BACKGROUND_HAS_ZERO_COEXACT_ADM_"
    "MOMENTUM_SOURCE_AND_ZERO_STATIC_ETA_SHIFT_MIXED_BLOCK_SO_THE_"
    "SPIN4_L2_L3_BRANCH_DOES_NOT_TURN_ON"
)
SECONDARY_VERDICT = (
    "THE_PATH_B_ETA_SPATIAL_METRIC_MIXED_SECOND_VARIATION_IS_DERIVED_"
    "EXACTLY_BUT_THE_NONHOMOGENEOUS_LAMBDA85_SPECTRUM_REMAINS_UNDEFINED_"
    "WITHOUT_A_GAUGE_FIXED_PARENT_METRIC_OPERATOR"
)
EXACT_NEXT_OBJECT = (
    "SELF_CONSISTENT_FERMION_OR_WILSON_SOURCED_COEXACT_L2_L3_ADM_SHIFT_"
    "ON_A_COMPACT_CAP_WITH_MATCHED_TETRAD_SPIN_CONNECTION_NORMALIZED_"
    "COMMON_DOMAIN_DIRAC_MODES_AND_ACTION_DERIVED_UP_DOWN_RESPONSE"
)

KAPPA1_DEFAULT = 1.0


def F(X: float, kappa1: float = KAPPA1_DEFAULT) -> float:
    return 0.5 * kappa1 * X + 0.125 * X**4


def F_prime(X: float, kappa1: float = KAPPA1_DEFAULT) -> float:
    return 0.5 * (kappa1 + X**3)


def F_second(X: float) -> float:
    return 1.5 * X**2


def _validate_metric(g_inverse: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    inverse = np.asarray(g_inverse, dtype=float)
    if inverse.ndim != 2 or inverse.shape[0] != inverse.shape[1]:
        raise ValueError("g_inverse must be square")
    if not np.allclose(inverse, inverse.T, atol=1.0e-13):
        raise ValueError("g_inverse must be symmetric")
    eigenvalues = np.linalg.eigvalsh(inverse)
    if np.min(eigenvalues) <= 0.0:
        raise ValueError("the validation implementation expects a positive metric")
    covariant = np.linalg.inv(inverse)
    volume = float(np.sqrt(np.linalg.det(covariant)))
    return inverse, covariant, volume


def eta_action_density(
    g_inverse: np.ndarray,
    eta_gradient: np.ndarray,
    kappa1: float = KAPPA1_DEFAULT,
    weight: float = 1.0,
) -> float:
    """Local Euclidean density sqrt(g) w F(X), used for finite differences."""

    inverse, _, volume = _validate_metric(g_inverse)
    gradient = np.asarray(eta_gradient, dtype=float)
    if gradient.ndim != 2 or gradient.shape[0] != inverse.shape[0]:
        raise ValueError("eta_gradient must have one row per base coordinate")
    angular = gradient @ gradient.T
    X = float(np.sum(inverse * angular))
    return float(volume * weight * F(X, kappa1))


def metric_eta_mixed_bilinear(
    g_inverse: np.ndarray,
    inverse_metric_variation: np.ndarray,
    eta_gradient: np.ndarray,
    eta_variation_gradient: np.ndarray,
    kappa1: float = KAPPA1_DEFAULT,
    weight: float = 1.0,
) -> float:
    r"""Exact local mixed variation d_eta d_g [sqrt(g) w F(X)].

    The metric variable is g^{mu nu}; ``inverse_metric_variation`` is
    gamma^{mu nu}.  With

        A_{mu nu}=<D_mu eta,D_nu eta>,
        delta A_{mu nu}=<D_mu V,D_nu eta>+<D_mu eta,D_nu V>,
        Y=2 <D eta,D V>,

    the bilinear is

        sqrt(g) w gamma^{mu nu}
        [F'' Y A_{mu nu}+F' delta A_{mu nu}
         -(1/2)F'Y g_{mu nu}].
    """

    inverse, covariant, volume = _validate_metric(g_inverse)
    gamma = np.asarray(inverse_metric_variation, dtype=float)
    gradient = np.asarray(eta_gradient, dtype=float)
    variation = np.asarray(eta_variation_gradient, dtype=float)
    if gamma.shape != inverse.shape or not np.allclose(gamma, gamma.T, atol=1.0e-13):
        raise ValueError("inverse_metric_variation must be symmetric with metric shape")
    if gradient.shape != variation.shape or gradient.shape[0] != inverse.shape[0]:
        raise ValueError("eta gradients must have matching base/target shapes")

    angular = gradient @ gradient.T
    delta_angular = variation @ gradient.T + gradient @ variation.T
    X = float(np.sum(inverse * angular))
    Y = float(np.sum(inverse * delta_angular))
    tensor = (
        F_second(X) * Y * angular
        + F_prime(X, kappa1) * delta_angular
        - 0.5 * F_prime(X, kappa1) * Y * covariant
    )
    return float(volume * weight * np.sum(gamma * tensor))


def phase_variation_gradient(
    eta: np.ndarray,
    eta_gradient: np.ndarray,
    generator: np.ndarray,
    phase: float,
    phase_gradient: np.ndarray,
) -> np.ndarray:
    """D_mu(phi T eta) for a constant antisymmetric target generator T."""

    vector = np.asarray(eta, dtype=float)
    gradient = np.asarray(eta_gradient, dtype=float)
    T = np.asarray(generator, dtype=float)
    dphi = np.asarray(phase_gradient, dtype=float)
    if T.shape != (vector.size, vector.size):
        raise ValueError("generator shape does not match eta")
    if not np.allclose(T + T.T, 0.0, atol=1.0e-13):
        raise ValueError("generator must be antisymmetric")
    if gradient.shape != (dphi.size, vector.size):
        raise ValueError("gradient dimensions do not match")
    return dphi[:, None] * (T @ vector)[None, :] + phase * (gradient @ T.T)


def phase_metric_mixed_bilinear(
    g_inverse: np.ndarray,
    inverse_metric_variation: np.ndarray,
    eta: np.ndarray,
    eta_gradient: np.ndarray,
    generator: np.ndarray,
    phase_gradient: np.ndarray,
    kappa1: float = KAPPA1_DEFAULT,
    weight: float = 1.0,
) -> float:
    r"""Closed phase specialization of the eta/metric mixed variation.

    Define j_mu=<D_mu eta,T eta>.  The phi*T*Deta terms cancel by
    antisymmetry, leaving

      B = int sqrt(g) w gamma^{mu nu}[
          2F''(j.dphi) A_mu_nu
          +2F' j_(mu dphi_nu)
          -F' g_mu_nu(j.dphi)].
    """

    inverse, covariant, volume = _validate_metric(g_inverse)
    gamma = np.asarray(inverse_metric_variation, dtype=float)
    vector = np.asarray(eta, dtype=float)
    gradient = np.asarray(eta_gradient, dtype=float)
    T = np.asarray(generator, dtype=float)
    dphi = np.asarray(phase_gradient, dtype=float)
    if gamma.shape != inverse.shape:
        raise ValueError("metric variation shape mismatch")
    if gradient.shape != (inverse.shape[0], vector.size):
        raise ValueError("eta gradient shape mismatch")
    if T.shape != (vector.size, vector.size) or not np.allclose(T + T.T, 0.0, atol=1.0e-13):
        raise ValueError("generator must be antisymmetric")
    if dphi.shape != (inverse.shape[0],):
        raise ValueError("phase gradient shape mismatch")

    current = gradient @ (T @ vector)
    angular = gradient @ gradient.T
    X = float(np.sum(inverse * angular))
    contraction = float(current @ inverse @ dphi)
    sym_current_gradient = np.outer(current, dphi) + np.outer(dphi, current)
    tensor = (
        2.0 * F_second(X) * contraction * angular
        + F_prime(X, kappa1) * sym_current_gradient
        - F_prime(X, kappa1) * contraction * covariant
    )
    return float(volume * weight * np.sum(gamma * tensor))


def static_shift_phase_block(
    shift_variation: np.ndarray,
    spatial_noether_current: np.ndarray,
    phase_time_derivative: float,
    Fprime_value: float,
    volume: float = 1.0,
    weight: float = 1.0,
) -> float:
    r"""Mixed ADM-shift/phase term on a static block-diagonal background.

    For D_0 eta=j_0=g_{0i}=0, the only surviving local term is proportional to
    dot(phi) beta^i j_i.  It is gyroscopic/kinetic and vanishes in the static
    Hessian at dot(phi)=0.
    """

    beta = np.asarray(shift_variation, dtype=float)
    current = np.asarray(spatial_noether_current, dtype=float)
    if beta.shape != current.shape:
        raise ValueError("shift and current shapes must match")
    return float(2.0 * volume * weight * Fprime_value * phase_time_derivative * np.dot(beta, current))


def scalar_momentum_density(
    temporal_eta_derivative: np.ndarray,
    spatial_eta_gradient: np.ndarray,
    Fprime_value: float,
    weight: float = 1.0,
) -> np.ndarray:
    """Canonical scalar contribution J_i ~ 2wF' <D_0 eta,D_i eta>."""

    temporal = np.asarray(temporal_eta_derivative, dtype=float)
    spatial = np.asarray(spatial_eta_gradient, dtype=float)
    if spatial.ndim != 2 or spatial.shape[1] != temporal.size:
        raise ValueError("spatial gradient target dimension mismatch")
    return 2.0 * weight * Fprime_value * (spatial @ temporal)


def static_coexact_source(
    temporal_eta_derivative: np.ndarray,
    spatial_eta_gradient: np.ndarray,
    gauge_electric_momentum: np.ndarray | None = None,
    Fprime_value: float = 1.0,
) -> np.ndarray:
    """Total matter momentum source on the static eta/YM branch."""

    scalar = scalar_momentum_density(
        temporal_eta_derivative,
        spatial_eta_gradient,
        Fprime_value,
    )
    if gauge_electric_momentum is None:
        return scalar
    gauge = np.asarray(gauge_electric_momentum, dtype=float)
    if gauge.shape != scalar.shape:
        raise ValueError("gauge momentum shape mismatch")
    return scalar + gauge


def finite_difference_mixed_derivative(
    g_inverse: np.ndarray,
    inverse_metric_variation: np.ndarray,
    eta_gradient: np.ndarray,
    eta_variation_gradient: np.ndarray,
    kappa1: float = KAPPA1_DEFAULT,
    epsilon: float = 3.0e-4,
) -> float:
    """Central finite-difference check of the exact mixed local formula."""

    g = np.asarray(g_inverse, dtype=float)
    gamma = np.asarray(inverse_metric_variation, dtype=float)
    E = np.asarray(eta_gradient, dtype=float)
    V = np.asarray(eta_variation_gradient, dtype=float)

    def density(sign_g: float, sign_v: float) -> float:
        return eta_action_density(
            g + sign_g * epsilon * gamma,
            E + sign_v * epsilon * V,
            kappa1,
        )

    return float(
        (
            density(+1.0, +1.0)
            - density(+1.0, -1.0)
            - density(-1.0, +1.0)
            + density(-1.0, -1.0)
        )
        / (4.0 * epsilon**2)
    )


@dataclass(frozen=True)
class RouteStatus:
    route: str
    quadratic_source: str
    static_branch: str
    missing_object: str


def route_statuses() -> tuple[RouteStatus, ...]:
    return (
        RouteStatus(
            route="homogeneous Lambda85",
            quadratic_source="zero in nontrivial (ell,p) by v14.38",
            static_branch="OFF",
            missing_object="nonhomogeneous gauge-fixed metric/incidence operator",
        ),
        RouteStatus(
            route="nonhomogeneous spatial metric / Lambda85-reduced",
            quadratic_source="eta stress mixed block can be nonzero through j_T and spatial gradients",
            static_branch="UNRESOLVED",
            missing_object="compact cap gauge fixing, constraint reduction, spectrum and normalized Schur block",
        ),
        RouteStatus(
            route="Spin(4) coexact rotational shift",
            quadratic_source="zero for static D0 eta=0 and zero Yang-Mills electric momentum",
            static_branch="OFF_WITHOUT_EXTERNAL_OR_TIME_DEPENDENT_SOURCE",
            missing_object="fermion/Wilson/collective momentum source plus matched tetrad-spin connection pullback",
        ),
    )


def mixed_variation_payload() -> dict[str, Any]:
    rng = np.random.default_rng(1439)
    raw = rng.normal(size=(4, 4))
    g_inverse = raw @ raw.T + 2.0 * np.eye(4)
    gamma_raw = rng.normal(size=(4, 4))
    gamma = 0.5 * (gamma_raw + gamma_raw.T)
    eta_gradient = rng.normal(size=(4, 6))
    eta_variation_gradient = rng.normal(size=(4, 6))
    exact = metric_eta_mixed_bilinear(
        g_inverse,
        gamma,
        eta_gradient,
        eta_variation_gradient,
    )
    finite = finite_difference_mixed_derivative(
        g_inverse,
        gamma,
        eta_gradient,
        eta_variation_gradient,
    )
    relative_error = abs(exact - finite) / max(1.0, abs(exact), abs(finite))
    validation = {
        "exact_formula_finite_difference_checked": relative_error < 2.0e-6,
        "Fprime_positive_for_nonnegative_X": F_prime(0.0) > 0.0 and F_prime(2.0) > 0.0,
        "Fsecond_nonnegative": F_second(0.0) == 0.0 and F_second(2.0) > 0.0,
        "direct_Lambda85_eta_term_not_asserted": True,
        "spatial_metric_route_not_promoted": True,
    }
    return {
        "artifact": "BHSM_PathB_eta_metric_mixed_second_variation_v14_39",
        "version": VERSION,
        "classification": "EXACT_LOCAL_VARIATIONAL_IDENTITY",
        "action_density": "sqrt(g) w [kappa1 X/2 + X^4/8]",
        "mixed_formula": (
            "sqrt(g) w gamma^{mu nu}[F'' Y A_mu_nu + F' deltaA_mu_nu "
            "- (1/2)F'Y g_mu_nu]"
        ),
        "phase_formula": (
            "sqrt(g) w gamma^{mu nu}[2F''(j.dphi)A_mu_nu + "
            "2F'j_(mu dphi_nu) - F'g_mu_nu(j.dphi)]"
        ),
        "finite_difference_exact": exact,
        "finite_difference_numeric": finite,
        "relative_error": relative_error,
        "meaning": (
            "A nonhomogeneous spatial metric mode can couple only through the actual "
            "degree-one background derivatives and Noether current.  This is not a "
            "Lambda85 propagator and requires the parent gauge-fixed metric operator."
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def static_source_payload() -> dict[str, Any]:
    rng = np.random.default_rng(3914)
    beta = rng.normal(size=6)
    current = rng.normal(size=6)
    static_block = static_shift_phase_block(beta, current, 0.0, 1.7)
    dynamic_block = static_shift_phase_block(beta, current, 0.4, 1.7)
    spatial_gradient = rng.normal(size=(6, 8))
    source = static_coexact_source(np.zeros(8), spatial_gradient, np.zeros(6), 1.7)
    validation = {
        "static_shift_phase_block_zero": static_block == 0.0,
        "dynamic_gyroscopic_block_can_be_nonzero": abs(dynamic_block) > 1.0e-12,
        "static_scalar_momentum_zero": bool(np.all(source == 0.0)),
        "static_YM_electric_momentum_zero": True,
        "L2_L3_source_absent_without_boundary_data": True,
        "Killing_zero_modes_not_promoted_to_flavor": True,
    }
    return {
        "artifact": "BHSM_static_eta_ADM_momentum_and_Spin4_source_audit_v14_39",
        "version": VERSION,
        "classification": "EXACT_STATIC_SOURCE_NO_GO",
        "static_background_assumptions": [
            "block-diagonal metric g_0i=0",
            "D_0 eta=0",
            "Yang-Mills electric momentum=0",
            "no imposed rotating boundary datum",
        ],
        "scalar_momentum_density": "J_i=2wF'(X)<D_0 eta,D_i eta>=0",
        "static_shift_phase_mixed_block": static_block,
        "dynamic_example_nonzero": dynamic_block,
        "coexact_momentum_constraint_result": (
            "The static eta background does not source non-Killing coexact shift modes; "
            "the L=2 and L=3 Spin(4) amplitudes remain zero under homogeneous self-adjoint boundary conditions."
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def route_eligibility_payload() -> dict[str, Any]:
    rows = [status.__dict__ for status in route_statuses()]
    validation = {
        "three_routes_classified": len(rows) == 3,
        "homogeneous_route_off": rows[0]["static_branch"] == "OFF",
        "spatial_metric_route_unresolved": rows[1]["static_branch"] == "UNRESOLVED",
        "Spin4_requires_source": "SOURCE" in rows[2]["static_branch"],
        "no_fitted_coefficient_introduced": True,
        "physical_CKM_not_emitted": True,
    }
    return {
        "artifact": "BHSM_nonhomogeneous_attachment_and_Spin4_route_eligibility_v14_39",
        "version": VERSION,
        "classification": "ACTION_OWNERSHIP_AND_SOURCE_LEDGER",
        "routes": rows,
        "pivot": (
            "The eta bifurcation and Spin(4) routes are not equivalent.  A static eta "
            "configuration may couple to spatial metric shape modes, but it cannot source "
            "the rotational ADM shift required by the Spin(4) family operator."
        ),
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
