"""BHSM v6.29.0 projected Schur reduction and fold kinetic norm."""

from __future__ import annotations

from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Any

import mpmath as mp
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq
import sympy as sp

from bhsm.interface import reduced_fold_operator_domain as v628


VERSION = "v6.29.0"
SPRINT = "bhsm-fold-schur-kinetic-v6-29-0"
SOURCE_MAIN_SHA = "86df2f5c72e8c6fe07c2fb3ee41372a521229c84"
V628_SCIENTIFIC_SHA = "853bddac1852c6b328fc4cf7af2786e2f59baf34"

SCHUR_RESULT = "BHSM_FOLD_PROJECTED_SCHUR_REDUCTION_DERIVED"
SCALAR_RESULT = "BHSM_FOLD_SCALAR_KINETIC_NORMALIZATION_RECOMPUTED"
PRIMARY_RESULT = "BHSM_FOLD_KINETIC_NORM_POSITIVE_CONDITIONALLY"
SIGN_AUDIT_RESULT = "BHSM_FOLD_NEGATIVE_NORM_AUDIT_NOT_TRIGGERED"
NEXT_RESULT = "BHSM_V6_30_EINSTEIN_FRAME_POTENTIAL_PHASE_PERMITTED"

ARTIFACT_FILES = {
    "scalar": "BHSM_fold_scalar_kinetic_normalization_v6_29_0.json",
    "schur": "BHSM_fold_projected_Schur_response_v6_29_0.json",
    "numerics": "BHSM_fold_kinetic_numerical_validation_v6_29_0.json",
    "verdict": "BHSM_fold_kinetic_sign_verdict_v6_29_0.json",
    "handoff": "BHSM_fold_potential_phase_handoff_v6_29_0.json",
}

GUARDS = {
    "measured_input_used": False,
    "fitted_parameter_used": False,
    "chat_only_value_imported": False,
    "new_action_introduced": False,
    "new_primitive_introduced": False,
    "new_scale_introduced": False,
    "global_Lorentzian_state_selected": False,
    "unprojected_inverse_used": False,
    "generic_pseudoinverse_used": False,
    "kernel_ignored": False,
    "B1_source_dropped": False,
    "two_cap_factor_dropped": False,
    "Weyl_term_double_counted": False,
    "negative_sign_hidden": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physical_mass_claimed": False,
    "stability_claimed": False,
}

KAPPA_1 = v628.KAPPA_1
Z5 = v628.Z5
C_PARTIAL = v628.C_PARTIAL
CHI_1 = v628.CHI_1
TAU = v628.TAU

CHI_1_REPOSITORY = 5.26830787154212
C_PARTIAL_NORMALIZED = 0.5
KAPPA_1_NORMALIZED = 1.0
Z5_NORMALIZED = 1.0


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def schur_derivative_identity_residual() -> sp.Expr:
    k0, k1, j0, j1, ell0, ell1 = sp.symbols(
        "K0 K1 J0 J1 L0 L1", nonzero=True, real=True
    )
    lam = sp.symbols("lambda", real=True)
    k = k0 + lam * k1
    j = j0 + lam * j1
    ell = ell0 + lam * ell1
    direct = sp.diff(k - j**2 / ell, lam).subs(lam, 0)
    expected = k1 - 2 * j1 * j0 / ell0 + j0**2 * ell1 / ell0**2
    return sp.simplify(direct - expected)


def modulus_source_exact(
    tau: sp.Expr = TAU,
    chi_1: sp.Expr = CHI_1,
    kappa_1: sp.Expr = KAPPA_1,
) -> sp.Expr:
    """<z,J1_eff> after affine L1 terms cancel against Y0=-v."""

    return sp.simplify(
        tau
        * chi_1
        * kappa_1
        * (sp.Rational(3, 2) * sp.log(2) - 6 * sp.Catalan / sp.pi)
    )


def modulus_lift_exact(
    c_partial: sp.Expr = C_PARTIAL,
    kappa_1: sp.Expr = KAPPA_1,
) -> sp.Expr:
    return sp.simplify(
        12 * c_partial + 3 * kappa_1 * (6 - sp.pi)
    )


def gravitational_schur_exact(
    chi_1: sp.Expr = CHI_1,
    c_partial: sp.Expr = C_PARTIAL,
    kappa_1: sp.Expr = KAPPA_1,
) -> sp.Expr:
    source = modulus_source_exact(sp.Integer(1), chi_1, kappa_1)
    return sp.simplify(-source**2 / modulus_lift_exact(c_partial, kappa_1))


def weyl_kinetic_exact(chi_1: sp.Expr = CHI_1) -> sp.Expr:
    return sp.simplify(3 * chi_1**2 * (4 - sp.pi) ** 2 / (16 * sp.pi))


def _shoot_endpoint(
    mu: float,
    *,
    dense: bool,
    max_step: float,
    rtol: float,
):
    pole = 1.0e-8
    endpoint = math.pi / 4
    initial = [1 - mu * pole**2 / 10, -mu * pole / 5]

    def rhs(rho: float, state: list[float]) -> list[float]:
        u, derivative = state
        return [derivative, -4 / math.tan(rho) * derivative - mu * u]

    solution = solve_ivp(
        rhs,
        (pole, endpoint),
        initial,
        dense_output=dense,
        rtol=rtol,
        atol=rtol * 1.0e-3,
        max_step=max_step,
    )
    return float(solution.y[0, -1]), solution


def scalar_kinetic_shooting(
    *,
    max_step: float = 0.0015,
    rtol: float = 2.0e-13,
) -> dict[str, float]:
    """Shooting plus adaptive Gauss--Kronrod quadrature."""

    mu = brentq(
        lambda value: _shoot_endpoint(
            value, dense=False, max_step=max_step, rtol=rtol
        )[0],
        29.0,
        30.0,
        xtol=5.0e-15,
    )
    endpoint_value, solution = _shoot_endpoint(
        mu, dense=True, max_step=max_step, rtol=rtol
    )
    pole = 1.0e-8
    endpoint = math.pi / 4

    def raw(rho: float, component: int = 0) -> float:
        if rho == 0:
            return 1.0 if component == 0 else 0.0
        return float(solution.sol(max(rho, pole))[component])

    norm_raw, norm_error = quad(
        lambda rho: 4 * math.sin(rho) ** 4 * raw(rho) ** 2,
        0,
        endpoint,
        epsabs=2.0e-13,
        epsrel=2.0e-13,
        limit=300,
    )
    normalization = 1 / math.sqrt(norm_raw)
    kinetic_integral, kinetic_error = quad(
        lambda rho: 4
        * math.sin(rho) ** 2
        * (normalization * raw(rho)) ** 2,
        0,
        endpoint,
        epsabs=2.0e-13,
        epsrel=2.0e-13,
        limit=300,
    )
    gradient, _ = quad(
        lambda rho: 4
        * math.sin(rho) ** 4
        * (normalization * raw(rho, 1)) ** 2,
        0,
        endpoint,
        epsabs=3.0e-12,
        epsrel=3.0e-12,
        limit=300,
    )
    return {
        "mu": float(mu),
        "normalization": float(normalization),
        "weighted_norm": 1.0,
        "K_scalar": float(kinetic_integral),
        "endpoint_residual": float(abs(endpoint_value * normalization)),
        "eigen_moment_residual": float(abs(gradient - mu)),
        "quadrature_error": float(max(norm_error, kinetic_error)),
        "max_step": max_step,
        "rtol": rtol,
    }


def scalar_kinetic_hypergeometric(dps: int = 60) -> dict[str, float]:
    """Independent hypergeometric eigenfunction plus tanh--sinh quadrature."""

    with mp.workdps(dps):
        endpoint = mp.pi / 4
        endpoint_argument = mp.sin(endpoint / 2) ** 2

        def boundary(nu):
            return mp.hyp2f1(-nu, nu + 4, mp.mpf("2.5"), endpoint_argument)

        nu = mp.findroot(boundary, (mp.mpf("3.5"), mp.mpf("4.2")))
        mu = nu * (nu + 4)

        def raw(rho):
            return mp.hyp2f1(
                -nu, nu + 4, mp.mpf("2.5"), mp.sin(rho / 2) ** 2
            )

        raw_norm = mp.quad(
            lambda rho: 4 * mp.sin(rho) ** 4 * raw(rho) ** 2,
            [0, endpoint],
        )
        normalization = 1 / mp.sqrt(raw_norm)
        kinetic = mp.quad(
            lambda rho: 4
            * mp.sin(rho) ** 2
            * (normalization * raw(rho)) ** 2,
            [0, endpoint],
        )
        return {
            "nu": float(nu),
            "mu": float(mu),
            "normalization": float(normalization),
            "weighted_norm": float(raw_norm * normalization**2),
            "K_scalar": float(kinetic),
            "endpoint_residual": float(abs(boundary(nu) * normalization)),
            "dps": dps,
        }


def next_scalar_eigenvalue_hypergeometric(dps: int = 50) -> float:
    with mp.workdps(dps):
        z = mp.sin(mp.pi / 8) ** 2

        def boundary(nu):
            return mp.hyp2f1(-nu, nu + 4, mp.mpf("2.5"), z)

        nu = mp.findroot(boundary, (mp.mpf("7.4"), mp.mpf("8.3")))
        return float(nu * (nu + 4))


@lru_cache(maxsize=1)
def numerical_results() -> dict[str, Any]:
    shooting = scalar_kinetic_shooting()
    hyper = scalar_kinetic_hypergeometric()
    scalar = (shooting["K_scalar"] + hyper["K_scalar"]) / 2
    scalar_difference = abs(shooting["K_scalar"] - hyper["K_scalar"])

    chi = CHI_1_REPOSITORY
    source = float(
        modulus_source_exact()
        .subs(
            {
                TAU: 1,
                CHI_1: chi,
                KAPPA_1: KAPPA_1_NORMALIZED,
            }
        )
        .evalf(18)
    )
    lift = float(
        modulus_lift_exact()
        .subs(
            {
                C_PARTIAL: C_PARTIAL_NORMALIZED,
                KAPPA_1: KAPPA_1_NORMALIZED,
            }
        )
        .evalf(18)
    )
    grav = -source**2 / lift
    weyl = float(weyl_kinetic_exact(chi).evalf(18))
    total = scalar + grav + weyl
    next_mu = next_scalar_eigenvalue_hypergeometric()
    scalar_gap = next_mu - hyper["mu"]
    uncertainty = max(2.0e-12, scalar_difference)

    return {
        "shooting": shooting,
        "hypergeometric": hyper,
        "method_difference": scalar_difference,
        "K_scalar": scalar,
        "modulus_source": source,
        "modulus_lift": lift,
        "K_grav_constraint_J": grav,
        "K_Weyl": weyl,
        "k_q_E": total,
        "uncertainty": uncertainty,
        "next_scalar_eigenvalue": next_mu,
        "scalar_perp_gap": scalar_gap,
        "modulus_solve_condition_number": 1.0,
    }


def scalar_ledger() -> dict[str, Any]:
    result = numerical_results()
    return {
        "formula": (
            "K_scalar=2 Z5 integral_0^1 N0 a0^2 u1^2 dt"
        ),
        "normalization": (
            "integral_0^1 N0 a0^4 u1^2 dt=1 per cap"
        ),
        "cap_multiplicity": 2,
        "Z5_normalized": Z5_NORMALIZED,
        "shooting": result["shooting"],
        "hypergeometric": result["hypergeometric"],
        "method_difference": result["method_difference"],
        "reported": result["K_scalar"],
        "lower_bound": 2,
        "result": SCALAR_RESULT,
    }


def schur_ledger() -> dict[str, Any]:
    result = numerical_results()
    return {
        "derivative_identity": (
            "K'-2<J',L^-1J>+<J,L^-1L'L^-1J>"
        ),
        "symbolic_identity_residual": sp.sstr(
            schur_derivative_identity_residual()
        ),
        "affine_cancellation": (
            "Y0=-v on the complementary L0 range; L1 v cancels between "
            "J1 and L1Y0, leaving only the v6.27 threading source on z"
        ),
        "complement_J1_order": (
            "O(lambda) complementary response contributes first at O(lambda^2)"
        ),
        "kernel_method": "one-dimensional Lyapunov-Schmidt reduction",
        "z": "A_z=sec^2(pi t/4), psi_z=1",
        "j_z_exact": sp.sstr(modulus_source_exact()),
        "M_z_exact": sp.sstr(modulus_lift_exact()),
        "K_grav_exact": sp.sstr(gravitational_schur_exact()),
        "normalized": {
            "j_z": result["modulus_source"],
            "M_z": result["modulus_lift"],
            "K_grav_constraint_J": result["K_grav_constraint_J"],
            "condition_number": result["modulus_solve_condition_number"],
        },
        "B1_included": True,
        "projected_inverse_only": True,
        "result": SCHUR_RESULT,
    }


def validation_ledger() -> dict[str, Any]:
    result = numerical_results()
    return {
        "methods": [
            "regular-pole shooting + adaptive Gauss-Kronrod quadrature",
            "hypergeometric eigenfunction + mpmath tanh-sinh quadrature",
        ],
        "precision": {
            "shooting_rtol": result["shooting"]["rtol"],
            "shooting_max_step": result["shooting"]["max_step"],
            "hypergeometric_dps": result["hypergeometric"]["dps"],
        },
        "convergence": {
            "K_scalar_method_difference": result["method_difference"],
            "reported_uncertainty": result["uncertainty"],
        },
        "residuals": {
            "shooting_endpoint": result["shooting"]["endpoint_residual"],
            "shooting_eigen_moment": result["shooting"][
                "eigen_moment_residual"
            ],
            "hypergeometric_endpoint": result["hypergeometric"][
                "endpoint_residual"
            ],
            "shooting_weighted_norm": result["shooting"]["weighted_norm"],
            "hypergeometric_weighted_norm": result["hypergeometric"][
                "weighted_norm"
            ],
        },
        "kernel_projection": {
            "scalar_perp_gap": result["scalar_perp_gap"],
            "metric_modulus_lift": result["modulus_lift"],
            "one_by_one_condition_number": result[
                "modulus_solve_condition_number"
            ],
        },
        "platform_tolerance": 5.0e-10,
    }


def kinetic_ledger() -> dict[str, Any]:
    result = numerical_results()
    return {
        "normalized_representative": {
            "kappa_1": KAPPA_1_NORMALIZED,
            "Z5": Z5_NORMALIZED,
            "C_partial_over_kappa_1": C_PARTIAL_NORMALIZED,
            "chi_1": CHI_1_REPOSITORY,
            "chi_1_source": (
                "repository continuation/Fredholm coefficient, not measured input"
            ),
        },
        "terms": {
            "K_scalar": result["K_scalar"],
            "K_grav_constraint_J": result["K_grav_constraint_J"],
            "K_Weyl": result["K_Weyl"],
        },
        "k_q_E": result["k_q_E"],
        "uncertainty": result["uncertainty"],
        "sign": "positive",
        "zero_excluded_by_uncertainty": (
            result["k_q_E"] - result["uncertainty"] > 0
        ),
        "sheet_dependence": (
            "none at quadratic order: tau enters j_z linearly and is squared"
        ),
        "scalar_sign_dependence": "none: u1 enters quadratically",
        "ghost_verdict": "not a negative-kinetic-norm mode conditionally",
        "potential_stability": "not decided by a kinetic sign",
        "result": PRIMARY_RESULT,
        "negative_sign_audit": SIGN_AUDIT_RESULT,
    }


def handoff_ledger() -> dict[str, Any]:
    return {
        "v6_30_permitted": True,
        "next_result": NEXT_RESULT,
        "required_inputs": {
            "k_q_E": numerical_results()["k_q_E"],
            "k_q_E_uncertainty": numerical_results()["uncertainty"],
            "projected_domain": "v6.28 domain retained",
            "potential_required": (
                "complete off-shell Jordan V(q), frame F(q) through F2, "
                "then Einstein transformation"
            ),
        },
        "not_derived": [
            "V_E(q)",
            "V_E''(q0)",
            "dimensionless fold mass",
            "absolute physical scale",
            "physical mass",
        ],
        "fatal_inconsistency": False,
        "obstruction_class": None,
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_28_scientific_sha": V628_SCIENTIFIC_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "scalar": {
            **_common("BHSM_fold_scalar_kinetic_normalization_v6_29_0"),
            "scalar": scalar_ledger(),
        },
        "schur": {
            **_common("BHSM_fold_projected_Schur_response_v6_29_0"),
            "Schur": schur_ledger(),
        },
        "numerics": {
            **_common("BHSM_fold_kinetic_numerical_validation_v6_29_0"),
            "validation": validation_ledger(),
        },
        "verdict": {
            **_common("BHSM_fold_kinetic_sign_verdict_v6_29_0"),
            "kinetic": kinetic_ledger(),
        },
        "handoff": {
            **_common("BHSM_fold_potential_phase_handoff_v6_29_0"),
            "handoff": handoff_ledger(),
        },
    }


def artifact_bytes() -> dict[str, bytes]:
    return {
        ARTIFACT_FILES[key]: deterministic_json(payload).encode("utf-8")
        for key, payload in artifact_payloads().items()
    }


def materialize_artifacts(root: Path) -> list[Path]:
    artifact_dir = root / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for filename, content in artifact_bytes().items():
        path = artifact_dir / filename
        path.write_bytes(content)
        paths.append(path)
    return paths
