import pytest

from bhsm.interface import aether_post_cut_dirac_constraint_reduction_v15_49 as constrained


@pytest.fixture(scope="module")
def payload():
    return constrained.completion_payload()


def test_lapse_shift_contract_is_the_dirac_multiplier_system():
    contract = constrained.multiplier_contract()
    assert len(contract["constraints"]) == 5
    assert contract["radial_boundary_shift_flux"] == 0.0
    assert contract["new_continuous_coefficient"] is False


def test_joint_constraint_projection_closes_and_preserves_orientation(payload):
    result = payload["constraint_projected_initial_data"]
    assert result["success"] is True
    assert result["maximum_constraint_residual"] < 2e-8
    assert result["independent_grid_maximum_constraint_residual"] < 6e-4
    assert result["gauge"].startswith("f=chi")
    assert result["velocities"][7:] == [0.0, 0.0]
    assert payload["initial_Dirac_vector_field"]["matrix_rank"] == 11
    assert payload["initial_Dirac_vector_field"]["gauge_modes_removed"] == 2
    assert result["child_scale_velocity"] < 0.0


def test_completion_selects_constrained_flow_without_overclaim(payload):
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["nonconstant_lapse_shift_constraints_reduced"]
    assert payload["claim_boundary"]["full_constrained_flow_integrated"] is True
    assert payload["controlled_Dirac_reduced_flow"]["final_child_scale_x"] < 0.0
    assert payload["claim_boundary"]["persistent_particle_derived"] is False
    event = payload["extended_branch_event"]
    assert event["last_regular_state"]["minimum_lapse"] > 0.0
    assert event["last_regular_state"]["minimum_eta_Legendre"] > 0.0
    assert event["last_regular_state"]["turning_point_count"] == 0
    assert event["relative_periodic_return_reached"] is False
    assert event["foundational_no_go_claimed"] is False


def test_payload_json_is_deterministic(payload):
    assert constrained.deterministic_json(payload) == constrained.deterministic_json(
        constrained.completion_payload()
    )
