"""Materialize the fail-closed post-AE2 localization extension contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
TARGET = ARTIFACTS / (
    "action_extension/BHSM_POST_AE2_LOCALIZATION_CARRIER_EXTENSION_CONTRACT.json"
)
INPUTS = (
    ARTIFACTS
    / "flagship_integration/BHSM_N12_GATE7_LOCALIZATION_CARRIER_KILL_SCREEN.json",
    ARTIFACTS
    / "flagship_integration/BHSM_N12_GATE7_PHYSICAL_ENCAPSULATION_IDENTIFICATION_BRIDGE.json",
    ARTIFACTS / "action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    ARTIFACTS / "BHSM_primitive_support_character_ledger_v11_2.json",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    canonical = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(canonical).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    """Return the acceptance contract without selecting an extension."""

    missing = [path.as_posix() for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("extension-contract inputs required: " + ", ".join(missing))
    records = {path.name: _load(path) for path in INPUTS}
    kill_screen = records["BHSM_N12_GATE7_LOCALIZATION_CARRIER_KILL_SCREEN.json"]
    bridge = records[
        "BHSM_N12_GATE7_PHYSICAL_ENCAPSULATION_IDENTIFICATION_BRIDGE.json"
    ]
    reset = records["BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"]
    support = records["BHSM_primitive_support_character_ledger_v11_2.json"]

    acceptance_gates = [
        {
            "gate_id": "LEC_01",
            "requirement": "OWNER_AUTHORIZES_EXPLICIT_NEW_ACTION_VERSION",
            "status": "OPEN_OWNER_DECISION",
        },
        {
            "gate_id": "LEC_02",
            "requirement": "COVARIANT_LOCALIZATION_SCALAR_OR_DOMAIN_SELECTOR_IS_ACTION_OWNED",
            "status": "OPEN",
        },
        {
            "gate_id": "LEC_03",
            "requirement": "REGULAR_LEVEL_SET_OR_WELL_POSED_EMBEDDED_DOMAIN_AND_ORIENTATION",
            "status": "OPEN",
        },
        {
            "gate_id": "LEC_04",
            "requirement": "SAME_ACTION_VARIATION_DERIVES_INTERFACE_AND_JUNCTION_EQUATIONS",
            "status": "OPEN",
        },
        {
            "gate_id": "LEC_05",
            "requirement": "ACTION_SELECTS_ENCLOSURE_ROUTE_WITHOUT_MANUAL_ROUTE_CHOICE",
            "status": "OPEN",
        },
        {
            "gate_id": "LEC_06",
            "requirement": "ACTION_DEPENDENCY_CLOSURE_IS_TRANSPORTED_ON_THE_ENCLOSURE",
            "status": "OPEN",
        },
        {
            "gate_id": "LEC_07",
            "requirement": "EXISTING_AE2_RESET_TRACE_AND_FAMILY_PROJECTOR_INTERTWINER_ARE_PRESERVED",
            "status": "AVAILABLE_UPSTREAM_NOT_YET_ATTACHED",
        },
        {
            "gate_id": "LEC_08",
            "requirement": "FAMILY_MODE_SLOT_IS_INSTANTIATED_ON_THE_ACTUAL_C2_PARENT",
            "status": "OPEN",
        },
        {
            "gate_id": "LEC_09",
            "requirement": "CHILD_INHERITS_ENCLOSURE_AND_DEPENDENCY_CLOSED_BHSM_STATE",
            "status": "OPEN",
        },
        {
            "gate_id": "LEC_10",
            "requirement": "EXTENSION_REDUCES_TO_AE2_AWAY_FROM_THE_LOCALIZATION_SUPPORT",
            "status": "OPEN",
        },
        {
            "gate_id": "LEC_11",
            "requirement": "EVERY_NEW_COEFFICIENT_HAS_DIMENSIONAL_AND_NONFIT_PROVENANCE",
            "status": "OPEN_IF_ANY_COEFFICIENT_IS_PROPOSED",
        },
        {
            "gate_id": "LEC_12",
            "requirement": "FROZEN_PARTICLE_FAMILY_REPRESENTATION_PROJECTOR_CURRENT_AND_TOPOLOGY_ASSETS_REMAIN_UNCHANGED",
            "status": "REQUIRED",
        },
    ]

    validation = {
        "unchanged_ae2_carrier_absence_is_input": (
            kill_screen["carrier_audit"][
                "carrier_exists_in_audited_unchanged_ae2"
            ]
            is False
        ),
        "physical_bridge_remains_open": (
            bridge["bridge_evaluation"]["physical_encapsulation_identified"]
            is False
        ),
        "ae2_reset_is_reused": reset["validation_passed"] is True,
        "support_character_missing_object_is_preserved": (
            support["exact_next_object"]
            == "ACTION_OWNED_CORE_SURFACE_ATTACHMENT_TERM_FIXING_ATTACHMENT_CHARACTER_AND_EXCHANGE_CURRENT"
        ),
        "no_candidate_selected": True,
        "no_action_version_assigned": True,
        "no_equation_or_coefficient_added": True,
        "no_particle_spectrum_rebuilt": True,
    }

    return {
        "artifact": "BHSM_POST_AE2_LOCALIZATION_CARRIER_EXTENSION_CONTRACT",
        "schema_version": 1,
        "status": "ACCEPTANCE_CONTRACT_DEFINED__EXTENSION_NOT_AUTHORIZED_OR_INSTANTIATED",
        "current_action_version": "BHSM-AE-2.0.0",
        "proposed_action_version": None,
        "selected_localization_candidate": None,
        "selected_enclosure_route": None,
        "new_coefficients": [],
        "purpose": (
            "Define the minimum review and proof boundary for a future action-owned "
            "localization carrier without choosing or adding that carrier."
        ),
        "minimum_carrier_signature": {
            "domain_map": "D_A:z->(D_enc,Sigma_enc,X,n,K,...)",
            "scalar_option": "Sigma_enc={x:chi_A[Phi](x)=0}",
            "regularity": "dchi_A|Sigma_enc != 0_OR_EQUIVALENT_DOMAIN_WELL_POSEDNESS",
            "variation_owner": "delta_S_extension|Sigma_enc",
        },
        "acceptance_gates": acceptance_gates,
        "dependency_transport_rule": kill_screen["dependency_closure_rule"],
        "reusable_subclosures": {
            "fermionic_event_child_reset_trace": "AVAILABLE",
            "tensor_factor_family_projector_intertwiner": "AVAILABLE",
            "promotion_of_PEI_05_or_PEI_11": False,
        },
        "forbidden_shortcuts": [
            "RELABEL_LAMBDA24_ZERO_AS_SIGMA_ENC",
            "RELABEL_AE2_RESET_LOCUS_AS_A_NEW_SPACETIME_DOMAIN",
            "HAND_SELECT_LOCAL_SAME_SPACETIME_ENCLOSURE",
            "ASSUME_B1_OR_COLLAR_AS_ACTION_SELECTED",
            "FIT_A_LOCALIZATION_COEFFICIENT_TO_A_DESIRED_PARTICLE_OUTPUT",
            "REBUILD_OR_RETUNE_FROZEN_PARTICLE_ASSETS",
            "PROMOTE_THE_ALGEBRAIC_INTERTWINER_WITHOUT_ACTUAL_C2_INSTANTIATION",
        ],
        "authorization_boundary": {
            "contract_is_authorization": False,
            "extension_may_be_implemented_now": False,
            "owner_decision_required": True,
            "decision_must_identify": [
                "new action version",
                "carrier field or domain selector",
                "action term and coefficient provenance",
            ],
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET)


if __name__ == "__main__":
    main()
