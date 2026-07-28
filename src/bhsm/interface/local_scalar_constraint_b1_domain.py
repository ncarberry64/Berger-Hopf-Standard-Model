"""BHSM v6.24.0 local scalar constraint and moving-B1-domain audit.

The frozen P1+GHY+B1+matcher+scalar action has a fixed B1 embedding.  A
moving graph is therefore available as a coordinate representative of that
fixed support, but not as an independently varied endpoint.  This module
derives the universal first-order graph geometry and the corresponding gauge
invariants, then applies the earliest-stop rule before manufacturing a
free-boundary equation, boundary matrix, full operator, or Schur inverse.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.24.0"
SPRINT = "bhsm-local-scalar-constraint-b1-domain-v6-24-0"
SOURCE_MAIN_SHA = "21c7e8fe9057d75f353e4f23ad5dbe49a1b41c6b"
V623_SCIENTIFIC_SHA = "9d13432b055a52e4a7e0ca4d599b7f465328f447"

LOCAL_RESULT = (
    "BHSM_LOCAL_SCALAR_CONSTRAINT_SYSTEM_BLOCKED_BY_"
    "UNSTORED_X_DEPENDENT_EMBEDDING_DOMAIN"
)
B1_RESULT = (
    "BHSM_B1_MOVING_ENDPOINT_DOMAIN_BLOCKED_BY_"
    "UNSTORED_X_DEPENDENT_GLUE_REFLECTION_DATUM"
)
SOURCE_RESULT = (
    "BHSM_FOLD_COMPLETE_LOCAL_MIXED_SOURCE_BLOCKED_BY_"
    "UNSTORED_X_DEPENDENT_EMBEDDING_DOMAIN"
)
SCHUR_RESULT = (
    "BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_"
    "UNSTORED_X_DEPENDENT_EMBEDDING_DOMAIN"
)
KINETIC_RESULT = (
    "BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_"
    "UNSTORED_X_DEPENDENT_EMBEDDING_DOMAIN"
)

ARTIFACT_FILES = {
    "gauge": "BHSM_local_scalar_gauge_ledger_v6_24_0.json",
    "operator": "BHSM_P1_GHY_scalar_quadratic_operator_v6_24_0.json",
    "domain": "BHSM_B1_matcher_moving_endpoint_domain_v6_24_0.json",
    "source": "BHSM_fold_complete_local_source_v6_24_0.json",
    "schur": "BHSM_fold_local_schur_status_v6_24_0.json",
}

GUARDS = {
    "measured_inputs_used": False,
    "fitted_coefficients_introduced": False,
    "new_primitive_introduced": False,
    "new_scale_introduced": False,
    "new_action_introduced": False,
    "new_corner_term_introduced": False,
    "embedding_variation_assumed": False,
    "arbitrary_boundary_parameter_introduced": False,
    "arbitrary_global_green_state_selected": False,
    "chat_only_candidate_imported": False,
    "local_X_field_invented": False,
    "scalar_curvature_inverse_revived": False,
    "conformal_tangent_used_as_action_input": False,
    "generic_pseudoinverse_emitted": False,
    "schur_number_emitted": False,
    "kinetic_number_emitted": False,
    "ghost_or_stability_claimed": False,
    "physical_mass_claimed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}

N0, A0 = sp.symbols("N_0 a_0", positive=True, real=True)
B, ZETA, E_RHO = sp.symbols("B zeta E_rho", real=True)
XI_RHO, XI_RHO_D = sp.symbols("xi_rho xi_rho_d", real=True)
KAPPA_1 = sp.symbols("kappa_1", positive=True, real=True)
T = sp.symbols("t", real=True)


def deterministic_json(payload: dict[str, Any]) -> str:
    """Return canonical UTF-8 JSON with exactly one trailing LF."""

    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def induced_metric_variation(
    metric_pullback: sp.MatrixBase,
    extrinsic_curvature: sp.MatrixBase,
    zeta: sp.Expr,
    tangential_lie: sp.MatrixBase | None = None,
) -> sp.ImmutableMatrix:
    """First variation of the metric induced on a moving graph.

    Conventions are n.n=+1 and K_ab=(1/2)L_n gamma_ab.  ``metric_pullback``
    is e_a^A e_b^B delta g_AB and ``tangential_lie`` is L_v gamma.
    """

    p = sp.Matrix(metric_pullback)
    k = sp.Matrix(extrinsic_curvature)
    if p.shape != k.shape or p.rows != p.cols:
        raise ValueError("metric pullback and extrinsic curvature must be square")
    lie = sp.zeros(p.rows) if tangential_lie is None else sp.Matrix(tangential_lie)
    if lie.shape != p.shape:
        raise ValueError("tangential Lie derivative has the wrong shape")
    return sp.ImmutableMatrix(p + 2 * zeta * k + lie)


def normal_covector_variation(
    metric_normal_normal: sp.Expr,
    zeta_gradient: sp.MatrixBase,
) -> sp.ImmutableMatrix:
    """Frame components of delta n_A for a normal graph.

    The returned column is ``(normal, tangential...)``:
    delta n_A=(delta g_nn/2)n_A-(D_a zeta)e^a_A.
    """

    gradient = sp.Matrix(zeta_gradient)
    if gradient.cols != 1:
        raise ValueError("zeta gradient must be a column vector")
    return sp.ImmutableMatrix.vstack(
        sp.ImmutableMatrix([[metric_normal_normal / 2]]),
        sp.ImmutableMatrix(-gradient),
    )


def shape_extrinsic_curvature_variation(
    zeta_hessian: sp.MatrixBase,
    shape_operator_square: sp.MatrixBase,
    normal_riemann: sp.MatrixBase,
    zeta: sp.Expr,
) -> sp.ImmutableMatrix:
    """Pure normal-displacement part of delta K_ab.

    ``normal_riemann`` denotes R_{n a n b}.  Fixed-coordinate metric
    perturbations have an additional standard ADM linearization; this
    function isolates the embedding-dependent part whose sign is at issue.
    """

    hessian = sp.Matrix(zeta_hessian)
    k2 = sp.Matrix(shape_operator_square)
    rann = sp.Matrix(normal_riemann)
    if not (hessian.shape == k2.shape == rann.shape) or hessian.rows != hessian.cols:
        raise ValueError("all shape-variation tensors must have the same square shape")
    return sp.ImmutableMatrix(-hessian + zeta * (k2 - rann))


def shape_trace_curvature_variation(
    laplacian_zeta: sp.Expr,
    extrinsic_norm_squared: sp.Expr,
    ricci_normal_normal: sp.Expr,
    zeta: sp.Expr,
) -> sp.Expr:
    """Pure normal-displacement variation of K."""

    return sp.expand(
        -laplacian_zeta
        - (extrinsic_norm_squared + ricci_normal_normal) * zeta
    )


def boundary_measure_fractional_variation(
    metric_tangential_trace: sp.Expr,
    mean_curvature: sp.Expr,
    zeta: sp.Expr,
    tangential_divergence: sp.Expr = sp.Integer(0),
) -> sp.Expr:
    """delta sqrt(|gamma|)/sqrt(|gamma|) on the moving graph."""

    return sp.expand(
        metric_tangential_trace / 2
        + mean_curvature * zeta
        + tangential_divergence
    )


def scalar_pullback_variation(
    scalar_variation: sp.Expr,
    zeta: sp.Expr,
    normal_scalar_gradient: sp.Expr,
    tangential_transport: sp.Expr = sp.Integer(0),
) -> sp.Expr:
    """First variation of a scalar pulled back to the graph."""

    return sp.expand(
        scalar_variation
        + zeta * normal_scalar_gradient
        + tangential_transport
    )


def endpoint_shift_invariant(
    b: sp.Expr = B,
    zeta: sp.Expr = ZETA,
    e_rho: sp.Expr = E_RHO,
) -> sp.Expr:
    """Repository-normalized gauge-invariant endpoint threading scalar."""

    return sp.expand(b + N0**2 * zeta - A0**2 * e_rho)


def transformed_endpoint_shift_invariant() -> sp.Expr:
    """Apply the stored radial and M4-scalar diffeomorphism laws."""

    transformed_b = B - N0**2 * XI_RHO - A0**2 * XI_RHO_D
    transformed_zeta = ZETA + XI_RHO
    transformed_e_rho = E_RHO - XI_RHO_D
    return endpoint_shift_invariant(
        transformed_b, transformed_zeta, transformed_e_rho
    )


def principal_lapse_weyl_block(
    kappa_1: sp.Expr = KAPPA_1,
    scale_factor: sp.Expr = A0,
) -> sp.ImmutableMatrix:
    """The inherited v6.20 critical order-zero A--psi block."""

    return sp.ImmutableMatrix(
        (6 * kappa_1 / scale_factor**2)
        * sp.Matrix([[0, 1], [1, 2]])
    )


def critical_radial_measure(t: sp.Expr = T) -> sp.Expr:
    """N0*a0^4 in the normalized critical representative."""

    a0 = sp.sqrt(2) * sp.sin(sp.pi * t / 4)
    n0 = sp.pi / 4
    return sp.simplify(n0 * a0**4)


def affine_schur_identity_residual() -> sp.Expr:
    """Scalar-block check of K'-J'L^-1J'=K-JL^-1J."""

    k, j, ell, v = sp.symbols("K J L v", nonzero=True, real=True)
    k_prime = k + 2 * j * v + ell * v**2
    j_prime = j + ell * v
    return sp.simplify(
        k_prime - j_prime**2 / ell - (k - j**2 / ell)
    )


def action_and_background_ledger() -> dict[str, Any]:
    return {
        "provenance": {
            "frozen_action": "intrinsic_m4_junction_background.py:224-263",
            "scalar_completion": "scalar_wall_junction_audit.py:266-291",
            "critical_background": "scalar_wall_junction_audit.py:359-370",
            "fixed_embedding_domain": "moving_endpoint_shift_domain.py:repository_domain_ledger",
            "Z2_gluing_domain": "z2_double_cap_threading_domain.py:support_domain_ledger",
            "threading_response": "covariant_threading_response.py:kernel_ledger,response_domain_ledger",
            "principal_block": "critical_lapse_weyl_hessian.py",
        },
        "action": {
            "total": [
                "S_P1,cap+",
                "S_P1,cap-",
                "S_GHY,cap+",
                "S_GHY,cap-",
                "S_B1",
                "S_match",
                "S_sigma",
            ],
            "P1": (
                "∫sqrt(-g)[kappa_1 R5/2-kappa_0/2"
                "-Z5(grad sigma)^2/2-U5(sigma)]"
            ),
            "U5": "A5 sigma^2/2+G5 sigma^4/4",
            "GHY_each_oriented_cap": "+kappa_1 ∫sqrt(-h) K",
            "B1_primary_freeze": (
                "∫sqrt(-h)[C_partial R4-tau_A Tr(F^2)/4"
                "-Z_partial(partial sigma_partial)^2/2]"
            ),
            "U_partial": "absent (zero in the primary freeze)",
            "matcher": (
                "∫_B1 sqrt(-h) Lambda^(mu nu)"
                "(h_mu nu-iota^*g_mu nu)"
            ),
            "cap_count": 2,
            "common_B1_count": 1,
            "matcher_coefficient": None,
            "new_term_added": False,
        },
        "background": {
            "metric": (
                "ds5^2=N0^2 dt^2+a0(t)^2 hbar_mu_nu dx^mu dx^nu"
            ),
            "radial_coordinate": "t∈[0,1] on each normalized cap",
            "N0": "pi/4",
            "a0": "sqrt(2) sin(pi t/4)",
            "sigma0": 0,
            "normal": "n_out=N0^-1 partial_t on each outward cap coordinate",
            "K_convention": "K_mu_nu=(1/2)L_n h_mu_nu",
            "cap_endpoint": "t=1",
            "regular_pole": "t=0",
            "X_c": 2,
            "q5": 1,
            "kappa1": 1,
            "Z5": 1,
            "C_partial_over_kappa1": "1/2",
            "M4": "Ric(hbar)=3 X_c hbar (maximally symmetric branch)",
            "R4": "12 X_c",
            "Z2": "two reflected regular caps and one common B1",
            "common_normal": (
                "outward normals are used capwise; signed common-normal "
                "threading amplitudes have opposite signs"
            ),
        },
    }


def gauge_ledger() -> dict[str, Any]:
    return {
        "pre_quotient_fields": {
            "each_cap": [
                "A (radial lapse scalar)",
                "B (radial shift potential)",
                "psi (M4 trace/Weyl scalar)",
                "E (M4 scalar-longitudinal potential)",
                "delta sigma_perp",
            ],
            "collective_source": "q with delta sigma=s u1 q+delta sigma_perp",
            "diagnostic_endpoint_representative": "zeta",
            "independent_B1_before_matching": [
                "intrinsic metric trace scalar",
                "intrinsic metric scalar-longitudinal scalar",
                "retained intrinsic scalar if sourced",
            ],
            "matcher_before_elimination": [
                "Lambda trace scalar",
                "Lambda scalar-longitudinal scalar",
            ],
        },
        "gauge_functions": {
            "radial": "xi^rho",
            "M4_scalar": "L with xi^mu=D^mu L",
            "intrinsic_B1": (
                "the pullback of L at B1, acting simultaneously on intrinsic "
                "fields and iota^*g"
            ),
        },
        "convention": "delta g→delta g-L_xi g; zeta→zeta+xi^rho|B1",
        "transformations": {
            "A": "A-(N0 xi^rho)'/N0",
            "B": "B-N0^2 xi^rho-a0^2 partial_rho L",
            "psi": "psi-(a0'/a0)xi^rho",
            "E": "E-L",
            "delta_sigma": "delta sigma-sigma0' xi^rho",
            "zeta": "zeta+xi^rho|B1",
            "intrinsic_metric": "delta h_partial→delta h_partial-L_(xi_parallel)hbar",
            "matcher": "tensor-density pullback law; no physical multiplier mode",
        },
        "invariants": {
            "threading": "S_Sigma=B+N0^2 zeta-a0^2 partial_rho E",
            "metric_pullback": (
                "delta gamma_ab|B1+2K_ab zeta+L_v gamma_ab"
            ),
            "scalar_pullback": "delta sigma|B1+zeta n(sigma0)",
            "critical_scalar_pullback": "delta sigma|B1 because n(sigma0)=0",
        },
        "fixed_support_equivalence": {
            "moving_coordinate_representative": "zeta may be nonzero",
            "fixed_endpoint_gauge": "xi^rho|B1=-zeta gives zeta=0",
            "threading_unchanged": True,
            "physical_support_moved": False,
        },
        "physical_moving_support": {
            "gauge_equivalent_to_fixed_support": False,
            "reason": (
                "changing the embedded submanifold and the Z2 reflection map "
                "changes action-domain data, not merely coordinates"
            ),
        },
        "count_status": {
            "fixed_embedding_count": "inherited and consistent",
            "physical_moving_embedding_count": None,
            "why": (
                "zeta has neither a declared variation nor a conjugate "
                "boundary/domain condition in the frozen configuration space"
            ),
        },
        "symbolic_threading_invariance": sp.sstr(
            sp.simplify(
                transformed_endpoint_shift_invariant()
                - endpoint_shift_invariant()
            )
        ),
    }


def moving_geometry_ledger() -> dict[str, Any]:
    return {
        "status": "Derived consequence (kinematics only)",
        "graph": "X_zeta(x)=Exp_iota(x)[zeta(x)n]+v^a e_a+O(zeta^2)",
        "conventions": "n.n=+1; K_ab=(1/2)L_n gamma_ab",
        "induced_metric": (
            "delta gamma_ab=p_ab+2zeta K_ab+2D_(a v_b)"
        ),
        "normal_covector": (
            "delta n_A=(p_nn/2)n_A-(D_a zeta)e^a_A "
            "(normal-graph representative)"
        ),
        "normal_vector": (
            "delta n^A=-(p_nn/2)n^A-(p_n^a+D^a zeta)e_a^A"
        ),
        "ADM_graph": {
            "exact_induced_metric": (
                "[gamma_mu_nu+N_mu D_nu zeta+N_nu D_mu zeta"
                "+(N^2+N_alpha N^alpha)D_mu zeta D_nu zeta]_graph"
            ),
            "relative_shift_one_form": "V_mu=N_mu+N^2D_mu zeta",
            "linear_normal_lapse": "delta N_graph=A+zeta partial_rho N0",
        },
        "extrinsic_curvature_shape_part": (
            "delta_zeta K_ab=-D_aD_b zeta"
            "+zeta(K_a^c K_cb-R_n a n b)"
        ),
        "trace_shape_part": (
            "delta_zeta K=-D^2 zeta"
            "-(K_ab K^ab+Ric_nn)zeta"
        ),
        "measure": (
            "delta sqrt(|gamma|)/sqrt(|gamma|)"
            "=p^a_a/2+K zeta+D_a v^a"
        ),
        "scalar_pullback": (
            "delta sigma_ind=delta sigma+zeta n(sigma0)+v^aD_a sigma0"
        ),
        "critical_scalar_pullback": "delta sigma_ind=delta sigma because sigma0=0",
        "gauge_pullback": (
            "delta A_ind=iota^*(delta A+L_(zeta n+v)A0); "
            "zero on the retained A0=0 background"
        ),
        "matcher_pullback": (
            "delta(iota_zeta^*g)_ab=p_ab+2zeta K_ab+2D_(a v_b)"
        ),
        "scope": (
            "these identities compare embeddings geometrically; they do not "
            "declare iota_zeta to be a field varied by the frozen action"
        ),
    }


def moving_domain_obstruction_ledger() -> dict[str, Any]:
    return {
        "earliest_stop_section": "moving-endpoint geometry / variational status",
        "fixed_action_fact": (
            "the matcher contains a fixed iota and the action varies g, h, "
            "Lambda, and scalars, not iota"
        ),
        "homogeneous_reduced_exception": (
            "v6.1.7 varies the one-dimensional cap upper limit along the "
            "homogeneous solved family and obtains transversality/shape "
            "response; this does not declare an arbitrary iota_zeta(x)"
        ),
        "stored_homogeneous_endpoint_condition": (
            "delta a'_J=delta X/2 in the normalized homogeneous tangent"
        ),
        "local_extension_of_homogeneous_condition": None,
        "why_no_local_extension": (
            "the D_mu zeta, D_mu q, and D_muD_nu q corrections depend on the "
            "unstored x-dependent embedding/gluing variational domain"
        ),
        "repository_fact": (
            "v6.13 records embedding_varied=False and "
            "x_dependent_embedding_variation=False"
        ),
        "double_cap_fact": (
            "v6.15 records an x-dependent reflection center as an additional "
            "orbifold/gluing datum, not a fixed-double diffeomorphism"
        ),
        "later_threading_fact": (
            "v6.18 supplies an induced threading response on spatial "
            "Pi_perp modes and adopts C_Sigma=0; it does not promote iota"
        ),
        "smallest_missing_object": (
            "an off-shell family of embeddings iota_zeta together with its "
            "Z2 cap-exchange/reflection extension, declared as part of the "
            "variational domain"
        ),
        "also_required_if_adopted": [
            "which endpoint variations are free versus fixed",
            "the pullback/matcher transformation under those variations",
            "the cap-domain shape variation and any required corner data",
            "the resulting endpoint boundary equation and boundary matrix",
        ],
        "coordinate_zeta_is_available": True,
        "physical_zeta_is_action_selected": False,
        "matcher_fixes_physical_zeta": False,
        "junction_fixes_physical_zeta": False,
        "free_endpoint_equation_derived": False,
        "why_no_endpoint_equation": (
            "a functional derivative with respect to a variable outside the "
            "configuration space is not an Euler-Lagrange equation"
        ),
        "Noether_identity_available": (
            "for coordinate displacement of the fixed support, covariance "
            "relates pullback variations to bulk equations and tangential "
            "Ward identities; this does not create a normal free-boundary law"
        ),
        "arbitrary_domain_axiom_added": False,
        "verdict": B1_RESULT,
    }


def operator_ledger() -> dict[str, Any]:
    return {
        "action_expansion_started": False,
        "reason": "earliest stop occurs before promoting iota_zeta in the action",
        "retained_exact_checks": {
            "principal_A_psi_block": (
                "(6kappa_1/a0^2)[[0,1],[1,2]]"
            ),
            "principal_matrix_symbolic": [
                ["0", "6*kappa_1/a_0**2"],
                ["6*kappa_1/a_0**2", "12*kappa_1/a_0**2"],
            ],
            "radial_measure": "N0 a0^4=pi sin^4(pi t/4)",
            "GHY_fixed_cap": (
                "normal derivatives of delta g cancel capwise in the stored "
                "fixed-embedding variation"
            ),
            "tensor_junction": (
                "kappa_1[Q_ab]+2C_partial G_ab^(4)=T_partial,ab"
            ),
            "matcher": (
                "h_ab=iota^*g_ab after independent variation and "
                "Lambda elimination"
            ),
        },
        "not_derived": {
            "complete_quadratic_action": None,
            "lower_order_radial_blocks": None,
            "moving_endpoint_mixing": None,
            "complete_scalar_junction_projections": None,
            "endpoint_Noether_dependency_matrix": None,
            "L0": None,
            "L1": None,
            "boundary_matrix": None,
            "formal_adjoint": None,
            "Green_current": None,
            "domain": None,
            "adjoint_domain": None,
            "kernel_dimension": None,
            "adjoint_kernel_dimension": None,
        },
        "zero_assigned_to_missing_blocks": False,
        "operator_verdict": LOCAL_RESULT,
    }


def threading_coverage_ledger() -> dict[str, Any]:
    return {
        "v6_18_exact_scope": {
            "background": "round spatial S3 symmetric background",
            "kernel": "Khat_Sigma=(2/a^2)D_spatial^2",
            "projected_response": (
                "Pi_perp Sbar=-tau(pi chi_1/16)Pi_perp q"
            ),
            "homogeneous_constant": "C_Sigma=0 by adopted BHSM axiom",
        },
        "sector_audit": {
            "spatial_nonhomogeneous_ell_ge_1": "covered mode by mode",
            "spatial_homogeneous_ell_0_time_independent": (
                "kernel; selected by C_Sigma=0 axiom"
            ),
            "time_dependent_spatially_homogeneous": (
                "not covered by the time-independent S3 harmonic Hessian"
            ),
            "general_Lorentzian_M4_scalar": (
                "not covered; general lower DtN terms were left open"
            ),
            "moving_endpoint_trace": (
                "not covered; zeta was not promoted to an action variable"
            ),
        },
        "required_mode_outside_v6_18": True,
        "why_it_matters": (
            "the requested local q(x) operator includes Lorentzian homogeneous "
            "response and endpoint mixing, so the spatial Pi_perp inverse "
            "cannot be inserted as the complete threading block"
        ),
    }


def source_ledger() -> dict[str, Any]:
    return {
        "bookkeeping_convention": (
            "A: homogeneous radial profiles would be affine shifts of "
            "constraint variables; they are not also inserted as direct terms"
        ),
        "homogeneous_input_only": {
            "delta_sigma": "s u1 q+delta sigma_perp",
            "delta_X_FRW": "tau chi_1 q",
            "status": "on-shell homogeneous tangent data, not local equations",
        },
        "known_components": {
            "scalar_direct": "K_scalar=2∫a0^2 u1^2 d rho>=2",
            "threading_projected": (
                "Pi_perp Sbar=-tau(pi chi_1/16)Pi_perp q"
            ),
            "principal_lapse_weyl": "partial source only from v6.20",
            "Einstein_frame_later": (
                "K_Weyl=3 chi_1^2(4-pi)^2/(16pi), counted once only "
                "after a Jordan-frame reduction"
            ),
        },
        "missing_components": [
            "physical moving-endpoint source",
            "matcher source induced by iota_zeta",
            "complete intrinsic B1 scalar-curvature source",
            "time-dependent homogeneous threading source",
            "delta sigma_perp mixed source after the full constraint solve",
            "all lower-order coupled metric sources",
        ],
        "affine_identity": (
            "K'-<J',L^-1J'>=K-<J,L^-1J>"
        ),
        "affine_identity_symbolic_residual": sp.sstr(
            affine_schur_identity_residual()
        ),
        "identity_applicability": (
            "algebraically proved, but numerical use requires the same closed "
            "invertible quotient operator and domain, which are unavailable"
        ),
        "full_J0": None,
        "full_J1": None,
        "no_double_counting_proved_for_available_terms": True,
        "source_verdict": SOURCE_RESULT,
    }


def schur_ledger() -> dict[str, Any]:
    return {
        "final_field_vector": None,
        "reason": (
            "the status of physical zeta and its boundary equation must be "
            "known before matcher elimination and final quotient counting"
        ),
        "operator_pencil": {
            "sign_convention": "lambda corresponds locally to -D^2",
            "L0": None,
            "L1": None,
            "J0": None,
            "J1": None,
        },
        "inner_product": "action weight begins with N0 a0^4 dt",
        "complete_weighted_inner_product": None,
        "domain": None,
        "adjoint_domain": None,
        "kernel_dimensions": None,
        "source_compatibility": None,
        "inverse_constructed": False,
        "global_green_state_selected": False,
        "Schur_complement": None,
        "K_grav_constraint_J": None,
        "K_scalar": "2∫a0^2 u1^2 d rho>=2 (preserved bound)",
        "K_Weyl": "3 chi_1^2(4-pi)^2/(16pi) (preserved, not added)",
        "k_q_E": None,
        "kinetic_sign": None,
        "ghost_claim": None,
        "stability_claim": None,
        "exact_next_construction_target": (
            "declare or derive the off-shell x-dependent B1 embedding and "
            "Z2 reflection/gluing variational domain; then derive its endpoint "
            "equation before reopening the complete quadratic operator"
        ),
        "Schur_verdict": SCHUR_RESULT,
        "kinetic_verdict": KINETIC_RESULT,
    }


def provenance_status_ledger() -> list[dict[str, str]]:
    return [
        {
            "item": "moving-hypersurface first-variation identities",
            "status": "Adopted from established physics/mathematics",
        },
        {
            "item": "frozen P1+GHY+B1+matcher+scalar action and fixed iota",
            "status": "Adopted BHSM axiom",
        },
        {
            "item": "two-cap/common-B1 identification",
            "status": "BHSM identification",
        },
        {
            "item": "coordinate moving/fixed endpoint gauge equivalence",
            "status": "Derived consequence",
        },
        {
            "item": "physical moving-endpoint equation from the frozen action",
            "status": "Rejected by calculation",
        },
        {
            "item": "x-dependent embedding and Z2 gluing variational domain",
            "status": "Active construction target",
        },
    ]


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_23_scientific_sha": V623_SCIENTIFIC_SHA,
        "local_operator_verdict": LOCAL_RESULT,
        "B1_domain_verdict": B1_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    action_background = action_and_background_ledger()
    geometry = moving_geometry_ledger()
    obstruction = moving_domain_obstruction_ledger()
    return {
        "gauge": {
            **_common("BHSM_local_scalar_gauge_ledger_v6_24_0"),
            "provenance_status": provenance_status_ledger(),
            "action_and_background": action_background,
            "gauge": gauge_ledger(),
            "moving_graph_kinematics": geometry,
        },
        "operator": {
            **_common("BHSM_P1_GHY_scalar_quadratic_operator_v6_24_0"),
            "action_and_background": action_background,
            "operator": operator_ledger(),
        },
        "domain": {
            **_common("BHSM_B1_matcher_moving_endpoint_domain_v6_24_0"),
            "moving_graph_kinematics": geometry,
            "domain_obstruction": obstruction,
        },
        "source": {
            **_common("BHSM_fold_complete_local_source_v6_24_0"),
            "threading_coverage": threading_coverage_ledger(),
            "source": source_ledger(),
        },
        "schur": {
            **_common("BHSM_fold_local_schur_status_v6_24_0"),
            "domain_obstruction": obstruction,
            "threading_coverage": threading_coverage_ledger(),
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
    written: list[Path] = []
    for filename, content in artifact_bytes().items():
        path = artifact_dir / filename
        path.write_bytes(content)
        written.append(path)
    return written
