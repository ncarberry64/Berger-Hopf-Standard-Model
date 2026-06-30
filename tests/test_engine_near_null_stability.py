import numpy as np

from bhsm.interface.engine_invariants import boundary_chart_forward, lorentz_boost_x, minkowski_norm_sq


def test_near_null_vector_remains_finite_and_invariant_under_boost():
    eps = np.finfo(float).eps
    state = np.array([[1.0, 1.0 - 8 * eps, 0.0, 0.0]])
    boosted = lorentz_boost_x(state, 0.4)
    assert np.all(np.isfinite(boundary_chart_forward(boosted)))
    np.testing.assert_allclose(minkowski_norm_sq(boosted), minkowski_norm_sq(state), rtol=1e-13, atol=1e-13)

