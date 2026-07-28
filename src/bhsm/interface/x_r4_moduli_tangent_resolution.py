"""BHSM v6.23.0 X-to-R4 normalization and M4 response-type theorem.

The frozen scalar-wall ansatz uses a maximally symmetric M4 reference with
Ric(h)=3 X_FRW h and therefore R4=12 X_FRW.  The fold relation
X_FRW=2+tau chi_1 q+O(q^2) is a homogeneous on-shell background relation,
not a declaration of an independent local field X_FRW(x).  The frozen
P1+GHY+B1+matcher action varies the M4 metric independently.  Consequently
the local M4 response to the promoted collective field q(x) must be obtained
from the metric and junction constraints; it is not a scalar-curvature Green
operator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.23.0"
SPRINT = "bhsm-x-r4-moduli-tangent-resolution-v6-23-0"
SOURCE_MAIN_SHA = "1cea7ee804a7a4a07f7b42dc0635a24642d43317"
V622_SCIENTIFIC_SHA = "8034dbfd0865e469a669dea5605114f234b5e119"

NORMALIZATION_RESULT = "BHSM_X_TO_R4_ACTION_NORMALIZATION_DERIVED"
RESPONSE_RESULT = "BHSM_M4_X_RESPONSE_REQUIRES_LOCAL_CONSTRAINT_SOLVE"
RIGHT_INVERSE_RESULT = (
    "BHSM_V6_20_LOCAL_RIGHT_INVERSE_TARGET_REJECTED_BY_CALCULATION"
)
TANGENT_RESULT = (
    "BHSM_HOMOGENEOUS_M4_FAMILY_TANGENTS_DERIVED_AS_DIAGNOSTICS"
)
SCHUR_RESULT = (
    "BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_"
    "INCOMPLETE_LOCAL_CONSTRAINT_OPERATOR_AND_B1_DOMAIN"
)
KINETIC_RESULT = (
    "BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_"
    "INCOMPLETE_LOCAL_CONSTRAINT_OPERATOR_AND_B1_DOMAIN"
)

ARTIFACT_FILES = {
    "normalization": "BHSM_X_R4_action_normalization_v6_23_0.json",
    "response": "BHSM_M4_response_type_decision_v6_23_0.json",
    "tangent": "BHSM_gauge_quotiented_M4_moduli_tangent_v6_23_0.json",
    "double_counting": (
        "BHSM_moduli_constraint_double_counting_audit_v6_23_0.json"
    ),
    "schur": "BHSM_fold_schur_reopening_v6_23_0.json",
}

GUARDS = {
    "measured_inputs_used": False,
    "fitted_coefficients_introduced": False,
    "new_primitive_introduced": False,
    "new_scale_introduced": False,
    "new_action_introduced": False,
    "arbitrary_boundary_parameter_introduced": False,
    "chat_only_candidate_imported": False,
    "local_X_field_invented": False,
    "conformal_tangent_assumed_as_action_input": False,
    "generic_green_operator_emitted": False,
    "K_Weyl_double_counted": False,
    "kinetic_number_emitted": False,
    "physical_mass_claimed": False,
    "stability_claimed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}

X = sp.symbols("X_FRW", positive=True, real=True)
X0 = sp.symbols("X_0", positive=True, real=True)
Q = sp.symbols("q", real=True)
TAU = sp.symbols("tau", real=True)
CHI_1 = sp.symbols("chi_1", positive=True, real=True)
ALPHA = sp.symbols("alpha", real=True)
BETA = sp.symbols("beta", real=True)
U, U0, Z = sp.symbols("u u_0 z", real=True)


def deterministic_json(payload: dict[str, Any]) -> str:
    """Return canonical UTF-8 JSON text with one trailing LF."""

    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def frw_scalar_curvature(
    acceleration: sp.Expr, x_frw: sp.Expr = X
) -> sp.Expr:
    """Closed-FRW identity R4=6(A+X_FRW)."""

    return sp.simplify(6 * (acceleration + x_frw))


def maximally_symmetric_scalar_curvature(x_frw: sp.Expr = X) -> sp.Expr:
    """R4 on the stored Ric(h)=3 X_FRW h scalar-wall branch."""

    return frw_scalar_curvature(x_frw, x_frw)


def static_scalar_curvature(x_frw: sp.Expr = X) -> sp.Expr:
    """R4 on the critical H=A=0, a=X_FRW^(-1/2) branch."""

    return frw_scalar_curvature(sp.Integer(0), x_frw)


def dx_dq(tau: sp.Expr = TAU, chi_1: sp.Expr = CHI_1) -> sp.Expr:
    """Leading fold derivative from X=2+tau chi_1 q+O(q^2)."""

    return sp.simplify(tau * chi_1)


def dr4_dq_maximally_symmetric(
    tau: sp.Expr = TAU, chi_1: sp.Expr = CHI_1
) -> sp.Expr:
    return sp.simplify(
        sp.diff(maximally_symmetric_scalar_curvature(), X)
        * dx_dq(tau, chi_1)
    )


def dr4_dq_static(
    tau: sp.Expr = TAU, chi_1: sp.Expr = CHI_1
) -> sp.Expr:
    return sp.simplify(
        sp.diff(static_scalar_curvature(), X) * dx_dq(tau, chi_1)
    )


def ds4_spatial_factor_fixed_u(
    x_frw: sp.Expr = X,
    u: sp.Expr = U,
    u0: sp.Expr = U0,
) -> sp.Expr:
    """Closed-dS spatial coefficient at fixed dimensional proper time."""

    return sp.cosh(sp.sqrt(x_frw) * (u - u0)) ** 2 / x_frw


def ds4_raw_tangent_fixed_u() -> dict[str, sp.Expr]:
    """Components multiplying du^2 and the unit-S3 metric at fixed u."""

    spatial = ds4_spatial_factor_fixed_u()
    return {
        "uu": sp.Integer(0),
        "S3": sp.simplify(sp.diff(spatial, X)),
    }


def ds4_conformal_tangent_fixed_z() -> dict[str, sp.Expr]:
    """Fixed-z derivative of X^-1[-dz^2+cosh(z)^2 dOmega3^2]."""

    return {
        "zz": sp.diff(-1 / X, X),
        "S3": sp.diff(sp.cosh(Z) ** 2 / X, X),
    }


def ds4_fixed_u_gauge_vector() -> sp.Expr:
    """xi^u relating the fixed-u and fixed-z family derivatives."""

    return sp.simplify((U - U0) / (2 * X))


def ds4_gauge_equivalence_residuals() -> dict[str, sp.Expr]:
    """Verify k_fixed-u-k_conformal=L_xi h componentwise."""

    spatial = ds4_spatial_factor_fixed_u()
    raw = ds4_raw_tangent_fixed_u()
    conformal = {"uu": 1 / X, "S3": -spatial / X}
    xi_u = ds4_fixed_u_gauge_vector()
    lie = {
        "uu": -2 * sp.diff(xi_u, U),
        "S3": sp.simplify(xi_u * sp.diff(spatial, U)),
    }
    return {
        component: sp.trigsimp(
            sp.simplify(raw[component] - conformal[component] - lie[component])
        )
        for component in ("uu", "S3")
    }


def static_raw_tangent_fixed_u() -> dict[str, sp.Expr]:
    """Fixed-u derivative of -du^2+X_FRW^-1 dOmega3^2."""

    return {"uu": sp.Integer(0), "S3": -1 / X**2}


def static_gauge_equivalence_residuals() -> dict[str, sp.Expr]:
    """Verify static raw derivative equals -h/X plus L_xi h."""

    raw = static_raw_tangent_fixed_u()
    conformal = {"uu": 1 / X, "S3": -1 / X**2}
    xi_u = ds4_fixed_u_gauge_vector()
    lie = {"uu": -2 * sp.diff(xi_u, U), "S3": sp.Integer(0)}
    return {
        component: sp.simplify(
            raw[component] - conformal[component] - lie[component]
        )
        for component in ("uu", "S3")
    }


def conformal_dr4(
    scalar_curvature: sp.Expr, conformal_coefficient: sp.Expr
) -> sp.Expr:
    """Homogeneous DR for k=c h, where c is constant on M4."""

    # k=2 phi h with phi=c/2 gives DR=-2 R phi=-c R.
    return sp.simplify(-conformal_coefficient * scalar_curvature)


def local_conformal_promotion_coefficients() -> dict[str, sp.Expr]:
    """Derivative terms for h(q)=[X0/X(q)]h0 at q=0.

    With X'(0)=alpha and X''(0)=beta,
      R[h(q)] = 12 X(q) + C1 Box q + C2 (Dq)^2 + ...
    in the fixed-conformal-coordinate diagnostic representative.
    """

    return {
        "C1": sp.simplify(3 * ALPHA / X0),
        "C2": sp.simplify(
            3 * BETA / X0 - sp.Rational(9, 2) * ALPHA**2 / X0**2
        ),
    }


def schur_affine_shift_residual() -> sp.Expr:
    """Prove Schur invariance under Y=Z+v q for a scalar test block."""

    k, j, ell, v = sp.symbols("K J L v", real=True, nonzero=True)
    k_shift = k + 2 * j * v + ell * v**2
    j_shift = j + ell * v
    return sp.simplify(
        k_shift - j_shift**2 / ell - (k - j**2 / ell)
    )


def source_ledger() -> dict[str, Any]:
    """Repository provenance for q -> delta X -> metric -> action."""

    return {
        "chain": "q -> delta X_FRW -> homogeneous background curvature; local h is varied independently -> action variation",
        "symbols": {
            "X_FRW": {
                "definition": "H^2+a^-2",
                "type": "homogeneous closed-FRW invariant and on-shell branch coordinate",
                "source": "intrinsic_m4_junction_background.py:264,298,337",
            },
            "A_FRW": {
                "definition": "N_partial^-1 dot(H)+H^2",
                "source": "intrinsic_m4_junction_background.py:264,298",
            },
            "H": {
                "definition": "proper-lapse Hubble rate of the closed-FRW B1 metric",
                "source": "intrinsic_m4_junction_background.py:130-140",
            },
            "a": {
                "definition": "closed-FRW scale factor; a=X_FRW^-1/2 at a bounce/static slice",
                "source": "intrinsic_m4_junction_background.py:172-180,191-210",
            },
            "R4": {
                "definition": "four-dimensional scalar curvature",
                "relations": {
                    "general_closed_FRW": "6(A_FRW+X_FRW)",
                    "maximally_symmetric": "12 X_FRW",
                    "critical_static": "6 X_FRW",
                },
            },
            "Ric_h": {
                "definition": "Ric_mu_nu(h)=3 X_FRW h_mu_nu on the scalar-wall reference",
                "source": "scalar_wall_junction_audit.py:269-275",
            },
            "mu": {
                "definition": "-A5/Z5",
                "type": "external fold/action control parameter",
                "source": "scalar_wall_puiseux_fold.py:299-304",
            },
            "epsilon": {
                "definition": "signed scalar amplitude",
                "source": "scalar_wall_puiseux_fold.py:320-327",
            },
            "r": {
                "definition": "|epsilon|>=0",
                "type": "one-sided Puiseux branch amplitude",
            },
            "tau": {
                "definition": "+/-1 curvature-sheet label",
                "not": "normal orientation or scalar sign",
            },
            "q": {
                "definition": "q=r on each sheet after fixed-control Lyapunov-Schmidt projection",
                "type": "promoted collective field",
                "dimension": "dimensionless in the q5=kappa1=Z5=1 normalized representative",
                "source": "scalar_wall_fold_morse_sheet_selection.py:312-335",
            },
            "chi_1": {
                "definition": "positive leading curvature-sheet coefficient",
                "relation": "dX_FRW/dq|0=tau chi_1",
            },
            "delta_X_FRW": {
                "definition": "tau chi_1 q+O(q^2)",
                "clarification": "tau chi_1 is the derivative; multiplying by q gives the linear variation",
            },
            "hbar_mu_nu": {
                "definition": "maximally symmetric reference metric satisfying Ric(hbar)=3X_FRW hbar",
                "status": "no action-level local family hbar[X_FRW(x)] or regulator domain is declared",
            },
            "physical_M4_metric": {
                "definition": "independent B1 metric h_mu_nu during variation",
                "source": "intrinsic_m4_junction_background.py:249-255",
            },
            "Einstein_frame_metric": {
                "definition": "g_E=(F(q)/F0)h",
                "source": "fold_einstein_frame_kinetic_reduction.py:131-172",
            },
            "B1_intrinsic_metric": {
                "definition": "independent h_mu_nu in the intrinsic C_partial R4 action before matcher elimination",
            },
            "matcher_pullback_metric": {
                "definition": "iota^*g_mu_nu",
                "constraint": "h_mu_nu=iota^*g_mu_nu",
            },
        },
        "questions": {
            "1_fold_control_parameter": "mu=-A5/Z5; q is the one-sided collective amplitude, not the external control",
            "2_collective_field": "q=r=|epsilon| on a fixed tau sheet",
            "3_delta_X": "dX_FRW/dq|0=tau chi_1, hence delta X_FRW=tau chi_1 q+O(q^2)",
            "4_q_dimensionless": True,
            "5_X_varied_off_shell": False,
            "6_X_eliminated_before_promotion": True,
            "7_h_independent_during_variation": True,
            "8_action_declares_local_hbar_family": False,
            "9_scalar_wall_is_moduli_reduction": "homogeneous on-shell Lyapunov-Schmidt/background reduction; not a local metric-family substitution theorem",
            "10_v6_20_target_origin": "later attempted completion ansatz, not derived from the frozen action variation",
        },
    }


def normalization_ledger() -> dict[str, Any]:
    return {
        "action_selected_branch": "maximally symmetric scalar-wall reference",
        "X_definition": "X_FRW=H^2+a^-2",
        "action_identity": "Ric_mu_nu(h)=3 X_FRW h_mu_nu",
        "dimension": 4,
        "trace": "R4=h^(mu nu)Ric_mu_nu=4*3 X_FRW=12 X_FRW",
        "fold_relation": "X_FRW(q)=2+tau chi_1 q+O(q^2)",
        "dX_dq": "tau chi_1",
        "dR4_dq": "12 tau chi_1",
        "static_comparison": {
            "branch": "critical R x S3, H=A=0 and a=X_FRW^-1/2",
            "R4": "6 X_FRW",
            "dR4_dq": "6 tau chi_1",
            "no_conflict_reason": "the dS4 and static metrics are distinct homogeneous branches even when X_FRW=2q5",
        },
        "coefficient_one_target": {
            "historical_source": "critical_lapse_weyl_hessian.py:265-305",
            "stored_equation": "delta R4[T_X]=delta X_FRW=tau chi_1 q",
            "classification": "unsupported local-field/right-inverse promotion with an X_FRW-to-R4 normalization error",
            "implicit_X_R_equals_R4": False,
            "implicit_x_R_equals_R4_over_12": False,
            "notation_redefinition_stored": False,
            "historical_artifacts_edited": False,
            "superseded_by": [NORMALIZATION_RESULT, RIGHT_INVERSE_RESULT],
        },
        "verdict": NORMALIZATION_RESULT,
    }


def response_type_ledger() -> dict[str, Any]:
    return {
        "routes": {
            "A_homogeneous_family_derivative": {
                "exists": True,
                "use": "diagnostic background derivative only",
                "selected_for_local_action": False,
                "reason": "the action does not identify the independent h field with hbar[X_FRW(q(x))]",
            },
            "B_local_curvature_right_inverse": {
                "required": False,
                "selected": False,
                "rejected_by_calculation": True,
                "reasons": [
                    "X_FRW(x) is not an action field",
                    "DR_h[k]=source is only one contraction of the metric equation",
                    "TT and gauge components make the scalar equation underdetermined",
                    "the Einstein and junction equations supply the tensor response",
                    "inserting a Green operator would double count independent metric variation",
                ],
                "verdict": RIGHT_INVERSE_RESULT,
            },
            "C_adiabatic_metric_family_promotion": {
                "mathematically_testable": True,
                "selected": False,
                "derivative_corrections": (
                    "for h=(X0/X(q))h0, R4=12X(q)+(X/X0)"
                    "[3 Box ln X-(3/2)(D ln X)^2]"
                ),
                "missing_for_quadratic_expansion": "X''(0) and an action/domain-selected coordinate representative",
                "reason": "the scalar-tensor action retains independent h rather than imposing this ansatz",
            },
            "D_independent_metric_plus_collective_field": {
                "selected": True,
                "action": (
                    "P1 metric g and B1 metric h are independently varied; "
                    "the matcher imposes h=iota^*g after variation"
                ),
                "reduced_form": (
                    "S_J=integral sqrt(-h)[F(q)R4/2-K_J(q)(Dq)^2/2-V_J(q)]"
                ),
                "local_response": "solve the linearized Einstein, radial ADM, B1 junction, and matcher constraints",
            },
        },
        "selected_route": "D",
        "classification": "local constraint response about a homogeneous on-shell fold background",
        "Green_operator_required": False,
        "scalar_curvature_right_inverse_emitted": False,
        "verdict": RESPONSE_RESULT,
    }


def tangent_ledger() -> dict[str, Any]:
    raw = ds4_raw_tangent_fixed_u()
    return {
        "role": "diagnostic homogeneous-family comparison; not the local action response",
        "maximally_symmetric_family": (
            "ds4^2=-du^2+X_FRW^-1 cosh^2(sqrt(X_FRW)(u-u0))dOmega3^2"
        ),
        "fixed_u_raw_derivative": {
            "K_uu": sp.sstr(raw["uu"]),
            "K_ij": (
                "X_FRW^-2[z sinh(z)cosh(z)-cosh(z)^2] gamma_ij, "
                "z=sqrt(X_FRW)(u-u0)"
            ),
        },
        "fixed_dimensionless_time": {
            "coordinate": "z=sqrt(X_FRW)(u-u0)",
            "metric": "X_FRW^-1[-dz^2+cosh(z)^2dOmega3^2]",
            "derivative": "K_mu_nu=-h_mu_nu/X_FRW",
        },
        "fixed_conformal_time": {
            "metric": "X_FRW^-1 sec(eta)^2[-deta^2+dOmega3^2]",
            "derivative": "K_mu_nu=-h_mu_nu/X_FRW",
        },
        "gauge_relation": {
            "equation": "K_fixed_u-K_fixed_z=L_xi h",
            "xi": "(u-u0)/(2X_FRW) partial_u",
            "component_residuals": {
                key: sp.sstr(value)
                for key, value in ds4_gauge_equivalence_residuals().items()
            },
            "changes_u0": False,
            "regularity": "smooth for X_FRW>0 on every finite-u chart",
        },
        "normalization": {
            "conformal_DR": sp.sstr(
                conformal_dr4(
                    maximally_symmetric_scalar_curvature(), -1 / X
                )
            ),
            "required": 12,
            "passed": True,
        },
        "static_family": {
            "metric": "-du^2+X_FRW^-1dOmega3^2",
            "raw_derivative": "K_uu=0, K_ij=-X_FRW^-2 gamma_ij",
            "same_xi_relation_to_conformal": True,
            "component_residuals": {
                key: sp.sstr(value)
                for key, value in static_gauge_equivalence_residuals().items()
            },
            "DR": sp.sstr(
                conformal_dr4(static_scalar_curvature(), -1 / X)
            ),
            "required": 6,
        },
        "boundary_and_matcher": {
            "intrinsic_B1_diffeomorphism": "preserves the whole B1 and matcher when applied simultaneously to h and iota^*g",
            "regulated_time_boundary": (
                "xi vanishes only at u=u0 and is not boundary-preserving at "
                "generic fixed-u regulator endpoints"
            ),
            "repository_regulator_domain": None,
            "boundary_admissible_equivalence_proved": False,
            "canonical_action_representative": None,
            "diagnostic_representative": "fixed conformal time, K=-h/X_FRW",
        },
        "TT_audit": {
            "homogeneous_family_TT_component": 0,
            "general_DR_kernel_contains_TT": True,
            "uniqueness": "unique only within the declared one-parameter homogeneous family and chosen coordinate identification",
            "general_right_inverse_unique": False,
        },
        "local_promotion": {
            "exact_diagnostic_formula": (
                "R4[(X0/X(q))h0]=12X(q)+(X/X0)"
                "[3 Box ln X-(3/2)(D ln X)^2]"
            ),
            "at_q0": {
                key: sp.sstr(value)
                for key, value in local_conformal_promotion_coefficients().items()
            },
            "alpha": "X'(0)=tau chi_1",
            "beta": "X''(0), not fixed by the first-order fold tangent",
            "used_in_action": False,
        },
        "verdict": TANGENT_RESULT,
    }


def double_counting_ledger() -> dict[str, Any]:
    return {
        "independent_variables": {
            "q": "collective scalar zero-mode amplitude",
            "metric_scalar_sector": ["A", "B", "psi", "E"],
            "threading": "v6.18 fixed response plus C_Sigma=0",
        },
        "radial_profile_overlap": {
            "lapse": "N=N0+tau N1 q+constraint correction",
            "Weyl": "a=a0+tau a1 q+constraint correction",
            "longitudinal": "E is an independent scalar-gauge/constraint variable",
            "M4_X_family_tangent": "not added",
        },
        "affine_field_redefinition": {
            "form": "Y_total=Y_constraint+v q",
            "before": "1/2 K(Dq)^2+(Dq)<J,Y>+1/2<Y,LY>",
            "after": {
                "K_prime": "K+2<J,v>+<v,Lv>",
                "J_prime": "J+Lv",
                "L_prime": "L",
            },
            "identity": (
                "K_prime-<J_prime,L^-1J_prime>="
                "K-<J,L^-1J>"
            ),
            "symbolic_residual": sp.sstr(schur_affine_shift_residual()),
            "condition": "only after the same invertible quotient operator and domain are used",
        },
        "no_double_counting_theorem": (
            "the homogeneous radial profiles may be encoded either as an "
            "affine q shift of A,psi or in the direct source, never both; "
            "the independent M4 metric is not supplemented by K^(X)"
        ),
        "Jordan_frame": {
            "F_q_R4": "retained once with independent h",
            "constraint_contribution": "unevaluated until the full local operator/domain is derived",
        },
        "Einstein_frame": {
            "K_Weyl": "3 chi_1^2(4-pi)^2/(16 pi)",
            "count": 1,
            "reason": "generated once by g_E=(F/F0)h after the Jordan reduction",
        },
        "proof_complete_algebraically": True,
        "numerical_constraint_term": None,
    }


def schur_ledger() -> dict[str, Any]:
    return {
        "response_type_resolved": True,
        "action_insertion": {
            "selected_form": "independent h plus q; vary before imposing homogeneous X_FRW(q)",
            "P1_GHY_B1_matcher_scalar": "all retained",
            "two_caps": 2,
            "common_B1": 1,
            "matcher_elimination": "h=iota^*g after independent variation",
        },
        "complete_field_vector": [
            "q",
            "A",
            "B",
            "psi",
            "E",
            "delta sigma_perp",
            "endpoint compensator",
        ],
        "known": {
            "K_scalar": "2 integral a0^2 u1^2 d rho>=2",
            "K_Weyl": "3 chi_1^2(4-pi)^2/(16 pi)",
            "threading": "Pi_perp B=-tau(pi chi_1/16)t Pi_perp q",
            "principal_A_psi_block": (
                "[[0,6kappa1/a0^2],[6kappa1/a0^2,12kappa1/a0^2]]"
            ),
        },
        "not_reopened": {
            "full_operator_L": None,
            "full_source_J": None,
            "lower_order_radial_blocks": None,
            "x_dependent_B1_scalar_junction_conditions": None,
            "moving_endpoint_longitudinal_condition": None,
            "formal_adjoint_domain": None,
            "kernel": None,
            "adjoint_kernel": None,
            "compatibility": None,
        },
        "why_v6_20_tangent_is_not_missing_object": (
            "the action requires the coupled metric/junction equations, not "
            "DR_h^-1 applied to a local X_FRW source"
        ),
        "exact_next_obstruction": (
            "derive the complete local scalar metric constraint operator, "
            "source, and x-dependent B1/matcher moving-endpoint domain from "
            "the frozen action"
        ),
        "arbitrary_green_prescription_required": False,
        "Schur_complement": None,
        "k_q_E": None,
        "kinetic_sign": None,
        "Schur_verdict": SCHUR_RESULT,
        "kinetic_verdict": KINETIC_RESULT,
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_22_scientific_sha": V622_SCIENTIFIC_SHA,
        "normalization_verdict": NORMALIZATION_RESULT,
        "response_type_verdict": RESPONSE_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "normalization": {
            **_common("BHSM_X_R4_action_normalization_v6_23_0"),
            "provenance": source_ledger(),
            "normalization": normalization_ledger(),
        },
        "response": {
            **_common("BHSM_M4_response_type_decision_v6_23_0"),
            "response_type": response_type_ledger(),
        },
        "tangent": {
            **_common(
                "BHSM_gauge_quotiented_M4_moduli_tangent_v6_23_0"
            ),
            "homogeneous_tangent": tangent_ledger(),
        },
        "double_counting": {
            **_common(
                "BHSM_moduli_constraint_double_counting_audit_v6_23_0"
            ),
            "double_counting": double_counting_ledger(),
        },
        "schur": {
            **_common("BHSM_fold_schur_reopening_v6_23_0"),
            "Schur": schur_ledger(),
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
    written = []
    for filename, content in artifact_bytes().items():
        path = artifact_dir / filename
        path.write_bytes(content)
        written.append(path)
    return written
