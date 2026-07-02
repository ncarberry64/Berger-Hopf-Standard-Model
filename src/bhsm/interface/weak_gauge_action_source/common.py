"""Shared contracts for the v3.0 weak gauge action source audit."""

from bhsm.interface.charged_current_action.common import input_guard, repository_root

STATUS_ALGEBRA = "CONDITIONAL_WEAK_GAUGE_ALGEBRA_SOURCE"
STATUS_SKELETON = "CONDITIONAL_NORMALIZED_WEAK_GAUGE_ACTION_SKELETON"
STATUS_TRACE = "CONDITIONAL_WEAK_GAUGE_TRACE_NORMALIZATION"
STATUS_G2_RUNTIME = "ARTIFACT_BACKED_G2_BH_RUNTIME_INPUT"
STATUS_ALPHA2_REGISTERED = "ARTIFACT_BACKED_ALPHA2_BH_REGISTERED_COUPLING"
STATUS_CONVENTION = "CONDITIONAL_WEAK_COUPLING_CONVENTION"
STATUS_COEFFICIENT = "OPEN_MISSING_NORMALIZED_WEAK_GAUGE_ACTION_COEFFICIENT"
STATUS_CKM_VALUE = "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE"

REQUIRED_STATEMENTS = (
    "A weak gauge algebra source does not derive the coupling value.",
    "A gauge action skeleton does not derive g2_BH unless it fixes the coefficient.",
    "Trace/generator normalization may fix conventions without fixing the physical coupling.",
    "g2_BH remains runtime/input unless the action fixes it.",
    "alpha2_BH remains registered unless the action fixes it.",
    "The CKM coefficient form is artifact-backed, but the coefficient value remains open.",
    "The CKM exponent remains not derived.",
)

REJECTED_CLAIMS = (
    "REJECTED_RUNTIME_INPUT_AS_ACTION_DERIVATION",
    "REJECTED_ALPHA2_REGISTRY_AS_ACTION_DERIVATION",
    "REJECTED_CONVENTION_AS_COUPLING_DERIVATION",
    "REJECTED_BRIDGE_ARITHMETIC_AS_GAUGE_COUPLING",
)
