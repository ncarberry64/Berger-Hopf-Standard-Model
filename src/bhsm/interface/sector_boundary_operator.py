"""Structural v4.6 sector boundary-operator candidates."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Literal

from .gauge_coupling_spectral_residue import (
    CASIMIR_SHELL_RESIDUES,
    GAUGE_ADJOINT_DIMS,
    TAU_FRAME_CANDIDATE,
    candidate_lambda_reference,
    universal_weyl_3d_density,
)

Sector = Literal["U1", "SU2", "SU3"]
FRAME_COUNT = 3
PRINCIPAL_SYMBOL = "|xi|^2_{h_rho} I_{T*Sigma_rho} tensor I_{ad_i}"
ACTS_ON = "active adjoint-valued boundary one-forms A_i in Omega^1(Sigma_rho, ad_i)"

OPEN_GATES = (
    "OPEN_MISSING_SECTOR_BOUNDARY_OPERATOR_ACTION_SOURCE",
    "OPEN_MISSING_GAUGE_FIXED_BOUNDARY_DOMAIN",
    "OPEN_MISSING_LOWER_ORDER_BOUNDARY_OPERATOR_TERMS",
    "OPEN_MISSING_WHITENED_BOUNDARY_OPERATOR_ACTION_SOURCE",
    "OPEN_MISSING_SPECTRAL_COVARIANCE_SOURCE",
    "OPEN_MISSING_INVERSE_COVARIANCE_ACTION_ATTACHMENT",
    "OPEN_MISSING_SPECTRAL_CORRECTION_Z_i",
    "OPEN_MISSING_ACTION_SELECTED_RHO_i_OF_MU",
    "OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION",
    "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
    "OPEN_MISSING_G2_BH_ACTION_SOURCE",
    "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
    "CKM_EXPONENT_NOT_DERIVED",
    "FULL_BHSM_NOT_COMPLETE",
    "OPEN_MISSING_CASIMIR_SHELL_ACTION_ATTACHMENT",
    "OPEN_MISSING_SECTOR_BOUNDARY_OPERATOR_L_i",
)

LOWER_ORDER_TERMS = (
    "Berger curvature and one-form Ricci terms",
    "adjoint connection-curvature terms",
    "shape-operator and collar terms",
    "boundary extrinsic-curvature terms",
    "sector/projector terms",
    "scalar/topographic response terms",
)

INVALIDATIONS = (
    "A raw unrestricted one-form Weyl count introduces a factor of three; the conditional primitive frame state tau_frame=1/3 prevents this overcount.",
    "A Laplace-type principal symbol does not determine the full physical boundary operator; lower-order terms and the action source remain open.",
    "L_i(rho) is not final on unrestricted gauge potentials without a gauge-fixed, transverse/coexact, quotient, or admissible boundary domain.",
    "Whitened boundary-action coherence does not prove lambda_i=alpha_i; physical coupling identification remains action-gated.",
    "Leading Weyl density plus candidate L_i does not produce running without Z_i, lower heat-kernel/collar corrections, and action-selected rho_i(mu).",
    "This sprint does not derive gauge couplings, CKM values or exponent, or full BHSM completion.",
)

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
    "frozen_predictions_modified": False,
    "official_prediction_logic_modified": False,
    "physics_validation_claimed": False,
}


@dataclass(frozen=True)
class BoundaryOperatorCandidate:
    sector: Sector
    operator_family: str
    acts_on: str
    principal_symbol: str
    candidate_full_operator: str
    gauge_fixed_candidate: str
    berger_hodge_relation: str
    gauge_domain_status: str
    lower_order_terms_status: str
    action_source_status: str
    physical_coupling_status: str


def sector_boundary_operator_candidate(sector: Sector) -> BoundaryOperatorCandidate:
    if sector not in GAUGE_ADJOINT_DIMS:
        raise KeyError(sector)
    return BoundaryOperatorCandidate(
        sector=sector,
        operator_family="Laplace-type / Hodge-de Rham-type boundary kinetic operator",
        acts_on=ACTS_ON,
        principal_symbol=PRINCIPAL_SYMBOL,
        candidate_full_operator="Delta_1,rho^ad_i=d_i,rho^dagger d_i,rho+d_i,rho d_i,rho^dagger",
        gauge_fixed_candidate="L_i^gf(rho)=d_i,rho^dagger d_i,rho on a controlled transverse/coexact domain",
        berger_hodge_relation="d_i,rho^dagger is defined using the Berger boundary metric h_rho and Hodge star *_{h_rho}",
        gauge_domain_status="OPEN_MISSING_GAUGE_FIXED_BOUNDARY_DOMAIN",
        lower_order_terms_status="OPEN_MISSING_LOWER_ORDER_BOUNDARY_OPERATOR_TERMS",
        action_source_status="OPEN_MISSING_SECTOR_BOUNDARY_OPERATOR_ACTION_SOURCE",
        physical_coupling_status="OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
    )


def has_laplace_type_principal_symbol(candidate: BoundaryOperatorCandidate) -> bool:
    return candidate.principal_symbol == PRINCIPAL_SYMBOL and "Laplace-type" in candidate.operator_family


def effective_frame_normalized_residue(sector: Sector) -> float:
    return TAU_FRAME_CANDIDATE * FRAME_COUNT * CASIMIR_SHELL_RESIDUES[sector]


def candidate_operator_table() -> dict[str, dict[str, object]]:
    return {sector: asdict(sector_boundary_operator_candidate(sector)) for sector in GAUGE_ADJOINT_DIMS}


def frame_normalized_principal_residue_table() -> dict[str, dict[str, object]]:
    return {
        sector: {
            "gauge_algebra_dimension": GAUGE_ADJOINT_DIMS[sector],
            "active_residue": CASIMIR_SHELL_RESIDUES[sector],
            "raw_frame_count": FRAME_COUNT,
            "tau_frame": TAU_FRAME_CANDIDATE,
            "effective_frame_factor": FRAME_COUNT * TAU_FRAME_CANDIDATE,
            "effective_residue": effective_frame_normalized_residue(sector),
            "lambda_reference": candidate_lambda_reference(sector),
            "is_gauge_boson_count": False,
        }
        for sector in GAUGE_ADJOINT_DIMS
    }


def whitened_action_formula(sector: Sector) -> dict[str, object]:
    return {
        "sector": sector,
        "whitened_variable": "B_i=L_i(rho)^(1/2) A_i",
        "quadratic_action": "S_i=[1/(2 lambda_i)] <A_i,L_i(rho)A_i>=[1/(2 lambda_i)] <B_i,B_i>",
        "spectral_covariance": "lambda_i(mu,rho)=[w_i/(6*pi^2)] Z_i(mu,rho_i(mu))",
        "reference_condition": "Z_i(mu0,rho0)=1",
        "lambda_reference": candidate_lambda_reference(sector),
        "physical_alpha_status": "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
        "is_action_derived": False,
    }


def required_open_gates() -> list[str]:
    return list(OPEN_GATES)


def status_table() -> dict[str, str]:
    return {
        "sector_boundary_operator": "SECTOR_BOUNDARY_OPERATOR_CONDITIONAL_CANDIDATE",
        "principal_symbol": "LAPLACE_TYPE_PRINCIPAL_SYMBOL_CONDITIONAL",
        "frame_normalized_residue": "FRAME_NORMALIZED_PRINCIPAL_RESIDUE_CONDITIONAL",
        "whitened_gauge_action": "WHITENED_GAUGE_ACTION_CONDITIONAL",
        "gauge_domain": "OPEN_MISSING_GAUGE_FIXED_BOUNDARY_DOMAIN",
        "lower_order_terms": "OPEN_MISSING_LOWER_ORDER_BOUNDARY_OPERATOR_TERMS",
        "alpha_i": "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
        "g2_BH": "OPEN_MISSING_G2_BH_ACTION_SOURCE",
        "ckm_value": "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
        "ckm_exponent": "CKM_EXPONENT_NOT_DERIVED",
        "full_completion": "FULL_BHSM_NOT_COMPLETE",
    }


def build_artifact_payloads() -> dict[str, dict[str, object]]:
    candidate = asdict(sector_boundary_operator_candidate("SU2"))
    common = {"version": "v4.6", "open_gates": list(OPEN_GATES), "no_go_notes": list(INVALIDATIONS), **GUARDS}
    payloads = {
        "sector_boundary_operator": {"artifact": "BHSM_sector_boundary_operator_v4_6", "status": "SECTOR_BOUNDARY_OPERATOR_CONDITIONAL_CANDIDATE", "claim_boundary": "conditional_candidate_not_action_derived", "operator_candidate": candidate, "sector_operator_table": candidate_operator_table(), "residue_source": {"depends_on_v4_5": True, "active_residues": dict(CASIMIR_SHELL_RESIDUES), "lambda_reference": "w_i/(6*pi^2)", "physical_alpha_status": "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION"}},
        "whitened_gauge_action": {"artifact": "BHSM_whitened_gauge_action_v4_6", "status": "WHITENED_GAUGE_ACTION_CONDITIONAL", "candidate_actions": {sector: whitened_action_formula(sector) for sector in GAUGE_ADJOINT_DIMS}, "claim_boundary": "The coherent quadratic form is not an action-derived physical coupling identification."},
        "boundary_operator_principal_symbol": {"artifact": "BHSM_boundary_operator_principal_symbol_v4_6", "status": "LAPLACE_TYPE_PRINCIPAL_SYMBOL_CONDITIONAL", "acts_on": ACTS_ON, "principal_symbol": PRINCIPAL_SYMBOL, "weyl_3d": universal_weyl_3d_density(), "berger_hodge_relation": candidate["berger_hodge_relation"], "claim_boundary": "The principal symbol supports conditional Weyl asymptotics but does not determine the full operator."},
        "frame_normalized_principal_residue": {"artifact": "BHSM_frame_normalized_principal_residue_v4_6", "status": "FRAME_NORMALIZED_PRINCIPAL_RESIDUE_CONDITIONAL", "frame_normalization": {"raw_frame_count": FRAME_COUNT, "tau_frame": "1/3", "effective_frame_factor": 1}, "residue_table": frame_normalized_principal_residue_table(), "claim_boundary": "The primitive frame state prevents candidate overcounting but does not close action-selected frame averaging."},
        "gauge_fixed_domain_gate": {"artifact": "BHSM_gauge_fixed_domain_gate_v4_6", "status": "OPEN_MISSING_GAUGE_FIXED_BOUNDARY_DOMAIN", "admissible_domain_candidates": ["gauge-fixed", "transverse/coexact", "quotient by exact gauge directions", "otherwise physically admissible boundary fluctuation space"], "unrestricted_domain_solved": False, "claim_boundary": "The operator class is not a final physical operator on unrestricted gauge potentials."},
        "lower_order_operator_terms_gate": {"artifact": "BHSM_lower_order_operator_terms_gate_v4_6", "status": "OPEN_MISSING_LOWER_ORDER_BOUNDARY_OPERATOR_TERMS", "candidate_terms": list(LOWER_ORDER_TERMS), "principal_symbol_determines_full_operator": False, "claim_boundary": "Berger/Hodge compatibility fixes the leading class only; lower-order geometry and action sources remain open."},
        "open_gates": {"artifact": "BHSM_v4_6_open_gates", "status": "FULL_BHSM_NOT_COMPLETE", "statuses": status_table(), "claim_boundary": "No physical coupling, running law, CKM value or exponent, or full-BHSM result is promoted."},
    }
    for payload in payloads.values():
        payload.update(deepcopy(common))
    return payloads
