import numpy as np

from bhsm.interface.aether_common_source_frechet_response_v15_99 import (
    completion_payload,
    finite_difference_response_witness,
    frechet_first_response,
    physical_source_vertex_contract,
)


def test_first_response_is_basis_independent():
    operator = np.diag([2.0, 3.0, 5.0])
    vertex = np.asarray([[0.2, 0.4, 0.0], [0.4, -0.1, 0.3], [0.0, 0.3, 0.5]])
    rotation = np.asarray(
        [[1.0, 1.0, 0.0], [-1.0, 1.0, 0.0], [0.0, 0.0, np.sqrt(2.0)]]
    ) / np.sqrt(2.0)
    assert np.isclose(
        frechet_first_response(operator, vertex),
        frechet_first_response(
            rotation.T @ operator @ rotation, rotation.T @ vertex @ rotation
        ),
    )


def test_complex_hermitian_vertices_are_supported():
    operator = np.asarray([[2.0, 0.2j], [-0.2j, 3.0]])
    vertex = np.asarray([[0.1, 0.3j], [-0.3j, -0.2]])
    assert np.isfinite(frechet_first_response(operator, vertex))


def test_noncommuting_second_response_matches_finite_difference():
    assert finite_difference_response_witness()["relative_residual"] < 2.0e-8


def test_source_contract_is_one_unsplit_operator():
    result = physical_source_vertex_contract()
    assert result["differentiate_before_extracting_sectors"]
    assert result["separate_finite_gauge_counterterm"] is False
    assert result["separate_finite_Yukawa_insertion"] is False
    assert "5/3:1:1" in result["group_generators"]


def test_payload_validates_without_claiming_matrix_assembly():
    result = completion_payload()
    assert result["validation_passed"]
    assert result["claim_boundary"]["radial_angular_vertex_matrices_assembled"] is False
