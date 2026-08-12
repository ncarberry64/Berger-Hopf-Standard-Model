from bhsm.interface.aether_semiclassical_conformal_constraint_v15_38 import (
    completion_payload,
    conformal_constraint_contract,
    deterministic_json,
    remaining_equation_gate,
    round_positive_energy_obstruction,
    solve_conformal_hamiltonian_constraint,
)


def test_round_constraint_factorization_excludes_positive_child_energy():
    result = round_positive_energy_obstruction()
    assert "(y-1)^2" in result["factorization"]
    assert result["C_round_nonpositive_for_positive_radius"]
    assert result["equality_only_at_identity_radius"]
    assert result["round_radius_adjustment_can_solve_child_constraint"] is False


def test_conformal_constraint_contract_contains_no_free_pressure():
    result = conformal_constraint_contract()
    assert "R_h=" in result["scalar_curvature"]
    assert "rho_FR=" in result["FR_energy_density"]
    assert result["pole_domain"].startswith("u_prime")


def test_nonround_conformal_hamiltonian_constraint_companion_converges():
    result = solve_conformal_hamiltonian_constraint(
        pole_cutoff=2e-3, homotopy_steps=8, tolerance=7e-4
    )
    assert result["connected_by_homotopy_to_round_identity_branch"]
    assert result["Hamiltonian_constraint_companion_solved"]
    assert result["nonround_response_nonzero"]
    assert result["maximum_pointwise_constraint_residual"] < 3e-2
    assert result["maximum_boundary_residual"] < 5e-5
    assert abs(result["FR_normalization_residual"]) < 5e-5


def test_remaining_full_euler_system_is_kept_open():
    result = remaining_equation_gate()
    assert result["Hamiltonian_constraint"].startswith("SOLVED")
    assert result["spatial_Einstein_equations"] == "OPEN"
    assert result["eta_Euler_equation_on_backreacted_metric"] == "OPEN"
    assert result["sigma_Euler_equation_on_backreacted_metric"] == "OPEN"
    assert result["complete_child_Hessian"] == "OPEN"


def test_payload_is_deterministic_and_does_not_claim_complete_child():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["nonround_Hamiltonian_constraint_companion_derived"]
    assert payload["claim_boundary"]["complete_stationary_child_solution_derived"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
