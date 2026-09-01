import numpy as np
import pytest

from bhsm.interface.aether_forward_common_source_incidence import (
    canonical_temporal_form_laplacian,
    temporal_form_pair_residual,
)
from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import (
    periodic_first_derivative,
    periodic_laplacian,
)


def test_historical_periodic_seed_obeys_temporal_form_identity() -> None:
    derivative = periodic_first_derivative(24, 0.1)
    laplacian = periodic_laplacian(24, 0.1)
    residual = temporal_form_pair_residual(derivative, laplacian)
    assert residual / np.linalg.norm(laplacian, ord=2) < 1.0e-14


def test_action_owned_endpoint_form_enters_once() -> None:
    derivative = np.array(
        [[-1.0, 1.0, 0.0], [0.0, -1.0, 1.0], [0.0, 0.0, 0.0]],
        dtype=complex,
    )
    endpoint = np.diag([0.25, 0.0, 0.5])
    laplacian = canonical_temporal_form_laplacian(derivative, endpoint)
    assert np.allclose(laplacian, laplacian.conj().T)
    assert np.min(np.linalg.eigvalsh(laplacian)) >= -1.0e-13
    assert temporal_form_pair_residual(derivative, laplacian, endpoint) == 0.0


def test_negative_or_nonhermitian_endpoint_form_is_rejected() -> None:
    derivative = np.eye(2)
    with pytest.raises(ValueError, match="nonnegative"):
        canonical_temporal_form_laplacian(derivative, np.diag([-1.0, 0.0]))
    with pytest.raises(ValueError, match="Hermitian"):
        canonical_temporal_form_laplacian(
            derivative, np.array([[0.0, 1.0], [0.0, 0.0]])
        )
