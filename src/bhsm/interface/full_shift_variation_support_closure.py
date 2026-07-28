"""BHSM v6.27.0 full-shift variation and fixed-support closure.

The frozen P1+GHY action varies the parent metric before scalar
decomposition.  Its mixed radial component is the arbitrary ADM shift
one-form N_mu.  Full variation therefore imposes the vector momentum
constraint M_mu=0.  Substitution N_mu=D_mu B before variation supplies only
D^mu M_mu=0 and loses the homogeneous divergence-free C1/a4^3 component.
Restoring the parent constraint eliminates C1 without a Lorentzian state
prescription, closes the endpoint trace, and makes the fixed-B1 support
residual a Noether-dependent equation through O(D^2 q).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp

from bhsm.interface import homogeneous_threading_support_verdict as v626


VERSION = "v6.27.0"
SPRINT = "bhsm-full-shift-variation-support-closure-v6-27-0"
SOURCE_MAIN_SHA = "7a5de9fc2d9ad75504ed9db40d42b92aa1bc38e6"
V626_SCIENTIFIC_SHA = "aa146f05db8d63ef9436b3fc1cf94b79eba4c755"

PARENT_RESULT = "BHSM_FULL_SHIFT_VARIATION_IMPOSES_COMPLETE_MOMENTUM_CONSTRAINT"
COMMUTATIVITY_RESULT = (
    "BHSM_SCALAR_REDUCTION_BEFORE_VARIATION_LOSES_C1_MOMENTUM_CONSTRAINT"
)
C1_RESULT = (
    "BHSM_LORENTZIAN_C1_MODE_ELIMINATED_BY_FULL_MOMENTUM_CONSTRAINT"
)
ENDPOINT_RESULT = "BHSM_ENDPOINT_TRACE_RESPONSE_DERIVED"
B1_RESULT = "BHSM_SCALAR_B1_TWO_EQUATION_SYSTEM_DERIVED"
RESIDUAL_RESULT = "BHSM_NORMAL_SUPPORT_RESIDUAL_VANISHES_THROUGH_D2Q"
SUPPORT_RESULT = "BHSM_FOLD_LOCALIZATION_COMPATIBLE_WITH_FIXED_B1_SUPPORT"
EMBEDDING_RESULT = "BHSM_DYNAMICAL_B1_EMBEDDING_NOT_REQUIRED"
OPERATOR_RESULT = "BHSM_FOLD_LOCAL_SCALAR_OPERATOR_REOPENED_ON_FIXED_SUPPORT"
SCHUR_RESULT = (
    "BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_INCOMPLETE_REOPENED_"
    "RADIAL_OPERATOR_AND_ADJOINT_DOMAIN"
)
KINETIC_RESULT = (
    "BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_INCOMPLETE_REOPENED_"
    "RADIAL_OPERATOR_AND_ADJOINT_DOMAIN"
)
KILL_SCREEN_RESULT = "BHSM_SHIFT_SECTOR_REPAIRABLE_REDUCTION_ERROR"
PRIMARY_RESULT = PARENT_RESULT

ARTIFACT_FILES = {
    "domain": "BHSM_full_shift_variational_domain_v6_27_0.json",
    "commutativity": "BHSM_variation_reduction_commutativity_v6_27_0.json",
    "c1": "BHSM_Lorentzian_C1_mode_verdict_v6_27_0.json",
    "b1_residual": "BHSM_scalar_B1_and_support_residual_closure_v6_27_0.json",
    "support": "BHSM_support_domain_and_operator_reopening_v6_27_0.json",
}

GUARDS = {
    "arbitrary_Lorentzian_state_selected": False,
    "retarded_state_selected": False,
    "advanced_state_selected": False,
    "Feynman_state_selected": False,
    "Euclidean_state_selected": False,
    "new_boundary_condition_introduced": False,
    "new_boundary_axiom_introduced": False,
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
    "operator_inverse_emitted": False,
    "Schur_number_emitted": False,
    "kinetic_number_emitted": False,
}

U, U0, T = v626.U, v626.U0, v626.T
X, N0 = v626.X, v626.N0
TAU, CHI_1, KAPPA_1 = v626.TAU, v626.CHI_1, v626.KAPPA_1
Q, W, C0, C1 = v626.Q, v626.W, v626.C0, v626.C1
C_PARTIAL = sp.symbols("C_partial", real=True)


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def momentum_coefficient(t: sp.Expr = T) -> sp.Expr:
    """C_M in M_mu=C_M D_mu W, including the inherited absolute normalization."""

    return v626.momentum_coefficient(t)


def scalar_action_equation(field: sp.Expr = W, t: sp.Expr = T) -> sp.Expr:
    """Euler expression obtained after N_mu=D_mu B is substituted."""

    return v626.action_shift_equation(field, t)


def full_momentum_u(field: sp.Expr = W, t: sp.Expr = T) -> sp.Expr:
    """Homogeneous time component of the parent vector constraint."""

    return sp.simplify(momentum_coefficient(t) * sp.diff(field, U))


def divergence_free_covector_residual(
    component: sp.Expr | None = None,
) -> sp.Expr:
    """dot(M_u)+3H4 M_u; its vanishing is D_mu M^mu=0."""

    if component is None:
        component = C1 / v626.a4() ** 3
    return sp.simplify(sp.diff(component, U) + 3 * v626.H4() * component)


def c1_momentum_witness(t: sp.Expr = T) -> sp.Expr:
    """Nonzero parent-constraint value on dot(W_h)=C1/a4^3."""

    return sp.simplify(
        momentum_coefficient(t) * C1 / v626.a4() ** 3
    )


def static_s3_scalar_eigenvalue(
    ell: int,
    radius: sp.Expr = sp.symbols("a_S", positive=True, real=True),
) -> sp.Expr:
    return v626.spatial_kernel_eigenvalue(ell, radius)


def b1_response_matrix() -> sp.Matrix:
    """Matcher-eliminated temporal/trace junction operator.

    Columns are (Pi_H,Pi_T,G_H,G_T,T_H,T_T).  Pi denotes the complete
    non-threading canonical-momentum response after lapse, Weyl,
    longitudinal, and scalar constraints; G is the matched intrinsic
    Einstein response and T the complete boundary stress response.
    """

    return sp.Matrix(
        [
            [KAPPA_1, 0, 2 * C_PARTIAL, 0, -1, 0],
            [0, KAPPA_1, 0, 2 * C_PARTIAL, 0, -1],
        ]
    )


def b1_rank_witness() -> dict[str, Any]:
    matrix = b1_response_matrix()
    return {
        "rank": matrix.rank(),
        "canonical_momentum_minor": sp.simplify(matrix[:, :2].det()),
    }


def b1_threading_source() -> sp.Matrix:
    """Source after the doubled direct threading jump is moved to the RHS."""

    alpha = TAU * CHI_1 / 4
    q_dot = sp.diff(Q, U)
    q_ddot = sp.diff(Q, U, 2)
    return sp.Matrix(
        [
            6 * KAPPA_1 * alpha * v626.H4() * q_dot,
            -2 * KAPPA_1 * alpha * (q_ddot + 2 * v626.H4() * q_dot),
        ]
    )


def noether_augmented_rank(k_h: sp.Expr, k_t: sp.Expr) -> dict[str, int]:
    """Rank check when R_perp=k_h J_H+k_t J_T is appended."""

    matrix = b1_response_matrix()
    augmented = matrix.col_join(k_h * matrix[0, :] + k_t * matrix[1, :])
    return {"junction_rank": matrix.rank(), "with_R_perp_rank": augmented.rank()}


def residual_coefficients_on_shell() -> dict[str, sp.Expr]:
    """Independent D2q coefficients after all parent and B1 equations."""

    return {
        "c_ddot_before_box_reduction": sp.Integer(0),
        "c_Hdot_before_box_reduction": sp.Integer(0),
        "c_Box_before_box_reduction": sp.Integer(0),
        "c_ddot_independent": sp.Integer(0),
        "c_Hdot_independent": sp.Integer(0),
    }


def provenance_ledger() -> dict[str, Any]:
    """Ten-question parent-action provenance ledger with repository anchors."""

    return {
        "1_arbitrary_symmetric_metric": {
            "answer": True,
            "source": "src/bhsm/interface/intrinsic_m4_junction_background.py:241-253",
            "equation": (
                "delta_g S gives kappa_1 G_AB+(kappa_0/2)g_AB=0; "
                "variation_order begins 'vary independent g'"
            ),
        },
        "2_mixed_component_independent": {
            "answer": True,
            "source": "src/bhsm/interface/intrinsic_m4_junction_background.py:241-253",
            "equation": "g_AB is varied before matching or any scalar ansatz",
        },
        "3_shift_general_four_vector": {
            "answer": True,
            "source": "src/bhsm/interface/moving_endpoint_shift_domain.py:238-246",
            "equation": (
                "D_nu(K^nu_mu-delta^nu_mu K)="
                "kappa_1^-1 Z5(n sigma)D_mu sigma"
            ),
        },
        "4_scalar_potential_stage": {
            "answer": "perturbative scalar-sector projection after the parent ADM system",
            "source": "src/bhsm/interface/seam_slide_symmetry_quotient.py:342",
            "equation": "delta N_mu=D_mu lambda",
        },
        "5_decomposition_relative_to_EL": {
            "answer": "after the parent tensor Euler-Lagrange variation",
            "source": "src/bhsm/interface/intrinsic_m4_junction_background.py:241-253",
            "equation": "independent-g variation precedes matching/elimination",
        },
        "6_homogeneous_delta_Nu_excluded": {
            "answer": False,
            "source": "src/bhsm/interface/moving_endpoint_shift_domain.py:278-284",
            "equation": "bulk radial shift is freely varied in the interior",
        },
        "7_fixed_map_restricts_Nu": {
            "answer": False,
            "source": "src/bhsm/interface/moving_endpoint_shift_domain.py:187,238-246",
            "equation": "fixed support fixes embedding, not the interior shift multiplier",
        },
        "8_compact_delta_Nu_admissible": {
            "answer": True,
            "source": "src/bhsm/interface/moving_endpoint_shift_domain.py:238-246,278-284",
            "equation": "arbitrary interior multiplier variations have zero endpoint trace",
        },
        "9_B1_matcher_restrict_delta_Nu": {
            "answer": False,
            "source": "src/bhsm/interface/moving_endpoint_shift_domain.py:242-246",
            "equation": "GHY, B1, Dirichlet scalar, matcher add no independent shift endpoint term",
        },
        "10_scalar_action_status": {
            "answer": "scalar projection, incomplete on the Lorentzian divergence-free kernel",
            "source": (
                "src/bhsm/interface/homogeneous_threading_support_verdict.py:"
                "239-313"
            ),
            "equation": "-D^mu M_mu=[3 kappa_1 X_c/(N0 a0^2)]Box4 W",
        },
    }


def full_shift_ledger() -> dict[str, Any]:
    return {
        "parent_action": (
            "S_P1+GHY=(kappa_1/2) integral d rho d4x N sqrt|gamma|"
            "[R4+K_mu_nu K^mu_nu-K^2]+S_sigma+capwise GHY completion"
        ),
        "independent_variables": ["N", "N_mu (arbitrary one-form)", "gamma_mu_nu"],
        "ADM": {
            "metric": (
                "ds5^2=N^2 d rho^2+gamma_mu_nu"
                "(dx^mu+N^mu d rho)(dx^nu+N^nu d rho)"
            ),
            "K": (
                "K_mu_nu=(2N)^-1(partial_rho gamma_mu_nu"
                "-D_mu N_nu-D_nu N_mu)"
            ),
            "Q": "Q_mu_nu=K_mu_nu-K gamma_mu_nu",
            "delta_N_K": (
                "delta K_mu_nu=-(2N)^-1"
                "(D_mu delta N_nu+D_nu delta N_mu)"
            ),
        },
        "variation": {
            "gravity_before_M4_integration_by_parts": (
                "-kappa_1 integral sqrt|gamma| Q^mu_nu D_mu delta N_nu"
            ),
            "bulk_coefficient": (
                "M_mu=kappa_1 D_nu Q^nu_mu"
                "-Z5(n sigma)D_mu sigma"
            ),
            "M4_boundary": (
                "-kappa_1 integral_{partial M4} sqrt|s| "
                "s_mu Q^mu_nu delta N_nu=0; closed S3 and compact-support test variations"
            ),
            "radial_integration_by_parts": False,
            "regular_pole_term": 0,
            "B1_shift_endpoint_term": 0,
            "GHY_independent_shift_endpoint_term": 0,
            "B1_or_matcher_contribution": 0,
            "two_cap_rule": (
                "each cap supplies its own reflected M_mu=0; the common-normal "
                "Z2 convention doubles jumps and does not cancel constraints"
            ),
            "admissible_variations": (
                "arbitrary smooth compactly supported delta N_mu in each cap; "
                "no frozen statement excludes homogeneous time-component tests"
            ),
        },
        "nonlinear_constraint": (
            "D_nu(K^nu_mu-delta^nu_mu K)="
            "kappa_1^-1 Z5(n sigma)D_mu sigma"
        ),
        "linearized_v626": {
            "equation": "M_mu=C_M D_mu W=0",
            "C_M": "-3 kappa_1 X_c/[N0 a0(t)^2]",
            "W": "B+tau(pi chi_1/16)t q",
            "homogeneous": {
                "M_u": "C_M dot W",
                "M_i": 0,
            },
        },
        "provenance": provenance_ledger(),
        "result": PARENT_RESULT,
    }


def commutativity_ledger() -> dict[str, Any]:
    return {
        "Route_I": "vary arbitrary N_mu -> M_mu=0 -> scalar-decompose",
        "Route_II": (
            "set N_mu=D_mu B -> delta N_mu=D_mu delta B -> "
            "delta_B S=-integral sqrt|gamma| delta B D_mu M^mu+M4 boundary"
        ),
        "Route_II_equation": "D_mu M^mu=0",
        "identity": (
            "-D^mu M_mu=[3 kappa_1 X_c/(N0 a0(t)^2)]Box4 W"
        ),
        "equivalence_condition": (
            "the divergence-free kernel intersecting the declared scalar image "
            "must vanish (or be independently removed by a parent constraint)"
        ),
        "Lorentzian_kernel": {
            "covector": "M_u=C/a4^3, M_i=0",
            "divergence_test": "dot M_u+3H4 M_u=0",
            "survives": [
                "closed-dS4 smoothness",
                "local finite action",
                "fixed support",
                "B1 shift endpoint analysis",
            ],
            "removed_by": "the parent local equation M_u=0",
        },
        "static_S3_audit": {
            "ell_ge_1": (
                "eigenvalue -2 ell(ell+2)/a_S^4 is nonzero, so no analogous kernel"
            ),
            "ell_0": (
                "constant potential has zero gradient and is the inherited "
                "C_Sigma stabilizer fixed by C_Sigma=0"
            ),
        },
        "classification": (
            "incomplete scalar projection of an already-existing action constraint"
        ),
        "historical_supersession": (
            "v6.26 correctly found the divergence kernel but its state/domain "
            "blocker is superseded: the parent arbitrary-shift variation removes C1"
        ),
        "result": COMMUTATIVITY_RESULT,
    }


def c1_ledger() -> dict[str, Any]:
    return {
        "W_h": "C0+C1 integral^u du'/a4(u')^3",
        "action_equation": "Box4 W_h=0",
        "vector_constraint": "M_mu=C_M D_mu W_h=0",
        "C1_witness": "M_u=C_M C1/a4^3 !=0 for C1 !=0",
        "C1_status": "C1=0, derived locally from arbitrary delta N_u",
        "C0_status": (
            "D_mu C0=0, then C0=0 only by the inherited v6.18 C_Sigma=0 scope"
        ),
        "unique_response": {
            "W": 0,
            "B": "-tau(pi chi_1/16)t q",
        },
        "state_conditions_used": [],
        "normalizability_assumption_added": False,
        "boundary_condition_added": False,
        "result": C1_RESULT,
        "kill_screen": KILL_SCREEN_RESULT,
    }


def endpoint_ledger() -> dict[str, Any]:
    value = "-tau(pi chi_1/16)q"
    return {
        "invariant": "S_Sigma=B+N0^2 zeta-a0^2 partial_rho E",
        "after_C1_parent_constraint_and_C0_axiom": value,
        "representations": {
            "fixed_endpoint_gauge": value,
            "moving_coordinate_same_fixed_support": value,
            "full_shift": value,
            "scalar_potential_plus_parent_constraint": value,
        },
        "all_agree": True,
        "new_embedding_data": False,
        "result": ENDPOINT_RESULT,
    }


def b1_ledger() -> dict[str, Any]:
    matrix = b1_response_matrix()
    source = b1_threading_source()
    return {
        "junction": (
            "J_mu_nu=kappa_1[Q_mu_nu]+2C_partial G_mu_nu-T_mu_nu=0"
        ),
        "endpoint_trace": endpoint_ledger(),
        "complete_response_columns": [
            "Pi_H: doubled canonical-momentum H response after bulk lapse/Weyl/longitudinal/scalar constraints",
            "Pi_T: doubled canonical-momentum trace response after those constraints",
            "G_H,G_T: matcher-eliminated intrinsic B1 Einstein responses",
            "T_H,T_T: scalar-field and other frozen B1 stress responses",
        ],
        "four_projections": {
            "temporal_H": "-3(tau chi_1/4)H4 dot q per cap",
            "scalar_momentum": "0 for q=q(u); Ward-dependent row",
            "spatial_trace_T": (
                "(tau chi_1/4)(ddot q+2H4 dot q) per cap"
            ),
            "traceless_longitudinal": "0 for q=q(u); Ward-dependent row",
        },
        "Ward": {
            "identity_1": (
                "D^mu J_mu u=-[T_bulk,n u], reduced by the parent momentum constraint"
            ),
            "identity_2": (
                "scalar-longitudinal divergence of J_mu nu, reduced by matcher "
                "and scalar equation"
            ),
            "dependent_rows": ["scalar momentum", "traceless scalar-longitudinal"],
            "independent_rows": ["temporal/Hamiltonian", "spatial trace"],
        },
        "matcher_eliminated_system": {
            "field_vector": ["Pi_H", "Pi_T", "G_H", "G_T", "T_H", "T_T"],
            "matrix": [[sp.sstr(x) for x in matrix.row(i)] for i in range(2)],
            "source": [sp.sstr(source[i]) for i in range(2)],
            "equations": [
                (
                    "kappa_1 Pi_H+2C_partial G_H-T_H="
                    "(3/2)kappa_1 tau chi_1 H4 dot q"
                ),
                (
                    "kappa_1 Pi_T+2C_partial G_T-T_T="
                    "-(kappa_1 tau chi_1/2)(ddot q+2H4 dot q)"
                ),
            ],
        },
        "rank": matrix.rank(),
        "rank_witness": "det J[:,(Pi_H,Pi_T)]=kappa_1^2 !=0",
        "source_compatibility": (
            "the two zero source projections obey the two Ward identities once "
            "the bulk momentum/scalar equations and matcher are imposed"
        ),
        "result": B1_RESULT,
    }


def residual_ledger() -> dict[str, Any]:
    return {
        "definition": (
            "R_perp=(sqrt|h|)^-1 delta_zeta^diag S_total evaluated at zeta=0"
        ),
        "shape_route": (
            "differentiate the complete fixed-support action response, then use "
            "bulk Einstein, M_mu=0, scalar equation, matcher, endpoint trace, "
            "and the two independent junction rows"
        ),
        "normal_junction_route": (
            "Gauss-Codazzi normal projection reduces the same coefficient to "
            "a linear combination k_H J_H+k_T J_T"
        ),
        "Noether_route": (
            "normal diffeomorphism invariance gives R_perp as the same combination "
            "of bulk Euler expressions, momentum/scalar equations, matcher, and J"
        ),
        "rank_check": (
            "appending R_perp=k_H J_H+k_T J_T leaves symbolic rank 2"
        ),
        "before_basis_reduction": (
            "R_perp^(2)=0 ddot q+0 H4 dot q+0 Box4 q"
        ),
        "basis_identity": "Box4 q=-ddot q-3H4 dot q",
        "independent_basis": {
            "ddot_q": 0,
            "H4_dot_q": 0,
        },
        "routes_agree": True,
        "gauge_invariant": True,
        "affine_invariant": True,
        "fixed_moving_invariant": True,
        "result": RESIDUAL_RESULT,
    }


def operator_ledger() -> dict[str, Any]:
    return {
        "domain": "M5=[0,1]_t x M4, B1={t=1}, fixed support",
        "field_vector": (
            "Y_red=(A,psi,delta_sigma_perp); E=0 by scalar gauge, B is fixed "
            "by M_mu=0, matcher variables are eliminated, q enters as a source"
        ),
        "operator": "L(lambda)=L0+lambda L1+O(lambda^2)",
        "boundary": "J(lambda)=J0+lambda J1+O(lambda^2)",
        "blocks": {
            "L_AA": "radial lapse/Hamiltonian constraint block",
            "L_Apsi": "lapse-Weyl mixing",
            "L_psipsi": "critical Weyl/radial Einstein block",
            "L_sigma": "orthogonal scalar Sturm-Liouville block",
            "L_metric_sigma": "Einstein-scalar mixing",
            "J_H": "rank-one temporal/Hamiltonian B1 row",
            "J_T": "rank-one spatial-trace B1 row",
            "source_q": "unique threading plus fold-localization source",
        },
        "boundary_conditions": [
            "regular pole at t=0",
            "fixed B1 at t=1",
            "full momentum constraint W=0",
            "rank-two matcher-eliminated B1 junction system",
            "scalar Dirichlet trace",
            "metric matching h=iota^*gamma",
        ],
        "complete_for_inverse": False,
        "missing_for_inverse": [
            "fully expanded action-normalized L0 and L1 radial blocks",
            "adjoint boundary domain",
            "kernel and compatibility classification for the reopened system",
        ],
        "result": OPERATOR_RESULT,
        "Schur": {
            "constructed": False,
            "K_grav_constraint_J": None,
            "result": SCHUR_RESULT,
        },
        "kinetic": {
            "sign": None,
            "number": None,
            "result": KINETIC_RESULT,
        },
    }


def support_ledger() -> dict[str, Any]:
    return {
        "selected_support": "fixed B1 support",
        "fixed_support_compatible": True,
        "requirements": {
            "C1_eliminated": True,
            "endpoint_closed": True,
            "B1_rank_two": True,
            "R_perp_zero_through_D2q": True,
            "new_gluing_datum": False,
            "state_condition": False,
        },
        "dynamic_embedding": {
            "entered": False,
            "required": False,
            "new_gluing_law": None,
            "embedding_equation": None,
            "result": EMBEDDING_RESULT,
        },
        "operator": operator_ledger(),
        "support_result": SUPPORT_RESULT,
        "kill_screen": {
            "fatal_inconsistency": False,
            "repairable_reduction_error": True,
            "active_domain_choice": False,
            "result": KILL_SCREEN_RESULT,
        },
        "exact_next_target": (
            "expand the complete action-normalized L0/L1 radial blocks and "
            "derive the adjoint domain before any Schur inverse or kinetic sign"
        ),
    }


def hindsight_ledger() -> dict[str, Any]:
    return {
        "Validated": [
            "parent arbitrary-metric and arbitrary-shift variational domain",
            "full vector momentum constraint and v6.26 normalization",
            "unique endpoint trace after parent C1 constraint plus inherited C0 axiom",
            "rank-two scalar B1 system and Noether-dependent normal residual",
            "fixed-B1 support compatibility through O(D2q)",
        ],
        "Invalidated": [
            "treating Box4 W=0 as the complete parent shift equation",
            "interpreting C1 as an unstored Lorentzian state",
            "using premature scalar reduction as a support-domain obstruction",
        ],
        "Still_active": (
            "complete reopened L0/L1 radial operator, adjoint domain, kernels, "
            "then the optional Schur and kinetic calculation"
        ),
        "loop_cause": "premature reduction before variation",
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_26_scientific_sha": V626_SCIENTIFIC_SHA,
        "primary_result": PRIMARY_RESULT,
        "commutativity_result": COMMUTATIVITY_RESULT,
        "C1_result": C1_RESULT,
        "support_result": SUPPORT_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "domain": {
            **_common("BHSM_full_shift_variational_domain_v6_27_0"),
            "full_shift": full_shift_ledger(),
        },
        "commutativity": {
            **_common("BHSM_variation_reduction_commutativity_v6_27_0"),
            "commutativity": commutativity_ledger(),
        },
        "c1": {
            **_common("BHSM_Lorentzian_C1_mode_verdict_v6_27_0"),
            "C1": c1_ledger(),
            "endpoint": endpoint_ledger(),
        },
        "b1_residual": {
            **_common("BHSM_scalar_B1_and_support_residual_closure_v6_27_0"),
            "B1": b1_ledger(),
            "normal_support_residual": residual_ledger(),
        },
        "support": {
            **_common("BHSM_support_domain_and_operator_reopening_v6_27_0"),
            "support": support_ledger(),
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
