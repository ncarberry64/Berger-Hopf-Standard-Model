"""Shared v2.8 contracts."""

from bhsm.interface.charged_current_action.common import channel_dimensions, input_guard, repository_root

STATUS_MEASURE = "CONDITIONAL_BOUNDARY_MEASURE_SOURCE"
STATUS_COEFFICIENT = "OPEN_MISSING_CKM_COEFFICIENT_NORMALIZATION"
STATUS_PAIR = "OPEN_MISSING_CKM_ACTION_MEASURE_COEFFICIENT_PAIR"
STATUS_ACTION = "OPEN_MISSING_NORMALIZED_CKM_ACTION_CANDIDATE"
STATUS_PROJECTOR = "OPEN_MISSING_PROJECTOR_SANDWICH_REQUIREMENT"
STATUS_PAIRED = "OPEN_MISSING_PAIRED_NORMALIZATION_RULE"
STATUS_TRANSPORT = "OPEN_MISSING_CKM_TRANSPORT_SPACE_SELECTION"
STATUS_IDENTIFICATION = "OPEN_MISSING_CKM_IDENTIFICATION_THEOREM"
CANDIDATE_FORM = "S_CKM = C_CKM integral_boundary dmu_B [psi_d^dagger Pi_d J_du Pi_u psi_u + psi_u^dagger Pi_u J_ud Pi_d psi_d]"
REQUIRED_STATEMENTS = (
    "L_CKM_charged_current_bounded is artifact-backed as a bounded interface term, but it is not a normalized action term unless measure, coefficient, projectors, paired normalization, and variational provenance are all supplied.",
    "A boundary measure alone does not select the CKM transport space.",
    "A coefficient normalization alone does not derive the CKM exponent.",
    "The CKM exponent remains not derived unless a normalized action-selected CKM transport space is proven and the CKM identification theorem closes.",
    "No empirical CKM fitting, charged-mass fitting, PDG values, W calibration, neutrino limits, or legacy threshold tables are used as theorem inputs.",
)
