from bhsm.interface.aether_momentum_balanced_shear_data_v15_43 import (
    completion_payload,
    deterministic_json,
    shear_constraint_contract,
    solve_momentum_balanced_shear_data,
)


def test_declared_shear_is_trace_free_transverse_and_coefficient_free():
    contract = shear_constraint_contract()
    assert contract["trace"] == "K=0"
    assert contract["radial_momentum_constraint"].startswith("D_j K")
    assert contract["new_current_inserted"] is False
    assert contract["new_continuous_coefficient"] is False


def test_shear_initial_data_solves_both_ADM_constraints():
    result = solve_momentum_balanced_shear_data(
        homotopy_steps=10, tolerance=3e-4
    )
    assert result["shear_amplitude_nonzero"]
    assert result["eta_Legendre_regular"]
    assert result["maximum_Hamiltonian_constraint_residual"] < 4e-3
    assert result["maximum_momentum_constraint_residual"] < 2e-8
    assert abs(result["FR_normalization_residual"]) < 2e-5
    assert result["maximum_boundary_residual"] < 2e-5


def test_payload_is_deterministic_and_does_not_overclaim_evolution():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"][
        "response_constrained_both_ADM_constraints_solved"
    ]
    assert payload["claim_boundary"][
        "full_spatial_Einstein_evolution_equations_solved"
    ] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
