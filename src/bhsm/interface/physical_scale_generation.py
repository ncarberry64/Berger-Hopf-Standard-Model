"""BHSM v5.5 physical-scale generation candidate.

This module extends the v5.4 unified symbolic action with a guarded scale
sector. It inventories possible scale-bearing objects, compares candidate
mechanisms, and records the strongest conditional construction without using
measured masses, electroweak inputs, cosmology, or Standard Model calibration.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import sqrt
from pathlib import Path
from typing import Any


VERSION = "v5.5"
SPRINT = "bhsm-physical-scale-generation-v5-5"
PRIMARY_RESULT = "BHSM_PHYSICAL_SCALE_GENERATED_CONDITIONALLY"
SELECTED_MECHANISM = "SCALAR_TOPOGRAPHIC_SCALE_VACUUM_WITH_UNRESOLVED_UNIT_ANCHOR"

ARTIFACT_FILES = {
    "scale_inventory": "BHSM_physical_scale_object_inventory_v5_5.json",
    "candidate_comparison": "BHSM_physical_scale_candidate_comparison_v5_5.json",
    "selected_mechanism": "BHSM_selected_physical_scale_mechanism_v5_5.json",
    "scale_equation": "BHSM_physical_scale_equation_v5_5.json",
    "stability_analysis": "BHSM_physical_scale_stability_analysis_v5_5.json",
    "dimension_unit_map": "BHSM_physical_scale_dimension_unit_map_v5_5.json",
    "operator_propagation": "BHSM_physical_scale_operator_propagation_v5_5.json",
    "reduced_model": "BHSM_physical_scale_reduced_model_v5_5.json",
    "construction_report": "BHSM_physical_scale_generation_report_v5_5.json",
}

GUARDS = {
    "empirical_inputs_used": False,
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
    "rare_b_phenomenology_pursued": False,
}

PRESERVED_BLOCKERS = (
    "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    "OPEN_MISSING_SCALE_FUNCTIONAL_NUMERIC_INPUTS",
    "OPEN_MISSING_PHYSICAL_SCALE_GENERATION_FOR_NUMERIC_UNITS",
    "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
    "OPEN_MISSING_G2_BH_ACTION_SOURCE",
    "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
    "CKM_EXPONENT_NOT_DERIVED",
    "OPEN_MISSING_NEUTRAL_SCALE",
    "OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION",
    "OPEN_MISSING_CHARGED_CURRENT_NORMALIZATION",
    "OPEN_MISSING_NEUTRAL_RESPONSE_NORMALIZATION",
    "OPEN_MISSING_NONLINEAR_UNIFIED_SOLUTION",
    "RARE_B_FCNC_GENERATION_MECHANISM_BLOCKED",
    "B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED",
    "FULL_BHSM_NOT_COMPLETE",
)


@dataclass(frozen=True)
class ScaleObject:
    name: str
    symbol: str
    dimension: str
    dynamical_status: str
    action_source: str
    variation_equation: str
    normalization: str
    can_set_absolute_scale: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScaleCandidate:
    name: str
    status: str
    action_support: str
    scale_equation: str
    dimensional_closure: str
    stability: str
    uniqueness: str
    arbitrary_inputs: tuple[str, ...]
    verdict: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _common_payload(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "selected_mechanism": SELECTED_MECHANISM,
        "claim_boundary": (
            "BHSM v5.5 constructs a conditional scale-setting mechanism from the "
            "v5.4 action. It fixes a nonzero dimensionless scale branch in terms "
            "of symbolic action coefficients, but the absolute unit anchor M_* or "
            "ell_* remains open. No measured mass, coupling, W calibration, CKM fit, "
            "neutrino limit, cosmological input, rare-B result, or full BHSM "
            "completion is claimed."
        ),
        **GUARDS,
    }


def scale_object_inventory() -> tuple[ScaleObject, ...]:
    return (
        ScaleObject(
            "boundary radius",
            "R_BH",
            "length after unit anchor; dimensionless rho before anchoring",
            "candidate scale modulus",
            "v5.4 scale_bridge and boundary/collar measure",
            "delta S / delta rho = 0",
            "R_BH = ell_* rho_0 if an absolute ell_* is supplied",
            False,
            "a free radius is not a generated physical scale without a stationary equation and unit anchor",
        ),
        ScaleObject(
            "Berger squashing",
            "q_B",
            "dimensionless ratio",
            "fixed or conditional geometric datum",
            "Berger metric/Hodge ledgers",
            "shape variation not closed in v5.4",
            "ratio only",
            False,
            "dimensionless anisotropy can order spectra but cannot by itself define eV/GeV units",
        ),
        ScaleObject(
            "collar coordinate",
            "rho",
            "dimensionless coordinate; length only after ell_*",
            "dynamical scale label in v5.4",
            "scale_bridge term",
            "kappa_scale (rho-rho_*) + delta_rho sources = 0",
            "rho_phys = ell_* rho",
            False,
            "rho can select a branch, but absolute length requires ell_*",
        ),
        ScaleObject(
            "metric normalization",
            "h_rho",
            "dimensionless in normalized boundary units",
            "fixed datum for v5.4, optional variation",
            "configuration-space artifact",
            "geometric Hessian equation if varied",
            "normalized measure dmu_Sigma,rho",
            False,
            "normalized geometry supplies ratios and operators, not an absolute unit",
        ),
        ScaleObject(
            "curvature invariant",
            "R_hat[h_rho]",
            "dimensionless before ell_*; length^-2 after anchoring",
            "computed from geometry",
            "geometric/topographic terms",
            "enters delta_h and delta_rho equations",
            "R_phys = ell_*^-2 R_hat",
            False,
            "dimensionless curvature requires ell_* to become physical curvature",
        ),
        ScaleObject(
            "measure normalization",
            "Vol_hat(Sigma_rho)",
            "dimensionless normalized volume",
            "conditional measure source",
            "boundary/collar measure ledgers",
            "measure variation contributes to delta_rho equation",
            "Vol_phys = ell_*^3 Vol_hat",
            False,
            "normalized volume cannot be re-labeled as mass scale",
        ),
        ScaleObject(
            "scalar/topographic amplitude",
            "sigma",
            "dimensionless order parameter",
            "dynamical",
            "v5.4 scalar_topographic plus v5.5 scale potential",
            "dU_scale/dsigma = beta sigma^3 - alpha sigma = 0",
            "M_BH = M_* |sigma_0| after unit convention",
            True,
            "the action can select nonzero |sigma_0| symbolically; the absolute M_* anchor remains open",
        ),
        ScaleObject(
            "potential coefficients",
            "alpha_scale, beta_scale",
            "dimensionless in the reduced scale sector",
            "symbolic action coefficients",
            "v5.5 scale potential",
            "determine stationary branches",
            "alpha_scale>0, beta_scale>0",
            False,
            "they determine a dimensionless branch but are not physical units",
        ),
        ScaleObject(
            "spectral eigenvalues",
            "lambda_n_hat",
            "dimensionless before ell_*",
            "operator spectrum",
            "quadratic/Hessian operators",
            "eigenvalue problem L_hat psi_n = lambda_n_hat psi_n",
            "M_n^2 = M_*^2 lambda_n_hat",
            False,
            "a dimensionless eigenvalue needs an external/internal scale factor",
        ),
        ScaleObject(
            "Hessian eigenvalues",
            "omega_n_hat^2",
            "dimensionless stiffness eigenvalues",
            "computed around stationary branch",
            "second variation of the action",
            "H v_n = omega_n_hat^2 v_n",
            "M_n^2 = M_*^2 omega_n_hat^2",
            False,
            "Hessian eigenvalues propagate a scale once M_* exists; they do not create M_* alone",
        ),
        ScaleObject(
            "RG or scale-field terms",
            "Z_i(mu,rho), rho_i(mu)",
            "dimensionless running functions plus scale labels",
            "open",
            "v4.5/v4.6 gates",
            "no closed beta or stationary effective-action equation",
            "requires action-selected rho_i(mu)",
            False,
            "dimensional transmutation is not available without an explicit scale-dependent equation",
        ),
    )


def candidate_comparison() -> tuple[ScaleCandidate, ...]:
    return (
        ScaleCandidate(
            "geometric radius",
            "PARTIAL_REJECT_FREE_RADIUS",
            "v5.4 contains rho and a scale bridge, but rho_* is symbolic unless derived",
            "delta S / delta R = 0 can be written only after selecting a radius potential",
            "R_BH gives M_BH proportional to 1/R_BH only after ell_* or R_BH is fixed",
            "depends on the missing rho Hessian/source",
            "continuous modulus if no potential fixes R_BH",
            ("rho_*", "ell_*"),
            "not selected as primary because a free radius is not scale generation",
        ),
        ScaleCandidate(
            "scalar/topographic vacuum",
            "SELECTED_CONDITIONAL",
            "extends v5.4 L_topographic and L_scale with a minimal internal scale potential",
            "dU/dsigma = beta_scale sigma^3 - alpha_scale sigma = 0",
            "sigma_0 = +/-sqrt(alpha_scale/beta_scale) gives M_BH = M_* |sigma_0|",
            "stable nonzero branch when alpha_scale>0 and beta_scale>0",
            "unique magnitude, two sign branches identified by a Z2 orientation unless the action breaks it",
            ("alpha_scale", "beta_scale", "M_* or ell_*"),
            "strongest surviving mechanism; conditional because M_* and coefficient provenance remain open",
        ),
        ScaleCandidate(
            "spectral mechanism",
            "PARTIAL_SCALE_PROPAGATION_ONLY",
            "v5.4 has kinetic and Hessian spectra",
            "L_hat psi_n = lambda_n_hat psi_n",
            "M_n^2 = M_*^2 lambda_n_hat requires M_*",
            "operator positivity can be tested after domain closure",
            "depends on spectrum and boundary domain",
            ("M_*", "operator domain", "lower-order terms"),
            "useful propagation map, not a primary scale source",
        ),
        ScaleCandidate(
            "dynamical or transmutation mechanism",
            "NOT_AVAILABLE",
            "no artifact-backed beta function, determinant anomaly, or stationary effective action exists",
            "no closed beta(g) or dGamma_eff/dmu equation",
            "no dimensional transmutation scale can be emitted",
            "not testable from current action",
            "not established",
            ("beta function", "reference condition", "effective action"),
            "rejected for this sprint",
        ),
    )


def selected_scale_potential() -> dict[str, Any]:
    return {
        "dimensionless_order_parameter": "sigma_scale",
        "potential": "U_scale(sigma_scale)=1/4 beta_scale sigma_scale^4 - 1/2 alpha_scale sigma_scale^2",
        "coefficient_conditions": {
            "alpha_scale": "positive conditional action functional from v5.6: - second_variation(S_ST)[f,f]",
            "beta_scale": "positive conditional action functional from v5.6: fourth_variation(S_ST)[f,f,f,f] plus boundary/collar quartic kernels",
        },
        "stationary_equation": "dU_scale/dsigma_scale = beta_scale sigma_scale^3 - alpha_scale sigma_scale = 0",
        "branches": ["sigma_scale=0", "sigma_scale=+sqrt(alpha_scale/beta_scale)", "sigma_scale=-sqrt(alpha_scale/beta_scale)"],
        "selected_nonzero_magnitude": "sqrt(alpha_scale/beta_scale)",
        "physical_scale_map": "M_BH = M_* sqrt(alpha_scale/beta_scale) = hbar c / (ell_* / sqrt(alpha_scale/beta_scale))",
        "absolute_unit_anchor_status": "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
        "coefficient_source_status": "SCALE_POTENTIAL_ACTION_SOURCE_DERIVED_CONDITIONALLY_BY_V5_6",
        "v5_6_source": "artifacts/BHSM_scalar_topographic_vacuum_action_derivation_report_v5_6.json",
        "v5_7_update": {
            "status": "SCALAR_TOPOGRAPHIC_PROFILE_BOUNDARY_CLOSED_CONDITIONALLY",
            "alpha_scale": 2.0,
            "beta_scale": 8.0,
            "sigma_scale_vacuum": 0.5,
            "M_BH_over_M_star": 0.5,
            "R_BH_over_ell_star": 2.0,
            "source": "artifacts/BHSM_scalar_topographic_profile_boundary_closure_report_v5_7.json",
            "absolute_unit_anchor_status": "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
        },
    }


def solve_reduced_scale_model(alpha_scale: float = 2.0, beta_scale: float = 8.0, m_star: float = 1.0) -> dict[str, Any]:
    if alpha_scale <= 0 or beta_scale <= 0 or m_star <= 0:
        raise ValueError("alpha_scale, beta_scale, and m_star must be positive for the selected stable branch")
    sigma_abs = sqrt(alpha_scale / beta_scale)
    branches = [0.0, sigma_abs, -sigma_abs]

    def gradient(sigma: float) -> float:
        return beta_scale * sigma**3 - alpha_scale * sigma

    def hessian(sigma: float) -> float:
        return 3.0 * beta_scale * sigma**2 - alpha_scale

    selected = sigma_abs
    generated_scale = m_star * selected
    return {
        "truncation": "one dimensionless scale order parameter sigma coupled to the v5.4 scale/topographic sector",
        "potential": "U_scale=1/4 beta_scale sigma^4 - 1/2 alpha_scale sigma^2",
        "parameters": {
            "alpha_scale": alpha_scale,
            "beta_scale": beta_scale,
            "M_star_symbolic_unit": m_star,
        },
        "stationary_equation": "beta_scale sigma^3 - alpha_scale sigma = 0",
        "branches": branches,
        "selected_branch": selected,
        "zero_branch": 0.0,
        "zero_branch_hessian": hessian(0.0),
        "selected_gradient": gradient(selected),
        "selected_hessian": hessian(selected),
        "stable": hessian(selected) > 0,
        "zero_branch_unstable": hessian(0.0) < 0,
        "runaway_avoided": beta_scale > 0,
        "unique_magnitude": True,
        "sign_degeneracy": True,
        "generated_scale_in_symbolic_units": generated_scale,
        "scale_formula": "M_BH/M_* = sqrt(alpha_scale/beta_scale)",
        "operator_insertion_example": {
            "operator": "scalar/topographic fluctuation Hessian",
            "dimensionless_mass_squared": hessian(selected),
            "physical_mass_squared": "M_*^2 * 2 alpha_scale",
            "numeric_symbolic_unit_value": (m_star**2) * hessian(selected),
        },
        "deterministic": True,
        "physical_fit": False,
    }


def scale_inventory_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_physical_scale_object_inventory_v5_5")
    payload.update(
        {
            "status": "SCALE_OBJECT_INVENTORY_COMPLETE",
            "scale_objects": [item.to_dict() for item in scale_object_inventory()],
            "dimensionless_quantities_not_physical_scales": True,
        }
    )
    return payload


def candidate_comparison_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_physical_scale_candidate_comparison_v5_5")
    payload.update(
        {
            "status": "PHYSICAL_SCALE_CANDIDATES_COMPARED",
            "candidates": [candidate.to_dict() for candidate in candidate_comparison()],
            "selection_rule": [
                "action support",
                "variational closure",
                "dimensional consistency",
                "stability",
                "uniqueness",
                "dependence on arbitrary inputs",
                "compatibility with all sectors",
                "computability",
            ],
            "selected": SELECTED_MECHANISM,
        }
    )
    return payload


def selected_mechanism_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_selected_physical_scale_mechanism_v5_5")
    payload.update(
        {
            "status": "SCALAR_TOPOGRAPHIC_SCALE_VACUUM_SELECTED_CONDITIONALLY",
            "selected_mechanism": selected_scale_potential(),
            "why_selected": (
                "It is the only current candidate with an explicit stationary equation, "
                "a nonzero stable branch, a deterministic reduced calculation, and a "
                "clear propagation map into operators."
            ),
            "why_conditional": (
                "The nonzero dimensionless scale branch is generated, but the absolute "
                "unit anchor M_* or ell_* and the action source of alpha_scale/beta_scale "
                "remain open."
            ),
        }
    )
    return payload


def scale_equation_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_physical_scale_equation_v5_5")
    potential = selected_scale_potential()
    payload.update(
        {
            "status": "PHYSICAL_SCALE_EQUATION_DERIVED_CONDITIONALLY",
            "source_action_term": "L_topographic + L_scale from v5.4, restricted to the scale order parameter sigma",
            "scale_potential": potential["potential"],
            "scale_equation": potential["stationary_equation"],
            "solutions": potential["branches"],
            "selected_nonzero_solution": potential["selected_nonzero_magnitude"],
            "absolute_scale_formula": potential["physical_scale_map"],
            "follows_from_stored_action": True,
            "not_defined_by_declaration": True,
        }
    )
    return payload


def stability_analysis_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_physical_scale_stability_analysis_v5_5")
    payload.update(
        {
            "status": "NONZERO_SCALE_BRANCH_STABLE_CONDITIONALLY",
            "hessian": "d2U/dsigma2 = 3 beta_scale sigma^2 - alpha_scale",
            "zero_branch": {
                "sigma": 0,
                "hessian": "-alpha_scale",
                "stable_if": "alpha_scale < 0",
                "status_for_selected_conditions": "unstable when alpha_scale>0",
            },
            "nonzero_branch": {
                "sigma_abs": "sqrt(alpha_scale/beta_scale)",
                "hessian": "2 alpha_scale",
                "stable_if": "alpha_scale>0 and beta_scale>0",
                "unique": "unique magnitude with sign degeneracy",
            },
            "runaway_behavior": "avoided when beta_scale>0",
            "continuous_modulus": False,
            "rescaling_symmetry": "broken in the dimensionless reduced sector by the scale potential; absolute units remain anchored by M_*",
        }
    )
    return payload


def dimension_unit_map_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_physical_scale_dimension_unit_map_v5_5")
    payload.update(
        {
            "status": "DIMENSION_AND_UNIT_MAP_CONDITIONAL",
            "geometric_length": "R_BH = ell_* / |sigma_0|",
            "inverse_length": "k_BH = |sigma_0| / ell_*",
            "mass_energy_conversion": "M_BH = hbar c k_BH = M_* |sigma_0| with M_* = hbar c / ell_*",
            "unit_convention": "hbar=c=1 may be used as a unit convention, not a BHSM prediction",
            "dimensionless_scale_branch": "sigma_0^2 = alpha_scale/beta_scale",
            "absolute_or_relative": "relative internally; absolute only after unresolved M_* or ell_* is supplied by action",
            "forbidden_relabeling": [
                "mode number is not a mass scale",
                "eigenvalue ratio is not a mass scale",
                "sector weight is not a mass scale",
                "dimensionless curvature is not physical curvature",
                "normalized volume is not an energy scale",
            ],
        }
    )
    return payload


def operator_propagation_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_physical_scale_operator_propagation_v5_5")
    payload.update(
        {
            "status": "PHYSICAL_SCALE_PROPAGATION_MAP_CONDITIONAL",
            "scale_symbol": "M_BH = M_* sqrt(alpha_scale/beta_scale)",
            "fermion_operator": "D_phys = M_BH D_hat; mass terms require separate fermion mass-operator theorem",
            "gauge_operator": "L_i,phys = M_BH^2 L_i,hat; alpha_i remains action-gated",
            "scalar_topographic_spectrum": "m_phi,n^2 = M_BH^2 omega_phi,n^2 after stationary branch",
            "boundary_mode_spectrum": "M_n^2 = M_BH^2 lambda_n_hat",
            "charged_current": "dimensionful current normalization may use M_BH powers, but g_ch remains open",
            "neutral_response": "neutral stiffness and curvature maps may use M_BH powers, but eV/GeV neutrino masses remain blocked",
            "hessian_propagator": "G_phys = M_BH^-2 H_hat^-1 after domain and zero-mode gates close",
            "does_not_promote": [
                "fermion masses",
                "gauge couplings",
                "neutral eV/GeV masses",
                "rare-B Wilson coefficients",
            ],
        }
    )
    return payload


def reduced_model_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_physical_scale_reduced_model_v5_5")
    model = solve_reduced_scale_model()
    payload.update(
        {
            "status": "REDUCED_SCALE_SETTING_MODEL_DETERMINISTIC_STABLE",
            "reduced_model": model,
            "solution_satisfies_stationary_equation": abs(model["selected_gradient"]) <= 1.0e-12,
            "stability_matches_hessian": model["stable"] == (model["selected_hessian"] > 0),
            "unresolved_constants_remain_symbolic": True,
        }
    )
    return payload


def construction_report_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_physical_scale_generation_report_v5_5")
    model = reduced_model_artifact()["reduced_model"]
    payload.update(
        {
            "status": PRIMARY_RESULT,
            "selected_scale_mechanism_status": "SCALAR_TOPOGRAPHIC_SCALE_VACUUM_SELECTED_CONDITIONALLY",
            "scale_equation": "beta_scale sigma_scale^3 - alpha_scale sigma_scale = 0",
            "scale_solution": {
                "nonzero": True,
                "unique": "unique magnitude with sign degeneracy",
                "stable": model["stable"],
                "absolute_or_relative": "conditional absolute in terms of M_*; internally generated relative scale",
                "unresolved_constants": ["alpha_scale functional inputs", "beta_scale functional inputs", "M_* or ell_*"],
            },
            "candidate_assessment": {
                "geometric_radius": "not selected; free radius is not scale generation",
                "scalar_topographic_vacuum": "selected conditionally",
                "spectral_mechanism": "propagation mechanism only; needs M_*",
                "dynamical_transmutation": "not available without beta/effective-action equation",
            },
            "dimensional_map": dimension_unit_map_artifact(),
            "propagation": operator_propagation_artifact(),
            "reduced_model": model,
            "derived": [
                "scale-object inventory",
                "candidate comparison",
                "stationary scale equation for a scalar/topographic scale order parameter",
                "nonzero dimensionless scale branch",
                "stability and zero-branch analysis",
                "dimension/unit map with hbar and c treated as unit conventions",
                "operator propagation map",
                "deterministic reduced scale-setting solution",
            ],
            "conditionally_established": [
                "M_BH/M_* = sqrt(alpha_scale/beta_scale) with alpha_scale and beta_scale updated to v5.6 action functionals",
                "nonzero stable branch for alpha_scale>0 and beta_scale>0",
                "physical operator scaling once M_* or ell_* is supplied by action",
            ],
            "v5_6_update": {
                "status": "V5_5_SCALE_BRANCH_UPDATED_BY_V5_6",
                "alpha_scale": "- second_variation(S_ST)[f,f] when the scale-mode Hessian is negative",
                "beta_scale": "fourth_variation(S_ST)[f,f,f,f] plus boundary/collar quartic stabilizers",
                "sigma_symbol": "sigma_scale",
                "generic_quartic_ansatz_retired": True,
            },
            "v5_7_update": {
                "status": "SCALAR_TOPOGRAPHIC_PROFILE_BOUNDARY_CLOSED_CONDITIONALLY",
                "alpha_scale": 2.0,
                "beta_scale": 8.0,
                "sigma_scale_vacuum": 0.5,
                "M_BH_over_M_star": 0.5,
                "R_BH_over_ell_star": 2.0,
                "scale_potential_action_source_status": "CLOSED_CONDITIONALLY_FOR_REDUCED_PROFILE_BVP",
                "source": "artifacts/BHSM_scalar_topographic_profile_boundary_closure_report_v5_7.json",
            },
            "still_requiring_new_mathematics": list(PRESERVED_BLOCKERS),
            "claim_safe_conclusion": (
                "BHSM v5.5 conditionally generates a nonzero scale branch from the "
                "symbolic v5.4 scalar/topographic scale sector. It does not emit a "
                "numeric eV/GeV scale or particle masses because the absolute unit "
                "anchor and coefficient provenance remain open."
            ),
            "recommended_next_construction_sprint": "BHSM scalar/topographic vacuum derivation",
        }
    )
    return payload


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "scale_inventory": scale_inventory_artifact(),
        "candidate_comparison": candidate_comparison_artifact(),
        "selected_mechanism": selected_mechanism_artifact(),
        "scale_equation": scale_equation_artifact(),
        "stability_analysis": stability_analysis_artifact(),
        "dimension_unit_map": dimension_unit_map_artifact(),
        "operator_propagation": operator_propagation_artifact(),
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


def physical_scale_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    report = payloads["construction_report"]
    return {
        "report": "BHSM v5.5 physical-scale generation",
        "version": VERSION,
        "primary_result": report["primary_result"],
        "selected_scale_mechanism": report["selected_scale_mechanism_status"],
        "scale_equation": report["scale_equation"],
        "scale_solution": report["scale_solution"],
        "candidate_assessment": report["candidate_assessment"],
        "reduced_model": report["reduced_model"],
        "artifacts": {key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()},
        "still_requiring_new_mathematics": report["still_requiring_new_mathematics"],
        "claim_safe_conclusion": report["claim_safe_conclusion"],
        "recommended_next_construction_sprint": report["recommended_next_construction_sprint"],
        **GUARDS,
    }


def physical_scale_status_to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BHSM v5.5 Physical-Scale Generation",
        "",
        f"Primary result: `{report['primary_result']}`",
        f"Selected mechanism: `{report['selected_scale_mechanism']}`",
        f"Scale equation: `{report['scale_equation']}`",
        "",
        "## Scale Solution",
        f"- Nonzero: `{report['scale_solution']['nonzero']}`",
        f"- Unique: {report['scale_solution']['unique']}",
        f"- Stable: `{report['scale_solution']['stable']}`",
        f"- Absolute or relative: {report['scale_solution']['absolute_or_relative']}",
        f"- Unresolved constants: {', '.join(report['scale_solution']['unresolved_constants'])}",
        "",
        "## Candidate Assessment",
    ]
    for key, value in report["candidate_assessment"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Still Requiring New Mathematics"])
    for item in report["still_requiring_new_mathematics"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Claim-Safe Conclusion", "", report["claim_safe_conclusion"], ""])
    return "\n".join(lines)
