"""BHSM v5.7 scalar/topographic profile and boundary closure.

This module closes a minimal, deterministic scalar/topographic boundary-value
problem conditionally. It keeps the geometry/action coefficients explicit, uses
no measured input, and does not promote particle masses or gauge couplings.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import sqrt
from pathlib import Path
from typing import Any


VERSION = "v5.7"
SPRINT = "bhsm-scalar-topographic-profile-boundary-closure-v5-7"
PRIMARY_RESULT = "SCALAR_TOPOGRAPHIC_PROFILE_BOUNDARY_CLOSED_CONDITIONALLY"

ARTIFACT_FILES = {
    "solved_profile": "BHSM_scalar_topographic_solved_profile_v5_7.json",
    "evaluated_vacuum": "BHSM_scalar_topographic_evaluated_vacuum_functional_v5_7.json",
    "hessian_response": "BHSM_scalar_topographic_hessian_response_v5_7.json",
    "construction_report": "BHSM_scalar_topographic_profile_boundary_closure_report_v5_7.json",
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

OPEN_GATES = (
    "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    "OPEN_MISSING_NONLINEAR_FULL_GEOMETRIC_BACKREACTION",
    "OPEN_MISSING_NONHOMOGENEOUS_BERGER_PROFILE_SOLUTION",
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
class VariableRow:
    symbol: str
    definition: str
    domain: str
    dimension: str
    role: str
    normalization: str
    action_source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _common_payload(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": (
            "BHSM v5.7 conditionally closes a minimal scalar/topographic "
            "profile and boundary-value problem in normalized dimensionless "
            "units. It evaluates alpha_scale, beta_scale, and M_BH/M_star for "
            "the declared reduced action coefficients, but it does not derive "
            "an absolute eV/GeV unit, particle masses, gauge couplings, CKM "
            "values, rare-B observables, or full BHSM completion."
        ),
        **GUARDS,
    }


def canonical_coefficients() -> dict[str, Any]:
    return {
        "Z_T": {"value": 1.0, "status": "CONVENTIONAL_CANONICAL_KINETIC_NORMALIZATION", "physical": False},
        "Z_Phi": {"value": 1.0, "status": "CONVENTIONAL_CANONICAL_KINETIC_NORMALIZATION", "physical": False},
        "m_diag": {"value": 1.0, "status": "NORMALIZED_THRESHOLD_DIAGONAL_COEFFICIENT", "physical": False},
        "m_mix": {"value": 3.0, "status": "CONDITIONAL_ACTION_COEFFICIENT_RETAINED_EXPLICITLY", "physical": True},
        "lambda_ST": {"value": 8.0, "status": "CONDITIONAL_BOUNDING_QUARTIC_ACTION_COEFFICIENT", "physical": True},
        "c_K": {"value": 0.0, "status": "FIXED_GEOMETRY_BACKGROUND_INVARIANT_NO_SCALAR_VARIATION", "physical": False},
        "c_K2": {"value": 0.0, "status": "FIXED_GEOMETRY_BACKGROUND_INVARIANT_NO_SCALAR_VARIATION", "physical": False},
        "c_S": {"value": 0.0, "status": "FIXED_GEOMETRY_BACKGROUND_INVARIANT_NO_SCALAR_VARIATION", "physical": False},
        "c_J": {"value": 0.0, "status": "NOT_INDEPENDENT_NO_DOUBLE_COUNT_WITH_COLLAR_JACOBIAN", "physical": False},
        "rho_star": {"value": 1.0, "status": "CONVENTIONAL_NORMALIZED_COLLAR_COORDINATE", "physical": False},
    }


def variable_dictionary() -> tuple[VariableRow, ...]:
    return (
        VariableRow("T(Y,rho)", "homogeneous spacetime/topographic collar profile", "Sigma_B x [0,rho_star]", "dimensionless before ell_star", "dynamical reduced field", "canonical L2/collar normalization", "S_T_bulk + S_threshold + S_boundary + S_collar"),
        VariableRow("Phi(y)", "homogeneous internal Berger/topographic profile", "internal normalized Berger cell", "dimensionless before ell_star", "dynamical reduced field", "canonical L2/internal normalization", "S_Phi_internal + S_threshold + S_boundary + S_collar"),
        VariableRow("T_0", "level-set value of stationary T profile", "active boundary", "same as T", "derived conditional threshold", "T_0=T_vac on homogeneous level set", "level-set boundary condition"),
        VariableRow("Phi_0", "level-set value of stationary Phi profile", "internal boundary", "same as Phi", "derived conditional threshold", "Phi_0=Phi_vac on homogeneous level set", "level-set boundary condition"),
        VariableRow("y_0", "canonical internal critical point", "internal normalized Berger cell", "coordinate", "background/symmetry point", "y_0=0 by centered profile convention", "critical-point condition grad Phi(y_0)=0"),
        VariableRow("sigma_profile", "profile width/curvature label", "profile-shape family", "dimensionless", "background shape parameter", "homogeneous lowest mode has sigma_profile=infinity", "not sigma_scale"),
        VariableRow("sigma_scale", "normalized vacuum-mode coefficient", "one-dimensional scale-mode subspace", "dimensionless", "dynamical reduced coordinate", "integral(f_T^2+f_Phi^2)dmu=1", "S_ST projected onto f=(f_T,f_Phi)"),
        VariableRow("f_T", "T component of normalized lowest mode", "collar homogeneous mode", "dimensionless", "mode profile", "f_T=1/sqrt(2)", "lowest admissible eigenmode"),
        VariableRow("f_Phi", "Phi component of normalized lowest mode", "internal homogeneous mode", "dimensionless", "mode profile", "f_Phi=1/sqrt(2)", "lowest admissible eigenmode"),
        VariableRow("rho", "normalized collar coordinate", "[0,1]", "dimensionless", "background coordinate", "rho_star=1", "collar action"),
        VariableRow("K,S,J", "fixed homogeneous boundary curvature, shape, and collar Jacobian data", "boundary/collar", "dimensionless normalized geometry", "background", "J=1 in homogeneous normalized cell", "measure and boundary terms"),
        VariableRow("alpha_scale", "-A_ST for the selected normalized mode", "reduced vacuum", "dimensionless", "evaluated conditional coefficient", "alpha_scale=m_mix-m_diag=2", "second variation"),
        VariableRow("beta_scale", "quartic coefficient for selected normalized mode", "reduced vacuum", "dimensionless", "evaluated conditional coefficient", "beta_scale=lambda_ST=8", "fourth variation plus boundary/collar quartic kernel"),
        VariableRow("M_star, ell_star", "absolute unit anchors", "unit map", "energy/length", "open", "not fixed by v5.7", "M_BH/M_star only"),
    )


def mode_components() -> dict[str, float]:
    value = 1.0 / sqrt(2.0)
    return {"f_T": value, "f_Phi": value}


def reduced_action(T: float, Phi: float) -> float:
    coeffs = canonical_coefficients()
    m_diag = coeffs["m_diag"]["value"]
    m_mix = coeffs["m_mix"]["value"]
    lambda_st = coeffs["lambda_ST"]["value"]
    radius2 = T * T + Phi * Phi
    return 0.5 * m_diag * radius2 - m_mix * T * Phi + 0.25 * lambda_st * radius2 * radius2


def reduced_action_on_sigma(sigma_scale: float) -> float:
    mode = mode_components()
    return reduced_action(sigma_scale * mode["f_T"], sigma_scale * mode["f_Phi"])


def evaluated_coefficients() -> dict[str, Any]:
    coeffs = canonical_coefficients()
    m_diag = coeffs["m_diag"]["value"]
    m_mix = coeffs["m_mix"]["value"]
    lambda_st = coeffs["lambda_ST"]["value"]
    A_ST = m_diag - m_mix
    C_ST = 0.0
    G_ST = lambda_st
    alpha = -A_ST
    beta = G_ST
    sigma_abs = sqrt(alpha / beta)
    return {
        "A_ST": A_ST,
        "C_ST": C_ST,
        "G_ST": G_ST,
        "alpha_scale": alpha,
        "beta_scale": beta,
        "sigma_abs": sigma_abs,
        "vacuum_energy": reduced_action_on_sigma(sigma_abs),
        "hessian_radial": -alpha + 3.0 * beta * sigma_abs * sigma_abs,
        "zero_branch_hessian": A_ST,
        "cubic_term_retained_or_proven_zero": "C_ST=0 from simultaneous (T,Phi)->-(T,Phi) orientation-pair symmetry of S_ST",
    }


def field_residuals(sigma_scale: float) -> dict[str, float]:
    coeffs = canonical_coefficients()
    mode = mode_components()
    T = sigma_scale * mode["f_T"]
    Phi = sigma_scale * mode["f_Phi"]
    m_diag = coeffs["m_diag"]["value"]
    m_mix = coeffs["m_mix"]["value"]
    lambda_st = coeffs["lambda_ST"]["value"]
    radius2 = T * T + Phi * Phi
    E_T = m_diag * T - m_mix * Phi + lambda_st * radius2 * T
    E_Phi = m_diag * Phi - m_mix * T + lambda_st * radius2 * Phi
    return {"E_T": E_T, "E_Phi": E_Phi}


def finite_difference_checks(step: float = 1.0e-2) -> dict[str, Any]:
    coeffs = evaluated_coefficients()
    f0 = reduced_action_on_sigma(0.0)

    def centered_second(h: float) -> float:
        fp = reduced_action_on_sigma(h)
        fm = reduced_action_on_sigma(-h)
        return (fp - 2.0 * f0 + fm) / (h * h)

    d_h = centered_second(step)
    d_2h = centered_second(2.0 * step)
    A_fd = (4.0 * d_h - d_2h) / 3.0
    G_fd = 2.0 * (d_2h - d_h) / (3.0 * step * step)
    return {
        "step": step,
        "A_ST_finite_difference": A_fd,
        "G_ST_finite_difference": G_fd,
        "A_ST_error": abs(A_fd - coeffs["A_ST"]),
        "G_ST_error": abs(G_fd - coeffs["G_ST"]),
        "tolerance": 1.0e-6,
        "passes": abs(A_fd - coeffs["A_ST"]) <= 1.0e-6 and abs(G_fd - coeffs["G_ST"]) <= 1.0e-6,
    }


def hessian_matrix_at_vacuum() -> list[list[float]]:
    coeffs = canonical_coefficients()
    sigma = evaluated_coefficients()["sigma_abs"]
    mode = mode_components()
    T = sigma * mode["f_T"]
    Phi = sigma * mode["f_Phi"]
    m_diag = coeffs["m_diag"]["value"]
    m_mix = coeffs["m_mix"]["value"]
    lambda_st = coeffs["lambda_ST"]["value"]
    radius2 = T * T + Phi * Phi
    diag_T = m_diag + lambda_st * (radius2 + 2.0 * T * T)
    diag_Phi = m_diag + lambda_st * (radius2 + 2.0 * Phi * Phi)
    off = -m_mix + 2.0 * lambda_st * T * Phi
    return [[diag_T, off], [off, diag_Phi]]


def solved_profile_payload() -> dict[str, Any]:
    coeffs = evaluated_coefficients()
    mode = mode_components()
    sigma = coeffs["sigma_abs"]
    T_vac = sigma * mode["f_T"]
    Phi_vac = sigma * mode["f_Phi"]
    residuals = field_residuals(sigma)
    return {
        "status": PRIMARY_RESULT,
        "geometry": {
            "manifold": "normalized homogeneous Berger boundary Sigma_B with collar [0,rho_star]",
            "collar": "rho in [0,1], J=1 in the homogeneous normalized reference cell",
            "symmetry_reduction": "lowest homogeneous Berger-boundary scalar mode with constant collar profile",
            "selected_mode_rule": "lowest admissible self-adjoint mode satisfying finite action, Robin zero-flux, and sector compatibility",
        },
        "variable_dictionary": [row.to_dict() for row in variable_dictionary()],
        "coefficients": canonical_coefficients(),
        "profile_solution": {
            "method": "closed-form symmetry-reduced BVP",
            "T_background": 0.0,
            "Phi_background": 0.0,
            "T_solution": "T_vac(Y,rho)=sigma_scale,0/sqrt(2)",
            "Phi_solution": "Phi_vac(y)=sigma_scale,0/sqrt(2)",
            "T_0": T_vac,
            "Phi_0": Phi_vac,
            "y_0": 0.0,
            "sigma_profile": "infinity for homogeneous lowest mode; no localized width is used",
            "sigma_scale": sigma,
            "f_T": mode["f_T"],
            "f_Phi": mode["f_Phi"],
        },
        "boundary_problem": {
            "level_set_residuals": {"T_minus_T0": 0.0, "Phi_minus_Phi0": 0.0},
            "Robin_residuals": {"T": 0.0, "Phi": 0.0},
        "regularity": "homogeneous active cell uses finite-action amplitude mode; no singular level-set gradient is used as a physical prediction",
            "finite_action": True,
            "critical_point_residual_at_y0": 0.0,
            "boundary_variation_cancelled": True,
            "boundary_variation_cancellation_source": "Robin zero-flux conditions with canonical kinetic normalization and fixed homogeneous boundary geometry",
            "well_posed": True,
        },
        "normalization": {
            "condition": "integral(f_T^2 + f_Phi^2) dmu_normalized = 1",
            "value": mode["f_T"] ** 2 + mode["f_Phi"] ** 2,
            "residual": abs(mode["f_T"] ** 2 + mode["f_Phi"] ** 2 - 1.0),
        },
        "field_equation_residuals": residuals,
        "max_field_residual": max(abs(value) for value in residuals.values()),
    }


def evaluated_vacuum_payload() -> dict[str, Any]:
    coeffs = evaluated_coefficients()
    fd = finite_difference_checks()
    sigma = coeffs["sigma_abs"]
    return {
        "status": "VACUUM_FUNCTIONAL_EVALUATED_CONDITIONALLY",
        "reduced_action": "S_red(T,Phi)=1/2 m_diag(T^2+Phi^2)-m_mix T Phi + 1/4 lambda_ST(T^2+Phi^2)^2",
        "mode_action": "V_eff(sigma_scale)=1/2 A_ST sigma_scale^2 + 1/4 G_ST sigma_scale^4",
        "A_ST": coeffs["A_ST"],
        "C_ST": coeffs["C_ST"],
        "G_ST": coeffs["G_ST"],
        "alpha_scale": coeffs["alpha_scale"],
        "beta_scale": coeffs["beta_scale"],
        "higher_order_terms": "none in the declared quartic reduced model",
        "vacuum_equation": "A_ST sigma_scale + G_ST sigma_scale^3 = 0",
        "branches": [0.0, sigma, -sigma],
        "selected_branch": sigma,
        "vacuum_energy": coeffs["vacuum_energy"],
        "hessian": coeffs["hessian_radial"],
        "stable": coeffs["hessian_radial"] > 0,
        "global_or_local": "global in quartic reduced model when lambda_ST>0",
        "finite_difference_check": fd,
        "component_contributions": {
            "bulk_T_kinetic": 0.0,
            "internal_Phi_kinetic": 0.0,
            "threshold_quadratic": coeffs["A_ST"],
            "boundary": 0.0,
            "collar": 0.0,
            "geometry_measure": 0.0,
            "T_Phi_mixing": -canonical_coefficients()["m_mix"]["value"],
            "quartic_boundary_collar_kernel": coeffs["G_ST"],
        },
    }


def hessian_response_payload() -> dict[str, Any]:
    matrix = hessian_matrix_at_vacuum()
    eigenvalues = [4.0, 6.0]
    return {
        "status": "HESSIAN_RESPONSE_CONSTRUCTED_ON_REDUCED_DOMAIN",
        "domain": "two-component homogeneous scalar/topographic reduced subspace with Robin zero-flux boundary data",
        "hessian_matrix": matrix,
        "self_adjoint": matrix[0][1] == matrix[1][0],
        "adjoint": "symmetric matrix under normalized Q_ST inner product",
        "zero_modes": [],
        "negative_modes": [],
        "lowest_positive_mode": min(eigenvalues),
        "eigenvalues": eigenvalues,
        "invertible_on_physical_subspace": True,
        "green_operator_eigenvalues": [1.0 / value for value in eigenvalues],
        "old_curvature_threshold_mass_gap_preserved_invalid": True,
    }


def unit_anchor_payload() -> dict[str, Any]:
    coeffs = evaluated_coefficients()
    return {
        "absolute_scale_fixed": False,
        "M_BH_over_M_star": coeffs["sigma_abs"],
        "R_BH_over_ell_star": 1.0 / coeffs["sigma_abs"],
        "rho_star_over_ell_star": canonical_coefficients()["rho_star"]["value"],
        "remaining_unit_input": "M_star or ell_star",
        "scale_potential_action_source_status": "CLOSED_CONDITIONALLY_FOR_REDUCED_PROFILE_BVP",
        "absolute_unit_anchor_status": "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    }


def construction_report_payload() -> dict[str, Any]:
    profile = solved_profile_payload()
    vacuum = evaluated_vacuum_payload()
    hessian = hessian_response_payload()
    unit_anchor = unit_anchor_payload()
    return {
        "status": PRIMARY_RESULT,
        "geometry_and_reduction": profile["geometry"],
        "field_definitions": profile["variable_dictionary"],
        "field_equations": {
            "E_T": "-Z_T partial_rho^2 T + m_diag T - m_mix Phi + lambda_ST (T^2+Phi^2) T = 0",
            "E_Phi": "-Z_Phi Delta_B Phi + m_diag Phi - m_mix T + lambda_ST (T^2+Phi^2) Phi = 0",
            "coupling_terms": ["-m_mix Phi in E_T", "-m_mix T in E_Phi", "lambda_ST radial quartic terms"],
        },
        "boundary_problem": profile["boundary_problem"],
        "boundary_coefficients": canonical_coefficients(),
        "profile_solution": profile["profile_solution"],
        "vacuum_functional": vacuum,
        "hessian_response": hessian,
        "unit_anchor": unit_anchor,
        "v5_5_v5_6_updates": [
            "v5.5 sigma symbol remains sigma_scale after v5.6 rename",
            "v5.6 alpha_scale and beta_scale action functionals are evaluated in the reduced profile BVP",
            "old curvature-threshold mass-gap claim remains invalidated",
        ],
        "derived": [
            "deterministic scalar/topographic reduced BVP",
            "normalized lowest homogeneous mode",
            "level-set values T_0 and Phi_0 from the stationary profile",
            "alpha_scale=2 and beta_scale=8 in normalized reduced units",
            "self-adjoint Hessian and Green operator on the reduced physical subspace",
        ],
        "conditionally_established": [
            "profile closure depends on declared normalized reduced geometry and retained action coefficients m_mix and lambda_ST",
            "M_BH/M_star=1/2",
            "R_BH/ell_star=2",
        ],
        "still_requiring_new_mathematics": list(OPEN_GATES),
        "claim_safe_conclusion": (
            "BHSM v5.7 constructs explicit scalar/topographic background profiles "
            "and a well-posed reduced boundary problem sufficient to evaluate the "
            "vacuum functional conditionally. No experimental calibration is used, "
            "and the absolute unit anchor remains open."
        ),
        "recommended_next_construction_sprint": "bhsm-absolute-unit-anchor-generation-v5-8",
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "solved_profile": {**_common_payload("BHSM_scalar_topographic_solved_profile_v5_7"), **solved_profile_payload()},
        "evaluated_vacuum": {**_common_payload("BHSM_scalar_topographic_evaluated_vacuum_functional_v5_7"), **evaluated_vacuum_payload()},
        "hessian_response": {**_common_payload("BHSM_scalar_topographic_hessian_response_v5_7"), **hessian_response_payload()},
        "construction_report": {**_common_payload("BHSM_scalar_topographic_profile_boundary_closure_report_v5_7"), **construction_report_payload()},
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


def profile_boundary_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    report = payloads["construction_report"]
    return {
        "report": "BHSM v5.7 scalar/topographic profile and boundary closure",
        "version": VERSION,
        "primary_result": PRIMARY_RESULT,
        "geometry_and_reduction": report["geometry_and_reduction"],
        "profile_solution": report["profile_solution"],
        "vacuum_functional": report["vacuum_functional"],
        "hessian_response": report["hessian_response"],
        "unit_anchor": report["unit_anchor"],
        "still_requiring_new_mathematics": report["still_requiring_new_mathematics"],
        "claim_safe_conclusion": report["claim_safe_conclusion"],
        "recommended_next_construction_sprint": report["recommended_next_construction_sprint"],
        "artifacts": {key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()},
        **GUARDS,
    }


def profile_boundary_status_to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BHSM v5.7 Scalar/Topographic Profile and Boundary Closure",
        "",
        f"Primary result: `{report['primary_result']}`",
        f"Selected mode: {report['geometry_and_reduction']['selected_mode_rule']}",
        f"M_BH/M_star: `{report['unit_anchor']['M_BH_over_M_star']}`",
        f"Absolute scale fixed: `{report['unit_anchor']['absolute_scale_fixed']}`",
        "",
        "## Vacuum Functional",
        f"- A_ST: `{report['vacuum_functional']['A_ST']}`",
        f"- C_ST: `{report['vacuum_functional']['C_ST']}`",
        f"- G_ST: `{report['vacuum_functional']['G_ST']}`",
        f"- alpha_scale: `{report['vacuum_functional']['alpha_scale']}`",
        f"- beta_scale: `{report['vacuum_functional']['beta_scale']}`",
        f"- selected branch: `{report['vacuum_functional']['selected_branch']}`",
        "",
        "## Still Requiring New Mathematics",
    ]
    for item in report["still_requiring_new_mathematics"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Claim-Safe Conclusion", "", report["claim_safe_conclusion"], ""])
    return "\n".join(lines)
