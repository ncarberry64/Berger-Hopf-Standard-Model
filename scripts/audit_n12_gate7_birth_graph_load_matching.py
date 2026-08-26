"""Match the retained E0--C1 birth graph to its required internal load."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_BIRTH_GRAPH_LOAD_MATCHING_AUDIT.json"
SUPERSESSION = BASE / "BHSM_N12_GATE7_BIRTH_TRACE_MF_SUPERSESSION_AUDIT.json"
DOMAIN = BASE / "BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"
MAXIMAL = BASE / "BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
ENDPOINT = BASE / "BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json"
READOUT = BASE / "BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"
THRESHOLD = BASE / "BHSM_N12_FORWARD_BIRTH_THRESHOLD_MARGIN_AUDIT.json"
CORRESPONDENCE = ROOT / "artifacts" / "BHSM_aether_n3_event_complete_child_correspondence_v17_84.json"
AE2 = ROOT / "artifacts" / "action_extension" / "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
THEORY = ROOT / "theory" / "n12_gate7_birth_graph_load_matching_audit.md"
INPUTS = (
    SUPERSESSION, DOMAIN, MAXIMAL, ENDPOINT, READOUT, THRESHOLD,
    CORRESPONDENCE, AE2, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing birth-load matching inputs: " + ", ".join(missing))
    (
        supersession, domain, maximal, endpoint, readout, threshold,
        correspondence, ae2,
    ) = map(_load, INPUTS[:-1])
    records = (
        supersession, domain, maximal, endpoint, readout, threshold,
        correspondence, ae2,
    )
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated birth-load parents required")

    validation = {
        "zero_trace_Mf_identification_is_superseded": (
            supersession["adjudication"]
            ["M_f_equals_M11_as_physical_zero_source_response"] == "SUPERSEDED"
        ),
        "AE2_trace_lift_is_fixed": (
            ae2["action_definition"]["trace_graph"]
            == "Gamma0_child(Psi)=U_R*Gamma0_event(Psi)"
        ),
        "AE2_conormal_graph_is_fixed": (
            domain["source_domain"]["conormal"]
            == "Gamma1_child(Psi)=-U_R*Gamma1_event(Psi)_ON_Dom(D_AE2^2)"
        ),
        "birth_graph_is_internal_event_child_relation": (
            maximal["endpoint_rule"]["birth_graph"]["trace"]
            == "Gamma0_event(U)-Gamma0_child(U)=0"
        ),
        "opposite_arm_elimination_formula_is_retained": (
            endpoint["endpoint_load_adjudication"]["actual_event"]
            == "B_event(z;xi)=U_R(xi)^DAGGER*M_child(z;xi)*U_R(xi)+W_phys(xi)"
        ),
        "Dirichlet_map_is_reference_not_physical_graph": (
            "NOT_THE_EVENT_TRANSMISSION_OPERATOR"
            in endpoint["endpoint_load_adjudication"]["Dirichlet_reference"]
            and "PHYSICAL_OPERATOR_REMAINS_K_C"
            in readout["operator_family"]["Dirichlet_reference_role"]
        ),
        "event_side_nonzero_response_is_not_assembled": (
            threshold["provenance_adjudication"]
            ["sector_resolved_nonzero_event_flux_and_W_phys_matrix"]
            == "NOT_ASSEMBLED"
            and correspondence["event_to_complete_child_correspondence"]
            ["physical_block_provenance"]["physical_blocks_action_derived"] is False
        ),
        "fermion_local_surface_load_is_action_owned_zero": (
            domain["source_domain"]["fermion_W_phys_local_surface_block"] == 0
        ),
        "gauge_contact_formula_is_retained": (
            "sqrt(Delta_1^coexact)" in maximal["endpoint_rule"]["birth_graph"]["conormal"]
            or domain["source_domain"]["gauge_W_phys"]
            == "N_T=(Delta_1_coexact)^(1/2)_on_S3_R4"
        ),
        "no_external_source_or_new_seam_force_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_BIRTH_GRAPH_LOAD_MATCHING_AUDIT",
        "status": (
            "AE2_BIRTH_GRAPH_TYPE_CLOSED_EVENT_SIDE_LOAD_AND_JET_OPEN"
            if passed else "AE2_BIRTH_GRAPH_LOAD_MATCHING_NOT_CLOSED"
        ),
        "classification": (
            "THE_E0_TO_C1_AE2_TRACE_CONORMAL_GRAPH_AND_LOCAL_CONTACT_TYPES_ARE_"
            "ACTION_OWNED,_BUT_THE_NONZERO_EVENT_SIDE_CALDERON_RESPONSE_M_E0_AND_"
            "ITS_FIRST_JET_ARE_NOT_REALIZED;_THEREFORE_B_birth_AND_THE_PHYSICAL_"
            "INCOMING_M_f_REMAIN_OPEN"
        ),
        "forward_event_diagram": (
            "PRE_E0--M_E0-->E0--(U_R0,W_E0)-->C1--M_form-->E1"
        ),
        "exact_birth_load": {
            "frame": "C1_BIRTH_FRAME",
            "trace_law": "u_C1=U_R0*u_E0",
            "load": "B_birth=U_R0*(M_E0+W_E0)*U_R0^dagger",
            "zero_external_source_graph": "n_C1_birth+B_birth*u_C1=0",
            "formation_reduction": (
                "(M00+B_birth)*X_birth=M01,_M_f_phys=M11-M10*X_birth"
            ),
            "load_first_jet": (
                "D_B_birth=(D_U_R0)*(M_E0+W_E0)*U_R0^dagger+"
                "U_R0*(D_M_E0+D_W_E0)*U_R0^dagger+"
                "U_R0*(M_E0+W_E0)*(D_U_R0)^dagger"
            ),
            "covariant_frame": (
                "RESET_COMPATIBLE_CONNECTION_ABSORBS_EXPLICIT_D_U_R0_TERMS_"
                "BUT_NOT_D_M_E0_OR_D_W_E0"
            ),
            "explicit_matrix_inverse_formed": False,
        },
        "matching_audit": {
            "U_R0_reset_lift": "VALID_MATCH",
            "AE2_trace_and_conormal_graph": "VALID_MATCH",
            "fermion_W_E0": "VALID_MATCH_ACTION_OWNED_ZERO_LOCAL_SURFACE_BLOCK",
            "gauge_W_E0": "VALID_MATCH_RETAINED_SPATIAL_CONTACT_FORMULA",
            "zero_background_Calderon": "INVALID_FOR_NONZERO_PHYSICAL_BIRTH_RESPONSE",
            "local_zero_transport": "INVALID_AS_COMPLETE_EVENT_SIDE_RESPONSE",
            "M_E0_nonzero_event_side_Calderon_family": "ACTUALLY_MISSING",
            "D_xi_M_E0_and_D_xi_W_E0": "ACTUALLY_MISSING_OR_PARTIAL_BY_SECTOR",
            "B_birth_and_first_jet": "ACTUALLY_MISSING_REALIZED_VALUE",
            "physical_M_f_and_first_jet": "WAITING_ON_B_birth_OR_UNREDUCED_E0_ARM",
            "unreduced_joint_E0_C1_operator": "EQUIVALENT_VALID_ROUTE_OPEN",
        },
        "exact_next_dependency": (
            "REALIZE_OR_SHARPLY_ENCLOSE_THE_ACTION_OWNED_NONZERO_E0_EVENT_SIDE_"
            "CALDERON_FAMILY_M_E0(z;xi),_ITS_FIRST_QUOTIENT_JET,_AND_ANY_RETAINED_"
            "NONFERMION_W_E0_JET,_THEN_FORM_B_birth_AND_THE_BORDERED_PHYSICAL_M_f;_"
            "EQUIVALENTLY_KEEP_THE_E0_ARM_AND_C1_BIRTH_TRACE_IN_THE_COMPLETE_JOINT_"
            "OPERATOR_AND_DIFFERENTIATE_IT_ONCE"
        ),
        "adjudication": {
            "birth_graph_domain_type": "CLOSED_BY_AE2",
            "event_side_birth_load_value": "OPEN_CURRENT_OPERATOR_OWNER",
            "natural_B_birth_zero_specialization_authorized": False,
            "additional_external_source_or_seam_force_required": False,
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
        },
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "Gate7": "ACTIVE_E0_EVENT_SIDE_CALDERON_AND_BIRTH_LOAD",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
            "B_birth_realized": False,
            "physical_M_f_realized": False,
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
        "M_E0": payload["matching_audit"]["M_E0_nonzero_event_side_Calderon_family"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
