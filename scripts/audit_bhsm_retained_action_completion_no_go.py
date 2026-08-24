"""Materialize the canonical completion no-go for the unchanged action."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FLAGSHIP = ROOT / "artifacts/flagship_integration"
DEFINITION = ROOT / "docs/BHSM_1_0_DEFINITION_OF_DONE.md"
RECONCILIATION = ROOT / "artifacts/BHSM_historical_action_reconciliation_v7_0.json"
BOUNDARY = ROOT / "artifacts/BHSM_aether_boundary_identity_ejection_v15_13.json"
DOMAIN = FLAGSHIP / "BHSM_N12_FORWARD_MATTER_DOMAIN_NO_GO.json"
GRADED = FLAGSHIP / "BHSM_N12_FORWARD_GRADED_PHASE_INDEPENDENCE_NO_GO.json"
RESULT = FLAGSHIP / "BHSM_RETAINED_ACTION_COMPLETION_NO_GO.json"
INPUTS = (DEFINITION, RECONCILIATION, BOUNDARY, DOMAIN, GRADED)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite completion no-go value")
        return value
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all retained-action completion inputs are required")
    definition = DEFINITION.read_text(encoding="utf-8")
    reconciliation, boundary, domain, graded = (
        json.loads(path.read_text(encoding="utf-8")) for path in INPUTS[1:]
    )
    for record in (boundary, domain, graded):
        if record.get("validation_passed") is not True:
            raise RuntimeError("validated retained-action no-go inputs required")

    matter_row = next(
        row for row in reconciliation["architectures"]
        if row["architecture"] == "v6.7 boundary matter action"
    )
    identity = boundary["boundary_identity_and_transport"]
    validation = {
        "definition_of_done_requires_complete_variational_domains": (
            "complete configurations and variational domains" in definition
        ),
        "matter_action_is_only_conditional_effective": (
            matter_row["status"] == "CONDITIONAL_EFFECTIVE_ACTION"
        ),
        "unique_self_adjoint_domain_claim_was_retired": (
            "unique self-adjoint domain claim" in matter_row["retired"]
        ),
        "retained_matter_junction_action_is_zero": identity[
            "existing_matter_junction_action"
        ] == 0,
        "continuous_physical_domain_family_survives": (
            identity["continuous_ambiguity_remains"]
            and identity["surviving_domain_witness"][
                "remaining_family_continuous"
            ]
        ),
        "allowed_domains_have_inequivalent_spectra": identity[
            "surviving_domain_witness"
        ]["inequivalent_endpoint_spectra_remain"],
        "native_compact_source_resolvent_separates_domains": domain[
            "exact_resolvent_separation"
        ]["nonzero"],
        "universal_graded_phase_identity_is_invalidated": not graded[
            "adjudication"
        ]["universal_Ward_BRST_phase_independence_identity"],
        "no_action_term_domain_phase_selector_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_RETAINED_ACTION_COMPLETION_NO_GO",
        "status": "TERMINAL_CANONICAL_NO_GO_FOR_UNCHANGED_RETAINED_ACTION",
        "campaign_terminal_condition": 2,
        "classification": (
            "BHSM_TIER_A_REQUIRES_COMPLETE_CONFIGURATIONS_AND_VARIATIONAL_"
            "DOMAINS,_BUT_THE_RECONCILED_RETAINED_MATTER_ACTION_IS_ONLY_"
            "CONDITIONAL_EFFECTIVE_AND_EXPLICITLY_RETIRES_A_UNIQUE_SELF_"
            "ADJOINT_DOMAIN_CLAIM._THE_RETAINED_JUNCTION_ACTION_IS_ZERO,_"
            "A_CONTINUOUS_U1_PARENT_TIMES_U1_CHILD_DOMAIN_FAMILY_SURVIVES,_"
            "ITS_RESOLVENTS_ARE_DISTINCT,_AND_UNIVERSAL_WARD_BRST_PHASE_"
            "INDEPENDENCE_IS_FALSE._THEREFORE_THE_UNCHANGED_RETAINED_ACTION_"
            "CANNOT_SATISFY_A_NECESSARY_INTERNAL_COMPLETION_CONDITION"
        ),
        "necessary_internal_condition": {
            "source": "docs/BHSM_1_0_DEFINITION_OF_DONE.md",
            "tier": "TIER_A_BHSM_CORE_COMPLETE",
            "requirement": "COMPLETE_CONFIGURATIONS_AND_VARIATIONAL_DOMAINS",
            "classification": "INTERNAL_CONSISTENCY_REQUIRED",
            "observable_cancellation_can_waive_requirement": False,
        },
        "retained_action_failure_chain": [
            {
                "step": 1,
                "fact": "V6_7_MATTER_ACTION_IS_CONDITIONAL_EFFECTIVE",
                "evidence": matter_row,
            },
            {
                "step": 2,
                "fact": "UNIQUE_SELF_ADJOINT_DOMAIN_CLAIM_RETIRED",
                "evidence": matter_row["retired"],
            },
            {
                "step": 3,
                "fact": "NORMAL_MATTER_JUNCTION_ACTION_IS_ZERO",
                "evidence": identity["existing_matter_junction_action"],
            },
            {
                "step": 4,
                "fact": "CONTINUOUS_IDENTITY_PRESERVING_DOMAIN_FAMILY_SURVIVES",
                "evidence": identity["surviving_domain_witness"][
                    "boundary_identity_allowed_group"
                ],
            },
            {
                "step": 5,
                "fact": "THE_ALLOWED_DOMAINS_DEFINE_DISTINCT_RESOLVENTS",
                "evidence": domain["exact_resolvent_separation"][
                    "compact_source_resolvent_difference"
                ],
            },
            {
                "step": 6,
                "fact": "WARD_BRST_IS_NOT_A_UNIVERSAL_PHASE_INDEPENDENCE_IDENTITY",
                "evidence": graded[
                    "graded_heat_integrand_phase_difference"
                ]["strict_lower"],
            },
        ],
        "theorem": {
            "statement": (
                "NO_DETERMINISTIC_COMPLETION_GATE_FOR_THE_UNCHANGED_RETAINED_"
                "ACTION_CAN_SET_FULL_BHSM_COMPLETE_TRUE_WHILE_THE_REQUIRED_"
                "PHYSICAL_VARIATIONAL_DOMAIN_REMAINS_A_CONTINUOUS_"
                "ACTION_UNSELECTED_FAMILY"
            ),
            "proof_type": (
                "REPOSITORY_NATIVE_DEFINITION_OF_DONE_PLUS_ACTION_PROVENANCE_"
                "PLUS_EXACT_SELF_ADJOINT_DOMAIN_AND_RESOLVENT_SEPARATION"
            ),
            "not_merely": [
                "FAILED_NUMERICAL_CERTIFICATE",
                "MISSING_COEFFICIENT_ORACLE",
                "FAILED_REPRESENTATION",
                "STALE_GATE_INTERPRETATION",
                "UNPROVED_TERMINAL_REACHABILITY",
            ],
        },
        "terminal_adjudication": {
            "Gate_7": "CANNOT_CLOSE_FROM_UNCHANGED_RETAINED_ACTION",
            "Gate_8": "LOCKED",
            "zero_source_force": "NOT_UNIQUELY_DEFINED_ON_ONE_ACTION_OWNED_DOMAIN",
            "same_action_saddle": "NOT_EVALUABLE",
            "pair_plus_contact_Hessian": "NOT_EVALUABLE",
            "FULL_BHSM_COMPLETE": False,
            "canonical_no_go_earned": True,
        },
        "future_scope": {
            "no_go_for_all_possible_BHSM_action_extensions": False,
            "explicitly_versioned_normal_matter_boundary_action_could_change_result": True,
            "declaring_one_phase_without_action_derivation_is_allowed": False,
            "choosing_a_phase_would_select_between_inequivalent_physical_theories": True,
            "owner_policy_may_invent_the_missing_mathematics": False,
            "future_action_extension_requires_explicit_physical_authorization": True,
        },
        "claim_boundary": {
            "FULL_BHSM_COMPLETE_set_true": False,
            "Gate_7_falsely_closed": False,
            "new_action_term_added": False,
            "phase_selected": False,
            "frozen_predictions_changed": False,
            "new_physics_added": False,
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def materialize() -> Path:
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(_canonical(build_payload()), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return RESULT


if __name__ == "__main__":
    print(materialize())
