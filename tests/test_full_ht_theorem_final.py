from full_ht_theorem_final import STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP, build_full_ht_theorem_final_report


def test_full_ht_final_cannot_close_with_conditional_nodes():
    report = build_full_ht_theorem_final_report()

    assert report.complete_operator_status == "COMPLETE_OPERATOR_IDENTIFICATION_PROVEN"
    assert report.action_uniqueness_status == "COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED"
    assert report.commutator_control_status == "PROJECTOR_COMMUTATOR_CONTROL_CLOSED"
    assert report.projector_graph_domain_status == "PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN"
    assert report.lower_bound_transfer_status == "HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_INDEX_MIRROR"
    assert report.index_status == "INDEX_THEOREM_CONDITIONAL"
    assert report.mirror_status == "MIRROR_EXCLUSION_CONDITIONAL"
    assert report.final_result == STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    assert report.exact_blocker == "INDEX_THEOREM_FINAL_GAP"
    assert report.theorem_complete is False
    assert report.final_paper_allowed is False
    assert {"lower_bound_transfer", "index_theorem", "mirror_exclusion"} <= set(report.open_or_conditional_nodes)
