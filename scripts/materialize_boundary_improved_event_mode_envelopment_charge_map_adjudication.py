"""Materialize the boundary-improved event/envelopment charge obstruction."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.boundary_improved_event_mode_envelopment_charge_map_adjudication import (  # noqa: E402
    ACTION_VERSION,
    AE4R_CLASS,
    CHG_CLASS,
    CLASSIFICATION,
    DOMH_CLASS,
    ENVH_CLASS,
    EXACT_NEXT_OBJECT,
    MODEE_CLASS,
    REF_CLASS,
    XI_CLASS,
    adjudication_payload,
)


TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_BOUNDARY_IMPROVED_EVENT_MODE_ENVELOPMENT_CHARGE_MAP_ADJUDICATION.json"
)
INPUTS = (
    ROOT / "src/bhsm/interface/boundary_improved_event_mode_envelopment_charge_map_adjudication.py",
    ROOT / "scripts/materialize_boundary_improved_event_mode_envelopment_charge_map_adjudication.py",
    ROOT / "tests/test_boundary_improved_event_mode_envelopment_charge_map_adjudication.py",
    ROOT / "theory/bhsm_boundary_improved_event_mode_envelopment_charge_map_adjudication.md",
    ROOT / "src/bhsm/interface/master_action/terms.py",
    ROOT / "src/bhsm/interface/master_action/variations.py",
    ROOT / "src/bhsm/interface/completion/support_covariant_phase_space_v11_2.py",
    ROOT / "src/bhsm/interface/completion/boundary_variational_domain_v11_2.py",
    ROOT / "src/bhsm/interface/nonfermion_relative_boundary_variation.py",
    ROOT / "src/bhsm/interface/action_extension_global_spin_reset_ae2.py",
    ROOT / "src/bhsm/interface/ae3_reciprocal_join_localization.py",
    ROOT / "src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py",
    ROOT / "src/bhsm/interface/relative_diffeomorphism_generator_charge_adjudication.py",
    ROOT / "src/bhsm/interface/energetically_admissible_encapsulation_carrier_adjudication.py",
    ROOT / "theory/n12_child_boundary_hamiltonian_ownership.md",
    ROOT / "theory/n12_ae2_child_boundary_hamiltonian_non_supersession.md",
    ROOT / "artifacts/action_extension/BHSM_RELATIVE_DIFFEOMORPHISM_GENERATOR_CHARGE_ADJUDICATION.json",
    ROOT / "artifacts/action_extension/BHSM_ENERGETICALLY_ADMISSIBLE_ENCAPSULATION_CARRIER_ADJUDICATION.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CHILD_BOUNDARY_HAMILTONIAN_OWNERSHIP_GATE.json",
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))

    result = adjudication_payload()
    theta = result["complete_presymplectic_potential"]
    generator = result["generator"]
    charge = result["charge_differentiability_integrability"]
    reference = result["reference"]
    mode = result["event_and_mode_charge"]
    child = result["child_seam_and_increment"]
    domain = result["common_domain"]
    ae4 = result["AE4_impedance_and_crossing"]
    claims = result["claim_boundary"]
    validation = {
        "all_thirteen_registered_terms_audited": result["registered_action"]["registered_term_count"] == 13,
        "registered_action_not_promoted_to_closed_parent": not result["registered_action"]["single_closed_parent_action"],
        "nine_sector_rows_present": len(result["sector_contribution_ledger"]) == 9,
        "sector_rows_do_not_claim_common_charge_domains": all(
            not row["common_event_child_domain"]
            and not row["charge_assembler_available"]
            for row in result["sector_contribution_ledger"]
        ),
        "complete_Theta_fails_closed": (
            theta["complete_Theta_event"] is None
            and theta["complete_Theta_child"] is None
            and theta["complete_relative_Theta"] is None
            and not theta["complete_boundary_presymplectic_potential_derived"]
        ),
        "XI5_stops_at_domain_tangency": (
            generator["classification"] == XI_CLASS == "XI5"
            and generator["common_action_owned_generator"] is None
            and not generator["tangent_to_active_domain"]
            and generator["stop_charge_comparison_here"]
        ),
        "CHG4_precedes_integrability_and_improvement": (
            charge["classification"] == CHG_CLASS == "CHG4"
            and not charge["functional_differential_exists_on_current_domain"]
            and not charge["integrability_test_reached"]
            and charge["required_improvement_B_xi"] is None
            and charge["B_xi_is_zero"] is None
        ),
        "REF5_preserves_absent_zero_point": (
            reference["classification"] == REF_CLASS == "REF5"
            and reference["usable_common_reference"] is None
        ),
        "MODEE5_preserves_absent_physical_projector": (
            mode["mode_classification"] == MODEE_CLASS == "MODEE5"
            and mode["initiating_mode_projector_P_mode"] is None
            and mode["initiating_mode_charge_H_xi_mode"] is None
        ),
        "available_charge_not_fabricated": (
            result["available_charge"]["value"] is None
            and not result["available_charge"]["definition_earned"]
            and not result["available_charge"]["candidate_subtraction_formula_adopted"]
        ),
        "ENVH5_preserves_absent_child_and_increment_charges": (
            child["classification"] == ENVH_CLASS == "ENVH5"
            and child["H_xi_child_plus_seam"] is None
            and child["Delta_H_xi_child_plus_seam"] is None
        ),
        "DOMH4_preserves_absent_comparison_domain": (
            domain["classification"] == DOMH_CLASS == "DOMH4"
            and domain["D_H"] is None
            and domain["sectorwise_domains_exist"]
        ),
        "AE4R5_blocks_ratio_and_crossing": (
            ae4["classification"] == AE4R_CLASS == "AE4R5"
            and ae4["rho_hold_modern_value"] is None
            and ae4["first_future_crossing_function"] is None
            and not ae4["root_search_performed"]
        ),
        "conservation_does_not_invent_children": (
            result["conservation_and_branching"]["proposed_child_charge_tests_completed"] == 0
            and not result["conservation_and_branching"]["multiple_children_forced_by_charge_analysis"]
        ),
        "N12_rank_firewall_preserved": (
            result["N12_rank"]["actual_new_independent_rank"] == 0
            and result["N12_rank"]["residual_before_time_quotient"] == 67
            and result["N12_rank"]["residual_after_time_quotient"] == 66
        ),
        "exact_prior_blocker_remains_next": result["exact_next_object"]["object"] == EXACT_NEXT_OBJECT,
        "claim_boundaries_preserved": (
            not claims["H_XI_MODE_AVAILABLE_DERIVED"]
            and not claims["DELTA_H_XI_CHILD_PLUS_SEAM_DERIVED"]
            and not claims["RESPONSE_FUNCTION_SELECTED"]
            and not claims["FROZEN_PREDICTIONS_CHANGED"]
            and not claims["GATE7_PROMOTED"]
            and not claims["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_BOUNDARY_IMPROVED_EVENT_MODE_ENVELOPMENT_CHARGE_MAP_ADJUDICATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "scientific_result": (
            "THE_REQUESTED_CHARGE_MAP_IS_RIGOROUSLY_OBSTRUCTED_AT_XI5_AND_"
            "CHG4_BECAUSE_NO_COMMON_EVENT_CHILD_GENERATOR_IS_TANGENT_TO_AN_"
            "ACTION_OWNED_FULL_FIELD_MOVING_TRACE_DOMAIN;_EVENT_MODE_AVAILABLE_"
            "AND_CHILD_PLUS_SEAM_INCREMENT_CHARGES_REMAIN_UNDEFINED"
        ),
        "adjudication": result,
        "classifications": {
            "xi": XI_CLASS,
            "charge": CHG_CLASS,
            "reference": REF_CLASS,
            "mode_energy": MODEE_CLASS,
            "envelopment_charge": ENVH_CLASS,
            "common_domain": DOMH_CLASS,
            "AE4_ratio": AE4R_CLASS,
        },
        "VALIDATED": [
            "COMPLETE_SECTORWISE_BOUNDARY_VARIATION_LEDGER",
            "ABSENCE_OF_COMPLETE_EVENT_CHILD_AND_RELATIVE_THETA",
            "ABSENCE_OF_A_COMMON_TANGENT_ACTION_OWNED_GENERATOR",
            "XI5_CHG4_REF5_MODEE5_ENVH5_DOMH4_AE4R5",
            "NO_EX_NIHILO_FIREWALL_WITH_ZERO_TESTED_CHILD_LEDGERS",
            "ZERO_NEW_N12_RANK",
        ],
        "INVALIDATED": [
            "ASSEMBLING_DISCONNECTED_LEVELWISE_FORMS_INTO_A_COMPLETE_THETA",
            "USING_COORDINATE_TIME_RETARDED_BOUNDARY_VALUE_EVENT_EIGENLINE_OR_HOPF_ROTOR_AS_XI",
            "SETTING_B_XI_TO_ZERO_BEFORE_DIFFERENTIABILITY",
            "TREATING_ACTION_NORMALIZATION_AS_REFERENCE_SUBTRACTION",
            "FORCING_THE_AE4_RATIO_OR_CROSSING",
        ],
        "REDUNDANT": [
            "RECOMPUTING_THE_FORMAL_TWO_SIDED_DIFFEO_ACTION",
            "REPEATING_AE2_OR_AE3_INTERNAL_CANCELLATION",
            "TESTING_REFERENCE_CHOICES_BEFORE_A_DIFFERENTIABLE_GENERATOR",
            "NUMERICAL_ROOT_SEARCH_FOR_AN_UNDEFINED_CROSSING_FUNCTION",
        ],
        "OPEN": [EXACT_NEXT_OBJECT],
        "DECISION_POWER": (
            "CHARGE_CONSTRUCTION_STOPS_AT_DOMAIN_TANGENCY_BEFORE_COUNTERTERM_"
            "REFERENCE_MODE_PROJECTION_OR_NUMERICAL_EVALUATION"
        ),
        "EXACT_NEXT_OBJECT": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "source_hashes_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in INPUTS
        },
    }


def main() -> Path:
    payload = build_payload()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    main()
