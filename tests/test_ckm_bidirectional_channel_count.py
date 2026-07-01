from bhsm.interface.ckm_bidirectional_channel import audit_bidirectional_channel_count


def test_bidirectional_and_competing_channel_counts_are_exact():
    report = audit_bidirectional_channel_count()
    assert report["s_u"] == 2
    assert report["s_d"] == 4
    assert report["N_one_way_ud"] == 8
    assert report["N_one_way_du"] == 8
    assert report["N_bidirectional_ud_du"] == 16
    assert report["N_sum_self"] == 21
    assert report["N_total_end"] == 49
    assert report["N_max_self"] == 16
    assert report["bidirectional_reciprocal_exact"] is True
    assert report["same_number_distinct_sources"] is True

