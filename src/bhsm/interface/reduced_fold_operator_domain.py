"""BHSM v6.28.0 reduced fold operator and radial domain.

This module derives the complete local two-M4-derivative operator pencil on
Y=(A, psi, delta_sigma_perp) directly from the frozen P1+GHY+scalar+B1
action.  The shift and endpoint are eliminated with the v6.27 parent
momentum constraint.  The result is a symmetric differential-algebraic
radial form: A is algebraic, psi is second order before the radial gauge
quotient, and the orthogonal scalar block is Sturm--Liouville.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.28.0"
SPRINT = "bhsm-reduced-fold-operator-domain-v6-28-0"
SOURCE_MAIN_SHA = "d94f2dd71eac8f03649f73011e6b4ee830f7b09b"
V627_SCIENTIFIC_SHA = "643bc7371fc81f07cce465abded3f5d2885bca3c"

OPERATOR_RESULT = "BHSM_REDUCED_FOLD_OPERATOR_L0_L1_DERIVED"
SOURCE_RESULT = "BHSM_REDUCED_FOLD_SOURCE_J0_J1_DERIVED"
ADJOINT_RESULT = "BHSM_REDUCED_FOLD_ADJOINT_DOMAIN_DERIVED"
KERNEL_RESULT = "BHSM_REDUCED_FOLD_KERNEL_AND_COMPATIBILITY_DERIVED"
PRIMARY_RESULT = OPERATOR_RESULT
PHASE_RESULT = "BHSM_REDUCED_FOLD_OPERATOR_AND_DOMAIN_CLOSED_CONDITIONALLY"
NEXT_RESULT = "BHSM_V6_29_SCHUR_REDUCTION_PERMITTED_WITH_PROJECTED_PENCIL"

ARTIFACT_FILES = {
    "operator": "BHSM_reduced_fold_L0_L1_operator_v6_28_0.json",
    "source": "BHSM_reduced_fold_J0_J1_source_v6_28_0.json",
    "domain": "BHSM_reduced_fold_adjoint_domain_v6_28_0.json",
    "kernel": "BHSM_reduced_fold_kernel_compatibility_v6_28_0.json",
    "verdict": "BHSM_reduced_fold_operator_phase_verdict_v6_28_0.json",
}

GUARDS = {
    "measured_input_used": False,
    "fitted_parameter_used": False,
    "new_action_introduced": False,
    "new_primitive_introduced": False,
    "new_scale_introduced": False,
    "new_boundary_parameter_introduced": False,
    "global_Lorentzian_propagator_selected": False,
    "generic_pseudoinverse_used": False,
    "radial_profile_double_counted": False,
    "M4_curvature_tangent_double_counted": False,
    "operator_inverse_emitted": False,
    "Schur_number_emitted": False,
    "kinetic_sign_emitted": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physical_mass_claimed": False,
    "stability_claimed": False,
}

T = sp.symbols("t", nonnegative=True, real=True)
LAMBDA = sp.symbols("lambda", real=True)
KAPPA_1 = sp.symbols("kappa_1", positive=True, real=True)
Z5 = sp.symbols("Z5", positive=True, real=True)
A5 = sp.symbols("A5", real=True)
C_PARTIAL = sp.symbols("C_partial", positive=True, real=True)
TAU = sp.symbols("tau", nonzero=True, real=True)
CHI_1 = sp.symbols("chi_1", positive=True, real=True)
X_CRITICAL = sp.Integer(2)
KAPPA_0 = 12 * KAPPA_1
N0 = sp.pi / 4


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def a0(t: sp.Expr = T) -> sp.Expr:
    return sp.sqrt(2) * sp.sin(sp.pi * t / 4)


def radial_weight(t: sp.Expr = T) -> sp.Expr:
    return sp.simplify(N0 * a0(t) ** 4)


def radial_hubble(t: sp.Expr = T) -> sp.Expr:
    """H=a_rho/a with rho=N0 t."""

    return sp.simplify(sp.diff(a0(t), t) / (N0 * a0(t)))


def background_residuals(t: sp.Expr = T) -> dict[str, sp.Expr]:
    a = a0(t)
    h = radial_hubble(t)
    return {
        "Hamiltonian": sp.trigsimp(h**2 - X_CRITICAL / a**2 + 1),
        "radial_evolution": sp.trigsimp(
            sp.diff(a, t, 2) / (N0**2 * a) + 1
        ),
        "B1_H": sp.simplify(h.subs(t, 1) - 1),
        "kappa0_relation": sp.simplify(KAPPA_0 - 12 * KAPPA_1),
    }


def metric_q0_coefficients(t: sp.Expr = T) -> dict[str, sp.Expr]:
    """Coefficients of the two-cap quadratic density.

    Q0=cAA A^2+d A psi'+e A psi+cPP psi'^2+f psi psi'+g psi^2.
    The density follows by expanding the stored one-dimensional action
    6*kappa_1[a^2 a'^2/N+N X a^2]-N a^4 kappa_0/2 on both caps.
    """

    a = a0(t)
    ap = sp.diff(a, t)
    return {
        "cAA": sp.simplify(12 * KAPPA_1 * a**2 * ap**2 / N0),
        "d": sp.simplify(-24 * KAPPA_1 * a**3 * ap / N0),
        "e": sp.simplify(
            24 * X_CRITICAL * KAPPA_1 * N0 * a**2
            - 48 * KAPPA_1 * a**2 * ap**2 / N0
            - 4 * KAPPA_0 * N0 * a**4
        ),
        "cPP": sp.simplify(12 * KAPPA_1 * a**4 / N0),
        "f": sp.simplify(48 * KAPPA_1 * a**3 * ap / N0),
        "g": sp.simplify(
            48 * KAPPA_1 * a**2 * ap**2 / N0
            - 4 * KAPPA_0 * N0 * a**4
        ),
    }


def metric_quadratic_density(
    lapse: sp.Expr,
    weyl: sp.Expr,
    lam: sp.Expr = LAMBDA,
    t: sp.Expr = T,
) -> sp.Expr:
    c = metric_q0_coefficients(t)
    derivative = sp.diff(weyl, t)
    q0 = (
        c["cAA"] * lapse**2
        + c["d"] * lapse * derivative
        + c["e"] * lapse * weyl
        + c["cPP"] * derivative**2
        + c["f"] * weyl * derivative
        + c["g"] * weyl**2
    )
    q1 = (
        radial_weight(t)
        * lam
        * (
            6 * KAPPA_1 * lapse * weyl / a0(t) ** 2
            + 6 * KAPPA_1 * weyl**2 / a0(t) ** 2
        )
    )
    return sp.expand(q0 + q1)


def scalar_quadratic_density(
    scalar: sp.Expr,
    lam: sp.Expr = LAMBDA,
    t: sp.Expr = T,
) -> sp.Expr:
    """Two-cap scalar Hessian at sigma0=0."""

    a = a0(t)
    return sp.expand(
        -Z5 * a**4 * sp.diff(scalar, t) ** 2 / N0
        - N0 * a**4 * A5 * scalar**2
        - Z5 * N0 * a**2 * lam * scalar**2
    )


def metric_euler_expressions(
    lapse: sp.Expr,
    weyl: sp.Expr,
    lam: sp.Expr = LAMBDA,
    t: sp.Expr = T,
) -> dict[str, sp.Expr]:
    """Weighted Euler expressions reconstructed from the quadratic density."""

    c = metric_q0_coefficients(t)
    w = radial_weight(t)
    e_a = (
        2 * c["cAA"] * lapse
        + c["d"] * sp.diff(weyl, t)
        + c["e"] * weyl
        + w * lam * 6 * KAPPA_1 * weyl / a0(t) ** 2
    )
    e_psi = (
        -sp.diff(c["d"] * lapse, t)
        + c["e"] * lapse
        - 2 * sp.diff(c["cPP"] * sp.diff(weyl, t), t)
        + (2 * c["g"] - sp.diff(c["f"], t)) * weyl
        + w
        * lam
        * (
            6 * KAPPA_1 * lapse / a0(t) ** 2
            + 12 * KAPPA_1 * weyl / a0(t) ** 2
        )
    )
    return {
        "A": sp.simplify(e_a / w),
        "psi": sp.simplify(e_psi / w),
    }


def scalar_euler_expression(
    scalar: sp.Expr,
    lam: sp.Expr = LAMBDA,
    t: sp.Expr = T,
) -> sp.Expr:
    return (
        2
        * Z5
        / radial_weight(t)
        * sp.diff(a0(t) ** 4 / N0 * sp.diff(scalar, t), t)
        - 2 * A5 * scalar
        - 2 * Z5 * lam * scalar / a0(t) ** 2
    )


def metric_bilinear_density(
    A1: sp.Expr,
    psi1: sp.Expr,
    A2: sp.Expr,
    psi2: sp.Expr,
    lam: sp.Expr = LAMBDA,
    t: sp.Expr = T,
) -> sp.Expr:
    """Polarization of the metric quadratic density."""

    alpha, beta = sp.symbols("alpha beta", real=True)
    density = metric_quadratic_density(
        alpha * A1 + beta * A2,
        alpha * psi1 + beta * psi2,
        lam,
        t,
    )
    return sp.simplify(sp.diff(density, alpha, beta).subs({alpha: 0, beta: 0}))


def b1_quadratic_form(weyl_at_b1: sp.Expr, lam: sp.Expr = LAMBDA) -> sp.Expr:
    """One common intrinsic B1 action; no zero-derivative Hessian."""

    return sp.simplify(6 * C_PARTIAL * lam * weyl_at_b1**2)


def L0_L1_block_ledger() -> dict[str, Any]:
    c = metric_q0_coefficients()
    w = radial_weight()
    return {
        "weight": sp.sstr(w),
        "L0": {
            "L_AA": sp.sstr(sp.simplify(2 * c["cAA"] / w)),
            "L_Apsi": (
                f"({sp.sstr(sp.simplify(c['d']/w))}) partial_t"
                f"+({sp.sstr(sp.simplify(c['e']/w))})"
            ),
            "L_Adelta_sigma": "0",
            "L_psiA": (
                f"-w^-1 partial_t[({sp.sstr(c['d'])}) .]"
                f"+({sp.sstr(sp.simplify(c['e']/w))})"
            ),
            "L_psipsi": (
                f"-2 w^-1 partial_t[({sp.sstr(c['cPP'])}) partial_t]"
                f"+({sp.sstr(sp.simplify((2*c['g']-sp.diff(c['f'],T))/w))})"
            ),
            "L_psidelta_sigma": "0",
            "L_delta_sigmadelta_sigma": (
                "2 Z5 w^-1 partial_t[a0^4/N0 partial_t]-2 A5"
            ),
        },
        "L1": {
            "metric": [
                ["0", sp.sstr(6 * KAPPA_1 / a0() ** 2), "0"],
                [
                    sp.sstr(6 * KAPPA_1 / a0() ** 2),
                    sp.sstr(12 * KAPPA_1 / a0() ** 2),
                    "0",
                ],
                ["0", "0", sp.sstr(-2 * Z5 / a0() ** 2)],
            ],
            "B1_endpoint_Hessian": "12 C_partial in the psi-psi slot",
        },
        "mixed_scalar_blocks_zero_reason": (
            "sigma0=0 and D sigma0=0, so every metric-scalar cross term "
            "starts at cubic order"
        ),
        "operator_type": (
            "symmetric radial differential-algebraic pencil: A algebraic, "
            "psi second order, delta_sigma_perp Sturm-Liouville"
        ),
    }


def principal_lapse_weyl_matrix(t: sp.Expr = T) -> sp.ImmutableMatrix:
    return sp.ImmutableMatrix(
        [
            [0, 6 * KAPPA_1 / a0(t) ** 2],
            [6 * KAPPA_1 / a0(t) ** 2, 12 * KAPPA_1 / a0(t) ** 2],
        ]
    )


def hamiltonian_solution_for_A(
    weyl: sp.Expr, t: sp.Expr = T
) -> sp.Expr:
    """Solve the lambda=0 A equation before any elimination."""

    h = radial_hubble(t)
    return sp.simplify(
        (
            h * sp.diff(weyl, t) / N0
            + X_CRITICAL * weyl / a0(t) ** 2
        )
        / h**2
    )


def metric_boundary_momentum(
    lapse: sp.Expr, weyl: sp.Expr, t: sp.Expr = T
) -> sp.Expr:
    c = metric_q0_coefficients(t)
    return sp.simplify(
        c["d"] * lapse
        + 2 * c["cPP"] * sp.diff(weyl, t)
        + c["f"] * weyl
    )


def metric_b1_operator(
    lapse: sp.Expr,
    weyl: sp.Expr,
    lam: sp.Expr = LAMBDA,
) -> sp.Expr:
    return sp.simplify(
        metric_boundary_momentum(lapse, weyl, T).subs(T, 1)
        + 12 * C_PARTIAL * lam * weyl.subs(T, 1)
    )


def green_current(
    A1: sp.Expr,
    psi1: sp.Expr,
    s1: sp.Expr,
    A2: sp.Expr,
    psi2: sp.Expr,
    s2: sp.Expr,
    t: sp.Expr = T,
) -> sp.Expr:
    c = metric_q0_coefficients(t)
    metric = (
        c["d"] * (A1 * psi2 - A2 * psi1)
        - 2
        * c["cPP"]
        * (psi1 * sp.diff(psi2, t) - sp.diff(psi1, t) * psi2)
    )
    scalar = (
        2
        * Z5
        * a0(t) ** 4
        / N0
        * (s1 * sp.diff(s2, t) - sp.diff(s1, t) * s2)
    )
    return sp.simplify(metric + scalar)


def gauge_kernel(
    xi: sp.Expr,
    t: sp.Expr = T,
) -> dict[str, sp.Expr]:
    return {
        "A": -sp.diff(xi, t),
        "psi": -sp.diff(a0(t), t) * xi / a0(t),
        "delta_sigma": sp.Integer(0),
    }


def metric_modulus(t: sp.Expr = T) -> dict[str, sp.Expr]:
    """Representative of the one quotient metric kernel."""

    return {
        "A": sp.simplify(1 / sp.cos(sp.pi * t / 4) ** 2),
        "psi": sp.Integer(1),
        "delta_sigma": sp.Integer(0),
    }


def metric_modulus_lifting_coefficient() -> sp.Expr:
    """<z,L1 z> including the common B1 Hessian."""

    return sp.simplify(12 * C_PARTIAL + 3 * KAPPA_1 * (6 - sp.pi))


def a1(t: sp.Expr = T) -> sp.Expr:
    return sp.simplify(
        CHI_1
        * (
            a0(t) / 4
            - sp.sqrt(2) * t * sp.cos(sp.pi * t / 4) / 4
        )
    )


def affine_profiles(t: sp.Expr = T) -> dict[str, sp.Expr | str]:
    """The v6.23 independent-h affine convention, used exactly once."""

    return {
        "A_q": sp.simplify(-TAU * CHI_1 / sp.pi),
        "psi_q": sp.simplify(TAU * a1(t) / a0(t)),
        "sigma_q": "s u1(t), with <u1,u1>_(N0 a0^4)=1 per cap",
        "B_q": sp.simplify(-TAU * sp.pi * CHI_1 * t / 16),
        "E_q": sp.Integer(0),
        "zeta_q": sp.Integer(0),
        "M4_X_tangent_added": False,
    }


def threading_source_coefficients(t: sp.Expr = T) -> dict[str, sp.Expr]:
    b = sp.sympify(affine_profiles(t)["B_q"])
    return {
        "J_A": sp.simplify(
            6
            * KAPPA_1
            * b
            * (sp.diff(a0(t), t) / a0(t))
            / (N0**2 * a0(t) ** 2)
        ),
        "J_psi_derivative": sp.simplify(
            -6 * KAPPA_1 * b / (N0**2 * a0(t) ** 2)
        ),
    }


def source_ledger() -> dict[str, Any]:
    profiles = affine_profiles()
    threading = threading_source_coefficients()
    return {
        "affine_convention": (
            "Y_total=Y_response+q v with v=(N1/N0,a1/a0,s u1); "
            "independent M4 h is varied and no separate X-metric tangent is added"
        ),
        "profiles": {key: sp.sstr(value) for key, value in profiles.items()},
        "J0": (
            "J0[Y]=B0_metric(v_metric,Y_metric)"
            "+B0_scalar(s u1,delta_sigma_perp); the scalar term is zero "
            "and the metric functional includes its B1 boundary distribution"
        ),
        "J1": (
            "J1[Y]=B1_metric(v_metric,Y_metric)"
            "-2Z5 integral N0 a0^2(s u1)delta_sigma_perp dt"
            "+integral w[J_A A+J_psi_derivative partial_t psi]dt"
        ),
        "threading": {
            "J_A": sp.sstr(threading["J_A"]),
            "J_psi_derivative": sp.sstr(threading["J_psi_derivative"]),
            "endpoint_after_radial_IBP": (
                "[w J_psi_derivative psi]_(0,1); retained with the B1 source"
            ),
        },
        "K_direct": {
            "K0": (
                "B0_metric(v,v)+B0_scalar(su1,su1); the scalar term vanishes "
                "by the critical Jacobi equation"
            ),
            "K1": (
                "B1_metric(v,v)-2Z5 integral N0 a0^2 u1^2 dt"
                "+2 integral w[J_A v_A+J_psi_derivative partial_t v_psi]dt"
            ),
            "pure_shift_square": (
                "zero after the parent constraint: the shift Hessian is a "
                "quadratic form in W=B+tau(pi chi_1/16)tq and W=0"
            ),
            "radial_profiles_counted_once": True,
            "Einstein_frame_Weyl_term_included": False,
        },
        "source_boundary_form_retained": True,
        "global_Lorentzian_state": None,
        "result": SOURCE_RESULT,
    }


def projector_ledger() -> dict[str, Any]:
    return {
        "critical_mode": (
            "u1 solves [a0^-4 partial_rho(a0^4 partial_rho)"
            "-A5/Z5]u1=0"
        ),
        "boundary": "u1,_rho(0)=0, u1(1)=0",
        "normalization": (
            "integral_0^1 N0 a0^4 u1^2 dt=1 per cap"
        ),
        "projector": (
            "P_perp f=f-u1 integral_0^1 N0 a0^4 u1 f dt"
        ),
        "domain_condition": (
            "integral_0^1 N0 a0^4 u1 delta_sigma_perp dt=0"
        ),
        "source_projection": "J_sigma is replaced by P_perp J_sigma",
        "kernel_removed": True,
    }


def domain_ledger() -> dict[str, Any]:
    return {
        "inner_product": (
            "<Y1,Y2>=integral_0^1 N0 a0^4"
            "(A1 A2+psi1 psi2+s1 s2)dt"
        ),
        "regular_pole": {
            "derivative_expansion": (
                "A=A0+O(t^2), psi=psi0+O(t^2), "
                "delta_sigma=s0+O(t^2); coefficientwise radial flux vanishes"
            ),
            "finite_lambda_resummation": (
                "not used; lambda is the local derivative-pencil parameter"
            ),
        },
        "B1": {
            "metric": (
                "P_psi(1)+12 C_partial lambda psi(1)=0, "
                "P_psi=d A+2cPP psi'+f psi"
            ),
            "scalar": "delta_sigma_perp(1)=0",
            "matcher": "h=iota^*gamma eliminated algebraically",
            "full_momentum": "W=0; B is not an independent domain variable",
        },
        "gauge_quotient": (
            "(A,psi)~(A-xi',psi-(a0'/a0)xi) for regular xi with xi(0)=xi(1)=0"
        ),
        "scalar_orthogonality": projector_ledger()["domain_condition"],
        "formal_adjoint": "the displayed differential expressions with the same weight",
        "adjoint_domain": (
            "the same pole, B1 Robin/Dirichlet, matcher, quotient, and "
            "orthogonality conditions"
        ),
        "self_adjointness": True,
        "proof": (
            "the exact Green current vanishes at the pole; at B1 it becomes "
            "psi2 P1-psi1 P2 plus the scalar Dirichlet current and vanishes "
            "for two fields in the domain"
        ),
        "result": ADJOINT_RESULT,
    }


def kernel_ledger() -> dict[str, Any]:
    return {
        "L0_prequotient": {
            "metric": (
                "infinite radial-diffeomorphism kernel generated by regular "
                "xi with xi(0)=xi(1)=0"
            ),
            "scalar": "simple critical Jacobi kernel span{u1}",
        },
        "classifications": {
            "radial_diffeomorphisms": "gauge",
            "u1": "physical fold collective mode, removed from delta_sigma_perp",
            "metric_z": (
                "one background conformal modulus after the endpoint-preserving "
                "radial gauge quotient"
            ),
            "C1_shift": "forbidden by the v6.27 full momentum constraint",
        },
        "metric_modulus_representative": {
            key: sp.sstr(value) for key, value in metric_modulus().items()
        },
        "quotient_kernel_dimension": 1,
        "adjoint_kernel_dimension": 1,
        "scalar_perp_kernel_dimension": 0,
        "compatibility": {
            "J0": (
                "orthogonal to the adjoint quotient kernel by the B0 Green "
                "identity including the affine B1 boundary distribution"
            ),
            "gauge": (
                "J0 and J1 annihilate endpoint-preserving gauge generators "
                "by the radial Noether identity"
            ),
            "scalar": "P_perp J_sigma is orthogonal to u1 by construction",
            "metric_at_lambda1": (
                "Lyapunov-Schmidt equation uses M_z=<z,L1 z>="
                "12C_partial+3kappa_1(6-pi)"
            ),
            "M_z": sp.sstr(metric_modulus_lifting_coefficient()),
            "M_z_nonzero": True,
            "kernel_amplitude": (
                "c_z=-<z,J1>/<z,L1z>; no inverse on the unprojected L0 is used"
            ),
        },
        "projected_inverse_ready": True,
        "generic_pseudoinverse_required": False,
        "result": KERNEL_RESULT,
    }


def action_ledger() -> dict[str, Any]:
    return {
        "P1": (
            "(1/2)integral sqrt|g|(kappa_1 R5-kappa_0), "
            "kappa_0=12kappa_1 on the critical representative"
        ),
        "GHY": "kappa_1 integral_B1 sqrt|h|K on each of two caps",
        "scalar": (
            "integral sqrt|g|[-Z5(grad sigma)^2/2-U5], "
            "U5''(0)=A5"
        ),
        "B1": "one common integral sqrt|h| C_partial R4",
        "matcher": (
            "integral sqrt|h| Lambda^(mu nu)(h_mu nu-iota^*gamma_mu nu)"
        ),
        "cap_count": 2,
        "common_B1_count": 1,
        "radial_measure": "N0 a0^4 dt=pi sin^4(pi t/4)dt",
        "metric_ansatz": (
            "N=N0(1+A), gamma_mu_nu=a0^2(1+2psi)hbar_mu_nu, "
            "E=0 after the momentum equation"
        ),
        "scalar_background": "sigma0=0",
        "v627": (
            "W=0, B=-tau(pi chi_1/16)tq, fixed B1 support, "
            "S_Sigma=-tau(pi chi_1/16)q"
        ),
        "new_term": False,
    }


def verdict_ledger() -> dict[str, Any]:
    return {
        "required_results": {
            "operator": OPERATOR_RESULT,
            "source": SOURCE_RESULT,
            "adjoint_domain": ADJOINT_RESULT,
            "kernel_compatibility": KERNEL_RESULT,
        },
        "all_four_derived": True,
        "phase_result": PHASE_RESULT,
        "v6_29_permitted": True,
        "next_result": NEXT_RESULT,
        "v6_29_requirements": [
            "use the quotient/projected L0 inverse only",
            "retain the metric-modulus Lyapunov-Schmidt amplitude",
            "include the inhomogeneous B1 source distribution",
            "project the scalar source with P_perp",
            "count the Einstein-frame Weyl term once",
        ],
        "not_yet_derived": [
            "Schur coefficient",
            "canonical fold kinetic sign",
            "Einstein-frame potential Hessian",
            "dimensionful scale",
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
        "v6_27_scientific_sha": V627_SCIENTIFIC_SHA,
        "primary_result": PRIMARY_RESULT,
        "phase_result": PHASE_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "operator": {
            **_common("BHSM_reduced_fold_L0_L1_operator_v6_28_0"),
            "action": action_ledger(),
            "background": {
                key: sp.sstr(value) for key, value in background_residuals().items()
            },
            "operator": L0_L1_block_ledger(),
            "principal_matrix": [
                [sp.sstr(value) for value in row]
                for row in principal_lapse_weyl_matrix().tolist()
            ],
        },
        "source": {
            **_common("BHSM_reduced_fold_J0_J1_source_v6_28_0"),
            "source": source_ledger(),
            "projector": projector_ledger(),
        },
        "domain": {
            **_common("BHSM_reduced_fold_adjoint_domain_v6_28_0"),
            "domain": domain_ledger(),
        },
        "kernel": {
            **_common("BHSM_reduced_fold_kernel_compatibility_v6_28_0"),
            "kernel": kernel_ledger(),
        },
        "verdict": {
            **_common("BHSM_reduced_fold_operator_phase_verdict_v6_28_0"),
            "verdict": verdict_ledger(),
            "integrity": dict(GUARDS),
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
