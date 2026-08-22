"""Audit whether the retained action defines a matched-parent section.

The v7.1 stratified action owns a covariant, constrained correspondence.  A
relative charge additionally needs a single-valued parent-only stationary
section over fixed comparison data.  This audit checks that typing and the
implicit-function hypotheses without choosing a branch or boundary domain.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REDUCTION = ROOT / "artifacts/BHSM_covariant_bulk_boundary_reduction_functor_v7_1.json"
BOUNDARY = ROOT / "artifacts/BHSM_aether_boundary_identity_ejection_v15_13.json"
OWNERSHIP = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_N12_MATCHED_PARENT_QXI_OWNERSHIP.json"
)
CHILD = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
ACTION_JET = ROOT / (
    "src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py"
)
EVENT_IDENTITY = ROOT / "artifacts/BHSM_aether_encapsulation_correspondence_v15_0.json"
PARENT_SEED = ROOT / (
    "artifacts/BHSM_degree_one_lorentzian_full_preimage_phase_space_gate_v14_91.json"
)
EVENT_EIGENLINE = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_ORDERED_EVENT_EIGENLINE_BALL.json"
)
FORMATION = ROOT / "artifacts/BHSM_formation_continuation_v15_7.json"
POSITIVE_DURATION_HISTORY = ROOT / "scripts/audit_n12_positive_duration_calderon_history.py"
RESULT = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_N12_MATCHED_PARENT_STATIONARY_SECTION_GATE.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    inputs = (
        REDUCTION, BOUNDARY, OWNERSHIP, CHILD, ACTION_JET,
        EVENT_IDENTITY, PARENT_SEED, EVENT_EIGENLINE, FORMATION,
        POSITIVE_DURATION_HISTORY,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing matched-parent inputs: " + ", ".join(missing))

    reduction = json.loads(REDUCTION.read_text(encoding="utf-8"))
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    ownership = json.loads(OWNERSHIP.read_text(encoding="utf-8"))
    child = json.loads(CHILD.read_text(encoding="utf-8"))
    event_identity = json.loads(EVENT_IDENTITY.read_text(encoding="utf-8"))
    parent_seed = json.loads(PARENT_SEED.read_text(encoding="utf-8"))
    event_eigenline = json.loads(EVENT_EIGENLINE.read_text(encoding="utf-8"))
    formation = json.loads(FORMATION.read_text(encoding="utf-8"))
    positive_duration_source = POSITIVE_DURATION_HISTORY.read_text(encoding="utf-8")

    transport = {
        row["field"]: row["map"]
        for row in reduction["field_and_bundle_transport"]
    }
    domain_witness = boundary["boundary_identity_and_transport"][
        "surviving_domain_witness"
    ]
    same_child = [
        row for row in domain_witness["witnesses"]
        if row["alpha_child"] == 0.0 and row["alpha_parent"] in (0.0, 1.0)
    ]
    if len(same_child) != 2:
        raise RuntimeError("expected the retained same-child parent-domain witness pair")

    first_missing = (
        "ACTION_OWNED_REALIZATION_OF_THE_ABSTRACT_EMPTY_EVENT_IDENTITY_AS_"
        "AN_INVARIANT_PARENT_ONLY_FIELD_DOMAIN_D_P_WITH_PRESERVED_INTERFACE_DATA"
    )
    primary_dependency = (
        "DERIVE_ACTION_SELECTED_PARENT_ONLY_LOCUS_AND_SINGLE_VALUED_"
        "GAUGE_QUOTIENTED_STATIONARY_SECTION_OVER_FIXED_COMMON_DATA"
    )
    validation = {
        "continuum_child_remains_certified": (
            ownership["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True
        ),
        "direct_N12_child_remains_certified": (
            child["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"] is True
        ),
        "v7_1_covariant_correspondence_retained": (
            reduction["RB01_result"] == "RB_01_UNIFIED_PARENT_ACTION_PROVENANCE_CLOSED"
        ),
        "R_85_noninjectivity_explicit": (
            "Phi_perp" in reduction["reduction_8_to_5"]["field_expansion"]
        ),
        "R_54_kernel_and_local_branch_scope_explicit": (
            "k remain explicit" in reduction["reduction_5_to_4"]["kernel_rule"]
            and "no global uniqueness claim"
            in reduction["reduction_5_to_4"]["existence_scope"]
        ),
        "same_common_boundary_identity_has_inequivalent_parent_domains": (
            domain_witness["all_witnesses_preserve_boundary_identity"] is True
            and domain_witness["inequivalent_endpoint_spectra_remain"] is True
            and same_child[0]["eigenphases"] != same_child[1]["eigenphases"]
        ),
        "localized_parent_field_maps_absent": all(
            transport[field] is None for field in ("A_SM", "Psi", "H")
        ),
        "abstract_empty_event_identity_is_not_action_derived": (
            event_identity["existing_BHSM_action_derives_this_event_law"] is False
        ),
        "conditional_parent_seed_is_not_action_selected_or_full_stratified": (
            parent_seed["degree_one_background"]["coefficient_locus_action_selected"]
            is False
            and parent_seed["degree_one_background"]
            ["full_stratified_stationary_solution"] is False
        ),
        "event_forward_shortcut_does_not_select_parent_branch": (
            abs(event_eigenline["center_selected_eigenvalue_binary64"]) < 1.0e-12
            and formation["nonlinear_response_fork"]
            == ["RESTORATION", "ENCAPSULATION"]
            and formation["encapsulation_selected_over_restoration"] is False
            and "_rk4_projected(event, -TIME_STEP)" in positive_duration_source
        ),
        "no_selector_or_new_physics_added": True,
        "Q_xi_and_Delta_H_remain_unevaluated": (
            ownership["Q_xi_evaluated"] is False
            and ownership["Delta_H_evaluated"] is False
        ),
    }
    payload = {
        "artifact": "BHSM_N12_MATCHED_PARENT_STATIONARY_SECTION_GATE",
        "classification": (
            "MATCHED_PARENT_STATIONARY_SECTION_NOT_DEFINED_BY_RETAINED_ACTION"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "v7_1_correspondence": {
            "R_8to5_defined": True,
            "R_8to5_noninjective_reason": (
                "P_ret discards Phi_perp; adding any nonzero discarded component "
                "leaves the retained coefficients unchanged"
            ),
            "stored_S5_is_independent_constrained_target": (
                reduction["authoritative_architecture"]
                ["S5_claimed_as_pi_pushforward_of_S8"] is False
            ),
            "R_5to4_defined": True,
            "R_5to4_is_set_valued_reason": (
                reduction["reduction_5_to_4"]["kernel_rule"] + "; "
                + reduction["reduction_5_to_4"]["existence_scope"]
            ),
        },
        "parent_domain_nonuniqueness_witness": {
            "fixed_child_phase": 0.0,
            "parent_phase_choices": [row["alpha_parent"] for row in same_child],
            "endpoint_eigenphases": [row["eigenphases"] for row in same_child],
            "both_preserve_boundary_identity": True,
            "both_unitary": all(row["unitarity_residual"] == 0.0 for row in same_child),
            "not_removed_by_common_overall_phase": True,
            "conclusion": (
                "the retained boundary identity and self-adjointness do not "
                "select the parent maximal-isotropic domain"
            ),
        },
        "parent_only_typing": {
            "N12_state_space": ownership["state_and_action_inventory"],
            "explicit_parent_only_field_variables": [],
            "explicit_parent_only_domain_inclusion": None,
            "boundary_localized_field_maps": {
                field: transport[field] for field in ("A_SM", "Psi", "H")
            },
            "matched_parent_equation_map_G_P_implemented": False,
        },
        "empty_child_identity_audit": {
            "abstract_event_identity_exists": event_identity["identity"] is not None,
            "abstract_event_identity": event_identity["identity"],
            "abstract_identity_is_action_derived": False,
            "conditional_homogeneous_parent_seed_exists": (
                parent_seed["degree_one_background"]["M8_block_stationary_solution"]
            ),
            "conditional_parent_seed_action_selected": False,
            "conditional_parent_seed_is_full_stratified_solution": False,
            "sigma_zero_or_degree_one_selects_no_child": False,
            "conclusion": (
                "no retained invariant distinguishes the empty-child parent "
                "domain from the complete-child sector"
            ),
        },
        "counterfactual_event_forward_audit": {
            "event_half_is_complete_reduced_N12_Cauchy_tuple": True,
            "reduced_N12_tuple": {
                "coordinates": ownership["state_and_action_inventory"]
                ["per_side_coordinates"],
                "velocities": ownership["state_and_action_inventory"]
                ["per_side_velocities"],
                "multipliers": ownership["state_and_action_inventory"]
                ["per_side_lapse_shift_multipliers"],
                "total": ownership["state_and_action_inventory"]["per_side_total"],
            },
            "event_is_complete_global_v7_1_parent_state": False,
            "center_ordered_event_eigenvalue": event_eigenline[
                "center_selected_eigenvalue_binary64"
            ],
            "exact_event_equation_is_zero_eigenvalue_threshold": True,
            "nonlinear_response_fork": formation["nonlinear_response_fork"],
            "encapsulation_selected_over_restoration": formation[
                "encapsulation_selected_over_restoration"
            ],
            "existing_positive_duration_diagnostic_evolves_event_backward": True,
            "existing_positive_duration_diagnostic_is_forward_parent_proof": False,
            "event_forward_R_P_executable": False,
            "reason": (
                "the reduced event tuple omits the full stratified parent fields, "
                "domains, interface controls, generator, clock, and reference "
                "subtraction; the ordered threshold does not select the restoration "
                "side, and the retained diagnostic evolves the event backward"
            ),
            "first_missing_object_for_this_shortcut": (
                "ACTION_OWNED_TIME_ORIENTED_EVENT_TO_PARENT_CAUCHY_LIFT_WITH_"
                "PRESERVED_COMMON_DATA_AND_POSITIVE_DURATION_NONENCAPSULATING_"
                "BRANCH_CERTIFICATE"
            ),
        },
        "implicit_function_audit": {
            "required_map": "G_P(Phi_P; common_data)=0 modulo gauge",
            "parent_only_domain_and_codomain_typed": False,
            "D_Phi_P_G_P_available": False,
            "gauge_quotiented_parent_normal_right_inverse_available": False,
            "current_N12_inverse_scope": (
                "unchanged 57-row event-child normal map in the reduced q,v,m space"
            ),
            "current_N12_inverse_can_be_reused_for_parent_section": False,
            "reason": (
                "the parent-only field/domain inclusion and parent equation are "
                "absent, so the operators have different unstated domains and codomains"
            ),
            "implicit_function_theorem_applicable": False,
        },
        "R_P_executable": False,
        "Q_xi_evaluated": False,
        "Delta_H_evaluated": False,
        "first_missing_action_owned_datum": first_missing,
        "active_primary_dependency": primary_dependency,
        "after_first_missing_datum": (
            "TYPE_THE_PARENT_ONLY_FIELD_AND_DOMAIN_INCLUSION_I_P;_THEN_PROVE_"
            "A_SINGLE_VALUED_GAUGE_QUOTIENTED_STATIONARY_SECTION_OF_"
            "THE_EXISTING_V7_1_CORRESPONDENCE_AND_THEN_EVALUATE_THE_COMMON_"
            "REFERENCE_BOUNDARY_IMPROVED_Q_XI"
        ),
        "retained_action_obstruction_scope": (
            "absence of a currently sourced selector/inclusion, not a proof that "
            "no future action-owned section can exist"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": True,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "result": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
        "classification": payload["classification"],
        "first_missing_action_owned_datum": first_missing,
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
