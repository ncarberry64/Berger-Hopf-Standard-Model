import math

import numpy as np

from bhsm.interface.aether_response_constrained_child_galerkin_v15_41 import (
    completion_payload,
    deterministic_json,
    galerkin_fields,
    reduced_action_contract,
    round_branch_check,
    solve_response_constrained_galerkin,
)


def test_contract_uses_derived_sigma_and_constant_lapse_constraint():
    contract = reduced_action_contract()
    assert contract["response"].startswith("sigma=C_J")
    assert "Hamiltonian-constraint" in contract["constraint_semantics"]


def test_round_critical_branch_is_recovered():
    result = round_branch_check(260)
    assert result["round_critical_branch_recovered"]
    assert result["maximum_X_eta_residual"] < 1e-12


def test_regular_ansatz_preserves_response_endpoints_and_finite_geometry():
    fields = galerkin_fields(np.zeros(10), points=180)
    sigma = np.asarray(fields["sigma"])
    assert sigma[0] > -0.5 and sigma[-1] < 0.5
    assert np.all(np.diff(sigma) > 0.0)
    assert np.all(np.isfinite(np.asarray(fields["R7"])))


def test_spatial_projection_derives_moving_constraint_data():
    result = solve_response_constrained_galerkin(points=180, homotopy_steps=8)
    assert result["maximum_solve_grid_spatial_Euler_residual"] < 2e-4
    assert result["maximum_independent_grid_spatial_Euler_residual"] < 4e-3
    assert result["integrated_Hamiltonian_constraint_defect"] > 0.0
    assert result["uniform_shape_shear_squared_estimate"] > 0.0
    assert result["shape_shear_closes_integrated_constraint"]
    assert abs(result["projected_child_scale_x"]) < 1e-6


def test_payload_is_deterministic_and_does_not_call_projection_the_particle():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["full_two-pole_function-space_BVP_solved"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
