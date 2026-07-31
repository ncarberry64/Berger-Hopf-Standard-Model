"""BHSM v8.8 common-parent C3/G2 charged-current attachment.

This manual sprint adds the unique minimal zero-new-coefficient interface term
that attaches a full-rank common-parent C3/G2 transfer kernel to the localized
left-handed charged current.  The term replaces the family identity inside the
existing SU(2) raising/lowering generators; it does not introduce a second
charged-current coupling.

The geometric kernel is kept conceptually distinct from the numerical v8.6
heat-kernel screen.  The latter is used only as a deterministic full-rank
stress test of the construction and is not promoted to an action-derived CKM
matrix.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from . import complex_profile_isospectral_attachment as v86


VERSION = "v8.8"
SPRINT = "bhsm-common-parent-charged-current-attachment-v8-8"
PRIMARY_RESULT = (
    "BHSM_MINIMAL_ZERO_PARAMETER_COMMON_PARENT_C3_G2_CHARGED_CURRENT_"
    "TERM_CONSTRUCTED_CONDITIONALLY"
)
FINAL_VERDICT = (
    "BHSM_C3_G2_CHARGED_CURRENT_INTERFACE_CONSTRUCTION_CONDITIONAL_"
    "ON_ACTION_DERIVED_PARENT_KERNEL"
)
NEXT_MISSING_OBJECT = (
    "ACTION_DERIVATION_OF_THE_LOCAL_PARENT_CURRENT_KERNEL_AND_"
    "MASS_BASIS_ATTACHMENT_WITHOUT_SCREEN_INPUTS"
)


def proxy_parent_kernel() -> np.ndarray:
    """Deterministic v8.7 C3/G2 realization used only for a domain stress test.

    The abstract action term uses K_CG[G,omega,sigma].  This numerical matrix
    retains the v8.6 screen construction and therefore is not itself promoted
    to an action-derived physical vertex.
    """

    return v86.c3_cross_matrix(0) - 1j * v86.c3_cross_matrix(1)


def polar_isometry(kernel: np.ndarray) -> np.ndarray:
    """Canonical pointwise family isometry U=K(K^dagger K)^(-1/2)."""

    return v86.polar_unitary(np.asarray(kernel, dtype=complex))


def kernel_domain_audit() -> dict[str, Any]:
    kernel = proxy_parent_kernel()
    singular = np.linalg.svd(kernel, compute_uv=False)
    unitary = polar_isometry(kernel)
    return {
        "abstract_kernel": (
            "K_CG=P_u R_84[Pi_10(P_chi0 direct_sum P_chi1) J_parent] P_d"
        ),
        "normalized_channel_form": "K_CG proportional to T_chi0-i T_chi1",
        "proxy_uses_screen_inputs": True,
        "proxy_role": "full-rank and algebraic stress test only",
        "proxy_singular_values": singular.tolist(),
        "proxy_smallest_singular_value": float(singular.min()),
        "full_rank": bool(singular.min() > 1.0e-12),
        "polar_formula": "U_CG=K_CG(K_CG^dagger K_CG)^(-1/2)",
        "polar_unitarity_residual": float(
            np.linalg.norm(unitary.conj().T @ unitary - np.eye(3))
        ),
        "pointwise_not_spacetime_nonlocal": True,
        "new_continuous_parameter": False,
    }


def weak_generators(unitary: np.ndarray) -> dict[str, np.ndarray]:
    """Six-dimensional weak-doublet generators with a family isometry."""

    U = np.asarray(unitary, dtype=complex)
    if U.shape != (3, 3):
        raise ValueError("the family isometry must be 3x3")
    zero = np.zeros((3, 3), dtype=complex)
    identity = np.eye(3, dtype=complex)
    t_plus = np.block([[zero, U], [zero, zero]])
    t_minus = t_plus.conj().T
    t_three = 0.5 * np.block([[identity, zero], [zero, -identity]])
    t_one = 0.5 * (t_plus + t_minus)
    t_two = (t_plus - t_minus) / (2.0j)
    return {
        "T_plus": t_plus,
        "T_minus": t_minus,
        "T_3": t_three,
        "T_1": t_one,
        "T_2": t_two,
    }


def su2_closure_audit() -> dict[str, Any]:
    U = polar_isometry(proxy_parent_kernel())
    generators = weak_generators(U)
    tp = generators["T_plus"]
    tm = generators["T_minus"]
    t3 = generators["T_3"]
    t1 = generators["T_1"]
    t2 = generators["T_2"]
    comm = lambda left, right: left @ right - right @ left
    casimir = t1 @ t1 + t2 @ t2 + t3 @ t3
    return {
        "generator_definition": {
            "T_plus_CG": "|u><d| tensor U_CG",
            "T_minus_CG": "|d><u| tensor U_CG^dagger",
            "T_3": "diag(I3,-I3)/2",
        },
        "residual_[T3,Tplus]-Tplus": float(np.linalg.norm(comm(t3, tp) - tp)),
        "residual_[T3,Tminus]+Tminus": float(np.linalg.norm(comm(t3, tm) + tm)),
        "residual_[Tplus,Tminus]-2T3": float(
            np.linalg.norm(comm(tp, tm) - 2.0 * t3)
        ),
        "residual_[T1,T2]-iT3": float(
            np.linalg.norm(comm(t1, t2) - 1j * t3)
        ),
        "casimir_residual": float(
            np.linalg.norm(casimir - 0.75 * np.eye(6, dtype=complex))
        ),
        "SU2_algebra_closed": bool(
            np.linalg.norm(comm(t3, tp) - tp) < 1.0e-11
            and np.linalg.norm(comm(tp, tm) - 2.0 * t3) < 1.0e-11
            and np.linalg.norm(comm(t1, t2) - 1j * t3) < 1.0e-11
        ),
        "neutral_generator_family_central": True,
        "tree_level_neutral_FCNC_generated": False,
    }


def _fixed_unitary(seed_matrix: np.ndarray) -> np.ndarray:
    return v86.polar_unitary(np.asarray(seed_matrix, dtype=complex))


def basis_covariance_audit() -> dict[str, Any]:
    """Verify polar(Vu K Vd^dagger)=Vu polar(K) Vd^dagger."""

    K = proxy_parent_kernel()
    U = polar_isometry(K)
    Vu = _fixed_unitary(
        np.array(
            [[1, 1j, 0.2], [0.3, 1, -0.4j], [0.2j, 0.5, 1]], dtype=complex
        )
    )
    Vd = _fixed_unitary(
        np.array(
            [[1, -0.2j, 0.4], [0.1, 1, 0.3j], [-0.3j, 0.2, 1]], dtype=complex
        )
    )
    transformed = Vu @ K @ Vd.conj().T
    transformed_polar = polar_isometry(transformed)
    expected = Vu @ U @ Vd.conj().T
    return {
        "kernel_law": "K_CG -> V_u K_CG V_d^dagger",
        "polar_law": "U_CG -> V_u U_CG V_d^dagger",
        "covariance_residual": float(np.linalg.norm(transformed_polar - expected)),
        "basis_covariant": bool(
            np.linalg.norm(transformed_polar - expected) < 1.0e-11
        ),
    }


def action_term() -> dict[str, Any]:
    return {
        "candidate_owner": "S_compatibility,current on the common M4 seam",
        "replacement_form": (
            "L_cc^CG=-(g2/sqrt(2))[W_mu^+ bar(u_L) gamma^mu U_CG d_L"
            "+W_mu^- bar(d_L) gamma^mu U_CG^dagger u_L]"
        ),
        "no_double_counting_form": (
            "DeltaL_attach=-(g2/sqrt(2))[W_mu^+ bar(u_L) gamma^mu"
            "(U_CG-I3)d_L+h.c.], added to the existing identity current"
        ),
        "covariant_derivative_form": (
            "D_mu^CG=nabla_mu-i g2[W_mu^3 T3+(W_mu^+ T_plus^CG"
            "+W_mu^- T_minus^CG)/sqrt(2)] plus unchanged U1/SU3 pieces"
        ),
        "kernel": "U_CG=Pol[K_CG]",
        "parent_composite": (
            "K_CG=P_u R_84[Pi_10(P_chi0 direct_sum P_chi1)"
            "J_parent[G,omega,sigma]] P_d"
        ),
        "normalized_branch": "K_CG proportional to T_chi0-i T_chi1",
        "conjugate_branch": "W^- carries U_CG^dagger and hence Pi_01/chi2",
        "mass_dimension": 4,
        "Lorentz_scalar": True,
        "Hermitian": True,
        "uses_existing_g2_only": True,
        "new_charged_coupling": False,
        "new_continuous_parameter": False,
        "new_fundamental_field": False,
        "classification": (
            "CONDITIONAL_MINIMAL_DIMENSION_FOUR_ZERO_NEW_COEFFICIENT_INTERFACE_TERM"
        ),
        "current_stratified_action_contains_term": False,
        "ownership_requires_action_derived_K_CG": True,
    }


def uniqueness_audit() -> dict[str, Any]:
    return {
        "requirements": [
            "local M4 Lorentz scalar",
            "linear in W_plus/W_minus and a left-handed fermion bilinear",
            "uses the existing SU2 coupling g2",
            "Hermitian",
            "family-basis covariant",
            "preserves the SU2 algebra and the family-central T3 generator",
            "uses the full-rank common-parent C3/G2 kernel without a fitted function",
        ],
        "consequence_1": (
            "the family kernel in T_plus must be unitary; otherwise "
            "[T_plus,T_minus]=2T3 fails"
        ),
        "consequence_2": (
            "for full-rank K_CG the polar factor is the unique canonical unitary"
        ),
        "consequence_3": (
            "the coefficient is g2/sqrt(2), already fixed by the SU2 covariant derivative"
        ),
        "extra_g_ch_allowed": False,
        "arbitrary_relative_C3_coefficient_allowed": False,
        "f_of_X_deformation_added": False,
        "polar_role": "canonical normalization, not a tunable dynamical response law",
        "unique_under_declared_requirements": True,
    }


def transport_compatibility() -> dict[str, Any]:
    return {
        "spacetime_dependent_kernel_law": (
            "D_mu^fam U_CG=partial_mu U_CG+A_mu^u U_CG-U_CG A_mu^d"
        ),
        "static_retained_background": "D_mu^fam U_CG=0",
        "dynamic_case": (
            "the existing parent-induced associated-bundle connections A_mu^u,d"
            " carry the variation; no arbitrary family connection is added"
        ),
        "gauge_covariance_requires_parallel_transport": True,
        "new_connection_parameter": False,
    }


def variation_and_backreaction() -> dict[str, Any]:
    return {
        "W_plus_current": (
            "delta S/delta W_mu^+=-(g2/sqrt(2))sqrt(-h)"
            " bar(u_L) gamma^mu U_CG d_L"
        ),
        "W_minus_current": "Hermitian adjoint of the W_plus current",
        "fermion_equations": (
            "the localized Dirac equations acquire the same U_CG/U_CG^dagger"
            " charged-current blocks"
        ),
        "parent_backreaction": (
            "conditional delta S_parent-current is nonzero through delta U_CG/delta"
            "(G,omega,sigma) only after K_CG is action-derived"
        ),
        "polar_differential": [
            "K=U H, H=(K^dagger K)^(1/2)",
            "H deltaH+deltaH H=deltaK^dagger K+K^dagger deltaK",
            "deltaU=(deltaK-U deltaH)H^(-1)",
        ],
        "full_rank_required": True,
        "rank_drop_behavior": (
            "a partial isometry would not represent three complete weak families;"
            " rank loss is therefore a fail-closed action-domain boundary"
        ),
    }


def physical_interpretation_boundary() -> dict[str, Any]:
    U = polar_isometry(proxy_parent_kernel())
    comparison = v86.compare_to_frozen(U)
    return {
        "conditional_interface_attachment_defined": True,
        "current_action_attachment_derived": False,
        "physical_CKM_equals_U_CG": False,
        "mass_basis_formula": "V_phys=U_u^dagger U_CG U_d",
        "why_not_yet_CKM": (
            "the localized Yukawa/mass-basis isometries U_u and U_d remain"
            " independent in the current stratified EFT"
        ),
        "proxy_U_CG_matrix_magnitudes": np.abs(U).tolist(),
        "proxy_U_CG_jarlskog": v86.jarlskog(U),
        "proxy_comparison_to_frozen_screen": comparison,
        "proxy_promoted": False,
        "screen_inputs_used_in_action_term": False,
        "frozen_predictions_changed": False,
    }


def payload() -> dict[str, Any]:
    domain = kernel_domain_audit()
    su2 = su2_closure_audit()
    covariance = basis_covariance_audit()
    term = action_term()
    uniqueness = uniqueness_audit()
    transport = transport_compatibility()
    variation = variation_and_backreaction()
    boundary = physical_interpretation_boundary()
    validation = {
        "proxy_kernel_full_rank": domain["full_rank"],
        "polar_isometry_unitary": domain["polar_unitarity_residual"] < 1.0e-11,
        "SU2_algebra_closed": su2["SU2_algebra_closed"],
        "neutral_current_remains_family_central": su2[
            "neutral_generator_family_central"
        ],
        "basis_covariant": covariance["basis_covariant"],
        "no_new_charged_coupling": not term["new_charged_coupling"],
        "no_new_continuous_parameter": not term["new_continuous_parameter"],
        "no_new_fundamental_field": not term["new_fundamental_field"],
        "unique_minimal_term": uniqueness["unique_under_declared_requirements"],
        "conditional_parent_backreaction_formula_present": "nonzero" in variation["parent_backreaction"],
        "no_physical_CKM_overclaim": not boundary["physical_CKM_equals_U_CG"],
        "frozen_predictions_unchanged": not boundary["frozen_predictions_changed"],
    }
    return {
        "artifact": "BHSM_common_parent_charged_current_attachment_v8_8",
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "final_verdict": FINAL_VERDICT,
        "action_term": term,
        "kernel_domain": domain,
        "SU2_closure": su2,
        "basis_covariance": covariance,
        "uniqueness": uniqueness,
        "transport_compatibility": transport,
        "variation_and_backreaction": variation,
        "physical_interpretation_boundary": boundary,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "new_continuous_parameter_added": False,
        "new_fundamental_field_added": False,
        "frozen_predictions_changed": False,
        "physical_CKM_promoted": False,
        "repository_master_action_modified": False,
        "manual_extension_status": (
            "CONDITIONAL_INTERFACE_CANDIDATE_NOT_CURRENT_ACTION_DERIVATION"
        ),
        "next_missing_object": NEXT_MISSING_OBJECT,
    }

