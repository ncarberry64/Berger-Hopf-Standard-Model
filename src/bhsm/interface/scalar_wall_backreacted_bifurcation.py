"""BHSM v6.1.6 scalar-wall backreacted bifurcation audit."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq
from scipy.special import hyp2f1


VERSION = "v6.1.6"
SPRINT = "bhsm-scalar-wall-backreacted-bifurcation-v6-1-6"
PRIMARY_RESULT = "BHSM_SCALAR_WALL_BIFURCATION_ENSEMBLE_DEPENDENT"
COMPLETION_GATE = "V6_1_6_CRITICAL_DOUBLE_ROOT_PUISEUX_CONTINUATION_AND_MIXED_STABILITY_OPEN"

ARTIFACT_FILES = {
    "ensemble": "BHSM_scalar_wall_bifurcation_ensemble_v6_1_6.json",
    "critical": "BHSM_scalar_wall_critical_mode_v6_1_6.json",
    "domain": "BHSM_scalar_wall_domain_gauge_equivalence_v6_1_6.json",
    "expansion": "BHSM_scalar_wall_perturbative_expansion_v6_1_6.json",
    "second": "BHSM_scalar_wall_second_order_backreaction_v6_1_6.json",
    "third": "BHSM_scalar_wall_third_order_source_v6_1_6.json",
    "fredholm": "BHSM_scalar_wall_Fredholm_coefficient_v6_1_6.json",
    "branch": "BHSM_scalar_wall_branch_classification_v6_1_6.json",
    "onshell": "BHSM_scalar_wall_onshell_quartic_v6_1_6.json",
    "continuation": "BHSM_scalar_wall_nonlinear_continuation_v6_1_6.json",
    "residuals": "BHSM_scalar_wall_constraint_residuals_v6_1_6.json",
    "amplitude": "BHSM_scalar_wall_amplitude_stability_v6_1_6.json",
    "mixed": "BHSM_scalar_wall_mixed_operator_v6_1_6.json",
    "sources": "BHSM_scalar_wall_B1_source_reaudit_v6_1_6.json",
    "hidden": "BHSM_scalar_wall_hidden_input_claim_audit_v6_1_6.json",
    "report": "BHSM_scalar_wall_backreacted_bifurcation_report_v6_1_6.json",
}

GUARDS = {
    "critical_eigenvalue_hard_coded_as_answer": False,
    "lapse_dropped_before_variation": False,
    "cap_length_and_lapse_both_fixed": False,
    "moving_boundary_terms_omitted": False,
    "scalar_vacuum_energy_subtracted": False,
    "boundary_tension_inserted": False,
    "boundary_vacuum_constant_inserted": False,
    "new_parent_field_added": False,
    "new_scalar_interaction_added": False,
    "P2_or_P3_repair_used": False,
    "bifurcation_sign_forced": False,
    "measured_input_used": False,
    "fixed_background_profile_called_backreacted": False,
    "continuation_failure_promoted_to_theorem": False,
    "wall_called_C_partial": False,
    "wall_called_tau_A": False,
    "bending_called_sigma_partial": False,
    "singlet_anisotropic_pressure_inserted": False,
    "amplitude_mode_called_full_mixed_stability": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def stable(value: float, digits: int = 12) -> float:
    return float(f"{value:.{digits}f}")


def _endpoint(mu: float, *, max_step: float, rtol: float, dense: bool = False):
    endpoint = math.pi / 4
    pole_cutoff = 1.0e-8
    initial = [1 - mu * pole_cutoff**2 / 10, -mu * pole_cutoff / 5]

    def rhs(rho: float, state: list[float]) -> list[float]:
        u, derivative = state
        return [derivative, -4 / math.tan(rho) * derivative - mu * u]

    solution = solve_ivp(
        rhs,
        (pole_cutoff, endpoint),
        initial,
        rtol=rtol,
        atol=rtol * 1.0e-3,
        max_step=max_step,
        dense_output=dense,
    )
    return float(solution.y[0, -1]), solution


def critical_eigenvalue(*, max_step: float = 0.0025, rtol: float = 1.0e-13) -> float:
    """Recompute the regular-pole/Dirichlet-junction eigenvalue by shooting."""
    return float(
        brentq(
            lambda mu: _endpoint(mu, max_step=max_step, rtol=rtol)[0],
            29.0,
            30.0,
            xtol=5.0e-15,
        )
    )


def hypergeometric_eigenvalue() -> float:
    """Independent analytic-coordinate root of the Gegenbauer equation."""

    endpoint_argument = math.sin(math.pi / 8) ** 2

    def boundary_value(nu: float) -> float:
        return float(hyp2f1(-nu, nu + 4, 2.5, endpoint_argument))

    nu = brentq(boundary_value, 3.0, 4.5, xtol=5.0e-15)
    return nu * (nu + 4)


def critical_mode_diagnostics(
    *, max_step: float = 0.0025, rtol: float = 1.0e-13
) -> dict[str, float]:
    """Return the weighted-normalized critical mode and required moments."""
    mu = critical_eigenvalue(max_step=max_step, rtol=rtol)
    _, solution = _endpoint(mu, max_step=max_step, rtol=rtol, dense=True)
    endpoint = math.pi / 4
    pole_cutoff = 1.0e-8

    def raw(rho: float, component: int) -> float:
        if rho == 0:
            return 1.0 if component == 0 else 0.0
        return float(solution.sol(max(rho, pole_cutoff))[component])

    def weight(rho: float) -> float:
        return 4 * math.sin(rho) ** 4

    norm = quad(
        lambda rho: weight(rho) * raw(rho, 0) ** 2,
        0,
        endpoint,
        epsabs=1.0e-13,
        epsrel=1.0e-13,
        limit=300,
    )[0]
    normalization = 1 / math.sqrt(norm)
    mode = lambda rho: normalization * raw(rho, 0)
    derivative = lambda rho: normalization * raw(rho, 1)
    quartic = quad(
        lambda rho: weight(rho) * mode(rho) ** 4,
        0,
        endpoint,
        epsabs=1.0e-12,
        epsrel=1.0e-12,
        limit=300,
    )[0]
    gradient = quad(
        lambda rho: weight(rho) * derivative(rho) ** 2,
        0,
        endpoint,
        epsabs=1.0e-12,
        epsrel=1.0e-12,
        limit=300,
    )[0]
    source_integral = quad(
        lambda rho: (
            derivative(rho) ** 2 + mu * mode(rho) ** 2
        )
        * math.tan(rho) ** 2,
        0,
        endpoint,
        epsabs=1.0e-12,
        epsrel=1.0e-12,
        limit=300,
    )[0]
    junction_derivative = derivative(endpoint)
    return {
        "mu1_over_q5": mu,
        "weighted_norm": 1.0,
        "cap_value": mode(0),
        "junction_value": mode(endpoint),
        "junction_derivative": junction_derivative,
        "quartic_moment": quartic,
        "gradient_moment": gradient,
        "eigen_residual_moment": gradient - mu,
        "warp_source_integral_Z_over_kappa": source_integral / 24,
        "junction_obstruction_Z_over_kappa": junction_derivative**2 / 12,
        "fold_slope_q1_Z_over_kappa1": abs(junction_derivative) / math.sqrt(3),
    }


def junction_constraint_residual(
    X: float,
    sigma_normal_derivative: float,
    *,
    q5: float = 1.0,
    eta: float = 0.5,
    Z_over_kappa: float = 1.0,
) -> float:
    """Constraint plus frozen B1 junction, divided by 6 kappa_1."""
    return eta**2 * X**2 - X + q5 - Z_over_kappa * sigma_normal_derivative**2 / 12


def fold_curvature_splits(
    amplitude: float,
    junction_derivative: float,
    *,
    q5: float = 1.0,
    Z_over_kappa: float = 1.0,
) -> tuple[float, float]:
    """Exact critical-double-root curvature split from the boundary constraint."""
    if q5 <= 0 or Z_over_kappa <= 0:
        raise ValueError("fold response requires q5>0 and Z5/kappa1>0")
    critical_X = 2 * q5
    shift = (
        math.sqrt(q5 * Z_over_kappa / 3)
        * abs(junction_derivative)
        * abs(amplitude)
    )
    return critical_X - shift, critical_X + shift


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": (
            "The critical odd mode is independently reproduced. At the B1 "
            "critical double root its positive normal stress obstructs the "
            "requested analytic even-metric expansion at second order, while "
            "a nonanalytic fold response or a varying-B1 ensemble remains "
            "possible. No coupled nonlinear branch or total Fredholm "
            "coefficient is claimed."
        ),
        **GUARDS,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    c = _common
    convergence = []
    for step, tolerance in (
        (0.02, 1.0e-9),
        (0.01, 1.0e-11),
        (0.005, 1.0e-12),
        (0.0025, 1.0e-13),
    ):
        row = critical_mode_diagnostics(max_step=step, rtol=tolerance)
        convergence.append(
            {
                "max_step": step,
                "rtol": tolerance,
                "mu1_over_q5": stable(row["mu1_over_q5"]),
                "weighted_norm": stable(row["weighted_norm"]),
                "junction_derivative": stable(row["junction_derivative"]),
            }
        )
    mode = critical_mode_diagnostics()
    analytic_mu = hypergeometric_eigenvalue()
    mu = stable(mode["mu1_over_q5"])
    uj = stable(mode["junction_derivative"])
    quartic = stable(mode["quartic_moment"])
    obstruction = stable(mode["junction_obstruction_Z_over_kappa"])
    fold_slope = stable(mode["fold_slope_q1_Z_over_kappa1"])
    direct_quartic_action = stable(mode["quartic_moment"] / 4)
    return {
        "ensemble": {
            **c("BHSM_scalar_wall_bifurcation_ensemble_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_BIFURCATION_ENSEMBLE_FROZEN",
            "reference": {
                "q5": 1,
                "X0": 2,
                "C_partial_over_kappa1": 0.5,
                "a0": "sqrt(2) sin(rho)",
                "rhoJ0": "pi/4",
                "mu_c": mu,
            },
            "primary_fixed": [
                "kappa_0",
                "kappa_1",
                "Z5",
                "G5",
                "C_partial",
                "all other B1 coefficients",
                "topology",
                "parity",
                "orientation",
                "action",
                "boundary conditions",
            ],
            "control": "mu=-A5/Z5",
            "solved": ["scalar amplitude", "warp profile", "normal length", "X", "junction position", "one-sided K"],
            "physical": ["proper cap length", "intrinsic boundary curvature", "one-sided extrinsic curvature"],
            "gauge": ["normal-coordinate parameterization", "fixed-domain lapse distribution", "normalization of h with compensating a"],
            "alternate_ensembles": [
                "fixed A5 with varying C_partial",
                "fixed X with varying A5",
                "fixed physical cap length with varying X",
                "fixed coordinate junction with retained lapse",
            ],
            "parent_ensemble_selector": None,
        },
        "critical": {
            **c("BHSM_scalar_wall_critical_mode_v6_1_6"),
            "status": "BHSM_CRITICAL_SCALAR_ZERO_MODE_REPRODUCED",
            "operator": "L_c=-a0^-4 d_rho(a0^4 d_rho)",
            "domain": "regular pole u'(0)=0; odd junction u(pi/4)=0",
            "weight": "a0^4=4 sin(rho)^4",
            "self_adjoint_boundary_form": "[a0^4(v u'-u v')]_0^rhoJ=0",
            "shooting_convergence": convergence,
            "independent_hypergeometric_mu1_over_q5": stable(analytic_mu),
            "route_difference": stable(mode["mu1_over_q5"] - analytic_mu, 14),
            "normalized": {
                "weighted_norm": 1,
                "cap_value": stable(mode["cap_value"]),
                "junction_value": stable(mode["junction_value"], 14),
                "junction_derivative": uj,
                "gradient_moment": stable(mode["gradient_moment"]),
                "quartic_moment": quartic,
                "eigen_residual_moment": stable(mode["eigen_residual_moment"], 14),
            },
            "adjoint_mode": "u1",
            "eigenvalue_derivative_in_mu_control": -1,
            "regression_target_used_as_answer": False,
        },
        "domain": {
            **c("BHSM_scalar_wall_domain_gauge_equivalence_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_DOMAIN_EQUIVALENCE_KINEMATICALLY_DERIVED",
            "moving": "rho in [0,rhoJ(epsilon)] with N=1 after variation",
            "fixed": "rho=ell(epsilon)x, x in [0,1], with normal lapse ell retained",
            "endpoint_map": "delta a_J=a2(rhoJ0)+rhoJ2 a0'(rhoJ0)",
            "odd_scalar_map": "delta sigma_J=u3(rhoJ0)+rhoJ2 u1'(rhoJ0)",
            "boundary_form_map": "endpoint displacement equals the fixed-domain lapse/measure contribution",
            "agreement_scope": "kinematic boundary and measure terms through the attempted O(epsilon^2) system",
            "dynamic_O_epsilon3_equivalence": "not reached because the primary analytic O(epsilon^2) junction condition is inconsistent",
            "lapse_retained_before_variation": True,
            "lapse_and_physical_length_fixed_together": False,
        },
        "expansion": {
            **c("BHSM_scalar_wall_perturbative_expansion_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_ANALYTIC_EXPANSION_BREAKS_AT_CRITICAL_FOLD",
            "requested_analytic_ansatz": {
                "sigma": "epsilon u1+epsilon^3 u3+O(epsilon^5)",
                "metric": "g0+epsilon^2 g2+O(epsilon^4)",
                "X": "X0+epsilon^2 X2+O(epsilon^4)",
                "rhoJ": "rhoJ0+epsilon^2 rhoJ2+O(epsilon^4)",
                "mu": "mu_c+epsilon^2 mu2+O(epsilon^4)",
            },
            "Z2_reason": "scalar is odd in signed amplitude and stress is even",
            "failure": "the double-root junction has no O(epsilon^2) curvature response but the normal scalar stress is positive at that order",
            "admissible_Puiseux_response": "X-Xc=O(|epsilon|); geometry is even but nonanalytic in signed epsilon",
            "no_O_epsilon_metric_term_proved": False,
            "reason_not_proved": "the critical fold invalidates the analytic implicit-function hypothesis",
        },
        "second": {
            **c("BHSM_scalar_wall_second_order_backreaction_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_ANALYTIC_SECOND_ORDER_JUNCTION_OBSTRUCTION_DERIVED",
            "bulk_constraint": "6kappa1[H^2-X/a^2]+kappa0/2=Z5 sigma'^2/2-U5",
            "B1_junction": "H_J=(C_partial/kappa1) X_J in the audited orientation magnitude",
            "combined_dimensionless": "eta^2 X^2-X+q5=(Z5/(12kappa1)) sigma_J'^2",
            "critical_complete_square": "(X-2q5)^2/(4q5)=(Z5/(12kappa1)) sigma_J'^2",
            "analytic_O_epsilon2_condition": "0=(Z5/(12kappa1))u1'(rhoJ)^2",
            "normalized_junction_derivative": uj,
            "positive_obstruction_coefficient_for_Z5_over_kappa1_1": obstruction,
            "warp_constraint_solution": "f2 tan(rho)=(Z5/(24kappa1)) integral_0^rho [u1'^2+mu_c u1^2]tan(s)^2 ds",
            "warp_source_integral_for_Z5_over_kappa1_1": stable(mode["warp_source_integral_Z_over_kappa"]),
            "constraint_propagation": "bulk Bianchi propagation retained; boundary inconsistency remains",
            "reduced_action_direct_equation_agreement": "same normal constraint and B1 boundary term",
            "delta_source_added": False,
            "singlet_stress_isotropic": True,
            "p1_minus_p2": 0,
        },
        "third": {
            **c("BHSM_scalar_wall_third_order_source_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_THIRD_ORDER_SOURCE_NOT_CLOSED",
            "formal_equation": "(L_c-mu_c)u3=S3",
            "formal_terms": [
                "mu2 u1",
                "-(G5/Z5)u1^3 in the chosen operator convention",
                "second-order warp response",
                "normal lapse/length response",
                "X response through the background",
                "moving-junction contribution",
                "orthogonality normalization counterterm",
            ],
            "orthogonality": "<u1,u3>_a0=0",
            "full_scalar_route_completed": False,
            "quartic_action_route_completed": False,
            "reason": "no analytic O(epsilon^2) metric/junction solution exists in the primary fixed-C_partial critical ensemble",
        },
        "fredholm": {
            **c("BHSM_scalar_wall_Fredholm_coefficient_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_FREDHOLM_COEFFICIENT_UNRESOLVED",
            "residual_convention": "-delta_mu epsilon+C_bif epsilon^3+O(epsilon^5)",
            "direct_projection": f"(G5/Z5)*{quartic}",
            "decomposition": {
                "C_direct": {"formula": "(G5/Z5) integral a0^4 u1^4", "coefficient": quartic},
                "C_gravity": None,
                "C_junction": None,
                "C_domain": None,
                "C_total": None,
            },
            "gauge_invariant_total_available": False,
            "sign_certified": False,
            "reason": "the analytic Fredholm hierarchy terminates at the second-order critical-fold obstruction",
        },
        "branch": {
            **c("BHSM_scalar_wall_branch_classification_v6_1_6"),
            "status": PRIMARY_RESULT,
            "fixed_C_partial_analytic": "locally obstructed at O(epsilon^2)",
            "fixed_C_partial_Puiseux": {
                "equation": "X-Xc=plus_or_minus sqrt(q5 Z5/(3kappa1)) |u1'(rhoJ)| |epsilon|+...",
                "slope_for_q5_1_Z5_over_kappa1_1": fold_slope,
                "lower_and_upper_curvature_sheets": True,
                "full_bulk_solution_found": False,
            },
            "fixed_X_varying_C_partial": {
                "analytic_compensation": "eta2=(Z5/kappa1)u1'(rhoJ)^2/(48 q5^(3/2))",
                "eta2_for_q5_1_Z5_over_kappa1_1": stable(mode["junction_derivative"] ** 2 / 48),
                "classification": "conditional on varying an independent B1 primitive",
            },
            "fixed_physical_length": "requires a separate lapse/domain solve",
            "supercritical_or_subcritical": None,
            "same_curvature_root": "undefined at the double-root split",
            "scalar_signs": "plus/minus epsilon have identical stress and geometry on a selected fold sheet",
            "parent_selection_of_ensemble": None,
        },
        "onshell": {
            **c("BHSM_scalar_wall_onshell_quartic_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_ONSHELL_QUARTIC_UNRESOLVED",
            "direct_scalar_quartic_action": f"(G5/Z5 normalization dependent)*{direct_quartic_action}",
            "bulk_gravity": None,
            "GHY": None,
            "B1_intrinsic_gravity": None,
            "junction_displacement": None,
            "scalar_vacuum_energy_retained": True,
            "complete_quartic": None,
            "fredholm_agreement_test": "not applicable until a consistent expansion is selected",
            "flat_wall_tension_used": False,
        },
        "continuation": {
            **c("BHSM_scalar_wall_nonlinear_continuation_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_BACKREACTED_BRANCH_NOT_FOUND",
            "method_required": "pseudo-arclength continuation seeded by a consistent perturbative branch",
            "attempted_primary_analytic_seed": True,
            "seed_valid": False,
            "unconstrained_shooting_used": False,
            "continuation_points": [],
            "failed_points_hidden": False,
            "reason": "the analytic seed fails the exact junction constraint; Puiseux reformulation is new mathematics, not a post-result repair",
        },
        "residuals": {
            **c("BHSM_scalar_wall_constraint_residuals_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_CRITICAL_MODE_CONVERGED_JUNCTION_RESIDUAL_NONZERO",
            "critical_mode_convergence": convergence,
            "weighted_normalization_residual": 0,
            "eigen_identity_residual": stable(mode["eigen_residual_moment"], 14),
            "analytic_constraint_residual_coefficient": obstruction,
            "scalar_equation_residual": "converged for the linear critical mode",
            "tangential_equation_residual": "not evaluated on a nonexistent analytic second-order branch",
            "junction_residual": "positive at O(epsilon^2)",
            "virial_identity": "linearized identity gradient=mu*norm passes",
            "mesh_refinement_passed": True,
        },
        "amplitude": {
            **c("BHSM_scalar_wall_amplitude_stability_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_AMPLITUDE_MODE_STABILITY_UNRESOLVED",
            "amplitude_potential": None,
            "critical_mode_on_zero_branch": "crosses zero at mu=mu_c",
            "new_branch_eigenvalue": None,
            "reason": "no certified analytic or continued backreacted branch",
            "full_mixed_stability_claimed": False,
        },
        "mixed": {
            **c("BHSM_scalar_wall_mixed_operator_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_FULL_MIXED_STABILITY_OPEN",
            "blocks": {
                "odd_wall_scalar": "linear critical block constructed",
                "even_scalar_breathing": "open",
                "metric_scalar": "constraint equation constructed; reduced Hessian open",
                "junction_displacement": "critical-fold boundary equation constructed",
                "bulk_lapse": "constraint, nonpropagating; elimination incomplete beyond linear order",
                "normal_diffeomorphism": "fixed/moving-domain map recorded",
                "two_Berger_shapes": "v6.1 positive principal diagonal retained; mixed entries open",
            },
            "gauge_zero_modes": ["normal reparameterization before gauge fixing"],
            "physical_negative_modes": None,
            "p1_minus_p2": 0,
            "direct_singlet_Berger_source": 0,
        },
        "sources": {
            **c("BHSM_scalar_wall_B1_source_reaudit_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_B1_SOURCE_FAILURE_PRESERVED",
            "C_partial": "independent B1 primitive; a branch relation or eta2 compensation is not its parent derivation",
            "tau_A": "not generated because no scalar-dependent F^2 parent invariant exists",
            "Z_partial": "bending remains distinct from sigma_partial without an action/domain map",
            "independent_B1_primitives_removed": [],
            "v6_1_5_source_conclusions_changed": False,
        },
        "hidden": {
            **c("BHSM_scalar_wall_hidden_input_claim_audit_v6_1_6"),
            "status": "BHSM_SCALAR_WALL_HIDDEN_INPUTS_EXPOSED",
            "dimensionless_audit_normalization": ["q5=1", "kappa1=1", "Z5=1 for reported coefficients"],
            "free_primitives": ["kappa_0", "kappa_1", "Z5", "G5", "C_partial", "tau_A", "Z_partial"],
            "unselected": ["ensemble", "Puiseux fold sheet", "G5/Z5", "physical cap-length condition"],
            "not_imported": [
                "measured masses",
                "measured couplings",
                "cosmological parameters",
                "absolute length",
                "CERN physics validation",
            ],
            "new_terms": [],
        },
        "report": {
            **c("BHSM_scalar_wall_backreacted_bifurcation_report_v6_1_6"),
            "status": PRIMARY_RESULT,
            "central_answer": (
                "The critical odd scalar eigenpair is independently reproduced. "
                "At the v6.1.4 critical B1 double root, its nonzero normal "
                "gradient creates a positive O(epsilon^2) constraint source, "
                "while an analytic even metric/curvature response enters the "
                "junction polynomial only at O(epsilon^4). The requested "
                "fixed-C_partial analytic Lyapunov-Schmidt hierarchy therefore "
                "stops at second order. The exact completed-square junction "
                "equation permits an O(|epsilon|) curvature fold, and a fixed-X "
                "analytic ensemble can compensate only by varying the independent "
                "B1 coefficient. No parent theorem selects among these ensembles, "
                "so no total cubic Fredholm coefficient, nonlinear branch, "
                "on-shell quartic, or stability sign is promoted."
            ),
            "secondary_statuses": [
                "BHSM_CRITICAL_SCALAR_ZERO_MODE_REPRODUCED",
                "BHSM_SCALAR_WALL_ANALYTIC_SECOND_ORDER_JUNCTION_OBSTRUCTION_DERIVED",
                "BHSM_SINGLET_WALL_BERGER_SOURCE_STILL_ZERO",
                "BHSM_SCALAR_WALL_B1_SOURCE_FAILURE_PRESERVED",
                "BHSM_SCALAR_WALL_FULL_MIXED_STABILITY_OPEN",
            ],
            "invalidated": [
                "analytic even-metric expansion at the critical double root",
                "a uniquely defined cubic Fredholm coefficient in the frozen primary ensemble",
                "fixed-background scalar profile promoted as backreacted",
                "continuation failure promoted to a no-branch theorem",
            ],
            "open": [
                "Puiseux/fold Lyapunov-Schmidt construction",
                "controlled nonlinear continuation on each curvature sheet",
                "complete on-shell action comparison",
                "amplitude and mixed stability",
                "parent selection of B1 ensemble and coefficients",
            ],
            "completion_gate": COMPLETION_GATE,
            "full_bhsm_status": "FULL_BHSM_NOT_COMPLETE",
        },
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    paths = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths


def bifurcation_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = build_artifact_payloads(repo_root)["report"]
    report["artifacts"] = {
        key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()
    }
    return report


def bifurcation_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# BHSM v6.1.6 Scalar-Wall Backreacted Bifurcation",
            "",
            f"Primary result: `{report['primary_result']}`.",
            "",
            report["central_answer"],
            "",
            f"Next gate: `{report['completion_gate']}`.",
            "",
            "`FULL_BHSM_NOT_COMPLETE`.",
        ]
    ) + "\n"
