from bhsm.interface.aether_n3_covector_consistent_curvature_v16_53 import CURVATURE_RELATIVE_STEP


def test_curvature_step_stays_inside_audited_soft_branch_chart():
    assert CURVATURE_RELATIVE_STEP < 1e-4
