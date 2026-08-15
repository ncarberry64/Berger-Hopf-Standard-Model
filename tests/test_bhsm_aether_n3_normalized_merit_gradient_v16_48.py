from bhsm.interface.aether_n3_normalized_merit_gradient_v16_48 import TRUST_RADII


def test_merit_trust_grid_brackets_v16_47_step():
    assert min(TRUST_RADII) < 0.003444598383031 < max(TRUST_RADII)
