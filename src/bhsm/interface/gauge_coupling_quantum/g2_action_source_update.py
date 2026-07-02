"""Propagate the v3.1 alpha2 audit to g2_BH."""

from .common import STATUS_G2, input_guard


def audit_g2_action_source_update() -> dict[str, object]:
    return {
        "alpha2_action_status": "OPEN_MISSING_ALPHA2_BH_ACTION_SOURCE",
        "weak_convention_status": "CONDITIONAL_WEAK_COUPLING_CONVENTION",
        "g2_action_status": STATUS_G2,
        "g2_runtime_status": "ARTIFACT_BACKED_G2_BH_RUNTIME_INPUT",
        "does_action_fix_g2": False,
        "blocking_conditions": [
            "alpha2_BH is not action-derived",
            "g2_BH^2/(4*pi)=alpha2_BH is a convention only",
            "normalized weak gauge-action coefficient remains open",
        ],
        "status": STATUS_G2,
        **input_guard(),
    }
