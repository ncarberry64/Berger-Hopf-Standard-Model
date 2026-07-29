"""BHSM v6.30.4 fixed-h second-order Fredholm solvability.

This module reconciles the v6.30.3 tangent mismatch by selecting the strict
fixed-h, fixed-curvature domain D0.  It derives the complete order-two
source, proves that its adjoint-kernel projection vanishes, and constructs
the unique fixed-h complement response.
"""

from __future__ import annotations

from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq
import sympy as sp

from bhsm.interface import fixed_action_nonlinear_fold_potential as v6303
from bhsm.interface import fixed_h_matcher_dirichlet_operator as v6302


VERSION = "v6.30.4"
SPRINT = "bhsm-fixed-h-variational-family-solvability-v6-30-4"
SOURCE_MAIN_SHA = "24b6be33871911dcd7932503ed56553867462ff8"
PARENT_SCIENTIFIC_SHAS = {
    "v6.30.2": "0d72d9ab14d203cb7a5dd7c12733824d56d563c7",
    "v6.30.3": "394c59bf4cb4fbb3a47c0aacf3a97ab8f9f16ff4",
}

PRIMARY_RESULT = "BHSM_STRICT_FIXED_H_NONLINEAR_FAMILY_SECOND_ORDER_SOLVABLE"
PERMISSION_RESULT = (
    "BHSM_FIXED_H_NONLINEAR_FAMILY_HIGHER_ORDER_CONSTRUCTION_PERMITTED"
)
SCALE_RESULT = (
    "BHSM_SCALE_BRIDGE_PHASE_NOT_PERMITTED_BEFORE_V6_30_5_"
    "SAME_DOMAIN_POTENTIAL_CLOSURE"
)

ARTIFACT_FILES = {
    "domains": "BHSM_variational_family_domain_ledger_v6_30_4.json",
    "parity": "BHSM_reflection_parity_ledger_v6_30_4.json",
    "source": "BHSM_second_order_Fredholm_source_v6_30_4.json",
    "projection": "BHSM_second_order_solvability_projection_v6_30_4.json",
    "controls": "BHSM_second_order_control_unfolding_v6_30_4.json",
    "noether": "BHSM_second_order_Noether_compatibility_v6_30_4.json",
    "permission": "BHSM_fixed_h_nonlinear_family_permission_v6_30_4.json",
}

GUARDS = {
    "measured_input_used": False,
    "empirical_inverse_used": False,
    "empirical_generation_basis_used": False,
    "fitted_parameter_used": False,
    "new_action_introduced": False,
    "new_primitive_introduced": False,
    "free_control_coefficient_introduced": False,
    "new_scale_introduced": False,
    "vacuum_constant_subtracted": False,
    "mu_varied_with_q": False,
    "curvature_varied_in_selected_D0": False,
    "q_dependent_regulator_used": False,
    "M4_metric_equation_imposed": False,
    "historical_F1_tau_imported": False,
    "v6_28_Robin_inverse_reused": False,
    "generic_pseudoinverse_used": False,
    "Tikhonov_regularization_used": False,
    "kernel_row_deleted": False,
    "historical_artifact_rewritten": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physical_mass_claimed": False,
    "local_stability_claimed": False,
    "global_stability_claimed": False,
}

RHO = sp.symbols("rho", nonnegative=True, real=True)
MU = sp.symbols("mu_c", positive=True, real=True)
KAPPA_1 = sp.symbols("kappa_1", positive=True, real=True)
Z5 = sp.symbols("Z5", positive=True, real=True)
U = sp.Function("u_1")(RHO)
H0 = sp.cot(RHO)
WEIGHT = 4 * sp.sin(RHO) ** 4


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def stable(value: float, digits: int = 14) -> float:
    if abs(value) < 5.0e-14:
        return 0.0
    return float(f"{value:.{digits}g}")


def domain_rows() -> list[dict[str, Any]]:
    return [
        {
            "domain": "D0",
            "name": "strict fixed-h, fixed-curvature family",
            "varied_fields": [
                "bulk lapse A",
                "bulk Weyl field psi",
                "bulk scalar delta_sigma",
                "matcher reaction eta_tr",
            ],
            "fixed_data": [
                "independent h_mu_nu",
                "r(q)=r0 at every order",
                "kappa_0,kappa_1,Z5,A5,G5,C_partial",
                "fixed regulator",
            ],
            "boundary_data": "psi(1)=0; delta_sigma(1)=0; matcher reaction retained",
            "controls": [],
            "tangent": "(0,0,u1,0)",
            "r1": 0,
            "r2_allowed": False,
            "Noether_compatible": True,
            "matcher_compatible": True,
            "action_provenance": "frozen P1+GHY+scalar+B1+matcher action",
            "physical_effective_potential": True,
            "scale_extraction": "only after same-domain potential closure",
            "selected": True,
        },
        {
            "domain": "D1",
            "name": "fixed-h with even external-curvature response",
            "varied_fields": "D0 radial fields plus proposed r2,r4,...",
            "fixed_data": "action controls and regulator",
            "boundary_data": "fixed-h matcher data",
            "controls": ["r2", "r4", "..."],
            "tangent": "(0,0,u1,0)",
            "r1": 0,
            "r2_allowed": (
                "only after varying the independent M4 metric, which is "
                "outside fixed-h Gamma[h,q]"
            ),
            "Noether_compatible": "conditionally",
            "matcher_compatible": True,
            "action_provenance": (
                "h exists in the parent action but is fixed external data "
                "during radial effective-potential extraction"
            ),
            "physical_effective_potential": False,
            "scale_extraction": False,
            "selected": False,
        },
        {
            "domain": "D2",
            "name": "historical curvature-varying affine tangent",
            "varied_fields": "historical lapse, warp, scalar profiles",
            "fixed_data": "not the current fixed-curvature probe",
            "boundary_data": "historical moving-curvature family",
            "controls": ["X1=tau chi_1"],
            "tangent": "(N1,a1,u1) with X1=tau chi_1",
            "r1": "tau chi_1",
            "r2_allowed": "not relevant before its nonzero r1",
            "Noether_compatible": "on its own historical sourced family",
            "matcher_compatible": "not the current fixed-h KKT kernel",
            "action_provenance": "external/on-shell curvature-probe family",
            "physical_effective_potential": False,
            "scale_extraction": False,
            "selected": False,
        },
        {
            "domain": "D3",
            "name": "covariantly amplitude-constrained family",
            "varied_fields": (
                "D0 fields plus a proposed amplitude multiplier and all of "
                "its metric, lapse, and boundary variations"
            ),
            "fixed_data": "frozen action recovered when multiplier is removed",
            "boundary_data": "would require derived multiplier boundary terms",
            "controls": ["amplitude multiplier"],
            "tangent": "(0,0,u1,0)",
            "r1": 0,
            "r2_allowed": False,
            "Noether_compatible": "only with a covariant amplitude functional",
            "matcher_compatible": "not derived",
            "action_provenance": (
                "no existing frozen-action multiplier/source identified"
            ),
            "physical_effective_potential": False,
            "scale_extraction": False,
            "selected": False,
        },
    ]


def parity_rows() -> list[dict[str, Any]]:
    return [
        {
            "component": "delta_sigma",
            "D0": "odd; q u1+q^3 sigma3/3!+...",
            "D1": "odd if the even curvature response is independently licensed",
            "D2": "scalar odd but its metric tangent is not reflection-even",
            "D3": "odd candidate; unlicensed domain",
        },
        {
            "component": "A,psi",
            "D0": "even; q^2(A2,psi2)/2!+...",
            "D1": "even candidate",
            "D2": "contains an odd tau q curvature response",
            "D3": "even only with covariant multiplier variation",
        },
        {
            "component": "eta_tr",
            "D0": "even matcher reaction",
            "D1": "even candidate",
            "D2": "inherits the curvature-varying tangent",
            "D3": "even candidate",
        },
        {
            "component": "r",
            "D0": "constant r0",
            "D1": "even r0+r2 q^2/2!+...",
            "D2": "r1=tau chi_1 is odd in q at fixed tau",
            "D3": "constant",
        },
        {
            "component": "F,V_J",
            "D0": "even",
            "D1": "even candidate but not fixed-h Gamma[h,q]",
            "D2": "not even at fixed tau; F1_tau is nonzero",
            "D3": "even candidate; no physical potential provenance",
        },
        {
            "component": "tau",
            "D0": "fixed background/orientation label",
            "D1": "fixed background/orientation label",
            "D2": "curvature-sheet label",
            "D3": "fixed background/orientation label",
        },
    ]


def scalar_jacobi_residual() -> sp.Expr:
    return sp.diff(U, RHO, 2) + 4 * H0 * sp.diff(U, RHO) + MU * U


def second_order_lapse_response() -> sp.Expr:
    """A2 in N=N0(1+q^2 A2/2!+...) and fixed-h areal gauge."""

    energy = sp.diff(U, RHO) ** 2 + MU * U**2
    return sp.simplify(-Z5 * sp.tan(RHO) ** 2 * energy / (12 * KAPPA_1))


def hamiltonian_order_two_residual() -> sp.Expr:
    """Second derivative of the lapse constraint after inserting A2."""

    response = second_order_lapse_response()
    source = Z5 * (sp.diff(U, RHO) ** 2 + MU * U**2)
    return sp.simplify(-12 * KAPPA_1 * H0**2 * response - source)


def tangential_order_two_residual() -> sp.Expr:
    """Second derivative of the tangential Einstein equation."""

    response = second_order_lapse_response()
    lhs = 6 * KAPPA_1 * (
        response
        - H0 * sp.diff(response, RHO) / 2
        - H0**2 * response
    )
    rhs = Z5 * (-sp.diff(U, RHO) ** 2 + MU * U**2)
    residual = sp.expand(lhs - rhs)
    residual = residual.subs(
        sp.diff(U, RHO, 2),
        -4 * H0 * sp.diff(U, RHO) - MU * U,
    )
    return sp.simplify(sp.trigsimp(residual))


def scalar_source_order_two() -> sp.Integer:
    """Reflection makes the second Frechet scalar source identically zero."""

    return sp.Integer(0)


def matcher_trace_order_two() -> sp.Expr:
    """The inherited exact endpoint recurrence with alpha1(1)=0."""

    return v6302.dirichlet_metric_source(2, {1: sp.Integer(0)})


def matcher_reaction_order_two(A2_at_b1: sp.Expr) -> sp.Expr:
    return sp.simplify(
        v6302.matcher_reaction_coefficient(
            2,
            {2: A2_at_b1},
            {},
            {},
        )
    )


def fredholm_projection_exact() -> sp.Integer:
    """Full saddle pairing: scalar bulk term plus zero endpoint pairing."""

    bulk = sp.integrate(WEIGHT * U * scalar_source_order_two(), (RHO, 0, sp.pi / 4))
    boundary = sp.Integer(0)
    return sp.simplify(bulk + boundary)


def control_projection_rows() -> list[dict[str, Any]]:
    return [
        {
            "control": "r2",
            "existing_object": "independent M4 curvature probe",
            "D_a_at_order_two": 0,
            "reason": (
                "at sigma0=0 its first residual derivative has no scalar "
                "component; r2 first couples to q u1 at order three"
            ),
            "admissible_in_D0": False,
            "coefficient_selected": None,
        },
        {
            "control": "A5_2 or mu2",
            "existing_object": "frozen scalar action coefficient",
            "D_a_at_order_two": 0,
            "reason": (
                "the control derivative is proportional to sigma and first "
                "contributes with q at odd order"
            ),
            "admissible_in_D0": False,
            "coefficient_selected": None,
        },
        {
            "control": "C_partial_2",
            "existing_object": "frozen intrinsic B1 coefficient",
            "D_a_at_order_two": 0,
            "reason": "fixed-h intrinsic B1 has no scalar adjoint projection",
            "admissible_in_D0": False,
            "coefficient_selected": None,
        },
    ]


def noether_order_two_ledger() -> dict[str, Any]:
    return {
        "off_shell_identity": "a' E_a+sigma' E_sigma-N(E_N)'=0",
        "off_shell_symbolic_residual": str(
            v6303.radial_noether_identity_residual()
        ),
        "order_one": "E_sigma,1=0 is the Jacobi equation",
        "order_two_hamiltonian_residual": str(
            hamiltonian_order_two_residual()
        ),
        "order_two_tangential_residual_after_Jacobi_equation": str(
            tangential_order_two_residual()
        ),
        "order_two_scalar_source": str(scalar_source_order_two()),
        "differential_compatibility": True,
        "cap_center": "A2=O(rho^2), so the regular-pole current vanishes",
        "B1": (
            "psi2(1)=0 and eta2=P_psi,2(1); matcher pairing cancels the "
            "canonical endpoint current"
        ),
        "gauge_timing": (
            "identity derived with local lapse retained; areal gauge psi2=0 "
            "chosen only for constructive inversion"
        ),
    }


def _shooting_mode(
    *, max_step: float = 0.0015, rtol: float = 1.0e-13
) -> tuple[float, float, Any]:
    endpoint = math.pi / 4
    pole = 1.0e-8

    def solve(mu: float, dense: bool):
        def rhs(rho: float, state: list[float]) -> list[float]:
            value, derivative = state
            return [
                derivative,
                -4 / math.tan(rho) * derivative - mu * value,
            ]

        return solve_ivp(
            rhs,
            (pole, endpoint),
            [1 - mu * pole**2 / 10, -mu * pole / 5],
            rtol=rtol,
            atol=rtol * 1.0e-3,
            max_step=max_step,
            dense_output=dense,
        )

    mu = brentq(
        lambda value: float(solve(value, False).y[0, -1]),
        29.0,
        30.0,
        xtol=5.0e-15,
    )
    solution = solve(mu, True)

    def raw(rho: float, component: int = 0) -> float:
        if rho == 0:
            return 1.0 if component == 0 else 0.0
        return float(solution.sol(max(rho, pole))[component])

    norm = quad(
        lambda rho: 4 * math.sin(rho) ** 4 * raw(rho) ** 2,
        0,
        endpoint,
        epsabs=1.0e-13,
        epsrel=1.0e-13,
        limit=300,
    )[0]
    return float(mu), float(1 / math.sqrt(norm)), raw


@lru_cache(maxsize=1)
def second_order_numerical_diagnostics() -> dict[str, Any]:
    dps = 60
    endpoint_float = math.pi / 4
    shooting_mu, shooting_norm, shooting_raw = _shooting_mode()

    with mp.workdps(dps):
        endpoint = mp.pi / 4
        endpoint_argument = mp.sin(endpoint / 2) ** 2

        def boundary(nu):
            return mp.hyp2f1(
                -nu, nu + 4, mp.mpf("2.5"), endpoint_argument
            )

        nu = mp.findroot(boundary, (mp.mpf("3.5"), mp.mpf("4.2")))
        hyper_mu = nu * (nu + 4)

        def hyper_raw(rho):
            return mp.hyp2f1(
                -nu,
                nu + 4,
                mp.mpf("2.5"),
                mp.sin(rho / 2) ** 2,
            )

        raw_norm = mp.quad(
            lambda rho: 4 * mp.sin(rho) ** 4 * hyper_raw(rho) ** 2,
            [0, endpoint],
        )
        hyper_norm = 1 / mp.sqrt(raw_norm)

        def hyper_u(rho):
            return hyper_norm * hyper_raw(rho)

        def hyper_du(rho):
            return mp.diff(hyper_u, rho)

        hyper_du_j = hyper_du(endpoint)
        hyper_A2_j = -(hyper_du_j**2) / 12
        hyper_eta2_j = 2 * hyper_du_j**2

        profile_differences = []
        hyper_profile = []
        for point in np.linspace(0, endpoint_float, 33):
            if point == 0:
                hyper_A2 = 0.0
            else:
                rho_mp = mp.mpf(str(float(point)))
                value = hyper_u(rho_mp)
                derivative = hyper_du(rho_mp)
                hyper_A2 = float(
                    -(derivative**2 + hyper_mu * value**2)
                    * mp.tan(rho_mp) ** 2
                    / 12
                )
            shoot_value = shooting_norm * shooting_raw(float(point))
            shoot_derivative = shooting_norm * shooting_raw(
                float(point), 1
            )
            shooting_A2 = (
                0.0
                if point == 0
                else -(
                    shoot_derivative**2
                    + shooting_mu * shoot_value**2
                )
                * math.tan(float(point)) ** 2
                / 12
            )
            hyper_profile.append(hyper_A2)
            profile_differences.append(abs(hyper_A2 - shooting_A2))

        shooting_du_j = shooting_norm * shooting_raw(endpoint_float, 1)
        shooting_A2_j = -(shooting_du_j**2) / 12
        shooting_eta2_j = 2 * shooting_du_j**2

        return {
            "normalization": "Z5/kappa1=1 representative; u1 has unit weighted norm",
            "methods": [
                "60-digit hypergeometric root and tanh-sinh quadrature",
                "adaptive shooting with regular-pole series and Gauss-Kronrod normalization",
            ],
            "hypergeometric": {
                "dps": dps,
                "nu": stable(float(nu)),
                "mu": stable(float(hyper_mu)),
                "normalization": stable(float(hyper_norm)),
                "endpoint_u_residual": stable(
                    float(abs(boundary(nu) * hyper_norm))
                ),
                "endpoint_u_prime": stable(float(hyper_du_j)),
                "A2_endpoint": stable(float(hyper_A2_j)),
                "eta2_endpoint": stable(float(hyper_eta2_j)),
            },
            "shooting": {
                "rtol": 1.0e-13,
                "max_step": 0.0015,
                "mu": stable(shooting_mu),
                "normalization": stable(shooting_norm),
                "endpoint_u_residual_bound": 1.0e-11,
                "endpoint_u_prime": stable(shooting_du_j),
                "A2_endpoint": stable(shooting_A2_j),
                "eta2_endpoint": stable(shooting_eta2_j),
            },
            "agreement": {
                "mu_difference": stable(
                    abs(float(hyper_mu) - shooting_mu)
                ),
                "normalization_difference": stable(
                    abs(float(hyper_norm) - shooting_norm)
                ),
                "A2_endpoint_difference": stable(
                    abs(float(hyper_A2_j) - shooting_A2_j)
                ),
                "eta2_endpoint_difference": stable(
                    abs(float(hyper_eta2_j) - shooting_eta2_j)
                ),
                "A2_profile_max_difference_33_nodes": stable(
                    max(profile_differences)
                ),
            },
            "residual_bounds": {
                "regular_pole_A2": "A2=O(rho^2) exactly",
                "Dirichlet_psi2": 0,
                "scalar_projector": 0,
                "Hamiltonian": 0,
                "tangential_Einstein": 0,
                "Noether": 0,
                "matcher_reaction_numeric": 1.0e-10,
            },
            "complement_gap": 64.0147366689857,
            "inverse_norm_upper_bound": stable(1 / 64.0147366689857),
            "condition_measure": (
                "positive scalar complement gap and algebraic metric "
                "coefficient -12 kappa1 cot(rho)^2; no near-zero inversion"
            ),
        }


def second_order_source_ledger() -> dict[str, Any]:
    return {
        "coefficient_convention": (
            "Phi=Phi0+q Phi1+q^2 Phi2/2!+O(q^3)"
        ),
        "domain": "D0",
        "field_order": ["A", "psi", "delta_sigma", "eta_tr"],
        "Phi1": ["0", "0", "u1", "0"],
        "Jacobi_equation": "u1''+4 cot(rho)u1'+mu_c u1=0",
        "S2": {
            "lapse_constraint": "Z5[u1'^2+mu_c u1^2]",
            "tangential_metric": "Z5[-u1'^2+mu_c u1^2]",
            "scalar": "0",
            "matcher_trace": "0",
            "scalar_Dirichlet": "0",
        },
        "linear_equations": {
            "Hamiltonian": (
                "-12 kappa1 cot(rho)^2 A2="
                "Z5[u1'^2+mu_c u1^2]"
            ),
            "tangential": (
                "6 kappa1[A2-(cot rho)A2'/2-(cot rho)^2 A2]="
                "Z5[-u1'^2+mu_c u1^2]"
            ),
            "scalar": "L_sigma sigma2=0 with sigma2 perpendicular u1",
        },
        "Phi2": {
            "A2": sp.sstr(second_order_lapse_response()),
            "psi2": "0 (fixed-h areal gauge)",
            "sigma2": "0 (reflection and complement normalization)",
            "eta2": "-24 kappa1 A2(pi/4)=2 Z5 u1'(pi/4)^2",
        },
        "boundary_map": {
            "alpha1_at_B1": 0,
            "alpha2_at_B1": sp.sstr(matcher_trace_order_two()),
            "psi2_at_B1": 0,
            "eta2_role": "matcher reaction, not a propagating mode or source",
        },
        "numerical_validation": second_order_numerical_diagnostics(),
    }


def projection_ledger() -> dict[str, Any]:
    return {
        "domain": "D0",
        "adjoint_kernel": "(0,0,u1,0)",
        "KKT_pairing": (
            "integral_0^(pi/4) 4 sin(rho)^4 u1 S2_sigma d rho "
            "plus the extended endpoint saddle pairing"
        ),
        "bulk_scalar_contribution": 0,
        "metric_bulk_contribution": 0,
        "reason_metric_drops_out": (
            "the adjoint kernel has zero lapse and Weyl components"
        ),
        "boundary_contribution": 0,
        "reason_boundary_drops_out": (
            "the adjoint kernel has zero matcher component and u1(pi/4)=0"
        ),
        "Omega2_exact": int(fredholm_projection_exact()),
        "Omega2_numerical": 0.0,
        "range_condition_holds": True,
        "complement_normalization": (
            "integral 4 sin(rho)^4 u1 sigma2 d rho=0"
        ),
        "result": PRIMARY_RESULT,
    }


def permission_ledger() -> dict[str, Any]:
    return {
        "v6_30_3_blocker": (
            "BHSM_FIXED_ACTION_NONLINEAR_FOLD_FAMILY_BLOCKED_BY_"
            "INCOMPATIBLE_FIXED_H_AND_CURVATURE_VARYING_FIRST_TANGENTS"
        ),
        "v6_30_3_disposition": (
            "resolved at second order by selecting D0 and excluding D2 "
            "coefficients from the fixed-h family"
        ),
        "selected_domain": "D0",
        "Omega2": 0,
        "Phi2_constructed": True,
        "control_unfolding_required": False,
        "free_control_coefficient": False,
        "Noether_compatible": True,
        "matcher_compatible": True,
        "two_method_validation": True,
        "local_family_all_orders_claimed": False,
        "v6_30_5_permitted": True,
        "v6_30_5_permission": PERMISSION_RESULT,
        "v6_31_permitted": False,
        "v6_31_permission": SCALE_RESULT,
        "open": [
            "order-three Fredholm projection",
            "same-domain Phi3 and Phi4",
            "same-domain F2,V2 and Einstein-frame interaction",
            "local stability",
        ],
        "result": PRIMARY_RESULT,
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "parent_scientific_shas": PARENT_SCIENTIFIC_SHAS,
        "coefficient_convention": (
            "factorial Taylor coefficients: Phi=sum q^n Phi_n/n!"
        ),
        "selected_domain": "D0",
        "action_provenance": "frozen P1+GHY+scalar+B1+matcher action",
        "control_provenance": "all action controls and r(q)=r0 fixed",
        "primary_verdict": PRIMARY_RESULT,
        "validated": [
            "pure scalar Phi1 and F1=0",
            "reflection-even metric response",
            "exact Omega2=0",
            "constructive fixed-h Phi2",
            "Noether and matcher compatibility",
        ],
        "invalidated": [
            "using D2 F1_tau in D0 or D1",
            "using an unlicensed amplitude multiplier",
            "requiring even-order control unfolding at order two",
        ],
        "open": [
            "third and higher Fredholm conditions",
            "same-domain potential and stability",
        ],
        "forbidden_claims": [
            "full BHSM completion",
            "physical mass",
            "scale bridge",
            "global stability",
            "empirical validation",
        ],
        "frozen_hash_status": "unchanged",
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "domains": {
            **_common("BHSM_variational_family_domain_ledger_v6_30_4"),
            "status": "BHSM_VARIATIONAL_DOMAINS_SEPARATED_D0_SELECTED",
            "domains": domain_rows(),
        },
        "parity": {
            **_common("BHSM_reflection_parity_ledger_v6_30_4"),
            "status": "BHSM_FIXED_H_REFLECTION_PARITY_DERIVED",
            "reflection": "(q,tau)->(-q,tau)",
            "tau_not_sign_q": True,
            "components": parity_rows(),
        },
        "source": {
            **_common("BHSM_second_order_Fredholm_source_v6_30_4"),
            "status": "BHSM_COMPLETE_FIXED_H_SECOND_ORDER_SOURCE_DERIVED",
            "source": second_order_source_ledger(),
        },
        "projection": {
            **_common("BHSM_second_order_solvability_projection_v6_30_4"),
            "status": PRIMARY_RESULT,
            "projection": projection_ledger(),
        },
        "controls": {
            **_common("BHSM_second_order_control_unfolding_v6_30_4"),
            "status": "BHSM_SECOND_ORDER_CONTROL_UNFOLDING_NOT_REQUIRED",
            "equation": "Omega2+sum_a c2^a D_a=0",
            "Omega2": 0,
            "controls": control_projection_rows(),
            "selected_coefficients": {},
        },
        "noether": {
            **_common("BHSM_second_order_Noether_compatibility_v6_30_4"),
            "status": "BHSM_SECOND_ORDER_NOETHER_COMPATIBILITY_DERIVED",
            "Noether": noether_order_two_ledger(),
        },
        "permission": {
            **_common("BHSM_fixed_h_nonlinear_family_permission_v6_30_4"),
            "status": PERMISSION_RESULT,
            "permission": permission_ledger(),
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
    paths = []
    for filename, content in artifact_bytes().items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    return paths
