"""BHSM v11.6 parent-action spectral-current provenance gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bhsm.interface.envelopment.relational_axioms import deterministic_json

from .ckm_action_equivalence_v11_6 import equivalence_payload
from .completion_gate_v11_5 import completion_payload as v11_5_payload
from .parent_action_charged_current_v11_6 import (
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    current_reduction_payload,
    parent_action_term_ledger,
)
from .spectral_current_uniqueness_v11_6 import uniqueness_payload


VERSION = "v11.6"
ARTIFACT_FILES = {
    "parent_action_charged_current": "BHSM_parent_action_charged_current_v11_6.json",
    "parent_action_current_reduction": "BHSM_parent_action_current_reduction_v11_6.json",
    "spectral_current_uniqueness": "BHSM_spectral_current_uniqueness_v11_6.json",
    "ckm_action_equivalence": "BHSM_CKM_action_equivalence_v11_6.json",
    "completion_gate": "BHSM_completion_gate_v11_6.json",
}


def completion_payload() -> dict[str, Any]:
    prior = v11_5_payload()
    ledger = parent_action_term_ledger()
    reduction = current_reduction_payload()
    uniqueness = uniqueness_payload()
    equivalence = equivalence_payload()
    validation = {
        "v11_5_recovery_point_valid": prior["validation_passed"],
        "parent_action_sources_traced": ledger["validation_passed"],
        "mixed_variation_reduced": reduction["validation_passed"],
        "live_action_current_is_family_universal": reduction["validation"]["action_kernel_is_I3"],
        "v11_5_not_action_equivalent": equivalence["validation_passed"],
        "viability_axioms_not_unique": uniqueness["validation_passed"] and not uniqueness["uniqueness_established"],
        "narrower_missing_action_object_identified": bool(EXACT_NEXT_OBJECT),
        "v11_5_candidate_not_promoted": True,
        "nontrivial_CKM_not_unconditionally_closed": True,
        "flavor_action_not_unconditionally_closed": True,
        "downstream_tests_do_not_replace_provenance": True,
        "frozen_predictions_unchanged": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v11_6",
        "version": VERSION,
        "classification": "TESTED_PARENT_ACTION_REDUCTION_AND_UNIQUENESS_NO_GO",
        "v11_5_recovery_point": prior,
        "parent_action_charged_current": ledger,
        "parent_action_current_reduction": reduction,
        "spectral_current_uniqueness": uniqueness,
        "ckm_action_equivalence": equivalence,
        "Mark_I": "REACHED",
        "Mark_II": "REACHED_ON_SELECTED_FINITE_RADIUS_CORE_BRANCH",
        "Mark_III": "NOT_REACHED",
        "Mark_IV": "NOT_REACHED",
        "BHSM_1_0_release_complete": False,
        "validated_in_v11_6": [
            "the live effective-action SU2L Dirac current reduces to family kernel I3",
            "the v11.5 spectral kernel is not equivalent to that current under physical quark rephasings",
            "full rank, unitarity, SU2 closure, neutral-current centrality, and nonzero CP leave a continuous kernel family",
            "joint functional calculus of the commuting v11.4 response pair remains diagonal",
            "the missing data are common-domain family wavefunctions, their action-owned relative orientation, and the current pairing map",
        ],
        "invalidated_in_v11_6": [
            "mathematical viability of the v11.5 kernel implies action ownership",
            "SU2 closure uniquely selects a 3x3 family kernel",
            "the polar functor selects a raw kernel before that raw kernel is action-derived",
            "commuting up/down scalar spectral weights alone generate nontrivial CKM mixing",
        ],
        "open": [
            EXACT_NEXT_OBJECT,
            "Mark III gauge-dressed orbit/current, stability, hadron, neutrino-current, unit-bridge, and canonical-normalization objects",
            "Mark IV finite empirical replacement tests after Mark III",
        ],
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "previous_exact_object": "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_CHARGED_CURRENT_KERNEL",
        "previous_object_resolution": "ATTACKED_BOTH_ROUTES_AND_REPLACED_BY_A_MORE_PRECISE_ACTION_LEVEL_MISSING_OBJECT",
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "physical_CKM_derived": False,
        "flavor_action_unconditionally_closed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    gate = completion_payload()
    return {
        "parent_action_charged_current": gate["parent_action_charged_current"],
        "parent_action_current_reduction": gate["parent_action_current_reduction"],
        "spectral_current_uniqueness": gate["spectral_current_uniqueness"],
        "ckm_action_equivalence": gate["ckm_action_equivalence"],
        "completion_gate": gate,
    }


def canonical_completion_gate_payload() -> dict[str, Any]:
    from .completion_gate_v11_5 import canonical_completion_gate_payload as prior_gate

    gate = prior_gate()
    payload = completion_payload()
    gate.update(
        {
            "version": VERSION,
            "sprint": "bhsm-parent-action-spectral-current-v11-6",
            "current_verdict": PRIMARY_VERDICT,
            "next_highest_upstream_blocker": EXACT_NEXT_OBJECT,
            "parent_action_charged_current_mixed_variation_evaluated": True,
            "parent_action_current_family_kernel": "I3",
            "v11_5_kernel_equivalent_to_action_current": False,
            "spectral_kernel_uniqueness_theorem_established": False,
            "residual_continuous_equivariant_kernel_family_proved": True,
            "spectral_charged_current_kernel_action_derived": False,
            "spectral_charged_current_kernel_provenance_gate_satisfied": False,
            "Mark_III": payload["Mark_III"],
            "Mark_IV": payload["Mark_IV"],
            "BHSM_1_0_release_complete": False,
            "frozen_predictions_changed": False,
            "validation_passed": payload["validation_passed"],
        }
    )
    gate["RB15"] = {
        "status": "COMMON_DOMAIN_FAMILY_WAVEFUNCTION_AND_CURRENT_MAP_OPEN",
        "resolution": EXACT_NEXT_OBJECT,
    }
    gate["RB16"] = {
        "status": "DOWNSTREAM_CONDITIONAL_EVALUATIONS_OPEN",
        "resolution": "RG transport, normalization, and empirical replacement cannot resolve RB15",
    }
    return gate


def materialize(repository: Path | None = None) -> list[Path]:
    root = Path(__file__).resolve().parents[4] if repository is None else Path(repository)
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for key, payload in artifact_payloads().items():
        path = target / ARTIFACT_FILES[key]
        path.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
        paths.append(path)
    canonical = target / "BHSM_1_0_completion_gate.json"
    canonical.write_text(deterministic_json(canonical_completion_gate_payload()), encoding="utf-8", newline="\n")
    paths.append(canonical)
    from bhsm.interface.current_program_status import status_payload

    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    status = docs / "current_bhsm_status.json"
    status.write_text(deterministic_json(status_payload()), encoding="utf-8", newline="\n")
    paths.append(status)
    return paths
