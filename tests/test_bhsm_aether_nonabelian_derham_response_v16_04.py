import numpy as np

from bhsm.interface.aether_nonabelian_derham_response_v16_04 import (
    derham_identity_witness,
    full_oneform_ghost_matrices,
    nonabelian_derham_response,
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


def test_exact_angular_derham_complex():
    for row in derham_identity_witness(6):
        assert row["curl_gradient_residual"] < 1.0e-12
        assert row["scalar_laplacian_residual"] < 1.0e-12
        assert (
            row["longitudinal_eigenvalue_count"]
            == row["expected_longitudinal_eigenvalue_count"]
        )


def test_full_oneform_and_ghost_vertices_are_hermitian():
    matrices = full_oneform_ghost_matrices(
        1,
        np.asarray([1.0, 1.05, 0.98, 1.02]),
        0.1,
        np.asarray([0.2, -0.1, 0.3, 0.05]),
    )
    for matrix in matrices.values():
        assert np.linalg.norm(matrix - matrix.conj().T) < 1.0e-11


def test_nonabelian_electric_and_magnetic_responses_share_derham_block():
    result = nonabelian_derham_response(
        SYNTHETIC_CYCLE, points=6, maximum_level=2
    )
    assert np.isfinite(result["SU2_adjoint_delta_KB"])
    assert np.isfinite(result["SU2_adjoint_delta_KE"])
    assert result["SU3_adjoint_delta_KB"] == 1.5 * result["SU2_adjoint_delta_KB"]
    assert result["SU3_adjoint_delta_KE"] == 1.5 * result["SU2_adjoint_delta_KE"]
    assert result["full_oneform_minus_two_complex_ghost_weight"]
    assert result["gyromagnetic_F0z_vertex_included"]
