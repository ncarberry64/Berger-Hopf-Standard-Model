import numpy as np

from bhsm.interface.aether_forward_channel_transfer import (
    backward_weyl_mobius,
    product_dirac_channel_log_radius_jets,
    product_dirac_channel_transfer_generator,
    scalar_channel_log_radius_jets,
    scalar_channel_transfer_generator,
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


def test_backward_weyl_mobius_inverts_terminal_graph() -> None:
    transfer = np.asarray([[1.2, 0.4], [0.3, 1.1]], dtype=complex)
    birth = 0.7
    terminal = (transfer[1, 0] + transfer[1, 1] * birth) / (
        transfer[0, 0] + transfer[0, 1] * birth
    )
    recovered = backward_weyl_mobius(transfer, terminal)
    assert abs(recovered - birth) < 1.0e-14
