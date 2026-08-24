import numpy as np

from bhsm.interface.aether_forward_common_source_incidence import (
    forward_hs_scalar_operator_and_gauge_vertices,
    forward_oneform_ghost_matrices,
    forward_weyl_squared_operator_and_vertices,
)
from bhsm.interface.aether_nonabelian_derham_response_v16_04 import (
    full_oneform_ghost_matrices,
)
from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import (
    hs_scalar_operator_and_gauge_vertices,
    periodic_first_derivative,
    periodic_laplacian,
    weyl_squared_operator_and_vertices,
)


def _inputs() -> tuple[np.ndarray, float, np.ndarray, np.ndarray, np.ndarray]:
    radii = np.asarray([1.0, 1.05, 1.02, 0.98])
    step = 0.1
    profile = np.asarray([0.2, -0.1, 0.3, 0.05])
    first = periodic_first_derivative(len(radii), step)
    laplacian = periodic_laplacian(len(radii), step)
    return radii, step, profile, first, laplacian


def test_domain_parametric_weyl_incidence_reproduces_periodic_builder() -> None:
    radii, step, profile, first, _ = _inputs()
    for source in ("coexact_gauge", "HS"):
        expected = weyl_squared_operator_and_vertices(
            1, radii, step, profile, source=source
        )
        actual = forward_weyl_squared_operator_and_vertices(
            1, radii, first, profile, source=source
        )
        assert all(np.allclose(left, right) for left, right in zip(actual, expected))


def test_domain_parametric_hs_incidence_reproduces_periodic_builder() -> None:
    radii, step, profile, _, laplacian = _inputs()
    expected = hs_scalar_operator_and_gauge_vertices(1, radii, step, profile)
    actual = forward_hs_scalar_operator_and_gauge_vertices(
        1, radii, laplacian, profile
    )
    assert all(np.allclose(left, right) for left, right in zip(actual, expected))


def test_domain_parametric_derham_incidence_reproduces_periodic_builder() -> None:
    radii, step, profile, first, laplacian = _inputs()
    for level in (0, 1):
        expected = full_oneform_ghost_matrices(level, radii, step, profile)
        actual = forward_oneform_ghost_matrices(
            level, radii, first, laplacian, profile
        )
        assert set(actual) == set(expected)
        assert all(np.allclose(actual[key], expected[key]) for key in actual)


def test_incidence_accepts_a_nonperiodic_realization_without_selecting_it() -> None:
    radii = np.asarray([1.0, 1.01, 1.02, 1.03])
    profile = np.asarray([0.0, 0.2, -0.1, 0.0])
    first = np.asarray([
        [-1.0, 1.0, 0.0, 0.0],
        [-0.5, 0.0, 0.5, 0.0],
        [0.0, -0.5, 0.0, 0.5],
        [0.0, 0.0, -1.0, 1.0],
    ])
    laplacian = first.conj().T @ first
    matrices = forward_oneform_ghost_matrices(
        1, radii, first, laplacian, profile
    )
    assert all(np.all(np.isfinite(value)) for value in matrices.values())
    assert all(
        np.allclose(value, value.conj().T)
        for value in matrices.values()
    )
