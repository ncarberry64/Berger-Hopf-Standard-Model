import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_dop853_boundary_cluster_probe as dense  # noqa: E402
import recon_n12_c2_stop_dop853_dense_residual as residual  # noqa: E402


CENTER = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
)


def _bernstein_value(controls: np.ndarray, fraction: float) -> np.ndarray:
    degree = controls.shape[0] - 1
    return sum(
        math.comb(degree, index)
        * fraction**index * (1.0 - fraction)**(degree - index)
        * controls[index]
        for index in range(degree + 1)
    )


def test_dense_bernstein_conversion_replays_stored_polynomial() -> None:
    with np.load(CENTER) as source:
        values = source["fine_grid_augmented_action_values"]
        coefficients = source["fine_grid_DOP853_dense_coefficients"]
    for interval in (0, 137, 369):
        controls = dense._dense_bernstein_controls(
            values[interval], coefficients[interval],
        )
        for fraction in (0.0, 0.137, 0.5, 0.893, 1.0):
            expected = residual._dense(
                values[interval], coefficients[interval], fraction,
            )
            assert np.allclose(
                _bernstein_value(controls, fraction), expected,
                rtol=2e-15, atol=8e-15,
            )


def test_bernstein_simplex_lies_in_declared_action_ellipsoid() -> None:
    geometry = dense.dense_subspan_geometry(137, 2)
    controls = geometry["augmented_Bernstein_controls"][:, :-1]
    midpoint = np.mean(controls, axis=0)
    projection = geometry["projection"]
    for fraction in (0.0, 0.2, 0.5, 0.8, 1.0):
        degree = controls.shape[0] - 1
        theta = np.asarray([
            math.comb(degree, index)
            * fraction**index * (1.0 - fraction)**(degree - index)
            for index in range(degree + 1)
        ])
        assert np.linalg.norm(theta) <= 1.0 + 2e-15
        assert np.allclose(
            midpoint + projection @ theta,
            _bernstein_value(controls, fraction),
            rtol=2e-15, atol=8e-15,
        )
