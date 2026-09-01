import numpy as np

from bhsm.interface.aether_forward_channel_transfer import (
    backward_weyl_mobius,
    reduce_two_boundary_weyl_with_terminal_load_jets,
    scalar_compact_history_weyl_jets,
)


KEYS = ("base", "first_left", "first_right", "mixed_second")


def _constant_radius_jets(scale: float, mixed: float):
    def jets(_time: float) -> dict[str, float]:
        return {
            "base": 0.2,
            "first_left": scale,
            "first_right": -0.4,
            "mixed_second": mixed,
        }

    return jets


def _weyl(scale: float, mixed: float, duration_left: float = 0.07):
    return scalar_compact_history_weyl_jets(
        2.3,
        -1.0,
        _constant_radius_jets(scale, mixed),
        {
            "base": 0.8,
            "first_left": duration_left,
            "first_right": -0.03,
            "mixed_second": 0.02,
        },
        relative_tolerance=2.0e-12,
        absolute_tolerance=2.0e-14,
    )["weyl"]


def _load(left: float, right: float, mixed: float):
    return {
        "base": np.asarray([[1.4]]),
        "first_left": np.asarray([[left]]),
        "first_right": np.asarray([[right]]),
        "mixed_second": np.asarray([[mixed]]),
    }


def test_terminal_load_reduction_matches_scalar_transfer_mobius() -> None:
    history = scalar_compact_history_weyl_jets(
        2.3,
        -1.0,
        _constant_radius_jets(0.5, 0.11),
        {
            "base": 0.8,
            "first_left": 0.07,
            "first_right": -0.03,
            "mixed_second": 0.02,
        },
    )
    reduced = reduce_two_boundary_weyl_with_terminal_load_jets(
        history["weyl"], _load(0.2, -0.1, 0.04)
    )
    # backward_weyl_mobius returns p_birth/u_birth.  The reduced response uses
    # the outward birth conormal -p_birth and p_terminal=-B*u_terminal.
    pulled_back = -backward_weyl_mobius(
        history["transfer"]["base"], -1.4
    )
    assert abs(reduced["base"][0, 0] - pulled_back) < 2.0e-12
    assert reduced["explicit_matrix_inverse_formed"] is False
    assert reduced["terminal_load_selected_by_routine"] is False
    assert max(reduced["bordered_solve_residuals"].values()) < 2.0e-14


def test_terminal_load_reduction_jets_match_centered_differences() -> None:
    epsilon = 2.0e-5

    def evaluate(left_parameter: float, right_parameter: float) -> np.ndarray:
        dl = left_parameter - 1.0
        dr = right_parameter - 1.0
        log_radius = 0.2 + 0.5 * dl - 0.4 * dr + 0.11 * dl * dr
        duration = 0.8 + 0.07 * dl - 0.03 * dr + 0.02 * dl * dr

        def radius(_time: float) -> dict[str, float]:
            return {
                "base": log_radius,
                "first_left": 0.0,
                "first_right": 0.0,
                "mixed_second": 0.0,
            }

        weyl = scalar_compact_history_weyl_jets(
            2.3,
            -1.0,
            radius,
            {
                "base": duration,
                "first_left": 0.0,
                "first_right": 0.0,
                "mixed_second": 0.0,
            },
            relative_tolerance=2.0e-12,
            absolute_tolerance=2.0e-14,
        )["weyl"]
        load_base = 1.4 + 0.2 * dl - 0.1 * dr + 0.04 * dl * dr
        load = {
            "base": np.asarray([[load_base]]),
            "first_left": np.zeros((1, 1)),
            "first_right": np.zeros((1, 1)),
            "mixed_second": np.zeros((1, 1)),
        }
        return reduce_two_boundary_weyl_with_terminal_load_jets(
            weyl, load
        )["base"]

    center_weyl = _weyl(0.5, 0.11)
    center = reduce_two_boundary_weyl_with_terminal_load_jets(
        center_weyl, _load(0.2, -0.1, 0.04)
    )
    left_fd = (
        evaluate(1.0 + epsilon, 1.0)
        - evaluate(1.0 - epsilon, 1.0)
    ) / (2.0 * epsilon)
    right_fd = (
        evaluate(1.0, 1.0 + epsilon)
        - evaluate(1.0, 1.0 - epsilon)
    ) / (2.0 * epsilon)
    mixed_fd = (
        evaluate(1.0 + epsilon, 1.0 + epsilon)
        - evaluate(1.0 + epsilon, 1.0 - epsilon)
        - evaluate(1.0 - epsilon, 1.0 + epsilon)
        + evaluate(1.0 - epsilon, 1.0 - epsilon)
    ) / (4.0 * epsilon**2)
    assert np.linalg.norm(center["first_left"] - left_fd) < 2.0e-8
    assert np.linalg.norm(center["first_right"] - right_fd) < 2.0e-8
    assert np.linalg.norm(center["mixed_second"] - mixed_fd) < 2.0e-6


def test_terminal_graph_margin_is_enforced_without_inverse() -> None:
    weyl = {
        key: np.zeros((2, 2), dtype=float) for key in KEYS
    }
    load = {key: np.zeros((1, 1), dtype=float) for key in KEYS}
    try:
        reduce_two_boundary_weyl_with_terminal_load_jets(
            weyl, load, minimum_singular_value=1.0e-12
        )
    except np.linalg.LinAlgError:
        pass
    else:
        raise AssertionError("singular terminal graph was not rejected")
