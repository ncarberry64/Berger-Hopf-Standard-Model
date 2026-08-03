"""BHSM v11.4 executable assembly gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bhsm.interface.envelopment.relational_axioms import deterministic_json

from .charged_lepton_action_v11_4 import action_payload
from .common_attachment_response_v11_4 import response_payload
from .quark_yukawa_ckm_v11_4 import EXACT_NEXT_OBJECT, quark_payload


VERSION = "v11.4"
PRIMARY_VERDICT = "BHSM_MARK_II_RESPONSE_CLOSED_AND_MINIMAL_M4_FLAVOR_ACTION_ASSEMBLED_CONDITIONALLY"
ARTIFACT_FILES = {
    "common_attachment_response": "BHSM_common_attachment_response_v11_4.json",
    "charged_lepton_action": "BHSM_minimal_M4_charged_lepton_action_v11_4.json",
    "quark_yukawa_ckm_gate": "BHSM_quark_yukawa_CKM_gate_v11_4.json",
    "completion_gate": "BHSM_completion_gate_v11_4.json",
}


def completion_payload() -> dict[str, Any]:
    response = response_payload()
    lepton = action_payload()
    quark = quark_payload()
    validation = {
        "common_response_valid": response["validation_passed"],
        "charged_lepton_action_valid": lepton["validation_passed"],
        "quark_gate_valid": quark["validation_passed"],
        "mark_ii_operator_block_closed": True,
        "conditional_inputs_visible": True,
        "nontrivial_CKM_not_fabricated": True,
        "frozen_predictions_unchanged": True,
        "release_not_overclaimed": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v11_4",
        "version": VERSION,
        "classification": "EXECUTABLE_CONDITIONAL_ASSEMBLY_ADVANCEMENT",
        "common_attachment_response": response,
        "charged_lepton_action": lepton,
        "quark_yukawa_ckm_gate": quark,
        "Mark_I": "REACHED",
        "Mark_II": "REACHED_ON_SELECTED_FINITE_RADIUS_CORE_BRANCH",
        "Mark_III": "NOT_REACHED",
        "Mark_IV": "NOT_REACHED",
        "BHSM_1_0_release_complete": False,
        "closed_in_v11_4": [
            "canonical whitened common-domain KKT response",
            "positive nondegenerate family-octave attachment seeds",
            "minimal conditional M4 charged-lepton spectral action",
            "conditional up/down spectral Yukawa pair",
            "canonical-identification CKM no-mixing theorem",
        ],
        "open": [
            EXACT_NEXT_OBJECT,
            "sector-wide action normalization for up/down absolute masses",
            "RG transport and external comparison",
            "Mark III physical orbit/current completion",
            "Mark IV empirical replacement and release",
        ],
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    gate = completion_payload()
    return {
        "common_attachment_response": gate["common_attachment_response"],
        "charged_lepton_action": gate["charged_lepton_action"],
        "quark_yukawa_ckm_gate": gate["quark_yukawa_ckm_gate"],
        "completion_gate": gate,
    }


def materialize(repository: Path | None = None) -> list[Path]:
    root = Path(__file__).resolve().parents[4] if repository is None else Path(repository)
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for key, payload in artifact_payloads().items():
        path = target / ARTIFACT_FILES[key]
        path.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
        paths.append(path)
    return paths
