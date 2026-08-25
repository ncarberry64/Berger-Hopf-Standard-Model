import numpy as np

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_weight_five_action_jet_at_state,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.weight_seven_transverse_descriptor import (
    ROUND_EXPANSION_RATE,
    weight_five_center_lift_system,
)


def _state(scale=0.0):
    dims = dimensions(12)
    q = np.zeros(dims["coordinates"])
    q[0] = scale
    v = np.zeros_like(q)
    v[0] = ROUND_EXPANSION_RATE
    m = np.zeros(dims["multipliers"])
    return q, v, m


def test_weight_five_action_has_exact_scale_covariance():
    normalized = []
    for scale in (0.0, 1.0, 2.0):
        q, v, m = _state(scale)
        jet = exact_weight_five_action_jet_at_state(
            12, q, v, m, points=192
        )
        radius = RADIUS0 * np.exp(scale)
        normalized.append((
            jet.value / radius**5,
            np.linalg.norm(jet.gradient) / radius**5,
            np.linalg.norm(jet.hessian, 2) / radius**5,
        ))
    assert np.ptp([row[0] for row in normalized]) < 2.0e-12
    assert np.ptp([row[1] for row in normalized]) < 2.0e-10
    assert np.ptp([row[2] for row in normalized]) < 2.0e-8


def test_weight_five_action_has_no_velocity_dependence():
    q, v, m = _state()
    jet = exact_weight_five_action_jet_at_state(12, q, v, m, points=192)
    qdim = q.size
    assert np.max(np.abs(jet.gradient[qdim:2 * qdim])) == 0.0
    assert np.max(np.abs(jet.hessian[qdim:2 * qdim, :])) == 0.0


def test_weight_five_center_lift_is_returned_without_solution():
    system = weight_five_center_lift_system(points=192)
    assert system["matrix"].shape == (74, 74)
    assert system["right_hand_side"].shape == (74,)
    assert np.isclose(
        system["descriptor_exponent"], -2.0 * ROUND_EXPANSION_RATE
    )
    assert system["condition_number"] > 1.0e10
