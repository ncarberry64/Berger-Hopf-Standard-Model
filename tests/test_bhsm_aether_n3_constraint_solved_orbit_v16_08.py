import numpy as np

from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    integrate_n3_orbit,
    match_eigenframe,
    sobolev_eigenframe,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import sobolev_weights


def test_sobolev_generalized_eigenvectors_are_normalized():
    size = dimensions(3)["Dirac_pencil"]
    hessian = np.diag(np.linspace(-2.0, 3.0, size))
    values, physical, _ = sobolev_eigenframe(3, hessian)
    weights = sobolev_weights(3)
    product = np.concatenate((weights["velocities"], weights["multipliers"]))
    gram = physical.T @ np.diag(product**2) @ physical
    assert np.allclose(gram, np.eye(size), atol=1.0e-11)
    assert np.all(np.diff(values) >= 0.0)


def test_branch_matching_recovers_a_permutation_and_orientation():
    previous = np.eye(4)
    current = previous[:, [2, 0, 3, 1]]
    current[:, 1] *= -1.0
    permutation, overlap = match_eigenframe(previous, current)
    assert np.array_equal(permutation, [1, 3, 0, 2])
    assert np.allclose(overlap, 1.0)


def test_short_orbit_executes_two_constraint_solved_steps():
    orbit = integrate_n3_orbit(
        time_step=1.0e-3, maximum_steps=2, points=36
    )
    assert orbit["steps_completed"] == 2
    assert orbit["maximum_constraint_residual"] < 1.0e-7
