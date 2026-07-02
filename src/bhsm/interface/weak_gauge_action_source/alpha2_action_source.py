"""Audit registered and action provenance for alpha2_BH."""

from .common import STATUS_ALPHA2_REGISTERED, input_guard


def audit_alpha2_bh_action_source() -> dict[str, object]:
    return {
        "symbol": "alpha2_BH",
        "registered_value_if_present": "2/(6*pi^2)",
        "registry_source": "src/gauge_couplings.py",
        "action_source": None,
        "relation_to_g2": "conditional convention alpha2_BH=g2_BH^2/(4*pi)",
        "is_action_derived": False,
        "is_registered": True,
        "is_reference_or_fitted": False,
        "evidence_for": ["alpha_2 is registered as a geometric gauge screen"],
        "evidence_against": ["no weak gauge action derives the registered value"],
        "status": STATUS_ALPHA2_REGISTERED,
        "action_derivation_status": "OPEN_MISSING_ALPHA2_BH_ACTION_SOURCE",
        "claim_boundary": "alpha2_BH remains registered unless the action fixes it.",
        **input_guard(),
    }
