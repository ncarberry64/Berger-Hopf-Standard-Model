"""Shared contracts for the v3.1 gauge-coupling quantum audit."""

from bhsm.interface.charged_current_action.common import input_guard, repository_root


STATUS_REGISTRY = "ARTIFACT_BACKED_GAUGE_COUPLING_REGISTRY_PATTERN"
STATUS_VOLUME = "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR"
STATUS_WEIGHTS = "CONDITIONAL_GAUGE_SECTOR_WEIGHT_SOURCE"
STATUS_QUANTUM = "OPEN_MISSING_UNIVERSAL_GAUGE_COUPLING_QUANTUM"
STATUS_ATTACHMENT = "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT"
STATUS_ALPHA_I = "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION"
STATUS_G2 = "OPEN_MISSING_G2_BH_ACTION_SOURCE"
STATUS_CKM = "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE"

REQUIRED_STATEMENTS = (
    "The pattern α_i = w_i/(6π²) is not an action derivation unless attached to the normalized gauge action.",
    "The identity 6π² = 3 Vol(S³) does not by itself derive the gauge couplings.",
    "Sector weights do not by themselves derive the gauge couplings.",
    "Registered coupling expressions are not action derivations.",
    "The overall gauge-action coefficient k remains open unless the action fixes it.",
    "The CKM coefficient value remains open unless g2_BH is action-derived.",
    "The CKM exponent remains not derived.",
)

REJECTED_CLAIMS = (
    "REJECTED_NUMERIC_PATTERN_AS_ACTION_DERIVATION",
    "REJECTED_REGISTRY_AS_ACTION_DERIVATION",
    "REJECTED_VOLUME_DENOMINATOR_ALONE_AS_COUPLING_DERIVATION",
    "REJECTED_SECTOR_WEIGHT_ALONE_AS_COUPLING_DERIVATION",
    "REJECTED_BRIDGE_ARITHMETIC_AS_GAUGE_COUPLING",
)
