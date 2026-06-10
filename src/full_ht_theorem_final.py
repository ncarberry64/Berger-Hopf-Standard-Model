"""No-churn sprint final H_T theorem decision."""

from __future__ import annotations

from dataclasses import dataclass

from complete_operator_action_uniqueness_decision import COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED, build_complete_operator_action_uniqueness_decision
from complete_operator_identification_closure import build_complete_operator_identification_closure_report
from complete_twisted_dirac_operator import COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
from ht_lower_bound_transfer import HT_LOWER_BOUND_TRANSFER_PROVEN, build_ht_lower_bound_transfer_sprint_report
from index_theorem_hardening import build_index_theorem_hardening_report
from mirror_exclusion_hardening import build_mirror_exclusion_hardening_report
from projector_commutator_control_decision import PROJECTOR_COMMUTATOR_CONTROL_CLOSED, build_projector_commutator_control_decision
from projector_graph_domain_stability import PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN, build_projector_graph_domain_stability_report


FULL_HT_THEOREM_PROVEN = "FULL_HT_THEOREM_PROVEN"
STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"


@dataclass(frozen=True)
class FullHTTheoremFinalReport:
    final_result: str
    theorem_complete: bool
    exact_blocker: str
    complete_operator_status: str
    action_uniqueness_status: str
    commutator_control_status: str
    projector_graph_domain_status: str
    lower_bound_transfer_status: str
    index_status: str
    mirror_status: str
    open_or_conditional_nodes: tuple[str, ...]
    final_paper_allowed: bool
    limitations: tuple[str, ...]


def build_full_ht_theorem_final_report() -> FullHTTheoremFinalReport:
    operator = build_complete_operator_identification_closure_report()
    action = build_complete_operator_action_uniqueness_decision()
    commutator = build_projector_commutator_control_decision()
    graph = build_projector_graph_domain_stability_report()
    lower = build_ht_lower_bound_transfer_sprint_report()
    index = build_index_theorem_hardening_report()
    mirror = build_mirror_exclusion_hardening_report()
    node_statuses = {
        "complete_operator": operator.final_status,
        "action_uniqueness": action.final_result,
        "commutator_control": commutator.final_result,
        "projector_graph_domain": graph.status,
        "lower_bound_transfer": lower.status,
        "index_theorem": index.status,
        "mirror_exclusion": mirror.status,
    }
    open_or_conditional = tuple(
        name for name, status in node_statuses.items() if "OPEN" in status or "CONDITIONAL" in status or "BLOCKED" in status
    )
    hard_failure = any("FAIL" in status for status in node_statuses.values())
    all_closed = (
        operator.final_status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
        and action.final_result == COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED
        and commutator.final_result == PROJECTOR_COMMUTATOR_CONTROL_CLOSED
        and graph.status == PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN
        and lower.status == HT_LOWER_BOUND_TRANSFER_PROVEN
        and index.theorem_complete
        and mirror.theorem_complete
    )
    if hard_failure:
        result = BHSM_THEOREM_FAILURE
        blocker = next(name for name, status in node_statuses.items() if "FAIL" in status)
    elif all_closed:
        result = FULL_HT_THEOREM_PROVEN
        blocker = ""
    else:
        result = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
        blocker = lower.exact_blocker or index.exact_blocker or mirror.exact_blocker
    return FullHTTheoremFinalReport(
        final_result=result,
        theorem_complete=result == FULL_HT_THEOREM_PROVEN,
        exact_blocker=blocker,
        complete_operator_status=operator.final_status,
        action_uniqueness_status=action.final_result,
        commutator_control_status=commutator.final_result,
        projector_graph_domain_status=graph.status,
        lower_bound_transfer_status=lower.status,
        index_status=index.status,
        mirror_status=mirror.status,
        open_or_conditional_nodes=open_or_conditional,
        final_paper_allowed=False,
        limitations=(
            "The full H_T theorem is not marked proven while any required node remains conditional or blocked.",
            "No final paper preparation is allowed from this sprint unless the full theorem package is complete.",
        ),
    )
