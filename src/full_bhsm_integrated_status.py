from __future__ import annotations

from typing import Dict, Tuple

import full_bhsm_closure_dependency_graph as graph
import full_bhsm_freeze_boundary as freeze
import rg_transport_interface as rg


PUBLIC_STATUS = graph.PUBLIC_STATUS

TARGET_RG = "RG_TRANSPORT_RULE_DERIVATION"
TARGET_BRIDGE = "BRIDGE_MAGNITUDE_ACTION_SOURCE"
TARGET_NEUTRAL = "NEUTRAL_HESSIAN_ACTION_SOURCE"
TARGET_THRESHOLD = "FULL_THRESHOLD_OPERATOR_SOURCE"


def _count_by_status_group() -> Dict[str, int]:
    counts = {
        "derived_or_conditional_count": 0,
        "candidate_count": 0,
        "open_localizable_count": 0,
        "open_count": 0,
        "invalidated_count": 0,
    }
    for node in graph.closure_graph_nodes():
        status = node.status
        if status.startswith("DERIVED"):
            counts["derived_or_conditional_count"] += 1
        elif "CANDIDATE" in status or "STRUCTURALLY_INTERESTING_BRANCH" == status:
            counts["candidate_count"] += 1
        elif status == "OPEN_LOCALIZABLE":
            counts["open_localizable_count"] += 1
        elif status in {"OPEN", "NO_THRESHOLD_SOURCE_FOUND", "REFERENCE_SLOT_NOT_THRESHOLD_TARGET"}:
            counts["open_count"] += 1
        elif status == "INVALIDATED_DO_NOT_CLAIM":
            counts["invalidated_count"] += 1
    return counts


def recommended_targets_ranked() -> Tuple[str, ...]:
    rg_status = rg.STATUS_TABLE["RG_transport_interface_v1"]
    graph_nodes = graph.node_map()
    if rg_status == "STRUCTURAL_SCAFFOLD" and graph_nodes["RG_transport_interface"].status == "OPEN":
        return (TARGET_RG, TARGET_BRIDGE, TARGET_NEUTRAL, TARGET_THRESHOLD)
    if graph_nodes["beta_f_reference_bridge_magnitude"].status == "OPEN_LOCALIZABLE":
        return (TARGET_BRIDGE, TARGET_RG, TARGET_NEUTRAL, TARGET_THRESHOLD)
    if graph_nodes["neutral_Hessian_symbolic_form"].status == "OPEN_LOCALIZABLE":
        return (TARGET_NEUTRAL, TARGET_RG, TARGET_BRIDGE, TARGET_THRESHOLD)
    return (TARGET_THRESHOLD, TARGET_RG, TARGET_BRIDGE, TARGET_NEUTRAL)


def next_recommended_mathematical_target() -> str:
    return recommended_targets_ranked()[0]


def report_as_dict() -> Dict[str, object]:
    counts = _count_by_status_group()
    return {
        "id": "PO-BH-full-BHSM-integrated-status-v1",
        "title": "Full BHSM Integrated Status v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "total_node_count": graph.report_as_dict()["node_count"],
        **counts,
        "freeze_class_counts": freeze.freeze_class_counts(),
        "rg_interface_status": rg.STATUS_TABLE["RG_transport_interface_v1"],
        "numerical_closure": "OPEN",
        "next_recommended_mathematical_target": next_recommended_mathematical_target(),
        "ranked_recommended_targets": list(recommended_targets_ranked()),
        "recommendation_scope": "dependency-graph recommendation, not final scientific truth",
        "claim_boundary": "Integrated status localizes blockers and does not claim numerical closure.",
    }
