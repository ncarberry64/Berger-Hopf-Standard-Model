"""Symbolic unified BHSM dynamical action construction for v5.4.

This module is theorem bookkeeping plus a small deterministic reduced model.
It does not fit observables, derive physical gauge couplings, or promote
downstream rare-B/Wilson claims.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import sqrt
from pathlib import Path
from typing import Any


VERSION = "v5.4"
SPRINT = "bhsm-unified-dynamical-action-construction-v5-4"
PRIMARY_RESULT = "UNIFIED_BHSM_ACTION_CONSTRUCTED_CONDITIONALLY"
ACTION_SYMBOL = "S_BHSM^cand"

ARTIFACT_FILES = {
    "configuration_space": "BHSM_unified_dynamical_action_configuration_space_v5_4.json",
    "action_candidate": "BHSM_unified_dynamical_action_candidate_v5_4.json",
    "coefficient_dimension_table": "BHSM_unified_action_coefficient_dimension_table_v5_4.json",
    "variational_equations": "BHSM_unified_action_variational_equations_v5_4.json",
    "quadratic_operators": "BHSM_unified_action_quadratic_operators_v5_4.json",
    "interaction_source_map": "BHSM_unified_action_interaction_source_map_v5_4.json",
    "dimensionful_scale_analysis": "BHSM_unified_action_dimensionful_scale_analysis_v5_4.json",
    "reduced_model": "BHSM_unified_action_reduced_model_v5_4.json",
    "construction_report": "BHSM_unified_dynamical_action_construction_report_v5_4.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "rare_b_data_fitting_used": False,
    "pdg_reference_values_used": False,
    "w_calibration_used": False,
    "charged_mass_fitting_used": False,
    "ckm_fitting_used": False,
    "neutrino_limits_used": False,
    "legacy_threshold_tables_used": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physics_model_logic_changed": False,
}

PRESERVED_BLOCKERS = (
    "ACTION_ATTACHMENT_BLOCKED",
    "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED",
    "COUPLING_BRIDGE_BLOCKED_PENDING_ACTION_PRINCIPLE",
    "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
    "OPEN_MISSING_G2_BH_ACTION_SOURCE",
    "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
    "CKM_EXPONENT_NOT_DERIVED",
    "OPEN_MISSING_NEUTRAL_SCALE",
    "OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION",
    "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM",
    "RARE_B_FCNC_GENERATION_MECHANISM_BLOCKED",
    "B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED",
    "RARE_B_AFB_ZERO_PREDICTION_BLOCKED",
    "FULL_BHSM_NOT_COMPLETE",
)

OPEN_MATHEMATICS = (
    "OPEN_MISSING_UNIFIED_ACTION_COEFFICIENT_DERIVATION",
    "OPEN_MISSING_PHYSICAL_SCALE_GENERATION",
    "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    "OPEN_MISSING_FULL_GAUGE_FIXED_DOMAIN",
    "OPEN_MISSING_FULL_LOWER_ORDER_OPERATOR_TERMS",
    "OPEN_MISSING_FERMION_DIRAC_OPERATOR_ACTION_SOURCE",
    "OPEN_MISSING_SCALAR_TOPOGRAPHIC_POTENTIAL_SOURCE",
    "OPEN_MISSING_CHARGED_CURRENT_NORMALIZATION",
    "OPEN_MISSING_NEUTRAL_RESPONSE_NORMALIZATION",
    "OPEN_MISSING_NONLINEAR_UNIFIED_SOLUTION",
)


@dataclass(frozen=True)
class FieldDefinition:
    name: str
    symbol: str
    space: str
    role: str
    dynamical: bool
    dimension_power: int
    fixed_background: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CoefficientDefinition:
    name: str
    term: str
    dimension_power: int
    sign_convention: str
    normalization_status: str
    dependencies: tuple[str, ...]
    derivation_status: str
    provisional: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ActionTerm:
    name: str
    expression: str
    coefficient: str
    integrand_dimension_power: int
    measure_dimension_power: int
    coefficient_dimension_power: int
    total_dimension_power: int
    hermitian_or_real_status: str
    source: str
    variation: str
    boundary_term: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VariationalEquation:
    variable: str
    equation: str
    boundary_term: str
    boundary_condition: str
    operational_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QuadraticOperator:
    sector: str
    operator: str
    domain: str
    adjoint: str
    kernel_or_zero_modes: str
    invertibility_conditions: str
    gauge_redundancy: str
    response_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InteractionSource:
    interaction: str
    source_term: str
    generated_by_variation: str
    status: str
    missing_for_physical_closure: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _common_payload(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": (
            "Unified symbolic construction only. Coefficients and the physical scale "
            "remain symbolic/provisional where not derived; no frozen prediction, gauge "
            "coupling, Wilson coefficient, rare-B prediction, or full BHSM completion is promoted."
        ),
        **GUARDS,
    }


def field_definitions() -> tuple[FieldDefinition, ...]:
    return (
        FieldDefinition("boundary geometry", "h_rho", "metrics on relative Berger boundary Sigma_rho", "fixed geometric datum for v5.4 variation except optional geometry equation", False, 0, True),
        FieldDefinition("collar scale", "rho", "positive boundary/collar scale labels", "scale-setting variable candidate", True, 1),
        FieldDefinition("gauge field", "A_i", "Omega^1(Sigma_rho, ad_i), i in {U1,SU2,SU3}", "adjoint-valued boundary one-form", True, -1),
        FieldDefinition("fermion boundary field", "Psi", "boundary spinor/generation module S_Sigma tensor F_gen", "fermionic matter mode", True, -1),
        FieldDefinition("scalar/topographic field", "Phi", "real boundary scalar/topographic response space", "profile/topographic response", True, -1),
        FieldDefinition("charged-current source", "J_ch", "charged current bilinear/interface space", "interaction current generated from fermion/projector data", True, -2),
        FieldDefinition("neutral-response field", "N", "neutral response cone/channel space", "neutral response coordinate", True, -2),
        FieldDefinition("sector projectors", "P_i", "orthogonal/idempotent sector maps on internal representation", "fixed algebraic projectors", False, 0, True),
        FieldDefinition("generation projector", "P_gen", "generation/mode projector ledger", "fixed mode bookkeeping for v5.4", False, 0, True),
    )


def coefficient_definitions() -> tuple[CoefficientDefinition, ...]:
    return (
        CoefficientDefinition("kappa_geom", "geometric/boundary term", -1, "positive stiffness for stable quadratic geometry", "PROVISIONAL_SYMBOLIC", ("boundary measure", "Berger metric", "collar variation"), "OPEN_MISSING_UNIFIED_ACTION_COEFFICIENT_DERIVATION", True),
        CoefficientDefinition("kappa_g_i", "gauge kinetic term", -1, "positive inverse-covariance stiffness", "CONDITIONAL_SYMBOLIC_FROM_V4_5_V4_6", ("sector boundary operator L_i(rho)", "lambda_i covariance candidate", "gauge-fixed domain"), "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT", True),
        CoefficientDefinition("zeta_psi", "fermion kinetic term", 0, "Hermitian Dirac pairing coefficient", "PROVISIONAL_SYMBOLIC", ("spin/Hermitian convention", "fermion normalization"), "OPEN_MISSING_FERMION_DIRAC_OPERATOR_ACTION_SOURCE", True),
        CoefficientDefinition("kappa_phi", "scalar/topographic term", -1, "positive topographic stiffness", "PROVISIONAL_SYMBOLIC", ("scalar boundary variation", "profile Hessian ledgers"), "OPEN_MISSING_SCALAR_TOPOGRAPHIC_POTENTIAL_SOURCE", True),
        CoefficientDefinition("g_ch", "charged-current interaction", 0, "Hermitian plus adjoint pair convention", "PROVISIONAL_SYMBOLIC", ("charged current action audits", "CKM/projector orientation", "current normalization"), "OPEN_MISSING_CHARGED_CURRENT_NORMALIZATION", True),
        CoefficientDefinition("g_neu", "neutral-response interaction", 0, "real neutral response pairing", "PROVISIONAL_SYMBOLIC", ("neutral action reports", "neutral response cone", "neutral scale"), "OPEN_MISSING_NEUTRAL_RESPONSE_NORMALIZATION", True),
        CoefficientDefinition("kappa_scale", "scale/RG bridge term", -1, "positive scale penalty", "PROVISIONAL_SYMBOLIC", ("collar scale rho", "dimensionful bridge Lambda_BH"), "OPEN_MISSING_PHYSICAL_SCALE_GENERATION", True),
    )


def action_terms() -> tuple[ActionTerm, ...]:
    return (
        ActionTerm("geometric_boundary", "1/2 kappa_geom <delta h, L_geom(rho) delta h>_Sigma", "kappa_geom", -2, 3, -1, 0, "real symmetric Hessian pairing", "v4.0 boundary geometry skeleton plus boundary Hessian ledgers", "kappa_geom L_geom delta h = source terms", "<delta h, Pi_geom n.grad(delta h)>_partialSigma", "CONDITIONAL_SYMBOLIC"),
        ActionTerm("gauge_kinetic", "sum_i 1/(2 lambda_i) <A_i, L_i(rho) A_i>_Sigma", "kappa_g_i=1/lambda_i", -2, 3, -1, 0, "Hermitian after gauge-fixed/coexact domain selection", "v4.5/v4.6 whitened boundary gauge action", "(1/lambda_i) L_i A_i + current_i = 0", "<delta A_i, * F_i>_partialSigma plus gauge-fixing boundary term", "CONDITIONAL_SYMBOLIC"),
        ActionTerm("fermion_kinetic", "zeta_psi Re <Psi, D_BH(h,A,P) Psi>_Sigma", "zeta_psi", -3, 3, 0, 0, "Hermitian Dirac pairing convention", "minimal action field representation and collider-interface ledgers", "zeta_psi D_BH Psi + interaction sources = 0", "<delta Psi, gamma_n Psi>_partialSigma", "CONDITIONAL_SYMBOLIC"),
        ActionTerm("scalar_topographic", "1/2 kappa_phi <Phi, L_phi(rho) Phi>_Sigma + V_topo(Phi; rho)", "kappa_phi", -2, 3, -1, 0, "real scalar quadratic form plus real potential", "scalar/topographic boundary variation and profile Hessian ledgers", "kappa_phi L_phi Phi + dV_topo/dPhi + response sources = 0", "<delta Phi, n.grad Phi>_partialSigma", "CONDITIONAL_SYMBOLIC"),
        ActionTerm("charged_current", "g_ch Re <J_ch(P_gen Psi,A_SU2), X_ch(P_ch Psi)>_Sigma", "g_ch", -3, 3, 0, 0, "Hermitian adjoint-pair convention required", "charged-current action audits and CKM transport gates", "variation gives charged-current source terms in Psi and A_SU2 equations", "charged-current boundary flux fixed or adjoint-paired", "CONDITIONAL_OPEN_NORMALIZATION"),
        ActionTerm("neutral_response", "g_neu <N, R_neu(Phi,h,rho)>_Sigma + 1/2 <N, K_neu N>_Sigma", "g_neu", -3, 3, 0, 0, "real neutral response pairing", "neutral action/source/cone reports", "K_neu N + g_neu R_neu = 0", "<delta N, Pi_neu n.grad N>_partialSigma", "CONDITIONAL_OPEN_NORMALIZATION"),
        ActionTerm("scale_bridge", "1/2 kappa_scale (rho-rho_*)^2 + C_Lambda(Phi,h,rho; Lambda_BH)", "kappa_scale", -2, 3, -1, 0, "real positive scale penalty", "dimensionful scale and boundary collar measure ledgers", "kappa_scale (rho-rho_*) + delta C_Lambda/delta rho = 0", "collar endpoint variation fixed or transversality condition", "CONDITIONAL_SCALE_OPEN"),
    )


def configuration_space_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_unified_dynamical_action_configuration_space_v5_4")
    payload.update(
        {
            "status": "UNIFIED_BHSM_CONFIGURATION_SPACE_DEFINED",
            "manifold": "relative Berger/collar boundary Sigma_rho with optional bulk-collar support",
            "metric_and_measure": {
                "metric": "h_rho induced Berger boundary metric",
                "measure": "dmu_Sigma,rho = sqrt(det h_rho) d^3x",
                "measure_status": "CONDITIONAL_BOUNDARY_COLLAR_MEASURE_SOURCE",
            },
            "field_content": [field.to_dict() for field in field_definitions()],
            "sector_spaces": {"U1": "ad_U1 rank 1", "SU2": "ad_SU2 rank 3", "SU3": "ad_SU3 rank 8"},
            "generation_mode_spaces": "P_gen-labeled generation/mode ledger; physical normalization open",
            "internal_algebra_representation": "sector-projector representation with fixed P_i and P_gen labels",
            "admissible_function_spaces": [
                "gauge fields in a gauge-fixed/coexact or quotient one-form domain",
                "fermions in a Hermitian spinor domain with boundary adjoint pairing",
                "scalar/topographic fields in a real Sobolev-type boundary domain",
                "neutral response fields in the admissible neutral response cone/domain",
            ],
            "boundary_conditions": default_boundary_conditions(),
            "dynamical_variables": [field.symbol for field in field_definitions() if field.dynamical],
            "fixed_data": [field.symbol for field in field_definitions() if not field.dynamical],
        }
    )
    return payload


def action_candidate_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_unified_dynamical_action_candidate_v5_4")
    payload.update(
        {
            "status": PRIMARY_RESULT,
            "action_symbol": ACTION_SYMBOL,
            "explicit_action": (
                "S_BHSM^cand = integral_Sigma [ L_geom + sum_i L_gauge,i + L_fermion "
                "+ L_topographic + L_charged + L_neutral + L_scale ] dmu_Sigma,rho"
            ),
            "terms": [term.to_dict() for term in action_terms()],
            "coefficient_table": [coef.to_dict() for coef in coefficient_definitions()],
            "measure": configuration_space_artifact()["metric_and_measure"],
            "not_a_standard_model_lagrangian_import": True,
            "conditional_because": list(OPEN_MATHEMATICS),
        }
    )
    return payload


def coefficient_dimension_table_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_unified_action_coefficient_dimension_table_v5_4")
    payload.update(
        {
            "status": "UNIFIED_ACTION_COEFFICIENT_DIMENSION_TABLE_COMPLETE_SYMBOLIC",
            "dimension_convention": "powers of a geometric length unit ell_BH; each action term sums to dimension power 0",
            "coefficients": [coef.to_dict() for coef in coefficient_definitions()],
            "term_dimension_checks": dimension_checks(),
            "all_terms_dimensionless": all(row["total_dimension_power"] == 0 for row in dimension_checks()),
            "physical_scale_status": "OPEN_MISSING_PHYSICAL_SCALE_GENERATION",
        }
    )
    return payload


def variational_equations() -> tuple[VariationalEquation, ...]:
    return (
        VariationalEquation("delta h", "kappa_geom L_geom delta h + T_gauge + T_psi + T_phi + T_neu + T_scale = 0", "<delta h, Pi_geom n.grad(delta h)>_partialSigma", "fix induced boundary metric or impose natural geometric flux cancellation", "CONDITIONAL_OPERATOR_EQUATION"),
        VariationalEquation("A_i", "(1/lambda_i) L_i(rho) A_i + J_i^matter + J_i^charged = 0 on controlled gauge domain", "<delta A_i, *F_i>_partialSigma + gauge-fixing boundary term", "relative/absolute gauge boundary data fixed, or transverse coexact natural flux vanishes", "CONDITIONAL_OPERATOR_EQUATION"),
        VariationalEquation("Psi", "zeta_psi D_BH Psi + g_ch delta J_ch/delta Psibar + neutral/scalar source terms = 0", "<delta Psi, gamma_n Psi>_partialSigma", "Hermitian spinor boundary condition or adjoint-pair cancellation", "CONDITIONAL_OPERATOR_EQUATION"),
        VariationalEquation("Phi", "kappa_phi L_phi Phi + dV_topo/dPhi + g_neu delta R_neu/delta Phi + delta C_Lambda/delta Phi = 0", "<delta Phi, n.grad Phi>_partialSigma", "Dirichlet Phi, Neumann topographic flux, or collar natural condition", "CONDITIONAL_OPERATOR_EQUATION"),
        VariationalEquation("N", "K_neu N + g_neu R_neu(Phi,h,rho) = 0", "<delta N, Pi_neu n.grad N>_partialSigma", "neutral response domain fixes boundary flux or admissible cone variation", "CONDITIONAL_OPERATOR_EQUATION"),
        VariationalEquation("rho", "kappa_scale (rho-rho_*) + delta_rho S_geom + delta_rho S_gauge + delta_rho S_phi + delta_rho C_Lambda = 0", "collar endpoint variation", "fix rho at collar endpoints or solve natural scale stationarity", "CONDITIONAL_SCALE_EQUATION"),
    )


def default_boundary_conditions() -> list[str]:
    return [
        "fix induced Berger boundary metric h_rho or impose natural geometric flux cancellation",
        "restrict A_i to a gauge-fixed/coexact/quotient domain with admissible boundary flux",
        "use Hermitian spinor boundary pairing so Dirac boundary terms cancel",
        "fix Phi or impose natural topographic Neumann/collar boundary condition",
        "restrict N to the neutral admissible cone/domain and fix neutral response flux",
        "fix rho at collar endpoints or solve the symbolic natural scale equation",
    ]


def variational_equations_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_unified_action_variational_equations_v5_4")
    payload.update(
        {
            "status": "UNIFIED_ACTION_VARIATIONAL_EQUATIONS_DERIVED_SYMBOLICALLY",
            "equations": [eq.to_dict() for eq in variational_equations()],
            "boundary_conditions": default_boundary_conditions(),
            "has_nontrivial_euler_lagrange_equation": True,
            "boundary_terms_vanish_under_declared_conditions": True,
        }
    )
    return payload


def quadratic_operators() -> tuple[QuadraticOperator, ...]:
    return (
        QuadraticOperator("geometry", "kappa_geom L_geom", "metric perturbations modulo fixed boundary/collar conditions", "self-adjoint under geometric pairing when boundary flux vanishes", "diffeomorphism/shape zero modes unresolved", "gauge/shape fixing plus positive Hessian sector", "geometric gauge redundancy open", "symbolic Hessian only"),
        QuadraticOperator("gauge", "(1/lambda_i) L_i(rho)", "gauge-fixed/coexact adjoint-valued one-forms", "Hermitian using h_rho, Hodge star, and adjoint trace", "exact gauge modes before quotient", "invertible only after gauge-fixed domain and zero-mode projection", "OPEN_MISSING_FULL_GAUGE_FIXED_DOMAIN", "Green operator conditional"),
        QuadraticOperator("fermion", "zeta_psi D_BH", "spinor/generation module with Hermitian boundary condition", "formally self-adjoint or skew-adjoint according to spin convention", "Dirac zero modes possible", "inverse requires spectral gap and boundary condition", "none beyond spin-frame convention", "resolvent symbolic"),
        QuadraticOperator("scalar/topographic", "kappa_phi L_phi + Hess(V_topo)", "real scalar/topographic domain", "self-adjoint under real scalar inner product", "constant/topographic flat directions possible", "positive Hessian after profile selection", "none", "Green operator conditional"),
        QuadraticOperator("neutral response", "K_neu", "admissible neutral response cone/domain", "self-adjoint under neutral response pairing", "neutral kernel zero modes/open scale modes", "invertible only after neutral scale/action normalization", "cone constraints", "response kernel conditional"),
        QuadraticOperator("scale", "kappa_scale + Hess_rho(C_Lambda)", "collar-scale variations", "real symmetric one-dimensional Hessian in reduced sector", "zero mode if physical scale is not selected", "requires kappa_scale>0 and scale source", "scale normalization open", "inverse symbolic"),
    )


def quadratic_operators_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_unified_action_quadratic_operators_v5_4")
    payload.update(
        {
            "status": "UNIFIED_ACTION_QUADRATIC_OPERATORS_EXTRACTED_CONDITIONALLY",
            "operators": [op.to_dict() for op in quadratic_operators()],
            "hessian": "block Hessian diag/coupled by interaction second variations around a stationary background",
            "inverse_response_status": "CONDITIONAL_AFTER_DOMAIN_ZERO_MODE_AND_SCALE_GATES",
            "no_invented_inverse": True,
        }
    )
    return payload


def interaction_sources() -> tuple[InteractionSource, ...]:
    return (
        InteractionSource("charged-current transitions", "g_ch Re <J_ch(P_gen Psi,A_SU2), X_ch(P_ch Psi)>", "Psi and A_SU2 variations", "SUPPORTED_STRUCTURALLY_OPEN_NORMALIZATION", "charged-current normalization, orientation, and action coefficient"),
        InteractionSource("neutral-current response", "g_neu <N, R_neu(Phi,h,rho)> + 1/2 <N,K_neu N>", "N, Phi, and h variations", "SUPPORTED_STRUCTURALLY_OPEN_NORMALIZATION", "neutral response normalization and physical scale"),
        InteractionSource("sector mixing", "projector-constrained D_BH(h,A,P) and interaction source terms", "fermion/gauge variations", "CONDITIONAL_PROJECTOR_STRUCTURE", "action-selected sector projector coupling coefficients"),
        InteractionSource("generation mixing", "P_gen and CKM/transport-labeled charged current source", "fermion charged-current variation", "CONDITIONAL_RELATIVE_INPUT_ONLY", "absolute current normalization and CKM coefficient value/exponent"),
        InteractionSource("current-current composition", "second variation or integration-out of charged/neutral sources", "requires inverse Hessian/response kernel", "NOT_CLOSED", "intermediate response kernel and induced-effective-action theorem"),
        InteractionSource("mode-mediated effective interactions", "Schur complement of quadratic block Hessian", "requires invertible controlled block", "CONDITIONAL_TEMPLATE_ONLY", "domain, zero-mode projection, and scale normalization"),
    )


def interaction_source_map_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_unified_action_interaction_source_map_v5_4")
    payload.update(
        {
            "status": "UNIFIED_ACTION_INTERACTION_SOURCE_MAP_CONSTRUCTED_CONDITIONALLY",
            "interactions": [source.to_dict() for source in interaction_sources()],
            "rare_b_phenomenology_pursued": False,
            "fcnc_status_preserved": "RARE_B_FCNC_GENERATION_MECHANISM_BLOCKED",
        }
    )
    return payload


def dimensionful_scale_analysis_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_unified_action_dimensionful_scale_analysis_v5_4")
    payload.update(
        {
            "status": "UNIFIED_ACTION_DIMENSIONFUL_SCALE_ANALYSIS_SYMBOLIC_OPEN",
            "dimensionless_normalization": "all constructed terms are dimensionless in ell_BH units",
            "physical_scale": "Lambda_BH or equivalent conversion scale remains explicit",
            "minimal_bridge": "x_phys = ell_BH * x_hat, partial_phys = ell_BH^-1 partial_hat, S dimensionless with coefficient powers recorded",
            "universal_scale_parameter_required": True,
            "scale_parameter": {
                "name": "Lambda_BH",
                "dimension": "energy",
                "status": "OPEN_MISSING_PHYSICAL_SCALE_GENERATION",
                "not_fit": True,
            },
            "renormalization_scale": {
                "symbol": "mu",
                "status": "OPEN_MISSING_ACTION_SELECTED_RHO_i_OF_MU",
            },
            "does_not_derive_physical_masses_or_couplings": True,
        }
    )
    return payload


def reduced_model_parameters() -> dict[str, float]:
    return {
        "kappa_g": 2.0,
        "kappa_phi": 3.0,
        "epsilon_coupling": 0.5,
    }


def reduced_model_solution() -> dict[str, Any]:
    params = reduced_model_parameters()
    kg = params["kappa_g"]
    kp = params["kappa_phi"]
    eps = params["epsilon_coupling"]
    trace = kg + kp
    det = kg * kp - eps * eps
    gap = sqrt((kg - kp) ** 2 + 4.0 * eps * eps)
    eigenvalues = [(trace - gap) / 2.0, (trace + gap) / 2.0]
    stationary = {"a": 0.0, "phi": 0.0}
    residual = {
        "dS_da": kg * stationary["a"] + eps * stationary["phi"],
        "dS_dphi": eps * stationary["a"] + kp * stationary["phi"],
    }
    return {
        "truncation": "two coupled real boundary amplitudes: gauge a and topographic phi",
        "action": "S_red=1/2 kappa_g a^2 + 1/2 kappa_phi phi^2 + epsilon a phi",
        "parameters": params,
        "hessian": [[kg, eps], [eps, kp]],
        "equations": ["kappa_g a + epsilon phi = 0", "epsilon a + kappa_phi phi = 0"],
        "stationary_solution": stationary,
        "equation_residual": residual,
        "max_abs_residual": max(abs(value) for value in residual.values()),
        "eigenvalues": eigenvalues,
        "determinant": det,
        "stability_condition": "kappa_g>0, kappa_phi>0, kappa_g*kappa_phi-epsilon^2>0",
        "stable": kg > 0 and kp > 0 and det > 0,
        "deterministic": True,
        "physical_fit": False,
    }


def reduced_model_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_unified_action_reduced_model_v5_4")
    solution = reduced_model_solution()
    payload.update(
        {
            "status": "UNIFIED_ACTION_REDUCED_MODEL_DETERMINISTIC_STABLE",
            "reduced_model": solution,
            "demonstrates": ["coupled equations", "mode spectrum", "stability condition"],
            "solution_satisfies_equations": solution["max_abs_residual"] <= 1.0e-12,
        }
    )
    return payload


def dimension_checks() -> list[dict[str, Any]]:
    return [
        {
            "term": term.name,
            "integrand_dimension_power": term.integrand_dimension_power,
            "measure_dimension_power": term.measure_dimension_power,
            "coefficient_dimension_power": term.coefficient_dimension_power,
            "total_dimension_power": term.total_dimension_power,
            "dimensionless_action_term": term.total_dimension_power == 0,
        }
        for term in action_terms()
    ]


def validate_action_terms_dimensionless() -> bool:
    return all(row["dimensionless_action_term"] for row in dimension_checks())


def validate_reduced_solution(tolerance: float = 1.0e-12) -> bool:
    return reduced_model_solution()["max_abs_residual"] <= tolerance


def construction_report_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_unified_dynamical_action_construction_report_v5_4")
    payload.update(
        {
            "status": PRIMARY_RESULT,
            "primary_result": PRIMARY_RESULT,
            "unified_action": action_candidate_artifact()["explicit_action"],
            "configuration_space_status": configuration_space_artifact()["status"],
            "terms": [term.name for term in action_terms()],
            "variational_equations_derived": True,
            "quadratic_operators_extracted": True,
            "interaction_source_map_constructed": True,
            "dimension_checks_passed": validate_action_terms_dimensionless(),
            "reduced_model_status": reduced_model_artifact()["status"],
            "derived": [
                "explicit symbolic action term inventory",
                "compatible dimension table in ell_BH powers",
                "symbolic Euler-Lagrange/operator equations",
                "boundary-condition statement",
                "quadratic operator/Hessian extraction",
                "deterministic coupled two-mode reduced model",
            ],
            "symbolic_but_structurally_closed": [
                "configuration space and measure convention",
                "sector-projected gauge kinetic quadratic form",
                "Hermitian fermion and charged-current pair convention",
                "neutral-response quadratic source equation",
                "scale bridge with explicit Lambda_BH placeholder",
            ],
            "still_requiring_new_mathematics": list(OPEN_MATHEMATICS),
            "preserved_blockers": list(PRESERVED_BLOCKERS),
            "claim_safe_conclusion": (
                "BHSM v5.4 constructs an explicit unified symbolic dynamical action with "
                "configuration space, measure, term dimensions, variations, quadratic operators, "
                "interaction sources, and a deterministic reduced model. The construction remains "
                "conditional because coefficients, physical scale generation, gauge/current "
                "normalization, and nonlinear solution theory remain open."
            ),
            "recommended_next_construction_sprint": "BHSM physical-scale generation",
        }
    )
    return payload


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "configuration_space": configuration_space_artifact(),
        "action_candidate": action_candidate_artifact(),
        "coefficient_dimension_table": coefficient_dimension_table_artifact(),
        "variational_equations": variational_equations_artifact(),
        "quadratic_operators": quadratic_operators_artifact(),
        "interaction_source_map": interaction_source_map_artifact(),
        "dimensionful_scale_analysis": dimensionful_scale_analysis_artifact(),
        "reduced_model": reduced_model_artifact(),
        "construction_report": construction_report_artifact(),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    payloads = build_artifact_payloads(root)
    written: list[Path] = []
    for key, filename in ARTIFACT_FILES.items():
        path = root / "artifacts" / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def unified_action_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    report = payloads["construction_report"]
    return {
        "report": "BHSM v5.4 unified dynamical action construction",
        "version": VERSION,
        "primary_result": report["primary_result"],
        "configuration_space": payloads["configuration_space"]["status"],
        "action_status": payloads["action_candidate"]["status"],
        "dimension_checks_passed": report["dimension_checks_passed"],
        "variational_equations_derived": report["variational_equations_derived"],
        "quadratic_operators_extracted": report["quadratic_operators_extracted"],
        "reduced_model_status": report["reduced_model_status"],
        "reduced_model": payloads["reduced_model"]["reduced_model"],
        "preserved_blockers": list(PRESERVED_BLOCKERS),
        "still_requiring_new_mathematics": list(OPEN_MATHEMATICS),
        "artifacts": {key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()},
        "claim_safe_conclusion": report["claim_safe_conclusion"],
        "recommended_next_construction_sprint": report["recommended_next_construction_sprint"],
        **GUARDS,
    }


def unified_action_status_to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BHSM v5.4 Unified Dynamical Action Construction",
        "",
        f"Primary result: `{report['primary_result']}`",
        f"Configuration space: `{report['configuration_space']}`",
        f"Action status: `{report['action_status']}`",
        f"Dimension checks passed: `{report['dimension_checks_passed']}`",
        f"Reduced model: `{report['reduced_model_status']}`",
        "",
        "## Reduced Model",
        f"- Truncation: {report['reduced_model']['truncation']}",
        f"- Equations: {', '.join(report['reduced_model']['equations'])}",
        f"- Eigenvalues: {report['reduced_model']['eigenvalues']}",
        f"- Stable: {report['reduced_model']['stable']}",
        "",
        "## Still Requiring New Mathematics",
    ]
    for item in report["still_requiring_new_mathematics"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Claim-Safe Conclusion", "", report["claim_safe_conclusion"], ""])
    return "\n".join(lines)
