from bhsm.interface.ckm_bidirectional_channel import search_ckm_bidirectional_sources


def test_bidirectional_source_search_preserves_target_convention_limit():
    report = search_ckm_bidirectional_sources()
    assert report["all_sources_present"] is True
    assert report["ckm_charged_current_target_identified"] is True
    assert report["hermitian_conjugate_present"] is True
    assert report["up_down_off_diagonal_interpretation_present"] is True
    assert report["target_convention_only"] is True
    assert report["bhsm_action_selects_adjoint_pair"] is False

