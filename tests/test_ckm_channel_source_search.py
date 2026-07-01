from bhsm.interface.ckm_channel_equivalence import search_ckm_channel_sources


def test_ckm_channel_search_locates_sources_without_claiming_selection():
    report = search_ckm_channel_sources()
    assert report["all_sources_present"] is True
    assert report["N_16_occurs_in_artifacts"] is True
    assert report["bilinear_Vd_tensor_dual_identified"] is False
    assert report["maximal_sector_selection_rule_found"] is False
    assert report["empirical_inputs_used"] is False

