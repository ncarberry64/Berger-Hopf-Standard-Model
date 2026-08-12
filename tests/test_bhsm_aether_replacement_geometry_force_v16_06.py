import math

import numpy as np

from bhsm.interface.aether_replacement_geometry_force_v16_06 import (
    force_finite_difference_witness,
    log_radius_coordinate_jacobian,
    zeta_geometry_response,
)


def test_heat_geometry_force_matches_finite_difference():
    assert force_finite_difference_witness()["relative_residual"] < 2.0e-8


def test_exact_boundary_radius_coordinate_jacobian():
    q = np.zeros((2, 9))
    q[1, 5] = 0.3
    q[1, 6] = -0.1
    result = log_radius_coordinate_jacobian(q)
    assert np.allclose(result[:, :3], [[1.0, -1.0, 1.0]] * 2)
    assert result[0, 5] == result[0, 6] == 0.0
    assert math.isclose(result[1, 5], -math.tanh(0.8))
    assert math.isclose(result[1, 6], math.tanh(0.8))
    assert np.all(result[:, 7:] == 0.0)


def test_removed_zeta_force_has_correct_sign():
    result = zeta_geometry_response(np.ones(6), 0.1)
    assert result["Gamma_SM_zeta"] < 0.0
    assert np.all(result["d_Gamma_SM_zeta_d_log_R_nodes"] > 0.0)
