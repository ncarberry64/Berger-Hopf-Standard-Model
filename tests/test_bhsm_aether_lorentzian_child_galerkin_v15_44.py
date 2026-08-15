import numpy as np

from bhsm.interface.aether_lorentzian_child_galerkin_v15_44 import (
    completion_payload,
    deterministic_json,
    initial_evolution_data,
    lorentzian_reduction_contract,
    odd_enclosure_linearization,
    reduced_lagrangian,
)


def test_lorentzian_contract_uses_complete_response_action():
    contract = lorentzian_reduction_contract()
    assert contract["response"].startswith("sigma=C_J")
    assert contract["carrier"] == "Lambda=1-4sigma^2"
    assert contract["new_continuous_coefficient"] is False


def test_initial_Euler_data_has_regular_invertible_Legendre_map():
    data = initial_evolution_data()
    assert data["Legendre_map_invertible"]
    assert data["finite_acceleration"]
    assert data["eta_Legendre_minimum"] > 0.0
    assert data["reduced_Hamiltonian_constraint_residual"] < 2e-7
    assert len(data["accelerations"]) == 9


def test_orientation_odd_enclosure_sector_has_real_growth_direction():
    data = initial_evolution_data()
    result = odd_enclosure_linearization(data, points=120)
    assert result["orientation_odd_enclosure_direction_grows"]
    assert result["largest_real_growth_rate"] > 1.0
    assert result["Floquet_claim"] is False


def test_lagrangian_is_even_under_time_reversal():
    data = initial_evolution_data()
    q = np.asarray(data["coordinates"])
    velocity = np.asarray(data["velocities"])
    assert abs(
        reduced_lagrangian(q, velocity, points=180)
        - reduced_lagrangian(q, -velocity, points=180)
    ) < 1e-10


def test_payload_is_deterministic_and_trajectory_is_still_active():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["Lorentzian_reduced_Euler_operator_derived"]
    assert payload["claim_boundary"]["nonlinear_encapsulation_trajectory_integrated"]
    assert payload["claim_boundary"]["negative_child_scale_reached"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
