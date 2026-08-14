from bhsm.interface.aether_n3_event_complete_child_correspondence_v17_84 import (
    completion_payload,
    deterministic_json,
    event_to_child_correspondence_derivation,
)


def test_F_child_is_derived_but_current_firewall_has_zero_selection_rank():
    result = event_to_child_correspondence_derivation()
    assert "P_coker" in result["first_variation_derivation"][
        "reduced_solvability_map"
    ]
    current = result["current_firewall_evaluation"]
    assert current["differential_rank"] == 0
    assert current["can_select_a_point_on_near_flat_event_surface"] is False


def test_direct_N3_solve_waits_for_physical_boundary_blocks():
    result = event_to_child_correspondence_derivation()
    assert result["event_architecture_verdict"][
        "direct_N3_solver_must_wait"
    ] is True
    assert result["physical_block_provenance"][
        "physical_blocks_action_derived"
    ] is False


def test_correspondence_derivation_validates_deterministically():
    first = completion_payload()
    second = completion_payload()
    assert first["validation_passed"] is True
    assert deterministic_json(first) == deterministic_json(second)
