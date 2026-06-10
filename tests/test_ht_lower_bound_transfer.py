from math import isclose

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from ht_lower_bound_transfer import (
    HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_INDEX_MIRROR,
    INDEX_THEOREM_FINAL_GAP,
    build_ht_lower_bound_transfer_sprint_report,
)


def test_ht_lower_bound_transfer_stops_at_index_mirror_blocker():
    report = build_ht_lower_bound_transfer_sprint_report()

    assert report.complete_operator_status == "COMPLETE_OPERATOR_IDENTIFICATION_PROVEN"
    assert report.action_uniqueness_status == "COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED"
    assert report.commutator_control_status == "PROJECTOR_COMMUTATOR_CONTROL_CLOSED"
    assert report.projector_graph_domain_status == "PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN"
    assert report.formal_kernel_coordinates == (0, 18, 36)
    assert report.formal_kernel_sectors == ("lepton", "up", "down")
    assert report.old_coordinate_first_kernel_used is False
    assert report.clears_required_threshold is True
    assert report.represented_terms_lower_bound_safe is True
    assert report.status == HT_LOWER_BOUND_TRANSFER_BLOCKED_BY_INDEX_MIRROR
    assert report.exact_blocker == INDEX_THEOREM_FINAL_GAP
    assert report.theorem_complete is False


def test_ht_lower_bound_transfer_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_ht_lower_bound_transfer_sprint_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]
    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
