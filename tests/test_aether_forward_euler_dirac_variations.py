import numpy as np

from bhsm.interface.aether_forward_euler_dirac_variations import (
    implicit_linear_solve_jet_bounds,
    implicit_linear_solve_jets,
    jacobi_cocycle_bounds,
)


def test_implicit_solve_jets_match_mixed_differences() -> None:
    operators = {
        "base": np.asarray([[2.0, 0.2], [0.1, 1.7]]),
        "first_left": np.asarray([[0.2, -0.1], [0.0, 0.1]]),
        "first_right": np.asarray([[-0.1, 0.0], [0.2, 0.05]]),
        "mixed_second": np.asarray([[0.03, 0.02], [-0.01, 0.04]]),
    }
    rhs = {
        "base": np.asarray([1.0, -0.4]),
        "first_left": np.asarray([0.2, 0.1]),
        "first_right": np.asarray([-0.1, 0.3]),
        "mixed_second": np.asarray([0.05, -0.02]),
    }
    jets = implicit_linear_solve_jets(operators, rhs)

    def value(left: float, right: float) -> np.ndarray:
        matrix = (
            operators["base"]
            + left * operators["first_left"]
            + right * operators["first_right"]
            + left * right * operators["mixed_second"]
        )
        vector = (
            rhs["base"]
            + left * rhs["first_left"]
            + right * rhs["first_right"]
            + left * right * rhs["mixed_second"]
        )
        return np.linalg.solve(matrix, vector)

    eps = 1e-4
    mixed = (
        value(eps, eps)
        - value(eps, -eps)
        - value(-eps, eps)
        + value(-eps, -eps)
    ) / (4.0 * eps**2)
    assert np.linalg.norm(jets["mixed_second"] - mixed) < 1e-8


def test_solve_and_cocycle_majorants_are_finite() -> None:
    bounds = implicit_linear_solve_jet_bounds(
        2.0, 3.0, 4.0, 5.0, 6.0, 0.2, 0.3, 0.4
    )
    assert bounds["base"] == 6.0
    assert bounds["mixed_second"] > bounds["first_left"]
    cocycle = jacobi_cocycle_bounds(3.0, 7.0, 0.1)
    assert cocycle["first"] > 1.0
    assert cocycle["mixed_second"] > 0.0
