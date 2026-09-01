from full_ht_theorem_final import FULL_HT_THEOREM_PROVEN, build_full_ht_theorem_final_report


def test_full_ht_final_closes_when_all_required_nodes_are_proven():
    report = build_full_ht_theorem_final_report()

    assert report.complete_operator_status == "COMPLETE_OPERATOR_IDENTIFICATION_PROVEN"
    assert report.action_uniqueness_status == "COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED"
    assert report.commutator_control_status == "PROJECTOR_COMMUTATOR_CONTROL_CLOSED"
    assert report.projector_graph_domain_status == "PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN"
    assert report.lower_bound_transfer_status == "HT_LOWER_BOUND_TRANSFER_PROVEN"
    assert report.index_status == "INDEX_THEOREM_PROVEN"
    assert report.mirror_status == "MIRROR_EXCLUSION_PROVEN"
    assert report.final_result == FULL_HT_THEOREM_PROVEN
    assert report.exact_blocker == ""
    assert report.theorem_complete is True
    assert report.open_or_conditional_nodes == ()
