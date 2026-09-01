import numpy as np

from bhsm.interface.weight_seven_transverse_descriptor import (
    ROUND_EXPANSION_RATE,
    bordered_physical_pencil,
    cluster_residuals,
    constraint_solved_crosscheck,
    descriptor_data,
    homogeneous_spectrum,
    physical_coordinate_indices,
    time_gauge_vector,
)


def test_polynomial_time_gauge_chains_are_exact():
    data = descriptor_data(points=192)
    for sigma in (0.0, 0.3, -1.1, 2.0):
        pencil = data.A - sigma * data.E
        scale = max(1.0, np.linalg.norm(pencil, 2))
        for mode in range(12):
            vector = time_gauge_vector(sigma, mode)
            residual = np.linalg.norm(pencil @ vector) / (
                scale * np.linalg.norm(vector)
            )
            assert residual < 2.0e-12


def test_physical_quotient_retains_common_scale():
    physical = physical_coordinate_indices()
    assert physical.size == 25
    assert physical[0] == 0
    assert np.array_equal(physical[1:], np.arange(13, 37))


def test_bordered_descriptor_mode_classification():
    data = descriptor_data(points=384)
    A, E = bordered_physical_pencil(data)
    values, infinite = homogeneous_spectrum(A, E)
    clusters = cluster_residuals(values)
    assert A.shape == (74, 74)
    assert infinite == 24
    assert values.size == 50
    assert clusters["center_count"] == 25
    assert clusters["stable_count"] == 25
    assert clusters["unstable_count"] == 0
    assert clusters["maximum_center_residual"] < 2.0e-6
    assert clusters["maximum_stable_residual"] < 2.0e-6
    assert np.isclose(-7.0 * ROUND_EXPANSION_RATE, -2.7351681423105507)


def test_constraint_solved_crosscheck_without_combined_inverse():
    data = descriptor_data(points=384)
    result = constraint_solved_crosscheck(data)
    values = result.pop("finite_eigenvalues")
    clusters = cluster_residuals(values)
    assert result["combined_euler_dirac_inverse_formed"] is False
    assert result["algebraic_solve_relative_residual"] < 2.0e-10
    assert result["infinite_modes"] == 0
    assert clusters["center_count"] == 25
    assert clusters["stable_count"] == 25
