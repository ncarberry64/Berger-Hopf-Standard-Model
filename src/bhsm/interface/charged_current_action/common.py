"""Shared contracts for the v2.6 charged-current action transport audit."""

from __future__ import annotations

from pathlib import Path


S_LEPTON = 1
S_UP = 2
S_DOWN = 4

STATUS_ARTIFACT_ACTION = "ARTIFACT_BACKED_NORMALIZED_CHARGED_CURRENT_ACTION_TERM"
STATUS_CONDITIONAL_ACTION = "CONDITIONAL_NORMALIZED_CHARGED_CURRENT_ACTION_TERM"
STATUS_OPEN_ACTION = "OPEN_MISSING_NORMALIZED_CHARGED_CURRENT_ACTION_TERM"

STATUS_ARTIFACT_SPACE = "ARTIFACT_BACKED_CHARGED_CURRENT_TRANSPORT_SPACE"
STATUS_CONDITIONAL_SPACE = "CONDITIONAL_CHARGED_CURRENT_TRANSPORT_SPACE"
STATUS_OPEN_SPACE = "OPEN_MISSING_CHARGED_CURRENT_TRANSPORT_SPACE"

STATUS_ARTIFACT_ADJOINT = "ARTIFACT_BACKED_HERMITIAN_ADJOINT_PAIR_TRANSPORT_SPACE"
STATUS_CONDITIONAL_ADJOINT = "CONDITIONAL_HERMITIAN_ADJOINT_PAIR_TRANSPORT_SPACE"
STATUS_OPEN_ADJOINT = "OPEN_MISSING_HERMITIAN_ADJOINT_PAIR_TRANSPORT_SPACE"

STATUS_ARTIFACT_CKM_SPACE = "ARTIFACT_BACKED_CKM_TRANSPORT_SPACE_THEOREM"
STATUS_CONDITIONAL_CKM_SPACE = "CONDITIONAL_CKM_TRANSPORT_SPACE_THEOREM"
STATUS_OPEN_CKM_SPACE = "OPEN_MISSING_CKM_TRANSPORT_SPACE_THEOREM"

STATUS_MULTIPLE_SPACES = "MULTIPLE_COMPETING_TRANSPORT_SPACES"
STATUS_REJECTED_OVERCLAIM = "REJECTED_TRANSPORT_SPACE_OVERCLAIM"
STATUS_RETIRED_MAXIMAL = "RETIRED_MAXIMAL_SELF_RESPONSE_AS_PRIMARY_CKM_SOURCE"

FORBIDDEN_INPUTS = (
    "empirical CKM fitting",
    "PDG/reference values",
    "W calibration",
    "charged-mass fitting",
    "neutrino limits",
    "legacy threshold tables",
)

REQUIRED_BOUNDARY_STATEMENTS = (
    "The normalized charged-current action term, not arithmetic channel-count coincidence, must select the CKM transport space.",
    "The Hermitian adjoint-pair channel count is 16, but the CKM exponent remains not derived unless BHSM proves CKM acts on that selected transport space.",
    "The existence of a Hermitian-conjugate term supports action reality but does not by itself derive CKM transport-space selection.",
    "Same numerical dimension does not establish the physical source.",
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
        "bidirectional_adjoint_pair": 2 * S_UP * S_DOWN,
        "sector_self_response_sum": S_LEPTON**2 + S_UP**2 + S_DOWN**2,
        "total_charged_endomorphism": (S_LEPTON + S_UP + S_DOWN) ** 2,
        "maximal_self_response": S_DOWN**2,
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
