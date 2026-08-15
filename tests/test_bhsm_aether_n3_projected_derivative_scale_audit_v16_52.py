from bhsm.interface.aether_n3_projected_derivative_scale_audit_v16_52 import DERIVATIVE_SCALES


def test_scale_grid_brackets_internal_covector_step():
    assert min(DERIVATIVE_SCALES) < 2e-6 < max(DERIVATIVE_SCALES)
