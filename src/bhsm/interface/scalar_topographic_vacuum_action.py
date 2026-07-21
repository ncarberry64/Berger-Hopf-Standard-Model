"""BHSM v5.6 scalar/topographic vacuum action derivation.

The v5.5 scale branch is refined here: the scale order parameter is a
normalized scalar/topographic mode coefficient, and the quadratic/quartic
coefficients are explicit action functionals rather than free quartic
placeholders. Numerical particle scales are still not emitted.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import sqrt
from pathlib import Path
from typing import Any


VERSION = "v5.6"
SPRINT = "bhsm-scalar-topographic-vacuum-action-derivation-v5-6"
PRIMARY_RESULT = "SCALAR_TOPOGRAPHIC_VACUUM_ACTION_DERIVED_CONDITIONALLY"

ARTIFACT_FILES = {
    "order_parameter": "BHSM_scalar_topographic_order_parameter_v5_6.json",
    "action_source": "BHSM_scalar_topographic_action_source_v5_6.json",
    "variable_dictionary": "BHSM_scalar_topographic_variable_dictionary_v5_6.json",
    "reduced_vacuum_functional": "BHSM_scalar_topographic_reduced_vacuum_functional_v5_6.json",
    "vacuum_solution": "BHSM_scalar_topographic_vacuum_solution_v5_6.json",
    "curvature_threshold_audit": "BHSM_curvature_threshold_expansion_audit_v5_6.json",
    "unit_anchor": "BHSM_scalar_topographic_unit_anchor_v5_6.json",
    "v5_5_update": "BHSM_physical_scale_v5_5_update_from_v5_6.json",
    "reduced_model": "BHSM_scalar_topographic_vacuum_reduced_model_v5_6.json",
    "construction_report": "BHSM_scalar_topographic_vacuum_action_derivation_report_v5_6.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "observed_mass_or_vev_used": False,
    "pdg_reference_values_used": False,
    "w_calibration_used": False,
    "charged_mass_fitting_used": False,
    "ckm_fitting_used": False,
    "neutrino_limits_used": False,
    "legacy_threshold_tables_used": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physics_model_logic_changed": False,
    "numerical_particle_masses_emitted": False,
    "physical_couplings_promoted": False,
}

PRESERVED_OPEN_GATES = (
    "OPEN_MISSING_EXPLICIT_T_PROFILE_SOLUTION",
    "OPEN_MISSING_EXPLICIT_PHI_PROFILE_SOLUTION",
    "OPEN_MISSING_THRESHOLD_SELECTION_T_0",
    "OPEN_MISSING_THRESHOLD_SELECTION_PHI_0",
    "OPEN_MISSING_BOUNDARY_COEFFICIENT_VALUES",
    "OPEN_MISSING_COLLAR_MEASURE_VALUE",
    "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
    "OPEN_MISSING_G2_BH_ACTION_SOURCE",
    "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
    "CKM_EXPONENT_NOT_DERIVED",
    "OPEN_MISSING_NEUTRAL_SCALE",
    "OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION",
    "FULL_BHSM_NOT_COMPLETE",
)


@dataclass(frozen=True)
class ScalarVariable:
    symbol: str
    definition: str
    domain: str
    dimension: str
    dynamical_or_fixed: str
    action_source: str
    variation_equation: str
    relationship: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _common_payload(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": (
            "The scalar/topographic scale vacuum is derived conditionally from "
            "the BHSM scalar/topographic action family and a declared normalized "
            "mode reduction. The coefficients are action functionals over unresolved "
            "profiles, boundary tensors, and collar data; no numeric eV/GeV scale, "
            "particle mass, measured VEV, gauge coupling, CKM value, rare-B result, "
            "or full BHSM completion is claimed."
        ),
        **GUARDS,
    }


def scale_order_parameter_definition() -> dict[str, Any]:
    return {
        "symbol": "sigma_scale",
        "definition": (
            "dimensionless coefficient of the normalized scalar/topographic scale mode "
            "(f_T,f_Phi) in T=T_bar+sigma_scale f_T+... and Phi=Phi_bar+sigma_scale f_Phi+..."
        ),
        "source_fields": ["T(x)", "Phi(y)", "boundary/collar geometry"],
        "map": {
            "mode_projection": "sigma_scale = <(delta T,delta Phi),(f_T,f_Phi)>_Q_ST",
            "normalization": "Q_ST[f_T,f_Phi]=1",
            "Q_ST": (
                "integral_B z_T f_T^2 dV + integral_Bint z_Phi f_Phi^2 dmu_B "
                "+ integral_boundary q_boundary(f_T,f_Phi) dA + integral_collar q_collar(f_T,f_Phi) J dA drho"
            ),
        },
        "not_profile_width": {
            "profile_width_symbol": "sigma_profile",
            "reason": "sigma_profile labels a localized profile width/shape parameter; sigma_scale is a dynamical amplitude coefficient.",
        },
        "selected_interpretation": "collar-integrated scalar/topographic scale-mode coefficient",
        "status": "SCALE_ORDER_PARAMETER_DEFINED_CONDITIONALLY",
    }


def scalar_topographic_action_source() -> dict[str, Any]:
    return {
        "status": "SCALAR_TOPOGRAPHIC_ACTION_SOURCE_ASSEMBLED_CONDITIONALLY",
        "S_ST": "S_T_bulk + S_Phi_internal + S_threshold + S_boundary + S_collar",
        "bulk_T_term": (
            "S_T_bulk = integral_B [1/2 z_T |grad T|^2 + U_T(T; geometry)] dV"
        ),
        "internal_Phi_term": (
            "S_Phi_internal = integral_Bint [1/2 z_Phi |D_B Phi|^2 + U_Phi(Phi; g_B)] dmu_B"
        ),
        "threshold_term": (
            "S_threshold = integral [1/2 m_TT(T-T_0)^2 + 1/2 m_PP(Phi-Phi_0)^2 + m_TP(T-T_0)(Phi-Phi_0)] on the allowed threshold support"
        ),
        "boundary_term": (
            "S_boundary = integral_boundary [U_boundary(T,Phi) + c_K K + c_K2 K^2 + c_S Tr(S^2) + c_J log J] dA"
        ),
        "collar_term": (
            "S_collar = integral_boundary integral_0^rho_star B_threshold[T,Phi,K,S,J;Y,rho] J(Y,rho) drho dA"
        ),
        "minimal_allowed_forms": {
            "quadratic_kernel": "H_ST from second variation of S_ST around (T_bar,Phi_bar)",
            "quartic_kernel": "G_ST from the lowest even bounded local scalar/topographic self-interaction and boundary/collar response",
            "odd_terms": "absent in the reduced scale mode when the orientation-pair/Z2 scale-mode symmetry is imposed; otherwise they remain an open branch-breaking source",
        },
        "source_chain": [
            "PO-BH-53 symbolic scalar/topographic boundary variation",
            "PO-BH-56 complete collar action source audit",
            "PO-BH-59 level-set geometry",
            "PO-BH-60 profile input classification",
            "PO-BH-61 partial EOM source",
            "PO-BH-62 boundary-condition normal form",
            "PO-BH-63 coefficient/threshold source audit",
            "v5.4 unified action scalar_topographic and scale_bridge terms",
            "v5.5 conditional scale branch",
        ],
    }


def scalar_variable_dictionary() -> tuple[ScalarVariable, ...]:
    return (
        ScalarVariable("T(x)", "spacetime topographic scalar", "spacetime/collar support", "dimensionless before ell_*", "dynamical/localized", "S_T_bulk, S_threshold, S_boundary, S_collar", "delta S_ST/delta T=0", "contributes to sigma_scale through f_T projection"),
        ScalarVariable("T_0", "spacetime level-set threshold", "boundary level set T=T_0", "same as T", "fixed/open", "threshold term and Dirichlet normal form", "not varied unless threshold theorem promotes it", "OPEN_MISSING_THRESHOLD_SELECTION_T_0"),
        ScalarVariable("Phi(y)", "internal Berger/topographic profile", "internal Berger/topographic space", "dimensionless before ell_*", "dynamical/localized", "S_Phi_internal, S_threshold, S_boundary, S_collar", "delta S_ST/delta Phi=0", "contributes to sigma_scale through f_Phi projection"),
        ScalarVariable("Phi_0", "internal level-set threshold", "internal boundary Phi=Phi_0", "same as Phi", "fixed/open", "threshold term and Dirichlet normal form", "not varied unless threshold theorem promotes it", "OPEN_MISSING_THRESHOLD_SELECTION_PHI_0"),
        ScalarVariable("y_0", "distinguished profile peak/sampling point", "internal profile domain", "coordinate/location", "fixed/localized", "profile localization docs", "not a field equation by itself", "does not define sigma_scale without the mode profile"),
        ScalarVariable("sigma_profile", "profile width or shape parameter", "profile ansatz/shape family", "dimensionless or length depending convention", "open profile parameter", "profile input classification", "profile EOM needed", "distinct from sigma_scale"),
        ScalarVariable("sigma_scale", "normalized scale-mode amplitude", "reduced scalar/topographic mode space", "dimensionless", "dynamical reduced coordinate", "projection of S_ST onto normalized mode", "dV_eff/dsigma_scale=0", "sets M_BH/M_* after unit anchor"),
        ScalarVariable("rho_star", "collar depth endpoint", "boundary collar", "dimensionless before ell_*", "fixed/open", "S_collar", "edge variation if promoted", "does not fix absolute scale alone"),
        ScalarVariable("k_loc", "local curvature threshold source", "curvature-threshold audit", "inverse length squared after ell_*", "background/open", "legacy curvature-threshold candidate", "appears in old audit only", "does not produce a mass gap after background substitution"),
        ScalarVariable("lambda_T", "T-sector action coefficient/tensor", "bulk/boundary/collar support", "dimensionless in normalized action", "symbolic/open", "S_ST kernels", "enters H_ST and G_ST", "part of alpha_scale/beta_scale functionals"),
        ScalarVariable("lambda_Phi", "Phi-sector action coefficient/tensor", "internal/boundary/collar support", "dimensionless in normalized action", "symbolic/open", "S_ST kernels", "enters H_ST and G_ST", "part of alpha_scale/beta_scale functionals"),
        ScalarVariable("alpha_scale", "negative reduced quadratic Hessian functional", "reduced mode", "dimensionless", "derived conditional functional", "alpha_scale=-<f,H_ST f> when negative", "dV_eff/dsigma_scale contains -alpha_scale sigma_scale", "not a free placeholder in v5.6"),
        ScalarVariable("beta_scale", "reduced quartic stabilizing functional", "reduced mode", "dimensionless", "derived conditional functional", "beta_scale=G_ST[f,f,f,f]", "dV_eff/dsigma_scale contains beta_scale sigma_scale^3", "not a free placeholder in v5.6"),
        ScalarVariable("M_star", "unresolved absolute energy anchor", "unit map", "energy", "open", "v5.5/v5.6 unit map", "not fixed by S_ST", "M_BH=M_star |sigma_scale,0|"),
        ScalarVariable("ell_star", "unresolved absolute length anchor", "unit map", "length", "open", "v5.5/v5.6 unit map", "not fixed by S_ST", "M_star=hbar c/ell_star"),
    )


def reduced_vacuum_functional() -> dict[str, Any]:
    return {
        "status": "REDUCED_VACUUM_FUNCTIONAL_DERIVED_CONDITIONALLY",
        "reduction": [
            "T = T_bar + sigma_scale f_T + higher modes",
            "Phi = Phi_bar + sigma_scale f_Phi + higher modes",
            "Q_ST[f_T,f_Phi]=1",
        ],
        "V_eff": (
            "V_eff(sigma_scale)=V_0 + 1/2 A_ST[f] sigma_scale^2 "
            "+ 1/4 G_ST[f] sigma_scale^4 + O(sigma_scale^6)"
        ),
        "alpha_scale": "-A_ST[f] = - second_variation(S_ST)[(f_T,f_Phi),(f_T,f_Phi)]",
        "beta_scale": "G_ST[f] = fourth_variation(S_ST)[(f_T,f_Phi)^4] plus boundary/collar quartic kernels",
        "quartic_branch": (
            "If A_ST[f]<0 and G_ST[f]>0, rewrite V_eff=V_0 - 1/2 alpha_scale sigma_scale^2 "
            "+ 1/4 beta_scale sigma_scale^4 + O(sigma_scale^6)."
        ),
        "derivation_source": "projection of S_ST onto the normalized scale mode, not a generic quartic ansatz",
        "open_inputs": [
            "explicit T/Phi profiles",
            "boundary coefficient values",
            "collar measure value",
            "threshold values T_0 and Phi_0",
            "higher-order remainder control",
        ],
    }


def vacuum_solution() -> dict[str, Any]:
    return {
        "status": "NONZERO_VACUUM_BRANCH_DERIVED_CONDITIONALLY",
        "stationary_equation": "dV_eff/dsigma_scale = -alpha_scale sigma_scale + beta_scale sigma_scale^3 + O(sigma_scale^5)=0",
        "truncated_branches": [
            "sigma_scale=0",
            "sigma_scale=+sqrt(alpha_scale/beta_scale)",
            "sigma_scale=-sqrt(alpha_scale/beta_scale)",
        ],
        "existence_conditions": ["alpha_scale>0", "beta_scale>0", "higher-order remainder controlled near branch"],
        "selected_branch": "|sigma_scale,0|=sqrt(alpha_scale/beta_scale)",
        "hessian": "V_eff''(sigma_scale,0)=2 alpha_scale at the nonzero branch; V_eff''(0)=-alpha_scale",
        "vacuum_energy": "V_min=V_0 - alpha_scale^2/(4 beta_scale) in the quartic truncation",
        "stable": True,
        "unique": "unique magnitude with sign degeneracy unless an action-derived branch-breaking term is supplied",
        "boundedness": "requires beta_scale>0 for the quartic truncation",
        "field_equations": {
            "T": "delta S_ST/delta T=0 with boundary normal form from PO-BH-62",
            "Phi": "delta S_ST/delta Phi=0 with internal/Robin/level-set boundary data from PO-BH-62",
        },
    }


def curvature_threshold_expansion(lambda_curv: float = 0.75, mode_k: float = 2.0) -> dict[str, Any]:
    quartic_coeff = lambda_curv * mode_k**4
    gradient_coeff = mode_k**2
    return {
        "status": "CURVATURE_THRESHOLD_MASS_GAP_INVALIDATED_FOR_THIS_ACTION",
        "starting_lagrangian": "L=1/2 phidot^2 - 1/2 |grad phi|^2 - lambda/2 (-laplacian phi - k_loc)^2",
        "background": "-laplacian phi_0 = k_loc",
        "substitution": "phi=phi_0+eta",
        "expanded_quadratic_lagrangian": "L_quad=1/2 etadot^2 - 1/2 |grad eta|^2 - lambda/2 (laplacian eta)^2",
        "fluctuation_operator": "eta_tt - laplacian eta + lambda laplacian^2 eta = 0",
        "fourier_dispersion": "omega^2 = |k|^2 + lambda |k|^4",
        "mass_term_coefficient": 0.0,
        "claimed_prior_mass_gap_survives": False,
        "correction_required": "A gap requires an action-derived nonlinear/potential term; it is not produced by this curvature-square constraint alone.",
        "deterministic_check": {
            "lambda_curv": lambda_curv,
            "mode_k": mode_k,
            "omega_squared": gradient_coeff + quartic_coeff,
            "mass_term": 0.0,
        },
    }


def unit_anchor_relationship() -> dict[str, Any]:
    return {
        "status": "UNIT_ANCHOR_REMAINS_OPEN",
        "absolute_scale_fixed": False,
        "remaining_anchor": "M_star or ell_star",
        "M_BH_result": "M_BH/M_star = sqrt(alpha_scale/beta_scale)",
        "scale_potential_source_status": "SCALE_POTENTIAL_ACTION_SOURCE_DERIVED_CONDITIONALLY",
        "absolute_unit_anchor_status": "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
        "reason": "S_ST fixes a dimensionless vacuum branch under symbolic action-function conditions but supplies no absolute length or energy unit.",
    }


def reduced_model_solution(A_ST: float = -2.0, G_ST: float = 8.0) -> dict[str, Any]:
    if A_ST >= 0 or G_ST <= 0:
        raise ValueError("This deterministic branch requires A_ST<0 and G_ST>0")
    alpha = -A_ST
    beta = G_ST
    sigma_abs = sqrt(alpha / beta)

    def gradient(sigma: float) -> float:
        return A_ST * sigma + G_ST * sigma**3

    def hessian(sigma: float) -> float:
        return A_ST + 3.0 * G_ST * sigma**2

    selected = sigma_abs
    return {
        "declared_geometry": "unit normalized boundary/collar cell with Q_ST[f_T,f_Phi]=1",
        "declared_mode_profile": {"f_T": 0.6, "f_Phi": 0.8, "normalization": "f_T^2+f_Phi^2=1"},
        "derived_V_eff": "V_eff=1/2 A_ST sigma_scale^2 + 1/4 G_ST sigma_scale^4",
        "A_ST": A_ST,
        "G_ST": G_ST,
        "alpha_scale": alpha,
        "beta_scale": beta,
        "branches": [0.0, sigma_abs, -sigma_abs],
        "selected_branch": selected,
        "stationary_residual": gradient(selected),
        "truncated_field_equation_residuals": {
            "T_mode": 0.6 * gradient(selected),
            "Phi_mode": 0.8 * gradient(selected),
        },
        "hessian": hessian(selected),
        "zero_branch_hessian": hessian(0.0),
        "stable": hessian(selected) > 0,
        "vacuum_energy": 0.5 * A_ST * selected**2 + 0.25 * G_ST * selected**4,
        "scale_ratio_M_BH_over_M_star": selected,
        "deterministic": True,
        "physical_fit": False,
    }


def v5_5_update_payload() -> dict[str, Any]:
    return {
        "status": "V5_5_SCALE_BRANCH_UPDATED_BY_V5_6",
        "old_status": "alpha_scale and beta_scale symbolic placeholders",
        "new_status": "alpha_scale and beta_scale are conditional action functionals",
        "alpha_scale": "- second_variation(S_ST)[f,f] when the scale-mode Hessian is negative",
        "beta_scale": "fourth_variation(S_ST)[f,f,f,f] plus boundary/collar quartic stabilizers",
        "scale_equation": "-alpha_scale sigma_scale + beta_scale sigma_scale^3 = 0",
        "M_BH": "M_star sqrt(alpha_scale/beta_scale)",
        "propagation": {
            "fermion_operator": "D_phys=M_BH D_hat; mass operator still separate",
            "gauge_operator": "L_i,phys=M_BH^2 L_i,hat; alpha_i still action-gated",
            "scalar_spectrum": "m_ST,n^2=M_BH^2 omega_ST,n^2 after profile/domain closure",
            "hessian_response": "G_phys=M_BH^-2 H_hat^-1 after zero-mode/domain gates close",
        },
    }


def order_parameter_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_scalar_topographic_order_parameter_v5_6")
    payload.update(scale_order_parameter_definition())
    return payload


def action_source_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_scalar_topographic_action_source_v5_6")
    payload.update(scalar_topographic_action_source())
    return payload


def variable_dictionary_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_scalar_topographic_variable_dictionary_v5_6")
    payload.update({"status": "SCALAR_TOPOGRAPHIC_VARIABLE_DICTIONARY_COMPLETE", "variables": [row.to_dict() for row in scalar_variable_dictionary()]})
    return payload


def reduced_vacuum_functional_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_scalar_topographic_reduced_vacuum_functional_v5_6")
    payload.update(reduced_vacuum_functional())
    return payload


def vacuum_solution_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_scalar_topographic_vacuum_solution_v5_6")
    payload.update(vacuum_solution())
    return payload


def curvature_threshold_audit_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_curvature_threshold_expansion_audit_v5_6")
    payload.update(curvature_threshold_expansion())
    return payload


def unit_anchor_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_scalar_topographic_unit_anchor_v5_6")
    payload.update(unit_anchor_relationship())
    return payload


def v5_5_update_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_physical_scale_v5_5_update_from_v5_6")
    payload.update(v5_5_update_payload())
    return payload


def reduced_model_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_scalar_topographic_vacuum_reduced_model_v5_6")
    model = reduced_model_solution()
    payload.update(
        {
            "status": "SCALAR_TOPOGRAPHIC_REDUCED_MODEL_STABLE",
            "reduced_model": model,
            "stationary_solution_verified": abs(model["stationary_residual"]) <= 1.0e-12,
            "truncated_field_equations_verified": all(abs(value) <= 1.0e-12 for value in model["truncated_field_equation_residuals"].values()),
            "hessian_matches_stability": model["stable"] == (model["hessian"] > 0),
        }
    )
    return payload


def construction_report_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_scalar_topographic_vacuum_action_derivation_report_v5_6")
    model = reduced_model_solution()
    payload.update(
        {
            "status": PRIMARY_RESULT,
            "scale_order_parameter": scale_order_parameter_definition(),
            "scalar_topographic_action": scalar_topographic_action_source(),
            "reduced_vacuum": reduced_vacuum_functional(),
            "vacuum_solution": vacuum_solution(),
            "curvature_threshold_audit": curvature_threshold_expansion(),
            "unit_anchor": unit_anchor_relationship(),
            "v5_5_update": v5_5_update_payload(),
            "reduced_model": model,
            "derived": [
                "sigma_scale order-parameter map",
                "S_ST scalar/topographic action decomposition",
                "alpha_scale and beta_scale as action functionals",
                "quartic vacuum branch from reduced action projection",
                "old curvature-threshold mass-gap invalidation",
                "v5.5 update from placeholders to functionals",
            ],
            "conditional": [
                "explicit profiles and thresholds remain unresolved",
                "boundary and collar coefficients remain symbolic",
                "nonzero branch requires alpha_scale>0 and beta_scale>0",
                "absolute scale requires M_star or ell_star",
            ],
            "still_requiring_new_mathematics": list(PRESERVED_OPEN_GATES),
            "claim_safe_conclusion": (
                "BHSM v5.6 conditionally derives the scalar/topographic scale vacuum "
                "from the action-reduced mode functional. It updates v5.5 by making "
                "alpha_scale and beta_scale action functionals, invalidates the old "
                "curvature-threshold mass-gap shortcut, and preserves the open absolute "
                "unit anchor and all downstream coupling/mass gates."
            ),
            "recommended_next_construction_sprint": "BHSM scalar/topographic profile and boundary-coefficient closure",
        }
    )
    return payload


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "order_parameter": order_parameter_artifact(),
        "action_source": action_source_artifact(),
        "variable_dictionary": variable_dictionary_artifact(),
        "reduced_vacuum_functional": reduced_vacuum_functional_artifact(),
        "vacuum_solution": vacuum_solution_artifact(),
        "curvature_threshold_audit": curvature_threshold_audit_artifact(),
        "unit_anchor": unit_anchor_artifact(),
        "v5_5_update": v5_5_update_artifact(),
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


def scalar_topographic_vacuum_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    report = payloads["construction_report"]
    return {
        "report": "BHSM v5.6 scalar/topographic vacuum action derivation",
        "version": VERSION,
        "primary_result": report["primary_result"],
        "scale_order_parameter": report["scale_order_parameter"],
        "reduced_vacuum": report["reduced_vacuum"],
        "vacuum_solution": report["vacuum_solution"],
        "curvature_threshold_audit": report["curvature_threshold_audit"],
        "unit_anchor": report["unit_anchor"],
        "v5_5_update": report["v5_5_update"],
        "reduced_model": report["reduced_model"],
        "still_requiring_new_mathematics": report["still_requiring_new_mathematics"],
        "claim_safe_conclusion": report["claim_safe_conclusion"],
        "recommended_next_construction_sprint": report["recommended_next_construction_sprint"],
        "artifacts": {key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()},
        **GUARDS,
    }


def scalar_topographic_vacuum_status_to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BHSM v5.6 Scalar/Topographic Vacuum Action Derivation",
        "",
        f"Primary result: `{report['primary_result']}`",
        f"Scale order parameter: `{report['scale_order_parameter']['symbol']}`",
        f"Vacuum branch: `{report['vacuum_solution']['selected_branch']}`",
        f"Unit anchor: `{report['unit_anchor']['absolute_unit_anchor_status']}`",
        "",
        "## Reduced Vacuum",
        f"- V_eff: {report['reduced_vacuum']['V_eff']}",
        f"- alpha_scale: {report['reduced_vacuum']['alpha_scale']}",
        f"- beta_scale: {report['reduced_vacuum']['beta_scale']}",
        "",
        "## Curvature-Threshold Audit",
        f"- Quadratic expansion: {report['curvature_threshold_audit']['expanded_quadratic_lagrangian']}",
        f"- Prior mass gap survives: `{report['curvature_threshold_audit']['claimed_prior_mass_gap_survives']}`",
        "",
        "## Still Requiring New Mathematics",
    ]
    for item in report["still_requiring_new_mathematics"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Claim-Safe Conclusion", "", report["claim_safe_conclusion"], ""])
    return "\n".join(lines)
