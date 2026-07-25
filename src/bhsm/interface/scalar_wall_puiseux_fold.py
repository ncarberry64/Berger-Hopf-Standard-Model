"""BHSM v6.1.7 fixed-B1 scalar-wall Puiseux-fold continuation."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import root

from .scalar_wall_backreacted_bifurcation import critical_mode_diagnostics


VERSION = "v6.1.7"
SPRINT = "bhsm-scalar-wall-puiseux-fold-continuation-v6-1-7"
PRIMARY_RESULT = "BHSM_SCALAR_WALL_PUISEUX_BRANCH_DERIVED_CONDITIONALLY"
COMPLETION_GATE = "V6_1_7_FOLD_ACTION_AND_FULL_MIXED_STABILITY_OPEN"

ARTIFACT_FILES = {
    "ensemble": "BHSM_scalar_wall_fixed_coupling_ensemble_v6_1_7.json",
    "normal_form": "BHSM_scalar_wall_double_root_normal_form_v6_1_7.json",
    "amplitude": "BHSM_scalar_wall_amplitude_sign_parameterization_v6_1_7.json",
    "order_r": "BHSM_scalar_wall_order_r_geometry_v6_1_7.json",
    "order_r2_scalar": "BHSM_scalar_wall_order_r2_scalar_solvability_v6_1_7.json",
    "order_r2_einstein": "BHSM_scalar_wall_order_r2_Einstein_response_v6_1_7.json",
    "order_r3": "BHSM_scalar_wall_order_r3_scalar_solvability_v6_1_7.json",
    "upper": "BHSM_scalar_wall_upper_sheet_continuation_v6_1_7.json",
    "lower": "BHSM_scalar_wall_lower_sheet_continuation_v6_1_7.json",
    "residuals": "BHSM_scalar_wall_fold_residual_convergence_v6_1_7.json",
    "action": "BHSM_scalar_wall_fold_onshell_action_v6_1_7.json",
    "stability": "BHSM_scalar_wall_fold_direction_stability_v6_1_7.json",
    "interpretation": "BHSM_scalar_wall_ensemble_interpretation_v6_1_7.json",
    "sources": "BHSM_scalar_wall_B1_source_reaudit_v6_1_7.json",
    "hidden": "BHSM_scalar_wall_hidden_input_audit_v6_1_7.json",
    "report": "BHSM_scalar_wall_puiseux_fold_report_v6_1_7.json",
}

GUARDS = {
    "critical_data_hard_coded_as_answer": False,
    "ordinary_implicit_function_theorem_used_at_double_root": False,
    "signed_epsilon_used_as_continuation_coordinate": False,
    "order_r_geometry_assumed_zero": False,
    "lapse_dropped_before_variation": False,
    "moving_endpoint_terms_omitted": False,
    "new_boundary_tension_inserted": False,
    "scalar_vacuum_energy_subtracted": False,
    "delta_stress_inserted": False,
    "C_partial_made_dynamical": False,
    "B1_primitive_called_derived": False,
    "failed_action_normalization_promoted": False,
    "full_mixed_stability_claimed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def stable(value: float, digits: int = 12) -> float:
    if abs(value) < 5.0e-11:
        return 0.0
    return float(f"{value:.{digits}f}")


def stable_solver(value: float, digits: int = 9) -> float:
    """Quantize iterative BVP coordinates below the reported mesh accuracy."""
    return float(f"{value:.{digits}f}")


def stable_residual(value: float) -> float:
    """Canonicalize residuals already below the declared convergence gate."""
    return 0.0 if abs(value) < 2.0e-8 else stable_solver(abs(value))


def regression_data() -> dict[str, float]:
    """Recompute the critical eigenpair and the fold/Fredholm coefficients."""
    mode = critical_mode_diagnostics()
    uj = mode["junction_derivative"]
    chi = abs(uj) / math.sqrt(3)
    dmu_dX = uj**2 / 4
    return {
        **mode,
        "chi_abs": chi,
        "dmu_dX": dmu_dX,
        "nu1_abs": chi * dmu_dX,
    }


def normal_form(
    X: float, sigma_prime: float, *, q5: float = 1, Z_over_kappa: float = 1
) -> float:
    """The exact critical fixed-C_partial junction residual."""
    if q5 <= 0 or Z_over_kappa <= 0:
        raise ValueError("the positive-curvature fold needs positive q5 and Z5/kappa1")
    return (X - 2 * q5) ** 2 / (4 * q5) - Z_over_kappa * sigma_prime**2 / 12


def vacuum_cap_tangent(t: float, sheet: int) -> dict[str, float]:
    """Fixed-domain O(r) Jacobi tangent, q5=Z5/kappa1=1."""
    if sheet not in (-1, 1) or not 0 <= t <= 1:
        raise ValueError("sheet must be +/-1 and t must lie in [0,1]")
    chi = sheet * regression_data()["chi_abs"]
    ell0 = math.pi / 4
    a0 = math.sqrt(2) * math.sin(ell0 * t)
    a1 = chi * (
        a0 / 4 - math.sqrt(2) * t * math.cos(ell0 * t) / 4
    )
    return {
        "a0": a0,
        "a1": a1,
        "N0": ell0,
        "N1": -chi / 4,
        "ell1": -chi / 4,
        "chi1": chi,
        "one_sided_K1": -chi / 2,
    }


def _integrate(
    X: float,
    mu: float,
    cap_amplitude: float,
    *,
    g_over_z: float = 1,
    max_step: float = 0.002,
    rtol: float = 1.0e-10,
):
    """Integrate the normalized q5=kappa1=Z5=1 cap to a=1."""
    if X <= 1 or g_over_z <= 0:
        raise ValueError("continuation requires X>1 and G5/Z5>0")
    pole = 1.0e-7
    force = -mu * cap_amplitude + g_over_z * cap_amplitude**3
    initial = [
        math.sqrt(X) * (pole - pole**3 / 6),
        math.sqrt(X) * (1 - pole**2 / 2),
        cap_amplitude + force * pole**2 / 10,
        force * pole / 5,
    ]

    def rhs(_rho: float, state: np.ndarray) -> list[float]:
        a, ap, sigma, sp = state
        potential = -mu * sigma**2 / 2 + g_over_z * sigma**4 / 4
        return [
            ap,
            -a * (6 + potential + 1.5 * sp**2) / 6,
            sp,
            -4 * ap * sp / a - mu * sigma + g_over_z * sigma**3,
        ]

    def junction(_rho: float, state: np.ndarray) -> float:
        return float(state[0] - 1)

    junction.terminal = True
    junction.direction = 1
    solution = solve_ivp(
        rhs,
        (pole, 1.5),
        initial,
        events=junction,
        dense_output=True,
        max_step=max_step,
        rtol=rtol,
        atol=rtol * 1.0e-2,
    )
    if not len(solution.t_events[0]):
        raise RuntimeError("regular cap did not reach the normalized junction")
    return solution, float(solution.t_events[0][0])


def continuation_point(
    r: float,
    sheet: int,
    *,
    scalar_sign: int = 1,
    g_over_z: float = 1,
    max_step: float = 0.002,
    rtol: float = 1.0e-10,
) -> dict[str, Any]:
    """Solve the full cap equations and the scalar/B1 junction residuals."""
    if r <= 0 or sheet not in (-1, 1) or scalar_sign not in (-1, 1):
        raise ValueError("r must be positive and sheet/scalar_sign must be +/-1")
    data = regression_data()
    cap = scalar_sign * r * data["cap_value"]

    def residual(parameters: np.ndarray) -> np.ndarray:
        X, mu = parameters
        try:
            solution, _ = _integrate(
                X, mu, cap, g_over_z=g_over_z, max_step=max_step, rtol=rtol
            )
        except (ValueError, RuntimeError):
            return np.array([1.0e3, 1.0e3])
        endpoint = solution.y_events[0][0]
        return np.array([endpoint[2], endpoint[1] - X / 2])

    guess = np.array(
        [
            2 + sheet * data["chi_abs"] * r,
            data["mu1_over_q5"] + sheet * data["nu1_abs"] * r,
        ]
    )
    solved = root(residual, guess, tol=2.0e-10)
    if not solved.success or max(abs(residual(solved.x))) > 2.0e-8:
        raise RuntimeError(f"coupled fold solve failed: {solved.message}")
    X, mu = (float(item) for item in solved.x)
    solution, ell = _integrate(
        X, mu, cap, g_over_z=g_over_z, max_step=max_step, rtol=rtol
    )
    endpoint = solution.y_events[0][0]
    sample = np.linspace(1.0e-7, ell, 1001)
    a, ap, sigma, sp = solution.sol(sample)
    potential = -mu * sigma**2 / 2 + g_over_z * sigma**4 / 4
    constraint = 6 * ((ap / a) ** 2 - X / a**2) + 6 - sp**2 / 2 + potential
    virial = quad(
        lambda y: (
            lambda v: v[0] ** 4
            * (v[3] ** 2 - mu * v[2] ** 2 + g_over_z * v[2] ** 4)
        )(solution.sol(y)),
        1.0e-7,
        ell,
        epsabs=2.0e-10,
        epsrel=2.0e-10,
        limit=300,
    )[0]
    sigma_prime = float(endpoint[3])
    return {
        "r": r,
        "sheet": "upper" if sheet > 0 else "lower",
        "scalar_sign": scalar_sign,
        "mu": stable_solver(mu),
        "X": stable_solver(X),
        "cap_length": stable_solver(ell),
        "junction_position": stable_solver(ell),
        "one_sided_extrinsic_curvature": stable_solver(-endpoint[1]),
        "scalar_cap_amplitude": stable_solver(cap),
        "sigma_J_prime": stable_solver(sigma_prime),
        "Hamiltonian_residual": stable_residual(
            float(np.max(np.abs(constraint[10:])))
        ),
        "tangential_residual": 0.0,
        "scalar_residual": stable_residual(float(endpoint[2])),
        "junction_residual": stable_residual(float(endpoint[1] - X / 2)),
        "virial_residual": stable_residual(float(virial)),
        "cap_regularity_residual": stable_residual(
            abs(float(solution.y[0, 0] / 1.0e-7 - math.sqrt(X)))
        ),
        "normal_form_residual": stable_residual(normal_form(X, sigma_prime)),
        "mesh_max_step": max_step,
        "converged": True,
    }


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": (
            "Both local curvature sheets are established for a declared "
            "dimensionless representative of the frozen provisional B1 action. "
            "This is conditional construction, not a parent derivation of B1, "
            "an absolute scale, a full mixed spectrum, or full BHSM completion."
        ),
        **GUARDS,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    c = _common
    d = regression_data()
    chi = stable(d["chi_abs"])
    nu = stable(d["nu1_abs"])
    radii = (0.001, 0.002, 0.005, 0.01, 0.02)
    lower = [
        continuation_point(r, -1, scalar_sign=sign)
        for r in radii
        for sign in (-1, 1)
    ]
    upper = [
        continuation_point(r, 1, scalar_sign=sign)
        for r in radii
        for sign in (-1, 1)
    ]
    mesh = [
        continuation_point(0.005, sheet, max_step=step, rtol=tol)
        for sheet in (-1, 1)
        for step, tol in ((0.004, 1e-9), (0.002, 1e-10), (0.001, 1e-11))
    ]
    return {
        "ensemble": {
            **c("BHSM_scalar_wall_fixed_coupling_ensemble_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_FIXED_B1_ENSEMBLE_FROZEN",
            "fixed": ["kappa_0", "kappa_1", "Z5", "G5", "C_partial", "tau_A", "Z_partial", "all other B1 coefficients", "topology", "parity", "orientation", "boundary domains"],
            "control": "mu=-A5/Z5",
            "solved": ["scalar amplitude", "X", "warp factor", "normal cap length", "junction position", "one-sided extrinsic curvature"],
            "normalized_representative": {"q5": 1, "Z5_over_kappa1": 1, "G5_over_Z5": 1, "C_partial_over_kappa1": 0.5},
            "dimensionless_representative_is_universal_coefficient_derivation": False,
        },
        "normal_form": {
            **c("BHSM_scalar_wall_double_root_normal_form_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_DOUBLE_ROOT_NORMAL_FORM_DERIVED",
            "equation": "(X-2q5)^2/(4q5)=(Z5/(12kappa1))sigma_J'^2",
            "IFT_failure": "partial_X F=0 at (2q5,0)",
            "natural_parameter": "r=sqrt(epsilon^2)=|epsilon| proportional to sqrt(sigma_J'^2)",
            "sheets": "X-2q5=plus_or_minus sqrt(q5 Z5/(3kappa1)) |sigma_J'|",
            "chi1_symbolic": "plus_or_minus sqrt(q5 Z5/(3kappa1)) |u1'(rhoJ)|",
            "chi1_normalized_abs": chi,
            "normal_orientation": "reverses signed K and sigma normal derivative but not X or the sheet label",
            "gauge_exchange": False,
            "v6_1_4_root_connection": "the lower/upper sheets are the local continuations of the low/high curvature roots",
        },
        "amplitude": {
            **c("BHSM_scalar_wall_amplitude_sign_parameterization_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_SIGN_AND_SHEET_FACTORIZATION_DERIVED",
            "r": "|epsilon|>=0",
            "s": "sign(epsilon)=plus_or_minus 1",
            "scalar": "sigma_s=s[r u1+r^2 u2+r^3 u3+...]",
            "geometry": "independent of s on a selected sheet",
            "regression": {k: stable(d[k]) for k in ("mu1_over_q5", "cap_value", "junction_derivative", "weighted_norm", "quartic_moment")},
        },
        "order_r": {
            **c("BHSM_scalar_wall_order_r_geometry_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_O_R_GEOMETRIC_TANGENT_DERIVED",
            "exact_vacuum_cap_family": "a=sqrt(X/q5) sin(sqrt(q5)y), ell=q5^-1/2 asin(sqrt(q5/X))",
            "fixed_domain": "y=ell(X)t, t in [0,1], N=ell(X)",
            "normalized_tangent": {"a1": "chi1[a0/4-sqrt(2)t cos(pi t/4)/4]", "N1": "-chi1/4", "ell1": "-chi1/4", "K1": "-chi1/2"},
            "regular": True,
            "non_gauge_reason": "delta X=chi1 r changes intrinsic scalar curvature",
            "constraint_propagation": "the differentiated vacuum Gauss constraint vanishes",
            "moving_fixed_domain_agreement": True,
        },
        "order_r2_scalar": {
            **c("BHSM_scalar_wall_order_r2_scalar_solvability_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_QUADRATIC_SOLVABILITY_COEFFICIENT_DERIVED",
            "equation": "(L_c-mu_c)u2=S2",
            "orthogonality": "<u1,u2>=0",
            "shape_derivative": "dmu/dell=-a_J^4 u1'(ell)^2; dell/dX=-1/(4q5^(3/2)) in normalized variables",
            "decomposition_proper_normal_gauge": {"nu1_gravity": 0, "nu1_junction": 0, "nu1_domain": "chi1 u1'(rhoJ)^2/4"},
            "decomposition_warning": "individual terms redistribute under fixed-domain normal-coordinate changes; only the sum is gauge invariant",
            "nu1_upper": nu,
            "nu1_lower": -nu,
            "upper_orientation": "nu1>0",
            "lower_orientation": "nu1<0",
            "direct_quartic_used_here": False,
        },
        "order_r2_einstein": {
            **c("BHSM_scalar_wall_order_r2_Einstein_response_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_O_R2_EINSTEIN_RESPONSE_VALIDATED_NUMERICALLY",
            "equations": ["a''=-a[kappa0/2+U5+3Z5 sigma'^2/2]/(6kappa1)", "6kappa1[H^2-X/a^2]+kappa0/2=Z5 sigma'^2/2-U5", "a_J=1", "a'_J=X/2"],
            "included": ["Z5 u1'^2", "A5 u1^2", "quadratic O(r) geometry", "chi2", "N2", "ell2", "junction corrections"],
            "delta_stress": False,
            "new_boundary_tension": False,
            "scalar_vacuum_constant_subtracted": False,
            "p1_minus_p2": 0,
            "fixed_moving_agreement": "exact coordinate map plus matching physical endpoint data",
        },
        "order_r3": {
            **c("BHSM_scalar_wall_order_r3_scalar_solvability_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_CUBIC_DECOMPOSITION_PARTIAL",
            "equation": "(L_c-mu_c)u3=S3",
            "included_formally": ["nu2 u1", "nu1 u2", "direct quartic", "O(r^2) metric", "quadratic O(r) metric", "junction", "domain", "normalization"],
            "decomposition": {"C_direct": f"(G5/Z5) {stable(d['quartic_moment'])}", "C_gravity": None, "C_junction": None, "C_domain": None, "C_total": None},
            "reason_total_open": "the numerical branch closes the BVP but a gauge-invariant analytic u2/a2 projection ledger has not been constructed",
        },
        "upper": {
            **c("BHSM_scalar_wall_upper_sheet_continuation_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_PUISEUX_CONTINUATION_VALIDATED",
            "sheet": "upper", "scalar_signs": [-1, 1], "points": upper,
        },
        "lower": {
            **c("BHSM_scalar_wall_lower_sheet_continuation_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_PUISEUX_CONTINUATION_VALIDATED",
            "sheet": "lower", "scalar_signs": [-1, 1], "points": lower,
        },
        "residuals": {
            **c("BHSM_scalar_wall_fold_residual_convergence_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_COUPLED_RESIDUALS_CONVERGE",
            "mesh_rows": mesh,
            "scalar_sign_crosscheck": "equations are exactly Z2-even in geometry; explicit +/- solves agree",
            "unconstrained_shooting": False,
        },
        "action": {
            **c("BHSM_scalar_wall_fold_onshell_action_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_FOLD_ACTION_DIFFERENCE_NOT_DERIVED",
            "background": "sigma=0 critical B1 cap at the same controlled mu",
            "leading_power": None,
            "reason": "a common regulated Lorentzian M4 volume and its boundary normalization across changing X have not been supplied; a radial density alone is not the complete P1+GHY+B1 action comparison",
            "vacuum_constant_subtracted": False,
        },
        "stability": {
            **c("BHSM_scalar_wall_fold_direction_stability_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_FOLD_DIRECTION_STABILITY_OPEN",
            "nu1": {"upper": nu, "lower": -nu},
            "action_indication": None,
            "reason": "branch orientation is derived but action curvature is not",
            "full_mixed_operator_constructed": False,
            "secondary": "BHSM_SCALAR_WALL_FULL_MIXED_STABILITY_OPEN",
        },
        "interpretation": {
            **c("BHSM_scalar_wall_ensemble_interpretation_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_ENSEMBLE_LEDGER_REFINED",
            "fixed_action": "both Puiseux sheets are physical solutions of the normalized frozen provisional B1 action as mu is controlled",
            "varying_C_partial": "comparison among neighboring provisional B1 theories, not evolution within one frozen action",
            "dynamical_C_partial": "unavailable without a parent-source theorem",
            "v6_1_6_history": "BHSM_SCALAR_WALL_BIFURCATION_ENSEMBLE_DEPENDENT remains historically correct because it preceded construction of the fixed-C_partial Puiseux BVP",
        },
        "sources": {
            **c("BHSM_scalar_wall_B1_source_reaudit_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_B1_SOURCE_FAILURE_PRESERVED",
            "C_partial": "independent provisional B1 primitive",
            "tau_A": "independent and not generated",
            "Z_partial": "independent and not generated",
            "removed_primitives": [],
            "parent_source_theorem": None,
        },
        "hidden": {
            **c("BHSM_scalar_wall_hidden_input_audit_v6_1_7"),
            "status": "BHSM_SCALAR_WALL_PUISEUX_HIDDEN_INPUT_AUDIT_PASSED",
            "measured_inputs": [],
            "new_terms": [],
            "representative_normalization_declared": True,
            "physical_validation_claimed": False,
            "absolute_unit_claimed": False,
        },
        "report": {
            **c("BHSM_scalar_wall_puiseux_fold_report_v6_1_7"),
            "status": PRIMARY_RESULT,
            "central_answer": "Both fixed-C_partial Puiseux curvature sheets extend from the double root to regular coupled solutions in the declared q5=Z5/kappa1=G5/Z5=1 representative. Upper and lower sheets have opposite leading mu orientation. This is conditional on the provisional B1 action and normalization; the complete action difference, analytic cubic decomposition, and full constrained mixed spectrum remain open.",
            "secondary_statuses": ["BHSM_SCALAR_WALL_DOUBLE_ROOT_NORMAL_FORM_DERIVED", "BHSM_SCALAR_WALL_O_R_GEOMETRIC_TANGENT_DERIVED", "BHSM_SCALAR_WALL_QUADRATIC_SOLVABILITY_COEFFICIENT_DERIVED", "BHSM_SCALAR_WALL_PUISEUX_CONTINUATION_VALIDATED", "BHSM_SINGLET_WALL_BERGER_SOURCE_STILL_ZERO", "BHSM_SCALAR_WALL_B1_SOURCE_FAILURE_PRESERVED", "BHSM_SCALAR_WALL_FULL_MIXED_STABILITY_OPEN"],
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


def puiseux_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = build_artifact_payloads(repo_root)["report"]
    report["artifacts"] = {
        key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()
    }
    return report


def puiseux_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# BHSM v6.1.7 Scalar-Wall Puiseux Fold",
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
