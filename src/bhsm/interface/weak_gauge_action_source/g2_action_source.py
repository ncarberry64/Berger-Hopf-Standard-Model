"""Audit runtime and action provenance for g2_BH."""

from .common import STATUS_G2_RUNTIME, input_guard


def audit_g2_bh_action_source() -> dict[str, object]:
    return {
        "symbol": "g2_BH",
        "runtime_source": "artifacts/BHSM_minimal_runtime_parameter_requirements_v1_2.json",
        "registry_source": "artifacts/BHSM_candidate_parameter_card_v0_5.json",
        "action_source": None,
        "normalized_gauge_action_source": "conditional skeleton with unfixed k",
        "trace_or_measure_source": "conditional relative trace and symbolic measure only",
        "is_action_derived": False,
        "is_runtime_input": True,
        "evidence_for": ["g2_BH_runtime is explicitly required by collider-interface artifacts"],
        "evidence_against": ["no normalized weak action fixes the value"],
        "status": STATUS_G2_RUNTIME,
        "action_derivation_status": "OPEN_MISSING_G2_BH_ACTION_SOURCE",
        "claim_boundary": "g2_BH remains runtime/input unless the action fixes it.",
        **input_guard(),
    }
