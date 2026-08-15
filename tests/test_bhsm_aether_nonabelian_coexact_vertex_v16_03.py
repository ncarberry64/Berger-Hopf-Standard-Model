import numpy as np

from bhsm.interface.aether_nonabelian_coexact_vertex_v16_03 import (
    adjoint_magnetic_response,
    coexact_operator_and_magnetic_vertices,
    curl_spectrum_witness,
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


def test_exact_coexact_and_longitudinal_curl_spectrum():
    for row in curl_spectrum_witness(6):
        assert np.allclose(
            row["coexact_eigenvalues"], row["expected_coexact_eigenvalues"],
            rtol=0.0, atol=1.0e-12,
        )
        assert row["longitudinal_dimension"] == row["expected_longitudinal_dimension"]


def test_projected_operator_and_vertices_are_hermitian():
    operator, vertex, contact = coexact_operator_and_magnetic_vertices(
        2, np.asarray([1.0, 1.1, 1.05, 0.98]), 0.1,
        np.asarray([0.2, -0.1, 0.3, 0.05]),
    )
    for matrix in (operator, vertex, contact):
        assert np.linalg.norm(matrix - matrix.conj().T) < 1.0e-11
    assert np.linalg.eigvalsh(operator)[0] > 0.0


def test_adjoint_response_has_fixed_casimir_scaling():
    result = adjoint_magnetic_response(
        SYNTHETIC_CYCLE, points=6, maximum_level=2
    )
    assert np.isfinite(result["unit_adjoint_delta_KB"])
    assert result["SU3_adjoint_delta_KB"] == 1.5 * result["SU2_adjoint_delta_KB"]
    assert result["U1_adjoint_delta_KB"] == 0.0
    assert result["longitudinal_and_ghost_removed_by_coexact_projection"]
