"""Materialize the reset/charge/carrier cycle adjudication."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.reset_charge_carrier_dependency_cycle_adjudication import (  # noqa: E402
    CG_CLASS,
    EDGE_CLASSES,
    EXACT_NEXT_OBJECT,
    GE_CLASS,
    HJ_CLASS,
    INC_CLASS,
    LOOP_CLASS,
    adjudication_payload,
)


TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_RESET_CHARGE_CARRIER_DEPENDENCY_CYCLE_ADJUDICATION.json"
)
INPUTS = (
    ROOT / "src/bhsm/interface/reset_charge_carrier_dependency_cycle_adjudication.py",
    ROOT / "scripts/materialize_reset_charge_carrier_dependency_cycle_adjudication.py",
    ROOT / "tests/test_reset_charge_carrier_dependency_cycle_adjudication.py",
    ROOT / "theory/bhsm_reset_charge_carrier_dependency_cycle_adjudication.md",
    ROOT / "src/bhsm/interface/reset_correspondence_stationarity_adjudication.py",
    ROOT / "src/bhsm/interface/relative_diffeomorphism_generator_charge_adjudication.py",
    ROOT / "src/bhsm/interface/boundary_improved_event_mode_envelopment_charge_map_adjudication.py",
    ROOT / "src/bhsm/interface/completion/global_envelopment_cap_selection_v14_60.py",
    ROOT / "src/bhsm/interface/completion/full_global_envelopment_v14_61.py",
    ROOT / "src/bhsm/interface/completion/global_attachment_incidence_curvature_v14_68.py",
    ROOT / "src/bhsm/interface/completion/tensor_differential_incidence_v14_69.py",
    ROOT / "src/bhsm/interface/completion/aether_reconstruction_v15_0.py",
    ROOT / "src/bhsm/interface/aether_dynamical_correspondence_v15_1.py",
    ROOT / "src/bhsm/interface/aether_generator_selection_v15_2.py",
    ROOT / "src/bhsm/interface/aether_event_algebra_state_v15_4.py",
    ROOT / "src/bhsm/interface/aether_master_closure_v15_5.py",
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
    graph = result["graph"]
    cycle = result["cycle_analysis"]
    routes = result["route_classifications"]
    primitive = result["primitive_constraint"]
    downstream = result["downstream"]
    claims = result["claim_boundary"]
    node_ids = {node["id"] for node in graph["nodes"]}
    validation = {
        "all_required_nodes_present": {
            "reset_graph", "nonfermion_Ls", "moving_variation", "tangent_domain",
            "theta", "generator_xi", "hamiltonian", "reference", "event_mode_charge",
            "available_charge", "child_seam_charge", "envelopment_increment", "rho_hold",
            "energetic_carrier", "actual_stabilizer", "physical_projectors",
            "event_child_incidence", "active_response", "reduced_reset", "beta",
            "graph_jets", "S1", "S2", "S3", "S4", "full_attachment",
        }.issubset(node_ids),
        "all_edges_typed": all(edge["classification"] in EDGE_CLASSES for edge in graph["edges"]),
        "all_edge_endpoints_exist": all(
            edge["source"] in node_ids and edge["target"] in node_ids for edge in graph["edges"]
        ),
        "true_cycle_computed": cycle["cycle_exists"] and cycle["cyclic_component_count"] == 1,
        "graph_feedback_cut_computed": (
            cycle["minimum_feedback_vertex_cardinality"] == 2
            and all("reset_graph" in cut for cut in cycle["minimum_feedback_vertex_sets"])
        ),
        "one_coupled_functional_is_minimum_physical_set": (
            result["minimum_primitive_set"]["cardinality"] == 1
            and result["minimum_primitive_set"]["set"] == ["P-A*"]
            and result["minimum_primitive_set"]["one_object_sufficient"]
        ),
        "deep_routes_fail_closed": (
            routes["CA_to_GA"]["classification"] == CG_CLASS == "CG3"
            and routes["global_envelopment"]["classification"] == GE_CLASS == "GE3"
            and routes["boundary_HJ"]["classification"] == HJ_CLASS == "HJ3"
            and routes["event_child_incidence"]["classification"] == INC_CLASS == "INC3"
            and all(not route["breaks_cycle"] for route in routes.values())
        ),
        "all_targeted_recovery_concepts_adjudicated": (
            len(result["targeted_recovery_matrix"]) == 34
            and len({row["concept"] for row in result["targeted_recovery_matrix"]}) == 34
        ),
        "LOOP3_is_not_implemented_physics": (
            result["loop_verdict"] == LOOP_CLASS == "LOOP3"
            and primitive["value"] is None
            and not primitive["implemented"]
            and not primitive["tuned"]
        ),
        "one_infinite_dimensional_functional_degree": (
            primitive["minimum_independent_choice_count"] == 1
            and primitive["free_functional_degrees"].startswith("ONE_REAL_INVARIANT_FUNCTIONAL")
        ),
        "downstream_and_N12_firewall_preserved": (
            downstream["newly_unlocked_physical_objects"] == []
            and downstream["N12_rank_added"] == 0
            and downstream["N12_residual_before_time_quotient"] == 67
            and downstream["N12_residual_after_time_quotient"] == 66
        ),
        "exact_next_object_recorded": result["exact_next_object"] == EXACT_NEXT_OBJECT,
        "one_owner_question_prepared": isinstance(result["owner_question_for_handoff_only"], str),
        "claim_firewall_preserved": not any(claims.values()),
    }
    source_hashes = {str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path) for path in INPUTS}
    return {
        "artifact": "BHSM_RESET_CHARGE_CARRIER_DEPENDENCY_CYCLE_ADJUDICATION",
        "scientific_result": (
            "LOOP3__ONE_TRUE_DIRECTED_SCC_REQUIRES_ONE_NEW_ACTION_OWNED_"
            "COVARIANT_INTERFACE_GENERATING_FUNCTIONAL_EQUIVALENCE_CLASS;_"
            "NO_VALUE_OR_COEFFICIENT_IS_SELECTED"
        ),
        "adjudication": result,
        "VALIDATED": [
            "typed machine-readable prerequisite graph and deterministic Tarjan SCC computation",
            "one 25-node active reset-charge-carrier SCC",
            "minimum graph feedback cut has two state nodes while one coupled functional primitive supplies both stationarity equations",
            "CG3, GE3, HJ3, INC3, and LOOP3",
            "P-A* is constrained but not instantiated",
            "N12 residual remains 67, or 66 after the owned time quotient",
        ],
        "INVALIDATED": [
            "existing action already selects a full-field event-child reset graph",
            "historical global-envelopment witness coefficients are physical inputs",
            "the current on-shell regional action independently defines the missing principal function",
            "local or reduced incidence is the complete physical event-child functor",
        ],
        "REDUNDANT": [
            "repeating levelwise covariance, BRST, moving-graph-family, carrier, and charge-map adjudications",
            "treating a graph-theoretic node deletion as a physical primitive",
            "adding a carrier alone without a generating relation",
        ],
        "OPEN": [
            EXACT_NEXT_OBJECT,
            "the value/form of P-A* under the listed covariance and conservation constraints",
            "every physical downstream object beginning with its coupled stationarity equations",
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
        "source_sha256": source_hashes,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        failed = [key for key, value in payload["validation"].items() if not value]
        raise RuntimeError("cycle adjudication validation failed: " + ", ".join(failed))
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
