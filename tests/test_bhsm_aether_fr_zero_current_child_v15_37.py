from bhsm.interface.aether_fr_zero_current_child_v15_37 import (
    compact_constraint_reclassification,
    completion_payload,
    deterministic_json,
    fr_zero_current_ground_state_theorem,
    numerical_domain_check,
    stationary_zero_current_reduced_child,
)


def test_antiperiodic_ground_state_has_zero_current_and_nonzero_casimir():
    result = fr_zero_current_ground_state_theorem()
    assert result["expectation_J"] == 0.0
    assert result["expectation_J_squared"] == 0.25
    assert result["momentum_constraint_source"] == 0.0
    assert result["energy_nonzero"]
    assert result["physical_ground_orbit_count"] == 1


def test_numerical_domain_and_moments_close():
    result = numerical_domain_check(12001)
    assert result["domain_and_moments_verified"]
    assert abs(result["antiperiodic_value_residual"]) < 1e-12
    assert abs(result["antiperiodic_derivative_residual"]) < 1e-12


def test_zero_current_stationary_reduced_child_is_stable():
    result = stationary_zero_current_reduced_child(points=12001)
    assert result["child_scale_x"] < 0.0
    assert result["enclosure_curvature"] > 0.0
    assert result["enclosure_frequency_squared"] > 0.0
    assert abs(result["fixed_charge_formula_residual"]) < 1e-12
    assert result["Hopf_momentum_density_expectation"] == 0.0
    assert result["classical_internal_rotation_required"] is False


def test_classical_rotor_results_are_reclassified_not_hidden():
    result = compact_constraint_reclassification()
    assert result["v15_34_localized_inertia_and_Routh_energy"] == "PRESERVED"
    assert "UNCONSTRAINED_CHARGED_BRANCH" in result[
        "v15_35_lone_classical_relative_periodic_rotor"
    ]
    assert result["local_Hopf_shift_source_expectation"] == 0.0
    assert result["stress_fluctuation_backreaction_computed"] is False


def test_payload_is_deterministic_and_preserves_full_claim_boundary():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["compact_mean_momentum_constraint_closed"]
    assert payload["claim_boundary"]["complete_physical_child_derived"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
