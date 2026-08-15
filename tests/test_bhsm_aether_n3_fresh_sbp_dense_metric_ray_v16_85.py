from bhsm.interface.aether_n3_fresh_sbp_dense_metric_ray_v16_85 import CAUCHY,completion_payload
def test_dense_joint_boundary_grid():assert all(v in CAUCHY for v in (0.3,0.4,0.5,0.6,0.8,1.0))
def test_dense_metric_ray_validates():assert completion_payload()["validation_passed"]
