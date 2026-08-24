import numpy as np

from bhsm.interface.aether_forward_channel_transfer import (
    backward_weyl_mobius,
    backward_weyl_mobius_jets,
    product_dirac_channel_log_radius_jets,
    product_dirac_channel_transfer_generator,
    scalar_channel_log_radius_jets,
    scalar_channel_transfer_generator,
    transfer_variation_rhs,
)


def _mixed_difference(builder, x: float, h: float, k: float) -> np.ndarray:
    eps = 2.0e-4
    return (
        builder(x + eps * h + eps * k)
        - builder(x + eps * h - eps * k)
        - builder(x - eps * h + eps * k)
        + builder(x - eps * h - eps * k)
    ) / (4.0 * eps**2)


def test_scalar_channel_generator_and_jets() -> None:
    x, h, k = 0.17, 0.3, -0.4
    builder = lambda value: scalar_channel_transfer_generator(5.0, value, -1.0)
    jets = scalar_channel_log_radius_jets(5.0, x, -1.0, h, k)
    eps = 1.0e-6
    first = (builder(x + eps * h) - builder(x - eps * h)) / (2.0 * eps)
    assert np.trace(jets["base"]) == 0.0
    assert np.allclose(jets["first_left"], first, rtol=1.0e-8, atol=1.0e-9)
    assert np.allclose(
        jets["mixed_second"], _mixed_difference(builder, x, h, k), atol=1.0e-7
    )


def test_product_dirac_channel_generator_and_jets() -> None:
    x, h, k = -0.08, 0.2, 0.5
    builder = lambda value: product_dirac_channel_transfer_generator(
        -2.5, value, -1.0, chirality=-1
    )
    jets = product_dirac_channel_log_radius_jets(
        -2.5, x, -1.0, h, k, chirality=-1
    )
    eps = 1.0e-6
    first = (builder(x + eps * h) - builder(x - eps * h)) / (2.0 * eps)
    assert np.trace(jets["base"]) == 0.0
    assert np.allclose(jets["first_left"], first, rtol=1.0e-8, atol=1.0e-9)
    assert np.allclose(
        jets["mixed_second"], _mixed_difference(builder, x, h, k), atol=1.0e-8
    )


def test_generator_jets_include_mixed_second_log_radius_direction() -> None:
    x, h, k, ell = 0.11, 0.2, -0.3, 0.4
    eps = 2.0e-4

    def mixed(builder) -> np.ndarray:
        return (
            builder(x + eps * h + eps * k + eps**2 * ell)
            - builder(x + eps * h - eps * k - eps**2 * ell)
            - builder(x - eps * h + eps * k - eps**2 * ell)
            + builder(x - eps * h - eps * k + eps**2 * ell)
        ) / (4.0 * eps**2)

    scalar = scalar_channel_log_radius_jets(3.0, x, -0.5, h, k, ell)
    dirac = product_dirac_channel_log_radius_jets(
        2.0, x, -0.5, h, k, mixed_second_direction=ell
    )
    assert np.allclose(
        scalar["mixed_second"],
        mixed(lambda value: scalar_channel_transfer_generator(3.0, value, -0.5)),
        atol=1.0e-7,
    )
    assert np.allclose(
        dirac["mixed_second"],
        mixed(
            lambda value: product_dirac_channel_transfer_generator(
                2.0, value, -0.5
            )
        ),
        atol=1.0e-8,
    )


def test_transfer_variation_rhs_is_the_exact_product_jet() -> None:
    generator = {
        "base": np.asarray([[0.0, 1.0], [2.0, 0.0]]),
        "first_left": np.asarray([[0.1, 0.0], [0.2, -0.1]]),
        "first_right": np.asarray([[-0.3, 0.0], [0.4, 0.3]]),
        "mixed_second": np.asarray([[0.2, 0.1], [-0.2, -0.2]]),
    }
    transfer = {
        "base": np.asarray([[1.1, 0.2], [0.3, 0.9]]),
        "first_left": np.asarray([[0.2, -0.1], [0.0, 0.3]]),
        "first_right": np.asarray([[-0.1, 0.4], [0.2, 0.0]]),
        "mixed_second": np.asarray([[0.3, 0.0], [-0.2, 0.1]]),
    }
    rhs = transfer_variation_rhs(generator, transfer)
    expected = (
        generator["base"] @ transfer["mixed_second"]
        + generator["first_left"] @ transfer["first_right"]
        + generator["first_right"] @ transfer["first_left"]
        + generator["mixed_second"] @ transfer["base"]
    )
    assert np.allclose(rhs["mixed_second"], expected)


def test_backward_weyl_mobius_inverts_terminal_graph() -> None:
    transfer = np.asarray([[1.2, 0.4], [0.3, 1.1]], dtype=complex)
    birth = 0.7
    terminal = (transfer[1, 0] + transfer[1, 1] * birth) / (
        transfer[0, 0] + transfer[0, 1] * birth
    )
    recovered = backward_weyl_mobius(transfer, terminal)
    assert abs(recovered - birth) < 1.0e-14


def test_backward_weyl_mobius_jets_match_directional_differences() -> None:
    transfer = {
        "base": np.asarray([[1.2, 0.4], [0.3, 1.1]], dtype=complex),
        "first_left": np.asarray([[0.1, -0.2], [0.05, 0.03]], dtype=complex),
        "first_right": np.asarray([[-0.07, 0.08], [0.02, -0.04]], dtype=complex),
        "mixed_second": np.asarray([[0.02, 0.01], [-0.03, 0.05]], dtype=complex),
    }
    terminal = {
        "base": 0.8,
        "first_left": 0.06,
        "first_right": -0.09,
        "mixed_second": 0.04,
    }
    jets = backward_weyl_mobius_jets(transfer, terminal)

    def value(left: float, right: float) -> complex:
        matrix = (
            transfer["base"]
            + left * transfer["first_left"]
            + right * transfer["first_right"]
            + left * right * transfer["mixed_second"]
        )
        admittance = (
            terminal["base"]
            + left * terminal["first_left"]
            + right * terminal["first_right"]
            + left * right * terminal["mixed_second"]
        )
        return backward_weyl_mobius(matrix, admittance)

    eps = 1.0e-4
    left = (value(eps, 0.0) - value(-eps, 0.0)) / (2.0 * eps)
    right = (value(0.0, eps) - value(0.0, -eps)) / (2.0 * eps)
    mixed = (
        value(eps, eps)
        - value(eps, -eps)
        - value(-eps, eps)
        + value(-eps, -eps)
    ) / (4.0 * eps**2)
    assert abs(jets["first_left"] - left) < 1.0e-9
    assert abs(jets["first_right"] - right) < 1.0e-9
    assert abs(jets["mixed_second"] - mixed) < 1.0e-7
