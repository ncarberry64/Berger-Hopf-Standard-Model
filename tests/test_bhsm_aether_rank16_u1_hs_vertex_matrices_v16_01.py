import numpy as np

from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import (
    matrix_contract_witness,
    periodic_first_derivative,
    rank16_trace_ledger,
    rank16_u1_hs_responses,
)


SYNTHETIC_CYCLE = {
    "rows": [
        {
            "time": time,
            "boundary_lapse": 1.0 + 0.1 * time,
            "M4_spatial_radius": 1.0 + 0.05 * time,
        }
        for time in np.linspace(0.0, 0.1, 8)
    ]
}


def test_rank16_and_hs_trace_weights_are_fixed():
    result = rank16_trace_ledger()
    assert result["three_family_hypercharge_square_trace"] == 10.0
    assert result["effective_HS_hypercharge_square_weight"] == 1.0
    assert result["three_family_unit_EC_HS_Dirac_pairings"] == 24


def test_periodic_first_derivative_is_antihermitian():
    result = periodic_first_derivative(8, 0.1)
    assert np.linalg.norm(result + result.conj().T) < 1.0e-14
    assert np.linalg.matrix_rank(result, tol=1.0e-10) == 7


def test_first_order_squared_operator_vertices_are_hermitian():
    result = matrix_contract_witness()
    for row in result.values():
        assert row["operator_Hermitian_residual"] < 1.0e-12
        assert row["vertex_Hermitian_residual"] < 1.0e-12
        assert row["contact_Hermitian_residual"] < 1.0e-12
        assert row["minimum_operator_eigenvalue"] > 0.0


def test_low_level_rank16_responses_are_joint_and_finite():
    result = rank16_u1_hs_responses(
        SYNTHETIC_CYCLE, points=6, maximum_level=0
    )
    assert np.isfinite(result["U1_delta_K_magnetic_seed"])
    assert np.isfinite(result["U1_delta_K_electric_seed"])
    assert np.isfinite(result["HS_delta_Z_seed"])
    assert result["independent_channel_pairing_multiplicities"] == {
        "up": 9, "down": 9, "charged_lepton": 3, "neutrino": 3,
    }
    assert result["single_collective_direction_selected_by_current_calculation"] is False
    assert result["rank16_group_and_unit_HS_vertices_share_one_geometry"]
