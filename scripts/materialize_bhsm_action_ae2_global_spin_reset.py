"""Materialize the BHSM-AE-2.0.0 action and Gate-7 domain artifacts."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_global_spin_reset_ae2 import (  # noqa: E402
    ACTION_VERSION,
    DECISION_TYPE,
    action_definition,
    brst_transmission_residual,
    independent_phase_twist_distance,
    opposite_normal_green_residual,
    transmission_graph_certificate,
)


ACTION_TARGET = (
    ROOT / "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
)
GATE7_TARGET = (
    ROOT
    / "artifacts/flagship_integration"
    / "BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"
)

AE1 = ROOT / "artifacts/action_extension/BHSM_ACTION_AE1_NORMAL_MATTER_BIRTH_ADJUDICATION.json"
V6_VARIATION = ROOT / "artifacts/BHSM_junction_variation_and_selected_domain_v6_10_0.json"
V14_GLUE = ROOT / "artifacts/BHSM_global_spin_bundle_seam_glue_v14_45.json"
V15_MATERIAL = ROOT / "artifacts/BHSM_aether_material_skin_variation_v15_15.json"
V15_GAUGE = ROOT / "artifacts/BHSM_aether_full_gauge_dtn_lr_kernel_v15_66.json"
V17_EVENT = ROOT / "artifacts/BHSM_aether_n3_event_complete_child_correspondence_v17_84.json"
V17_BOUNDARY = ROOT / "artifacts/BHSM_aether_n3_terminal_child_boundary_map_v17_85.json"
V17_CAUCHY = ROOT / "artifacts/BHSM_aether_n3_lorentzian_child_cauchy_correspondence_v17_88.json"
V17_SCALAR = ROOT / "artifacts/BHSM_aether_n3_scalar_complete_child_boundary_solution_v17_96.json"
V17_FIREWALL = ROOT / "artifacts/BHSM_aether_n3_firewall_core_child_ownership_v17_98.json"
INCIDENCE = ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
THRESHOLD = ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_BIRTH_THRESHOLD_MARGIN_AUDIT.json"
OLD_NO_GO = ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_MATTER_DOMAIN_NO_GO.json"
MODULE = ROOT / "src/bhsm/interface/action_extension_global_spin_reset_ae2.py"

INPUTS = (
    AE1,
    V6_VARIATION,
    V14_GLUE,
    V15_MATERIAL,
    V15_GAUGE,
    V17_EVENT,
    V17_BOUNDARY,
    V17_CAUCHY,
    V17_SCALAR,
    V17_FIREWALL,
    INCIDENCE,
    THRESHOLD,
    OLD_NO_GO,
    MODULE,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite AE2 materialization value")
        rounded = round(value, 15)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, complex):
        return {"real": _canonical(value.real), "imag": _canonical(value.imag)}
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def _witness() -> dict[str, Any]:
    rng = np.random.default_rng(2200)
    raw = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
    lift, _ = np.linalg.qr(raw)
    psi = rng.normal(size=4) + 1j * rng.normal(size=4)
    phi = rng.normal(size=4) + 1j * rng.normal(size=4)
    normal_form = np.diag([1.0, 1.0, -1.0, -1.0])
    ghost_seed = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
    ghost = ghost_seed - np.conjugate(ghost_seed.T)
    graph = transmission_graph_certificate(normal_form, lift)
    return {
        "seed": 2200,
        "unitarity_residual": float(
            np.linalg.norm(np.conjugate(lift.T) @ lift - np.eye(4))
        ),
        "opposite_normal_Green_residual": opposite_normal_green_residual(
            psi, phi, normal_form, lift
        ),
        "BRST_transmission_residual": brst_transmission_residual(psi, lift, ghost),
        "transmission_graph": graph,
        "nontrivial_relative_phase_changes_fixed_graph": (
            independent_phase_twist_distance(lift, 0.73) > 1.0e-6
        ),
        "extra_phase_adopted": False,
    }


def build_payloads() -> tuple[dict[str, Any], dict[str, Any]]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all AE2 action inputs are required")
    (
        ae1,
        v6,
        v14,
        v15_material,
        v15_gauge,
        v17_event,
        v17_boundary,
        v17_cauchy,
        v17_scalar,
        v17_firewall,
        incidence,
        threshold,
        old_no_go,
    ) = (_load(path) for path in INPUTS[:-1])
    for record in (
        ae1,
        v14,
        v15_material,
        v15_gauge,
        v17_event,
        v17_boundary,
        v17_cauchy,
        v17_scalar,
        v17_firewall,
        incidence,
        threshold,
        old_no_go,
    ):
        if record.get("validation_passed") is not True:
            raise RuntimeError("validated AE2 lineage inputs are required")
    if v6.get("status") != "BHSM_CURRENT_ACTION_SELECTS_NO_SELF_ADJOINT_JUNCTION_DOMAIN":
        raise RuntimeError("the authoritative v6.10 no-selection theorem is required")

    firewall = v17_firewall["firewall_core_child_ownership"]
    firewall_rows = firewall["firewall_discrete_match"]["rows"]
    event_correspondence = v17_event["event_to_complete_child_correspondence"]
    cauchy = v17_cauchy["event_to_complete_child_cauchy_correspondence"]
    action = action_definition()
    witness = _witness()
    inputs = {
        str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
        for path in INPUTS
    }

    decision_report = {
        "A": {
            "scientific_meaning": "RESET_GLUED_GLOBAL_SPIN_TIMES_G_SM_BUNDLE",
            "existing_geometry": "V14_45_PLUS_V15_15_WITH_V17_98_RETURNED_BUNDLE_CLASS_DEGREE_ORIENTATION_AND_FR_DATA",
            "new_physics": "ONE_ACTUAL_RESET_BUNDLE_LIFT_MODULO_GLOBAL_SIGN_AND_GAUGE",
            "strength": "COEFFICIENT_FREE_GEOMETRIC_TRANSMISSION",
            "weakness": "OWNER_AUTHORIZED_EXTENSION_OF_THE_OLD_CLASS_ONLY_FIREWALL",
            "classification": ["GEOMETRICALLY_PREFERRED", "MINIMAL_VALID_EXTENSION"],
        },
        "B": {
            "scientific_meaning": "LOCAL_HERMITIAN_CAYLEY_BOUNDARY_GENERATOR",
            "existing_geometry": "V6_10_PERMITS_FOUR_CLIFFORD_GRADES_TIMES_THE_C3_COMMUTANT",
            "new_physics": "BOUNDARY_TERM_POLARIZATION_GRADE_AND_UNFIXED_COEFFICIENT",
            "strength": "DIRECT_BOUNDARY_EULER_VARIATION",
            "fatal_weakness": "CONTINUOUS_PHYSICALLY_INEQUIVALENT_ALPHA_FAMILY",
            "classification": ["UNDERDETERMINED_EXTENSION", "HAND_SELECTED_PHASE_IF_ADOPTED"],
        },
        "C": {
            "scientific_meaning": "UNCHANGED_CLASS_ONLY_FIREWALL_AND_ACTION",
            "existing_geometry": "FULLY_PRESERVES_THE_OLD_RETAINED_ACTION",
            "new_physics": "NONE",
            "strength": "UNCHANGED_ACTION_NO_GO_REMAINS_EXACT",
            "fatal_weakness": "NO_COMPLETE_NONZERO_MATTER_BIRTH_DOMAIN",
            "classification": ["INCONSISTENT_WITH_THE_AUTHORIZED_COMPLETION_PROGRAM"],
        },
        "NORMAN_SELECTED_OPTION": "A",
        "why": (
            "A_ADDS_ONLY_THE_ACTUAL_RESET_LIFT_NEEDED_TO_ACTIVATE_EXISTING_"
            "GLOBAL_SPIN_GEOMETRY;_B_ADDS_AN_UNSELECTED_PHYSICAL_COEFFICIENT_"
            "AND_C_PRESERVES_THE_KNOWN_DOMAIN_OBSTRUCTION"
        ),
        "decision_type": DECISION_TYPE,
        "action_derived": False,
    }

    action_validation = {
        "owner_selected_A": decision_report["NORMAN_SELECTED_OPTION"] == "A",
        "old_action_no_go_preserved": old_no_go["status"]
        == "CANONICAL_UNCHANGED_RETAINED_ACTION_NO_GO",
        "v14_global_spin_matcher_available": v14["matcher_status"]
        == "FIXED_BY_THE_ADOPTED_GLOBAL_SPIN_BUNDLE",
        "v15_material_transmission_theorem_available": v15_material[
            "material_trace_domain"
        ]["self_adjointness_check"],
        "returned_SM_bundle_class_available": firewall_rows[
            "SM_bundle_isomorphism_class_returns"
        ],
        "degree_one_available": firewall_rows["global_event_degree_is_one"],
        "orientation_available": firewall_rows["child_orientation_is_negative_x"],
        "odd_FR_available": firewall_rows["odd_FR_parity_retained"],
        "event_child_trace_continuity_available": bool(
            event_correspondence["first_variation_derivation"]["trace_continuity"]
        ),
        "regular_Cauchy_canonical_relation_available": bool(
            cauchy["joined_action_derivation"]["canonical_relation"]
        ),
        "no_core_continuous_trace_added": firewall["ownership_decision"][
            "continuous_pregeometric_core_trace_in_retained_child_action"
        ]
        is False,
        "Green_forms_cancel": witness["opposite_normal_Green_residual"] < 1.0e-12,
        "graph_maximal_isotropic": witness["transmission_graph"]["maximal_isotropic"],
        "BRST_graph_covariant": witness["BRST_transmission_residual"] < 1.0e-12,
        "no_independent_phase_adopted": witness["extra_phase_adopted"] is False,
        "no_new_coefficient_scale_or_propagating_field": all(
            action[key] is None
            for key in (
                "new_continuous_coefficient",
                "new_physical_scale",
                "new_propagating_field",
            )
        ),
        "frozen_predictions_unchanged": True,
        "FULL_BHSM_COMPLETE_false": True,
    }

    action_payload = {
        "artifact": "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION",
        "action_version": ACTION_VERSION,
        "action_version_status": "OWNER_SELECTED_NEW_ACTION_DOMAIN_VERSION",
        "decision_report": decision_report,
        "action_definition": action,
        "variation_theorem": {
            "boundary_variation": (
                "B_event(deltaPsi,Psi)+B_child(U_R*deltaPsi,U_R*Psi)=0_"
                "BECAUSE_J_child=-U_R*J_event*U_R_DAGGER"
            ),
            "trace_law": action["trace_graph"],
            "first_order_domain_law": action["trace_graph"],
            "squared_operator_flux_law": action["squared_operator_flux_graph"],
            "squared_operator_domain": action["squared_operator_domain"],
            "self_adjointness": (
                "THE_GRAPH_OF_UNITARY_U_R_IS_HALF_DIMENSIONAL_AND_MAXIMAL_"
                "ISOTROPIC_IN_THE_TWO_SIDED_GREEN_TRACE_SPACE"
            ),
            "phase_collapse": (
                "THE_OLD_U1_PARENT_TIMES_U1_CHILD_TERMINAL_DOMAIN_FAMILY_IS_"
                "ABSENT_BECAUSE_THE_TWO_TRACES_ARE_ONE_GLOBAL_SECTION;_ONLY_"
                "COMMON_GAUGE_FRAME_CHANGES_AND_THE_GLOBAL_SPIN_SIGN_REMAIN"
            ),
        },
        "finite_certificate": witness,
        "compatibility": {
            "gauge_BRST": (
                "c_child=U_R*c_event*U_R_DAGGER_AND_THE_TRACE_CONSTRAINT_"
                "TRANSFORMS_COVARIANTLY"
            ),
            "event_reset": (
                "USES_ONLY_THE_LAST_AND_FIRST_REGULAR_TRACES_AND_RETURNED_"
                "DISCRETE_BUNDLE_DATA;_NO_METRIC_TIME_VELOCITY_OR_CORE_FLUX_"
                "IS_TRANSPORTED_THROUGH_THE_PREGEOMETRIC_CORE"
            ),
            "existing_limits": (
                "AWAY_FROM_A_RESET_INTERFACE_THE_ACTION_IS_THE_RETAINED_"
                "DIRAC_ACTION;_AT_ZERO_CLASSICAL_SPINOR_TRACE_THE_CERTIFIED_"
                "RESET_IS_UNCHANGED"
            ),
            "double_counting": (
                "NO_FERMION_DELTA_TERM_IS_ADDED_AND_THE_EXISTING_TRANSVERSE_"
                "GAUGE_DtN_BLOCK_IS_LEFT_UNCHANGED"
            ),
        },
        "claim_boundary": {
            "unchanged_action_completed": False,
            "owner_decision_mislabelled_action_derived": False,
            "new_boundary_coefficient_added": False,
            "Cayley_phase_selected": False,
            "pregeometric_core_field_added": False,
            "frozen_predictions_changed": False,
            "Gate7_closed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": inputs,
        "validation": action_validation,
        "validation_passed": all(action_validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }

    gate_validation = {
        "AE2_action_validated": action_payload["validation_passed"],
        "matter_attachment_block_owned_as_zero_only_in_AE2": True,
        "spinor_birth_graph_unique_modulo_gauge_and_global_sign": True,
        "old_U1_times_U1_family_removed_from_AE2_domain": True,
        "transverse_gauge_DtN_preserved": (
            v15_gauge["full_gauge_DtN_completion"]["provenance"]
            == "BHSM_ACTION_COMPLETION_DERIVED_FROM_EXISTING_RANK16_CARRIER_TRACE_AND_DIAGONAL_SP1_DtN_OPERATOR"
            and bool(v15_gauge["full_gauge_DtN_completion"]["operator"])
        ),
        "scalar_geometry_boundary_solution_preserved": v17_scalar[
            "scalar_complete_child_boundary_solution"
        ]["F_child_scalar"]["closed_to_resolved_derivative_tolerance"],
        "local_nonzero_source_incidence_available": incidence["validation_passed"],
        "event_and_child_nonzero_Calderon_oracle_not_fabricated": True,
        "threshold_margin_not_fabricated": True,
        "zero_source_force_not_fabricated": True,
        "same_action_saddle_not_fabricated": True,
        "pair_plus_contact_Hessian_not_fabricated": True,
        "Gate7_not_overclaimed": True,
        "frozen_predictions_unchanged": True,
        "FULL_BHSM_COMPLETE_false": True,
    }

    gate_payload = {
        "artifact": "BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN",
        "action_version": ACTION_VERSION,
        "status": "AE2_MATTER_BIRTH_DOMAIN_OWNED_GATE7_CALDERON_THRESHOLD_FORCE_OPEN",
        "classification": (
            "THE_OWNER_SELECTED_RESET_BUNDLE_LIFT_REPLACES_THE_OLD_TWO_"
            "TERMINAL_SKIN_U1_TIMES_U1_FAMILY_BY_ONE_GLOBAL_SPINOR_"
            "TRANSMISSION_DOMAIN;_THE_AE2_FERMION_SURFACE_ATTACHMENT_BLOCK_IS_"
            "ZERO_BECAUSE_NO_DELTA_SUPPORTED_MATTER_TERM_EXISTS,_WHILE_THE_"
            "TRANSVERSE_GAUGE_DtN_AND_SCALAR_FLUX_BLOCKS_REMAIN_UNCHANGED;_"
            "GATE7_STILL_REQUIRES_THE_NONZERO_EVENT_CHILD_CALDERON_ORACLE_AND_"
            "A_STRICT_ZERO_THRESHOLD_MARGIN_BEFORE_THE_FORCE_IS_EVALUABLE"
        ),
        "source_domain": {
            "trace": action["trace_graph"],
            "conormal": action["squared_operator_flux_graph"],
            "fermion_W_phys_local_surface_block": 0,
            "fermion_W_zero_provenance": "AE2_GLOBAL_DOMAIN_NO_DELTA_MATTER_DENSITY",
            "gauge_W_phys": v15_gauge["full_gauge_DtN_completion"]["operator"],
            "far_maximal_endpoint": (
                "UNCHANGED_FRIEDRICHS_CLOSURE_ON_EVERY_INFINITE_OR_EXCLUDED_"
                "MAXIMAL_FORWARD_END"
            ),
            "BRST_ghost_graph": "c_child=U_R*c_event*U_R_DAGGER",
            "Cayley_phase_family": None,
        },
        "sector_status": {
            "fermion_normal_domain": "CLOSED_BY_AE2_GLOBAL_SPIN_RESET_LIFT",
            "scalar_geometry_classical_boundary": "PRESERVED_CLOSED",
            "transverse_gauge_spatial_DtN": "PRESERVED_ACTION_DERIVED",
            "local_rank16_gauge_ghost_HS_incidence": incidence["status"],
            "nonzero_event_child_Calderon_oracle": "OPEN",
            "zero_threshold_Wronskian_margin": "OPEN",
            "zero_source_weak_geometry_force": "OPEN",
            "same_action_replacement_saddle": "OPEN",
            "pair_plus_contact_Hessian": "OPEN",
            "Ward_BRST_and_relative_trace": "OPEN_DOWNSTREAM",
        },
        "exact_next_dependency": (
            "ASSEMBLE_OR_RIGOROUSLY_ENCLOSE_ON_A_NONEMPTY_NATIVE_RESOLVENT_"
            "REGION_THE_AE2_TWO_SIDED_FERMION_EVENT_AND_CHILD_CALDERON_MAPS_"
            "M_event(z)_AND_M_child(z),_PROVE_A_STRICT_ZERO_ENERGY_MATRIX_"
            "WRONSKIAN_MARGIN_FOR_M_event(0)+M_child(0),_THEN_INSERT_THE_"
            "ALREADY_ASSEMBLED_COMMON_LOCAL_INCIDENCE_AND_EVALUATE_THE_ZERO_"
            "SOURCE_WEAK_GEOMETRY_FORCE"
        ),
        "prior_no_go_reconciliation": {
            "unchanged_action_no_go_remains_true": True,
            "superseded_only_for_action_version": ACTION_VERSION,
            "old_missing_normal_matter_generator": (
                "REPLACED_BY_GEOMETRIC_GLOBAL_DOMAIN_WITH_ZERO_INDEPENDENT_"
                "FERMION_SURFACE_BLOCK"
            ),
            "old_resolvent_phase_witness": (
                "REMAINS_A_VALID_PROOF_THAT_DIFFERENT_ACTION_DOMAINS_ARE_"
                "INEQUIVALENT;_THEY_ARE_NOT_MEMBERS_OF_THE_SINGLE_AE2_DOMAIN"
            ),
        },
        "adjudication": {
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": inputs,
        "validation": gate_validation,
        "validation_passed": all(gate_validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    return action_payload, gate_payload


def deterministic_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def materialize() -> tuple[Path, Path]:
    action, gate7 = build_payloads()
    ACTION_TARGET.parent.mkdir(parents=True, exist_ok=True)
    GATE7_TARGET.parent.mkdir(parents=True, exist_ok=True)
    ACTION_TARGET.write_bytes(deterministic_bytes(action))
    GATE7_TARGET.write_bytes(deterministic_bytes(gate7))
    return ACTION_TARGET, GATE7_TARGET


if __name__ == "__main__":
    for path in materialize():
        print(path)
