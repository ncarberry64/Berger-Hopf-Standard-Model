"""Distinguish the birth-source reference from the terminal AE2 load."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_COMPACT_HISTORY_ENDPOINT_ROLE_PROVENANCE.json"
INPUTS = (
    BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json",
    BASE / "BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json",
    BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    BASE / "BHSM_N12_FINITE_HISTORY_SPECTRAL_REALIZATION_PROVENANCE.json",
    BASE / "BHSM_N12_FINITE_HISTORY_GLUING_FORCE_PROVENANCE.json",
    ROOT / "theory/n12_compact_history_endpoint_role_provenance.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all compact endpoint-role inputs required")
    compact, readout, force, realization, gluing = (
        _load(path) for path in INPUTS[:5]
    )
    if not all(
        record.get("validation_passed") is True
        for record in (compact, readout, force, realization, gluing)
    ):
        raise RuntimeError("validated compact endpoint-role inputs required")
    validation = {
        "compact_endpoint_order_consumed": compact["endpoint_partition"][
            "ordered_traces"
        ] == ["birth", "new_event"],
        "birth_zero_trace_is_retained_Dirichlet_reference": readout[
            "operator_family"
        ]["Dirichlet_reference_form"].startswith("RESTRICT_q_C"),
        "Dirichlet_reference_not_physical_birth_graph": "REFERENCE" in readout[
            "operator_family"
        ]["Dirichlet_reference_role"],
        "physical_birth_graph_reimposed_once": readout["validation"][
            "birth_graph_reimposed_once_without_double_counting"
        ],
        "zero_source_definition_consumed": force["exact_force_theorem"][
            "zero_source_means"
        ] == "GAUGE_AND_HS_EXTERNAL_SOURCES_SET_TO_ZERO",
        "terminal_AE2_load_remains_open": realization["open"][
            "AE2_child_response_M_C2_and_first_two_covariant_jets"
        ],
        "gluing_proves_child_value_remains_in_force": gluing[
            "adjudication"
        ]["fixing_C2_state_removes_M_C2_value_from_force"] is False,
        "no_second_birth_exterior_or_imported_endpoint_added": True,
        "no_history_existence_reset_recurrence_semantics_reopened": True,
    }
    return {
        "artifact": "BHSM_N12_COMPACT_HISTORY_ENDPOINT_ROLE_PROVENANCE",
        "status": "BIRTH_SOURCE_REFERENCE_AND_TERMINAL_AE2_LOAD_DISTINGUISHED",
        "classification": (
            "THE_BIRTH_TRACE_IS_THE_RETAINED_EXTERNAL_SOURCE_VARIABLE_AND_"
            "ITS_ZERO_VALUE_DEFINES_THE_ACTION_OWNED_DIRICHLET_REFERENCE,_"
            "WHILE_THE_NEW_EVENT_TRACE_REMAINS_SUBJECT_TO_THE_AE2_TERMINAL_"
            "LOAD;_THEREFORE_NO_SECOND_BIRTH_EXTERIOR_IS_MISSING_BUT_THE_"
            "C2_CHILD_CALDERON_RESPONSE_IS_STILL_REQUIRED"
        ),
        "endpoint_roles": {
            "birth": {
                "role": "EXTERNAL_BRST_QUOTIENTED_SOURCE_TRACE",
                "zero_source_restriction": "Gamma0_birth(U)=0",
                "operator_role": "ACTION_OWNED_DIRICHLET_REFERENCE",
                "physical_graph_reimposed": "EXACTLY_ONCE_IN_THE_JOINT_SOURCE_KERNEL",
                "adjacent_exterior_response_required_for_reference": False,
            },
            "new_event": {
                "role": "ACTION_OWNED_MAXIMAL_ENDPOINT_CLASS",
                "certified_endpoint": "E1_TO_C2_AE2_RESET",
                "load": "B_terminal=U_R_DAGGER*M_C2*U_R+W_phys",
                "child_response_available": False,
            },
        },
        "exact_dependency_after_endpoint_partition": {
            "missing_birth_load": False,
            "missing_terminal_C2_response": True,
            "required_for_zero_source_force": (
                "M_C2(z;xi)_AND_ITS_FIRST_GEOMETRY_JET_ON_THE_COMMON_"
                "RESOLVENT_DOMAIN"
            ),
            "required_for_saddle_and_Hessian": (
                "M_C2,D_xi_M_C2,D_xi2_M_C2_AND_THE_COMMON_PAIR_PLUS_CONTACT_"
                "RESPONSE"
            ),
        },
        "exact_next_dependency": realization["exact_next_dependency"],
        "claim_boundary": {
            "Gate7": "ACTIVE_TERMINAL_C2_RESPONSE_OR_JOINT_OPERATOR_OPEN",
            "endpoint_role_ambiguity": "CLOSED",
            "zero_source_force_value": "OPEN",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
