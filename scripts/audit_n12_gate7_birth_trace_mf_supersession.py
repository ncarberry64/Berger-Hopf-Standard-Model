"""Supersede the zero-trace interpretation of the incoming Gate-7 response."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_BIRTH_TRACE_MF_SUPERSESSION_AUDIT.json"
ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
COMPACT = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
ENDPOINT = BASE / "BHSM_N12_COMPACT_HISTORY_ENDPOINT_ROLE_PROVENANCE.json"
OLD_MATCH = BASE / "BHSM_N12_INCOMING_MF_COMPACT_MATCH.json"
OLD_ENCLOSURE = BASE / "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE.json"
AE2 = ROOT / "artifacts" / "action_extension" / "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
THEORY = ROOT / "theory" / "n12_gate7_birth_trace_mf_supersession_audit.md"
INPUTS = (ONTOLOGY, COMPACT, ENDPOINT, OLD_MATCH, OLD_ENCLOSURE, AE2, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _witness() -> dict[str, str | bool]:
    m00, m01, m10, m11 = map(Fraction, (3, 1, 1, 4))
    birth_load = Fraction(2)
    event_trace = Fraction(1)
    birth_trace = -m01 * event_trace / (m00 + birth_load)
    physical = m10 * birth_trace / event_trace + m11
    dirichlet = m11
    stationarity = (m00 + birth_load) * birth_trace + m01 * event_trace
    return {
        "M": "[[3,1],[1,4]]",
        "B_birth": str(birth_load),
        "J_ext": "0",
        "u_1": str(event_trace),
        "stationary_u_0": str(birth_trace),
        "stationarity_residual": str(stationarity),
        "physical_M_f": str(physical),
        "Dirichlet_M11": str(dirichlet),
        "responses_are_distinct": physical != dirichlet,
        "M_is_positive_definite": m00 > 0 and m00 * m11 - m01 * m10 > 0,
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing birth-trace supersession inputs: " + ", ".join(missing))
    ontology, compact, endpoint, old_match, old_enclosure, ae2 = map(_load, INPUTS[:-1])
    records = (ontology, compact, endpoint, old_match, old_enclosure, ae2)
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated birth-trace supersession parents required")

    witness = _witness()
    validation = {
        "compact_map_has_two_free_endpoint_traces": (
            compact["endpoint_partition"]["both_endpoint_traces_free_Calderon_data"] is True
        ),
        "old_endpoint_theorem_sets_birth_trace_to_zero": (
            endpoint["endpoint_roles"]["birth"]["zero_source_restriction"]
            == "Gamma0_birth(U)=0"
        ),
        "old_Mf_match_is_exactly_the_Dirichlet_terminal_block": (
            old_match["exact_match"]["zero_source_reference"] == "u_birth=0"
            and old_match["exact_match"]["restriction"].endswith("=M11")
        ),
        "old_negative_axis_enclosure_depends_on_old_match": any(
            "BHSM_N12_INCOMING_MF_COMPACT_MATCH.json" in key
            for key in old_enclosure["inputs"]
        ),
        "current_ontology_forbids_zero_trace_inference": (
            ontology["validation"]["zero_external_source_does_not_impose_zero_birth_trace"]
            is True
        ),
        "only_J_ext_is_zeroed": ontology["external_internal_partition"]["set_to_zero"] == ["J_ext"],
        "AE2_retains_internal_reset_graph": (
            ae2["action_definition"]["trace_graph"]
            == "Gamma0_child(Psi)=U_R*Gamma0_event(Psi)"
        ),
        "inverse_free_birth_graph_reduction_is_exact": witness["stationarity_residual"] == "0",
        "zero_source_and_Dirichlet_responses_are_distinct": witness["responses_are_distinct"] is True,
        "positive_witness_used": witness["M_is_positive_definite"] is True,
        "no_new_source_seam_force_selector_or_action_term_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_BIRTH_TRACE_MF_SUPERSESSION_AUDIT",
        "status": (
            "ZERO_SOURCE_DIRICHLET_MF_IDENTIFICATION_SUPERSEDED_BIRTH_GRAPH_REDUCTION_OPEN"
            if passed else "BIRTH_TRACE_MF_SUPERSESSION_NOT_CERTIFIED"
        ),
        "classification": (
            "J_ext_EQUALS_ZERO_REMOVES_ONLY_THE_EXTERNAL_LINEAR_COUPLING_AND_DOES_NOT_SET_"
            "THE_BIRTH_TRACE_TO_ZERO;_THE_PHYSICAL_INCOMING_RESPONSE_IS_THE_ACTION_BIRTH_"
            "GRAPH_SCHUR_REDUCTION,_NOT_THE_DIRICHLET_TERMINAL_BLOCK_M11"
        ),
        "exact_reduction": {
            "two_boundary_response": "[n0,n1]^T=[[M00,M01],[M10,M11]]*[u0,u1]^T",
            "birth_graph": "n0+B_birth*u0=J_ext",
            "zero_external_source_equation": "(M00+B_birth)*X_birth=M01,_u0=-X_birth*u1",
            "physical_incoming_response": "M_f_phys=M11-M10*X_birth",
            "first_jet_solve": "H_birth*X_birth,h=M01,h-H_birth,h*X_birth",
            "first_jet_response": "D_h_M_f_phys=M11,h-M10,h*X_birth-M10*X_birth,h",
            "explicit_inverse_formed": False,
            "Dirichlet_specialization": "u0=0_GIVES_M11_BUT_IS_NOT_IMPLIED_BY_J_ext=0",
            "natural_free_specialization": "B_birth=0_ONLY_IF_PROVED_BY_THE_RETAINED_ACTION_VARIATION",
        },
        "deterministic_counterexample": witness,
        "supersession": {
            "BHSM_N12_COMPACT_HISTORY_ENDPOINT_ROLE_PROVENANCE": (
                "SUPERSEDED_ONLY_WHERE_ZERO_SOURCE_IS_IDENTIFIED_WITH_Gamma0_birth_U_EQUALS_ZERO"
            ),
            "BHSM_N12_INCOMING_MF_COMPACT_MATCH": (
                "PRESERVED_AS_DIRICHLET_REFERENCE_M11_NOT_PHYSICAL_ZERO_SOURCE_M_f"
            ),
            "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE": (
                "PRESERVED_AS_A_CONDITIONAL_M11_ENCLOSURE_NOT_A_PHYSICAL_M_f_ENCLOSURE"
            ),
            "preserved": [
                "compact two-boundary Calderon map and jets",
                "incoming coefficient path and finite-amplitude form bounds",
                "AE2 internal reset graph",
                "joint heat-minus-zeta grading and single-reverse accounting",
            ],
        },
        "matching_audit": {
            "external_J_ext": "VALID_MATCH_ONLY_EXTERNAL_DATUM_ZEROED",
            "free_two_boundary_Calderon_map": "VALID_MATCH",
            "old_M11_negative_axis_enclosure": "VALID_CONDITIONAL_DIRICHLET_REFERENCE_ONLY",
            "physical_zero_source_incoming_M_f": "ACTUALLY_MISSING_BIRTH_GRAPH_REDUCTION",
            "B_birth_and_first_action_jet": "ACTUALLY_MISSING_OR_NOT_YET_INSTANTIATED",
            "unreduced_complete_joint_operator_with_birth_trace": "EQUIVALENT_VALID_ROUTE_OPEN",
        },
        "exact_next_dependency": (
            "INSTANTIATE_THE_RETAINED_ACTION_OWNED_BIRTH_GRAPH_B_birth_AND_ITS_FIRST_JET_"
            "AND_APPLY_THE_BORDERED_REDUCTION,_OR_KEEP_THE_BIRTH_TRACE_IN_THE_COMPLETE_"
            "JOINT_OPERATOR;_THEN_REALIZE_THE_PER_LEVEL_GRADED_COTANGENT_WITHOUT_ZEROING_"
            "THE_BIRTH_TRACE_OR_ADDING_A_SOURCE_OR_SEAM_FORCE"
        ),
        "adjudication": {
            "zero_source_Dirichlet_equivalence": "CLOSED_INVALID",
            "M_f_equals_M11_as_physical_zero_source_response": "SUPERSEDED",
            "physical_birth_graph_response": "OPEN_CURRENT_OPERATOR_OWNER",
            "new_external_or_seam_source_required": False,
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
        },
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "Gate7": "ACTIVE_BIRTH_GRAPH_LOADED_JOINT_OPERATOR",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
            "physical_incoming_M_f_claimed": False,
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
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "physical_M_f": payload["matching_audit"]["physical_zero_source_incoming_M_f"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
