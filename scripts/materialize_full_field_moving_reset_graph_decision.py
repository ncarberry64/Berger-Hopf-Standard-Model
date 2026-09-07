"""Materialize the BHSM full-field moving-reset graph decision."""

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

from bhsm.interface.full_field_moving_reset_graph_decision import (  # noqa: E402
    ACTION_VERSION,
    CHARGE_CLASS,
    CLASSIFICATION,
    DIFFERENTIABILITY_CLASS,
    EXACT_NEXT_OBJECT,
    OUTCOME,
    R_CLASS,
    STATUS,
    claim_boundary,
    conditional_full_field_reset_graph,
    existing_reset_contract_inventory,
    field_by_field_attachment_rules,
    first_moving_domain_variation,
    hopf_rotor_adversarial_result,
    outcome_and_hindsight,
    reconstruction_determinism_audit,
    relative_tangent_and_generator_verdict,
    second_order_and_downstream_status,
    transport_and_tangent_witness,
    uniqueness_and_ambiguity_verdict,
)


TARGET = ROOT / "artifacts/action_extension/BHSM_FULL_FIELD_MOVING_RESET_GRAPH_DECISION.json"
MODULE = ROOT / "src/bhsm/interface/full_field_moving_reset_graph_decision.py"
SCRIPT = Path(__file__).resolve()
THEORY = ROOT / "theory/bhsm_full_field_moving_reset_graph_decision.md"
TEST = ROOT / "tests/test_full_field_moving_reset_graph_decision.py"


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
    inventory = existing_reset_contract_inventory()
    rules = field_by_field_attachment_rules()
    graph = conditional_full_field_reset_graph()
    variation = first_moving_domain_variation()
    witness = transport_and_tangent_witness()
    reconstruction = reconstruction_determinism_audit()
    uniqueness = uniqueness_and_ambiguity_verdict()
    tangent = relative_tangent_and_generator_verdict()
    second = second_order_and_downstream_status()
    hopf = hopf_rotor_adversarial_result()
    hindsight = outcome_and_hindsight()
    claims = claim_boundary()

    source_paths = (
        "src/bhsm/interface/action_extension_global_spin_reset_ae2.py",
        "src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py",
        "src/bhsm/interface/aether_master_closure_v15_5.py",
        "src/bhsm/interface/aether_norman_cycle_closure_v15_6.py",
        "src/bhsm/interface/aether_moving_interface_transfer_v15_12.py",
        "src/bhsm/interface/aether_n3_whole_child_encapsulation_audit_v17_82.py",
        "src/bhsm/interface/aether_n3_complete_child_chart_reconstruction_v18_24.py",
        "src/bhsm/interface/gauge_connection_reset_bundle_lift_adjudication.py",
        "src/bhsm/interface/nonfermion_relative_boundary_variation.py",
        "src/bhsm/interface/physical_encapsulation_identification.py",
        "artifacts/flagship_integration/BHSM_N12_GATE7_PHYSICAL_ENCAPSULATION_IDENTIFICATION_BRIDGE.json",
        "artifacts/action_extension/BHSM_RELATIVE_DIFFEOMORPHISM_GENERATOR_CHARGE_ADJUDICATION.json",
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
        "reset_contract_inventory_complete": inventory["inventory_complete"],
        "conditional_full_field_family_constructed": graph["maximal_authorized_family_constructed"],
        "single_graph_not_fabricated": not graph["single_graph_constructed"],
        "AE2_fixed_component_preserved": "Graph(U_R)" in graph["AE2_fixed_component"],
        "moving_pullback_linearization_verified": witness["moving_tensor_pullback_residual"] < 1.0e-8,
        "cotangent_transport_symplectic": witness["cotangent_symplectic_residual"] < 1.0e-12,
        "conditional_graph_equivariant": witness["equivariant_graph_residual"] < 1.0e-12,
        "relative_vector_conditionally_tangent": (
            witness["linearized_tangent_residual"] < 1.0e-8
            and witness["relative_attachment_variation_norm"] > 0.0
        ),
        "full_first_variation_explicit": variation["first_variation_derived_for_entire_conditional_family"],
        "first_variation_not_promoted_to_action": not variation["first_variation_action_owned"],
        "Norman_cycle_not_promoted_to_operator": not reconstruction["typed_cycle_is_physical_operator"],
        "no_master_fixed_point_substitution": (
            not reconstruction["master_self_reconstruction_map_exists"]
            and reconstruction["repository_Fix_P_s_singleton_found"] is False
        ),
        "N3_local_chart_scope_preserved": "NOT_A_GLOBAL" in reconstruction["N3_local_child_chart"]["scope"],
        "N12_relation_not_falsely_unique": (
            reconstruction["N12_event_child_relation"]["fixed_event_child_fiber_dimension"] == 67
            and not reconstruction["N12_event_child_relation"]["unique_physical_domain_selected"]
        ),
        "R4_has_base_map_witness": (
            uniqueness["same_topology_orientation_metric_volume_distinct_DF"]
            and uniqueness["missing_DF_changes_connection_components"]
        ),
        "R4_has_physical_boundary_witness": (
            uniqueness["both_nonfermion_graphs_admissible"]
            and uniqueness["boundary_potentials_differ"]
            and uniqueness["physical_transfer_spectra_differ"]
        ),
        "R1_R2_R3_rejected_R4_selected": (
            not uniqueness["R1_unique"] and not uniqueness["R2_representation_only"]
            and not uniqueness["R3_finite_or_small_physical_family"]
            and uniqueness["R4_uncontrolled_functional_choice"]
        ),
        "arbitrary_child_data_rejected_by_Norman_semantics": (
            "INCONSISTENT" in uniqueness["Norman_semantics_consistency"]["arbitrary_independent_child_boundary_data"]
        ),
        "active_domain_still_not_tangent": not tangent["relative_vector_tangent_to_active_BHSM_reset_domain"],
        "generator_charge_fail_closed": (
            tangent["Hamiltonian_generator"] is None
            and tangent["event_charge_Q_e"] is None
            and tangent["child_charge_Q_c"] is None
            and tangent["relative_charge_Q_rel"] is None
        ),
        "G4_U_D_retained": (
            tangent["differentiability_class"] == "G4"
            and tangent["charge_class"] == "U"
            and hindsight["outcome"] == "D"
        ),
        "second_order_not_overlaunched": not second["second_variation_required_now"],
        "positive_Hopf_rotor_not_quotiented": (
            hopf["relative_energy_positive"] and hopf["blanket_Hopf_quotient_rejected"]
        ),
        "minimum_missing_law_is_smaller_than_free_child_data": (
            reconstruction["minimum_information_is_not_full_F_B"]
            and reconstruction["minimum_missing_law"] == EXACT_NEXT_OBJECT
        ),
        "no_new_physics_inserted": not claims["new_physical_postulate_inserted"],
        "frozen_predictions_unchanged": not claims["frozen_predictions_changed"],
    }
    return {
        "artifact": "BHSM_FULL_FIELD_MOVING_RESET_GRAPH_DECISION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "status": STATUS,
        "R_class": R_CLASS,
        "differentiability_class": DIFFERENTIABILITY_CLASS,
        "charge_class": CHARGE_CLASS,
        "outcome": OUTCOME,
        "existing_reset_contract_inventory": inventory,
        "field_by_field_attachment_rules": rules,
        "conditional_full_field_reset_graph": graph,
        "first_moving_domain_variation": variation,
        "transport_and_tangent_witness": witness,
        "reconstruction_determinism_audit": reconstruction,
        "uniqueness_and_ambiguity": uniqueness,
        "relative_tangent_and_generator": tangent,
        "second_order_and_downstream": second,
        "Hopf_rotor_adversarial_result": hopf,
        "VALIDATED": hindsight["VALIDATED"],
        "INVALIDATED": hindsight["INVALIDATED"],
        "REDUNDANT": hindsight["REDUNDANT"],
        "OPEN": hindsight["OPEN"],
        "DECISION_POWER": hindsight["DECISION_POWER"],
        "EXACT_NEXT_OBJECT": EXACT_NEXT_OBJECT,
        "claim_boundary": claims,
        "source_sha256": hashes,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def main() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(build_payload()), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(main())
