import numpy as np

from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    anchored_kkt_dimensions,
    boundary_radius_and_jacobian,
    event_gradient_indices,
    kkt_variable_scales,
    open_difference_matrix,
    pack_reduced,
    unpack_reduced,
)


def test_anchored_n3_event_kkt_is_376_by_376():
    row = anchored_kkt_dimensions()
    assert row["square"]
    assert row["total_unknowns"] == row["total_equations"] == 376
    assert not row["old_386_count_valid"]
    assert row["event_multiplier_unknowns"] == 1


def test_reduced_pack_eliminates_reset_coordinates():
    q = np.arange(240.0).reshape(24, 10) / 100.0
    m = np.arange(144.0).reshape(24, 6) / 200.0
    vector = pack_reduced(q, m, 0.05, 0.2)
    unpacked = unpack_reduced(vector)
    assert vector.shape == (376,)
    assert np.allclose(unpacked["coordinates"][1:], q[1:])
    assert np.allclose(unpacked["multipliers"], m)
    assert unpacked["period"] == 0.05
    assert unpacked["event_multiplier"] == 0.2


def test_boundary_radius_jacobian_matches_finite_difference():
    q = np.zeros((24, 10))
    q[:, 0] = np.linspace(-0.1, 0.1, 24)
    q[:, 7:] = np.asarray((0.2, -0.1, 0.05))
    radius, jacobian = boundary_radius_and_jacobian(q)
    direction = np.linspace(-0.3, 0.4, 10)
    epsilon = 1.0e-7
    plus, _ = boundary_radius_and_jacobian(q + epsilon * direction)
    minus, _ = boundary_radius_and_jacobian(q - epsilon * direction)
    finite = (np.log(plus) - np.log(minus)) / (2.0 * epsilon)
    assert np.allclose(finite, jacobian @ direction, rtol=2.0e-8, atol=2.0e-9)


def test_open_difference_is_exact_on_quadratics():
    x = np.linspace(0.0, 1.0, 24)
    derivative = open_difference_matrix() @ x**2
    assert np.allclose(derivative, 2.0 * x, atol=2.0e-14)


def test_event_gradient_has_the_expected_37_variable_support():
    indices = event_gradient_indices()
    assert len(indices) == 37
    assert len(np.unique(indices)) == 37
    assert indices[-1] == 374


def test_kkt_scaling_is_positive_and_preserves_event_duality():
    event_scale = 2.5e-3
    scales = kkt_variable_scales(event_scale)
    assert scales.shape == (376,)
    assert np.all(scales > 0.0)
    assert scales[-2] == 1.0
    assert scales[-1] == event_scale
