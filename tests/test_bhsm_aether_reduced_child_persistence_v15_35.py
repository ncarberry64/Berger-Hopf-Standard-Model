from bhsm.interface.aether_reduced_child_persistence_v15_35 import (
    completion_payload,
    deterministic_json,
    formation_to_child_event_classification,
    nonlinear_constraint_continuation_theorem,
    relative_periodic_reduced_child,
)


def test_relative_equilibrium_is_a_stable_negative_x_child():
    result = relative_periodic_reduced_child(points=12001)
    assert result["x_log_Rc_over_Rp"] < 0.0
    assert result["theta_dot"] > 0.0
    assert result["relative_period"] > 0.0
    assert result["linearly_stable_in_reduced_physical_enclosure_sector"]
    assert result["child_well_is_separated_from_seam"]


def test_reduced_physical_floquet_pair_has_unit_modulus():
    result = relative_periodic_reduced_child(points=12001)
    assert result["physical_floquet_moduli"] == [1.0, 1.0]
    first, second = result["physical_floquet_pair"]
    assert first["real"] == second["real"]
    assert first["imag"] == -second["imag"]
    assert result["cyclic_unit_multipliers_removed"]
    assert result["gauge_diffeomorphism_multipliers_removed"]


def test_full_constraint_continuation_gate_is_not_a_passive_stabilizer_claim():
    result = nonlinear_constraint_continuation_theorem()
    assert "H_ell_ell-H_ell_I" in result["on_shell_Hessian"]
    assert result["ordinary_positive_auxiliary_modes_claimed_to_stabilize"] is False
    assert result["direct_localized_cyclic_term_is_the_positive_contribution"]
    assert len(result["what_remains_to_calculate"]) == 5


def test_event_is_classified_without_fake_capture_or_kick():
    result = formation_to_child_event_classification()
    assert result["negative_mode_is_transition_coordinate"]
    assert result["orientation_selected_child_branch"].startswith("ell<0")
    assert result["dissipative_capture_inserted"] is False
    assert result["arbitrary_kick_inserted"] is False


def test_payload_is_deterministic_and_preserves_claim_boundary():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["reduced_relative_periodic_child_derived"]
    assert payload["claim_boundary"]["complete_constraint_solved_child_derived"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
