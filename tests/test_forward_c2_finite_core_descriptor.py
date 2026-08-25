from __future__ import annotations

import numpy as np

from bhsm.interface.aether_forward_c2_finite_core_descriptor import (
    assemble_finite_core_descriptor,
)


def _dense(diagonal: np.ndarray, off: np.ndarray) -> np.ndarray:
    return np.diag(diagonal) + np.diag(off, 1) + np.diag(off, -1)


def test_scalar_element_derivatives_match_centered_differences() -> None:
    x = np.asarray([0.1, 0.12])
    h = np.asarray([0.3])
    base = assemble_finite_core_descriptor(
        log_radii=x, proper_durations=h, channel="scalar", unit_channel_value=3.0
    )
    epsilon = 1.0e-6
    x_plus = x + epsilon
    x_minus = x - epsilon
    plus = assemble_finite_core_descriptor(
        log_radii=x_plus, proper_durations=h, channel="scalar", unit_channel_value=3.0
    )
    minus = assemble_finite_core_descriptor(
        log_radii=x_minus, proper_durations=h, channel="scalar", unit_channel_value=3.0
    )
    finite = (_dense(plus["K_diagonal"], plus["K_off_diagonal"])
              - _dense(minus["K_diagonal"], minus["K_off_diagonal"])) / (2 * epsilon)
    analytic = base["D_x_mid_K_elements"][0, :1, :1]
    assert np.allclose(finite, analytic, rtol=1.0e-9, atol=1.0e-9)


def test_product_dirac_pencil_is_positive_and_inverse_free() -> None:
    result = assemble_finite_core_descriptor(
        log_radii=np.asarray([0.0, 0.02, 0.01]),
        proper_durations=np.asarray([0.2, 0.25]),
        channel="product_Dirac",
        unit_channel_value=1.5,
        chirality=-1,
    )
    K = _dense(result["K_diagonal"], result["K_off_diagonal"])
    assert np.linalg.eigvalsh(K)[0] > 0.0
    assert result["generalized_gap_lower"] > 0.0
    assert result["explicit_matrix_inverse_formed"] is False
    assert result["birth_node_retained"] is True
    assert result["far_core_Dirichlet_node_eliminated"] is True
