from bhsm.interface.aether_york_response_initial_data_v15_42 import (
    completion_payload,
    deterministic_json,
    solve_york_response_initial_data,
    york_constraint_contract,
)


def test_york_contract_uses_response_and_pure_trace_geometry():
    contract = york_constraint_contract()
    assert contract["material_response"].startswith("sigma=C_J")
    assert contract["extrinsic_curvature"].startswith("K_ij=H")
    assert contract["new_physical_coefficient"] is False


def test_pure_trace_continuation_selects_no_real_CMC_slice():
    result = solve_york_response_initial_data(
        homotopy_steps=8, tolerance=2e-4
    )
    assert result["H_squared_positive"] is False
    assert result["H"] is None
    assert result["physical_real_CMC_initial_data"] is False
    assert result["maximum_pointwise_Hamiltonian_residual"] < 3e-3
    assert result["momentum_constraint_residual"] == 0.0
    assert abs(result["FR_normalization_residual"]) < 2e-5
    assert result["maximum_boundary_residual"] < 2e-5
    assert result["conformal_response_nonconstant"]


def test_payload_is_deterministic_and_initial_data_is_not_persistence():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["response_constrained_real_CMC_initial_data_solved"] is False
    assert payload["claim_boundary"]["trace_free_shape_shear_required"]
    assert payload["claim_boundary"]["Lorentzian_encapsulation_evolution_solved"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
