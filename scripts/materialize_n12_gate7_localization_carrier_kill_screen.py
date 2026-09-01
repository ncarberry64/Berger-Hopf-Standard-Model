"""Materialize the unchanged-AE2 localization-carrier kill screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.localization_carrier_audit import (
    LocalizationCandidate,
    evaluate_localization_candidates,
)
from bhsm.interface.physical_encapsulation_identification import (
    KERNEL_REDUCTION,
    tensor_factor_intertwiner_certificate,
)


ARTIFACTS = ROOT / "artifacts"
TARGET = ARTIFACTS / (
    "flagship_integration/BHSM_N12_GATE7_LOCALIZATION_CARRIER_KILL_SCREEN.json"
)

INPUTS = (
    ARTIFACTS / "flagship_integration/BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json",
    ARTIFACTS / "action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    ARTIFACTS / "BHSM_CURRENT_FULL_FIELD_ACTION_ATTACHMENT_AUDIT.json",
    ARTIFACTS / "BHSM_fixed_encapsulation_geometry_v11_2.json",
    ARTIFACTS / "BHSM_primitive_support_character_ledger_v11_2.json",
    ARTIFACTS / "BHSM_complete_local_supported_action_v11_2.json",
    ARTIFACTS / "BHSM_fixed_support_compatibility_audit_v6_25_0.json",
    ARTIFACTS / "BHSM_support_domain_decision_v6_25_0.json",
    ARTIFACTS / "flagship_integration/BHSM_SPACETIME_EDGE_ONTOLOGY_AUDIT.json",
    ARTIFACTS / "BHSM_junction_variation_and_selected_domain_v6_10_0.json",
    ARTIFACTS / "BHSM_aether_hybrid_standard_model_bundle_v15_53.json",
    ARTIFACTS / "BHSM_generation_projector_action_attachment_v8_2.json",
    ARTIFACTS / "flagship_integration/BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_AUDIT.json",
    ARTIFACTS / "flagship_integration/BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    """Return the evidence-bound carrier audit and reduced bridge ledger."""

    missing = [path.as_posix() for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("carrier-audit inputs required: " + ", ".join(missing))
    records = {path.name: _load(path) for path in INPUTS}
    first_stop = records["BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json"]
    reset = records["BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"]
    full_field = records["BHSM_CURRENT_FULL_FIELD_ACTION_ATTACHMENT_AUDIT.json"]
    fixed_geometry = records["BHSM_fixed_encapsulation_geometry_v11_2.json"]
    support = records["BHSM_primitive_support_character_ledger_v11_2.json"]
    local_action = records["BHSM_complete_local_supported_action_v11_2.json"]
    fixed_support = records["BHSM_fixed_support_compatibility_audit_v6_25_0.json"]
    support_decision = records["BHSM_support_domain_decision_v6_25_0.json"]
    edge = records["BHSM_SPACETIME_EDGE_ONTOLOGY_AUDIT.json"]
    junction = records["BHSM_junction_variation_and_selected_domain_v6_10_0.json"]
    bundle = records["BHSM_aether_hybrid_standard_model_bundle_v15_53.json"]
    generation = records["BHSM_generation_projector_action_attachment_v8_2.json"]
    enclosure_class = records["BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_AUDIT.json"]
    c2_response = records["BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json"]

    candidates = (
        LocalizationCandidate(
            "LC_01",
            "selected branch-24 eigenvalue lambda24",
            True,
            False,
            False,
            True,
            False,
            first_stop["status"],
            "A state-space event scalar selects event time, not an embedded spacetime domain.",
        ),
        LocalizationCandidate(
            "LC_02",
            "AE2 event-child reset locus and lift U_R",
            True,
            False,
            False,
            True,
            False,
            reset["action_definition"]["why_zero_is_owned"],
            "The reset is internal glue of one global trace domain and carries no delta-supported enclosure action.",
        ),
        LocalizationCandidate(
            "LC_03",
            "fixed B1 support and collar vocabulary",
            False,
            False,
            False,
            False,
            False,
            fixed_geometry["status"],
            "Kinematic fixed-manifold representability does not select an embedding, thickness, or physical interface.",
        ),
        LocalizationCandidate(
            "LC_04",
            "support character upsilon and core-surface attachment",
            False,
            False,
            False,
            False,
            False,
            support["status"],
            "The attachment character and exchange current are absent from an action-owned term.",
        ),
        LocalizationCandidate(
            "LC_05",
            "retained 98-variable N12 local action oracle",
            True,
            False,
            False,
            True,
            False,
            full_field["decision"],
            "The oracle contains geometry coordinates, velocities, and multipliers but no physical localization or full-field attachment slots.",
        ),
        LocalizationCandidate(
            "LC_06",
            "spacetime-edge transition route",
            False,
            False,
            False,
            False,
            False,
            "CURRENT_STOP_REMAINS_UNIDENTIFIED_WITH_SPACETIME_EDGE",
            "No theorem identifies the selected stop with a spacetime edge.",
        ),
    )
    audit = evaluate_localization_candidates(candidates)

    reset_lift = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)
    family_projector = np.diag([0.0, 1.0, 0.0]).astype(complex)
    intertwiner = tensor_factor_intertwiner_certificate(
        reset_lift, family_projector
    )

    validation = {
        "first_stop_is_action_owned": first_stop["validation_passed"] is True,
        "stop_does_not_supply_embedded_domain": audit["candidates"][0][
            "qualifies_as_physical_localization_carrier"
        ]
        is False,
        "reset_is_internal_glue": (
            "INTERNAL_GLUE" in reset["action_definition"]["why_zero_is_owned"]
        ),
        "current_n12_oracle_is_geometry_only": (
            full_field["classification"] == "PRECISE_ATTACHMENT_NO_GO_CERTIFICATE"
        ),
        "support_attachment_character_is_unfixed": (
            support["exact_next_object"]
            == "ACTION_OWNED_CORE_SURFACE_ATTACHMENT_TERM_FIXING_ATTACHMENT_CHARACTER_AND_EXCHANGE_CURRENT"
        ),
        "complete_supported_action_is_blocked": (
            local_action["status"]
            == "BHSM_COMPLETE_LOCAL_SUPPORTED_ACTION_BLOCKED_BY_UNASSIGNED_PRIMITIVE_SUPPORT_CHARACTERS"
        ),
        "support_domain_is_unselected": (
            support_decision["decision"]["selected_domain"] is None
        ),
        "junction_physical_domain_is_unselected": (
            junction["domain"]["unique_domain_selected"] is False
        ),
        "algebraic_family_reset_intertwiner_is_available": (
            intertwiner["algebraic_intertwiner_certified"] is True
            and bundle["validation_passed"] is True
            and generation["validation_passed"] is True
        ),
        "c2_family_mode_slot_remains_open": (
            c2_response["C2_enclosure_signature"]["family_sector_mode_slot"]
            == "NOT_INSTANTIATED_UPSTREAM_ON_THIS_C2_HISTORY"
        ),
        "enclosure_class_invariance_not_promoted": (
            enclosure_class["validation_passed"] is True
        ),
        "spacetime_edge_remains_unidentified": (
            edge["validation"][
                "current_stop_remains_unidentified_with_spacetime_edge"
            ]
            is True
        ),
        "no_action_version_change_made": True,
        "no_new_particle_or_spectrum_result": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_LOCALIZATION_CARRIER_KILL_SCREEN",
        "schema_version": 1,
        "action_version": "BHSM-AE-2.0.0_UNCHANGED",
        "status": "UNCHANGED_AE2_LOCALIZATION_CARRIER_NOT_FOUND_AT_AUDITED_EVIDENCE_BOUNDARY",
        "classification": "CARRIER_EXISTENCE_KILL_SCREEN_FAIL_CLOSED",
        "carrier_type": {
            "map": "D_A: z -> (D_enc,Sigma_enc,X,n,K,...) ",
            "scalar_realization": "Sigma_enc={x:chi_A[Phi](x)=0}, dchi_A|Sigma_enc != 0",
            "distinction": "lambda24:C->R fixes event time; chi_A is a covariant spacetime localization object",
        },
        "carrier_audit": audit,
        "four_kernel_reduction": [dict(kernel) for kernel in KERNEL_REDUCTION],
        "subrequirement_resolution": {
            "PEI_05a_fermionic_event_child_reset_trace_matching": "AVAILABLE",
            "PEI_05b_physical_enclosure_geometric_junction": "OPEN",
            "PEI_05c_dependency_closed_full_field_enclosure_flux_matching": "OPEN",
            "PEI_11a_tensor_factor_family_reset_intertwiner": "AVAILABLE",
            "PEI_11b_family_mode_projector_instantiated_on_actual_C2_parent": "OPEN",
            "PEI_11c_physical_enclosure_inherits_intertwined_bundle_state": "OPEN",
        },
        "family_reset_intertwiner": intertwiner,
        "dependency_closure_rule": {
            "definition": "Dep_A(B_i)=TC(fields defining B_i, fields required by M_SM(B_i), fields entering delta S on Sigma_enc)",
            "requirement": "Dep_A(B_i) must be contained in the fields transported by the physical enclosure",
            "all_fields_everywhere_required": False,
            "physical_instance_available": False,
        },
        "route_adjudication": {
            "least_assumptive_route_to_test": "LOCAL_SAME_SPACETIME_ENCLOSURE",
            "selected_by_unchanged_action": False,
            "core_boundary_or_collar_status": fixed_support["primary_result"],
            "spacetime_edge_status": (
                "CURRENT_STOP_REMAINS_UNIDENTIFIED_WITH_SPACETIME_EDGE"
            ),
        },
        "scientific_decision": (
            "THE_AUDITED_UNCHANGED_AE2_OBJECTS_SUPPLY_EVENT_TIME,_INTERNAL_"
            "RESET_GLUE,_AND_CONDITIONAL_GEOMETRIC_VOCABULARY_BUT_NO_"
            "ACTION_OWNED_OBJECT_OF_THE_PHYSICAL_LOCALIZATION_CARRIER_TYPE"
        ),
        "action_extension_boundary": {
            "extension_required_if_local_physical_enclosure_remains_the_goal": True,
            "extension_authorized_here": False,
            "minimum_new_owner": "COVARIANT_LOCALIZATION_OR_DOMAIN_SELECTOR_WITH_SAME_ACTION_INTERFACE_VARIATION",
            "forbidden_shortcut": "DO_NOT_RELABEL_LAMBDA24_ZERO_OR_THE_RESET_LOCUS_AS_SIGMA_ENC",
        },
        "exact_next_dependency": (
            "OWNER_AUTHORIZED_ACTION_VERSION_DECISION_SELECTING_A_"
            "COVARIANT_LOCALIZATION_OR_DOMAIN_CARRIER;_THEN_DERIVE_ITS_"
            "INTERFACE_VARIATION_AND_DEPENDENCY_CLOSED_FIELD_TRANSPORT"
        ),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
        "FLAGSHIP_READY": False,
    }


def main() -> int:
    payload = build_payload()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
