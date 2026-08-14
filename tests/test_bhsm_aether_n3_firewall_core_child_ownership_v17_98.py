from bhsm.interface.aether_n3_firewall_core_child_ownership_v17_98 import (
    completion_payload,
)


def test_firewall_core_is_discrete_match_not_extra_continuous_row():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["firewall_core_child_ownership"]
    ownership = result["ownership_decision"]
    assert ownership["continuous_core_row_count"] == 0
    assert not ownership["setting_an_unknown_core_Calderon_operator_to_zero"]
    assert not ownership["microscopic_pregeometric_generator_derived"]
    assert result["firewall_discrete_match"]["all_rows_closed"]
    assert result["complete_retained_F_child"]["boundary_map_closed"]
    assert result["complete_retained_F_child"][
        "positive_duration_persistence_witness"
    ] == "OPEN"
    assert not payload["direct_N3_solve_authorized_next"]
