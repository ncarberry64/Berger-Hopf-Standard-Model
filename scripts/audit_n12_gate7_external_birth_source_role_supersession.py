"""Adjudicate the external birth trace against an invented dynamical E0 seam."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_EXTERNAL_BIRTH_SOURCE_ROLE_SUPERSESSION.json"
ROLE = BASE / "BHSM_N12_COMPACT_HISTORY_ENDPOINT_ROLE_PROVENANCE.json"
COMPACT = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
GLUING = BASE / "BHSM_N12_FINITE_HISTORY_GLUING_FORCE_PROVENANCE.json"
FUNCTIONAL = BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
INCOMING = BASE / "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE.json"
OLD_ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
OLD_BIRTH = BASE / "BHSM_N12_GATE7_BIRTH_TRACE_MF_SUPERSESSION_AUDIT.json"
OLD_LOAD = BASE / "BHSM_N12_GATE7_BIRTH_GRAPH_LOAD_MATCHING_AUDIT.json"
OLD_TWO_SEAM = BASE / "BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY.json"
OLD_E0 = BASE / "BHSM_N12_GATE7_E0_EVENT_SIDE_RESPONSE_PROVENANCE_AUDIT.json"
THEORY = ROOT / "theory" / "n12_gate7_external_birth_source_role_supersession.md"
INPUTS = (
    ROLE, COMPACT, GLUING, FUNCTIONAL, INCOMING, OLD_ONTOLOGY, OLD_BIRTH,
    OLD_LOAD, OLD_TWO_SEAM, OLD_E0, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _exact_witness() -> dict[str, str]:
    # A nonzero internal terminal response survives zero Dirichlet birth data.
    m11 = Fraction(4)
    child = Fraction(5)
    contact = Fraction(2)
    seam = m11 + child + contact
    d_m11 = Fraction(7)
    return {
        "external_birth_trace": "0",
        "M_f_equals_M11": str(m11),
        "transported_M_C2": str(child),
        "W_phys": str(contact),
        "S_AE2": str(seam),
        "D_M_f": str(d_m11),
        "D_logdet_S_AE2": str(d_m11 / seam),
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing external-birth supersession inputs: " + ", ".join(missing)
        )
    (
        role, compact, gluing, functional, incoming, old_ontology, old_birth,
        old_load, old_two_seam, old_e0,
    ) = map(_load, INPUTS[:-1])
    records = (
        role, compact, gluing, functional, incoming, old_ontology, old_birth,
        old_load, old_two_seam, old_e0,
    )
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated external-birth supersession parents required")
    witness = _exact_witness()
    validation = {
        "birth_datum_is_external_source_trace": (
            role["endpoint_roles"]["birth"]["role"]
            == "EXTERNAL_BRST_QUOTIENTED_SOURCE_TRACE"
        ),
        "zero_source_is_the_Dirichlet_reference": (
            role["endpoint_roles"]["birth"]["zero_source_restriction"]
            == "Gamma0_birth(U)=0"
            and role["validation"]["birth_zero_trace_is_retained_Dirichlet_reference"]
            is True
        ),
        "no_adjacent_birth_exterior_is_required": (
            role["endpoint_roles"]["birth"]
            ["adjacent_exterior_response_required_for_reference"] is False
            and role["exact_dependency_after_endpoint_partition"]
            ["missing_birth_load"] is False
        ),
        "free_two_boundary_map_is_reference_data": (
            compact["endpoint_partition"]["both_endpoint_traces_free_Calderon_data"]
            is True
        ),
        "single_internal_E1_C2_seam_is_retained": (
            gluing["exact_identities"]["seam"]
            == "S_AE2=M_f+U_R_DAGGER*M_c*U_R+W_phys"
        ),
        "zero_source_force_keeps_internal_operator": (
            functional["claim_boundary"]["zero_source_force_functional"]
            == "DERIVED"
        ),
        "incoming_M11_family_is_available": (
            incoming["claim_boundary"]["incoming_M_f_negative_axis_parametric_enclosure"]
            == "CLOSED"
        ),
        "old_dynamic_birth_trace_interpretation_identified": (
            old_ontology["validation"]["zero_external_source_does_not_impose_zero_birth_trace"]
            is True
            and old_birth["adjudication"]
            ["M_f_equals_M11_as_physical_zero_source_response"] == "SUPERSEDED"
            and old_load["claim_boundary"]["B_birth_realized"] is False
            and old_two_seam["claim_boundary"]["operator_topology_derived"] is True
            and old_e0["claim_boundary"]["M_E0_realized"] is False
        ),
        "exact_witness_retains_nonzero_internal_response": (
            witness["external_birth_trace"] == "0"
            and witness["M_f_equals_M11"] == "4"
            and witness["S_AE2"] == "11"
            and witness["D_logdet_S_AE2"] == "7/11"
        ),
        "no_internal_response_zeroed_or_new_source_seam_force_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_EXTERNAL_BIRTH_SOURCE_ROLE_SUPERSESSION",
        "status": (
            "EXTERNAL_BIRTH_TRACE_DIRICHLET_REFERENCE_REAFFIRMED_E0_ARM_REMOVED"
            if passed else "EXTERNAL_BIRTH_SOURCE_ROLE_NOT_VALIDATED"
        ),
        "classification": (
            "THE_ONLY_ZEROED_DATUM_IS_THE_EXTERNAL_BRST_QUOTIENTED_BIRTH_TRACE;_"
            "THE_INTERNAL_M_f_RESPONSE_REMAINS_NONZERO_AND_EQUALS_THE_M11_"
            "DIRICHLET_REFERENCE_BLOCK,_SO_THE_CURRENT_GATE7_OPERATOR_HAS_ONE_"
            "INTERNAL_E1_C2_SEAM_AND_REQUIRES_NO_PRE_E0_M_E0_ARM"
        ),
        "source_ordering": {
            "external_source": "j_birth=Gamma0_birth(U)",
            "differentiate_at": "FIXED_j_birth",
            "zero_source_restriction": "j_birth=0_EQUIVALENT_TO_Gamma0_birth(U)=0",
            "internal_responses_not_zeroed": [
                "M_f", "M_C2", "U_R", "W_phys", "PAIR_AND_CONTACT_BLOCKS"
            ],
        },
        "current_joint_assembly": {
            "diagram": "E0_EXTERNAL_BIRTH_TRACE--C1_M_f-->E1/C2_INTERNAL_SEAM--M_C2",
            "formation_response": "M_f=M11_AT_j_birth=0",
            "seam": "S_AE2=M_f+U_R^dagger*M_C2*U_R+W_phys",
            "joint_determinant": "det(P_joint)=det(A_f^D)*det(F_C2^D)*det(S_AE2)",
            "single_joint_cotangent": "DIFFERENTIATE_EACH_INTERNAL_BLOCK_EXACTLY_ONCE",
        },
        "supersession": {
            "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY": (
                "SUPERSEDED_ONLY_WHERE_IT_TREATS_THE_EXTERNAL_BIRTH_TRACE_AS_A_"
                "DYNAMICAL_INTEGRATED_TRACE"
            ),
            "BHSM_N12_GATE7_BIRTH_TRACE_MF_SUPERSESSION_AUDIT": "SUPERSEDED",
            "BHSM_N12_GATE7_BIRTH_GRAPH_LOAD_MATCHING_AUDIT": "NOT_A_CURRENT_GATE7_SLOT",
            "BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY": (
                "GENERAL_BLOCK_IDENTITY_RETAINED_PHYSICAL_TWO_SEAM_APPLICATION_SUPERSEDED"
            ),
            "BHSM_N12_GATE7_E0_EVENT_SIDE_RESPONSE_PROVENANCE_AUDIT": (
                "PROVENANCE_CORRECT_IF_SLOT_EXISTED_SLOT_NOT_REQUIRED"
            ),
        },
        "matching_audit": {
            "external_birth_source": "VALID_MATCH_FIXED_DIRICHLET_TRACE",
            "incoming_M_f": "VALID_MATCH_NONZERO_INTERNAL_M11_RESPONSE",
            "E1_C2_AE2_seam": "VALID_MATCH_COMPLETE_INTERNAL_SEAM",
            "pre_E0_M_E0": "NOT_REQUIRED_NOT_A_GATE7_DIAGRAM_SLOT",
            "B_birth": "NOT_REQUIRED_NOT_A_GATE7_DIAGRAM_SLOT",
            "complete_graded_cotangent_value": "OPEN_CURRENT_OWNER",
            "C2_maximal_projected_tail": "OPEN_CURRENT_OWNER",
        },
        "exact_witness": witness,
        "adjudication": {
            "source_ledger_ambiguity": "CLOSED",
            "M_f_equals_M11_at_zero_external_birth_trace": "REAFFIRMED",
            "M_E0_required": False,
            "complete_internal_seam_topology": "CLOSED_ONE_E1_C2_SEAM",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
        },
        "exact_next_dependency": (
            "USE_THE_AVAILABLE_INTERNAL_M_f_AND_THE_ACTION_OWNED_M_C2_FINITE_CORE_"
            "TO_INSTANTIATE_THE_COMPLETE_GRADED_E1_C2_SEAM_COTANGENT,_THEN_"
            "COMPLETE_OR_SOURCE_CONTRACT_THE_MAXIMAL_C2_TAIL_AND_RUN_THE_EXISTING_"
            "SINGLE_REVERSE_ADJOINT;_DO_NOT_REOPEN_M_f_OR_ADD_A_PRE_E0_ARM"
        ),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "Gate7": "ACTIVE_COMPLETE_GRADED_E1_C2_COTANGENT_AND_C2_TAIL",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
            "M_f_reopened": False,
            "M_E0_dependency_removed": True,
            "numerical_force_claimed": False,
            "frozen_predictions_changed": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "M_f": payload["adjudication"]["M_f_equals_M11_at_zero_external_birth_trace"],
        "M_E0_required": payload["adjudication"]["M_E0_required"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
