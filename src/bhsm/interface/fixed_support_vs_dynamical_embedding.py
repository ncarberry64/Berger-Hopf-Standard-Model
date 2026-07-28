"""BHSM v6.25.0 fixed-support versus dynamical-embedding audit.

The homogeneous cap-length modulus can be localized on a fixed interval by
the pullback rho=ell(q(x))*t.  This produces an ADM shift entirely within the
frozen field content and reproduces the v6.18 spatial threading coefficient.
The same pullback produces a D_mu D_nu q term in the B1 extrinsic curvature.
Its time-dependent spatially homogeneous projection is outside the v6.18
threading theorem.  Consequently the normal-support residual cannot yet be
evaluated on the complete fixed-support equations, and neither candidate
support domain is selected.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.25.0"
SPRINT = "bhsm-fixed-support-vs-dynamical-embedding-v6-25-0"
SOURCE_MAIN_SHA = "4a59a2a3d1dc7e2d21fbc5f0d9e0f69aac28b34e"
V624_SCIENTIFIC_SHA = "94879c94ac8ef5b61d5072a6c4eb1af7d3003b16"
V624_REPRODUCIBILITY_SHA = "16e75be50b12545383b62fd9d0d9ded0915b568a"

LOCALIZATION_RESULT = "BHSM_FIXED_MANIFOLD_LOCALIZATION_MAP_DERIVED"
RESIDUAL_RESULT = (
    "BHSM_NORMAL_SUPPORT_RESIDUAL_BLOCKED_BY_"
    "UNDERIVED_TIME_DEPENDENT_HOMOGENEOUS_THREADING_JUNCTION_RESPONSE"
)
PRIMARY_RESULT = (
    "BHSM_SUPPORT_DOMAIN_DECISION_BLOCKED_BY_"
    "UNDERIVED_TIME_DEPENDENT_HOMOGENEOUS_THREADING_JUNCTION_RESPONSE"
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
    "localization": "BHSM_fixed_manifold_localization_map_v6_25_0.json",
    "residual": "BHSM_normal_support_residual_v6_25_0.json",
    "fixed": "BHSM_fixed_support_compatibility_audit_v6_25_0.json",
    "embedding": "BHSM_Z2_embedding_variational_domain_v6_25_0.json",
    "decision": "BHSM_support_domain_decision_v6_25_0.json",
}

GUARDS = {
    "fixed_support_success_emitted": False,
    "dynamical_embedding_necessity_emitted": False,
    "embedding_domain_invented": False,
    "embedding_equation_invented": False,
    "measured_inputs_used": False,
    "fitted_coefficients_introduced": False,
    "new_primitive_introduced": False,
    "new_action_introduced": False,
    "new_scale_introduced": False,
    "new_corner_term_introduced": False,
    "arbitrary_boundary_condition_introduced": False,
    "arbitrary_regulator_selected": False,
    "local_X_field_invented": False,
    "scalar_curvature_inverse_revived": False,
    "chat_only_candidate_imported": False,
    "generic_pseudoinverse_emitted": False,
    "kinetic_number_emitted": False,
    "physical_mass_claimed": False,
    "stability_claimed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}

T = sp.symbols("t", real=True, nonnegative=True)
Q = sp.symbols("q", real=True)
TAU = sp.symbols("tau", real=True)
CHI_1 = sp.symbols("chi_1", positive=True, real=True)
ELL_2 = sp.symbols("ell_2", real=True)
DQ2 = sp.symbols("(Dq)^2", real=True)
ZETA, B, E_T = sp.symbols("zeta B E_t", real=True)
XI_T, L_T = sp.symbols("xi_t L_t", real=True)


def deterministic_json(payload: dict[str, Any]) -> str:
    """Return canonical UTF-8 JSON with one trailing LF."""

    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def a0(t: sp.Expr = T) -> sp.Expr:
    return sp.sqrt(2) * sp.sin(sp.pi * t / 4)


def lapse0() -> sp.Expr:
    return sp.pi / 4


def a1(t: sp.Expr = T) -> sp.Expr:
    """Stored positive-chi radial warp profile before the sheet factor tau."""

    return sp.simplify(
        CHI_1
        * (
            a0(t) / 4
            - sp.sqrt(2) * t * sp.cos(sp.pi * t / 4) / 4
        )
    )


def length1() -> sp.Expr:
    """Stored first cap-length response before multiplication by tau."""

    return -CHI_1 / 4


def cap_length(
    q: sp.Expr = Q,
    tau: sp.Expr = TAU,
    ell2: sp.Expr = ELL_2,
) -> sp.Expr:
    """Homogeneous cap length through an explicitly unresolved second response."""

    return sp.expand(lapse0() + tau * length1() * q + ell2 * q**2 / 2)


def proper_radius_map(
    t: sp.Expr = T,
    q: sp.Expr = Q,
    tau: sp.Expr = TAU,
    ell2: sp.Expr = ELL_2,
) -> sp.Expr:
    """rho(t,x)=ell(q(x))*t."""

    return sp.expand(t * cap_length(q, tau, ell2))


def shift_potential(
    t: sp.Expr = T,
    q: sp.Expr = Q,
    tau: sp.Expr = TAU,
    ell2: sp.Expr = ELL_2,
) -> sp.Expr:
    """B such that N_mu=D_mu B after pulling proper rho to fixed t.

    The irrelevant q-independent constant is subtracted.
    """

    ell = cap_length(q, tau, ell2)
    return sp.expand(t * (ell**2 - lapse0() ** 2) / 2)


def linear_shift_profile(
    t: sp.Expr = T,
    tau: sp.Expr = TAU,
) -> sp.Expr:
    """Coefficient of q in B at the fold."""

    return sp.simplify(sp.diff(shift_potential(t, Q, tau), Q).subs(Q, 0))


def expected_threading_profile(
    t: sp.Expr = T,
    tau: sp.Expr = TAU,
) -> sp.Expr:
    return sp.simplify(-tau * sp.pi * CHI_1 * t / 16)


def shift_match_residual() -> sp.Expr:
    return sp.simplify(linear_shift_profile() - expected_threading_profile())


def induced_metric_rank_one_coefficient(
    t: sp.Expr = T,
    q: sp.Expr = Q,
    tau: sp.Expr = TAU,
    ell2: sp.Expr = ELL_2,
) -> sp.Expr:
    """Coefficient of D_mu q D_nu q in gamma_mu_nu."""

    ell_q = sp.diff(cap_length(q, tau, ell2), q)
    return sp.expand(t**2 * ell_q**2)


def fixed_lapse_squared(
    derivative_norm: sp.Expr = DQ2,
    t: sp.Expr = T,
    q: sp.Expr = Q,
    tau: sp.Expr = TAU,
    ell2: sp.Expr = ELL_2,
) -> sp.Expr:
    """Fixed-t ADM lapse squared through O((Dq)^2)."""

    ell = cap_length(q, tau, ell2)
    ell_q = sp.diff(ell, q)
    return sp.expand(ell**2 * (1 - t**2 * ell_q**2 * derivative_norm))


def extrinsic_hessian_coefficient(
    t: sp.Expr = T,
    q: sp.Expr = Q,
    tau: sp.Expr = TAU,
    ell2: sp.Expr = ELL_2,
) -> sp.Expr:
    """Coefficient of D_mu D_nu q in the derivative part of K_mu_nu."""

    return sp.simplify(-t * sp.diff(cap_length(q, tau, ell2), q))


def fold_extrinsic_hessian_coefficient(
    t: sp.Expr = T,
    tau: sp.Expr = TAU,
) -> sp.Expr:
    return sp.simplify(
        extrinsic_hessian_coefficient(t, Q, tau).subs(Q, 0)
    )


def endpoint_graph_in_fixed_t(
    q: sp.Expr = Q,
    tau: sp.Expr = TAU,
) -> sp.Expr:
    """Linear moving-coordinate endpoint displacement in background t units."""

    return sp.simplify(tau * length1() * q / lapse0())


def endpoint_threading_invariant(
    b: sp.Expr = B,
    zeta: sp.Expr = ZETA,
    e_t: sp.Expr = E_T,
) -> sp.Expr:
    return sp.expand(b + lapse0() ** 2 * zeta - a0(1) ** 2 * e_t)


def transformed_endpoint_threading() -> sp.Expr:
    transformed_b = B - lapse0() ** 2 * XI_T - a0(1) ** 2 * L_T
    transformed_zeta = ZETA + XI_T
    transformed_e_t = E_T - L_T
    return endpoint_threading_invariant(
        transformed_b, transformed_zeta, transformed_e_t
    )


def threading_gauge_residual() -> sp.Expr:
    return sp.simplify(
        transformed_endpoint_threading() - endpoint_threading_invariant()
    )


def faddeev_popov_matrix() -> sp.ImmutableMatrix:
    """Gauge map for the pair of conditions zeta=0 and E=0."""

    return sp.ImmutableMatrix([[1, 0], [0, -1]])


def affine_schur_residual() -> sp.Expr:
    """Bookkeeping invariance under Y=Z+v q in one scalar test block."""

    k, j, ell, v = sp.symbols("K J L v", nonzero=True, real=True)
    kp = k + 2 * j * v + ell * v**2
    jp = j + ell * v
    return sp.simplify(kp - jp**2 / ell - (k - j**2 / ell))


def fixed_manifold_ledger() -> dict[str, Any]:
    return {
        "result": LOCALIZATION_RESULT,
        "domain_F": {
            "manifold": "M5=[0,1]_t×M4 on each cap",
            "B1": "{t=1}",
            "embedding": "fixed inclusion iota(x)=(1,x)",
            "physical_embedding_variation": 0,
            "fields": [
                "N(t,x)",
                "N_mu(t,x)",
                "gamma_mu_nu(t,x)",
                "sigma(t,x)",
                "independent h_mu_nu(x)",
                "Lambda_mu_nu(x)",
            ],
        },
        "homogeneous_profiles": {
            "ell0_equals_N0": "pi/4",
            "ell1_equals_N1": "-chi_1/4 before tau",
            "a0": "sqrt(2)sin(pi t/4)",
            "a1": "chi_1[a0/4-sqrt(2)t cos(pi t/4)/4]",
            "sigma1": "s u1 with u1(1)=0",
            "delta_X": "tau chi_1",
            "endpoint": "a1(1)=0",
            "junction_tangent": "delta a'_J=delta X/2 after domain correction",
        },
        "local_q_ansatz": {
            "N": "N0+tau N1 q+delta N_constraint",
            "a": "a0+tau a1 q+delta a_constraint",
            "sigma": "s u1 q+delta sigma_perp",
            "N_mu": "D_mu B with B=t[ell(q)^2-ell0^2]/2",
        },
        "affine_convention": (
            "the homogeneous ell1,a1,u1 profiles are included as affine "
            "q-dependent fixed-domain fields; they are not duplicated in J_q"
        ),
        "coordinate_map": {
            "proper_domain": "0≤rho≤ell(q(x))",
            "fixed_domain": "rho=ell(q(x))t, 0≤t≤1",
            "differential": "d rho=ell dt+t ell_q D_mu q dx^mu",
            "invertible_near_fold": True,
        },
        "ADM_components": {
            "g_tt": "ell^2",
            "N_mu": "t ell ell_q D_mu q",
            "B": "t[ell(q)^2-ell0^2]/2",
            "gamma_mu_nu": (
                "gamma_tilde_mu_nu(ell t,q)"
                "+t^2 ell_q^2 D_mu q D_nu q"
            ),
            "N_squared": (
                "ell^2[1-t^2 ell_q^2(Dq)^2]+O(D^4)"
            ),
            "linear_B": "-tau(pi chi_1/16)t q",
            "linear_shift_match_residual": sp.sstr(shift_match_residual()),
        },
        "derivative_placement": {
            "O(Dq)": "N_mu=t ell ell_q D_mu q",
            "O(D2q)": (
                "delta K_mu_nu contains -t ell_q D_muD_nu q; "
                "at q=0 this is +tau(chi_1/4)t D_muD_nu q"
            ),
            "O((Dq)^2)": [
                "rank-one induced metric t^2 ell_q^2 D_muq D_nuq",
                "lapse correction -ell^2 t^2 ell_q^2(Dq)^2",
                (
                    "the complete K_mu_nu coefficient also contains ell_qq "
                    "and q-dependent connection/profile terms"
                ),
            ],
            "scalar_pullback": (
                "sigma_fixed(t,x)=sigma_tilde(ell(q)t,q); "
                "sigma_fixed(1,x)=0 because u1(1)=0"
            ),
            "matcher_pullback": (
                "h_mu_nu equals the complete fixed-t gamma_mu_nu at t=1, "
                "including the rank-one (Dq)^2 term"
            ),
        },
        "second_response": {
            "ell2": "not stored",
            "a2_N2": "not stored",
            "needed_for_complete_quadratic_coefficient": True,
            "needed_for_linear_O(D2q)_support_test": False,
        },
    }


def gauge_ledger() -> dict[str, Any]:
    fp = faddeev_popov_matrix()
    return {
        "gauge_functions": ["xi^t(t,x)", "L(t,x)"],
        "transformations": {
            "A": "A-N0^-1 partial_t(N0 xi^t)",
            "B": "B-N0^2 xi^t-a0^2 partial_t L",
            "psi": "psi-(a0'/a0)xi^t",
            "E": "E-L",
            "delta_sigma": "delta sigma-sigma0' xi^t",
            "zeta": "zeta+xi^t|B1",
        },
        "endpoint_invariant": "S_Sigma=B+N0^2 zeta-a0^2 partial_t E",
        "symbolic_invariance_residual": sp.sstr(threading_gauge_residual()),
        "moving_to_fixed": {
            "moving_graph": "zeta_t=tau ell1 q/ell0 at B1",
            "parameter": "xi^t=-t(tau ell1/ell0)q",
            "fixed_graph": "zeta=0",
            "generated_B": "tau ell0 ell1 t q=-tau(pi chi_1/16)t q",
            "pullback_data_equal": True,
        },
        "gauge_fix": {
            "conditions": ["zeta=0", "E=0"],
            "FP_matrix": [
                [int(entry) for entry in row] for row in fp.tolist()
            ],
            "determinant": sp.sstr(fp.det()),
            "rank": fp.rank(),
            "nonsingular": True,
        },
        "pole_and_B1": {
            "pole": "xi^t(0,x)=0",
            "B1": "xi^t(1,x)=-zeta(x) before fixing",
            "compatible_interpolation": "xi^t=-t zeta is smooth",
            "residual_normal_gauge": "xi^t(1,x)=0 after zeta=0",
        },
        "support_count": {
            "coordinate_graph_variables_before_fix": 1,
            "normal_gauge_values_used": 1,
            "M4_scalar_gauge_functions": 1,
            "M4_scalar_gauge_conditions": 1,
            "physical_embedding_scalars_added": 0,
            "unpaired_support_variable": None,
            "support_specific_count_closes": True,
            "full_constraint_reduced_propagating_count": None,
        },
    }


def boundary_equation_ledger() -> dict[str, Any]:
    return {
        "tensor_junction": (
            "J_mu_nu=kappa_1[Q_mu_nu]+2C_partial G_mu_nu^(4)"
            "-T_boundary,mu_nu=0"
        ),
        "scalar_projections_on_closed_FRW_foliation": {
            "Hamiltonian": "u^mu u^nu J_mu_nu=0",
            "momentum": "D^i(u^mu s_i^nu J_mu_nu)=0",
            "spatial_trace": "(1/3)s^mu_nu J_mu^nu=0",
            "traceless_longitudinal": (
                "(D^iD^j-D_sp^2 s^ij/3)J_ij=0"
            ),
        },
        "dependency": {
            "identity": (
                "D^mu J_mu_nu=-[T_bulk,n nu] after intrinsic Bianchi"
            ),
            "bulk_momentum_constraint": "[T_bulk,n nu] supplies the same Ward source",
            "scalar_Ward_relations": 2,
            "scalar_projection_count": 4,
            "independent_scalar_junction_combinations": 2,
            "dependency_rank": 2,
            "independent_rank": 2,
            "double_counted": False,
        },
        "matcher": {
            "equation": "h_mu_nu=iota^*g_mu_nu at fixed t=1",
            "scalar_matcher_components": 2,
            "multiplier_eliminated": True,
            "propagating_multiplier": False,
            "algebraic_closure": True,
        },
        "bulk_scalar": {
            "equation": "Z5 box_5 sigma-U5'(sigma)=0",
            "B1_data": "odd Dirichlet sigma|B1=0",
            "linear_pullback": "u1(1)q=0",
        },
        "local_q_status": {
            "spatial_Pi_perp_junction_threading": "covered by v6.18",
            "time_dependent_spatially_homogeneous_junction_threading": None,
            "endpoint_trace_response": None,
            "all_scalar_B1_equations_closed": False,
        },
    }


def normal_residual_ledger() -> dict[str, Any]:
    return {
        "primary_definition": (
            "R_perp[q]=(sqrt|h|)^-1 delta_zeta^diag S_total|zeta=0, "
            "where delta_zeta^diag is a diagnostic simultaneous normal "
            "domain displacement and field pullback, not a varied field"
        ),
        "covariance": "scalar on the common B1",
        "action_origin": [
            "two P1 cap domain responses",
            "two capwise GHY responses",
            "one intrinsic B1 response",
            "exact matcher pullback response",
            "bulk and boundary scalar responses",
        ],
        "equivalent_routes": {
            "normal_system": (
                "normal projection of the cap Einstein constraints plus the "
                "contraction of the tensor junction with the background "
                "extrinsic curvature and scalar/matcher boundary equations"
            ),
            "Noether": (
                "boundary coefficient in the five-dimensional diffeomorphism "
                "identity for xi^A=zeta n^A"
            ),
            "shape": (
                "diagnostic shape derivative of P1+GHY+B1+matcher+scalar "
                "without adding zeta to the configuration space"
            ),
        },
        "linearized_structure": (
            "R_perp^(1)=sum_caps c_H delta E_nn"
            "+Kbar^(mu nu)delta J_mu_nu"
            "+terms proportional to the scalar and matcher boundary equations"
        ),
        "normalization_status": (
            "the coefficient c_H and complete endpoint terms require the "
            "unexpanded fixed-support quadratic action; no arbitrary "
            "normalization is assigned"
        ),
        "homogeneous_order": {
            "O(q)": "zero on the stored homogeneous bulk and junction tangent",
            "evidence": "a1(1)=u1(1)=0 and delta a'_J=delta X/2",
        },
        "local_orders": {
            "O(Dq)": "enters the shift one-form but cannot form R_perp alone",
            "O(D2q)": (
                "enters delta K_mu_nu through "
                "+tau(chi_1/4)t D_muD_nu q at the fold"
            ),
            "O((Dq)^2)": (
                "present beyond linear order and additionally depends on "
                "ell2,a2,N2 and constraint corrections"
            ),
            "first_unresolved_order": "O(D2q)",
        },
        "gauge": {
            "built_from_covariant_equations": True,
            "transformation": "R_perp -> R_perp",
            "fixed_moving_coordinate_independent": True,
            "affine_bookkeeping_residual": sp.sstr(affine_schur_residual()),
        },
        "Z2": {
            "outward_cap_Hamiltonian_terms": "orientation even",
            "common_normal_junction": "uses the stored [Q_mu_nu] jump",
            "cap_exchange": "R_perp is even",
            "tau": "changes the linear source sign, not the dependency rank",
            "scalar_sign_s": "absent at linear order because sigma0=0",
        },
        "Noether_Bianchi": {
            "normal_boundary_diffeomorphism_is_Domain_F_gauge": False,
            "reason": "xi^t|B1!=0 does not preserve the fixed abstract support",
            "identity_role": (
                "relates R_perp to bulk normal constraints and independent "
                "B1/scalar/matcher equations; it does not set R_perp to zero "
                "before those equations are solved"
            ),
            "independence_decided": False,
        },
        "missing_object": (
            "the action-normalized time-dependent spatially homogeneous "
            "threading contribution to the scalar B1 junction projections "
            "and endpoint trace"
        ),
        "why_v6_18_insufficient": (
            "v6.18 derives K_Sigma=(2/a^2)D_spatial^2 on round S3 and "
            "C_Sigma=0; it does not derive D_0D_0 q or the Lorentzian "
            "homogeneous endpoint response"
        ),
        "explicit_result": None,
        "proved_zero": False,
        "proved_nonzero": False,
        "result": RESIDUAL_RESULT,
    }


def fixed_support_compatibility_ledger() -> dict[str, Any]:
    return {
        "localization_map_exists": True,
        "induced_shift_uses_existing_field": True,
        "shift_matches_v6_18_spatial_response": True,
        "coordinate_zeta_eliminated_nonsingularly": True,
        "support_specific_gauge_count_closes": True,
        "complete_field_vector": [
            "A",
            "B",
            "psi",
            "E",
            "delta sigma_perp",
            "independent B1 trace scalar",
            "independent B1 scalar-longitudinal scalar",
            "matcher trace scalar",
            "matcher scalar-longitudinal scalar",
        ],
        "constraints": [
            "radial Hamiltonian",
            "radial scalar momentum",
            "bulk scalar equation",
            "two independent scalar tensor-junction combinations",
            "two algebraic scalar matcher equations",
        ],
        "constraint_count": {
            "bulk_radial_scalar_constraints": 2,
            "bulk_scalar_equations": 1,
            "independent_scalar_junction_combinations": 2,
            "algebraic_scalar_matcher_equations": 2,
        },
        "known_checks": {
            "principal_A_psi": "(6kappa_1/a0^2)[[0,1],[1,2]]",
            "radial_measure": "pi sin^4(pi t/4)dt",
            "GHY": "normal derivatives cancel capwise on fixed t=1",
            "matcher": "exact algebraic elimination",
        },
        "closure": {
            "spatial_nonhomogeneous": "leading threading covered",
            "time_dependent_homogeneous": None,
            "endpoint_trace": None,
            "R_perp_on_all_equations": None,
            "all_success_criteria_met": False,
        },
        "fixed_support_success": False,
        "failure_proved": False,
        "interpretation": (
            "kinematic representability is proved, but compatibility requires "
            "the missing Lorentzian homogeneous junction response"
        ),
    }


def embedding_domain_ledger() -> dict[str, Any]:
    return {
        "reached": False,
        "reason": (
            "Domain D is allowed only after a nonzero gauge-invariant "
            "R_perp survives the complete Domain-F equations; no such "
            "residual has been derived"
        ),
        "necessity_proved": False,
        "common_abstract_B1": None,
        "cap_embeddings": None,
        "Z2_glue_rule": None,
        "normal_relation": None,
        "gauge_invariant_embedding_scalar": None,
        "existing_action_differentiability": None,
        "new_corner_required": None,
        "embedding_equation": None,
        "embedding_degree_of_freedom": None,
        "new_action_primitive": False,
        "dynamic_code_path_enabled": False,
        "result": EMBEDDING_RESULT,
    }


def decision_ledger() -> dict[str, Any]:
    return {
        "candidate_domains": {
            "F": "fixed abstract support B1={t=1}",
            "D": "common abstract B1 with two varied cap embeddings",
        },
        "evidence_for_F": [
            "rho=ell(q(x))t maps the moving homogeneous cap to fixed support",
            "the induced shift is an existing ADM field",
            "its linear coefficient exactly matches v6.18 on Pi_perp",
            "zeta=0 has a nonsingular gauge map and adds no support scalar",
        ],
        "evidence_against_declaring_F_success": [
            "the time-dependent spatially homogeneous scalar junction response is underived",
            "the endpoint threading trace entering R_perp is underived",
            "R_perp has not been evaluated on every existing equation",
        ],
        "evidence_against_declaring_D_required": [
            "no explicit nonzero R_perp has been derived",
            "existing ADM fields already encode the local cap-length coordinate effect",
            "failure of a calculation is not proof of dynamical embedding necessity",
        ],
        "selected_domain": None,
        "rejected_alternative": None,
        "primary_result": PRIMARY_RESULT,
        "one_primary_support_result": True,
        "operator": {
            "reopened": False,
            "field_vector_status": "candidate Domain-F vector recorded",
            "result": OPERATOR_RESULT,
        },
        "Schur": {
            "inverse_constructed": False,
            "K_scalar": "2 integral a0^2 u1^2 d rho>=2",
            "K_Weyl": "3 chi_1^2(4-pi)^2/(16pi)",
            "K_grav_constraint_J": None,
            "k_q_E": None,
            "result": SCHUR_RESULT,
        },
        "kinetic": {
            "sign": None,
            "ghost": None,
            "stability": None,
            "result": KINETIC_RESULT,
        },
        "exact_next_target": (
            "derive the action-normalized time-dependent spatially homogeneous "
            "threading/endpoint response and insert it into the two independent "
            "scalar B1 junction projections, then evaluate R_perp at O(D^2q)"
        ),
    }


def provenance_ledger() -> list[dict[str, str]]:
    return [
        {
            "item": "field-dependent coordinate pullback and ADM decomposition",
            "status": "Adopted from established physics/mathematics",
        },
        {
            "item": "frozen two-cap P1+GHY+B1+matcher+scalar action",
            "status": "Adopted BHSM axiom",
        },
        {
            "item": "q=r on one fold sheet and the Z2 cap identification",
            "status": "BHSM identification",
        },
        {
            "item": "fixed-manifold localization map and induced shift",
            "status": "Derived consequence",
        },
        {
            "item": "either fixed-support success or dynamical-embedding necessity",
            "status": "Active construction target",
        },
    ]


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_24_scientific_sha": V624_SCIENTIFIC_SHA,
        "v6_24_reproducibility_sha": V624_REPRODUCIBILITY_SHA,
        "localization_result": LOCALIZATION_RESULT,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    fixed_map = fixed_manifold_ledger()
    gauge = gauge_ledger()
    residual = normal_residual_ledger()
    return {
        "localization": {
            **_common("BHSM_fixed_manifold_localization_map_v6_25_0"),
            "provenance": provenance_ledger(),
            "fixed_manifold": fixed_map,
            "gauge": gauge,
        },
        "residual": {
            **_common("BHSM_normal_support_residual_v6_25_0"),
            "normal_support_residual": residual,
            "boundary_equations": boundary_equation_ledger(),
        },
        "fixed": {
            **_common("BHSM_fixed_support_compatibility_audit_v6_25_0"),
            "fixed_manifold": fixed_map,
            "gauge": gauge,
            "boundary_equations": boundary_equation_ledger(),
            "normal_support_residual": residual,
            "compatibility": fixed_support_compatibility_ledger(),
        },
        "embedding": {
            **_common("BHSM_Z2_embedding_variational_domain_v6_25_0"),
            "embedding_domain": embedding_domain_ledger(),
        },
        "decision": {
            **_common("BHSM_support_domain_decision_v6_25_0"),
            "decision": decision_ledger(),
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
