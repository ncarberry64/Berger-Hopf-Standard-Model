from bhsm.interface.aether_n3_fresh_sbp_fifth_post_dense_family_v17_18 import completion_payload,v17_17_selected_raw_vector
def test_v17_17_state_has_complete_dimension():assert v17_17_selected_raw_vector().shape==(376,)
def test_fifth_post_dense_family_validates():assert completion_payload()["validation_passed"]
