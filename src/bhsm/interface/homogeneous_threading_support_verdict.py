"""BHSM v6.26.0 homogeneous Lorentzian threading/support audit.

The fixed-manifold map supplies a unique local particular threading response.
On the action-selected closed-dS4 background, however, variation of the
longitudinal shift potential supplies only the divergence of the radial
momentum constraint.  It permits a source-free homogeneous solution of
Box_4 W=0, whereas the unprojected momentum constraint requires D_mu W=0.
The v6.18 C_Sigma=0 axiom fixes the time-independent spatial zero mode, not
this Lorentzian homogeneous mode.  No state or boundary condition is added,
so the endpoint trace, scalar B1 closure, and support verdict remain blocked.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.26.0"
SPRINT = "bhsm-homogeneous-threading-support-verdict-v6-26-0"
SOURCE_MAIN_SHA = "2236cade321828e26d9a78ecbd5f2a6c67b67982"
V625_SCIENTIFIC_SHA = "df76a3d30a76df90bed2d0aecd0dbaa29af280a0"

THREADING_RESULT = (
    "BHSM_HOMOGENEOUS_THREADING_RESPONSE_BLOCKED_BY_"
    "UNSTORED_LORENTZIAN_STATE"
)
ENDPOINT_RESULT = (
    "BHSM_ENDPOINT_TRACE_RESPONSE_BLOCKED_BY_"
    "UNFIXED_SOURCE_FREE_HOMOGENEOUS_LORENTZIAN_THREADING_MODE"
)
B1_RESULT = (
    "BHSM_SCALAR_B1_TWO_EQUATION_CLOSURE_BLOCKED_BY_"
    "UNFIXED_SOURCE_FREE_HOMOGENEOUS_LORENTZIAN_THREADING_MODE"
)
RESIDUAL_RESULT = (
    "BHSM_NORMAL_SUPPORT_RESIDUAL_D2Q_BLOCKED_BY_"
    "UNFIXED_SOURCE_FREE_HOMOGENEOUS_LORENTZIAN_THREADING_MODE"
)
PRIMARY_RESULT = (
    "BHSM_SUPPORT_DOMAIN_DECISION_BLOCKED_BY_"
    "UNFIXED_SOURCE_FREE_HOMOGENEOUS_LORENTZIAN_THREADING_MODE"
)
EMBEDDING_RESULT = (
    "BHSM_DYNAMICAL_EMBEDDING_DOMAIN_NOT_REACHED_BECAUSE_NECESSITY_NOT_PROVEN"
)
OPERATOR_RESULT = (
    "BHSM_FOLD_LOCAL_SCALAR_OPERATOR_REOPENING_BLOCKED_BY_"
    "UNDECIDED_SUPPORT_DOMAIN"
)
SCHUR_RESULT = (
    "BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_UNDECIDED_SUPPORT_DOMAIN"
)
KINETIC_RESULT = (
    "BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_UNDECIDED_SUPPORT_DOMAIN"
)

ARTIFACT_FILES = {
    "threading": "BHSM_homogeneous_Lorentzian_threading_response_v6_26_0.json",
    "endpoint": "BHSM_endpoint_trace_response_v6_26_0.json",
    "b1": "BHSM_scalar_B1_two_equation_closure_v6_26_0.json",
    "residual": "BHSM_normal_support_residual_D2q_v6_26_0.json",
    "verdict": "BHSM_support_and_fold_operator_verdict_v6_26_0.json",
}

GUARDS = {
    "fixed_support_success_emitted": False,
    "dynamical_embedding_necessity_emitted": False,
    "dynamic_domain_enabled": False,
    "operator_inverse_emitted": False,
    "kinetic_number_emitted": False,
    "arbitrary_Lorentzian_state_selected": False,
    "retarded_state_selected": False,
    "advanced_state_selected": False,
    "Feynman_state_selected": False,
    "Euclidean_state_selected": False,
    "new_boundary_condition_introduced": False,
    "new_action_introduced": False,
    "new_primitive_introduced": False,
    "new_scale_introduced": False,
    "new_corner_term_introduced": False,
    "measured_input_used": False,
    "fitted_coefficient_introduced": False,
    "local_X_field_invented": False,
    "scalar_curvature_inverse_revived": False,
    "chat_only_candidate_imported": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physical_mass_claimed": False,
    "stability_claimed": False,
}

U, U0, T = sp.symbols("u u_0 t", real=True)
X = sp.symbols("X", positive=True, real=True)
N0 = sp.pi / 4
TAU = sp.symbols("tau", nonzero=True, real=True)
CHI_1 = sp.symbols("chi_1", positive=True, real=True)
KAPPA_1 = sp.symbols("kappa_1", positive=True, real=True)
Q = sp.Function("q")(U)
W = sp.Function("W")(U)
C0, C1 = sp.symbols("C_0 C_1", real=True)


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def radial_warp(t: sp.Expr = T) -> sp.Expr:
    return sp.sqrt(2) * sp.sin(sp.pi * t / 4)


def a4(
    u: sp.Expr = U,
    x: sp.Expr = X,
    u0: sp.Expr = U0,
) -> sp.Expr:
    return sp.cosh(sp.sqrt(x) * (u - u0)) / sp.sqrt(x)


def H4(
    u: sp.Expr = U,
    x: sp.Expr = X,
    u0: sp.Expr = U0,
) -> sp.Expr:
    scale = a4(u, x, u0)
    return sp.simplify(sp.diff(scale, u) / scale)


def dS4_background_residual(
    u: sp.Expr = U,
    x: sp.Expr = X,
    u0: sp.Expr = U0,
) -> sp.Expr:
    hubble = H4(u, x, u0)
    return sp.simplify(sp.diff(hubble, u) + hubble**2 - x)


def box_homogeneous(
    field: sp.Expr,
    u: sp.Expr = U,
    x: sp.Expr = X,
    u0: sp.Expr = U0,
) -> sp.Expr:
    return sp.simplify(
        -sp.diff(field, u, 2) - 3 * H4(u, x, u0) * sp.diff(field, u)
    )


def homogeneous_hessian(
    field: sp.Expr,
    u: sp.Expr = U,
    x: sp.Expr = X,
    u0: sp.Expr = U0,
) -> dict[str, sp.Expr]:
    hubble = H4(u, x, u0)
    return {
        "uu": sp.diff(field, u, 2),
        "ui": sp.Integer(0),
        "ij_over_hij": -hubble * sp.diff(field, u),
        "box": box_homogeneous(field, u, x, u0),
    }


def response_coefficient(
    tau: sp.Expr = TAU,
    chi_1: sp.Expr = CHI_1,
) -> sp.Expr:
    return sp.simplify(tau * sp.pi * chi_1 / 16)


def B_particular(
    t: sp.Expr = T,
    q: sp.Expr = Q,
    tau: sp.Expr = TAU,
    chi_1: sp.Expr = CHI_1,
) -> sp.Expr:
    return sp.simplify(-response_coefficient(tau, chi_1) * t * q)


def B_derivatives(
    t: sp.Expr = T,
    q: sp.Expr = Q,
    tau: sp.Expr = TAU,
    chi_1: sp.Expr = CHI_1,
) -> dict[str, sp.Expr]:
    b = B_particular(t, q, tau, chi_1)
    hessian = homogeneous_hessian(b)
    return {
        "D_u_B": sp.diff(b, U),
        "D_u_D_u_B": hessian["uu"],
        "D_i_D_j_B_over_h_ij": hessian["ij_over_hij"],
        "Box4_B": hessian["box"],
    }


def N_u_particular(
    t: sp.Expr = T,
    q: sp.Expr = Q,
    tau: sp.Expr = TAU,
    chi_1: sp.Expr = CHI_1,
) -> sp.Expr:
    return B_derivatives(t, q, tau, chi_1)["D_u_B"]


def coordinate_map_alpha(
    t: sp.Expr = T,
    tau: sp.Expr = TAU,
    chi_1: sp.Expr = CHI_1,
) -> sp.Expr:
    return sp.simplify(response_coefficient(tau, chi_1) * t / N0)


def shift_extrinsic_curvature(
    t: sp.Expr = T,
    q: sp.Expr = Q,
) -> dict[str, sp.Expr]:
    alpha = coordinate_map_alpha(t)
    hubble = H4()
    q_dot = sp.diff(q, U)
    q_ddot = sp.diff(q, U, 2)
    box_q = box_homogeneous(q)
    return {
        "delta_K_uu": sp.simplify(alpha * q_ddot),
        "delta_K_ui": sp.Integer(0),
        "delta_K_ij_over_h_ij": sp.simplify(-alpha * hubble * q_dot),
        "delta_K_trace": sp.simplify(alpha * box_q),
        "delta_Q_uu": sp.simplify(alpha * (q_ddot + box_q)),
        "delta_Q_ui": sp.Integer(0),
        "delta_Q_ij_over_h_ij": sp.simplify(
            alpha * (-hubble * q_dot - box_q)
        ),
        "delta_Q_trace": sp.simplify(-3 * alpha * box_q),
    }


def momentum_coefficient(
    t: sp.Expr = T,
    x: sp.Expr = X,
    kappa_1: sp.Expr = KAPPA_1,
) -> sp.Expr:
    return sp.simplify(
        -3 * kappa_1 * x / (N0 * radial_warp(t) ** 2)
    )


def action_euler_coefficient(
    t: sp.Expr = T,
    x: sp.Expr = X,
    kappa_1: sp.Expr = KAPPA_1,
) -> sp.Expr:
    return sp.simplify(-momentum_coefficient(t, x, kappa_1))


def action_shift_equation(
    field: sp.Expr = W,
    t: sp.Expr = T,
) -> sp.Expr:
    """Euler expression from varying the longitudinal shift potential."""

    return sp.simplify(action_euler_coefficient(t) * box_homogeneous(field))


def momentum_u_equation(
    field: sp.Expr = W,
    t: sp.Expr = T,
) -> sp.Expr:
    """Homogeneous u component of the unprojected momentum constraint."""

    return sp.simplify(momentum_coefficient(t) * sp.diff(field, U))


def minus_divergence_momentum_equation(
    field: sp.Expr = W,
    t: sp.Expr = T,
) -> sp.Expr:
    """Minus the covariant divergence of C_M D_mu field."""

    return sp.simplify(-momentum_coefficient(t) * box_homogeneous(field))


def spatial_kernel_eigenvalue(
    ell: int,
    radius: sp.Expr = sp.symbols("a_S", positive=True, real=True),
) -> sp.Expr:
    if ell < 0:
        raise ValueError("ell must be nonnegative")
    return sp.simplify(-2 * ell * (ell + 2) / radius**4)


def source_free_mode_derivative(
    u: sp.Expr = U,
    x: sp.Expr = X,
    u0: sp.Expr = U0,
) -> sp.Expr:
    return sp.simplify(C1 / a4(u, x, u0) ** 3)


def source_free_mode_box_residual() -> sp.Expr:
    derivative = source_free_mode_derivative()
    second = sp.diff(derivative, U)
    return sp.simplify(-second - 3 * H4() * derivative)


def source_free_momentum_residual() -> sp.Expr:
    return sp.simplify(
        momentum_coefficient() * source_free_mode_derivative()
    )


def action_momentum_kernel_rank() -> dict[str, int]:
    """Ranks on the local homogeneous jet (W_dot,W_ddot).

    The action equation is W_ddot+3H W_dot=0 (one row); the unprojected
    momentum equation is W_dot=0.  Together they have rank two for the
    displayed jet when the derivative consequence is included.
    """

    return {
        "action_equation_rank": 1,
        "momentum_equation_rank": 1,
        "action_kernel_constants": 2,
        "momentum_kernel_constants": 1,
        "unfixed_action_only_modes": 1,
    }


def action_ledger() -> dict[str, Any]:
    return {
        "total": [
            "S_P1,+",
            "S_P1,-",
            "S_GHY,+",
            "S_GHY,-",
            "S_B1",
            "S_match",
            "S_sigma",
        ],
        "P1": (
            "integral sqrt(-g)[kappa_1 R5/2-kappa_0/2"
            "-Z5(grad sigma)^2/2-U5(sigma)]"
        ),
        "GHY_each_cap": "kappa_1 integral_B1 sqrt(-h) K",
        "B1": (
            "integral_B1 sqrt(-h)[C_partial R4"
            "-tau_A Tr(F^2)/4-Z_partial(partial sigma_partial)^2/2]"
        ),
        "matcher": (
            "integral_B1 sqrt(-h) Lambda^(mu nu)"
            "(h_mu nu-iota^*g_mu nu)"
        ),
        "cap_count": 2,
        "common_B1_count": 1,
        "matcher_coefficient": None,
        "new_term_added": False,
        "conventions": {
            "signature_M4": "(-,+,+,+)",
            "K": (
                "K_mu_nu=(2N)^-1(partial_t gamma_mu_nu"
                "-D_mu N_nu-D_nu N_mu)"
            ),
            "Q": "Q_mu_nu=K_mu_nu-K gamma_mu_nu",
        },
    }


def background_ledger() -> dict[str, Any]:
    return {
        "branch": "action-selected maximally symmetric closed dS4",
        "metric": "ds4^2=-du^2+a4(u)^2 dOmega3^2",
        "a4": "X_c^-1/2 cosh[sqrt(X_c)(u-u0)]",
        "X_c": 2,
        "H4": "sqrt(X_c)tanh[sqrt(X_c)(u-u0)]",
        "identity": "dot H4+H4^2=X_c",
        "connection": {
            "Gamma^u_ij": "H4 h_ij",
            "Gamma^i_uj": "H4 delta^i_j",
            "Gamma^u_uu": 0,
        },
        "Ricci": "Ric_mu_nu=3 X_c h_mu_nu",
        "turning_point_used_for_verdict": False,
    }


def threading_ledger() -> dict[str, Any]:
    return {
        "q_sector": "q=q(u), smooth and spatially homogeneous; dot q need not vanish",
        "fixed_map": "rho=ell(q(u))t",
        "B_particular": "-tau(pi chi_1/16)t q(u)",
        "N_u_particular": "-tau(pi chi_1/16)t dot q",
        "derivatives": {
            "D_uD_u_B": "-c t ddot q",
            "D_iD_j_B": "+c t H4 h_ij dot q",
            "Box4_B": "+c t(ddot q+3H4 dot q)",
            "c": "tau pi chi_1/16",
        },
        "completion_variable": "W=B+c t q",
        "P1_GHY_quadratic_density": (
            "(kappa_1/2)N sqrt|gamma| N^-2"
            "[(D_muD_nu W)^2-(Box4 W)^2]"
        ),
        "action_variation": {
            "equation": "[-C_M] Box4 W=0",
            "absolute_coefficient": (
                "[-C_M]=3 kappa_1 X_c/[N0 a0(t)^2]"
            ),
            "origin": "P1 shift Hessian; GHY cancels radial metric derivatives",
        },
        "momentum_constraint": {
            "equation": "M_mu=C_M D_mu W=0",
            "C_M": "-3 kappa_1 X_c/[N0 a0(t)^2]",
            "divergence": "D^mu M_mu=C_M Box4 W",
            "normalization_match": "the action equation is -D^mu M_mu=0",
        },
        "v6_18_recovery": {
            "static_round_S3_operator": "(2/a_S^2)Delta_S3",
            "eigenvalue": "-2 ell(ell+2)/a_S^4",
            "particular_response": "-tau(pi chi_1/16)t Pi_perp q",
        },
        "solutions": {
            "particular": "W=0, hence B=-c t q",
            "action_kernel": (
                "W_h=C0+C1 integral^u du'/a4(u')^3"
            ),
            "momentum_kernel": "W_h=C0",
            "extra_action_only_mode": "C1 integral^u du'/a4(u')^3",
        },
        "C_Sigma_axiom_scope": {
            "exact_inherited_scope": (
                "time-independent spatial ell=0 integration constant in the "
                "v6.18 round-S3 projected domain"
            ),
            "fixes_C0": True,
            "fixes_C1_Lorentzian_mode": False,
            "extension_assumed": False,
        },
        "state_requirement": {
            "local_particular_coefficient_derived": True,
            "complete_response_unique": False,
            "would_require": (
                "an initial/final or Green-state condition eliminating C1"
            ),
            "selected": None,
        },
        "result": THREADING_RESULT,
    }


def endpoint_ledger() -> dict[str, Any]:
    return {
        "invariant": (
            "S_Sigma=B+N0^2 zeta-a0^2 partial_rho E "
            "(partial_t form after fixed-t normalization)"
        ),
        "fixed_gauge": {
            "zeta": 0,
            "E": 0,
            "value": "-tau(pi chi_1/16)q(u)+W_h(u)",
        },
        "moving_coordinate": {
            "transformation": (
                "B->B-N0^2 xi^rho-a0^2 partial_rho L; "
                "zeta->zeta+xi^rho; E->E-L"
            ),
            "value": "-tau(pi chi_1/16)q(u)+W_h(u)",
            "agreement": True,
        },
        "gauge_invariant": True,
        "particular_trace_derived": True,
        "source_free_trace": (
            "W_h=C1 integral^u du'/a4^3 after C0=0"
        ),
        "classification": (
            "gauge-invariant threading state mode, not a physical embedding mode"
        ),
        "junction_origin_complete": False,
        "unique_endpoint_trace": False,
        "result": ENDPOINT_RESULT,
    }


def b1_ledger() -> dict[str, Any]:
    direct = shift_extrinsic_curvature(1)
    return {
        "junction": (
            "J_mu_nu=kappa_1[Q_mu_nu]"
            "+2C_partial G_mu_nu^(4)-T_boundary,mu_nu=0"
        ),
        "direct_particular_one_cap_Q": {
            key: sp.sstr(value)
            for key, value in direct.items()
            if key.startswith("delta_Q")
        },
        "four_scalar_projections": {
            "temporal_threading_piece": (
                "u^mu u^nu delta Q_mu_nu"
                "=-3(tau chi_1/4)H4 dot q at t=1"
            ),
            "scalar_momentum_threading_piece": "0 for q=q(u)",
            "spatial_trace_threading_piece": (
                "(1/3)s^mu_nu delta Q_mu^nu"
                "=(tau chi_1/4)(ddot q+2H4 dot q) at t=1"
            ),
            "traceless_longitudinal_threading_piece": "0 for q=q(u)",
        },
        "Ward": {
            "projection_count": 4,
            "dependency_count": 2,
            "expected_independent_count": 2,
            "identity": "D^mu J_mu nu=-[T_bulk,n nu]",
        },
        "unfixed_mode_contribution": (
            "delta Q_mu_nu[W_h]=N0^-1[-D_muD_nu W_h"
            "+h_mu_nu Box4 W_h]=-N0^-1 D_muD_nu W_h"
        ),
        "missing_insertions": [
            "unique endpoint W_h",
            "complete lapse/Weyl/longitudinal constraint response",
            "action-normalized cap-jump orientation after that response",
        ],
        "matcher_elimination": "algebraic and retained",
        "complete_O_D2q_coefficients": False,
        "two_independent_equations": None,
        "rank_after_complete_insertion": None,
        "compatibility": None,
        "earliest_stop": THREADING_RESULT,
        "result": B1_RESULT,
    }


def residual_ledger() -> dict[str, Any]:
    return {
        "definition": (
            "R_perp=(sqrt|h|)^-1 delta_zeta^diag S_total|zeta=0"
        ),
        "status": "diagnostic shape coefficient; zeta is not varied",
        "independent_routes": {
            "shape": "requires the unique endpoint threading trace",
            "junction": "requires the two completed independent scalar B1 equations",
            "Noether": (
                "relates R_perp to bulk equations, momentum constraint, "
                "junction, matcher, and scalar equations"
            ),
        },
        "derivative_basis": [
            "q",
            "Box4 q",
            "u^mu u^nu D_muD_nu q",
            "H4 u^mu D_mu q",
        ],
        "coefficients": {
            "c0": 0,
            "Box4_q": None,
            "D_0D_0_q": None,
            "H4_D_0_q": None,
        },
        "why_D_0D_0_coefficient_not_unique": (
            "the allowed action-kernel mode W_h has nonzero D_0D_0 W_h "
            "and changes the endpoint Q projection while Box4 W_h=0"
        ),
        "Noether_dependency_rank": None,
        "gauge_invariant": True,
        "affine_invariant": True,
        "fixed_moving_invariant": True,
        "proved_zero": False,
        "proved_nonzero": False,
        "explicit_result": None,
        "result": RESIDUAL_RESULT,
    }


def verdict_ledger() -> dict[str, Any]:
    return {
        "selected_support_domain": None,
        "rejected_alternative": None,
        "fixed_support_compatible": False,
        "fixed_support_failure_proved": False,
        "dynamical_embedding_required": False,
        "primary_result": PRIMARY_RESULT,
        "one_primary_support_result": True,
        "dynamic_embedding": {
            "reached": False,
            "Z2_glue_rule": None,
            "action_differentiability": None,
            "embedding_equation": None,
            "result": EMBEDDING_RESULT,
        },
        "operator": {
            "reopened": False,
            "inverse": None,
            "adjoint_domain": None,
            "kernel": None,
            "result": OPERATOR_RESULT,
        },
        "Schur": {
            "constructed": False,
            "K_grav_constraint_J": None,
            "k_q_E": None,
            "result": SCHUR_RESULT,
        },
        "kinetic": {
            "coefficient": None,
            "sign": None,
            "ghost": None,
            "stability": None,
            "result": KINETIC_RESULT,
        },
        "exact_next_target": (
            "derive an action-selected Lorentzian scalar-shift domain that "
            "eliminates or retains the C1/a4^3 homogeneous momentum mode, "
            "then complete the two scalar B1 equations and R_perp"
        ),
    }


def hindsight_ledger() -> dict[str, Any]:
    return {
        "Validated": [
            "closed-dS4 Hessian and Box4 identities",
            "local particular B=-tau(pi chi_1/16)t q(u)",
            "action equation equals the divergence of the momentum constraint",
            "fixed/moving endpoint invariant agreement",
            "direct threading pieces of delta K and delta Q",
        ],
        "Invalidated": [
            "treating spatial homogeneity as four-dimensional constancy",
            "extending C_Sigma=0 to the Lorentzian C1 mode without domain data",
            "declaring the local particular solution to be the unique response",
        ],
        "Still active": (
            "action-selected Lorentzian scalar-shift zero-mode domain and "
            "the resulting two-equation B1/R_perp closure"
        ),
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_25_scientific_sha": V625_SCIENTIFIC_SHA,
        "threading_result": THREADING_RESULT,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "threading": {
            **_common("BHSM_homogeneous_Lorentzian_threading_response_v6_26_0"),
            "action": action_ledger(),
            "background": background_ledger(),
            "threading": threading_ledger(),
            "hindsight": hindsight_ledger(),
        },
        "endpoint": {
            **_common("BHSM_endpoint_trace_response_v6_26_0"),
            "background": background_ledger(),
            "endpoint": endpoint_ledger(),
        },
        "b1": {
            **_common("BHSM_scalar_B1_two_equation_closure_v6_26_0"),
            "B1": b1_ledger(),
        },
        "residual": {
            **_common("BHSM_normal_support_residual_D2q_v6_26_0"),
            "normal_support_residual": residual_ledger(),
        },
        "verdict": {
            **_common("BHSM_support_and_fold_operator_verdict_v6_26_0"),
            "verdict": verdict_ledger(),
            "hindsight": hindsight_ledger(),
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
    written: list[Path] = []
    for filename, content in artifact_bytes().items():
        path = artifact_dir / filename
        path.write_bytes(content)
        written.append(path)
    return written
