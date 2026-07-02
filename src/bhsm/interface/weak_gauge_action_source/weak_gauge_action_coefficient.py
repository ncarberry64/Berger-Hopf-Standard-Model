"""Gate the overall normalized weak gauge-action coefficient."""

from .common import STATUS_ALGEBRA, STATUS_ALPHA2_REGISTERED, STATUS_COEFFICIENT, STATUS_G2_RUNTIME, STATUS_SKELETON, STATUS_TRACE, input_guard


def audit_normalized_weak_gauge_action_coefficient() -> dict[str, object]:
    return {
        "weak_algebra_status": STATUS_ALGEBRA,
        "action_skeleton_status": STATUS_SKELETON,
        "trace_normalization_status": STATUS_TRACE,
        "g2_action_status": STATUS_G2_RUNTIME,
        "g2_action_derivation_status": "OPEN_MISSING_G2_BH_ACTION_SOURCE",
        "alpha2_action_status": STATUS_ALPHA2_REGISTERED,
        "alpha2_action_derivation_status": "OPEN_MISSING_ALPHA2_BH_ACTION_SOURCE",
        "coefficient_formula": "k candidate proportional to 1/g2_BH^2",
        "coefficient_value_status": "open",
        "blocking_conditions": ["overall k not fixed", "k not identified with a derived g2_BH", "physical measure normalization open"],
        "status": STATUS_COEFFICIENT,
        "claim_boundary": "Relative trace normalization does not fix the overall physical weak coupling.",
        **input_guard(),
    }
