from index_theorem_hardening import INDEX_THEOREM_FINAL_GAP, build_index_theorem_hardening_report
from mirror_exclusion_hardening import MIRROR_EXCLUSION_FINAL_GAP, build_mirror_exclusion_hardening_report


def test_index_hardening_verifies_sector_kernel_but_does_not_overclaim():
    report = build_index_theorem_hardening_report()

    assert report.target_kernel_dimension == 3
    assert report.visible_kernel_count == 3
    assert report.formal_kernel_coordinates == (0, 18, 36)
    assert report.formal_kernel_sectors == ("lepton", "up", "down")
    assert report.exactly_one_each_sector is True
    assert report.coordinate_first_artifact_rejected is True
    assert report.accidental_extra_degeneracy_rejected is True
    assert report.empirical_output_fitting_used is False
    assert report.status == "INDEX_THEOREM_CONDITIONAL"
    assert report.theorem_complete is False
    assert report.exact_blocker == INDEX_THEOREM_FINAL_GAP


def test_mirror_hardening_reports_conditional_channels_without_upgrade():
    report = build_mirror_exclusion_hardening_report()

    assert report.mirror_candidate_count == 3
    assert report.chiral_channel_status == "CHIRAL_PROJECTOR_CLOSURE_CONDITIONAL"
    assert report.higgs_u1_channel_status == "HIGGS_U1_MIRROR_CHANNEL_CONDITIONAL"
    assert report.boundary_channel_status == "BOUNDARY_MIRROR_CHANNEL_CONDITIONAL"
    assert report.sector_labeled_alignment_used is True
    assert report.topographic_representation_rule_used is True
    assert report.status == "MIRROR_EXCLUSION_CONDITIONAL"
    assert report.theorem_complete is False
    assert report.exact_blocker == MIRROR_EXCLUSION_FINAL_GAP
