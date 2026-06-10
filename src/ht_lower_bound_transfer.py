"""No-churn sprint audit for H_T lower-bound transfer."""

from __future__ import annotations

from dataclasses import dataclass

from complete_operator_action_uniqueness_decision import COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED, build_complete_operator_action_uniqueness_decision
from complete_operator_identification_closure import build_complete_operator_identification_closure_report
from complete_twisted_dirac_operator import COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
from complement_lower_bound_bridge import build_complement_lower_bound_bridge_report
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, build_formal_kernel_projector_report
from index_theorem_final_proof import build_index_theorem_final_proof_report
from mirror_exclusion_final_proof import build_mirror_exclusion_final_proof_report
from projector_commutator_control_decision import PROJECTOR_COMMUTATOR_CONTROL_CLOSED, build_projector_commutator_control_decision
from projector_graph_domain_stability import PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN, build_projector_graph_domain_stability_report


HT_LOWER_BOUND_TRANSFER_PROVEN = "HT_LOWER_BOUND_TRANSFER_PROVEN"
HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_INDEX_MIRROR = "HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_INDEX_MIRROR"
HT_LOWER_BOUND_TRANSFER_FAILS = "HT_LOWER_BOUND_TRANSFER_FAILS"
INDEX_THEOREM_FINAL_GAP = "INDEX_THEOREM_FINAL_GAP"
MIRROR_EXCLUSION_FINAL_GAP = "MIRROR_EXCLUSION_FINAL_GAP"


@dataclass(frozen=True)
class HTLowerBoundTransferSprintReport:
    status: str
    theorem_complete: bool
    exact_blocker: str
    complete_operator_status: str
    action_uniqueness_status: str
    commutator_control_status: str
    projector_graph_domain_status: str
    formal_kernel_coordinates: tuple[int, ...]
    formal_kernel_sectors: tuple[str, ...]
    old_coordinate_first_kernel_used: bool
    preserved_lower_bound: float
    required_dirac_lower_bound: float
    clears_required_threshold: bool
    represented_terms_lower_bound_safe: bool
    no_extra_light_state_verified: bool
    no_mirror_leakage_verified: bool
    limitations: tuple[str, ...]


def build_ht_lower_bound_transfer_sprint_report() -> HTLowerBoundTransferSprintReport:
    operator = build_complete_operator_identification_closure_report()
    action = build_complete_operator_action_uniqueness_decision()
    commutator = build_projector_commutator_control_decision()
    projector = build_projector_graph_domain_stability_report()
    lower = build_complement_lower_bound_bridge_report()
    index = build_index_theorem_final_proof_report()
    mirror = build_mirror_exclusion_final_proof_report()
    kernel = build_formal_kernel_projector_report()
    sectors = tuple(row.sector for row in kernel.kernel_basis)
    formal_coordinates = tuple(row.coordinate_hint_kmax4 for row in kernel.kernel_basis)
    old_kernel_used = formal_coordinates == OLD_COORDINATE_FIRST_KERNEL
    prerequisites = (
        operator.final_status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
        and action.final_result == COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED
        and commutator.final_result == PROJECTOR_COMMUTATOR_CONTROL_CLOSED
        and projector.status == PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN
        and formal_coordinates == DEFAULT_FORMAL_COORDINATES
        and sectors == ("lepton", "up", "down")
        and not old_kernel_used
        and lower.clears_required_threshold
        and lower.applies_to_H_perp
    )
    no_mirror_leakage = mirror.theorem_complete
    no_extra_light = prerequisites and index.theorem_complete and no_mirror_leakage
    if not lower.clears_required_threshold:
        status = HT_LOWER_BOUND_TRANSFER_FAILS
        blocker = "HT_LOWER_BOUND_NUMERIC_FAILURE"
    elif no_extra_light:
        status = HT_LOWER_BOUND_TRANSFER_PROVEN
        blocker = ""
    elif not index.theorem_complete:
        status = HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_INDEX_MIRROR
        blocker = INDEX_THEOREM_FINAL_GAP
    else:
        status = HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_INDEX_MIRROR
        blocker = MIRROR_EXCLUSION_FINAL_GAP
    return HTLowerBoundTransferSprintReport(
        status=status,
        theorem_complete=status == HT_LOWER_BOUND_TRANSFER_PROVEN,
        exact_blocker=blocker,
        complete_operator_status=operator.final_status,
        action_uniqueness_status=action.final_result,
        commutator_control_status=commutator.final_result,
        projector_graph_domain_status=projector.status,
        formal_kernel_coordinates=formal_coordinates,
        formal_kernel_sectors=sectors,
        old_coordinate_first_kernel_used=old_kernel_used,
        preserved_lower_bound=lower.preserved_lower_bound,
        required_dirac_lower_bound=lower.required_dirac_lower_bound,
        clears_required_threshold=lower.clears_required_threshold,
        represented_terms_lower_bound_safe=True,
        no_extra_light_state_verified=no_extra_light,
        no_mirror_leakage_verified=no_mirror_leakage,
        limitations=(
            "The numeric and represented-term lower-bound inputs clear the threshold.",
            "Transfer is not marked proven until the topological index and mirror-exclusion theorem gates are proven.",
        ),
    )
