from fractions import Fraction

from bhsm.interface import aether_m4_standard_model_zeta_backreaction_v15_51 as zeta


def test_closed_s3_zeta_coefficients_and_sm_count():
    coefficients = zeta.zeta_coefficients()
    assert coefficients["real_conformal_scalar"] == Fraction(1, 240)
    assert coefficients["physical_massless_vector"] == Fraction(11, 120)
    assert coefficients["complex_two_component_Weyl"] == Fraction(17, 960)
    contract = zeta.standard_model_zeta_contract()
    assert contract["counts"]["complex_two_component_Weyl"] == 48
    assert contract["counts"]["physical_massless_vectors"] == 12
    assert contract["total_C_SM"] == "59/30"
    assert contract["all_local_anomalies_zero"]
    assert contract["Witten_parity_even"]


def test_zeta_term_is_shape_restoring_at_fixed_fiber_radius():
    result = zeta.shape_restoring_term(1.66630, 1.21895)
    assert result["child_scale_x"] < 0.0
    assert result["fixed_fiber_first_derivative"] < 0.0
    assert result["fixed_fiber_second_derivative"] > 0.0


def test_attached_constraint_projection_closes_without_new_coefficient():
    payload = zeta.completion_payload()
    assert payload["validation_passed"]
    projection = payload["attached_constraint_projection"]
    assert projection["success"]
    assert projection["maximum_constraint_residual"] < 2e-7
    assert projection["independent_grid_maximum_constraint_residual"] < 1.2e-3
    assert projection["child_scale_velocity"] < 0.0
    assert projection["time_reversal_applied_to_select_transported_orientation"]
    assert payload["initial_attached_Dirac_vector_field"]["matrix_rank"] == 11
    flow = payload["controlled_attached_Dirac_flow"]
    assert flow["exit_reason"] == "maximum_steps"
    assert flow["final_child_scale_x"] < 0.0
    assert flow["independent_grid_final_constraint_residual"] < 1.5e-3
    assert payload["claim_boundary"]["persistent_particle_derived"] is False
    event = payload["extended_attached_branch_event"]
    assert event["last_controlled_state"]["turning_point_count"] == 0
    assert event["free_conformal_attachment_produced_return"] is False
    assert event["free_conformal_attachment_sufficient_for_persistence"] is False
    assert event["coefficient_retuned"] is False


def test_payload_json_is_deterministic():
    payload = zeta.completion_payload()
    assert zeta.deterministic_json(payload) == zeta.deterministic_json(
        zeta.completion_payload()
    )
