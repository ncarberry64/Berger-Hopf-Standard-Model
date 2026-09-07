"""Materialize the relative diffeomorphism generator/charge adjudication."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.relative_diffeomorphism_generator_charge_adjudication import (  # noqa: E402
    ACTION_VERSION,
    CHARGE_CLASS,
    CLASSIFICATION,
    DIFFERENTIABILITY_CLASS,
    EXACT_NEXT_OBJECT,
    STATUS,
    candidate_relative_generator,
    claim_boundary,
    constraint_noether_ownership,
    decision_power_ledger,
    differentiability_and_charge_verdict,
    hopf_rotor_charge_adjudication,
    infinitesimal_action_and_trace_witness,
    infinitesimal_relative_transformation,
    outcome_and_downstream_status,
    presymplectic_potential_inventory,
    reset_trace_domain_independence_witness,
)


TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_RELATIVE_DIFFEOMORPHISM_GENERATOR_CHARGE_ADJUDICATION.json"
)
MODULE = ROOT / (
    "src/bhsm/interface/"
    "relative_diffeomorphism_generator_charge_adjudication.py"
)
SCRIPT = Path(__file__).resolve()
THEORY = ROOT / "theory/bhsm_relative_diffeomorphism_generator_charge_adjudication.md"
TEST = ROOT / "tests/test_relative_diffeomorphism_generator_charge_adjudication.py"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".py", ".md", ".json"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.ndarray):
        return _canonical(value.tolist())
    if isinstance(value, np.complexfloating):
        value = complex(value)
    if isinstance(value, complex):
        if not (math.isfinite(value.real) and math.isfinite(value.imag)):
            raise ValueError("non-finite complex value")
        return {"real": _canonical(value.real), "imag": _canonical(value.imag)}
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float value")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True, allow_nan=False) + "\n"


def build_payload() -> dict[str, Any]:
    theta = presymplectic_potential_inventory()
    infinitesimal = infinitesimal_relative_transformation()
    witness = infinitesimal_action_and_trace_witness()
    independence = reset_trace_domain_independence_witness()
    generator = candidate_relative_generator()
    charge = differentiability_and_charge_verdict()
    hopf = hopf_rotor_charge_adjudication()
    noether = constraint_noether_ownership()
    outcome = outcome_and_downstream_status()
    decisions = decision_power_ledger()
    claims = claim_boundary()

    source_paths = (
        "src/bhsm/interface/master_action/terms.py",
        "src/bhsm/interface/completion/support_covariant_phase_space_v11_2.py",
        "src/bhsm/interface/completion/boundary_variational_domain_v11_2.py",
        "src/bhsm/interface/completion/attachment_boundary_core_domain_v11_3.py",
        "src/bhsm/interface/completion/intrinsic_full_preimage_dynamical_momentum_gate_v14_90.py",
        "src/bhsm/interface/action_extension_global_spin_reset_ae2.py",
        "src/bhsm/interface/nonfermion_relative_boundary_variation.py",
        "src/bhsm/interface/ae3_reciprocal_join_localization.py",
        "src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py",
        "src/bhsm/interface/aether_moving_interface_transfer_v15_12.py",
        "src/bhsm/interface/aether_parent_child_relative_rotor_v15_36.py",
        "scripts/audit_n12_radial_diffeo_noether_compatibility.py",
        "theory/n12_child_boundary_hamiltonian_ownership.md",
        "theory/n12_ae2_child_boundary_hamiltonian_non_supersession.md",
        "artifacts/intrinsic_state_selection/BHSM_N12_CHILD_BOUNDARY_HAMILTONIAN_OWNERSHIP_GATE.json",
        "artifacts/n12_continuum_source_compatibility_checkpoint/BHSM_N12_RADIAL_DIFFEO_NOETHER_COMPATIBILITY_AUDIT.json",
        "artifacts/action_extension/BHSM_GAUGE_CONNECTION_RESET_BUNDLE_LIFT_ADJUDICATION.json",
        MODULE.relative_to(ROOT).as_posix(),
        SCRIPT.relative_to(ROOT).as_posix(),
        THEORY.relative_to(ROOT).as_posix(),
        TEST.relative_to(ROOT).as_posix(),
    )
    hashes = {
        source: _sha256(ROOT / source)
        for source in sorted(source_paths)
        if (ROOT / source).is_file()
    }
    validation = {
        "all_master_action_terms_traced": len(theta["master_action_terms_traced"]) == 13,
        "sectorwise_potentials_not_promoted_to_complete_Theta": (
            theta["complete_Theta_event"] is None
            and theta["complete_Theta_child"] is None
            and theta["complete_relative_Theta"] is None
        ),
        "AE2_and_AE4_add_no_spatial_boundary_generator": (
            not theta["reset_and_seam"]["AE2_spatial_base_pullback_present"]
            and not theta["reset_and_seam"]["AE4_adds_boundary_counterterm"]
        ),
        "algebraic_attachment_adds_zero_Theta_and_flux": (
            theta["reset_and_seam"]["algebraic_attachment_Theta"] == 0
            and theta["reset_and_seam"]["algebraic_attachment_flux"] == 0
        ),
        "infinitesimal_two_sided_action_derived": (
            infinitesimal["infinitesimal_attachment"].startswith("delta_F")
            and infinitesimal["stabilizer_delta_F"] == 0
        ),
        "finite_difference_linearization_verified": (
            witness["finite_difference_residual"] < 1.0e-9
            and witness["analytic_relative_generator_norm"] > 0.0
            and witness["stabilizer_generator_norm"] < 1.0e-12
        ),
        "formal_F_dependent_trace_equivariance_verified": (
            witness["formal_trace_equivariance_residual"] < 1.0e-12
            and not witness["witness_instantiates_current_BHSM_reset_graph"]
        ),
        "moving_trace_domain_nonuniqueness_is_independent": (
            independence["nonfermion_different_first_field_jets"]
            and independence["both_graphs_maximal_isotropic"]
            and independence["both_graphs_cancel_fixed_field_variations"]
            and independence["hypothetical_boundary_potentials_differ"]
            and not independence["self_adjointness_selects_trace_unitary"]
            and independence["inequivalent_conservative_transfer_spectra"]
        ),
        "coefficient_locked_corner_does_not_select_matter_graph": (
            independence["moving_gravity_corner_coefficient_locked"]
            and not independence["moving_gravity_selects_matter_domain"]
        ),
        "varied_seam_embedding_absent_from_active_action": (
            independence["seam_embedding_action_owned"] is False
            and independence["seam_embedding_canonical_momentum"] is None
        ),
        "generator_failure_order_is_explicit": (
            generator["failure_order"][0]
            == "F_B_IS_NOT_A_VARIED_CONFIGURATION_ARGUMENT"
            and not generator["delta_xi_rel_is_a_vector_field_on_current_reset_domain"]
            and generator["Hamiltonian_generator"] is None
        ),
        "G4_classification_earned_before_later_G3_choice": (
            charge["differentiability_class"] == DIFFERENTIABILITY_CLASS == "G4"
            and charge["G4"]
            and charge["later_boundary_ensemble_choice_may_be_G3"]
            and charge["later_G3_not_reached"]
        ),
        "event_child_and_relative_charges_fail_closed": (
            charge["event_charge_Q_e"] is None
            and charge["child_charge_Q_c"] is None
            and charge["relative_charge_Q_rel"] is None
            and charge["charge_class"] == CHARGE_CLASS == "U"
        ),
        "gauge_kernel_not_confused_with_stabilizer": (
            charge["charge_kernel"] is None
            and "NOT_COMPARABLE" in charge[
                "gauge_kernel_relation_to_fixed_F_stabilizer"
            ]
        ),
        "Hopf_rotor_classified_without_boundary_charge_promotion": (
            hopf["J_total"] == 0.0
            and hopf["positive_energy"]
            and not hopf["is_event_child_attachment_boundary_charge_Q_rel"]
        ),
        "within_side_Noether_identity_not_promoted_to_attachment_generator": (
            not noether["N12_identity_moves_F_B"]
            and not noether["existing_first_class_constraint_generates_relative_attachment"]
            and not noether["relative_Noether_identity_owned"]
        ),
        "Outcome_D_retained_at_sharper_boundary": (
            outcome["selected_outcome"] == "D"
            and outcome["D_is_sharper_than_prior"]
            and outcome["exact_next_object"] == EXACT_NEXT_OBJECT
        ),
        "no_unearned_BRST_or_reduction": (
            not outcome["relative_BRST_extension_earned"]
            and not outcome["new_relative_ghost_added"]
            and outcome["reduced_reset"] is None
        ),
        "decision_power_classified_for_every_new_result": all(
            row["distinguishes_A_B_C_D"] for row in decisions
        ),
        "claim_boundaries_preserved": (
            not claims["event_charge_evaluated"]
            and not claims["child_charge_evaluated"]
            and not claims["relative_charge_evaluated"]
            and not claims["frozen_predictions_changed"]
            and not claims["FULL_BHSM_COMPLETE"]
        ),
        "exact_next_object_refined": (
            generator["prior_blocker"] != EXACT_NEXT_OBJECT
            and generator["refined_first_blocker"] == EXACT_NEXT_OBJECT
            and claims["exact_next_object"] == EXACT_NEXT_OBJECT
        ),
    }
    payload = {
        "artifact": "BHSM_RELATIVE_DIFFEOMORPHISM_GENERATOR_CHARGE_ADJUDICATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "status": STATUS,
        "presymplectic_potential": theta,
        "infinitesimal_relative_transformation": infinitesimal,
        "infinitesimal_witness": witness,
        "reset_trace_domain_independence": independence,
        "candidate_generator": generator,
        "differentiability": charge,
        "event_charge_Q_e": charge["event_charge_Q_e"],
        "child_charge_Q_c": charge["child_charge_Q_c"],
        "relative_charge_Q_rel": charge["relative_charge_Q_rel"],
        "charge": charge,
        "Hopf_rotor": hopf,
        "constraint_Noether_ownership": noether,
        "BRST_consequence": {
            "gauge_status_earned": False,
            "relative_BRST_extension": None,
            "new_ghost_added": False,
        },
        "identity_fixing": "NOT_AUTHORIZED",
        "outcome": outcome,
        "downstream": {
            key: outcome[key]
            for key in (
                "reduced_reset", "connection_curvature_quotient_classes",
                "beta", "generator_propagation", "graph_jets",
                "S1", "S2", "S3", "S4", "full_field_action_attachment",
            )
        },
        "VALIDATED": [
            "THE_FORMAL_INFINITESIMAL_ACTION_IS_delta_F=xi_c_COMPOSE_F-F_STAR_xi_e",
            "THE_STABILIZER_IS_EXACTLY_THE_ZERO_delta_F_SUBALGEBRA",
            "SECTORWISE_CANONICAL_PAIRS_GREEN_FORMS_AND_ZERO_SEAM_TERMS_ARE_INVENTORIED",
            "THE_COMPLETE_Theta_e_Theta_c_AND_RELATIVE_Theta_ARE_NOT_OWNED",
            "THE_CURRENT_AE2_TRACE_GRAPH_HAS_NO_SPATIAL_F_B_PULLBACK",
            "AE4_ADDS_A_RETARDED_DOMAIN_BUT_NO_RELATIVE_BOUNDARY_COUNTERTERM",
            "TWO_BRST_COMPATIBLE_MAXIMAL_ISOTROPIC_NONFERMION_GRAPH_JETS_REMAIN_ADMISSIBLE",
            "COEFFICIENT_LOCKED_GHY_HAYWARD_GRAVITY_DOES_NOT_SELECT_THE_MATTER_TRANSFER_GRAPH",
            "F_B_IS_NOT_A_VARIED_CONFIGURATION_ARGUMENT_OF_THE_ACTIVE_RESET_ACTION",
            "THE_RELATIVE_VECTOR_IS_NOT_TANGENT_DEFINED_ON_THE_ACTIVE_RESET_DOMAIN",
            "DIFFERENTIABILITY_CLASS_G4",
            "CHARGE_CLASS_U",
            "OUTCOME_D_RETAINED_AT_A_STRICTLY_SHARPER_DOMAIN_BOUNDARY",
        ],
        "INVALIDATED": [
            "ASSEMBLING_A_COMPLETE_RELATIVE_Theta_FROM_DISCONNECTED_SECTORWISE_GREEN_FORMS",
            "USING_THE_SMOOTH_AE3_ENCLOSURE_GHY_CANCELLATION_AT_THE_EVENT_CHILD_RESET",
            "USING_THE_HAYWARD_CORNER_PAIR_TO_SELECT_A_MATTER_OR_GFHS_TRACE_GRAPH",
            "TREATING_THE_AE4_RETARDED_SCHUR_DOMAIN_AS_A_SPATIAL_F_B_ACTION",
            "CALLING_THE_WITHIN_SIDE_ENDPOINT_FIXED_RADIAL_WARD_IDENTITY_A_RELATIVE_ATTACHMENT_GENERATOR",
            "CALLING_THE_POSITIVE_HOPF_ROTOR_ENERGY_THE_MISSING_BOUNDARY_Q_REL",
            "CANCELLING_Q_E_AND_Q_C_BEFORE_EITHER_CHARGE_IS_DEFINED",
            "ADDING_A_RELATIVE_DIFFEO_GHOST_BEFORE_A_GAUGE_KERNEL_EXISTS",
            "CHOOSING_A_BOUNDARY_ENSEMBLE_TO_FORCE_ZERO_CHARGE",
        ],
        "REDUNDANT": [
            "OBJECTWISE_TENSORIAL_COVARIANCE_REPROOFS",
            "RECOMPUTING_THE_POSITIVE_ENERGY_HOPF_ROTOR",
            "REPEATING_THE_FINITE_ORBIT_STABILIZER_AUDIT",
        ],
        "OPEN": [EXACT_NEXT_OBJECT],
        "DECISION_POWER": decisions,
        "EXACT_NEXT_OBJECT": EXACT_NEXT_OBJECT,
        "after_exact_next_object": [
            "ASSEMBLE_THE_COMPLETE_Theta_e_AND_Theta_c_ON_THAT_MOVING_GRAPH",
            "TEST_WHICH_BOUNDARY_POLARIZATION_OR_COUNTERTERM_IS_ACTION_SELECTED",
            "DERIVE_Q_e_Q_c_AND_Q_rel_WITHOUT_SILENT_CANCELLATION",
            "ONLY_THEN_CLASSIFY_Z_K_OR_N_AND_ANY_GAUGE_KERNEL",
        ],
        "claims": claims,
        "empirical_inputs": [],
        "source_sha256": hashes,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    payload["validated"] = payload["VALIDATED"]
    payload["invalidated"] = payload["INVALIDATED"]
    payload["redundant"] = payload["REDUNDANT"]
    payload["open"] = payload["OPEN"]
    payload["decision_power"] = payload["DECISION_POWER"]
    return payload


def main() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(build_payload()), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(main())
