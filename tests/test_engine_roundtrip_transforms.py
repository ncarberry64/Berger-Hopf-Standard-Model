import numpy as np

from bhsm.interface.engine_invariants import boundary_chart_forward, boundary_chart_inverse


def test_boundary_chart_roundtrip_including_origin_and_pole():
    states = np.array([[2.0, 0.0, 0.0, 0.0], [5.0, 0.0, 0.0, 4.0], [5.0, 3.0, 4.0, 0.0]])
    np.testing.assert_allclose(boundary_chart_inverse(boundary_chart_forward(states)), states)

