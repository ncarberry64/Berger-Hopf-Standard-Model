from bhsm.interface.aether_n3_fresh_sbp_post_dense_tangent_family_v17_13 import completion_payload,v17_12_selected_raw_vector
def test_v17_12_state_has_complete_dimension():assert v17_12_selected_raw_vector().shape==(376,)
def test_post_dense_tangent_family_validates():assert completion_payload()["validation_passed"]
