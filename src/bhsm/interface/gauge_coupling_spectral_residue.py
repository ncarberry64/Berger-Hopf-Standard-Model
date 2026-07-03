"""Conservative v4.5 Casimir-shell spectral-residue candidates."""

from __future__ import annotations

import math
from copy import deepcopy

GAUGE_ADJOINT_DIMS = {"U1": 1, "SU2": 3, "SU3": 8}
CASIMIR_SHELL_RESIDUES = {"U1": 1, "SU2": 2, "SU3": 7}
TAU_FRAME_CANDIDATE = 1.0 / 3.0

OPEN_GATES = (
    "OPEN_MISSING_CASIMIR_SHELL_ACTION_ATTACHMENT",
    "OPEN_MISSING_SECTOR_BOUNDARY_OPERATOR_L_i",
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
)

INVALIDATIONS = (
    "Direct classical Yang-Mills density alone does not derive w=(1,2,7); it sees the radial norm R_i^2, not the angular dimension dim(g_i)-1.",
    "Raw Green covariance of A_i does not scale as Weyl mode counting; the density belongs to whitened modes B_i=L_i^(1/2)A_i.",
    "A fixed rank-7 SU(3) subalgebra or projector is not the primitive object; the candidate is the field-dependent tangent residue of the adjoint Casimir shell.",
    "Leading Weyl density alone does not produce physical running; Z_i, lower spectral corrections, and an action-selected rho_i(mu) remain open.",
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


def casimir_shell_residue(sector: str) -> int:
    """Return the candidate active residue, not a gauge-boson count."""
    return CASIMIR_SHELL_RESIDUES[sector]


def universal_weyl_3d_density() -> float:
    return 1.0 / (6.0 * math.pi**2)


def candidate_lambda_reference(sector: str) -> float:
    return casimir_shell_residue(sector) * universal_weyl_3d_density()


def candidate_residue_table() -> dict[str, dict[str, object]]:
    return {
        sector: {
            "gauge_algebra_dimension": GAUGE_ADJOINT_DIMS[sector],
            "candidate_active_residue": CASIMIR_SHELL_RESIDUES[sector],
            "is_gauge_boson_count": False,
            "candidate_lambda_reference": candidate_lambda_reference(sector),
        }
        for sector in GAUGE_ADJOINT_DIMS
    }


def frame_normalized_residue(raw_frame_count: int, tau_frame: float, active_residue: int) -> float:
    return raw_frame_count * tau_frame * active_residue


def status_table() -> dict[str, str]:
    return {
        "casimir_shell_residue": "CASIMIR_SHELL_RESIDUE_STRONG_CANDIDATE",
        "radial_angular_adjoint_split": "RADIAL_ANGULAR_ADJOINT_SPLIT_CONDITIONAL",
        "spectral_density_gauge_quantum": "SPECTRAL_DENSITY_GAUGE_QUANTUM_CONDITIONAL",
        "primitive_frame_trace": "CONDITIONAL_PRIMITIVE_FRAME_TRACE_NORMALIZATION",
        "action_frame_average": "OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION",
        "whitened_boundary_fluctuation": "WHITENED_BOUNDARY_FLUCTUATION_CONDITIONAL",
        "inverse_covariance_placement": "INVERSE_COVARIANCE_PLACEMENT_CONDITIONAL",
        "gauge_coupling_action_attachment": "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
        "full_completion": "FULL_BHSM_NOT_COMPLETE",
    }


def build_artifact_payloads() -> dict[str, dict[str, object]]:
    table = candidate_residue_table()
    common = {"open_gates": list(OPEN_GATES), "invalidations": list(INVALIDATIONS), **GUARDS}
    payloads = {
        "casimir_shell_residue": {
            "artifact_id": "BHSM_CASIMIR_SHELL_RESIDUE_V4_5",
            "status": "CASIMIR_SHELL_RESIDUE_STRONG_CANDIDATE",
            "radial_angular_split_status": "RADIAL_ANGULAR_ADJOINT_SPLIT_CONDITIONAL",
            "gauge_algebra_dimensions": dict(GAUGE_ADJOINT_DIMS),
            "candidate_active_residues": dict(CASIMIR_SHELL_RESIDUES),
            "residue_table": table,
            "candidate_derivation": {"U1": "retain sole abelian amplitude channel", "SU2": "dim(su(2))-1=2", "SU3": "dim(su(3))-1=7"},
            "claim_boundary": "The residues are coupling-normalization candidates, not gauge-boson counts or gauge-algebra dimensions, and remain action-gated.",
            "action_attachment_status": "OPEN_MISSING_CASIMIR_SHELL_ACTION_ATTACHMENT",
        },
        "spectral_density_gauge_quantum": {
            "artifact_id": "BHSM_SPECTRAL_DENSITY_GAUGE_QUANTUM_V4_5",
            "status": "SPECTRAL_DENSITY_GAUGE_QUANTUM_CONDITIONAL",
            "universal_weyl_3d_formula": "1/(6*pi^2)",
            "universal_weyl_3d_value": universal_weyl_3d_density(),
            "counting_law": "N_i(mu,rho) approximately w_i Vol(Sigma_rho) mu^3/(6*pi^2)",
            "normalized_density": "lambda_i=N_i/[Vol(Sigma_rho) mu^3] approximately w_i/(6*pi^2)",
            "candidate_lambda_reference": {sector: row["candidate_lambda_reference"] for sector, row in table.items()},
            "tau_frame_candidate": TAU_FRAME_CANDIDATE,
            "effective_frame_factor": 3 * TAU_FRAME_CANDIDATE,
            "frame_claim_boundary": "The primitive 1/3 trace prevents candidate channel overcounting but does not close action-selected frame averaging.",
            "claim_boundary": "Leading Weyl density is conditional and does not derive physical running or gauge couplings.",
        },
        "whitened_boundary_operator": {
            "artifact_id": "BHSM_WHITENED_BOUNDARY_OPERATOR_V4_5",
            "status": "WHITENED_BOUNDARY_FLUCTUATION_CONDITIONAL",
            "whitened_variable": "B_i=L_i(rho)^(1/2) A_i",
            "whitened_action": "S_i=[1/(2 lambda_i)] <B_i,B_i>",
            "equivalent_action": "S_i=[1/(2 lambda_i)] <A_i,L_i(rho)A_i>",
            "spectral_covariance": "lambda_i=[w_i/(6*pi^2)] Z_i(mu,rho_i(mu))",
            "reference_condition": "Z_i(mu0,rho0)=1",
            "claim_boundary": "Weyl density attaches to whitened active boundary modes, not the raw Green covariance of A_i.",
        },
        "inverse_covariance_placement": {
            "artifact_id": "BHSM_INVERSE_COVARIANCE_PLACEMENT_V4_5",
            "status": "INVERSE_COVARIANCE_PLACEMENT_CONDITIONAL",
            "covariance_candidate": "lambda_i proportional to w_i/(6*pi^2)",
            "kinetic_stiffness_candidate": "K_i proportional to 1/lambda_i",
            "coupling_candidate": "alpha_i proportional to lambda_i",
            "alpha_i_action_status": "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
            "is_action_derived": False,
            "claim_boundary": "Inverse-covariance placement and physical coupling identification require normalized-action attachment.",
        },
        "open_gates": {
            "artifact_id": "BHSM_OPEN_GATES_V4_5",
            "status": "FULL_BHSM_NOT_COMPLETE",
            "statuses": status_table(),
            "ckm_exponent_status": "CKM_EXPONENT_NOT_DERIVED",
            "claim_boundary": "No coupling, CKM coefficient, CKM exponent, or full-BHSM result is promoted by this candidate chain.",
        },
    }
    for payload in payloads.values():
        payload.update(deepcopy(common))
    return payloads
