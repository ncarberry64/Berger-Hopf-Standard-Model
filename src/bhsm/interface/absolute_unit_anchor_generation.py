"""BHSM v5.8 absolute unit-anchor generation audit.

This module tests whether the merged v5.4-v5.7 construction fixes an absolute
length ell_star without importing measured masses, cosmology, or Standard Model
calibration. The result is intentionally conservative: the current normalized
action fixes dimensionless ratios but leaves a global size modulus unfixed.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


VERSION = "v5.8"
SPRINT = "bhsm-absolute-unit-anchor-generation-v5-8"
PRIMARY_RESULT = "BHSM_ABSOLUTE_UNIT_ANCHOR_NOT_GENERATED"

ARTIFACT_FILES = {
    "primordial_state": "BHSM_primordial_compact_state_v5_8.json",
    "scale_modulus": "BHSM_absolute_unit_scale_modulus_audit_v5_8.json",
    "unit_propagation": "BHSM_absolute_unit_propagation_v5_8.json",
    "construction_report": "BHSM_absolute_unit_anchor_generation_report_v5_8.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "observed_mass_or_vev_used": False,
    "pdg_reference_values_used": False,
    "w_calibration_used": False,
    "cosmological_parameter_used": False,
    "hubble_or_cmb_calibration_used": False,
    "planck_length_inserted": False,
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

OPEN_GATES = (
    "OPEN_MISSING_GLOBAL_SCALE_MODULUS_ACTION_SOURCE",
    "OPEN_MISSING_NONLINEAR_GEOMETRIC_BACKREACTION",
    "OPEN_MISSING_ABSOLUTE_ACTION_QUANTUM_OR_BOUNDARY_TENSION",
    "OPEN_MISSING_ABSOLUTE_SPECTRAL_EIGENVALUE_SOURCE",
    "OPEN_MISSING_PRIMORDIAL_REGULARITY_SCALE_CONDITION",
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
class InvariantCandidate:
    name: str
    symbol: str
    dimension: str
    action_source: str
    dynamical: bool
    fixed_by_equation: bool
    rescaling_behavior: str
    can_define_ell_star: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScalingTerm:
    term: str
    normalized_source: str
    raw_L_power: int | str
    coefficient_requirement: str
    status: str
    reason_no_absolute_anchor: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _common_payload(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": (
            "BHSM v5.8 audits the primordial compact-state and global size "
            "modulus as possible absolute unit anchors. The current action "
            "selects dimensionless ratios M_BH/M_star=1/2 and R_BH/ell_star=2 "
            "but does not generate ell_star, M_star, particle masses, gauge "
            "couplings, CKM values, rare-B observables, or full BHSM completion."
        ),
        **GUARDS,
    }


def primordial_state() -> dict[str, Any]:
    return {
        "status": "PRIMORDIAL_COMPACT_STATE_DEFINED_AS_CANDIDATE",
        "geometry": "compact normalized Berger-Hopf boundary cell Sigma_B with collar/turning layer [0,rho_star]",
        "topology": "Hopf-fibered compact boundary topology retained as dimensionless topological data",
        "metric": "g(L)=L^2 g_hat with dimensionless Berger metric g_hat",
        "orientation": "outward oriented initial boundary/turning surface",
        "boundary_or_turning_surface": "regular compact-to-expanding transition hypersurface in normalized variables",
        "scalar_topographic_state": {
            "sigma_scale": 0.5,
            "M_BH_over_M_star": 0.5,
            "R_BH_over_ell_star": 2.0,
            "source": "v5.7 reduced scalar/topographic profile-boundary closure",
        },
        "collar_or_transition_layer": "rho in [0,1] in normalized coordinates; physical width is L times dimensionless width",
        "dynamical_variables": ["global size modulus L", "normalized metric variations", "scalar/topographic fields", "sector fields"],
        "fixed_variables": ["dimensionless topology", "orientation", "normalized reference coordinates"],
        "white_hole_like_interpretation": (
            "The primordial hot plasma is treated as the outward high-energy "
            "phase of an initial compact geometric release. This is an "
            "interpretation of the candidate initial data, not an additional "
            "equation that fixes L."
        ),
        "late_universe_doctrine": {
            "early_release_still_occurring": False,
            "redshifted_relics_are_physical": True,
            "effective_or_virtual_memory": "present boundary/topographic response memory, not on-shell relic matter",
        },
    }


def invariant_candidates() -> tuple[InvariantCandidate, ...]:
    return (
        InvariantCandidate("primordial curvature radius", "R_0=L R_hat", "length", "normalized Berger/collar geometry", True, False, "R_0 -> lambda R_0", False, "R_hat is dimensionless and L is the unfixed modulus"),
        InvariantCandidate("compact volume", "V_0=L^3 V_hat", "length^3", "boundary/collar measure", True, False, "V_0 -> lambda^3 V_0", False, "volume scales with L and no equation fixes V_0"),
        InvariantCandidate("boundary area", "A_0=L^2 A_hat", "length^2", "boundary measure", True, False, "A_0 -> lambda^2 A_0", False, "area is proportional to the unfixed modulus"),
        InvariantCandidate("integrated scalar curvature", "int R dmu", "length or dimensionless depending support", "geometric action skeleton", True, False, "rescales with the chosen support dimension", False, "no absolute curvature normalization or action quantum is derived"),
        InvariantCandidate("extrinsic curvature invariant", "int K dA", "length or dimensionless depending normalization", "boundary action normal form", True, False, "tracks L through K~1/L and dA~L^2", False, "boundary coefficient/tension with absolute units is not derived"),
        InvariantCandidate("collar width", "rho_star L", "length", "v5.7 collar coordinate", True, False, "rho_star L -> lambda rho_star L", False, "rho_star=1 is a coordinate convention, not a physical length"),
        InvariantCandidate("lowest nonzero spectral eigenvalue", "lambda_n=lambda_hat_n/L^2", "length^-2", "Laplace-type spectral structures", True, False, "lambda_n -> lambda_n/lambda^2", False, "lambda_hat_n is dimensionless; no absolute eigenvalue theorem exists"),
        InvariantCandidate("topological quantization number", "n", "dimensionless", "Hopf/topological data", False, True, "invariant", False, "integer topology can label sectors but cannot supply a length"),
        InvariantCandidate("action stationary scale", "L_0", "length", "global scale-modulus action", True, False, "undetermined", False, "current S_eff is flat or depends on free dimensionful coefficients"),
        InvariantCandidate("regular turning surface", "K_or_pi=0", "constraint", "primordial transition regularity", True, False, "homogeneous under L rescaling", False, "regularity removes singular branches but does not select a magnitude for L"),
    )


def scaling_terms() -> tuple[ScalingTerm, ...]:
    return (
        ScalingTerm("geometric curvature term", "v5.4 symbolic geometry action", 2, "absolute gravitational/curvature coefficient or constraint normalization", "SCALE_WEIGHT_RECORDED_SOURCE_OPEN", "a coefficient with absolute dimensions is required to compare this term to dimensionless sectors"),
        ScalingTerm("gauge Yang-Mills term", "v4.6/v5.4 normalized gauge skeleton", 0, "gauge coupling/action attachment", "CONFORMAL_WEIGHT_DOES_NOT_FIX_L", "classical four-dimensional gauge scaling is L-neutral after field normalization"),
        ScalingTerm("fermion kinetic term", "v5.4 fermion operator slot", 0, "Dirac operator action source and mass operator theorem", "NORMALIZED_NO_MASS_ANCHOR", "massless kinetic normalization does not select L"),
        ScalingTerm("scalar/topographic kinetic term", "v5.6/v5.7 normalized profile sector", 2, "absolute kinetic coefficient if physical units are demanded", "RELATIVE_SCALE_ONLY", "v5.7 fixes sigma_scale but not the physical length multiplying the normalized cell"),
        ScalingTerm("scalar/topographic vacuum term", "v5.7 evaluated A_ST/G_ST", 4, "absolute vacuum-density coefficient", "DIMENSIONLESS_BRANCH_FIXED_ONLY", "alpha_scale=2 and beta_scale=8 fix M_BH/M_star, not M_star"),
        ScalingTerm("boundary term", "boundary normal forms", 2, "boundary tension or absolute boundary action coefficient", "BOUNDARY_TENSION_OPEN", "a boundary area term can fix L only if its absolute coefficient is action-derived"),
        ScalingTerm("collar term", "collar measure normal form", 3, "collar density or transition-layer action source", "COLLAR_SCALE_SOURCE_OPEN", "rho_star is normalized; physical collar width remains L times rho_star"),
        ScalingTerm("spectral term", "Laplace/Weyl spectral candidate", "depends on heat-kernel coefficient", "absolute eigenvalue/action quantum", "SPECTRAL_ANCHOR_OPEN", "lambda_hat_n/L^2 is not an absolute energy without a fixed physical eigenvalue"),
        ScalingTerm("measure", "g=L^2 g_hat", "d-volume power", "chosen integration dimension and coefficient units", "MEASURE_SCALING_ONLY", "the measure tracks L but does not by itself create a stationary equation"),
    )


def effective_scale_action() -> dict[str, Any]:
    return {
        "status": "GLOBAL_SCALE_MODULUS_FLAT_OR_UNDERDETERMINED",
        "size_modulus": "L",
        "metric_decomposition": "g = L^2 g_hat",
        "coordinates": "x = L x_hat",
        "rescaling_transformation": {
            "g": "g -> lambda^2 g",
            "L": "L -> lambda L",
            "ell_star": "ell_star -> lambda ell_star",
            "M_star": "M_star -> M_star/lambda",
            "dimensionless_fields_and_topology": "unchanged",
        },
        "S_eff_current": "S_eff(L)=S_hat[sigma_scale=1/2] after factoring the arbitrary unit ell_star",
        "dS_eff_dL": 0.0,
        "d2S_eff_dL2": 0.0,
        "stationary_points": "all positive L are stationary in the normalized reduced model",
        "selected_branch": None,
        "positive_finite_unique_solution": False,
        "zero_size_branch_handled": "L=0 is excluded as degenerate geometry, not selected",
        "infinite_size_runaway": "flat direction rather than bounded finite minimum",
        "dimensionful_inputs": [],
        "why_no_anchor": (
            "Every serious candidate either rescales with L, is dimensionless "
            "topological data, or requires an unproved absolute action coefficient, "
            "boundary tension, action quantum, or spectral eigenvalue."
        ),
    }


def spectral_topological_assessment() -> dict[str, Any]:
    return {
        "topology_fixes_scale": False,
        "topology_reason": "topological charges and Hopf data are dimensionless",
        "spectrum_fixes_scale": False,
        "spectrum_reason": "lambda_n=lambda_hat_n/L^2 leaves L arbitrary without an absolute eigenvalue theorem",
        "regularity_fixes_scale": False,
        "regularity_reason": "finite action, smooth turning surface, and zero canonical momentum are homogeneous constraints in the current normalized model",
        "action_stationarity_fixes_scale": False,
        "action_stationarity_reason": "dS_eff/dL=0 is identically flat or depends on missing dimensionful coefficients",
    }


def unit_anchor_payload() -> dict[str, Any]:
    return {
        "status": PRIMARY_RESULT,
        "ell_star": None,
        "M_star": None,
        "M_BH": None,
        "R_BH": None,
        "absolute_or_relative": "relative only",
        "preserved_relative_ratios": {
            "M_BH_over_M_star": 0.5,
            "R_BH_over_ell_star": 2.0,
            "sigma_scale": 0.5,
        },
        "M_BH_equals_M_star_over_2_only_after_M_star_exists": True,
        "hbar_c_status": "conversion convention only; hbar=c=1 may be used as natural-unit convention",
        "unresolved_constants": ["ell_star", "M_star", "absolute action coefficient or scale-modulus source"],
    }


def propagation_payload() -> dict[str, Any]:
    return {
        "status": "UNIT_PROPAGATION_BLOCKED_PENDING_ABSOLUTE_ANCHOR",
        "fermion_operator": "D_phys = M_BH D_hat only after M_BH exists; no fermion masses are derived",
        "gauge_operator": "L_gauge,phys = M_BH^2 L_gauge,hat only after M_BH exists; alpha_i remains action-gated",
        "scalar_spectrum": "H_ST,phys = M_BH^2 H_ST,hat only after M_BH exists",
        "charged_current": "dimensionful current normalization remains open",
        "neutral_response": "neutral physical eV/GeV scale remains open",
        "collar_thickness": "rho_star L is physical only after L=ell_star is fixed",
        "hessian_green_operator": "G_phys = M_BH^-2 H_hat^-1 only after M_BH exists",
        "particle_masses_derived_by_multiplication": False,
    }


def primordial_to_late_time_map() -> dict[str, Any]:
    return {
        "initial_release": "candidate compact geometric release from normalized primordial boundary data",
        "redshifted_relics": "physical on-shell relic matter/radiation may be redshifted from an already-defined initial scale",
        "virtual_or_effective_memory": "late boundary/topographic response memory can be effective or virtual",
        "cmb_and_relic_matter_are_virtual": False,
        "redshift_generates_unit": False,
        "scale_transport": "redshift can transport a scale after ell_star exists; it cannot create ell_star",
        "cosmological_fit_attempted": False,
    }


def primordial_state_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_primordial_compact_state_v5_8")
    payload.update(
        {
            "status": "PRIMORDIAL_COMPACT_STATE_DEFINED_AS_CANDIDATE",
            "primordial_state": primordial_state(),
            "candidate_invariants": [candidate.to_dict() for candidate in invariant_candidates()],
            "primordial_to_late_time_map": primordial_to_late_time_map(),
        }
    )
    return payload


def scale_modulus_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_absolute_unit_scale_modulus_audit_v5_8")
    payload.update(
        {
            "status": "ABSOLUTE_UNIT_SCALE_MODULUS_NOT_FIXED",
            "effective_scale_action": effective_scale_action(),
            "scaling_terms": [term.to_dict() for term in scaling_terms()],
            "spectral_topological_assessment": spectral_topological_assessment(),
        }
    )
    return payload


def unit_propagation_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_absolute_unit_propagation_v5_8")
    payload.update(
        {
            "status": "UNIT_PROPAGATION_BLOCKED_PENDING_ABSOLUTE_ANCHOR",
            "unit_anchor": unit_anchor_payload(),
            "propagation": propagation_payload(),
            "primordial_to_late_time_map": primordial_to_late_time_map(),
        }
    )
    return payload


def construction_report_payload() -> dict[str, Any]:
    return {
        "status": PRIMARY_RESULT,
        "primordial_state": primordial_state(),
        "scale_modulus": effective_scale_action(),
        "candidate_invariants": [candidate.to_dict() for candidate in invariant_candidates()],
        "action_scaling_terms": [term.to_dict() for term in scaling_terms()],
        "unit_anchor": unit_anchor_payload(),
        "spectral_topological_assessment": spectral_topological_assessment(),
        "primordial_to_late_time_map": primordial_to_late_time_map(),
        "propagation": propagation_payload(),
        "derived": [
            "primordial compact-state candidate in normalized Berger-Hopf variables",
            "global size-modulus transformation g=L^2 g_hat",
            "action scaling audit for current v5.4-v5.7 terms",
            "proof that v5.7 sigma_scale=1/2 remains a relative scale only",
        ],
        "conditionally_established": [
            "redshift can transport a BHSM-native scale after it exists",
            "CMB/relic matter are physical relics, while boundary/topographic memory may be effective or virtual",
            "M_BH/M_star=1/2 and R_BH/ell_star=2 remain valid relative ratios",
        ],
        "still_requiring_new_mathematics": list(OPEN_GATES),
        "claim_safe_conclusion": (
            "BHSM v5.8 does not generate an absolute unit anchor. The present "
            "primordial compact-state candidate and normalized action preserve a "
            "continuous global size modulus unless a new BHSM-native scale-modulus "
            "action source, absolute action quantum, boundary tension, spectral "
            "eigenvalue, or nonlinear backreaction theorem fixes L."
        ),
        "recommended_next_construction_sprint": "bhsm-global-scale-modulus-action-source-v5-9",
    }


def construction_report_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_absolute_unit_anchor_generation_report_v5_8")
    payload.update(construction_report_payload())
    return payload


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "primordial_state": primordial_state_artifact(),
        "scale_modulus": scale_modulus_artifact(),
        "unit_propagation": unit_propagation_artifact(),
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


def absolute_unit_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    report = payloads["construction_report"]
    return {
        "report": "BHSM v5.8 absolute unit-anchor generation",
        "version": VERSION,
        "primary_result": PRIMARY_RESULT,
        "primordial_state": report["primordial_state"],
        "scale_modulus": report["scale_modulus"],
        "unit_anchor": report["unit_anchor"],
        "spectral_topological_assessment": report["spectral_topological_assessment"],
        "primordial_to_late_time_map": report["primordial_to_late_time_map"],
        "propagation": report["propagation"],
        "still_requiring_new_mathematics": report["still_requiring_new_mathematics"],
        "claim_safe_conclusion": report["claim_safe_conclusion"],
        "recommended_next_construction_sprint": report["recommended_next_construction_sprint"],
        "artifacts": {key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()},
        **GUARDS,
    }


def absolute_unit_status_to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BHSM v5.8 Absolute Unit-Anchor Generation",
        "",
        f"Primary result: `{report['primary_result']}`",
        f"ell_star: `{report['unit_anchor']['ell_star']}`",
        f"M_star: `{report['unit_anchor']['M_star']}`",
        f"M_BH/M_star: `{report['unit_anchor']['preserved_relative_ratios']['M_BH_over_M_star']}`",
        f"R_BH/ell_star: `{report['unit_anchor']['preserved_relative_ratios']['R_BH_over_ell_star']}`",
        "",
        "## Scale Modulus",
        f"- S_eff(L): {report['scale_modulus']['S_eff_current']}",
        f"- dS_eff/dL: `{report['scale_modulus']['dS_eff_dL']}`",
        f"- selected branch: `{report['scale_modulus']['selected_branch']}`",
        f"- unique finite solution: `{report['scale_modulus']['positive_finite_unique_solution']}`",
        "",
        "## Still Requiring New Mathematics",
    ]
    for item in report["still_requiring_new_mathematics"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Claim-Safe Conclusion", "", report["claim_safe_conclusion"], ""])
    return "\n".join(lines)
