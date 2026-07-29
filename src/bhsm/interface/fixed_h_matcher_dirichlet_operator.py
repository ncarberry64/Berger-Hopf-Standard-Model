"""BHSM v6.30.2 fixed-h, uneliminated-matcher Dirichlet operator.

The module keeps the exact metric matcher as a saddle variable.  It derives
the fixed-induced-metric trace map, the radial KKT realization, its Green
identity, kernel/range data, the complementary inverse, and the nonlinear
fixed-h boundary map from the frozen P1+GHY+scalar+B1+matcher action.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import sympy as sp
from scipy.integrate import quad, solve_bvp
from scipy.optimize import brentq
from scipy.special import hyp2f1

from bhsm.interface import fold_schur_kinetic as v629
from bhsm.interface import reduced_fold_operator_domain as v628


VERSION = "v6.30.2"
SPRINT = "bhsm-fixed-h-matcher-dirichlet-operator-v6-30-2"
SOURCE_MAIN_SHA = "57f5945f93b7db6d5781a2b919904073dcc05def"
V6301_SCIENTIFIC_SHA = "e54960b714edd4baba740d9fcb1a587ff0d64f1c"

OPERATOR_RESULT = "BHSM_FIXED_H_UNELIMINATED_MATCHER_OPERATOR_DERIVED"
SECOND_VARIATION_RESULT = "BHSM_FIXED_H_MATCHER_SECOND_VARIATION_DERIVED"
ADJOINT_RESULT = (
    "BHSM_FIXED_H_DIRICHLET_GREEN_CURRENT_AND_ADJOINT_DOMAIN_DERIVED"
)
RANGE_RESULT = "BHSM_FIXED_H_MATCHER_KERNEL_AND_CLOSED_RANGE_DERIVED"
INVERSE_RESULT = "BHSM_FIXED_H_MATCHER_COMPLEMENT_INVERSE_DERIVED"
NONLINEAR_RESULT = "BHSM_FIXED_H_NONLINEAR_BOUNDARY_MAP_DERIVED"

ARTIFACT_FILES = {
    "variation": "BHSM_fixed_h_matcher_second_variation_v6_30_2.json",
    "operator": "BHSM_fixed_h_Dirichlet_KKT_operator_v6_30_2.json",
    "adjoint": "BHSM_fixed_h_Green_current_and_adjoint_domain_v6_30_2.json",
    "inverse": "BHSM_fixed_h_kernel_closed_range_inverse_v6_30_2.json",
    "nonlinear": "BHSM_fixed_h_nonlinear_boundary_map_v6_30_2.json",
}

GUARDS = {
    "matcher_eliminated_before_variation": False,
    "v6_28_Robin_inverse_reused": False,
    "generic_pseudoinverse_used": False,
    "arbitrary_regularization_used": False,
    "measured_input_used": False,
    "empirical_inverse_used": False,
    "empirical_generation_basis_used": False,
    "fitted_parameter_used": False,
    "action_control_varied": False,
    "q_dependent_regulator_used": False,
    "M4_equation_imposed": False,
    "new_action_introduced": False,
    "new_primitive_introduced": False,
    "new_scale_introduced": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physical_mass_claimed": False,
    "stability_claimed": False,
}

T = v628.T
Q = sp.symbols("q", real=True)
KAPPA_1 = v628.KAPPA_1
Z5 = v628.Z5
C_PARTIAL = v628.C_PARTIAL
LAMBDA_PENCIL = v628.LAMBDA


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def action_variation_ledger() -> dict[str, Any]:
    """Exact fixed-h disposition of every frozen action sector."""

    return {
        "total_action": (
            "S_P1,+ + S_P1,- + S_GHY,+ + S_GHY,- + "
            "S_scalar + S_B1 + S_match"
        ),
        "P1": (
            "(1/2) integral sqrt|g|(kappa_1 R5-kappa_0), "
            "two reflected caps"
        ),
        "GHY": (
            "kappa_1 integral_B1 sqrt|h| K on each cap; cancels normal "
            "derivatives of delta gamma cap by cap"
        ),
        "scalar": (
            "integral sqrt|g|[-Z5(grad sigma)^2/2-U5(sigma)]"
        ),
        "B1": (
            "one common C_partial integral sqrt|h| R4; at fixed h its "
            "variation and Hessian with respect to bulk fields vanish"
        ),
        "matcher": (
            "integral_B1 sqrt|h| Lambda^(mu nu)"
            "(h_mu nu-iota^*gamma_mu nu)"
        ),
        "fixed_h_variation": "delta h_mu_nu=0",
        "arbitrary_variations": [
            "bulk delta gamma_mu_nu including its B1 trace",
            "delta Lambda^(mu nu) on B1",
            "bulk delta sigma with odd Dirichlet B1 data",
        ],
        "matcher_equations": {
            "delta_Lambda": "h_mu_nu-iota^*gamma_mu_nu=0",
            "delta_gamma": "Pi_cap,mu_nu-Lambda_mu_nu=0",
            "delta_h": "not imposed in Gamma[h,q] because h is fixed",
        },
        "two_cap_orientation": (
            "outward normals reverse under cap exchange while the common-normal "
            "canonical-momentum jump adds the two reflected responses"
        ),
        "intrinsic_B1_in_radial_KKT": False,
        "intrinsic_B1_reason": (
            "S_B1 is a functional of independent fixed h, not of the bulk "
            "induced metric before the matcher equation is solved"
        ),
        "Ward_identity": (
            "D^mu(Pi_mu_nu-Lambda_mu_nu)=0 after the bulk momentum "
            "constraint; scalar momentum and traceless-longitudinal rows are "
            "the two dependent scalar projections"
        ),
        "new_action_term": False,
        "result": SECOND_VARIATION_RESULT,
    }


def scalar_trace_map(
    psi_at_b1: sp.Expr,
    E_at_b1: sp.Expr,
    box4_E_at_b1: sp.Expr,
) -> dict[str, sp.Expr]:
    """Two independent scalar projections of the induced metric trace.

    For delta gamma/(2a_J^2)=psi hbar+D_mu D_nu E, the normalized tensor
    trace is psi+Box4(E)/4.  On every nonzero scalar harmonic the independent
    traceless-longitudinal coefficient is E.  The constant E mode is a
    scalar-coordinate null representative and is quotiented.
    """

    return {
        "trace_scalar": sp.simplify(psi_at_b1 + box4_E_at_b1 / 4),
        "scalar_longitudinal": sp.simplify(E_at_b1),
    }


def reduced_homogeneous_trace(psi_at_b1: sp.Expr) -> sp.Expr:
    """After the momentum equation and E=0 scalar gauge, B_D Y=psi(1)."""

    return sp.sympify(psi_at_b1)


def scalar_trace_ledger() -> dict[str, Any]:
    return {
        "pre_gauge_bulk_vector": [
            "A: radial lapse",
            "B: radial M4 scalar shift",
            "psi: induced Weyl trace",
            "E: induced scalar-longitudinal metric potential",
            "delta_sigma",
        ],
        "induced_metric": (
            "delta gamma_mu_nu/(2a_J^2)="
            "psi hbar_mu_nu+D_mu D_nu E"
        ),
        "B_D": {
            "trace_scalar": "psi(1)+Box4 E(1)/4",
            "scalar_longitudinal": "E(1) on nonzero scalar harmonics",
        },
        "does_not_enter_trace": [
            "A (normal-normal radial lapse)",
            "B (normal-tangential shift)",
        ],
        "matcher_reactions": [
            "eta_tr: normalized matcher trace scalar",
            "eta_L: normalized matcher scalar-longitudinal scalar",
        ],
        "separate_equations": {
            "induced_metric_Dirichlet": "B_D Y=0",
            "bulk_scalar": "delta_sigma(1)=0",
            "momentum": "W=0 fixes B after variation",
            "reaction": "Pi_tr=eta_tr and Pi_L=eta_L",
            "gauge": "E=0 may be chosen only after the momentum equation",
        },
        "homogeneous_reduction": {
            "E": 0,
            "B_D": "psi(1)",
            "minimum_condition_recovered": "psi(1)=0",
            "active_matcher_reaction": "eta_tr",
            "eta_L": "Ward-dependent reaction paired with the removed E row",
        },
    }


def matcher_hessian_bilinear(
    psi1: sp.Expr,
    eta1: sp.Expr,
    psi2: sp.Expr,
    eta2: sp.Expr,
) -> sp.Expr:
    """Polarized matcher Hessian in the v6.28 doubled-Hessian convention."""

    return sp.simplify(-(eta1 * psi2 + eta2 * psi1))


def kkt_block_matrix() -> list[list[str]]:
    """Reduced homogeneous strong KKT blocks on (A,psi,s,eta_tr)."""

    return [
        ["L_AA", "L_Apsi", "0", "0"],
        ["L_psiA", "L_psipsi", "0", "-B_D^dagger"],
        ["0", "0", "L_sigma", "0"],
        ["0", "-B_D", "0", "0"],
    ]


def kkt_operator_ledger() -> dict[str, Any]:
    return {
        "extended_vector": [
            "A",
            "psi",
            "delta_sigma",
            "eta_tr",
        ],
        "pre_gauge_boundary_extension": ["E", "eta_L"],
        "matrix": kkt_block_matrix(),
        "L_bulk": v628.L0_L1_block_ledger(),
        "B_D": "endpoint evaluation psi -> psi(1)",
        "B_D_dagger": "endpoint delta distribution in the psi equation",
        "matcher_sign": (
            "minus because S_match=Lambda(h-gamma); "
            "Q_match=-(eta_1 psi_2+eta_2 psi_1)"
        ),
        "matcher_normalization": (
            "eta_tr absorbs 2a_J^2 hbar_mu_nu delta Lambda^(mu nu) and "
            "uses the same doubled-Hessian convention as v6.28"
        ),
        "strong_equations": [
            "L_AA A+L_Apsi psi=f_A",
            "L_psiA A+L_psipsi psi-B_D^dagger eta_tr=f_psi",
            "L_sigma s=f_sigma",
            "B_D psi=b_D",
        ],
        "natural_boundary_reaction": "P_psi(1)-eta_tr=r_eta",
        "scalar_boundary": "s(1)=0",
        "intrinsic_B1_Hessian_included": False,
        "quadratic_reconstruction": (
            "integral(Q_g+Q_sigma)dt "
            "-eta_tr psi(1), polarized before taking equations"
        ),
        "operator_type": (
            "symmetric indefinite saddle operator, not a Robin realization"
        ),
        "result": OPERATOR_RESULT,
    }


def extended_green_current(
    A1: sp.Expr,
    psi1: sp.Expr,
    s1: sp.Expr,
    eta1: sp.Expr,
    A2: sp.Expr,
    psi2: sp.Expr,
    s2: sp.Expr,
    eta2: sp.Expr,
    t: sp.Expr = T,
) -> sp.Expr:
    """Bulk current plus the finite-dimensional matcher pairing."""

    bulk = v628.green_current(A1, psi1, s1, A2, psi2, s2, t)
    return sp.simplify(bulk + psi1 * eta2 - psi2 * eta1)


def green_adjoint_ledger() -> dict[str, Any]:
    return {
        "bulk_current": (
            "d(A1 psi2-A2 psi1)"
            "-2cPP(psi1 psi2'-psi1' psi2)"
            "+2Z5 a0^4/N0(s1 s2'-s1' s2)"
        ),
        "matcher_pairing": "psi1 eta2-psi2 eta1",
        "extended_current": (
            "J_D=J_bulk+psi1 eta2-psi2 eta1"
        ),
        "pole": (
            "regular A,psi,s have even expansions; coefficientwise "
            "J_D(0)=0 and no matcher variable lives at the pole"
        ),
        "KKT_domain": {
            "bulk": "regular radial fields with s(1)=0",
            "endpoint_trace": (
                "psi(1) is retained in the extended saddle space and paired "
                "with eta_tr"
            ),
            "gauge": (
                "endpoint-preserving radial diffeomorphisms xi(0)=xi(1)=0 "
                "are quotiented"
            ),
        },
        "constrained_realization": {
            "Dirichlet": "psi(1)=0",
            "reaction": "eta_tr=P_psi(1)",
            "scalar": "s(1)=0",
        },
        "adjoint_domain": (
            "the same regular saddle domain; the matcher pairing cancels the "
            "canonical-momentum endpoint current"
        ),
        "domains_equal": True,
        "self_adjointness_scope": (
            "formally self-adjoint as an indefinite KKT saddle operator; "
            "no positive-definite operator claim"
        ),
        "result": ADJOINT_RESULT,
    }


def metric_modulus_dirichlet_residual() -> sp.Expr:
    return sp.simplify(v628.metric_modulus()["psi"].subs(T, 1))


def fixed_h_kernel_ledger() -> dict[str, Any]:
    return {
        "radial_gauge": (
            "(A,psi)=(-xi',-(a0'/a0)xi), xi(0)=xi(1)=0; quotient"
        ),
        "metric_modulus": {
            "representative": "z_A=sec^2(pi t/4), z_psi=1",
            "Dirichlet_residual": int(metric_modulus_dirichlet_residual()),
            "admitted": False,
        },
        "scalar_Jacobi": {
            "vector": "(A,psi,s,eta_tr)=(0,0,u1,0)",
            "admitted": True,
            "normalization": "integral_0^1 N0 a0^4 u1^2 dt=1",
        },
        "threading": "W=0 by the full parent momentum constraint",
        "matcher_only": (
            "Y=0 forces eta_tr=0 through P_psi-eta_tr=0; no multiplier zero mode"
        ),
        "curvature_probe": "external fixed-h source, not a radial kernel vector",
        "background_rescaling": "same excluded z direction",
        "quotient_kernel": "span{u1}",
        "kernel_dimension": 1,
        "adjoint_kernel": "span{u1}",
        "adjoint_kernel_dimension": 1,
        "Fredholm_index": 0,
        "closed_range": True,
        "closed_range_reason": (
            "regular singular Sturm-Liouville scalar block plus a finite-rank "
            "KKT boundary extension on a compact interval; the metric quotient "
            "has no Dirichlet zero mode"
        ),
        "compatibility": (
            "<u1,f_sigma>_w=0; metric sources obey the radial Noether identity"
        ),
        "result": RANGE_RESULT,
    }


def scalar_projector_formula() -> str:
    return "Q_D f=f-u1 integral_0^1 N0 a0^4 u1 f_sigma dt"


def metric_areal_inverse(source_A: sp.Expr) -> dict[str, sp.Expr]:
    """Exact metric inverse on the Noether-compatible range in areal gauge.

    Fixed-h Dirichlet data permit the endpoint-preserving gauge choice
    psi=0.  The algebraic Hamiltonian row then fixes A.  The remaining metric
    row is precisely the source Noether-compatibility condition, and the
    matcher reaction is the endpoint canonical momentum.
    """

    c = v628.metric_q0_coefficients(T)
    weight = v628.radial_weight(T)
    l_aa = sp.simplify(2 * c["cAA"] / weight)
    lapse = sp.simplify(source_A / l_aa)
    zero = sp.Integer(0)
    reaction = sp.simplify(
        v628.metric_boundary_momentum(lapse, zero, T).subs(T, 1)
    )
    return {"A": lapse, "psi": zero, "eta_tr": reaction}


def inverse_ledger() -> dict[str, Any]:
    return {
        "projector": scalar_projector_formula(),
        "complement": (
            "endpoint-preserving radial-gauge quotient, fixed-h psi(1)=0, "
            "and scalar fields orthogonal to u1"
        ),
        "metric_inverse": {
            "gauge": "areal gauge psi=0",
            "formula": "A=f_A/L_AA",
            "compatibility": "f_psi=L_psiA A by the radial Noether identity",
            "reaction": "eta_tr=P_psi[A,0](1)",
            "metric_kernel": 0,
        },
        "scalar_inverse": (
            "G_sigma^D f=sum_{n>=2} "
            "<u_n,f>_w u_n/(mu_n-mu_1)"
        ),
        "inverse": "G_D=(Q_D mathbb L_D Q_D)^-1",
        "source_compatibility": [
            "<u1,f_sigma>_w=0",
            "metric source satisfies the radial Noether identity",
            "Dirichlet trace source is supplied in the KKT lower row",
        ],
        "normalization": (
            "u_n are unit normalized in weight 4 sin(rho)^4 d rho"
        ),
        "v6_28_Robin_inverse_used": False,
        "generic_pseudoinverse_used": False,
        "result": INVERSE_RESULT,
    }


def _boundary_root(nu: float) -> float:
    endpoint_argument = math.sin(math.pi / 8) ** 2
    return float(hyp2f1(-nu, nu + 4, 2.5, endpoint_argument))


def _normalized_mode(nu: float):
    endpoint = math.pi / 4

    def raw(rho):
        values = np.asarray(rho)
        return hyp2f1(-nu, nu + 4, 2.5, np.sin(values / 2) ** 2)

    norm = 1 / math.sqrt(
        quad(
            lambda rho: 4
            * math.sin(rho) ** 4
            * float(raw(rho)) ** 2,
            0,
            endpoint,
            epsabs=2.0e-13,
            epsrel=2.0e-13,
            limit=300,
        )[0]
    )
    return lambda rho: norm * raw(rho)


@lru_cache(maxsize=1)
def complement_inverse_diagnostics() -> dict[str, Any]:
    """Independent collocation and spectral checks on the first complement mode."""

    first = v629.scalar_kinetic_hypergeometric(60)
    nu1 = float(first["nu"])
    mu1 = float(first["mu"])
    nu2 = float(brentq(_boundary_root, 7.0, 9.0, xtol=5.0e-15))
    mu2 = nu2 * (nu2 + 4)
    gap = mu2 - mu1
    u1 = _normalized_mode(nu1)
    u2 = _normalized_mode(nu2)

    endpoint = math.pi / 4
    pole = 1.0e-5
    mesh = np.linspace(pole, endpoint, 240)

    def ode(rho, state, parameter):
        mode1 = u1(rho)
        source = u2(rho)
        weight = 4 * np.sin(rho) ** 4
        return np.vstack(
            (
                state[1],
                -4 / np.tan(rho) * state[1]
                - mu1 * state[0]
                - source
                + parameter[0] * mode1,
                weight * mode1 * state[0],
            )
        )

    def boundary(left, right, parameter):
        _ = parameter
        return np.array([left[1], right[0], left[2], right[2]])

    solution = solve_bvp(
        ode,
        boundary,
        mesh,
        np.zeros((3, mesh.size)),
        p=np.array([0.0]),
        tol=3.0e-8,
        max_nodes=20000,
    )
    if not solution.success:
        raise RuntimeError(f"fixed-h complement collocation failed: {solution.message}")

    grid = np.linspace(pole, endpoint, 900)
    collocation = solution.sol(grid)[0]
    spectral = u2(grid) / gap
    route_difference = math.sqrt(
        float(
            np.trapezoid(
                4 * np.sin(grid) ** 4 * (collocation - spectral) ** 2,
                grid,
            )
        )
    )
    projector_residual = abs(
        float(
            np.trapezoid(
                4 * np.sin(grid) ** 4 * u1(grid) * collocation,
                grid,
            )
        )
    )
    source_compatibility = abs(
        quad(
            lambda rho: 4
            * math.sin(rho) ** 4
            * float(u1(rho))
            * float(u2(rho)),
            0,
            endpoint,
            epsabs=2.0e-12,
            epsrel=2.0e-12,
            limit=300,
        )[0]
    )

    checks = {
        "route_difference": (route_difference, 1.0e-10),
        "projector_residual": (projector_residual, 1.0e-10),
        "source_compatibility": (source_compatibility, 1.0e-10),
        "Dirichlet_residual": (abs(float(solution.y[0, -1])), 1.0e-10),
        "pole_residual": (abs(float(solution.y[1, 0])), 1.0e-10),
        "matcher_parameter_residual": (
            abs(float(solution.p[0])),
            1.0e-8,
        ),
    }
    for name, (value, bound) in checks.items():
        if not value < bound:
            raise RuntimeError(f"{name}={value!r} exceeds {bound!r}")

    return {
        "methods": [
            "SciPy adaptive collocation with an augmented orthogonality row",
            "independent hypergeometric spectral eigenfunction inversion",
        ],
        "working_precision": {
            "collocation_tolerance": 3.0e-8,
            "hypergeometric_decimal_digits": 60,
        },
        "critical_mu1": float(f"{mu1:.15g}"),
        "next_mu2": float(f"{mu2:.15g}"),
        "positive_complement_gap": float(f"{gap:.15g}"),
        "inverse_norm_upper_bound": float(f"{1 / gap:.15g}"),
        "collocation_nodes": int(solution.x.size),
        "condition_measure": (
            "spectral complement denominator mu2-mu1; no near-zero "
            "complement eigenvalue"
        ),
        **{
            name: {
                "certified_upper_bound": bound,
                "relation": "<",
            }
            for name, (_, bound) in checks.items()
        },
        "convergence": (
            "collocation and the one-mode spectral inverse agree within the "
            "certified weighted-L2 bound"
        ),
    }


def dirichlet_metric_source(
    order: int,
    lower_alpha: Mapping[int, sp.Expr],
) -> sp.Expr:
    """Source for alpha_n from (1+alpha(q))^2=1.

    The expansion convention is alpha(q)=sum q^n alpha_n/n!.  The returned
    value is the right-hand side of
    alpha_n=S_B,n after isolating the nth-order linear trace.
    """

    if order < 1:
        raise ValueError("perturbative order must be positive")
    return sp.simplify(
        -sp.Rational(1, 2)
        * sum(
            sp.binomial(order, k)
            * lower_alpha.get(k, sp.Integer(0))
            * lower_alpha.get(order - k, sp.Integer(0))
            for k in range(1, order)
        )
    )


def warp_to_weyl_coefficient(
    order: int,
    alpha_coefficients: Mapping[int, sp.Expr],
) -> sp.Expr:
    """Convert alpha=a/a0-1 to gamma=a0^2(1+2psi) order by order."""

    if order < 1:
        raise ValueError("perturbative order must be positive")
    return sp.simplify(
        alpha_coefficients.get(order, sp.Integer(0))
        + sp.Rational(1, 2)
        * sum(
            sp.binomial(order, k)
            * alpha_coefficients.get(k, sp.Integer(0))
            * alpha_coefficients.get(order - k, sp.Integer(0))
            for k in range(1, order)
        )
    )


def matcher_reaction_coefficient(
    order: int,
    lapse_coefficients: Mapping[int, sp.Expr],
    weyl_coefficients: Mapping[int, sp.Expr],
    weyl_t_coefficients: Mapping[int, sp.Expr],
) -> sp.Expr:
    """Arbitrary-order fixed-h matcher reaction from the exact P1+GHY density.

    The inputs use the repository's additive induced-metric variable
    gamma=a0^2(1+2 psi)hbar.  Thus a=a0 sqrt(1+2 psi) and N=N0(1+A).
    The exact canonical momentum conjugate to psi is differentiated order by
    order.  A factor two implements the doubled-Hessian convention used by
    the v6.28 radial operator.
    """

    if order < 1:
        raise ValueError("perturbative order must be positive")

    def series(rows: Mapping[int, sp.Expr]) -> sp.Expr:
        return sum(
            Q**n * sp.sympify(value) / sp.factorial(n)
            for n, value in rows.items()
            if 1 <= n <= order
        )

    lapse = series(lapse_coefficients)
    weyl = series(weyl_coefficients)
    weyl_t = series(weyl_t_coefficients)
    a0_j = sp.Integer(1)
    a0_t_j = sp.pi / 4
    n0 = sp.pi / 4
    root = sp.sqrt(1 + 2 * weyl)
    warp = a0_j * root
    warp_t = a0_t_j * root + a0_j * weyl_t / root
    lapse_exact = n0 * (1 + lapse)
    momentum = sp.simplify(
        12
        * KAPPA_1
        * warp**2
        * warp_t
        / lapse_exact
        * a0_j
        / root
    )
    return sp.simplify(
        2 * sp.diff(momentum, Q, order).subs(Q, 0)
    )


def linear_reaction_identity_residual() -> sp.Expr:
    A1, p1, dp1 = sp.symbols("A1 p1 dp1", real=True)
    derived = matcher_reaction_coefficient(
        1,
        {1: A1},
        {1: p1},
        {1: dp1},
    )
    trial_A = A1
    trial_psi = p1 + dp1 * (T - 1)
    inherited = v628.metric_boundary_momentum(
        trial_A,
        trial_psi,
        T,
    ).subs(T, 1)
    return sp.simplify(sp.trigsimp(derived - inherited))


def nonlinear_boundary_ledger() -> dict[str, Any]:
    a1, a2 = sp.symbols("alpha_1 alpha_2", real=True)
    return {
        "exact_trace_equation": "(1+alpha(q,1))^2=1",
        "coordinate_conversion": (
            "alpha=a/a0-1 is the warp response, while the KKT Weyl variable "
            "satisfies psi=alpha+alpha^2/2"
        ),
        "coordinate_conversion_arbitrary_order": (
            "psi_n=alpha_n+(1/2)sum_{k=1}^{n-1}"
            "binomial(n,k)alpha_k alpha_(n-k)"
        ),
        "factorial_convention": "alpha(q)=sum_{n>=1}q^n alpha_n/n!",
        "arbitrary_order": (
            "alpha_n=-(1/2)sum_{k=1}^{n-1}"
            "binomial(n,k)alpha_k alpha_(n-k)"
        ),
        "orders": {
            "1": sp.sstr(dirichlet_metric_source(1, {})),
            "2": sp.sstr(dirichlet_metric_source(2, {1: a1})),
            "3": sp.sstr(
                dirichlet_metric_source(3, {1: a1, 2: a2})
            ),
        },
        "fixed_h_consequence": (
            "alpha_1(1)=0 implies alpha_n(1)=0 recursively for every n; "
            "the nonlinear trace source vanishes on lower-order solutions"
        ),
        "longitudinal_map": (
            "E_n(1)=0 in additive scalar-longitudinal coordinates; "
            "its source is zero after lower-order fixed-h data"
        ),
        "multiplier_reaction": (
            "eta_n is generated at arbitrary order by "
            "matcher_reaction_coefficient from the exact canonical momentum "
            "after converting warp alpha coefficients to additive Weyl psi"
        ),
        "linear_reaction_matches_v6_28_momentum": (
            linear_reaction_identity_residual() == 0
        ),
        "result": NONLINEAR_RESULT,
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_30_1_scientific_sha": V6301_SCIENTIFIC_SHA,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "variation": {
            **_common("BHSM_fixed_h_matcher_second_variation_v6_30_2"),
            "variation": action_variation_ledger(),
            "trace": scalar_trace_ledger(),
        },
        "operator": {
            **_common("BHSM_fixed_h_Dirichlet_KKT_operator_v6_30_2"),
            "operator": kkt_operator_ledger(),
        },
        "adjoint": {
            **_common(
                "BHSM_fixed_h_Green_current_and_adjoint_domain_v6_30_2"
            ),
            "Green_and_domain": green_adjoint_ledger(),
        },
        "inverse": {
            **_common("BHSM_fixed_h_kernel_closed_range_inverse_v6_30_2"),
            "kernel_and_range": fixed_h_kernel_ledger(),
            "inverse": inverse_ledger(),
            "numerical_validation": complement_inverse_diagnostics(),
        },
        "nonlinear": {
            **_common("BHSM_fixed_h_nonlinear_boundary_map_v6_30_2"),
            "boundary_map": nonlinear_boundary_ledger(),
        },
    }


def artifact_bytes() -> dict[str, bytes]:
    return {
        ARTIFACT_FILES[key]: deterministic_json(payload).encode("utf-8")
        for key, payload in artifact_payloads().items()
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for filename, content in artifact_bytes().items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    return paths
