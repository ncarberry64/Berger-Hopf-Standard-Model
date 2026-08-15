from bhsm.interface.aether_n3_fresh_sbp_metric_projected_newton_v16_76 import completion_payload,metric_projected_newton
from bhsm.interface.aether_n3_fresh_sbp_refined_damped_cone_v16_73 import FILTER_RELATIVE_SCALES,CONE_FACTORS

def test_metric_projection_probes_complete_grid():
    result=metric_projected_newton()
    assert result["direction_count"]==len(FILTER_RELATIVE_SCALES)*len(CONE_FACTORS)
    assert result["projection_metric"].startswith("DAMPED_GAUSS_NEWTON")

def test_metric_projected_step_validates():assert completion_payload()["validation_passed"]
