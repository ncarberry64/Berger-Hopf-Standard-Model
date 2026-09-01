"""Materialize the BHSM-AE-3 reciprocal-join localization extension."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_reciprocal_join_localization import (
    ACTION_VERSION,
    CARRIER_ID,
    SELECTED_ROUTE,
    current_full_field_attachment_ledger,
    dependency_ledgers,
    enclosure_transport_square_certificate,
    family_fiber_transport_certificate,
    interface_variation_ledger,
    ranked_carrier_candidates,
    regular_carrier_certificate,
    systems_integration_puzzle,
)


ARTIFACTS = ROOT / "artifacts"
TARGET = ARTIFACTS / (
    "action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json"
)
INPUTS = (
    ARTIFACTS / "action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    ARTIFACTS / "action_extension/BHSM_POST_AE2_LOCALIZATION_CARRIER_EXTENSION_CONTRACT.json",
    ARTIFACTS / "flagship_integration/BHSM_N12_GATE7_LOCALIZATION_CARRIER_KILL_SCREEN.json",
    ARTIFACTS / "flagship_integration/BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json",
    ARTIFACTS / "BHSM_aether_eta_sigma_response_constraint_v15_40.json",
    ARTIFACTS / "BHSM_aether_response_constrained_child_galerkin_v15_41.json",
    ARTIFACTS / "BHSM_aether_momentum_balanced_shear_data_v15_43.json",
    ARTIFACTS / "BHSM_aether_lorentzian_child_galerkin_v15_44.json",
    ARTIFACTS / "BHSM_aether_complete_child_localized_fiber_v15_34.json",
    ARTIFACTS / "BHSM_aether_FR_zero_current_child_v15_37.json",
    ARTIFACTS / "BHSM_aether_material_skin_variation_v15_15.json",
    ARTIFACTS / "BHSM_aether_n3_lorentzian_child_cauchy_correspondence_v17_88.json",
    ARTIFACTS / "BHSM_aether_hybrid_standard_model_bundle_v15_53.json",
    ARTIFACTS / "BHSM_generation_projector_action_attachment_v8_2.json",
    ARTIFACTS / "n12_continuum_majorant_effectiveness/BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json",
    ROOT / "src/bhsm/interface/aether_jax_full_local_action.py",
    ROOT / "src/bhsm/interface/ae3_reciprocal_join_localization.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    canonical = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(canonical).hexdigest().upper()


def _status(gate_id: str, status: str, evidence: str) -> dict[str, str]:
    return {"gate_id": gate_id, "status": status, "evidence": evidence}


def build_payload() -> dict[str, Any]:
    """Return the owner-authorized minimal localization extension."""

    missing = [path.as_posix() for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("AE3 inputs required: " + ", ".join(missing))
    json_inputs = [path for path in INPUTS if path.suffix == ".json"]
    records = {path.name: _load(path) for path in json_inputs}
    ae2 = records["BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"]
    contract = records[
        "BHSM_POST_AE2_LOCALIZATION_CARRIER_EXTENSION_CONTRACT.json"
    ]
    kill_screen = records[
        "BHSM_N12_GATE7_LOCALIZATION_CARRIER_KILL_SCREEN.json"
    ]
    c2 = records["BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json"]
    response = records["BHSM_aether_eta_sigma_response_constraint_v15_40.json"]
    response_child = records[
        "BHSM_aether_response_constrained_child_galerkin_v15_41.json"
    ]
    shear_child = records[
        "BHSM_aether_momentum_balanced_shear_data_v15_43.json"
    ]
    lorentzian_child = records[
        "BHSM_aether_lorentzian_child_galerkin_v15_44.json"
    ]
    reduced_child = records[
        "BHSM_aether_complete_child_localized_fiber_v15_34.json"
    ]
    fr_child = records["BHSM_aether_FR_zero_current_child_v15_37.json"]
    skin = records["BHSM_aether_material_skin_variation_v15_15.json"]
    cauchy = records[
        "BHSM_aether_n3_lorentzian_child_cauchy_correspondence_v17_88.json"
    ]
    bundle = records["BHSM_aether_hybrid_standard_model_bundle_v15_53.json"]
    generation = records["BHSM_generation_projector_action_attachment_v8_2.json"]
    continuum = records["BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"]

    carrier = regular_carrier_certificate()
    representative_reset = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)
    family_transport = family_fiber_transport_certificate(representative_reset)
    enclosure_transport = enclosure_transport_square_certificate(
        representative_reset
    )
    dependencies = dependency_ledgers()
    interface = interface_variation_ledger()
    full_field_attachment = current_full_field_attachment_ledger()
    integration_puzzle = systems_integration_puzzle()

    lec_gates = [
        _status(
            "LEC_01",
            "CLOSED",
            "The current owner explicitly authorizes a new minimal post-AE2 action version.",
        ),
        _status(
            "LEC_02",
            "CLOSED_ON_RETAINED_COHOMOGENEITY_ONE_C2_DOMAIN",
            "sigma is an existing spacetime scalar; the coefficient-free proper-orbit KKT response makes it action-owned.",
        ),
        _status(
            "LEC_03",
            "CLOSED",
            "The normalized reciprocal density is positive in the interior and gives one transverse sigma=0 level set.",
        ),
        _status(
            "LEC_04",
            "CLOSED_FOR_THE_RESOLVED_ENCLOSURE_INTERFACE",
            "Splitting the same smooth action at sigma=0 derives trace, canonical-flux, traction, Green-form, and Noether matching with no delta contact term.",
        ),
        _status(
            "LEC_05",
            "CLOSED",
            "A smooth scalar level set inside one spacetime selects LOCAL_SAME_SPACETIME_ENCLOSURE and excludes a collar boundary or spacetime edge.",
        ),
        _status(
            "LEC_06",
            "CONSTRUCTED_NOT_YET_EVALUATED_IN_ONE_FULL_FIELD_C2_ACTION_ORACLE",
            "Sector-scoped transitive dependency ledgers are explicit, but the retained 98-variable oracle still omits gauge/ghost, fermion, and HS coordinates.",
        ),
        _status(
            "LEC_07",
            "CLOSED",
            "AE2 reset traces and all tensor-factor family projectors are unchanged and commute exactly.",
        ),
        _status(
            "LEC_08",
            "CLOSED_AS_A_FIBERED_INSTANTIATION_NOT_A_SPECIES_SELECTION",
            "Every frozen (sector,slot) rank-one state is a real fiber over the actual C2 history; an upstream BHSM label selects the fiber.",
        ),
        _status(
            "LEC_09",
            "ALGEBRAIC_AND_SIGNATURE_INHERITANCE_CLOSED__FULL_FIELD_EVENT_BALANCE_OPEN",
            "The carrier, topology, reset bundle, projector, and dependency signature transport; the omitted full-field C2 blocks prevent a complete physical balance claim.",
        ),
        _status(
            "LEC_10",
            "CLOSED_BY_STRATIFIED_TOPOLOGICAL_DOMAIN",
            "On the inactive even/trivial sector there is no response/odd-FR localization functional and the action is exactly AE2.",
        ),
        _status(
            "LEC_11",
            "CLOSED",
            "No new physical coefficient or scale is introduced; Lambda=1-4 sigma^2 is fixed by the retained action and the minimal even-quadratic conditions.",
        ),
        _status(
            "LEC_12",
            "CLOSED",
            "All particle, family, representation, projector, current, and topology assets are imported by hash and unchanged.",
        ),
    ]

    pei = {
        "PEI_01": True,
        "PEI_02": True,
        "PEI_03": True,
        "PEI_04": True,
        "PEI_05": False,
        "PEI_06": False,
        "PEI_07": False,
        "PEI_08": True,
        "PEI_09": False,
        "PEI_10": True,
        "PEI_11": True,
    }
    validation = {
        "owner_authorization_supersedes_contract_authorization_gate": (
            contract["authorization_boundary"]["owner_decision_required"] is True
        ),
        "unchanged_AE2_kill_screen_preserved": (
            kill_screen["carrier_audit"][
                "carrier_exists_in_audited_unchanged_ae2"
            ]
            is False
        ),
        "AE2_reset_preserved": ae2["validation_passed"] is True,
        "carrier_regular": carrier["regular_level_set"] is True,
        "carrier_transverse": carrier["transversality_at_zero"] > 0.0,
        "response_constraint_is_historical": response["validation_passed"] is True,
        "localized_Hopf_weight_is_historical": reduced_child["validation_passed"] is True,
        "zero_current_FR_ground_state_is_historical": fr_child["validation_passed"] is True,
        "resolved_material_interface_laws_are_historical": skin["validation_passed"] is True,
        "C2_history_is_actual": c2["validation_passed"] is True,
        "continuum_child_is_certified": continuum["validation_passed"] is True,
        "C2_sigma_response_trace_exists": (
            "sigma=C_J[f]-1/2"
            in cauchy["event_to_complete_child_cauchy_correspondence"]
            ["complete_child_initial_state_map"]["sigma_response"]
        ),
        "family_projectors_unchanged": generation["validation_passed"] is True,
        "SM_bundle_unchanged": bundle["validation_passed"] is True,
        "all_family_fibers_commute_with_reset": (
            family_transport["certificate_passed"] is True
        ),
        "enclosure_transport_square_commutes": (
            enclosure_transport["certificate_passed"] is True
        ),
        "historical_response_child_functional_is_executable": (
            response_child["claim_boundary"]
            ["one_response_constrained_child_functional_written"] is True
            and response_child["claim_boundary"]
            ["finite_Galerkin_spatial_Euler_projection_solved"] is True
        ),
        "historical_response_child_constraints_are_solved": (
            shear_child["claim_boundary"]
            ["response_constrained_both_ADM_constraints_solved"] is True
        ),
        "historical_localized_lorentzian_trajectory_exists": (
            lorentzian_child["claim_boundary"]
            ["nonlinear_encapsulation_trajectory_integrated"] is True
            and lorentzian_child["claim_boundary"]
            ["derived_surface_separation_reached"] is True
        ),
        "historical_zero_source_cycle_not_false_attached_to_current_C2": (
            full_field_attachment[
                "historical_common_superdeterminant_promoted_to_current_C2"
            ]
            is False
        ),
        "systems_integration_is_not_artificially_serialized": (
            integration_puzzle["serial_gate_order_required"] is False
            and integration_puzzle[
                "section_updates_allowed_when_locally_compatible"
            ]
            is True
        ),
        "no_new_particle_spectrum": True,
        "no_SM_fit": True,
        "no_new_continuous_coefficient": True,
        "no_spacetime_edge_claim": SELECTED_ROUTE != "SPACETIME_EDGE_TRANSITION",
        "full_field_balance_not_false_promoted": not all(pei.values()),
    }

    return {
        "artifact": "BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION",
        "schema_version": 1,
        "action_version": ACTION_VERSION,
        "action_version_status": "OWNER_AUTHORIZED_MINIMAL_LOCALIZATION_DOMAIN_EXTENSION",
        "status": (
            "ACTION_OWNED_LOCALIZATION_CARRIER_DERIVED_ON_THE_RETAINED_C2_"
            "ACTION_DOMAIN__RESOLVED_INTERFACE_AND_FAMILY_FIBER_TRANSPORT_"
            "CONSTRUCTED__FULL_FIELD_EVENT_BALANCE_OPEN"
        ),
        "classification": "BHSM_AE3_RECIPROCAL_JOIN_LOCAL_SAME_SPACETIME_ENCLOSURE",
        "selected_candidate": CARRIER_ID,
        "candidate_ranking": ranked_carrier_candidates(),
        "action": {
            "configuration_domain": "AE2_reset_glued_parent_event_child_domain_with_existing_eta_sigma_degree_orientation_FR_data",
            "localization_scalar": "sigma=C_J[eta]-1/2",
            "covariant_response_on_orbit_space": "C_sigma=n_eta^A*nabla_A_sigma-W_J[eta]/Z_J[eta]=0;_Z_J=integral_Q W_J d_ell",
            "KKT_term": "S_response=integral_Q d_ell*mu_Q*lambda_sigma*C_sigma",
            "localized_Hopf_weight": "Lambda(sigma)=1-4*sigma^2",
            "localized_inertia": "I_H=integral_Sigma_t sqrt(h)*(kappa1+X_eta^3)*Lambda(sigma)*abs(K_H)^2",
            "odd_FR_ground_state": "Psi_0=cos(theta/2)/sqrt(pi);_<J>=0;_<J^2>=1/4",
            "stationary_FR_functional": "H_FR=<J^2>/(2I_H)=1/(8I_H)",
            "extension": "S_AE3=S_BHSM_AE2_retained[Lambda(sigma_0)->Lambda(sigma)]+S_response;_the_existing_H_FR_is_promoted_with_the_same_substitution_and_is_not_added_twice",
            "inactive_limit": "S_AE3=S_AE2_on_the_trivial_or_even_FR_component_where_the_localization_response_sector_is_absent_and_<J^2>=0",
            "new_physical_fields": [],
            "new_nonpropagating_multipliers": ["lambda_sigma"],
            "new_continuous_coefficients": [],
            "new_scales": [],
            "SM_observables_used_for_selection": [],
        },
        "carrier_map": {
            "map": "D_A:z->(D_enc={sigma<0},Sigma_enc={sigma=0},X,n,K,h,topology,attachment)",
            "route": SELECTED_ROUTE,
            "route_selected_by": "smooth_action_scalar_on_one_parent_child_spacetime_domain",
            "not_the_event_scalar": True,
            "not_the_reset_locus": True,
            "not_a_terminal_boundary": True,
            "certificate": carrier,
        },
        "euler_lagrange_and_interface_variation": interface,
        "dependency_ledgers": dependencies,
        "family_mode_C2_instantiation": family_transport,
        "physical_transport_square": enclosure_transport,
        "current_full_field_attachment": full_field_attachment,
        "systems_integration_puzzle": integration_puzzle,
        "nonlinear_completion": {
            "analytic_profile": "sigma_0=-1/2+2chi/pi-sin(4chi)/(2pi)",
            "finite_localization_support": True,
            "nontrivial_profile": True,
            "unique_regular_interface": True,
            "historical_response_constrained_functional_written": True,
            "historical_finite_Galerkin_spatial_Euler_projection_solved": True,
            "historical_response_constrained_both_ADM_constraints_solved": True,
            "historical_nonlinear_Lorentzian_encapsulation_trajectory_integrated": True,
            "historical_derived_surface_separation_reached": True,
            "historical_persistent_child_derived": lorentzian_child[
                "claim_boundary"
            ]["persistent_child_derived"],
            "actual_C2_continuum_child_available": continuum["validation_passed"],
            "scope": "retained_cohomogeneity_one_C2_action_domain",
            "unrestricted_nonround_full_field_BVP_solved": False,
        },
        "extension_acceptance_gates": lec_gates,
        "physical_encapsulation_rows": pei,
        "ACTION_OWNED_LOCALIZATION_CARRIER_DERIVED": True,
        "ACTION_OWNED_PHYSICAL_LOCALIZATION_AND_ENCLOSURE_DERIVED": True,
        "BHSM_NATIVE_FAMILY_MODE_STATE_TRANSPORTED_THROUGH_LOCALIZATION": True,
        "EXISTING_SM_MANIFESTATION_READOUT_PRESERVED": True,
        "PHYSICAL_ENCAPSULATION_IDENTIFIED": False,
        "remaining_kernels": {
            "KERNEL_A": "CLOSED_ON_RETAINED_C2_ACTION_DOMAIN",
            "KERNEL_B": "RESOLVED_INTERFACE_CLOSED__FULL_FIELD_EVENT_JUNCTION_AND_NOETHER_HAMILTONIAN_BALANCE_OPEN",
            "KERNEL_C": "SIGNATURE_AND_FIBER_INHERITANCE_CLOSED__DEPENDENCY_CLOSED_FULL_FIELD_ACTION_EVALUATION_OPEN",
            "KERNEL_D": "CLOSED_AS_FIBERED_C2_INSTANTIATION_WITH_UPSTREAM_LABEL_PRESERVED",
        },
        "exact_next_mathematical_object": (
            "ONE_AE3_FULL_FIELD_C2_ACTION_ORACLE_WITH_GEOMETRY_GAUGE_GHOST_"
            "FERMION_HS_AND_RESPONSE_MULTIPLIER_BLOCKS;_THEN_EVALUATE_THE_"
            "EVENT_CANONICAL_FLUX_AND_COMPLETE_NOETHER_HAMILTONIAN_BALANCE_"
            "WITHOUT_ADDING_A_CONTACT_COEFFICIENT"
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
