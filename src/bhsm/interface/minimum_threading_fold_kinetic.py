"""BHSM v6.17.0 minimum-threading axiom and fold-constraint audit.

The adopted boundary rule is tested against the leading derivative momentum
constraint of the frozen P1+GHY+B1+scalar fold.  The critical constraint fixes
the gauge-invariant threading profile to a nonzero endpoint value.  Hence the
new zero-threading trace is kinematically well defined but overconstrains a
spacetime-dependent fold tangent, and the kinetic inversion must stop.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.17.0"
SPRINT = "bhsm-minimum-threading-fold-kinetic-closure-v6-17-0"
SOURCE_MAIN_SHA = "bd1f929d2f04d37f876bb798eaf57da22adc8b21"
V616_HEAD_SHA = "8975cf83486833d32d4f5864240291fcd35819db"
PR176_MERGE_SHA = SOURCE_MAIN_SHA

AXIOM_RESULT = "BHSM_MINIMUM_NET_THREADING_AXIOM"
DOMAIN_RESULT = "BHSM_MINIMUM_THREADING_AXIOM_OVERCONSTRAINS_FOLD_CONSTRAINT"
KINETIC_RESULT = (
    "BHSM_FOLD_KINETIC_REMAINS_UNRESOLVED_BY_EXACT_OPERATOR_OBSTRUCTION"
)
PRIMARY_RESULT = DOMAIN_RESULT

AXIOM_TEXT = (
    "Sbar_Sigma(x)=1/2[S_out,Sigma,+(x)+S_out,Sigma,-(x)]=0 "
    "for all admissible scalar harmonics in the resting interface domain."
)

ARTIFACT_FILES = {
    "axiom": "BHSM_minimum_threading_axiom_and_domain_v6_17_0.json",
    "operator": "BHSM_fold_constraint_operator_Green_v6_17_0.json",
    "kinetic": "BHSM_fold_reduced_kinetic_norm_v6_17_0.json",
    "closure": "BHSM_v6_17_0_fold_closure_and_model_map.json",
}

GUARDS = {
    "new_action_term": False,
    "seam_potential_added": False,
    "seam_stiffness_coefficient": False,
    "new_numerical_primitive": False,
    "new_dimensionful_primitive": False,
    "fitted_parameter": False,
    "measured_input": False,
    "boundary_tension": False,
    "tau_J": False,
    "radion_potential": False,
    "neutral_work": False,
    "physical_bulk_Dirac_law": False,
    "generic_pseudoinverse": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "metric_assigned_to_common_core": False,
}

T = sp.symbols("t", real=True, nonnegative=True)
TAU = sp.symbols("tau", real=True, nonzero=True)
CHI_1 = sp.symbols("chi_1", real=True, positive=True)
X_CRITICAL = sp.Integer(2)
N_0 = sp.pi / 4

CHI_1_VALUE = 5.26830787154212
NU_1_VALUE = 109.6666817404231


def a0(t: sp.Expr = T) -> sp.Expr:
    return sp.sqrt(2) * sp.sin(sp.pi * t / 4)


def critical_hubble_tangent(
    t: sp.Expr = T,
    tau: sp.Expr = TAU,
    chi_1: sp.Expr = CHI_1,
) -> sp.Expr:
    """Fold derivative of H=a_t/(Na) on the critical cap."""
    return sp.simplify(
        tau * chi_1 * t / (4 * sp.sin(sp.pi * t / 4) ** 2)
    )


def inherited_shift_source(
    t: sp.Expr = T,
    tau: sp.Expr = TAU,
    chi_1: sp.Expr = CHI_1,
) -> sp.Expr:
    """The v6.12 leading momentum-constraint source J_shift=-3 H_q."""
    return sp.simplify(-3 * critical_hubble_tangent(t, tau, chi_1))


def threading_operator_coefficient(t: sp.Expr = T) -> sp.Expr:
    """Multiplication coefficient of S in the leading momentum constraint.

    The longitudinal ADM contribution is
    -3 X S/(N a^2) D_mu q.  It contains no radial derivative of the shift.
    """
    return sp.simplify(-3 * X_CRITICAL / (N_0 * a0(t) ** 2))


def required_threading_profile(
    t: sp.Expr = T,
    tau: sp.Expr = TAU,
    chi_1: sp.Expr = CHI_1,
) -> sp.Expr:
    """Solve J_shift+L_S S_q=0 for the linear threading response."""
    return sp.simplify(
        -inherited_shift_source(t, tau, chi_1)
        / threading_operator_coefficient(t)
    )


def required_endpoint_threading(
    tau: sp.Expr = TAU, chi_1: sp.Expr = CHI_1
) -> sp.Expr:
    return sp.simplify(required_threading_profile(1, tau, chi_1))


def axiom_endpoint_residual(
    tau: sp.Expr = TAU, chi_1: sp.Expr = CHI_1
) -> sp.Expr:
    """Momentum residual when the adopted rule enforces S_Sigma=0."""
    return sp.simplify(inherited_shift_source(1, tau, chi_1))


def weyl_kinetic_exact(chi_1: sp.Expr = CHI_1) -> sp.Expr:
    return sp.simplify(
        3 * chi_1**2 * (4 - sp.pi) ** 2 / (16 * sp.pi)
    )


def threading_average(s_plus: sp.Expr, s_minus: sp.Expr) -> sp.Expr:
    return sp.simplify((s_plus + s_minus) / 2)


def axiom_ledger() -> dict[str, Any]:
    return {
        "name": AXIOM_RESULT,
        "classification": "Adopted BHSM axiom",
        "statement": AXIOM_TEXT,
        "one_cap_Z2_consequence": "S_out,Sigma,+=S_out,Sigma,-=S_Sigma=0",
        "physical_interpretation": (
            "Uniform contact with an unmarked common core selects zero net "
            "longitudinal threading bias in the resting configuration."
        ),
        "old_action_derivation_claimed": False,
        "coefficient_free": True,
        "new_action_term": False,
        "seam_potential_adopted": False,
        "seam_stiffness_coefficient": None,
        "common_core": {
            "metric": None,
            "distance": None,
            "duration": None,
            "density": None,
            "ordinary_stress_tensor": None,
            "ordinary_inside_outside": None,
        },
        "historical_status": (
            "S_Sigma=0 was not previously derived or licensed as a quotient "
            "representative; v6.17 explicitly adopts it as domain data."
        ),
    }


def provenance_ledger() -> list[dict[str, str]]:
    return [
        {
            "item": "ADM momentum constraint and constant-curvature commutator",
            "status": "Adopted from established physics/mathematics",
        },
        {
            "item": "minimum net threading rule Sbar_Sigma=0",
            "status": "Adopted BHSM axiom",
        },
        {
            "item": "uniform unmarked-core interpretation",
            "status": "BHSM identification",
        },
        {
            "item": "Z2 one-cap zero trace",
            "status": "Derived consequence",
        },
        {
            "item": "critical required profile S=-tau*pi*chi_1*t/16",
            "status": "Derived consequence",
        },
        {
            "item": "nonzero normalized endpoint residual",
            "status": "Numerically validated",
        },
        {
            "item": "minimum-threading domain for a dynamical fold tangent",
            "status": "Rejected by calculation",
        },
        {
            "item": "alternative action-derived fold-compatible interface domain",
            "status": "Active construction target",
        },
    ]


def consistency_ledger() -> dict[str, Any]:
    return {
        "gauge": {
            "Sbar_invariant_under_declared_diffeomorphisms": True,
            "E_zero_gauge_allowed": True,
            "fixed_support_form": "E=0 and zeta=0 imply S_Sigma=B_Sigma",
            "result": "kinematically consistent",
        },
        "Z2": {
            "outward_relation": "S_out,Sigma,+=S_out,Sigma,-",
            "average_rule_equivalent_to_one_cap_zero": True,
            "glue_jet_difference_preserved": True,
        },
        "pole": {
            "required_constraint_profile": "-tau*pi*chi_1*t/16",
            "limit_t_to_zero": 0,
            "regular": True,
            "axiom_alone_conflicts_with_pole_regularity": False,
        },
        "junction": {
            "independent_metric_condition": (
                "kappa_1[Q_mu_nu]+2C_partial G_mu_nu^(4)"
                "=T_partial,mu_nu"
            ),
            "duplicated_by_axiom": False,
            "critical_endpoint_H_q": "tau*chi_1/2",
            "critical_scalar_flux": 0,
        },
        "Ward": {
            "Codazzi_Bianchi_counted_as_new_equation": False,
            "axiom_duplicates_Ward_identity": False,
            "role": (
                "the bulk momentum constraint evaluates the compatibility "
                "of the independent boundary trace with the junction tangent"
            ),
        },
        "support": {
            "official": "fixed-iota support (least assumption-heavy)",
            "fixed_iota": "axiom gives B_Sigma=0 in E=0 gauge",
            "composite_center_manifold": (
                "axiom gives the same invariant S_Sigma=0 after zeta is "
                "reconstructed from sigma_hat"
            ),
            "support_choice_changes_obstruction": False,
        },
        "v6_16_seam_cost": {
            "zero_trace_is_stationary": True,
            "old_action_proves_minimum": False,
            "reason": (
                "the P1 Hessian is nonzero and convention/sign dependent; "
                "the boundary rule is an axiom, not an induced potential"
            ),
            "conflict_with_homogeneous_resting_background": False,
            "conflict_with_nonconstant_fold_tangent": True,
        },
        "condition_count": {
            "unresolved_trace_before": 1,
            "new_scalar_trace_conditions": 1,
            "formal_free_trace_after": 0,
            "duplicate_conditions": 0,
            "admissible_dynamical_fold_solutions_after": 0,
            "interpretation": (
                "the count closes formally, but the inhomogeneous momentum "
                "source fails the imposed endpoint value"
            ),
        },
        "result": DOMAIN_RESULT,
    }


def leading_constraint_operator_ledger() -> dict[str, Any]:
    return {
        "derivative_expansion": "coefficient of D_mu q at q=0",
        "full_requested_unknown_vector": [
            "A",
            "B",
            "psi",
            "E",
            "delta sigma",
            "zeta",
        ],
        "gauge_invariant_threading": (
            "S=B+N0^2 zeta-a0^2 partial_rho E"
        ),
        "critical_subblock": {
            "equation": "J_shift(t)+L_S(t)S_q(t)=0",
            "J_shift": (
                "-3 tau chi_1 t/[4 sin^2(pi t/4)]"
            ),
            "L_S": "-3 X_c/[N0 a0(t)^2]",
            "X_c": 2,
            "N0": "pi/4",
            "a0": "sqrt(2) sin(pi t/4)",
            "radial_differential_order": 0,
            "reason": (
                "the ADM shift enters K_mu_nu through tangential derivatives "
                "and has no radial derivative"
            ),
            "solution": "S_q,req(t)=-tau*pi*chi_1*t/16",
        },
        "radial_measure": "N0*a0(t)^4 dt for the inherited scalar ADM pairing",
        "inner_product": (
            "<u,v>_0=integral_0^1 N0 a0^4 conjugate(u)v dt"
        ),
        "formal_adjoint_subblock": "L_S^dagger=L_S (real multiplication)",
        "Green_boundary_form_subblock": 0,
        "pole_domain": "S_q(t)=O(t), regular at t=0",
        "B1_domain_adopted": "S_q(1)=0 from S_Sigma(q)=0 for all q",
        "source_compatibility_condition": "J_shift(1)=0",
        "actual_source_endpoint": "-3 tau chi_1/2",
        "source_compatible": False,
        "subblock_kernel_dimension": 0,
        "full_L_C_constructed": False,
        "why_full_construction_stops": DOMAIN_RESULT,
        "full_formal_adjoint": None,
        "full_kernel_dimension": None,
        "full_adjoint_kernel_dimension": None,
        "Fredholm_index": None,
        "strong_ellipticity": None,
        "projector": None,
        "generic_pseudoinverse_used": False,
        "result": DOMAIN_RESULT,
    }


def endpoint_obstruction_ledger() -> dict[str, Any]:
    endpoint_required = -math.pi * CHI_1_VALUE / 16
    endpoint_residual = -3 * CHI_1_VALUE / 2
    return {
        "upper_exterior_tau_plus": {
            "partial_q_S_required": endpoint_required,
            "axiom_value": 0.0,
            "momentum_residual": endpoint_residual,
        },
        "lower_core_tau_minus": {
            "partial_q_S_required": -endpoint_required,
            "axiom_value": 0.0,
            "momentum_residual": -endpoint_residual,
        },
        "scalar_sign_plus": "same",
        "scalar_sign_minus": "same",
        "scalar_sign_independent": True,
        "analytic_q_to_zero": (
            "S_Sigma(q)=-tau*pi*chi_1*q/16+O(q^2)"
        ),
        "finite_q_consequence": (
            "by continuity no sufficiently small q>0 sequence satisfying "
            "S_Sigma=0 can converge to the fold tangent"
        ),
        "convergence_study_started": False,
        "reason": "the q=0 compatibility residual is bounded away from zero",
        "normalized_chi_1": CHI_1_VALUE,
        "normalized_nu_1": NU_1_VALUE,
        "result": DOMAIN_RESULT,
    }


def green_operator_ledger() -> dict[str, Any]:
    return {
        "local_unconstrained_inverse": (
            "L_S^-1 J=-N0 a0^2 J/(3 X_c)"
        ),
        "local_inverse_result": "S_q,req=-tau*pi*chi_1*t/16",
        "maps_source_into_adopted_domain": False,
        "Green_operator_on_adopted_domain": None,
        "shooting_method_run": False,
        "collocation_method_run": False,
        "spectral_method_run": False,
        "residual_norm": None,
        "boundary_residual": "abs(S_q,req(1))=pi*chi_1/16",
        "boundary_residual_numeric": math.pi * CHI_1_VALUE / 16,
        "method_agreement": None,
        "mesh_convergence": None,
        "kernel_orthogonality": None,
        "upper_lower_consistency": "equal magnitude, opposite sign",
        "scalar_sign_independence": True,
        "stop_rule_applied": True,
        "result": DOMAIN_RESULT,
    }


def kinetic_ledger() -> dict[str, Any]:
    return {
        "K_shift_endpoint_red": None,
        "reason_K_shift_unavailable": (
            "the adopted endpoint domain rejects the leading fold momentum "
            "source before a constraint Schur complement exists"
        ),
        "K_scalar_at_fold": ">=2>0",
        "K_Weyl_exact": "3 chi_1^2(4-pi)^2/(16 pi)>0",
        "K_Weyl_numeric": float(
            3
            * CHI_1_VALUE**2
            * (4 - math.pi) ** 2
            / (16 * math.pi)
        ),
        "k_q_E": None,
        "error_estimate": None,
        "sign": None,
        "positive_norm": False,
        "ghost": False,
        "null_or_strongly_coupled": False,
        "nondynamical": False,
        "domain_inconsistent_for_fold_promotion": True,
        "sheet_dependence": (
            "obstruction has opposite sign and equal nonzero magnitude"
        ),
        "scalar_sign_dependence": "none",
        "q_to_zero_limit": None,
        "fold_coordinate_promoted_to_4D_field": False,
        "result": KINETIC_RESULT,
    }


def phase_separation_ledger() -> dict[str, Any]:
    return {
        "classification": "BHSM identification",
        "status": "conditional and not adopted as a new evolution law",
        "early_or_initial_resting_phase": {
            "D_mu_q": 0,
            "Sbar_Sigma": 0,
            "minimum_threading_axiom_applies": True,
        },
        "fold_transition_phase": {
            "D_mu_q": "nonzero",
            "constraint_required_trace": (
                "S_Sigma(x)=-tau*pi*chi_1*q(x)/16+O(q^2), "
                "up to the fixed potential convention"
            ),
            "minimum_threading_axiom_as_hard_domain_applies": False,
        },
        "late_or_final_resting_phase": {
            "D_mu_q": 0,
            "physical_longitudinal_shift": 0,
            "zero_constant_representative_selected": True,
        },
        "constant_threading_potential": (
            "a spacetime-constant shift potential is the trivial stabilizer "
            "identified in v6.16 because its gradient vanishes"
        ),
        "white_hole_interpretation": (
            "possible BHSM interpretation of an early M4/interface release, "
            "not derived by the present constraint calculation"
        ),
        "time_assigned_to_common_core": False,
        "time_location": "M4/interface history only",
        "required_for_adoption": (
            "a covariant phase criterion or action-derived switching/evolution "
            "law joining the resting and transition domains"
        ),
        "rescues_hard_all_harmonic_domain": False,
        "reason": (
            "a phase-dependent rule is a different domain from imposing "
            "Sbar_Sigma=0 on every dynamical harmonic"
        ),
    }


def static_sheet_ledger() -> dict[str, Any]:
    return {
        "fixed_mu_curvature": "B_tau^red=-tau(nu_1/2)q+O(q^2)",
        "exterior_tau_plus": "negative reduced static curvature",
        "core_tau_minus": "positive reduced static curvature",
        "physical_mass_numerator": False,
        "m_ext_squared": None,
        "m_core_squared": None,
        "reason": (
            "no positive Einstein-frame kinetic norm and no matching "
            "off-shell Einstein-frame potential curvature are available"
        ),
    }


def closure_map_ledger() -> dict[str, Any]:
    return {
        "parent_core_topology": {
            "adopted_foundation": "common core non-spatiotemporal",
            "derived_equations": "topology/orientation ledgers",
            "active_construction_target": "core transfer mechanism",
            "rejected_route": "assigning ordinary core metric data",
        },
        "P1_geometry": {
            "adopted_foundation": "conditional P1+GHY parent representative",
            "derived_equations": "bulk constraints and junction projections",
            "active_construction_target": "parent coefficient/source selection",
            "rejected_route": "GHY as physical tension",
        },
        "B1_intrinsic_action": {
            "adopted_foundation": "provisional intrinsic B1 action",
            "derived_equations": "metric junction and Ward identities",
            "active_construction_target": "coefficient-lock/source theorem",
            "rejected_route": "duplicate longitudinal junction equation",
        },
        "scalar_wall_fold": {
            "adopted_foundation": "fixed-C_partial Puiseux cap domain",
            "derived_equations": "two static curvature sheets",
            "numerical_validation": "chi_1 and nu_1 continuation data",
            "active_construction_target": "fold-compatible interface domain",
            "rejected_route": "direct q=0 level-set division",
        },
        "fold_kinetic_sector": {
            "adopted_foundation": "minimum net threading axiom",
            "derived_equations": "critical threading subconstraint",
            "active_construction_target": (
                "replace or refine the axiom with an action-derived condition "
                "admitting the required nonzero linear threading response"
            ),
            "rejected_route": "S_Sigma=0 for nonconstant fold harmonics",
        },
        "gauge_connections": {
            "adopted_foundation": "boundary gauge-action scaffolds",
            "active_construction_target": "normalization and localized domain",
        },
        "fermionic_action_domain": {
            "adopted_foundation": "conditional chiral representation ledger",
            "active_construction_target": "complete sourced Dirac action/domain",
        },
        "charged_current_CKM": {
            "adopted_foundation": "basis-misalignment interpretation",
            "active_construction_target": "independent current normalization",
        },
        "neutral_propagation_PMNS": {
            "adopted_foundation": "effective neutral-response scaffolds",
            "active_construction_target": "physical operator and scale closure",
        },
        "dimensionful_scale_bridge": {
            "adopted_foundation": "dimensionless normalized representatives",
            "active_construction_target": "sourced absolute-scale mechanism",
        },
        "scalar_topographic_sector": {
            "adopted_foundation": "finite-basis conditional operator",
            "active_construction_target": "full action-level Hessian/spectrum",
        },
        "prediction_falsification_layer": {
            "adopted_foundation": "frozen screen ledger",
            "active_construction_target": "independent mode-selection rules",
            "frozen_predictions_changed": False,
        },
    }


def verdict_ledger() -> dict[str, Any]:
    return {
        "domain_theorem": DOMAIN_RESULT,
        "kinetic_theorem": KINETIC_RESULT,
        "axiom_adopted": True,
        "axiom_kinematically_gauge_and_Z2_consistent": True,
        "axiom_compatible_with_homogeneous_resting_background": True,
        "axiom_compatible_with_dynamical_fold_tangent": False,
        "unresolved_interface_trace_count_before": 1,
        "formal_trace_count_after_axiom": 0,
        "admissible_fold_domain_after_axiom": "empty at leading D_mu q order",
        "Green_operator_ready": False,
        "fold_kinetic_calculable": False,
        "fold_route": "stopped by the mandated inconsistency rule",
        "exact_remaining_fold_issue": (
            "derive an action-selected interface condition whose endpoint "
            "linear response admits partial_q S_Sigma=-tau*pi*chi_1/16"
        ),
        "model_wide_completion_claim": False,
    }


def integrity_ledger() -> dict[str, Any]:
    return {
        "preserved": {
            "v6_15": "BHSM_Z2_SYMPLECTIC_FLUX_LEAVES_ONE_INTERFACE_TRACE",
            "v6_16": "BHSM_SEAM_SLIDE_HAS_NONZERO_HIGHER_ORDER_ACTION_COST",
            "lambda_jet": "S_out,+-S_out,-",
            "Sbar": "(S_out,++S_out,-)/2",
            "F0_equals_M4_squared": "pi/2",
            "K_scalar": ">=2>0",
            "K_Weyl": "3 chi_1^2(4-pi)^2/(16 pi)>0",
            "chi_1": CHI_1_VALUE,
            "nu_1": NU_1_VALUE,
            "J_shift": "-3 tau chi_1 t/[4 sin^2(pi t/4)]",
        },
        "guards": dict(GUARDS),
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_16_head_sha": V616_HEAD_SHA,
        "pr_176_merge_sha": PR176_MERGE_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "axiom": {
            **_common("BHSM_minimum_threading_axiom_and_domain_v6_17_0"),
            "axiom": axiom_ledger(),
            "provenance": provenance_ledger(),
            "consistency": consistency_ledger(),
            "endpoint_obstruction": endpoint_obstruction_ledger(),
        },
        "operator": {
            **_common("BHSM_fold_constraint_operator_Green_v6_17_0"),
            "constraint_operator": leading_constraint_operator_ledger(),
            "Green": green_operator_ledger(),
        },
        "kinetic": {
            **_common("BHSM_fold_reduced_kinetic_norm_v6_17_0"),
            "kinetic": kinetic_ledger(),
            "static_sheets": static_sheet_ledger(),
        },
        "closure": {
            **_common("BHSM_v6_17_0_fold_closure_and_model_map"),
            "verdict": verdict_ledger(),
            "phase_separation": phase_separation_ledger(),
            "model_map": closure_map_ledger(),
            "integrity": integrity_ledger(),
        },
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def artifact_bytes() -> dict[str, bytes]:
    payloads = artifact_payloads()
    return {
        ARTIFACT_FILES[key]: deterministic_json(payload).encode("utf-8")
        for key, payload in payloads.items()
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
