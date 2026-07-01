"""Shared contracts for the normalized-action adjoint-pair CKM audit."""

from __future__ import annotations

from pathlib import Path


S_LEPTON = 1
S_UP = 2
S_DOWN = 4

STATUS_OPEN_SELECTION = "OPEN_MISSING_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION"
STATUS_CONDITIONAL_SELECTION = "CONDITIONAL_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION"
STATUS_ARTIFACT_SELECTION = "ARTIFACT_BACKED_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION"

STATUS_OPEN_HERMITIAN = "OPEN_MISSING_HERMITIAN_CHARGED_CURRENT_ACTION_RULE"
STATUS_CONDITIONAL_HERMITIAN = "CONDITIONAL_HERMITIAN_CHARGED_CURRENT_ACTION_RULE"
STATUS_ARTIFACT_HERMITIAN = "ARTIFACT_BACKED_HERMITIAN_CHARGED_CURRENT_ACTION_RULE"

STATUS_OPEN_TRANSPORT = "OPEN_MISSING_CKM_TRANSPORT_SPACE_THEOREM"
STATUS_CONDITIONAL_TRANSPORT = "CONDITIONAL_CKM_TRANSPORT_SPACE_THEOREM"
STATUS_ARTIFACT_TRANSPORT = "ARTIFACT_BACKED_CKM_TRANSPORT_SPACE_THEOREM"

STATUS_OPEN_LOG_APPLICATION = "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM"
STATUS_CONDITIONAL_LOG_APPLICATION = "CONDITIONAL_CKM_LOG_TRANSPORT_APPLICATION"
STATUS_ARTIFACT_LOG_APPLICATION = "ARTIFACT_BACKED_CKM_LOG_TRANSPORT_APPLICATION"

STATUS_COMPETING_ASSIGNMENTS = "MULTIPLE_COMPETING_CHANNEL_ASSIGNMENTS"
STATUS_RETIRED_MAXIMAL = "RETIRED_MAXIMAL_SELF_RESPONSE_AS_PRIMARY_CKM_SOURCE"
STATUS_REJECTED_OVERCLAIM = "REJECTED_ACTION_SELECTION_OVERCLAIM"

FORBIDDEN_INPUTS = (
    "empirical CKM fitting",
    "PDG/reference values",
    "W calibration",
    "charged-mass fitting",
    "neutrino limits",
    "legacy threshold tables",
)

REQUIRED_BOUNDARY_STATEMENTS = (
    "The existence of a Hermitian-conjugate charged-current term does not by itself derive the CKM exponent.",
    "The CKM exponent remains open unless BHSM proves that CKM transport acts on the normalized Hermitian adjoint-pair charged-current space.",
    "The bidirectional adjoint-pair channel count is 16, but this is a conditional channel assignment until selected by the normalized action.",
    "The maximal self-response channel also has dimension 16, but it is retired as the primary CKM source unless action evidence revives it.",
    "No empirical CKM fitting, charged-mass fitting, PDG values, W calibration, neutrino limits, or legacy threshold tables are used as theorem inputs.",
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def channel_dimensions() -> dict[str, int]:
    return {
        "s_l": S_LEPTON,
        "s_u": S_UP,
        "s_d": S_DOWN,
        "one_way_up_down": S_UP * S_DOWN,
        "one_way_down_up": S_DOWN * S_UP,
        "bidirectional_adjoint_pair": 2 * S_UP * S_DOWN,
        "maximal_self_response": S_DOWN**2,
        "sector_self_response_sum": S_LEPTON**2 + S_UP**2 + S_DOWN**2,
        "total_charged_endomorphism": (S_LEPTON + S_UP + S_DOWN) ** 2,
    }


def input_guard() -> dict[str, object]:
    return {
        "empirical_inputs_used": False,
        "pdg_reference_values_used": False,
        "w_calibration_used": False,
        "charged_mass_fitting_used": False,
        "ckm_fitting_used": False,
        "neutrino_limits_used": False,
        "legacy_threshold_tables_used": False,
        "forbidden_theorem_inputs": list(FORBIDDEN_INPUTS),
        "forbidden_theorem_inputs_used": [],
        "frozen_predictions_modified": False,
        "official_prediction_logic_modified": False,
        "physics_validation_claimed": False,
        "detector_reconstruction_claimed": False,
        "cms_cern_endorsement_claimed": False,
    }

