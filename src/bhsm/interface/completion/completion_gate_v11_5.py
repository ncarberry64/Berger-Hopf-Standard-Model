"""BHSM v11.5 flavor-action assembly gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bhsm.interface.envelopment.relational_axioms import deterministic_json

from .completion_gate_v11_4 import completion_payload as v11_4_payload
from .spectral_charged_current_v11_5 import current_payload


VERSION = "v11.5"
PRIMARY_VERDICT = "BHSM_FLAVOR_ACTION_CANDIDATES_ASSEMBLED_WITH_CHARGED_CURRENT_PROVENANCE_GATE_OPEN"
EXACT_NEXT_OBJECT = "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_CHARGED_CURRENT_KERNEL"
ARTIFACT_FILES = {
    "spectral_charged_current": "BHSM_spectral_charged_current_v11_5.json",
    "completion_gate": "BHSM_completion_gate_v11_5.json",
}


def completion_payload() -> dict[str, Any]:
    prior = v11_4_payload()
    current = current_payload()
    validation = {
        "v11_4_assembly_valid": prior["validation_passed"],
        "spectral_current_valid": current["validation_passed"],
        "nontrivial_CKM_kernel_present": current["determinant_modulus"] > 0,
        "CP_orientation_present": abs(current["jarlskog"]) > 0,
        "SU2_closed": current["validation"]["SU2_algebra_closed"],
        "no_measured_CKM_input": current["validation"]["no_measured_CKM_input"],
        "author_selected_candidate_boundary_exposed": current["action_derived"] is False,
        "provenance_gate_open": current["provenance_gate_satisfied"] is False,
        "downstream_tests_do_not_replace_provenance": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v11_5",
        "version": VERSION,
        "classification": "EXECUTABLE_FLAVOR_ACTION_CANDIDATES_WITH_UPSTREAM_PROVENANCE_GATE_OPEN",
        "v11_4": prior,
        "spectral_charged_current": current,
        "Mark_I": "REACHED",
        "Mark_II": "REACHED_ON_SELECTED_FINITE_RADIUS_CORE_BRANCH",
        "Mark_III": "NOT_REACHED",
        "Mark_IV": "NOT_REACHED",
        "BHSM_1_0_release_complete": False,
        "validated_in_v11_5": [
            "full-rank author-selected no-fit K_ud candidate",
            "unitarity of the CKM candidate",
            "nonzero candidate CP invariant",
            "exact SU2 algebra for the declared candidate kernel",
            "family-central neutral current for the declared candidate kernel",
        ],
        "open": [
            EXACT_NEXT_OBJECT,
            "explicit parent-action mixed second variation/current pairing or a BHSM-axiom uniqueness theorem",
            "sector-wide up/down absolute normalization",
            "common-scheme RG transport and finite empirical replacement tests as downstream conditional evaluations",
            "neutrino/PMNS extension outside the minimal Standard Model core",
            "full release synchronization after finite empirical audit",
        ],
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def canonical_completion_gate_payload() -> dict[str, Any]:
    from .mark_ii_gate_v11_3 import canonical_completion_gate_payload as prior_gate

    gate = prior_gate()
    payload = completion_payload()
    gate.update({
        "version": VERSION,
        "sprint": "bhsm-spectral-charged-current-provenance-gate-v11-5",
        "current_verdict": PRIMARY_VERDICT,
        "next_highest_upstream_blocker": EXACT_NEXT_OBJECT,
        "physical_three_mode_Hessian_complete": True,
        "minimal_M4_charged_lepton_action_complete_conditionally": True,
        "up_down_spectral_yukawa_pair_complete_conditionally": True,
        "full_rank_spectral_charged_current_kernel_mathematically_viable_candidate": True,
        "spectral_charged_current_kernel_action_derived": False,
        "spectral_charged_current_kernel_provenance_gate_satisfied": False,
        "Mark_II": payload["Mark_II"],
        "Mark_III": payload["Mark_III"],
        "Mark_IV": payload["Mark_IV"],
        "BHSM_1_0_release_complete": False,
        "frozen_predictions_changed": False,
        "validation_passed": payload["validation_passed"],
    })
    gate["RB15"] = {"status": "CHARGED_CURRENT_PARENT_ACTION_PROVENANCE_OPEN", "resolution": EXACT_NEXT_OBJECT}
    gate["RB16"] = {"status": "DOWNSTREAM_CONDITIONAL_EVALUATIONS_OPEN", "resolution": "RG transport, normalization, and empirical tests cannot resolve RB15"}
    return gate


def materialize(repository: Path | None = None) -> list[Path]:
    root = Path(__file__).resolve().parents[4] if repository is None else Path(repository)
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payload = completion_payload()
    records = {
        "spectral_charged_current": payload["spectral_charged_current"],
        "completion_gate": payload,
    }
    paths = []
    for key, record in records.items():
        path = target / ARTIFACT_FILES[key]
        path.write_text(deterministic_json(record), encoding="utf-8", newline="\n")
        paths.append(path)
    canonical = target / "BHSM_1_0_completion_gate.json"
    canonical.write_text(deterministic_json(canonical_completion_gate_payload()), encoding="utf-8", newline="\n")
    paths.append(canonical)
    from bhsm.interface.current_program_status import status_payload

    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    status = docs / "current_bhsm_status.json"
    status.write_text(deterministic_json(status_payload()), encoding="utf-8", newline="\n")
    return paths
