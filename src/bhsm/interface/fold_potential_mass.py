"""BHSM v6.30.0 Einstein-frame potential and fold-mass audit.

The completed v6.28 quadratic action fixes the invariant potential Hessian
at the critical fold even though the coefficientwise Jordan reconstruction
does not fix V2 and F2 separately.  The affine radial response cancels in
the projected zero-derivative Schur form, while the scalar amplitude is the
critical Jacobi zero mode.  A regular Einstein-frame field redefinition
therefore preserves a null Hessian.  The full off-shell potential remains
unavailable because the stored Puiseux curve varies an action control and
does not supply a fixed-action, fixed-regulator radial family.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp

from bhsm.interface import fold_einstein_frame_kinetic_reduction as v612
from bhsm.interface import fold_schur_kinetic as v629


VERSION = "v6.30.0"
SPRINT = "bhsm-fold-potential-mass-v6-30-0"
SOURCE_MAIN_SHA = "6e123ec1864044a3949b13e26c205acbe26ad898"
V628_SCIENTIFIC_SHA = "853bddac1852c6b328fc4cf7af2786e2f59baf34"
V629_SCIENTIFIC_SHA = "0c65bd9bf6480eee705fc6ee7769ecb4521b3abf"
V629_REPRODUCIBILITY_SHA = "4f7ca8791c74bc86397e0f8275de25cea4a71c73"

PRIMARY_RESULT = (
    "BHSM_FOLD_EINSTEIN_POTENTIAL_REQUIRES_FIXED_ACTION_OFFSHELL_RADIAL_FAMILY"
)
LOCAL_POTENTIAL_RESULT = (
    "BHSM_FOLD_EINSTEIN_POTENTIAL_DERIVED_THROUGH_QUADRATIC_ORDER_AT_CRITICALITY"
)
MASS_RESULT = "BHSM_FOLD_DIMENSIONLESS_MASS_CURVATURE_DERIVED"
MASS_CLASSIFICATION = "BHSM_FOLD_CRITICAL_MASS_CURVATURE_NULL"
STOP_RESULT = "BHSM_FULL_CLOSURE_CAMPAIGN_STOPPED_AT_V6_30_CLASS_B_BLOCKER"
NEXT_RESULT = "BHSM_V6_31_NOT_PERMITTED_BY_MISSING_FULL_OFFSHELL_POTENTIAL"

REQUIRED_FULL_POTENTIAL_RESULT = "BHSM_FOLD_EINSTEIN_FRAME_POTENTIAL_DERIVED"

ARTIFACT_FILES = {
    "jordan": "BHSM_fold_Jordan_potential_provenance_audit_v6_30_0.json",
    "einstein": "BHSM_fold_Einstein_potential_sufficiency_v6_30_0.json",
    "hessian": "BHSM_fold_critical_potential_Hessian_v6_30_0.json",
    "mass": "BHSM_fold_dimensionless_mass_curvature_v6_30_0.json",
    "stop": "BHSM_full_closure_campaign_stop_v6_30_0.json",
}

GUARDS = {
    "measured_input_used": False,
    "fitted_parameter_used": False,
    "chat_only_value_imported": False,
    "new_action_introduced": False,
    "new_primitive_introduced": False,
    "new_scale_introduced": False,
    "vacuum_constant_subtracted": False,
    "control_varying_curve_used_as_fixed_action_potential": False,
    "on_shell_cusp_used_as_off_shell_potential": False,
    "F2_assumed": False,
    "V2_assumed": False,
    "full_potential_claimed": False,
    "physical_mass_claimed": False,
    "potential_stability_claimed": False,
    "v6_31_permitted": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}

Q = sp.symbols("q", real=True)
F0, F1, F2 = sp.symbols("F_0 F_1 F_2", real=True)
V0, V1, V2 = sp.symbols("V_0 V_1 V_2", real=True)
L, V_AFFINE = sp.symbols("L v", nonzero=True, real=True)
DELTA_MU = sp.symbols("delta_mu", real=True)
NU_1 = sp.symbols("nu_1", positive=True, real=True)
TAU = sp.symbols("tau", real=True)

K_Q_E_DECIMAL = "6.935084858283065"
K_Q_E_UNCERTAINTY_DECIMAL = "2e-12"


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def jordan_taylor() -> sp.Expr:
    return V0 + V1 * Q + V2 * Q**2 / 2


def frame_taylor() -> sp.Expr:
    return F0 + F1 * Q + F2 * Q**2 / 2


def einstein_taylor() -> sp.Expr:
    """Formal local V_E=(F0/F)^2 V_J before coefficient closure."""

    return sp.simplify((F0 / frame_taylor()) ** 2 * jordan_taylor())


def einstein_value() -> sp.Expr:
    return sp.simplify(einstein_taylor().subs(Q, 0))


def einstein_gradient() -> sp.Expr:
    return sp.simplify(sp.diff(einstein_taylor(), Q).subs(Q, 0))


def einstein_hessian() -> sp.Expr:
    return sp.simplify(sp.diff(einstein_taylor(), Q, 2).subs(Q, 0))


def stationary_jordan_gradient() -> sp.Expr:
    """V1 relation implied by V_E'(0)=0."""

    return sp.simplify(2 * F1 * V0 / F0)


def stationary_einstein_hessian() -> sp.Expr:
    return sp.factor(
        einstein_hessian().subs(V1, stationary_jordan_gradient())
    )


def null_hessian_jordan_relation() -> sp.Expr:
    """V2 relation implied by stationarity plus the critical null Hessian."""

    solution = sp.solve(sp.Eq(stationary_einstein_hessian(), 0), V2)
    if len(solution) != 1:
        raise RuntimeError("critical Hessian relation is not uniquely solvable")
    return sp.factor(solution[0])


def frame_coefficients(tau: int) -> dict[str, sp.Expr]:
    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    return {
        "F0": sp.simplify(v612.frame_F0()),
        "F1": sp.simplify(v612.frame_F1(tau)),
        "F2_functional": sp.simplify(v612.frame_F2_formula()),
    }


def affine_zero_derivative_schur() -> sp.Expr:
    """K0-J0 L0^-1 J0 for J0=L0 v and K0=v L0 v."""

    j0 = L * V_AFFINE
    k0 = L * V_AFFINE**2
    return sp.simplify(k0 - j0**2 / L)


def scalar_critical_quadratic_form() -> sp.Integer:
    """The normalized Jacobi amplitude lies in ker(L0_scalar)."""

    return sp.Integer(0)


def critical_jordan_reduced_hessian() -> sp.Expr:
    """Metric affine cancellation plus the scalar Jacobi zero mode."""

    return sp.simplify(
        affine_zero_derivative_schur() + scalar_critical_quadratic_form()
    )


def critical_einstein_hessian() -> sp.Expr:
    """A regular field redefinition preserves the stationary null Hessian."""

    if sp.simplify(v612.frame_F0()) == 0:
        raise RuntimeError("Einstein transformation is singular at the fold")
    return critical_jordan_reduced_hessian()


def dimensionless_mass_squared() -> sp.Expr:
    """mu_q^2=V_E''/k_q^E at the critical stationary point."""

    k_q_e = sp.Float(K_Q_E_DECIMAL, 30)
    return sp.simplify(critical_einstein_hessian() / k_q_e)


def reduced_normal_form(tau: sp.Expr = TAU) -> sp.Expr:
    """Inherited fixed-control local reduced action, excluding Gamma_c."""

    return DELTA_MU * Q**2 / 4 - tau * NU_1 * Q**3 / 6


def branch_control(tau: sp.Expr = TAU) -> sp.Expr:
    return tau * NU_1 * Q


def on_shell_cusp(tau: sp.Expr = TAU) -> sp.Expr:
    return sp.simplify(
        reduced_normal_form(tau).subs(DELTA_MU, branch_control(tau))
    )


def fixed_control_hessian_at_fold(tau: sp.Expr = TAU) -> sp.Expr:
    return sp.simplify(
        sp.diff(reduced_normal_form(tau), Q, 2).subs(
            {Q: 0, DELTA_MU: 0}
        )
    )


def f2_sensitivity_after_stationarity() -> sp.Expr:
    return sp.simplify(sp.diff(stationary_einstein_hessian(), F2))


def v2_sensitivity_after_stationarity() -> sp.Expr:
    return sp.simplify(sp.diff(stationary_einstein_hessian(), V2))


def action_ledger() -> dict[str, Any]:
    return {
        "sectors": [
            "two reflected P1 Einstein-Hilbert caps",
            "two capwise GHY completions",
            "bulk scalar kinetic and U5=A5 sigma^2/2+G5 sigma^4/4",
            "one common intrinsic C_partial R4 action",
            "exact matcher",
            "v6.27 full momentum constraint",
            "v6.28 projected L0/J0/K0 quadratic action",
            "v6.29 positive Einstein-frame kinetic coefficient",
        ],
        "critical_point": "q0=0 at Xc=2 in the normalized representative",
        "stationarity": (
            "the critical background obeys the frozen Euler-Lagrange and "
            "junction equations; the first variation along q therefore vanishes"
        ),
        "frame_regular": sp.sstr(frame_coefficients(1)["F0"]),
        "cap_multiplicity": 2,
        "common_B1_multiplicity": 1,
        "matcher_eliminated": True,
    }


def jordan_provenance_ledger() -> dict[str, Any]:
    return {
        "available": {
            "quadratic_action": (
                "v6.28 S2 on (A,psi,delta_sigma_perp) with affine q profiles"
            ),
            "affine_identity": "J0=L0 v and K0=<v,L0 v>",
            "scalar_identity": "u1 is the critical normalized Jacobi zero mode",
            "fixed_control_normal_form": (
                "Gamma-Gamma_c=delta_mu q^2/4-tau nu1 q^3/6+..."
            ),
            "control_branch": "delta_mu=tau nu1 q+O(q^2)",
            "stored_cusp": "tau nu1 q^3/12+O(q^4)",
        },
        "not_available": [
            "a fixed-action off-shell nonlinear radial family indexed by q",
            "a common regulated M4 density for comparing different q",
            "the full coefficient functions V_J(q) and F(q)",
            "analytic a2(t), N2(t), and higher radial responses",
        ],
        "candidate_rejected": (
            "the Puiseux continuation changes mu=-A5/Z5 with q and therefore "
            "moves among neighboring actions; it is not V_J(q) in one action"
        ),
        "on_shell_cusp_is_off_shell_potential": False,
        "control_varying_curve_is_fixed_action": False,
        "full_Jordan_potential_derived": False,
        "obstruction_class": "B: missing derivation within the frozen action",
    }


def einstein_sufficiency_ledger() -> dict[str, Any]:
    plus = frame_coefficients(1)
    minus = frame_coefficients(-1)
    return {
        "formal_transform": "V_E=(F0/F)^2 V_J",
        "formal_value": sp.sstr(einstein_value()),
        "formal_gradient": sp.sstr(einstein_gradient()),
        "formal_hessian": sp.sstr(einstein_hessian()),
        "stationary_relation": sp.sstr(
            sp.Eq(V1, stationary_jordan_gradient())
        ),
        "stationary_hessian": sp.sstr(stationary_einstein_hessian()),
        "critical_null_relation": sp.sstr(
            sp.Eq(V2, null_hessian_jordan_relation())
        ),
        "frame": {
            "F0": sp.sstr(plus["F0"]),
            "F1_plus": sp.sstr(plus["F1"]),
            "F1_minus": sp.sstr(minus["F1"]),
            "F2_functional": sp.sstr(plus["F2_functional"]),
        },
        "coefficient_sensitivities": {
            "d_hessian_d_V2": sp.sstr(v2_sensitivity_after_stationarity()),
            "d_hessian_d_F2": sp.sstr(f2_sensitivity_after_stationarity()),
        },
        "invariant_combination_fixed": (
            "the complete v6.28 stationary Hessian fixes the displayed "
            "V2/F2 combination to zero, not V2 or F2 separately"
        ),
        "full_function_fixed": False,
        "required_full_potential_verdict_emitted": False,
        "result": PRIMARY_RESULT,
    }


def critical_hessian_ledger() -> dict[str, Any]:
    return {
        "metric": {
            "J0": "L0 v on the projected complementary range",
            "K0": "<v,L0 v>",
            "Schur": sp.sstr(affine_zero_derivative_schur()),
            "kernel_handling": (
                "the metric modulus is retained; compatibility is the v6.28 "
                "Lyapunov-Schmidt condition, not a generic pseudoinverse"
            ),
        },
        "scalar": {
            "mode": "u1",
            "domain": "regular pole, Dirichlet at B1",
            "normalization": "integral N0 a0^4 u1^2 dt=1 per cap",
            "quadratic_form": sp.sstr(scalar_critical_quadratic_form()),
        },
        "Jordan_reduced_hessian": sp.sstr(critical_jordan_reduced_hessian()),
        "Einstein_reduced_hessian": sp.sstr(critical_einstein_hessian()),
        "Einstein_reason": (
            "at a stationary point the Hessian transforms by congruence under "
            "the regular F0=pi/2 frame redefinition, preserving its null mode"
        ),
        "local_potential": "V_E(q)=V_E(0)+O(q^3) on each one-sided sheet",
        "stationary": True,
        "sheet_dependence_at_q0": "none",
        "scalar_sign_dependence_at_q0": "none",
        "result": LOCAL_POTENTIAL_RESULT,
    }


def mass_ledger() -> dict[str, Any]:
    return {
        "q0": 0,
        "k_q_E": K_Q_E_DECIMAL,
        "k_q_E_uncertainty": K_Q_E_UNCERTAINTY_DECIMAL,
        "kinetic_result": v629.PRIMARY_RESULT,
        "V_E_second_at_q0": sp.sstr(critical_einstein_hessian()),
        "formula": "mu_q^2=V_E''(q0)/k_q^E",
        "mu_q_squared": sp.sstr(dimensionless_mass_squared()),
        "classification": "null curvature at the critical fold",
        "ghost": False,
        "tachyon": False,
        "positive_mass": False,
        "potential_stability_away_from_q0": "not derived",
        "physical_unit": None,
        "physical_mass": None,
        "result": MASS_RESULT,
        "secondary_result": MASS_CLASSIFICATION,
    }


def blocker_ledger() -> dict[str, Any]:
    return {
        "campaign_stopped": True,
        "stopped_after_phase": "v6.30",
        "v6_31_permitted": False,
        "reason": (
            "v6.30 derives the local critical Hessian and null dimensionless "
            "mass, but not the required full off-shell Einstein potential"
        ),
        "smallest_missing_object": (
            "a fixed-action, fixed-regulator off-shell constrained radial "
            "family C_(q,tau) with independent M4 metric, holding "
            "kappa0,kappa1,Z5,A5,G5,C_partial fixed"
        ),
        "required_outputs_of_missing_object": [
            "F(q), including analytic a2(t), N2(t) and higher responses",
            "V_J(q) before the M4 metric equation is imposed",
            "one common regulated M4 action density",
            "nonlinear B1/matcher boundary form on the same family",
        ],
        "why_existing_curve_fails": (
            "delta_mu=tau nu1 q varies A5/Z5 and the regulated M4 geometry"
        ),
        "repair_path_uses_existing_action": True,
        "new_action_required": False,
        "fatal_inconsistency": False,
        "obstruction_class": "B: missing derivation within the frozen action",
        "next_result": NEXT_RESULT,
        "result": STOP_RESULT,
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_28_scientific_sha": V628_SCIENTIFIC_SHA,
        "v6_29_scientific_sha": V629_SCIENTIFIC_SHA,
        "v6_29_reproducibility_sha": V629_REPRODUCIBILITY_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "jordan": {
            **_common("BHSM_fold_Jordan_potential_provenance_audit_v6_30_0"),
            "action": action_ledger(),
            "Jordan": jordan_provenance_ledger(),
            "normal_form_checks": {
                "fixed_control": sp.sstr(reduced_normal_form()),
                "branch_control": sp.sstr(branch_control()),
                "on_shell_cusp": sp.sstr(on_shell_cusp()),
                "fixed_control_hessian_at_fold": sp.sstr(
                    fixed_control_hessian_at_fold()
                ),
            },
        },
        "einstein": {
            **_common("BHSM_fold_Einstein_potential_sufficiency_v6_30_0"),
            "Einstein": einstein_sufficiency_ledger(),
        },
        "hessian": {
            **_common("BHSM_fold_critical_potential_Hessian_v6_30_0"),
            "Hessian": critical_hessian_ledger(),
        },
        "mass": {
            **_common("BHSM_fold_dimensionless_mass_curvature_v6_30_0"),
            "mass": mass_ledger(),
        },
        "stop": {
            **_common("BHSM_full_closure_campaign_stop_v6_30_0"),
            "stop": blocker_ledger(),
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
