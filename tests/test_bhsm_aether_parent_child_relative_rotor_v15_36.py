from bhsm.interface.aether_parent_child_relative_rotor_v15_36 import (
    compact_killing_momentum_constraint_theorem,
    completion_payload,
    constrained_relative_routhian_solution,
    deterministic_json,
    local_momentum_constraint_status,
    relative_rotor_terms,
    unlocalized_parent_inertia,
)


def test_compact_killing_constraint_rejects_a_lone_rotor():
    result = compact_killing_momentum_constraint_theorem()
    assert result["boundary_term"] == 0.0
    assert result["single_nonzero_Hopf_rotor_admissible"] is False
    assert result["event_degree_can_replace_countercharge"] is False
    assert "J_child+J_parent=0" in result["admissible_nonzero_sector"]


def test_parent_inertia_is_positive_and_relative_charge_sums_to_zero():
    assert unlocalized_parent_inertia() > 0.0
    result = relative_rotor_terms(-4.0, points=12001)
    assert result["I_child"] > 0.0
    assert result["I_parent"] > 0.0
    assert result["J_total"] == 0.0
    assert abs(result["energy_sum_residual"]) < 1e-12


def test_parallel_sum_is_smaller_than_each_inertia():
    result = relative_rotor_terms(0.0, points=12001)
    assert result["I_relative_parallel_sum"] < result["I_child"]
    assert result["I_relative_parallel_sum"] < result["I_parent"]


def test_zero_total_charge_relative_child_retains_finite_stable_minimum():
    result = constrained_relative_routhian_solution(points=12001)
    assert result["child_scale_x"] < 0.0
    assert result["finite_minimum_survives_compact_charge_constraint"]
    assert result["relative_child_curvature"] > 0.0
    assert result["omega_enclosure_squared"] > 0.0
    assert abs(result["stationarity_residual"]) < 2e-4


def test_local_hopf_shift_constraint_is_kept_open():
    result = local_momentum_constraint_status()
    assert result["radial_shift_alone_sufficient"] is False
    assert result["integrated_Killing_constraint_satisfied_by_relative_sector"]
    assert result["pointwise_shift_equation_solved"] is False


def test_payload_is_deterministic_and_retracts_single_rotor_claim():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["single_rotor_physical_child_claim_retracted"]
    assert payload["claim_boundary"]["complete_constraint_solved_child_derived"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
