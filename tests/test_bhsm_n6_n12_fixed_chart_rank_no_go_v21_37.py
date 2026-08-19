from bhsm.interface.aether_n6_n12_fixed_chart_rank_no_go_v21_37 import (
    fixed_chart_rank_no_go_audit,
)


def test_fixed_chart_rank_no_go_is_dimensionally_exact_and_fail_closed():
    audit = fixed_chart_rank_no_go_audit()

    assert audit["validation_passed"] is True
    assert audit["actual_dimensions"]["new_state_directions"] == 96
    assert audit["actual_dimensions"]["new_physical_rows"] == 24
    assert audit["theorem"]["derivative_consequence"].endswith(
        "rank(D_F0)<=33<57"
    )
    assert audit["scope"]["physical_obstruction_claimed"] is False
    assert audit["linear_cover_status"]["validated"] is True
    assert audit["linear_cover_status"][
        "upgraded_to_nonlinear_continuation"
    ] is False
    assert audit["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert audit["Q_XI_READOUT_UNLOCKED"] is False
    assert audit["FULL_BHSM_COMPLETE"] is False


def test_each_regular_fixed_endpoint_route_loses_one_required_property():
    routes = fixed_chart_rank_no_go_audit()[
        "exhausted_regular_endpoint_routes"
    ]

    assert routes["omit_N12_high_rows"]["full_N12_normal_rank"] is False
    assert routes["retain_N12_high_rows"]["N6_rooted"] is False
    assert routes["scale_N12_high_rows_to_zero_at_t0"][
        "full_N12_normal_rank"
    ] is False
    assert routes["add_Bh_or_subtract_endpoint_source"][
        "unchanged_N6_endpoint_map"
    ] is False
