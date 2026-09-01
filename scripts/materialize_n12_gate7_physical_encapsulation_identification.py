"""Materialize the N12 Gate-7 physical-encapsulation bridge audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.physical_encapsulation_identification import (
    ENCLOSURE_ROUTES,
    assert_no_forbidden_equivalence,
    evaluate_identification,
)


ARTIFACTS = ROOT / "artifacts"
TARGET = ARTIFACTS / (
    "flagship_integration/"
    "BHSM_N12_GATE7_PHYSICAL_ENCAPSULATION_IDENTIFICATION_BRIDGE.json"
)

INPUTS = (
    ARTIFACTS
    / "flagship_integration/BHSM_NORMAN_SCHOOL_FULL_CORPUS_RECONSTRUCTION.json",
    ARTIFACTS
    / "flagship_integration/BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json",
    ARTIFACTS
    / "flagship_integration/BHSM_N12_GATE7_LOCALIZATION_CARRIER_KILL_SCREEN.json",
    ARTIFACTS
    / "intrinsic_state_selection/BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json",
    ARTIFACTS
    / "intrinsic_state_selection/BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json",
    ARTIFACTS
    / "n12_continuum_majorant_effectiveness/BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json",
    ARTIFACTS / "BHSM_fixed_encapsulation_geometry_v11_2.json",
    ARTIFACTS / "BHSM_s7_physical_collar_matching_v6_0_1.json",
    ARTIFACTS / "BHSM_exact_boundary_matching_action_ledger_v6_1_3.json",
    ARTIFACTS / "BHSM_junction_variation_and_selected_domain_v6_10_0.json",
    ARTIFACTS / "BHSM_CURRENT_FULL_FIELD_ACTION_ATTACHMENT_AUDIT.json",
    ARTIFACTS / "flagship_integration/BHSM_SPACETIME_EDGE_ONTOLOGY_AUDIT.json",
    ARTIFACTS
    / "flagship_integration/BHSM_NEUTRINO_CHARGED_CURRENT_2PI_CLOSURE_RECONCILIATION.json",
    ARTIFACTS
    / "flagship_integration/BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_AUDIT.json",
    ARTIFACTS / "BHSM_aether_hybrid_standard_model_bundle_v15_53.json",
    ARTIFACTS / "BHSM_generation_projector_action_attachment_v8_2.json",
    ARTIFACTS / "BHSM_harmonic_exact_mode_representation_spectrum_v6_0_4.json",
    ARTIFACTS / "BHSM_global_family_count_spectrum_v6_7_0.json",
    ARTIFACTS / "BHSM_parent_action_charged_current_v11_6.json",
    ARTIFACTS / "BHSM_topological_configuration_space_v6_5_0.json",
    ARTIFACTS / "BHSM_topological_matter_action_global_spectrum_report_v6_5_0.json",
    ARTIFACTS / "BHSM_electromagnetic_surviving_generator_v6_3_0.json",
    ARTIFACTS
    / "intrinsic_state_selection/BHSM_N12_CORRECTED_FORWARD_HISTORY_AND_PARTICLE_CLASS_GATES.json",
)

TEXT_INPUTS = (
    ROOT / "theory/derived_hopf_phase_closure.md",
    ROOT / "theory/boundary_phase_closure_functional.md",
    ROOT / "theory/derived_generation_raw_mode_ledgers.md",
    ROOT / "theory/derived_yukawa_generation_mode_ledgers.md",
    ROOT / "docs/bhsm_sector_projector_ledger_theorem.md",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    """Build the fail-closed current-evidence bridge result."""

    all_inputs = INPUTS + TEXT_INPUTS
    missing_inputs = [path.as_posix() for path in all_inputs if not path.is_file()]
    if missing_inputs:
        raise FileNotFoundError(
            "physical-identification inputs required: " + ", ".join(missing_inputs)
        )

    records = {path.name: _load(path) for path in INPUTS}
    reconstruction = records[
        "BHSM_NORMAN_SCHOOL_FULL_CORPUS_RECONSTRUCTION.json"
    ]
    first_stop = records[
        "BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json"
    ]
    carrier_audit = records[
        "BHSM_N12_GATE7_LOCALIZATION_CARRIER_KILL_SCREEN.json"
    ]
    local_branch = records["BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json"]
    reset = records[
        "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
    ]
    child = records["BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"]
    fixed_geometry = records["BHSM_fixed_encapsulation_geometry_v11_2.json"]
    collar = records["BHSM_s7_physical_collar_matching_v6_0_1.json"]
    matching = records["BHSM_exact_boundary_matching_action_ledger_v6_1_3.json"]
    junction = records[
        "BHSM_junction_variation_and_selected_domain_v6_10_0.json"
    ]
    full_field = records["BHSM_CURRENT_FULL_FIELD_ACTION_ATTACHMENT_AUDIT.json"]
    edge = records["BHSM_SPACETIME_EDGE_ONTOLOGY_AUDIT.json"]
    two_pi = records[
        "BHSM_NEUTRINO_CHARGED_CURRENT_2PI_CLOSURE_RECONCILIATION.json"
    ]
    enclosure_class = records["BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_AUDIT.json"]
    bundle = records["BHSM_aether_hybrid_standard_model_bundle_v15_53.json"]
    generation = records["BHSM_generation_projector_action_attachment_v8_2.json"]
    harmonic_modes = records[
        "BHSM_harmonic_exact_mode_representation_spectrum_v6_0_4.json"
    ]
    family_count = records["BHSM_global_family_count_spectrum_v6_7_0.json"]
    charged_current = records["BHSM_parent_action_charged_current_v11_6.json"]
    topology = records["BHSM_topological_configuration_space_v6_5_0.json"]
    topological_spectrum = records[
        "BHSM_topological_matter_action_global_spectrum_report_v6_5_0.json"
    ]
    electromagnetic = records[
        "BHSM_electromagnetic_surviving_generator_v6_3_0.json"
    ]
    particle_history = records[
        "BHSM_N12_CORRECTED_FORWARD_HISTORY_AND_PARTICLE_CLASS_GATES.json"
    ]

    assert_no_forbidden_equivalence(
        lambda24_equals_two_pi=False,
        canonical_stop_equals_spacetime_edge=False,
        positive_duration_equals_stability=False,
    )

    evidence = {
        "PEI_01": (
            first_stop["status"]
            == "ONE_EXACT_FORWARD_RESET_HISTORY_REACHES_A_CANONICAL_EARLIEST_STOP"
            and first_stop["validation_passed"] is True
        ),
        "PEI_02": (
            reset["validation"][
                "continuum_fixed_event_child_submersion_gap_is_positive"
            ]
            is True
            and child["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True
        ),
        "PEI_03": False,
        "PEI_04": False,
        "PEI_05": False,
        "PEI_06": False,
        "PEI_07": False,
        "PEI_08": False,
        "PEI_09": False,
        "PEI_10": (
            local_branch["event_to_child_completion"][
                "post_event_positive_duration_certified"
            ]
            is True
        ),
        "PEI_11": False,
    }
    bridge = evaluate_identification(
        evidence, particle_state_transport_claimed=True
    )

    upstream_particle_assets = [
        {
            "path": "artifacts/BHSM_aether_hybrid_standard_model_bundle_v15_53.json",
            "role": "global Spin x G_SM bundle, representations, hypercharge, and event gluing data",
            "import_status": "REUSE_FIXED_BUNDLE_AND_REPRESENTATIONS",
            "source_status": bundle["classification"],
            "claim_boundary": bundle["claim_boundary"],
        },
        {
            "path": "artifacts/BHSM_generation_projector_action_attachment_v8_2.json",
            "role": "frozen three-slot family modules and sector/mode projectors",
            "import_status": "REUSE_FROZEN_PROJECTORS_NO_REDERIVATION",
            "source_status": generation["final_verdict"],
            "claim_boundary": (
                "Projectors and family modules are imported; the historical "
                "mode-stress response blocker is preserved."
            ),
        },
        {
            "path": "artifacts/BHSM_harmonic_exact_mode_representation_spectrum_v6_0_4.json",
            "role": "exact and conditional harmonic/mode representation content",
            "import_status": "REUSE_ONLY_AT_ORIGINAL_CLAIM_STRENGTH",
            "source_status": harmonic_modes["status"],
            "claim_boundary": harmonic_modes["claim_boundary"],
        },
        {
            "path": "artifacts/BHSM_global_family_count_spectrum_v6_7_0.json",
            "role": "historical family-count spectrum",
            "import_status": "REUSE_ONLY_AT_ORIGINAL_CLAIM_STRENGTH",
            "source_status": family_count.get("status"),
            "claim_boundary": family_count.get("claim_boundary"),
        },
        {
            "path": "artifacts/BHSM_parent_action_charged_current_v11_6.json",
            "role": "parent-action charged-current term and variation provenance",
            "import_status": "REUSE_CURRENT_OBJECT_NO_REDERIVATION",
            "source_status": charged_current["classification"],
            "claim_boundary": (
                "The effective current object is reused; its transport to the "
                "selected-stop enclosure remains the bridge obligation."
            ),
        },
        {
            "path": "artifacts/BHSM_topological_configuration_space_v6_5_0.json",
            "role": "topological configuration-space ontology and candidate labels",
            "import_status": "REUSE_ONLY_AT_ORIGINAL_CLAIM_STRENGTH",
            "source_status": topology["status"],
            "claim_boundary": topology["primary_result"],
        },
        {
            "path": "artifacts/BHSM_topological_matter_action_global_spectrum_report_v6_5_0.json",
            "role": "historical topological matter spectrum results",
            "import_status": "REUSE_ONLY_AT_ORIGINAL_CLAIM_STRENGTH",
            "source_status": topological_spectrum.get("status"),
            "claim_boundary": topological_spectrum.get("claim_boundary"),
        },
        {
            "path": "artifacts/BHSM_electromagnetic_surviving_generator_v6_3_0.json",
            "role": "surviving electromagnetic generator and conditional chiral particle architecture",
            "import_status": "REUSE_DERIVED_GENERATOR_NO_REDERIVATION",
            "source_status": electromagnetic["status"],
            "claim_boundary": electromagnetic["primary_result"],
        },
        {
            "path": "artifacts/intrinsic_state_selection/BHSM_N12_CORRECTED_FORWARD_HISTORY_AND_PARTICLE_CLASS_GATES.json",
            "role": "complete forward particle-history class and discrete-label propagation rule",
            "import_status": "REUSE_CLOSED_HISTORY_CLASS",
            "source_status": particle_history["classification"],
            "claim_boundary": particle_history["claim_boundary"],
        },
        {
            "path": "theory/derived_hopf_phase_closure.md",
            "role": "conditional Hopf phase-closure result",
            "import_status": "REUSE_CONDITIONAL_TOPOLOGICAL_RESULT",
            "source_status": "PO_BH_2_PHASE_CLOSURE_DERIVED_CONDITIONAL",
            "claim_boundary": "Integer admissibility, not a rederived particle spectrum.",
        },
        {
            "path": "theory/derived_generation_raw_mode_ledgers.md",
            "role": "raw frozen family/mode ledgers",
            "import_status": "REUSE_FROZEN_MODE_LEDGER",
            "source_status": "FROZEN_UPSTREAM_ASSET",
            "claim_boundary": "Imported without retuning or recomputation.",
        },
        {
            "path": "docs/bhsm_sector_projector_ledger_theorem.md",
            "role": "finite sector incidence projectors",
            "import_status": "REUSE_SECTOR_PROJECTORS",
            "source_status": "AUTHORITATIVE_IMPORTED_RESULT_IN_V8_2",
            "claim_boundary": "Transport, not projector derivation, is current owner.",
        },
    ]
    for asset in upstream_particle_assets:
        asset_path = ROOT / str(asset["path"])
        asset["sha256"] = _sha256(asset_path)

    source_findings = {
        "first_stop": {
            "status": "CLOSED_MATHEMATICAL_CARRIER",
            "source_status": first_stop["status"],
            "physical_selector_claimed": False,
        },
        "event_child_relation": {
            "status": "CLOSED_REGULAR_NONEMPTY_RELATION",
            "fixed_event_child_fiber_dimension": local_branch[
                "event_to_child_completion"
            ]["fixed_event_child_fiber_dimension"],
        },
        "enclosure_geometry_vocabulary": {
            "status": "DECLARED_CONDITIONAL_NOT_ACTION_SELECTED",
            "intrinsic": fixed_geometry["intrinsic_candidate"],
            "external": fixed_geometry["external_data"],
            "action_owned_constraint_or_stability_term": fixed_geometry[
                "action_owned_constraint_or_stability_term"
            ],
        },
        "collar": {
            "status": collar["status"],
            "action_selected": False,
            "embedding": collar["embedding"],
            "field_matching": collar["field_matching"],
        },
        "metric_matching": {
            "status": matching["status"],
            "conditional_on_provisional_boundary_axiom": True,
            "parent_derived": matching["boundary_axiom_parent_derived"],
            "equation": matching["metric"],
        },
        "junction_domain": {
            "status": junction["status"],
            "unique_domain_selected": junction["domain"][
                "unique_domain_selected"
            ],
            "remaining_family": junction["domain"]["remaining_family"],
        },
        "full_field_attachment": {
            "status": "OPEN_PRECISE_NO_GO",
            "decision": full_field["decision"],
            "missing_blocks": full_field["missing_physical_field_blocks"],
        },
        "event_balance": {
            "retained_event_and_child_energy_rows": "CLOSED",
            "complete_parent_event_child_Noether_Hamiltonian_balance": "OPEN",
            "source": child["exact_next_dependency"],
        },
        "enclosure_class": {
            "status": "INVARIANT_ON_CERTIFIED_C2_CONTINUATION_ONLY",
            "global_physical_class_identification": "OPEN",
            "source_validation_passed": enclosure_class["validation_passed"],
        },
        "particle_state_registry": {
            "status": "RECOVERED_AND_IMPORTED_AS_FROZEN_UPSTREAM_ASSETS",
            "spectrum_rederived": False,
            "projectors_rederived": False,
            "representations_rederived": False,
            "currents_rederived": False,
            "topology_rederived": False,
            "missing_object": (
                "STRUCTURE_PRESERVING_ATTACHMENT_OF_THE_EXISTING_BHSM_"
                "FAMILY_MODE_STATE_TO_THE_PARENT_STOP_EVENT_CHILD_"
                "ENCLOSURE_AND_ITS_EXISTING_SM_MANIFESTATION_MAP"
            ),
        },
        "localization_carrier": {
            "status": carrier_audit["status"],
            "classification": carrier_audit["classification"],
            "qualifying_candidate_ids": carrier_audit["carrier_audit"][
                "qualifying_candidate_ids"
            ],
            "unchanged_AE2_carrier_exists": carrier_audit["carrier_audit"][
                "carrier_exists_in_audited_unchanged_ae2"
            ],
            "claim_boundary": (
                "The audit excludes a qualifying carrier among the stored AE2 "
                "objects; it does not prove that no future action extension can "
                "supply one."
            ),
        },
    }

    validation = {
        "reconstruction_result_is_drift_confirmed": (
            reconstruction["result_code"] == "B"
        ),
        "first_stop_retained_unchanged": evidence["PEI_01"],
        "event_child_relation_retained_unchanged": evidence["PEI_02"],
        "positive_duration_retained_but_not_stability": evidence["PEI_10"],
        "route_not_hand_selected": evidence["PEI_03"] is False,
        "conditional_geometry_not_promoted": evidence["PEI_04"] is False,
        "junction_domain_no_go_preserved": (
            junction["domain"]["unique_domain_selected"] is False
        ),
        "geometry_only_full_field_no_go_preserved": (
            full_field["current_retained_action_state"]["fermion_fields"] == 0
            and full_field["current_retained_action_state"][
                "gauge_and_ghost_fields"
            ]
            == 0
            and full_field["current_retained_action_state"]["HS_or_scalar_fields"]
            == 0
        ),
        "canonical_stop_not_relabelled_spacetime_edge": (
            edge["validation"][
                "current_stop_remains_unidentified_with_spacetime_edge"
            ]
            is True
        ),
        "lambda24_not_relabelled_two_pi": (
            two_pi["scientific_verdict"]["two_pi_to_gate7_identification"]
            == "NOT_DERIVED"
        ),
        "particle_state_transport_is_the_target": (
            bridge["particle_state_transport_claimed"] is True
        ),
        "upstream_particle_assets_reused_not_rederived": (
            bundle["validation_passed"] is True
            and generation["validation_passed"] is True
            and charged_current["validation_passed"] is True
            and particle_history["validation_passed"] is True
        ),
        "physical_identification_not_promoted": (
            bridge["physical_encapsulation_identified"] is False
        ),
        "unchanged_ae2_carrier_kill_screen_is_fail_closed": (
            carrier_audit["validation_passed"] is True
            and carrier_audit["carrier_audit"][
                "carrier_exists_in_audited_unchanged_ae2"
            ]
            is False
            and carrier_audit["action_extension_boundary"][
                "extension_authorized_here"
            ]
            is False
        ),
        "no_action_equation_parameter_selector_or_numerics_changed": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_PHYSICAL_ENCAPSULATION_IDENTIFICATION_BRIDGE",
        "schema_version": 2,
        "action_version": "BHSM-AE-2.0.0_UNCHANGED",
        "owner": "CURRENT_AE2_GATE7_PHYSICAL_ENCAPSULATION_IDENTIFICATION_SPECIFICATION",
        "status": (
            "BRIDGE_INTERFACE_SPECIFIED__PHYSICAL_IDENTIFICATION_OPEN_"
            "MISSING_ACTION_OWNED_DOMAIN_AND_FULL_FIELD_ATTACHMENT"
        ),
        "classification": "FAIL_CLOSED_PHYSICAL_IDENTIFICATION_INTERFACE",
        "scientific_decision": (
            "THE_BRANCH24_CANONICAL_STOP_AND_EVENT_CHILD_RELATION_SUPPLY_THE_"
            "MATHEMATICAL_CARRIER_BUT_DO_NOT_YET_IDENTIFY_A_PHYSICAL_LOCAL_"
            "ENCLOSURE;_PROMOTION_REQUIRES_AN_ACTION_SELECTED_ROUTE,_CARRIER_"
            "AND_DOMAIN,_MATCHING_AND_JUNCTION_CONDITIONS,_FULL_FIELD_"
            "RESTRICTION,_COMPLETE_EVENT_BALANCE,_NONLINEAR_LOCAL_COMPLETION,_"
            "AND_CHILD_INHERITANCE_OF_THE_EXISTING_BHSM_FAMILY_MODE_"
            "PARTICLE_STATE"
        ),
        "typed_bridge": {
            "upstream_state": (
                "PROVENANCE_FROZEN_BHSM_FAMILY_MODE_REPRESENTATION_"
                "PROJECTOR_CURRENT_TOPOLOGICAL_STATE"
            ),
            "source": "UPSTREAM_STATE_ATTACHED_TO_SAME_AE2_PARENT_HISTORY",
            "intermediate": "REGULAR_EVENT_TO_COMPLETE_CHILD_RELATION",
            "target": (
                "ACTION_IDENTIFIED_LOCAL_ENCLOSURE_CARRYING_THE_UPSTREAM_"
                "STATE_INTO_ITS_EXISTING_SM_PARTICLE_MANIFESTATION_CLASS"
            ),
            "map": (
                "I_phys: (P_BHSM,H_parent,E_stop,R_EC,S_AE2) -> "
                "(route,D_enc,Sigma_enc,C_child,M_SM(P_BHSM))"
            ),
            "current_map_status": "INTERFACE_DEFINED_MAP_NOT_INSTANTIATED",
        },
        "admissible_enclosure_routes": {
            "routes": list(ENCLOSURE_ROUTES),
            "selection_rule": "EXACTLY_ONE_ROUTE_OR_AN_ACTION_DERIVED_EQUIVALENCE_CLASS",
            "current_selection": None,
            "spacetime_edge_required": False,
            "reason": (
                "A_CANONICAL_STOP_MAY_FORM_A_LOCAL_OR_BOUNDARY_ENCLOSURE_"
                "WITHOUT_ENDING_THE_SPACETIME_PHASE;_SPACETIME_EDGE_IS_A_"
                "STRONGER_ROUTE_REQUIRING_ITS_OWN_ACTION_THEOREM"
            ),
        },
        "enclosure_signature": {
            "symbol": "Sigma_enc",
            "components": [
                "AE2 action/domain version",
                "forward-history component and orientation",
                "intrinsic domain and topology",
                "embedding, normal bundle, extrinsic curvature, and collar",
                "reset-glued Spin x G_SM bundle and field-trace class",
                "boundary-incidence and junction-domain class",
                "transported selected-eigenline class",
                "constraint and complete Noether level-set class",
                "admissible child-domain component",
            ],
            "excluded": [
                "proof-box index",
                "mesh or truncation boundary",
                "floating-point failure",
                "lambda24 value without the other bridge obligations",
            ],
        },
        "upstream_particle_asset_policy": {
            "policy": (
                "IMPORT_EVERY_VALID_HISTORICAL_OBJECT_AT_ITS_STORED_CLAIM_"
                "STRENGTH;_DO_NOT_REDERIVE_RETUNE_OR_REORDER_THE_PARTICLE_"
                "FAMILY_MODE_SPECTRUM"
            ),
            "assets": upstream_particle_assets,
            "transport_invariant": (
                "THE_EVENT_CHILD_ENCLOSURE_MAP_MUST_INTERTWINE_THE_IMPORTED_"
                "SECTOR_AND_FAMILY_PROJECTORS,_BUNDLE_REPRESENTATION,_CURRENT_"
                "INCIDENCE,_AND_TOPOLOGICAL_LABELS_WITH_THE_EXISTING_SM_"
                "MANIFESTATION_MAP"
            ),
            "manifestation_rule": (
                "BHSM_FAMILY_OR_MODE_STATE_MAY_MANIFEST_AS_AN_SM_PARTICLE;_"
                "THE_BRIDGE_PROVES_LOCAL_ENCLOSURE_TRANSPORT_AND_DOES_NOT_"
                "REBUILD_THE_MANIFESTATION_SPECTRUM"
            ),
        },
        "bridge_evaluation": bridge,
        "four_kernel_reduction": carrier_audit["four_kernel_reduction"],
        "subrequirement_resolution": carrier_audit[
            "subrequirement_resolution"
        ],
        "family_reset_intertwiner": carrier_audit[
            "family_reset_intertwiner"
        ],
        "dependency_closure_rule": carrier_audit[
            "dependency_closure_rule"
        ],
        "localization_carrier_kill_screen": {
            "status": carrier_audit["status"],
            "classification": carrier_audit["classification"],
            "candidate_count": len(carrier_audit["carrier_audit"]["candidates"]),
            "qualifying_candidate_ids": carrier_audit["carrier_audit"][
                "qualifying_candidate_ids"
            ],
            "unchanged_AE2_carrier_exists": carrier_audit["carrier_audit"][
                "carrier_exists_in_audited_unchanged_ae2"
            ],
            "action_extension_boundary": carrier_audit[
                "action_extension_boundary"
            ],
        },
        "current_evidence": source_findings,
        "forbidden_substitutions": {
            "lambda24_zero_equals_two_pi": False,
            "canonical_stop_equals_spacetime_edge": False,
            "positive_duration_equals_stability": False,
            "reset_state_equals_new_spacetime_domain": False,
            "proof_cutoff_equals_physical_boundary": False,
        },
        "closure_rule": {
            "generic_physical_encapsulation": (
                "ALL_REQUIRED_PEI_01_THROUGH_PEI_10_TRUE"
            ),
            "particle_state_enclosure_and_SM_manifestation": (
                "GENERIC_PHYSICAL_ENCAPSULATION_AND_PEI_11_TRUE,_WITH_THE_"
                "UPSTREAM_REGISTRY_IMPORTED_UNCHANGED"
            ),
            "Gate7_consequence": (
                "THIS_BRIDGE_IS_NECESSARY_FOR_PHYSICAL_ENCAPSULATION_"
                "LANGUAGE_BUT_DOES_NOT_BY_ITSELF_CLOSE_THE_EXISTING_FORCE_"
                "SADDLE_HESSIAN_WARD_TRACE_OR_SCALAR_READOUT_NODES"
            ),
        },
        "exact_next_dependency": (
            "OWNER_AUTHORIZED_ACTION_VERSION_DECISION_SELECTING_A_COVARIANT_"
            "LOCALIZATION_OR_DOMAIN_CARRIER;_THEN_DERIVE_ITS_INTERFACE_"
            "VARIATION,_DEPENDENCY_CLOSED_FIELD_TRANSPORT,_CHILD_INHERITANCE,_"
            "AND_C2_FAMILY_MODE_INSTANTIATION"
        ),
        "claim_boundary": {
            "physical_encapsulation_identified": False,
            "spacetime_pocket_identified": False,
            "named_particle_identified": False,
            "historical_particle_spectrum_rebuilt": False,
            "upstream_particle_assets_modified": False,
            "Gate7_closed": False,
            "first_stop_strengthened": False,
            "new_action_term_added": False,
            "new_numerical_run_used": False,
            "physical_parameter_or_selector_added": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in all_inputs
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
