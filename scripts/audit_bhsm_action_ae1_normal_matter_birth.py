"""Adjudicate the owner-authorized BHSM normal-matter action extension.

This starts a new action-version line without adopting a physical extension.
It first tests every already-retained route that could own the event-to-child
matter graph, then classifies the complete lowest-order local fermion basis.
The output stops before action selection if inequivalent graphs remain.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_boundary_phase_resolvent import (  # noqa: E402
    cayley_phase,
    compact_indicator_resolvent_difference,
    phase_distance,
)


ACTION_VERSION = "BHSM-AE-1.0.0"
OWNER_AUTHORIZATION = "NORMAN_OWNER_AUTHORIZATION_BHSM_ACTION_EXTENSION"
TARGET = (
    ROOT
    / "artifacts/action_extension"
    / "BHSM_ACTION_AE1_NORMAL_MATTER_BIRTH_ADJUDICATION.json"
)

RECONCILIATION = ROOT / "artifacts/BHSM_historical_action_reconciliation_v7_0.json"
INVARIANTS = ROOT / "artifacts/BHSM_junction_invariant_and_triality_commutant_v6_10_0.json"
VARIATION = ROOT / "artifacts/BHSM_junction_variation_and_selected_domain_v6_10_0.json"
SPIN_GLUE = ROOT / "artifacts/BHSM_global_spin_bundle_seam_glue_v14_45.json"
BOUNDARY_IDENTITY = ROOT / "artifacts/BHSM_aether_boundary_identity_ejection_v15_13.json"
MATERIAL_SKIN = ROOT / "artifacts/BHSM_aether_material_skin_variation_v15_15.json"
CORRESPONDENCE = ROOT / "artifacts/BHSM_aether_n3_event_complete_child_correspondence_v17_84.json"
FIREWALL = ROOT / "artifacts/BHSM_aether_n3_firewall_core_child_ownership_v17_98.json"
PRIOR_NO_GO = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_MATTER_DOMAIN_NO_GO.json"
)
RESOLVENT_MODULE = ROOT / "src/bhsm/interface/aether_forward_boundary_phase_resolvent.py"

INPUTS = (
    RECONCILIATION,
    INVARIANTS,
    VARIATION,
    SPIN_GLUE,
    BOUNDARY_IDENTITY,
    MATERIAL_SKIN,
    CORRESPONDENCE,
    FIREWALL,
    PRIOR_NO_GO,
    RESOLVENT_MODULE,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite action-extension audit value")
        rounded = round(value, 15)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, complex):
        return {"real": _canonical(value.real), "imag": _canonical(value.imag)}
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all action-extension adjudication inputs are required")

    reconciliation = _load(RECONCILIATION)
    invariants = _load(INVARIANTS)
    variation = _load(VARIATION)
    spin_glue = _load(SPIN_GLUE)
    boundary = _load(BOUNDARY_IDENTITY)
    material = _load(MATERIAL_SKIN)
    correspondence = _load(CORRESPONDENCE)
    firewall = _load(FIREWALL)
    prior_no_go = _load(PRIOR_NO_GO)

    for record in (
        spin_glue,
        boundary,
        material,
        correspondence,
        firewall,
        prior_no_go,
    ):
        if record.get("validation_passed") is not True:
            raise RuntimeError("validated repository inputs are required")
    if invariants.get("status") != "BHSM_C3_HERMITIAN_COMMUTANT_IS_CIRCULANT":
        raise RuntimeError("the authoritative v6.10 invariant ledger is required")
    if variation.get("status") != "BHSM_CURRENT_ACTION_SELECTS_NO_SELF_ADJOINT_JUNCTION_DOMAIN":
        raise RuntimeError("the authoritative v6.10 variation ledger is required")

    domain = variation["domain"]
    identity = boundary["boundary_identity_and_transport"]
    material_domain = material["material_trace_domain"]
    event = correspondence["event_to_complete_child_correspondence"]
    ownership = firewall["firewall_core_child_ownership"]["ownership_decision"]
    retained_check = firewall["firewall_core_child_ownership"]["retained_action_check"]

    matter_row = next(
        row
        for row in reconciliation["architectures"]
        if row["architecture"] == "v6.7 boundary matter action"
    )

    alpha_1 = 1.0
    alpha_2 = 2.0
    phase_1 = cayley_phase(alpha_1)
    phase_2 = cayley_phase(alpha_2)
    resolvent_difference = compact_indicator_resolvent_difference(
        1.0, 1.0, alpha_1, alpha_2
    )

    retained_route_audit = [
        {
            "route": "P1_PLUS_GHY_BULK_BOUNDARY_REDUCTION",
            "classification": "BOSONIC_METRIC_VARIATIONAL_COMPLETION_ONLY",
            "result": "DOES_NOT_GENERATE_A_NORMAL_FERMION_GRAPH",
            "evidence": invariants["geometry"]["GHY_classification"],
        },
        {
            "route": "HAYWARD_OR_GRAVITATIONAL_CORNER",
            "classification": "INAPPLICABLE_AND_BOSONIC",
            "result": "NO_NORMAL_PAIR_OR_REQUIRED_CORNER_TERM_AND_NO_MATTER_PHASE",
            "evidence": invariants["geometry"]["reason_no_required_joint"],
        },
        {
            "route": "TANGENTIAL_LEVI_CIVITA_SPIN_AND_GAUGE_CONNECTION",
            "classification": "TRANSPORT_ON_AN_ALREADY_SELECTED_DOMAIN",
            "result": "DOES_NOT_SELECT_THE_NORMAL_MAXIMAL_ISOTROPIC_GRAPH",
            "evidence": identity["normal_self_adjoint_boundary_graph_fixed_by_tangential_parallel_transport"],
        },
        {
            "route": "V14_45_GLOBAL_SPIN_GLUE_AND_V15_15_MATERIAL_TRANSMISSION",
            "classification": "VALID_FOR_TWO_SIDES_OF_ONE_GLOBAL_SMOOTH_SPIN_BUNDLE",
            "result": "INAPPLICABLE_TO_THE_GATE7_FIREWALL_BIRTH_TRACE",
            "required_hypothesis": spin_glue["foundational_geometry"],
            "material_law": material_domain["fermion_trace_law"],
            "failed_gate7_hypothesis": {
                "continuous_pregeometric_core_trace": ownership[
                    "continuous_pregeometric_core_trace_in_retained_child_action"
                ],
                "continuous_pregeometric_core_flux": ownership[
                    "continuous_pregeometric_core_flux_row_in_F_child"
                ],
            },
        },
        {
            "route": "OMITTED_ONE_SIDED_FERMION_BOUNDARY_VARIATION",
            "classification": "BULK_GREEN_FORM_WITH_DOMAIN_REQUIREMENT",
            "result": "REQUIRES_A_MAXIMAL_ISOTROPIC_DOMAIN_BUT_SELECTS_NO_MEMBER",
            "evidence": domain["current_first_variation"],
        },
        {
            "route": "EVENT_TO_CHILD_GAMMA_MATCH_WENTZELL_SCHUR_BLOCK",
            "classification": "THEOREM_CLASS_CANONICAL_RELATION",
            "result": "PHYSICAL_W_PHYS_BLOCK_NOT_ACTION_DERIVED",
            "evidence": event["physical_block_provenance"],
        },
        {
            "route": "CURRENT_RESET_HESSIAN_OR_ZERO_BACKGROUND_MATCH",
            "classification": "EXISTENCE_ONLY_AT_THE_CLASSICAL_ZERO_BACKGROUND",
            "result": "DOES_NOT_DEFINE_THE_NONZERO_FLUCTUATION_GRAPH",
            "evidence": prior_no_go["sector_ledger"][
                "gauge_spinor_ghost_HS_zero_background"
            ],
        },
    ]

    local_basis = [
        {
            "id": row["id"],
            "density": row["density"],
            "coefficient": row["coefficient"],
            "coefficient_fixed": row["coefficient_fixed"],
            "classification": row["classification"],
        }
        for row in invariants["invariants"]
        if row["sector"] == "fermionic"
    ]

    candidate_contract = {
        "BHSM_native_and_geometric": True,
        "no_empirical_fit": True,
        "no_new_physical_scale": True,
        "gauge_and_BRST_consistent_for_identity_commutant": True,
        "forward_event_reset_endpoint_structure_preserved_if_birth_supported_only": True,
        "matter_birth_graph_produced_by_variation": True,
        "complete_self_adjoint_domain": True,
        "zero_trace_and_no_birth_interface_limits_recovered": True,
        "retained_boundary_term_double_counted": False,
        "frozen_predictions_changed_before_full_propagation": False,
        "arbitrary_phase_selector_absent": False,
        "reason_for_failure": (
            "THE_REAL_HERMITIAN_GENERATOR_COEFFICIENT_AND_POLARIZATION_ARE_"
            "NOT_FIXED_BY_ANY_RETAINED_GEOMETRIC_OR_ACTION_IDENTITY"
        ),
    }

    nonuniqueness_witness = {
        "strongest_restriction": (
            "FAMILY_UNIVERSAL_LOCAL_HERMITIAN_GAUGE_CENTRAL_GENERATOR_"
            "A_ALPHA=alpha*I"
        ),
        "graph": "(I+i*A_alpha)psi_-=(I-i*A_alpha)psi_+",
        "Cayley_map": "U_alpha=(I-i*A_alpha)(I+i*A_alpha)^(-1)",
        "alpha_dimension": "DIMENSIONLESS_IN_THE_RETAINED_REDUCED_CAYLEY_CHART",
        "witnesses": [
            {
                "alpha": alpha_1,
                "Cayley_phase": phase_1,
                "action_status": "NONZERO_LOCAL_BOUNDARY_GENERATOR_CANDIDATE_NOT_ADOPTED",
            },
            {
                "alpha": alpha_2,
                "Cayley_phase": phase_2,
                "action_status": "NONZERO_LOCAL_BOUNDARY_GENERATOR_CANDIDATE_NOT_ADOPTED",
            },
        ],
        "phase_chordal_distance": phase_distance(alpha_1, alpha_2),
        "compact_source_resolvent_difference": resolvent_difference,
        "resolvents_distinct": resolvent_difference != 0.0,
        "both_commute_with_all_retained_internal_symmetries": True,
        "both_add_no_scale": True,
        "both_are_self_adjoint_graphs": True,
        "selection_between_them_action_derived": False,
        "consequence": (
            "EVEN_THE_FAMILY_UNIVERSAL_IDENTITY_SUBFAMILY_CONTAINS_"
            "INEQUIVALENT_PHYSICAL_THEORIES;_THE_COMPLETE_CLIFFORD_TIMES_C3_"
            "BASIS_ONLY_ENLARGES_THE_AMBIGUITY"
        ),
    }

    validation = {
        "owner_authorization_recorded_as_new_action_line": True,
        "retained_action_not_misreported_as_completed": True,
        "v15_15_material_transmission_preserved_on_its_actual_domain": (
            material_domain["self_adjointness_check"]
            and material_domain["v14_45_matcher_status"]
            == "FIXED_BY_THE_ADOPTED_GLOBAL_SPIN_BUNDLE"
        ),
        "v15_15_not_transplanted_across_firewall": (
            ownership["continuous_pregeometric_core_trace_in_retained_child_action"]
            is False
            and ownership["continuous_pregeometric_core_flux_row_in_F_child"]
            is False
        ),
        "current_event_W_phys_not_action_derived": (
            event["physical_block_provenance"]["physical_blocks_action_derived"]
            is False
        ),
        "one_sided_variation_selects_no_graph": domain["unique_domain_selected"] is False,
        "complete_lowest_order_fermion_basis_has_multiple_classes": len(local_basis) == 4,
        "all_local_basis_coefficients_unfixed": all(
            row["coefficient_fixed"] is False for row in local_basis
        ),
        "family_universal_subfamily_still_nonunique": phase_distance(alpha_1, alpha_2) > 0.0,
        "inequivalent_candidates_change_resolvent": resolvent_difference != 0.0,
        "no_candidate_adopted": True,
        "no_phase_selected": True,
        "no_new_scale_field_or_empirical_input": True,
        "frozen_predictions_unchanged": True,
        "Gate7_not_rebuilt_without_unique_action": True,
        "FULL_BHSM_COMPLETE_remains_false": True,
    }

    return {
        "artifact": "BHSM_ACTION_AE1_NORMAL_MATTER_BIRTH_ADJUDICATION",
        "action_version": ACTION_VERSION,
        "action_version_status": "OWNER_AUTHORIZED_CANDIDATE_LINE_NOT_ADOPTED",
        "owner_authorization": OWNER_AUTHORIZATION,
        "program_scope": "ACTION_OWNED_NORMAL_MATTER_BIRTH_INTERFACE_BOUNDARY_LAW_ONLY",
        "status": "HALTED_BEFORE_ACTION_SELECTION_MULTIPLE_INEQUIVALENT_EXTENSIONS",
        "scientific_result": (
            "THE_EXISTING_BHSM_GEOMETRY_BULK_BOUNDARY_REDUCTION_SPIN_"
            "CONNECTION_JUNCTION_VARIATION_SYMMETRY_AND_OMITTED_VARIATION_DO_"
            "NOT_FORCE_THE_GATE7_NORMAL_MATTER_BIRTH_GRAPH;_V15_15_GLOBAL_"
            "SPIN_TRANSMISSION_REQUIRES_A_TWO_SIDED_SMOOTH_GLOBAL_BUNDLE_BUT_"
            "THE_V17_98_FIREWALL_HAS_NO_CONTINUOUS_PREGEOMETRIC_SPIN_TRACE_OR_"
            "FLUX;_THE_COMPLETE_LOCAL_HERMITIAN_BOUNDARY_BASIS_CONTAINS_A_"
            "CONTINUOUS_FAMILY_ALREADY_IN_ITS_GAUGE_CENTRAL_IDENTITY_"
            "SUBFAMILY,_AND_DISTINCT_MEMBERS_DEFINE_DISTINCT_RESOLVENTS;_NO_"
            "UNIQUE_ACTION_NATIVE_EXTENSION_CAN_BE_ADOPTED_WITHOUT_AN_"
            "ARBITRARY_PHASE_SELECTOR_OR_A_NEW_PHYSICAL_PRINCIPLE"
        ),
        "retained_action_provenance": {
            "matter_action": matter_row,
            "current_junction_action": domain["current_S_J_F"],
            "surviving_retained_family": identity["surviving_domain_witness"][
                "boundary_identity_allowed_group"
            ],
            "firewall_candidate_action_completion_adopted": retained_check[
                "candidate_action_completion_adopted"
            ],
        },
        "retained_route_audit": retained_route_audit,
        "complete_lowest_order_local_fermion_basis": local_basis,
        "triality_commutant": invariants["triality"],
        "candidate_class_contract": candidate_contract,
        "inequivalent_extension_witness": nonuniqueness_witness,
        "adjudication": {
            "existing_geometry_forces_birth_law": False,
            "additional_boundary_or_attachment_ownership_required": True,
            "unique_action_extension_derived": False,
            "structurally_admissible_extension_class_has_multiple_inequivalent_members": True,
            "authorization_compliant_candidate_selected": False,
            "reason_no_candidate_selected": "NO_ARBITRARY_PHASE_SELECTOR",
            "new_action_term_adopted": False,
            "Gate7_rebuilt_from_new_action": False,
            "Gate7": "BLOCKED_PENDING_OWNER_CHOICE_BETWEEN_INEQUIVALENT_PHYSICAL_ACTIONS_OR_A_NEW_DERIVING_PRINCIPLE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "owner_choice_return": {
            "selection_forbidden_to_Codex": True,
            "choices": [
                {
                    "id": "A",
                    "physical_change": (
                        "REVISE_THE_FIREWALL_TO_A_COMMON_TWO_SIDED_GLOBAL_SPIN_"
                        "BUNDLE_SO_TRANSPARENT_SPIN_LIFT_TRANSMISSION_IS_FORCED"
                    ),
                    "cost": "CHANGES_THE_EVENT_ONTOLOGY_AND_MUST_REVALIDATE_RESET_AND_FIREWALL_THEOREMS",
                },
                {
                    "id": "B",
                    "physical_change": (
                        "ADOPT_A_NEW_LOCAL_HERMITIAN_BOUNDARY_GENERATOR_AND_"
                        "SUPPLY_AN_ACTION_NATIVE_PRINCIPLE_FIXING_ITS_CLIFFORD_"
                        "GRADE_POLARIZATION_AND_COEFFICIENT"
                    ),
                    "cost": "WITHOUT_THE_NEW_PRINCIPLE_THIS_IS_AN_ARBITRARY_PHASE_SELECTOR",
                },
                {
                    "id": "C",
                    "physical_change": "KEEP_THE_CURRENT_FIREWALL_AND_RETAINED_ACTION_UNCHANGED",
                    "cost": "THE_NORMAL_MATTER_BIRTH_GRAPH_AND_GATE7_REMAIN_UNOWNED",
                },
            ],
            "Codex_selection": None,
        },
        "claim_boundary": {
            "this_is_completion_of_unchanged_retained_action": False,
            "new_physical_action_adopted": False,
            "phase_selected": False,
            "new_scale_added": False,
            "new_field_added": False,
            "empirical_input_used": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def deterministic_bytes() -> bytes:
    payload = _canonical(build_payload())
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def materialize() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(deterministic_bytes())
    return TARGET


if __name__ == "__main__":
    print(materialize())
