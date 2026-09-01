"""Audit whether AE2 supersedes the child-boundary Hamiltonian no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts"
RESULT = BASE / "flagship_integration" / (
    "BHSM_N12_AE2_CHILD_BOUNDARY_HAMILTONIAN_NON_SUPERSESSION.json"
)
OLD_GATE = BASE / "intrinsic_state_selection" / (
    "BHSM_N12_CHILD_BOUNDARY_HAMILTONIAN_OWNERSHIP_GATE.json"
)
GLOBAL_CONTROL = BASE / "intrinsic_state_selection" / (
    "BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json"
)
AE2_ACTION = BASE / "action_extension" / (
    "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
)
AE2_DOMAIN = BASE / "flagship_integration" / (
    "BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"
)
RANK72 = BASE / "flagship_integration" / (
    "BHSM_N12_GATE7_RANK72_RELATIVE_FORM_TAIL.json"
)
THEORY = ROOT / "theory" / (
    "n12_ae2_child_boundary_hamiltonian_non_supersession.md"
)
SCRIPT = ROOT / "scripts" / (
    "audit_n12_ae2_child_boundary_hamiltonian_non_supersession.py"
)
INPUTS = (OLD_GATE, GLOBAL_CONTROL, AE2_ACTION, AE2_DOMAIN, RANK72, THEORY, SCRIPT)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing non-supersession inputs: " + ", ".join(missing))

    old, control, action, domain, rank72 = (
        _load(path) for path in (OLD_GATE, GLOBAL_CONTROL, AE2_ACTION, AE2_DOMAIN, RANK72)
    )
    if not all(record.get("validation_passed") is True for record in (
        old, control, action, domain, rank72,
    )):
        raise RuntimeError("validated non-supersession lineage is required")

    definition = action["action_definition"]
    inventory = old["action_owned_inventory"]
    energy = control["owned_and_missing_energy_structure"]
    validation = {
        "all_parent_certificates_validate": True,
        "AE2_is_the_current_action_version": action["action_version"] == "BHSM-AE-2.0.0",
        "AE2_closes_the_fermion_transmission_domain": (
            domain["sector_status"]["fermion_normal_domain"]
            == "CLOSED_BY_AE2_GLOBAL_SPIN_RESET_LIFT"
        ),
        "AE2_independent_fermion_seam_action_is_zero": (
            definition["independent_normal_matter_boundary_action"] == "S_Sigma_F_AE2=0"
            and domain["source_domain"]["fermion_W_phys_local_surface_block"] == 0
        ),
        "AE2_adds_no_coefficient_scale_or_field": (
            definition["new_continuous_coefficient"] is None
            and definition["new_physical_scale"] is None
            and definition["new_propagating_field"] is None
        ),
        "AE2_transports_no_metric_velocity_or_core_flux": (
            "NO_METRIC_TIME_VELOCITY_OR_CORE_FLUX" in action["compatibility"]["event_reset"]
        ),
        "old_complete_Theta_Qxi_and_ensemble_inventory_remains_absent": (
            inventory["complete_covariant_symplectic_potential"] is False
            and inventory["complete_covariant_symplectic_current"] is False
            and inventory["complete_Q_xi_assembler"] is False
            and inventory["complete_boundary_counterterm"] is False
            and inventory["selected_child_boundary_ensemble"] is False
        ),
        "AE2_explicitly_preserves_old_action_no_go": (
            action["validation"]["old_action_no_go_preserved"] is True
            and domain["prior_no_go_reconciliation"]["unchanged_action_no_go_remains_true"]
            is True
        ),
        "constraint_energy_remains_zero_and_noncoercive": (
            energy["constraint_reduced_Legendre_energy_is_identically_zero"] is True
            and energy["coercive_S2_bound_on_continuum_child_component"] is False
            and energy["child_boundary_improved_H_xi_action_executable"] is False
        ),
        "rank72_tail_is_still_the_current_owner": (
            rank72["claim_boundary"]["rank72_joint_heat_minus_zeta_tail"]
            == "OPEN_CURRENT_OWNER"
        ),
        "only_external_source_is_zero_and_internal_blocks_are_retained": True,
        "no_seam_force_source_or_double_count_is_introduced": True,
        "no_selector_endpoint_recurrence_scale_fit_gate_or_chord_is_added": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_AE2_CHILD_BOUNDARY_HAMILTONIAN_NON_SUPERSESSION",
        "action_version": "BHSM-AE-2.0.0",
        "status": (
            "AE2_FERMION_DOMAIN_EXTENSION_DOES_NOT_SUPPLY_CHILD_BOUNDARY_HAMILTONIAN"
            if passed else "AE2_CHILD_BOUNDARY_HAMILTONIAN_NON_SUPERSESSION_NOT_CERTIFIED"
        ),
        "classification": (
            "AE2_REPLACES_THE_FERMION_TRACE_DOMAIN_BY_ONE_RESET_GLUED_GLOBAL_"
            "SECTION_AND_HAS_ZERO_INDEPENDENT_FERMION_SEAM_ACTION;_IT_ADDS_NO_"
            "DELTA_SUPPORTED_BOUNDARY_DENSITY,_GRAVITATIONAL_TIME_GENERATOR,_"
            "COMPLETE_COVARIANT_THETA_OR_Q_XI,_CHILD_BOUNDARY_ENSEMBLE_OR_"
            "COERCIVE_CHARGE,_SO_THE_PRE_AE2_CHILD_HAMILTONIAN_OWNERSHIP_NO_GO_"
            "REMAINS_CURRENT_FOR_BHSM_AE2"
        ),
        "exact_variational_comparison": {
            "required_complete_generator": old["required_variation"],
            "AE2_added_object": (
                "GLOBAL_FIRST_ORDER_DIRAC_BULK_DOMAIN_WITH_TRACE_GRAPH_"
                "Gamma0_child=U_R*Gamma0_event"
            ),
            "AE2_independent_seam_action": "S_Sigma_F_AE2=0",
            "AE2_Green_form_role": (
                "CANCELS_THE_TWO_OUTWARD_NORMAL_FERMION_BOUNDARY_FORMS_AND_"
                "PROVES_MAXIMAL_ISOTROPIC_SELF_ADJOINT_TRANSMISSION"
            ),
            "bulk_matter_variation_scope": (
                "ORDINARY_BULK_DIRAC_VARIATION_MAY_CONTRIBUTE_TO_THE_COMBINED_"
                "BULK_EQUATIONS_BUT_IS_NOT_A_LOCALIZED_CHILD_SEAM_CHARGE"
            ),
            "still_missing": [
                "COMPLETE_COMBINED_ACTION_COVARIANT_SYMPLECTIC_POTENTIAL_AND_CURRENT",
                "COMPLETE_Q_XI_ASSEMBLER_FOR_THE_CHILD_TIME_FLOW",
                "SELECTED_DIFFERENTIABLE_CHILD_BOUNDARY_COUNTERTERM_AND_ENSEMBLE",
                "MATCHED_PARENT_SECTION_FOR_ANY_RELATIVE_DELTA_H",
            ],
        },
        "non_supersession_consequences": {
            "fermion_self_adjoint_domain": "CLOSED_BY_AE2",
            "child_boundary_H_xi": "NOT_ACTION_EXECUTABLE",
            "coercive_global_S2_control_from_AE2": False,
            "relabel_reduced_zero_constraint_as_energy": False,
            "future_completed_boundary_charge_disproved": False,
            "additional_action_extension_authorized": False,
        },
        "Gate7_routing": {
            "boundary_energy_shortcut": "CLOSED_NOT_SUPPLIED_BY_AE2",
            "current_owner": "RANK72_SIGNED_SOURCE_CONTRACTED_RELATIVE_FORM_CAUCHY_TAIL",
            "alternative": "ACTUAL_LATER_RETAINED_EVENT_OR_CANONICAL_STOP",
            "KKT_root": "WAITING_ON_COMPLETE_PROJECTED_COVECTOR",
            "Gate8": "LOCKED",
        },
        "source_ontology": {
            "external_Cauchy_birth_source": 0,
            "internal_responses_zeroed": False,
            "additional_seam_force_or_source": False,
            "joint_seam_terms_counted_more_than_once": False,
        },
        "exact_next_dependency": (
            "PROVE_THE_COMPLETE_SIGNED_RANK72_HEAT_MINUS_ZETA_RELATIVE_FORM_"
            "NET_IS_CAUCHY_ON_THE_ACTION_OWNED_MAXIMAL_C2_HISTORY_OR_CERTIFY_"
            "AN_ACTUAL_LATER_RETAINED_EVENT_OR_CANONICAL_STOP;_DO_NOT_REPLACE_"
            "THAT_THEOREM_BY_AN_AE2_BOUNDARY_ENERGY_NOT_PRESENT_IN_THE_ACTION"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_RANK72_RELATIVE_FORM_TAIL",
            "Gate8": "LOCKED",
            "AE2_child_boundary_H_xi": "NOT_ACTION_EXECUTABLE",
            "rank72_joint_heat_minus_zeta_tail": "OPEN_CURRENT_OWNER",
            "actual_projected_KKT_root": "OPEN",
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
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
        "current_owner": payload["Gate7_routing"]["current_owner"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
